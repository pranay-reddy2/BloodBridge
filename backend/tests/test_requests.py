import pytest


def _request(client, **overrides):
    payload = {"hospital": "City General", "patient_ref": "P-001", "blood_group": "A+", "units_needed": 2}
    payload.update(overrides)
    response = client.post("/api/requests", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_create_request_defaults(client):
    req = _request(client)
    assert req["status"] == "PENDING"
    assert req["component"] == "RED_CELLS"
    assert req["units_issued"] == 0


def test_requests_are_listed_most_urgent_first(client):
    _request(client, patient_ref="routine", urgency="ROUTINE")
    _request(client, patient_ref="critical", urgency="CRITICAL")
    _request(client, patient_ref="urgent", urgency="URGENT")
    order = [r["patient_ref"] for r in client.get("/api/requests").json()]
    assert order == ["critical", "urgent", "routine"]


def test_fulfil_prefers_identical_group_and_spares_o_negative(client, stock):
    o_neg = stock("O-", 2)
    a_pos = stock("A+", 2)
    req = _request(client, blood_group="A+", units_needed=2)

    result = client.post(f"/api/requests/{req['id']}/fulfil").json()

    assert result["shortfall"] == 0
    assert result["request"]["status"] == "FULFILLED"
    assert sorted(u["id"] for u in result["allocated_units"]) == sorted(u["id"] for u in a_pos)
    assert all(client.get(f"/api/units/{u['id']}").json()["status"] == "AVAILABLE" for u in o_neg)


def test_fulfil_uses_first_expiring_unit(client, stock, days_ago):
    newer = stock("B+", collected_on=days_ago(1))[0]
    older = stock("B+", collected_on=days_ago(20))[0]
    req = _request(client, blood_group="B+", units_needed=1)

    allocated = client.post(f"/api/requests/{req['id']}/fulfil").json()["allocated_units"]
    assert [u["id"] for u in allocated] == [older["id"]]
    assert client.get(f"/api/units/{newer['id']}").json()["status"] == "AVAILABLE"


def test_partial_fulfilment_then_completion(client, stock):
    stock("O-", 1)
    req = _request(client, blood_group="O-", units_needed=3, urgency="CRITICAL")

    first = client.post(f"/api/requests/{req['id']}/fulfil").json()
    assert first["request"]["status"] == "PARTIAL"
    assert first["shortfall"] == 2

    stock("O-", 2)
    second = client.post(f"/api/requests/{req['id']}/fulfil").json()
    assert second["request"]["status"] == "FULFILLED"
    assert second["request"]["units_issued"] == 3


def test_fulfil_with_no_compatible_stock_conflicts(client, stock):
    stock("A+", 3)  # A+ cannot be given to an O+ patient
    req = _request(client, blood_group="O+", units_needed=1)
    response = client.post(f"/api/requests/{req['id']}/fulfil")
    assert response.status_code == 409
    assert client.get(f"/api/requests/{req['id']}").json()["status"] == "PENDING"


def test_plasma_follows_reverse_abo_rules(client, stock):
    stock("AB+", 1, component="PLASMA")
    req = _request(client, blood_group="O-", component="PLASMA", units_needed=1)
    assert client.post(f"/api/requests/{req['id']}/fulfil").json()["request"]["status"] == "FULFILLED"


def test_expired_units_are_never_issued(client, stock, days_ago):
    stock("AB+", 1, component="PLATELETS", collected_on=days_ago(6))
    req = _request(client, blood_group="AB+", component="PLATELETS", units_needed=1)
    assert client.post(f"/api/requests/{req['id']}/fulfil").status_code == 409


@pytest.mark.parametrize("final_status", ["FULFILLED", "CANCELLED"])
def test_closed_requests_cannot_be_modified(client, stock, final_status):
    stock("A+", 1)
    req = _request(client, units_needed=1)
    if final_status == "FULFILLED":
        client.post(f"/api/requests/{req['id']}/fulfil")
    else:
        assert client.put(f"/api/requests/{req['id']}", json={"status": "CANCELLED"}).status_code == 200
    assert client.put(f"/api/requests/{req['id']}", json={"notes": "late edit"}).status_code == 409
    assert client.post(f"/api/requests/{req['id']}/fulfil").status_code == 409


def test_delete_request(client, stock):
    req = _request(client)
    assert client.delete(f"/api/requests/{req['id']}").status_code == 204
    assert client.get(f"/api/requests/{req['id']}").status_code == 404

    stock("A+", 1)
    issued = _request(client, units_needed=1)
    client.post(f"/api/requests/{issued['id']}/fulfil")
    assert client.delete(f"/api/requests/{issued['id']}").status_code == 409

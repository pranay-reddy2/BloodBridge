def test_create_and_get_donor(client, make_donor):
    donor = make_donor(full_name="Asha Rao", blood_group="B-")
    assert donor["eligible"] is True
    assert donor["next_eligible_on"] is None

    fetched = client.get(f"/api/donors/{donor['id']}").json()
    assert fetched["full_name"] == "Asha Rao"
    assert fetched["blood_group"] == "B-"


def test_create_donor_rejects_invalid_blood_group(client):
    response = client.post(
        "/api/donors",
        json={"full_name": "X Y", "blood_group": "C+", "email": "x@y.org", "phone": "9876543210", "city": "Goa"},
    )
    assert response.status_code == 422


def test_duplicate_email_conflicts_case_insensitively(client, make_donor):
    make_donor(email="same@example.org")
    response = client.post(
        "/api/donors",
        json={"full_name": "Other", "blood_group": "A+", "email": "SAME@example.org", "phone": "9876543210", "city": "Goa"},
    )
    assert response.status_code == 409


def test_list_donors_filters(client, make_donor, days_ago):
    make_donor(blood_group="A+", city="Pune")
    make_donor(blood_group="A+", city="Delhi")
    make_donor(blood_group="O-", city="Pune", full_name="Recent Giver", last_donation_date=days_ago(10).isoformat())

    assert len(client.get("/api/donors", params={"blood_group": "A+"}).json()) == 2
    assert len(client.get("/api/donors", params={"city": "pune"}).json()) == 2
    assert [d["full_name"] for d in client.get("/api/donors", params={"eligible": "false"}).json()] == ["Recent Giver"]
    assert [d["full_name"] for d in client.get("/api/donors", params={"q": "recent"}).json()] == ["Recent Giver"]


def test_update_donor(client, make_donor):
    donor = make_donor()
    response = client.put(f"/api/donors/{donor['id']}", json={"city": "Mumbai", "phone": "+91 90000 00000"})
    assert response.status_code == 200
    assert response.json()["city"] == "Mumbai"


def test_delete_donor_without_units(client, make_donor):
    donor = make_donor()
    assert client.delete(f"/api/donors/{donor['id']}").status_code == 204
    assert client.get(f"/api/donors/{donor['id']}").status_code == 404


def test_delete_donor_with_units_is_blocked(client, make_donor):
    donor = make_donor()
    client.post(f"/api/donors/{donor['id']}/donations", json={})
    assert client.delete(f"/api/donors/{donor['id']}").status_code == 409


def test_unknown_donor_returns_404(client):
    assert client.get("/api/donors/9999").status_code == 404

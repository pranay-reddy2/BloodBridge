from datetime import date, timedelta

from app.models import BloodUnit


def test_donation_creates_unit_with_component_shelf_life(client, make_donor):
    donor = make_donor(blood_group="AB-")
    unit = client.post(f"/api/donors/{donor['id']}/donations", json={"component": "PLATELETS", "volume_ml": 250}).json()

    assert unit["blood_group"] == "AB-"
    assert unit["status"] == "AVAILABLE"
    assert date.fromisoformat(unit["expires_on"]) - date.fromisoformat(unit["collected_on"]) == timedelta(days=5)

    donor_after = client.get(f"/api/donors/{donor['id']}").json()
    assert donor_after["eligible"] is False
    assert donor_after["last_donation_date"] == date.today().isoformat()


def test_donor_cannot_donate_again_within_interval(client, make_donor, days_ago):
    donor = make_donor(last_donation_date=days_ago(30).isoformat())
    response = client.post(f"/api/donors/{donor['id']}/donations", json={})
    assert response.status_code == 409
    assert "not eligible" in response.json()["detail"]


def test_donor_can_donate_after_interval(client, make_donor, days_ago):
    donor = make_donor(last_donation_date=days_ago(91).isoformat())
    assert client.post(f"/api/donors/{donor['id']}/donations", json={}).status_code == 201


def test_future_collection_date_rejected(client, make_donor):
    donor = make_donor()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    assert client.post(f"/api/donors/{donor['id']}/donations", json={"collected_on": tomorrow}).status_code == 422


def test_quarantine_and_discard_unit(client, stock):
    unit = stock("B+")[0]
    assert client.put(f"/api/units/{unit['id']}", json={"status": "QUARANTINED"}).json()["status"] == "QUARANTINED"
    assert client.put(f"/api/units/{unit['id']}", json={"status": "DISCARDED"}).json()["status"] == "DISCARDED"
    # discarded is terminal
    assert client.put(f"/api/units/{unit['id']}", json={"status": "AVAILABLE"}).status_code == 409


def test_cannot_set_unit_to_issued_directly(client, stock):
    unit = stock("B+")[0]
    assert client.put(f"/api/units/{unit['id']}", json={"status": "ISSUED"}).status_code == 422


def test_expire_sweep_marks_old_stock(client, stock, days_ago, db_session):
    fresh = stock("O+")[0]
    old = stock("O+", component="PLATELETS", collected_on=days_ago(10))[0]  # platelets last 5 days

    assert client.post("/api/units/expire-sweep").json() == {"expired": 1}
    assert client.get(f"/api/units/{old['id']}").json()["status"] == "EXPIRED"
    assert client.get(f"/api/units/{fresh['id']}").json()["status"] == "AVAILABLE"
    assert db_session.get(BloodUnit, old["id"]).status == "EXPIRED"


def test_list_units_expiring_within(client, stock, days_ago):
    stock("A-", component="PLATELETS", collected_on=days_ago(3))  # expires in 2 days
    stock("A-", component="PLASMA")  # expires in a year
    expiring = client.get("/api/units", params={"expiring_within_days": 7}).json()
    assert [u["component"] for u in expiring] == ["PLATELETS"]

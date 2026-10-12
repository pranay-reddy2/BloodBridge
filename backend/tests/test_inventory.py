import pytest

from app.services.compatibility import compatible_donor_groups


@pytest.mark.parametrize(
    ("recipient", "component", "expected"),
    [
        ("O-", "RED_CELLS", ["O-"]),
        ("AB+", "RED_CELLS", ["AB+", "AB-", "A+", "A-", "B+", "B-", "O+", "O-"]),
        ("B+", "WHOLE_BLOOD", ["B+", "B-", "O+", "O-"]),
        ("AB-", "PLASMA", ["AB-", "AB+"]),
        ("O+", "PLASMA", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"]),
        ("A+", "PLATELETS", ["A+", "A-", "AB+", "AB-"]),
    ],
)
def test_compatibility_matrix(recipient, component, expected):
    assert compatible_donor_groups(recipient, component) == expected


def test_universal_red_cell_donor_appears_last_for_every_recipient():
    for recipient in ("O+", "A+", "A-", "B+", "B-", "AB+", "AB-"):
        assert compatible_donor_groups(recipient, "RED_CELLS")[-1] == "O-"


def test_inventory_summary(client, stock, make_donor, days_ago):
    stock("O-", 2)
    stock("A+", 1, component="PLATELETS", collected_on=days_ago(2))  # expiring soon
    stock("B+", 1, component="PLATELETS", collected_on=days_ago(9))  # already expired -> not counted
    client.post(
        "/api/requests",
        json={"hospital": "Ruby Hall", "patient_ref": "P-9", "blood_group": "O-", "units_needed": 1, "urgency": "CRITICAL"},
    )

    summary = client.get("/api/inventory/summary").json()
    by_group = {g["blood_group"]: g for g in summary["by_blood_group"]}

    assert summary["available_units"] == 3
    assert summary["expiring_soon"] == 1
    assert summary["critical_requests"] == 1
    assert summary["pending_requests"] == 1
    assert summary["total_donors"] == 4
    assert by_group["O-"]["available"] == 2
    assert by_group["B+"]["available"] == 0
    assert by_group["B+"]["low_stock"] is True
    assert summary["by_component"]["PLATELETS"] == 1


def test_compatibility_endpoint_counts_usable_units(client, stock):
    stock("O-", 2)
    stock("A-", 1)
    stock("B+", 4)
    body = client.get("/api/compatibility", params={"blood_group": "A+", "component": "RED_CELLS"}).json()
    assert body["compatible_donor_groups"] == ["A+", "A-", "O+", "O-"]
    assert body["available_units"] == 3

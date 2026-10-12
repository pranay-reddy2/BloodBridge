def test_health_is_up(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_ready_checks_database(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "READY", "database": "UP"}


def test_meta_reports_service_and_environment(client):
    body = client.get("/api/meta").json()
    assert body["service"] == "BloodBridge API"
    assert body["environment"] == "test"


def test_metrics_exposes_http_and_domain_metrics(client, stock):
    stock("A+", 2)
    client.get("/api/donors")

    text = client.get("/metrics").text
    assert "http_requests_total" in text
    assert 'bloodbridge_donations_total{blood_group="A+",component="RED_CELLS"}' in text
    assert 'bloodbridge_inventory_available_units{blood_group="A+"} 2.0' in text
    assert 'bloodbridge_inventory_available_units{blood_group="O-"} 0.0' in text

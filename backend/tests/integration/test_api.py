def test_health_check_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_latest_sensors_endpoint(client):
    response = client.get("/api/v1/sensors/latest")
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert "raw" in res["data"]


def test_digital_twin_state_endpoint(client):
    response = client.get("/api/v1/digital-twin/state")
    assert response.status_code == 200
    res = response.json()
    assert res["data"]["synchronization_state"] is not None


def test_predictions_anomaly_endpoint(client):
    response = client.get("/api/v1/predictions/anomaly")
    assert response.status_code == 200
    res = response.json()
    assert "anomaly_score" in res["data"]


def test_trigger_backwash_control(client):
    response = client.post("/api/v1/control/backwash", json={"mode": "manual", "duration_seconds": 15})
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True

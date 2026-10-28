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


def test_ingest_telemetry_endpoint(client):
    payload = {
        "device_id": "esp32_001",
        "pressure_inlet": 2.65,
        "pressure_outlet": 1.90,
        "flow": 74.5,
        "current": 3.42
    }
    response = client.post("/api/v1/sensors/telemetry", json=payload)
    assert response.status_code == 201
    res = response.json()
    assert res["success"] is True
    assert res["data"]["clogging_index"] is not None
    assert res["data"]["readings"]["pressure_inlet"] == 2.65

    # Verify latest endpoint reflects this ingested telemetry
    latest = client.get("/api/v1/sensors/latest").json()
    assert latest["data"]["raw"]["pressure_inlet"] == 2.65
    assert latest["data"]["has_live_data"] is True


def test_ingest_single_reading_endpoint(client):
    payload = {
        "device_id": "esp32_001",
        "sensor_id": "flow",
        "value": 72.0,
        "unit": "L/min"
    }
    response = client.post("/api/v1/sensors/reading", json=payload)
    assert response.status_code == 201
    assert response.json()["success"] is True


def test_sensor_dynamic_statistics_endpoint(client):
    response = client.get("/api/v1/sensors/flow/statistics?minutes=30")
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert "mean" in res["data"]
    assert "std_dev" in res["data"]


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
    assert res["data"]["log"]["maintenance_type"] == "backwash"

    # Verify maintenance logs contain the new record
    maint_res = client.get("/api/v1/maintenance/logs").json()
    assert len(maint_res["data"]) >= 1

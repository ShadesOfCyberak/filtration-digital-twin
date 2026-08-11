import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_telemetry():
    return {
        "pressure_inlet": 2.5,
        "pressure_outlet": 1.9,
        "pressure_drop": 0.6,
        "flow_rate": 76.0,
        "pump_current": 3.3,
        "pump_power": 79.2,
        "clogging_index": 115.0,
        "flow_efficiency": 95.0,
        "specific_power_consumption": 0.017
    }

import pytest
from app.services.digital_twin_service import digital_twin_service
from app.services.data_processing_service import data_processor


def test_pressure_drop_calculation():
    dp = data_processor.calculate_pressure_drop(2.5, 1.8)
    assert pytest.approx(dp, 0.01) == 0.7


def test_clogging_index_calculation():
    ci = data_processor.calculate_clogging_index(0.6, 60.0)
    # (0.6 / 0.3) * (80 / 60) * 100 = 2 * 1.333 * 100 = 266.67
    assert ci > 250.0


def test_digital_twin_physics_model(sample_telemetry):
    twin_state = digital_twin_service.evaluate_twin_state(sample_telemetry)
    assert twin_state.twin_id == "filtration_system_001"
    assert twin_state.expected_pressure_drop > 0
    assert twin_state.expected_flow_rate > 0
    assert twin_state.synchronization_state in ["SYNCHRONIZED", "MINOR_DEVIATION", "MAJOR_DEVIATION", "CRITICAL_DIVERGENCE"]

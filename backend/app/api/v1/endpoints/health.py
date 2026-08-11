from fastapi import APIRouter
from app.schemas.responses import APIResponse
from app.services.mqtt_service import mqtt_service
from app.services.data_processing_service import data_processor
from app.services.digital_twin_service import digital_twin_service
from app.services.health_monitoring_service import health_service

router = APIRouter(prefix="/health", tags=["Health Monitoring"])


@router.get("/overall", response_model=APIResponse)
async def get_overall_health():
    """Get system health scores (Filter, Pump, Sensors, Overall Maintenance Urgency)"""
    processed = data_processor.process_telemetry_frame(mqtt_service.latest_raw_telemetry)
    twin_state = digital_twin_service.evaluate_twin_state(processed)
    summary = health_service.evaluate_system_health(processed, twin_state)
    
    return APIResponse(
        success=True,
        message="System health evaluation completed",
        data=summary.dict()
    )


@router.get("/filter", response_model=APIResponse)
async def get_filter_health():
    """Detailed filter component health assessment"""
    processed = data_processor.process_telemetry_frame(mqtt_service.latest_raw_telemetry)
    metrics = health_service.calculate_filter_health(
        processed["clogging_index"],
        processed["pressure_drop"],
        processed["flow_efficiency"]
    )
    return APIResponse(success=True, message="Filter health metrics", data=metrics)


@router.get("/pump", response_model=APIResponse)
async def get_pump_health():
    """Detailed pump component health assessment"""
    processed = data_processor.process_telemetry_frame(mqtt_service.latest_raw_telemetry)
    twin_state = digital_twin_service.evaluate_twin_state(processed)
    metrics = health_service.calculate_pump_health(
        processed["pump_power"],
        twin_state.expected_pump_power,
        processed["flow_rate"]
    )
    return APIResponse(success=True, message="Pump health metrics", data=metrics)

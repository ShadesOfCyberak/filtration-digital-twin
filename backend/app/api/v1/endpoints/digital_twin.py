from fastapi import APIRouter
from app.schemas.responses import APIResponse
from app.services.mqtt_service import mqtt_service
from app.services.data_processing_service import data_processor
from app.services.digital_twin_service import digital_twin_service

router = APIRouter(prefix="/digital-twin", tags=["Digital Twin Service"])


@router.get("/state", response_model=APIResponse)
async def get_digital_twin_state():
    """Get live physical state vs virtual expected model state & residuals"""
    processed = data_processor.process_telemetry_frame(mqtt_service.latest_raw_telemetry)
    twin_state = digital_twin_service.evaluate_twin_state(processed)
    
    return APIResponse(
        success=True,
        message="Digital Twin state evaluated",
        data=twin_state.dict()
    )


@router.get("/residuals", response_model=APIResponse)
async def get_twin_residuals():
    """Get pressure, flow, and power residuals & deviation percentages"""
    processed = data_processor.process_telemetry_frame(mqtt_service.latest_raw_telemetry)
    twin_state = digital_twin_service.evaluate_twin_state(processed)
    
    return APIResponse(
        success=True,
        message="Model residuals computed",
        data={
            "pressure_residual": twin_state.pressure_residual,
            "flow_residual": twin_state.flow_residual,
            "power_residual": twin_state.power_residual,
            "pressure_deviation_pct": twin_state.pressure_deviation_pct,
            "flow_deviation_pct": twin_state.flow_deviation_pct,
            "power_deviation_pct": twin_state.power_deviation_pct,
            "synchronization_state": twin_state.synchronization_state
        }
    )

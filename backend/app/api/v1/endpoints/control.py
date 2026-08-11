from fastapi import APIRouter, HTTPException
from app.schemas.requests import BackwashTriggerRequest
from app.schemas.responses import APIResponse
from app.services.mqtt_service import mqtt_service
from app.services.digital_twin_service import digital_twin_service

router = APIRouter(prefix="/control", tags=["Control Commands"])


@router.post("/backwash", response_model=APIResponse)
async def trigger_backwash(request: BackwashTriggerRequest):
    """Trigger manual or automated backwash control pulse"""
    success = mqtt_service.publish_control_command(
        command="backwash",
        parameters={
            "mode": request.mode,
            "duration_seconds": request.duration_seconds,
            "operator": request.operator_id
        }
    )
    if success:
        digital_twin_service.trigger_backwash_reset()
        return APIResponse(
            success=True,
            message=f"Backwash sequence initiated successfully (duration={request.duration_seconds}s)",
            data={"status": "running", "duration": request.duration_seconds}
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to publish backwash MQTT command")


@router.post("/reset", response_model=APIResponse)
async def reset_twin_state():
    """Reset digital twin state parameters"""
    digital_twin_service.trigger_backwash_reset()
    return APIResponse(
        success=True,
        message="Digital Twin state parameters reset",
        data={"status": "reset_completed"}
    )

import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.schemas.requests import BackwashTriggerRequest
from app.schemas.responses import APIResponse
from app.services.mqtt_service import mqtt_service
from app.services.digital_twin_service import digital_twin_service
from app.services.data_processing_service import data_processor
from app.repositories.influxdb_repository import influx_repo

router = APIRouter(prefix="/control", tags=["Control Commands"])


@router.post("/backwash", response_model=APIResponse)
async def trigger_backwash(request: BackwashTriggerRequest):
    """Trigger manual or automated backwash control pulse"""
    # Capture dynamic pre-backwash clogging index
    processed = data_processor.process_telemetry_frame(mqtt_service.latest_raw_telemetry)
    pre_ci = processed.get("clogging_index", 100.0)

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
        
        # Dynamically record maintenance log
        log_entry = {
            "id": f"maint-{str(uuid.uuid4())[:8]}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "maintenance_type": "backwash",
            "performed_by": request.operator_id or "system",
            "duration_minutes": round(request.duration_seconds / 60.0, 2),
            "success": True,
            "description": f"Executed {request.mode} backwash cycle for {request.duration_seconds}s",
            "pre_backwash_clogging_index": round(pre_ci, 2),
            "post_backwash_clogging_index": 100.0
        }
        await influx_repo.write_maintenance_log(log_entry)

        return APIResponse(
            success=True,
            message=f"Backwash sequence initiated successfully (duration={request.duration_seconds}s)",
            data={"status": "running", "duration": request.duration_seconds, "log": log_entry}
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

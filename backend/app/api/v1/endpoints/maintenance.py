import uuid
from fastapi import APIRouter, status
from typing import List, Optional
from datetime import datetime
from app.schemas.responses import APIResponse
from app.models.maintenance import MaintenanceLog
from app.repositories.influxdb_repository import influx_repo

router = APIRouter(prefix="/maintenance", tags=["Maintenance & Service Logs"])


@router.get("/logs", response_model=APIResponse)
async def get_maintenance_logs():
    """Get history of dynamic maintenance and backwash operations"""
    logs = await influx_repo.get_maintenance_logs()
    return APIResponse(
        success=True,
        message=f"Retrieved {len(logs)} dynamic maintenance log(s)",
        data=logs
    )


@router.post("/logs", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def record_maintenance_log(log: MaintenanceLog):
    """Record a dynamic maintenance intervention log"""
    log_dict = log.dict()
    if not log_dict.get("id"):
        log_dict["id"] = f"maint-{str(uuid.uuid4())[:8]}"
    if not log_dict.get("timestamp"):
        log_dict["timestamp"] = datetime.utcnow().isoformat() + "Z"
    elif isinstance(log_dict["timestamp"], datetime):
        log_dict["timestamp"] = log_dict["timestamp"].isoformat() + "Z"

    await influx_repo.write_maintenance_log(log_dict)
    return APIResponse(
        success=True,
        message="Dynamic maintenance action logged successfully",
        data=log_dict
    )

from fastapi import APIRouter
from typing import List
from datetime import datetime
from app.schemas.responses import APIResponse
from app.models.maintenance import MaintenanceLog

router = APIRouter(prefix="/maintenance", tags=["Maintenance & Service Logs"])

# In-memory maintenance log history
sample_logs: List[MaintenanceLog] = [
    MaintenanceLog(
        id="maint-001",
        timestamp=datetime.utcnow(),
        maintenance_type="backwash",
        performed_by="automatic",
        duration_minutes=0.5,
        success=True,
        description="Automated pressure differential backwash pulse completed",
        pre_backwash_clogging_index=195.0,
        post_backwash_clogging_index=105.0
    )
]


@router.get("/logs", response_model=APIResponse)
async def get_maintenance_logs():
    """Get history of maintenance and backwash operations"""
    return APIResponse(
        success=True,
        message="Maintenance logs retrieved",
        data=[log.dict() for log in sample_logs]
    )

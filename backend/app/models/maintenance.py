from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MaintenanceLog(BaseModel):
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    maintenance_type: str = Field(..., description="backwash | manual_cleaning | filter_replacement | calibration")
    performed_by: str = Field(default="automatic", description="automatic | operator_id")
    duration_minutes: float
    success: bool = True
    description: Optional[str] = None
    pre_backwash_clogging_index: Optional[float] = None
    post_backwash_clogging_index: Optional[float] = None

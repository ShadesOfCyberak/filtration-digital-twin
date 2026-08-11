from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class BackwashTriggerRequest(BaseModel):
    mode: str = Field(default="auto", description="auto | manual")
    duration_seconds: int = Field(default=30, ge=5, le=300)
    operator_id: Optional[str] = "system"


class ModelCalibrationRequest(BaseModel):
    filter_area: Optional[float] = None
    clean_medium_resistance: Optional[float] = None
    reset_volume: bool = False


class HistoricalQueryRequest(BaseModel):
    sensor_id: str
    start_time: str
    end_time: str
    interval: Optional[str] = "1m"

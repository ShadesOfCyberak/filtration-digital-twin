from datetime import datetime
from typing import Dict
from pydantic import BaseModel, Field


class SensorHealth(BaseModel):
    sensor_id: str
    health_score: float = Field(..., ge=0, le=100)
    status: str = "good"  # good, warning, critical
    message_delivery_rate: float = 100.0


class SystemHealthSummary(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    overall_health_score: float = Field(..., ge=0, le=100)
    status: str = "healthy"  # healthy, degraded, critical
    
    filter_health_score: float = Field(..., ge=0, le=100)
    clogging_index: float
    pressure_health_score: float
    flow_health_score: float
    efficiency_health_score: float
    
    pump_health_score: float = Field(..., ge=0, le=100)
    power_consumption_score: float
    pump_performance_score: float
    
    sensors: Dict[str, SensorHealth]
    
    maintenance_score: float = Field(..., ge=0, le=100, description="Higher score means urgent maintenance needed")
    maintenance_urgency: str
    recommended_action: str
    estimated_time_to_backwash_hours: float

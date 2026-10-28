from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class TelemetryIngestRequest(BaseModel):
    device_id: Optional[str] = Field(default="esp32_001", description="Device hardware identifier")
    pressure_inlet: float = Field(..., description="Inlet pressure in bar")
    pressure_outlet: float = Field(..., description="Outlet pressure in bar")
    flow: float = Field(..., description="Flow rate in L/min")
    current: float = Field(..., description="Pump current in Amperes")
    timestamp: Optional[str] = Field(default=None, description="ISO-8601 timestamp string")


class SensorReadingIngestRequest(BaseModel):
    device_id: Optional[str] = Field(default="esp32_001", description="Device hardware identifier")
    sensor_id: str = Field(..., description="Sensor metric identifier: pressure_inlet, pressure_outlet, flow, current")
    value: float = Field(..., description="Measured sensor value")
    unit: Optional[str] = Field(default="bar", description="Engineering unit")
    quality: Optional[str] = Field(default="good", description="Measurement signal quality")
    timestamp: Optional[str] = Field(default=None, description="ISO-8601 timestamp string")


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

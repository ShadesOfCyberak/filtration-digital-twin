from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field


class RawSensorPayload(BaseModel):
    device_id: str = Field(..., example="esp32_001")
    sensor_id: str = Field(..., example="pressure_inlet")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    value: float = Field(..., example=2.45)
    unit: str = Field(default="bar", example="bar")
    quality: str = Field(default="good", example="good")


class ProcessedSensorMetrics(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    pressure_inlet: float = Field(..., description="Inlet Pressure in bar")
    pressure_outlet: float = Field(..., description="Outlet Pressure in bar")
    pressure_drop: float = Field(..., description="Delta P (Pin - Pout) in bar")
    flow_rate: float = Field(..., description="Flow rate in L/min")
    pump_current: float = Field(..., description="Pump current in Amperes")
    pump_power: float = Field(..., description="Pump power consumption in Watts")
    clogging_index: float = Field(..., description="Empirical filter clogging index")
    flow_efficiency: float = Field(..., description="Flow efficiency percentage")
    specific_power_consumption: float = Field(..., description="SPC in W*h/L")


class SensorReading(BaseModel):
    value: float
    unit: str
    quality: str = "good"


class MultiSensorSnapshot(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sensors: Dict[str, SensorReading]

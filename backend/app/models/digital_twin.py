from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class TwinState(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    twin_id: str = "filtration_system_001"
    
    # Actual Sensor Readings
    actual_pressure_inlet: float
    actual_pressure_outlet: float
    actual_pressure_drop: float
    actual_flow_rate: float
    actual_pump_power: float
    
    # Physics Model Expected Metrics
    expected_pressure_drop: float
    expected_flow_rate: float
    expected_pump_power: float
    
    # Model Residuals (Actual - Expected)
    pressure_residual: float
    flow_residual: float
    power_residual: float
    
    # Deviations (%)
    pressure_deviation_pct: float
    flow_deviation_pct: float
    power_deviation_pct: float
    
    # Internal Physical State Attributes
    accumulated_volume_liters: float
    estimated_cake_resistance: float
    estimated_filter_resistance: float
    time_since_last_backwash_sec: float
    
    # Twin Synchronization Status
    synchronization_state: str = Field(
        default="SYNCHRONIZED",
        description="SYNCHRONIZED | MINOR_DEVIATION | MAJOR_DEVIATION | CRITICAL_DIVERGENCE"
    )
    is_model_calibrated: bool = True

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AlertItem(BaseModel):
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    severity: str = Field(..., description="info | warning | critical")
    alert_type: str = Field(..., description="clogging | pressure_high | flow_low | divergence | anomaly")
    message: str
    trigger_value: float
    threshold_value: float
    recommended_action: str
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None

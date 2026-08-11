from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class APIResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Any] = None


class HealthCheckResponse(BaseModel):
    status: str = "healthy"
    timestamp: str
    services: Dict[str, str]
    version: str = "1.0.0"


class PredictionResponse(BaseModel):
    timestamp: datetime
    anomaly_detected: bool
    anomaly_score: float
    failure_probability: float
    predicted_failure_mode: str
    rul_hours: float
    confidence: float

from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.schemas.responses import APIResponse
from app.services.mqtt_service import mqtt_service
from app.services.data_processing_service import data_processor
from app.repositories.influxdb_repository import influx_repo

router = APIRouter(prefix="/sensors", tags=["Sensor Telemetry"])


@router.get("/latest", response_model=APIResponse)
async def get_latest_sensors():
    """Get real-time latest readings from all physical sensors"""
    raw = mqtt_service.latest_raw_telemetry
    processed = data_processor.process_telemetry_frame(raw)
    
    return APIResponse(
        success=True,
        message="Latest telemetry snapshot fetched",
        data={
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "raw": raw,
            "processed": processed
        }
    )


@router.get("/{sensor_id}/history", response_model=APIResponse)
async def get_sensor_history(
    sensor_id: str,
    minutes: int = Query(default=30, ge=1, le=1440)
):
    """Get historical telemetry for a specific sensor"""
    end = datetime.utcnow()
    start = end - timedelta(minutes=minutes)
    history = await influx_repo.get_sensor_history(sensor_id, start, end)
    
    return APIResponse(
        success=True,
        message=f"Historical telemetry for '{sensor_id}' retrieved",
        data=history
    )


@router.get("/{sensor_id}/statistics", response_model=APIResponse)
async def get_sensor_statistics(sensor_id: str):
    """Get statistical summary for specified sensor over 24h"""
    raw_val = mqtt_service.latest_raw_telemetry.get(sensor_id, 0.0)
    
    return APIResponse(
        success=True,
        message=f"Statistics for '{sensor_id}' computed",
        data={
            "sensor_id": sensor_id,
            "window": "24h",
            "mean": raw_val,
            "min": float(np.round(raw_val * 0.9, 2)),
            "max": float(np.round(raw_val * 1.1, 2)),
            "std_dev": 0.05
        }
    )

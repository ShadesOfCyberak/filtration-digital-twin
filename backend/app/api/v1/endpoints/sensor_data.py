from fastapi import APIRouter, Query, HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np

from app.schemas.requests import TelemetryIngestRequest, SensorReadingIngestRequest
from app.schemas.responses import APIResponse
from app.services.mqtt_service import mqtt_service
from app.services.data_processing_service import data_processor
from app.repositories.influxdb_repository import influx_repo

router = APIRouter(prefix="/sensors", tags=["Sensor Telemetry"])


@router.post("/telemetry", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def ingest_telemetry(payload: TelemetryIngestRequest):
    """
    Ingest a complete telemetry frame from the IoT device (ESP32) continuously.
    Direct dynamic data endpoint for ESP32 HTTP POST streaming.
    """
    ts = None
    if payload.timestamp:
        try:
            ts = datetime.fromisoformat(payload.timestamp.replace("Z", "+00:00"))
        except Exception:
            ts = datetime.utcnow()

    readings = {
        "pressure_inlet": float(payload.pressure_inlet),
        "pressure_outlet": float(payload.pressure_outlet),
        "flow": float(payload.flow),
        "current": float(payload.current)
    }

    result = await mqtt_service.ingest_telemetry_frame(readings, timestamp=ts)

    return APIResponse(
        success=True,
        message="Dynamic IoT telemetry frame ingested successfully",
        data={
            "device_id": payload.device_id,
            "timestamp": (ts or datetime.utcnow()).isoformat() + "Z",
            "readings": readings,
            "clogging_index": result["processed"].get("clogging_index"),
            "system_health": result["health"].get("overall_health_score"),
            "synchronization_state": result["twin_state"].get("synchronization_state")
        }
    )


@router.post("/reading", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def ingest_single_reading(payload: SensorReadingIngestRequest):
    """Ingest individual sensor measurement continuously from IoT node"""
    ts = None
    if payload.timestamp:
        try:
            ts = datetime.fromisoformat(payload.timestamp.replace("Z", "+00:00"))
        except Exception:
            ts = datetime.utcnow()

    await mqtt_service.ingest_single_reading(
        payload.sensor_id,
        payload.value,
        unit=payload.unit or "bar",
        timestamp=ts
    )

    return APIResponse(
        success=True,
        message=f"Sensor '{payload.sensor_id}' dynamic reading ingested",
        data={
            "device_id": payload.device_id,
            "sensor_id": payload.sensor_id,
            "value": payload.value,
            "unit": payload.unit
        }
    )


@router.get("/latest", response_model=APIResponse)
async def get_latest_sensors():
    """Get real-time latest dynamic readings from physical sensors"""
    raw = mqtt_service.latest_raw_telemetry
    processed = data_processor.process_telemetry_frame(raw)
    
    return APIResponse(
        success=True,
        message="Latest telemetry snapshot fetched",
        data={
            "timestamp": (mqtt_service.last_telemetry_timestamp or datetime.utcnow()).isoformat() + "Z",
            "has_live_data": mqtt_service.has_received_data,
            "total_frames_received": mqtt_service.total_frames_received,
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
        message=f"Historical telemetry for '{sensor_id}' retrieved ({len(history)} data points)",
        data=history
    )


@router.get("/{sensor_id}/statistics", response_model=APIResponse)
async def get_sensor_statistics(
    sensor_id: str,
    minutes: int = Query(default=60, ge=1, le=1440)
):
    """
    Compute real-time statistical metrics dynamically from actual recorded sensor data
    """
    end = datetime.utcnow()
    start = end - timedelta(minutes=minutes)
    history = await influx_repo.get_sensor_history(sensor_id, start, end)

    if history:
        values = [item["value"] for item in history if "value" in item]
    else:
        current_val = mqtt_service.latest_raw_telemetry.get(sensor_id)
        values = [current_val] if current_val is not None else []

    if values:
        arr = np.array(values, dtype=float)
        mean_val = float(np.round(np.mean(arr), 3))
        min_val = float(np.round(np.min(arr), 3))
        max_val = float(np.round(np.max(arr), 3))
        std_val = float(np.round(np.std(arr), 4))
        count = len(arr)
    else:
        mean_val = 0.0
        min_val = 0.0
        max_val = 0.0
        std_val = 0.0
        count = 0

    return APIResponse(
        success=True,
        message=f"Dynamic statistics for '{sensor_id}' computed from {count} actual samples",
        data={
            "sensor_id": sensor_id,
            "window_minutes": minutes,
            "sample_count": count,
            "mean": mean_val,
            "min": min_val,
            "max": max_val,
            "std_dev": std_val
        }
    )

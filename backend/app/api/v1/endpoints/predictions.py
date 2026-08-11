from fastapi import APIRouter
from app.schemas.responses import APIResponse, PredictionResponse
from app.services.mqtt_service import mqtt_service
from app.services.data_processing_service import data_processor
from app.services.ml_service import ml_service

router = APIRouter(prefix="/predictions", tags=["ML Machine Learning Predictions"])


@router.get("/anomaly", response_model=APIResponse)
async def get_anomaly_score():
    """Get Isolation Forest anomaly score & detection flag"""
    processed = data_processor.process_telemetry_frame(mqtt_service.latest_raw_telemetry)
    pred: PredictionResponse = ml_service.predict(processed)
    
    return APIResponse(
        success=True,
        message="Anomaly score calculated",
        data={
            "anomaly_detected": pred.anomaly_detected,
            "anomaly_score": pred.anomaly_score,
            "confidence": pred.confidence
        }
    )


@router.get("/rul", response_model=APIResponse)
async def get_rul_estimate():
    """Get Remaining Useful Life (RUL) estimate in operating hours"""
    processed = data_processor.process_telemetry_frame(mqtt_service.latest_raw_telemetry)
    pred: PredictionResponse = ml_service.predict(processed)
    
    return APIResponse(
        success=True,
        message="RUL estimation completed",
        data={
            "rul_hours": pred.rul_hours,
            "failure_probability": pred.failure_probability,
            "predicted_failure_mode": pred.predicted_failure_mode
        }
    )


@router.get("/full-assessment", response_model=APIResponse)
async def get_full_ml_assessment():
    """Comprehensive ML Assessment (Anomaly score, Failure Mode Classifier, RUL)"""
    processed = data_processor.process_telemetry_frame(mqtt_service.latest_raw_telemetry)
    pred: PredictionResponse = ml_service.predict(processed)
    return APIResponse(success=True, message="Full ML assessment", data=pred.dict())

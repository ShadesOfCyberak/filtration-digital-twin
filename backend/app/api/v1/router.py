from fastapi import APIRouter
from app.api.v1.endpoints import (
    sensor_data,
    health,
    digital_twin,
    predictions,
    maintenance,
    control
)

api_router = APIRouter()

api_router.include_router(sensor_data.router)
api_router.include_router(health.router)
api_router.include_router(digital_twin.router)
api_router.include_router(predictions.router)
api_router.include_router(maintenance.router)
api_router.include_router(control.router)

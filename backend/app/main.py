from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger
from app.api.v1.router import api_router
from app.repositories.influxdb_repository import influx_repo
from app.services.mqtt_service import mqtt_service
from app.schemas.responses import HealthCheckResponse, APIResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    logger.info("Initializing Filtration Digital Twin Backend Services...")
    await influx_repo.connect()
    mqtt_service.start()
    
    yield
    
    # Shutdown tasks
    logger.info("Shutting down Digital Twin Backend Services...")
    mqtt_service.stop()
    await influx_repo.close()


app = FastAPI(
    title=settings.api.title,
    description=settings.api.description,
    version=settings.api.version,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS Configuration
origins = settings.api.cors_origins
if isinstance(origins, str):
    origins = [origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds() * 1000.0
    response.headers["X-Process-Time-MS"] = f"{process_time:.2f}"
    return response


@app.get("/health", response_model=HealthCheckResponse, tags=["Health Check"])
async def health_check():
    """System diagnostic health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat() + "Z",
        services={
            "database": "connected" if influx_repo._connected else "simulated_memory",
            "mqtt_broker": "connected" if mqtt_service.is_connected else "simulated_stream",
            "digital_twin_engine": "running",
            "ml_inference_service": "loaded"
        },
        version=settings.api.version
    )


# Include API v1 routes
app.include_router(api_router, prefix=settings.api.api_v1_prefix)

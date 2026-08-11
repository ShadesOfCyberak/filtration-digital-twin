# API Request & Response Examples (cURL & Postman)

### 1. System Health Check
```bash
curl -X GET "http://localhost:8000/health"
```
**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-08-07T12:00:00Z",
  "services": {
    "database": "simulated_memory",
    "mqtt_broker": "simulated_stream",
    "digital_twin_engine": "running",
    "ml_inference_service": "loaded"
  },
  "version": "1.0.0"
}
```

### 2. Fetch Latest Telemetry
```bash
curl -X GET "http://localhost:8000/api/v1/sensors/latest"
```

### 3. Fetch Digital Twin Live State
```bash
curl -X GET "http://localhost:8000/api/v1/digital-twin/state"
```

### 4. Fetch Machine Health Metrics
```bash
curl -X GET "http://localhost:8000/api/v1/health/overall"
```

### 5. Fetch ML Anomaly & RUL Predictions
```bash
curl -X GET "http://localhost:8000/api/v1/predictions/full-assessment"
```

### 6. Trigger Manual Backwash Command
```bash
curl -X POST "http://localhost:8000/api/v1/control/backwash" \
     -H "Content-Type: application/json" \
     -d '{"mode": "manual", "duration_seconds": 30, "operator_id": "op_001"}'
```

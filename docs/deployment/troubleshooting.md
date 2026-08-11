# Deployment Troubleshooting Guide

| Issue / Symptom | Possible Cause | Resolution |
| :--- | :--- | :--- |
| Backend logs `MQTT connection failed` | Mosquitto container not running or port 1883 blocked | Backend automatically launches internal simulator. Verify Mosquitto with `docker-compose ps` |
| InfluxDB connection error | InfluxDB service starting up or bad admin token | Backend falls back gracefully to in-memory time-series store. Check `.env` for `INFLUXDB_TOKEN` |
| Dashboard charts not refreshing | CORS issue or network disconnect | Ensure `VITE_API_BASE_URL` in `frontend/.env` matches `http://localhost:8000/api/v1` |
| Digital Twin state shows `CRITICAL_DIVERGENCE` | Sensor drift or abnormal clogging | Execute backwash via control panel `/api/v1/control/backwash` to reset physics state |

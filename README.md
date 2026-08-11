# IoT-Enabled Digital Twin Framework for Machine Health Monitoring & Failure Prediction

![Phase 1 Milestone](https://img.shields.io/badge/Milestone-60%25%20Phase%201-cyan)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)
![React](https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-61DAFB)
![InfluxDB](https://img.shields.io/badge/Database-InfluxDB%202.x-22ADF6)
![MQTT](https://img.shields.io/badge/IoT-Mosquitto%20MQTT-3C873A)

An industrial-grade IoT-Enabled Digital Twin platform designed to monitor physical liquid filtration systems, mirror operational states using physics-based modeling (Darcy's Law & filter resistance curves), evaluate machine health scores in real time, detect anomalies, predict Remaining Useful Life (RUL), and visualize system behavior through an interactive industrial web dashboard.

---

## Key Capabilities (Phase 1 - 60% Milestone)

1. **IoT Telemetry Pipeline**: MQTT subscriber engine (`paho-mqtt`) ingesting inlet pressure, outlet pressure, flow rate, and pump current with noise filtering (Moving Average, Median, EMA) and outlier removal (Z-Score & IQR).
2. **First-Principles Physics Digital Twin Engine**: Real-time evaluation of expected pressure drop ($\Delta P$), expected flow rate, pump curve matching, residual computation, and synchronization tracking (`SYNCHRONIZED`, `MINOR_DEVIATION`, `MAJOR_DEVIATION`, `CRITICAL_DIVERGENCE`).
3. **Machine Health Monitoring & Alerting**: Real-time component health scores (Filter, Pump, Sensors, Overall System), Clogging Index ($CI$), maintenance urgency scoring, and severity-graded alerts.
4. **Machine Learning Baseline**: Isolation Forest anomaly detection, failure mode classification, and Remaining Useful Life (RUL) regression predictions.
5. **Interactive Industrial Dashboard**: Futuristic glassmorphism web interface displaying live pressure/flow/power charts, twin residual convergence gauges, component health breakdown, live alert drawers, and backwash control actions.
6. **Containerized Infrastructure**: Docker Compose setup orchestrating Mosquitto MQTT Broker, InfluxDB 2.x, FastAPI Backend, and React Vite Frontend.

---

## System Architecture Overview

```
[ ESP32 IoT Node ] ---> MQTT (Mosquitto:1883) ---> [ FastAPI Backend Ingestion Service ]
                                                            |
                 +------------------------------------------+------------------------------------------+
                 |                                          |                                          |
      [ Data Processing ]                         [ Digital Twin Engine ]                    [ Health & Alert Engine ]
      - Noise Filters (EMA/MA)                    - Darcy's Law Porous Media                 - Filter/Pump Scores
      - Feature Extraction                        - Pump Characteristic Curve                - Clogging Index (CI)
      - Outlier Filtering                         - Residual Calculation                     - Threshold & Warnings
                 |                                          |                                          |
                 +------------------------------------------+------------------------------------------+
                                                            |
                                             [ InfluxDB 2.x Repository ]
                                                            |
                                        [ Async REST API / Web Dashboard ]
```

---

## Quick Start (Local Setup)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/filtration-digital-twin.git
cd filtration-digital-twin

# Create root environment file
cp .env.docker.example .env

# Launch services via Docker Compose
docker-compose up --build -d

# Verify services status
docker-compose ps
```

- **Dashboard UI**: [http://localhost:3000](http://localhost:3000)
- **FastAPI API Docs**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **Mosquitto MQTT**: `localhost:1883` (WebSockets: `localhost:9001`)
- **InfluxDB UI**: [http://localhost:8086](http://localhost:8086)

---

### Option 2: Local Python & Frontend Development

```bash
# 1. Setup Backend
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

# Run FastAPI Server (auto-falls back to simulated database/MQTT if external services aren't running)
uvicorn app.main:app --reload --port 8000

# 2. Seed Simulated Telemetry & Run ML Baseline
python scripts/seed_data.py

# 3. Setup Frontend
cd ../frontend
npm install
cp .env.example .env
npm run dev
```

---

## Project Folder Structure

```
filtration-digital-twin/
├── backend/                  # FastAPI Application Core
│   ├── app/
│   │   ├── api/              # REST Endpoints (v1) & Router
│   │   ├── core/             # Configuration, Logging, Security
│   │   ├── models/           # Pydantic Schemas & Data Classes
│   │   ├── repositories/     # InfluxDB Data Access Layer
│   │   ├── services/         # Twin Engine, Health, Alert, MQTT Services
│   │   └── utils/            # Physics Calculators & Utilities
│   ├── scripts/              # Data Seeding & Health Check Scripts
│   └── tests/                # Pytest Unit & Integration Test Suite
├── ml/                       # Machine Learning Baseline
│   ├── models/               # Saved Model Artifacts (.pkl)
│   └── src/                  # Synthetic Data Gen, Training, Inference
├── frontend/                 # React 18 + TypeScript + Vite Dashboard
│   ├── src/
│   │   ├── components/       # Telemetry Charts, Twin View, Health Panel
│   │   ├── hooks/            # Live Data Polling Hooks
│   │   ├── store/            # Redux Toolkit Slices (Sensors, Health, Alerts)
│   │   └── services/         # Axios API Client Layer
├── iot-firmware/             # ESP32 Sensor Node Arduino Firmware
├── database/                 # InfluxDB Initialization Flux Scripts
├── deployment/               # Dockerfiles, Mosquitto & Nginx Configs
└── docs/                     # System Architecture & API Docs
```

---

## Verification & Testing

- **Backend Unit & Integration Tests**: `pytest backend/tests`
- **ML Training Pipeline**: `python ml/src/training/train_all.py`
- **Frontend Typecheck & Build**: `cd frontend && npm run build`

---

## License

MIT License - see [LICENSE](LICENSE) for details.

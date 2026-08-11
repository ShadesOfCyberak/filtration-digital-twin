# Developer Guide & Setup Procedure

This document provides developer guidelines for setting up, running, testing, and contributing to the **IoT-Enabled Digital Twin Framework for Machine Health Monitoring**.

---

## 1. Prerequisites

Ensure your workstation has the following installed:
- **Python**: v3.11 or higher
- **Node.js**: v18.x LTS or v20.x LTS (with `npm` v9+)
- **Docker Desktop**: v24.0+ (with `docker-compose` v2.20+)
- **Git**: v2.30+

---

## 2. Environment Configurations

The system relies on localized environment files for each service:

| File Location | Purpose |
| :--- | :--- |
| `.env.docker.example` | Template for root `docker-compose.yml` environment setup |
| `backend/.env.example` | Backend configuration (FastAPI, InfluxDB, MQTT, Security) |
| `frontend/.env.example` | Frontend environment variables (`VITE_API_BASE_URL`, etc.) |

To set up your local environment:
```bash
cp .env.docker.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

---

## 3. Running Services Individually

### 3.1 Backend (Python FastAPI)

```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
> **Note**: If InfluxDB or Mosquitto are not reachable, the backend will auto-initialize in **simulated fallback mode**, generating live synthetic physics telemetry in-memory for seamless local development.

### 3.2 Machine Learning Pipeline

```bash
cd ml
pip install -r requirements.txt

# Train baseline ML models (Isolation Forest, RUL Regressor)
python src/training/train_all.py
```

### 3.3 Frontend Dashboard (Vite + React + TS)

```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 4. Running via Docker Compose

To start the full stack including Mosquitto MQTT broker and InfluxDB:

```bash
# Start all containers
docker-compose up --build -d

# Check container status
docker-compose ps

# View backend logs
docker-compose logs -f backend
```

---

## 5. Simulating Telemetry Data

To simulate ESP32 MQTT sensor output publishing to Mosquitto:

```bash
# Launch telemetry simulator script
python backend/scripts/seed_data.py --mode stream --interval 1.0
```

This will publish synthetic sensor JSON packets to:
- `filtration/sensor/pressure/inlet`
- `filtration/sensor/pressure/outlet`
- `filtration/sensor/flow`
- `filtration/sensor/current`

---

## 6. Running Unit & Integration Tests

```bash
# Backend pytest suite
cd backend
pytest tests/ -v

# Frontend component tests
cd frontend
npm test
```

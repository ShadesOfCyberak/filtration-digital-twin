# System Architecture & Technical Design Specification

## Overview
The **IoT-Enabled Digital Twin Framework** is a hybrid physical-virtual platform designed for continuous machine health monitoring, fouling state estimation, and failure prediction on industrial liquid filtration systems.

## Data Ingestion & Processing Pipeline
1. **Physical Sensors**: Pressure transducers ($P_{in}, P_{out}$), Hall-effect flow meter ($Q$), and Current sensor ($I$).
2. **Microcontroller**: ESP32 reading analog/pulse signals and packaging JSON frames.
3. **MQTT Broker**: Eclipse Mosquitto broker running on port 1883.
4. **FastAPI Backend**: Asynchronous message consumption, noise filtering (Moving Average, Median, EMA), feature extraction ($\Delta P$, Clogging Index $CI$, Specific Power Consumption $SPC$).
5. **Physics Engine**: First-principles Darcy's law equations computing expected pressure drop ($\Delta P_{exp}$) based on exponential cake buildup resistance $R_{cake}(t) = R_{max}(1 - e^{-kt})$.
6. **Health & Alert Service**: Calculating real-time composite health metrics (0-100 score) and generating severity-graded alerts.
7. **Storage**: InfluxDB 2.x time-series database.
8. **Frontend**: React + TypeScript industrial glassmorphism dashboard.

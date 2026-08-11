# Industrial Dashboard Operational Guide

## Features Overview

1. **Header & Status Bar**: Displays system status (`HEALTHY` / `DEGRADED` / `CRITICAL`), connection status (Live MQTT Ingestion), and real-time auto-refresh toggle.
2. **Key Metric Tiles**: Real-time display for Pressure Drop ($\Delta P$), Flow Rate ($Q$), Pump Power ($P$), and Clogging Index ($CI$).
3. **Live Telemetry Charts**: Time-series visualization of inlet/outlet pressure, flow rate, and pump current.
4. **Digital Twin Visualization**: Live residual gauges comparing physical system vs Darcy's law physics model predictions, alongside synchronization badges (`SYNCHRONIZED`, `MINOR_DEVIATION`, `CRITICAL_DIVERGENCE`).
5. **Component Health Breakdown**: Visual gauges for Filter Health, Pump Health, Sensors, and overall Maintenance Urgency.
6. **Active Alerts Panel**: Live list of warning/critical events with acknowledgement buttons.
7. **Backwash Control Panel**: Manual trigger button for automated backwash pulse sequence.

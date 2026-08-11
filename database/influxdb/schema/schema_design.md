# InfluxDB Time-Series Data Schema Design

## Measurements:

### 1. `sensor_data`
- **Tags**: `sensor_id` (`pressure_inlet`, `pressure_outlet`, `flow`, `current`), `device_id` (`esp32_001`)
- **Fields**: `value` (float), `unit` (string), `quality` (string)

### 2. `digital_twin_state`
- **Tags**: `twin_id` (`filtration_system_001`), `synchronization_state` (`SYNCHRONIZED`, `MINOR_DEVIATION`, `MAJOR_DEVIATION`, `CRITICAL_DIVERGENCE`)
- **Fields**: `actual_pressure_drop`, `expected_pressure_drop`, `pressure_residual`, `actual_flow_rate`, `expected_flow_rate`, `flow_residual`

### 3. `health_metrics`
- **Tags**: `component` (`filter`, `pump`, `system`)
- **Fields**: `overall_health_score`, `clogging_index`, `maintenance_score`

### 4. `alerts`
- **Tags**: `severity` (`info`, `warning`, `critical`), `alert_type`
- **Fields**: `message`, `trigger_value`, `threshold_value`

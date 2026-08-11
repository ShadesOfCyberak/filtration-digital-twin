export interface RawSensors {
  pressure_inlet: number;
  pressure_outlet: number;
  flow: number;
  current: number;
}


export interface ProcessedTelemetry {
  pressure_inlet: number;
  pressure_outlet: number;
  pressure_drop: number;
  flow_rate: number;
  pump_current: number;
  pump_power: number;
  specific_power_consumption: number;
  clogging_index: number;
  flow_efficiency: number;
}

export interface DigitalTwinStateData {
  timestamp: string;
  twin_id: string;
  actual_pressure_inlet: number;
  actual_pressure_outlet: number;
  actual_pressure_drop: number;
  actual_flow_rate: number;
  actual_pump_power: number;
  expected_pressure_drop: number;
  expected_flow_rate: number;
  expected_pump_power: number;
  pressure_residual: number;
  flow_residual: number;
  power_residual: number;
  pressure_deviation_pct: number;
  flow_deviation_pct: number;
  power_deviation_pct: number;
  accumulated_volume_liters: number;
  estimated_cake_resistance: number;
  estimated_filter_resistance: number;
  time_since_last_backwash_sec: number;
  synchronization_state: 'SYNCHRONIZED' | 'MINOR_DEVIATION' | 'MAJOR_DEVIATION' | 'CRITICAL_DIVERGENCE';
  is_model_calibrated: boolean;
}

export interface SensorHealth {
  sensor_id: string;
  health_score: number;
  status: string;
}

export interface SystemHealthData {
  timestamp: string;
  overall_health_score: number;
  status: 'healthy' | 'degraded' | 'critical';
  filter_health_score: number;
  clogging_index: number;
  pressure_health_score: number;
  flow_health_score: number;
  efficiency_health_score: number;
  pump_health_score: number;
  power_consumption_score: number;
  pump_performance_score: number;
  sensors: Record<string, SensorHealth>;
  maintenance_score: number;
  maintenance_urgency: string;
  recommended_action: string;
  estimated_time_to_backwash_hours: number;
}

export interface AlertItemData {
  id: string;
  timestamp: string;
  severity: 'info' | 'warning' | 'critical';
  alert_type: string;
  message: string;
  trigger_value: number;
  threshold_value: number;
  recommended_action: string;
  acknowledged: boolean;
}

export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data: T;
}

export interface MLPredictionData {
  timestamp: string;
  anomaly_detected: boolean;
  anomaly_score: number;
  failure_probability: number;
  predicted_failure_mode: string;
  rul_hours: number;
  confidence: number;
}

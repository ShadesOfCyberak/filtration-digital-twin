import axios from 'axios';
import { ApiResponse, MLPredictionData } from '../types/api.types';
import { ProcessedTelemetry, DigitalTwinStateData } from '../types/sensor.types';
import { SystemHealthData } from '../types/health.types';

const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 8000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for unified error formatting
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.warn('API Request warning/failure:', error?.message);
    return Promise.reject(error);
  }
);

export const apiService = {
  // Sensor endpoints
  getLatestSensors: async (): Promise<ApiResponse<{ raw: any; processed: ProcessedTelemetry }>> => {
    return apiClient.get('/sensors/latest');
  },

  getSensorHistory: async (sensorId: string, minutes = 30): Promise<ApiResponse<any[]>> => {
    return apiClient.get(`/sensors/${sensorId}/history?minutes=${minutes}`);
  },

  // Health Monitoring
  getOverallHealth: async (): Promise<ApiResponse<SystemHealthData>> => {
    return apiClient.get('/health/overall');
  },

  // Digital Twin
  getDigitalTwinState: async (): Promise<ApiResponse<DigitalTwinStateData>> => {
    return apiClient.get('/digital-twin/state');
  },

  // ML Predictions
  getMLPredictions: async (): Promise<ApiResponse<MLPredictionData>> => {
    return apiClient.get('/predictions/full-assessment');
  },

  // Controls
  triggerBackwash: async (durationSeconds = 30): Promise<ApiResponse> => {
    return apiClient.post('/control/backwash', {
      mode: 'manual',
      duration_seconds: durationSeconds,
      operator_id: 'dashboard_ui'
    });
  },

  resetTwinState: async (): Promise<ApiResponse> => {
    return apiClient.post('/control/reset');
  }
};

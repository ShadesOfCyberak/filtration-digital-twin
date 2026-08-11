import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../store';
import { setLatestTelemetry, setTwinState } from '../store/slices/sensorSlice';
import { setSystemHealth, setMLPrediction } from '../store/slices/healthSlice';
import { apiService } from '../services/api';

export const useRealTimeData = (pollIntervalMs = 1500) => {
  const dispatch = useDispatch();
  const isLive = useSelector((state: RootState) => state.sensor.isLive);

  useEffect(() => {
    if (!isLive) return;

    const fetchData = async () => {
      try {
        const [sensorsRes, twinRes, healthRes, mlRes] = await Promise.all([
          apiService.getLatestSensors(),
          apiService.getDigitalTwinState(),
          apiService.getOverallHealth(),
          apiService.getMLPredictions()
        ]);

        if (sensorsRes.success && sensorsRes.data?.processed) {
          dispatch(setLatestTelemetry(sensorsRes.data.processed));
        }
        if (twinRes.success && twinRes.data) {
          dispatch(setTwinState(twinRes.data));
        }
        if (healthRes.success && healthRes.data) {
          dispatch(setSystemHealth(healthRes.data));
        }
        if (mlRes.success && mlRes.data) {
          dispatch(setMLPrediction(mlRes.data));
        }
      } catch (err) {
        console.warn('Real-time data polling attempt failed, retrying on next tick...', err);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, pollIntervalMs);
    return () => clearInterval(interval);
  }, [dispatch, isLive, pollIntervalMs]);
};

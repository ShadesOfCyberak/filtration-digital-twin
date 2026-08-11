import { configureStore } from '@reduxjs/toolkit';
import sensorReducer from './slices/sensorSlice';
import healthReducer from './slices/healthSlice';
import alertReducer from './slices/alertSlice';

export const store = configureStore({
  reducer: {
    sensor: sensorReducer,
    health: healthReducer,
    alert: alertReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { SystemHealthData } from '../../types/health.types';
import { MLPredictionData } from '../../types/api.types';

interface HealthState {
  systemHealth: SystemHealthData | null;
  mlPrediction: MLPredictionData | null;
}

const initialState: HealthState = {
  systemHealth: null,
  mlPrediction: null,
};

export const healthSlice = createSlice({
  name: 'health',
  initialState,
  reducers: {
    setSystemHealth: (state, action: PayloadAction<SystemHealthData>) => {
      state.systemHealth = action.payload;
    },
    setMLPrediction: (state, action: PayloadAction<MLPredictionData>) => {
      state.mlPrediction = action.payload;
    },
  },
});

export const { setSystemHealth, setMLPrediction } = healthSlice.actions;
export default healthSlice.reducer;

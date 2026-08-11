import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { ProcessedTelemetry, DigitalTwinStateData } from '../../types/sensor.types';

interface SensorState {
  telemetry: ProcessedTelemetry | null;
  twinState: DigitalTwinStateData | null;
  history: Array<{ timestamp: string; dp: number; flow: number; power: number }>;
  isLive: boolean;
}

const initialState: SensorState = {
  telemetry: null,
  twinState: null,
  history: [],
  isLive: true,
};

export const sensorSlice = createSlice({
  name: 'sensor',
  initialState,
  reducers: {
    setLatestTelemetry: (state, action: PayloadAction<ProcessedTelemetry>) => {
      state.telemetry = action.payload;
      const nowStr = new Date().toLocaleTimeString();
      state.history.push({
        timestamp: nowStr,
        dp: action.payload.pressure_drop,
        flow: action.payload.flow_rate,
        power: action.payload.pump_power,
      });
      if (state.history.length > 25) {
        state.history.shift();
      }
    },
    setTwinState: (state, action: PayloadAction<DigitalTwinStateData>) => {
      state.twinState = action.payload;
    },
    toggleLiveMode: (state) => {
      state.isLive = !state.isLive;
    },
  },
});

export const { setLatestTelemetry, setTwinState, toggleLiveMode } = sensorSlice.actions;
export default sensorSlice.reducer;

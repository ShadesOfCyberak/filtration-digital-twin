import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { AlertItemData } from '../../types/health.types';

interface AlertState {
  alerts: AlertItemData[];
}

const initialState: AlertState = {
  alerts: [],
};

export const alertSlice = createSlice({
  name: 'alert',
  initialState,
  reducers: {
    setAlerts: (state, action: PayloadAction<AlertItemData[]>) => {
      state.alerts = action.payload;
    },
    acknowledgeAlert: (state, action: PayloadAction<string>) => {
      const target = state.alerts.find(a => a.id === action.payload);
      if (target) {
        target.acknowledged = true;
      }
    },
  },
});

export const { setAlerts, acknowledgeAlert } = alertSlice.actions;
export default alertSlice.reducer;

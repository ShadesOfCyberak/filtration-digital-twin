from typing import List, Dict, Tuple, Any
import numpy as np
from app.core.config import settings
from app.core.logging import logger


class DataProcessingService:
    def __init__(self):
        self.ma_window = 5
        self.median_window = 3
        self.ema_alpha = 0.2
        self.clean_pressure_drop = 0.3  # bar
        self.clean_flow_rate = 80.0  # L/min
        self.pump_voltage = 24.0  # Volts
        
        # Buffer for sliding windows per sensor
        self._history_buffers: Dict[str, List[float]] = {
            "pressure_inlet": [],
            "pressure_outlet": [],
            "flow": [],
            "current": []
        }

    def apply_moving_average(self, values: List[float], window: int = 5) -> float:
        if not values:
            return 0.0
        subset = values[-window:]
        return float(np.mean(subset))

    def apply_median_filter(self, values: List[float], window: int = 3) -> float:
        if not values:
            return 0.0
        subset = values[-window:]
        return float(np.median(subset))

    def apply_ema(self, current_value: float, previous_ema: float, alpha: float = 0.2) -> float:
        return alpha * current_value + (1 - alpha) * previous_ema

    def is_outlier_zscore(self, values: List[float], new_val: float, threshold: float = 3.0) -> bool:
        if len(values) < 5:
            return False
        mean = np.mean(values)
        std = np.std(values)
        if std == 0:
            return False
        z_score = abs(new_val - mean) / std
        return z_score > threshold

    def calculate_pressure_drop(self, inlet: float, outlet: float) -> float:
        return max(0.0, float(inlet - outlet))

    def calculate_pump_power(self, current: float, voltage: float = 24.0) -> float:
        return max(0.0, float(voltage * current))

    def calculate_specific_power_consumption(self, power: float, flow: float) -> float:
        if flow <= 0.1:
            return 0.0
        # W * h / L => power (W) / (flow L/min * 60)
        return float(power / (flow * 60.0))

    def calculate_clogging_index(self, pressure_drop: float, flow_rate: float) -> float:
        if flow_rate <= 0.1:
            return 300.0  # Critical blockage condition
        ci = (pressure_drop / self.clean_pressure_drop) * (self.clean_flow_rate / flow_rate) * 100.0
        return float(np.round(ci, 2))

    def calculate_flow_efficiency(self, actual_flow: float, expected_flow: float = 80.0) -> float:
        if expected_flow <= 0:
            return 0.0
        eff = (actual_flow / expected_flow) * 100.0
        return float(np.clip(eff, 0.0, 100.0))

    def process_telemetry_frame(self, raw_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Input: dict with pressure_inlet, pressure_outlet, flow, current
        Output: Enriched dict with processed metrics and features
        """
        inlet = float(raw_data.get("pressure_inlet", 0.0))
        outlet = float(raw_data.get("pressure_outlet", 0.0))
        flow = float(raw_data.get("flow", 0.0))
        current = float(raw_data.get("current", 0.0))

        # Append to buffers
        for key, val in [("pressure_inlet", inlet), ("pressure_outlet", outlet), ("flow", flow), ("current", current)]:
            buf = self._history_buffers[key]
            buf.append(val)
            if len(buf) > 50:
                buf.pop(0)

        # Smooth readings
        clean_inlet = self.apply_moving_average(self._history_buffers["pressure_inlet"], self.ma_window)
        clean_outlet = self.apply_moving_average(self._history_buffers["pressure_outlet"], self.ma_window)
        clean_flow = self.apply_median_filter(self._history_buffers["flow"], self.median_window)
        clean_current = self.apply_moving_average(self._history_buffers["current"], self.ma_window)

        pressure_drop = self.calculate_pressure_drop(clean_inlet, clean_outlet)
        pump_power = self.calculate_pump_power(clean_current, self.pump_voltage)
        spc = self.calculate_specific_power_consumption(pump_power, clean_flow)
        clogging_index = self.calculate_clogging_index(pressure_drop, clean_flow)
        flow_efficiency = self.calculate_flow_efficiency(clean_flow, self.clean_flow_rate)

        return {
            "pressure_inlet": clean_inlet,
            "pressure_outlet": clean_outlet,
            "pressure_drop": float(np.round(pressure_drop, 3)),
            "flow_rate": float(np.round(clean_flow, 2)),
            "pump_current": float(np.round(clean_current, 2)),
            "pump_power": float(np.round(pump_power, 2)),
            "specific_power_consumption": float(np.round(spc, 4)),
            "clogging_index": clogging_index,
            "flow_efficiency": float(np.round(flow_efficiency, 2)),
        }


data_processor = DataProcessingService()

import math
from datetime import datetime
from typing import Dict, Any
import numpy as np

from app.core.config import settings
from app.core.logging import logger
from app.models.digital_twin import TwinState


class DigitalTwinService:
    def __init__(self):
        # Physical System Parameters
        self.filter_area = settings.twin.filter_area  # m^2
        self.filter_thickness = settings.twin.filter_thickness  # m
        self.R_medium = settings.twin.medium_resistance_clean  # m^-1
        self.R_max = settings.twin.max_cake_resistance  # m^-1
        self.fouling_k = settings.twin.fouling_rate_constant
        self.pump_a = settings.twin.pump_a  # bar
        self.pump_b = settings.twin.pump_b  # bar / (L/min)^2
        self.pump_eff = settings.twin.pump_efficiency
        self.viscosity = settings.twin.fluid_viscosity  # Pa*s

        # Dynamic Twin State Variables
        self.accumulated_volume = 0.0  # liters
        self.time_since_backwash = 0.0  # seconds
        self.last_update_timestamp = datetime.utcnow()

    def calculate_cake_resistance(self, time_sec: float) -> float:
        """Exponential buildup model for cake resistance"""
        return self.R_max * (1.0 - math.exp(-self.fouling_k * time_sec))

    def calculate_expected_pressure_drop(self, flow_l_min: float, time_sec: float) -> float:
        """
        Physics Model: Delta P = Q * (R_medium + R_cake) * mu * L / A
        Convert units: Flow in m^3/s, Pressure in bar (1 bar = 1e5 Pa)
        """
        Q_m3_s = (flow_l_min / 1000.0) / 60.0
        R_cake = self.calculate_cake_resistance(time_sec)
        R_total = self.R_medium + R_cake
        
        delta_P_pascals = (Q_m3_s * R_total * self.viscosity * self.filter_thickness) / self.filter_area
        delta_P_bar = delta_P_pascals / 1e5
        return float(np.clip(delta_P_bar, 0.1, 4.0))

    def calculate_expected_flow_rate(self, delta_p_bar: float) -> float:
        """Pump curve: Delta P = a - b * Q^2  =>  Q = sqrt((a - Delta P) / b)"""
        head_diff = self.pump_a - delta_p_bar
        if head_diff <= 0:
            return 10.0  # Minimum flow near shutoff head
        q = math.sqrt(head_diff / self.pump_b)
        return float(np.clip(q, 10.0, 100.0))

    def calculate_expected_pump_power(self, delta_p_bar: float, flow_l_min: float) -> float:
        """Hydraulic Power = Delta P (Pa) * Q (m^3/s) / eta"""
        delta_p_pa = delta_p_bar * 1e5
        q_m3_s = (flow_l_min / 1000.0) / 60.0
        hydraulic_power_w = (delta_p_pa * q_m3_s) / self.pump_eff
        return float(max(10.0, hydraulic_power_w))

    def evaluate_twin_state(self, processed_telemetry: Dict[str, Any]) -> TwinState:
        now = datetime.utcnow()
        dt_sec = (now - self.last_update_timestamp).total_seconds()
        self.last_update_timestamp = now
        
        actual_flow = float(processed_telemetry.get("flow_rate", 0.0))
        actual_dp = float(processed_telemetry.get("pressure_drop", 0.0))
        actual_power = float(processed_telemetry.get("pump_power", 0.0))

        self.time_since_backwash += dt_sec
        self.accumulated_volume += (actual_flow / 60.0) * dt_sec

        # Compute Expected Physics Metrics
        exp_dp = self.calculate_expected_pressure_drop(actual_flow, self.time_since_backwash)
        exp_flow = self.calculate_expected_flow_rate(actual_dp)
        exp_power = self.calculate_expected_pump_power(exp_dp, actual_flow)

        # Residuals
        dp_res = float(np.round(actual_dp - exp_dp, 3))
        flow_res = float(np.round(actual_flow - exp_flow, 2))
        power_res = float(np.round(actual_power - exp_power, 2))

        # Deviations (%)
        dp_dev_pct = float(np.round((dp_res / exp_dp) * 100.0 if exp_dp > 0 else 0, 1))
        flow_dev_pct = float(np.round((flow_res / exp_flow) * 100.0 if exp_flow > 0 else 0, 1))
        power_dev_pct = float(np.round((power_res / exp_power) * 100.0 if exp_power > 0 else 0, 1))

        # Determine Synchronization State
        abs_max_dev = max(abs(dp_dev_pct), abs(flow_dev_pct), abs(power_dev_pct))
        if abs_max_dev < 15.0:
            sync_state = "SYNCHRONIZED"
        elif abs_max_dev < 30.0:
            sync_state = "MINOR_DEVIATION"
        elif abs_max_dev < 50.0:
            sync_state = "MAJOR_DEVIATION"
        else:
            sync_state = "CRITICAL_DIVERGENCE"

        r_cake = self.calculate_cake_resistance(self.time_since_backwash)

        return TwinState(
            timestamp=now,
            twin_id="filtration_system_001",
            actual_pressure_inlet=float(processed_telemetry.get("pressure_inlet", 0.0)),
            actual_pressure_outlet=float(processed_telemetry.get("pressure_outlet", 0.0)),
            actual_pressure_drop=actual_dp,
            actual_flow_rate=actual_flow,
            actual_pump_power=actual_power,
            expected_pressure_drop=float(np.round(exp_dp, 3)),
            expected_flow_rate=float(np.round(exp_flow, 2)),
            expected_pump_power=float(np.round(exp_power, 2)),
            pressure_residual=dp_res,
            flow_residual=flow_res,
            power_residual=power_res,
            pressure_deviation_pct=dp_dev_pct,
            flow_deviation_pct=flow_dev_pct,
            power_deviation_pct=power_dev_pct,
            accumulated_volume_liters=float(np.round(self.accumulated_volume, 1)),
            estimated_cake_resistance=r_cake,
            estimated_filter_resistance=self.R_medium + r_cake,
            time_since_last_backwash_sec=self.time_since_backwash,
            synchronization_state=sync_state,
            is_model_calibrated=True
        )

    def trigger_backwash_reset(self):
        """Reset internal physical state following backwash"""
        self.time_since_backwash = 0.0
        self.accumulated_volume = 0.0
        logger.info("Digital Twin state reset after backwash operation.")


digital_twin_service = DigitalTwinService()

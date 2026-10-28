from datetime import datetime
from typing import Dict, Any
import numpy as np

from app.models.health_metrics import SystemHealthSummary, SensorHealth
from app.models.digital_twin import TwinState


class HealthMonitoringService:
    def calculate_filter_health(self, clogging_index: float, pressure_drop: float, flow_eff: float) -> Dict[str, float]:
        # Clogging Score (100 -> clean, 0 -> fully clogged at CI=250)
        clogging_score = float(np.clip(100.0 - ((clogging_index - 100.0) / 1.5), 0.0, 100.0)) if clogging_index >= 100 else 100.0
        
        # Pressure Health (100 -> normal 0.3-0.8 bar, 0 -> critical 2.0 bar)
        pressure_score = float(np.clip(100.0 * (1.0 - (max(0.0, pressure_drop - 0.3) / 1.7)), 0.0, 100.0))
        
        # Flow Health (100 -> 80 L/min, 0 -> 20 L/min)
        flow_score = float(np.clip(flow_eff, 0.0, 100.0))

        # Overall Weighted Filter Health
        filter_health = 0.40 * clogging_score + 0.30 * pressure_score + 0.30 * flow_score
        return {
            "filter_health": float(np.round(filter_health, 1)),
            "clogging_score": float(np.round(clogging_score, 1)),
            "pressure_score": float(np.round(pressure_score, 1)),
            "flow_score": float(np.round(flow_score, 1)),
        }

    def calculate_pump_health(self, actual_power: float, expected_power: float, actual_flow: float) -> Dict[str, float]:
        # Power deviation penalty
        p_dev = abs(actual_power - expected_power) / max(1.0, expected_power)
        power_score = float(np.clip(100.0 * (1.0 - p_dev), 0.0, 100.0))
        
        # Performance ratio score
        perf_score = float(np.clip((actual_flow / 80.0) * 100.0, 0.0, 100.0))
        
        pump_health = 0.50 * power_score + 0.50 * perf_score
        return {
            "pump_health": float(np.round(pump_health, 1)),
            "power_score": float(np.round(power_score, 1)),
            "perf_score": float(np.round(perf_score, 1))
        }

    def evaluate_sensor_health(self, sensor_id: str, value: float, secondary_val: float = None) -> SensorHealth:
        """Dynamically evaluate sensor health status and noise/validity from real readings"""
        health_score = 100.0
        status = "good"
        
        if sensor_id == "pressure_inlet":
            if value <= 0.0 or value > 6.0:
                health_score = max(10.0, 100.0 - abs(value - 2.5) * 20.0)
                status = "warning" if health_score > 50 else "faulty"
            elif secondary_val is not None and value < secondary_val:
                # Reverse differential pressure anomaly
                health_score = 40.0
                status = "faulty"
            else:
                health_score = 98.0 - min(20.0, max(0.0, value - 3.5) * 10.0)
                status = "good"
        elif sensor_id == "pressure_outlet":
            if value < 0.0 or value > 6.0:
                health_score = max(10.0, 100.0 - abs(value - 2.0) * 20.0)
                status = "warning" if health_score > 50 else "faulty"
            else:
                health_score = 98.0
                status = "good"
        elif sensor_id == "flow":
            if value <= 0.0:
                health_score = 45.0
                status = "warning"
            elif value > 120.0:
                health_score = 50.0
                status = "warning"
            else:
                health_score = 98.0
                status = "good"
        elif sensor_id == "current":
            if value <= 0.0 or value > 10.0:
                health_score = 40.0
                status = "warning"
            else:
                health_score = 99.0
                status = "good"
                
        return SensorHealth(sensor_id=sensor_id, health_score=float(np.round(health_score, 1)), status=status)

    def evaluate_system_health(self, processed_telemetry: Dict[str, Any], twin_state: TwinState) -> SystemHealthSummary:
        ci = processed_telemetry.get("clogging_index", 100.0)
        dp = processed_telemetry.get("pressure_drop", 0.0)
        flow_eff = processed_telemetry.get("flow_efficiency", 100.0)
        actual_power = processed_telemetry.get("pump_power", 0.0)
        exp_power = twin_state.expected_pump_power
        actual_flow = processed_telemetry.get("flow_rate", 0.0)
        p_in = processed_telemetry.get("pressure_inlet", 0.0)
        p_out = processed_telemetry.get("pressure_outlet", 0.0)
        curr = processed_telemetry.get("pump_current", 0.0)

        f_metrics = self.calculate_filter_health(ci, dp, flow_eff)
        p_metrics = self.calculate_pump_health(actual_power, exp_power, actual_flow)

        # Dynamic Sensors health calculation
        sensors_health = {
            "pressure_inlet": self.evaluate_sensor_health("pressure_inlet", p_in, p_out),
            "pressure_outlet": self.evaluate_sensor_health("pressure_outlet", p_out),
            "flow": self.evaluate_sensor_health("flow", actual_flow),
            "current": self.evaluate_sensor_health("current", curr)
        }
        avg_sensor_health = float(np.mean([s.health_score for s in sensors_health.values()]))

        # Overall System Health
        overall_health = 0.50 * f_metrics["filter_health"] + 0.35 * p_metrics["pump_health"] + 0.15 * avg_sensor_health
        overall_health = float(np.round(overall_health, 1))

        # Status
        if overall_health >= 80.0:
            status = "healthy"
        elif overall_health >= 55.0:
            status = "degraded"
        else:
            status = "critical"

        # Maintenance Score calculation
        maintenance_score = float(np.clip(100.0 - overall_health, 0.0, 100.0))
        if maintenance_score < 30.0:
            urgency = "Low - Routine check recommended"
            action = "System operating within normal parameters."
        elif maintenance_score < 60.0:
            urgency = "Medium - Schedule backwash soon"
            action = "Filter fouling detected. Schedule automated backwash cycle."
        elif maintenance_score < 80.0:
            urgency = "High - Backwash required within 2 hours"
            action = "High pressure drop across filter medium. Initiate immediate backwash."
        else:
            urgency = "Critical - Immediate shutdown / Backwash"
            action = "Severe clogging index exceeded threshold. Perform immediate maintenance."

        # Estimate time to backwash (hours)
        est_hours = float(np.clip((200.0 - ci) / 10.0, 0.1, 48.0)) if ci < 200 else 0.0

        return SystemHealthSummary(
            timestamp=datetime.utcnow(),
            overall_health_score=overall_health,
            status=status,
            filter_health_score=f_metrics["filter_health"],
            clogging_index=ci,
            pressure_health_score=f_metrics["pressure_score"],
            flow_health_score=f_metrics["flow_score"],
            efficiency_health_score=flow_eff,
            pump_health_score=p_metrics["pump_health"],
            power_consumption_score=p_metrics["power_score"],
            pump_performance_score=p_metrics["perf_score"],
            sensors=sensors_health,
            maintenance_score=maintenance_score,
            maintenance_urgency=urgency,
            recommended_action=action,
            estimated_time_to_backwash_hours=float(np.round(est_hours, 1))
        )


health_service = HealthMonitoringService()

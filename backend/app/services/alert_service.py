import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.models.alerts import AlertItem
from app.models.digital_twin import TwinState
from app.models.health_metrics import SystemHealthSummary
from app.repositories.influxdb_repository import influx_repo
from app.core.logging import logger


class AlertService:
    def __init__(self):
        self.active_alerts: Dict[str, AlertItem] = {}
        self.last_alert_timestamps: Dict[str, datetime] = {}

    async def evaluate_rules(self, telemetry: Dict[str, Any], twin_state: TwinState, health: SystemHealthSummary) -> List[AlertItem]:
        new_alerts: List[AlertItem] = []
        now = datetime.utcnow()

        # Rule 1: High Pressure Drop / Filter Clogging
        dp = telemetry.get("pressure_drop", 0.0)
        ci = telemetry.get("clogging_index", 100.0)

        if ci >= 200.0 or dp >= 1.5:
            alert = self._create_alert(
                alert_type="clogging",
                severity="critical",
                message=f"Critical Filter Clogging Detected! Clogging Index: {ci:.1f}, Delta P: {dp:.2f} bar",
                trigger_value=ci,
                threshold_value=200.0,
                recommended_action="Trigger automated backwash cycle immediately to prevent pump damage."
            )
            if self._should_fire("clogging_critical", now):
                new_alerts.append(alert)
        elif ci >= 150.0 or dp >= 1.0:
            alert = self._create_alert(
                alert_type="clogging",
                severity="warning",
                message=f"Warning: Moderate Filter Fouling. Clogging Index: {ci:.1f}, Delta P: {dp:.2f} bar",
                trigger_value=ci,
                threshold_value=150.0,
                recommended_action="Prepare for backwash sequence in the next operating window."
            )
            if self._should_fire("clogging_warning", now):
                new_alerts.append(alert)

        # Rule 2: Low Flow Rate / Restriction
        flow = telemetry.get("flow_rate", 80.0)
        if flow <= 40.0:
            alert = self._create_alert(
                alert_type="flow_low",
                severity="critical",
                message=f"Critical Low Flow Rate Detected: {flow:.1f} L/min",
                trigger_value=flow,
                threshold_value=40.0,
                recommended_action="Inspect inlet valve and check for pump cavitation or blockage."
            )
            if self._should_fire("flow_low_critical", now):
                new_alerts.append(alert)

        # Rule 3: Digital Twin Divergence
        if twin_state.synchronization_state == "CRITICAL_DIVERGENCE":
            alert = self._create_alert(
                alert_type="divergence",
                severity="critical",
                message=f"Digital Twin Critical Divergence! Max Residual Deviation > 50%",
                trigger_value=abs(twin_state.pressure_deviation_pct),
                threshold_value=50.0,
                recommended_action="Recalibrate physics parameters or check physical sensors for drift."
            )
            if self._should_fire("twin_divergence", now):
                new_alerts.append(alert)

        # Store new alerts
        for alert in new_alerts:
            self.active_alerts[alert.id] = alert
            await influx_repo.write_alert(alert.dict())
            logger.warning(f"ALERT GENERATED [{alert.severity.upper()}]: {alert.message}")

        return list(self.active_alerts.values())[-20:]

    def _create_alert(self, alert_type: str, severity: str, message: str, trigger_value: float, threshold_value: float, recommended_action: str) -> AlertItem:
        return AlertItem(
            id=str(uuid.uuid4())[:8],
            timestamp=datetime.utcnow(),
            severity=severity,
            alert_type=alert_type,
            message=message,
            trigger_value=trigger_value,
            threshold_value=threshold_value,
            recommended_action=recommended_action,
            acknowledged=False
        )

    def _should_fire(self, alert_key: str, now: datetime, cooldown_sec: int = 60) -> bool:
        last = self.last_alert_timestamps.get(alert_key)
        if not last or (now - last).total_seconds() > cooldown_sec:
            self.last_alert_timestamps[alert_key] = now
            return True
        return False

    def acknowledge_alert(self, alert_id: str) -> bool:
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            self.active_alerts[alert_id].acknowledged_at = datetime.utcnow()
            return True
        return False


alert_service = AlertService()

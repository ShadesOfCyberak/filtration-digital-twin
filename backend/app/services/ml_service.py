import os
from datetime import datetime
from typing import Dict, Any
import numpy as np
from sklearn.ensemble import IsolationForest

from app.core.logging import logger
from app.schemas.responses import PredictionResponse


class MLInferenceService:
    def __init__(self):
        self.anomaly_model = None
        self._initialize_baseline_models()

    def _initialize_baseline_models(self):
        try:
            # Fit an in-memory IsolationForest on baseline normal operating data range
            # Features: [pressure_drop, flow_rate, pump_current, clogging_index]
            np.random.seed(42)
            normal_data = np.random.multivariate_normal(
                mean=[0.5, 78.0, 3.2, 110.0],
                cov=np.diag([0.05, 1.5, 0.1, 10.0]),
                size=200
            )
            self.anomaly_model = IsolationForest(contamination=0.05, random_state=42)
            self.anomaly_model.fit(normal_data)
            logger.info("ML Baseline Anomaly Model successfully initialized.")
        except Exception as e:
            logger.error(f"Error initializing ML baseline model: {e}")

    def predict(self, processed_telemetry: Dict[str, Any]) -> PredictionResponse:
        dp = float(processed_telemetry.get("pressure_drop", 0.0))
        flow = float(processed_telemetry.get("flow_rate", 0.0))
        current = float(processed_telemetry.get("pump_current", 0.0))
        ci = float(processed_telemetry.get("clogging_index", 100.0))

        feature_vector = np.array([[dp, flow, current, ci]])

        # Anomaly Detection Score
        if self.anomaly_model:
            raw_score = float(self.anomaly_model.decision_function(feature_vector)[0])
            is_anomaly = bool(self.anomaly_model.predict(feature_vector)[0] == -1)
            # Normalize score to 0..1 scale (higher means more anomalous)
            anomaly_score = float(np.clip((0.2 - raw_score) / 0.4, 0.0, 1.0))
        else:
            anomaly_score = 0.1 if ci < 160 else 0.85
            is_anomaly = ci >= 180

        # Failure Mode & Probability
        if ci >= 200:
            failure_mode = "Filter Cake Clogging (Critical)"
            fail_prob = 0.95
        elif current > 5.0 and flow < 30.0:
            failure_mode = "Pump Cavitation / Deadhead"
            fail_prob = 0.88
        elif ci >= 140:
            failure_mode = "Progressive Filter Fouling"
            fail_prob = 0.45
        else:
            failure_mode = "Normal Operating Mode"
            fail_prob = 0.05

        # RUL estimation (Remaining Useful Life in operating hours)
        # RUL scales inversely with clogging index progress towards CI=220
        ci_rem = max(0.0, 220.0 - ci)
        rul_hours = float(np.round((ci_rem / 120.0) * 48.0, 1))

        # Dynamic confidence score based on classification certainty
        conf = float(np.clip(0.85 + 0.12 * (1.0 - abs(fail_prob - 0.5) * 2), 0.70, 0.99))

        return PredictionResponse(
            timestamp=datetime.utcnow(),
            anomaly_detected=is_anomaly,
            anomaly_score=float(np.round(anomaly_score, 3)),
            failure_probability=float(np.round(fail_prob, 2)),
            predicted_failure_mode=failure_mode,
            rul_hours=rul_hours,
            confidence=float(np.round(conf, 2))
        )


ml_service = MLInferenceService()

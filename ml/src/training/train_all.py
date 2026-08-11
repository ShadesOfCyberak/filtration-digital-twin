import os
import sys

# Ensure ml directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.data.synthetic_generator import generate_synthetic_telemetry
from src.models.anomaly_detector import AnomalyDetector
from src.models.rul_estimator import RULEstimator


def train_and_save_models():
    print("Generating synthetic filtration telemetry dataset...")
    df = generate_synthetic_telemetry(num_samples=1000)

    feature_cols = ["pressure_drop", "flow_rate", "pump_current", "clogging_index"]
    X = df[feature_cols]
    y_rul = df["rul_hours"]

    # Target Directory
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../models"))
    os.makedirs(models_dir, exist_ok=True)

    # 1. Train Anomaly Detector
    print("Training Isolation Forest Anomaly Detector...")
    ad = AnomalyDetector(contamination=0.05)
    ad.train(X)
    ad_path = os.path.join(models_dir, "anomaly_detector_v1.0.0.pkl")
    ad.save(ad_path)
    print(f"Saved anomaly detector model to {ad_path}")

    # 2. Train RUL Estimator
    print("Training Random Forest RUL Estimator...")
    rul = RULEstimator(n_estimators=50)
    rul.train(X, y_rul)
    rul_path = os.path.join(models_dir, "rul_estimator_v1.0.0.pkl")
    rul.save(rul_path)
    print(f"Saved RUL estimator model to {rul_path}")

    print("All ML baseline models successfully trained and serialized!")


if __name__ == "__main__":
    train_and_save_models()

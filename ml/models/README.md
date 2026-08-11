# ML Model Artifact Storage

This directory stores serialized model artifacts (`.pkl` / `.joblib`).

## Standard File Naming Conventions:
- Anomaly Detector: `anomaly_detector_v1.0.0.pkl`
- Failure Mode Classifier: `failure_classifier_v1.0.0.pkl`
- Remaining Useful Life (RUL) Regressor: `rul_estimator_v1.0.0.pkl`

To retrain and regenerate model artifacts, run:
```bash
python ml/src/training/train_all.py
```

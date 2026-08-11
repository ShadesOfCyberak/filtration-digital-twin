import numpy as np
import pandas as pd


def generate_synthetic_telemetry(num_samples: int = 1000, random_seed: int = 42) -> pd.DataFrame:
    np.random.seed(random_seed)
    
    # Time steps
    t = np.linspace(0, 100, num_samples)
    
    # Fouling progression curve (linear + exponential)
    fouling = 0.01 * t + 0.05 * np.exp(t / 25.0)
    
    # Sensor measurements with gaussian noise
    p_inlet = 2.4 + fouling + np.random.normal(0, 0.03, num_samples)
    p_outlet = 1.95 + np.random.normal(0, 0.02, num_samples)
    p_drop = np.maximum(0.1, p_inlet - p_outlet)
    
    flow = np.maximum(10.0, 80.0 - (fouling * 12.0) + np.random.normal(0, 0.5, num_samples))
    current = 3.2 + (fouling * 0.8) + np.random.normal(0, 0.05, num_samples)
    
    # Clogging index calculation
    ci = (p_drop / 0.3) * (80.0 / flow) * 100.0
    
    # Target RUL (Remaining Useful Life in hours)
    rul = np.maximum(0.0, 48.0 - (ci / 200.0) * 48.0)
    
    df = pd.DataFrame({
        "time_step": t,
        "pressure_inlet": p_inlet,
        "pressure_outlet": p_outlet,
        "pressure_drop": p_drop,
        "flow_rate": flow,
        "pump_current": current,
        "clogging_index": ci,
        "rul_hours": rul
    })
    return df

import joblib
from sklearn.ensemble import RandomForestRegressor


class RULEstimator:
    def __init__(self, n_estimators: int = 100):
        self.model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)

    def train(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)

    def save(self, filepath: str):
        joblib.dump(self.model, filepath)

    def load(self, filepath: str):
        self.model = joblib.load(filepath)

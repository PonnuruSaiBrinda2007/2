import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

np.random.seed(42)

samples = 1000

area = np.random.randint(500, 6000, samples)
workers = np.random.randint(5, 60, samples)
budget = np.random.randint(1000000, 20000000, samples)

# Cost increases non-linearly with area
cost = (
    area * 1800 +
    workers * 8000 +
    (area ** 1.05) +
    np.random.randint(-300000, 300000, samples)
)

# Delay logic:
# - Large area increases delay
# - More workers reduce delay
# - Low budget increases delay
delay = (
    (area / 400) -
    (workers * 0.8) +
    (10000000 / budget) * 20 +
    np.random.normal(5, 3, samples)
)

delay = np.clip(delay, 5, 120)

X = np.column_stack((area, workers, budget))

cost_model = RandomForestRegressor(n_estimators=150)
cost_model.fit(X, cost)

delay_model = RandomForestRegressor(n_estimators=150)
delay_model.fit(X, delay)

if not os.path.exists("models"):
    os.makedirs("models")

joblib.dump(cost_model, "models/cost_model.pkl")
joblib.dump(delay_model, "models/delay_model.pkl")

print("Advanced models trained and saved!")
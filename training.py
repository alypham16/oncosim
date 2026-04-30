import numpy as np
import pickle
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression


drug_map = {"doxorubicin": 0, "vincristine": 1, "paclitaxel": 2}


def generate_data(n=1000):
    rng = np.random.default_rng(42)
    X, y = [], []

    for _ in range(n):
        r = rng.uniform(0.1, 1.0)
        K = rng.uniform(1e4, 1e6)
        drug = rng.choice(list(drug_map.values()))

        # simple rule
        resistance = 1 if (r > 0.6 and drug == 0) else 0

        X.append([r, K, drug])
        y.append(resistance)

    return np.array(X), np.array(y)


X, y = generate_data()

model = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", LogisticRegression(max_iter=1000))
])

model.fit(X, y)

with open("model.pkl", "wb") as f:
    pickle.dump(model, f)
import pandas as pd
import numpy as np
import pickle
from pathlib import Path

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "data" / "tnbc_ic50vals.csv"
MODEL_PATH = BASE_DIR / "model" / "model.pkl"


drug_map = {
    "cisplatin": 0, "docetaxel": 1, "olaparib": 2,
    "paclitaxel": 3, "gemcitabine": 4,
    "talazoparib": 5, "epirubicin": 6,
    "cyclophosphamide": 7
}

cell_line_map = {
    "231": 0,
    "468": 1,
    "1806": 2,
    "549": 3,
}


def load_data():
    df = pd.read_csv(DATA_PATH)

    df = df.rename(columns={
        "DRUG_NAME": "drug",
        "CELL_LINE_NAME": "cell_line",
        "LN_IC50": "ln_ic50"
    })

    df["drug"] = df["drug"].str.lower()
    df["cell_line"] = df["cell_line"].str.upper()

    df = df[df["drug"].isin(drug_map.keys())]

    cell_line_alias = {
        "MDA-MB-231": "231",
        "MDA-MB-468": "468",
        "HCC1806": "1806",
        "BT-549": "549"
    }

    df = df[df["cell_line"].isin(cell_line_alias.keys())]

    # map to IDs
    df["cell_line"] = df["cell_line"].map(cell_line_alias)

    df["drug_id"] = df["drug"].map(drug_map)
    df["cell_id"] = df["cell_line"].map(cell_line_map)

    df = df.dropna(subset=["drug_id", "cell_id"])

    # convert ln(IC50)
    df["ic50"] = np.exp(df["ln_ic50"])

    # define resistance (per drug)
    df["resistance"] = df.groupby("drug")["ic50"].transform(
        lambda x: (x > x.median()).astype(int)
    )

    return df


def generate_features(df, samples_per_condition=300):
    rng = np.random.default_rng(42)

    X, y = [], []

    for _, row in df.iterrows():
        for _ in range(samples_per_condition):

            r = rng.normal(0.5, 0.15)
            r = np.clip(r, 0.05, 1.5)

            K = rng.lognormal(mean=10, sigma=1)
            K = np.clip(K, 1e4, 1e7)

            base = int(row["resistance"])
            prob = 0.7 * base + 0.3 * (r > 0.6)
            label = 1 if rng.random() < prob else 0

            X.append([
                r,
                K,
                int(row["drug_id"]),
                int(row["cell_id"])
            ])

            y.append(label)

    return np.array(X), np.array(y)


df = load_data()
X, y = generate_features(df)

model = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", LogisticRegression(max_iter=1000))
])

model.fit(X, y)

with open(MODEL_PATH, "wb") as f:
    pickle.dump(model, f)

print("Model trained on GDSC-derived labels")
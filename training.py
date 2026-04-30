import pandas as pd
import numpy as np
import pickle
from pathlib import Path

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "data" / "GDSC_data.csv"
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
    """
    Loads and prepares the GDSC dataset for training the resistance prediction model. 
    The function reads the dataset, renames columns, filters relevant drugs and cell lines, 
    maps categorical variables to numerical IDs, converts ln(IC50) to IC50 values, 
    and defines resistance labels based on median IC50 values for each drug.

    Parameters:
    - None

    Returns:
    - A pandas DataFrame containing the prepared dataset with columns for drug, cell line, 
    IC50 values, and resistance labels.
    """
    df = pd.read_csv(DATA_PATH)

    df = df.rename(columns={
        "DRUG_NAME": "drug",
        "CELL_LINE_NAME": "cell_line",
        "LN_IC50": "ln_ic50"
    })

    df["drug"] = df["drug"].str.lower()
    df["cell_line"] = df["cell_line"].str.upper()
    df["log_ic50"] = df["ln_ic50"]
    df = df[df["drug"].isin(drug_map.keys())]

    cell_line_alias = {
        "MDA-MB-231": "231",
        "MDA-MB-468": "468",
        "HCC1806": "1806",
        "BT-549": "549"
    }

    df = df[df["cell_line"].isin(cell_line_alias.keys())]
    df["cell_line"] = df["cell_line"].map(cell_line_alias)

    df["drug_id"] = df["drug"].map(drug_map)
    df["cell_id"] = df["cell_line"].map(cell_line_map)

    df = df.dropna(subset=["drug_id", "cell_id"])

    # define resistance using log_ic50 and the drug-specific median
    df["resistance"] = df.groupby("drug")["log_ic50"].transform(
        lambda x: (x > x.median()).astype(int)
    )
    
    return df

def generate_features(df: pd.DataFrame, samples_per_condition = 300) -> tuple[np.ndarray, np.ndarray]:
    """
    Generates synthetic features for training the resistance prediction 
    model due to lack of available real samples from the dataset.

    Due to limited experience on what to do without enough samples,
    ChatGPT was used to help generate this function and with guidance on how to 
    deal with the lack of samples by prompting it with the issue and requesting
    how to generate synthetic data based on the existing real samples.
    AI was used for lines 105-120.

    Parameters:
    - df: A pandas DataFrame containing the prepared dataset.
    - samples_per_condition: An integer representing the number of synthetic samples 
    to generate for each condition (default = 300).

    Returns:
    - A tuple of two numpy arrays: X (features) and y (labels).
    """
    rng = np.random.default_rng(42)

    X, y = [], []

    for _, row in df.iterrows():
        for _ in range(samples_per_condition):
            r = np.clip(rng.normal(0.5, 0.15), 0.05, 1.5)
            K = rng.lognormal(mean = 10, sigma = 1)
            K = np.clip(K, 1e4, 1e7)

            base = int(row["resistance"])
            ic50_effect = 1 if row["log_ic50"] > np.median(df["log_ic50"]) else 0
            prob = 0.7 * base + 0.3 * ic50_effect + 0.1 * (r > 0.6)
            label = 1 if rng.random() < prob else 0

            X.append([
                r,
                K,
                int(row["drug_id"]),
                int(row["cell_id"]),
                row["log_ic50"]
            ])
            y.append(label)

    return np.array(X), np.array(y)

def ic50_lookup(df: pd.DataFrame) -> dict:
    """
    Creates a lookup dictionary for median IC50 values for each drug from the dataset.

    Parameters:
    - df: A pandas DataFrame containing the prepared dataset.

    Returns:
    - A dictionary mapping each drug to its median IC50 value.
    """
    return df.groupby(["drug", "cell_line"])["log_ic50"].mean().to_dict()


df = load_data()
X, y = generate_features(df)

model = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", LogisticRegression(max_iter=1000))
])

model.fit(X, y)

with open(MODEL_PATH, "wb") as f:
    pickle.dump({
        "model": model,
        "ic50_lookup": ic50_lookup(df)
    }, f)

print("Model trained on GDSC-derived labels")
import redis
import json
import pickle
from pathlib import Path

from simulator import fit_logistic, simulate

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "model.pkl"

rdb = redis.Redis(host="redis", port=6379, decode_responses=True)

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)


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


def fit_and_store(time, counts):
    params = fit_logistic(time, counts)
    rdb.set("last_fit", json.dumps(params))
    return params


def get_fit():
    data = rdb.get("last_fit")
    return json.loads(data) if data else None


def predict_resistance(params, drug, cell_line=None, exposure=None):
    X = [[
        params["r"],
        params["K"],
        drug_map[drug],
        cell_line_map[cell_line]
    ]]
    return float(model.predict_proba(X)[0][1])


def run_simulation(params, drug, resistance, exposure=None):
    return simulate(params, drug, resistance)
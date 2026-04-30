import redis
import json
import pickle

from simulator import fit_logistic, simulate

rdb = redis.Redis(host="redis", port=6379, decode_responses=True)

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

drug_map = {"doxorubicin": 0, "vincristine": 1, "paclitaxel": 2}

def fit_and_store(time, counts):
    params = fit_logistic(time, counts)
    rdb.set("last_fit", json.dumps(params))
    return params

def get_fit():
    data = rdb.get("last_fit")
    return json.loads(data) if data else None

def predict_resistance(params, drug, cell_line=None, exposure=None):
    X = [[params["r"], params["K"], drug_map[drug]]]
    return float(model.predict_proba(X)[0][1])

def run_simulation(params, drug, resistance, exposure=None):
    return simulate(params, drug, resistance)
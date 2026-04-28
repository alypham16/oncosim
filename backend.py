import redis
import json
import pickle

from simulator import fit_logistic, simulate_future

rdb = redis.Redis(host="redis", port=6379, decode_responses=True)

with open("model.pkl", "rb") as f:
    model = pickle.load(f)


def fit_and_store(time, counts):
    params = fit_logistic(time, counts)
    rdb.set("last_fit", json.dumps(params))
    return params


def get_fit():
    data = rdb.get("last_fit")
    if not data:
        return None
    return json.loads(data)


def predict(params, drug):
    X = [[params["r"], params["K"], drug]]
    return int(model.predict(X)[0])


def simulate(params):
    return simulate_future(params, days=30)
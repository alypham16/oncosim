import redis
import json
import pickle
from pathlib import Path

from simulator import fit_logistic, simulate

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "model.pkl"

rdb = redis.Redis(host = "redis", port = 6379, decode_responses = True)

with open(MODEL_PATH, "rb") as f:
    bundle = pickle.load(f)

model = bundle["model"]
ic50_lookup = bundle["ic50_lookup"]

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


def fit_and_store(time: list, counts: list) -> dict:
    """
    Fit the logistic model to the provided time and counts data, store the parameters in Redis, and return them.
    
    Parameters:
    - time: List of time points, in hours.
    - counts: List of cell counts corresponding to the time points.

    Returns:
    - params: Dictionary containing the fitted parameters 'r' (growth rate), 'K' (carrying capacity) and 'N0' (initial cell count).
    """
    params = fit_logistic(time, counts)
    rdb.set("last_fit", json.dumps(params))
    return params

def get_fit():
    """
    Gets the last fitted parameters from Redis. Returns None if no parameters are found.
    
    Parameters:
    - None

    Returns:
    - A dictionary with the last fitted parameters 'r', 'K' and 'N0', or None if no parameters are stored.
    """
    data = rdb.get("last_fit")
    return json.loads(data) if data else None


def predict_resistance(params: dict, drug: str, cell_line = None) -> float:
    """
    Predicts the probability of drug resistance based on the fitted parameters, drug, and cell line.

    Parameters:
    - params: Dictionary containing the fitted parameters 'r' (growth rate), 'K' (carrying capacity) and 'N0' (initial cell count).
    - drug: String representing the therapeutic drug for which to predict resistance.
    - cell_line: String representing the TNBC cell line for which to predict resistance.

    Returns:
    - A float of the predicted probability of drug resistance.
    """
    if params is None:
        raise ValueError("No fitted parameters found. Please fit the model first.")
    
    log_ic50 = ic50_lookup.get((drug, cell_line), 0.0)

    X = [[
        params["r"],
        params["K"],
        drug_map[drug],
        cell_line_map[cell_line],
        log_ic50
    ]]
    return float(model.predict_proba(X)[0][1])


def run_simulation(params: dict, drug: str, cell_line: str, resistance: float) -> dict:
    """
    Runs a simulation of tumor growth under drug treatment, incorporating the predicted resistance.

    Parameters:
    - params: Dictionary containing the fitted parameters 'r' (growth rate), 'K' (carrying capacity) and 'N0' (initial cell count).
    - drug: String representing the therapeutic drug for which to run the simulation.
    - cell_line: String representing the TNBC cell line for which to run the simulation.
    - ic50_lookup: Dictionary mapping (drug, cell_line) to its log(IC50).
    - resistance: Float representing the predicted probability of drug resistance.

    Returns:
    - A dictionary containing the simulation results, including time points and cell counts for sensitive, resistant, and total populations.
    """
    return simulate(params, drug, cell_line, ic50_lookup, resistance)
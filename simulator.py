import numpy as np
from scipy.optimize import curve_fit

def logistic(t: np.ndarray, r: float, K: float, N0: float) -> np.ndarray:
    """
    Standard logistic growth model for cell populations.

    Parameters:
    - t: Array of time points.
    - r: Growth rate parameter.
    - K: Carrying capacity parameter.
    - N0: Initial cell count population

    Returns:
    - Array of predicted cell counts at each time point based on the logistic growth model.
    """
    return K / (1 + ((K - N0) / N0) * np.exp(-r * t))

def fit_logistic(time: list, counts: list) -> dict:
    """
    Fits a logistic growth model to the provided time and counts data.

    Parameters:
    - time: List of time points, in hours.
    - counts: List of cell counts corresponding to the time points.

    Returns:
    - A dictionary containing the fitted parameters 'r' (growth rate) and 'K'
    (carrying capacity), as well as 'N0' (initial cell count).
    """
    time = np.array(time, dtype=float)
    counts = np.array(counts, dtype=float)
    N0 = max(counts[0], 1e-6)

    def model(t: np.ndarray, r: float, K: float) -> np.ndarray:
        return logistic(t, r, K, N0)
    
    popt, _ = curve_fit(
        model,
        time,
        counts,
        bounds = (0, [5.0, 1e7]),
        maxfev = 10000
    )

    r, K = popt

    return {
        "r": float(r),
        "K": float(K),
        "N0": float(N0)
    }

def simulate(params: dict, drug: str, cell_line: str,
             ic50_lookup: dict, resistance: float, hours: int = 168) -> dict:
    """
    Simulates tumor growth under treatment using logistic growth, where
    drug effects are derived from IC50 data and resistance predictions.

    Parameters:
    - params: Dictionary with 'r', 'K', 'N0'
    - resistance: Predicted probability of resistance (0–1)
    - drug: Selected drug name
    - cell_line: Selected TNBC cell line
    - ic50_lookup: Dictionary mapping (drug, cell_line) → log(IC50)
    - hours: Simulation duration

    Returns:
    - Dictionary with time series for sensitive, resistant, and total populations
    """

    r = float(params["r"])
    K = float(params["K"])
    N0 = float(params["N0"])
    resistance = float(resistance)

    key = (drug, cell_line)
    log_ic50 = ic50_lookup.get(key)

    # convert IC50
    drug_kill = 1 / (1 + np.exp(log_ic50))

    cell_values = [v for (_, c), v in ic50_lookup.items() if c == cell_line]
    cell_scale = 1.0
    if cell_values:
        cell_scale = 1 + 0.2 * (np.mean(cell_values) - np.mean(list(ic50_lookup.values())))

    r = r * cell_scale

    t = np.arange(hours)

    # Sensitive cells
    sensitive = logistic(
        t,
        r * (1 - drug_kill),
        K,
        N0
    )

    # Resistant cells
    resistant = logistic(
        t,
        r * (1 - drug_kill * (1 - resistance)),
        K,
        N0 * 0.2
    )

    return {
        "hours": t.tolist(),
        "sensitive": sensitive.tolist(),
        "resistant": resistant.tolist(),
        "total": (sensitive + resistant).tolist()
    }
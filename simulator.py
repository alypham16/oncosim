import numpy as np
from scipy.optimize import curve_fit

def logistic(t, r, K, N0):
    return K / (1 + ((K - N0) / N0) * np.exp(-r * t))

def fit_logistic(time, counts):
    time = np.array(time, dtype=float)
    counts = np.array(counts, dtype=float)

    N0 = max(counts[0], 1e-6)

    def model(t, r, K):
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

def simulate(params, resistance, hours = 168): # typical logistic growth curve for TNBC cells
    r = params["r"]

    K = params["K"]
    N0 = params["N0"]

    t = np.arange(hours)

    sensitive = logistic(t, r, K, N0)
    resistant = logistic(
        t,
        r * (0.3 + 0.7 * float(resistance)),
        K,
        N0 * 0.2
    )

    return {
        "hours": t.tolist(),
        "sensitive": sensitive.tolist(),
        "resistant": resistant.tolist(),
        "total": (sensitive + resistant).tolist()
    }
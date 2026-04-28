import numpy as np
from scipy.optimize import curve_fit

def logistic(t, r, K, N0):
    t = np.array(t)
    return K / (1 + ((K - N0) / max(N0, 1e-6)) * np.exp(-r * t))


def fit_logistic(time, counts):
    time = np.array(time)
    counts = np.array(counts)

    N0 = counts[0]

    popt, _ = curve_fit(
        lambda t, r, K: logistic(t, r, K, N0),
        time,
        counts,
        bounds=(0, [5.0, 1e7])
    )

    r, K = popt
    return {"r": float(r), "K": float(K), "N0": float(N0)}


def simulate_future(params, days=30, drug=0):
    t = np.arange(0, days)

    # drug reduces growth rate
    r = params["r"] * (1 - 0.3 * drug)

    y = logistic(t, r, params["K"], params["N0"])

    return {"days": t.tolist(), "counts": y.tolist()}
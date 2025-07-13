import numpy as np
import pandas as pd
from scipy.optimize import minimize

def _fopdt_response(t, K, tau, theta):
    y = K * (1 - np.exp(-(t - theta) / tau))
    y[t < theta] = 0.0
    return y

def identify_fopdt(df: pd.DataFrame):
    t = df["timestamp"].values - df["timestamp"].values[0]
    pv = df["temp"].values
    cv = df["power"].values

    du = cv.max() - cv.min()
    dy = pv[-1] - pv[0]
    K0 = dy / du if du else 1.0
    tau0 = t[np.argmin(np.abs(pv - (pv[0] + 0.632*dy)))]
    theta0 = t[np.argmax(np.diff(pv))] / 2

    def err(params):
        K, tau, theta = params
        y_hat = _fopdt_response(t, K, tau, theta) * du + pv[0]
        return np.sum(np.abs(y_hat - pv))

    bounds = [(1e-6, None), (1e-3, None), (0.0, max(t))]
    K, tau, theta = minimize(err, (K0, tau0, theta0), bounds=bounds).x
    return float(K), float(tau), float(theta)

def cohen_coon(K, tau, theta):
    if theta <= 0 or tau <= 0:
        raise ValueError("tau and theta must be >0")

    r  = theta / tau
    kp = (1 / K) * (1.35 + 0.27 * r) / r
    Ti = tau * (2.5 + 0.66 * r) / (1 + 0.444 * r)
    Td = 0.37 * tau / (1 + 0.2 * r)

    ki = kp / Ti
    kd = kp * Td
    return kp, ki, kd

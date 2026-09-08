"""
ou_estimation.py: Estimating the Ornstein-Uhlenbeck Parameters

"""

import os
import sys

import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

DT = 1.0 / 252.0  # daily time step, annualized convention (Leung & Li, 2015)


"""
Loading the formation-period spread series (already built by cointegration.py).
"""
def load_formation_spreads() -> pd.DataFrame:
    path = os.path.join(config.PROCESSED_DATA_DIR, "spreads_formation.csv")
    return pd.read_csv(path, index_col="Date", parse_dates=True)


"""
Computing the five summary statistics (Xx, Xy, Xxx, Xxy, Xyy) needed
for the closed-form OU-MLE, from the formation-period spread series.
"""
def compute_summary_stats(spread: pd.Series) -> dict:
    x = spread.values[:-1]   # x_{k-1}, k = 1..n
    y = spread.values[1:]    # x_k
    n = len(x)

    return {
        "n": n,
        "Xx": x.sum(),
        "Xy": y.sum(),
        "Xxx": (x ** 2).sum(),
        "Xxy": (x * y).sum(),
        "Xyy": (y ** 2).sum(),
    }


"""
Closed-form OU-MLE estimation for a single pair's spread
"""
def estimate_ou_parameters(spread: pd.Series) -> dict:
    stats = compute_summary_stats(spread)
    n = stats["n"]
    Xx, Xy, Xxx, Xxy, Xyy = stats["Xx"], stats["Xy"], stats["Xxx"], stats["Xxy"], stats["Xyy"]

    # OLS slope (a_hat) and intercept (b_hat) from regressing x_k on x_{k-1}
    a_hat = (n * Xxy - Xx * Xy) / (n * Xxx - Xx ** 2)
    b_hat = (Xy - a_hat * Xx) / n

    # Closed-form theta, mu
    theta_hat = -np.log(a_hat) / DT
    mu_hat = b_hat / (1 - a_hat)

    # Residual sum of squares -> sigma_tilde^2 (discrete-time MLE variance)
    x = spread.values[:-1]
    y = spread.values[1:]
    residuals = y - a_hat * x - b_hat
    rss = (residuals ** 2).sum()
    sigma_tilde_sq = rss / n

    # Continuous-time sigma^2
    sigma_hat_sq = 2 * theta_hat * sigma_tilde_sq / (1 - a_hat ** 2)
    sigma_hat = np.sqrt(sigma_hat_sq)

    # Maximized average log-likelihood (closed-form at the optimum)
    sigma_tilde = np.sqrt(sigma_tilde_sq)
    l_star = -0.5 * (np.log(2 * np.pi) + 1) - np.log(sigma_tilde)

    return {
        "theta_star": theta_hat,
        "mu_star": mu_hat,
        "sigma_star": sigma_hat,
        "l_star": l_star,
    }


"""
Running OU-MLE for all pairs, then computing the normalized quantities needed for MRB.
"""
def run_ou_estimation(spreads: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for pair_label in spreads.columns:
        params = estimate_ou_parameters(spreads[pair_label])
        params["Pair"] = pair_label
        rows.append(params)

    table = pd.DataFrame(rows).set_index("Pair")

    # l_tilde_i: min-max normalize l_star across all pairs (Eq. 23)
    l_min = table["l_star"].min()
    l_max = table["l_star"].max()
    table["l_tilde"] = (table["l_star"] - l_min) / (l_max - l_min)

    # theta_r_i: volatility-scaled speed of reversion (Eq. 24)
    table["theta_r"] = table["theta_star"] / table["sigma_star"]

    return table


def main():
    os.makedirs(config.TABLES_DIR, exist_ok=True)

    print("Loading formation-period spreads...")
    spreads = load_formation_spreads()

    print("\nRunning closed-form OU-MLE estimation for all pairs...")
    results = run_ou_estimation(spreads)
    print(results)

    results_path = os.path.join(config.TABLES_DIR, "ou_estimation_results.csv")
    results.to_csv(results_path)
    print(f"\nSaved -> {results_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()
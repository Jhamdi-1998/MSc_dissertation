"""
allocation.py: Capital Allocation Methods

--
Four allocation scenarios, all producing portfolio weights w_i that feed into the portfolio return R_p,t
"""

import os
import sys

import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config


"""
Loading the daily excess-return
"""
def load_daily_excess_returns() -> pd.DataFrame:
    path = os.path.join(config.PROCESSED_DATA_DIR, "daily_excess_returns.csv")
    return pd.read_csv(path, index_col="Date", parse_dates=True)


"""
Loading OU estimators
"""
def load_ou_results() -> pd.DataFrame:
    path = os.path.join(config.TABLES_DIR, "ou_estimation_results.csv")
    return pd.read_csv(path, index_col="Pair")


"""
Equal-Weight allocation (EW)
"""
def compute_ew_weights(pair_labels: list) -> pd.Series:
    n = len(pair_labels)
    return pd.Series(1.0 / n, index=pair_labels)


"""
Mean-Variance allocation (MVA)
"""
def compute_mva_weights(daily_returns: pd.DataFrame) -> pd.Series:
    R = daily_returns.mean()                 
    Sigma = daily_returns.cov()              

    Sigma_inv = np.linalg.inv(Sigma.values)
    raw_weights = Sigma_inv @ R.values
    weights = raw_weights / raw_weights.sum()  # normalize so sum(w) = 1

    return pd.Series(weights, index=daily_returns.columns)


"""
6.2.3 Mean Reversion Budgeting (MRB). Eq. 23-26.
theta_tilde_i: min-max normalized theta_r_i (Eq. 25).
l_tilde_i: already min-max normalized in ou_estimation.py (Eq. 23).
w_i = theta_tilde_i * l_tilde_i / sum_j(theta_tilde_j * l_tilde_j)
"""
def compute_mrb_weights(ou_results: pd.DataFrame) -> pd.Series:
    theta_r = ou_results["theta_r"]
    theta_tilde = (theta_r - theta_r.min()) / (theta_r.max() - theta_r.min())
    l_tilde = ou_results["l_tilde"]

    scores = theta_tilde * l_tilde
    weights = scores / scores.sum()

    return weights


"""
6.2.4 Mean Reversion Ranking (MRR). Eq. 27.
Rank pairs by theta_tilde_i * l_tilde_i (ascending: lowest score = rank 1).
Weight for rank k (k=1..N): (N-1 + 2*(k-1)) / (2*N*(N-1))
"""
def compute_mrr_weights(ou_results: pd.DataFrame) -> pd.Series:
    theta_r = ou_results["theta_r"]
    theta_tilde = (theta_r - theta_r.min()) / (theta_r.max() - theta_r.min())
    l_tilde = ou_results["l_tilde"]

    scores = theta_tilde * l_tilde
    ranked_pairs = scores.sort_values(ascending=True).index.tolist()  # rank 1 = lowest score

    n = len(ranked_pairs)
    rank_weights = [(n - 1 + 2 * k) / (2 * n * (n - 1)) for k in range(n)]  # k=0..n-1 -> rank 1..N

    weights = pd.Series(rank_weights, index=ranked_pairs)
    return weights.reindex(theta_r.index)  # restore original pair ordering


"""
Computing portfolio-level daily return R_p,t = sum_i w_i * R_i,t (Eq. 10).
"""
def compute_portfolio_returns(daily_returns: pd.DataFrame, weights: pd.Series) -> pd.Series:
    return (daily_returns * weights).sum(axis=1)


"""
Basic performance summary for a portfolio return series.
"""
def summarize_performance(portfolio_returns: pd.Series) -> dict:
    total_return = (1 + portfolio_returns).prod() - 1
    annualized_vol = portfolio_returns.std() * np.sqrt(252)
    sharpe = (portfolio_returns.mean() / portfolio_returns.std()) * np.sqrt(252) if portfolio_returns.std() > 0 else np.nan
    max_drawdown = ((1 + portfolio_returns).cumprod() / (1 + portfolio_returns).cumprod().cummax() - 1).min()

    return {
        "Total Return": total_return,
        "Annualized Volatility": annualized_vol,
        "Sharpe Ratio": sharpe,
        "Max Drawdown": max_drawdown,
    }


def main():
    os.makedirs(config.TABLES_DIR, exist_ok=True)

    print("Loading daily excess returns and OU estimation results...")
    daily_returns = load_daily_excess_returns()
    ou_results = load_ou_results()
    pair_labels = daily_returns.columns.tolist()

    print("\nComputing allocation weights for all four scenarios...\n")

    ew_weights = compute_ew_weights(pair_labels)
    mva_weights = compute_mva_weights(daily_returns)
    mrb_weights = compute_mrb_weights(ou_results)
    mrr_weights = compute_mrr_weights(ou_results)

    weights_table = pd.DataFrame({
        "EW": ew_weights,
        "MVA": mva_weights,
        "MRB": mrb_weights,
        "MRR": mrr_weights,
    })
    print("=== ALLOCATION WEIGHTS ===")
    print(weights_table)

    weights_path = os.path.join(config.TABLES_DIR, "allocation_weights.csv")
    weights_table.to_csv(weights_path)
    print(f"\nSaved -> {weights_path}")

    print("\nComputing portfolio-level performance for each scenario...\n")
    performance_rows = {}
    for scenario_name in ["EW", "MVA", "MRB", "MRR"]:
        weights = weights_table[scenario_name]
        portfolio_returns = compute_portfolio_returns(daily_returns, weights)
        performance_rows[scenario_name] = summarize_performance(portfolio_returns)

    performance_table = pd.DataFrame(performance_rows).T
    print("=== SCENARIO PERFORMANCE COMPARISON ===")
    print(performance_table)

    performance_path = os.path.join(config.TABLES_DIR, "allocation_performance.csv")
    performance_table.to_csv(performance_path)
    print(f"\nSaved -> {performance_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()
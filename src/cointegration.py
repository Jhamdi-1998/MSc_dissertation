"""
cointegration.py - Testing for Cointegration

--
Stage 1: ADF test on log-prices for each stock.
Stage 2: OLS cointegrating regression on log-prices.
Stage 3: ADF test on eps_hat_t using
Output: a results table per pair
"""

import os
import sys

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller, coint
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

"""
Loading the formation-period log-price panel
"""
def load_formation_log_prices() -> pd.DataFrame:
    path = os.path.join(config.PROCESSED_DATA_DIR, "log_prices_formation.csv")
    df = pd.read_csv(path, index_col="Date", parse_dates=True)
    return df

"""
Stage 1:
"""
def adf_precondition_test(series: pd.Series) -> dict:
    result = adfuller(series, regression="c", autolag="AIC")
    stat, pvalue, used_lag, nobs, crit_values, _ = result
    return {
        "ADF Statistic": stat,
        "p-value": pvalue,
        "Lags Used": used_lag,
        "N Obs": nobs,
        "1%": crit_values["1%"],
        "5%": crit_values["5%"],
        "10%": crit_values["10%"],
        "Fails to Reject H0 (unit root, as expected)": pvalue > 0.05,
    }

def run_precondition_tests(log_prices: pd.DataFrame) -> pd.DataFrame:
    rows = {}
    for ticker in config.ALL_TICKERS:
        rows[ticker] = adf_precondition_test(log_prices[ticker])
    table = pd.DataFrame(rows).T
    table.index.name = "Ticker"
    return table

"""
Stage 2:
"""
def engle_granger_step1(log_prices: pd.DataFrame, stock_a: str, stock_b: str):
    y = log_prices[stock_a]
    X = sm.add_constant(log_prices[stock_b])
    model = sm.OLS(y, X).fit()
    alpha_hat = model.params["const"]
    beta_hat = model.params[stock_b]
    residuals = model.resid
    return alpha_hat, beta_hat, residuals

"""
Stage 3:
"""
def engle_granger_step2(log_prices: pd.DataFrame, stock_a: str, stock_b: str) -> dict:
    score, pvalue, crit_values = coint(log_prices[stock_a], log_prices[stock_b])
    return {
        "EG Test Statistic": score,
        "p-value": pvalue,
        "1%": crit_values[0],
        "5%": crit_values[1],
        "10%": crit_values[2],
        "Rejects H0 (cointegrated, as desired)": pvalue < 0.05,
    }

"""
Running the full Engle-Granger tests for all the pairs
"""
def run_cointegration_tests(log_prices: pd.DataFrame):
    summary_rows = {}
    spreads = {}

    for stock_a, stock_b in config.PAIRS:
        pair_label = f"{stock_a}_{stock_b}"

        alpha_hat, beta_hat, residuals = engle_granger_step1(log_prices, stock_a, stock_b)
        step2 = engle_granger_step2(log_prices, stock_a, stock_b)

        summary_rows[pair_label] = {
            "Stock A": stock_a,
            "Stock B": stock_b,
            "alpha_hat": alpha_hat,
            "beta_hat": beta_hat,
            **step2,
        }

        # Spread X_t = log P_A - beta_hat * log P_B, same object as eps_hat_t
        spread = log_prices[stock_a] - beta_hat * log_prices[stock_b]
        spreads[pair_label] = spread

    summary_table = pd.DataFrame(summary_rows).T
    summary_table.index.name = "Pair"
    return summary_table, spreads

"""
Plotting the spread for each pair over the formation period.
"""
def plot_spreads(spreads: dict):
    os.makedirs(config.FIGURES_DIR, exist_ok=True)
    for pair_label, spread in spreads.items():
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(spread.index, spread.values)
        ax.axhline(spread.mean(), color="red", linestyle="--", linewidth=1, label="Mean")
        ax.set_title(f"{pair_label.replace('_', '-')} Spread (Formation Period)")
        ax.set_xlabel("Date")
        ax.set_ylabel("Spread $X_t$")
        ax.legend()
        fig.tight_layout()

        out_path = os.path.join(config.FIGURES_DIR, f"{pair_label}_spread.png")
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        print(f"  saved {out_path}")


def main():
    os.makedirs(config.TABLES_DIR, exist_ok=True)
    os.makedirs(config.FIGURES_DIR, exist_ok=True)

    print("Loading formation-period log prices...")
    log_prices = load_formation_log_prices()

    print("\nStage 1: ADF precondition test on log-price levels (all 12 tickers)...")
    precondition_table = run_precondition_tests(log_prices)
    print(precondition_table)
    precondition_path = os.path.join(config.TABLES_DIR, "adf_precondition_test.csv")
    precondition_table.to_csv(precondition_path)
    print(f"\nSaved -> {precondition_path}")

    n_fail_as_expected = precondition_table["Fails to Reject H0 (unit root, as expected)"].sum()
    print(f"\n{n_fail_as_expected}/{len(config.ALL_TICKERS)} tickers show the expected "
          f"unit-root behaviour (fail to reject H0 at 5%).")

    print("\nStage 2 & 3: Engle-Granger cointegration test on all pairs...")
    summary_table, spreads = run_cointegration_tests(log_prices)
    print(summary_table)
    summary_path = os.path.join(config.TABLES_DIR, "engle_granger_results.csv")
    summary_table.to_csv(summary_path)
    print(f"\nSaved -> {summary_path}")

    n_cointegrated = summary_table["Rejects H0 (cointegrated, as desired)"].sum()
    print(f"\n{n_cointegrated}/{len(config.PAIRS)} pairs confirmed cointegrated at 5%.")
    if n_cointegrated < len(config.PAIRS):
        failed = summary_table[~summary_table["Rejects H0 (cointegrated, as desired)"]].index.tolist()
        print(f"NOT cointegrated (need replacement): {failed}")

    print("\nSaving spread series...")
    spreads_df = pd.DataFrame(spreads)
    spreads_path = os.path.join(config.PROCESSED_DATA_DIR, "spreads_formation.csv")
    spreads_df.to_csv(spreads_path)
    print(f"  saved {spreads_path}")

    print("\nPlotting spreads...")
    plot_spreads(spreads)

    print("\nDone.")


if __name__ == "__main__":
    main()
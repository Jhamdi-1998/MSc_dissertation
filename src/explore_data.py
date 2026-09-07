"""
explore_data.py: In this part we will generate:
  1. A descriptive statistics table (N, Mean, Std Dev, Min, Max) per ticker, over the formation period.
  2. A chart showing each pair's price movements
"""

import os
import sys

import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

"""
Loading the aligned adjusted-close data
"""
def load_formation_adj_close() -> pd.DataFrame:
   
    path = os.path.join(config.PROCESSED_DATA_DIR, "adj_close_formation.csv")
    df = pd.read_csv(path, index_col="Date", parse_dates=True)
    return df

"""
Computing the statistics
"""
def compute_descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
  
    stats = pd.DataFrame({
        "N": df.count(),
        "Mean": df.mean(),
        "Std Dev": df.std(),
        "Min": df.min(),
        "Max": df.max(),
    })
    stats = stats.round(2)
    stats.index.name = "Ticker"
    return stats

def compute_log_returns(log_price_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute daily log returns from a log-price panel:
        r_t = log(P_t) - log(P_t-1)
    First row will be NaN (no prior day to difference against) and is dropped.
    """
    returns = log_price_df.diff().dropna(how="all")
    return returns


def compute_return_stats(returns_df: pd.DataFrame) -> pd.DataFrame:
    """
    Descriptive statistics on daily log returns: N, Mean, Std Dev, Min, Max.
    """
    stats = pd.DataFrame({
        "N": returns_df.count(),
        "Mean": returns_df.mean(),
        "Std Dev": returns_df.std(),
        "Min": returns_df.min(),
        "Max": returns_df.max(),
    })
    stats.index.name = "Ticker"
    return stats

"""
Plotting the graphs for each pair.
"""
def plot_pairs(df: pd.DataFrame):

    os.makedirs(config.FIGURES_DIR, exist_ok=True)

    for stock_a, stock_b in config.PAIRS:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(df.index, df[stock_a], label=stock_a)
        ax.plot(df.index, df[stock_b], label=stock_b)
        ax.set_title(f"{stock_a} vs {stock_b} - Adjusted Close (Formation Period)")
        ax.set_xlabel("Date")
        ax.set_ylabel("Adjusted Close Price ($)")
        ax.legend()
        fig.tight_layout()

        out_path = os.path.join(config.FIGURES_DIR, f"{stock_a}_{stock_b}_prices.png")
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        print(f"  saved {out_path}")


def main():
    os.makedirs(config.TABLES_DIR, exist_ok=True)

    print("Loading formation-period adjusted close prices...")
    df = load_formation_adj_close()

    print("\nComputing descriptive statistics (price levels, formation period)...")
    stats = compute_descriptive_stats(df)
    print(stats)

    stats_path = os.path.join(config.TABLES_DIR, "descriptive_stats.csv")
    stats.to_csv(stats_path)
    print(f"\nSaved price-level descriptive stats table -> {stats_path}")

    # Returns-based table - formation + trading period
    print("\nLoading full log-price panel (2021-2022)...")
    log_price_path = os.path.join(config.PROCESSED_DATA_DIR, "log_prices_full.csv")
    log_prices = pd.read_csv(log_price_path, index_col="Date", parse_dates=True)

    print("Computing daily log returns...")
    log_returns = compute_log_returns(log_prices)

    print("\nComputing descriptive statistics (log returns, full sample)...")
    return_stats = compute_return_stats(log_returns)
    print(return_stats)

    return_stats_path = os.path.join(config.TABLES_DIR, "descriptive_stats_returns.csv")
    return_stats.to_csv(return_stats_path)
    print(f"\nSaved return-based descriptive stats table -> {return_stats_path}")

    print("\nPlotting pairs...")
    plot_pairs(df)

    print("\nDone.")


if __name__ == "__main__":
    main()
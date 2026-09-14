"""
explore_data.py: In this part we will generate: A descriptive statistics table (N, Mean, Std Dev, Min, Max) per ticker, over the formation period.
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
    returns = log_price_df.diff().dropna(how="all")
    return returns


def compute_return_stats(returns_df: pd.DataFrame) -> pd.DataFrame:
    stats = pd.DataFrame({
        "N": returns_df.count(),
        "Mean": returns_df.mean(),
        "Std Dev": returns_df.std(),
        "Min": returns_df.min(),
        "Max": returns_df.max(),
    })
    stats.index.name = "Ticker"
    return stats


def main():
    os.makedirs(config.TABLES_DIR, exist_ok=True)
    df = load_formation_adj_close()
    stats = compute_descriptive_stats(df)
    print(stats)
    stats_path = os.path.join(config.TABLES_DIR, "descriptive_stats.csv")
    stats.to_csv(stats_path)
    print(f"\nSaved descriptive stats table -> {stats_path}")
    log_price_path = os.path.join(config.PROCESSED_DATA_DIR, "log_prices_full.csv")
    log_prices = pd.read_csv(log_price_path, index_col="Date", parse_dates=True)
    log_returns = compute_log_returns(log_prices)
    return_stats = compute_return_stats(log_returns)
    print(return_stats)
    return_stats_path = os.path.join(config.TABLES_DIR, "descriptive_stats_returns.csv")
    return_stats.to_csv(return_stats_path)
    print(f"\ntable saved-> {return_stats_path}")
    print("\nDone.")

if __name__ == "__main__":
    main()
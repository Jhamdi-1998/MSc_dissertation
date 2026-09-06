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

    print("\nComputing descriptive statistics...")
    stats = compute_descriptive_stats(df)
    print(stats)

    stats_path = os.path.join(config.TABLES_DIR, "descriptive_stats.csv")
    stats.to_csv(stats_path)
    print(f"\nSaved descriptive stats table -> {stats_path}")

    print("\nPlotting pairs...")
    plot_pairs(df)

    print("\nDone.")


if __name__ == "__main__":
    main()
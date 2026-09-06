"""
build_dataset.py: here we extract, clean and then get the logs of our adj closing prices.

--
Stage 1: Here we extract the adj closing prices over the formation + trading window and save them into CSVs.
"""

import os
import sys
import time

import pandas as pd
import numpy as np
import yfinance as yf

# importing config.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

"""
    Downloading adjusted close prices for a single ticker.
"""
def fetch_ticker(ticker: str, start: str, end: str, max_retries: int = 3) -> pd.DataFrame:
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            df = yf.download(
                ticker,
                start=start,
                end=end,
                auto_adjust=False,
                progress=False,
            )
            if df.empty:
                raise ValueError(f"No data returned for {ticker}")

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df = df[["Adj Close", "Close", "Volume"]].copy()
            df.index.name = "Date"
            return df

        except Exception as e:
            last_error = e
            print(f"  [{ticker}] attempt {attempt}/{max_retries} failed: {e}")
            time.sleep(1.5 * attempt)

    raise RuntimeError(f"Failed to fetch {ticker} after {max_retries} attempts: {last_error}")


def pull_all_tickers():
    os.makedirs(config.RAW_DATA_DIR, exist_ok=True)

    print(f"Pulling {len(config.ALL_TICKERS)} tickers "
          f"from {config.PULL_START} to {config.PULL_END}\n")

    failures = []
    for ticker in config.ALL_TICKERS:
        print(f"Fetching {ticker}...")
        try:
            df = fetch_ticker(ticker, config.PULL_START, config.PULL_END)
            out_path = os.path.join(config.RAW_DATA_DIR, f"{ticker}.csv")
            df.to_csv(out_path)
            print(f"  saved {len(df)} rows -> {out_path}")
        except RuntimeError as e:
            print(f"  FAILED: {e}")
            failures.append(ticker)

    print()
    if failures:
        print(f"Completed with {len(failures)} failure(s): {failures}")
    else:
        print("All tickers pulled successfully.")
    return failures

"""
Stage 2: processing the extracted data and getting the log adj closing prices

--
We start off by combining all the extracted data from the CSV to have one database with the asj cloding prices
from all the tickers
"""

def load_raw_adj_close() -> pd.DataFrame:
    series_by_ticker = {}
    for ticker in config.ALL_TICKERS:
        path = os.path.join(config.RAW_DATA_DIR, f"{ticker}.csv")
        df = pd.read_csv(path, index_col="Date", parse_dates=True)
        series_by_ticker[ticker] = df["Adj Close"]

    panel = pd.DataFrame(series_by_ticker)
    panel = panel.sort_index()
    return panel

"""
As per our methodology, we make sure that there is no forward-filling in our data.
"""
def align_panel(panel: pd.DataFrame) -> pd.DataFrame:
    before = len(panel)
    aligned = panel.dropna(how="any")
    after = len(aligned)
    dropped = before - after
    print(f"Alignment: {before} rows -> {after} rows ({dropped} dropped due to missing data)")
    return aligned

"""
Spliting inot formation and trading period
"""
def split_by_period(df: pd.DataFrame):
    formation = df.loc[config.FORMATION_START:config.FORMATION_END]
    trading = df.loc[config.TRADING_START:config.TRADING_END]
    return formation, trading

"""
Building the cleaned dataset
"""
def build_processed_dataset():
    os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)

    print("\nStage 2: loading raw data and aligning...")
    raw_panel = load_raw_adj_close()
    aligned_panel = align_panel(raw_panel)

    log_panel = np.log(aligned_panel)

    adj_formation, adj_trading = split_by_period(aligned_panel)
    log_formation, log_trading = split_by_period(log_panel)

    aligned_panel.to_csv(os.path.join(config.PROCESSED_DATA_DIR, "adj_close_full.csv"))
    log_panel.to_csv(os.path.join(config.PROCESSED_DATA_DIR, "log_prices_full.csv"))

    # Save period-split versions (useful for formation-only / trading-only work)
    adj_formation.to_csv(os.path.join(config.PROCESSED_DATA_DIR, "adj_close_formation.csv"))
    adj_trading.to_csv(os.path.join(config.PROCESSED_DATA_DIR, "adj_close_trading.csv"))
    log_formation.to_csv(os.path.join(config.PROCESSED_DATA_DIR, "log_prices_formation.csv"))
    log_trading.to_csv(os.path.join(config.PROCESSED_DATA_DIR, "log_prices_trading.csv"))

    print(f"Formation period: {len(adj_formation)} rows "
          f"({config.FORMATION_START} to {config.FORMATION_END})")
    print(f"Trading period:   {len(adj_trading)} rows "
          f"({config.TRADING_START} to {config.TRADING_END})")
    print(f"\nStage 2: processed files saved to {config.PROCESSED_DATA_DIR}/")

def main():
    failures = pull_all_tickers()
    if failures:
        print(f"\nAborting Stage 2 - fix failed ticker(s) first: {failures}")
        return

    build_processed_dataset()


if __name__ == "__main__":
    main()
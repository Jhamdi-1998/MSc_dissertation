"""
build_dataset.py: here we extract, clean and then get the logs of our adj closing prices.

--
Stage 1: Here we extract the adj closing prices over the formation + trading window and save them into CSVs.
"""

import os
import sys
import time

import pandas as pd
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


def main():
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


if __name__ == "__main__":
    main()
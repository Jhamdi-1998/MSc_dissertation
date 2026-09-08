"""
trading_rules.py: Section 5.4 - Trading Rules

--
Z-score: Zt = (Xt - mu_hat_s) / sigma_hat_s, using the FORMATION-period
         sample mean/std of the spread (mu_hat_s, sigma_hat_s), applied
         to the trading-period spread (GGR, 2006).

Entry:   |Zt| > k = 2 (GGR, 2006; Krauss, 2017). Long the spread
         (buy 1 unit of A, short beta_hat units of B) when Zt < -k.
         Short the spread when Zt > +k.

Exit:    position closes when Zt reverts to 0 (GGR, 2006).

Stop-loss: 7% realised loss on committed capital, checked against
           cumulative P&L since entry (Caldeira & Moura, 2013).

Forced closure: any position still open at the end of the trading
                period is closed (GGR, 2006).

Committed capital convention: since the position Xt = log P_A,t - beta_hat * log P_B,t
is built in log-price space, we use a fixed notional C_i per pair
(C_i = 100), with daily position value change approximated as
Delta V_i,t = C_i * Delta X_t * position_sign. This matches GGR (2006)'s
committed capital convention (fixed notional per pair regardless of each
stock's raw share price), which keeps excess returns comparable in scale
across all six pairs for the allocation methods in Section 6.
"""

import os
import sys

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

K_ENTRY = 2.0          # entry threshold, in standard deviations (GGR, 2006; Krauss, 2017)
STOP_LOSS_PCT = 0.07   # 7% of committed capital (Caldeira & Moura, 2013)
COMMITTED_CAPITAL = 100.0  # fixed notional per pair (C_i), GGR (2006) convention


"""
Loading formation-period spread stats (mu_hat_s, sigma_hat_s) per pair,
from the spreads already saved by cointegration.py.
"""
def load_formation_spread_stats() -> dict:
    path = os.path.join(config.PROCESSED_DATA_DIR, "spreads_formation.csv")
    spreads = pd.read_csv(path, index_col="Date", parse_dates=True)
    stats = {}
    for pair_label in spreads.columns:
        stats[pair_label] = {
            "mu_hat_s": spreads[pair_label].mean(),
            "sigma_hat_s": spreads[pair_label].std(),
        }
    return stats


"""
Loading beta_hat per pair from the Engle-Granger results table.
"""
def load_beta_hats() -> dict:
    path = os.path.join(config.TABLES_DIR, "engle_granger_results.csv")
    eg_results = pd.read_csv(path, index_col="Pair")
    return eg_results["beta_hat"].to_dict()


"""
Loading trading-period log prices.
"""
def load_trading_log_prices() -> pd.DataFrame:
    path = os.path.join(config.PROCESSED_DATA_DIR, "log_prices_trading.csv")
    df = pd.read_csv(path, index_col="Date", parse_dates=True)
    return df


"""
Building the trading-period spread X_t, using the beta_hat FIXED at
formation (not re-estimated on trading data).
"""
def build_trading_spread(log_prices: pd.DataFrame, stock_a: str, stock_b: str, beta_hat: float) -> pd.Series:
    return log_prices[stock_a] - beta_hat * log_prices[stock_b]


"""
Running the trading simulation for a single pair over the trading period.
Returns a trade log (list of dicts) and a daily excess-return series
r_i,t (per Section 5.2, Eq. 2: Delta V_i,t / C_i on days the pair is open, else 0).
"""
def simulate_pair_trading(pair_label: str, spread: pd.Series, mu_hat_s: float, sigma_hat_s: float) -> tuple:
    z_scores = (spread - mu_hat_s) / sigma_hat_s

    trade_log = []
    daily_returns = pd.Series(0.0, index=spread.index)

    position_open = False
    position_sign = 0       # +1 = long the spread, -1 = short the spread
    entry_date = None
    entry_spread_value = None
    cumulative_pnl = 0.0

    dates = spread.index

    for i, date in enumerate(dates):
        z_t = z_scores.loc[date]

        if not position_open:
            # Check entry condition
            if z_t < -K_ENTRY:
                position_open = True
                position_sign = 1  # long the spread
                entry_date = date
                entry_spread_value = spread.loc[date]
                cumulative_pnl = 0.0
            elif z_t > K_ENTRY:
                position_open = True
                position_sign = -1  # short the spread
                entry_date = date
                entry_spread_value = spread.loc[date]
                cumulative_pnl = 0.0

        else:
            # Position is open - compute today's P&L contribution
            if i > 0:
                prev_date = dates[i - 1]
                delta_x = spread.loc[date] - spread.loc[prev_date]
                delta_v = COMMITTED_CAPITAL * delta_x * position_sign
                daily_returns.loc[date] = delta_v / COMMITTED_CAPITAL  # r_i,t = Delta V_i,t / C_i
                cumulative_pnl += delta_v

            exit_reason = None

            # Exit condition 1: reversion to zero
            if (position_sign == 1 and z_t >= 0) or (position_sign == -1 and z_t <= 0):
                exit_reason = "reversion"

            # Exit condition 2: stop-loss (7% of committed capital)
            elif cumulative_pnl <= -STOP_LOSS_PCT * COMMITTED_CAPITAL:
                exit_reason = "stop_loss"

            # Exit condition 3: forced closure at end of trading period
            elif date == dates[-1]:
                exit_reason = "forced_closure"

            if exit_reason is not None:
                trade_log.append({
                    "Pair": pair_label,
                    "Entry Date": entry_date,
                    "Exit Date": date,
                    "Direction": "Long Spread" if position_sign == 1 else "Short Spread",
                    "Entry Spread": entry_spread_value,
                    "Exit Spread": spread.loc[date],
                    "P&L ($)": round(cumulative_pnl, 4),
                    "Return on Committed Capital": round(cumulative_pnl / COMMITTED_CAPITAL, 4),
                    "Exit Reason": exit_reason,
                })
                position_open = False
                position_sign = 0
                entry_date = None
                entry_spread_value = None
                cumulative_pnl = 0.0

    return trade_log, daily_returns


"""
Plotting z-score with entry/exit markers for a pair.
"""
def plot_zscore_trades(pair_label: str, spread: pd.Series, mu_hat_s: float, sigma_hat_s: float, trade_log: list):
    z_scores = (spread - mu_hat_s) / sigma_hat_s

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(z_scores.index, z_scores.values, label="Z-score", linewidth=1)
    ax.axhline(K_ENTRY, color="red", linestyle="--", linewidth=1, label=f"+/- k = {K_ENTRY}")
    ax.axhline(-K_ENTRY, color="red", linestyle="--", linewidth=1)
    ax.axhline(0, color="black", linestyle="-", linewidth=0.8)

    pair_trades = [t for t in trade_log if t["Pair"] == pair_label]
    for trade in pair_trades:
        entry_z = z_scores.loc[trade["Entry Date"]]
        exit_z = z_scores.loc[trade["Exit Date"]]
        color = "green" if trade["P&L ($)"] >= 0 else "red"
        ax.scatter(trade["Entry Date"], entry_z, color="blue", marker="^", zorder=5)
        ax.scatter(trade["Exit Date"], exit_z, color=color, marker="v", zorder=5)

    ax.set_title(f"{pair_label.replace('_', '-')} Z-score with Trade Entries/Exits (Trading Period)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Z-score")
    ax.legend()
    fig.tight_layout()

    out_path = os.path.join(config.FIGURES_DIR, f"{pair_label}_zscore_trades.png")
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  saved {out_path}")


def main():
    os.makedirs(config.TABLES_DIR, exist_ok=True)
    os.makedirs(config.FIGURES_DIR, exist_ok=True)

    print("Loading formation-period spread stats (mu_hat_s, sigma_hat_s)...")
    formation_stats = load_formation_spread_stats()

    print("Loading beta_hat per pair...")
    beta_hats = load_beta_hats()

    print("Loading trading-period log prices...")
    trading_log_prices = load_trading_log_prices()

    all_trade_logs = []
    all_daily_returns = {}

    for stock_a, stock_b in config.PAIRS:
        pair_label = f"{stock_a}_{stock_b}"
        print(f"\nSimulating trading for {pair_label}...")

        beta_hat = beta_hats[pair_label]
        mu_hat_s = formation_stats[pair_label]["mu_hat_s"]
        sigma_hat_s = formation_stats[pair_label]["sigma_hat_s"]

        trading_spread = build_trading_spread(trading_log_prices, stock_a, stock_b, beta_hat)

        trade_log, daily_returns = simulate_pair_trading(pair_label, trading_spread, mu_hat_s, sigma_hat_s)

        print(f"  {len(trade_log)} trade(s) closed")
        for t in trade_log:
            print(f"    {t['Entry Date'].date()} -> {t['Exit Date'].date()} | "
                  f"{t['Direction']} | P&L: ${t['P&L ($)']} | Reason: {t['Exit Reason']}")

        all_trade_logs.extend(trade_log)
        all_daily_returns[pair_label] = daily_returns

        plot_zscore_trades(pair_label, trading_spread, mu_hat_s, sigma_hat_s, trade_log)

    # Save trade log
    trade_log_df = pd.DataFrame(all_trade_logs)
    trade_log_path = os.path.join(config.TABLES_DIR, "trade_log.csv")
    trade_log_df.to_csv(trade_log_path, index=False)
    print(f"\nSaved trade log -> {trade_log_path}")

    # Save daily excess-return series (r_i,t)
    daily_returns_df = pd.DataFrame(all_daily_returns)
    daily_returns_path = os.path.join(config.PROCESSED_DATA_DIR, "daily_excess_returns.csv")
    daily_returns_df.to_csv(daily_returns_path)
    print(f"Saved daily excess returns -> {daily_returns_path}")

    # Summary
    print("\n=== SUMMARY ===")
    summary_rows = []
    for stock_a, stock_b in config.PAIRS:
        pair_label = f"{stock_a}_{stock_b}"
        pair_trades = trade_log_df[trade_log_df["Pair"] == pair_label] if len(trade_log_df) > 0 else pd.DataFrame()
        n_trades = len(pair_trades)
        n_stop_loss = (pair_trades["Exit Reason"] == "stop_loss").sum() if n_trades > 0 else 0
        n_forced = (pair_trades["Exit Reason"] == "forced_closure").sum() if n_trades > 0 else 0
        n_reversion = (pair_trades["Exit Reason"] == "reversion").sum() if n_trades > 0 else 0
        total_return = pair_trades["Return on Committed Capital"].sum() if n_trades > 0 else 0.0

        summary_rows.append({
            "Pair": pair_label,
            "N Trades": n_trades,
            "N Reversion Exits": n_reversion,
            "N Stop-Loss Exits": n_stop_loss,
            "N Forced Closures": n_forced,
            "Total Return on Committed Capital": round(total_return, 4),
        })

    summary_df = pd.DataFrame(summary_rows).set_index("Pair")
    print(summary_df)
    summary_path = os.path.join(config.TABLES_DIR, "trading_summary.csv")
    summary_df.to_csv(summary_path)
    print(f"\nSaved -> {summary_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()
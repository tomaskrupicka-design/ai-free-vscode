from __future__ import annotations

import numpy as np
import pandas as pd

from .backtest import run_backtest
from .radar import add_radar_score, latest_radar_snapshot
from .regime import add_market_regime
from .report import print_summary, summarize_backtest
from .signals import add_trend_signal


def make_synthetic_data(rows: int = 600, seed: int = 7) -> pd.DataFrame:
    """Create deterministic synthetic prices for development/testing only."""
    rng = np.random.default_rng(seed)
    daily_returns = rng.normal(loc=0.00025, scale=0.012, size=rows)
    close = 100.0 * np.cumprod(1.0 + daily_returns)
    dates = pd.date_range("2024-01-01", periods=rows, freq="D")
    return pd.DataFrame({"date": dates, "close": close}).set_index("date")


def main() -> None:
    data = make_synthetic_data()
    data = add_market_regime(data, fast_window=20, slow_window=100, vol_window=20)
    data = add_trend_signal(data, fast_window=20, slow_window=100)
    data = add_radar_score(data)

    tested, result = run_backtest(data)
    summary = summarize_backtest(tested, result)
    radar = latest_radar_snapshot(data)

    print("Trading Research Agent v1 — synthetic demo")
    print_summary(summary)
    print("\n=== Latest Radar ===")
    print(f"Score:   {radar['score']:.1f}")
    print(f"Signal:  {radar['signal']}")
    print(f"Reason:  {radar['reason']}")
    print(f"Parts:   {radar['components']}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import numpy as np
import pandas as pd

from .backtest import run_backtest
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
    data = add_trend_signal(data, fast_window=20, slow_window=100)
    result = run_backtest(data)

    print("Trading Research Agent v1 — synthetic demo")
    print(f"Total return:      {result.total_return:.2%}")
    print(f"Max drawdown:      {result.max_drawdown:.2%}")
    print(f"Position changes:  {result.position_changes}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import pandas as pd


def add_trend_signal(
    frame: pd.DataFrame,
    fast_window: int = 20,
    slow_window: int = 100,
) -> pd.DataFrame:
    """Add a simple moving-average trend signal.

    signal values:
      1  = hypothetical LONG bias
      0  = WAIT / neutral
     -1  = hypothetical SHORT bias
    """
    if "close" not in frame.columns:
        raise ValueError("Input data must contain a 'close' column.")
    if fast_window <= 1 or slow_window <= 1 or fast_window >= slow_window:
        raise ValueError("Require 1 < fast_window < slow_window.")

    out = frame.copy()
    out["sma_fast"] = out["close"].rolling(fast_window).mean()
    out["sma_slow"] = out["close"].rolling(slow_window).mean()

    out["signal"] = 0
    out.loc[out["sma_fast"] > out["sma_slow"], "signal"] = 1
    out.loc[out["sma_fast"] < out["sma_slow"], "signal"] = -1
    return out

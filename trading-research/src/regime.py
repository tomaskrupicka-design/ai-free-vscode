from __future__ import annotations

import pandas as pd


def add_market_regime(
    frame: pd.DataFrame,
    fast_window: int = 20,
    slow_window: int = 100,
    vol_window: int = 20,
) -> pd.DataFrame:
    """Add simple trend/range and volatility regime labels."""
    if "close" not in frame.columns:
        raise ValueError("Input data must contain a 'close' column.")

    out = frame.copy()
    returns = out["close"].pct_change()

    out["sma_fast"] = out["close"].rolling(fast_window).mean()
    out["sma_slow"] = out["close"].rolling(slow_window).mean()
    out["rolling_vol"] = returns.rolling(vol_window).std()

    spread = (out["sma_fast"] / out["sma_slow"] - 1.0).abs()
    spread_threshold = spread.rolling(slow_window).median()

    out["trend_regime"] = "unknown"
    out.loc[spread <= spread_threshold, "trend_regime"] = "range"
    out.loc[spread > spread_threshold, "trend_regime"] = "trend"

    vol_threshold = out["rolling_vol"].rolling(slow_window).median()
    out["vol_regime"] = "unknown"
    out.loc[out["rolling_vol"] <= vol_threshold, "vol_regime"] = "low"
    out.loc[out["rolling_vol"] > vol_threshold, "vol_regime"] = "high"

    return out

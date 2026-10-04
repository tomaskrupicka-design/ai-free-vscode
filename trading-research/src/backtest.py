from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class BacktestResult:
    total_return: float
    max_drawdown: float
    position_changes: int
    equity_curve: pd.Series


def run_backtest(frame: pd.DataFrame) -> tuple[pd.DataFrame, BacktestResult]:
    """Run a minimal close-to-close research backtest.

    The signal is shifted by one bar to reduce look-ahead bias.
    No leverage, brokerage integration, or live execution is used.
    """
    required = {"close", "signal"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    data = frame.copy()
    data["market_return"] = data["close"].pct_change().fillna(0.0)
    data["position"] = data["signal"].shift(1).fillna(0.0)
    data["strategy_return"] = data["position"] * data["market_return"]

    equity = (1.0 + data["strategy_return"]).cumprod()
    running_peak = equity.cummax()
    drawdown = equity / running_peak - 1.0

    changes = int(data["position"].diff().fillna(0).ne(0).sum())

    result = BacktestResult(
        total_return=float(equity.iloc[-1] - 1.0),
        max_drawdown=float(drawdown.min()),
        position_changes=changes,
        equity_curve=equity,
    )
    return data, result

from __future__ import annotations

from typing import Any

import pandas as pd

from .backtest import BacktestResult


def summarize_backtest(
    frame: pd.DataFrame,
    result: BacktestResult,
) -> dict[str, Any]:
    """Create a compact research summary with regime statistics."""
    summary: dict[str, Any] = {
        "total_return": result.total_return,
        "max_drawdown": result.max_drawdown,
        "position_changes": result.position_changes,
    }

    if {"trend_regime", "vol_regime", "strategy_return"}.issubset(frame.columns):
        by_trend = (
            frame.groupby("trend_regime")["strategy_return"]
            .agg(["count", "mean", "sum"])
            .to_dict("index")
        )
        by_vol = (
            frame.groupby("vol_regime")["strategy_return"]
            .agg(["count", "mean", "sum"])
            .to_dict("index")
        )
        summary["by_trend_regime"] = by_trend
        summary["by_vol_regime"] = by_vol

    return summary


def print_summary(summary: dict[str, Any]) -> None:
    print("=== Research Summary ===")
    print(f"Total return:     {summary['total_return']:.2%}")
    print(f"Max drawdown:     {summary['max_drawdown']:.2%}")
    print(f"Position changes: {summary['position_changes']}")

    for key, title in [
        ("by_trend_regime", "By trend regime"),
        ("by_vol_regime", "By volatility regime"),
    ]:
        if key not in summary:
            continue
        print(f"\n{title}:")
        for regime, stats in summary[key].items():
            print(
                f"  {regime:>8} | n={int(stats['count'])}"
                f" | mean={stats['mean']:.6f}"
                f" | sum={stats['sum']:.4f}"
            )

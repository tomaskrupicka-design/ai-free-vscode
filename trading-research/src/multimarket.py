from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

from .backtest import BacktestResult, run_backtest
from .data import load_price_csv
from .radar import add_radar_score, latest_radar_snapshot
from .regime import add_market_regime
from .report import summarize_backtest
from .signals import add_trend_signal


@dataclass(frozen=True)
class MarketResearchResult:
    symbol: str
    rows: int
    latest_close: float
    radar_score: float
    radar_signal: str
    radar_reason: str
    total_return: float
    max_drawdown: float
    position_changes: int


def analyze_market(symbol: str, frame: pd.DataFrame) -> tuple[pd.DataFrame, MarketResearchResult]:
    """Run the full research pipeline for one market."""
    if frame.empty:
        raise ValueError(f"{symbol}: input frame is empty.")

    data = add_market_regime(frame, fast_window=20, slow_window=100, vol_window=20)
    data = add_trend_signal(data, fast_window=20, slow_window=100)
    data = add_radar_score(data)

    tested, result = run_backtest(data)
    radar = latest_radar_snapshot(data)

    market_result = MarketResearchResult(
        symbol=symbol,
        rows=len(data),
        latest_close=float(data["close"].iloc[-1]),
        radar_score=float(radar["score"]),
        radar_signal=str(radar["signal"]),
        radar_reason=str(radar["reason"]),
        total_return=result.total_return,
        max_drawdown=result.max_drawdown,
        position_changes=result.position_changes,
    )
    return tested, market_result


def analyze_csv_markets(
    market_files: dict[str, str | Path],
) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    """Analyze several markets from CSV files.

    Example:
        {
            "ES": "sample-data/ES.csv",
            "NQ": "sample-data/NQ.csv",
        }
    """
    details: dict[str, pd.DataFrame] = {}
    rows: list[dict[str, object]] = []

    for symbol, path in market_files.items():
        frame = load_price_csv(path)
        tested, result = analyze_market(symbol, frame)
        details[symbol] = tested
        rows.append(
            {
                "symbol": result.symbol,
                "rows": result.rows,
                "latest_close": result.latest_close,
                "radar_score": result.radar_score,
                "radar_signal": result.radar_signal,
                "radar_reason": result.radar_reason,
                "total_return": result.total_return,
                "max_drawdown": result.max_drawdown,
                "position_changes": result.position_changes,
            }
        )

    summary = pd.DataFrame(rows)
    if not summary.empty:
        summary = summary.sort_values(
            by=["radar_score", "symbol"],
            ascending=[False, True],
        ).reset_index(drop=True)
    return details, summary

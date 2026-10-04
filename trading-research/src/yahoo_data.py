from __future__ import annotations

from pathlib import Path

import pandas as pd
import yfinance as yf


YAHOO_FUTURES = {
    "ES": "ES=F",
    "NQ": "NQ=F",
    "GC": "GC=F",
    "CL": "CL=F",
}


def download_history(
    symbol: str,
    *,
    period: str = "5y",
    interval: str = "1d",
) -> pd.DataFrame:
    """Download historical Yahoo Finance data for research/backtesting only."""
    if symbol not in YAHOO_FUTURES:
        raise ValueError(
            f"Unsupported symbol {symbol!r}. "
            f"Choose from {sorted(YAHOO_FUTURES)}."
        )

    ticker = YAHOO_FUTURES[symbol]
    raw = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
        threads=False,
        multi_level_index=False,
    )

    if raw.empty:
        raise RuntimeError(f"No historical data returned for {symbol} ({ticker}).")

    frame = raw.reset_index()
    frame.columns = [str(c).lower().replace(" ", "_") for c in frame.columns]

    date_col = "date" if "date" in frame.columns else "datetime"
    if date_col not in frame.columns:
        raise RuntimeError("Downloaded data has no date/datetime column.")

    frame = frame.rename(columns={date_col: "date", "adj_close": "adj_close"})
    wanted = [c for c in ["date", "open", "high", "low", "close", "volume"] if c in frame]
    frame = frame[wanted].copy()
    frame["date"] = pd.to_datetime(frame["date"], utc=True, errors="raise")
    frame = frame.dropna(subset=["close"]).sort_values("date").drop_duplicates("date")

    for column in [c for c in ["open", "high", "low", "close", "volume"] if c in frame]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    frame = frame.dropna(subset=["close"]).set_index("date")
    return frame


def save_history_csv(
    symbol: str,
    destination: str | Path,
    *,
    period: str = "5y",
    interval: str = "1d",
) -> Path:
    """Download and save historical research data to CSV."""
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = download_history(symbol, period=period, interval=interval)
    frame.reset_index().to_csv(path, index=False)
    return path

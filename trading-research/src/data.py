from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"date", "close"}


def load_price_csv(path: str | Path) -> pd.DataFrame:
    """Load historical price data from a CSV file.

    Required columns:
      - date
      - close

    Optional columns:
      - open
      - high
      - low
      - volume
    """
    frame = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(frame.columns.str.lower())
    if missing:
        raise ValueError(f"Missing required CSV columns: {sorted(missing)}")

    frame.columns = [str(c).lower() for c in frame.columns]
    frame["date"] = pd.to_datetime(frame["date"], utc=True, errors="raise")
    frame = frame.sort_values("date").drop_duplicates("date").set_index("date")

    numeric_columns = [
        c for c in ["open", "high", "low", "close", "volume"] if c in frame.columns
    ]
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="raise")

    if frame["close"].isna().any():
        raise ValueError("Close column contains missing values.")
    if (frame["close"] <= 0).any():
        raise ValueError("Close prices must be positive.")

    return frame

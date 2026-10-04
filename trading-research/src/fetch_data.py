from __future__ import annotations

from pathlib import Path

from .yahoo_data import YAHOO_FUTURES, save_history_csv


def main() -> None:
    base = Path(__file__).resolve().parents[1] / "sample-data"

    print("Downloading historical research data...")
    for symbol in YAHOO_FUTURES:
        target = base / f"{symbol}.csv"
        try:
            path = save_history_csv(symbol, target, period="5y", interval="1d")
            print(f"  {symbol}: saved to {path}")
        except Exception as exc:
            print(f"  {symbol}: failed: {exc}")

    print("\nHistorical data only. No live trading or order execution is performed.")


if __name__ == "__main__":
    main()

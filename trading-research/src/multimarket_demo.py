from __future__ import annotations

from pathlib import Path

from .multimarket import analyze_csv_markets


def main() -> None:
    base = Path(__file__).resolve().parents[1] / "sample-data"
    market_files = {
        "ES": base / "ES.csv",
        "NQ": base / "NQ.csv",
        "GC": base / "GC.csv",
        "CL": base / "CL.csv",
    }

    missing = [str(path) for path in market_files.values() if not path.exists()]
    if missing:
        print("Multi-market demo is ready, but historical CSV files are missing.")
        print("Expected files:")
        for path in missing:
            print(f"  - {path}")
        print("\nSee sample-data/README.md for the required CSV format.")
        return

    _, summary = analyze_csv_markets(market_files)

    print("=== Multi-Market Radar ===")
    if summary.empty:
        print("No markets analyzed.")
        return

    display = summary[
        [
            "symbol",
            "latest_close",
            "radar_score",
            "radar_signal",
            "total_return",
            "max_drawdown",
            "position_changes",
        ]
    ]
    print(display.to_string(index=False))


if __name__ == "__main__":
    main()

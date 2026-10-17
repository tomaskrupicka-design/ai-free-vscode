"""Import real historical fixtures from a user-supplied CSV; never invent match results."""
import argparse
from pathlib import Path
import pandas as pd

REQUIRED = ["date", "home_team", "away_team", "home_goals", "away_goals"]

def import_matches(source, destination):
    df = pd.read_csv(source)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    df = df[REQUIRED].copy()
    df["date"] = pd.to_datetime(df["date"], errors="raise", utc=True)
    for col in ("home_goals", "away_goals"):
        df[col] = pd.to_numeric(df[col], errors="raise").astype(int)
        if (df[col] < 0).any():
            raise ValueError("Negative goals")
    if df[["home_team", "away_team"]].isna().any().any():
        raise ValueError("Missing team")
    df = df.sort_values("date")
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destination, index=False)
    return len(df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("--output", default="data/matches.csv")
    args = parser.parse_args()
    print(f"Imported {import_matches(args.source, args.output)} fixtures")

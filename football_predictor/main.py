"""Historická analýza fotbalových zápasů, bez kurzů a sázení."""
import argparse
from pathlib import Path
import pandas as pd
from evaluation.backtest import backtest
from storage import save_predictions

ROOT = Path(__file__).resolve().parent

def run(real=False, fetch=False, sync_supabase=False):
    if fetch and not real:
        raise ValueError("--fetch vyžaduje také --real")
    if sync_supabase and not real:
        raise ValueError("Supabase ukládání je povoleno pouze pro skutečná data (--real).")
    input_file = ROOT / "data" / ("matches_real.csv" if real else "matches.csv")
    output_file = ROOT / "output" / ("predictions_real.csv" if real else "predictions.csv")
    if fetch:
        from data.openfootball import refresh
        count, warnings = refresh(input_file)
        print(f"OpenFootball: načteno {count} skutečných historických výsledků.")
        if warnings:
            print("Varování:", "; ".join(warnings))
    if real and not input_file.exists():
        raise FileNotFoundError("Chybí skutečná data. Spusť: python main.py --real --fetch")
    matches = pd.read_csv(input_file, parse_dates=["date"])
    if matches.empty:
        raise ValueError("Dataset je prázdný.")
    results = backtest(matches)
    df = save_predictions(results, output_file)
    print(f"Zápasy: {len(df)}; Brier: {df.brier.mean():.4f}; log-loss: {df.log_loss.mean():.4f}")
    print("Výstup:", output_file)
    if sync_supabase:
        from database.supabase_sync import sync
        n_matches, n_predictions = sync(df, matches)
        print(f"Supabase: {n_matches} zápasů, {n_predictions} retrospektivních predikcí.")
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--real", action="store_true", help="Použij reálné historické zápasy.")
    parser.add_argument("--fetch", action="store_true", help="Stáhni OpenFootball JSON.")
    parser.add_argument("--sync-supabase", action="store_true", help="Ulož na server Supabase.")
    args = parser.parse_args()
    run(real=args.real, fetch=args.fetch, sync_supabase=args.sync_supabase)

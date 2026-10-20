"""Historická fotbalová analytika bez kurzů a sázení."""
import argparse
from pathlib import Path
import subprocess
import sys
import pandas as pd
from evaluation.backtest import backtest
from evaluation.compare import benchmark, metrics_table
from storage import save_predictions

ROOT = Path(__file__).resolve().parent

def _run_worker(real=False, fetch=False, sync_supabase=False, compare=False, output_dir=None):
    if fetch and not real:
        raise ValueError("--fetch vyžaduje také --real.")
    if sync_supabase and not real:
        raise ValueError("Supabase synchronizace vyžaduje --real.")
    if compare and sync_supabase:
        raise ValueError("Porovnání V2 nyní ukládáme jen do lokálních CSV, nikoliv do Supabase.")
    suffix = "_real" if real else ""
    input_file = ROOT / "data" / ("matches_real.csv" if real else "matches.csv")
    output_dir = Path(output_dir) if output_dir else ROOT / "output"
    output_file = output_dir / f"predictions{suffix}.csv"
    if fetch:
        from data.openfootball import refresh
        count, warnings = refresh(input_file)
        print(f"OpenFootball: načteno {count} historických výsledků.")
        if warnings:
            print("Varování:", "; ".join(warnings))
    if real and not input_file.exists():
        raise FileNotFoundError("Chybí data. Spusť: python main.py --real --fetch")
    matches = pd.read_csv(input_file, parse_dates=["date"])
    if matches.empty:
        raise ValueError("Dataset je prázdný.")
    original = save_predictions(backtest(matches), output_file)
    print(f"V1: {len(original)} zápasů; Brier: {original.brier.mean():.4f}; log-loss: {original.log_loss.mean():.4f}")
    print("Výstup V1:", output_file)
    if compare:
        comparison = save_predictions(benchmark(matches), output_dir / f"comparison{suffix}.csv")
        overall = metrics_table(comparison)
        summary_file = output_dir / f"benchmark_summary{suffix}.csv"
        overall.to_csv(summary_file, index=False)
        print("\nPOROVNÁNÍ MODELU (nižší skóre znamená menší chybu):")
        print(overall.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
        if real:
            recent = metrics_table(comparison, holdout_start="2026-08-01")
            if not recent.empty:
                print("\nNOVĚJŠÍ SEZÓNA (od 1. 8. 2026):")
                print(recent.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
        print("Porovnání:", summary_file)
    if sync_supabase:
        from database.supabase_sync import sync
        n_matches, n_predictions = sync(original, matches)
        print(f"Supabase: {n_matches} zápasů, {n_predictions} retrospektivních analýz.")
    return original


def run(real=False, fetch=False, sync_supabase=False, compare=False, timeout=300):
    from runtime import run_bounded
    flags = [flag for flag, enabled in (("--real", real), ("--fetch", fetch),
             ("--sync-supabase", sync_supabase), ("--compare", compare)) if enabled]
    run_bounded(lambda stage: [sys.executable, str(ROOT / "main.py"), "--worker",
                "--output-dir", str(stage), *flags], ROOT / "output",
                "run_status_real.json" if real else "run_status_demo.json", timeout)
    print("Dokončeno. Výstupy:", ROOT / "output")
    suffix = "_real" if real else ""
    return pd.read_csv(ROOT / "output" / f"predictions{suffix}.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--real", action="store_true", help="Použij skutečné historické výsledky.")
    parser.add_argument("--fetch", action="store_true", help="Stáhni OpenFootball JSON.")
    parser.add_argument("--sync-supabase", action="store_true", help="Zapiš pouze původní V1 do Supabase.")
    parser.add_argument("--compare", action="store_true", help="Porovnej V1, nový model útoku/obrany a baseline.")
    parser.add_argument("--timeout", type=float, default=300,
                        help="Limit celého běhu v sekundách (výchozí 300).")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--output-dir", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        _run_worker(real=args.real, fetch=args.fetch, sync_supabase=args.sync_supabase,
                    compare=args.compare, output_dir=args.output_dir)
    else:
        try:
            run(real=args.real, fetch=args.fetch, sync_supabase=args.sync_supabase,
                compare=args.compare, timeout=args.timeout)
        except (subprocess.SubprocessError, ValueError, RuntimeError) as exc:
            print(f"Pipeline nebyla dokončena: {exc}", file=sys.stderr)
            sys.exit(1)

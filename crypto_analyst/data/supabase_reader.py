"""Read-only, server-side reader for the existing Crypto Radar tables.

Use ONLY in a trusted backend (for example, a private Streamlit server).
Never use secret/service-role keys in a browser or commit them to GitHub.
"""
import os
import re

import pandas as pd
import requests


def configured():
    return bool(os.environ.get("SUPABASE_URL") and (
        os.environ.get("SUPABASE_SECRET_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    ))


def _select(table, params):
    if table not in {"crypto_candles", "crypto_analysis_reports"}:
        raise ValueError("Unsupported table")
    base = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_SECRET_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not base or not key:
        raise RuntimeError("Nastav SUPABASE_URL a SUPABASE_SECRET_KEY na serveru.")
    if not base.startswith("https://"):
        raise RuntimeError("SUPABASE_URL musi zacinat https://")
    response = requests.get(
        f"{base}/rest/v1/{table}",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
        },
        params=params,
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list):
        raise ValueError("Neocekavana odpoved databaze")
    return payload


def _check(symbol, interval):
    symbol = symbol.strip().upper()
    if not re.fullmatch(r"[A-Z0-9]{5,20}", symbol):
        raise ValueError("Neplatny symbol")
    if interval not in {"15m", "1h", "4h", "1d"}:
        raise ValueError("Nepodporovany interval")
    return symbol


def fetch_candles(symbol="BTCUSDT", interval="1h", limit=500):
    symbol = _check(symbol, interval)
    limit = max(1, min(int(limit), 1000))
    rows = _select("crypto_candles", {
        "select": "open_time,close_time,open,high,low,close,volume",
        "symbol": f"eq.{symbol}",
        "timeframe": f"eq.{interval}",
        "order": "open_time.desc",
        "limit": str(limit),
    })
    if not rows:
        raise ValueError(f"Pro {symbol} / {interval} nejsou v Supabase zadna data.")
    df = pd.DataFrame(rows)
    for col in ("open", "high", "low", "close", "volume"):
        df[col] = pd.to_numeric(df[col], errors="raise")
    df["open_time"] = pd.to_datetime(df["open_time"], utc=True)
    df["close_time"] = pd.to_datetime(df["close_time"], utc=True)
    # Database stores completed candles. Additional guard for incomplete rows.
    df = df[df["close_time"] <= pd.Timestamp.now(tz="UTC")].copy()
    df = df.sort_values("open_time").reset_index(drop=True)
    if df.empty:
        raise ValueError("Zadne dokoncene svicky v databazi.")
    return df


def latest_saved_report(symbol="BTCUSDT", interval="1h"):
    symbol = _check(symbol, interval)
    rows = _select("crypto_analysis_reports", {
        "select": "symbol,timeframe,candle_open_time,model_version,analyzed_at,last_close,market_regime,indicators,market_levels,analysis_notes",
        "symbol": f"eq.{symbol}",
        "timeframe": f"eq.{interval}",
        "order": "candle_open_time.desc",
        "limit": "1",
    })
    return rows[0] if rows else None

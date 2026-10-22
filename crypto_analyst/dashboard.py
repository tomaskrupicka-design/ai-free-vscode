"""Crypto Analyzer: read-only dashboard for Binance data or Hollywood Supabase."""
import streamlit as st
import requests

from data.binance_public import fetch_klines
from data.supabase_reader import configured, fetch_candles, latest_saved_report
from analysis.indicators import enrich
from analysis.report import build_report

st.set_page_config(page_title="Crypto Analyzer", layout="wide")
st.title("Crypto Analyzer")
st.caption("Technicka analyza kryptomen. Bez pristupu k obchodnimu uctu a bez zadavani prikazu.")

symbol = st.sidebar.selectbox("Kryptomena", ["BTCUSDT", "ETHUSDT"])
interval = st.sidebar.selectbox("Interval", ["1h", "4h", "1d", "15m"])
sources = ["Supabase / hollywood", "Binance Spot / verejna data"]
source = st.sidebar.radio("Zdroj dat", sources, index=0 if configured() else 1)

if not configured():
    st.sidebar.info(
        "Pro cteni databaze nastav na serveru SUPABASE_URL a SUPABASE_SECRET_KEY. "
        "Bez klice funguje verejny Binance zdroj."
    )

@st.cache_data(ttl=120, show_spinner=False)
def load_supabase(symbol, interval):
    return fetch_candles(symbol, interval, limit=500)

@st.cache_data(ttl=120, show_spinner=False)
def load_binance(symbol, interval):
    return fetch_klines(symbol, interval)

try:
    if source == sources[0]:
        if not configured():
            st.warning("Nejsou nastavene pristupove udaje Supabase na serveru.")
            st.stop()
        raw = load_supabase(symbol, interval)
    else:
        raw = load_binance(symbol, interval)

    if len(raw) < 200:
        st.warning(
            "Mene nez 200 svicek: EMA200 ma malo historickych dat, "
            "vysledky mohou byt mene spolehlive."
        )

    df = enrich(raw)
    report = build_report(df, symbol, interval)
    a, b, c, d = st.columns(4)
    a.metric("Posledni cena (USDT)", f"{report['price']:,.2f}")
    b.metric("Rezim trhu", report["regime"])
    c.metric("RSI 14", report["rsi14"])
    d.metric("ATR %", report["atr_pct"])

    st.caption(
        f"Zdroj: {source} | Posledni pouzita svicka: "
        f"{df.iloc[-1]['open_time']} (UTC). Data nemusi byt aktualni v realnem case."
    )
    st.subheader("Cena a klouzave prumery")
    st.line_chart(
        df.set_index("open_time")[["close", "ema20", "ema50", "ema200"]].tail(200)
    )
    left, right = st.columns(2)
    with left:
        st.subheader("Technicke urovne")
        st.write({
            "support": report["support"],
            "resistance": report["resistance"],
            "volume_ratio": report["volume_ratio"],
        })
    with right:
        st.subheader("Komentar")
        for note in report["notes"]:
            st.write("- " + note)

    if source == sources[0]:
        saved = latest_saved_report(symbol, interval)
        if saved:
            with st.expander("Posledni ulozeny report v Hollywoodu"):
                st.write({
                    "analyzovano_utc": saved["analyzed_at"],
                    "verze": saved["model_version"],
                    "rezim_trhu": saved["market_regime"],
                    "indikatory": saved["indicators"],
                    "urovne": saved["market_levels"],
                    "poznamky": saved["analysis_notes"],
                })
        else:
            st.info("Pro tento par a interval zatim neni ulozeny report.")

    st.caption("Pouze vzdelavaci a analyticke pouziti; nejde o financni doporuceni.")
except requests.exceptions.RequestException:
    st.error("Nepodarilo se nacist data. Over pripojeni nebo serverove nastaveni.")
except (ValueError, RuntimeError) as e:
    st.error(str(e))

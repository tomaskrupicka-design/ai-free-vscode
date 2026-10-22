"""Crypto Radar: market analysis plus historical educational simulation."""
import streamlit as st

from data.binance_public import fetch_klines, closed_candles
from analysis.indicators import enrich
from analysis.report import build_report
from simulation.paper_trader import SimulationSettings, simulate_ema_history

st.set_page_config(page_title="Crypto Radar – Analýza a simulátor", layout="wide")
st.title("Crypto Radar")
st.caption("Analýza trhu a simulované obchodování. Žádné skutečné burzovní příkazy ani účty.")

symbol = st.sidebar.selectbox("Kryptoměna", ["BTCUSDT", "ETHUSDT"])
interval = st.sidebar.selectbox("Interval", ["15m", "1h", "4h", "1d"], index=1)

@st.cache_data(ttl=180)
def load_history(pair, candle_interval):
    return closed_candles(fetch_klines(pair, candle_interval, limit=500))

try:
    history = load_history(symbol, interval)
    if len(history) < 60:
        st.warning("Na vyhodnocení je málo dokončených svíček.")
        st.stop()

    enriched = enrich(history)
    report = build_report(enriched, symbol, interval)

    market_tab, paper_tab = st.tabs(["Analýza trhu", "Paper Trader – simulace"])

    with market_tab:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Poslední uzavřená cena", f'{report["price"]:,.2f}')
        c2.metric("Tržní režim", report["regime"])
        c3.metric("RSI (14)", f'{report["rsi14"]:.1f}')
        c4.metric("ATR / cena", f'{report["atr_pct"]:.2f} %')

        st.subheader("Historický graf")
        st.line_chart(enriched.set_index("open_time")[["close", "ema20", "ema50", "ema200"]].tail(200))
        st.write("**Support:**", report["support"], " | **Resistance:**", report["resistance"])
        for note in report["notes"]:
            st.write("•", note)

    with paper_tab:
        st.info("Tady se přepočítávají pouze historické hypotetické pozice. "
                "Vždy se používají data z předchozí dokončené svíčky; modelová změna "
                "pozice nastává na otevření další svíčky.")
        starting = 10_000.0
        settings = SimulationSettings(initial_balance=starting, allocation=0.25,
                                      fee_bps=10, slippage_bps=5)
        sim = simulate_ema_history(history, settings)
        summary = sim["summary"]

        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Demo hodnota portfolia", f'{summary["ending_demo_value"]:,.2f}')
        d2.metric("Demo výnos", f'{summary["simulated_return_pct"]:.2f} %')
        d3.metric("Max. historický propad", f'{summary["max_drawdown_pct"]:.2f} %')
        d4.metric("Simulovaná uzavření", summary["hypothetical_exits"])

        st.subheader("Modelové portfolio vs. jednoduché držení aktiva")
        curve = sim["equity_curve"].set_index("time")
        st.line_chart(curve[["simulated_portfolio", "buy_hold_reference"]])

        st.subheader("Historie modelových změn pozice")
        if sim["events"].empty:
            st.write("Pro zvolený úsek nebyly žádné hypotetické změny pozice.")
        else:
            st.dataframe(sim["events"].tail(60), use_container_width=True)

        st.caption("Model: EMA20/EMA50, hypotetická alokace 25 %, poplatek 0,10 % "
                   "a skluz 0,05 %. Bez páky a shortování. "
                   "Zjednodušený backtest není důkaz předpovědní schopnosti ani záruka výsledků.")

except Exception as exc:
    st.error(f"Chyba při načtení nebo analýze dat: {exc}")

import streamlit as st

from data.binance_public import fetch_klines
from analysis.indicators import enrich
from analysis.report import build_report

st.set_page_config(page_title="Crypto Analyst",layout="wide")
st.title("Crypto Analyst")

symbol=st.sidebar.text_input("Symbol","BTCUSDT").upper()
interval=st.sidebar.selectbox("Interval",["15m","1h","4h","1d"],index=1)

try:
    df=enrich(fetch_klines(symbol,interval))
    report=build_report(df,symbol,interval)

    c1,c2,c3,c4=st.columns(4)
    c1.metric("Price",report["price"])
    c2.metric("Regime",report["regime"])
    c3.metric("RSI 14",report["rsi14"])
    c4.metric("ATR %",report["atr_pct"])

    st.subheader("Price")
    st.line_chart(df.set_index("open_time")[["close","ema20","ema50","ema200"]].tail(200))

    a,b=st.columns(2)
    with a:
        st.subheader("Market levels")
        st.write({
            "support":report["support"],
            "resistance":report["resistance"],
            "volume_ratio":report["volume_ratio"]
        })
    with b:
        st.subheader("Analysis")
        for note in report["notes"]:
            st.write("- "+note)

    st.caption("Analysis-only dashboard. It does not place orders.")
except Exception as e:
    st.error(f"Data error: {e}")

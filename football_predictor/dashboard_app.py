"""Interactive Streamlit dashboard for football model evaluation."""
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Football Predictor", layout="wide")
st.title("Fotbalový predikční radar")
st.caption("Pouze analytika výsledků. Ukázková data nejsou reálné zápasy.")
path = Path(__file__).resolve().parent / "output" / "predictions.csv"
if not path.exists():
    st.warning("Nejdřív spusť: python main.py")
    st.stop()
df = pd.read_csv(path)
teams = sorted(set(df.home_team) | set(df.away_team))
team = st.selectbox("Filtrovat tým", ["Všechny týmy"] + teams)
if team != "Všechny týmy":
    df = df[(df.home_team == team) | (df.away_team == team)]
if df.empty:
    st.info("Žádné zápasy pro vybraný filtr.")
    st.stop()
a,b,c = st.columns(3)
a.metric("Zápasy", len(df))
b.metric("Brier", f"{df.brier.mean():.3f}")
c.metric("Log-loss", f"{df.log_loss.mean():.3f}")
st.dataframe(df, use_container_width=True, hide_index=True)
st.line_chart(df[["brier", "log_loss"]].reset_index(drop=True))

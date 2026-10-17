"""Dashboard nad historií fotbalového modelu: žádné kurzy, žádné sázky."""
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Fotbalový radar", layout="wide")
st.title("Fotbalový radar – predikční statistiky")
real_path = ROOT / "output" / "predictions_real.csv"
demo_path = ROOT / "output" / "predictions.csv"
source = st.radio("Dataset", ["Skutečné historické výsledky", "Ukázková data"], horizontal=True)
path = real_path if source.startswith("Skutečné") else demo_path
if not path.exists():
    st.warning("Tento dataset ještě není připraven. Pro reálná data spusť: python main.py --real --fetch")
    st.stop()
df = pd.read_csv(path)
if source.startswith("Skutečné"):
    st.info("Zdroj: OpenFootball. Aktualizace nemusí být okamžité. Všechny zdejší predikce jsou RETROSPEKTIVNÍ testy.")
else:
    st.warning("Ukázkové výsledky jsou umělé a nesmí být vydávány za skutečné zápasy.")
teams = sorted(set(df.home_team).union(df.away_team))
team = st.selectbox("Tým", ["Všechny týmy"] + teams)
if team != "Všechny týmy":
    df = df[(df.home_team == team) | (df.away_team == team)]
if df.empty:
    st.info("Pro vybraný filtr nejsou zápasy.")
    st.stop()
a, b, c = st.columns(3)
a.metric("Počet utkání", len(df))
b.metric("Brier score", f"{df.brier.mean():.3f}")
c.metric("Log-loss", f"{df.log_loss.mean():.3f}")
st.dataframe(df, hide_index=True, use_container_width=True)
st.subheader("Vývoj chybovosti")
st.line_chart(df[["brier", "log_loss"]].reset_index(drop=True))

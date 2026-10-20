"""Český dashboard pro srovnání retrospektivních modelů fotbalových výsledků."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from runtime import read_status

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Football Radar 2.0", layout="wide")
st.title("Fotbalový radar 2.0")
st.caption("Nezávislá analýza výsledků, nikoliv kurzů nebo sázení.")

dataset = st.radio("Zdroj dat", ["Skutečné historické výsledky", "Ukázková data"],
                   horizontal=True)
real = dataset.startswith("Skutečné")
suffix = "_real" if real else ""
path = ROOT / "output" / f"predictions{suffix}.csv"
comparison_path = ROOT / "output" / f"comparison{suffix}.csv"
status = read_status(ROOT / "output" / ("run_status_real.json" if real else "run_status_demo.json"))
last_success = status.get("last_success_at")
if last_success:
    try:
        completed = datetime.fromisoformat(last_success).astimezone(ZoneInfo("Europe/Prague"))
        st.caption("Poslední úspěšný běh: " + completed.strftime("%d. %m. %Y %H:%M:%S %Z"))
    except (ValueError, TypeError):
        st.warning("Čas posledního běhu nelze přečíst.")
else:
    st.caption("Poslední úspěšný běh: zatím neevidován.")
if status.get("state") in ("failed", "timeout"):
    st.warning("Poslední pokus selhal nebo překročil časový limit. Zobrazené výstupy mohou být starší.")
elif status.get("state") == "running":
    st.warning("Běh není dokončený. Zobrazujeme dříve uložené výstupy; při přerušeném řídicím procesu může být tento stav zastaralý.")
if (comparison_path.exists() and status.get("last_success_files")
        and comparison_path.name not in status["last_success_files"]):
    st.warning("Srovnání modelů nepochází z posledního úspěšného běhu. Pro aktualizaci spusť pipeline s --compare.")
if real:
    st.info("OpenFootball – historické výsledky. Nejnovější zveřejněné údaje mohou mít zpoždění. Všechny modelové odhady jsou RETROSPEKTIVNÍ backtesty.")
else:
    st.warning("Ukázková data jsou smyšlená. Nejde o skutečné zápasy.")

if not path.exists():
    st.warning("Nejdřív spusť: python main.py --real --fetch --compare (nebo python main.py --compare pro demo)")
    st.stop()

if comparison_path.exists():
    frame = pd.read_csv(comparison_path)
    teams = sorted(set(frame.home_team).union(frame.away_team))
    with st.form("comparison_filters"):
        col1, col2 = st.columns(2)
        with col1:
            team = st.selectbox("Tým", ["Všechny týmy"] + teams)
        with col2:
            period = st.selectbox("Hodnocené období",
                                  ["Celá historie"] +
                                  (["Sezóna 2026/27 (od 1. 8. 2026)"] if real else []))
        st.form_submit_button("Použít filtry")
    if team != "Všechny týmy":
        frame = frame[(frame.home_team == team) | (frame.away_team == team)]
    if period != "Celá historie":
        frame = frame[frame.date >= "2026-08-01"]
    if frame.empty:
        st.info("Pro vybraný filtr nemáme dokončené zápasy.")
        st.stop()

    from evaluation.compare import metrics_table
    summary = metrics_table(frame)
    st.subheader("Srovnání modelů")
    st.caption("Brier score a log-loss: nižší je lepší. Toto srovnání nedokazuje budoucí převahu modelu.")
    st.dataframe(summary.round(4), width="stretch", hide_index=True)
    st.bar_chart(summary.set_index("model_version")[["brier", "log_loss"]])
    model = st.selectbox("Zobrazit detaily modelu", sorted(frame.model_version.unique()))
    details = frame[frame.model_version == model].sort_values("date").reset_index(drop=True)
    a, b, c = st.columns(3)
    a.metric("Počet zápasů", len(details))
    b.metric("Průměrný Brier", f"{details.brier.mean():.4f}")
    c.metric("Průměrný log-loss", f"{details.log_loss.mean():.4f}")
    st.subheader("Jednotlivé zápasy")
    st.caption("Očekávané góly jsou statistické odhady z výsledků, nikoliv skutečně naměřené xG.")
    st.dataframe(details, width="stretch", hide_index=True)
    st.subheader("Klouzavý průměr chybovosti")
    rolling = details[["brier", "log_loss"]].rolling(window=30, min_periods=1).mean()
    st.line_chart(rolling)
    st.download_button("Export filtrovaných analýz (CSV)",
                       data=details.to_csv(index=False).encode("utf-8"),
                       file_name="football_radar_comparison.csv", mime="text/csv")
else:
    st.warning("Porovnání V2 zatím chybí. Spusť v terminálu: python main.py --real --compare")
    frame = pd.read_csv(path)
    teams = sorted(set(frame.home_team).union(frame.away_team))
    with st.form("original_filters"):
        team = st.selectbox("Tým", ["Všechny týmy"] + teams)
        st.form_submit_button("Použít filtry")
    if team != "Všechny týmy":
        frame = frame[(frame.home_team == team) | (frame.away_team == team)]
    if not frame.empty:
        a, b, c = st.columns(3)
        a.metric("Zápasy", len(frame))
        b.metric("Brier", f"{frame.brier.mean():.4f}")
        c.metric("Log-loss", f"{frame.log_loss.mean():.4f}")
        st.dataframe(frame, hide_index=True, width="stretch")

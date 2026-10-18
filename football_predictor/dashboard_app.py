"""Český dashboard pro srovnání retrospektivních modelů fotbalových výsledků."""
from pathlib import Path
import pandas as pd
import streamlit as st

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
    col1, col2 = st.columns(2)
    with col1:
        team = st.selectbox("Tým", ["Všechny týmy"] + teams)
    with col2:
        period = st.selectbox("Hodnocené období",
                              ["Celá historie"] +
                              (["Sezóna 2026/27 (od 1. 8. 2026)"] if real else []))
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
    st.dataframe(summary.round(4), use_container_width=True, hide_index=True)
    st.bar_chart(summary.set_index("model_version")[["brier", "log_loss"]])
    model = st.selectbox("Zobrazit detaily modelu", sorted(frame.model_version.unique()))
    details = frame[frame.model_version == model].sort_values("date").reset_index(drop=True)
    a, b, c = st.columns(3)
    a.metric("Počet zápasů", len(details))
    b.metric("Průměrný Brier", f"{details.brier.mean():.4f}")
    c.metric("Průměrný log-loss", f"{details.log_loss.mean():.4f}")
    st.subheader("Jednotlivé zápasy")
    st.caption("Očekávané góly jsou statistické odhady z výsledků, nikoliv skutečně naměřené xG.")
    st.dataframe(details, use_container_width=True, hide_index=True)
    from evaluation.monitoring import rolling_error, monthly_error, calibration
    st.subheader("Časová osa chybovosti modelů")
    window = st.selectbox("Klouzavé okno (zápasů na model)", [10, 30, 50, 100], index=1)
    trend = rolling_error(frame, window=window)
    st.caption("Křivky znázorňují zpětné testy; nižší hodnoty znamenají menší chybu.")
    st.line_chart(trend.pivot(index="date", columns="model_version", values="rolling_brier"))
    st.caption("Log-loss za stejné období:")
    st.line_chart(trend.pivot(index="date", columns="model_version", values="rolling_log_loss"))

    st.subheader("Chybovost po měsících")
    month_table = monthly_error(frame)
    st.dataframe(month_table.round(4), use_container_width=True, hide_index=True)

    st.subheader("Kalibrace pravděpodobností")
    labels = {"Domácí": "home", "Remíza": "draw", "Hosté": "away"}
    outcome_label = st.selectbox("Vyhodnocovaný výsledek", list(labels))
    calibration_data = calibration(frame, outcome=labels[outcome_label])
    st.caption("Zobrazené intervaly mají aspoň 10 historických zápasů na model. "
               "Malé vzorky nelze spolehlivě interpretovat.")
    plotted = calibration_data[calibration_data["n"] >= 10]
    if plotted.empty:
        st.info("Pro kalibrační graf není ve vybraném filtru dost dat.")
    else:
        st.scatter_chart(plotted, x="predicted_probability",
                         y="observed_frequency", color="model_version")
    st.dataframe(calibration_data.round(4), use_container_width=True, hide_index=True)
    st.download_button("Export filtrovaných analýz (CSV)",
                       data=details.to_csv(index=False).encode("utf-8"),
                       file_name="football_radar_comparison.csv", mime="text/csv")
else:
    st.warning("Porovnání V2 zatím chybí. Spusť v terminálu: python main.py --real --compare")
    frame = pd.read_csv(path)
    teams = sorted(set(frame.home_team).union(frame.away_team))
    team = st.selectbox("Tým", ["Všechny týmy"] + teams)
    if team != "Všechny týmy":
        frame = frame[(frame.home_team == team) | (frame.away_team == team)]
    if not frame.empty:
        a, b, c = st.columns(3)
        a.metric("Zápasy", len(frame))
        b.metric("Brier", f"{frame.brier.mean():.4f}")
        c.metric("Log-loss", f"{frame.log_loss.mean():.4f}")
        st.dataframe(frame, hide_index=True, use_container_width=True)

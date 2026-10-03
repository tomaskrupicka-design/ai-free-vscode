from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parent
path=ROOT/"output"/"predictions.csv"
if not path.exists():
    raise SystemExit("Nejdriv spust: python main.py")

df=pd.read_csv(path)
print("\n=== FOOTBALL PREDICTOR DASHBOARD ===")
print("Predikci:",len(df))
print("Brier:",round(df.brier.mean(),4))
print("Log-loss:",round(df.log_loss.mean(),4))
print("\nPosledni predikce:")
cols=["date","home_team","away_team","p_home","p_draw","p_away","actual"]
print(df[cols].tail(10).to_string(index=False))

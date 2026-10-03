from pathlib import Path
import pandas as pd
from evaluation.backtest import backtest
from storage import save_predictions

ROOT=Path(__file__).resolve().parent
INPUT=ROOT/"data"/"matches.csv"
OUTPUT=ROOT/"output"/"predictions.csv"

def run():
    matches=pd.read_csv(INPUT,parse_dates=["date"])
    rows=backtest(matches)
    df=save_predictions(rows,OUTPUT)

    print(df.to_string(index=False))
    print("\n=== MODEL METRICS ===")
    print("Matches:",len(df))
    print("Mean Brier:",round(df["brier"].mean(),4))
    print("Mean log-loss:",round(df["log_loss"].mean(),4))
    print("Saved:",OUTPUT)
    return df

if __name__=="__main__":
    run()

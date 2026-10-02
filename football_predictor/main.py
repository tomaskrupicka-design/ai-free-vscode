from pathlib import Path
import pandas as pd
from evaluation.backtest import backtest

root=Path(__file__).resolve().parent
matches=pd.read_csv(root/"data"/"matches.csv",parse_dates=["date"])
df=pd.DataFrame(backtest(matches))
print(df.to_string(index=False))
print("\nMean Brier:",round(df.brier.mean(),4))
print("Mean log-loss:",round(df.log_loss.mean(),4))

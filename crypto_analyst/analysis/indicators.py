import numpy as np
import pandas as pd

def ema(s,period):
    return s.ewm(span=period,adjust=False).mean()

def rsi(close,period=14):
    delta=close.diff()
    up=delta.clip(lower=0).ewm(alpha=1/period,adjust=False).mean()
    down=(-delta.clip(upper=0)).ewm(alpha=1/period,adjust=False).mean()
    rs=up/down.replace(0,np.nan)
    return 100-(100/(1+rs))

def atr(df,period=14):
    prev=df["close"].shift(1)
    tr=pd.concat([
        df["high"]-df["low"],
        (df["high"]-prev).abs(),
        (df["low"]-prev).abs()
    ],axis=1).max(axis=1)
    return tr.ewm(alpha=1/period,adjust=False).mean()

def enrich(df):
    out=df.copy()
    out["ema20"]=ema(out["close"],20)
    out["ema50"]=ema(out["close"],50)
    out["ema200"]=ema(out["close"],200)
    out["rsi14"]=rsi(out["close"],14)
    out["atr14"]=atr(out,14)
    out["volume_ma20"]=out["volume"].rolling(20).mean()
    out["return_1"]=out["close"].pct_change()
    return out

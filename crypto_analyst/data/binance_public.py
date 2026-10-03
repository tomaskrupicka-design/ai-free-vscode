import requests
import pandas as pd
from config import BINANCE_PUBLIC_API, KLINES_LIMIT

def fetch_klines(symbol="BTCUSDT", interval="1h", limit=KLINES_LIMIT):
    url=f"{BINANCE_PUBLIC_API}/api/v3/klines"
    r=requests.get(url,params={"symbol":symbol.upper(),"interval":interval,"limit":limit},timeout=15)
    r.raise_for_status()
    raw=r.json()
    cols=["open_time","open","high","low","close","volume","close_time","quote_volume",
          "trades","taker_buy_base","taker_buy_quote","ignore"]
    df=pd.DataFrame(raw,columns=cols)
    for c in ["open","high","low","close","volume","quote_volume","taker_buy_base","taker_buy_quote"]:
        df[c]=pd.to_numeric(df[c],errors="coerce")
    df["open_time"]=pd.to_datetime(df["open_time"],unit="ms",utc=True)
    return df

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


def closed_candles(frame, as_of=None):
    """Keep only completed OHLC bars; the currently forming candle is excluded."""
    if "close_time" not in frame.columns:
        raise ValueError("V datech chybi close_time pro overeni dokonceni svicek.")
    now = pd.Timestamp.now(tz="UTC") if as_of is None else pd.Timestamp(as_of)
    if now.tzinfo is None:
        now = now.tz_localize("UTC")
    closing = pd.to_datetime(frame["close_time"], unit="ms", utc=True)
    return (frame.loc[closing <= now]
            .sort_values("open_time")
            .drop_duplicates("open_time", keep="last")
            .reset_index(drop=True))

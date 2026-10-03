def recent_levels(df,window=50):
    d=df.tail(window)
    return {
        "support": float(d["low"].min()),
        "resistance": float(d["high"].max()),
        "range_mid": float((d["low"].min()+d["high"].max())/2)
    }

def regime(row):
    if row["close"]>row["ema20"]>row["ema50"]>row["ema200"]:
        return "strong_uptrend"
    if row["close"]<row["ema20"]<row["ema50"]<row["ema200"]:
        return "strong_downtrend"
    if row["close"]>row["ema50"]:
        return "bullish_mixed"
    if row["close"]<row["ema50"]:
        return "bearish_mixed"
    return "neutral"

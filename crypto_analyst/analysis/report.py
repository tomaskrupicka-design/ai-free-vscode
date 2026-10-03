from analysis.structure import recent_levels, regime

def build_report(df,symbol,interval):
    row=df.iloc[-1]
    levels=recent_levels(df)
    vol_ratio=float(row["volume"]/row["volume_ma20"]) if row["volume_ma20"] else None
    atr_pct=float(row["atr14"]/row["close"]*100)

    notes=[]
    if row["rsi14"]>=70: notes.append("RSI is elevated; momentum is strong but stretched.")
    elif row["rsi14"]<=30: notes.append("RSI is depressed; downside momentum is strong but stretched.")
    else: notes.append("RSI is in the middle zone.")

    if vol_ratio and vol_ratio>1.5: notes.append("Volume is materially above its 20-period average.")
    if atr_pct>4: notes.append("Volatility is high relative to price.")

    return {
        "symbol":symbol.upper(),
        "interval":interval,
        "price":round(float(row["close"]),4),
        "regime":regime(row),
        "ema20":round(float(row["ema20"]),4),
        "ema50":round(float(row["ema50"]),4),
        "ema200":round(float(row["ema200"]),4),
        "rsi14":round(float(row["rsi14"]),2),
        "atr_pct":round(atr_pct,2),
        "volume_ratio":round(vol_ratio,2) if vol_ratio else None,
        "support":round(levels["support"],4),
        "resistance":round(levels["resistance"],4),
        "notes":notes
    }

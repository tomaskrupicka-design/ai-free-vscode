import argparse
import json
from data.binance_public import fetch_klines
from analysis.indicators import enrich
from analysis.report import build_report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--symbol",default="BTCUSDT")
    p.add_argument("--interval",default="1h")
    args=p.parse_args()

    df=enrich(fetch_klines(args.symbol,args.interval))
    report=build_report(df,args.symbol,args.interval)
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()

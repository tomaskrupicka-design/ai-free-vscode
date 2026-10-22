# Crypto Radar – Analyzer + Paper Trader (simulátor)

Dva propojené moduly pro vzdělávací analýzu veřejných historických krypto dat.

- **Analyzer:** EMA 20/50/200, RSI, ATR, objem, support/resistance, vývoj ceny.
- **Paper Trader:** historické fiktivní portfolio s EMA20/50, equity křivkou,
  modelovými transakcemi, poplatky, skluzem, srovnáním s držením aktiva a maximálním propadem.
- **Bez obchodních účtů:** žádné API klíče burzy, žádné skutečné nákupy/prodeje,
  žádná páka ani shortování.

**Historický backtest je pouze model.** Není prediktivní důkaz ani doporučení k obchodování.
Algoritmus používá předchozí uzavřenou svíčku pro simulovanou změnu pozice
na otevření následující svíčky a vynechává právě tvořenou svíčku.

## Kali Linux / Windows

```bash
cd crypto_analyst
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard.py
```

Ve Windows nahraď `source .venv/bin/activate` příkazem
`.venv\\Scripts\\activate` (PowerShell: `.venv\\Scripts\\Activate.ps1`).

Testy:
```bash
python -m unittest discover -s tests -v
```

Původní textový analytický výpis:
```bash
python main.py --symbol BTCUSDT --interval 1h
```

## Databáze
Stávající Supabase projekt `hollywood` obsahuje historická data a dva jednorázové reporty.
Nový simulátor funguje nezávisle na databázových přístupových klíčích a nevykonává obchodní příkazy.

Pro nynější dashboard je potřeba připojení k veřejnému Binance Spot API.
Průběžný sběr a nasazení na veřejně dostupnou adresu zatím nejsou zprovozněné.

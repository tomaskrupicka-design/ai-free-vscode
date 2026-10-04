# Trading Research Agent v1

Bezpečný výzkumný/backtestovací modul pro studium dlouhodobých futures strategií.

## Co umí
- načíst OHLCV data z CSV,
- spočítat jednoduchý trendový signál,
- vytvořit hypotetické LONG / SHORT / WAIT značky,
- spustit jednoduchý backtest bez páky a bez live exekuce,
- vypsat základní metriky: celkový výnos, max drawdown a počet změn pozice.

## Co záměrně neumí
- nepřipojuje se k brokerovi ani burze,
- neposílá skutečné příkazy,
- nepracuje s API klíči,
- nepoužívá finanční páku.

## Struktura
- `src/signals.py` – tvorba signálů
- `src/backtest.py` – jednoduchý backtest engine
- `src/demo.py` – ukázka se syntetickými daty
- `requirements.txt` – Python závislosti

## Spuštění
```bash
cd trading-research
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.demo
```

> Tento modul je určen pouze pro výzkum a vzdělávání. Výsledky backtestu nejsou předpověď budoucích výsledků.

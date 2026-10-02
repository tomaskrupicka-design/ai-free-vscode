# Football Predictor

Fotbalovy analyticky predikcni engine.

Pipeline: data -> chronologicky backtest -> Elo -> Poisson -> 1/X/2 pravdepodobnosti -> Brier/log-loss.

Model aktualizuje Elo az po vytvoreni predikce, aby nevznikal look-ahead bias.

## Spusteni
```bash
cd football_predictor
pip install -r requirements.txt
python main.py
```

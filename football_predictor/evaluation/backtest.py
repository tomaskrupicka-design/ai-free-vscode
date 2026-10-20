"""Chronologický backtest: výsledky všech zápasů téhož dne až po predikcích."""
from models.elo import EloModel
from models.poisson import result_probabilities
from evaluation.metrics import brier, log_loss
import pandas as pd

def outcome(home_goals, away_goals):
    if home_goals > away_goals:
        return "home"
    if home_goals == away_goals:
        return "draw"
    return "away"

def backtest(matches):
    matches = matches.copy()
    matches["date"] = pd.to_datetime(matches["date"], errors="raise").dt.normalize()
    elo = EloModel()
    rows = []
    # Historický zdroj poskytuje jen datum, nikoli ověřený okamžik zveřejnění.
    # Proto vzájemné zápasy z jednoho dne nevstupují do modelu předčasně.
    for date, group in matches.sort_values("date").groupby("date", sort=True):
        pending = []
        for _, match in group.iterrows():
            home, away = match.home_team, match.away_team
            strength = elo.expected_home(home, away)
            home_xg = max(0.25, 0.85 + 1.10 * strength)
            away_xg = max(0.20, 0.70 + 1.10 * (1.0 - strength))
            probs = result_probabilities(home_xg, away_xg)
            hg, ag = int(match.home_goals), int(match.away_goals)
            actual = outcome(hg, ag)
            rows.append({
                "date": str(date.date()),
                "home_team": home,
                "away_team": away,
                "home_xg": round(home_xg, 3),
                "away_xg": round(away_xg, 3),
                "p_home": probs["home"],
                "p_draw": probs["draw"],
                "p_away": probs["away"],
                "actual": actual,
                "brier": brier(probs, actual),
                "log_loss": log_loss(probs, actual),
                "source_match_key": match.get("source_match_key", ""),
                "data_source": match.get("source", "demo"),
                "prediction_kind": "retrospective_backtest",
            })
            pending.append((home, away, 1 if hg > ag else 0 if hg == ag else -1))
        for home, away, result in pending:
            elo.update(home, away, result)
    return rows

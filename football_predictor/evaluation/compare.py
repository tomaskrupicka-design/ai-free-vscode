"""Independent chronological comparison of predictive models."""
import pandas as pd
from models.elo import EloModel
from models.poisson import result_probabilities
from models.team_goals import TeamGoalModel
from evaluation.metrics import brier, log_loss

MODELS = ("elo-poisson-v0.2", "team-goals-v0.3",
          "historical-frequency-baseline")

def outcome(hg, ag):
    return "home" if hg > ag else "draw" if hg == ag else "away"

def benchmark(matches):
    if matches.empty:
        raise ValueError("No matches")
    ordered = matches.copy()
    ordered["date"] = pd.to_datetime(ordered["date"], errors="raise")
    ordered = ordered.sort_values(["date", "home_team", "away_team"], kind="stable")
    elo = EloModel()
    team = TeamGoalModel()
    # Pre-data assumptions for an online historical-frequency baseline.
    frequency = {"home": 4.5, "draw": 2.7, "away": 2.8}
    records = []

    def record(row, model, home_est, away_est, probs, actual):
        records.append({
            "date": row.date.date().isoformat(),
            "home_team": row.home_team,
            "away_team": row.away_team,
            "model_version": model,
            "expected_home_goals": home_est,
            "expected_away_goals": away_est,
            "p_home": probs["home"],
            "p_draw": probs["draw"],
            "p_away": probs["away"],
            "actual": actual,
            "brier": brier(probs, actual),
            "log_loss": log_loss(probs, actual),
            "source_match_key": row.get("source_match_key", ""),
            "data_source": row.get("source", "demo"),
            "prediction_kind": "retrospective_backtest",
        })

    for date, group in ordered.groupby("date", sort=True):
        pending = []
        total = sum(frequency.values())
        baseline = {k: v / total for k, v in frequency.items()}
        for _, row in group.iterrows():
            h, a = row.home_team, row.away_team
            hg, ag = int(row.home_goals), int(row.away_goals)
            actual = outcome(hg, ag)
            strength = elo.expected_home(h, a)
            old_h = max(0.25, 0.85 + 1.10 * strength)
            old_a = max(0.20, 0.70 + 1.10 * (1.0 - strength))
            record(row, MODELS[0], round(old_h, 3), round(old_a, 3),
                   result_probabilities(old_h, old_a), actual)

            new_h, new_a = team.predict(h, a, date)
            record(row, MODELS[1], round(new_h, 3), round(new_a, 3),
                   result_probabilities(new_h, new_a), actual)
            record(row, MODELS[2], None, None, baseline, actual)
            pending.append((h, a, hg, ag, actual))

        # ALL results on a given date enter the models only after all forecasts.
        for h, a, hg, ag, actual in pending:
            elo.update(h, a, 1 if hg > ag else 0 if hg == ag else -1)
            team.update(h, a, hg, ag, date)
            frequency[actual] += 1.0
    return records

def metrics_table(predictions, holdout_start=None):
    df = pd.DataFrame(predictions)
    if holdout_start is not None:
        df = df[df.date >= str(holdout_start)]
    return (df.groupby("model_version", as_index=False)
              .agg(matches=("brier", "size"), brier=("brier", "mean"),
                   log_loss=("log_loss", "mean"))
              .sort_values("brier").reset_index(drop=True))

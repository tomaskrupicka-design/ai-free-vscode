"""Historical model monitoring. All inputs must be retrospective backtest rows.

No live fixture ingestion or betting recommendations are provided here.
"""
import pandas as pd

OUTCOMES = ("home", "draw", "away")
REQUIRED = {"date", "home_team", "away_team", "model_version", "actual",
            "p_home", "p_draw", "p_away", "brier", "log_loss"}


def _clean(rows):
    frame = pd.DataFrame(rows).copy()
    missing = REQUIRED.difference(frame.columns)
    if missing:
        raise ValueError("Chybí sloupce pro monitoring: " + ", ".join(sorted(missing)))
    if frame.empty:
        return frame
    frame["date"] = pd.to_datetime(frame["date"], errors="raise").dt.normalize()
    for column in ("p_home", "p_draw", "p_away", "brier", "log_loss"):
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    probabilities = frame[["p_home", "p_draw", "p_away"]]
    if (probabilities.isna().any().any() or
            ((probabilities < 0) | (probabilities > 1)).any().any() or
            ((probabilities.sum(axis=1) - 1).abs() > 0.001).any()):
        raise ValueError("Nesprávné pravděpodobnosti modelu.")
    if not frame["actual"].isin(OUTCOMES).all():
        raise ValueError("Neznámý skutečný výsledek zápasu.")
    if not frame[["brier", "log_loss"]].notna().all().all():
        raise ValueError("Chybí metriky některých zápasů.")
    if "prediction_kind" in frame.columns and not (frame["prediction_kind"] == "retrospective_backtest").all():
        raise ValueError("Monitorování přijímá pouze retrospektivní backtesty.")
    return frame


def rolling_error(rows, window=30):
    """Average error over trailing N matches, separately for each model."""
    if not isinstance(window, int) or window < 1:
        raise ValueError("Velikost okna musí být kladné celé číslo.")
    frame = _clean(rows)
    if frame.empty:
        return pd.DataFrame(columns=["date", "model_version", "matches_seen",
                                     "rolling_brier", "rolling_log_loss"])
    frame = frame.sort_values(["model_version", "date", "home_team", "away_team"],
                              kind="stable").reset_index(drop=True)
    group = frame.groupby("model_version", sort=False)
    frame["rolling_brier"] = group["brier"].transform(
        lambda s: s.rolling(window, min_periods=1).mean())
    frame["rolling_log_loss"] = group["log_loss"].transform(
        lambda s: s.rolling(window, min_periods=1).mean())
    frame["matches_seen"] = group.cumcount() + 1
    # One chart point per date/model, after all matches of that date.
    return (frame.groupby(["date", "model_version"], as_index=False, sort=True)
                 .tail(1)[["date", "model_version", "matches_seen",
                           "rolling_brier", "rolling_log_loss"]]
                 .sort_values(["date", "model_version"]).reset_index(drop=True))


def monthly_error(rows):
    """Monthly retrospective error per model, for drift inspection."""
    frame = _clean(rows)
    if frame.empty:
        return pd.DataFrame(columns=["month", "model_version", "matches", "brier", "log_loss"])
    frame["month"] = frame["date"].dt.to_period("M").dt.to_timestamp()
    return (frame.groupby(["month", "model_version"], as_index=False)
                 .agg(matches=("brier", "size"), brier=("brier", "mean"),
                      log_loss=("log_loss", "mean"))
                 .sort_values(["month", "model_version"]).reset_index(drop=True))


def calibration(rows, outcome="home", bins=10):
    """Mean predicted probability vs observed outcome frequency in probability bins."""
    if outcome not in OUTCOMES or not isinstance(bins, int) or bins < 2:
        raise ValueError("Neplatný výsledek nebo počet intervalů.")
    frame = _clean(rows)
    if frame.empty:
        return pd.DataFrame(columns=["model_version", "interval", "n",
                                     "predicted_probability", "observed_frequency"])
    frame["bin"] = (frame[f"p_{outcome}"] * bins).clip(upper=bins - 1e-9).astype(int)
    frame["occurred"] = (frame["actual"] == outcome).astype(int)
    result = (frame.groupby(["model_version", "bin"], as_index=False)
                   .agg(n=("occurred", "size"),
                        predicted_probability=(f"p_{outcome}", "mean"),
                        observed_frequency=("occurred", "mean")))
    result["interval"] = result["bin"].map(
        lambda b: f"{b / bins:.0%}–{(b + 1) / bins:.0%}")
    return result[["model_version", "interval", "n", "predicted_probability",
                   "observed_frequency"]].sort_values(["model_version", "predicted_probability"]).reset_index(drop=True)

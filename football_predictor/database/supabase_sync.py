"""Zápis historických zápasů a RETROSPEKTIVNÍHO backtestu do Supabase.
Používejte pouze na serveru; service_role klíč nikdy nedávejte do webového klienta.
Nejdřív aplikujte schema.sql v SQL editoru projektu Supabase.
"""
import json
import os
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

def _request(url, key, rows, conflict):
    req = Request(
        url + "?" + urlencode({"on_conflict": conflict}),
        data=json.dumps(rows, allow_nan=False).encode("utf-8"),
        headers={
            "apikey": key,
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=representation",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=40) as response:
            return json.load(response)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"Supabase sync HTTP {exc.code}: {detail}") from exc

def sync(df, source_df, batch_size=100):
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not (url.startswith("https://") and key):
        raise RuntimeError("Chybí SUPABASE_URL nebo SUPABASE_SERVICE_ROLE_KEY.")
    if "source_match_key" not in source_df.columns:
        raise RuntimeError("Do databáze ukládáme pouze zápasy s ověřitelným klíčem zdroje.")
    api = url + "/rest/v1/"
    source_rows = source_df.to_dict(orient="records")
    lookup = {}
    for start in range(0, len(source_rows), batch_size):
        batch = source_rows[start:start + batch_size]
        matches = [{
            "source_match_key": r["source_match_key"],
            "match_date": str(r["date"])[:10],
            "home_team": r["home_team"],
            "away_team": r["away_team"],
            "home_goals": int(r["home_goals"]),
            "away_goals": int(r["away_goals"]),
            "source": r["source"],
            "season": r["season"],
        } for r in batch]
        for row in _request(api + "matches", key, matches, "source_match_key"):
            lookup[row["source_match_key"]] = row["id"]
    pred_rows = []
    for r in df.to_dict(orient="records"):
        key_value = r.get("source_match_key")
        if key_value not in lookup:
            raise RuntimeError("Chybí propojení predikce se zápasem: " + str(key_value))
        pred_rows.append({
            "match_id": lookup[key_value],
            "model_version": "elo-poisson-v0.2",
            "prediction_kind": "retrospective_backtest",
            "home_xg": float(r["home_xg"]),
            "away_xg": float(r["away_xg"]),
            "p_home": float(r["p_home"]),
            "p_draw": float(r["p_draw"]),
            "p_away": float(r["p_away"]),
            "actual_outcome": r["actual"],
            "brier": float(r["brier"]),
            "log_loss": float(r["log_loss"]),
        })
    for start in range(0, len(pred_rows), batch_size):
        _request(api + "predictions", key, pred_rows[start:start + batch_size],
                 "match_id,model_version,prediction_kind")
    return len(source_rows), len(pred_rows)

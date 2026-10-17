"""Stahování historických výsledků z otevřeného projektu OpenFootball.
Zdroj nemusí být aktuální v reálném čase; žádné kurzy ani sázky.
"""
import argparse
import csv
import datetime as dt
import io
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

BASE = "https://raw.githubusercontent.com/openfootball/football.json/master"
SEASONS = ("2024-25", "2025-26", "2026-27")
LEAGUE = "en.1"
FIELDS = ("date", "home_team", "away_team", "home_goals", "away_goals",
          "season", "league", "source", "source_match_key")

def parse_matches(document, season, today=None):
    """Přijme jen zápasy se známým konečným výsledkem PŘED dneškem."""
    if today is None:
        today = dt.datetime.now(dt.timezone.utc).date()
    records = []
    for m in document.get("matches", []):
        date_value = m.get("date")
        home, away = m.get("team1"), m.get("team2")
        if not (date_value and home and away):
            continue
        try:
            played_on = dt.date.fromisoformat(str(date_value))
        except ValueError:
            continue
        if played_on >= today:
            continue
        score = m.get("score")
        full_time = score.get("ft") if isinstance(score, dict) else score
        if (not isinstance(full_time, list) or len(full_time) != 2 or
            not all(type(v) is int and v >= 0 for v in full_time)):
            continue
        key = f"openfootball:{LEAGUE}:{played_on}:{home}:{away}"
        records.append({
            "date": played_on.isoformat(),
            "home_team": home,
            "away_team": away,
            "home_goals": full_time[0],
            "away_goals": full_time[1],
            "season": season,
            "league": "Premier League",
            "source": "openfootball",
            "source_match_key": key,
        })
    return records

def download(season, opener=urlopen):
    url = f"{BASE}/{season}/{LEAGUE}.json"
    request = Request(url, headers={"User-Agent": "football-predictor-v1"})
    with opener(request, timeout=20) as response:
        data = json.load(response)
    return parse_matches(data, season)

def refresh(output, seasons=SEASONS, downloader=download):
    """Nesmaže existující data, pokud selžou všechna stažení."""
    results, failures = {}, []
    for season in seasons:
        try:
            rows = downloader(season)
            for row in rows:
                results[row["source_match_key"]] = row
        except Exception as exc:
            failures.append(f"{season}: {exc}")
    if not results:
        raise RuntimeError("Nepodařilo se získat žádné odehrané zápasy. " +
                           "; ".join(failures))
    rows = sorted(results.values(), key=lambda r: (r["date"], r["home_team"], r["away_team"]))
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Přepis až po úplném vytvoření validního CSV.
    csv_data = io.StringIO()
    writer = csv.DictWriter(csv_data, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    temp = output.with_suffix(output.suffix + ".tmp")
    temp.write_text(csv_data.getvalue(), encoding="utf-8")
    os.replace(temp, output)
    return len(rows), failures

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/matches_real.csv")
    args = parser.parse_args()
    count, warnings = refresh(args.output)
    print(f"Staženo {count} historických zápasů.")
    if warnings:
        print("Některé sezony chybí: " + "; ".join(warnings))

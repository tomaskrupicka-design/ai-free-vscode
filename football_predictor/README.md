# Football Predictor V1 — sportovní analytika

## Co je skutečně hotové
- Historické výsledky z veřejného projektu OpenFootball (bez API klíče)
- Elo + Poisson a retrospektivní backtest (1/X/2, chybovost)
- CSV report a český Streamlit dashboard
- Volitelný **serverový** zápis historie zápasů a testů modelu do Supabase
- Ochrana proti použití výsledků jiných zápasů ze stejného dne

**Důležité:** Zdroj OpenFootball nemusí být aktuální; výsledky a časy publikace nejsou živým přenosem. Výstupy pro historické zápasy jsou výhradně RETROSPEKTIVNÍ backtesty, nikoliv skutečně dříve uložené předzápasové predikce. Žádná funkce pro sázení.

## Instalace

```bash
cd football_predictor
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Reálná data a dashboard

```bash
python main.py --real --fetch
streamlit run dashboard_app.py
```

Pro opakované přepočítání ze staženého souboru:
```bash
python main.py --real
```

Dataset: `data/matches_real.csv`. Report: `output/predictions_real.csv`.

## Supabase (volitelné)

1. V Supabase vytvořte projekt a spusťte `database/schema.sql` v jeho SQL Editoru.
2. Do soukromých serverových proměnných prostředí uložte `SUPABASE_URL` a `SUPABASE_SERVICE_ROLE_KEY`. Klíč **nikdy** nepište do GitHubu ani do klientského dashboardu. Nevkládejte ho do chatu.
3. Spusťte `python main.py --real --fetch --sync-supabase`.

Při synchronizaci se používá unikátní `source_match_key` a jedinečná kombinace (`match_id`, `model_version`, `prediction_kind`), takže další import nepřidá duplicitní zápasy. RLS je zapnuté; žádnou veřejnou politiku toto schéma nezakládá.

## Testovací/demo data

```bash
python main.py
```

Soubor `data/matches.csv` obsahuje **smyšlené zápasy** a nesmí být interpretován jako skutečné výsledky.

## Odkud pocházejí data
[OpenFootball/football.json](https://github.com/openfootball/football.json) – otevřená datová sada výsledků a rozpisů. Sezóna 2026/27 může obsahovat rozpisy zápasů bez konečných výsledků; ty importer vynechá.

## Zatím nezapojeno
- Projekt Supabase / SQL migrace a hesla musí být připojeny v prostředí s přístupem k Supabase.
- Živá skóre a ověřený čas zveřejnění dat, automatické předzápasové predikce a soukromé hostování dashboardu.

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


## Novinka: Football Radar 2.0 — srovnání tří modelů

Nový modul `models/team_goals.py` počítá odhady počtu gólů z historie branek,
oddělených útočných a obranných faktorů a časového útlumu starších výsledků.
**Tyto odhady nejsou naměřené xG.**

`evaluation/compare.py` porovnává tři retrospektivní modely na přesně stejných datech:
- `elo-poisson-v0.2`: původní model,
- `team-goals-v0.3`: časově vážená síla útoku a obrany,
- `historical-frequency-baseline`: průběžné četnosti výsledků.

Každý kalendářní den se všechny predikce vytvoří před použitím výsledků
toho dne. Pravidla i parametry musí být předem stanovené, aby se předešlo
úniku informací z budoucnosti.

### Spuštění na Kali Linuxu

```bash
cd ~/ai-free-vscode
git pull
cd football_predictor
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py --real --compare
python -m streamlit run dashboard_app.py
```

Chceš-li současně znovu načíst zdroj, použij `python main.py --real --fetch --compare`.

Výstup:
- `output/predictions_real.csv`: původní V1,
- `output/comparison_real.csv`: srovnání všech tří modelů po zápasech,
- `output/benchmark_summary_real.csv`: průměrný Brier score a log-loss.

Nový dashboard zobrazuje srovnání, filtr týmů, výběr novější sezóny,
detail jednotlivých zápasů a export CSV.

### Ověřená retrospektivní metrika (810 skutečných utkání)
| Model | Brier | Log-loss |
|---|---:|---:|
| Původní Elo + Poisson | 0.6305 | 1.0473 |
| Útok/obrana v0.3 | 0.6144 | 1.0252 |
| Historické četnosti | 0.6587 | 1.0870 |

Metriky jsou **historické**, nikoliv záruka budoucí výkonnosti.
Na zápasech od srpna 2026 jde zatím pouze o 50 utkání.
Pro odhad reálné robustnosti je nutné sbírat nové predikce před výkopem,
časově odděleně od jejich pozdějšího vyhodnocení.

### Supabase
V soukromém projektu Football Radar V1 v Supabase je nyní uloženo
810 skutečných zápasů a po 810 retrospektivních analýzách pro každý
ze tří modelů. Lokální příkaz `--compare` zatím zapíše výsledky
jen do CSV; `--sync-supabase` je vyhrazen původnímu modelu.
Služební/secret klíč nikdy nevkládej do veřejného frontend kódu ani GitHubu.

### Testy
```bash
python -m unittest discover -s tests -v
```

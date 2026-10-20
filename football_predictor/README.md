# Football Predictor V1 — sportovní analytika

## Co je skutečně hotové
- Historické výsledky z veřejného projektu OpenFootball (bez API klíče)
- Elo + Poisson a retrospektivní backtest (1/X/2, chybovost)
- CSV report a český Streamlit dashboard
- Volitelný **serverový** zápis historie zápasů a testů modelu do Supabase
- Ochrana proti použití výsledků jiných zápasů ze stejného dne

**Důležité:** Zdroj OpenFootball nemusí být aktuální; výsledky a časy publikace nejsou živým přenosem. Výstupy pro historické zápasy jsou výhradně RETROSPEKTIVNÍ backtesty, nikoliv skutečně dříve uložené předzápasové predikce. Žádná funkce pro sázení.

## Instalace

Vyžaduje Python 3.11 nebo novější. Streamlit je připnutý na testovanou verzi 1.66.0.

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

## Spolehlivé běhy a ovládání filtrů

```bash
python main.py --real --fetch --compare --timeout 300
python -m streamlit run dashboard_app.py
```

`--timeout` omezuje celý pracovní proces (stažení, modely a případný Supabase
import), výchozí limit je 300 sekund. Při překročení se proces ukončí a CLI
vrátí nenulový návratový kód. Nejde jen o timeout jednoho síťového požadavku.
Počítané CSV vznikají v dočasném adresáři a zveřejní se až po úspěšném
dokončení. Neúspěšný výpočet tedy nepřepíše předchozí reporty.
Publikace jednotlivých CSV je atomická, celá sada ale není databázová transakce;
dashboard upozorňuje na nedokončený běh. Stažený vstupní dataset se může změnit
i při pozdějším selhání výpočtu.

Stav se ukládá zvlášť pro skutečná a ukázková data do
`output/run_status_real.json` a `output/run_status_demo.json`. Dashboard ukazuje
poslední úspěšné dokončení v českém čase a upozorní na selhání, timeout nebo
starší srovnání modelů. Tento čas není časem posledního zápasu ani potvrzením
aktuálnosti OpenFootball. Staré výstupy bez záznamu nemají vymyšlené datum úspěchu.
Filtry týmů a období se aplikují tlačítkem **Použít filtry** ve formuláři;
samotná změna rozevírací nabídky nespouští nové filtrování.

Zámek brání souběžným běhům této lokální pipeline v jednom výstupním adresáři.
Při násilném ukončení řídicího procesu může stav zůstat `running`;
další spuštění jej nahradí. Zámek nenahrazuje distribuovanou koordinaci.

Supabase již používá upsert a unikátní klíče. Test `test_sync.py` simuluje
opakovaný import i opakování po částečném zápisu; neprovádí síťové zápisy do
produkce. Synchronizace více HTTP dávek není jedna transakce: přijaté dávky
nelze timeoutem vrátit zpět. Bezpečný další krok je opakovat stejný import.
Databázové schéma ani oprávnění se touto úpravou nemění.

`test_dashboard.py` ověřuje ve Streamlit AppTest formuláře, filtr týmů, detail
modelu, dostupnost exportu, chybějící data a upozornění po timeoutu.
`test_runtime.py` kontroluje ukončení zaseknutého procesu, zachování starých
výstupů a odmítnutí souběžného běhu. Nejde o test spuštění na uživatelově Kali.

Pydantic AI a LangGraph zatím v tomto projektu nejsou závislosti. Současné
výpočty jsou statistické modely; pro časový limit nepotřebují LLM ani API klíč.

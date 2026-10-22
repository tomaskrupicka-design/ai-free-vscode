# Crypto Analyzer → Supabase: hollywood

**Napojeni databaze (22. 10. 2026):** Uloziste Crypto Analyzer je existujici projekt `hollywood` (project ref `yhcefzqelvjzbazwngye`). Nezakladej dalsi projekt a nemen Football Radar V1.

## Overeny stav databaze
- `public.crypto_candles`: 478 hodinovych historickych svicek, 239 BTCUSDT a 239 ETHUSDT (`binance_spot`)
- `public.crypto_analysis_reports`: 2 ulozene reporty pro BTCUSDT/ETHUSDT, timeframe 1h
- `public.crypto_ingestion_runs`: 0 zaznamu
- Vsechny tabulky maji zapnute RLS a nemaji verejne politiky.
- Data jsou jednorazovy import; automaticka synchronizace jeste neni zapnuta.

## Dashboard a pripojeni
Aplikace `dashboard.py` ted umi zvolit:
1. `Supabase / hollywood` – nacte ulozene OHLCV svicky a posledni report ze Supabase.
2. `Binance Spot / verejna data` – stahne verejna spotova data rovnou ze zdroje.

Na **soukromem serveru** nastav promene prostredi:
```bash
export SUPABASE_URL="https://yhcefzqelvjzbazwngye.supabase.co"
export SUPABASE_SECRET_KEY="DOPLN_SOUKROMY_SERVEROVY_KLIC"
streamlit run dashboard.py
```

Klic ziskej bezpecne ze sveho projektu v administraci Supabase a nikdy ho neposilej do chatu nebo do GitHubu. Pro starsi instance lze alternativne pouzit `SUPABASE_SERVICE_ROLE_KEY`.

**Dulezite:** Sekretni klic musi zustat pouze na duveryhodnem serveru; tento dashboard nezverejnuj jako verejne pristupnou aplikaci s cizim pristupem ke konfiguraci. Pristupove udaje nesmi byt ulozene do zdrojoveho kodu. RLS blokuje pristup bez opravneni.

## Spusteni v Kali Linuxu
```bash
cd ~/ai-free-vscode/crypto_analyst
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard.py
```

## Omezeni
- Zdroj db aktualne obsahuje jen timeframe `1h`; jine intervaly vyzaduji import.
- Streamlit dashboard cte jen data, nic do DB nezapisuje.
- Pro pravidelny import je nutny dalsi serverovy job se zaznamem do `crypto_ingestion_runs`.
- Zadna soucast systemu neprovadi obchody nebo nepouziva pristup k obchodnimu uctu.

# Crypto Analyzer – Supabase databáze

**Aktuální stav (22. 10. 2026):** Analytické tabulky byly vytvořeny v EXISTUJÍCÍM Supabase projektu `hollywood`, nikoli v novém projektu. Název projektu v administraci je stále `hollywood`.

## Tabulky
- `public.crypto_candles`: historické OHLCV svíčky z veřejných tržních dat
- `public.crypto_analysis_reports`: analytické reporty EMA, RSI, ATR, objem a tržní úrovně
- `public.crypto_ingestion_runs`: volitelný protokol synchronizace

## První import
- BTCUSDT: 239 dokončených hodinových spotových svíček
- ETHUSDT: 239 dokončených hodinových spotových svíček
- 2 jednorázové analytické reporty modelu `ema-rsi-atr-v0.1`
- Zdroj: veřejná tržní data Binance Spot
- **Nejde o automatické aktualizace.** Pro průběžný sběr je potřeba zavést a otestovat plánovanou synchronizaci.

## Zabezpečení
Každá tabulka má zapnuté Row Level Security (RLS). Neexistují žádné obecně čitelné klientské politiky. Připojení pro zápis smějí používat jen důvěryhodné serverové komponenty s odpovídajícími právy.

V souborech repozitáře nikdy neuchovávej secret ani service-role klíč. Analytický engine nepoužívá obchodní API a nemůže zadávat příkazy.

## SQL
`schema.sql` je původní idempotentní návrh struktury nasazené databáze; nepoužívej ho pro vytváření dalšího placeného projektu.

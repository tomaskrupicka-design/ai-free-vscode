# Crypto Radar V1 – databáze

Tato složka připravuje **samostatnou** Supabase databázi pro veřejná historická krypto data a analytické výstupy.

## Struktura
- `crypto_candles`: časové řady OHLCV svíček
- `crypto_analysis_reports`: uložené indikátory, režim trhu a komentář
- `crypto_ingestion_runs`: protokol synchronizace dat

## Nasazení
1. Založ samostatný Supabase projekt po kontrole nákladů a dostupných projektových slotů.
2. V SQL editoru **nového** projektu spusť `schema.sql`.
3. Zkontroluj, že tabulky vznikly a RLS je povolené.
4. Připoj datovou synchronizaci ze serveru a ukládej jen dokončené svíčky.
5. Teprve potom zprovozni dashboard pro čtení výsledků.

**Bezpečnost:** Neukládej secret/service-role key do repozitáře ani do veřejného Streamlit dashboardu. Schéma nemá žádné veřejné RLS politiky a nemá žádné právo otevírat obchody.

**Stav:** SQL soubor je připraven, ale není aplikován do žádné databáze. Účet aktuálně používá dvě aktivní databáze na tarifu Free.

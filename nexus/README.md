# NEXUS secure foundation + AI

Aplikace je Vite + React frontend ve složce `nexus/`.

## Přihlášení bez e-mailu

Přihlášení zachovává přezdívku a osobní pozvánkový kód. Ověření probíhá na serverové Vercel API route `/api/authorize-guest`; kódy nejsou součástí klientského JavaScriptu.

Ve Vercelu nastav v projektu (Root Directory: `nexus`) tyto serverové Environment Variables pro Production i Preview:

- `NEXUS_INVITE_CODES`: JSON objekt povolených kódů, např. `{"SEM_PATRI_TVŮJ_NAHODNÝ_KÓD":true}`. Použij vlastní dlouhý náhodný kód a nikomu ho neposílej.
- `FIREBASE_SERVICE_ACCOUNT_JSON`: celý JSON service-account klíče Firebase projektu `nexus-chat-cc27e`. Jde o citlivý serverový klíč: nevkládej jej do chatu, repozitáře ani do proměnných začínajících `VITE_`.

Service account musí mít oprávnění vytvářet Firebase Authentication custom tokeny a zapisovat do Firestore pro rate limiting. Po uložení proměnných je nutné vytvořit nový Vercel deployment, aby se proměnné načetly.

API omezuje pokusy na 10 za 10 minut podle IP adresy. Přihlášení používá Firebase Custom Authentication; ve Firebase Authentication musí být povoleno Anonymous sign-in? Ne — custom token sign-in používá Firebase Authentication custom token flow a nevyžaduje e-mail/heslo poskytovatele.

## Firebase

- Firestore Database → Rules: nasadit `firestore.rules`.
- Realtime Database → Rules: nasadit `database.rules.json`.
- Firebase web config patří do Vercel `VITE_*` proměnných podle `.env.example`.

## NEXUS AI

NEXUS AI stále volá Firebase Cloud Function `nexusAi` a používá secret `OPENAI_API_KEY`. Tato AI funkce vyžaduje tarif Firebase, který podporuje Cloud Functions. Přihlášení přes Vercel API však placenou Firebase Cloud Function nepotřebuje.

## Bezpečnostní omezení

Místnosti jsou nyní sdílené pro všechny přihlášené uživatele. Aplikace zatím není end-to-end šifrovaný soukromý messenger. Neposílej přes ni citlivé zprávy, dokud nebude doplněno členství a E2E šifrování.

## Build

```bash
npm install
npm run build
```

# NEXUS secure foundation + AI

Tahle aplikace je samostatný frontend Vite + React ve složce `nexus/`.

## Spuštění frontendu

```bash
cd nexus
cp .env.example .env
npm install
npm run dev
```

Do `.env` zkopíruj webovou Firebase konfiguraci projektu. Pro `VITE_FIREBASE_DATABASE_URL` použij přesnou URL Realtime Database z Firebase Console.

## Firebase nastavení

1. Authentication → Sign-in method → zapnout **Anonymous**.
2. Firestore Database → Rules → nasadit obsah `firestore.rules`.
3. Realtime Database → vytvořit databázi.
4. Realtime Database → Rules → nasadit obsah `database.rules.json`.
5. Nainstalovat Firebase CLI a přihlásit se k projektu.
6. Nastavit OpenAI klíč jako Functions secret:

```bash
firebase functions:secrets:set OPENAI_API_KEY
```

7. Nasadit pravidla a AI funkci až po samostatném schválení:

```bash
firebase deploy --only firestore:rules,database,functions:nexusAi
```

Cloud Function běží v regionu `europe-west1` na Node.js 22, vyžaduje Firebase Authentication a používá serverový secret. Má limit 10 požadavků za minutu a 80 požadavků denně na jedno Firebase UID.

## AI vrstva

Frontend používá `httpsCallable(functions, 'nexusAi')`. Funkce přijímá nejvýše 20 zpráv, nejvýše 4000 znaků na zprávu a 12000 znaků celkem. Výstup je omezen na 1200 tokenů. Požadavek používá `store: false`.

`OPENAI_API_KEY` je Firebase Functions secret a nikdy nepatří do Reactu, `VITE_*` proměnných ani do veřejného repozitáře. Texty konverzace z panelu NEXUS AI se posílají do OpenAI Responses API; `store: false` je nastaveno v požadavku, ale uživatel by i tak neměl zadávat hesla ani citlivé osobní údaje.

## Bezpečnostní hranice

- Firebase web config není serverové tajemství; ochranu dat zajišťují Firebase Authentication a Security Rules.
- Firestore pravidla omezují zprávy na známé místnosti, kontrolují povinná pole a typy, validují odpovědi a dovolují uživateli měnit pouze jeho vlastní reakci.
- Realtimová presence data mají validaci UID, přezdívky, místnosti a datového typu.
- AI funkce má serverové limity délky vstupu a rate limit podle Firebase UID.

**Důležité:** Anonymous Authentication není ověření skutečné identity. Aktuální místnosti jsou sdílené pro všechny přihlášené návštěvníky a pravidla zatím nevyžadují členství v konkrétní místnosti. Aplikace proto není soukromým osobním chatem ani end-to-end šifrovaným messengerem. Neposílej přes ni důvěrné zprávy. Pro soukromé konverzace je nutné doplnit pozvánky/členství a samostatnou end-to-end šifrovací vrstvu.

## Vercel

Projekt používá Vite. Ve Vercelu je potřeba nastavit:

- Framework Preset: Vite
- Root Directory: `nexus`
- Build Command: `npm run build`
- Output Directory: `dist`
- Node.js: 20.x

Vercel environment variables musí obsahovat veřejnou Firebase web konfiguraci z `.env.example`. OpenAI secret zůstává pouze ve Firebase Functions Secret Manager.

## Testy a nasazení

GitHub Actions workflow `NEXUS CI` sestaví frontend na Node.js 22, provede audit produkčních npm závislostí, zkontroluje syntaxi Cloud Function a validitu JSON konfigurace. Firebase Functions používají přesně připnuté verze `firebase-admin` 14.5.0 a `firebase-functions` 7.4.0. CI ani tento audit nenasazují Firebase nebo Vercel.

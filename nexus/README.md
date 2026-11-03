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

1. Přihlášení používá Firebase Custom Authentication tokeny vytvořené serverově přes Firebase Admin SDK; není potřeba zapínat e-mailové ani anonymní přihlášení. Frontend nabízí pouze přezdívku a osobní přístupový kód; e-mail ani heslo se nezadávají.
2. Nastav serverový secret s povolenými individuálními kódy. Hodnota secretu je JSON objekt, kde každý povolený kód má hodnotu true, například {"KOD-OSOBA-A-NAHODNY-32-ZNAKU":true,"KOD-OSOBA-B-NAHODNY-32-ZNAKU":true}. Kódy musí být náhodné a odlišné pro každého pozvaného uživatele:

```bash
firebase functions:secrets:set NEXUS_INVITE_CODES
```

Při výzvě vlož celý JSON objekt. Secret zůstává na serveru a není součástí frontendu.
3. Firestore Database → Rules → nasadit obsah `firestore.rules`.
4. Realtime Database → vytvořit databázi.
5. Realtime Database → Rules → nasadit obsah `database.rules.json`.
6. Nainstalovat Firebase CLI a přihlásit se k projektu.
7. Nastavit OpenAI klíč jako Functions secret:

```bash
firebase functions:secrets:set OPENAI_API_KEY
```

8. Nasadit přihlašovací a AI funkce až po nastavení secretů:

```bash
firebase deploy --only functions:authorizeGuest,functions:nexusAi
```

Cloud Function běží v regionu `europe-west1`, vyžaduje Firebase Authentication a používá serverový secret. Má limit 10 požadavků za minutu a 80 požadavků denně na jedno Firebase UID.

## AI vrstva

Frontend používá `httpsCallable(functions, 'authorizeGuest')` pro přihlášení a `httpsCallable(functions, 'nexusAi')` pro AI. Funkce přijímá nejvýše 20 zpráv, nejvýše 4000 znaků na zprávu a 12000 znaků celkem. Výstup je omezen na 1200 tokenů. Požadavek používá `store: false`.

`OPENAI_API_KEY` je Firebase Functions secret a nikdy nepatří do Reactu, `VITE_*` proměnných ani do veřejného repozitáře.

## Bezpečnostní hranice

- Firebase web config není serverové tajemství; ochranu dat zajišťují Firebase Authentication a Security Rules.
- Vstup je přes přezdívku a individuální pozvánkový kód. Server ověří kód uložený ve Firebase Secret Manageru, omezí pokusy podle IP a vytvoří vlastní Firebase UID přes custom token. Přístupové kódy nejsou součástí klientského kódu.
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

GitHub Actions workflow `NEXUS CI` sestaví frontend, zkontroluje syntaxi Cloud Function a validitu JSON konfigurace. CI ani tento audit nenasazují Firebase nebo Vercel.

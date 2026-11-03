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

1. V Authentication → Sign-in method zapni **Email/Password**.
2. V Authentication → Users vytvoř uživatelské účty předem. Veřejná registrace v aplikaci není dostupná. Každému uživateli předej jeho e-mail a heslo bezpečným způsobem.
3. Firestore Database → Rules → nasadit obsah `firestore.rules`.
4. Realtime Database → vytvořit databázi.
5. Realtime Database → Rules → nasadit obsah `database.rules.json`.
6. Pro samotné přihlášení není potřeba Cloud Functions, Firebase Admin SDK, vlastní token ani placený tarif Blaze.

Přihlášení používá přímo Firebase Authentication `signInWithEmailAndPassword`. Přezdívka se uloží jako zobrazované jméno účtu. Aplikace nepovoluje veřejné vytváření účtů.

## AI vrstva

Frontend používá `httpsCallable(functions, 'nexusAi')` pro AI. Funkce přijímá nejvýše 20 zpráv, nejvýše 4000 znaků na zprávu a 12000 znaků celkem. Výstup je omezen na 1200 tokenů. Požadavek používá `store: false`.

`OPENAI_API_KEY` je Firebase Functions secret a nikdy nepatří do Reactu, `VITE_*` proměnných ani do veřejného repozitáře. **NEXUS AI nadále používá Cloud Functions, které vyžadují tarif podporující Functions.** Změna přihlašování tento požadavek pro AI neodstraňuje.

## Bezpečnostní hranice

- Firebase web config není serverové tajemství; ochranu dat zajišťují Firebase Authentication a Security Rules.
- Přístup mají pouze předem vytvořené účty Firebase Authentication; aplikace nemá veřejnou registraci.
- Firestore pravidla omezují zprávy na známé místnosti, kontrolují povinná pole a typy, validují odpovědi a dovolují uživateli měnit pouze jeho vlastní reakci.
- Realtime presence data mají validaci UID, přezdívky, místnosti a datového typu.
- Aktuální místnosti jsou sdílené pro všechny přihlášené účty a pravidla zatím nevyžadují členství v konkrétní místnosti. Aplikace proto zatím není soukromým osobním chatem ani end-to-end šifrovaným messengerem. Neposílej přes ni důvěrné zprávy. Pro soukromé konverzace je nutné doplnit členství a samostatnou end-to-end šifrovací vrstvu.

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

# NEXUS secure foundation + AI

Tahle verze převádí původní jednosouborový prototyp do Vite + React projektu a opravuje nejrizikovější části:

- Firebase Anonymous Auth dává každému klientovi vlastní UID.
- Přezdívka už není identita uživatele; je pouze zobrazované jméno.
- Firestore ukládá zprávy a pravidla povolují autorovi mazání vlastních zpráv.
- Reakce jsou uložené podle UID a pravidla dovolí uživateli měnit jen vlastní reakci.
- Realtime Database řeší presence pomocí `onDisconnect()`, bez heartbeat zápisu každých 20 sekund.
- Konfigurace je přes `.env`; žádný serverový tajný klíč nepatří do klienta.
- Odeslání zprávy zachová text při chybě a má limit 2000 znaků.
- Místnost **NEXUS AI** volá přihlášenou Firebase callable funkci.
- `OPENAI_API_KEY` je Firebase Functions secret a nikdy nejde do Reactu ani Firestore.

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

7. Nasadit pravidla a AI funkci:

```bash
firebase deploy --only firestore:rules,database,functions:nexusAi
```

Cloud Function běží v regionu `europe-west1` a před voláním OpenAI kontroluje Firebase Authentication. Klient proto neposílá žádný OpenAI secret.

## AI vrstva

Frontend používá `httpsCallable(functions, 'nexusAi')`. Funkce přijme posledních 20 zpráv, každou omezí na 4000 znaků a volá OpenAI Responses API. Aktuální model je v `functions/index.js` nastavený na `gpt-6-luna`.

## Bezpečnost

Firebase web config (včetně webového `apiKey`) není serverové tajemství; skutečnou ochranu dat dělají Authentication + Security Rules. Tajné klíče jako `OPENAI_API_KEY` se nikdy nesmí dát do `VITE_*` proměnné, React kódu ani veřejného repozitáře.

## Kontrola

GitHub Actions workflow `NEXUS CI` instaluje frontend i Functions dependencies, sestaví produkční Vite build a kontroluje syntaxi Cloud Function.

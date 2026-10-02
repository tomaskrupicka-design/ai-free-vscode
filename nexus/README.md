# NEXUS secure foundation

Tahle verze převádí původní jednosouborový prototyp do Vite + React projektu a opravuje nejrizikovější části:

- Firebase Anonymous Auth dává každému klientovi vlastní UID.
- Přezdívka už není identita uživatele; je pouze zobrazované jméno.
- Firestore ukládá zprávy a pravidla povolují autorovi mazání vlastních zpráv.
- Reakce jsou uložené podle UID a pravidla dovolí uživateli měnit jen vlastní reakci.
- Realtime Database řeší presence pomocí `onDisconnect()`, bez heartbeat zápisu každých 20 sekund.
- Konfigurace je přes `.env`; žádný serverový tajný klíč nepatří do klienta.
- Odeslání zprávy zachová text při chybě a má limit 2000 znaků.

## Spuštění

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

## Bezpečnost

Firebase web config (včetně webového `apiKey`) není serverové tajemství; skutečnou ochranu dat dělají Authentication + Security Rules. Tajné klíče jako `OPENAI_API_KEY` se ale nikdy nesmí dát do `VITE_*` proměnné ani do React kódu.

## Další krok

AI část připoj přes serverový endpoint (Firebase Functions, Cloud Run, Vercel Function apod.). Klient NEXUS potom volá jen vlastní endpoint a `OPENAI_API_KEY` zůstává jako serverový secret.

const admin = require('firebase-admin')
const crypto = require('node:crypto')
const { onCall, HttpsError } = require('firebase-functions/v2/https')
const { defineSecret } = require('firebase-functions/params')

if (!admin.apps.length) {
  admin.initializeApp()
}

const db = admin.firestore()
const OPENAI_API_KEY = defineSecret('OPENAI_API_KEY')
const NEXUS_INVITE_CODES = defineSecret('NEXUS_INVITE_CODES')

exports.authorizeGuest = onCall(
  {
    region: 'europe-west1',
    secrets: [NEXUS_INVITE_CODES],
    timeoutSeconds: 15,
    memory: '256MiB',
  },
  async (request) => {
    const nickname = typeof request.data?.nickname === 'string'
      ? request.data.nickname.trim()
      : ''
    const accessCode = typeof request.data?.accessCode === 'string'
      ? request.data.accessCode.trim()
      : ''

    if (nickname.length < 2 || nickname.length > 20 || accessCode.length < 8 || accessCode.length > 128) {
      throw new HttpsError('invalid-argument', 'Přezdívka nebo přístupový kód nemají platný formát.')
    }

    const ip = request.rawRequest.ip || 'unknown'
    const ipKey = crypto.createHash('sha256').update(ip).digest('hex')
    const attemptRef = db.collection('_nexusGuestAccessAttempts').doc(ipKey)
    const now = Date.now()
    await db.runTransaction(async (transaction) => {
      const snapshot = await transaction.get(attemptRef)
      const state = snapshot.exists ? snapshot.data() : {}
      const windowStart = Number(state.windowStart || 0)
      const attempts = now - windowStart < 10 * 60 * 1000
        ? Number(state.attempts || 0)
        : 0

      if (attempts >= 10) {
        throw new HttpsError('resource-exhausted', 'Příliš mnoho pokusů. Zkus to za chvíli.')
      }

      transaction.set(attemptRef, {
        windowStart: attempts ? windowStart : now,
        attempts: attempts + 1,
        updatedAt: admin.firestore.FieldValue.serverTimestamp(),
      })
    })

    let allowedCodes
    try {
      allowedCodes = JSON.parse(NEXUS_INVITE_CODES.value())
    } catch {
      console.error('NEXUS_INVITE_CODES secret must contain a JSON object.')
      throw new HttpsError('failed-precondition', 'Přístupové kódy nejsou na serveru nastavené.')
    }

    if (
      !allowedCodes
      || typeof allowedCodes !== 'object'
      || Array.isArray(allowedCodes)
      || allowedCodes[accessCode] !== true
    ) {
      throw new HttpsError('unauthenticated', 'Přístupový kód není platný.')
    }

    const uid = `guest_${crypto.randomUUID().replace(/-/g, '')}`
    const token = await admin.auth().createCustomToken(uid, {
      guest: true,
      nickname,
    })

    return { token }
  },
)
const MODEL = 'gpt-6-luna'
const MAX_MESSAGES = 20
const MAX_MESSAGE_CHARS = 4000
const MAX_TOTAL_CHARS = 12000
const MAX_REQUESTS_PER_MINUTE = 10
const MAX_REQUESTS_PER_DAY = 80

function extractOutputText(data) {
  if (typeof data?.output_text === 'string' && data.output_text.trim()) {
    return data.output_text.trim()
  }

  return (data?.output || [])
    .flatMap((item) => item?.content || [])
    .filter((part) => part?.type === 'output_text' && typeof part.text === 'string')
    .map((part) => part.text)
    .join('\n')
    .trim()
}

async function enforceRateLimit(uid) {
  const now = Date.now()
  const minuteBucket = Math.floor(now / 60_000)
  const dayKey = new Date(now).toISOString().slice(0, 10)
  const usageRef = db.collection('_nexusAiUsage').doc(uid)

  await db.runTransaction(async (transaction) => {
    const snapshot = await transaction.get(usageRef)
    const usage = snapshot.exists ? snapshot.data() : {}

    const minuteCount = usage.minuteBucket === minuteBucket
      ? Number(usage.minuteCount || 0)
      : 0
    const dayCount = usage.dayKey === dayKey
      ? Number(usage.dayCount || 0)
      : 0

    if (minuteCount >= MAX_REQUESTS_PER_MINUTE || dayCount >= MAX_REQUESTS_PER_DAY) {
      throw new HttpsError('resource-exhausted', 'Byl dosažen limit požadavků NEXUS AI. Zkus to později.')
    }

    transaction.set(usageRef, {
      minuteBucket,
      minuteCount: minuteCount + 1,
      dayKey,
      dayCount: dayCount + 1,
      updatedAt: admin.firestore.FieldValue.serverTimestamp(),
    })
  })
}

exports.nexusAi = onCall(
  {
    region: 'europe-west1',
    secrets: [OPENAI_API_KEY],
    timeoutSeconds: 60,
    memory: '256MiB',
  },
  async (request) => {
    if (!request.auth) {
      throw new HttpsError('unauthenticated', 'Pro NEXUS AI je nutné přihlášení.')
    }

    const rawMessages = request.data?.messages
    if (!Array.isArray(rawMessages) || rawMessages.length === 0 || rawMessages.length > MAX_MESSAGES) {
      throw new HttpsError('invalid-argument', 'Počet zpráv musí být mezi 1 a 20.')
    }

    let totalChars = 0
    const messages = rawMessages.map((message) => {
      if (
        !message
        || !['user', 'assistant'].includes(message.role)
        || typeof message.content !== 'string'
      ) {
        throw new HttpsError('invalid-argument', 'Formát zprávy není platný.')
      }

      const content = message.content.trim()
      if (!content || content.length > MAX_MESSAGE_CHARS) {
        throw new HttpsError('invalid-argument', 'Zpráva je prázdná nebo překračuje limit 4000 znaků.')
      }

      totalChars += content.length
      return { role: message.role, content }
    })

    if (totalChars > MAX_TOTAL_CHARS) {
      throw new HttpsError('invalid-argument', 'Celková délka konverzace překračuje limit 12000 znaků.')
    }

    if (!messages.some((message) => message.role === 'user')) {
      throw new HttpsError('invalid-argument', 'Konverzace musí obsahovat uživatelskou zprávu.')
    }

    await enforceRateLimit(request.auth.uid)

    const response = await fetch('https://api.openai.com/v1/responses', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${OPENAI_API_KEY.value()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: MODEL,
        instructions: 'Jsi NEXUS AI, stručný a užitečný asistent uvnitř chatu NEXUS. Odpovídej česky, pokud uživatel nepoužije jiný jazyk.',
        input: messages,
        max_output_tokens: 1200,
        store: false,
      }),
    })

    if (!response.ok) {
      console.error('OpenAI API error', response.status)
      throw new HttpsError('internal', 'OpenAI API požadavek selhal.')
    }

    const data = await response.json()
    const text = extractOutputText(data)

    if (!text) {
      throw new HttpsError('internal', 'OpenAI API vrátilo prázdnou odpověď.')
    }

    return { text, model: MODEL }
  },
)

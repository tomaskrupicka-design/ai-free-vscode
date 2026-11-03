import crypto from 'node:crypto'
import { cert, getApps, initializeApp } from 'firebase-admin/app'
import { getAuth } from 'firebase-admin/auth'
import { getFirestore, FieldValue } from 'firebase-admin/firestore'

function getAdminApp() {
  if (getApps().length) return getApps()[0]
  const rawServiceAccount = process.env.FIREBASE_SERVICE_ACCOUNT_JSON
  if (!rawServiceAccount) throw new Error('Missing FIREBASE_SERVICE_ACCOUNT_JSON')
  const serviceAccount = JSON.parse(rawServiceAccount)
  return initializeApp({ credential: cert(serviceAccount) })
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST')
    return res.status(405).json({ error: 'Method not allowed.' })
  }

  const origin = req.headers.origin
  const host = req.headers.host
  if (origin && host && new URL(origin).host !== host) {
    return res.status(403).json({ error: 'Invalid request origin.' })
  }

  const nickname = typeof req.body?.nickname === 'string' ? req.body.nickname.trim() : ''
  const accessCode = typeof req.body?.accessCode === 'string' ? req.body.accessCode.trim() : ''
  if (nickname.length < 2 || nickname.length > 20 || accessCode.length < 8 || accessCode.length > 128) {
    return res.status(400).json({ error: 'Zkontroluj přezdívku a přístupový kód.' })
  }

  let allowedCodes
  try {
    if (!process.env.NEXUS_INVITE_CODES) throw new Error('Missing invite-code secret')
    allowedCodes = JSON.parse(process.env.NEXUS_INVITE_CODES)
  } catch {
    return res.status(503).json({ error: 'Ověření přístupu zatím není nakonfigurované.' })
  }

  if (!allowedCodes || typeof allowedCodes !== 'object' || Array.isArray(allowedCodes)) {
    return res.status(503).json({ error: 'Konfigurace přístupových kódů není platná.' })
  }

  try {
    const app = getAdminApp()
    const db = getFirestore(app)
    const ip = String(req.headers['x-forwarded-for'] || req.socket?.remoteAddress || 'unknown').split(',')[0].trim()
    const ipKey = crypto.createHash('sha256').update(ip).digest('hex')
    const attemptRef = db.collection('_nexusGuestAccessAttempts').doc(ipKey)
    const now = Date.now()

    await db.runTransaction(async (transaction) => {
      const snapshot = await transaction.get(attemptRef)
      const state = snapshot.exists ? snapshot.data() : {}
      const windowStart = Number(state.windowStart || 0)
      const attempts = now - windowStart < 10 * 60 * 1000 ? Number(state.attempts || 0) : 0
      if (attempts >= 10) {
        const error = new Error('RATE_LIMIT')
        error.code = 'RATE_LIMIT'
        throw error
      }
      transaction.set(attemptRef, {
        windowStart: attempts ? windowStart : now,
        attempts: attempts + 1,
        updatedAt: FieldValue.serverTimestamp(),
      })
    })

    if (allowedCodes[accessCode] !== true) {
      return res.status(401).json({ error: 'Přístupový kód není platný.' })
    }

    const uid = `guest_${crypto.randomUUID().replace(/-/g, '')}`
    const token = await getAuth(app).createCustomToken(uid, { guest: true, nickname })
    return res.status(200).json({ token })
  } catch (error) {
    if (error.code === 'RATE_LIMIT') {
      return res.status(429).json({ error: 'Příliš mnoho pokusů. Zkus to za chvíli.' })
    }
    console.error('NEXTER guest authorization failed:', error)
    return res.status(503).json({ error: 'Ověření přístupu je momentálně nedostupné.' })
  }
}

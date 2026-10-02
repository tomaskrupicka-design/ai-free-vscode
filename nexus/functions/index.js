const { onCall, HttpsError } = require('firebase-functions/v2/https')
const { defineSecret } = require('firebase-functions/params')

const OPENAI_API_KEY = defineSecret('OPENAI_API_KEY')
const MODEL = 'gpt-6-luna'

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
    if (!Array.isArray(rawMessages) || rawMessages.length === 0) {
      throw new HttpsError('invalid-argument', 'Chybí zprávy.')
    }

    const messages = rawMessages
      .slice(-20)
      .map((message) => ({
        role: message?.role === 'assistant' ? 'assistant' : 'user',
        content: String(message?.content || '').trim().slice(0, 4000),
      }))
      .filter((message) => message.content)

    if (!messages.length) {
      throw new HttpsError('invalid-argument', 'Zprávy jsou prázdné.')
    }

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

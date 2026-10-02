import { useEffect, useRef, useState } from 'react'
import { httpsCallable } from 'firebase/functions'
import { functions } from '../firebase'

const MAX_AI_INPUT = 4000
const nexusAi = httpsCallable(functions, 'nexusAi')

export default function AiPanel() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Jsem NEXUS AI. Napiš, s čím chceš pomoct.',
    },
  ])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async () => {
    const text = input.trim()
    if (!text || sending) return

    const userMessage = { role: 'user', content: text }
    const nextMessages = [...messages, userMessage]
    setMessages(nextMessages)
    setInput('')
    setSending(true)
    setError('')

    try {
      const payload = nextMessages
        .filter((message) => message.role === 'user' || message.role === 'assistant')
        .slice(-20)
        .map(({ role, content }) => ({ role, content }))

      const result = await nexusAi({ messages: payload })
      const answer = result.data?.text

      if (!answer) throw new Error('AI odpověď je prázdná.')

      setMessages((current) => [
        ...current,
        { role: 'assistant', content: answer },
      ])
    } catch (err) {
      console.error(err)
      setError('NEXUS AI teď neodpověděl. Zkontroluj nasazení Cloud Function a OPENAI_API_KEY secret.')
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="ai-shell">
      <div className="ai-messages">
        {messages.map((message, index) => (
          <div
            className={`ai-message-row ${message.role === 'user' ? 'ai-user' : 'ai-assistant'}`}
            key={`${message.role}-${index}`}
          >
            <div className="ai-label">{message.role === 'user' ? 'TY' : 'NEXUS AI'}</div>
            <div className="ai-bubble">{message.content}</div>
          </div>
        ))}

        {sending && (
          <div className="ai-message-row ai-assistant">
            <div className="ai-label">NEXUS AI</div>
            <div className="ai-bubble">Přemýšlím…</div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {error && <div className="chat-error">{error}</div>}

      <div className="composer">
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
              event.preventDefault()
              send()
            }
          }}
          maxLength={MAX_AI_INPUT}
          placeholder="Napiš NEXUS AI…"
          aria-label="Zpráva pro NEXUS AI"
        />
        <span className="character-count">{input.length}/{MAX_AI_INPUT}</span>
        <button
          className="send-button"
          onClick={send}
          disabled={!input.trim() || sending}
          aria-label="Odeslat NEXUS AI"
        >
          {sending ? '…' : '➤'}
        </button>
      </div>
    </div>
  )
}

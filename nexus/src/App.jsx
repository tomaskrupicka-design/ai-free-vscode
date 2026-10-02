import { useEffect, useMemo, useRef, useState } from 'react'
import { onAuthStateChanged, signInAnonymously, signOut } from 'firebase/auth'
import {
  addDoc,
  collection,
  deleteField,
  doc,
  limitToLast,
  onSnapshot,
  orderBy,
  query,
  serverTimestamp as firestoreTimestamp,
  updateDoc,
} from 'firebase/firestore'
import {
  onDisconnect,
  onValue,
  ref,
  serverTimestamp as databaseTimestamp,
  set,
} from 'firebase/database'

import Login from './components/Login'
import Sidebar from './components/Sidebar'
import MessageBubble from './components/MessageBubble'
import AiPanel from './components/AiPanel'
import { auth, db, rtdb } from './firebase'
import { MAX_MESSAGE_LENGTH, ROOMS } from './constants'

const NICK_KEY = 'nexus:nickname'

export default function App() {
  const [authReady, setAuthReady] = useState(false)
  const [user, setUser] = useState(null)
  const [nickname, setNickname] = useState(null)
  const [authBusy, setAuthBusy] = useState(false)
  const [authError, setAuthError] = useState('')

  const [room, setRoom] = useState('general')
  const [messages, setMessages] = useState([])
  const [online, setOnline] = useState([])
  const [input, setInput] = useState('')
  const [replyTo, setReplyTo] = useState(null)
  const [picker, setPicker] = useState(null)
  const [sidebar, setSidebar] = useState(true)
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [chatError, setChatError] = useState('')

  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  const currentRoom = useMemo(
    () => ROOMS.find((item) => item.id === room) ?? ROOMS[0],
    [room],
  )

  useEffect(() => {
    return onAuthStateChanged(auth, (nextUser) => {
      setUser(nextUser)
      const savedNick = localStorage.getItem(NICK_KEY)
      setNickname(nextUser && savedNick ? savedNick : null)
      setAuthReady(true)
    })
  }, [])

  useEffect(() => {
    if (!user || !nickname) return undefined

    if (room === 'nexus-ai') {
      setMessages([])
      setLoading(false)
      return undefined
    }

    setLoading(true)
    setChatError('')

    const messagesQuery = query(
      collection(db, 'rooms', room, 'messages'),
      orderBy('timestamp', 'asc'),
      limitToLast(100),
    )

    const stop = onSnapshot(
      messagesQuery,
      (snapshot) => {
        setMessages(snapshot.docs.map((item) => ({ id: item.id, ...item.data() })))
        setLoading(false)
      },
      (error) => {
        console.error(error)
        setChatError('Zprávy se nepodařilo načíst.')
        setLoading(false)
      },
    )

    return () => {
      stop()
      setMessages([])
    }
  }, [room, user, nickname])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    setReplyTo(null)
    setPicker(null)
    setChatError('')
  }, [room])

  useEffect(() => {
    if (!user || !nickname) return undefined

    const statusRef = ref(rtdb, `presence/${user.uid}`)
    const connectedRef = ref(rtdb, '.info/connected')

    const stopConnection = onValue(connectedRef, async (snapshot) => {
      if (snapshot.val() !== true) return

      const offlineState = {
        uid: user.uid,
        nickname,
        room,
        online: false,
        lastSeen: databaseTimestamp(),
      }

      const onlineState = {
        uid: user.uid,
        nickname,
        room,
        online: true,
        lastSeen: databaseTimestamp(),
      }

      try {
        await onDisconnect(statusRef).set(offlineState)
        await set(statusRef, onlineState)
      } catch (error) {
        console.error('Presence error:', error)
      }
    })

    return () => stopConnection()
  }, [user, nickname, room])

  useEffect(() => {
    if (!user) return undefined

    const presenceRef = ref(rtdb, 'presence')
    return onValue(presenceRef, (snapshot) => {
      const value = snapshot.val() || {}
      const people = Object.entries(value)
        .map(([uid, data]) => ({ uid, ...data }))
        .filter((person) => person.online === true)
      setOnline(people)
    })
  }, [user])

  const handleLogin = async (nick) => {
    const clean = nick.trim().slice(0, 20)
    if (clean.length < 2) return

    setAuthBusy(true)
    setAuthError('')

    try {
      localStorage.setItem(NICK_KEY, clean)
      const nextUser = auth.currentUser ?? (await signInAnonymously(auth)).user
      setUser(nextUser)
      setNickname(clean)
    } catch (error) {
      console.error(error)
      localStorage.removeItem(NICK_KEY)
      setAuthError('Přihlášení se nepodařilo. Zkontroluj, že je ve Firebase zapnuté Anonymous Authentication.')
    } finally {
      setAuthBusy(false)
    }
  }

  const handleLogout = async () => {
    if (user) {
      try {
        await set(ref(rtdb, `presence/${user.uid}`), {
          uid: user.uid,
          nickname: nickname || 'uživatel',
          room,
          online: false,
          lastSeen: databaseTimestamp(),
        })
      } catch (error) {
        console.error(error)
      }
    }

    localStorage.removeItem(NICK_KEY)
    setNickname(null)
    await signOut(auth)
  }

  const send = async () => {
    const text = input.trim()
    if (!user || !nickname || !text || sending) return

    if (text.length > MAX_MESSAGE_LENGTH) {
      setChatError(`Zpráva může mít maximálně ${MAX_MESSAGE_LENGTH} znaků.`)
      return
    }

    setSending(true)
    setChatError('')

    try {
      await addDoc(collection(db, 'rooms', room, 'messages'), {
        authorUid: user.uid,
        nickname,
        text,
        timestamp: firestoreTimestamp(),
        reactions: {},
        replyTo: replyTo
          ? {
              authorUid: replyTo.authorUid,
              nickname: replyTo.nickname,
              text: replyTo.text,
            }
          : null,
      })

      setInput('')
      setReplyTo(null)
      inputRef.current?.focus()
    } catch (error) {
      console.error(error)
      setChatError('Zprávu se nepodařilo odeslat. Text zůstal zachovaný.')
    } finally {
      setSending(false)
    }
  }

  const toggleReaction = async (messageId, emoji) => {
    if (!user) return

    const message = messages.find((item) => item.id === messageId)
    if (!message) return

    const messageRef = doc(db, 'rooms', room, 'messages', messageId)
    const current = message.reactions?.[user.uid]

    try {
      await updateDoc(messageRef, {
        [`reactions.${user.uid}`]: current === emoji ? deleteField() : emoji,
      })
      setPicker(null)
    } catch (error) {
      console.error(error)
      setChatError('Reakci se nepodařilo uložit.')
    }
  }

  if (!authReady) {
    return <div className="center-state">Načítám NEXUS…</div>
  }

  if (!user || !nickname) {
    return <Login onLogin={handleLogin} busy={authBusy} error={authError} />
  }

  const usersHere = online.filter(
    (person) => person.room === room && person.uid !== user.uid,
  )

  return (
    <div className="app-shell" onClick={() => setPicker(null)}>
      {sidebar && (
        <Sidebar
          online={online}
          room={room}
          onRoomChange={setRoom}
          nickname={nickname}
          onLogout={handleLogout}
        />
      )}

      <section className="chat-shell">
        <header className="chat-header">
          <button className="icon-button" onClick={() => setSidebar((value) => !value)}>☰</button>
          <span className="room-emoji">{currentRoom.emoji}</span>
          <div className="header-copy">
            <strong style={{ color: currentRoom.color }}>#{currentRoom.name}</strong>
            <small>
              {currentRoom.ai
                ? 'Soukromý AI asistent'
                : usersHere.length
                  ? `${usersHere.map((person) => person.nickname).join(', ')} zde`
                  : 'nikdo jiný tady není'}
            </small>
          </div>
        </header>

        {currentRoom.ai ? (
          <AiPanel />
        ) : (
          <>
        <div className="messages" onClick={() => setPicker(null)}>
          {loading && <div className="center-state">Načítám…</div>}

          {!loading && messages.length === 0 && (
            <div className="empty-state">
              <div>{currentRoom.emoji}</div>
              <p>Zatím nic. Začni konverzaci!</p>
            </div>
          )}

          {messages.map((message) => (
            <MessageBubble
              key={message.id}
              msg={message}
              currentUid={user.uid}
              roomColor={currentRoom.color}
              pickerOpen={picker === message.id}
              onTogglePicker={(messageId) => {
                setPicker((current) => (current === messageId ? null : messageId))
              }}
              onReply={(selected) => {
                setReplyTo(selected)
                inputRef.current?.focus()
              }}
              onReact={toggleReaction}
            />
          ))}

          <div ref={bottomRef} />
        </div>

        {replyTo && (
          <div className="reply-bar">
            <div>
              <strong>↩ {replyTo.nickname}</strong>
              <span>{replyTo.text.slice(0, 100)}{replyTo.text.length > 100 ? '…' : ''}</span>
            </div>
            <button onClick={() => setReplyTo(null)}>✕</button>
          </div>
        )}

        {chatError && <div className="chat-error">{chatError}</div>}

        <footer className="composer">
          <input
            ref={inputRef}
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault()
                send()
              }
            }}
            maxLength={MAX_MESSAGE_LENGTH}
            placeholder={replyTo ? `Odpovědět ${replyTo.nickname}…` : `Napsat do #${currentRoom.name}…`}
            aria-label="Zpráva"
          />
          <span className="character-count">{input.length}/{MAX_MESSAGE_LENGTH}</span>
          <button
            className="send-button"
            onClick={send}
            disabled={!input.trim() || sending}
            aria-label="Odeslat"
          >
            {sending ? '…' : '➤'}
          </button>
        </footer>
          </>
        )}
      </section>
    </div>
  )
}

import { useState } from 'react'

export default function Login({ onAuthenticate, busy, error }) {
  const [mode, setMode] = useState('login')
  const [nickname, setNickname] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const cleanNickname = nickname.trim()
  const validEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())
  const validPassword = password.length >= 6
  const validNickname = cleanNickname.length >= 2 && cleanNickname.length <= 20
  const valid = validEmail && validPassword && (mode === 'login' || validNickname)

  const submit = (event) => {
    event.preventDefault()
    if (valid && !busy) onAuthenticate({ mode, email, password, nickname })
  }

  return (
    <main className="login-shell">
      <form className="login-card" onSubmit={submit}>
        <div className="logo-bolt">⚡</div>
        <h1 className="logo-title">Vítej v NEXUS</h1>
        <p className="muted">{mode === 'register' ? 'Vytvoř si vlastní účet' : 'Přihlas se ke svému účtu'}</p>

        {mode === 'register' && (
          <input
            value={nickname}
            onChange={(event) => setNickname(event.target.value)}
            placeholder="Přezdívka (2–20 znaků)"
            maxLength={20}
            autoComplete="nickname"
            aria-label="Přezdívka"
          />
        )}

        <input
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="E-mail"
          autoComplete="email"
          aria-label="E-mail"
          required
        />

        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Heslo (min. 6 znaků)"
          autoComplete={mode === 'register' ? 'new-password' : 'current-password'}
          aria-label="Heslo"
          minLength={6}
          required
        />

        {error && <p className="error-text">{error}</p>}

        <button className="primary-button" type="submit" disabled={!valid || busy}>
          {busy ? 'Pracuji…' : mode === 'register' ? 'Vytvořit účet →' : 'Přihlásit se →'}
        </button>

        <p className="login-note">
          {mode === 'register' ? 'Už máš účet?' : 'Ještě nemáš účet?'}{' '}
          <button className="text-button" type="button" onClick={() => setMode(mode === 'register' ? 'login' : 'register')}>
            {mode === 'register' ? 'Přihlásit se' : 'Vytvořit účet'}
          </button>
        </p>
      </form>
    </main>
  )
}

import { useState } from 'react'

export default function Login({ onSubmit, busy, error }) {
  const [mode, setMode] = useState('login')
  const [nickname, setNickname] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const validEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())
  const valid = validEmail && password.length >= 6 &&
    (mode === 'login' || nickname.trim().length >= 2)

  const submit = (event) => {
    event.preventDefault()
    if (!valid || busy) return
    onSubmit({
      mode,
      nickname: nickname.trim(),
      email: email.trim(),
      password,
    })
  }

  return (
    <main className="login-shell">
      <form className="login-card" onSubmit={submit}>
        <div className="logo-bolt">⚡</div>
        <h1 className="logo-title">Vítej v NEXUS</h1>
        <p className="muted">{mode === 'login' ? 'Přihlas se ke svému účtu' : 'Vytvoř si nový účet'}</p>

        {mode === 'register' && (
          <input
            value={nickname}
            onChange={(event) => setNickname(event.target.value)}
            placeholder="Přezdívka"
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
        />

        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Heslo (min. 6 znaků)"
          autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
          aria-label="Heslo"
        />

        {error && <p className="error-text">{error}</p>}

        <button className="primary-button" type="submit" disabled={!valid || busy}>
          {busy ? 'Pracuji…' : mode === 'login' ? 'Přihlásit se →' : 'Vytvořit účet →'}
        </button>

        <button
          className="ghost-button"
          type="button"
          onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
          disabled={busy}
        >
          {mode === 'login' ? 'Nemáš účet? Zaregistrovat se' : 'Už máš účet? Přihlásit se'}
        </button>
      </form>
    </main>
  )
}

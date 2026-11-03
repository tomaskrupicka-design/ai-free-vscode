import { useState } from 'react'

export default function Login({ onAuthenticate, busy, error }) {
  const [nickname, setNickname] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const cleanNickname = nickname.trim()
  const cleanEmail = email.trim()
  const valid = cleanNickname.length >= 2
    && cleanNickname.length <= 20
    && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cleanEmail)
    && password.length >= 6
    && password.length <= 128

  const submit = (event) => {
    event.preventDefault()
    if (valid && !busy) {
      onAuthenticate({
        nickname: cleanNickname,
        accessCode: { email: cleanEmail, password },
      })
    }
  }

  return (
    <main className="login-shell">
      <form className="login-card" onSubmit={submit}>
        <div className="logo-bolt">⚡</div>
        <h1 className="logo-title">Vítej v NEXTER</h1>
        <p className="muted">Přihlášení k osobnímu účtu</p>

        <input
          value={nickname}
          onChange={(event) => setNickname(event.target.value)}
          placeholder="Tvoje přezdívka"
          maxLength={20}
          autoComplete="nickname"
          aria-label="Přezdívka"
          required
        />

        <input
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="E-mail účtu"
          autoComplete="username"
          aria-label="E-mail"
          required
        />

        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Heslo"
          autoComplete="current-password"
          aria-label="Heslo"
          minLength={6}
          maxLength={128}
          required
        />

        {error && <p className="error-text">{error}</p>}

        <button className="primary-button" type="submit" disabled={!valid || busy}>
          {busy ? 'Přihlašuji…' : 'Přihlásit se do NEXTER →'}
        </button>

        <p className="login-note">Účet musí být předem vytvořený správcem.</p>
      </form>
    </main>
  )
}

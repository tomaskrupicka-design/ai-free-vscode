import { useState } from 'react'

export default function Login({ onLogin, busy, error }) {
  const [nick, setNick] = useState('')
  const clean = nick.trim()
  const valid = clean.length >= 2 && clean.length <= 20

  const submit = (event) => {
    event?.preventDefault()
    if (valid && !busy) onLogin(clean)
  }

  return (
    <main className="login-shell">
      <form className="login-card" onSubmit={submit}>
        <div className="logo-bolt">⚡</div>
        <h1 className="logo-title">NEXUS</h1>
        <p className="muted">Zadej přezdívku pro vstup</p>

        <input
          value={nick}
          onChange={(event) => setNick(event.target.value)}
          placeholder="Přezdívka..."
          maxLength={20}
          autoFocus
          aria-label="Přezdívka"
        />

        {error && <p className="error-text">{error}</p>}

        <button className="primary-button" type="submit" disabled={!valid || busy}>
          {busy ? 'Přihlašuji…' : 'Vstoupit →'}
        </button>

        <p className="login-note">Účet je chráněný anonymním Firebase UID. Přezdívka je jen veřejné jméno.</p>
      </form>
    </main>
  )
}

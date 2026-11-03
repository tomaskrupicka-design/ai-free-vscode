import { useState } from 'react'

export default function Login({ onContinue, busy, error }) {
  const [nick, setNick] = useState('')
  const clean = nick.trim()
  const valid = clean.length >= 2 && clean.length <= 20

  const submit = (event) => {
    event?.preventDefault()
    if (valid && !busy) onContinue(clean)
  }

  return (
    <main className="login-shell">
      <form className="login-card" onSubmit={submit}>
        <div className="logo-bolt">⚡</div>
        <h1 className="logo-title">Vítej v NEXUS</h1>
        <p className="muted">Vytvoř si přezdívku a vstup jako host</p>

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
          {busy ? 'Připravuji vstup…' : 'Pokračovat jako host →'}
        </button>

        <p className="login-note">Bez e-mailu, hesla a klasické registrace. NEXUS vytvoří anonymní technické ID, aby mohl bezpečně fungovat chat. Přezdívka je tvoje veřejné jméno.</p>
      </form>
    </main>
  )
}

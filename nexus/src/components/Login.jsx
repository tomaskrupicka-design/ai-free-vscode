import { useState } from 'react'

export default function Login({ onAuthenticate, busy, error }) {
  const [nickname, setNickname] = useState('')
  const [accessCode, setAccessCode] = useState('')

  const cleanNickname = nickname.trim()
  const cleanCode = accessCode.trim()
  const valid = cleanNickname.length >= 2
    && cleanNickname.length <= 20
    && cleanCode.length >= 8
    && cleanCode.length <= 128

  const submit = (event) => {
    event.preventDefault()
    if (valid && !busy) onAuthenticate({ nickname: cleanNickname, accessCode: cleanCode })
  }

  return (
    <main className="login-shell">
      <form className="login-card" onSubmit={submit}>
        <div className="logo-bolt">⚡</div>
        <h1 className="logo-title">Vítej v NEXTER</h1>
        <p className="muted">Vstup pomocí pozvánky</p>

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
          type="password"
          value={accessCode}
          onChange={(event) => setAccessCode(event.target.value)}
          placeholder="Osobní přístupový kód"
          autoComplete="one-time-code"
          aria-label="Přístupový kód"
          minLength={8}
          maxLength={128}
          required
        />

        {error && <p className="error-text">{error}</p>}

        <button className="primary-button" type="submit" disabled={!valid || busy}>
          {busy ? 'Ověřuji přístup…' : 'Vstoupit do NEXTER →'}
        </button>

        <p className="login-note">Přístup je možný pouze s platným pozvánkovým kódem.</p>
      </form>
    </main>
  )
}

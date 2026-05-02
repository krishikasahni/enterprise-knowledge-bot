import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { login, loading } = useAuth()
  const navigate = useNavigate()

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await login(username, password)
      navigate('/')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <div style={styles.logo}>
          <span style={styles.logoIcon}>⬡</span>
          <span style={styles.logoText}>KnowledgeBot</span>
        </div>

        <h1 style={styles.title}>Sign in</h1>
        <p style={styles.subtitle}>Access your enterprise knowledge base</p>

        {error && <div style={styles.error}>{error}</div>}

        <form onSubmit={submit} style={styles.form}>
          <label style={styles.label}>
            Username
            <input
              style={styles.input}
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="admin"
              autoComplete="username"
              required
            />
          </label>
          <label style={styles.label}>
            Password
            <input
              style={styles.input}
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              autoComplete="current-password"
              required
            />
          </label>
          <button style={styles.btn} type="submit" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign in →'}
          </button>
        </form>

        <p style={styles.hint}>
          Demo: <code style={styles.code}>admin / admin123</code> or <code style={styles.code}>user / user123</code>
        </p>
      </div>

      <div style={styles.bg} aria-hidden="true">
        {[...Array(6)].map((_, i) => (
          <div key={i} style={{ ...styles.orb, ...orbPos[i] }} />
        ))}
      </div>
    </div>
  )
}

const orbPos = [
  { top: '10%', left: '15%', width: 320, height: 320, background: 'radial-gradient(circle, rgba(124,109,250,0.15) 0%, transparent 70%)' },
  { top: '60%', right: '10%', width: 260, height: 260, background: 'radial-gradient(circle, rgba(79,209,197,0.1) 0%, transparent 70%)' },
  { bottom: '5%', left: '40%', width: 200, height: 200, background: 'radial-gradient(circle, rgba(124,109,250,0.08) 0%, transparent 70%)' },
  { top: '30%', right: '30%', width: 150, height: 150, background: 'radial-gradient(circle, rgba(79,209,197,0.07) 0%, transparent 70%)' },
  { top: '5%', right: '5%', width: 180, height: 180, background: 'radial-gradient(circle, rgba(124,109,250,0.1) 0%, transparent 70%)' },
  { bottom: '20%', left: '5%', width: 240, height: 240, background: 'radial-gradient(circle, rgba(79,209,197,0.08) 0%, transparent 70%)' },
]

const styles = {
  page: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    position: 'relative',
    overflow: 'hidden',
    background: 'var(--bg)',
  },
  bg: {
    position: 'fixed', inset: 0, pointerEvents: 'none', zIndex: 0,
  },
  orb: {
    position: 'absolute', borderRadius: '50%', pointerEvents: 'none',
  },
  card: {
    position: 'relative', zIndex: 1,
    background: 'var(--surface)',
    border: '1px solid var(--border-bright)',
    borderRadius: 20,
    padding: '48px 40px',
    width: '100%', maxWidth: 420,
    animation: 'fadeUp 0.5s ease',
  },
  logo: {
    display: 'flex', alignItems: 'center', gap: 10, marginBottom: 32,
  },
  logoIcon: {
    fontSize: 28, color: 'var(--accent)',
  },
  logoText: {
    fontFamily: 'var(--font-display)', fontSize: 20, fontWeight: 700, color: 'var(--text)',
  },
  title: {
    fontFamily: 'var(--font-display)', fontSize: 28, fontWeight: 700, color: 'var(--text)', marginBottom: 6,
  },
  subtitle: {
    color: 'var(--text-muted)', fontSize: 14, marginBottom: 28,
  },
  error: {
    background: 'rgba(248,113,113,0.1)',
    border: '1px solid rgba(248,113,113,0.3)',
    color: 'var(--danger)',
    borderRadius: 'var(--radius-sm)',
    padding: '10px 14px',
    fontSize: 14,
    marginBottom: 20,
  },
  form: { display: 'flex', flexDirection: 'column', gap: 18 },
  label: {
    display: 'flex', flexDirection: 'column', gap: 8,
    fontSize: 13, fontWeight: 500, color: 'var(--text-muted)', letterSpacing: '0.04em',
  },
  input: {
    background: 'var(--surface2)', border: '1px solid var(--border-bright)',
    borderRadius: 'var(--radius-sm)', padding: '11px 14px',
    color: 'var(--text)', fontSize: 15, outline: 'none',
    transition: 'border-color 0.2s',
    fontFamily: 'var(--font-body)',
  },
  btn: {
    marginTop: 8,
    background: 'var(--accent)', color: '#fff',
    border: 'none', borderRadius: 'var(--radius-sm)',
    padding: '13px 20px', fontSize: 15, fontWeight: 600,
    fontFamily: 'var(--font-display)',
    transition: 'opacity 0.2s, transform 0.1s',
    cursor: 'pointer',
  },
  hint: {
    marginTop: 24, textAlign: 'center', fontSize: 12, color: 'var(--text-dim)',
  },
  code: {
    fontFamily: 'var(--font-mono)', fontSize: 12,
    background: 'var(--surface2)', padding: '2px 6px', borderRadius: 4,
    color: 'var(--accent2)',
  },
}

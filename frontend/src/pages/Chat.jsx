import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { api } from '../utils/api'
import MessageBubble from '../components/MessageBubble'
import UploadPanel from '../components/UploadPanel'

const SUGGESTIONS = [
  'Summarize the key policies in the uploaded documents',
  'What information do we have about our products?',
  'Find all mentions of compliance requirements',
  'What are the main topics in the knowledge base?',
]

export default function Chat() {
  const { user, logout, isAdmin } = useAuth()
  const navigate = useNavigate()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [showUpload, setShowUpload] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const endRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const doLogout = () => { logout(); navigate('/login') }

  const send = async (question) => {
    if (!question.trim() || busy) return
    const q = question.trim()
    setInput('')
    setBusy(true)

    setMessages(prev => [
      ...prev,
      { id: Date.now(), role: 'user', content: q },
      { id: Date.now() + 1, role: 'bot', content: '', loading: true },
    ])

    try {
      const res = await api.query(q)
      setMessages(prev => prev.map((m, i) =>
        i === prev.length - 1
          ? { ...m, content: res.answer, sources: res.sources, loading: false }
          : m
      ))
    } catch (e) {
      setMessages(prev => prev.map((m, i) =>
        i === prev.length - 1
          ? { ...m, content: `Error: ${e.message}`, loading: false }
          : m
      ))
    } finally {
      setBusy(false)
      inputRef.current?.focus()
    }
  }

  const handleSubmit = (e) => { e.preventDefault(); send(input) }
  const handleSuggestion = (s) => send(s)

  return (
    <div style={styles.layout}>
      {/* Sidebar */}
      <aside style={{ ...styles.sidebar, ...(sidebarOpen ? {} : styles.sidebarClosed) }}>
        <div style={styles.sidebarTop}>
          <div style={styles.logo}>
            <span style={styles.logoIcon}>⬡</span>
            {sidebarOpen && <span style={styles.logoText}>KnowledgeBot</span>}
          </div>

          {sidebarOpen && (
            <>
              <div style={styles.userCard}>
                <div style={styles.userAvatar}>{user?.username[0]?.toUpperCase()}</div>
                <div>
                  <div style={styles.userName}>{user?.username}</div>
                  <div style={styles.userRole}>{user?.role}</div>
                </div>
              </div>

              {isAdmin && (
                <button style={styles.ingestBtn} onClick={() => setShowUpload(v => !v)}>
                  {showUpload ? '✕ Close upload' : '⬆ Ingest documents'}
                </button>
              )}

              {showUpload && isAdmin && (
                <div style={styles.uploadWrapper}>
                  <UploadPanel onSuccess={() => {}} />
                </div>
              )}

              <div style={styles.suggestions}>
                <p style={styles.suggestLabel}>Try asking</p>
                {SUGGESTIONS.map((s, i) => (
                  <button key={i} style={styles.suggestBtn} onClick={() => handleSuggestion(s)}>
                    {s}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>

        <div style={styles.sidebarBottom}>
          <button style={styles.logoutBtn} onClick={doLogout}>
            {sidebarOpen ? '← Sign out' : '←'}
          </button>
        </div>
      </aside>

      {/* Main */}
      <main style={styles.main}>
        <header style={styles.header}>
          <button style={styles.toggleBtn} onClick={() => setSidebarOpen(v => !v)}>
            {sidebarOpen ? '◀' : '▶'}
          </button>
          <h1 style={styles.headerTitle}>Enterprise Knowledge Base</h1>
          <div style={styles.headerStatus}>
            <span style={styles.dot} />
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Connected</span>
          </div>
        </header>

        <div style={styles.messages}>
          {messages.length === 0 && (
            <div style={styles.empty}>
              <div style={styles.emptyIcon}>⬡</div>
              <h2 style={styles.emptyTitle}>Ask your knowledge base</h2>
              <p style={styles.emptyText}>
                I can answer questions from your uploaded PDFs, Word docs, wikis, and databases.
              </p>
            </div>
          )}

          {messages.map(msg => (
            <MessageBubble key={msg.id} msg={msg} />
          ))}
          <div ref={endRef} />
        </div>

        <form style={styles.inputRow} onSubmit={handleSubmit}>
          <input
            ref={inputRef}
            style={styles.chatInput}
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Ask anything from your knowledge base…"
            disabled={busy}
          />
          <button style={styles.sendBtn} type="submit" disabled={busy || !input.trim()}>
            {busy ? <span style={styles.spinner} /> : '↑'}
          </button>
        </form>
      </main>
    </div>
  )
}

const styles = {
  layout: { display: 'flex', height: '100vh', overflow: 'hidden', background: 'var(--bg)' },

  sidebar: {
    width: 280, flexShrink: 0, background: 'var(--surface)',
    borderRight: '1px solid var(--border)', display: 'flex',
    flexDirection: 'column', transition: 'width 0.2s',
    overflow: 'hidden',
  },
  sidebarClosed: { width: 56 },

  sidebarTop: { flex: 1, padding: 16, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 16 },
  sidebarBottom: { padding: 16, borderTop: '1px solid var(--border)' },

  logo: { display: 'flex', alignItems: 'center', gap: 10, paddingBottom: 8 },
  logoIcon: { fontSize: 22, color: 'var(--accent)', flexShrink: 0 },
  logoText: { fontFamily: 'var(--font-display)', fontSize: 16, fontWeight: 700 },

  userCard: {
    display: 'flex', alignItems: 'center', gap: 10,
    background: 'var(--surface2)', borderRadius: 10, padding: '10px 12px',
  },
  userAvatar: {
    width: 32, height: 32, borderRadius: '50%',
    background: 'linear-gradient(135deg, var(--accent), var(--accent2))',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontSize: 14, fontWeight: 700, color: '#fff', flexShrink: 0,
  },
  userName: { fontSize: 13, fontWeight: 600, color: 'var(--text)' },
  userRole: { fontSize: 11, color: 'var(--text-muted)', textTransform: 'capitalize' },

  ingestBtn: {
    width: '100%', background: 'rgba(124,109,250,0.1)',
    border: '1px solid rgba(124,109,250,0.3)', borderRadius: 8,
    color: 'var(--accent)', padding: '9px 12px', fontSize: 13, fontWeight: 500,
  },
  uploadWrapper: { maxHeight: 400, overflowY: 'auto' },

  suggestions: { display: 'flex', flexDirection: 'column', gap: 6 },
  suggestLabel: { fontSize: 11, color: 'var(--text-dim)', fontWeight: 500, letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 4 },
  suggestBtn: {
    textAlign: 'left', background: 'transparent',
    border: '1px solid var(--border)', borderRadius: 8,
    color: 'var(--text-muted)', padding: '8px 10px', fontSize: 12,
    transition: 'all 0.15s', lineHeight: 1.4,
  },

  logoutBtn: {
    width: '100%', background: 'transparent',
    border: '1px solid var(--border)', borderRadius: 8,
    color: 'var(--text-muted)', padding: '9px 12px', fontSize: 13,
  },

  main: { flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' },

  header: {
    display: 'flex', alignItems: 'center', gap: 12,
    padding: '14px 20px', borderBottom: '1px solid var(--border)',
    background: 'var(--surface)', flexShrink: 0,
  },
  toggleBtn: {
    background: 'transparent', border: 'none', color: 'var(--text-muted)',
    fontSize: 12, padding: 4,
  },
  headerTitle: {
    fontFamily: 'var(--font-display)', fontSize: 16, fontWeight: 700, flex: 1,
  },
  headerStatus: { display: 'flex', alignItems: 'center', gap: 6 },
  dot: {
    width: 7, height: 7, borderRadius: '50%', background: 'var(--success)',
    boxShadow: '0 0 6px var(--success)',
  },

  messages: {
    flex: 1, overflowY: 'auto', padding: '24px 28px',
    display: 'flex', flexDirection: 'column', gap: 20,
  },

  empty: { margin: 'auto', textAlign: 'center', maxWidth: 380 },
  emptyIcon: {
    fontSize: 48, color: 'var(--accent)', marginBottom: 16,
    filter: 'drop-shadow(0 0 20px var(--accent-glow))',
  },
  emptyTitle: {
    fontFamily: 'var(--font-display)', fontSize: 22, fontWeight: 700, marginBottom: 10,
  },
  emptyText: { color: 'var(--text-muted)', fontSize: 14, lineHeight: 1.6 },

  inputRow: {
    display: 'flex', gap: 10, padding: '16px 20px',
    borderTop: '1px solid var(--border)', background: 'var(--surface)',
    flexShrink: 0,
  },
  chatInput: {
    flex: 1, background: 'var(--surface2)',
    border: '1px solid var(--border-bright)',
    borderRadius: 12, padding: '12px 16px',
    color: 'var(--text)', fontSize: 14, outline: 'none',
    fontFamily: 'var(--font-body)',
  },
  sendBtn: {
    width: 44, height: 44, borderRadius: 12, flexShrink: 0,
    background: 'var(--accent)', color: '#fff',
    border: 'none', fontSize: 18, fontWeight: 700,
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    transition: 'opacity 0.15s',
  },
  spinner: {
    width: 16, height: 16, border: '2px solid rgba(255,255,255,0.3)',
    borderTop: '2px solid #fff', borderRadius: '50%',
    display: 'inline-block',
    animation: 'spin 0.7s linear infinite',
  },
}

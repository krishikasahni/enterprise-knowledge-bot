import ReactMarkdown from 'react-markdown'

export default function MessageBubble({ msg }) {
  const isUser = msg.role === 'user'

  return (
    <div style={{ ...styles.wrapper, justifyContent: isUser ? 'flex-end' : 'flex-start' }}>
      {!isUser && <div style={styles.avatar}>⬡</div>}

      <div style={{ maxWidth: '72%' }}>
        <div style={{ ...styles.bubble, ...(isUser ? styles.userBubble : styles.botBubble) }}>
          {isUser ? (
            <p style={styles.userText}>{msg.content}</p>
          ) : (
            <div style={styles.markdown}>
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {msg.sources && msg.sources.length > 0 && (
          <div style={styles.sources}>
            <span style={styles.sourcesLabel}>📎 Sources</span>
            {msg.sources.map((s, i) => (
              <div key={i} style={styles.sourceChip} title={s.preview}>
                <span style={styles.sourceScore}>{Math.round(s.score * 100)}%</span>
                <span style={styles.sourceName} title={s.source}>
                  {s.source.length > 40 ? '…' + s.source.slice(-38) : s.source}
                </span>
              </div>
            ))}
          </div>
        )}

        {msg.loading && (
          <div style={styles.typing}>
            <span style={styles.dot} />
            <span style={{ ...styles.dot, animationDelay: '0.2s' }} />
            <span style={{ ...styles.dot, animationDelay: '0.4s' }} />
          </div>
        )}
      </div>
    </div>
  )
}

const styles = {
  wrapper: {
    display: 'flex', alignItems: 'flex-end', gap: 10,
    animation: 'fadeUp 0.3s ease',
  },
  avatar: {
    width: 32, height: 32, borderRadius: '50%',
    background: 'linear-gradient(135deg, var(--accent), var(--accent2))',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontSize: 14, color: '#fff', flexShrink: 0,
  },
  bubble: {
    borderRadius: 16, padding: '12px 16px', lineHeight: 1.65,
  },
  userBubble: {
    background: 'var(--accent)', borderBottomRightRadius: 4,
  },
  botBubble: {
    background: 'var(--surface2)', border: '1px solid var(--border)',
    borderBottomLeftRadius: 4,
  },
  userText: { color: '#fff', fontSize: 14 },
  markdown: {
    color: 'var(--text)', fontSize: 14,
  },
  sources: {
    marginTop: 8, display: 'flex', flexWrap: 'wrap', gap: 6, alignItems: 'center',
  },
  sourcesLabel: {
    fontSize: 11, color: 'var(--text-dim)', fontWeight: 500, letterSpacing: '0.04em',
  },
  sourceChip: {
    display: 'flex', alignItems: 'center', gap: 6,
    background: 'var(--surface)', border: '1px solid var(--border)',
    borderRadius: 99, padding: '3px 10px',
    fontSize: 11, color: 'var(--text-muted)',
    cursor: 'default',
  },
  sourceScore: {
    color: 'var(--accent2)', fontWeight: 600, fontFamily: 'var(--font-mono)',
  },
  sourceName: {
    overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 220,
  },
  typing: {
    display: 'flex', gap: 5, marginTop: 6, paddingLeft: 4,
  },
  dot: {
    width: 6, height: 6, borderRadius: '50%',
    background: 'var(--text-muted)',
    animation: 'pulse 1.2s ease-in-out infinite',
    display: 'inline-block',
  },
}

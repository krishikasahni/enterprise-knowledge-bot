import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { api } from '../utils/api'

const TABS = ['File', 'URL', 'SQL']

export default function UploadPanel({ onSuccess }) {
  const [tab, setTab] = useState('File')
  const [url, setUrl] = useState('')
  const [sqlConn, setSqlConn] = useState('')
  const [sqlQuery, setSqlQuery] = useState('')
  const [sqlLabel, setSqlLabel] = useState('')
  const [status, setStatus] = useState(null) // { type: 'ok'|'err', msg }
  const [busy, setBusy] = useState(false)

  const reset = () => setStatus(null)

  const onDrop = useCallback(async (files) => {
    if (!files[0]) return
    setBusy(true); reset()
    try {
      const res = await api.uploadFile(files[0])
      setStatus({ type: 'ok', msg: `✓ ${res.message} — ${res.chunks} chunks stored` })
      onSuccess?.()
    } catch (e) {
      setStatus({ type: 'err', msg: e.message })
    } finally { setBusy(false) }
  }, [onSuccess])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { 'application/pdf': ['.pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'] },
    multiple: false, disabled: busy,
  })

  const submitUrl = async (e) => {
    e.preventDefault(); setBusy(true); reset()
    try {
      const res = await api.uploadUrl(url)
      setStatus({ type: 'ok', msg: `✓ ${res.message} — ${res.chunks} chunks` })
      setUrl('')
      onSuccess?.()
    } catch (e) { setStatus({ type: 'err', msg: e.message }) }
    finally { setBusy(false) }
  }

  const submitSql = async (e) => {
    e.preventDefault(); setBusy(true); reset()
    try {
      const res = await api.uploadSql(sqlConn, sqlQuery, sqlLabel)
      setStatus({ type: 'ok', msg: `✓ ${res.message} — ${res.chunks} chunks` })
      onSuccess?.()
    } catch (e) { setStatus({ type: 'err', msg: e.message }) }
    finally { setBusy(false) }
  }

  return (
    <div style={styles.panel}>
      <h3 style={styles.heading}>Ingest documents</h3>

      <div style={styles.tabs}>
        {TABS.map(t => (
          <button key={t} style={{ ...styles.tab, ...(tab === t ? styles.tabActive : {}) }}
            onClick={() => { setTab(t); reset() }}>
            {t}
          </button>
        ))}
      </div>

      {status && (
        <div style={{ ...styles.toast, ...(status.type === 'ok' ? styles.toastOk : styles.toastErr) }}>
          {status.msg}
        </div>
      )}

      {tab === 'File' && (
        <div {...getRootProps()} style={{ ...styles.dropzone, ...(isDragActive ? styles.dropzoneActive : {}) }}>
          <input {...getInputProps()} />
          <span style={styles.dropIcon}>⬡</span>
          <p style={styles.dropText}>
            {busy ? 'Uploading…' : isDragActive ? 'Drop it!' : 'Drop PDF or DOCX here'}
          </p>
          <p style={styles.dropHint}>or click to browse</p>
        </div>
      )}

      {tab === 'URL' && (
        <form onSubmit={submitUrl} style={styles.form}>
          <input style={styles.input} placeholder="https://wiki.company.com/page"
            value={url} onChange={e => setUrl(e.target.value)} required />
          <button style={styles.btn} type="submit" disabled={busy}>
            {busy ? 'Fetching…' : 'Ingest URL'}
          </button>
        </form>
      )}

      {tab === 'SQL' && (
        <form onSubmit={submitSql} style={styles.form}>
          <input style={styles.input} placeholder="sqlite:///path/to/db.sqlite"
            value={sqlConn} onChange={e => setSqlConn(e.target.value)} required />
          <textarea style={{ ...styles.input, resize: 'vertical', minHeight: 72 }}
            placeholder="SELECT id, name, description FROM products"
            value={sqlQuery} onChange={e => setSqlQuery(e.target.value)} required />
          <input style={styles.input} placeholder="Label (e.g. Products DB)"
            value={sqlLabel} onChange={e => setSqlLabel(e.target.value)} required />
          <button style={styles.btn} type="submit" disabled={busy}>
            {busy ? 'Ingesting…' : 'Ingest SQL'}
          </button>
        </form>
      )}
    </div>
  )
}

const styles = {
  panel: {
    background: 'var(--surface)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius)', padding: 20,
  },
  heading: {
    fontFamily: 'var(--font-display)', fontSize: 15, fontWeight: 600,
    color: 'var(--text)', marginBottom: 14,
  },
  tabs: { display: 'flex', gap: 4, marginBottom: 16 },
  tab: {
    flex: 1, padding: '7px 12px', borderRadius: 8, border: '1px solid var(--border)',
    background: 'transparent', color: 'var(--text-muted)', fontSize: 13, fontWeight: 500,
    transition: 'all 0.15s',
  },
  tabActive: {
    background: 'var(--accent)', borderColor: 'var(--accent)', color: '#fff',
  },
  toast: {
    borderRadius: 8, padding: '9px 12px', fontSize: 12, marginBottom: 12,
  },
  toastOk: {
    background: 'rgba(52,211,153,0.1)', border: '1px solid rgba(52,211,153,0.3)', color: 'var(--success)',
  },
  toastErr: {
    background: 'rgba(248,113,113,0.1)', border: '1px solid rgba(248,113,113,0.3)', color: 'var(--danger)',
  },
  dropzone: {
    border: '2px dashed var(--border-bright)', borderRadius: 'var(--radius)',
    padding: '32px 20px', textAlign: 'center', cursor: 'pointer',
    transition: 'border-color 0.2s, background 0.2s',
  },
  dropzoneActive: {
    borderColor: 'var(--accent)', background: 'rgba(124,109,250,0.06)',
  },
  dropIcon: { fontSize: 28, color: 'var(--accent)', display: 'block', marginBottom: 10 },
  dropText: { color: 'var(--text)', fontSize: 14, marginBottom: 4 },
  dropHint: { color: 'var(--text-dim)', fontSize: 12 },
  form: { display: 'flex', flexDirection: 'column', gap: 10 },
  input: {
    background: 'var(--surface2)', border: '1px solid var(--border-bright)',
    borderRadius: 8, padding: '10px 12px', color: 'var(--text)', fontSize: 13,
    outline: 'none', fontFamily: 'var(--font-body)', width: '100%',
  },
  btn: {
    background: 'var(--accent)', color: '#fff', border: 'none',
    borderRadius: 8, padding: '10px 16px', fontSize: 13, fontWeight: 600,
    fontFamily: 'var(--font-display)', cursor: 'pointer',
  },
}

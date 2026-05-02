const BASE = import.meta.env.VITE_API_URL || ''

function getToken() {
  return localStorage.getItem('kb_token')
}

function authHeaders() {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(),
      ...(options.headers || {}),
    },
  })

  if (res.status === 401) {
    localStorage.removeItem('kb_token')
    localStorage.removeItem('kb_user')
    window.location.href = '/login'
    return
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail || 'Request failed')
  }

  return res.json()
}

export const api = {
  // Auth
  login: (username, password) => {
    const form = new URLSearchParams({ username, password })
    return fetch(`${BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form,
    }).then(async (res) => {
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Login failed')
      }
      return res.json()
    })
  },

  me: () => request('/auth/me'),

  // Query
  query: (question, topK = 5) =>
    request('/query', {
      method: 'POST',
      body: JSON.stringify({ question, stream: false, top_k: topK }),
    }),

  // Upload
  uploadFile: (file) => {
    const fd = new FormData()
    fd.append('file', file)
    return fetch(`${BASE}/upload/file`, {
      method: 'POST',
      headers: authHeaders(),
      body: fd,
    }).then(async (res) => {
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Upload failed')
      }
      return res.json()
    })
  },

  uploadUrl: (url) =>
    request('/upload/url', { method: 'POST', body: JSON.stringify({ url }) }),

  uploadSql: (connection_string, query, label) =>
    request('/upload/sql', {
      method: 'POST',
      body: JSON.stringify({ connection_string, query, label }),
    }),

  health: () => request('/health'),
}

import { createContext, useContext, useState, useEffect } from 'react'
import { api } from '../utils/api'

const AuthCtx = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('kb_user')) } catch { return null }
  })
  const [loading, setLoading] = useState(false)

  const login = async (username, password) => {
    setLoading(true)
    try {
      const data = await api.login(username, password)
      localStorage.setItem('kb_token', data.access_token)
      const u = { username: data.username, role: data.role }
      localStorage.setItem('kb_user', JSON.stringify(u))
      setUser(u)
      return u
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem('kb_token')
    localStorage.removeItem('kb_user')
    setUser(null)
  }

  return (
    <AuthCtx.Provider value={{ user, login, logout, loading, isAdmin: user?.role === 'admin' }}>
      {children}
    </AuthCtx.Provider>
  )
}

export const useAuth = () => useContext(AuthCtx)

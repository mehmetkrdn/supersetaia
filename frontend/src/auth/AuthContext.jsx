import { createContext, useContext, useEffect, useMemo, useState } from 'react'

const API_BASE = '/api'
const TOKEN_KEY = 'auth_token'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY) || '')
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  async function fetchMe(accessToken) {
    // DÜZELTME: URL için backtick (`) eklendi
    const res = await fetch(`${API_BASE}/v1/auth/me`, {
      method: 'GET',
      headers: {
        // DÜZELTME: Bearer token için backtick (`) eklendi
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
    })

    if (!res.ok) {
      throw new Error('Kullanıcı bilgisi alınamadı.')
    }

    return res.json()
  }

  async function login(username, password) {
    // DÜZELTME: URL için backtick (`) eklendi
    const res = await fetch(`${API_BASE}/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })

    const data = await res.json()

    if (!res.ok) {
      throw new Error(data.detail || 'Giriş başarısız.')
    }

    const accessToken = data.access_token
    localStorage.setItem(TOKEN_KEY, accessToken)
    setToken(accessToken)

    const me = await fetchMe(accessToken)
    setUser(me)

    return me
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY)
    setToken('')
    setUser(null)
  }

  useEffect(() => {
    let active = true

    async function restoreSession() {
      if (!token) {
        if (active) {
          setUser(null)
          setLoading(false)
        }
        return
      }

      try {
        const me = await fetchMe(token)
        if (active) {
          setUser(me)
        }
      } catch (err) {
        localStorage.removeItem(TOKEN_KEY)
        if (active) {
          setToken('')
          setUser(null)
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    restoreSession()

    return () => {
      active = false
    }
  }, [token])

  const value = useMemo(
    () => ({
      token,
      user,
      loading,
      isAuthenticated: Boolean(token && user),
      login,
      logout,
    }),
    [token, user, loading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return ctx
}
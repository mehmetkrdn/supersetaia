import React, { useEffect, useState } from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import './i18n'
import App from './App'
import AdminPanel from './AdminPanel'
import { AuthProvider } from './auth/AuthContext'

// Admin panelini koruyan ve yetki kontrolü yapan bileşen
function AdminPanelWrapper() {
  const [loading, setLoading] = useState(true)
  const [currentUser, setCurrentUser] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadMe() {
      const token = localStorage.getItem('access_token')

      if (!token) {
        setError('Giriş yapmadan admin paneline erişemezsiniz.')
        setLoading(false)
        return
      }

      try {
        const res = await fetch('/api/v1/auth/me', {
          headers: {
            Authorization: `Bearer ${token}`,
            Accept: 'application/json',
          },
        })

        const data = await res.json()

        if (!res.ok) {
          throw new Error(data.detail || 'Kullanıcı bilgisi alınamadı.')
        }

        // Sadece admin veya superadmin erişebilsin
        const isAdminRole =
          Array.isArray(data.role_codes) &&
          data.role_codes.some((r) => String(r).toLowerCase() === 'admin')

        const isAllowed = Boolean(data.is_superadmin) || isAdminRole

        if (!isAllowed) {
          throw new Error('Bu sayfaya erişim yetkiniz yok.')
        }

        setCurrentUser(data)
      } catch (err) {
        setError(err.message || 'Admin paneli açılamadı.')
      } finally {
        setLoading(false)
      }
    }

    loadMe()
  }, [])

  if (loading) {
    return <div style={{ padding: 24, textAlign: 'center' }}>Yükleniyor...</div>
  }

  if (error) {
    return (
      <div style={{ padding: 24, textAlign: 'center' }}>
        <h2 style={{ color: '#ff4d4f' }}>{error}</h2>
        <a href="/" style={{ color: '#1890ff', textDecoration: 'underline' }}>
          Ana sayfaya dön
        </a>
      </div>
    )
  }

  return (
    <AdminPanel
      currentUser={currentUser}
      onClose={() => (window.location.href = '/')}
    />
  )
}

// Render işlemi
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<App />} />
          <Route path="/admin" element={<AdminPanelWrapper />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>,
)
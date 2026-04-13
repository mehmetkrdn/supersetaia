import { useState } from 'react'
import { useAuth } from '../auth/AuthContext'

export default function LoginPage() {
  const { login } = useAuth()

  const [username, setUsername] = useState('manager_demo')
  const [password, setPassword] = useState('demo_manager_123')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(username.trim(), password)
    } catch (err) {
      setError(err.message || 'Giriş başarısız.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-brand">AI Superset Security Gateway</div>
        <h1 className="login-title">Giriş Yap</h1>
        <p className="login-subtitle">
          Sorgu asistanına erişmek için kullanıcı bilgilerinizi girin.
        </p>

        <form onSubmit={handleSubmit} className="login-form">
          <label className="login-label">
            Kullanıcı Adı
            <input
              className="input"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="manager_demo"
              disabled={loading}
            />
          </label>

          <label className="login-label">
            Şifre
            <input
              className="input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              disabled={loading}
            />
          </label>

          {error && <div className="login-error">{error}</div>}

          <button type="submit" className="btn login-btn" disabled={loading}>
            {loading ? 'Giriş yapılıyor…' : 'Giriş Yap'}
          </button>
        </form>

        <div className="login-help">
          Demo kullanıcı örneği: <strong>manager_demo</strong>
        </div>
      </div>
    </div>
  )
}
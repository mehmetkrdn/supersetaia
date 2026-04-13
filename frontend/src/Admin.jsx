import { useEffect, useState } from 'react'
import AdminPanel from './AdminPanel'

const API_BASE = '/api/v1/admin'

export default function Admin({ currentUser }) {
  const [showAdminPanel, setShowAdminPanel] = useState(false)
  
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const [createForm, setCreateForm] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
    is_active: true,
    is_superadmin: false,
  })

  const [roleForms, setRoleForms] = useState({})
  const [scopeForms, setScopeForms] = useState({})

  const canOpenAdmin =
    Boolean(currentUser?.is_superadmin) ||
    (Array.isArray(currentUser?.role_codes) &&
      currentUser.role_codes.some((r) => ['admin'].includes(String(r).toLowerCase())))

  async function loadUsers() {
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`${API_BASE}/users`)
      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || 'Kullanıcılar alınamadı.')
      }

      setUsers(data)

      const nextRoleForms = {}
      const nextScopeForms = {}

      data.forEach((user) => {
        nextRoleForms[user.id] = {
          role_code: user.role_assignments?.[0]?.role_code || '',
          company_id: user.role_assignments?.[0]?.company_id || '',
        }

        nextScopeForms[user.id] = {
          company_ids: (user.company_ids || []).join(','),
          country_ids: (user.country_ids || []).join(','),
          region_ids: (user.region_ids || []).join(','),
          branch_ids: (user.branch_ids || []).join(','),
          department_ids: (user.department_ids || []).join(','),
          team_ids: (user.team_ids || []).join(','),
          customer_ids: (user.customer_ids || []).join(','),
        }
      })

      setRoleForms(nextRoleForms)
      setScopeForms(nextScopeForms)
    } catch (err) {
      setError(err.message || 'Bir hata oluştu.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadUsers()
  }, [])

  function parseNumberList(value) {
    return String(value || '')
      .split(',')
      .map((x) => x.trim())
      .filter(Boolean)
      .map((x) => Number(x))
      .filter((x) => !Number.isNaN(x))
  }

  function parseStringList(value) {
    return String(value || '')
      .split(',')
      .map((x) => x.trim())
      .filter(Boolean)
  }

  async function handleCreateUser(e) {
    e.preventDefault()
    setMessage('')
    setError('')

    try {
      const res = await fetch(`${API_BASE}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(createForm),
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || data.message || 'Kullanıcı oluşturulamadı.')
      }

      setMessage('Kullanıcı oluşturuldu.')
      setCreateForm({
        username: '',
        email: '',
        full_name: '',
        password: '',
        is_active: true,
        is_superadmin: false,
      })

      loadUsers()
    } catch (err) {
      setError(err.message || 'Kullanıcı oluşturulamadı.')
    }
  }

  async function handleUpdateRoles(userId) {
    setMessage('')
    setError('')

    try {
      const form = roleForms[userId] || {}
      const roleCode = String(form.role_code || '').trim()
      const companyId = Number(form.company_id)

      const roles = roleCode && !Number.isNaN(companyId)
        ? [{ role_code: roleCode, company_id: companyId }]
        : []

      const res = await fetch(`${API_BASE}/users/${userId}/roles`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ roles }),
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || data.message || 'Rol güncellenemedi.')
      }

      setMessage(`Kullanıcı ${userId} için rol güncellendi.`)
      loadUsers()
    } catch (err) {
      setError(err.message || 'Rol güncellenemedi.')
    }
  }

  async function handleUpdateScopes(userId) {
    setMessage('')
    setError('')

    try {
      const form = scopeForms[userId] || {}

      const payload = {
        company_ids: parseNumberList(form.company_ids),
        country_ids: parseNumberList(form.country_ids),
        region_ids: parseNumberList(form.region_ids),
        branch_ids: parseNumberList(form.branch_ids),
        department_ids: parseNumberList(form.department_ids),
        team_ids: parseNumberList(form.team_ids),
        customer_ids: parseStringList(form.customer_ids),
      }

      const res = await fetch(`${API_BASE}/users/${userId}/scopes`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || data.message || 'Scope güncellenemedi.')
      }

      setMessage(`Kullanıcı ${userId} için scope güncellendi.`)
      loadUsers()
    } catch (err) {
      setError(err.message || 'Scope güncellenemedi.')
    }
  }

  if (showAdminPanel) {
    return (
      <AdminPanel
        currentUser={currentUser}
        onClose={() => setShowAdminPanel(false)}
      />
    )
  }

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h1 style={{ margin: 0 }}>Eski Admin Görünümü</h1>
        
        {canOpenAdmin && (
          <button
            type="button"
            className="btn"
            onClick={() => setShowAdminPanel(true)}
            style={{ padding: '8px 16px', cursor: 'pointer' }}
          >
            Admin Panelini Aç
          </button>
        )}
      </div>

      {message && (
        <div style={{ marginBottom: 16, color: 'green' }}>
          {message}
        </div>
      )}

      {error && (
        <div style={{ marginBottom: 16, color: 'crimson' }}>
          {error}
        </div>
      )}

      <section style={{ marginBottom: 32, border: '1px solid #ddd', padding: 16, borderRadius: 8 }}>
        <h2>Yeni Kullanıcı Ekle</h2>
        <form onSubmit={handleCreateUser} style={{ display: 'grid', gap: 8, maxWidth: 480 }}>
          <input
            placeholder="Username"
            value={createForm.username}
            onChange={(e) => setCreateForm({ ...createForm, username: e.target.value })}
          />
          <input
            placeholder="Email"
            value={createForm.email}
            onChange={(e) => setCreateForm({ ...createForm, email: e.target.value })}
          />
          <input
            placeholder="Full Name"
            value={createForm.full_name}
            onChange={(e) => setCreateForm({ ...createForm, full_name: e.target.value })}
          />
          <input
            placeholder="Password"
            type="password"
            value={createForm.password}
            onChange={(e) => setCreateForm({ ...createForm, password: e.target.value })}
          />

          <label>
            <input
              type="checkbox"
              checked={createForm.is_active}
              onChange={(e) => setCreateForm({ ...createForm, is_active: e.target.checked })}
            />
            Aktif
          </label>

          <label>
            <input
              type="checkbox"
              checked={createForm.is_superadmin}
              onChange={(e) => setCreateForm({ ...createForm, is_superadmin: e.target.checked })}
            />
            Superadmin
          </label>

          <button type="submit">Kullanıcı Ekle</button>
        </form>
      </section>

      <section>
        <h2>Kullanıcılar</h2>

        {loading ? (
          <p>Yükleniyor...</p>
        ) : (
          <div style={{ display: 'grid', gap: 16 }}>
            {users.map((user) => (
              <div
                key={user.id}
                style={{
                  border: '1px solid #ddd',
                  padding: 16,
                  borderRadius: 8,
                  background: '#fff',
                }}
              >
                <h3 style={{ marginTop: 0 }}>
                  {user.username} #{user.id}
                </h3>

                <p><strong>Email:</strong> {user.email || '-'}</p>
                <p><strong>Ad Soyad:</strong> {user.full_name || '-'}</p>
                <p><strong>Aktif:</strong> {user.is_active ? 'Evet' : 'Hayır'}</p>
                <p><strong>Superadmin:</strong> {user.is_superadmin ? 'Evet' : 'Hayır'}</p>

                <p>
                  <strong>Roller:</strong>{' '}
                  {user.role_assignments?.length
                    ? user.role_assignments.map((r) => `${r.role_code} (company ${r.company_id})`).join(', ')
                    : '-'}
                </p>

                <p><strong>Company:</strong> {(user.company_ids || []).join(', ') || '-'}</p>
                <p><strong>Country:</strong> {(user.country_ids || []).join(', ') || '-'}</p>
                <p><strong>Region:</strong> {(user.region_ids || []).join(', ') || '-'}</p>
                <p><strong>Branch:</strong> {(user.branch_ids || []).join(', ') || '-'}</p>
                <p><strong>Department:</strong> {(user.department_ids || []).join(', ') || '-'}</p>
                <p><strong>Team:</strong> {(user.team_ids || []).join(', ') || '-'}</p>
                <p><strong>Customer:</strong> {(user.customer_ids || []).join(', ') || '-'}</p>

                <div style={{ marginTop: 16, padding: 12, background: '#f8f8f8', borderRadius: 8 }}>
                  <h4>Rol Güncelle</h4>
                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    <input
                      placeholder="role_code"
                      value={roleForms[user.id]?.role_code || ''}
                      onChange={(e) =>
                        setRoleForms({
                          ...roleForms,
                          [user.id]: {
                            ...roleForms[user.id],
                            role_code: e.target.value,
                          },
                        })
                      }
                    />
                    <input
                      placeholder="company_id"
                      value={roleForms[user.id]?.company_id || ''}
                      onChange={(e) =>
                        setRoleForms({
                          ...roleForms,
                          [user.id]: {
                            ...roleForms[user.id],
                            company_id: e.target.value,
                          },
                        })
                      }
                    />
                    <button type="button" onClick={() => handleUpdateRoles(user.id)}>
                      Rol Kaydet
                    </button>
                  </div>
                </div>

                <div style={{ marginTop: 16, padding: 12, background: '#f8f8f8', borderRadius: 8 }}>
                  <h4>Scope Güncelle</h4>
                  <div style={{ display: 'grid', gap: 8 }}>
                    <input
                      placeholder="company_ids (örn: 1,2)"
                      value={scopeForms[user.id]?.company_ids || ''}
                      onChange={(e) =>
                        setScopeForms({
                          ...scopeForms,
                          [user.id]: {
                            ...scopeForms[user.id],
                            company_ids: e.target.value,
                          },
                        })
                      }
                    />
                    <input
                      placeholder="country_ids"
                      value={scopeForms[user.id]?.country_ids || ''}
                      onChange={(e) =>
                        setScopeForms({
                          ...scopeForms,
                          [user.id]: {
                            ...scopeForms[user.id],
                            country_ids: e.target.value,
                          },
                        })
                      }
                    />
                    <input
                      placeholder="region_ids"
                      value={scopeForms[user.id]?.region_ids || ''}
                      onChange={(e) =>
                        setScopeForms({
                          ...scopeForms,
                          [user.id]: {
                            ...scopeForms[user.id],
                            region_ids: e.target.value,
                          },
                        })
                      }
                    />
                    <input
                      placeholder="branch_ids"
                      value={scopeForms[user.id]?.branch_ids || ''}
                      onChange={(e) =>
                        setScopeForms({
                          ...scopeForms,
                          [user.id]: {
                            ...scopeForms[user.id],
                            branch_ids: e.target.value,
                          },
                        })
                      }
                    />
                    <input
                      placeholder="department_ids"
                      value={scopeForms[user.id]?.department_ids || ''}
                      onChange={(e) =>
                        setScopeForms({
                          ...scopeForms,
                          [user.id]: {
                            ...scopeForms[user.id],
                            department_ids: e.target.value,
                          },
                        })
                      }
                    />
                    <input
                      placeholder="team_ids"
                      value={scopeForms[user.id]?.team_ids || ''}
                      onChange={(e) =>
                        setScopeForms({
                          ...scopeForms,
                          [user.id]: {
                            ...scopeForms[user.id],
                            team_ids: e.target.value,
                          },
                        })
                      }
                    />
                    <input
                      placeholder="customer_ids (örn: ALFKI,ANATR)"
                      value={scopeForms[user.id]?.customer_ids || ''}
                      onChange={(e) =>
                        setScopeForms({
                          ...scopeForms,
                          [user.id]: {
                            ...scopeForms[user.id],
                            customer_ids: e.target.value,
                          },
                        })
                      }
                    />
                    <button type="button" onClick={() => handleUpdateScopes(user.id)}>
                      Scope Kaydet
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
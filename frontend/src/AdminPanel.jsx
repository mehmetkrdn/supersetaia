import { use, useEffect, useMemo, useState } from 'react'

const API = '/api/v1/admin'

const TABS = [
  { key: 'dashboard', label: 'Dashboard' },
  { key: 'users', label: 'Users' },
  { key: 'roles', label: 'Roles' },
  { key: 'permissions', label: 'Permissions' },
  { key: 'scopes', label: 'Scopes' },
  { key: 'dataset_access', label: 'Dataset Access' },
  { key: 'column_security', label: 'Column Security' },
  { key: 'audit_logs', label: 'Audit Logs' },
]

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

function Section({ title, children, right }) {
  return (
    <div style={{
      background: '#fff',
      border: '1px solid #e5e7eb',
      borderRadius: 14,
      padding: 16,
      marginBottom: 16,
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h3 style={{ margin: 0 }}>{title}</h3>
        {right}
      </div>
      {children}
    </div>
  )
}

function Grid({ children, cols = 2 }) {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))`,
        gap: 10,
      }}
    >
      {children}
    </div>
  )
}

function TextInput(props) {
  return (
    <input
      {...props}
      style={{
        width: '100%',
        padding: '10px 12px',
        borderRadius: 10,
        border: '1px solid #d1d5db',
        fontSize: 14,
        ...props.style,
      }}
    />
  )
}

function SelectInput(props) {
  return (
    <select
      {...props}
      style={{
        width: '100%',
        padding: '10px 12px',
        borderRadius: 10,
        border: '1px solid #d1d5db',
        fontSize: 14,
        background: '#fff',
        ...props.style,
      }}
    />
  )
}

function Button({ children, variant = 'primary', ...props }) {
  const styles = {
    primary: { background: '#0f766e', color: '#fff', border: 'none' },
    secondary: { background: '#fff', color: '#111827', border: '1px solid #d1d5db' },
    danger: { background: '#b91c1c', color: '#fff', border: 'none' },
  }

  return (
    <button
      {...props}
      style={{
        padding: '10px 14px',
        borderRadius: 10,
        fontWeight: 600,
        cursor: 'pointer',
        ...styles[variant],
        ...(props.style || {}),
      }}
    >
      {children}
    </button>
  )
}

export default function AdminPanel({ currentUser, onClose }) {
  const [tab, setTab] = useState('dashboard')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const [expandedUserId, setExpandedUserId] = useState(null)
  const [userSearch, setUserSearch] = useState('')
  const [permissionSearch, setPermissionSearch] = useState('')

  const [users, setUsers] = useState([])
  const [roles, setRoles] = useState([])
  const [permissions, setPermissions] = useState([])
  const [datasets, setDatasets] = useState([])
  const [datasetAccess, setDatasetAccess] = useState([])
  const [columnRules, setColumnRules] = useState([])
  const [auditLogs, setAuditLogs] = useState([])

  const [createUserForm, setCreateUserForm] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
    is_active: true,
    is_superadmin: false,
  })

  const [createRoleForm, setCreateRoleForm] = useState({
    code: '',
    name: '',
    description: '',
    priority: 100,
    is_system: false,
    is_active: true,
  })

  const [userEditForms, setUserEditForms] = useState({})
  const [userRoleForms, setUserRoleForms] = useState({})
  const [userScopeForms, setUserScopeForms] = useState({})
  const [resetPasswordForms, setResetPasswordForms] = useState({})
  const [rolePermissionForms, setRolePermissionForms] = useState({})
  const [datasetAccessForms, setDatasetAccessForms] = useState({})
  const [userPermissionForms, setUserPermissionForms] = useState({})
  const [columnRuleForm, setColumnRuleForm] = useState({
    dataset_id: '',
    column_name: '',
    rule_type: 'deny',
    role_code: '',
    user_id: '',
    is_active: true,
  })

  async function apiGet(path) {
    const res = await fetch(`${API}${path}`)
    const text = await res.text()

    let data = null
    try {
      data = text ? JSON.parse(text) : null
    } catch {
      throw new Error(text || 'Sunucudan geçersiz yanıt döndü.')
    }

    if (!res.ok) {
      let msg = data?.detail || data?.message || 'İstek başarısız.'

      if (Array.isArray(msg)) {
        msg = msg
          .map((item) => {
            const loc = Array.isArray(item.loc) ? item.loc.join(' > ') : ''
            return `${loc}: ${item.msg}`
          })
          .join(' | ')
      } else if (typeof msg === 'object') {
        msg = JSON.stringify(msg)
      }

      throw new Error(msg)
    }

    return data
  }

  async function apiSend(path, method, body) {
    const res = await fetch(`${API}${path}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: body ? JSON.stringify(body) : undefined,
    })

    const text = await res.text()

    let data = null
    try {
      data = text ? JSON.parse(text) : null
    } catch {
      throw new Error(text || 'Sunucudan geçersiz yanıt döndü.')
    }

    if (!res.ok) {
      let msg = data?.detail || data?.message || 'İstek başarısız.'

      if (Array.isArray(msg)) {
        msg = msg
          .map((item) => {
            const loc = Array.isArray(item.loc) ? item.loc.join(' > ') : ''
            return `${loc}: ${item.msg}`
          })
          .join(' | ')
      } else if (typeof msg === 'object') {
        msg = JSON.stringify(msg)
      }

      throw new Error(msg)
    }

    return data
  }

  async function loadAll() {
    setLoading(true)
    setError('')
    try {
      const [
        usersData,
        rolesData,
        permissionsData,
        datasetsData,
        datasetAccessData,
        columnSecurityData,
        auditLogsData,
      ] = await Promise.all([
        apiGet('/users'),
        apiGet('/roles'),
        apiGet('/permissions'),
        apiGet('/datasets'),
        apiGet('/dataset-access'),
        apiGet('/column-security'),
        apiGet('/audit-logs'),
      ])

      setUsers(usersData)
      setRoles(rolesData)
      setPermissions(permissionsData)
      setDatasets(datasetsData)
      setDatasetAccess(datasetAccessData)
      setColumnRules(columnSecurityData)
      setAuditLogs(auditLogsData)

      const nextUserEditForms = {}
      const nextUserRoleForms = {}
      const nextUserScopeForms = {}
      const nextResetForms = {}
      const nextRolePermissionForms = {}
      const nextDatasetAccessForms = {}
      const nextUserPermissionForms = {}

      usersData.forEach((user) => {
        nextUserEditForms[user.id] = {
          email: user.email || '',
          full_name: user.full_name || '',
          is_active: Boolean(user.is_active),
          is_superadmin: Boolean(user.is_superadmin),
        }

        nextUserRoleForms[user.id] = {
          role_code: user.role_assignments?.[0]?.role_code || '',
          company_id: user.role_assignments?.[0]?.company_id || '',
        }

        nextUserScopeForms[user.id] = {
          company_ids: (user.company_ids || []).join(','),
          country_ids: (user.country_ids || []).join(','),
          region_ids: (user.region_ids || []).join(','),
          branch_ids: (user.branch_ids || []).join(','),
          department_ids: (user.department_ids || []).join(','),
          team_ids: (user.team_ids || []).join(','),
          customer_ids: (user.customer_ids || []).join(','),
        }

        nextResetForms[user.id] = {
          password: '',
        }

        nextUserPermissionForms[user.id] = {
          permissions: '',
        }
      })

      rolesData.forEach((role) => {
        nextRolePermissionForms[role.id] = {
          permission_codes: (role.permission_codes || []).join(','),
        }
      })

      datasetsData.forEach((dataset) => {
        const rows = datasetAccessData.filter((x) => x.dataset_id === dataset.id)

        nextDatasetAccessForms[dataset.id] = {
          role_codes: rows
            .filter((x) => x.role_code)
            .map((x) => x.role_code)
            .join(','),
          user_ids: rows
            .filter((x) => x.user_id !== null && x.user_id !== undefined)
            .map((x) => x.user_id)
            .join(','),
        }
      })

      setUserEditForms(nextUserEditForms)
      setUserRoleForms(nextUserRoleForms)
      setUserScopeForms(nextUserScopeForms)
      setResetPasswordForms(nextResetForms)
      setRolePermissionForms(nextRolePermissionForms)
      setDatasetAccessForms(nextDatasetAccessForms)
      setUserPermissionForms(nextUserPermissionForms)
    } catch (err) {
      setError(err.message || 'Yükleme hatası.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAll()
  }, [])

  useEffect(() => {
    setMessage('')
    setError('')
  }, [tab])

  async function handleRefresh() {
    setMessage('')
    setError('')
    await loadAll()
  }


  async function handleCreateUser(e) {
    e.preventDefault()
    setMessage('')
    setError('')

    try {
      await apiSend('/users', 'POST', {
        username: createUserForm.username.trim(),
        email: createUserForm.email.trim() || null,
        full_name: createUserForm.full_name.trim() || null,
        password: createUserForm.password,
        is_active: Boolean(createUserForm.is_active),
        is_superadmin: Boolean(createUserForm.is_superadmin),
      })

      setMessage('Kullanıcı oluşturuldu.')
      setCreateUserForm({
        username: '',
        email: '',
        full_name: '',
        password: '',
        is_active: true,
        is_superadmin: false,
      })

      await loadAll()
    } catch (err) {
      setError(err.message || 'Kullanıcı oluşturulamadı.')
    }
  }

  async function handleUpdateUser(userId) {
    setMessage('')
    setError('')
    try {
      await apiSend(`/users/${userId}`, 'PUT', userEditForms[userId])
      setMessage(`Kullanıcı #${userId} güncellendi.`)
      await loadAll()
    } catch (err) {
      setError(err.message || 'Kullanıcı güncellenemedi.')
    }
  }

  async function handleToggleUser(userId) {
    setMessage('')
    setError('')
    try {
      const nextStatus = !Boolean(userEditForms[userId]?.is_active)
      await apiSend(`/users/${userId}/status`, 'PATCH', { is_active: nextStatus })
      setMessage(`Kullanıcı #${userId} durumu güncellendi.`)
      await loadAll()
    } catch (err) {
      setError(err.message || 'Durum güncellenemedi.')
    }
  }

  async function handleResetPassword(userId) {
    setMessage('')
    setError('')
    try {
      const password = resetPasswordForms[userId]?.password || ''
      if (!password.trim()) throw new Error('Yeni şifre girin.')

      await apiSend(`/users/${userId}/password`, 'PATCH', { password })
      setMessage(`Kullanıcı #${userId} şifresi güncellendi.`)
      setResetPasswordForms((prev) => ({
        ...prev,
        [userId]: { password: '' },
      }))
    } catch (err) {
      setError(err.message || 'Şifre güncellenemedi.')
    }
  }

  async function handleSaveUserPermissions(userId) {
    setMessage('')
    setError('')

    try {
      const raw = userPermissionForms[userId]?.permissions || ''

      const permissions = parseStringList(raw).map((item) => {
        const [permission_code, mode] = item.split(':').map((x) => String(x || '').trim())

        return {
          permission_code,
          allow: String(mode || 'allow').toLowerCase() !== 'deny',
        }
      })

      await apiSend(`/users/${userId}/permissions`, 'PUT', { permissions })
      setMessage(`Kullanıcı #${userId} permission override güncellendi.`)
    } catch (err) {
      setError(err.message || 'User permissions güncellenemedi.')
    }
  }

  async function handleSaveUserRoles(userId) {
    setMessage('')
    setError('')
    try {
      const form = userRoleForms[userId] || {}
      const roleCode = String(form.role_code || '').trim()
      const companyId = Number(form.company_id)

      const rolesPayload =
        roleCode && !Number.isNaN(companyId)
          ? [{ role_code: roleCode, company_id: companyId }]
          : []

      await apiSend(`/users/${userId}/roles`, 'PUT', { roles: rolesPayload })
      setMessage(`Kullanıcı #${userId} rolü güncellendi.`)
      await loadAll()
    } catch (err) {
      setError(err.message || 'Rol güncellenemedi.')
    }
  }

  async function handleSaveUserScopes(userId) {
    setMessage('')
    setError('')
    try {
      const form = userScopeForms[userId] || {}

      await apiSend(`/users/${userId}/scopes`, 'PUT', {
        company_ids: parseNumberList(form.company_ids),
        country_ids: parseNumberList(form.country_ids),
        region_ids: parseNumberList(form.region_ids),
        branch_ids: parseNumberList(form.branch_ids),
        department_ids: parseNumberList(form.department_ids),
        team_ids: parseNumberList(form.team_ids),
        customer_ids: parseStringList(form.customer_ids),
      })

      setMessage(`Kullanıcı #${userId} scope bilgileri güncellendi.`)
      await loadAll()
    } catch (err) {
      setError(err.message || 'Scope güncellenemedi.')
    }
  }

  async function handleCreateRole(e) {
    e.preventDefault()
    setMessage('')
    setError('')
    try {
      await apiSend('/roles', 'POST', {
        ...createRoleForm,
        priority: Number(createRoleForm.priority),
      })
      setMessage('Rol oluşturuldu.')
      setCreateRoleForm({
        code: '',
        name: '',
        description: '',
        priority: 100,
        is_system: false,
        is_active: true,
      })
      await loadAll()
    } catch (err) {
      setError(err.message || 'Rol oluşturulamadı.')
    }
  }

  async function handleSaveRolePermissions(roleId) {
    setMessage('')
    setError('')
    try {
      const value = rolePermissionForms[roleId]?.permission_codes || ''
      const permission_codes = parseStringList(value)
      await apiSend(`/roles/${roleId}/permissions`, 'PUT', { permission_codes })
      setMessage(`Rol #${roleId} permission bilgileri güncellendi.`)
      await loadAll()
    } catch (err) {
      setError(err.message || 'Permission güncellenemedi.')
    }
  }

  async function handleSaveDatasetAccess(datasetId) {
    setMessage('')
    setError('')
    try {
      const form = datasetAccessForms[datasetId] || {}
      await apiSend(`/dataset-access/${datasetId}`, 'PUT', {
        dataset_id: datasetId,
        role_codes: parseStringList(form.role_codes),
        user_ids: parseNumberList(form.user_ids),
      })
      setMessage(`Dataset #${datasetId} erişimi güncellendi.`)
      await loadAll()
    } catch (err) {
      setError(err.message || 'Dataset access güncellenemedi.')
    }
  }

  async function handleCreateColumnRule(e) {
    e.preventDefault()
    setMessage('')
    setError('')
    try {
      await apiSend('/column-security', 'POST', {
        dataset_id: Number(columnRuleForm.dataset_id),
        column_name: columnRuleForm.column_name,
        rule_type: columnRuleForm.rule_type,
        role_code: columnRuleForm.role_code || null,
        user_id: columnRuleForm.user_id ? Number(columnRuleForm.user_id) : null,
        is_active: Boolean(columnRuleForm.is_active),
      })
      setMessage('Column security kuralı oluşturuldu.')
      setColumnRuleForm({
        dataset_id: '',
        column_name: '',
        rule_type: 'deny',
        role_code: '',
        user_id: '',
        is_active: true,
      })
      await loadAll()
    } catch (err) {
      setError(err.message || 'Column security kuralı oluşturulamadı.')
    }
  }

  async function handleDeleteColumnRule(ruleId) {
    setMessage('')
    setError('')
    try {
      const res = await fetch(`${API}/column-security/${ruleId}`, { method: 'DELETE' })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Silinemedi.')
      setMessage(`Kural #${ruleId} silindi.`)
      await loadAll()
    } catch (err) {
      setError(err.message || 'Silinemedi.')
    }
  }

  const filteredUsers = useMemo(() => {
    const q = userSearch.trim().toLowerCase()

    if (!q) return users

    return users.filter((user) => {
      const username = String(user.username || '').toLowerCase()
      const email = String(user.email || '').toLowerCase()
      const fullName = String(user.full_name || '').toLowerCase()
      const firstRole = String(user.role_assignments?.[0]?.role_code || '').toLowerCase()

      return (
        username.includes(q) ||
        email.includes(q) ||
        fullName.includes(q) ||
        firstRole.includes(q) ||
        String(user.id).includes(q)
      )
    })
  }, [users, userSearch])


  const groupedPermissions = useMemo(() => {
    const q = permissionSearch.trim().toLowerCase()

    const filtered = permissions.filter((perm) => {
      if (!q) return true

      const code = String(perm.code || '').toLowerCase()
      const name = String(perm.name || '').toLowerCase()
      const description = String(perm.description || '').toLowerCase()

      return (
        code.includes(q) ||
        name.includes(q) ||
        description.includes(q)
      )
    })

    const groups = {}

    filtered.forEach((perm) => {
      const code = String(perm.code || '')
      const prefix = code.includes('.') ? code.split('.')[0] : 'other'

      if (!groups[prefix]) {
        groups[prefix] = []
      }

      groups[prefix].push(perm)
    })

    return Object.entries(groups)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([group, items]) => ({
        group,
        items: items.sort((a, b) => String(a.code || '').localeCompare(String(b.code || ''))),
      }))
  }, [permissions, permissionSearch])



  const stats = useMemo(() => {
    return {
      users: users.length,
      activeUsers: users.filter((x) => x.is_active).length,
      roles: roles.length,
      permissions: permissions.length,
      datasets: datasets.length,
      rules: columnRules.length,
      logs: auditLogs.length,
    }
  }, [users, roles, permissions, datasets, columnRules, auditLogs])

  return (
    <div style={{ minHeight: '100vh', background: '#f3f4f6', padding: 20 }}>
      <div style={{ maxWidth: 1500, margin: '0 auto' }}>
        <div
          style={{
            background: '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: 16,
            padding: 18,
            marginBottom: 16,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: 12,
          }}
        >
          <div>
            <h1 style={{ margin: 0 }}>Admin Panel</h1>
            <div style={{ color: '#6b7280', marginTop: 6 }}>
              {currentUser?.username || 'admin'} olarak giriş yapıldı
            </div>
          </div>

          <div style={{ display: 'flex', gap: 8 }}>
            <Button variant="secondary" onClick={handleRefresh}>Yenile</Button>
            <Button variant="secondary" onClick={onClose}>Panele Dön</Button>
          </div>
        </div>

        {message && (
          <div style={{
            background: '#ecfdf5',
            border: '1px solid #a7f3d0',
            color: '#065f46',
            padding: 12,
            borderRadius: 12,
            marginBottom: 12,
          }}>
            {message}
          </div>
        )}

        {error && (
          <div style={{
            background: '#fef2f2',
            border: '1px solid #fecaca',
            color: '#991b1b',
            padding: 12,
            borderRadius: 12,
            marginBottom: 12,
          }}>
            {error}
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: '250px 1fr', gap: 16 }}>
          <div style={{
            background: '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: 14,
            padding: 12,
            height: 'fit-content',
          }}>
            {TABS.map((item) => (
              <button
                key={item.key}
                type="button"
                onClick={() => setTab(item.key)}
                style={{
                  width: '100%',
                  textAlign: 'left',
                  border: 'none',
                  background: tab === item.key ? '#ccfbf1' : 'transparent',
                  padding: '12px 14px',
                  borderRadius: 10,
                  marginBottom: 6,
                  cursor: 'pointer',
                  fontWeight: tab === item.key ? 700 : 500,
                }}
              >
                {item.label}
              </button>
            ))}
          </div>

          <div>
            {tab === 'dashboard' && (
              <>
                <Grid cols={4}>
                  <Section title="Users">
                    <div style={{ fontSize: 28, fontWeight: 700 }}>{stats.users}</div>
                    <div style={{ color: '#6b7280' }}>Toplam kullanıcı</div>
                  </Section>
                  <Section title="Active Users">
                    <div style={{ fontSize: 28, fontWeight: 700 }}>{stats.activeUsers}</div>
                    <div style={{ color: '#6b7280' }}>Aktif kullanıcı</div>
                  </Section>
                  <Section title="Roles">
                    <div style={{ fontSize: 28, fontWeight: 700 }}>{stats.roles}</div>
                    <div style={{ color: '#6b7280' }}>Rol sayısı</div>
                  </Section>
                  <Section title="Permissions">
                    <div style={{ fontSize: 28, fontWeight: 700 }}>{stats.permissions}</div>
                    <div style={{ color: '#6b7280' }}>Permission sayısı</div>
                  </Section>
                </Grid>

                <Grid cols={3}>
                  <Section title="Datasets">
                    <div style={{ fontSize: 28, fontWeight: 700 }}>{stats.datasets}</div>
                  </Section>
                  <Section title="Column Rules">
                    <div style={{ fontSize: 28, fontWeight: 700 }}>{stats.rules}</div>
                  </Section>
                  <Section title="Audit Logs">
                    <div style={{ fontSize: 28, fontWeight: 700 }}>{stats.logs}</div>
                  </Section>
                </Grid>
              </>
            )}

            {tab === 'users' && (
              <>
                <Section title="Yeni Kullanıcı Ekle">
                  <form onSubmit={handleCreateUser}>
                    <Grid cols={2}>
                      <TextInput
                        placeholder="Username"
                        value={createUserForm.username}
                        onChange={(e) => setCreateUserForm({ ...createUserForm, username: e.target.value })}
                      />
                      <TextInput
                        placeholder="Email"
                        value={createUserForm.email}
                        onChange={(e) => setCreateUserForm({ ...createUserForm, email: e.target.value })}
                      />
                      <TextInput
                        placeholder="Full Name"
                        value={createUserForm.full_name}
                        onChange={(e) => setCreateUserForm({ ...createUserForm, full_name: e.target.value })}
                      />
                      <TextInput
                        type="password"
                        placeholder="Password"
                        value={createUserForm.password}
                        onChange={(e) => setCreateUserForm({ ...createUserForm, password: e.target.value })}
                      />
                    </Grid>

                    <div style={{ display: 'flex', gap: 16, marginTop: 12, flexWrap: 'wrap' }}>
                      <label>
                        <input
                          type="checkbox"
                          checked={createUserForm.is_active}
                          onChange={(e) => setCreateUserForm({ ...createUserForm, is_active: e.target.checked })}
                        /> Aktif
                      </label>
                      <label>
                        <input
                          type="checkbox"
                          checked={createUserForm.is_superadmin}
                          onChange={(e) => setCreateUserForm({ ...createUserForm, is_superadmin: e.target.checked })}
                        /> Superadmin
                      </label>
                    </div>

                    <div style={{ marginTop: 12 }}>
                      <Button type="submit">Kullanıcı Oluştur</Button>
                    </div>
                  </form>
                </Section>

                <Section
                  title="Kullanıcı Listesi"
                  right={
                    <div style={{ minWidth: 280 }}>
                      <TextInput
                        placeholder="Kullanıcı ara (username, email, ad soyad, rol, id)"
                        value={userSearch}
                        onChange={(e) => setUserSearch(e.target.value)}
                      />
                    </div>
                  }
                >
                  <div style={{ color: '#6b7280', marginBottom: 12, fontSize: 14 }}>
                    Toplam {filteredUsers.length} kullanıcı gösteriliyor.
                  </div>

                  <div style={{ display: 'grid', gap: 10 }}>
                    <div
                      style={{
                        display: 'grid',
                        gridTemplateColumns: '1.2fr 1.4fr 1.2fr 0.9fr 0.9fr 1fr 1.4fr',
                        gap: 10,
                        alignItems: 'center',
                        padding: '0 14px',
                        color: '#6b7280',
                        fontSize: 13,
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        letterSpacing: '0.02em',
                      }}
                    >
                      <div>Kullanıcı</div>
                      <div>Email</div>
                      <div>Ad Soyad</div>
                      <div>Durum</div>
                      <div>Yetki</div>
                      <div>Rol</div>
                      <div style={{ textAlign: 'right' }}>İşlemler</div>
                    </div>

                    {filteredUsers.map((user) => {
                      const isExpanded = expandedUserId === user.id
                      const firstRole = user.role_assignments?.[0]?.role_code || '-'

                      return (
                        <div
                          key={user.id}
                          style={{
                            border: '1px solid #e5e7eb',
                            borderRadius: 12,
                            overflow: 'hidden',
                            background: '#fff',
                          }}
                        >
                          <div
                            style={{
                              display: 'grid',
                              gridTemplateColumns: '1.2fr 1.4fr 1.2fr 0.9fr 0.9fr 1fr 1.4fr',
                              gap: 10,
                              alignItems: 'center',
                              padding: 14,
                            }}
                          >
                            <div>
                              <div style={{ fontWeight: 700 }}>{user.username}</div>
                              <div style={{ color: '#6b7280', fontSize: 12 }}>#{user.id}</div>
                            </div>

                            <div style={{ fontSize: 14 }}>
                              {user.email || '-'}
                            </div>

                            <div style={{ fontSize: 14 }}>
                              {user.full_name || '-'}
                            </div>

                            <div>
                              <span
                                style={{
                                  display: 'inline-block',
                                  padding: '4px 10px',
                                  borderRadius: 999,
                                  background: user.is_active ? '#ecfdf5' : '#fef2f2',
                                  color: user.is_active ? '#065f46' : '#991b1b',
                                  border: `1px solid ${user.is_active ? '#a7f3d0' : '#fecaca'}`,
                                  fontSize: 12,
                                  fontWeight: 700,
                                }}
                              >
                                {user.is_active ? 'Aktif' : 'Pasif'}
                              </span>
                            </div>

                            <div>
                              <span
                                style={{
                                  display: 'inline-block',
                                  padding: '4px 10px',
                                  borderRadius: 999,
                                  background: user.is_superadmin ? '#eff6ff' : '#f3f4f6',
                                  color: user.is_superadmin ? '#1d4ed8' : '#374151',
                                  border: `1px solid ${user.is_superadmin ? '#bfdbfe' : '#d1d5db'}`,
                                  fontSize: 12,
                                  fontWeight: 700,
                                }}
                              >
                                {user.is_superadmin ? 'Superadmin' : 'Normal'}
                              </span>
                            </div>

                            <div style={{ fontSize: 14 }}>
                              {firstRole}
                            </div>

                            <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end', flexWrap: 'wrap' }}>
                              <Button
                                variant="secondary"
                                onClick={() =>
                                  setExpandedUserId((prev) => (prev === user.id ? null : user.id))
                                }
                              >
                                {isExpanded ? 'Detayı Kapat' : 'Detay'}
                              </Button>

                              <Button variant="secondary" onClick={() => handleUpdateUser(user.id)}>
                                Kaydet
                              </Button>

                              <Button
                                variant={Boolean(userEditForms[user.id]?.is_active) ? 'danger' : 'primary'}
                                onClick={() => handleToggleUser(user.id)}
                              >
                                {Boolean(userEditForms[user.id]?.is_active) ? 'Pasif Yap' : 'Aktif Yap'}
                              </Button>
                            </div>
                          </div>

                          {isExpanded && (
                            <div
                              style={{
                                borderTop: '1px solid #e5e7eb',
                                padding: 16,
                                background: '#f9fafb',
                              }}
                            >
                              <div style={{ marginBottom: 16 }}>
                                <h4 style={{ margin: '0 0 10px 0' }}>Kullanıcı Bilgileri</h4>

                                <Grid cols={2}>
                                  <TextInput
                                    placeholder="Email"
                                    value={userEditForms[user.id]?.email || ''}
                                    onChange={(e) =>
                                      setUserEditForms((prev) => ({
                                        ...prev,
                                        [user.id]: { ...prev[user.id], email: e.target.value },
                                      }))
                                    }
                                  />
                                  <TextInput
                                    placeholder="Full Name"
                                    value={userEditForms[user.id]?.full_name || ''}
                                    onChange={(e) =>
                                      setUserEditForms((prev) => ({
                                        ...prev,
                                        [user.id]: { ...prev[user.id], full_name: e.target.value },
                                      }))
                                    }
                                  />
                                </Grid>

                                <div style={{ display: 'flex', gap: 16, marginTop: 12, flexWrap: 'wrap' }}>
                                  <label>
                                    <input
                                      type="checkbox"
                                      checked={Boolean(userEditForms[user.id]?.is_active)}
                                      onChange={(e) =>
                                        setUserEditForms((prev) => ({
                                          ...prev,
                                          [user.id]: { ...prev[user.id], is_active: e.target.checked },
                                        }))
                                      }
                                    /> Aktif
                                  </label>

                                  <label>
                                    <input
                                      type="checkbox"
                                      checked={Boolean(userEditForms[user.id]?.is_superadmin)}
                                      onChange={(e) =>
                                        setUserEditForms((prev) => ({
                                          ...prev,
                                          [user.id]: { ...prev[user.id], is_superadmin: e.target.checked },
                                        }))
                                      }
                                    /> Superadmin
                                  </label>
                                </div>
                              </div>

                              <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid #e5e7eb' }}>
                                <h4 style={{ margin: '0 0 10px 0' }}>Şifre Sıfırla</h4>
                                <div style={{ display: 'flex', gap: 8 }}>
                                  <TextInput
                                    type="password"
                                    placeholder="Yeni şifre"
                                    value={resetPasswordForms[user.id]?.password || ''}
                                    onChange={(e) =>
                                      setResetPasswordForms((prev) => ({
                                        ...prev,
                                        [user.id]: { password: e.target.value },
                                      }))
                                    }
                                  />
                                  <Button onClick={() => handleResetPassword(user.id)}>
                                    Şifreyi Güncelle
                                  </Button>
                                </div>
                              </div>

                              <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid #e5e7eb' }}>
                                <h4 style={{ margin: '0 0 8px 0' }}>User Permissions Override</h4>
                                <div style={{ color: '#6b7280', marginBottom: 8, fontSize: 13 }}>
                                  Format: permission_code:allow,permission_code:deny
                                </div>
                                <div style={{ display: 'flex', gap: 8 }}>
                                  <TextInput
                                    placeholder="örn: sql.run:allow,dashboard.publish:deny"
                                    value={userPermissionForms[user.id]?.permissions || ''}
                                    onChange={(e) =>
                                      setUserPermissionForms((prev) => ({
                                        ...prev,
                                        [user.id]: { permissions: e.target.value },
                                      }))
                                    }
                                  />
                                  <Button onClick={() => handleSaveUserPermissions(user.id)}>
                                    Permission Kaydet
                                  </Button>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      )
                    })}

                    {!filteredUsers.length && (
                      <div
                        style={{
                          border: '1px dashed #d1d5db',
                          borderRadius: 12,
                          padding: 20,
                          textAlign: 'center',
                          color: '#6b7280',
                          background: '#fff',
                        }}
                      >
                        Aramaya uygun kullanıcı bulunamadı.
                      </div>
                    )}
                  </div>
                </Section>
              </>
            )}

            {tab === 'roles' && (
              <>
                <Section title="Yeni Rol Oluştur">
                  <form onSubmit={handleCreateRole}>
                    <Grid cols={2}>
                      <TextInput
                        placeholder="Role Code"
                        value={createRoleForm.code}
                        onChange={(e) => setCreateRoleForm({ ...createRoleForm, code: e.target.value })}
                      />
                      <TextInput
                        placeholder="Role Name"
                        value={createRoleForm.name}
                        onChange={(e) => setCreateRoleForm({ ...createRoleForm, name: e.target.value })}
                      />
                      <TextInput
                        placeholder="Description"
                        value={createRoleForm.description}
                        onChange={(e) => setCreateRoleForm({ ...createRoleForm, description: e.target.value })}
                      />
                      <TextInput
                        placeholder="Priority"
                        value={createRoleForm.priority}
                        onChange={(e) => setCreateRoleForm({ ...createRoleForm, priority: e.target.value })}
                      />
                    </Grid>

                    <div style={{ display: 'flex', gap: 16, marginTop: 12, flexWrap: 'wrap' }}>
                      <label>
                        <input
                          type="checkbox"
                          checked={createRoleForm.is_system}
                          onChange={(e) => setCreateRoleForm({ ...createRoleForm, is_system: e.target.checked })}
                        /> System
                      </label>
                      <label>
                        <input
                          type="checkbox"
                          checked={createRoleForm.is_active}
                          onChange={(e) => setCreateRoleForm({ ...createRoleForm, is_active: e.target.checked })}
                        /> Active
                      </label>
                    </div>

                    <div style={{ marginTop: 12 }}>
                      <Button type="submit">Rol Oluştur</Button>
                    </div>
                  </form>
                </Section>

                <Section title="Rol Listesi">
                  <div style={{ color: '#6b7280', marginBottom: 12, fontSize: 14 }}>
                    Toplam {roles.length} rol gösteriliyor.
                  </div>

                  <div style={{ display: 'grid', gap: 12 }}>
                    {roles.map((role) => {
                      const permissionList = role.permission_codes || []
                      const previewPermissions = permissionList.slice(0, 8)
                      const remainingCount = Math.max(permissionList.length - previewPermissions.length, 0)

                      return (
                        <div
                          key={role.id}
                          style={{
                            border: '1px solid #e5e7eb',
                            borderRadius: 12,
                            padding: 16,
                            background: '#fff',
                          }}
                        >
                          <div
                            style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'flex-start',
                              gap: 12,
                              flexWrap: 'wrap',
                              marginBottom: 12,
                            }}
                          >
                            <div>
                              <div style={{ fontSize: 20, fontWeight: 700 }}>
                                {role.code} ({role.name})
                              </div>
                              <div style={{ color: '#6b7280', marginTop: 4, fontSize: 14 }}>
                                {role.description || 'Açıklama yok'}
                              </div>
                            </div>

                            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                              <span
                                style={{
                                  display: 'inline-block',
                                  padding: '4px 10px',
                                  borderRadius: 999,
                                  background: '#f3f4f6',
                                  color: '#374151',
                                  border: '1px solid #d1d5db',
                                  fontSize: 12,
                                  fontWeight: 700,
                                }}
                              >
                                Priority: {role.priority}
                              </span>

                              <span
                                style={{
                                  display: 'inline-block',
                                  padding: '4px 10px',
                                  borderRadius: 999,
                                  background: role.is_active ? '#ecfdf5' : '#fef2f2',
                                  color: role.is_active ? '#065f46' : '#991b1b',
                                  border: `1px solid ${role.is_active ? '#a7f3d0' : '#fecaca'}`,
                                  fontSize: 12,
                                  fontWeight: 700,
                                }}
                              >
                                {role.is_active ? 'Active' : 'Inactive'}
                              </span>

                              <span
                                style={{
                                  display: 'inline-block',
                                  padding: '4px 10px',
                                  borderRadius: 999,
                                  background: role.is_system ? '#eff6ff' : '#f9fafb',
                                  color: role.is_system ? '#1d4ed8' : '#4b5563',
                                  border: `1px solid ${role.is_system ? '#bfdbfe' : '#e5e7eb'}`,
                                  fontSize: 12,
                                  fontWeight: 700,
                                }}
                              >
                                {role.is_system ? 'System' : 'Custom'}
                              </span>

                              <span
                                style={{
                                  display: 'inline-block',
                                  padding: '4px 10px',
                                  borderRadius: 999,
                                  background: '#f9fafb',
                                  color: '#374151',
                                  border: '1px solid #e5e7eb',
                                  fontSize: 12,
                                  fontWeight: 700,
                                }}
                              >
                                {permissionList.length} permission
                              </span>
                            </div>
                          </div>

                          <div style={{ marginBottom: 14 }}>
                            <div style={{ fontWeight: 600, marginBottom: 8 }}>
                              Permission Ön İzleme
                            </div>

                            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                              {previewPermissions.length > 0 ? (
                                <>
                                  {previewPermissions.map((perm) => (
                                    <span
                                      key={perm}
                                      style={{
                                        display: 'inline-block',
                                        padding: '4px 10px',
                                        borderRadius: 999,
                                        background: '#f9fafb',
                                        color: '#374151',
                                        border: '1px solid #e5e7eb',
                                        fontSize: 12,
                                        fontWeight: 600,
                                      }}
                                    >
                                      {perm}
                                    </span>
                                  ))}

                                  {remainingCount > 0 && (
                                    <span
                                      style={{
                                        display: 'inline-block',
                                        padding: '4px 10px',
                                        borderRadius: 999,
                                        background: '#fff7ed',
                                        color: '#9a3412',
                                        border: '1px solid #fdba74',
                                        fontSize: 12,
                                        fontWeight: 700,
                                      }}
                                    >
                                      +{remainingCount} daha
                                    </span>
                                  )}
                                </>
                              ) : (
                                <span style={{ color: '#6b7280', fontSize: 14 }}>
                                  Bu role ait permission görünmüyor.
                                </span>
                              )}
                            </div>
                          </div>

                          <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: 14 }}>
                            <div style={{ fontWeight: 600, marginBottom: 8 }}>
                              Permission Düzenle
                            </div>

                            <TextInput
                              placeholder="permission codes (örn: sql.run,dashboard.view)"
                              value={rolePermissionForms[role.id]?.permission_codes || ''}
                              onChange={(e) =>
                                setRolePermissionForms((prev) => ({
                                  ...prev,
                                  [role.id]: { permission_codes: e.target.value },
                                }))
                              }
                            />

                            <div style={{ color: '#6b7280', marginTop: 8, fontSize: 13 }}>
                              Virgülle ayrılmış permission code listesi girin.
                            </div>

                            <div style={{ marginTop: 10 }}>
                              <Button onClick={() => handleSaveRolePermissions(role.id)}>
                                Permission Kaydet
                              </Button>
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </Section>
              </>
            )}

            {tab === 'permissions' && (
              <Section
                title="Permission Listesi"
                right={
                  <div style={{ minWidth: 280 }}>
                    <TextInput
                      placeholder="Permission ara (code, name, açıklama)"
                      value={permissionSearch}
                      onChange={(e) => setPermissionSearch(e.target.value)}
                    />
                  </div>
                }
              >
                <div style={{ color: '#6b7280', marginBottom: 12, fontSize: 14 }}>
                  Toplam {groupedPermissions.reduce((sum, group) => sum + group.items.length, 0)} permission gösteriliyor.
                </div>

                <div style={{ display: 'grid', gap: 14 }}>
                  {groupedPermissions.map(({ group, items }) => (
                    <div
                      key={group}
                      style={{
                        border: '1px solid #e5e7eb',
                        borderRadius: 12,
                        background: '#fff',
                        overflow: 'hidden',
                      }}
                    >
                      <div
                        style={{
                          padding: '12px 14px',
                          background: '#f9fafb',
                          borderBottom: '1px solid #e5e7eb',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                        }}
                      >
                        <div style={{ fontWeight: 700 }}>
                          {group}.*
                        </div>
                        <div style={{ color: '#6b7280', fontSize: 13 }}>
                          {items.length} kayıt
                        </div>
                      </div>

                      <div style={{ display: 'grid', gap: 0 }}>
                        {items.map((perm, index) => (
                          <div
                            key={perm.id}
                            style={{
                              padding: '12px 14px',
                              borderTop: index === 0 ? 'none' : '1px solid #f1f5f9',
                            }}
                          >
                            <div style={{ fontWeight: 700, marginBottom: 4 }}>
                              {perm.code}
                            </div>
                            <div style={{ marginBottom: 4 }}>
                              {perm.name || '-'}
                            </div>
                            <div style={{ color: '#6b7280', fontSize: 14 }}>
                              {perm.description || '-'}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}

                  {!groupedPermissions.length && (
                    <div
                      style={{
                        border: '1px dashed #d1d5db',
                        borderRadius: 12,
                        padding: 20,
                        textAlign: 'center',
                        color: '#6b7280',
                        background: '#fff',
                      }}
                    >
                      Aramaya uygun permission bulunamadı.
                    </div>
                  )}
                </div>
              </Section>
            )}

            {tab === 'scopes' && (
              <>
                {users.map((user) => (
                  <Section key={user.id} title={`Scope Yönetimi - ${user.username} #${user.id}`}>
                    <Grid cols={2}>
                      <TextInput
                        placeholder="company_ids (örn: 1,2)"
                        value={userScopeForms[user.id]?.company_ids || ''}
                        onChange={(e) =>
                          setUserScopeForms((prev) => ({
                            ...prev,
                            [user.id]: { ...prev[user.id], company_ids: e.target.value },
                          }))
                        }
                      />
                      <TextInput
                        placeholder="country_ids"
                        value={userScopeForms[user.id]?.country_ids || ''}
                        onChange={(e) =>
                          setUserScopeForms((prev) => ({
                            ...prev,
                            [user.id]: { ...prev[user.id], country_ids: e.target.value },
                          }))
                        }
                      />
                      <TextInput
                        placeholder="region_ids"
                        value={userScopeForms[user.id]?.region_ids || ''}
                        onChange={(e) =>
                          setUserScopeForms((prev) => ({
                            ...prev,
                            [user.id]: { ...prev[user.id], region_ids: e.target.value },
                          }))
                        }
                      />
                      <TextInput
                        placeholder="branch_ids"
                        value={userScopeForms[user.id]?.branch_ids || ''}
                        onChange={(e) =>
                          setUserScopeForms((prev) => ({
                            ...prev,
                            [user.id]: { ...prev[user.id], branch_ids: e.target.value },
                          }))
                        }
                      />
                      <TextInput
                        placeholder="department_ids"
                        value={userScopeForms[user.id]?.department_ids || ''}
                        onChange={(e) =>
                          setUserScopeForms((prev) => ({
                            ...prev,
                            [user.id]: { ...prev[user.id], department_ids: e.target.value },
                          }))
                        }
                      />
                      <TextInput
                        placeholder="team_ids"
                        value={userScopeForms[user.id]?.team_ids || ''}
                        onChange={(e) =>
                          setUserScopeForms((prev) => ({
                            ...prev,
                            [user.id]: { ...prev[user.id], team_ids: e.target.value },
                          }))
                        }
                      />
                    </Grid>

                    <div style={{ marginTop: 10 }}>
                      <TextInput
                        placeholder="customer_ids (örn: ALFKI,ANATR)"
                        value={userScopeForms[user.id]?.customer_ids || ''}
                        onChange={(e) =>
                          setUserScopeForms((prev) => ({
                            ...prev,
                            [user.id]: { ...prev[user.id], customer_ids: e.target.value },
                          }))
                        }
                      />
                    </div>

                    <div style={{ marginTop: 12 }}>
                      <Button onClick={() => handleSaveUserScopes(user.id)}>Scope Kaydet</Button>
                    </div>
                  </Section>
                ))}
              </>
            )}

            {tab === 'dataset_access' && (
              <>
                <Section title="Company Bazlı Rol Atama">
                  <div style={{ color: '#6b7280', marginBottom: 14, fontSize: 14, lineHeight: 1.5 }}>
                    Bu bölüm, kullanıcıya belirli bir company_id için rol atamak içindir.
                    Buradaki işlem dataset erişimi tanımlamaz; kullanıcı-şirket-rol ilişkisini günceller.
                  </div>

                  <div style={{ display: 'grid', gap: 10 }}>
                    {users.map((user) => (
                      <div
                        key={user.id}
                        style={{
                          border: '1px solid #e5e7eb',
                          borderRadius: 12,
                          padding: 14,
                          background: '#fff',
                        }}
                      >
                        <div
                          style={{
                            display: 'grid',
                            gridTemplateColumns: '1.1fr 1fr 1fr auto',
                            gap: 10,
                            alignItems: 'center',
                          }}
                        >
                          <div>
                            <div style={{ fontWeight: 700 }}>{user.username}</div>
                            <div style={{ color: '#6b7280', fontSize: 12 }}>#{user.id}</div>
                          </div>

                          <TextInput
                            placeholder="role_code"
                            value={userRoleForms[user.id]?.role_code || ''}
                            onChange={(e) =>
                              setUserRoleForms((prev) => ({
                                ...prev,
                                [user.id]: { ...prev[user.id], role_code: e.target.value },
                              }))
                            }
                          />

                          <TextInput
                            placeholder="company_id"
                            value={userRoleForms[user.id]?.company_id || ''}
                            onChange={(e) =>
                              setUserRoleForms((prev) => ({
                                ...prev,
                                [user.id]: { ...prev[user.id], company_id: e.target.value },
                              }))
                            }
                          />

                          <Button onClick={() => handleSaveUserRoles(user.id)}>
                            Rol Ata
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </Section>

                <Section title="Dataset Access Rules">
                  <div style={{ color: '#6b7280', marginBottom: 14, fontSize: 14, lineHeight: 1.5 }}>
                    Bu bölüm, dataset bazında hangi rollerin ve kullanıcıların erişebileceğini tanımlar.
                    Virgülle ayrılmış role_code ve user_id listeleri kullanılabilir.
                  </div>

                  <div style={{ display: 'grid', gap: 12 }}>
                    {datasets.map((dataset) => (
                      <div
                        key={dataset.id}
                        style={{
                          border: '1px solid #e5e7eb',
                          borderRadius: 12,
                          padding: 14,
                          background: '#fff',
                        }}
                      >
                        <div style={{ marginBottom: 10 }}>
                          <div style={{ fontWeight: 700 }}>{dataset.display_name || dataset.table_name}</div>
                          <div style={{ color: '#6b7280', fontSize: 13 }}>
                            table_name: {dataset.table_name} | dataset_id: {dataset.id}
                          </div>
                        </div>

                        <Grid cols={2}>
                          <TextInput
                            placeholder="role_codes (örn: manager,guest)"
                            value={datasetAccessForms[dataset.id]?.role_codes || ''}
                            onChange={(e) =>
                              setDatasetAccessForms((prev) => ({
                                ...prev,
                                [dataset.id]: { ...prev[dataset.id], role_codes: e.target.value },
                              }))
                            }
                          />

                          <TextInput
                            placeholder="user_ids (örn: 1,2,3)"
                            value={datasetAccessForms[dataset.id]?.user_ids || ''}
                            onChange={(e) =>
                              setDatasetAccessForms((prev) => ({
                                ...prev,
                                [dataset.id]: { ...prev[dataset.id], user_ids: e.target.value },
                              }))
                            }
                          />
                        </Grid>

                        <div style={{ marginTop: 10 }}>
                          <Button onClick={() => handleSaveDatasetAccess(dataset.id)}>
                            Dataset Access Kaydet
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </Section>
              </>
            )}

            {tab === 'column_security' && (
              <>
                <Section title="Yeni Column Security Kuralı">
                  <form onSubmit={handleCreateColumnRule}>
                    <Grid cols={2}>
                      <SelectInput
                        value={columnRuleForm.dataset_id}
                        onChange={(e) => setColumnRuleForm({ ...columnRuleForm, dataset_id: e.target.value })}
                      >
                        <option value="">Dataset seç</option>
                        {datasets.map((dataset) => (
                          <option key={dataset.id} value={dataset.id}>
                            {dataset.table_name} ({dataset.id})
                          </option>
                        ))}
                      </SelectInput>

                      <TextInput
                        placeholder="column_name"
                        value={columnRuleForm.column_name}
                        onChange={(e) => setColumnRuleForm({ ...columnRuleForm, column_name: e.target.value })}
                      />

                      <SelectInput
                        value={columnRuleForm.rule_type}
                        onChange={(e) => setColumnRuleForm({ ...columnRuleForm, rule_type: e.target.value })}
                      >
                        <option value="deny">deny</option>
                        <option value="mask">mask</option>
                      </SelectInput>

                      {/* ROLE DROPDOWN */}
                      <SelectInput
                        value={columnRuleForm.role_code}
                        onChange={e => setColumnRuleForm({ ...columnRuleForm, role_code: e.target.value, user_id: '' })}
                      >
                        <option value="">Rol seç (opsiyonel)</option>
                        {roles.map(r => <option key={r.id} value={r.code}>{r.name}</option>)}
                      </SelectInput>

                      {/* USER DROPDOWN */}
                      <SelectInput
                        value={columnRuleForm.user_id}
                        onChange={e => setColumnRuleForm({ ...columnRuleForm, user_id: e.target.value, role_code: '' })}
                      >
                        <option value="">Kullanıcı seç (opsiyonel)</option>
                        {users.map(u => <option key={u.id} value={u.id}>{u.username} (#{u.id})</option>)}
                      </SelectInput>
                    </Grid>

                    <div style={{ marginTop: 12 }}>
                      <Button type="submit">Kural Oluştur</Button>
                    </div>
                  </form>
                </Section>

                <Section title="Mevcut Kurallar">
                  <div style={{ display: 'grid', gap: 10 }}>
                    {columnRules.map((rule) => (
                      <div
                        key={rule.id}
                        style={{
                          border: '1px solid #e5e7eb',
                          borderRadius: 10,
                          padding: 12,
                          display: 'flex',
                          justifyContent: 'space-between',
                          gap: 12,
                          alignItems: 'center',
                        }}
                      >
                        <div>
                          <div><strong>Dataset:</strong> {datasets.find(d => d.id === rule.dataset_id)?.table_name || rule.dataset_id}</div>
                          <div><strong>Column:</strong> {rule.column_name}</div>
                          <div><strong>Rule:</strong> {rule.rule_type}</div>
                          <div><strong>Role:</strong> {rule.role_code || '-'}</div>
                          <div><strong>User:</strong> {rule.user_id ? (users.find(u => u.id === rule.user_id)?.username || rule.user_id) : '-'}</div>
                        </div>

                        <Button variant="danger" onClick={() => handleDeleteColumnRule(rule.id)}>
                          Sil
                        </Button>
                      </div>
                    ))}
                  </div>
                </Section>
              </>
            )}

            {tab === 'audit_logs' && (
              <Section title="Audit Logs">
                <div style={{ color: '#6b7280', marginBottom: 12, fontSize: 14 }}>
                  Toplam {auditLogs.length} log kaydı gösteriliyor.
                </div>

                <div style={{ display: 'grid', gap: 10 }}>
                  {auditLogs.map((log) => {
                    const summaryParts = [
                      log.action_type || '-',
                      log.target_type ? `${log.target_type}` : null,
                      log.target_id ? `#${log.target_id}` : null,
                    ].filter(Boolean)

                    return (
                      <div
                        key={log.id}
                        style={{
                          border: '1px solid #e5e7eb',
                          borderRadius: 12,
                          background: '#fff',
                          overflow: 'hidden',
                        }}
                      >
                        <div
                          style={{
                            display: 'grid',
                            gridTemplateColumns: '1.2fr 1fr 0.8fr 1fr auto',
                            gap: 12,
                            alignItems: 'center',
                            padding: 14,
                          }}
                        >
                          <div>
                            <div style={{ fontWeight: 700 }}>{log.action_type || '-'}</div>
                            <div style={{ color: '#6b7280', fontSize: 12 }}>
                              Log ID: {log.id}
                            </div>
                          </div>

                          <div style={{ fontSize: 14 }}>
                            <div style={{ fontWeight: 600 }}>User</div>
                            <div style={{ color: '#6b7280' }}>
                              {log.user_id ?? '-'}
                            </div>
                          </div>

                          <div style={{ fontSize: 14 }}>
                            <div style={{ fontWeight: 600 }}>Target</div>
                            <div style={{ color: '#6b7280' }}>
                              {log.target_type || '-'}
                            </div>
                          </div>

                          <div style={{ fontSize: 14 }}>
                            <div style={{ fontWeight: 600 }}>Time</div>
                            <div style={{ color: '#6b7280' }}>
                              {log.created_at || '-'}
                            </div>
                          </div>

                          <div>
                            <span
                              style={{
                                display: 'inline-block',
                                padding: '4px 10px',
                                borderRadius: 999,
                                background: '#f9fafb',
                                color: '#374151',
                                border: '1px solid #e5e7eb',
                                fontSize: 12,
                                fontWeight: 700,
                              }}
                            >
                              {summaryParts.join(' • ')}
                            </span>
                          </div>
                        </div>

                        <details
                          style={{
                            borderTop: '1px solid #e5e7eb',
                            background: '#f9fafb',
                          }}
                        >
                          <summary
                            style={{
                              cursor: 'pointer',
                              padding: '12px 14px',
                              fontWeight: 600,
                              color: '#374151',
                            }}
                          >
                            Detail JSON
                          </summary>

                          <div style={{ padding: '0 14px 14px 14px' }}>
                            <pre
                              style={{
                                margin: 0,
                                background: '#fff',
                                border: '1px solid #e5e7eb',
                                padding: 12,
                                borderRadius: 10,
                                whiteSpace: 'pre-wrap',
                                fontSize: 12,
                                overflowX: 'auto',
                              }}
                            >
                              {JSON.stringify(log.detail_json || {}, null, 2)}
                            </pre>
                          </div>
                        </details>
                      </div>
                    )
                  })}

                  {!auditLogs.length && (
                    <div
                      style={{
                        border: '1px dashed #d1d5db',
                        borderRadius: 12,
                        padding: 20,
                        textAlign: 'center',
                        color: '#6b7280',
                        background: '#fff',
                      }}
                    >
                      Audit log kaydı bulunamadı.
                    </div>
                  )}
                </div>
              </Section>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
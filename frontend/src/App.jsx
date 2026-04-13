import { useEffect, useMemo, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  AreaChart,
  Area,
  ComposedChart,
  RadialBarChart,
  RadialBar,
  FunnelChart,
  Funnel,
  LabelList,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import './App.css'
import EChart from './components/EChart'
import {
  analyzeVisualizationOptions,
  buildChartData,
  VISUALIZATION_TYPES,
} from './utils/visualization'

const API_BASE = '/api'
const AUTH_LOGIN_URL = '/api/v1/auth/login'
const AUTH_ME_URL = '/api/v1/auth/me'

const ROLES = [
  { value: 'admin', label: 'Admin' },
  { value: 'manager', label: 'Yönetici' },
  { value: 'team_leader', label: 'Takım Lideri' },
  { value: 'customer', label: 'Müşteri' },
  { value: 'hr', label: 'İK' },
  { value: 'guest', label: 'Misafir' },
]

const LIMIT_OPTIONS = [10, 25, 50, 100, 'all']
const UI_LOCALES = ['tr', 'en', 'ar', 'fr']
const LOCALE_LABELS = {
  tr: 'Türkçe',
  en: 'English',
  ar: 'العربية',
  fr: 'Français',
}

const VIEW_LABELS = {
  [VISUALIZATION_TYPES.TABLE]: 'Tablo',
  [VISUALIZATION_TYPES.BAR]: 'Bar',
  [VISUALIZATION_TYPES.LINE]: 'Line',
  [VISUALIZATION_TYPES.AREA]: 'Area',
  [VISUALIZATION_TYPES.PIE]: 'Pie',
  [VISUALIZATION_TYPES.SCATTER]: 'Scatter',
  [VISUALIZATION_TYPES.COMBO]: 'Combo',
  [VISUALIZATION_TYPES.TREND]: 'Trend',
  [VISUALIZATION_TYPES.PROGRESS]: 'Progress',
  [VISUALIZATION_TYPES.ROW]: 'Row',
  [VISUALIZATION_TYPES.FUNNEL]: 'Funnel',
  [VISUALIZATION_TYPES.GAUGE]: 'Gauge',
  [VISUALIZATION_TYPES.DETAIL]: 'Detail',
  [VISUALIZATION_TYPES.PIVOT]: 'Pivot',
  [VISUALIZATION_TYPES.WATERFALL]: 'Waterfall',
  [VISUALIZATION_TYPES.BOX_PLOT]: 'Box Plot',
  [VISUALIZATION_TYPES.SANKEY]: 'Sankey',
  [VISUALIZATION_TYPES.MAP]: 'Map',
  [VISUALIZATION_TYPES.KPI]: 'KPI',
}

const CHART_PALETTE = [
  {
    type: VISUALIZATION_TYPES.TABLE,
    labelKey: 'chart.table',
    hintKey: 'chartHint.table',
    icon: '▦',
  },
  {
    type: VISUALIZATION_TYPES.BAR,
    labelKey: 'chart.bar',
    hintKey: 'chartHint.bar',
    icon: '▮',
  },
  {
    type: VISUALIZATION_TYPES.LINE,
    labelKey: 'chart.line',
    hintKey: 'chartHint.line',
    icon: '⌁',
  },
  {
    type: VISUALIZATION_TYPES.KPI,
    labelKey: 'chart.kpi',
    hintKey: 'chartHint.kpi',
    icon: '#',
  },
  {
    type: VISUALIZATION_TYPES.PIE,
    labelKey: 'chart.pie',
    hintKey: 'chartHint.pie',
    icon: '◔',
  },
  {
    type: VISUALIZATION_TYPES.AREA,
    labelKey: 'chart.area',
    hintKey: 'chartHint.area',
    icon: '▱',
  },
  {
    type: VISUALIZATION_TYPES.SCATTER,
    labelKey: 'chart.scatter',
    hintKey: 'chartHint.scatter',
    icon: '⋯',
  },
  {
    type: VISUALIZATION_TYPES.COMBO,
    labelKey: 'chart.combo',
    hintKey: 'chartHint.combo',
    icon: '≋',
  },
  {
    type: VISUALIZATION_TYPES.TREND,
    labelKey: 'chart.trend',
    hintKey: 'chartHint.trend',
    icon: '↗',
  },
  {
    type: VISUALIZATION_TYPES.PROGRESS,
    labelKey: 'chart.progress',
    hintKey: 'chartHint.progress',
    icon: '◌',
  },
  {
    type: VISUALIZATION_TYPES.ROW,
    labelKey: 'chart.row',
    hintKey: 'chartHint.row',
    icon: '☰',
  },
  {
    type: VISUALIZATION_TYPES.FUNNEL,
    labelKey: 'chart.funnel',
    hintKey: 'chartHint.funnel',
    icon: '⏷',
  },
  {
    type: VISUALIZATION_TYPES.GAUGE,
    labelKey: 'chart.gauge',
    hintKey: 'chartHint.gauge',
    icon: '◠',
  },
  {
    type: VISUALIZATION_TYPES.DETAIL,
    labelKey: 'chart.detail',
    hintKey: 'chartHint.detail',
    icon: '☷',
  },
  {
    type: VISUALIZATION_TYPES.PIVOT,
    labelKey: 'chart.pivot',
    hintKey: 'chartHint.pivot',
    icon: '⊞',
  },
  {
    type: VISUALIZATION_TYPES.WATERFALL,
    labelKey: 'chart.waterfall',
    hintKey: 'chartHint.waterfall',
    icon: '⤓',
  },
  {
    type: VISUALIZATION_TYPES.BOX_PLOT,
    labelKey: 'chart.box',
    hintKey: 'chartHint.box',
    icon: '▢',
  },
  {
    type: VISUALIZATION_TYPES.SANKEY,
    labelKey: 'chart.sankey',
    hintKey: 'chartHint.sankey',
    icon: '⇄',
  },
  {
    type: VISUALIZATION_TYPES.MAP,
    labelKey: 'chart.map',
    hintKey: 'chartHint.map',
    icon: '⌖',
  },
]

const PIE_COLORS = ['#007b70', '#0ea5a0', '#14b8a6', '#2dd4bf', '#5eead4', '#99f6e4']

function formatNumber(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) return value
  return value.toLocaleString('tr-TR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  })
}

function truncateLabel(value, maxLength = 18) {
  const text = String(value ?? '')
  if (text.length <= maxLength) return text
  return `${text.slice(0, maxLength)}...`
}

let messageId = 0
function nextId() {
  messageId += 1
  return messageId
}

export default function App() {
  const { t, i18n } = useTranslation()
  const [question, setQuestion] = useState('')
  const [role, setRole] = useState('guest')
  const [username, setUsername] = useState('')
  const [country, setCountry] = useState('')
  const [region, setRegion] = useState('')
  const [department, setDepartment] = useState('')
  const [limit, setLimit] = useState(25)

  const [token, setToken] = useState(localStorage.getItem('access_token') || '')
  const [currentUser, setCurrentUser] = useState(null)
  const [authLoading, setAuthLoading] = useState(false)
  const [loginUsername, setLoginUsername] = useState('')
  const [loginPassword, setLoginPassword] = useState('')
  const [loginError, setLoginError] = useState('')

  const [uiLocale, setUiLocale] = useState(() => {
    const saved = localStorage.getItem('app_ui_locale')
    return UI_LOCALES.includes(saved) ? saved : 'tr'
  })
  const [isLocaleOpen, setIsLocaleOpen] = useState(false)
  const localeRef = useRef(null)

  useEffect(() => {
    localStorage.setItem('app_ui_locale', uiLocale)
  }, [uiLocale])

  useEffect(() => {
    if (!i18n) return
    if (i18n.language !== uiLocale) {
      i18n.changeLanguage(uiLocale)
    }
  }, [i18n, uiLocale])

  useEffect(() => {
    if (!isLocaleOpen) return
    const onDown = (e) => {
      const root = localeRef.current
      if (!root) return
      if (root.contains(e.target)) return
      setIsLocaleOpen(false)
    }
    document.addEventListener('mousedown', onDown)
    return () => document.removeEventListener('mousedown', onDown)
  }, [isLocaleOpen])

  const [sql, setSql] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const [columns, setColumns] = useState([])
  const [rows, setRows] = useState([])
  const [rowCount, setRowCount] = useState(0)
  const [truncated, setTruncated] = useState(false)
  const [selectedView, setSelectedView] = useState(VISUALIZATION_TYPES.TABLE)

  const [messages, setMessages] = useState([])

  const chatEndRef = useRef(null)

  const visualizationInfo = useMemo(() => {
    return analyzeVisualizationOptions(columns, rows)
  }, [columns, rows])

  const chartData = useMemo(() => {
    if (
      selectedView !== VISUALIZATION_TYPES.BAR &&
      selectedView !== VISUALIZATION_TYPES.LINE &&
      selectedView !== VISUALIZATION_TYPES.AREA &&
      selectedView !== VISUALIZATION_TYPES.COMBO &&
      selectedView !== VISUALIZATION_TYPES.TREND &&
      selectedView !== VISUALIZATION_TYPES.ROW &&
      selectedView !== VISUALIZATION_TYPES.FUNNEL
    ) {
      return []
    }

    return buildChartData(columns, rows)
  }, [columns, rows, selectedView])

  const pieData = useMemo(() => {
    if (selectedView !== VISUALIZATION_TYPES.PIE) return []
    const transformed = buildChartData(columns, rows)
    if (!Array.isArray(transformed) || transformed.length === 0) return []

    const firstRow = transformed[0] || {}
    const keys = Object.keys(firstRow)
    if (keys.length < 2) return []

    const labelKey = keys[0]
    const valueKey = keys.find((k) => typeof firstRow[k] === 'number' && k !== labelKey)
    if (!valueKey) return []

    return transformed
      .map((row) => ({
        name: String(row[labelKey]),
        value: Number(row[valueKey]),
      }))
      .filter((item) => Number.isFinite(item.value))
  }, [columns, rows, selectedView])

  const scatterConfig = useMemo(() => {
    if (selectedView !== VISUALIZATION_TYPES.SCATTER) {
      return { data: [], xKey: '', yKey: '' }
    }

    const transformed = buildChartData(columns, rows)
    if (transformed.length === 0) return { data: [], xKey: '', yKey: '' }

    const firstRow = transformed[0] || {}
    const numericKeys = Object.keys(firstRow).filter(
      (key) => typeof firstRow[key] === 'number',
    )

    if (numericKeys.length < 2) return { data: [], xKey: '', yKey: '' }

    const [xKey, yKey] = numericKeys
    return { data: transformed, xKey, yKey }
  }, [columns, rows, selectedView])

  const kpiValue = useMemo(() => {
    if (
      selectedView !== VISUALIZATION_TYPES.KPI ||
      rows.length !== 1 ||
      columns.length !== 1
    ) {
      return null
    }

    const rawValue = rows[0]?.[0]

    if (typeof rawValue === 'number') return rawValue

    if (typeof rawValue === 'string') {
      const parsed = Number(rawValue.replace(',', '.'))
      return Number.isNaN(parsed) ? rawValue : parsed
    }

    return rawValue
  }, [columns, rows, selectedView])

  const progressValue = useMemo(() => {
    if (selectedView !== VISUALIZATION_TYPES.PROGRESS) return null
    if (!rows.length || !columns.length) return null

    const rawValue = rows[0]?.[0]
    const numeric = typeof rawValue === 'number'
      ? rawValue
      : Number(String(rawValue ?? '').replace(',', '.'))
    if (Number.isNaN(numeric)) return null

    return Math.max(0, Math.min(100, numeric))
  }, [columns, rows, selectedView])

  const gaugeValue = useMemo(() => {
    if (selectedView !== VISUALIZATION_TYPES.GAUGE) return null
    if (!rows.length || !columns.length) return null

    const rawValue = rows[0]?.[0]
    const numeric = typeof rawValue === 'number'
      ? rawValue
      : Number(String(rawValue ?? '').replace(',', '.'))
    if (Number.isNaN(numeric)) return null
    return Math.max(0, Math.min(100, numeric))
  }, [columns, rows, selectedView])

  const funnelData = useMemo(() => {
    if (selectedView !== VISUALIZATION_TYPES.FUNNEL) return []
    if (!chartData.length) return []
    const first = chartData[0] || {}
    const keys = Object.keys(first)
    if (keys.length < 2) return []

    const labelKey = keys[0]
    const valueKey = keys.find((key) => typeof first[key] === 'number' && key !== labelKey)
    if (!valueKey) return []

    return chartData
      .map((row) => ({
        name: String(row[labelKey]),
        value: Number(row[valueKey]),
      }))
      .filter((item) => Number.isFinite(item.value))
      .sort((a, b) => b.value - a.value)
  }, [chartData, selectedView])

  const detailRows = useMemo(() => {
    if (selectedView !== VISUALIZATION_TYPES.DETAIL) return []
    return rows.slice(0, 30)
  }, [rows, selectedView])

  const pivotModel = useMemo(() => {
    if (selectedView !== VISUALIZATION_TYPES.PIVOT) {
      return { rowKeys: [], colKeys: [], matrix: {}, metricKey: '', rowDim: '', colDim: '' }
    }
    if (columns.length < 3 || rows.length === 0) {
      return { rowKeys: [], colKeys: [], matrix: {}, metricKey: '', rowDim: '', colDim: '' }
    }

    const transformed = buildChartData(columns, rows)
    const firstRow = transformed[0] || {}
    const numericKeys = Object.keys(firstRow).filter((key) => typeof firstRow[key] === 'number')
    if (numericKeys.length === 0) {
      return { rowKeys: [], colKeys: [], matrix: {}, metricKey: '', rowDim: '', colDim: '' }
    }

    const rowDim = columns[0]
    const colDim = columns[1]
    const metricKey = numericKeys[0]

    const matrix = {}
    const rowSet = new Set()
    const colSet = new Set()

    transformed.forEach((item) => {
      const r = String(item[rowDim] ?? 'N/A')
      const c = String(item[colDim] ?? 'N/A')
      const v = Number(item[metricKey] ?? 0)
      rowSet.add(r)
      colSet.add(c)
      if (!matrix[r]) matrix[r] = {}
      matrix[r][c] = (matrix[r][c] ?? 0) + (Number.isFinite(v) ? v : 0)
    })

    return {
      rowKeys: Array.from(rowSet),
      colKeys: Array.from(colSet),
      matrix,
      metricKey,
      rowDim,
      colDim,
    }
  }, [columns, rows, selectedView])

  function getTypedKeysFromRow(rowObj) {
    const keys = Object.keys(rowObj || {})
    const numericKeys = keys.filter((k) => typeof rowObj[k] === 'number' && Number.isFinite(rowObj[k]))
    const textKeys = keys.filter((k) => typeof rowObj[k] !== 'number')
    return { keys, numericKeys, textKeys }
  }

  function quantile(sortedValues, q) {
    const pos = (sortedValues.length - 1) * q
    const base = Math.floor(pos)
    const rest = pos - base
    if (sortedValues[base + 1] !== undefined) {
      return sortedValues[base] + rest * (sortedValues[base + 1] - sortedValues[base])
    }
    return sortedValues[base]
  }

  const echartsOption = useMemo(() => {
    const transformed = buildChartData(columns, rows)
    const first = transformed[0] || {}
    const { keys, numericKeys, textKeys } = getTypedKeysFromRow(first)

    if (selectedView === VISUALIZATION_TYPES.WATERFALL) {
      if (keys.length < 2) return null
      const labelKey = textKeys[0] || keys[0]
      const valueKey = numericKeys[0]
      if (!valueKey) return null

      const labels = transformed.map((r) => String(r[labelKey]))
      const values = transformed.map((r) => Number(r[valueKey] ?? 0))
      if (labels.length === 0) return null

      const assist = []
      let sum = 0
      values.forEach((v) => {
        assist.push(sum)
        sum += v
      })

      const finalTotal = sum
      const labelsWithTotal = [...labels, 'Toplam']
      const assistWithTotal = [...assist, 0]
      const valuesWithTotal = [...values, finalTotal]

      return {
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: 40, right: 20, bottom: 40, top: 20 },
        xAxis: { type: 'category', data: labelsWithTotal, axisLabel: { rotate: 20 } },
        yAxis: { type: 'value' },
        series: [
          {
            name: 'Assist',
            type: 'bar',
            stack: 'Total',
            itemStyle: { borderColor: 'transparent', color: 'transparent' },
            emphasis: { itemStyle: { borderColor: 'transparent', color: 'transparent' } },
            data: assistWithTotal,
          },
          {
            name: valueKey,
            type: 'bar',
            stack: 'Total',
            itemStyle: {
              color: (params) => (params.name === 'Toplam' ? '#f05a28' : '#007b70'),
            },
            data: valuesWithTotal,
          },
        ],
      }
    }

    if (selectedView === VISUALIZATION_TYPES.BOX_PLOT) {
      if (keys.length < 2) return null
      const categoryKey = textKeys[0] || keys[0]
      const valueKey = numericKeys[0]
      if (!valueKey) return null

      const groups = new Map()
      transformed.forEach((r) => {
        const c = String(r[categoryKey] ?? 'N/A')
        const v = Number(r[valueKey])
        if (!Number.isFinite(v)) return
        if (!groups.has(c)) groups.set(c, [])
        groups.get(c).push(v)
      })

      const categories = Array.from(groups.keys())
      const data = categories.map((c) => {
        const arr = groups.get(c).slice().sort((a, b) => a - b)
        const min = arr[0]
        const max = arr[arr.length - 1]
        const q1 = quantile(arr, 0.25)
        const med = quantile(arr, 0.5)
        const q3 = quantile(arr, 0.75)
        return [min, q1, med, q3, max]
      })

      if (!categories.length) return null

      return {
        tooltip: { trigger: 'item' },
        grid: { left: 40, right: 20, bottom: 70, top: 20 },
        xAxis: { type: 'category', data: categories, axisLabel: { rotate: 20 } },
        yAxis: { type: 'value' },
        series: [{ type: 'boxplot', name: valueKey, data }],
      }
    }

    if (selectedView === VISUALIZATION_TYPES.SANKEY) {
      if (keys.length < 3) return null
      if (textKeys.length < 2 || numericKeys.length < 1) return null

      const [sourceKey, targetKey] = textKeys
      const valueKey = numericKeys[0]

      const nodeSet = new Set()
      const links = []
      transformed.forEach((r) => {
        const s = String(r[sourceKey] ?? '')
        const t = String(r[targetKey] ?? '')
        const v = Number(r[valueKey] ?? 0)
        if (!s || !t || !Number.isFinite(v)) return
        nodeSet.add(s)
        nodeSet.add(t)
        links.push({ source: s, target: t, value: v })
      })

      const nodes = Array.from(nodeSet).map((name) => ({ name }))
      if (!nodes.length || !links.length) return null

      return {
        tooltip: { trigger: 'item', triggerOn: 'mousemove' },
        series: [
          {
            type: 'sankey',
            data: nodes,
            links,
            emphasis: { focus: 'adjacency' },
            lineStyle: { color: 'gradient', curveness: 0.5 },
            itemStyle: { borderWidth: 0 },
          },
        ],
      }
    }

    if (selectedView === VISUALIZATION_TYPES.MAP) {
      return null
    }

    return null
  }, [columns, rows, selectedView])

  const trendSummary = useMemo(() => {
    if (selectedView !== VISUALIZATION_TYPES.TREND) return null
    if (!chartData.length) return null

    const numericKey = Object.keys(chartData[0] || {}).find(
      (key) => typeof chartData[0][key] === 'number',
    )
    if (!numericKey) return null

    const first = Number(chartData[0][numericKey])
    const last = Number(chartData[chartData.length - 1][numericKey])
    if (!Number.isFinite(first) || !Number.isFinite(last)) return null

    const delta = last - first
    const direction = delta > 0 ? 'yukarı' : delta < 0 ? 'aşağı' : 'stabil'
    const percent = first !== 0 ? (delta / first) * 100 : null
    return { numericKey, delta, direction, percent }
  }, [chartData, selectedView])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function fetchCurrentUser(accessToken) {
    const res = await fetch(AUTH_ME_URL, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${accessToken}`,
        Accept: 'application/json',
      },
    })

    if (!res.ok) {
      throw new Error('Kullanıcı bilgisi alınamadı.')
    }

    return res.json()
  }

  useEffect(() => {
    async function bootstrapAuth() {
      if (!token) return

      setAuthLoading(true)
      try {
        const me = await fetchCurrentUser(token)
        setCurrentUser(me)
        setRole((me.role_codes && me.role_codes[0]) || 'guest')
        setUsername(me.username || '')
      } catch {
        localStorage.removeItem('access_token')
        setToken('')
        setCurrentUser(null)
      } finally {
        setAuthLoading(false)
      }
    }

    bootstrapAuth()
  }, [token])

  async function handleLogin(e) {
    e.preventDefault()

    const uname = loginUsername.trim()
    const pass = loginPassword.trim()

    if (!uname || !pass) {
      setLoginError('Kullanıcı adı ve şifre zorunlu.')
      return
    }

    setAuthLoading(true)
    setLoginError('')

    try {
      const res = await fetch(AUTH_LOGIN_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({
          username: uname,
          password: pass,
        }),
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || 'Giriş başarısız.')
      }

      const accessToken = data.access_token
      localStorage.setItem('access_token', accessToken)
      setToken(accessToken)

      const me = await fetchCurrentUser(accessToken)
      setCurrentUser(me)

      setRole((me.role_codes && me.role_codes[0]) || 'guest')
      setUsername(me.username || '')
      setCountry('')
      setRegion('')
      setDepartment('')
      setLoginPassword('')
    } catch (err) {
      setLoginError(err.message || 'Giriş başarısız.')
    } finally {
      setAuthLoading(false)
    }
  }

  function handleLogout() {
    localStorage.removeItem('access_token')
    setToken('')
    setCurrentUser(null)
    setLoginUsername('')
    setLoginPassword('')
    setLoginError('')
    setMessages([])
    setSql('')
    setColumns([])
    setRows([])
    setRowCount(0)
    setTruncated(false)
    setError('')
    setQuestion('')
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const q = question.trim()
    if (!q) return

    if (!currentUser) {
      setError('Oturum bulunamadı. Lütfen tekrar giriş yapın.')
      return
    }

    setError('')
    setSql('')
    setColumns([])
    setRows([])
    setRowCount(0)
    setTruncated(false)
    setSelectedView(VISUALIZATION_TYPES.TABLE)
    setLoading(true)

    setMessages((prev) => [
      ...prev,
      { id: nextId(), role: 'user', content: q },
    ])

    try {
      const res = await fetch(`${API_BASE}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-UI-Locale': uiLocale,
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          question: q,
          user_id: currentUser.user_id,
          username: currentUser.username,
          active_company_id: currentUser.active_company_id,
          role_codes: currentUser.role_codes || [],
          permission_codes: currentUser.permission_codes || [],
          company_ids: currentUser.company_ids || [],
          country_ids: currentUser.country_ids || [],
          region_ids: currentUser.region_ids || [],
          branch_ids: currentUser.branch_ids || [],
          department_ids: currentUser.department_ids || [],
          team_ids: currentUser.team_ids || [],
          customer_ids: currentUser.customer_ids || [],
          is_superadmin: Boolean(currentUser.is_superadmin),
          limit: limit === 'all' ? 0 : limit,
        }),
      })

      const data = await res.json()

      if (data.error) {
        setError(data.error)
        setSql(data.sql || '')
        setColumns([])
        setRows([])
        setRowCount(0)
        setTruncated(false)
        setSelectedView(VISUALIZATION_TYPES.TABLE)
        setMessages((prev) => [
          ...prev,
          {
            id: nextId(),
            role: 'assistant',
            error: data.error,
            answerText: data.answer_text || '',
            bullets: data.answer_bullets || [],
          },
        ])
      } else {
        const nextColumns = data.columns || []
        const nextRows = data.rows || []
        const nextVisualizationInfo = analyzeVisualizationOptions(nextColumns, nextRows)

        setSql(data.sql || '')
        setColumns(nextColumns)
        setRows(nextRows)
        setRowCount(data.row_count || 0)
        setTruncated(Boolean(data.truncated))
        setSelectedView(nextVisualizationInfo.defaultVisualization)
        setMessages((prev) => [
          ...prev,
          {
            id: nextId(),
            role: 'assistant',
            error: null,
            answerText: data.answer_text || '',
            bullets: data.answer_bullets || [],
          },
        ])
      }
    } catch (err) {
      const msg = err.message || 'Bağlantı hatası. Backend çalışıyor mu?'
      setError(msg)
      setSql('')
      setColumns([])
      setRows([])
      setRowCount(0)
      setTruncated(false)
      setSelectedView(VISUALIZATION_TYPES.TABLE)
      setMessages((prev) => [
        ...prev,
        {
          id: nextId(),
          role: 'assistant',
          error: msg,
          answerText: '',
          bullets: [],
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const {
    availableVisualizations,
    defaultVisualization,
    columnTypes,
  } = visualizationInfo

  const xAxisKey = chartData.length > 0 ? Object.keys(chartData[0])[0] : 'label'
  const dataKey = chartData.length > 0 ? Object.keys(chartData[0])[1] : 'value'
  const numericSeriesKeys = chartData.length
    ? Object.keys(chartData[0]).filter((key) => typeof chartData[0][key] === 'number')
    : []
  const comboLineKey = numericSeriesKeys[0] || dataKey
  const comboBarKey = numericSeriesKeys[1] || dataKey
  const kpiLabel = columns[0] || 'Değer'

  const hasResultCanvas = Boolean(sql && !error && rows.length > 0)
  const showEmptyResult = Boolean(sql && !error && rows.length === 0)

  const isAdminUser =
    Boolean(currentUser?.is_superadmin) ||
    (Array.isArray(currentUser?.role_codes) &&
      currentUser.role_codes.some((r) => String(r).toLowerCase() === 'admin'))

  if (authLoading && !currentUser) {
    return (
      <div className="app">
        <div className="card" style={{ maxWidth: 420, margin: '4rem auto' }}>
          <div className="card-label">Oturum</div>
          <p>Yükleniyor...</p>
        </div>
      </div>
    )
  }

  if (!currentUser) {
    return (
      <div className="app">
        <div className="card" style={{ maxWidth: 420, margin: '4rem auto' }}>
          <div className="card-label">Giriş Yap</div>

          <form onSubmit={handleLogin} className="form">
            <div className="field-group">
              <label className="role-label" htmlFor="login-username">
                Kullanıcı Adı
              </label>
              <input
                id="login-username"
                type="text"
                className="input"
                value={loginUsername}
                onChange={(e) => setLoginUsername(e.target.value)}
                placeholder="Örn: manager_demo"
                disabled={authLoading}
              />
            </div>

            <div className="field-group">
              <label className="role-label" htmlFor="login-password">
                Şifre
              </label>
              <input
                id="login-password"
                type="password"
                className="input"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                placeholder="Şifrenizi girin"
                disabled={authLoading}
              />
            </div>

            {loginError && (
              <div className="viz-error-banner" role="alert">
                {loginError}
              </div>
            )}

            <button type="submit" className="btn" disabled={authLoading}>
              {authLoading ? 'Giriş yapılıyor...' : 'Giriş Yap'}
            </button>
          </form>

          <div style={{ marginTop: '1rem', fontSize: '0.85rem', color: '#6b7280' }}>
            Demo kullanıcılar:
            <br />
            manager_demo / demo_manager_123
            <br />
            guest_demo / demo_guest_123
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-row">
          <div className="header-titles">
            <h1>{t('appTitle')}</h1>
            <p className="subtitle">{t('appSubtitle')}</p>
          </div>

          <div className="header-actions">
            <div className="locale-picker" ref={localeRef}>
              <button
                type="button"
                className="locale-button"
                onClick={() => setIsLocaleOpen((v) => !v)}
                aria-haspopup="menu"
                aria-expanded={isLocaleOpen}
                title={t('language')}
              >
                <span className="locale-icon" aria-hidden>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <circle cx="12" cy="12" r="10" />
                    <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                  </svg>
                </span>
                <span className="locale-code">{uiLocale.toUpperCase()}</span>
              </button>

              {isLocaleOpen && (
                <div className="locale-menu" role="menu" aria-label={t('language')}>
                  {UI_LOCALES.map((code) => (
                    <button
                      key={code}
                      type="button"
                      role="menuitemradio"
                      aria-checked={uiLocale === code}
                      className={`locale-item ${uiLocale === code ? 'active' : ''}`}
                      onClick={() => {
                        setUiLocale(code)
                        setIsLocaleOpen(false)
                      }}
                    >
                      {LOCALE_LABELS[code] || code.toUpperCase()}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div className="lang-switcher" aria-label="Kullanıcı menüsü">
              <button
                type="button"
                className="lang-button"
                title="Kullanıcı menüsü"
                aria-haspopup="true"
                aria-expanded="false"
              >
                👤{' '}
                <span className="lang-button-text">
                  {currentUser?.username || 'Kullanıcı'}
                </span>
              </button>

              <div className="lang-menu" role="menu" aria-label="Kullanıcı seçenekleri">
                <button type="button" className="lang-item" disabled>
                  Rol: {(currentUser?.role_codes || []).join(', ') || '—'}
                </button>

                <button type="button" className="lang-item" disabled>
                  Company: {currentUser?.active_company_id ?? '—'}
                </button>

                {isAdminUser && (
                  <button
                    type="button"
                    className="lang-item lang-item-action"
                    onClick={() => (window.location.href = '/admin')}
                  >
                    Admin Panel
                  </button>
                )}

                <button type="button" className="lang-item lang-item-action" onClick={handleLogout}>
                  Çıkış Yap
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <section className="top-filters" aria-label={t('filters')}>
        <div className="filter-item">
          <label htmlFor="role-select" className="role-label">
            {t('role')}
          </label>
          <select
            id="role-select"
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="role-select full-width"
            disabled
          >
            {ROLES.map((r) => (
              <option key={r.value} value={r.value}>
                {r.label}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-item">
          <label htmlFor="limit-select" className="role-label">
            {t('limit')}
          </label>
          <select
            id="limit-select"
            value={limit}
            onChange={(e) =>
              setLimit(e.target.value === 'all' ? 'all' : Number(e.target.value))
            }
            className="role-select full-width"
            disabled={loading}
          >
            {LIMIT_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option === 'all' ? t('all') : `${option} ${t('rows')}`}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-item">
          <label htmlFor="username-input" className="role-label">
            {t('username')}
          </label>
          <input
            id="username-input"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Örn: ALFKI"
            className="input compact-input"
            disabled
          />
        </div>

        <div className="filter-item">
          <label htmlFor="country-input" className="role-label">{t('country')}</label>
          <input
            id="country-input"
            type="text"
            value={country}
            onChange={(e) => setCountry(e.target.value)}
            placeholder="Germany"
            className="input compact-input"
            disabled
          />
        </div>

        <div className="filter-item">
          <label htmlFor="region-input" className="role-label">{t('region')}</label>
          <input
            id="region-input"
            type="text"
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            className="input compact-input"
            disabled
          />
        </div>

        <div className="filter-item">
          <label htmlFor="department-input" className="role-label">{t('department')}</label>
          <input
            id="department-input"
            type="text"
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
            className="input compact-input"
            disabled
          />
        </div>
      </section>

      <div className="workspace">
        <aside className="chart-sidebar" aria-label={t('viewTitle')}>
          <div className="sidebar-title">{t('viewTitle')}</div>
          <p className="sidebar-hint">{t('viewHint')}</p>
          <div className="chart-grid">
            {CHART_PALETTE.map((item) => {
              const allowed =
                sql && !error && availableVisualizations.includes(item.type)
              const active = selectedView === item.type && allowed
              return (
                <button
                  key={item.type}
                  type="button"
                  className={`chart-tile ${active ? 'active' : ''}`}
                  disabled={!allowed}
                  onClick={() => setSelectedView(item.type)}
                  title={t(item.hintKey)}
                >
                  <span className="chart-tile-icon" aria-hidden>{item.icon}</span>
                  <span className="chart-tile-label">{t(item.labelKey)}</span>
                  <span className="chart-tile-hint">{t(item.hintKey)}</span>
                </button>
              )
            })}
          </div>
          {sql && !error && (
            <div className="sidebar-meta">
              <div>
                Önerilen:{' '}
                <strong>{VIEW_LABELS[defaultVisualization]}</strong>
              </div>
              <div className="sidebar-meta-muted">
                Tipler: {columnTypes.join(', ') || '—'}
              </div>
            </div>
          )}
        </aside>

        <main className="viz-main">
          {error && (
            <div className="viz-error-banner" role="alert">
              {error}
            </div>
          )}

          {!sql && !loading && <p className="viz-placeholder">{t('vizPlaceholder')}</p>}

          {loading && (
            <div className="viz-loading">
              <span className="viz-loading-spinner" aria-hidden />
              Sorgu çalıştırılıyor…
            </div>
          )}

          {showEmptyResult && (
            <p className="viz-placeholder">
              Sorgu tamamlandı; koşullara uyan satır yok. Detay için sağdaki özeti
              okuyun.
            </p>
          )}

          {hasResultCanvas && (
            <>
              <div className="viz-toolbar">
                <span>
                  {rowCount} satır
                  {truncated ? ' (kısaltılmış)' : ''}
                </span>
                {sql && !error && (
                  <span className="viz-toolbar-meta">
                    Uygun chartlar: {availableVisualizations.map((v) => VIEW_LABELS[v] || v).join(', ')}
                  </span>
                )}
              </div>

              {selectedView === VISUALIZATION_TYPES.BAR && (
                <div className="chart-placeholder">
                  {chartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={380}>
                      <BarChart
                        data={chartData}
                        margin={{ top: 20, right: 24, left: 12, bottom: 72 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                          dataKey={xAxisKey}
                          interval={Math.max(0, Math.floor(chartData.length / 8))}
                          angle={-18}
                          textAnchor="end"
                          height={80}
                          tickFormatter={(value) => truncateLabel(value, 12)}
                          tick={{ fontSize: 12 }}
                        />
                        <YAxis
                          width={90}
                          tickFormatter={(value) => formatNumber(value)}
                          tick={{ fontSize: 12 }}
                        />
                        <Tooltip
                          formatter={(value, name) => [formatNumber(value), name]}
                          labelFormatter={(label) => String(label)}
                        />
                        <Bar
                          dataKey={dataKey}
                          radius={[6, 6, 0, 0]}
                          fill="#007b70"
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <p>Bu veri seti için bar grafik uygun değil.</p>
                  )}
                </div>
              )}

              {selectedView === VISUALIZATION_TYPES.LINE && (
                <div className="chart-placeholder">
                  {chartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={380}>
                      <LineChart
                        data={chartData}
                        margin={{ top: 20, right: 24, left: 12, bottom: 48 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                          dataKey={xAxisKey}
                          interval={Math.max(0, Math.floor(chartData.length / 8))}
                          tickFormatter={(value) => truncateLabel(value, 12)}
                          minTickGap={20}
                          tick={{ fontSize: 12 }}
                        />
                        <YAxis
                          width={90}
                          tickFormatter={(value) => formatNumber(value)}
                          tick={{ fontSize: 12 }}
                        />
                        <Tooltip
                          formatter={(value, name) => [formatNumber(value), name]}
                          labelFormatter={(label) => String(label)}
                        />
                        <Line
                          type="monotone"
                          dataKey={dataKey}
                          dot={{ r: 4, fill: '#007b70' }}
                          activeDot={{ r: 6 }}
                          stroke="#007b70"
                          strokeWidth={2}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  ) : (
                    <p>Bu veri seti için çizgi grafik uygun değil.</p>
                  )}
                </div>
              )}

              {selectedView === VISUALIZATION_TYPES.AREA && (
                <div className="chart-placeholder">
                  {chartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={380}>
                      <AreaChart
                        data={chartData}
                        margin={{ top: 20, right: 24, left: 12, bottom: 48 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                          dataKey={xAxisKey}
                          interval={Math.max(0, Math.floor(chartData.length / 8))}
                          tickFormatter={(value) => truncateLabel(value, 12)}
                          minTickGap={20}
                          tick={{ fontSize: 12 }}
                        />
                        <YAxis
                          width={90}
                          tickFormatter={(value) => formatNumber(value)}
                          tick={{ fontSize: 12 }}
                        />
                        <Tooltip
                          formatter={(value, name) => [formatNumber(value), name]}
                          labelFormatter={(label) => String(label)}
                        />
                        <Area
                          type="monotone"
                          dataKey={dataKey}
                          stroke="#007b70"
                          fill="#99f6e4"
                          fillOpacity={0.45}
                          strokeWidth={2}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  ) : (
                    <p>Bu veri seti için area chart uygun değil.</p>
                  )}
                </div>
              )}

              {selectedView === VISUALIZATION_TYPES.PIE && (
                <div className="chart-placeholder">
                  {pieData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={380}>
                      <PieChart>
                        <Tooltip formatter={(value) => formatNumber(value)} />
                        <Legend />
                        <Pie
                          data={pieData}
                          dataKey="value"
                          nameKey="name"
                          outerRadius={130}
                          label={(entry) => truncateLabel(entry.name, 14)}
                        >
                          {pieData.map((entry, index) => (
                            <Cell
                              key={`${entry.name}-${index}`}
                              fill={PIE_COLORS[index % PIE_COLORS.length]}
                            />
                          ))}
                        </Pie>
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <p>Bu veri seti için pie chart uygun değil.</p>
                  )}
                </div>
              )}

              {selectedView === VISUALIZATION_TYPES.SCATTER && (
                <div className="chart-placeholder">
                  {scatterConfig.data.length > 0 ? (
                    <ResponsiveContainer width="100%" height={380}>
                      <ScatterChart margin={{ top: 20, right: 24, left: 12, bottom: 32 }}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                          dataKey={scatterConfig.xKey}
                          type="number"
                          tick={{ fontSize: 12 }}
                          tickFormatter={(value) => formatNumber(value)}
                        />
                        <YAxis
                          dataKey={scatterConfig.yKey}
                          type="number"
                          tick={{ fontSize: 12 }}
                          tickFormatter={(value) => formatNumber(value)}
                        />
                        <Tooltip formatter={(value) => formatNumber(value)} />
                        <Scatter data={scatterConfig.data} fill="#007b70" />
                      </ScatterChart>
                    </ResponsiveContainer>
                  ) : (
                    <p>Bu veri seti için scatter chart uygun değil.</p>
                  )}
                </div>
              )}

              {selectedView === VISUALIZATION_TYPES.COMBO && (
                <div className="chart-placeholder">
                  {chartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={380}>
                      <ComposedChart
                        data={chartData}
                        margin={{ top: 20, right: 24, left: 12, bottom: 48 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                          dataKey={xAxisKey}
                          interval={Math.max(0, Math.floor(chartData.length / 8))}
                          tickFormatter={(value) => truncateLabel(value, 12)}
                          minTickGap={20}
                          tick={{ fontSize: 12 }}
                        />
                        <YAxis
                          width={90}
                          tickFormatter={(value) => formatNumber(value)}
                          tick={{ fontSize: 12 }}
                        />
                        <Tooltip
                          formatter={(value, name) => [formatNumber(value), name]}
                          labelFormatter={(label) => String(label)}
                        />
                        <Legend />
                        <Bar dataKey={comboBarKey} fill="#0ea5a0" />
                        <Line
                          type="monotone"
                          dataKey={comboLineKey}
                          stroke="#f05a28"
                          strokeWidth={2}
                          dot={{ r: 3 }}
                        />
                      </ComposedChart>
                    </ResponsiveContainer>
                  ) : (
                    <p>Bu veri seti için combo chart uygun değil.</p>
                  )}
                </div>
              )}

              {selectedView === VISUALIZATION_TYPES.ROW && (
                <div className="chart-placeholder">
                  {chartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={380}>
                      <BarChart
                        data={chartData}
                        layout="vertical"
                        margin={{ top: 20, right: 24, left: 80, bottom: 24 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                          type="number"
                          tickFormatter={(value) => formatNumber(value)}
                          tick={{ fontSize: 12 }}
                        />
                        <YAxis
                          dataKey={xAxisKey}
                          type="category"
                          tickFormatter={(value) => truncateLabel(value, 12)}
                          tick={{ fontSize: 12 }}
                          width={100}
                        />
                        <Tooltip
                          formatter={(value, name) => [formatNumber(value), name]}
                          labelFormatter={(label) => String(label)}
                        />
                        <Bar dataKey={dataKey} fill="#007b70" radius={[0, 6, 6, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <p>Bu veri seti için row chart uygun değil.</p>
                  )}
                </div>
              )}

              {selectedView === VISUALIZATION_TYPES.TREND && (
                <div className="chart-placeholder">
                  {chartData.length > 0 ? (
                    <>
                      <ResponsiveContainer width="100%" height={320}>
                        <LineChart
                          data={chartData}
                          margin={{ top: 20, right: 24, left: 12, bottom: 40 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis
                            dataKey={xAxisKey}
                            tickFormatter={(value) => truncateLabel(value, 12)}
                            tick={{ fontSize: 12 }}
                          />
                          <YAxis
                            tickFormatter={(value) => formatNumber(value)}
                            tick={{ fontSize: 12 }}
                          />
                          <Tooltip
                            formatter={(value, name) => [formatNumber(value), name]}
                            labelFormatter={(label) => String(label)}
                          />
                          <Line type="monotone" dataKey={dataKey} stroke="#007b70" strokeWidth={2} />
                        </LineChart>
                      </ResponsiveContainer>
                      {trendSummary && (
                        <p className="trend-text">
                          Trend {trendSummary.direction}. Delta: {formatNumber(trendSummary.delta)}
                          {trendSummary.percent !== null && ` (${formatNumber(trendSummary.percent)}%)`}.
                        </p>
                      )}
                    </>
                  ) : (
                    <p>Bu veri seti için trend chart uygun değil.</p>
                  )}
                </div>
              )}

              {selectedView === VISUALIZATION_TYPES.PROGRESS && (
                <div className="chart-placeholder">
                  {progressValue !== null ? (
                    <ResponsiveContainer width="100%" height={320}>
                      <RadialBarChart
                        cx="50%"
                        cy="50%"
                        innerRadius="60%"
                        outerRadius="90%"
                        barSize={18}
                        data={[{ name: 'Progress', value: progressValue, fill: '#007b70' }]}
                        startAngle={90}
                        endAngle={-270}
                      >
                        <RadialBar minAngle={15} background clockWise dataKey="value" />
                        <text
                          x="50%"
                          y="50%"
                          textAnchor="middle"
                          dominantBaseline="middle"
                          className="progress-text"
                        >
                          {`${Math.round(progressValue)}%`}
                        </text>
                      </RadialBarChart>
                    </ResponsiveContainer>
                  ) : (
                    <p>Progress için tek sayısal değer bekleniyor (0-100).</p>
                  )}
                </div>
              )}

              {selectedView === VISUALIZATION_TYPES.FUNNEL && (
                <div className="chart-placeholder">
                  {funnelData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={360}>
                      <FunnelChart>
                        <Tooltip formatter={(value) => formatNumber(value)} />
                        <Funnel
                          dataKey="value"
                          data={funnelData}
                          isAnimationActive
                          fill="#007b70"
                        >
                          <LabelList position="right" fill="#5a6d6a" stroke="none" dataKey="name" />
                        </Funnel>
                      </FunnelChart>
                    </ResponsiveContainer>
                  ) : (
                    <p>Funnel için kategori + numeric sonuç gerekiyor.</p>
                  )}
                </div>
              )}

              {selectedView === VISUALIZATION_TYPES.GAUGE && (
                <div className="chart-placeholder">
                  {gaugeValue !== null ? (
                    <ResponsiveContainer width="100%" height={320}>
                      <RadialBarChart
                        cx="50%"
                        cy="50%"
                        innerRadius="58%"
                        outerRadius="90%"
                        barSize={18}
                        data={[{ name: 'Gauge', value: gaugeValue, fill: '#f05a28' }]}
                        startAngle={180}
                        endAngle={0}
                      >
                        <RadialBar minAngle={15} background clockWise dataKey="value" />
                        <text
                          x="50%"
                          y="58%"
                          textAnchor="middle"
                          dominantBaseline="middle"
                          className="progress-text"
                        >
                          {`${Math.round(gaugeValue)}%`}
                        </text>
                      </RadialBarChart>
                    </ResponsiveContainer>
                  ) : (
                    <p>Gauge için tek sayısal değer bekleniyor (0-100).</p>
                  )}
                </div>
              )}

              {selectedView === VISUALIZATION_TYPES.DETAIL && (
                <div className="chart-placeholder">
                  {detailRows.length > 0 ? (
                    <div className="detail-grid">
                      {detailRows.map((row, rowIndex) => (
                        <div key={rowIndex} className="detail-card">
                          {columns.map((col, colIndex) => (
                            <div key={`${rowIndex}-${col}`} className="detail-item">
                              <span className="detail-key">{col}</span>
                              <span className="detail-value">
                                {row[colIndex] === null ? 'NULL' : String(row[colIndex])}
                              </span>
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p>Detail görünümü için sonuç satırı yok.</p>
                  )}
                </div>
              )}

              {selectedView === VISUALIZATION_TYPES.PIVOT && (
                <div className="chart-placeholder">
                  {pivotModel.rowKeys.length > 0 && pivotModel.colKeys.length > 0 ? (
                    <>
                      <div className="pivot-meta">
                        Satır: <strong>{pivotModel.rowDim}</strong> | Kolon: <strong>{pivotModel.colDim}</strong> | Metric:{' '}
                        <strong>{pivotModel.metricKey}</strong>
                      </div>
                      <div className="table-wrap">
                        <table className="result-table">
                          <thead>
                            <tr>
                              <th>{pivotModel.rowDim}</th>
                              {pivotModel.colKeys.map((colKey) => (
                                <th key={colKey}>{colKey}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {pivotModel.rowKeys.map((rowKey) => (
                              <tr key={rowKey}>
                                <td>{rowKey}</td>
                                {pivotModel.colKeys.map((colKey) => (
                                  <td key={`${rowKey}-${colKey}`}>
                                    {formatNumber(pivotModel.matrix[rowKey]?.[colKey] ?? 0)}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </>
                  ) : (
                    <p>Pivot için en az 2 boyut + 1 sayısal kolon gerekiyor.</p>
                  )}
                </div>
              )}

              {(selectedView === VISUALIZATION_TYPES.WATERFALL ||
                selectedView === VISUALIZATION_TYPES.BOX_PLOT ||
                selectedView === VISUALIZATION_TYPES.SANKEY ||
                selectedView === VISUALIZATION_TYPES.MAP) && (
                  <div className="chart-placeholder">
                    {echartsOption ? (
                      <EChart option={echartsOption} height={selectedView === VISUALIZATION_TYPES.MAP ? 420 : 380} />
                    ) : (
                      <p>Bu veri seti bu görselleştirme için uygun değil.</p>
                    )}
                  </div>
                )}

              {selectedView === VISUALIZATION_TYPES.KPI && (
                <div className="chart-placeholder kpi-wrap">
                  <span className="kpi-label">{kpiLabel}</span>
                  <strong className="kpi-value">
                    {typeof kpiValue === 'number'
                      ? formatNumber(kpiValue)
                      : String(kpiValue ?? '-')}
                  </strong>
                </div>
              )}

              {selectedView === VISUALIZATION_TYPES.TABLE && (
                <div className="table-wrap">
                  <table className="result-table">
                    <thead>
                      <tr>
                        {columns.map((col) => (
                          <th key={col}>{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map((row, rowIndex) => (
                        <tr key={rowIndex}>
                          {row.map((cell, cellIndex) => (
                            <td key={`${rowIndex}-${cellIndex}`}>
                              {cell === null ? 'NULL' : String(cell)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}

          {sql && (
            <details className="sql-details">
              <summary>Üretilen SQL</summary>
              <pre className="sql-block">{sql}</pre>
            </details>
          )}
        </main>

        <aside className="chat-sidebar" aria-label="Sohbet">
          <div className="chat-log">
            {messages.length === 0 && !loading && (
              <p className="chat-empty">
                {t('emptyChat')}
              </p>
            )}

            {messages.map((m) =>
              m.role === 'user' ? (
                <div key={m.id} className="bubble bubble-user">
                  <div className="bubble-label">{t('you')}</div>
                  <div className="bubble-body">{m.content}</div>
                </div>
              ) : (
                <div key={m.id} className="bubble bubble-assistant">
                  <div className="bubble-label">{t('assistant')}</div>
                  {m.error ? (
                    <div className="bubble-error">{m.error}</div>
                  ) : (
                    <>
                      {m.answerText && (
                        <div className="bubble-body">{m.answerText}</div>
                      )}
                      {Array.isArray(m.bullets) && m.bullets.length > 0 && (
                        <ul className="bubble-bullets">
                          {m.bullets.map((b, i) => (
                            <li key={i}>{b}</li>
                          ))}
                        </ul>
                      )}
                    </>
                  )}
                </div>
              ),
            )}

            {loading && (
              <div className="bubble bubble-assistant bubble-pending">
                <div className="bubble-label">{t('assistant')}</div>
                <div className="bubble-body muted">{t('pending')}</div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          <form onSubmit={handleSubmit} className="chat-form">
            <div className="chat-input-row">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder={t('questionPlaceholder')}
                className="input chat-question-input"
                disabled={loading}
              />
              <button type="submit" className="btn" disabled={loading}>
                {loading ? '…' : t('send')}
              </button>
            </div>
          </form>
        </aside>
      </div>
    </div>
  )
}
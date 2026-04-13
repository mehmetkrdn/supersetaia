/* columns + rows al
→ veri yapısını analiz et
→ uygun view seçeneklerini çıkar
→ default view seç
*/

const TABLE = 'table'
const BAR = 'bar'
const LINE = 'line'
const KPI = 'kpi'
const PIE = 'pie'
const AREA = 'area'
const SCATTER = 'scatter'
const COMBO = 'combo'
const TREND = 'trend'
const PROGRESS = 'progress'
const ROW = 'row'
const FUNNEL = 'funnel'
const GAUGE = 'gauge'
const DETAIL = 'detail'
const PIVOT = 'pivot'
const WATERFALL = 'waterfall'
const BOX_PLOT = 'box_plot'
const SANKEY = 'sankey'
const MAP = 'map'

function isNumericValue(value) {
    if (value === null || value === undefined) return false
    if (typeof value === 'number') return Number.isFinite(value)

    if (typeof value === 'string') {
        const normalized = value.trim().replace(',', '.')
        if (!normalized) return false
        return !Number.isNaN(Number(normalized))
    }

    return false
}

function isDateLikeValue(value) {
    if (value === null || value === undefined) return false
    if (value instanceof Date) return true

    if (typeof value !== 'string') return false

    const trimmed = value.trim()
    if (!trimmed) return false

    const datePattern =
        /^\d{4}-\d{2}-\d{2}$|^\d{4}-\d{2}$|^\d{4}\/\d{2}\/\d{2}$|^\d{2}\.\d{2}\.\d{4}$/

    if (datePattern.test(trimmed)) return true

    const parsed = Date.parse(trimmed)
    return !Number.isNaN(parsed)
}

function getColumnValues(rows, columnIndex) {
    return rows
        .map((row) => row?.[columnIndex])
        .filter((value) => value !== null && value !== undefined && value !== '')
}

function detectColumnType(columnName, values) {
    const loweredName = String(columnName || '').toLowerCase()

    const dateHints = ['date', 'day', 'month', 'year', 'time']
    const hasDateHint = dateHints.some((hint) => loweredName.includes(hint))

    if (values.length === 0) {
        if (hasDateHint) return 'date'
        return 'text'
    }

    const numericCount = values.filter(isNumericValue).length
    const dateCount = values.filter(isDateLikeValue).length

    const numericRatio = numericCount / values.length
    const dateRatio = dateCount / values.length

    if (hasDateHint && dateRatio >= 0.5) return 'date'
    if (dateRatio >= 0.8) return 'date'
    if (numericRatio >= 0.8) return 'numeric'

    return 'text'
}

export function analyzeVisualizationOptions(columns = [], rows = []) {
    const safeColumns = Array.isArray(columns) ? columns : []
    const safeRows = Array.isArray(rows) ? rows : []

    const availableVisualizations = [TABLE]

    if (safeColumns.length === 0 || safeRows.length === 0) {
        return {
            availableVisualizations,
            defaultVisualization: TABLE,
            columnTypes: [],
        }
    }

    availableVisualizations.push(DETAIL)

    const columnTypes = safeColumns.map((columnName, index) => {
        const values = getColumnValues(safeRows, index)
        return detectColumnType(columnName, values)
    })

    if (
        safeColumns.length === 1 &&
        safeRows.length === 1 &&
        columnTypes[0] === 'numeric'
    ) {
        availableVisualizations.unshift(KPI, PROGRESS, GAUGE)

        return {
            availableVisualizations,
            defaultVisualization: KPI,
            columnTypes,
        }
    }

    if (safeColumns.length === 2) {
        const firstType = columnTypes[0]
        const secondType = columnTypes[1]

        if (firstType === 'date' && secondType === 'numeric') {
            availableVisualizations.push(LINE, AREA, TREND, BAR)
            return {
                availableVisualizations,
                defaultVisualization: LINE,
                columnTypes,
            }
        }

        if (firstType === 'text' && secondType === 'numeric') {
            availableVisualizations.push(BAR, ROW, PIE, FUNNEL, WATERFALL, BOX_PLOT)
            return {
                availableVisualizations,
                defaultVisualization: BAR,
                columnTypes,
            }
        }
    }

    if (safeColumns.length >= 3) {
        const firstType = columnTypes[0]
        const numericCount = columnTypes.filter((type) => type === 'numeric').length

        if ((firstType === 'text' || firstType === 'date') && numericCount >= 2) {
            availableVisualizations.push(BAR, LINE, AREA, COMBO)
            return {
                availableVisualizations,
                defaultVisualization: COMBO,
                columnTypes,
            }
        }
    }

    if (safeColumns.length >= 2) {
        const numericIndices = columnTypes
            .map((type, index) => ({ type, index }))
            .filter((item) => item.type === 'numeric')

        if (numericIndices.length >= 2) {
            availableVisualizations.push(SCATTER)
        }
    }

    if (safeColumns.length >= 3 && columnTypes.filter((type) => type === 'numeric').length >= 1) {
        availableVisualizations.push(PIVOT)
    }

    // Sankey: source, target, value
    if (safeColumns.length >= 3) {
        const numericCount = columnTypes.filter((t) => t === 'numeric').length
        const textCount = columnTypes.filter((t) => t === 'text').length
        if (numericCount >= 1 && textCount >= 2) {
            availableVisualizations.push(SANKEY)
        }
    }

    // Map: sonraki faz (ECharts geo bundle / geojson gerektiriyor)

    // Box plot: kategori (text) + numeric dağılım (en az birkaç satır)
    // Ek kolonlar olabilir; ilk uygun text+numeric ikilisine göre çalıştırılır.
    if (
        safeColumns.length >= 2 &&
        columnTypes.includes('text') &&
        columnTypes.includes('numeric') &&
        safeRows.length >= 5
    ) {
        availableVisualizations.push(BOX_PLOT)
    }

    return {
        availableVisualizations: Array.from(new Set(availableVisualizations)),
        defaultVisualization: TABLE,
        columnTypes,
    }
}

export function buildChartData(columns = [], rows = []) {
    if (!Array.isArray(columns) || !Array.isArray(rows)) return []

    return rows.map((row) => {
        const item = {}

        columns.forEach((columnName, index) => {
            const rawValue = row?.[index]

            if (isNumericValue(rawValue)) {
                item[columnName] = Number(String(rawValue).replace(',', '.'))
            } else {
                item[columnName] = rawValue
            }
        })

        return item
    })
}

export const VISUALIZATION_TYPES = {
    TABLE,
    BAR,
    LINE,
    KPI,
    PIE,
    AREA,
    SCATTER,
    COMBO,
    TREND,
    PROGRESS,
    ROW,
    FUNNEL,
    GAUGE,
    DETAIL,
    PIVOT,
    WATERFALL,
    BOX_PLOT,
    SANKEY,
    MAP,
}
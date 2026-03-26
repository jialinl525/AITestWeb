// ── Color Palette ─────────────────────────────────────────────────────────────

export const HIGH_CONTRAST_PALETTE = [
  '#22d3ee', // cyan
  '#f472b6', // pink
  '#34d399', // emerald
  '#fb923c', // orange
  '#818cf8', // indigo
  '#facc15', // yellow
  '#60a5fa', // blue
  '#f87171', // red
  '#a78bfa', // violet
  '#4ade80', // green
  '#38bdf8', // sky
  '#e879f9', // fuchsia
]

export const hexToRgba = (hex, alpha) => {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

export const getLadderBarColor = (_modelName, index) =>
  HIGH_CONTRAST_PALETTE[index % HIGH_CONTRAST_PALETTE.length]

export const getModelColor = (modelName, index) => {
  const seed = [...(modelName || '')].reduce((sum, ch) => sum + ch.charCodeAt(0), 0)
  return HIGH_CONTRAST_PALETTE[(seed + index) % HIGH_CONTRAST_PALETTE.length]
}

// ── Math Helpers ──────────────────────────────────────────────────────────────

export const roundToTwo = v => Number(v.toFixed(2))

export const toDisplayMetricNumber = (value) => {
  const numeric = Number(value)
  return Number.isFinite(numeric) ? roundToTwo(numeric) : null
}

export const calcAxisRange = (values) => {
  if (!values.length) return { min: null, max: null }
  const minVal = Math.min(...values)
  const maxVal = Math.max(...values)
  if (minVal === maxVal) {
    const pad = Math.max(Math.abs(minVal) * 0.08, 1)
    return { min: roundToTwo(minVal - pad), max: roundToTwo(maxVal + pad) }
  }
  const pad = (maxVal - minVal) * 0.18
  return { min: roundToTwo(minVal - pad), max: roundToTwo(maxVal + pad) }
}

// ── Metric Formatting ─────────────────────────────────────────────────────────

export const formatMetricValue = (value, metricName = '', metricUnits = {}) => {
  if (value === undefined || value === null || value === '') return '--'
  const numeric = Number(value)
  const base = Number.isFinite(numeric) ? numeric.toFixed(2) : String(value)
  const unit = metricUnits[metricName] || ''
  if (!unit) return base
  return unit === '%' ? `${base}${unit}` : `${base} ${unit}`
}

export const isAccuracyMetric = metricName =>
  String(metricName || '').toLowerCase().startsWith('accuracy')

export const getMetricMin = metricName => (isAccuracyMetric(metricName) ? 0 : -Infinity)
export const getMetricMax = metricName => (isAccuracyMetric(metricName) ? 100 : Infinity)

// ── Pareto Front ──────────────────────────────────────────────────────────────

export const isMetricBetterOrEqual = (candidate, target, metricName, lowerIsBetterSet) =>
  lowerIsBetterSet.has(metricName) ? candidate <= target : candidate >= target

export const isMetricStrictlyBetter = (candidate, target, metricName, lowerIsBetterSet) =>
  lowerIsBetterSet.has(metricName) ? candidate < target : candidate > target

export const isParetoDominated = (candidate, target, xMetric, yMetric, lowerIsBetterSet) => {
  const boeX = isMetricBetterOrEqual(candidate.rawX, target.rawX, xMetric, lowerIsBetterSet)
  const boeY = isMetricBetterOrEqual(candidate.rawY, target.rawY, yMetric, lowerIsBetterSet)
  const sbX = isMetricStrictlyBetter(candidate.rawX, target.rawX, xMetric, lowerIsBetterSet)
  const sbY = isMetricStrictlyBetter(candidate.rawY, target.rawY, yMetric, lowerIsBetterSet)
  return boeX && boeY && (sbX || sbY)
}

export const buildParetoFront = (points, xMetric, yMetric, lowerIsBetterSet) =>
  points.filter(target =>
    !points.some(
      candidate =>
        candidate.modelName !== target.modelName &&
        isParetoDominated(candidate, target, xMetric, yMetric, lowerIsBetterSet)
    )
  )

// ── Radar / Polygon ───────────────────────────────────────────────────────────

/**
 * Normalize a single model's metric values to 0–100 for radar chart.
 * @param {string} modelName
 * @param {Array} metrics - array of metric defs { value, direction }
 * @param {string[]} allSelectedModels
 * @param {Object} metricsByModel - { modelName: { metricKey: value } }
 * @param {Function} getMetricValueByKey
 * @param {Set} lowerIsBetterSet
 */
export const normalizeForRadar = (
  modelName,
  metrics,
  allSelectedModels,
  metricsByModel,
  getMetricValueByKey,
  lowerIsBetterSet
) => {
  return metrics.map(metric => {
    const allVals = allSelectedModels
      .map(name => {
        const v = getMetricValueByKey(metricsByModel[name] || {}, metric.value)
        return v !== null && v !== undefined ? Number(v) : null
      })
      .filter(v => v !== null && Number.isFinite(v))

    const rawVal = getMetricValueByKey(metricsByModel[modelName] || {}, metric.value)
    const val = rawVal !== null && rawVal !== undefined ? Number(rawVal) : null

    if (val === null || !Number.isFinite(val) || !allVals.length) return 0

    const min = Math.min(...allVals)
    const max = Math.max(...allVals)
    if (min === max) return 50

    return lowerIsBetterSet.has(metric.value)
      ? ((max - val) / (max - min)) * 100
      : ((val - min) / (max - min)) * 100
  })
}

/**
 * Shoelace formula for polygon area (values are radii at evenly-spaced angles).
 */
export const computePolygonArea = (values) => {
  const n = values.length
  if (n < 3) return 0
  let area = 0
  for (let i = 0; i < n; i++) {
    const a1 = (2 * Math.PI * i / n) - Math.PI / 2
    const a2 = (2 * Math.PI * ((i + 1) % n) / n) - Math.PI / 2
    const x1 = values[i] * Math.cos(a1)
    const y1 = values[i] * Math.sin(a1)
    const x2 = values[(i + 1) % n] * Math.cos(a2)
    const y2 = values[(i + 1) % n] * Math.sin(a2)
    area += x1 * y2 - x2 * y1
  }
  return Math.abs(area) / 2
}

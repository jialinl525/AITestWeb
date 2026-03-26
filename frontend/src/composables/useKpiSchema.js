import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { getKPISchema } from '../api/kpi'

const LEGACY_METRIC_FALLBACKS = {
  accuracy_total: ['accuracy_overall'],
  accuracy_cn: ['accuracy_zh'],
  e2e_latency: ['latency']
}

export function useKpiSchema() {
  const kpiSchema = ref({ categories: [] })

  const schemaCategories = computed(() =>
    Array.isArray(kpiSchema.value?.categories) ? kpiSchema.value.categories : []
  )

  const MODEL_CATEGORY_KEYS = computed(() => schemaCategories.value.map(c => c.key))

  const MODEL_CATEGORY_INFO = computed(() =>
    Object.fromEntries(schemaCategories.value.map(c => [c.key, c.description || `${c.key} metrics`]))
  )

  const CATEGORY_METRIC_DEFS = computed(() => {
    const mapping = {}
    schemaCategories.value.forEach(category => {
      mapping[category.key] = (category.metrics || []).map(metric => ({
        label: metric.label || metric.key,
        value: metric.key,
        unit: metric.unit || '',
        direction: metric.direction || 'higher',
        chart_roles: Array.isArray(metric.chart_roles) ? metric.chart_roles : [],
        definition: metric.definition || ''
      }))
    })
    return mapping
  })

  const METRIC_META_MAP = computed(() => {
    const mapping = {}
    Object.values(CATEGORY_METRIC_DEFS.value).flat().forEach(metric => {
      if (!mapping[metric.value]) mapping[metric.value] = metric
    })
    return mapping
  })

  const METRIC_LABEL_MAP = computed(() =>
    Object.fromEntries(Object.entries(METRIC_META_MAP.value).map(([key, meta]) => [key, meta.label || key]))
  )

  const METRIC_UNITS = computed(() =>
    Object.fromEntries(Object.entries(METRIC_META_MAP.value).map(([key, meta]) => [key, meta.unit || '']))
  )

  const LOWER_IS_BETTER_METRICS = computed(() =>
    new Set(
      Object.entries(METRIC_META_MAP.value)
        .filter(([, meta]) => String(meta.direction || 'higher').toLowerCase() === 'lower')
        .map(([key]) => key)
    )
  )

  const getMetricDefsForCategory = (category, role = null) => {
    const defs =
      CATEGORY_METRIC_DEFS.value[category] ||
      CATEGORY_METRIC_DEFS.value[schemaCategories.value[0]?.key] ||
      []
    if (!role) return defs
    return defs.filter(m => (Array.isArray(m.chart_roles) ? m.chart_roles : []).includes(role))
  }

  const getMetricValueByKey = (metrics = {}, metricKey = '') => {
    if (!metricKey) return null
    if (metrics?.[metricKey] !== undefined) return metrics[metricKey]
    for (const fallbackKey of (LEGACY_METRIC_FALLBACKS[metricKey] || [])) {
      if (metrics?.[fallbackKey] !== undefined) return metrics[fallbackKey]
    }
    return null
  }

  const isLowerBetterMetric = (metricName = '') =>
    LOWER_IS_BETTER_METRICS.value.has(String(metricName || '').trim())

  const getMetricPreferenceText = (metricName = '') =>
    isLowerBetterMetric(metricName) ? 'lower is better' : 'higher is better'

  const getMetricName = (metric) => {
    const label = METRIC_LABEL_MAP.value[metric] || metric
    const unit = METRIC_UNITS.value[metric]
    return unit ? `${label} (${unit})` : label
  }

  const getLadderMetricTitle = (metricName = '') =>
    `${getMetricName(metricName)} Ranking • ${getMetricPreferenceText(metricName)}`

  const loadKPISchema = async () => {
    try {
      const payload = await getKPISchema()
      kpiSchema.value = { categories: Array.isArray(payload?.categories) ? payload.categories : [] }
    } catch (error) {
      kpiSchema.value = { categories: [] }
      ElMessage.error(error?.response?.data?.detail || 'Failed to load KPI schema')
    }
  }

  return {
    kpiSchema,
    schemaCategories,
    MODEL_CATEGORY_KEYS,
    MODEL_CATEGORY_INFO,
    CATEGORY_METRIC_DEFS,
    METRIC_META_MAP,
    METRIC_LABEL_MAP,
    METRIC_UNITS,
    LOWER_IS_BETTER_METRICS,
    getMetricDefsForCategory,
    getMetricValueByKey,
    isLowerBetterMetric,
    getMetricPreferenceText,
    getMetricName,
    getLadderMetricTitle,
    loadKPISchema
  }
}

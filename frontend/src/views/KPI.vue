<template>
  <div class="page-shell kpi-container">
    <section class="page-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">{{ LT.heroEyebrow }}</div>
        <h2 class="page-hero__title">{{ LT.heroTitle }}</h2>
        <p class="page-hero__desc">{{ DT.hero }}</p>
      </div>
      <div class="page-hero__actions">
        <div class="glass-pill">{{ DT.scope }}</div>
      </div>
    </section>

    <!-- Category Explorer -->
    <KpiCategoryExplorer
      :model-category="modelCategory"
      :schema-categories="schemaCategories"
      :category-info="MODEL_CATEGORY_INFO"
      :metric-defs="getMetricDefsForCategory(modelCategory)"
      :can-manage="canManageKPI"
      :get-metric-preference-text="getMetricPreferenceText"
      @select-category="selectModelCategory"
      @create="openCreateCategoryDialog"
      @edit="openEditCategoryDialog"
      @delete="deleteCategoryDefinition"
    />

    <!-- Ladder Chart -->
    <KpiLadderChart
      :chart-option="ladderChartOption"
      :loading="ladderLoading"
      :metric-options="LADDER_METRIC_OPTIONS"
      :ladder-metric="ladderMetric"
      @select-metric="selectLadderMetric"
      @chart-click="handleChartSingleClick"
      @chart-dblclick="handleChartDoubleClick"
    />

    <!-- Model List Table -->
    <KpiModelTable
      :model-list="modelList"
      :loading="modelListLoading"
      :can-manage="canManageKPI"
      @compare="showCompareDialog = true"
      @update-model="openUpdatePickerDialog"
      @new-model="openCreateModelDialog"
      @go-detail="goModelDetail"
      @edit="openEditModelDialog"
      @delete="deleteModelRow"
    />

    <!-- Compare Dialog -->
    <KpiCompareDialog
      v-model:visible="showCompareDialog"
      :model-category="modelCategory"
      :available-model-names="availableModelNames"
      :metrics-by-model="metricsByModel"
      :compare-metric-defs="getMetricDefsForCategory(modelCategory)"
      :latest-model-list="modelList"
      :is-lower-better-metric="isLowerBetterMetric"
      :get-metric-value-by-key="getMetricValueByKey"
      :get-metric-name="getMetricName"
      :format-metric-value="fmtMetricValue"
      :lower-is-better-set="LOWER_IS_BETTER_METRICS"
    />

    <!-- Model Create/Edit Dialog -->
    <KpiModelDialog
      v-model:visible="showModelDialog"
      :is-editing="isEditingModel"
      :model-form="modelForm"
      :model-categories="MODEL_CATEGORY_KEYS"
      :form-metrics="MODEL_FORM_METRICS"
      :saving="modelDialogSaving"
      :can-manage="canManageKPI"
      @save="saveModelDialog"
    />

    <!-- Update Picker Dialog -->
    <el-dialog v-model="showUpdatePickerDialog" title="Update Existing Model" width="500px">
      <el-form label-width="110px">
        <el-form-item label="Model Name">
          <el-select v-model="selectedUpdateModelName" style="width: 100%" filterable placeholder="Select model to update">
            <el-option v-for="row in modelList" :key="`update-${row.model_name}`" :label="row.model_name" :value="row.model_name" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUpdatePickerDialog = false">Cancel</el-button>
        <el-button v-if="canManageKPI" type="primary" @click="confirmUpdateModelSelection">Update</el-button>
      </template>
    </el-dialog>

    <!-- Category Create/Edit Dialog -->
    <KpiCategoryDialog
      v-model:visible="showCategoryDialog"
      :is-editing="isEditingCategory"
      :category-form="categoryForm"
      :saving="categoryDialogSaving"
      @save="saveCategoryDialog"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

import {
  createKPISchemaCategory, deleteKPISchemaCategory,
  getKPIMetrics, getLadderChartData, getKPIModelLatestList,
  createKPIModel, updateKPISchemaCategory, updateKPILatestModel, deleteKPIModel
} from '../api/kpi'
import { canCreateOrEditTest } from '../stores/auth'
import { LabelText } from '../texts/LabelText'
import { DescriptionText } from '../texts/DescriptionText'
import { useKpiSchema } from '../composables/useKpiSchema'
import { getLadderBarColor, toDisplayMetricNumber, calcAxisRange, formatMetricValue, isAccuracyMetric } from '../utils/kpiMetrics'

import KpiCategoryExplorer from '../components/kpi/KpiCategoryExplorer.vue'
import KpiLadderChart from '../components/kpi/KpiLadderChart.vue'
import KpiModelTable from '../components/kpi/KpiModelTable.vue'
import KpiCompareDialog from '../components/kpi/KpiCompareDialog.vue'
import KpiModelDialog from '../components/kpi/KpiModelDialog.vue'
import KpiCategoryDialog from '../components/kpi/KpiCategoryDialog.vue'

const LT = LabelText.kpi
const DT = DescriptionText.kpi
const router = useRouter()
const canManageKPI = computed(() => canCreateOrEditTest())

// ── Schema composable ─────────────────────────────────────────────────────────
const {
  schemaCategories, MODEL_CATEGORY_KEYS, MODEL_CATEGORY_INFO,
  LOWER_IS_BETTER_METRICS, METRIC_UNITS,
  getMetricDefsForCategory, getMetricValueByKey,
  isLowerBetterMetric, getMetricPreferenceText, getMetricName, getLadderMetricTitle,
  loadKPISchema
} = useKpiSchema()

// Wrapper so formatMetricValue can access METRIC_UNITS reactively
const fmtMetricValue = (value, metricName) =>
  formatMetricValue(value, metricName, METRIC_UNITS.value)

// ── State ─────────────────────────────────────────────────────────────────────
const ladderLoading = ref(false)
const ladderMetric = ref('')
const modelCategory = ref('')
const showCompareDialog = ref(false)
const ladderRecords = ref([])
const kpiMetrics = ref([])
const modelList = ref([])
const modelListLoading = ref(false)
const showModelDialog = ref(false)
const modelDialogSaving = ref(false)
const editingModelName = ref('')
const showUpdatePickerDialog = ref(false)
const selectedUpdateModelName = ref('')
const showCategoryDialog = ref(false)
const categoryDialogSaving = ref(false)
const editingCategoryKey = ref('')

// ── Computed ──────────────────────────────────────────────────────────────────
const LADDER_METRIC_OPTIONS = computed(() => getMetricDefsForCategory(modelCategory.value, 'ladder'))

const MODEL_FORM_METRICS = computed(() => {
  const preferred = getMetricDefsForCategory(modelForm.value.model_category || modelCategory.value, 'form')
  return preferred.length ? preferred : getMetricDefsForCategory(modelForm.value.model_category || modelCategory.value)
})

const metricsByModel = computed(() => {
  const grouped = {}
  for (const item of kpiMetrics.value) {
    if (!grouped[item.model_name]) grouped[item.model_name] = {}
    grouped[item.model_name][item.metric_name] = item.metric_value
  }
  return grouped
})

const availableModelNames = computed(() => Object.keys(metricsByModel.value))

// ── Category Form ─────────────────────────────────────────────────────────────
const createDefaultCategoryForm = () => ({
  key: '', label: '', description: '', implementation_notes: '',
  metrics: [{ key: '', label: '', unit: '', direction: 'higher', chart_roles: ['ladder', 'table', 'form'], definition: '' }]
})

const categoryForm = ref(createDefaultCategoryForm())
const isEditingCategory = computed(() => Boolean(editingCategoryKey.value))

// ── Model Form ────────────────────────────────────────────────────────────────
const buildDefaultMetrics = (category) => {
  const defaults = {}
  const defs = getMetricDefsForCategory(category, 'form')
  const selected = defs.length ? defs : getMetricDefsForCategory(category)
  selected.forEach(m => { defaults[m.value] = 0 })
  return defaults
}

const createDefaultModelForm = (category = '') => ({
  model_category: category || modelCategory.value || schemaCategories.value[0]?.key || '',
  model_name: '', source: '', model_size: '', description: '',
  test_date: '', test_platform: '', test_version: '', test_condition: '',
  metrics: buildDefaultMetrics(category || modelCategory.value || schemaCategories.value[0]?.key || '')
})

const modelForm = ref(createDefaultModelForm())
const isEditingModel = computed(() => Boolean(editingModelName.value))

// ── Schema helpers ────────────────────────────────────────────────────────────
const ensureActiveCategory = () => {
  const keys = MODEL_CATEGORY_KEYS.value
  if (!keys.length) { modelCategory.value = ''; return false }
  if (!modelCategory.value || !keys.includes(modelCategory.value)) modelCategory.value = keys[0]
  if (!modelForm.value.model_category || !keys.includes(modelForm.value.model_category)) {
    modelForm.value.model_category = modelCategory.value
  }
  return true
}

const syncLadderMetric = () => {
  const available = LADDER_METRIC_OPTIONS.value.map(m => m.value)
  if (!available.length) { ladderMetric.value = ''; return }
  const preferred = available.includes('accuracy_total') ? 'accuracy_total' : available[0]
  if (!available.includes(ladderMetric.value)) ladderMetric.value = preferred
}

// ── Ladder Chart ──────────────────────────────────────────────────────────────
const ladderChartOption = ref({
  title: { text: 'Model Performance Ranking', left: 'center', textStyle: { color: '#f8fafc', fontSize: 18, fontWeight: 700 } },
  tooltip: {
    trigger: 'axis', axisPointer: { type: 'shadow' },
    formatter: params => {
      const row = Array.isArray(params) ? params[0] : params
      if (!row) return ''
      const rawValue = typeof row.data === 'object' && row.data !== null ? row.data.value : row.value
      return `${row.name || row.axisValue || ''}<br/>${getMetricName(ladderMetric.value)}: ${fmtMetricValue(rawValue, ladderMetric.value)}`
    }
  },
  grid: { left: 24, right: 36, top: 70, bottom: 24, containLabel: true },
  xAxis: { type: 'value', name: 'Metric Value', scale: true, axisLabel: { color: 'rgba(226,232,240,0.72)' }, nameTextStyle: { color: 'rgba(226,232,240,0.72)' }, splitLine: { lineStyle: { color: 'rgba(148,163,184,0.12)' } } },
  yAxis: { type: 'category', data: [], name: 'Model Name', axisLabel: { color: 'rgba(226,232,240,0.72)' }, nameTextStyle: { color: 'rgba(226,232,240,0.72)' } },
  series: [{ name: 'Performance Metric', type: 'bar', data: [], barWidth: 14, itemStyle: { borderRadius: [0, 10, 10, 0] }, label: { show: true, position: 'right', color: '#e2e8f0' } }]
})

// ── Data Loading ──────────────────────────────────────────────────────────────
const loadModelList = async () => {
  modelListLoading.value = true
  try {
    modelList.value = await getKPIModelLatestList({ model_category: modelCategory.value })
  } catch { ElMessage.error('Failed to load model list') }
  finally { modelListLoading.value = false }
}

const loadMetricDetails = async () => {
  try {
    const data = await getKPIMetrics({ model_category: modelCategory.value })
    kpiMetrics.value = data || []
  } catch (e) { console.error('Failed to load model details', e) }
}

const loadLadderData = async () => {
  ladderLoading.value = true
  try {
    const data = await getLadderChartData(ladderMetric.value, modelCategory.value)
    ladderRecords.value = data.data || []
    const metricName = data.metric_name || ladderMetric.value
    const rawValues = ladderRecords.value.map(item => toDisplayMetricNumber(item.value)).filter(v => Number.isFinite(v))
    const xRange = calcAxisRange(rawValues)
    const ladderRows = (data.data || []).slice().reverse()
    const modelNames = ladderRows.map(item => item.model_name)
    const values = ladderRows.map((item, index) => ({
      value: toDisplayMetricNumber(item.value),
      itemStyle: { color: getLadderBarColor(item.model_name, index), borderRadius: [0, 10, 10, 0] },
      label: { color: '#e2e8f0' }
    }))
    ladderChartOption.value = {
      ...ladderChartOption.value,
      title: { ...ladderChartOption.value.title, text: getLadderMetricTitle(metricName) },
      xAxis: { ...ladderChartOption.value.xAxis, name: getMetricName(metricName), min: xRange.min, max: xRange.max },
      yAxis: { ...ladderChartOption.value.yAxis, data: modelNames },
      series: [{ ...ladderChartOption.value.series[0], data: values }]
    }
  } catch (e) { console.error('Failed to load ladder chart data', e) }
  finally { ladderLoading.value = false }
}

const reloadAll = async (preferredCategory = '') => {
  await loadKPISchema()
  const ready = ensureActiveCategory()
  if (!ready) return
  if (preferredCategory && MODEL_CATEGORY_KEYS.value.includes(preferredCategory)) {
    modelCategory.value = preferredCategory
    modelForm.value.model_category = preferredCategory
  }
  syncLadderMetric()
  await Promise.all([loadMetricDetails(), loadLadderData(), loadModelList()])
}

const handleCategoryChange = () => {
  syncLadderMetric()
  loadMetricDetails()
  loadLadderData()
  loadModelList()
}

const selectModelCategory = (category) => {
  if (!category || category === modelCategory.value) return
  modelCategory.value = category
  handleCategoryChange()
}

const selectLadderMetric = (metric) => {
  if (!metric || metric === ladderMetric.value) return
  ladderMetric.value = metric
  loadLadderData()
}

// ── Chart Handlers ────────────────────────────────────────────────────────────
const resolveClickedModelName = params => params?.data?.modelName || params?.name || ''

const handleChartSingleClick = (params) => {
  const name = resolveClickedModelName(params)
  if (!name) return
  ElMessage.closeAll()
  ElMessage({ type: 'info', duration: 2400, showClose: true, message: name })
}

const goModelDetail = (modelName) => {
  if (!modelName) return
  router.push({ path: `/kpi/models/${encodeURIComponent(modelName)}`, query: { category: modelCategory.value } })
}

const handleChartDoubleClick = (params) => {
  const name = resolveClickedModelName(params)
  if (name) goModelDetail(name)
}

// ── Model CRUD ────────────────────────────────────────────────────────────────
const openCreateModelDialog = () => {
  if (!canManageKPI.value) { ElMessage.warning('Only manager users can modify KPI models'); return }
  editingModelName.value = ''
  modelForm.value = createDefaultModelForm(modelCategory.value)
  showModelDialog.value = true
}

const openUpdatePickerDialog = () => {
  if (!canManageKPI.value) { ElMessage.warning('Only manager users can modify KPI models'); return }
  if (!modelList.value.length) { ElMessage.warning('No existing model available for update'); return }
  selectedUpdateModelName.value = modelList.value[0]?.model_name || ''
  showUpdatePickerDialog.value = true
}

const confirmUpdateModelSelection = () => {
  const target = modelList.value.find(row => row.model_name === selectedUpdateModelName.value)
  if (!target) { ElMessage.warning('Please select an existing model'); return }
  showUpdatePickerDialog.value = false
  openEditModelDialog(target)
}

const toMetricNumber = (value) => {
  const n = Number(value)
  return Number.isFinite(n) ? n : 0
}

const formatDateTimeForEdit = (value) => {
  if (!value) return ''
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return ''
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

const openEditModelDialog = (row) => {
  if (!canManageKPI.value) { ElMessage.warning('Only manager users can modify KPI models'); return }
  const targetCategory = row.model_category || modelCategory.value
  const metricDefs = getMetricDefsForCategory(targetCategory)
  const dynamicMetrics = {}
  metricDefs.forEach(m => { dynamicMetrics[m.value] = toMetricNumber(getMetricValueByKey(row.metrics, m.value)) })
  editingModelName.value = row.model_name || ''
  modelForm.value = {
    model_category: targetCategory, model_name: row.model_name || '',
    source: row.source || '', model_size: row.model_size || '',
    description: row.description || '',
    test_date: row.test_date ? formatDateTimeForEdit(row.test_date) : '',
    test_platform: row.test_platform || '', test_version: row.test_version || '',
    test_condition: row.test_condition || '', metrics: dynamicMetrics
  }
  showModelDialog.value = true
}

const saveModelDialog = async () => {
  if (!canManageKPI.value) { ElMessage.warning('Only manager users can modify KPI models'); return }
  if (!modelForm.value.model_name?.trim()) { ElMessage.warning('Model name is required'); return }

  const metrics = {}
  MODEL_FORM_METRICS.value.forEach(m => {
    const raw = modelForm.value.metrics?.[m.value]
    if (raw === undefined || raw === null || raw === '') return
    const n = Number(raw)
    if (Number.isFinite(n)) metrics[m.value] = n
  })
  if (!Object.keys(metrics).length) { ElMessage.warning('At least one metric value is required'); return }
  const outOfRange = Object.keys(metrics).find(k => isAccuracyMetric(k) && (metrics[k] < 0 || metrics[k] > 100))
  if (outOfRange) { ElMessage.warning('Accuracy values must be between 0 and 100'); return }

  const payload = {
    model_category: modelForm.value.model_category || modelCategory.value,
    model_name: modelForm.value.model_name.trim(),
    source: modelForm.value.source || '', model_size: modelForm.value.model_size || '',
    description: modelForm.value.description || '', test_date: modelForm.value.test_date || null,
    test_platform: modelForm.value.test_platform || '', test_version: modelForm.value.test_version || '',
    test_condition: modelForm.value.test_condition || '', metrics
  }

  modelDialogSaving.value = true
  try {
    if (isEditingModel.value) {
      await updateKPILatestModel(editingModelName.value, payload)
      ElMessage.success('Model updated')
    } else {
      await createKPIModel(payload)
      ElMessage.success('Model created')
    }
    showModelDialog.value = false
    editingModelName.value = ''
    await Promise.all([loadMetricDetails(), loadLadderData(), loadModelList()])
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to save model')
  } finally {
    modelDialogSaving.value = false
  }
}

const deleteModelRow = async (row) => {
  if (!canManageKPI.value) { ElMessage.warning('Only manager users can modify KPI models'); return }
  const targetName = row?.model_name
  if (!targetName) return
  try {
    await ElMessageBox.confirm(
      `Delete all KPI runs for model ${targetName} in category ${modelCategory.value}?`,
      'Delete Model', { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }
    )
  } catch { return }
  try {
    await deleteKPIModel(targetName, { model_category: modelCategory.value })
    ElMessage.success('Model deleted')
    await Promise.all([loadMetricDetails(), loadLadderData(), loadModelList()])
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to delete model')
  }
}

// ── Category CRUD ─────────────────────────────────────────────────────────────
const openCreateCategoryDialog = () => {
  editingCategoryKey.value = ''
  categoryForm.value = createDefaultCategoryForm()
  showCategoryDialog.value = true
}

const openEditCategoryDialog = (category) => {
  if (!category) return
  editingCategoryKey.value = category.key
  const normMetrics = (category.metrics || []).map(m => ({
    key: String(m.key || '').trim(), label: String(m.label || '').trim(),
    unit: String(m.unit || '').trim(),
    direction: String(m.direction || 'higher').trim().toLowerCase() === 'lower' ? 'lower' : 'higher',
    chart_roles: [...new Set((Array.isArray(m.chart_roles) ? m.chart_roles : []).map(r => String(r || '').trim().toLowerCase()).filter(Boolean))],
    definition: String(m.definition || '').trim()
  }))
  categoryForm.value = {
    key: category.key || '', label: category.label || category.key || '',
    description: category.description || '', implementation_notes: category.implementation_notes || '',
    metrics: normMetrics.length ? normMetrics : [{ key: '', label: '', unit: '', direction: 'higher', chart_roles: ['ladder', 'table', 'form'], definition: '' }]
  }
  showCategoryDialog.value = true
}

const saveCategoryDialog = async () => {
  const categoryKey = String(categoryForm.value.key || '').trim()
  if (!categoryKey) { ElMessage.warning('Model type key is required'); return }

  const metrics = (categoryForm.value.metrics || []).map(m => ({
    key: String(m.key || '').trim(), label: String(m.label || m.key || '').trim(),
    unit: String(m.unit || '').trim(),
    direction: String(m.direction || 'higher').trim().toLowerCase() === 'lower' ? 'lower' : 'higher',
    chart_roles: [...new Set((Array.isArray(m.chart_roles) ? m.chart_roles : []).map(r => String(r || '').trim().toLowerCase()).filter(Boolean))],
    definition: String(m.definition || '').trim()
  }))

  if (!metrics.length) { ElMessage.warning('At least one parameter is required'); return }
  if (metrics.find(m => !m.key)) { ElMessage.warning('Every parameter must have a metric key'); return }

  const seen = new Set(); const dupes = new Set()
  metrics.forEach(m => { const t = m.key.toLowerCase(); if (seen.has(t)) dupes.add(m.key); seen.add(t) })
  if (dupes.size) { ElMessage.warning(`Duplicate metric keys: ${[...dupes].join(', ')}`); return }

  const payload = {
    key: categoryKey, label: String(categoryForm.value.label || categoryKey).trim(),
    description: String(categoryForm.value.description || '').trim(),
    implementation_notes: String(categoryForm.value.implementation_notes || '').trim(),
    metrics: metrics.map(m => ({ ...m, chart_roles: m.chart_roles.length ? m.chart_roles : ['table', 'form'] }))
  }

  categoryDialogSaving.value = true
  try {
    if (isEditingCategory.value) {
      await updateKPISchemaCategory(editingCategoryKey.value, payload)
      ElMessage.success('Model type updated')
    } else {
      await createKPISchemaCategory(payload)
      ElMessage.success('Model type created')
    }
    showCategoryDialog.value = false
    editingCategoryKey.value = ''
    await reloadAll(payload.key)
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to save model type')
  } finally {
    categoryDialogSaving.value = false
  }
}

const deleteCategoryDefinition = async (category) => {
  if (!category?.key) return
  try {
    await ElMessageBox.confirm(
      `Delete model type ${category.key}? This only removes the schema definition and will be blocked if KPI data still exists.`,
      'Delete Model Type', { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }
    )
  } catch { return }
  try {
    await deleteKPISchemaCategory(category.key)
    ElMessage.success('Model type deleted')
    await reloadAll('')
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to delete model type')
  }
}

// ── Init ──────────────────────────────────────────────────────────────────────
onMounted(async () => {
  await loadKPISchema()
  const ready = ensureActiveCategory()
  if (!ready) return
  syncLadderMetric()
  loadMetricDetails()
  loadLadderData()
  loadModelList()
})
</script>

<style scoped>
.kpi-container { width: 100%; }
</style>

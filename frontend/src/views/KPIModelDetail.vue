<template>
  <div class="page-shell detail-container kpi-model-detail">
    <section class="page-hero detail-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">Model Detail</div>
        <h2 class="page-hero__title">{{ modelName }}</h2>
        <p class="page-hero__desc">View different test data by selecting test version.</p>
      </div>
      <div class="page-hero__actions">
        <el-button @click="goBack">Back to KPI</el-button>
      </div>
    </section>

    <el-card class="section-card detail-card" v-loading="loading || versionsLoading">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>Model Run Information</h3>
            <span class="section-title__meta">Switch test version to inspect version-specific metrics.</span>
          </div>
          <div class="detail-toolbar">
            <el-select
              v-model="selectedVersion"
              :disabled="!versionOptions.length"
              placeholder="Select test version"
              style="width: 300px"
            >
              <el-option
                v-for="item in versionOptions"
                :key="`${item.test_version}-${item.test_date}`"
                :label="formatVersionLabel(item)"
                :value="item.test_version"
              />
            </el-select>
          </div>
        </div>
      </template>

      <template v-if="detail">
        <el-descriptions :column="2" border class="detail-info">
          <el-descriptions-item label="Model Name">{{ detail.model_name }}</el-descriptions-item>
          <el-descriptions-item label="Model Category">{{ detail.model_category }}</el-descriptions-item>
          <el-descriptions-item label="Test Time">{{ formatDateTime(detail.test_date) }}</el-descriptions-item>
          <el-descriptions-item label="Test Platform">{{ detail.test_platform || '-' }}</el-descriptions-item>
          <el-descriptions-item label="Test Version">{{ detail.test_version || '-' }}</el-descriptions-item>
          <el-descriptions-item label="Test Condition" :span="2">
            <div class="description-text">{{ detail.test_condition || '-' }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="Source">{{ detail.source || '-' }}</el-descriptions-item>
          <el-descriptions-item label="Model Size">{{ detail.model_size || '-' }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">
            <div class="description-text">{{ detail.description || '-' }}</div>
          </el-descriptions-item>
        </el-descriptions>

        <el-card class="section-card detail-inner-card metrics-card">
          <template #header>
            <div class="section-title">
              <div class="section-title__main">
                <h3>Metrics</h3>
                <span class="section-title__meta">Metrics under current selected version</span>
              </div>
            </div>
          </template>
          <el-table :data="metricRows" stripe>
            <el-table-column prop="name" label="Metric" min-width="220" />
            <el-table-column prop="value" label="Value" min-width="160" />
          </el-table>
        </el-card>
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getKPIModelDetail, getKPIModelVersions } from '../api/kpi'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const versionsLoading = ref(false)
const detail = ref(null)
const versionOptions = ref([])
const selectedVersion = ref('')

const modelName = computed(() => decodeURIComponent(route.params.modelName || ''))
const modelCategory = computed(() => String(route.query.category || '').trim())

const METRIC_LABEL_MAP = {
  power_consumption: 'Power',
  latency: 'Latency',
  e2e_latency: 'E2E Latency',
  wakeup_rate: 'Wakeup Rate',
  accuracy_total: 'Accuracy-total',
  accuracy_overall: 'Accuracy-total',
  accuracy_en: 'Accuracy-en',
  accuracy_cn: 'Accuracy-cn',
  accuracy_zh: 'Accuracy-cn',
  accuracy_es: 'Accuracy-es',
  accuracy_en_to_cn: 'Accuracy-en to cn',
  accuracy_cn_to_en: 'Accuracy-cn to en',
  accuracy_en_to_es: 'Accuracy-en to es',
  accuracy_es_to_en: 'Accuracy-es to en'
}

const METRIC_UNITS = {
  power_consumption: 'W',
  latency: 'ms',
  e2e_latency: 'ms',
  wakeup_rate: '%',
  accuracy_total: '%',
  accuracy_overall: '%',
  accuracy_en: '%',
  accuracy_cn: '%',
  accuracy_zh: '%',
  accuracy_es: '%',
  accuracy_en_to_cn: '%',
  accuracy_cn_to_en: '%',
  accuracy_en_to_es: '%',
  accuracy_es_to_en: '%'
}

const isAccuracyMetric = (metricName = '') => String(metricName).toLowerCase().startsWith('accuracy')

const metricRows = computed(() => {
  const metrics = detail.value?.metrics || {}
  return Object.keys(metrics).map((key) => ({
    name: METRIC_LABEL_MAP[key] || key,
    value: formatMetric(metrics[key], key)
  }))
})

const formatMetric = (value, metricName = '') => {
  const numeric = Number(value)
  const hasNumeric = Number.isFinite(numeric)
  const displayValue = hasNumeric && isAccuracyMetric(metricName) ? numeric * 100 : numeric
  const base = hasNumeric ? displayValue.toFixed(2) : String(value ?? '--')
  const unit = METRIC_UNITS[metricName] || ''
  if (!unit) {
    return base
  }
  if (unit === '%') {
    return `${base}${unit}`
  }
  return `${base} ${unit}`
}

const formatDateTime = (value) => {
  if (!value) return '-'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return '-'
  return d.toLocaleString('en-US')
}

const formatVersionLabel = (item) => {
  const version = item.test_version || '(No Version)'
  return `${version} | ${formatDateTime(item.test_date)}`
}

const loadVersions = async () => {
  versionsLoading.value = true
  try {
    const params = {}
    if (modelCategory.value) params.model_category = modelCategory.value
    const data = await getKPIModelVersions(modelName.value, params)
    versionOptions.value = data || []
    if (!versionOptions.value.length) {
      selectedVersion.value = ''
      return
    }

    const matched = versionOptions.value.find((item) => item.test_version === selectedVersion.value)
    if (!matched) {
      selectedVersion.value = versionOptions.value[0].test_version
    }
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to load model versions')
  } finally {
    versionsLoading.value = false
  }
}

const loadDetail = async () => {
  if (!modelName.value) return

  loading.value = true
  try {
    const params = {}
    if (modelCategory.value) params.model_category = modelCategory.value
    if (selectedVersion.value) params.test_version = selectedVersion.value
    detail.value = await getKPIModelDetail(modelName.value, params)
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to load model detail')
  } finally {
    loading.value = false
  }
}

const loadAll = async () => {
  await loadVersions()
  await loadDetail()
}

const goBack = () => {
  router.push('/kpi')
}

watch(
  () => selectedVersion.value,
  (next, prev) => {
    if (next === prev) return
    loadDetail()
  }
)

watch(
  () => [route.params.modelName, route.query.category],
  () => {
    selectedVersion.value = ''
    loadAll()
  }
)

onMounted(() => {
  loadAll()
})
</script>

<style scoped src="../styles/detail-shared.css"></style>

<style scoped>
.kpi-model-detail {
  width: 100%;
}

.detail-toolbar {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.metrics-card {
  margin-top: 16px;
}

.description-text {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}
</style>

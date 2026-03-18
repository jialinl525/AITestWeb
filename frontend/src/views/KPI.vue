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
        <div v-if="showScatterChart" class="glass-pill">Comparison Axes: {{ getMetricName(scatterXMetric) }} / {{ getMetricName(scatterYMetric) }}</div>
        <div v-if="showScatterChart" class="glass-pill">Best Region: {{ getScatterBestRegionText(scatterXMetric, scatterYMetric) }}</div>
      </div>
    </section>

    <el-card class="section-card category-focus-card">
      <div class="category-focus">
        <div class="category-focus__left">
          <div class="category-focus__eyebrow">{{ LT.category.eyebrow }}</div>
          <h3 class="category-focus__title">{{ LT.category.title }}</h3>
          <p class="category-focus__desc">{{ DT.categoryCurrentPrefix }} <strong>{{ modelCategory }}</strong>. {{ DT.categoryCurrentSuffix }}</p>
        </div>
      </div>

      <div class="category-description-grid">
        <article
          v-for="(info, key) in MODEL_CATEGORY_INFO"
          :key="key"
          class="category-description-item"
          :class="{ 'is-active': key === modelCategory }"
          role="button"
          tabindex="0"
          @click="selectModelCategory(key)"
          @keydown.enter="selectModelCategory(key)"
          @keydown.space.prevent="selectModelCategory(key)"
        >
          <div class="category-description-item__header">
            <span>{{ key }}</span>
            <el-tag v-if="key === modelCategory" size="small" type="success">{{ LT.category.current }}</el-tag>
          </div>
          <p>{{ info }}</p>
        </article>
      </div>
    </el-card>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>{{ LT.section.ladder }}</h3>
            <span class="section-title__meta">{{ DT.sectionMeta.ladder }}</span>
          </div>
          <div class="metric-tag-group" role="tablist" aria-label="Ladder metric selector">
            <button
              v-for="item in LADDER_METRIC_OPTIONS"
              :key="item.value"
              type="button"
              class="metric-tag"
              :class="{ 'is-active': ladderMetric === item.value }"
              role="tab"
              :aria-selected="ladderMetric === item.value"
              @click="selectLadderMetric(item.value)"
            >
              {{ item.label }}
            </button>
          </div>
        </div>
      </template>
      <v-chart
        class="chart"
        :option="ladderChartOption"
        v-loading="ladderLoading"
        @click="handleChartSingleClick"
        @dblclick="handleChartDoubleClick"
        style="height: 400px"
      />
    </el-card>

    <el-card v-if="showScatterChart" class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>{{ LT.section.scatter }}</h3>
            <span class="section-title__meta">{{ DT.sectionMeta.scatter }}</span>
          </div>
          <div class="scatter-selector-wrap">
            <div class="metric-tag-group" role="group" aria-label="Scatter plot metric selector">
              <button
                v-for="item in SCATTER_METRIC_OPTIONS"
                :key="item.value"
                type="button"
                class="metric-tag"
                :class="{ 'is-active': scatterMetricSelection.includes(item.value) }"
                @click="toggleScatterMetric(item.value)"
              >
                {{ item.label }}
              </button>
            </div>
            <span class="selector-hint">{{ DT.scatterHint }}</span>
          </div>
        </div>
      </template>
      <v-chart
        class="chart"
        :option="scatterChartOption"
        v-loading="scatterLoading"
        @click="handleChartSingleClick"
        @dblclick="handleChartDoubleClick"
        style="height: 400px"
      />
    </el-card>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>Model List</h3>
            <span class="section-title__meta">Only latest test-time data is shown for each model name</span>
          </div>
          <div class="compare-toolbar">
            <el-button type="primary" @click="openCompareDialog">{{ BT.compareModels }}</el-button>
            <el-button type="warning" @click="openUpdatePickerDialog">Update Model</el-button>
            <el-button type="success" @click="openCreateModelDialog">New Model</el-button>
          </div>
        </div>
      </template>

      <el-table :data="modelList" v-loading="modelListLoading" stripe table-layout="fixed" class="model-list-table">
        <el-table-column prop="model_name" label="Model Name" align="center" header-align="center">
          <template #default="{ row }">
            <button type="button" class="model-link-btn" @click="goModelDetail(row.model_name)">
              {{ row.model_name }}
            </button>
          </template>
        </el-table-column>
        <el-table-column prop="test_version" label="Test Version" align="center" header-align="center" show-overflow-tooltip />
        <el-table-column prop="model_size" label="Model Size" align="center" header-align="center" show-overflow-tooltip />
        <el-table-column prop="source" label="Source" align="center" header-align="center" show-overflow-tooltip />
        <el-table-column prop="test_date" label="Test Time" align="center" header-align="center">
          <template #default="{ row }">{{ formatDateTime(row.test_date) }}</template>
        </el-table-column>
        <el-table-column label="Actions" align="center" header-align="center">
          <template #default="{ row }">
            <div class="row-actions">
              <el-button size="small" @click="openEditModelDialog(row)">Update</el-button>
              <el-button size="small" type="danger" plain @click="deleteModelRow(row)">Delete</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showModelDialog" :title="isEditingModel ? 'Edit Model (Latest Test Run)' : 'New Model Test Run'" width="760px">
      <el-form :model="modelForm" label-width="170px" class="model-dialog-form">
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="Model Category">
              <el-select v-model="modelForm.model_category" style="width: 100%">
                <el-option v-for="key in Object.keys(MODEL_CATEGORY_INFO)" :key="key" :label="key" :value="key" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Model Name">
              <el-input v-model="modelForm.model_name" :disabled="isEditingModel" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="Source">
              <el-input v-model="modelForm.source" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Model Size">
              <el-input v-model="modelForm.model_size" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="Description">
          <el-input v-model="modelForm.description" type="textarea" :rows="2" />
        </el-form-item>

        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="Test Time">
              <el-date-picker
                v-model="modelForm.test_date"
                type="datetime"
                value-format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Test Platform">
              <el-input v-model="modelForm.test_platform" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="Test Version">
              <el-input v-model="modelForm.test_version" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Test Condition">
              <el-input v-model="modelForm.test_condition" type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="12">
          <el-col v-for="metric in MODEL_FORM_METRICS" :key="metric.value" :span="24">
            <el-form-item :label="metric.label">
              <el-input-number
                v-model="modelForm.metrics[metric.value]"
                :min="getMetricMin(metric.value)"
                :max="getMetricMax(metric.value)"
                :step="0.01"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showModelDialog = false">Cancel</el-button>
        <el-button type="primary" :loading="modelDialogSaving" @click="saveModelDialog">Save</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showCompareDialog" :title="LT.compare.title" width="920px">
      <div class="compare-toolbar">
        <el-select v-model="compareModelA" :placeholder="DT.placeholders.selectModelA" style="width: 240px">
          <el-option v-for="name in availableModelNames" :key="`a-${name}`" :label="name" :value="name" />
        </el-select>
        <el-select v-model="compareModelB" :placeholder="DT.placeholders.selectModelB" style="width: 240px">
          <el-option v-for="name in availableModelNames" :key="`b-${name}`" :label="name" :value="name" />
        </el-select>
      </div>

      <el-table :data="compareRows" stripe :empty-text="DT.placeholders.compareEmpty">
        <el-table-column prop="label" :label="LT.compare.parameter" width="220" />
        <el-table-column prop="modelA" :label="compareModelA || LT.compare.modelA" min-width="220" />
        <el-table-column prop="modelB" :label="compareModelB || LT.compare.modelB" min-width="220" />
      </el-table>
    </el-dialog>

    <el-dialog v-model="showUpdatePickerDialog" title="Update Existing Model" width="500px">
      <el-form label-width="110px">
        <el-form-item label="Model Name">
          <el-select v-model="selectedUpdateModelName" style="width: 100%" filterable placeholder="Select model to update">
            <el-option
              v-for="row in modelList"
              :key="`update-${row.model_name}`"
              :label="row.model_name"
              :value="row.model_name"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUpdatePickerDialog = false">Cancel</el-button>
        <el-button type="primary" @click="confirmUpdateModelSelection">Update</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getKPIMetrics,
  getLadderChartData,
  getScatterChartData,
  getKPIModelLatestList,
  createKPIModel,
  updateKPILatestModel,
  deleteKPIModel
} from '../api/kpi'
import { LabelText } from '../texts/LabelText'
import { ButtonText } from '../texts/ButtonText'
import { DescriptionText } from '../texts/DescriptionText'

const LT = LabelText.kpi
const BT = ButtonText.kpi
const DT = DescriptionText.kpi
const router = useRouter()

const SCATTER_PALETTE = ['#22d3ee', '#60a5fa', '#a78bfa', '#f472b6', '#fb7185', '#f59e0b', '#34d399', '#facc15', '#38bdf8', '#818cf8']

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

const LOWER_IS_BETTER_METRICS = new Set([
  'power_consumption',
  'latency',
  'e2e_latency'
])

const MODEL_CATEGORY_INFO = {
  ASR: 'Automatic Speech Recognition. Focuses on recognition accuracy, real-time performance, and resource usage for speech-to-text scenarios.',
  TTS: 'Text To Speech. Focuses on naturalness, latency, and power efficiency for spoken output scenarios.',
  Translation: 'Text translation models. Focus on multilingual translation accuracy, end-to-end latency, and deployment cost.',
  'VoiceCallTranslation Solution': 'Real-time voice call translation solutions. Focus on latency, stability, and overall translation quality in call scenarios.',
  'LPI Recording': 'Low-power recording scenario focused on ultra-low power consumption.',
  'Multi Model Detection': 'Multi-model trigger/detection scenario focused on wakeup quality and responsiveness.'
}

const CATEGORY_METRIC_DEFS = {
  ASR: [
    { label: 'Power', value: 'power_consumption' },
    { label: 'Latency', value: 'latency' },
    { label: 'Accuracy-en', value: 'accuracy_en' },
    { label: 'Accuracy-cn', value: 'accuracy_cn' },
    { label: 'Accuracy-es', value: 'accuracy_es' },
    { label: 'Accuracy-total', value: 'accuracy_total' }
  ],
  TTS: [
    { label: 'Power', value: 'power_consumption' },
    { label: 'Latency', value: 'latency' },
    { label: 'Accuracy-en', value: 'accuracy_en' },
    { label: 'Accuracy-cn', value: 'accuracy_cn' },
    { label: 'Accuracy-es', value: 'accuracy_es' },
    { label: 'Accuracy-total', value: 'accuracy_total' }
  ],
  Translation: [
    { label: 'Power', value: 'power_consumption' },
    { label: 'Latency', value: 'latency' },
    { label: 'Accuracy-en to cn', value: 'accuracy_en_to_cn' },
    { label: 'Accuracy-cn to en', value: 'accuracy_cn_to_en' },
    { label: 'Accuracy-en to es', value: 'accuracy_en_to_es' },
    { label: 'Accuracy-es to en', value: 'accuracy_es_to_en' },
    { label: 'Accuracy-total', value: 'accuracy_total' }
  ],
  'VoiceCallTranslation Solution': [
    { label: 'Power', value: 'power_consumption' },
    { label: 'E2E Latency', value: 'e2e_latency' },
    { label: 'Accuracy-en to cn', value: 'accuracy_en_to_cn' },
    { label: 'Accuracy-cn to en', value: 'accuracy_cn_to_en' },
    { label: 'Accuracy-total', value: 'accuracy_total' }
  ],
  'LPI Recording': [
    { label: 'Power', value: 'power_consumption' }
  ],
  'Multi Model Detection': [
    { label: 'Power', value: 'power_consumption' },
    { label: 'Latency', value: 'latency' },
    { label: 'Wakeup Rate', value: 'wakeup_rate' }
  ]
}

const METRIC_LABEL_MAP = Object.fromEntries(
  Object.values(CATEGORY_METRIC_DEFS)
    .flat()
    .map((item) => [item.value, item.label])
)

const LEGACY_METRIC_FALLBACKS = {
  accuracy_total: ['accuracy_overall'],
  accuracy_cn: ['accuracy_zh'],
  e2e_latency: ['latency']
}

const getMetricDefsForCategory = (category) => {
  return CATEGORY_METRIC_DEFS[category] || CATEGORY_METRIC_DEFS.ASR
}

const getMetricValueByKey = (metrics = {}, metricKey = '') => {
  if (!metricKey) return null
  if (metrics?.[metricKey] !== undefined) {
    return metrics[metricKey]
  }
  const fallbacks = LEGACY_METRIC_FALLBACKS[metricKey] || []
  for (const fallbackKey of fallbacks) {
    if (metrics?.[fallbackKey] !== undefined) {
      return metrics[fallbackKey]
    }
  }
  return null
}

const MODEL_META_INFO = {
  'Model-A': {
    description: 'A lightweight model optimized for general speech recognition, with emphasis on real-time transcription and edge deployment.',
    source: 'Internal Benchmark Set A',
    modelSize: '1.2B'
  },
  'Model-B': {
    description: 'A standard baseline model for speech synthesis that balances voice stability and latency.',
    source: 'Internal TTS Baseline',
    modelSize: '980M'
  },
  'Model-C': {
    description: 'A multilingual translation model focused on accuracy and throughput across Chinese, English, and Spanish.',
    source: 'Translation Eval Pack',
    modelSize: '1.6B'
  },
  'Model-D': {
    description: 'A real-time call translation model optimized for streaming speech processing and pipeline stability.',
    source: 'Voicecall Solution Suite',
    modelSize: '2.1B'
  },
  'Model-E': {
    description: 'An enhanced ASR model focused on recognition robustness in complex noisy environments.',
    source: 'ASR Robustness Set',
    modelSize: '1.4B'
  },
  'Model-F': {
    description: 'A next-generation multilingual translation model focused on long-sentence semantics and cross-domain terminology consistency.',
    source: 'Global Translation Benchmark v2',
    modelSize: '1.9B'
  }
}

const getModelColor = (modelName, index) => {
  const seed = [...(modelName || '')].reduce((sum, ch) => sum + ch.charCodeAt(0), 0)
  return SCATTER_PALETTE[(seed + index) % SCATTER_PALETTE.length]
}

const roundToTwo = (value) => Number(value.toFixed(2))

const toDisplayMetricNumber = (value, metricName = '') => {
  const numeric = Number(value)
  if (!Number.isFinite(numeric)) {
    return null
  }
  const converted = isAccuracyMetric(metricName) ? numeric * 100 : numeric
  return roundToTwo(converted)
}

const isLowerBetterMetric = (metricName = '') => LOWER_IS_BETTER_METRICS.has(String(metricName || '').trim())

const getMetricPreferenceText = (metricName = '') => (isLowerBetterMetric(metricName) ? 'lower is better' : 'higher is better')

const getLadderMetricTitle = (metricName = '') => `${getMetricName(metricName)} Ranking • ${getMetricPreferenceText(metricName)}`

const getScatterBestRegionText = (xMetric = '', yMetric = '') => {
  const horizontal = isLowerBetterMetric(xMetric) ? 'left' : 'right'
  const vertical = isLowerBetterMetric(yMetric) ? 'bottom' : 'top'
  return `${vertical}-${horizontal}`
}

const getScatterMetricTitle = (xMetric = '', yMetric = '') => {
  return `${getMetricName(xMetric)} vs ${getMetricName(yMetric)} • Best region: ${getScatterBestRegionText(xMetric, yMetric)}`
}

const isMetricBetterOrEqual = (candidate, target, metricName = '') => {
  return isLowerBetterMetric(metricName) ? candidate <= target : candidate >= target
}

const isMetricStrictlyBetter = (candidate, target, metricName = '') => {
  return isLowerBetterMetric(metricName) ? candidate < target : candidate > target
}

const isParetoDominated = (candidate, target, xMetric = '', yMetric = '') => {
  const betterOrEqualX = isMetricBetterOrEqual(candidate.rawX, target.rawX, xMetric)
  const betterOrEqualY = isMetricBetterOrEqual(candidate.rawY, target.rawY, yMetric)
  const strictlyBetterX = isMetricStrictlyBetter(candidate.rawX, target.rawX, xMetric)
  const strictlyBetterY = isMetricStrictlyBetter(candidate.rawY, target.rawY, yMetric)

  return betterOrEqualX && betterOrEqualY && (strictlyBetterX || strictlyBetterY)
}

const buildParetoFront = (points = [], xMetric = '', yMetric = '') => {
  return points.filter((target) => {
    return !points.some((candidate) => {
      if (candidate.modelName === target.modelName) {
        return false
      }
      return isParetoDominated(candidate, target, xMetric, yMetric)
    })
  })
}

const getLadderBarColor = (modelName, index) => {
  const seed = [...(modelName || '')].reduce((sum, ch) => sum + ch.charCodeAt(0), 0)
  return SCATTER_PALETTE[(seed + index * 3) % SCATTER_PALETTE.length]
}

const calcAxisRange = (values) => {
  if (!values.length) {
    return { min: null, max: null }
  }

  const minVal = Math.min(...values)
  const maxVal = Math.max(...values)

  if (minVal === maxVal) {
    const pad = Math.max(Math.abs(minVal) * 0.08, 1)
    return {
      min: roundToTwo(minVal - pad),
      max: roundToTwo(maxVal + pad)
    }
  }

  const span = maxVal - minVal
  const pad = span * 0.18

  return {
    min: roundToTwo(minVal - pad),
    max: roundToTwo(maxVal + pad)
  }
}

const ladderLoading = ref(false)
const scatterLoading = ref(false)
const ladderMetric = ref('accuracy_total')
const modelCategory = ref('ASR')
const scatterMetricSelection = ref(['power_consumption', 'latency'])
const scatterXMetric = ref('power_consumption')
const scatterYMetric = ref('latency')
const selectedModelName = ref('')
const showCompareDialog = ref(false)
const compareModelA = ref('')
const compareModelB = ref('')
const ladderRecords = ref([])
const scatterRecords = ref([])
const kpiMetrics = ref([])
const modelList = ref([])
const modelListLoading = ref(false)
const showModelDialog = ref(false)
const modelDialogSaving = ref(false)
const editingModelName = ref('')
const showUpdatePickerDialog = ref(false)
const selectedUpdateModelName = ref('')

const LADDER_METRIC_OPTIONS = computed(() => getMetricDefsForCategory(modelCategory.value))

const SCATTER_METRIC_OPTIONS = computed(() => getMetricDefsForCategory(modelCategory.value))

const showScatterChart = computed(() => SCATTER_METRIC_OPTIONS.value.length > 1)

const MODEL_FORM_METRICS = computed(() => getMetricDefsForCategory(modelForm.value.model_category || modelCategory.value))

const buildDefaultMetricsForCategory = (category) => {
  const defaults = {}
  getMetricDefsForCategory(category).forEach((metric) => {
    defaults[metric.value] = 0
  })
  return defaults
}

const createDefaultModelForm = (category = modelCategory.value) => ({
  model_category: category,
  model_name: '',
  source: '',
  model_size: '',
  description: '',
  test_date: '',
  test_platform: '',
  test_version: '',
  test_condition: '',
  metrics: buildDefaultMetricsForCategory(category)
})

const modelForm = ref(createDefaultModelForm())
const isEditingModel = computed(() => Boolean(editingModelName.value))

const metricsByModel = computed(() => {
  const grouped = {}
  for (const item of kpiMetrics.value) {
    if (!grouped[item.model_name]) {
      grouped[item.model_name] = {}
    }
    grouped[item.model_name][item.metric_name] = item.metric_value
  }
  return grouped
})

const modelMetaByName = computed(() => {
  const grouped = {}
  for (const item of kpiMetrics.value) {
    const existing = grouped[item.model_name]
    const currentDate = item.test_date ? new Date(item.test_date).getTime() : 0
    const existingDate = existing?.__date || 0

    if (!existing || currentDate >= existingDate) {
      grouped[item.model_name] = {
        source: item.source || '',
        modelSize: item.model_size || '',
        description: item.description || '',
        __date: currentDate
      }
    }
  }

  Object.keys(grouped).forEach((name) => {
    delete grouped[name].__date
  })

  return grouped
})

const availableModelNames = computed(() => Object.keys(metricsByModel.value))

const selectedModelInfo = computed(() => {
  const name = selectedModelName.value || ladderSummary.value.topModel || '--'
  const dynamicMeta = modelMetaByName.value[name] || {}
  const staticMeta = MODEL_META_INFO[name] || {
    description: 'Add a detailed description for this model in MODEL_META_INFO.',
    source: 'TBD',
    modelSize: 'TBD'
  }

  return {
    name,
    ...staticMeta,
    ...dynamicMeta,
    metrics: metricsByModel.value[name] || {}
  }
})

const compareRows = computed(() => {
  if (!compareModelA.value || !compareModelB.value || compareModelA.value === compareModelB.value) {
    return []
  }

  const modelAInfo = buildModelInfo(compareModelA.value)
  const modelBInfo = buildModelInfo(compareModelB.value)

  const baseRows = [
    { label: 'Model Category', modelA: modelCategory.value, modelB: modelCategory.value },
    { label: 'Description', modelA: modelAInfo.description, modelB: modelBInfo.description },
    { label: 'Source', modelA: modelAInfo.source, modelB: modelBInfo.source },
    { label: 'Model Size', modelA: modelAInfo.modelSize, modelB: modelBInfo.modelSize }
  ]

  const metricRows = getMetricDefsForCategory(modelCategory.value).map((metric) => ({
    label: metric.label,
    modelA: formatMetricValue(getMetricValueByKey(modelAInfo.metrics, metric.value), metric.value),
    modelB: formatMetricValue(getMetricValueByKey(modelBInfo.metrics, metric.value), metric.value)
  }))

  return [...baseRows, ...metricRows]
})

const ladderChartOption = ref({
  title: {
    text: 'Model Performance Ranking',
    left: 'center',
    textStyle: {
      color: '#f8fafc',
      fontSize: 18,
      fontWeight: 700
    }
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    },
    formatter: (params) => {
      const row = Array.isArray(params) ? params[0] : params
      if (!row) return ''
      const modelName = row.name || row.axisValue || ''
      const rawValue = typeof row.data === 'object' && row.data !== null ? row.data.value : row.value
      return `${modelName}<br/>${getMetricName(ladderMetric.value)}: ${formatMetricValue(rawValue, ladderMetric.value, { alreadyDisplay: true })}`
    }
  },
  grid: {
    left: 24,
    right: 36,
    top: 70,
    bottom: 24,
    containLabel: true
  },
  xAxis: {
    type: 'value',
    name: 'Metric Value',
    scale: true,
    axisLabel: { color: 'rgba(226, 232, 240, 0.72)' },
    nameTextStyle: { color: 'rgba(226, 232, 240, 0.72)' },
    splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.12)' } }
  },
  yAxis: {
    type: 'category',
    data: [],
    name: 'Model Name',
    axisLabel: { color: 'rgba(226, 232, 240, 0.72)' },
    nameTextStyle: { color: 'rgba(226, 232, 240, 0.72)' }
  },
  series: [
    {
      name: 'Performance Metric',
      type: 'bar',
      data: [],
      barWidth: 14,
      itemStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 1,
          y2: 0,
          colorStops: [
            { offset: 0, color: '#22d3ee' },
            { offset: 1, color: '#818cf8' }
          ]
        },
        borderRadius: [0, 10, 10, 0]
      },
      label: {
        show: true,
        position: 'right',
        color: '#e2e8f0'
      }
    }
  ]
})

const scatterChartOption = ref({
  title: {
    text: 'Model Performance Comparison',
    subtext: '',
    left: 'center',
    textStyle: {
      color: '#f8fafc',
      fontSize: 18,
      fontWeight: 700
    },
    subtextStyle: {
      color: 'rgba(226, 232, 240, 0.72)',
      fontSize: 12
    }
  },
  tooltip: {
    trigger: 'item',
    formatter: (params) => {
      const modelName = params?.data?.modelName
      const point = params?.data?.value
      if (!modelName || !Array.isArray(point)) {
        return ''
      }
      const paretoTag = params?.data?.isParetoOptimal ? '<br/><strong>Pareto-optimal</strong>' : ''
      return `${modelName}<br/>${getMetricName(scatterXMetric.value)}: ${formatMetricValue(point[0], scatterXMetric.value, { alreadyDisplay: true })}<br/>${getMetricName(scatterYMetric.value)}: ${formatMetricValue(point[1], scatterYMetric.value, { alreadyDisplay: true })}${paretoTag}`
    }
  },
  grid: {
    left: 30,
    right: 24,
    top: 70,
    bottom: 42,
    containLabel: true
  },
  xAxis: {
    type: 'value',
    name: 'Power Consumption',
    scale: true,
    axisLabel: { color: 'rgba(226, 232, 240, 0.72)' },
    nameTextStyle: { color: 'rgba(226, 232, 240, 0.72)' },
    splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.12)' } }
  },
  yAxis: {
    type: 'value',
    name: 'Latency',
    scale: true,
    axisLabel: { color: 'rgba(226, 232, 240, 0.72)' },
    nameTextStyle: { color: 'rgba(226, 232, 240, 0.72)' },
    splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.12)' } }
  },
  series: [
    {
      name: 'Model Performance',
      type: 'scatter',
      data: [],
      symbolSize: 18,
      itemStyle: {
        borderColor: 'rgba(248, 250, 252, 0.85)',
        borderWidth: 1,
        shadowBlur: 16
      },
      label: {
        show: true,
        formatter: (params) => {
          return params.data.modelName
        },
        position: 'top',
        color: '#cbd5e1'
      },
      labelLayout: {
        hideOverlap: false,
        moveOverlap: 'shiftY'
      }
    }
  ]
})

const ladderSummary = computed(() => {
  if (!ladderRecords.value.length) {
    return {
      topModel: '--',
      topValue: '--',
      average: '--'
    }
  }

  const sorted = [...ladderRecords.value].sort((a, b) => {
    if (isLowerBetterMetric(ladderMetric.value)) {
      return a.value - b.value
    }
    return b.value - a.value
  })
  const avg = sorted.reduce((sum, item) => sum + item.value, 0) / sorted.length

  return {
    topModel: sorted[0].model_name,
    topValue: Number(sorted[0].value).toFixed(2),
    average: Number(avg).toFixed(2)
  }
})

const buildModelInfo = (name) => {
  const dynamicMeta = modelMetaByName.value[name] || {}
  const staticMeta = MODEL_META_INFO[name] || {
    description: 'Add a detailed description for this model in MODEL_META_INFO.',
    source: 'TBD',
    modelSize: 'TBD'
  }

  const meta = {
    ...staticMeta,
    ...dynamicMeta
  }

  return {
    ...meta,
    metrics: metricsByModel.value[name] || {}
  }
}

const loadModelList = async () => {
  modelListLoading.value = true
  try {
    modelList.value = await getKPIModelLatestList({ model_category: modelCategory.value })
  } catch (error) {
    console.error('Failed to load model list', error)
    ElMessage.error('Failed to load model list')
  } finally {
    modelListLoading.value = false
  }
}

const isAccuracyMetric = (metricName) => String(metricName || '').toLowerCase().startsWith('accuracy')

const getBestLatencyMetricName = (metrics = {}) => {
  const latency = getMetricValueByKey(metrics, 'latency')
  if (latency !== null && latency !== undefined) {
    return 'latency'
  }
  return 'e2e_latency'
}

const getMetricMin = (metricName) => (isAccuracyMetric(metricName) ? 0 : -Infinity)

const getMetricMax = (metricName) => (isAccuracyMetric(metricName) ? 1 : Infinity)

const loadMetricDetails = async () => {
  try {
    const data = await getKPIMetrics({ model_category: modelCategory.value })
    kpiMetrics.value = data || []
    const names = Object.keys(metricsByModel.value)
    if (!selectedModelName.value || !names.includes(selectedModelName.value)) {
      selectedModelName.value = names[0] || ''
    }
    if (!compareModelA.value || !names.includes(compareModelA.value)) {
      compareModelA.value = names[0] || ''
    }
    if (!compareModelB.value || compareModelB.value === compareModelA.value || !names.includes(compareModelB.value)) {
      compareModelB.value = names.find(name => name !== compareModelA.value) || ''
    }
  } catch (error) {
    console.error('Failed to load model details', error)
  }
}

const loadLadderData = async () => {
  ladderLoading.value = true
  try {
    const data = await getLadderChartData(ladderMetric.value, modelCategory.value)
    ladderRecords.value = data.data || []
    const metricName = data.metric_name || ladderMetric.value

    const rawValues = ladderRecords.value
      .map(item => toDisplayMetricNumber(item.value, metricName))
      .filter(v => Number.isFinite(v))
    const xRange = calcAxisRange(rawValues)
    
    const ladderRows = (data.data || []).slice().reverse()
    const modelNames = ladderRows.map(item => item.model_name)
    const values = ladderRows.map((item, index) => ({
      value: toDisplayMetricNumber(item.value, metricName),
      itemStyle: {
        color: getLadderBarColor(item.model_name, index),
        borderRadius: [0, 10, 10, 0]
      },
      label: {
        color: '#e2e8f0'
      }
    }))
    
    ladderChartOption.value = {
      ...ladderChartOption.value,
      title: {
        text: getLadderMetricTitle(metricName),
        left: 'center'
      },
      xAxis: {
        ...ladderChartOption.value.xAxis,
        name: getMetricName(metricName),
        min: xRange.min,
        max: xRange.max
      },
      yAxis: {
        ...ladderChartOption.value.yAxis,
        data: modelNames
      },
      series: [
        {
          ...ladderChartOption.value.series[0],
          data: values
        }
      ]
    }

    const names = ladderRows.map(item => item.model_name)
    if (names.length && !names.includes(selectedModelName.value)) {
      selectedModelName.value = names[0]
    }
  } catch (error) {
    console.error('Failed to load ladder chart data', error)
  } finally {
    ladderLoading.value = false
  }
}

const loadScatterData = async () => {
  scatterLoading.value = true
  try {
    const data = await getScatterChartData(scatterXMetric.value, scatterYMetric.value, modelCategory.value)
    scatterRecords.value = data.data || []
    const xMetric = data.x_metric || scatterXMetric.value
    const yMetric = data.y_metric || scatterYMetric.value

    const xValues = scatterRecords.value.map(item => toDisplayMetricNumber(item.x, xMetric)).filter(v => Number.isFinite(v))
    const yValues = scatterRecords.value.map(item => toDisplayMetricNumber(item.y, yMetric)).filter(v => Number.isFinite(v))
    const xRange = calcAxisRange(xValues)
    const yRange = calcAxisRange(yValues)
    
    const scatterData = data.data.map((item, index) => {
      const color = getModelColor(item.model_name, index)
      return {
        value: [toDisplayMetricNumber(item.x, xMetric), toDisplayMetricNumber(item.y, yMetric)],
        rawX: Number(item.x),
        rawY: Number(item.y),
        modelName: item.model_name,
        itemStyle: {
          color,
          shadowColor: color
        },
        label: {
          show: true,
          color
        }
      }
    }).filter((item) => Number.isFinite(item.value[0]) && Number.isFinite(item.value[1]))

    const paretoFront = buildParetoFront(scatterData, xMetric, yMetric)
    const paretoModelNames = new Set(paretoFront.map((item) => item.modelName))
    const displayScatterData = scatterData.map((item) => {
      const isParetoOptimal = paretoModelNames.has(item.modelName)
      return {
        ...item,
        isParetoOptimal,
        symbolSize: isParetoOptimal ? 24 : 18,
        itemStyle: {
          ...item.itemStyle,
          borderColor: isParetoOptimal ? '#facc15' : 'rgba(248, 250, 252, 0.85)',
          borderWidth: isParetoOptimal ? 3 : 1,
          shadowColor: isParetoOptimal ? '#facc15' : item.itemStyle.shadowColor,
          shadowBlur: isParetoOptimal ? 24 : 16
        },
        label: {
          ...item.label,
          fontWeight: isParetoOptimal ? 700 : 500
        }
      }
    })
    
    scatterChartOption.value = {
      ...scatterChartOption.value,
      title: {
        text: getScatterMetricTitle(xMetric, yMetric),
        subtext: paretoFront.length ? 'Pareto-optimal models are highlighted in gold' : '',
        left: 'center'
      },
      xAxis: {
        ...scatterChartOption.value.xAxis,
        name: getMetricName(xMetric),
        min: xRange.min,
        max: xRange.max
      },
      yAxis: {
        ...scatterChartOption.value.yAxis,
        name: getMetricName(yMetric),
        min: yRange.min,
        max: yRange.max
      },
      series: [
        {
          ...scatterChartOption.value.series[0],
          data: displayScatterData
        }
      ]
    }
  } catch (error) {
    console.error('Failed to load scatter chart data', error)
  } finally {
    scatterLoading.value = false
  }
}

const syncMetricSelectionsForCategory = () => {
  const available = SCATTER_METRIC_OPTIONS.value.map((item) => item.value)
  if (!available.length) {
    ladderMetric.value = ''
    scatterMetricSelection.value = []
    scatterXMetric.value = ''
    scatterYMetric.value = ''
    return
  }

  const preferredLadder = available.includes('accuracy_total') ? 'accuracy_total' : available[0]
  if (!available.includes(ladderMetric.value)) {
    ladderMetric.value = preferredLadder
  }

  const selected = scatterMetricSelection.value.filter((metric) => available.includes(metric))
  for (const metric of available) {
    if (selected.length >= 2) break
    if (!selected.includes(metric)) {
      selected.push(metric)
    }
  }

  if (selected.length === 1) {
    selected.push(selected[0])
  }

  scatterMetricSelection.value = selected.slice(0, 2)
  scatterXMetric.value = scatterMetricSelection.value[0] || available[0]
  scatterYMetric.value = scatterMetricSelection.value[1] || scatterXMetric.value
}

const handleCategoryChange = () => {
  syncMetricSelectionsForCategory()
  loadMetricDetails()
  loadLadderData()
  if (showScatterChart.value) {
    loadScatterData()
  }
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

const toggleScatterMetric = (metric) => {
  if (!showScatterChart.value) {
    return
  }

  if (scatterMetricSelection.value.includes(metric)) {
    return
  }

  const selected = [...scatterMetricSelection.value]
  selected.push(metric)

  // Queue strategy: keep at most two metrics, and remove the oldest when a third is selected.
  while (selected.length > 2) {
    selected.shift()
  }

  scatterMetricSelection.value = selected
  scatterXMetric.value = selected[0]
  scatterYMetric.value = selected[1]
  loadScatterData()
}

const resolveClickedModelName = (params) => {
  return params?.data?.modelName || params?.name || ''
}

const handleChartSingleClick = (params) => {
  const clickedName = resolveClickedModelName(params)
  if (!clickedName) return
  selectedModelName.value = clickedName
  const info = buildModelInfo(clickedName)
  ElMessage.closeAll()
  ElMessage({
    type: 'info',
    duration: 2400,
    showClose: true,
    message: `${clickedName}: ${info.description || 'No description'}`
  })
}

const goModelDetail = (modelName) => {
  if (!modelName) return
  router.push({ path: `/kpi/models/${encodeURIComponent(modelName)}`, query: { category: modelCategory.value } })
}

const handleChartDoubleClick = (params) => {
  const clickedName = resolveClickedModelName(params)
  if (!clickedName) return
  goModelDetail(clickedName)
}

const openCompareDialog = () => {
  const names = availableModelNames.value
  compareModelA.value = selectedModelName.value || names[0] || ''
  compareModelB.value = names.find(name => name !== compareModelA.value) || ''
  showCompareDialog.value = true
}

const openCreateModelDialog = () => {
  editingModelName.value = ''
  modelForm.value = createDefaultModelForm(modelCategory.value)
  showModelDialog.value = true
}

const openUpdatePickerDialog = () => {
  if (!modelList.value.length) {
    ElMessage.warning('No existing model available for update')
    return
  }
  selectedUpdateModelName.value = modelList.value[0]?.model_name || ''
  showUpdatePickerDialog.value = true
}

const confirmUpdateModelSelection = () => {
  const target = modelList.value.find((row) => row.model_name === selectedUpdateModelName.value)
  if (!target) {
    ElMessage.warning('Please select an existing model')
    return
  }
  showUpdatePickerDialog.value = false
  openEditModelDialog(target)
}

const deleteModelRow = async (row) => {
  const targetName = row?.model_name
  if (!targetName) {
    return
  }

  try {
    await ElMessageBox.confirm(
      `Delete all KPI runs for model ${targetName} in category ${modelCategory.value}?`,
      'Delete Model',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )
  } catch {
    return
  }

  try {
    await deleteKPIModel(targetName, { model_category: modelCategory.value })
    ElMessage.success('Model deleted')

    const refreshTasks = [loadMetricDetails(), loadLadderData(), loadModelList()]
    if (showScatterChart.value) {
      refreshTasks.push(loadScatterData())
    }
    await Promise.all(refreshTasks)
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to delete model')
  }
}

const openEditModelDialog = (row) => {
  const targetCategory = row.model_category || modelCategory.value
  const metricDefs = getMetricDefsForCategory(targetCategory)
  const dynamicMetrics = {}
  metricDefs.forEach((metric) => {
    dynamicMetrics[metric.value] = toMetricNumber(getMetricValueByKey(row.metrics, metric.value))
  })

  editingModelName.value = row.model_name || ''
  modelForm.value = {
    model_category: targetCategory,
    model_name: row.model_name || '',
    source: row.source || '',
    model_size: row.model_size || '',
    description: row.description || '',
    test_date: row.test_date ? formatDateTimeForEdit(row.test_date) : '',
    test_platform: row.test_platform || '',
    test_version: row.test_version || '',
    test_condition: row.test_condition || '',
    metrics: dynamicMetrics
  }
  showModelDialog.value = true
}

const saveModelDialog = async () => {
  if (!modelForm.value.model_name?.trim()) {
    ElMessage.warning('Model name is required')
    return
  }

  const metrics = {}
  MODEL_FORM_METRICS.value.forEach((metric) => {
    const raw = modelForm.value.metrics?.[metric.value]
    if (raw === undefined || raw === null || raw === '') return
    const numeric = Number(raw)
    if (Number.isFinite(numeric)) {
      metrics[metric.value] = numeric
    }
  })

  if (!Object.keys(metrics).length) {
    ElMessage.warning('At least one metric value is required')
    return
  }

  const outOfRangeAccuracyMetric = Object.keys(metrics).find(
    (metricName) => isAccuracyMetric(metricName) && (metrics[metricName] < 0 || metrics[metricName] > 1)
  )
  if (outOfRangeAccuracyMetric) {
    ElMessage.warning('Accuracy values must be between 0 and 1')
    return
  }

  const payload = {
    model_category: modelForm.value.model_category || modelCategory.value,
    model_name: modelForm.value.model_name.trim(),
    source: modelForm.value.source || '',
    model_size: modelForm.value.model_size || '',
    description: modelForm.value.description || '',
    test_date: modelForm.value.test_date || null,
    test_platform: modelForm.value.test_platform || '',
    test_version: modelForm.value.test_version || '',
    test_condition: modelForm.value.test_condition || '',
    metrics
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
    selectedModelName.value = payload.model_name
    const refreshTasks = [loadMetricDetails(), loadLadderData(), loadModelList()]
    if (showScatterChart.value) {
      refreshTasks.push(loadScatterData())
    }
    await Promise.all(refreshTasks)
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to save model')
  } finally {
    modelDialogSaving.value = false
  }
}

const formatMetricValue = (value, metricName = '', options = {}) => {
  if (value === undefined || value === null || value === '') {
    return '--'
  }
  const alreadyDisplay = options?.alreadyDisplay === true
  const numeric = Number(value)
  const hasNumeric = Number.isFinite(numeric)
  const displayValue = hasNumeric
    ? (alreadyDisplay ? numeric : (isAccuracyMetric(metricName) ? numeric * 100 : numeric))
    : numeric
  const base = hasNumeric ? displayValue.toFixed(2) : String(value)
  const unit = METRIC_UNITS[metricName] || ''
  if (!unit) {
    return base
  }
  if (unit === '%') {
    return `${base}${unit}`
  }
  return `${base} ${unit}`
}

const toMetricNumber = (value) => {
  const numeric = Number(value)
  return Number.isFinite(numeric) ? numeric : 0
}

const formatDateTime = (value) => {
  if (!value) return '-'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return '-'
  return d.toLocaleString('en-US')
}

const formatDateTimeForEdit = (value) => {
  if (!value) return ''
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return ''
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')
  const ss = String(d.getSeconds()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd} ${hh}:${mi}:${ss}`
}

const getMetricName = (metric) => {
  const label = METRIC_LABEL_MAP[metric] || metric
  const unit = METRIC_UNITS[metric]
  if (!unit) {
    return label
  }
  return `${label} (${unit})`
}

onMounted(() => {
  syncMetricSelectionsForCategory()
  loadMetricDetails()
  loadLadderData()
  if (showScatterChart.value) {
    loadScatterData()
  }
  loadModelList()
})
</script>

<style scoped>
.kpi-container {
  width: 100%;
}

.chart {
  width: 100%;
}

.metric-card__value--small {
  font-size: 24px;
  line-height: 1.2;
}

.model-info-card {
  padding-bottom: 24px;
}

.model-info-card__top {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.model-info-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.model-info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(255, 255, 255, 0.03);
}

.model-info-item--full {
  grid-column: 1 / -1;
}

.model-info-item__label {
  color: rgba(148, 163, 184, 0.82);
  font-size: 12px;
}

.model-info-item__value {
  color: #f8fafc;
  font-size: 14px;
  font-weight: 600;
}

.model-info-item__value--multiline {
  line-height: 1.7;
  font-weight: 500;
}

.compare-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.row-actions {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.model-dialog-form :deep(.el-form-item__label) {
  white-space: nowrap;
}

.model-link-btn {
  appearance: none;
  border: none;
  background: transparent;
  display: inline-block;
  width: 100%;
  margin: 0;
  padding: 0;
  color: #7dd3fc;
  cursor: pointer;
  font-weight: 700;
  text-align: center;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.model-link-btn:hover {
  color: #bae6fd;
}

.model-link-btn:focus-visible {
  outline: 2px solid rgba(125, 211, 252, 0.75);
  outline-offset: 2px;
  border-radius: 4px;
}

.category-focus-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.category-focus {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.category-focus__eyebrow {
  color: #5eead4;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.category-focus__title {
  margin: 8px 0 0;
  font-size: 22px;
}

.category-focus__desc {
  margin: 8px 0 0;
  color: rgba(226, 232, 240, 0.74);
  font-size: 14px;
}

.category-select {
  width: 320px;
}

.category-description-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.category-description-item {
  padding: 14px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  background: rgba(255, 255, 255, 0.03);
  cursor: pointer;
  transition: all 0.2s ease;
}

.category-description-item:hover {
  border-color: rgba(96, 165, 250, 0.32);
  background: rgba(96, 165, 250, 0.09);
  transform: translateY(-1px);
}

.category-description-item.is-active {
  border-color: rgba(94, 234, 212, 0.36);
  background: rgba(94, 234, 212, 0.08);
}

.category-description-item:focus-visible {
  outline: 2px solid rgba(94, 234, 212, 0.8);
  outline-offset: 2px;
}

.metric-tag-group {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.metric-tag {
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(226, 232, 240, 0.86);
  border-radius: 999px;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.18s ease;
}

.metric-tag:hover {
  border-color: rgba(96, 165, 250, 0.34);
  background: rgba(96, 165, 250, 0.12);
  color: #ffffff;
}

.metric-tag.is-active {
  border-color: rgba(94, 234, 212, 0.48);
  background: rgba(94, 234, 212, 0.16);
  color: #5eead4;
}

.metric-tag:focus-visible {
  outline: 2px solid rgba(94, 234, 212, 0.9);
  outline-offset: 2px;
}

.scatter-selector-wrap {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.selector-hint {
  color: rgba(148, 163, 184, 0.82);
  font-size: 12px;
}

.category-description-item__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  font-weight: 700;
}

.category-description-item p {
  margin: 8px 0 0;
  color: rgba(226, 232, 240, 0.78);
  font-size: 13px;
  line-height: 1.65;
}

@media (max-width: 768px) {
  .scatter-selector-wrap {
    align-items: flex-start;
  }

  .model-info-card__top {
    flex-direction: column;
  }
}
</style>

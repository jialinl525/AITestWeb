<template>
  <div class="page-shell kpi-container">
    <section class="page-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">Model Performance</div>
        <h2 class="page-hero__title">KPI Smart Analytics Dashboard</h2>
        <p class="page-hero__desc">Compare model performance through a modern visualization surface to spot leading models, key changes, and trade-offs across metrics.</p>
      </div>
      <div class="page-hero__actions">
        <div class="glass-pill">Current Scope: all models in the selected category</div>
        <div class="glass-pill">Comparison Axes: {{ getMetricName(scatterXMetric) }} / {{ getMetricName(scatterYMetric) }}</div>
      </div>
    </section>

    <el-card class="section-card category-focus-card">
      <div class="category-focus">
        <div class="category-focus__left">
          <div class="category-focus__eyebrow">Model Category</div>
          <h3 class="category-focus__title">Model Category Filter</h3>
          <p class="category-focus__desc">Current category: <strong>{{ modelCategory }}</strong>. The charts compare all models within this category only.</p>
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
            <el-tag v-if="key === modelCategory" size="small" type="success">Current</el-tag>
          </div>
          <p>{{ info }}</p>
        </article>
      </div>
    </el-card>

    <div class="metrics-grid metrics-grid--single">
      <article class="metric-card model-info-card accent-blue">
        <div class="model-info-card__top">
          <div>
            <div class="metric-card__label">Model Information</div>
            <div class="metric-card__value metric-card__value--small">{{ selectedModelInfo.name }}</div>
            <div class="metric-card__meta">Click a model in the ladder chart to sync the information shown here.</div>
          </div>
          <el-button type="primary" @click="openCompareDialog">Compare Models</el-button>
        </div>

        <div class="model-info-grid">
          <div class="model-info-item">
            <span class="model-info-item__label">Model Category</span>
            <span class="model-info-item__value">{{ modelCategory }}</span>
          </div>
          <div class="model-info-item">
            <span class="model-info-item__label">Current Metric</span>
            <span class="model-info-item__value">{{ getMetricName(ladderMetric) }}</span>
          </div>
          <div class="model-info-item model-info-item--full">
            <span class="model-info-item__label">Description</span>
            <span class="model-info-item__value model-info-item__value--multiline">{{ selectedModelInfo.description }}</span>
          </div>
          <div class="model-info-item">
            <span class="model-info-item__label">Source</span>
            <span class="model-info-item__value">{{ selectedModelInfo.source }}</span>
          </div>
          <div class="model-info-item">
            <span class="model-info-item__label">Model Size</span>
            <span class="model-info-item__value">{{ selectedModelInfo.modelSize }}</span>
          </div>
          <div class="model-info-item">
            <span class="model-info-item__label">Power Consumption</span>
            <span class="model-info-item__value">{{ formatMetricValue(selectedModelInfo.metrics.power_consumption) }}</span>
          </div>
          <div class="model-info-item">
            <span class="model-info-item__label">Latency</span>
            <span class="model-info-item__value">{{ formatMetricValue(selectedModelInfo.metrics.latency) }}</span>
          </div>
          <div class="model-info-item">
            <span class="model-info-item__label">Accuracy</span>
            <span class="model-info-item__value">{{ formatMetricValue(selectedModelInfo.metrics.accuracy_overall) }}</span>
          </div>
        </div>
      </article>
    </div>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>Model Performance Ladder</h3>
            <span class="section-title__meta">Vertical ranking of models in the same category under one core metric.</span>
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
        @click="handleLadderChartClick"
        style="height: 400px"
      />
    </el-card>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>Model Performance Scatter Plot</h3>
            <span class="section-title__meta">Observe the trade-offs and distribution between two core metrics for models in the same category.</span>
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
            <span class="selector-hint">Two metrics are selected by default; choosing a third removes the earliest selected metric.</span>
          </div>
        </div>
      </template>
      <v-chart
        class="chart"
        :option="scatterChartOption"
        v-loading="scatterLoading"
        style="height: 400px"
      />
    </el-card>

    <el-dialog v-model="showCompareDialog" title="Model Comparison" width="920px">
      <div class="compare-toolbar">
        <el-select v-model="compareModelA" placeholder="Select Model A" style="width: 240px">
          <el-option v-for="name in availableModelNames" :key="`a-${name}`" :label="name" :value="name" />
        </el-select>
        <el-select v-model="compareModelB" placeholder="Select Model B" style="width: 240px">
          <el-option v-for="name in availableModelNames" :key="`b-${name}`" :label="name" :value="name" />
        </el-select>
      </div>

      <el-table :data="compareRows" stripe empty-text="Select two different models to compare">
        <el-table-column prop="label" label="Parameter" width="220" />
        <el-table-column prop="modelA" :label="compareModelA || 'Model A'" min-width="220" />
        <el-table-column prop="modelB" :label="compareModelB || 'Model B'" min-width="220" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getKPIMetrics, getLadderChartData, getScatterChartData } from '../api/kpi'

const SCATTER_PALETTE = ['#22d3ee', '#60a5fa', '#a78bfa', '#f472b6', '#fb7185', '#f59e0b', '#34d399', '#facc15', '#38bdf8', '#818cf8']

const MODEL_CATEGORY_INFO = {
  ASR: 'Automatic Speech Recognition. Focuses on recognition accuracy, real-time performance, and resource usage for speech-to-text scenarios.',
  TTS: 'Text To Speech. Focuses on naturalness, latency, and power efficiency for spoken output scenarios.',
  Translation: 'Text translation models. Focus on multilingual translation accuracy, end-to-end latency, and deployment cost.',
  'VoicecallTranslation Solution': 'Real-time voice call translation solutions. Focus on latency, stability, and overall translation quality in call scenarios.'
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

const LADDER_METRIC_OPTIONS = [
  { label: 'Power Consumption', value: 'power_consumption' },
  { label: 'Latency', value: 'latency' },
  { label: 'Accuracy', value: 'accuracy_overall' }
]

const SCATTER_METRIC_OPTIONS = [
  { label: 'Power Consumption', value: 'power_consumption' },
  { label: 'Latency', value: 'latency' },
  { label: 'Accuracy', value: 'accuracy_overall' }
]

const getModelColor = (modelName, index) => {
  const seed = [...(modelName || '')].reduce((sum, ch) => sum + ch.charCodeAt(0), 0)
  return SCATTER_PALETTE[(seed + index) % SCATTER_PALETTE.length]
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
      min: Number((minVal - pad).toFixed(4)),
      max: Number((maxVal + pad).toFixed(4))
    }
  }

  const span = maxVal - minVal
  const pad = span * 0.18

  return {
    min: Number((minVal - pad).toFixed(4)),
    max: Number((maxVal + pad).toFixed(4))
  }
}

const ladderLoading = ref(false)
const scatterLoading = ref(false)
const ladderMetric = ref('accuracy_overall')
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

  return [
    { label: 'Model Category', modelA: modelCategory.value, modelB: modelCategory.value },
    { label: 'Description', modelA: modelAInfo.description, modelB: modelBInfo.description },
    { label: 'Source', modelA: modelAInfo.source, modelB: modelBInfo.source },
    { label: 'Model Size', modelA: modelAInfo.modelSize, modelB: modelBInfo.modelSize },
    { label: 'Power Consumption', modelA: formatMetricValue(modelAInfo.metrics.power_consumption), modelB: formatMetricValue(modelBInfo.metrics.power_consumption) },
    { label: 'Latency', modelA: formatMetricValue(modelAInfo.metrics.latency), modelB: formatMetricValue(modelBInfo.metrics.latency) },
    { label: 'Accuracy', modelA: formatMetricValue(modelAInfo.metrics.accuracy_overall), modelB: formatMetricValue(modelBInfo.metrics.accuracy_overall) },
    { label: 'Accuracy - English', modelA: formatMetricValue(modelAInfo.metrics.accuracy_en), modelB: formatMetricValue(modelBInfo.metrics.accuracy_en) },
    { label: 'Accuracy - Chinese', modelA: formatMetricValue(modelAInfo.metrics.accuracy_zh), modelB: formatMetricValue(modelBInfo.metrics.accuracy_zh) },
    { label: 'Accuracy - Spanish', modelA: formatMetricValue(modelAInfo.metrics.accuracy_es), modelB: formatMetricValue(modelBInfo.metrics.accuracy_es) }
  ]
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
    left: 'center',
    textStyle: {
      color: '#f8fafc',
      fontSize: 18,
      fontWeight: 700
    }
  },
  tooltip: {
    trigger: 'item',
    formatter: (params) => {
      return `${params.data.modelName}<br/>${getMetricName(scatterXMetric.value)}: ${params.data.value[0]}<br/>${getMetricName(scatterYMetric.value)}: ${params.data.value[1]}`
    }
  },
  grid: {
    left: 30,
    right: 24,
    top: 70,
    bottom: 30,
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

  const sorted = [...ladderRecords.value].sort((a, b) => b.value - a.value)
  const avg = sorted.reduce((sum, item) => sum + item.value, 0) / sorted.length

  return {
    topModel: sorted[0].model_name,
    topValue: Number(sorted[0].value).toFixed(3),
    average: Number(avg).toFixed(3)
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

    const rawValues = ladderRecords.value.map(item => Number(item.value)).filter(v => Number.isFinite(v))
    const xRange = calcAxisRange(rawValues)
    
    const ladderRows = (data.data || []).slice().reverse()
    const modelNames = ladderRows.map(item => item.model_name)
    const values = ladderRows.map((item, index) => ({
      value: item.value,
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
        text: `${getMetricName(data.metric_name)} Ranking`,
        left: 'center'
      },
      xAxis: {
        ...ladderChartOption.value.xAxis,
        name: getMetricName(data.metric_name),
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

    const xValues = scatterRecords.value.map(item => Number(item.x)).filter(v => Number.isFinite(v))
    const yValues = scatterRecords.value.map(item => Number(item.y)).filter(v => Number.isFinite(v))
    const xRange = calcAxisRange(xValues)
    const yRange = calcAxisRange(yValues)
    
    const scatterData = data.data.map((item, index) => {
      const color = getModelColor(item.model_name, index)
      return {
        value: [item.x, item.y],
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
    })
    
    scatterChartOption.value = {
      ...scatterChartOption.value,
      title: {
        text: `${getMetricName(data.x_metric)} vs ${getMetricName(data.y_metric)}`,
        left: 'center'
      },
      xAxis: {
        ...scatterChartOption.value.xAxis,
        name: getMetricName(data.x_metric),
        min: xRange.min,
        max: xRange.max
      },
      yAxis: {
        ...scatterChartOption.value.yAxis,
        name: getMetricName(data.y_metric),
        min: yRange.min,
        max: yRange.max
      },
      series: [
        {
          ...scatterChartOption.value.series[0],
          data: scatterData
        }
      ]
    }
  } catch (error) {
    console.error('Failed to load scatter chart data', error)
  } finally {
    scatterLoading.value = false
  }
}

const handleCategoryChange = () => {
  loadMetricDetails()
  loadLadderData()
  loadScatterData()
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

const handleLadderChartClick = (params) => {
  const clickedName = params?.name
  if (!clickedName) return
  selectedModelName.value = clickedName
}

const openCompareDialog = () => {
  const names = availableModelNames.value
  compareModelA.value = selectedModelName.value || names[0] || ''
  compareModelB.value = names.find(name => name !== compareModelA.value) || ''
  showCompareDialog.value = true
}

const formatMetricValue = (value) => {
  if (value === undefined || value === null || value === '') {
    return '--'
  }
  const numeric = Number(value)
  return Number.isFinite(numeric) ? numeric.toFixed(3) : String(value)
}

const getMetricName = (metric) => {
  const map = {
    power_consumption: 'Power Consumption',
    latency: 'Latency',
    accuracy_overall: 'Accuracy',
    accuracy_en: 'Accuracy - English',
    accuracy_zh: 'Accuracy - Chinese',
    accuracy_es: 'Accuracy - Spanish'
  }
  return map[metric] || metric
}

onMounted(() => {
  loadMetricDetails()
  loadLadderData()
  loadScatterData()
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

.metrics-grid--single {
  grid-template-columns: 1fr;
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

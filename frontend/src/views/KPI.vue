<template>
  <div class="page-shell kpi-container">
    <section class="page-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">Model Performance</div>
        <h2 class="page-hero__title">KPI 智能分析看板</h2>
        <p class="page-hero__desc">以更现代的可视化方式比较模型表现，快速识别领先模型、关键波动和不同指标间的平衡关系。</p>
      </div>
      <div class="page-hero__actions">
        <div class="glass-pill">当前范围：同分类全部模型</div>
        <div class="glass-pill">横向对比维度：{{ getMetricName(scatterXMetric) }} / {{ getMetricName(scatterYMetric) }}</div>
      </div>
    </section>

    <el-card class="section-card category-focus-card">
      <div class="category-focus">
        <div class="category-focus__left">
          <div class="category-focus__eyebrow">Model Category</div>
          <h3 class="category-focus__title">模型类型筛选</h3>
          <p class="category-focus__desc">当前类型：<strong>{{ modelCategory }}</strong>。图表仅对比该类型下的全部模型。</p>
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
            <el-tag v-if="key === modelCategory" size="small" type="success">当前</el-tag>
          </div>
          <p>{{ info }}</p>
        </article>
      </div>
    </el-card>

    <div class="metrics-grid metrics-grid--single">
      <article class="metric-card model-info-card accent-blue">
        <div class="model-info-card__top">
          <div>
            <div class="metric-card__label">模型信息</div>
            <div class="metric-card__value metric-card__value--small">{{ selectedModelInfo.name }}</div>
            <div class="metric-card__meta">点击天梯图中的模型后，这里的信息会同步更新</div>
          </div>
          <el-button type="primary" @click="openCompareDialog">模型对比</el-button>
        </div>

        <div class="model-info-grid">
          <div class="model-info-item">
            <span class="model-info-item__label">模型分类</span>
            <span class="model-info-item__value">{{ modelCategory }}</span>
          </div>
          <div class="model-info-item">
            <span class="model-info-item__label">当前指标</span>
            <span class="model-info-item__value">{{ getMetricName(ladderMetric) }}</span>
          </div>
          <div class="model-info-item model-info-item--full">
            <span class="model-info-item__label">具体描述</span>
            <span class="model-info-item__value model-info-item__value--multiline">{{ selectedModelInfo.description }}</span>
          </div>
          <div class="model-info-item">
            <span class="model-info-item__label">来源</span>
            <span class="model-info-item__value">{{ selectedModelInfo.source }}</span>
          </div>
          <div class="model-info-item">
            <span class="model-info-item__label">模型大小</span>
            <span class="model-info-item__value">{{ selectedModelInfo.modelSize }}</span>
          </div>
          <div class="model-info-item">
            <span class="model-info-item__label">功耗</span>
            <span class="model-info-item__value">{{ formatMetricValue(selectedModelInfo.metrics.power_consumption) }}</span>
          </div>
          <div class="model-info-item">
            <span class="model-info-item__label">延迟</span>
            <span class="model-info-item__value">{{ formatMetricValue(selectedModelInfo.metrics.latency) }}</span>
          </div>
          <div class="model-info-item">
            <span class="model-info-item__label">准确率</span>
            <span class="model-info-item__value">{{ formatMetricValue(selectedModelInfo.metrics.accuracy_overall) }}</span>
          </div>
        </div>
      </article>
    </div>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>模型性能天梯图</h3>
            <span class="section-title__meta">同分类模型在单一核心指标下的纵向排名</span>
          </div>
          <div class="metric-tag-group" role="tablist" aria-label="天梯图指标选择">
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
            <h3>模型性能坐标图</h3>
            <span class="section-title__meta">观察同分类模型在两个核心指标之间的平衡关系与分布</span>
          </div>
          <div class="scatter-selector-wrap">
            <div class="metric-tag-group" role="group" aria-label="坐标图指标选择">
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
            <span class="selector-hint">默认 2 项；勾选第 3 项时自动取消最早勾选的 1 项</span>
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

    <el-dialog v-model="showCompareDialog" title="模型对比" width="920px">
      <div class="compare-toolbar">
        <el-select v-model="compareModelA" placeholder="选择模型 A" style="width: 240px">
          <el-option v-for="name in availableModelNames" :key="`a-${name}`" :label="name" :value="name" />
        </el-select>
        <el-select v-model="compareModelB" placeholder="选择模型 B" style="width: 240px">
          <el-option v-for="name in availableModelNames" :key="`b-${name}`" :label="name" :value="name" />
        </el-select>
      </div>

      <el-table :data="compareRows" stripe empty-text="请选择两个不同模型进行对比">
        <el-table-column prop="label" label="参数" width="220" />
        <el-table-column prop="modelA" :label="compareModelA || '模型 A'" min-width="220" />
        <el-table-column prop="modelB" :label="compareModelB || '模型 B'" min-width="220" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getKPIMetrics, getLadderChartData, getScatterChartData } from '../api/kpi'

const SCATTER_PALETTE = ['#22d3ee', '#60a5fa', '#a78bfa', '#f472b6', '#fb7185', '#f59e0b', '#34d399', '#facc15', '#38bdf8', '#818cf8']

const MODEL_CATEGORY_INFO = {
  ASR: 'Automatic Speech Recognition。关注语音转文本场景下的识别准确率、实时性与资源消耗。',
  TTS: 'Text To Speech。关注合成语音自然度、时延与功耗表现，适合语音播报类业务。',
  Translation: '文本翻译模型。关注多语言翻译准确率、端到端延迟与部署资源成本。',
  'VoicecallTranslation Solution': '通话实时翻译方案。关注通话场景中的实时性、稳定性和综合翻译质量。'
}

const MODEL_META_INFO = {
  'Model-A': {
    description: '面向通用语音识别优化的轻量化模型，强调实时转写与端侧部署能力。',
    source: 'Internal Benchmark Set A',
    modelSize: '1.2B'
  },
  'Model-B': {
    description: '面向语音合成的标准基线模型，兼顾音色稳定性与时延表现。',
    source: 'Internal TTS Baseline',
    modelSize: '980M'
  },
  'Model-C': {
    description: '多语言翻译模型，强调中英西班牙语三语互译的准确率与吞吐。',
    source: 'Translation Eval Pack',
    modelSize: '1.6B'
  },
  'Model-D': {
    description: '实时通话翻译方案模型，针对语音流式处理和链路稳定性做过优化。',
    source: 'Voicecall Solution Suite',
    modelSize: '2.1B'
  },
  'Model-E': {
    description: 'ASR 增强模型，重点优化复杂噪声场景下的识别鲁棒性。',
    source: 'ASR Robustness Set',
    modelSize: '1.4B'
  },
  'Model-F': {
    description: '新一代多语言翻译模型，强化长句语义保持与跨领域术语一致性。',
    source: 'Global Translation Benchmark v2',
    modelSize: '1.9B'
  }
}

const LADDER_METRIC_OPTIONS = [
  { label: '功耗', value: 'power_consumption' },
  { label: '延迟', value: 'latency' },
  { label: '准确率', value: 'accuracy_overall' }
]

const SCATTER_METRIC_OPTIONS = [
  { label: '功耗', value: 'power_consumption' },
  { label: '延迟', value: 'latency' },
  { label: '准确率', value: 'accuracy_overall' }
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
    description: '请在 MODEL_META_INFO 中补充该模型的具体描述。',
    source: '待补充',
    modelSize: '待补充'
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
    { label: '模型分类', modelA: modelCategory.value, modelB: modelCategory.value },
    { label: '具体描述', modelA: modelAInfo.description, modelB: modelBInfo.description },
    { label: '来源', modelA: modelAInfo.source, modelB: modelBInfo.source },
    { label: '模型大小', modelA: modelAInfo.modelSize, modelB: modelBInfo.modelSize },
    { label: '功耗', modelA: formatMetricValue(modelAInfo.metrics.power_consumption), modelB: formatMetricValue(modelBInfo.metrics.power_consumption) },
    { label: '延迟', modelA: formatMetricValue(modelAInfo.metrics.latency), modelB: formatMetricValue(modelBInfo.metrics.latency) },
    { label: '准确率', modelA: formatMetricValue(modelAInfo.metrics.accuracy_overall), modelB: formatMetricValue(modelBInfo.metrics.accuracy_overall) },
    { label: '准确率-英语', modelA: formatMetricValue(modelAInfo.metrics.accuracy_en), modelB: formatMetricValue(modelBInfo.metrics.accuracy_en) },
    { label: '准确率-中文', modelA: formatMetricValue(modelAInfo.metrics.accuracy_zh), modelB: formatMetricValue(modelBInfo.metrics.accuracy_zh) },
    { label: '准确率-西班牙语', modelA: formatMetricValue(modelAInfo.metrics.accuracy_es), modelB: formatMetricValue(modelBInfo.metrics.accuracy_es) }
  ]
})

const ladderChartOption = ref({
  title: {
    text: '模型性能排名',
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
    name: '指标值',
    scale: true,
    axisLabel: { color: 'rgba(226, 232, 240, 0.72)' },
    nameTextStyle: { color: 'rgba(226, 232, 240, 0.72)' },
    splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.12)' } }
  },
  yAxis: {
    type: 'category',
    data: [],
    name: '模型名称',
    axisLabel: { color: 'rgba(226, 232, 240, 0.72)' },
    nameTextStyle: { color: 'rgba(226, 232, 240, 0.72)' }
  },
  series: [
    {
      name: '性能指标',
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
    text: '模型性能对比',
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
      return `${params.data.modelName}<br/>${getMetricName(scatterXMetric.value)}：${params.data.value[0]}<br/>${getMetricName(scatterYMetric.value)}：${params.data.value[1]}`
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
    name: '功耗',
    scale: true,
    axisLabel: { color: 'rgba(226, 232, 240, 0.72)' },
    nameTextStyle: { color: 'rgba(226, 232, 240, 0.72)' },
    splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.12)' } }
  },
  yAxis: {
    type: 'value',
    name: '延迟',
    scale: true,
    axisLabel: { color: 'rgba(226, 232, 240, 0.72)' },
    nameTextStyle: { color: 'rgba(226, 232, 240, 0.72)' },
    splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.12)' } }
  },
  series: [
    {
      name: '模型性能',
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
    description: '请在 MODEL_META_INFO 中补充该模型的具体描述。',
    source: '待补充',
    modelSize: '待补充'
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
    console.error('加载模型详情失败', error)
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
        text: `${getMetricName(data.metric_name)}排名`,
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
    console.error('加载天梯图数据失败', error)
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
    console.error('加载散点图数据失败', error)
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

  // 队列策略：最多保留 2 个，勾选第 3 个时移除最早选择的
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
    power_consumption: '功耗',
    latency: '延迟',
    accuracy_overall: '准确率',
    accuracy_en: '准确率-英语',
    accuracy_zh: '准确率-中文',
    accuracy_es: '准确率-西班牙语'
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

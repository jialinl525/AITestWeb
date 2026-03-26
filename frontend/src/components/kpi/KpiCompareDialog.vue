<template>
  <el-dialog :model-value="visible" @update:model-value="$emit('update:visible', $event)" title="Multi-Model Comparison" width="960px">
    <div class="compare-setup">
      <div class="compare-setup__row">
        <span class="compare-setup__label">Models:</span>
        <el-select
          v-model="selectedModels"
          multiple collapse-tags collapse-tags-tooltip filterable
          style="flex: 1"
          placeholder="Select models to compare (default: latest 5)"
        >
          <el-option v-for="name in availableModelNames" :key="name" :label="name" :value="name" />
        </el-select>
      </div>
      <div class="compare-hint-row">
        <el-tag :type="chartType === 'none' ? 'warning' : 'success'" size="small">{{ chartHint }}</el-tag>
        <span class="compare-metric-count">{{ compareMetricDefs.length }} metric(s) for {{ modelCategory }}</span>
      </div>
    </div>

    <template v-if="selectedModels.length >= 2 && chartType !== 'none'">
      <v-chart :option="chartOption" style="height: 500px; margin-top: 16px" />
      <div v-if="chartType === 'radar' && bestModel" class="compare-best-label">
        🏆 Best Overall: <strong>{{ bestModel }}</strong> — largest coverage area across all metrics
      </div>
    </template>
    <div v-else-if="chartType === 'none'" class="compare-no-chart">
      Only 1 metric available for this model type. Use the ladder chart above for single-metric comparison.
    </div>
    <div v-else class="compare-no-chart">Please select at least 2 models to compare.</div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  HIGH_CONTRAST_PALETTE, hexToRgba, toDisplayMetricNumber, calcAxisRange,
  buildParetoFront, normalizeForRadar, computePolygonArea
} from '../../utils/kpiMetrics'

const props = defineProps({
  visible: { type: Boolean, default: false },
  modelCategory: { type: String, default: '' },
  availableModelNames: { type: Array, default: () => [] },
  metricsByModel: { type: Object, default: () => ({}) },
  compareMetricDefs: { type: Array, default: () => [] },
  latestModelList: { type: Array, default: () => [] },
  isLowerBetterMetric: { type: Function, required: true },
  getMetricValueByKey: { type: Function, required: true },
  getMetricName: { type: Function, required: true },
  formatMetricValue: { type: Function, required: true },
  lowerIsBetterSet: { type: Object, default: () => new Set() }
})

defineEmits(['update:visible'])

const selectedModels = ref([])

// When dialog opens, default to latest 5 models
watch(() => props.visible, (val) => {
  if (val) {
    const sorted = [...props.latestModelList].sort((a, b) => {
      const da = a.test_date ? new Date(a.test_date).getTime() : 0
      const db = b.test_date ? new Date(b.test_date).getTime() : 0
      return db - da
    })
    selectedModels.value = sorted.slice(0, 5).map(r => r.model_name)
  }
})

const chartType = computed(() => {
  const n = props.compareMetricDefs.length
  if (n <= 1) return 'none'
  if (n === 2) return 'scatter'
  return 'radar'
})

const chartHint = computed(() => {
  const n = props.compareMetricDefs.length
  if (n <= 1) return '1 metric — use ladder chart above'
  if (n === 2) return '2 metrics → Scatter plot with Pareto highlight'
  return `${n} metrics → Radar polygon comparison`
})

const bestModel = computed(() => {
  if (chartType.value !== 'radar' || selectedModels.value.length < 2) return ''
  const metrics = props.compareMetricDefs
  let best = null
  let bestArea = -1
  for (const modelName of selectedModels.value) {
    const values = normalizeForRadar(
      modelName, metrics, selectedModels.value,
      props.metricsByModel, props.getMetricValueByKey, props.lowerIsBetterSet
    )
    const area = computePolygonArea(values)
    if (area > bestArea) { bestArea = area; best = modelName }
  }
  return best || ''
})

const chartOption = computed(() => {
  const models = selectedModels.value
  const metrics = props.compareMetricDefs
  if (models.length < 2 || !metrics.length) return {}

  if (chartType.value === 'scatter') {
    const xMetric = metrics[0]
    const yMetric = metrics[1]

    const points = models.map((modelName, index) => {
      const mData = props.metricsByModel[modelName] || {}
      const xRaw = props.getMetricValueByKey(mData, xMetric.value)
      const yRaw = props.getMetricValueByKey(mData, yMetric.value)
      const xVal = toDisplayMetricNumber(xRaw)
      const yVal = toDisplayMetricNumber(yRaw)
      const color = HIGH_CONTRAST_PALETTE[index % HIGH_CONTRAST_PALETTE.length]
      return {
        value: [xVal, yVal], rawX: Number(xRaw), rawY: Number(yRaw), modelName,
        symbolSize: 18,
        itemStyle: { color, shadowColor: color, shadowBlur: 12, borderColor: 'rgba(248,250,252,0.7)', borderWidth: 1 }
      }
    }).filter(p => Number.isFinite(p.value[0]) && Number.isFinite(p.value[1]))

    const paretoFront = buildParetoFront(points, xMetric.value, yMetric.value, props.lowerIsBetterSet)
    const paretoNames = new Set(paretoFront.map(p => p.modelName))

    const displayPoints = points.map(p => ({
      ...p,
      symbolSize: paretoNames.has(p.modelName) ? 26 : 18,
      itemStyle: {
        ...p.itemStyle,
        borderColor: paretoNames.has(p.modelName) ? '#facc15' : 'rgba(248,250,252,0.7)',
        borderWidth: paretoNames.has(p.modelName) ? 3 : 1,
        shadowBlur: paretoNames.has(p.modelName) ? 24 : 12
      }
    }))

    const xVals = points.map(p => p.value[0])
    const yVals = points.map(p => p.value[1])
    const xRange = calcAxisRange(xVals)
    const yRange = calcAxisRange(yVals)
    const xDir = props.isLowerBetterMetric(xMetric.value) ? 'left' : 'right'
    const yDir = props.isLowerBetterMetric(yMetric.value) ? 'bottom' : 'top'

    return {
      backgroundColor: 'transparent',
      title: {
        text: `${props.getMetricName(xMetric.value)} vs ${props.getMetricName(yMetric.value)}`,
        subtext: `Best region: ${yDir}-${xDir}${paretoFront.length ? ' · Pareto-optimal models highlighted in gold' : ''}`,
        left: 'center',
        textStyle: { color: '#f8fafc', fontSize: 16, fontWeight: 700 },
        subtextStyle: { color: 'rgba(226,232,240,0.72)', fontSize: 12 }
      },
      tooltip: {
        trigger: 'item',
        formatter: params => {
          const d = params.data
          if (!d?.modelName) return ''
          const pareto = paretoNames.has(d.modelName) ? '<br/><strong>⭐ Pareto-optimal</strong>' : ''
          return `<strong>${d.modelName}</strong><br/>${props.getMetricName(xMetric.value)}: ${props.formatMetricValue(d.value[0], xMetric.value)}<br/>${props.getMetricName(yMetric.value)}: ${props.formatMetricValue(d.value[1], yMetric.value)}${pareto}`
        }
      },
      grid: { left: 30, right: 24, top: 80, bottom: 42, containLabel: true },
      xAxis: { type: 'value', name: props.getMetricName(xMetric.value), scale: true, min: xRange.min, max: xRange.max, axisLabel: { color: 'rgba(226,232,240,0.72)' }, nameTextStyle: { color: 'rgba(226,232,240,0.72)' }, splitLine: { lineStyle: { color: 'rgba(148,163,184,0.12)' } } },
      yAxis: { type: 'value', name: props.getMetricName(yMetric.value), scale: true, min: yRange.min, max: yRange.max, axisLabel: { color: 'rgba(226,232,240,0.72)' }, nameTextStyle: { color: 'rgba(226,232,240,0.72)' }, splitLine: { lineStyle: { color: 'rgba(148,163,184,0.12)' } } },
      series: [{ type: 'scatter', data: displayPoints, label: { show: true, formatter: params => params.data.modelName, position: 'top', color: '#cbd5e1' }, labelLayout: { hideOverlap: false, moveOverlap: 'shiftY' } }]
    }
  }

  // Radar (≥3 metrics)
  const normalizedData = models.map((modelName, index) => {
    const values = normalizeForRadar(modelName, metrics, models, props.metricsByModel, props.getMetricValueByKey, props.lowerIsBetterSet)
    const color = HIGH_CONTRAST_PALETTE[index % HIGH_CONTRAST_PALETTE.length]
    return { modelName, values, color, area: computePolygonArea(values) }
  })

  const bestModelName = bestModel.value
  const indicator = metrics.map(m => ({ name: m.label + (m.unit ? ` (${m.unit})` : ''), max: 100 }))
  const seriesData = normalizedData.map(({ modelName, values, color }) => {
    const isBest = modelName === bestModelName
    return {
      name: isBest ? `${modelName} ★` : modelName,
      value: values,
      lineStyle: { color, width: isBest ? 3 : 2 },
      areaStyle: { color: hexToRgba(color, isBest ? 0.38 : 0.15) },
      itemStyle: { color },
      symbol: 'circle',
      symbolSize: isBest ? 8 : 5
    }
  })

  return {
    backgroundColor: 'transparent',
    title: {
      text: `${props.modelCategory} — Multi-Metric Comparison`,
      subtext: `${metrics.length} metrics · ${models.length} models · Normalized 0–100 per metric`,
      left: 'center',
      textStyle: { color: '#f8fafc', fontSize: 16, fontWeight: 700 },
      subtextStyle: { color: 'rgba(226,232,240,0.72)', fontSize: 12 }
    },
    tooltip: {
      trigger: 'item',
      formatter: params => {
        const modelName = (params.name || '').replace(' ★', '')
        const lines = metrics.map(metric => {
          const rawVal = props.getMetricValueByKey(props.metricsByModel[modelName] || {}, metric.value)
          return `${metric.label}: ${props.formatMetricValue(rawVal, metric.value)}`
        })
        return `<strong>${modelName}</strong><br/>${lines.join('<br/>')}`
      }
    },
    legend: { data: seriesData.map(d => d.name), bottom: 0, textStyle: { color: 'rgba(226,232,240,0.9)', fontSize: 12 }, itemGap: 16 },
    radar: {
      indicator, shape: 'polygon', splitNumber: 4, center: ['50%', '48%'], radius: '60%',
      axisName: { color: '#e2e8f0', fontSize: 12, fontWeight: 600 },
      splitLine: { lineStyle: { color: 'rgba(148,163,184,0.2)' } },
      splitArea: { areaStyle: { color: ['rgba(255,255,255,0.02)', 'rgba(255,255,255,0.04)'] } },
      axisLine: { lineStyle: { color: 'rgba(148,163,184,0.2)' } }
    },
    series: [{ type: 'radar', data: seriesData }]
  }
})
</script>

<style scoped>
.compare-setup { display: flex; flex-direction: column; gap: 12px; }
.compare-setup__row { display: flex; align-items: center; gap: 12px; }
.compare-setup__label { font-size: 14px; font-weight: 600; color: rgba(226, 232, 240, 0.9); white-space: nowrap; }
.compare-hint-row { display: flex; align-items: center; gap: 12px; }
.compare-metric-count { font-size: 13px; color: rgba(148, 163, 184, 0.82); }
.compare-best-label {
  margin-top: 12px; padding: 10px 16px; border-radius: 10px;
  background: rgba(250, 204, 21, 0.12); border: 1px solid rgba(250, 204, 21, 0.3);
  color: #fde68a; font-size: 14px; text-align: center;
}
.compare-no-chart { padding: 40px 24px; text-align: center; font-size: 14px; color: rgba(148, 163, 184, 0.8); }

@media (max-width: 768px) {
  .compare-setup__row { flex-direction: column; align-items: flex-start; }
}
</style>

<template>
  <div class="bug-overview-content">
    <div class="metrics-grid metrics-grid--compact">
      <MetricCard :label="LT.metrics.total" :value="stats.total || 0" :meta="DT.metricsMeta.total" accent="blue" size="sm" />
      <MetricCard :label="LT.metrics.analysis" :value="stats.by_status?.analysis || 0" :meta="DT.metricsMeta.analysis" accent="yellow" size="sm" />
      <MetricCard :label="LT.metrics.other" :value="stats.by_status?.other || 0" :meta="DT.metricsMeta.other" accent="purple" size="sm" />
      <MetricCard :label="LT.metrics.fixed" :value="stats.by_status?.fixed || 0" :meta="DT.metricsMeta.fixed" accent="green" size="sm" />
    </div>

    <div class="bugs-overview-grid">
      <div class="bug-chart-panel">
        <div class="bug-chart-panel__title">Bug Distribution</div>
        <v-chart class="bug-pie-chart" :option="pieOption" autoresize />
      </div>
      <div class="bug-chart-panel">
        <div class="bug-chart-panel__title">Monthly Bug Trend</div>
        <v-chart class="bug-line-chart" :option="trendOption" autoresize />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import MetricCard from '../common/MetricCard.vue'
import { LabelText } from '../../texts/LabelText'
import { DescriptionText } from '../../texts/DescriptionText'

const props = defineProps({
  stats: { type: Object, default: () => ({}) }
})

const LT = LabelText.bugs
const DT = DescriptionText.bugs

const pieOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: {
    bottom: 0, left: 'center', icon: 'circle',
    textStyle: { color: 'rgba(226, 232, 240, 0.9)' }
  },
  series: [{
    type: 'pie',
    radius: ['48%', '72%'],
    center: ['50%', '42%'],
    label: { show: true, color: '#f8fafc', formatter: '{b}\n{d}%' },
    itemStyle: { borderColor: 'rgba(8, 15, 33, 0.92)', borderWidth: 4 },
    data: [
      { value: props.stats.by_status?.analysis || 0, name: 'Analysis', itemStyle: { color: '#f97316' } },
      { value: props.stats.by_status?.other || 0, name: 'Other', itemStyle: { color: '#60a5fa' } },
      { value: props.stats.by_status?.fixed || 0, name: 'Fixed', itemStyle: { color: '#34d399' } }
    ]
  }]
}))

const trendOption = computed(() => {
  const monthlyTrend = Array.isArray(props.stats.monthly_trend) ? props.stats.monthly_trend : []
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { top: 0, textStyle: { color: 'rgba(226, 232, 240, 0.9)' } },
    grid: { left: 24, right: 24, top: 48, bottom: 24, containLabel: true },
    xAxis: {
      type: 'category', boundaryGap: false,
      data: monthlyTrend.map(item => item.month),
      axisLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.4)' } },
      axisLabel: { color: 'rgba(226, 232, 240, 0.9)' }
    },
    yAxis: {
      type: 'value', minInterval: 1,
      axisLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.4)' } },
      splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.12)' } },
      axisLabel: { color: 'rgba(226, 232, 240, 0.9)' }
    },
    series: [
      {
        name: 'Total CR', type: 'line', smooth: true, symbol: 'circle', symbolSize: 8, showSymbol: true,
        data: monthlyTrend.map(item => item.total || 0),
        lineStyle: { width: 3, color: '#60a5fa' },
        itemStyle: { color: '#60a5fa' },
        areaStyle: { color: 'rgba(96, 165, 250, 0.12)' }
      },
      {
        name: 'Fixed CR', type: 'line', smooth: true, symbol: 'circle', symbolSize: 8, showSymbol: true,
        data: monthlyTrend.map(item => item.fixed || 0),
        lineStyle: { width: 3, color: '#34d399' },
        itemStyle: { color: '#34d399' },
        areaStyle: { color: 'rgba(52, 211, 153, 0.1)' }
      }
    ]
  }
})
</script>

<style scoped>
.bug-overview-content {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.metrics-grid--compact {
  gap: 10px;
}

.metrics-grid--compact :deep(.metric-card) {
  padding: 8px 12px;
  min-height: 68px;
  border-radius: 14px;
}

.metrics-grid--compact :deep(.metric-card__label) { font-size: 14px; }
.metrics-grid--compact :deep(.metric-card__value) { margin-top: 6px; font-size: 20px; }
.metrics-grid--compact :deep(.metric-card__meta) { margin-top: 4px; font-size: 10px; }

.bugs-overview-grid {
  display: grid;
  grid-template-columns: minmax(320px, 0.9fr) minmax(420px, 1.1fr);
  gap: 14px;
  align-items: stretch;
}

.bug-chart-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0;
}

.bug-chart-panel__title {
  color: #f8fafc;
  font-size: 15px;
  font-weight: 600;
}

.bug-pie-chart { width: 100%; height: 240px; }
.bug-line-chart { width: 100%; height: 240px; }

@media (max-width: 768px) {
  .bugs-overview-grid { grid-template-columns: 1fr; }
  .bug-pie-chart, .bug-line-chart { height: 260px; }
}
</style>

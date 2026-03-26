<template>
  <el-card class="section-card">
    <template #header>
      <div class="section-title">
        <div class="section-title__main">
          <h3>{{ LT.section.ladder }}</h3>
          <span class="section-title__meta">{{ DT.sectionMeta.ladder }}</span>
        </div>
        <div class="metric-tag-group" role="tablist">
          <button
            v-for="item in metricOptions"
            :key="item.value"
            type="button"
            class="metric-tag"
            :class="{ 'is-active': ladderMetric === item.value }"
            role="tab"
            :aria-selected="ladderMetric === item.value"
            @click="$emit('select-metric', item.value)"
          >
            {{ item.label }}
          </button>
        </div>
      </div>
    </template>
    <v-chart
      class="chart"
      :option="chartOption"
      v-loading="loading"
      @click="$emit('chart-click', $event)"
      @dblclick="$emit('chart-dblclick', $event)"
      style="height: 400px"
    />
  </el-card>
</template>

<script setup>
import { LabelText } from '../../texts/LabelText'
import { DescriptionText } from '../../texts/DescriptionText'

const LT = LabelText.kpi
const DT = DescriptionText.kpi

defineProps({
  chartOption: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
  metricOptions: { type: Array, default: () => [] },
  ladderMetric: { type: String, default: '' }
})

defineEmits(['select-metric', 'chart-click', 'chart-dblclick'])
</script>

<style scoped>
.chart { width: 100%; }

.metric-tag-group { display: inline-flex; align-items: center; gap: 10px; flex-wrap: wrap; }
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
.metric-tag:hover { border-color: rgba(96, 165, 250, 0.34); background: rgba(96, 165, 250, 0.12); color: #ffffff; }
.metric-tag.is-active { border-color: rgba(94, 234, 212, 0.48); background: rgba(94, 234, 212, 0.16); color: #5eead4; }
.metric-tag:focus-visible { outline: 2px solid rgba(94, 234, 212, 0.9); outline-offset: 2px; }
</style>

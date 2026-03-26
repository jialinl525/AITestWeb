<template>
  <div class="progress-overview-panels">
    <section class="overview-panel overview-panel--tasks">
      <div class="overview-panel__header">
        <div>
          <div class="overview-panel__eyebrow">Test Tasks</div>
          <h4 class="overview-panel__title">Execution status by task</h4>
        </div>
      </div>
      <div class="metrics-grid progress-overview-metrics progress-overview-metrics--tasks">
        <MetricCard label="Total Tasks" :value="stats.total" :meta="DT.metricsMeta.total" accent="white" size="md" />
        <MetricCard label="In Progress" :value="stats.inprogress" :meta="DT.metricsMeta.running" accent="yellow" size="md" />
        <MetricCard label="Completed" :value="stats.completed" :meta="DT.metricsMeta.completed" accent="green" size="md" />
      </div>
    </section>

    <section class="overview-panel overview-panel--cases">
      <div class="overview-panel__header">
        <div>
          <div class="overview-panel__eyebrow">Test Cases</div>
          <h4 class="overview-panel__title">Execution outcome by case</h4>
        </div>
      </div>
      <div class="metrics-grid progress-overview-metrics progress-overview-metrics--cases">
        <MetricCard label="Total Cases" :value="stats.totalCases" meta="All tracked verification cases" accent="white" size="md" />
        <MetricCard :label="LT.summary.passed" :value="`${stats.passedCases}(${stats.passedRate}%)`" meta="Validated successfully" accent="green" size="md" />
        <MetricCard :label="LT.summary.failed" :value="`${stats.failedCases}(${stats.failedRate}%)`" meta="Need fix or retest" accent="red" size="md" />
      </div>
    </section>
  </div>
</template>

<script setup>
import MetricCard from '../common/MetricCard.vue'
import { LabelText } from '../../texts/LabelText'
import { DescriptionText } from '../../texts/DescriptionText'

defineProps({
  stats: { type: Object, required: true }
})

const LT = LabelText.testProgress
const DT = DescriptionText.testProgress
</script>

<style scoped>
.progress-overview-panels {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 20px;
}

.overview-panel {
  padding: 12px;
  border-radius: 16px;
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.88), rgba(15, 23, 42, 0.74));
  border: 1px solid rgba(148, 163, 184, 0.16);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.overview-panel--tasks { border-color: rgba(96, 165, 250, 0.24); }
.overview-panel--cases { border-color: rgba(45, 212, 191, 0.24); }

.overview-panel__header {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
  text-align: center;
}

.overview-panel__eyebrow {
  color: rgba(148, 163, 184, 0.92);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 4px;
  text-align: center;
}

.overview-panel__title {
  margin: 0;
  color: #f8fafc;
  font-size: 15px;
  font-weight: 700;
  text-align: center;
}

.progress-overview-metrics { margin-bottom: 0; }

.progress-overview-metrics--tasks,
.progress-overview-metrics--cases {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

@media (max-width: 960px) {
  .progress-overview-panels { grid-template-columns: 1fr; }
  .progress-overview-metrics--tasks,
  .progress-overview-metrics--cases { grid-template-columns: 1fr; }
}

@media (max-width: 640px) {
  .overview-panel { padding: 10px; }
}
</style>

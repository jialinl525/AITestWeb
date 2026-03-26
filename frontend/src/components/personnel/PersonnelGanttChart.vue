<template>
  <div>
    <div class="gantt-header-controls">
      <el-radio-group v-model="localViewMode" size="small">
        <el-radio-button value="active">Active Only</el-radio-button>
        <el-radio-button value="full_year">Full Year</el-radio-button>
      </el-radio-group>
      <div class="gantt-legend">
        <span class="gantt-legend-chip gantt-legend-chip--test">Test FR</span>
        <span class="gantt-legend-chip gantt-legend-chip--work">Work Task</span>
        <span class="gantt-legend-chip gantt-legend-chip--completed">Completed</span>
        <span class="gantt-legend-chip gantt-legend-chip--overlap">Overlap</span>
        <span class="gantt-legend-chip gantt-legend-chip--overload">⚠ Overload &gt;5d/wk</span>
      </div>
    </div>

    <div v-if="allGanttRange.start" class="gantt-container">
      <div class="gantt-header-row">
        <div class="gantt-name-col"></div>
        <div class="gantt-track gantt-track--header">
          <div
            v-for="marker in ganttMonthMarkers"
            :key="marker.label"
            class="gantt-month-marker"
            :style="{ left: marker.left + '%', width: marker.width + '%' }"
          >{{ marker.label }}</div>
        </div>
      </div>

      <div v-for="person in workload" :key="person.user_id" class="gantt-person-row">
        <button type="button" class="gantt-name-col member-link" @click="emit('view-member', person.user_id)">
          {{ person.display_name }}
        </button>
        <div class="gantt-track">
          <template v-for="seg in getPersonWeeklyLoadBgs(person)" :key="seg.key">
            <el-tooltip placement="top" effect="dark">
              <template #content>
                <div class="gantt-load-tooltip">
                  <div class="gantt-load-tooltip__week">{{ seg.weekLabel }}</div>
                  <div :class="seg.isOverloaded ? 'gantt-load-tooltip__overload' : 'gantt-load-tooltip__normal'">
                    {{ seg.isOverloaded ? '⚠ Overloaded' : 'Overlap' }}: {{ seg.weekLoad }} / 5.0 manday
                  </div>
                </div>
              </template>
              <div class="gantt-week-bg" :class="seg.isOverloaded ? 'gantt-week-bg--overload' : 'gantt-week-bg--overlap'" :style="seg.style"></div>
            </el-tooltip>
          </template>

          <template v-if="getPersonTaskBars(person).length">
            <el-tooltip v-for="bar in getPersonTaskBars(person)" :key="bar._key" placement="top" effect="dark">
              <template #content>
                <div class="gantt-tooltip">
                  <div class="gantt-tooltip__title">{{ bar.task_label || bar.test_name }}</div>
                  <div class="gantt-tooltip__row">{{ formatDate(bar.period_start) }} ~ {{ formatDate(bar.period_end) }}</div>
                  <div class="gantt-tooltip__row">Allocated: {{ bar.estimated_hours || 0 }} manday</div>
                  <div class="gantt-tooltip__row">Status: {{ bar.status }}</div>
                </div>
              </template>
              <div class="gantt-bar" :class="bar.colorClass" :style="bar.style">
                <span v-if="bar.hoursLabel" class="gantt-bar__label">{{ bar.hoursLabel }}</span>
              </div>
            </el-tooltip>
          </template>
          <div v-else class="gantt-empty">No tasks</div>
        </div>
      </div>

      <div class="gantt-footer-row">
        <div class="gantt-name-col"></div>
        <div class="gantt-scale">
          <span>{{ formatDate(allGanttRange.start) }}</span>
          <span>{{ formatDate(allGanttRange.end) }}</span>
        </div>
      </div>
    </div>

    <div v-else class="gantt-no-data">
      No tasks with date information in {{ localViewMode === 'active' ? 'Active Only' : 'Full Year' }} mode.
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { formatDate } from '../../utils/formatters'

const props = defineProps({
  workload: { type: Array, default: () => [] },
  viewMode: { type: String, default: 'active' }
})

const emit = defineEmits(['view-member', 'update:viewMode'])

const localViewMode = ref(props.viewMode)
watch(localViewMode, (v) => emit('update:viewMode', v))
watch(() => props.viewMode, (v) => { localViewMode.value = v })

const ACTIVE_STATUSES = new Set(['inprogress', 'in_progress', 'planning', 'in progress', 'planned'])
const isTaskActiveStatus = (task) => {
  const s = (task.status || '').toLowerCase().replace(/[\s-]/g, '_')
  return ACTIVE_STATUSES.has(s) || s.includes('progress') || s === 'planning' || s === 'planned'
}

const isTaskVisibleInGantt = (task) => {
  if (!task.period_start) return false
  if (isTaskActiveStatus(task)) return true
  if (!task.period_end) return false
  if (localViewMode.value === 'active') return false
  const endDate = new Date(task.period_end)
  const cutoff = new Date(); cutoff.setDate(cutoff.getDate() - 365)
  return endDate >= cutoff
}

const allGanttRange = computed(() => {
  const allTasks = props.workload.flatMap(p => (p.tasks || []).filter(t => isTaskVisibleInGantt(t)))
  if (!allTasks.length) return { start: null, end: null, totalDays: 0 }
  const starts = allTasks.map(t => new Date(t.period_start))
  const ends = allTasks.map(t => new Date(t.period_end || new Date()))
  const start = new Date(Math.min(...starts))
  const end = new Date(Math.max(...ends))
  const totalDays = Math.max(1, Math.round((end - start) / 86400000) + 1)
  return { start, end, totalDays }
})

const ganttMonthMarkers = computed(() => {
  const { start, end, totalDays } = allGanttRange.value
  if (!start || !end || !totalDays) return []
  const markers = []
  const current = new Date(start.getFullYear(), start.getMonth(), 1)
  while (current <= end) {
    const monthStart = new Date(current)
    const monthEnd = new Date(current.getFullYear(), current.getMonth() + 1, 0)
    const clampedStart = monthStart < start ? start : monthStart
    const clampedEnd = monthEnd > end ? end : monthEnd
    const leftDays = Math.round((clampedStart - start) / 86400000)
    const widthDays = Math.round((clampedEnd - clampedStart) / 86400000) + 1
    markers.push({
      label: `${current.getFullYear()}/${String(current.getMonth() + 1).padStart(2, '0')}`,
      left: (leftDays / totalDays) * 100,
      width: (widthDays / totalDays) * 100
    })
    current.setMonth(current.getMonth() + 1)
  }
  return markers
})

const getPersonTaskBars = (person) => {
  const { start, totalDays } = allGanttRange.value
  if (!start || !totalDays) return []
  const tasks = (person.tasks || []).filter(t => isTaskVisibleInGantt(t))
  if (!tasks.length) return []
  return tasks.map((task, index) => {
    const taskStart = new Date(task.period_start)
    const taskEnd = task.period_end ? new Date(task.period_end) : new Date()
    const leftDays = Math.max(0, Math.round((taskStart - start) / 86400000))
    const widthDays = Math.max(1, Math.round((taskEnd - taskStart) / 86400000) + 1)
    const hours = task.estimated_hours || 0
    const barHeight = 20
    const status = (task.status || '').toLowerCase()
    let colorClass = 'gantt-bar--test'
    if (status === 'completed') colorClass = 'gantt-bar--completed'
    else if (task.task_kind === 'work_task') colorClass = 'gantt-bar--work'
    return {
      ...task,
      _key: `${task.task_kind || 'test'}-${task.id}-${index}`,
      colorClass,
      style: {
        left: `${(leftDays / totalDays) * 100}%`,
        width: `${Math.max((widthDays / totalDays) * 100, 0.8)}%`,
        height: `${barHeight}px`,
        top: `${(32 - barHeight) / 2}px`
      },
      hoursLabel: hours > 0 ? `${hours}d` : ''
    }
  })
}

const WEEK_CAPACITY = 5

const getPersonWeeklyLoadBgs = (person) => {
  const { start, totalDays } = allGanttRange.value
  if (!start || !totalDays) return []
  const tasks = (person.tasks || []).filter(t => isTaskVisibleInGantt(t))
  if (!tasks.length) return []
  const rangeEnd = new Date(start); rangeEnd.setDate(rangeEnd.getDate() + totalDays - 1)
  const firstMonday = new Date(start)
  const dow = firstMonday.getDay()
  firstMonday.setDate(firstMonday.getDate() + (dow === 0 ? -6 : 1 - dow))
  const segments = []
  const current = new Date(firstMonday)
  while (current <= rangeEnd) {
    const weekStart = new Date(current)
    const weekEnd = new Date(current); weekEnd.setDate(weekEnd.getDate() + 6)
    let weekLoad = 0, taskCount = 0
    for (const task of tasks) {
      const taskStart = new Date(task.period_start)
      const taskEnd = task.period_end ? new Date(task.period_end) : new Date()
      const taskDays = Math.max(1, Math.round((taskEnd - taskStart) / 86400000) + 1)
      const overlapStart = taskStart > weekStart ? taskStart : weekStart
      const overlapEnd = taskEnd < weekEnd ? taskEnd : weekEnd
      if (overlapStart <= overlapEnd) {
        const overlapDays = Math.round((overlapEnd - overlapStart) / 86400000) + 1
        weekLoad += ((task.estimated_hours || 0) / taskDays) * overlapDays
        taskCount++
      }
    }
    if (taskCount >= 3 || weekLoad > 4 || weekLoad > WEEK_CAPACITY) {
      const clampedStart = weekStart < start ? start : weekStart
      const clampedEnd = weekEnd > rangeEnd ? rangeEnd : weekEnd
      const leftDays = Math.max(0, Math.round((clampedStart - start) / 86400000))
      const widthDays = Math.max(1, Math.round((clampedEnd - clampedStart) / 86400000) + 1)
      segments.push({
        key: `wk-${weekStart.getTime()}`,
        isOverloaded: weekLoad > WEEK_CAPACITY,
        weekLoad: Math.round(weekLoad * 10) / 10,
        weekLabel: `${weekStart.getMonth() + 1}/${weekStart.getDate()} ~ ${weekEnd.getMonth() + 1}/${weekEnd.getDate()}`,
        style: {
          left: `${(leftDays / totalDays) * 100}%`,
          width: `${Math.max((widthDays / totalDays) * 100, 0.5)}%`
        }
      })
    }
    current.setDate(current.getDate() + 7)
  }
  return segments
}
</script>

<style scoped>
.gantt-header-controls { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; margin-bottom: 14px; }
.gantt-container { display: flex; flex-direction: column; gap: 3px; }

.gantt-header-row, .gantt-person-row, .gantt-footer-row {
  display: grid; grid-template-columns: 120px 1fr; gap: 12px; align-items: center;
}

.gantt-name-col {
  font-size: 13px; font-weight: 600; white-space: nowrap; overflow: hidden;
  text-overflow: ellipsis; text-align: right; color: #7dd3fc;
}

.gantt-track {
  position: relative; height: 32px;
  background: rgba(51, 65, 85, 0.35); border-radius: 6px; overflow: hidden;
}

.gantt-track--header { height: 20px; background: transparent; overflow: visible; }

.gantt-month-marker {
  position: absolute; top: 0; height: 100%;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; color: rgba(148, 163, 184, 0.9);
  border-left: 1px solid rgba(148, 163, 184, 0.2);
  overflow: hidden; white-space: nowrap;
}

.gantt-week-bg { position: absolute; top: 0; height: 100%; pointer-events: auto; cursor: default; z-index: 0; }
.gantt-week-bg--overlap { background: rgba(251, 191, 36, 0.22); border-left: 2px solid rgba(251, 191, 36, 0.5); border-right: 2px solid rgba(251, 191, 36, 0.5); }
.gantt-week-bg--overload { background: rgba(239, 68, 68, 0.32); border-left: 2px solid rgba(239, 68, 68, 0.8); border-right: 2px solid rgba(239, 68, 68, 0.8); box-shadow: inset 0 0 0 1px rgba(239, 68, 68, 0.4); }

.gantt-bar {
  position: absolute; border-radius: 4px; cursor: default; overflow: hidden;
  display: flex; align-items: center; padding: 0 5px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.35);
  transition: opacity 0.15s, transform 0.1s; z-index: 1;
}
.gantt-bar:hover { opacity: 0.88; transform: scaleY(1.08); z-index: 10; }
.gantt-bar--test { background: linear-gradient(90deg, rgba(96, 165, 250, 0.92), rgba(59, 130, 246, 0.92)); }
.gantt-bar--work { background: linear-gradient(90deg, rgba(251, 191, 36, 0.92), rgba(245, 158, 11, 0.92)); }
.gantt-bar--completed { background: linear-gradient(90deg, rgba(52, 211, 153, 0.92), rgba(16, 185, 129, 0.92)); }

.gantt-bar__label { font-size: 10px; font-weight: 700; color: rgba(255, 255, 255, 0.95); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; pointer-events: none; }
.gantt-empty { position: absolute; top: 50%; left: 8px; transform: translateY(-50%); font-size: 12px; color: rgba(148, 163, 184, 0.5); }
.gantt-no-data { padding: 24px; text-align: center; font-size: 13px; color: rgba(148, 163, 184, 0.7); }
.gantt-scale { display: flex; justify-content: space-between; font-size: 12px; color: rgba(148, 163, 184, 0.9); padding-top: 4px; }

.gantt-legend { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.gantt-legend-chip { display: inline-flex; align-items: center; padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: 600; color: rgba(248, 250, 252, 0.96); }
.gantt-legend-chip--test { background: rgba(59, 130, 246, 0.8); }
.gantt-legend-chip--work { background: rgba(245, 158, 11, 0.8); }
.gantt-legend-chip--completed { background: rgba(16, 185, 129, 0.8); }
.gantt-legend-chip--overlap { background: rgba(180, 130, 20, 0.85); border: 1px solid rgba(251, 191, 36, 0.6); }
.gantt-legend-chip--overload { background: rgba(185, 28, 28, 0.85); border: 1px solid rgba(239, 68, 68, 0.7); }

.member-link { appearance: none; border: none; background: transparent; padding: 0; margin: 0; color: #7dd3fc; font-weight: 700; text-align: right; cursor: pointer; text-decoration: underline; text-underline-offset: 2px; width: 100%; }
.member-link:hover { color: #bae6fd; }

.gantt-tooltip { max-width: 320px; }
.gantt-tooltip__title { font-size: 13px; font-weight: 700; color: rgba(248, 250, 252, 0.96); margin-bottom: 6px; word-break: break-word; }
.gantt-tooltip__row { font-size: 12px; color: rgba(226, 232, 240, 0.9); line-height: 1.6; }

.gantt-load-tooltip { max-width: 260px; }
.gantt-load-tooltip__week { font-size: 12px; font-weight: 700; color: rgba(253, 230, 138, 0.96); margin-bottom: 4px; }
.gantt-load-tooltip__normal { font-size: 12px; color: rgba(226, 232, 240, 0.9); }
.gantt-load-tooltip__overload { font-size: 12px; font-weight: 700; color: rgba(252, 165, 165, 0.96); }
</style>

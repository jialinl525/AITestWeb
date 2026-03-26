<template>
  <el-table
    ref="tableRef"
    :data="workload"
    stripe
    class="full-width-table"
    style="width: 100%"
    :fit="true"
    table-layout="auto"
    @expand-change="handleExpandChange"
  >
    <el-table-column type="expand">
      <template #default="{ row }">
        <div class="member-task-grid">
          <div class="member-task-grid__head" :class="{ 'member-task-grid__head--readonly': !canEdit }">
            <div>Current Task</div>
            <div>{{ LT.table.partDescription }}</div>
            <div>{{ LT.table.startDate }}</div>
            <div>{{ LT.table.endDate }}</div>
            <div>{{ LT.table.status }}</div>
            <div>{{ LT.table.progress }}</div>
            <div>{{ LT.table.allocatedManday }}</div>
            <div v-if="canEdit">{{ LT.table.actions }}</div>
          </div>

          <div v-if="!getVisibleTaskRows(row).length" class="member-task-grid__empty">No tasks</div>

          <template v-for="group in getTaskGroups(row)" :key="group.key">
            <div v-if="group.tasks.length" class="member-task-group-title">{{ group.label }}</div>
            <div
              v-for="task in group.tasks"
              :key="task._row_key"
              class="member-task-grid__row"
              :class="{ 'member-task-grid__row--readonly': !canEdit }"
            >
              <div class="member-task-grid__cell member-task-grid__cell--task" :title="formatTaskName(task)">{{ formatTaskName(task) }}</div>
              <div class="member-task-grid__cell" :title="getPartDescription(task)">{{ getPartDescription(task) }}</div>
              <div class="member-task-grid__cell">{{ formatDate(task.start_date) }}</div>
              <div class="member-task-grid__cell">{{ formatDate(task.end_date) }}</div>
              <div class="member-task-grid__cell">
                <el-tag size="small" :type="getTaskStatusTagType(task.status)">{{ getTaskStatusText(task.status) }}</el-tag>
              </div>
              <div class="member-task-grid__cell">{{ formatPercent(task.progress) }}</div>
              <div class="member-task-grid__cell">{{ formatManday(task.estimated_hours) }}</div>
              <div v-if="canEdit" class="member-task-grid__cell member-task-grid__cell--actions">
                <el-button v-if="task.task_kind === 'test'" size="small" @click="emit('open-allocation', task)">{{ BT.allocateManday }}</el-button>
              </div>
            </div>
          </template>
        </div>
      </template>
    </el-table-column>

    <el-table-column :label="LT.table.member" min-width="220">
      <template #default="{ row }">
        <button type="button" class="member-link" @click="emit('view-member', row.user_id)">
          {{ row.display_name }}
        </button>
      </template>
    </el-table-column>
    <el-table-column prop="username" :label="LT.table.username" min-width="180" />
    <el-table-column :label="LT.table.taskCount" min-width="180">
      <template #default="{ row }">
        <div>{{ row.task_count }}</div>
        <div class="task-count-breakdown">FR {{ row.test_task_count || 0 }} / Other {{ row.other_task_count || 0 }}</div>
      </template>
    </el-table-column>
    <el-table-column :label="LT.table.completedTasks" min-width="120">
      <template #default="{ row }">{{ getCompletedTasks(row) }}</template>
    </el-table-column>
    <el-table-column prop="overlap_count" :label="LT.table.overlapGroups" min-width="130">
      <template #default="{ row }">
        <el-tag :type="getOverlapTagType(row.overlap_count)">{{ row.overlap_count || 0 }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="total_estimated_hours" :label="LT.table.allocatedManday" min-width="140">
      <template #default="{ row }">{{ Number(row.total_estimated_hours || 0).toFixed(1) }} manday</template>
    </el-table-column>
    <el-table-column label="Detail" width="120">
      <template #default="{ row }">
        <el-button size="small" @click.stop="toggleExpand(row)">{{ isExpanded(row.user_id) ? 'Collapse' : 'Expand' }}</el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup>
import { ref } from 'vue'
import { LabelText } from '../../texts/LabelText'
import { ButtonText } from '../../texts/ButtonText'
import { DescriptionText } from '../../texts/DescriptionText'
import { formatDate, formatManday as formatMandayValue, formatPercent } from '../../utils/formatters'
import { getTaskStatusTagType, getTaskStatusText } from '../../utils/taskStatus'
import { formatTaskLabel } from '../../utils/taskDisplay'

defineProps({
  workload: { type: Array, default: () => [] },
  canEdit: { type: Boolean, default: false }
})

const emit = defineEmits(['view-member', 'open-allocation'])

const LT = LabelText.personnel
const BT = ButtonText.personnel
const DT = DescriptionText.personnel

const tableRef = ref(null)
const expandedUserIds = ref([])

const formatManday = (value) => formatMandayValue(value)
const formatTaskName = (task) => formatTaskLabel(task)

const getPartDescription = (task) => {
  const text = String(task?.part_description || '').trim()
  return text || DT?.fallback?.unassignedPart || '-'
}

const getCompletedTasks = (row) =>
  (row.tasks || []).filter(task => String(task.status || '').toLowerCase() === 'completed').length

const getOverlapTagType = (count) => {
  const num = Number(count || 0)
  if (num >= 5) return 'danger'
  if (num >= 3) return 'warning'
  return 'success'
}

const toDateTime = (value, endOfDay = false) => {
  if (!value) return null
  const normalized = typeof value === 'string' && value.length <= 10
    ? `${value}${endOfDay ? 'T23:59:59' : 'T00:00:00'}` : value
  const date = new Date(normalized)
  return Number.isNaN(date.getTime()) ? null : date
}

const ACTIVE_STATUSES = new Set(['inprogress', 'in_progress', 'planning', 'in progress', 'planned'])
const isTaskActiveStatus = (task) => {
  const s = (task.status || '').toLowerCase().replace(/[\s-]/g, '_')
  return ACTIVE_STATUSES.has(s) || s.includes('progress') || s === 'planning' || s === 'planned'
}

const isTaskVisibleInPersonnelList = (task) => {
  const now = new Date()
  const windowStart = new Date(now); windowStart.setDate(windowStart.getDate() - 14); windowStart.setHours(0, 0, 0, 0)
  const windowEnd = new Date(now); windowEnd.setDate(windowEnd.getDate() + 14); windowEnd.setHours(23, 59, 59, 999)
  const startDate = toDateTime(task?.start_date || task?.period_start, false)
  const rawEndValue = task?.end_date || task?.period_end
  const isActive = isTaskActiveStatus(task)
  const endDate = rawEndValue ? toDateTime(rawEndValue, true) : (isActive ? now : toDateTime(task?.start_date || task?.period_start, true))
  const isOngoing = startDate && endDate && startDate <= now && endDate >= now
  const startsSoon = startDate && startDate >= windowStart && startDate <= windowEnd
  const endsSoon = endDate && endDate >= windowStart && endDate <= windowEnd
  return Boolean(isOngoing || startsSoon || endsSoon)
}

const normalizeTaskRows = (tasks) => {
  if (!Array.isArray(tasks)) return []
  return tasks.map((task, index) => ({
    ...task,
    _row_key: `${task?.task_kind || 'test'}-${task?.id ?? 'na'}-${index}`
  }))
}

const getVisibleTaskRows = (row) => {
  return normalizeTaskRows(row?.tasks)
    .filter(isTaskVisibleInPersonnelList)
    .sort((a, b) => {
      const aStart = a?.start_date || a?.period_start || '9999-12-31'
      const bStart = b?.start_date || b?.period_start || '9999-12-31'
      if (aStart !== bStart) return String(aStart).localeCompare(String(bStart))
      return String(a?.task_label || a?.test_name || '').localeCompare(String(b?.task_label || b?.test_name || ''))
    })
}

const getTaskGroups = (row) => {
  const visibleTasks = getVisibleTaskRows(row)
  return [
    { key: 'test', label: 'Test FR', tasks: visibleTasks.filter(t => t.task_kind === 'test') },
    { key: 'other', label: 'Other Tasks', tasks: visibleTasks.filter(t => t.task_kind !== 'test') }
  ]
}

const isExpanded = (userId) => expandedUserIds.value.includes(Number(userId))

const handleExpandChange = (_row, expandedRows) => {
  expandedUserIds.value = (expandedRows || []).map(item => Number(item?.user_id)).filter(Number.isFinite)
}

const toggleExpand = (row) => {
  if (!tableRef.value || !row) return
  tableRef.value.toggleRowExpansion(row, !isExpanded(Number(row.user_id)))
}
</script>

<style scoped>
.full-width-table { width: 100%; }

.member-task-grid {
  margin: 10px 0;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 12px;
  overflow: hidden;
}

.member-task-grid__head,
.member-task-grid__row {
  display: grid;
  grid-template-columns: 2.1fr 1.5fr 1fr 1fr 0.9fr 0.8fr 0.9fr 0.9fr;
  gap: 0;
}

.member-task-grid__head--readonly,
.member-task-grid__row--readonly {
  grid-template-columns: 2.2fr 1.6fr 1fr 1fr 0.9fr 0.8fr 0.9fr;
}

.member-task-grid__head {
  background: rgba(255, 255, 255, 0.04);
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
}

.member-task-group-title {
  padding: 10px 12px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: rgba(125, 211, 252, 0.96);
  background: rgba(59, 130, 246, 0.08);
  border-top: 1px solid rgba(148, 163, 184, 0.12);
}

.member-task-grid__head > div {
  padding: 10px 8px;
  font-size: 12px;
  font-weight: 700;
  color: rgba(226, 232, 240, 0.9);
}

.member-task-grid__row {
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
}

.member-task-grid__row:last-child { border-bottom: none; }

.member-task-grid__cell {
  padding: 10px 8px;
  font-size: 13px;
  color: rgba(226, 232, 240, 0.92);
  word-break: break-word;
}

.member-task-grid__cell--task { font-weight: 600; }
.member-task-grid__cell--actions { display: flex; align-items: center; }
.member-task-grid__empty { padding: 12px; color: rgba(148, 163, 184, 0.9); font-size: 13px; }

.member-link {
  appearance: none; border: none; background: transparent; padding: 0; margin: 0;
  color: #7dd3fc; font-weight: 700; text-align: left; cursor: pointer;
  text-decoration: underline; text-underline-offset: 2px;
}

.member-link:hover { color: #bae6fd; }
.member-link:focus-visible { outline: 2px solid rgba(125, 211, 252, 0.7); outline-offset: 2px; border-radius: 4px; }

.task-count-breakdown { margin-top: 4px; font-size: 12px; color: rgba(148, 163, 184, 0.9); }
</style>

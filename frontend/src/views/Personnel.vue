<template>
  <div class="page-shell personnel-container">
    <section class="page-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">{{ LT.heroEyebrow }}</div>
        <h2 class="page-hero__title">{{ LT.heroTitle }}</h2>
        <p class="page-hero__desc">
          {{ DT.hero }}
        </p>
      </div>
      <div class="page-hero__actions">
        <div class="glass-pill">{{ LT.pills.members }} {{ members.length }}</div>
        <div class="glass-pill">{{ LT.pills.tasks }} {{ totalTasks }}</div>
        <div class="glass-pill">Test FR {{ totalTestTasks }}</div>
        <div class="glass-pill">Other Tasks {{ totalOtherTasks }}</div>
        <div class="glass-pill">{{ LT.pills.mandays }} {{ totalHours }} manday</div>
        <div class="glass-pill">{{ LT.pills.overlaps }} {{ totalOverlaps }}</div>
        <el-button @click="loadData">{{ BTCommon.refresh }}</el-button>
      </div>
    </section>

    <div class="metrics-grid">
      <article class="metric-card accent-blue">
        <div class="metric-card__label">{{ LT.metrics.members }}</div>
        <div class="metric-card__value">{{ members.length }}</div>
        <div class="metric-card__meta">{{ DT.metricsMeta.members }}</div>
      </article>
      <article class="metric-card accent-green">
        <div class="metric-card__label">{{ LT.metrics.avgTasks }}</div>
        <div class="metric-card__value">{{ averageTasks }}</div>
        <div class="metric-card__meta">{{ DT.metricsMeta.avgTasks }}</div>
      </article>
      <article class="metric-card accent-orange">
        <div class="metric-card__label">{{ LT.metrics.totalManday }}</div>
        <div class="metric-card__value">{{ totalHours }} manday</div>
        <div class="metric-card__meta">{{ DT.metricsMeta.totalManday }}</div>
      </article>
      <article class="metric-card accent-red">
        <div class="metric-card__label">{{ LT.metrics.overlapGroups }}</div>
        <div class="metric-card__value">{{ totalOverlaps }}</div>
        <div class="metric-card__meta">{{ DT.metricsMeta.overlapGroups }}</div>
      </article>
    </div>

    <el-card v-if="canManagePersonnel" class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>Personnel Management</h3>
            <span class="section-title__meta">Only the admin account can create or delete users</span>
          </div>
          <div class="user-admin-actions">
            <el-button @click="loadManagementData">Refresh Users</el-button>
            <el-button type="primary" @click="openCreateUserDialog">New Member</el-button>
          </div>
        </div>
      </template>

      <el-table :data="managedUsers" stripe>
        <el-table-column prop="username" label="Username" min-width="160" />
        <el-table-column prop="display_name" label="Display Name" min-width="180" />
        <el-table-column prop="role" label="Role" min-width="120" />
        <el-table-column label="Status" min-width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? 'Active' : 'Inactive' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="140" fixed="right">
          <template #default="{ row }">
            <el-popconfirm title="Delete this user?" @confirm="handleDeleteUser(row)">
              <template #reference>
                <el-button type="danger" link>Delete</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>{{ LT.sectionTitle }}</h3>
            <span class="section-title__meta">{{ DT.sectionMeta }}</span>
          </div>
        </div>
      </template>

      <el-table
        ref="workloadTableRef"
        :data="workload"
        stripe
        class="full-width-table"
        style="width: 100%"
        :fit="true"
        table-layout="auto"
        @expand-change="handleExpandChange"
        @row-click="handleRowClickDebug"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="member-task-grid">
              <div class="member-task-grid__head" :class="{ 'member-task-grid__head--readonly': !canCreateOrEditTest() }">
                <div>Current Task</div>
                <div>{{ LT.table.partDescription }}</div>
                <div>{{ LT.table.startDate }}</div>
                <div>{{ LT.table.endDate }}</div>
                <div>{{ LT.table.status }}</div>
                <div>{{ LT.table.progress }}</div>
                <div>{{ LT.table.allocatedManday }}</div>
                <div v-if="canCreateOrEditTest()">{{ LT.table.actions }}</div>
              </div>

              <div v-if="!getVisibleTaskRows(row).length" class="member-task-grid__empty">No tasks</div>

              <template v-for="group in getTaskGroups(row)" :key="group.key">
                <div v-if="group.tasks.length" class="member-task-group-title">{{ group.label }}</div>
                <div
                  v-for="task in group.tasks"
                  :key="task._row_key"
                  class="member-task-grid__row"
                  :class="{ 'member-task-grid__row--readonly': !canCreateOrEditTest() }"
                >
                  <div class="member-task-grid__cell member-task-grid__cell--task" :title="formatTaskName(task)">{{ formatTaskName(task) }}</div>
                  <div class="member-task-grid__cell" :title="getPartDescription(task)">{{ getPartDescription(task) }}</div>
                  <div class="member-task-grid__cell">{{ formatDate(task.start_date) }}</div>
                  <div class="member-task-grid__cell">{{ formatDate(task.end_date) }}</div>
                  <div class="member-task-grid__cell">
                    <el-tag size="small" :type="getTaskStatusTagType(task.status)">{{ getTaskStatusText(task.status) }}</el-tag>
                  </div>
                  <div class="member-task-grid__cell">{{ formatProgress(task.progress) }}</div>
                  <div class="member-task-grid__cell">{{ formatManday(task.estimated_hours) }}</div>
                  <div v-if="canCreateOrEditTest()" class="member-task-grid__cell member-task-grid__cell--actions">
                    <el-button v-if="task.task_kind === 'test'" size="small" @click="openAllocationDialog(task)">{{ BT.allocateManday }}</el-button>
                  </div>
                </div>
              </template>
            </div>
          </template>
        </el-table-column>

        <el-table-column :label="LT.table.member" min-width="220">
          <template #default="{ row }">
            <button
              type="button"
              class="member-link"
              @click="viewMemberDetail(row.user_id)"
            >
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
    </el-card>

    <!-- Task Gantt Timeline for all members -->
    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>Task Timeline</h3>
            <span class="section-title__meta">
              <template v-if="allGanttRange.start">
                {{ formatDate(allGanttRange.start) }} ~ {{ formatDate(allGanttRange.end) }} · Bar height ∝ allocated manday
              </template>
              <template v-else>No tasks to display</template>
            </span>
          </div>
          <div class="gantt-header-controls">
            <el-radio-group v-model="ganttViewMode" size="small">
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
        </div>
      </template>

      <div v-if="allGanttRange.start" class="gantt-container">
        <!-- Month header -->
        <div class="gantt-header-row">
          <div class="gantt-name-col"></div>
          <div class="gantt-track gantt-track--header">
            <div
              v-for="marker in ganttMonthMarkers"
              :key="marker.label"
              class="gantt-month-marker"
              :style="{ left: marker.left + '%', width: marker.width + '%' }"
            >
              {{ marker.label }}
            </div>
          </div>
        </div>

        <!-- Person rows -->
        <div
          v-for="person in workload"
          :key="person.user_id"
          class="gantt-person-row"
        >
          <button
            type="button"
            class="gantt-name-col member-link"
            @click="viewMemberDetail(person.user_id)"
          >
            {{ person.display_name }}
          </button>
          <div class="gantt-track">
            <!-- Weekly load background (overlap / overload) -->
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
                <div
                  class="gantt-week-bg"
                  :class="seg.isOverloaded ? 'gantt-week-bg--overload' : 'gantt-week-bg--overlap'"
                  :style="seg.style"
                ></div>
              </el-tooltip>
            </template>

            <!-- Task bars -->
            <template v-if="getPersonTaskBars(person).length">
              <el-tooltip
                v-for="bar in getPersonTaskBars(person)"
                :key="bar._key"
                placement="top"
                effect="dark"
              >
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

        <!-- Scale footer -->
        <div class="gantt-footer-row">
          <div class="gantt-name-col"></div>
          <div class="gantt-scale">
            <span>{{ formatDate(allGanttRange.start) }}</span>
            <span>{{ formatDate(allGanttRange.end) }}</span>
          </div>
        </div>
      </div>

      <div v-else class="gantt-no-data">
        No tasks with date information in {{ ganttViewMode === 'active' ? 'Active Only' : 'Full Year' }} mode.
      </div>
    </el-card>

    <el-dialog v-model="showAllocationDialog" :title="`${LT.dialog.taskMandayAllocation} - ${allocationTask.test_name || ''}`" width="980px">
      <div class="muted-text allocation-summary">{{ LT.dialog.totalTaskManday }}: {{ Number(allocationTask.total_estimated_hours || 0).toFixed(1) }} manday</div>
      <el-table :data="allocationRows" size="small" stripe>
        <el-table-column :label="LT.dialog.tester" min-width="260">
          <template #default="{ row: item }">
            <el-select v-model="item.user_id" filterable style="width: 100%" :placeholder="DT.placeholders.selectMember">
              <el-option
                v-for="member in members"
                :key="member.id"
                :label="member.display_name || member.username"
                :value="member.id"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column :label="LT.dialog.allocatedManday" width="180">
          <template #default="{ row: item }">
            <el-input-number v-model="item.allocated_hours" :min="0" :step="0.5" :precision="1" style="width: 140px" />
          </template>
        </el-table-column>
        <el-table-column :label="LT.dialog.partDescription" min-width="300">
          <template #default="{ row: item }">
            <el-input
              v-model="item.part_description"
              type="textarea"
              :rows="2"
              resize="none"
              maxlength="300"
              show-word-limit
              :placeholder="DT.placeholders.partDescriptionExample"
            />
          </template>
        </el-table-column>
        <el-table-column :label="LT.dialog.actions" width="100">
          <template #default="{ $index }">
            <el-button type="danger" link @click="removeAllocationRow($index)">{{ BTCommon.delete }}</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="allocation-toolbar">
        <el-button @click="addAllocationRow">{{ BT.addAllocationRow }}</el-button>
      </div>
      <template #footer>
        <el-button @click="showAllocationDialog = false">{{ BTCommon.cancel }}</el-button>
        <el-button type="primary" :loading="savingAllocation" @click="saveAllocation">{{ BT.saveAllocation }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showCreateUserDialog" title="Create Member" width="620px">
      <el-form :model="createUserForm" label-width="120px">
        <el-form-item label="Username">
          <el-input v-model="createUserForm.username" maxlength="64" show-word-limit />
        </el-form-item>
        <el-form-item label="Display Name">
          <el-input v-model="createUserForm.display_name" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="Password">
          <el-input v-model="createUserForm.password" type="password" show-password maxlength="100" />
        </el-form-item>
        <el-form-item label="Role">
          <el-select v-model="createUserForm.role" style="width: 100%">
            <el-option label="Viewer" value="viewer" />
            <el-option label="Manager" value="manager" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateUserDialog = false">Cancel</el-button>
        <el-button type="primary" :loading="savingUser" @click="handleCreateUser">Create</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { LabelText } from '../texts/LabelText'
import { ButtonText } from '../texts/ButtonText'
import { DescriptionText } from '../texts/DescriptionText'
import { formatDate, formatManday as formatMandayValue, formatPercent } from '../utils/formatters'
import { getTaskStatusTagType, getTaskStatusText } from '../utils/taskStatus'
import { formatTaskLabel } from '../utils/taskDisplay'
import {
  getMembers,
  getWorkload,
  getTaskAllocations,
  updateTaskAllocations,
  getUsers,
  createUser,
  deleteUser
} from '../api/personnel'
import { canCreateOrEditTest, canManagePersonnelUsers } from '../stores/auth'

const router = useRouter()
const LT = LabelText.personnel
const BT = ButtonText.personnel
const BTCommon = ButtonText.common
const DT = DescriptionText.personnel
const members = ref([])
const workload = ref([])
const workloadTableRef = ref(null)
const expandedUserIds = ref([])
const managedUsers = ref([])

const showAllocationDialog = ref(false)
const savingAllocation = ref(false)
const showCreateUserDialog = ref(false)
const savingUser = ref(false)
const createUserForm = ref({
  username: '',
  display_name: '',
  password: '123456',
  role: 'viewer'
})

const allocationTask = ref({
  test_id: null,
  test_name: '',
  total_estimated_hours: 0
})
const allocationRows = ref([])

const totalHours = computed(() => {
  const sum = workload.value.reduce((acc, item) => acc + Number(item.total_estimated_hours || 0), 0)
  return Number(sum.toFixed(1))
})

const totalTasks = computed(() => {
  const taskIds = new Set()
  workload.value.forEach(item => {
    ;(item.tasks || []).forEach(task => taskIds.add(`${task.task_kind || 'test'}-${task.id}`))
  })
  return taskIds.size
})

const totalTestTasks = computed(() => {
  return workload.value.reduce((sum, item) => sum + Number(item.test_task_count || 0), 0)
})

const totalOtherTasks = computed(() => {
  return workload.value.reduce((sum, item) => sum + Number(item.other_task_count || 0), 0)
})

const totalOverlaps = computed(() => {
  return workload.value.reduce((sum, item) => sum + Number(item.overlap_count || 0), 0)
})

const canManagePersonnel = computed(() => canManagePersonnelUsers())

const averageTasks = computed(() => {
  if (!members.value.length) return 0
  const sum = workload.value.reduce((acc, item) => acc + Number(item.task_count || 0), 0)
  return Number((sum / members.value.length).toFixed(1))
})

const getCompletedTasks = (row) => {
  return (row.tasks || []).filter(task => String(task.status || '').toLowerCase() === 'completed').length
}

const getOverlapTagType = (count) => {
  const num = Number(count || 0)
  if (num >= 5) return 'danger'
  if (num >= 3) return 'warning'
  return 'success'
}

const formatProgress = (value) => {
  return formatPercent(value)
}

const formatManday = (value) => {
  return formatMandayValue(value)
}

const getPartDescription = (task) => {
  const text = String(task?.part_description || '').trim()
  if (text) return text
  return DT?.fallback?.unassignedPart || '-'
}

const formatTaskName = (task) => {
  return formatTaskLabel(task)
}

const normalizeTaskRows = (tasks) => {
  try {
    if (!Array.isArray(tasks)) return []
    return tasks.map((task, index) => ({
      ...task,
      _row_key: `${task?.task_kind || 'test'}-${task?.id ?? 'na'}-${index}`
    }))
  } catch (_error) {
    return []
  }
}

const toDateTime = (value, endOfDay = false) => {
  if (!value) return null
  const normalized = typeof value === 'string' && value.length <= 10
    ? `${value}${endOfDay ? 'T23:59:59' : 'T00:00:00'}`
    : value
  const date = new Date(normalized)
  return Number.isNaN(date.getTime()) ? null : date
}

const isTaskVisibleInPersonnelList = (task) => {
  const now = new Date()
  const windowStart = new Date(now)
  windowStart.setDate(windowStart.getDate() - 14)
  windowStart.setHours(0, 0, 0, 0)

  const windowEnd = new Date(now)
  windowEnd.setDate(windowEnd.getDate() + 14)
  windowEnd.setHours(23, 59, 59, 999)

  const startDate = toDateTime(task?.start_date || task?.period_start, false)

  // For active tasks with no end date, treat end as today so they always appear as ongoing
  const rawEndValue = task?.end_date || task?.period_end
  const isActive = isTaskActiveStatus(task)
  const endDate = rawEndValue
    ? toDateTime(rawEndValue, true)
    : (isActive ? now : toDateTime(task?.start_date || task?.period_start, true))

  const isOngoing = startDate && endDate && startDate <= now && endDate >= now
  const startsSoon = startDate && startDate >= windowStart && startDate <= windowEnd
  const endsSoon = endDate && endDate >= windowStart && endDate <= windowEnd

  return Boolean(isOngoing || startsSoon || endsSoon)
}

const getVisibleTaskRows = (row) => {
  const normalized = normalizeTaskRows(row?.tasks)
  return normalized
    .filter(isTaskVisibleInPersonnelList)
    .sort((first, second) => {
      const firstStart = first?.start_date || first?.period_start || '9999-12-31'
      const secondStart = second?.start_date || second?.period_start || '9999-12-31'
      if (firstStart !== secondStart) return String(firstStart).localeCompare(String(secondStart))
      return String(first?.task_label || first?.test_name || '').localeCompare(String(second?.task_label || second?.test_name || ''))
    })
}

const getTaskGroups = (row) => {
  const visibleTasks = getVisibleTaskRows(row)
  return [
    {
      key: 'test',
      label: 'Test FR',
      tasks: visibleTasks.filter(task => task.task_kind === 'test')
    },
    {
      key: 'other',
      label: 'Other Tasks',
      tasks: visibleTasks.filter(task => task.task_kind !== 'test')
    }
  ]
}

const isExpanded = (userId) => expandedUserIds.value.includes(Number(userId))

const handleExpandChange = (_row, expandedRows) => {
  expandedUserIds.value = (expandedRows || []).map(item => Number(item?.user_id)).filter(Number.isFinite)
}

const handleRowClickDebug = () => {}

const toggleExpand = (row) => {
  if (!workloadTableRef.value || !row) return
  const target = Number(row.user_id)
  const expanded = isExpanded(target)
  workloadTableRef.value.toggleRowExpansion(row, !expanded)
}

const viewMemberDetail = (userId) => {
  router.push({ path: `/personnel/${userId}` })
}

// ── Gantt Task Timeline (all members) ───────────────────────────────────────

// View mode: 'active' (default) = in_progress + planning only
//            'full_year' = active + ended within last 365 days
const ganttViewMode = ref('active')

const ACTIVE_STATUSES = new Set(['inprogress', 'in_progress', 'planning', 'in progress', 'planned'])

const isTaskActiveStatus = (task) => {
  const s = (task.status || '').toLowerCase().replace(/[\s-]/g, '_')
  return ACTIVE_STATUSES.has(s) || s.includes('progress') || s === 'planning' || s === 'planned'
}

const isTaskVisibleInGantt = (task) => {
  if (!task.period_start) return false
  // Active tasks always show even if end date is missing (e.g. ongoing work tasks)
  if (isTaskActiveStatus(task)) return true
  if (!task.period_end) return false
  if (ganttViewMode.value === 'active') return false
  // full_year: also include tasks that ended within last 365 days
  const endDate = new Date(task.period_end)
  const cutoff = new Date()
  cutoff.setDate(cutoff.getDate() - 365)
  return endDate >= cutoff
}

const allGanttRange = computed(() => {
  const allTasks = workload.value.flatMap(p =>
    (p.tasks || []).filter(t => isTaskVisibleInGantt(t))
  )
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

  const maxHours = Math.max(...tasks.map(t => t.estimated_hours || 0), 1)

  return tasks.map((task, index) => {
    const taskStart = new Date(task.period_start)
    const taskEnd = task.period_end ? new Date(task.period_end) : new Date()
    const leftDays = Math.max(0, Math.round((taskStart - start) / 86400000))
    const widthDays = Math.max(1, Math.round((taskEnd - taskStart) / 86400000) + 1)

    const hours = task.estimated_hours || 0
    const barHeight = 20 // uniform height for all bars

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

// Weekly load background: 1 week = 5 manday capacity
// For each week, sum up each task's daily manday contribution × overlap days
const WEEK_CAPACITY = 5

const getPersonWeeklyLoadBgs = (person) => {
  const { start, totalDays } = allGanttRange.value
  if (!start || !totalDays) return []

  const tasks = (person.tasks || []).filter(t => isTaskVisibleInGantt(t))
  if (!tasks.length) return []

  const rangeEnd = new Date(start)
  rangeEnd.setDate(rangeEnd.getDate() + totalDays - 1)

  // Find Monday of the first week
  const firstMonday = new Date(start)
  const dow = firstMonday.getDay() // 0=Sun
  const daysToMonday = dow === 0 ? -6 : 1 - dow
  firstMonday.setDate(firstMonday.getDate() + daysToMonday)

  const segments = []
  const current = new Date(firstMonday)

  while (current <= rangeEnd) {
    const weekStart = new Date(current)
    const weekEnd = new Date(current)
    weekEnd.setDate(weekEnd.getDate() + 6) // Sunday

    let weekLoad = 0
    let taskCount = 0

    for (const task of tasks) {
      const taskStart = new Date(task.period_start)
      const taskEnd = task.period_end ? new Date(task.period_end) : new Date()
      const taskDays = Math.max(1, Math.round((taskEnd - taskStart) / 86400000) + 1)

      const overlapStart = taskStart > weekStart ? taskStart : weekStart
      const overlapEnd = taskEnd < weekEnd ? taskEnd : weekEnd

      if (overlapStart <= overlapEnd) {
        const overlapDays = Math.round((overlapEnd - overlapStart) / 86400000) + 1
        const dailyRate = (task.estimated_hours || 0) / taskDays
        weekLoad += dailyRate * overlapDays
        taskCount++
      }
    }

    if (taskCount >= 3 || weekLoad > 4 || weekLoad > WEEK_CAPACITY) {
      const clampedStart = weekStart < start ? start : weekStart
      const clampedEnd = weekEnd > rangeEnd ? rangeEnd : weekEnd

      const leftDays = Math.max(0, Math.round((clampedStart - start) / 86400000))
      const widthDays = Math.max(1, Math.round((clampedEnd - clampedStart) / 86400000) + 1)
      const isOverloaded = weekLoad > WEEK_CAPACITY

      const weekLabel = `${weekStart.getMonth() + 1}/${weekStart.getDate()} ~ ${weekEnd.getMonth() + 1}/${weekEnd.getDate()}`

      segments.push({
        key: `wk-${weekStart.getTime()}`,
        isOverloaded,
        weekLoad: Math.round(weekLoad * 10) / 10,
        weekLabel,
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

// ────────────────────────────────────────────────────────────────────────────

const resetCreateUserForm = () => {
  createUserForm.value = {
    username: '',
    display_name: '',
    password: '123456',
    role: 'viewer'
  }
}

const loadManagementData = async () => {
  if (!canManagePersonnel.value) return
  try {
    const users = await getUsers()
    managedUsers.value = users
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to load personnel management data')
  }
}

const openCreateUserDialog = () => {
  resetCreateUserForm()
  showCreateUserDialog.value = true
}

const handleCreateUser = async () => {
  const username = (createUserForm.value.username || '').trim()
  const password = String(createUserForm.value.password || '')
  if (!username) {
    ElMessage.warning('Username is required')
    return
  }
  if (password.length < 6) {
    ElMessage.warning('Password must be at least 6 characters')
    return
  }

  savingUser.value = true
  try {
    await createUser({
      username,
      display_name: (createUserForm.value.display_name || '').trim() || username,
      password,
      role: createUserForm.value.role || 'viewer',
      is_active: true
    })
    ElMessage.success('User created successfully')
    showCreateUserDialog.value = false
    await loadData()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to create user')
  } finally {
    savingUser.value = false
  }
}

const handleDeleteUser = async (user) => {
  const userId = Number(user?.id)
  if (!userId) return
  try {
    await deleteUser(userId)
    ElMessage.success('User deleted successfully')
    await loadData()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to delete user')
  }
}

const loadData = async () => {
  try {
    const [memberData, workloadData] = await Promise.all([getMembers(), getWorkload()])
    members.value = memberData
    workload.value = workloadData
    if (canManagePersonnel.value) {
      await loadManagementData()
    } else {
      managedUsers.value = []
    }
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || DT.toast.loadFailed)
  }
}

const openAllocationDialog = async (task) => {
  try {
    const detail = await getTaskAllocations(task.id)
    allocationTask.value = {
      test_id: detail.test_id,
      test_name: detail.test_name,
      total_estimated_hours: detail.total_estimated_hours
    }
    allocationRows.value = (detail.allocations || []).map(item => ({
      user_id: item.user_id,
      allocated_hours: Number(item.allocated_hours || 0),
      part_description: item.part_description || ''
    }))
    if (!allocationRows.value.length) {
      allocationRows.value.push({ user_id: null, allocated_hours: 0, part_description: '' })
    }
    showAllocationDialog.value = true
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || DT.toast.loadTaskAllocationsFailed)
  }
}

const addAllocationRow = () => {
  allocationRows.value.push({ user_id: null, allocated_hours: 0, part_description: '' })
}

const removeAllocationRow = (index) => {
  allocationRows.value.splice(index, 1)
  if (!allocationRows.value.length) {
    allocationRows.value.push({ user_id: null, allocated_hours: 0, part_description: '' })
  }
}

const saveAllocation = async () => {
  if (!allocationTask.value.test_id) return

  const normalized = allocationRows.value
    .filter(item => item.user_id && Number(item.allocated_hours || 0) > 0)
    .map(item => ({
      user_id: Number(item.user_id),
      allocated_hours: Number(item.allocated_hours || 0),
      part_description: (item.part_description || '').trim()
    }))

  const userIds = normalized.map(item => item.user_id)
  if (new Set(userIds).size !== userIds.length) {
    ElMessage.warning(DT.toast.duplicateTester)
    return
  }

  savingAllocation.value = true
  try {
    await updateTaskAllocations(allocationTask.value.test_id, { allocations: normalized })
    ElMessage.success(DT.toast.saveSuccess)
    showAllocationDialog.value = false
    await loadData()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || DT.toast.saveFailed)
  } finally {
    savingAllocation.value = false
  }
}

onMounted(() => {
  loadData()
})

onBeforeUnmount(() => {})
</script>

<style scoped>
.personnel-container {
  width: 100%;
}

.full-width-table {
  width: 100%;
}

.personnel-container :deep(.full-width-table .el-table__inner-wrapper) {
  width: 100% !important;
}

.personnel-container :deep(.full-width-table .el-scrollbar__view) {
  width: 100% !important;
}

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

.member-task-grid__row:last-child {
  border-bottom: none;
}

.member-task-grid__cell {
  padding: 10px 8px;
  font-size: 13px;
  color: rgba(226, 232, 240, 0.92);
  word-break: break-word;
}

.member-task-grid__cell--task {
  font-weight: 600;
}

.member-task-grid__cell--actions {
  display: flex;
  align-items: center;
}

.member-task-grid__empty {
  padding: 12px;
  color: rgba(148, 163, 184, 0.9);
  font-size: 13px;
}

.member-link {
  appearance: none;
  border: none;
  background: transparent;
  padding: 0;
  margin: 0;
  color: #7dd3fc;
  font-weight: 700;
  text-align: left;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.task-count-breakdown {
  margin-top: 4px;
  font-size: 12px;
  color: rgba(148, 163, 184, 0.9);
}

.member-link:hover {
  color: #bae6fd;
}

.member-link:focus-visible {
  outline: 2px solid rgba(125, 211, 252, 0.7);
  outline-offset: 2px;
  border-radius: 4px;
}

.overlap-panel {
  width: 100%;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid rgba(148, 163, 184, 0.2);
}

.overlap-panel__title {
  font-size: 13px;
  margin-bottom: 8px;
  color: rgba(148, 163, 184, 0.92);
}

.allocation-summary {
  margin-bottom: 10px;
}

.allocation-toolbar {
  margin-top: 10px;
}

.user-admin-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ── Gantt Task Timeline ──────────────────────────────────────────────────── */

.gantt-header-controls {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.gantt-container {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.gantt-header-row,
.gantt-person-row,
.gantt-footer-row {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 12px;
  align-items: center;
}

.gantt-name-col {
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: right;
  color: #7dd3fc;
}

.gantt-track {
  position: relative;
  height: 32px;
  background: rgba(51, 65, 85, 0.35);
  border-radius: 6px;
  overflow: hidden;
}

.gantt-track--header {
  height: 20px;
  background: transparent;
  overflow: visible;
}

.gantt-month-marker {
  position: absolute;
  top: 0;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: rgba(148, 163, 184, 0.9);
  border-left: 1px solid rgba(148, 163, 184, 0.2);
  overflow: hidden;
  white-space: nowrap;
}

/* Weekly load backgrounds */
.gantt-week-bg {
  position: absolute;
  top: 0;
  height: 100%;
  pointer-events: auto;
  cursor: default;
  z-index: 0;
}

.gantt-week-bg--overlap {
  background: rgba(251, 191, 36, 0.22);
  border-left: 2px solid rgba(251, 191, 36, 0.5);
  border-right: 2px solid rgba(251, 191, 36, 0.5);
}

.gantt-week-bg--overload {
  background: rgba(239, 68, 68, 0.32);
  border-left: 2px solid rgba(239, 68, 68, 0.8);
  border-right: 2px solid rgba(239, 68, 68, 0.8);
  box-shadow: inset 0 0 0 1px rgba(239, 68, 68, 0.4);
}

.gantt-bar {
  position: absolute;
  border-radius: 4px;
  cursor: default;
  overflow: hidden;
  display: flex;
  align-items: center;
  padding: 0 5px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.35);
  transition: opacity 0.15s, transform 0.1s;
  z-index: 1;
}

.gantt-bar:hover {
  opacity: 0.88;
  transform: scaleY(1.08);
  z-index: 10;
}

.gantt-bar--test {
  background: linear-gradient(90deg, rgba(96, 165, 250, 0.92), rgba(59, 130, 246, 0.92));
}

.gantt-bar--work {
  background: linear-gradient(90deg, rgba(251, 191, 36, 0.92), rgba(245, 158, 11, 0.92));
}

.gantt-bar--completed {
  background: linear-gradient(90deg, rgba(52, 211, 153, 0.92), rgba(16, 185, 129, 0.92));
}

.gantt-bar__label {
  font-size: 10px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  pointer-events: none;
}

.gantt-empty {
  position: absolute;
  top: 50%;
  left: 8px;
  transform: translateY(-50%);
  font-size: 12px;
  color: rgba(148, 163, 184, 0.5);
}

.gantt-no-data {
  padding: 24px;
  text-align: center;
  font-size: 13px;
  color: rgba(148, 163, 184, 0.7);
}

.gantt-scale {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: rgba(148, 163, 184, 0.9);
  padding-top: 4px;
}

.gantt-legend {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.gantt-legend-chip {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  color: rgba(248, 250, 252, 0.96);
}

.gantt-legend-chip--test {
  background: rgba(59, 130, 246, 0.8);
}

.gantt-legend-chip--work {
  background: rgba(245, 158, 11, 0.8);
}

.gantt-legend-chip--completed {
  background: rgba(16, 185, 129, 0.8);
}

.gantt-legend-chip--overlap {
  background: rgba(180, 130, 20, 0.85);
  border: 1px solid rgba(251, 191, 36, 0.6);
}

.gantt-legend-chip--overload {
  background: rgba(185, 28, 28, 0.85);
  border: 1px solid rgba(239, 68, 68, 0.7);
}

.gantt-tooltip {
  max-width: 320px;
}

.gantt-tooltip__title {
  font-size: 13px;
  font-weight: 700;
  color: rgba(248, 250, 252, 0.96);
  margin-bottom: 6px;
  word-break: break-word;
}

.gantt-tooltip__row {
  font-size: 12px;
  color: rgba(226, 232, 240, 0.9);
  line-height: 1.6;
}

.gantt-load-tooltip {
  max-width: 260px;
}

.gantt-load-tooltip__week {
  font-size: 12px;
  font-weight: 700;
  color: rgba(253, 230, 138, 0.96);
  margin-bottom: 4px;
}

.gantt-load-tooltip__normal {
  font-size: 12px;
  color: rgba(226, 232, 240, 0.9);
}

.gantt-load-tooltip__overload {
  font-size: 12px;
  font-weight: 700;
  color: rgba(252, 165, 165, 0.96);
}
</style>

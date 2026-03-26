<template>
  <div class="page-shell detail-container">
    <section class="page-hero detail-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">{{ LT.heroEyebrow }}</div>
        <h2 class="page-hero__title">{{ LT.heroTitle }}</h2>
        <p class="page-hero__desc">{{ DT.hero }}</p>
      </div>
      <div class="page-hero__actions">
        <el-button v-if="memberDetail && canEditPersonnelProfile(memberDetail.username)" type="primary" @click="openProfileEditDialog">
          Edit Profile
        </el-button>
        <el-button @click="goBack">{{ BT.backToList }}</el-button>
      </div>
    </section>

    <el-card v-loading="loading" class="section-card detail-card">
      <template v-if="memberDetail">
        <div class="detail-header">
          <div>
            <h2>{{ memberDetail.display_name }}</h2>
            <p class="detail-subtitle">{{ LT.profile.username }}: {{ memberDetail.username }}</p>
            <p class="detail-subtitle">{{ LT.profile.email }}: {{ memberDetail.email || '-' }}</p>
          </div>
        </div>

        <div class="metrics-grid detail-metrics">
          <article class="metric-card accent-blue">
            <div class="metric-card__label">{{ LT.metrics.taskCount }}</div>
            <div class="metric-card__value">{{ memberDetail.task_count || 0 }}</div>
          </article>
          <article class="metric-card accent-green">
            <div class="metric-card__label">{{ LT.metrics.completedTasks }}</div>
            <div class="metric-card__value">{{ completedTasks }}</div>
          </article>
          <article class="metric-card accent-red">
            <div class="metric-card__label">{{ LT.metrics.overlapGroups }}</div>
            <div class="metric-card__value">{{ memberDetail.overlap_count || 0 }}</div>
            <div class="metric-card__meta">Max concurrent test FR periods</div>
          </article>
          <article class="metric-card accent-purple">
            <div class="metric-card__label">{{ LT.metrics.totalManday }}</div>
            <div class="metric-card__value">{{ formatManday(memberDetail.total_estimated_hours) }}</div>
          </article>
        </div>

        <el-card class="section-card detail-inner-card">
          <template #header>
            <div class="section-title">
              <div class="section-title__main">
                <h3>{{ LT.section.profile }}</h3>
                <span class="section-title__meta">{{ DT.sectionMeta.profile }}</span>
              </div>
            </div>
          </template>
          <el-descriptions :column="1" border class="detail-info detail-info--ratio">
            <el-descriptions-item :label="LT.profile.displayName">{{ memberDetail.display_name || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="LT.profile.username">{{ memberDetail.username || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="LT.profile.email">{{ memberDetail.email || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="LT.metrics.overlapGroups">{{ memberDetail.overlap_count || 0 }}</el-descriptions-item>
            <el-descriptions-item label="Task Breakdown">
              FR {{ memberDetail.test_task_count || 0 }} / Other {{ memberDetail.other_task_count || 0 }}
            </el-descriptions-item>
            <el-descriptions-item :label="LT.profile.responsibilities">
              <div class="profile-multiline">{{ memberDetail.responsibilities || '-' }}</div>
            </el-descriptions-item>
            <el-descriptions-item :label="LT.profile.specialtyTasks">
              <div class="profile-multiline">{{ memberDetail.specialty_tasks || '-' }}</div>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- Task Gantt Timeline -->
        <el-card class="section-card detail-inner-card">
          <template #header>
            <div class="section-title">
              <div class="section-title__main">
                <h3>Task Timeline</h3>
                <span class="section-title__meta">
                  <template v-if="ganttRange.start">
                    {{ formatDate(ganttRange.start) }} ~ {{ formatDate(ganttRange.end) }}
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

          <div v-if="ganttRange.start" class="gantt-container">
            <!-- Month header -->
            <div class="gantt-row gantt-row--header">
              <div class="gantt-label-col"></div>
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

            <!-- Single person task row -->
            <div class="gantt-row">
              <div class="gantt-label-col gantt-label-col--name">{{ memberDetail.display_name }}</div>
              <div class="gantt-track">
                <!-- Weekly load backgrounds -->
                <template v-for="seg in ganttWeeklyLoadBgs" :key="seg.key">
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
                <template v-if="ganttTaskBars.length">
                  <el-tooltip
                    v-for="bar in ganttTaskBars"
                    :key="bar._key"
                    placement="top"
                    effect="dark"
                  >
                    <template #content>
                      <div class="gantt-tooltip">
                        <div class="gantt-tooltip__title">{{ bar.task_label || bar.test_name }}</div>
                        <div class="gantt-tooltip__row">
                          {{ formatDate(bar.period_start) }} ~ {{ bar.period_end ? formatDate(bar.period_end) : 'Ongoing' }}
                        </div>
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
            <div class="gantt-row gantt-row--footer">
              <div class="gantt-label-col"></div>
              <div class="gantt-scale">
                <span>{{ formatDate(ganttRange.start) }}</span>
                <span>{{ formatDate(ganttRange.end) }}</span>
              </div>
            </div>
          </div>

          <div v-else class="gantt-no-data">
            No tasks with date information in {{ ganttViewMode === 'active' ? 'Active Only' : 'Full Year' }} mode.
          </div>
        </el-card>

        <el-card class="section-card detail-inner-card">
          <template #header>
            <div class="section-title">
              <div class="section-title__main">
                <h3>{{ LT.section.tasks }}</h3>
                <span class="section-title__meta">{{ DT.sectionMeta.tasks }}</span>
              </div>
            </div>
          </template>

          <el-table :data="visibleTasks" :row-key="taskRowKey" stripe>
            <el-table-column :label="LTP.table.task" min-width="280" show-overflow-tooltip>
              <template #default="{ row }">
                <button type="button" class="task-link" @click="goToTask(row)">{{ formatTaskName(row) }}</button>
              </template>
            </el-table-column>
            <el-table-column prop="part_description" :label="LTP.table.partDescription" min-width="220" show-overflow-tooltip>
              <template #default="{ row }">{{ row.part_description || DT.fallback.unassignedPart }}</template>
            </el-table-column>
            <el-table-column :label="LTP.table.startDate" min-width="140">
              <template #default="{ row }">{{ formatDate(row.start_date) }}</template>
            </el-table-column>
            <el-table-column :label="LTP.table.endDate" min-width="140">
              <template #default="{ row }">{{ formatDate(row.end_date) }}</template>
            </el-table-column>
            <el-table-column :label="LTP.table.status" min-width="140">
              <template #default="{ row }">
                <el-tag size="small" :type="getTaskStatusTagType(row.status)">{{ getTaskStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="progress" :label="LTP.table.progress" min-width="120">
              <template #default="{ row }">{{ formatPercent(row.progress) }}</template>
            </el-table-column>
            <el-table-column prop="estimated_hours" :label="LTP.table.allocatedManday" min-width="130">
              <template #default="{ row }">{{ formatManday(row.estimated_hours) }}</template>
            </el-table-column>
          </el-table>
          <div class="task-pagination">
            <el-pagination
              v-if="totalTaskCount > pageSize"
              background
              layout="prev, pager, next"
              :page-size="pageSize"
              :total="totalTaskCount"
              :current-page="currentPage"
              @current-change="handlePageChange"
            />
          </div>
        </el-card>
      </template>
    </el-card>

    <el-dialog v-model="showProfileEditDialog" title="Edit Member Profile" width="640px">
      <el-form :model="profileForm" label-width="150px">
        <el-form-item :label="LT.profile.displayName">
          <el-input v-model="profileForm.display_name" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item :label="LT.profile.email">
          <el-input v-model="profileForm.email" maxlength="120" show-word-limit />
        </el-form-item>
        <el-form-item :label="LT.profile.responsibilities">
          <el-input
            v-model="profileForm.responsibilities"
            type="textarea"
            :rows="4"
            resize="none"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
        <el-form-item :label="LT.profile.specialtyTasks">
          <el-input
            v-model="profileForm.specialty_tasks"
            type="textarea"
            :rows="4"
            resize="none"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showProfileEditDialog = false">Cancel</el-button>
        <el-button type="primary" :loading="savingProfile" @click="saveProfile">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getWorkloadByUser, updateUser } from '../api/personnel'
import { LabelText } from '../texts/LabelText'
import { ButtonText } from '../texts/ButtonText'
import { DescriptionText } from '../texts/DescriptionText'
import { canEditPersonnelProfile } from '../stores/auth'
import { formatDate, formatManday, formatPercent } from '../utils/formatters'
import { getTaskStatusTagType, getTaskStatusText } from '../utils/taskStatus'
import { formatTaskLabel } from '../utils/taskDisplay'

const route = useRoute()
const router = useRouter()

const LT = LabelText.personnelDetail
const LTP = LabelText.personnel
const BT = ButtonText.personnel
const DT = DescriptionText.personnelDetail

const loading = ref(false)
const memberDetail = ref(null)
const currentPage = ref(1)
const pageSize = 10
const showProfileEditDialog = ref(false)
const savingProfile = ref(false)
const profileForm = ref({
  display_name: '',
  email: '',
  responsibilities: '',
  specialty_tasks: ''
})

// ── Gantt Timeline ────────────────────────────────────────────────────────────

const ganttViewMode = ref('active')

const ACTIVE_STATUSES = new Set(['inprogress', 'in_progress', 'planning', 'in progress', 'planned'])

const isTaskActiveStatus = (task) => {
  const s = (task.status || '').toLowerCase().replace(/[\s-]/g, '_')
  return ACTIVE_STATUSES.has(s) || s.includes('progress') || s === 'planning' || s === 'planned'
}

const isTaskVisibleInGantt = (task) => {
  if (!task.period_start) return false
  if (isTaskActiveStatus(task)) return true
  if (!task.period_end) return false
  if (ganttViewMode.value === 'active') return false
  const endDate = new Date(task.period_end)
  const cutoff = new Date()
  cutoff.setDate(cutoff.getDate() - 365)
  return endDate >= cutoff
}

const ganttRange = computed(() => {
  const tasks = (memberDetail.value?.tasks || []).filter(t => isTaskVisibleInGantt(t))
  if (!tasks.length) return { start: null, end: null, totalDays: 0 }

  const starts = tasks.map(t => new Date(t.period_start))
  const ends = tasks.map(t => new Date(t.period_end || new Date()))
  const start = new Date(Math.min(...starts))
  const end = new Date(Math.max(...ends))
  const totalDays = Math.max(1, Math.round((end - start) / 86400000) + 1)
  return { start, end, totalDays }
})

const ganttMonthMarkers = computed(() => {
  const { start, end, totalDays } = ganttRange.value
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

const ganttTaskBars = computed(() => {
  const { start, totalDays } = ganttRange.value
  if (!start || !totalDays) return []

  const tasks = (memberDetail.value?.tasks || []).filter(t => isTaskVisibleInGantt(t))
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
})

const WEEK_CAPACITY = 5

const ganttWeeklyLoadBgs = computed(() => {
  const { start, totalDays } = ganttRange.value
  if (!start || !totalDays) return []

  const tasks = (memberDetail.value?.tasks || []).filter(t => isTaskVisibleInGantt(t))
  if (!tasks.length) return []

  const rangeEnd = new Date(start)
  rangeEnd.setDate(rangeEnd.getDate() + totalDays - 1)

  const firstMonday = new Date(start)
  const dow = firstMonday.getDay()
  const daysToMonday = dow === 0 ? -6 : 1 - dow
  firstMonday.setDate(firstMonday.getDate() + daysToMonday)

  const segments = []
  const current = new Date(firstMonday)

  while (current <= rangeEnd) {
    const weekStart = new Date(current)
    const weekEnd = new Date(current)
    weekEnd.setDate(weekEnd.getDate() + 6)

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
})

// ─────────────────────────────────────────────────────────────────────────────

const completedTasks = computed(() => {
  return (memberDetail.value?.tasks || []).filter(task => String(task.status || '').toLowerCase() === 'completed').length
})

const getTaskSortTime = (task) => {
  const rawValue = task?.end_date || task?.period_end || task?.start_date || task?.period_start
  if (!rawValue) return 0
  const normalized = typeof rawValue === 'string' && rawValue.length <= 10 ? `${rawValue}T23:59:59` : rawValue
  const date = new Date(normalized)
  return Number.isNaN(date.getTime()) ? 0 : date.getTime()
}

const sortedTasks = computed(() => {
  const tasks = Array.isArray(memberDetail.value?.tasks) ? [...memberDetail.value.tasks] : []
  return tasks.sort((first, second) => {
    const secondTime = getTaskSortTime(second)
    const firstTime = getTaskSortTime(first)
    if (secondTime !== firstTime) return secondTime - firstTime

    const secondStart = String(second?.start_date || second?.period_start || '')
    const firstStart = String(first?.start_date || first?.period_start || '')
    if (secondStart !== firstStart) return secondStart.localeCompare(firstStart)

    return String(second?.task_label || second?.test_name || '').localeCompare(String(first?.task_label || first?.test_name || ''))
  })
})

const totalTaskCount = computed(() => sortedTasks.value.length)

const visibleTasks = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize
  const endIndex = startIndex + pageSize
  return sortedTasks.value.slice(startIndex, endIndex)
})

const formatTaskName = (task) => {
  return formatTaskLabel(task)
}

const taskRowKey = (task) => `${task?.task_kind || 'test'}-${task?.id || 'na'}`

const handlePageChange = (page) => {
  currentPage.value = page
}

const goBack = () => {
  router.push('/personnel')
}

const openProfileEditDialog = () => {
  if (!memberDetail.value || !canEditPersonnelProfile(memberDetail.value.username)) return
  if (!memberDetail.value) return
  profileForm.value = {
    display_name: memberDetail.value.display_name || '',
    email: memberDetail.value.email || '',
    responsibilities: memberDetail.value.responsibilities || '',
    specialty_tasks: memberDetail.value.specialty_tasks || ''
  }
  showProfileEditDialog.value = true
}

const saveProfile = async () => {
  if (!memberDetail.value?.user_id) return
  if (!canEditPersonnelProfile(memberDetail.value.username)) {
    ElMessage.warning('You can only update your own profile')
    return
  }

  savingProfile.value = true
  try {
    const payload = {
      display_name: (profileForm.value.display_name || '').trim(),
      email: (profileForm.value.email || '').trim(),
      responsibilities: (profileForm.value.responsibilities || '').trim(),
      specialty_tasks: (profileForm.value.specialty_tasks || '').trim()
    }
    await updateUser(Number(memberDetail.value.user_id), payload)
    ElMessage.success('Member profile updated')
    showProfileEditDialog.value = false
    await loadDetail()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to update member profile')
  } finally {
    savingProfile.value = false
  }
}

const goToTask = (task) => {
  if (!task?.id) return
  if (task.task_kind === 'work_task') {
    router.push({ path: `/work-tasks/${task.id}` })
    return
  }
  router.push({ path: `/test-progress/${task.id}` })
}

const loadDetail = async () => {
  const userId = Number(route.params.id)
  if (!userId) return

  loading.value = true
  try {
    memberDetail.value = await getWorkloadByUser(userId)
    currentPage.value = 1
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || DT.toast.loadFailed)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDetail()
})
</script>
<style scoped src="../styles/detail-shared.css"></style>

<style scoped>
.profile-multiline {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}

/* ── Gantt Timeline ──────────────────────────────────────────────────────── */

.gantt-header-controls {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.gantt-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.gantt-row {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: 12px;
  align-items: center;
}

.gantt-row--header,
.gantt-row--footer {
  align-items: flex-end;
}

.gantt-label-col {
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: right;
  color: rgba(148, 163, 184, 0.9);
}

.gantt-label-col--name {
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

.gantt-legend-chip--test { background: rgba(59, 130, 246, 0.8); }
.gantt-legend-chip--work { background: rgba(245, 158, 11, 0.8); }
.gantt-legend-chip--completed { background: rgba(16, 185, 129, 0.8); }
.gantt-legend-chip--overlap {
  background: rgba(180, 130, 20, 0.85);
  border: 1px solid rgba(251, 191, 36, 0.6);
}
.gantt-legend-chip--overload {
  background: rgba(185, 28, 28, 0.85);
  border: 1px solid rgba(239, 68, 68, 0.7);
}

.gantt-tooltip { max-width: 320px; }

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

.gantt-load-tooltip { max-width: 260px; }

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

:deep(.detail-info--ratio .el-descriptions__table) {
  width: 100%;
  table-layout: fixed;
}

:deep(.detail-info--ratio .el-descriptions__label.is-bordered-label) {
  width: 25%;
}

:deep(.detail-info--ratio .el-descriptions__content.is-bordered-content) {
  width: 75%;
}
</style>

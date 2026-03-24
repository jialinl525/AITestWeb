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

        <el-card class="section-card detail-inner-card">
          <template #header>
            <div class="section-title">
              <div class="section-title__main">
                <h3>{{ LT.section.tasks }}</h3>
                <span class="section-title__meta">{{ DT.sectionMeta.tasks }}</span>
              </div>
            </div>
          </template>

          <div v-if="timelineSegments.length" class="overlap-timeline-card">
            <div class="overlap-timeline-card__header">
              <div>
                <div class="overlap-timeline-card__title">Overlap Timeline</div>
                <div class="overlap-timeline-card__meta">
                  {{ formatDate(timelineRange.start) }} ~ {{ formatDate(timelineRange.end) }}
                </div>
              </div>
              <div class="overlap-timeline-card__badge">
                Max {{ memberDetail.overlap_count || 0 }} FR
              </div>
            </div>

            <div class="overlap-timeline">
              <div class="overlap-timeline__axis"></div>
              <el-tooltip
                v-for="(segment, index) in timelineSegments"
                :key="`${segment.overlap_start}-${segment.overlap_end}-${index}`"
                placement="top"
                effect="dark"
              >
                <template #content>
                  <div class="overlap-tooltip">
                    <div class="overlap-tooltip__date">
                      {{ formatDate(segment.overlap_start) }} ~ {{ formatDate(segment.overlap_end) }}
                    </div>
                    <div
                      v-for="task in segment.tasks"
                      :key="task.id"
                      class="overlap-tooltip__item"
                    >
                      {{ task.fr_number || 'FR' }} | {{ task.task_name || '-' }}
                    </div>
                  </div>
                </template>
                <div
                  class="overlap-timeline__segment"
                  :class="segment.colorClass"
                  :style="segment.style"
                ></div>
              </el-tooltip>
            </div>

            <div class="overlap-timeline__scale">
              <span>{{ formatDate(timelineRange.start) }}</span>
              <span>{{ formatDate(timelineRange.end) }}</span>
            </div>

            <div class="overlap-timeline__legend">
              <span class="legend-chip legend-chip--level-2">2 FR</span>
              <span class="legend-chip legend-chip--level-3">3 FR</span>
              <span class="legend-chip legend-chip--level-4">4+ FR</span>
            </div>

          </div>
          <div v-else class="detail-overlap-empty">
            No overlapping test FR found
          </div>

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

const overlapSummaryList = computed(() => {
  return Array.isArray(memberDetail.value?.overlaps) ? memberDetail.value.overlaps : []
})

const timelineRange = computed(() => {
  const segments = overlapSummaryList.value
  if (!segments.length) {
    return {
      start: null,
      end: null,
      totalDays: 0
    }
  }

  const starts = segments.map(item => new Date(item.overlap_start))
  const ends = segments.map(item => new Date(item.overlap_end))
  const start = new Date(Math.min(...starts))
  const end = new Date(Math.max(...ends))
  const totalDays = Math.max(1, Math.round((end - start) / (1000 * 60 * 60 * 24)) + 1)

  return {
    start,
    end,
    totalDays
  }
})

const getSegmentColorClass = (count) => {
  if (count >= 4) return 'overlap-timeline__segment--level-4'
  if (count >= 3) return 'overlap-timeline__segment--level-3'
  return 'overlap-timeline__segment--level-2'
}

const timelineSegments = computed(() => {
  if (!timelineRange.value.start || !timelineRange.value.end || !timelineRange.value.totalDays) {
    return []
  }

  const rangeStartTime = timelineRange.value.start.getTime()
  const dayMs = 1000 * 60 * 60 * 24

  return overlapSummaryList.value.map(item => {
    const segmentStart = new Date(item.overlap_start)
    const segmentEnd = new Date(item.overlap_end)
    const startOffset = Math.max(0, Math.round((segmentStart.getTime() - rangeStartTime) / dayMs))
    const segmentDays = Math.max(1, Math.round((segmentEnd.getTime() - segmentStart.getTime()) / dayMs) + 1)
    const left = (startOffset / timelineRange.value.totalDays) * 100
    const width = (segmentDays / timelineRange.value.totalDays) * 100

    return {
      ...item,
      colorClass: getSegmentColorClass(Number(item.concurrent_task_count || 0)),
      style: {
        left: `${left}%`,
        width: `${Math.max(width, 1.5)}%`
      },
      tasks: Array.isArray(item.tasks) ? item.tasks : []
    }
  })
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

.overlap-timeline-card {
  margin-bottom: 16px;
  padding: 16px;
  border: 1px solid rgba(248, 113, 113, 0.18);
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.42);
}

.overlap-timeline-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.overlap-timeline-card__title {
  font-size: 15px;
  font-weight: 700;
  color: rgba(248, 250, 252, 0.96);
}

.overlap-timeline-card__meta {
  margin-top: 4px;
  font-size: 12px;
  color: rgba(148, 163, 184, 0.9);
}

.overlap-timeline-card__badge {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(127, 29, 29, 0.35);
  color: rgba(254, 202, 202, 0.96);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.overlap-timeline {
  position: relative;
  height: 24px;
  margin-bottom: 8px;
}

.overlap-timeline__axis {
  position: absolute;
  inset: 7px 0;
  border-radius: 999px;
  background: rgba(51, 65, 85, 0.9);
}

.overlap-timeline__segment {
  position: absolute;
  top: 2px;
  height: 20px;
  border-radius: 999px;
  box-shadow: 0 0 0 1px rgba(15, 23, 42, 0.45);
}

.overlap-timeline__segment--level-2 {
  background: linear-gradient(90deg, rgba(250, 204, 21, 0.92), rgba(249, 115, 22, 0.92));
}

.overlap-timeline__segment--level-3 {
  background: linear-gradient(90deg, rgba(249, 115, 22, 0.96), rgba(239, 68, 68, 0.96));
}

.overlap-timeline__segment--level-4 {
  background: linear-gradient(90deg, rgba(239, 68, 68, 0.96), rgba(127, 29, 29, 0.96));
}

.overlap-timeline__scale {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 12px;
  color: rgba(148, 163, 184, 0.9);
  margin-bottom: 12px;
}

.overlap-timeline__legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
}

.legend-chip {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  color: rgba(248, 250, 252, 0.96);
}

.legend-chip--level-2 {
  background: rgba(245, 158, 11, 0.85);
}

.legend-chip--level-3 {
  background: rgba(249, 115, 22, 0.88);
}

.legend-chip--level-4 {
  background: rgba(220, 38, 38, 0.88);
}

.detail-overlap-empty {
  color: rgba(148, 163, 184, 0.92);
}

.overlap-tooltip {
  max-width: 420px;
}

.overlap-tooltip__date {
  margin-bottom: 6px;
  font-size: 12px;
  font-weight: 700;
  color: rgba(253, 230, 138, 0.96);
}

.overlap-tooltip__item {
  font-size: 12px;
  line-height: 1.6;
  color: rgba(248, 250, 252, 0.96);
  word-break: break-word;
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

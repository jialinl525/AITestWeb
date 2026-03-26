<template>
  <div class="page-shell work-task-page">
    <section class="page-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">{{ LT.heroEyebrow }}</div>
        <h2 class="page-hero__title">{{ LT.heroTitle }}</h2>
        <p class="page-hero__desc">{{ DT.hero }}</p>
      </div>
      <div class="page-hero__actions">
        <div class="glass-pill">{{ LT.pills.totalTasks }} {{ filteredTasks.length }}</div>
        <div class="glass-pill">{{ LT.pills.totalManday }} {{ totalEstimatedHours }} manday</div>
        <div class="glass-pill">{{ LT.pills.inProgress }} {{ inProgressCount }}</div>
        <el-button @click="loadTasks">{{ BTCommon.refresh }}</el-button>
      </div>
    </section>

    <div class="metrics-grid">
      <MetricCard :label="LT.metrics.planned" :value="planCount" :meta="DT.metricsMeta.planned" accent="blue" />
      <MetricCard :label="LT.metrics.inProgress" :value="inProgressCount" :meta="DT.metricsMeta.inProgress" accent="orange" />
      <MetricCard :label="LT.metrics.completed" :value="doneCount" :meta="DT.metricsMeta.completed" accent="green" />
      <MetricCard :label="LT.metrics.paused" :value="pausedCount" :meta="DT.metricsMeta.paused" accent="red" />
    </div>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>{{ LT.sectionTitle }}</h3>
            <span class="section-title__meta">{{ DT.sectionMeta.list }}</span>
          </div>
        </div>
      </template>

      <WorkTaskFilterBar
        v-model:filters="filters"
        :task-type-options="taskTypeOptions"
        :status-options="statusOptions"
        :members="members"
        :can-create="canCreateOrEditTest()"
        @search="loadTasks"
        @reset="resetFilters"
        @create="openCreateTaskDialog"
      />

      <WorkTaskTable
        :tasks="paginatedTasks"
        :loading="loading"
        :can-edit="canCreateOrEditTest()"
        :total="filteredTasks.length"
        :page-size="pageSize"
        :current-page="currentPage"
        @view="viewDetail"
        @edit="openEditDialog"
        @delete="handleDelete"
        @page-change="handlePageChange"
      />
    </el-card>

    <WorkTaskDialog
      v-model="showDialog"
      :form="form"
      :is-editing="Boolean(editingId)"
      :saving="saving"
      :task-type-options="taskTypeOptions"
      :status-options="statusOptions"
      :members="members"
      @save="saveTask"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import MetricCard from '../components/common/MetricCard.vue'
import WorkTaskFilterBar from '../components/workTasks/WorkTaskFilterBar.vue'
import WorkTaskTable from '../components/workTasks/WorkTaskTable.vue'
import WorkTaskDialog from '../components/workTasks/WorkTaskDialog.vue'
import { LabelText } from '../texts/LabelText'
import { ButtonText } from '../texts/ButtonText'
import { DescriptionText } from '../texts/DescriptionText'
import { useCrudDialog } from '../composables/useCrudDialog'
import { useFilterState } from '../composables/useListState'
import { canCreateOrEditTest } from '../stores/auth'
import { getMembers } from '../api/personnel'
import { createWorkTask, deleteWorkTask, getWorkTaskMeta, getWorkTasks, updateWorkTask } from '../api/workTasks'

const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const LT = LabelText.workTasks
const BTCommon = ButtonText.common
const DT = DescriptionText.workTasks

const tasks = ref([])
const members = ref([])
const currentPage = ref(1)
const pageSize = 10

const taskTypeOptions = ref(['Customer Support', 'Automation Development', 'Other'])
const statusOptions = ref(['Planned', 'In Progress', 'Completed', 'Paused'])

const { filters, resetFilters: resetFilterState } = useFilterState({
  keyword: '',
  task_type: '',
  status: '',
  assignee_user_id: null
})

const createDefaultTaskForm = () => ({
  task_key: '',
  task_type: 'Customer Support',
  task_name: '',
  task_summary: '',
  task_detail: '',
  start_date: null,
  end_date: null,
  estimated_hours: 0,
  progress: 0,
  status: 'Planned',
  assignee_user_id: null
})

const mapTaskRowToForm = (row = {}) => ({
  task_key: row.task_key || '',
  task_type: row.task_type || 'Customer Support',
  task_name: row.task_name || '',
  task_summary: row.task_summary || '',
  task_detail: row.task_detail || '',
  start_date: row.start_date || null,
  end_date: row.end_date || null,
  estimated_hours: Number(row.estimated_hours || 0),
  progress: Number(row.progress || 0),
  status: row.status || 'Planned',
  assignee_user_id: row.assignee_user_id || null
})

const { showDialog, editingId, form, openCreateDialog, openEditDialog, closeDialog } =
  useCrudDialog(createDefaultTaskForm, mapTaskRowToForm)

const parseRecentTaskDate = (value) => {
  if (!value) return null
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return null
  date.setHours(0, 0, 0, 0)
  return date
}

const filteredTasks = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const startDate = new Date(today)
  startDate.setDate(startDate.getDate() - 365)
  return tasks.value.filter(item => {
    const candidateDates = [
      parseRecentTaskDate(item?.end_date),
      parseRecentTaskDate(item?.start_date)
    ].filter(Boolean)
    return candidateDates.some(date => date >= startDate)
  })
})

const paginatedTasks = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize
  return filteredTasks.value.slice(startIndex, startIndex + pageSize)
})

const totalEstimatedHours = computed(() =>
  Number(filteredTasks.value.reduce((sum, item) => sum + Number(item.estimated_hours || 0), 0).toFixed(1))
)
const planCount = computed(() => filteredTasks.value.filter(item => item.status === 'Planned').length)
const inProgressCount = computed(() => filteredTasks.value.filter(item => item.status === 'In Progress').length)
const doneCount = computed(() => filteredTasks.value.filter(item => item.status === 'Completed').length)
const pausedCount = computed(() => filteredTasks.value.filter(item => item.status === 'Paused').length)

const normalizeParams = () => {
  const params = {}
  const raw = filters.value
  if (raw.keyword?.trim()) params.keyword = raw.keyword.trim()
  if (raw.task_type) params.task_type = raw.task_type
  if (raw.status) params.status = raw.status
  if (raw.assignee_user_id) params.assignee_user_id = Number(raw.assignee_user_id)
  return params
}

const buildTaskKey = () => {
  const ts = new Date().toISOString().replace(/[-:TZ.]/g, '').slice(0, 14)
  const rand = Math.floor(Math.random() * 1000).toString().padStart(3, '0')
  return `TASK-${ts}-${rand}`
}

const viewDetail = (taskId) => router.push({ path: `/work-tasks/${taskId}` })

const loadMeta = async () => {
  try {
    const meta = await getWorkTaskMeta()
    if (Array.isArray(meta.task_types) && meta.task_types.length) taskTypeOptions.value = meta.task_types
    if (Array.isArray(meta.status_options) && meta.status_options.length) statusOptions.value = meta.status_options
  } catch { /* fallback to local defaults */ }
}

const loadMembers = async () => {
  try { members.value = await getMembers() } catch { members.value = [] }
}

const loadTasks = async () => {
  loading.value = true
  try {
    tasks.value = await getWorkTasks(normalizeParams())
    currentPage.value = 1
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || DT.toast.loadFailed)
  } finally {
    loading.value = false
  }
}

const openCreateTaskDialog = () => {
  openCreateDialog()
  form.value.task_key = buildTaskKey()
}

const saveTask = async () => {
  if (!form.value.task_name?.trim()) { ElMessage.warning(DT.toast.taskNameRequired); return }
  if (!form.value.task_type) { ElMessage.warning(DT.toast.taskTypeRequired); return }
  if (!form.value.status) { ElMessage.warning(DT.toast.taskStatusRequired); return }
  if (form.value.start_date && form.value.end_date && form.value.start_date > form.value.end_date) {
    ElMessage.warning(DT.toast.invalidDateRange); return
  }

  const payload = {
    task_key: (form.value.task_key || '').trim() || buildTaskKey(),
    task_type: form.value.task_type,
    task_name: form.value.task_name.trim(),
    task_summary: (form.value.task_summary || '').trim(),
    task_detail: (form.value.task_detail || '').trim(),
    start_date: form.value.start_date || null,
    end_date: form.value.end_date || null,
    estimated_hours: Number(form.value.estimated_hours || 0),
    progress: Number(form.value.progress || 0),
    status: form.value.status,
    assignee_user_id: form.value.assignee_user_id || null
  }

  saving.value = true
  try {
    if (editingId.value) {
      await updateWorkTask(editingId.value, payload)
      ElMessage.success(DT.toast.updateSuccess)
    } else {
      await createWorkTask(payload)
      ElMessage.success(DT.toast.createSuccess)
    }
    closeDialog()
    await loadTasks()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || DT.toast.saveFailed)
  } finally {
    saving.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `${DT.toast.deleteConfirmPrefix} ${row.task_name}${DT.toast.deleteConfirmSuffix}`,
      DT.toast.deleteConfirmTitle,
      { confirmButtonText: ButtonText.common.delete, cancelButtonText: ButtonText.common.cancel, type: 'warning' }
    )
    await deleteWorkTask(row.id)
    ElMessage.success(DT.toast.deleteSuccess)
    await loadTasks()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error(error?.response?.data?.detail || DT.toast.deleteFailed)
  }
}

const handlePageChange = (page) => { currentPage.value = page }

const resetFilters = async () => {
  resetFilterState()
  await loadTasks()
}

onMounted(async () => {
  await Promise.all([loadMeta(), loadMembers()])
  await loadTasks()
})
</script>

<style scoped>
.work-task-page {
  width: 100%;
}
</style>

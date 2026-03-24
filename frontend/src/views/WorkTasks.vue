<template>
  <div class="page-shell work-task-page">
    <section class="page-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">{{ LT.heroEyebrow }}</div>
        <h2 class="page-hero__title">{{ LT.heroTitle }}</h2>
        <p class="page-hero__desc">
          {{ DT.hero }}
        </p>
      </div>
      <div class="page-hero__actions">
        <div class="glass-pill">{{ LT.pills.totalTasks }} {{ filteredTasks.length }}</div>
        <div class="glass-pill">{{ LT.pills.totalManday }} {{ totalEstimatedHours }} manday</div>
        <div class="glass-pill">{{ LT.pills.inProgress }} {{ inProgressCount }}</div>
        <el-button @click="loadTasks">{{ BTCommon.refresh }}</el-button>
      </div>
    </section>

    <div class="metrics-grid">
      <article class="metric-card accent-blue">
        <div class="metric-card__label">{{ LT.metrics.planned }}</div>
        <div class="metric-card__value">{{ planCount }}</div>
        <div class="metric-card__meta">{{ DT.metricsMeta.planned }}</div>
      </article>
      <article class="metric-card accent-orange">
        <div class="metric-card__label">{{ LT.metrics.inProgress }}</div>
        <div class="metric-card__value">{{ inProgressCount }}</div>
        <div class="metric-card__meta">{{ DT.metricsMeta.inProgress }}</div>
      </article>
      <article class="metric-card accent-green">
        <div class="metric-card__label">{{ LT.metrics.completed }}</div>
        <div class="metric-card__value">{{ doneCount }}</div>
        <div class="metric-card__meta">{{ DT.metricsMeta.completed }}</div>
      </article>
      <article class="metric-card accent-red">
        <div class="metric-card__label">{{ LT.metrics.paused }}</div>
        <div class="metric-card__value">{{ pausedCount }}</div>
        <div class="metric-card__meta">{{ DT.metricsMeta.paused }}</div>
      </article>
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

      <div class="toolbar-panel task-toolbar">
        <el-input v-model="filters.keyword" :placeholder="DT.placeholders.search" clearable style="width: 280px" />
        <el-select v-model="filters.task_type" :placeholder="DT.placeholders.taskType" clearable style="width: 180px">
          <el-option v-for="item in taskTypeOptions" :key="item" :label="item" :value="item" />
        </el-select>
        <el-select v-model="filters.status" :placeholder="DT.placeholders.taskStatus" clearable style="width: 150px">
          <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
        </el-select>
        <el-select v-model="filters.assignee_user_id" :placeholder="DT.placeholders.assignee" clearable style="width: 180px">
          <el-option
            v-for="member in members"
            :key="member.id"
            :label="member.display_name || member.username"
            :value="member.id"
          />
        </el-select>

        <el-button @click="loadTasks">{{ BTCommon.search }}</el-button>
        <el-button @click="resetFilters">{{ BTCommon.reset }}</el-button>
        <el-button v-if="canCreateOrEditTest()" type="primary" @click="openCreateTaskDialog">{{ BT.newTask }}</el-button>
      </div>

      <el-table :data="paginatedTasks" v-loading="loading" stripe class="full-width-table" style="width: 100%" table-layout="auto">
        <el-table-column prop="task_name" :label="LT.table.taskName" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            <button
              v-if="row.id"
              type="button"
              class="task-name-link"
              @click="viewDetail(row.id)"
            >
              {{ row.task_name || '-' }}
            </button>
            <span v-else>{{ row.task_name || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="task_type" :label="LT.table.taskType" min-width="150" />
        <el-table-column prop="task_summary" :label="LT.table.taskSummary" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">{{ row.task_summary || '-' }}</template>
        </el-table-column>
        <el-table-column :label="LT.table.startDate" min-width="120">
          <template #default="{ row }">{{ formatDate(row.start_date) }}</template>
        </el-table-column>
        <el-table-column :label="LT.table.status" min-width="120">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="LT.table.progress" min-width="110">
          <template #default="{ row }">{{ formatPercent(row.progress) }}</template>
        </el-table-column>
        <el-table-column :label="LT.table.assignee" min-width="150">
          <template #default="{ row }">{{ row.assignee_display_name || '-' }}</template>
        </el-table-column>
        <el-table-column v-if="canCreateOrEditTest()" :label="LT.table.actions" min-width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEditDialog(row)">{{ BTCommon.edit }}</el-button>
            <el-button link type="danger" @click="handleDelete(row)">{{ BTCommon.delete }}</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="list-pagination">
        <el-pagination
          v-if="filteredTasks.length > pageSize"
          background
          layout="prev, pager, next"
          :page-size="pageSize"
          :total="filteredTasks.length"
          :current-page="currentPage"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="showDialog" :title="editingId ? LT.dialog.editTitle : LT.dialog.newTitle" width="760px">
      <el-form :model="form" label-width="110px">
        <el-form-item :label="LT.form.taskType" required>
          <el-select v-model="form.task_type" style="width: 100%" :placeholder="DT.placeholders.selectType">
            <el-option v-for="item in taskTypeOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item :label="LT.form.taskName" required>
          <el-input v-model="form.task_name" :placeholder="DT.placeholders.taskName" />
        </el-form-item>
        <el-form-item :label="LT.form.taskSummary">
          <el-input v-model="form.task_summary" type="textarea" :rows="2" maxlength="300" show-word-limit />
        </el-form-item>
        <el-form-item :label="LT.form.taskDetail">
          <el-input v-model="form.task_detail" type="textarea" :rows="4" maxlength="1000" show-word-limit />
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item :label="LT.form.startDate">
              <el-date-picker v-model="form.start_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="LT.form.endDate">
              <el-date-picker v-model="form.end_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item :label="LT.form.estimatedManday">
              <el-input-number v-model="form.estimated_hours" :min="0" :step="0.5" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="LT.form.progress">
              <el-input-number v-model="form.progress" :min="0" :max="100" :step="1" :precision="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item :label="LT.form.status" required>
              <el-select v-model="form.status" style="width: 100%" :placeholder="DT.placeholders.selectStatus">
                <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="LT.form.assignee">
              <el-select v-model="form.assignee_user_id" clearable style="width: 100%" :placeholder="DT.placeholders.optional">
                <el-option
                  v-for="member in members"
                  :key="member.id"
                  :label="member.display_name || member.username"
                  :value="member.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <template #footer>
        <el-button @click="showDialog = false">{{ BTCommon.cancel }}</el-button>
        <el-button type="primary" :loading="saving" @click="saveTask">{{ BTCommon.save }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { LabelText } from '../texts/LabelText'
import { ButtonText } from '../texts/ButtonText'
import { DescriptionText } from '../texts/DescriptionText'
import { useCrudDialog } from '../composables/useCrudDialog'
import { useFilterState } from '../composables/useListState'
import { formatDate, formatPercent } from '../utils/formatters'

import { canCreateOrEditTest } from '../stores/auth'
import { getMembers } from '../api/personnel'
import { createWorkTask, deleteWorkTask, getWorkTaskMeta, getWorkTasks, updateWorkTask } from '../api/workTasks'

const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const LT = LabelText.workTasks
const BT = ButtonText.workTasks
const BTCommon = ButtonText.common
const DT = DescriptionText.workTasks

const tasks = ref([])
const members = ref([])
const currentPage = ref(1)
const pageSize = 10

const taskTypeOptions = ref(['Customer Support', 'Automation Development', 'Other'])
const statusOptions = ref(['Planned', 'In Progress', 'Completed', 'Paused'])

const {
  filters,
  resetFilters: resetFilterState
} = useFilterState({
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

const {
  showDialog,
  editingId,
  form,
  openCreateDialog,
  openEditDialog,
  closeDialog
} = useCrudDialog(createDefaultTaskForm, mapTaskRowToForm)

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

const totalEstimatedHours = computed(() => Number(filteredTasks.value.reduce((sum, item) => sum + Number(item.estimated_hours || 0), 0).toFixed(1)))
const planCount = computed(() => filteredTasks.value.filter(item => item.status === 'Planned').length)
const inProgressCount = computed(() => filteredTasks.value.filter(item => item.status === 'In Progress').length)
const doneCount = computed(() => filteredTasks.value.filter(item => item.status === 'Completed').length)
const pausedCount = computed(() => filteredTasks.value.filter(item => item.status === 'Paused').length)

const statusTagType = (status) => {
  if (status === 'Completed') return 'success'
  if (status === 'In Progress') return 'warning'
  if (status === 'Paused') return 'danger'
  return 'info'
}

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

const viewDetail = (taskId) => {
  router.push({ path: `/work-tasks/${taskId}` })
}

const loadMeta = async () => {
  try {
    const meta = await getWorkTaskMeta()
    if (Array.isArray(meta.task_types) && meta.task_types.length) taskTypeOptions.value = meta.task_types
    if (Array.isArray(meta.status_options) && meta.status_options.length) statusOptions.value = meta.status_options
  } catch {
    // fallback to local defaults
  }
}

const loadMembers = async () => {
  try {
    members.value = await getMembers()
  } catch {
    members.value = []
  }
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
  if (!form.value.task_name?.trim()) {
    ElMessage.warning(DT.toast.taskNameRequired)
    return
  }
  if (!form.value.task_type) {
    ElMessage.warning(DT.toast.taskTypeRequired)
    return
  }
  if (!form.value.status) {
    ElMessage.warning(DT.toast.taskStatusRequired)
    return
  }
  if (form.value.start_date && form.value.end_date && form.value.start_date > form.value.end_date) {
    ElMessage.warning(DT.toast.invalidDateRange)
    return
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
    await ElMessageBox.confirm(`${DT.toast.deleteConfirmPrefix} ${row.task_name}${DT.toast.deleteConfirmSuffix}`, DT.toast.deleteConfirmTitle, {
      confirmButtonText: BTCommon.delete,
      cancelButtonText: BTCommon.cancel,
      type: 'warning'
    })

    await deleteWorkTask(row.id)
    ElMessage.success(DT.toast.deleteSuccess)
    await loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error?.response?.data?.detail || DT.toast.deleteFailed)
    }
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
}

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

.task-toolbar {
  margin-bottom: 14px;
}

.full-width-table {
  width: 100%;
}

.task-name-link {
  appearance: none;
  border: none;
  background: transparent;
  padding: 0;
  margin: 0;
  color: #7dd3fc;
  font-weight: 700;
  cursor: pointer;
  text-align: left;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.task-name-link:hover {
  color: #bae6fd;
}

.task-name-link:focus-visible {
  outline: 2px solid rgba(125, 211, 252, 0.7);
  outline-offset: 2px;
  border-radius: 4px;
}

.list-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>

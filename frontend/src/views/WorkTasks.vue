<template>
  <div class="page-shell work-task-page">
    <section class="page-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">Unified Task Board</div>
        <h2 class="page-hero__title">Customer Support / Automation Development Task Management</h2>
        <p class="page-hero__desc">
          Manage customer support, automation development, and other work items in one place with direct personnel assignment.
        </p>
      </div>
      <div class="page-hero__actions">
        <div class="glass-pill">Total Tasks {{ tasks.length }}</div>
        <div class="glass-pill">Total Manday {{ totalEstimatedHours }} manday</div>
        <div class="glass-pill">In Progress {{ inProgressCount }}</div>
        <el-button @click="loadTasks">Refresh</el-button>
      </div>
    </section>

    <div class="metrics-grid">
      <article class="metric-card accent-blue">
        <div class="metric-card__label">Planned</div>
        <div class="metric-card__value">{{ planCount }}</div>
        <div class="metric-card__meta">Tasks waiting to start</div>
      </article>
      <article class="metric-card accent-orange">
        <div class="metric-card__label">In Progress</div>
        <div class="metric-card__value">{{ inProgressCount }}</div>
        <div class="metric-card__meta">Tasks currently being executed</div>
      </article>
      <article class="metric-card accent-green">
        <div class="metric-card__label">Completed</div>
        <div class="metric-card__value">{{ doneCount }}</div>
        <div class="metric-card__meta">Closed work items</div>
      </article>
      <article class="metric-card accent-red">
        <div class="metric-card__label">Paused</div>
        <div class="metric-card__value">{{ pausedCount }}</div>
        <div class="metric-card__meta">Currently blocked tasks</div>
      </article>
    </div>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>Task List</h3>
            <span class="section-title__meta">Filter by type, status, assignee, and keyword</span>
          </div>
        </div>
      </template>

      <div class="toolbar-panel task-toolbar">
        <el-input v-model="filters.keyword" placeholder="Search by key, task name, summary, or detail" clearable style="width: 280px" />
        <el-select v-model="filters.task_type" placeholder="Task Type" clearable style="width: 180px">
          <el-option v-for="item in taskTypeOptions" :key="item" :label="item" :value="item" />
        </el-select>
        <el-select v-model="filters.status" placeholder="Task Status" clearable style="width: 150px">
          <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
        </el-select>
        <el-select v-model="filters.assignee_user_id" placeholder="Assignee" clearable style="width: 180px">
          <el-option
            v-for="member in members"
            :key="member.id"
            :label="member.display_name || member.username"
            :value="member.id"
          />
        </el-select>

        <el-button @click="loadTasks">Search</el-button>
        <el-button @click="resetFilters">Reset</el-button>
        <el-button v-if="canCreateOrEditTest()" type="primary" @click="openCreateDialog">New Task</el-button>
      </div>

      <el-table :data="tasks" v-loading="loading" stripe class="full-width-table" style="width: 100%" table-layout="auto">
        <el-table-column prop="task_key" label="Key" min-width="130" />
        <el-table-column prop="task_type" label="Task Type" min-width="140" />
        <el-table-column prop="task_name" label="Task Name" min-width="200" show-overflow-tooltip />
        <el-table-column prop="task_summary" label="Task Summary" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">{{ row.task_summary || '-' }}</template>
        </el-table-column>
        <el-table-column prop="task_detail" label="Task Detail" min-width="240" show-overflow-tooltip>
          <template #default="{ row }">{{ row.task_detail || '-' }}</template>
        </el-table-column>
        <el-table-column label="Start Date" min-width="120">
          <template #default="{ row }">{{ formatDate(row.start_date) }}</template>
        </el-table-column>
        <el-table-column label="End Date" min-width="120">
          <template #default="{ row }">{{ formatDate(row.end_date) }}</template>
        </el-table-column>
        <el-table-column label="Estimated Manday" min-width="140">
          <template #default="{ row }">{{ Number(row.estimated_hours || 0).toFixed(1) }} manday</template>
        </el-table-column>
        <el-table-column label="Status" min-width="120">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Assignee" min-width="150">
          <template #default="{ row }">{{ row.assignee_display_name || '-' }}</template>
        </el-table-column>
        <el-table-column v-if="canCreateOrEditTest()" label="Actions" min-width="170" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEditDialog(row)">Edit</el-button>
            <el-button link type="danger" @click="handleDelete(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showDialog" :title="editingId ? 'Edit Task' : 'New Task'" width="760px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="Task Key" required>
          <el-input v-model="form.task_key" placeholder="Example: CS-20260316-001" />
        </el-form-item>
        <el-form-item label="Task Type" required>
          <el-select v-model="form.task_type" style="width: 100%" placeholder="Select a type">
            <el-option v-for="item in taskTypeOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="Task Name" required>
          <el-input v-model="form.task_name" placeholder="Enter the task name" />
        </el-form-item>
        <el-form-item label="Task Summary">
          <el-input v-model="form.task_summary" type="textarea" :rows="2" maxlength="300" show-word-limit />
        </el-form-item>
        <el-form-item label="Task Detail">
          <el-input v-model="form.task_detail" type="textarea" :rows="4" maxlength="1000" show-word-limit />
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="Start Date">
              <el-date-picker v-model="form.start_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="End Date">
              <el-date-picker v-model="form.end_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="Estimated Manday">
              <el-input-number v-model="form.estimated_hours" :min="0" :step="0.5" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Status" required>
              <el-select v-model="form.status" style="width: 100%" placeholder="Select a status">
                <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Assignee">
          <el-select v-model="form.assignee_user_id" clearable style="width: 100%" placeholder="Optional">
            <el-option
              v-for="member in members"
              :key="member.id"
              :label="member.display_name || member.username"
              :value="member.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showDialog = false">Cancel</el-button>
        <el-button type="primary" :loading="saving" @click="saveTask">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { canCreateOrEditTest } from '../stores/auth'
import { getMembers } from '../api/personnel'
import { createWorkTask, deleteWorkTask, getWorkTaskMeta, getWorkTasks, updateWorkTask } from '../api/workTasks'

const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const editingId = ref(null)

const tasks = ref([])
const members = ref([])

const taskTypeOptions = ref(['Customer Support', 'Automation Development', 'Other'])
const statusOptions = ref(['Planned', 'In Progress', 'Completed', 'Paused'])

const filters = ref({
  keyword: '',
  task_type: '',
  status: '',
  assignee_user_id: null
})

const form = ref({
  task_key: '',
  task_type: 'Customer Support',
  task_name: '',
  task_summary: '',
  task_detail: '',
  start_date: null,
  end_date: null,
  estimated_hours: 0,
  status: 'Planned',
  assignee_user_id: null
})

const totalEstimatedHours = computed(() => Number(tasks.value.reduce((sum, item) => sum + Number(item.estimated_hours || 0), 0).toFixed(1)))
const planCount = computed(() => tasks.value.filter(item => item.status === 'Planned').length)
const inProgressCount = computed(() => tasks.value.filter(item => item.status === 'In Progress').length)
const doneCount = computed(() => tasks.value.filter(item => item.status === 'Completed').length)
const pausedCount = computed(() => tasks.value.filter(item => item.status === 'Paused').length)

const formatDate = (value) => {
  if (!value) return '-'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return '-'
  return d.toLocaleDateString('en-CA')
}

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
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to load tasks')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.value = {
    task_key: '',
    task_type: 'Customer Support',
    task_name: '',
    task_summary: '',
    task_detail: '',
    start_date: null,
    end_date: null,
    estimated_hours: 0,
    status: 'Planned',
    assignee_user_id: null
  }
}

const openCreateDialog = () => {
  editingId.value = null
  resetForm()
  showDialog.value = true
}

const openEditDialog = (row) => {
  editingId.value = row.id
  form.value = {
    task_key: row.task_key || '',
    task_type: row.task_type || 'Customer Support',
    task_name: row.task_name || '',
    task_summary: row.task_summary || '',
    task_detail: row.task_detail || '',
    start_date: row.start_date || null,
    end_date: row.end_date || null,
    estimated_hours: Number(row.estimated_hours || 0),
    status: row.status || 'Planned',
    assignee_user_id: row.assignee_user_id || null
  }
  showDialog.value = true
}

const saveTask = async () => {
  if (!form.value.task_key?.trim()) {
    ElMessage.warning('Task key cannot be empty')
    return
  }
  if (!form.value.task_name?.trim()) {
    ElMessage.warning('Task name cannot be empty')
    return
  }
  if (!form.value.task_type) {
    ElMessage.warning('Please select a task type')
    return
  }
  if (!form.value.status) {
    ElMessage.warning('Please select a task status')
    return
  }
  if (form.value.start_date && form.value.end_date && form.value.start_date > form.value.end_date) {
    ElMessage.warning('End date cannot be earlier than start date')
    return
  }

  const payload = {
    task_key: form.value.task_key.trim(),
    task_type: form.value.task_type,
    task_name: form.value.task_name.trim(),
    task_summary: (form.value.task_summary || '').trim(),
    task_detail: (form.value.task_detail || '').trim(),
    start_date: form.value.start_date || null,
    end_date: form.value.end_date || null,
    estimated_hours: Number(form.value.estimated_hours || 0),
    status: form.value.status,
    assignee_user_id: form.value.assignee_user_id || null
  }

  saving.value = true
  try {
    if (editingId.value) {
      await updateWorkTask(editingId.value, payload)
      ElMessage.success('Task updated successfully')
    } else {
      await createWorkTask(payload)
      ElMessage.success('Task created successfully')
    }
    showDialog.value = false
    await loadTasks()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to save task')
  } finally {
    saving.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`Delete task ${row.task_key}?`, 'Delete Confirmation', {
      confirmButtonText: 'Delete',
      cancelButtonText: 'Cancel',
      type: 'warning'
    })

    await deleteWorkTask(row.id)
    ElMessage.success('Task deleted')
    await loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error?.response?.data?.detail || 'Failed to delete task')
    }
  }
}

const resetFilters = async () => {
  filters.value = {
    keyword: '',
    task_type: '',
    status: '',
    assignee_user_id: null
  }
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
</style>

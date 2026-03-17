<template>
  <div class="page-shell bugs-container">
    <section class="page-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">Risk Tracking</div>
        <h2 class="page-hero__title">Bug Risk Tracking Dashboard</h2>
        <p class="page-hero__desc">Manage issue lifecycle by severity, status, and assignee to quickly identify high-risk defects and pending actions.</p>
      </div>
      <div class="page-hero__actions">
        <div v-if="route.query.testId" class="glass-pill">Current Test ID Filter: {{ route.query.testId }}</div>
        <el-button v-if="route.query.testId" class="btn-style-3" @click="clearTestFilter">Back to All Bugs</el-button>
        <el-button class="btn-style-1" :disabled="pagination.total === 0" @click="openExportDialog">Export Top N</el-button>
        <el-button v-if="canCreateBug()" class="btn-style-4" :loading="importingCsv" @click="importCsvBugs">Import CSV Bugs</el-button>
        <el-button v-if="canCreateBug()" class="btn-style-2" type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          New Bug
        </el-button>
        <input
          ref="csvFileInput"
          type="file"
          accept=".csv,text/csv"
          class="csv-file-input"
          @change="handleCsvFileSelected"
        />
      </div>
    </section>

    <div class="metrics-grid">
      <article class="metric-card accent-blue">
        <div class="metric-card__label">Total Bugs</div>
        <div class="metric-card__value">{{ bugStats.total || 0 }}</div>
        <div class="metric-card__meta">Issue records across the full lifecycle</div>
      </article>
      <article class="metric-card accent-red">
        <div class="metric-card__label">Analysis</div>
        <div class="metric-card__value">{{ bugStats.by_status?.analysis || 0 }}</div>
        <div class="metric-card__meta">Open and analysis-state CRs</div>
      </article>
      <article class="metric-card accent-orange">
        <div class="metric-card__label">Other</div>
        <div class="metric-card__value">{{ bugStats.by_status?.other || 0 }}</div>
        <div class="metric-card__meta">CRs outside fixed/analysis rules</div>
      </article>
      <article class="metric-card accent-green">
        <div class="metric-card__label">Fixed</div>
        <div class="metric-card__value">{{ bugStats.by_status?.fixed || 0 }}</div>
        <div class="metric-card__meta">In Progress / Build / Closed / Duplicate</div>
      </article>
    </div>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>Filter and Search</h3>
            <span class="section-title__meta">Focus on key issues by status and severity</span>
          </div>
        </div>
      </template>

      <el-form :inline="true" class="filter-form">
        <el-form-item label="Status">
          <el-select v-model="filters.status" class="filter-select" placeholder="All" clearable popper-class="bugs-filter-popper">
            <el-option
              v-for="status in statusOptions"
              :key="status"
              :label="status"
              :value="status"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Created By">
          <el-select
            v-model="filters.created_by"
            class="filter-select"
            placeholder="All"
            clearable
            filterable
            popper-class="bugs-filter-popper"
          >
            <el-option
              v-for="name in createdByOptions"
              :key="name"
              :label="name"
              :value="name"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button class="btn-style-2" type="primary" @click="applyFilters">Filter</el-button>
          <el-button class="btn-style-3" @click="resetFilters">Reset</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>Bug List</h3>
            <span class="section-title__meta">{{ pagination.total }} records total, sorted by CR Number (DESC)</span>
          </div>
        </div>
      </template>
      <el-table :data="bugsList" v-loading="loading" stripe :row-class-name="getTableRowClassName">
        <el-table-column prop="external_cr_number" label="CR Number" width="160">
          <template #default="{ row }">
            <a
              v-if="row.external_cr_number"
              :href="getCrLink(row.external_cr_number)"
              target="_blank"
              rel="noopener noreferrer"
              class="cr-link"
            >
              {{ row.external_cr_number }}
            </a>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="Title" min-width="340">
          <template #default="{ row }">
            <el-tooltip
              :content="row.title || ''"
              placement="top-start"
              effect="dark"
              :show-after="120"
            >
              <div class="title-cell-ellipsis">{{ row.title || '-' }}</div>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by" label="Created By" width="130" />
        <el-table-column prop="cr_assignee" label="CR Assignee" width="130" />
        <el-table-column prop="cr_created_on" label="Created On" width="180">
          <template #default="{ row }">
            {{ formatDate(row.cr_created_on) }}
          </template>
        </el-table-column>
        <el-table-column prop="software_image_integration_build" label="Software Image Integration Build" min-width="260" show-overflow-tooltip />
        <el-table-column label="Actions" width="150">
          <template #default="{ row }">
            <el-button v-if="canEditBug()" size="small" @click="editBug(row)">Edit</el-button>
            <el-button v-if="canDeleteBug()" size="small" type="danger" @click="deleteBug(row.id)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="bugs-list-footer">
        <el-pagination
          :current-page="pagination.page"
          :page-size="pagination.pageSize"
          :page-sizes="[30, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="showExportDialog"
      title="Export Top N Bugs"
      width="420px"
    >
      <el-form label-width="120px">
        <el-form-item label="Rows to export">
          <el-input-number
            v-model="exportTopN"
            :min="1"
            :max="Math.max(1, pagination.total)"
            :step="1"
            controls-position="right"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button class="btn-style-3" @click="showExportDialog = false">Cancel</el-button>
        <el-button class="btn-style-2" type="primary" :loading="exporting" @click="handleExportTopN">Export</el-button>
      </template>
    </el-dialog>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingBug ? 'Edit Bug' : 'New Bug'"
      width="600px"
    >
      <el-form :model="bugForm" label-width="100px">
        <el-form-item label="CR Number">
          <el-input v-model="bugForm.external_cr_number" placeholder="Optional: from CSV CR Number" />
        </el-form-item>
        <el-form-item label="Test Task">
          <el-select v-model="bugForm.test_progress_id" clearable filterable placeholder="Manual link if no FR keyword" style="width: 100%">
            <el-option
              v-for="item in testOptions"
              :key="item.id"
              :label="`${item.fr_number || 'No FR'} | ${item.test_name}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="WorkTask">
          <el-select v-model="bugForm.work_task_id" clearable filterable placeholder="Optional manual link" style="width: 100%">
            <el-option
              v-for="task in workTaskOptions"
              :key="task.id"
              :label="`${task.task_key} | ${task.task_name}`"
              :value="task.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Title">
          <el-input v-model="bugForm.title" />
        </el-form-item>
        <el-form-item label="Created By">
          <el-input v-model="bugForm.created_by" />
        </el-form-item>
        <el-form-item label="CR Assignee">
          <el-input v-model="bugForm.cr_assignee" />
        </el-form-item>
        <el-form-item label="Created On">
          <el-input v-model="bugForm.cr_created_on" placeholder="MM/DD/YYYY h:mm:ss AM" />
        </el-form-item>
        <el-form-item label="Build">
          <el-input v-model="bugForm.software_image_integration_build" placeholder="Software Image Integration Build" />
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="bugForm.status">
            <el-option label="Fixed" value="fixed" />
            <el-option label="Analysis" value="analysis" />
            <el-option label="Other" value="other" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button class="btn-style-3" @click="showCreateDialog = false">Cancel</el-button>
        <el-button class="btn-style-2" type="primary" @click="saveBug">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  queryBugs,
  createBug,
  updateBug,
  deleteBug as deleteBugApi,
  getBugStats,
  getBugFilterOptions,
  importBugsFromCsvFile
} from '../api/bugs'
import { getTestProgressList } from '../api/testProgress'
import { getWorkTasks } from '../api/workTasks'
import { canCreateBug, canEditBug, canDeleteBug } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const bugsList = ref([])
const bugStats = ref({})
const showCreateDialog = ref(false)
const editingBug = ref(null)
const importingCsv = ref(false)
const exporting = ref(false)
const showExportDialog = ref(false)
const exportTopN = ref(30)
const csvFileInput = ref(null)
const testOptions = ref([])
const workTaskOptions = ref([])
const createdByOptions = ref([])
const statusOptions = ref([])
const pagination = ref({
  page: 1,
  pageSize: 30,
  total: 0
})

const filters = ref({
  status: null,
  created_by: null
})

const bugForm = ref({
  test_progress_id: null,
  work_task_id: null,
  external_cr_number: '',
  created_by: '',
  cr_assignee: '',
  cr_created_on: '',
  software_image_integration_build: '',
  title: '',
  severity: 'medium',
  status: 'other'
})

const buildQueryParams = (override = {}) => {
  const page = override.page ?? pagination.value.page
  const pageSize = override.pageSize ?? pagination.value.pageSize
  const params = {
    skip: Math.max(0, (page - 1) * pageSize),
    limit: pageSize
  }

  if (filters.value.status) params.status = filters.value.status
  if (filters.value.created_by) params.created_by = filters.value.created_by
  if (route.query.testId) params.test_id = Number(route.query.testId)

  return params
}

const loadData = async () => {
  loading.value = true
  try {
    const data = await queryBugs(buildQueryParams())
    bugsList.value = data?.items || []
    pagination.value.total = Number(data?.total || 0)
    
    // Load summary stats.
    const stats = await getBugStats()
    bugStats.value = stats
  } catch (error) {
    ElMessage.error('Failed to load data')
  } finally {
    loading.value = false
  }
}

const applyFilters = async () => {
  pagination.value.page = 1
  await loadData()
}

const resetFilters = () => {
  filters.value = {
    status: null,
    created_by: null
  }
  pagination.value.page = 1
  loadData()
}

const handlePageSizeChange = (size) => {
  pagination.value.pageSize = size
  pagination.value.page = 1
  loadData()
}

const handlePageChange = (page) => {
  pagination.value.page = page
  loadData()
}

const loadFilterOptions = async () => {
  try {
    const options = await getBugFilterOptions()
    createdByOptions.value = options?.created_by || []
    statusOptions.value = options?.status || []
  } catch {
    createdByOptions.value = []
    statusOptions.value = []
  }
}

const clearTestFilter = () => {
  router.push({ path: '/bugs' })
}

const openExportDialog = () => {
  if (!pagination.value.total) {
    ElMessage.warning('No data to export')
    return
  }
  exportTopN.value = Math.min(pagination.value.pageSize, pagination.value.total)
  showExportDialog.value = true
}

const escapeCsvCell = (value) => {
  const text = String(value ?? '')
  if (text.includes('"') || text.includes(',') || text.includes('\n')) {
    return `"${text.replaceAll('"', '""')}"`
  }
  return text
}

const downloadCsv = (rows) => {
  const headers = [
    'CR Number',
    'Title',
    'Status',
    'Created By',
    'CR Assignee',
    'Created On',
    'Software Image Integration Build'
  ]

  const lines = [headers.join(',')]
  rows.forEach((item) => {
    lines.push([
      item.external_cr_number || '',
      item.title || '',
      item.status || '',
      item.created_by || '',
      item.cr_assignee || '',
      item.cr_created_on || '',
      item.software_image_integration_build || ''
    ].map(escapeCsvCell).join(','))
  })

  const blob = new Blob(['\uFEFF' + lines.join('\n')], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `bugs_top_${rows.length}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

const handleExportTopN = async () => {
  const desired = Math.max(1, Number(exportTopN.value || 1))
  const limit = Math.min(desired, pagination.value.total)

  exporting.value = true
  try {
    const data = await queryBugs({ ...buildQueryParams({ page: 1, pageSize: limit }), skip: 0, limit })
    const rows = data?.items || []
    downloadCsv(rows)
    showExportDialog.value = false
    ElMessage.success(`Exported top ${rows.length} records`)
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to export data')
  } finally {
    exporting.value = false
  }
}

const loadReferenceOptions = async () => {
  try {
    const [tests, tasks] = await Promise.all([
      getTestProgressList({ limit: 500 }),
      getWorkTasks()
    ])
    testOptions.value = tests || []
    workTaskOptions.value = tasks || []
  } catch {
    testOptions.value = []
    workTaskOptions.value = []
  }
}

const importCsvBugs = async () => {
  if (!csvFileInput.value) return
  csvFileInput.value.value = ''
  csvFileInput.value.click()
}

const handleCsvFileSelected = async (event) => {
  const file = event?.target?.files?.[0]
  if (!file) return

  importingCsv.value = true
  try {
    const result = await importBugsFromCsvFile(file)
    ElMessage.success(
      `${file.name}: imported ${result.imported}, updated ${result.updated}, skipped ${result.skipped}`
    )
    await loadFilterOptions()
    await loadData()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to import CSV bugs')
  } finally {
    importingCsv.value = false
    if (event?.target) {
      event.target.value = ''
    }
  }
}

const getCrLink = (crNumber) => {
  return `https://orbit/CR/${encodeURIComponent(crNumber)}`
}

const getStatusBucket = (status) => {
  const text = (status || '').trim().toLowerCase().replace(/\s|_|-/g, '')
  if (['inprogress', 'build', 'closed', 'duplicate', 'fixed', 'resolved', 'verified', 'cannotduplicate'].includes(text)) {
    return 'fixed'
  }
  if (['open', 'analysis'].includes(text)) {
    return 'analysis'
  }
  return 'other'
}

const getStatusType = (status) => {
  const map = {
    fixed: 'success',
    analysis: 'warning',
    other: 'info'
  }
  return map[getStatusBucket(status)] || 'info'
}

const getStatusText = (status) => {
  return status || 'Other'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('en-US')
}

const getTableRowClassName = ({ row }) => {
  const created = row?.cr_created_on ? new Date(row.cr_created_on) : null
  if (!created || Number.isNaN(created.getTime())) return ''
  const now = new Date()
  const diffDays = Math.floor((now.getTime() - created.getTime()) / 86400000)
  if (diffDays > 14 && getStatusBucket(row.status) !== 'fixed') {
    return 'stale-cr-row'
  }
  return ''
}

const editBug = (bug) => {
  editingBug.value = bug
  bugForm.value = {
    test_progress_id: bug.test_progress_id,
    work_task_id: bug.work_task_id || null,
    external_cr_number: bug.external_cr_number || '',
    created_by: bug.created_by || '',
    cr_assignee: bug.cr_assignee || '',
    cr_created_on: bug.cr_created_on || '',
    software_image_integration_build: bug.software_image_integration_build || '',
    title: bug.title,
    severity: bug.severity,
    status: bug.status
  }
  showCreateDialog.value = true
}

const saveBug = async () => {
  try {
    if (editingBug.value) {
      await updateBug(editingBug.value.id, bugForm.value)
      ElMessage.success('Updated successfully')
    } else {
      await createBug(bugForm.value)
      ElMessage.success('Created successfully')
    }
    showCreateDialog.value = false
    editingBug.value = null
    bugForm.value = {
      test_progress_id: null,
      work_task_id: null,
      external_cr_number: '',
      created_by: '',
      cr_assignee: '',
      cr_created_on: '',
      software_image_integration_build: '',
      title: '',
      severity: 'medium',
      status: 'other'
    }
    await loadFilterOptions()
    loadData()
  } catch (error) {
    ElMessage.error('Failed to save')
  }
}

const deleteBug = async (id) => {
  try {
    await ElMessageBox.confirm('Are you sure you want to delete this bug?', 'Confirm', {
      confirmButtonText: 'Confirm',
      cancelButtonText: 'Cancel',
      type: 'warning'
    })
    await deleteBugApi(id)
    ElMessage.success('Deleted successfully')
    await loadFilterOptions()
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to delete')
    }
  }
}

onMounted(() => {
  loadReferenceOptions()
  loadFilterOptions()
  loadData()
})

watch(() => route.query.testId, () => {
  pagination.value.page = 1
  loadData()
})
</script>

<style scoped>
.bugs-container {
  width: 100%;
}

.filter-form {
  margin-bottom: 0;
}

.csv-file-input {
  display: none;
}

.cr-link {
  color: #7dd3fc;
  text-decoration: none;
  font-weight: 600;
}

.cr-link:hover {
  text-decoration: underline;
}

.filter-select {
  min-width: 180px;
}

:deep(.bugs-filter-popper .el-select-dropdown__item) {
  white-space: nowrap;
}

.bugs-container :deep(.stale-cr-row > td.el-table__cell) {
  background: rgba(239, 68, 68, 0.14) !important;
}

.bugs-list-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
}

.title-cell-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .filter-form :deep(.el-form-item) {
    margin-right: 0;
    width: 100%;
  }
}
</style>

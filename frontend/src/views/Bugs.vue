<template>
  <div class="page-shell bugs-container">
    <section class="page-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">{{ LT.heroEyebrow }}</div>
        <h2 class="page-hero__title">{{ LT.heroTitle }}</h2>
        <p class="page-hero__desc">{{ DT.hero }}</p>
      </div>
      <div class="page-hero__actions">
        <div v-if="route.query.testId" class="glass-pill">{{ LT.testFilterLabel }}: {{ route.query.testId }}</div>
        <el-button v-if="route.query.testId" class="btn-style-3" @click="clearTestFilter">{{ BT.backToAll }}</el-button>
        <el-button class="btn-style-1" :disabled="!pagination.total" @click="openExportDialog">{{ BT.exportTopN }}</el-button>
        <el-button v-if="canCreateBug()" class="btn-style-4" :loading="importingCsv" @click="importCsvBugs">{{ BT.importCsv }}</el-button>
        <el-button v-if="canCreateBug()" class="btn-style-2" type="primary" @click="openCreateBugDialog">
          <el-icon><Plus /></el-icon>
          {{ BT.newBug }}
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
        <div class="metric-card__label">{{ LT.metrics.total }}</div>
        <div class="metric-card__value">{{ bugStats.total || 0 }}</div>
        <div class="metric-card__meta">{{ DT.metricsMeta.total }}</div>
      </article>
      <article class="metric-card accent-red">
        <div class="metric-card__label">{{ LT.metrics.analysis }}</div>
        <div class="metric-card__value">{{ bugStats.by_status?.analysis || 0 }}</div>
        <div class="metric-card__meta">{{ DT.metricsMeta.analysis }}</div>
      </article>
      <article class="metric-card accent-orange">
        <div class="metric-card__label">{{ LT.metrics.other }}</div>
        <div class="metric-card__value">{{ bugStats.by_status?.other || 0 }}</div>
        <div class="metric-card__meta">{{ DT.metricsMeta.other }}</div>
      </article>
      <article class="metric-card accent-green">
        <div class="metric-card__label">{{ LT.metrics.fixed }}</div>
        <div class="metric-card__value">{{ bugStats.by_status?.fixed || 0 }}</div>
        <div class="metric-card__meta">{{ DT.metricsMeta.fixed }}</div>
      </article>
    </div>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>{{ LT.section.filterTitle }}</h3>
            <span class="section-title__meta">{{ DT.sectionMeta.filter }}</span>
          </div>
        </div>
      </template>

      <el-form :inline="true" class="filter-form">
        <el-form-item label="Verification">
          <el-select v-model="filters.verification_zone" class="filter-select" style="width: 180px" popper-class="bugs-filter-popper">
            <el-option label="All" value="all" />
            <el-option label="Waiting Build" value="waiting_build" />
            <el-option label="Pending Verification" value="pending_verification" />
            <el-option label="Verified" value="verified" />
            <el-option label="Discarded" value="discarded" />
          </el-select>
        </el-form-item>
        <el-form-item :label="LT.filter.status">
          <el-select v-model="filters.status" class="filter-select" :placeholder="DT.placeholders.all" clearable popper-class="bugs-filter-popper">
            <el-option
              v-for="status in statusOptions"
              :key="status"
              :label="status"
              :value="status"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="LT.filter.createdBy">
          <el-select
            v-model="filters.created_by"
            class="filter-select"
            :placeholder="DT.placeholders.all"
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
          <el-button class="btn-style-3" @click="resetFilters">{{ BTCommon.reset }}</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>{{ LT.section.listTitle }}</h3>
            <span class="section-title__meta">{{ pagination.total }} {{ DT.sectionMeta.list }}</span>
          </div>
        </div>
      </template>
      <BugTable
        :bugs="bugsList"
        :loading="loading"
        :show-actions="canEditBug() || canDeleteBug()"
        :show-verify-action="canEditBug()"
        :editable="canEditBug()"
        :deletable="canDeleteBug()"
        :is-verifying="isVerifying"
        :row-class-name="getTableRowClassName"
        @verify="markBugVerified"
        @edit="editBug"
        @delete="deleteBug"
      />

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
      :title="LT.dialog.exportTopNTitle"
      width="420px"
    >
      <el-form label-width="120px">
        <el-form-item label="Export Area">
          <el-select v-model="exportArea" style="width: 100%">
            <el-option label="All" value="all" />
            <el-option label="Waiting Build" value="waiting_build" />
            <el-option label="Pending Verification" value="pending_verification" />
            <el-option label="Verified" value="verified" />
            <el-option label="Discarded" value="discarded" />
          </el-select>
        </el-form-item>
        <el-form-item :label="LT.dialog.rowsToExport">
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
        <el-button class="btn-style-3" @click="showExportDialog = false">{{ BTCommon.cancel }}</el-button>
        <el-button class="btn-style-2" type="primary" :loading="exporting" @click="handleExportTopN">{{ BT.export }}</el-button>
      </template>
    </el-dialog>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingBug ? LT.dialog.editTitle : LT.dialog.newTitle"
      width="600px"
    >
      <el-form :model="bugForm" label-width="100px">
        <el-form-item :label="LT.form.crNumber">
          <el-input v-model="bugForm.external_cr_number" :placeholder="DT.placeholders.optionalCrNumber" />
        </el-form-item>
        <el-form-item :label="LT.form.testTask">
          <el-select v-model="bugForm.test_progress_id" clearable filterable :placeholder="DT.placeholders.noFrKeyword" style="width: 100%">
            <el-option
              v-for="item in testOptions"
              :key="item.id"
              :label="`${item.fr_number || 'No FR'} | ${item.test_name}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="LT.form.workTask">
          <el-select v-model="bugForm.work_task_id" clearable filterable :placeholder="DT.placeholders.optionalManualLink" style="width: 100%">
            <el-option
              v-for="task in workTaskOptions"
              :key="task.id"
              :label="`${task.task_key} | ${task.task_name}`"
              :value="task.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="LT.form.title">
          <el-input v-model="bugForm.title" />
        </el-form-item>
        <el-form-item :label="LT.form.createdBy">
          <el-input v-model="bugForm.created_by" />
        </el-form-item>
        <el-form-item :label="LT.form.crAssignee">
          <el-input v-model="bugForm.cr_assignee" />
        </el-form-item>
        <el-form-item :label="LT.form.createdOn">
          <el-input v-model="bugForm.cr_created_on" :placeholder="DT.placeholders.createdOnFormat" />
        </el-form-item>
        <el-form-item :label="LT.form.build">
          <el-select
            v-if="bugBuildOptions.length"
            v-model="bugForm.software_image_integration_build"
            clearable
            filterable
            placeholder="Select from available images"
            style="width: 100%"
          >
            <el-option
              v-for="image in bugBuildOptions"
              :key="image"
              :label="image"
              :value="image"
            />
          </el-select>
          <el-input v-else v-model="bugForm.software_image_integration_build" :placeholder="DT.placeholders.softwareBuild" />
        </el-form-item>
        <el-form-item :label="LT.form.status">
          <el-select v-model="bugForm.status">
            <el-option :label="LT.statusOptions.fixed" value="fixed" />
            <el-option :label="LT.statusOptions.analysis" value="analysis" />
            <el-option :label="LT.statusOptions.other" value="other" />
            <el-option :label="LT.statusOptions.verified" value="verified" />
            <el-option :label="LT.statusOptions.discarded" value="discarded" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button class="btn-style-3" @click="showCreateDialog = false">{{ BTCommon.cancel }}</el-button>
        <el-button class="btn-style-2" type="primary" @click="saveBug">{{ BTCommon.save }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import BugTable from '../components/bugs/BugTable.vue'
import { LabelText } from '../texts/LabelText'
import { ButtonText } from '../texts/ButtonText'
import { DescriptionText } from '../texts/DescriptionText'
import { getStatusBucket } from '../utils/bugDisplay'
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
const LT = LabelText.bugs
const BT = ButtonText.bugs
const BTCommon = ButtonText.common
const DT = DescriptionText.bugs
const loading = ref(false)
const bugsList = ref([])
const bugStats = ref({})
const showCreateDialog = ref(false)
const editingBug = ref(null)
const importingCsv = ref(false)
const exporting = ref(false)
const verifyingMap = ref({})
const showExportDialog = ref(false)
const exportTopN = ref(30)
const exportArea = ref('all')
const csvFileInput = ref(null)
const testOptions = ref([])
const workTaskOptions = ref([])
const createdByOptions = ref([])
const statusOptions = ref([])
const bugBuildOptions = ref([])
const pagination = ref({
  page: 1,
  pageSize: 30,
  total: 0
})

const filters = ref({
  verification_zone: 'waiting_build',
  status: null,
  created_by: null
})

const createEmptyBugForm = () => ({
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

const bugForm = ref(createEmptyBugForm())

const parseAvailableImages = (value = '') => {
  return String(value || '')
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

const getBugBuildOptions = (bug) => {
  const options = []
  const seen = new Set()
  const addOption = (value) => {
    const text = String(value || '').trim()
    const key = text.toLowerCase()
    if (!text || seen.has(key)) {
      return
    }
    seen.add(key)
    options.push(text)
  }

  parseAvailableImages(bug?.available_images).forEach(addOption)
  addOption(bug?.software_image_integration_build)
  return options
}

const buildQueryParams = (override = {}) => {
  const page = override.page ?? pagination.value.page
  const pageSize = override.pageSize ?? pagination.value.pageSize
  const params = {
    skip: Math.max(0, (page - 1) * pageSize),
    limit: pageSize
  }

  if (filters.value.verification_zone) params.verification_zone = filters.value.verification_zone
  if (filters.value.status) params.status = filters.value.status
  if (filters.value.created_by) params.created_by = filters.value.created_by
  if (route.query.testId) params.test_id = Number(route.query.testId)

  return params
}

const isVerifying = (row) => Boolean(verifyingMap.value?.[Number(row?.id)])
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

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
    ElMessage.error(DT.toast.loadFailed)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    verification_zone: 'waiting_build',
    status: null,
    created_by: null
  }
  pagination.value.page = 1
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
    ElMessage.warning(DT.toast.noDataToExport)
    return
  }
  exportArea.value = filters.value.verification_zone || 'all'
  exportTopN.value = Math.min(30, Math.max(1, pagination.value.total))
  showExportDialog.value = true
}

const escapeCsvCell = (value) => {
  const text = String(value ?? '')
  if (text.includes('"') || text.includes(',') || text.includes('\n')) {
    return `"${text.replaceAll('"', '""')}"`
  }
  return text
}

const downloadCsv = (rows, areaKey) => {
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
  link.download = `bugs_${areaKey}_top_${rows.length}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

const handleExportTopN = async () => {
  const desired = Math.max(1, Number(exportTopN.value || 1))
  const limit = desired

  exporting.value = true
  try {
    const data = await queryBugs({
      ...buildQueryParams({ page: 1, pageSize: limit }),
      skip: 0,
      limit,
      verification_zone: exportArea.value || 'all'
    })
    const rows = data?.items || []
    downloadCsv(rows, exportArea.value || 'all')
    showExportDialog.value = false
    ElMessage.success(`${DT.toast.exportSuccessPrefix} ${rows.length} ${DT.toast.exportSuccessSuffix}`)
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || DT.toast.exportFailed)
  } finally {
    exporting.value = false
  }
}

const toBugUpdatePayload = (row, patch = {}) => {
  return {
    test_progress_id: row.test_progress_id || null,
    work_task_id: row.work_task_id || null,
    external_cr_number: row.external_cr_number || '',
    created_by: row.created_by || '',
    cr_assignee: row.cr_assignee || '',
    cr_created_on: row.cr_created_on || '',
    software_image_integration_build: row.software_image_integration_build || '',
    title: row.title || '',
    severity: row.severity || 'medium',
    status: row.status || 'other',
    ...patch
  }
}

const markBugVerified = async (row) => {
  const bugId = Number(row?.id)
  if (!bugId || isVerifying(row)) {
    return
  }

  verifyingMap.value[bugId] = true
  try {
    await delay(1000)
    await updateBug(row.id, toBugUpdatePayload(row, { status: 'verified' }))
    ElMessage.success('Moved to Verified')
    await loadFilterOptions()
    await loadData()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || DT.toast.saveFailed)
  } finally {
    verifyingMap.value[bugId] = false
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
    ElMessage.error(error?.response?.data?.detail || DT.toast.importFailed)
  } finally {
    importingCsv.value = false
    if (event?.target) {
      event.target.value = ''
    }
  }
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

const openCreateBugDialog = () => {
  editingBug.value = null
  bugBuildOptions.value = []
  bugForm.value = createEmptyBugForm()
  showCreateDialog.value = true
}

const editBug = (bug) => {
  editingBug.value = bug
  bugBuildOptions.value = getBugBuildOptions(bug)
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
      ElMessage.success(DT.toast.updateSuccess)
    } else {
      await createBug(bugForm.value)
      ElMessage.success(DT.toast.createSuccess)
    }
    showCreateDialog.value = false
    editingBug.value = null
    bugBuildOptions.value = []
    bugForm.value = createEmptyBugForm()
    await loadFilterOptions()
    loadData()
  } catch (error) {
    ElMessage.error(DT.toast.saveFailed)
  }
}

const deleteBug = async (id) => {
  try {
    await ElMessageBox.confirm(DT.toast.deleteConfirmContent, DT.toast.deleteConfirmTitle, {
      confirmButtonText: BTCommon.confirm,
      cancelButtonText: BTCommon.cancel,
      type: 'warning'
    })
    await deleteBugApi(id)
    ElMessage.success(DT.toast.deleteSuccess)
    await loadFilterOptions()
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(DT.toast.deleteFailed)
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

watch(
  () => [filters.value.verification_zone, filters.value.status, filters.value.created_by],
  () => {
    pagination.value.page = 1
    loadData()
  }
)
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

.filter-select {
  min-width: 180px;
}

:deep(.bugs-filter-popper .el-select-dropdown__item) {
  white-space: nowrap;
}

.bugs-container :deep(.stale-cr-row > td.el-table__cell) {
  background: rgba(239, 68, 68, 0.14) !important;
}

@media (max-width: 768px) {
  .filter-form :deep(.el-form-item) {
    margin-right: 0;
    width: 100%;
  }
}
</style>

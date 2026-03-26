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
        <input ref="csvFileInput" type="file" accept=".csv,text/csv" class="csv-file-input" @change="handleCsvFileSelected" />
      </div>
    </section>

    <el-card class="section-card bug-chart-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>Bug Overview</h3>
            <span class="section-title__meta">Bugs with CR created date >= today - 365 days and monthly CR trend</span>
          </div>
        </div>
      </template>
      <BugOverviewPanel :stats="bugStats" />
    </el-card>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>{{ LT.section.filterTitle }}</h3>
            <span class="section-title__meta">{{ DT.sectionMeta.filter }}</span>
          </div>
        </div>
      </template>
      <BugFilterBar
        :filters="filters"
        :status-options="statusOptions"
        :created-by-options="createdByOptions"
        @update:filters="Object.assign(filters, $event)"
        @reset="resetFilters"
      />
    </el-card>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>{{ LT.section.listTitle }}</h3>
            <span class="section-title__meta">{{ pagination.total }} {{ DT.sectionMeta.list }}</span>
          </div>
          <BugListToolbar
            v-if="canDeleteBug() || canEditBug()"
            :bulk-action-mode="bulkActionMode"
            :selected-count="selectedBugIds.length"
            :can-edit="canEditBug()"
            :can-delete="canDeleteBug()"
            :bulk-verifying="bulkVerifying"
            :bulk-deleting="bulkDeleting"
            @enter-verify="enterBulkVerifyMode"
            @enter-delete="enterBulkDeleteMode"
            @cancel="cancelBulkActionMode"
            @confirm-verify="confirmBulkVerify"
            @confirm-delete="confirmBulkDelete"
          />
        </div>
      </template>

      <BugTable
        :bugs="bugsList"
        :loading="loading"
        :show-actions="canEditBug() || canDeleteBug()"
        :show-verify-action="canEditBug()"
        :editable="canEditBug()"
        :deletable="canDeleteBug()"
        :hide-delete-action="canDeleteBug()"
        :enable-selection="Boolean(bulkActionMode)"
        :clear-selection-key="bugTableSelectionResetKey"
        :is-verifying="isVerifying"
        :row-class-name="getTableRowClassName"
        @selection-change="handleBugSelectionChange"
        @verify="markBugVerified"
        @edit="editBug"
        @delete="deleteBug"
        @quick-pick-build="openQuickBuildDialog"
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

    <BugExportDialog
      v-model="showExportDialog"
      :area="exportArea"
      :top-n="exportTopN"
      :total="pagination.total"
      :exporting="exporting"
      @export="handleExportTopN"
    />

    <BugQuickBuildDialog
      v-model="showQuickBuildDialog"
      :bug="quickBuildTargetBug"
      :options="quickBuildOptions"
      :selection="quickBuildSelection"
      :saving="quickBuildSaving"
      @save="saveQuickBuildSelection"
      @update:model-value="if (!$event) closeQuickBuildDialog()"
    />

    <BugCreateDialog
      v-model="showCreateDialog"
      :form="bugForm"
      :is-editing="Boolean(editingBug)"
      :build-options="bugBuildOptions"
      :test-options="testOptions"
      :work-task-options="workTaskOptions"
      @save="saveBug"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import BugTable from '../components/bugs/BugTable.vue'
import BugOverviewPanel from '../components/bugs/BugOverviewPanel.vue'
import BugFilterBar from '../components/bugs/BugFilterBar.vue'
import BugListToolbar from '../components/bugs/BugListToolbar.vue'
import BugCreateDialog from '../components/bugs/BugCreateDialog.vue'
import BugExportDialog from '../components/bugs/BugExportDialog.vue'
import BugQuickBuildDialog from '../components/bugs/BugQuickBuildDialog.vue'
import { LabelText } from '../texts/LabelText'
import { ButtonText } from '../texts/ButtonText'
import { DescriptionText } from '../texts/DescriptionText'
import { getStatusBucket } from '../utils/bugDisplay'
import { useFilterState, usePaginationState } from '../composables/useListState'
import { useAsyncAction } from '../composables/useAsyncAction'
import {
  queryBugs, createBug, updateBug, deleteBug as deleteBugApi,
  getBugStats, getBugFilterOptions, importBugsFromCsvFile
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
const { runAsync } = useAsyncAction()

const loading = ref(false)
const bugsList = ref([])
const bugStats = ref({})
const showCreateDialog = ref(false)
const editingBug = ref(null)
const importingCsv = ref(false)
const exporting = ref(false)
const verifyingMap = ref({})
const showQuickBuildDialog = ref(false)
const quickBuildSaving = ref(false)
const quickBuildTargetBug = ref(null)
const quickBuildOptions = ref([])
const quickBuildSelection = ref('')
const bulkActionMode = ref('')
const bulkDeleting = ref(false)
const bulkVerifying = ref(false)
const selectedBugIds = ref([])
const bugTableSelectionResetKey = ref(0)
const showExportDialog = ref(false)
const exportTopN = ref(30)
const exportArea = ref('all')
const csvFileInput = ref(null)
const testOptions = ref([])
const workTaskOptions = ref([])
const createdByOptions = ref([])
const statusOptions = ref([])
const bugBuildOptions = ref([])

const { pagination, resetPage, setPage, setPageSize, setTotal } = usePaginationState({ page: 1, pageSize: 30, total: 0 })
const { filters, resetFilters: resetFilterState } = useFilterState({ verification_zone: 'waiting_build', status: null, created_by: null })

const createEmptyBugForm = () => ({
  test_progress_id: null, work_task_id: null, external_cr_number: '',
  created_by: '', cr_assignee: '', cr_created_on: '',
  software_image_integration_build: '', title: '', severity: 'medium', status: 'other'
})

const bugForm = ref(createEmptyBugForm())

const isPendingConfirmationBuild = (value) => String(value || '').trim().toLowerCase() === 'pending confirmation'

const parseAvailableImages = (value = '') =>
  String(value || '').split(',').map(item => item.trim()).filter(Boolean)

const getBugBuildOptions = (bug) => {
  const options = [], seen = new Set()
  const addOption = (value) => {
    const text = String(value || '').trim()
    const key = text.toLowerCase()
    if (!text || seen.has(key)) return
    seen.add(key); options.push(text)
  }
  parseAvailableImages(bug?.available_images).forEach(addOption)
  addOption(bug?.software_image_integration_build)
  return options
}

const getQuickBuildOptions = (bug) => {
  const options = [], seen = new Set()
  parseAvailableImages(bug?.available_images).forEach(item => {
    const text = String(item || '').trim()
    const key = text.toLowerCase()
    if (!text || isPendingConfirmationBuild(text) || seen.has(key)) return
    seen.add(key); options.push(text)
  })
  return options
}

const closeQuickBuildDialog = () => {
  showQuickBuildDialog.value = false
  quickBuildTargetBug.value = null
  quickBuildOptions.value = []
  quickBuildSelection.value = ''
}

const openQuickBuildDialog = (bug) => {
  if (!canEditBug() || !isPendingConfirmationBuild(bug?.software_image_integration_build)) return
  const options = getQuickBuildOptions(bug)
  if (!options.length) { ElMessage.warning(DT.toast.noAvailableImage); return }
  quickBuildTargetBug.value = bug
  quickBuildOptions.value = options
  quickBuildSelection.value = options[0]
  showQuickBuildDialog.value = true
}

const saveQuickBuildSelection = async (selectedImage) => {
  const target = quickBuildTargetBug.value
  const image = String(selectedImage || '').trim()
  if (!target?.id || !image) { ElMessage.warning(DT.toast.selectImageRequired); return }
  await runAsync(async () => {
    await updateBug(target.id, toBugUpdatePayload(target, { software_image_integration_build: image }))
    ElMessage.success(DT.toast.quickBuildUpdated)
    closeQuickBuildDialog()
    await loadFilterOptions()
    await loadData()
  }, { loadingRef: quickBuildSaving, errorMessage: DT.toast.saveFailed })
}

const buildQueryParams = (override = {}) => {
  const page = override.page ?? pagination.value.page
  const pageSize = override.pageSize ?? pagination.value.pageSize
  const params = { skip: Math.max(0, (page - 1) * pageSize), limit: pageSize, recent_days: 365 }
  if (filters.value.verification_zone) params.verification_zone = filters.value.verification_zone
  if (filters.value.status) params.status = filters.value.status
  if (filters.value.created_by) params.created_by = filters.value.created_by
  if (route.query.testId) params.test_id = Number(route.query.testId)
  return params
}

const isVerifying = (row) => Boolean(verifyingMap.value?.[Number(row?.id)])
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms))

const loadData = async () => {
  await runAsync(async () => {
    const data = await queryBugs(buildQueryParams())
    bugsList.value = data?.items || []
    setTotal(data?.total)
    if (bulkActionMode.value) {
      const currentIds = new Set((bugsList.value || []).map(item => Number(item.id)))
      selectedBugIds.value = selectedBugIds.value.filter(id => currentIds.has(Number(id)))
    }
    const stats = await getBugStats({ recent_days: 365 })
    bugStats.value = stats
  }, { loadingRef: loading, errorMessage: DT.toast.loadFailed })
}

const resetFilters = () => { resetFilterState(); resetPage() }
const handlePageSizeChange = (size) => { setPageSize(size); loadData() }
const handlePageChange = (page) => { setPage(page); loadData() }

const enterBulkVerifyMode = () => { bulkActionMode.value = 'verify'; selectedBugIds.value = []; bugTableSelectionResetKey.value += 1 }
const enterBulkDeleteMode = () => { bulkActionMode.value = 'delete'; selectedBugIds.value = []; bugTableSelectionResetKey.value += 1 }
const cancelBulkActionMode = () => { bulkActionMode.value = ''; selectedBugIds.value = []; bugTableSelectionResetKey.value += 1 }

const handleBugSelectionChange = (rows) => {
  if (!bulkActionMode.value) return
  selectedBugIds.value = (rows || []).map(row => Number(row.id)).filter(id => Number.isFinite(id))
}

const confirmBulkVerify = async () => {
  const ids = [...selectedBugIds.value]
  if (!ids.length) { ElMessage.warning(DT.toast.selectBugsToVerify); return }
  const bugMap = new Map((bugsList.value || []).map(item => [Number(item.id), item]))
  try {
    await ElMessageBox.confirm(
      `${DT.toast.bulkVerifyConfirmPrefix} ${ids.length} ${DT.toast.bulkVerifyConfirmSuffix}`,
      DT.toast.bulkVerifyConfirmTitle,
      { confirmButtonText: BTCommon.confirm, cancelButtonText: BTCommon.cancel, type: 'warning' }
    )
  } catch { return }
  bulkVerifying.value = true
  try {
    const results = await Promise.allSettled(ids.map(id => {
      const bug = bugMap.get(Number(id))
      if (!bug) return Promise.reject(new Error(`Bug ${id} not found`))
      return updateBug(id, toBugUpdatePayload(bug, { status: 'verified' }))
    }))
    const successCount = results.filter(item => item.status === 'fulfilled').length
    const failedCount = results.length - successCount
    if (successCount > 0) ElMessage.success(`${DT.toast.bulkVerifySuccessPrefix} ${successCount} ${DT.toast.bulkVerifySuccessSuffix}`)
    if (failedCount > 0) ElMessage.error(`${DT.toast.bulkVerifyFailedPrefix} ${failedCount} ${DT.toast.bulkVerifyFailedSuffix}`)
    await loadFilterOptions(); await loadData(); cancelBulkActionMode()
  } finally { bulkVerifying.value = false }
}

const confirmBulkDelete = async () => {
  const ids = [...selectedBugIds.value]
  if (!ids.length) { ElMessage.warning(DT.toast.selectBugsToDelete); return }
  try {
    await ElMessageBox.confirm(
      `${DT.toast.bulkDeleteConfirmPrefix} ${ids.length} ${DT.toast.bulkDeleteConfirmSuffix}`,
      DT.toast.bulkDeleteConfirmTitle,
      { confirmButtonText: BTCommon.confirm, cancelButtonText: BTCommon.cancel, type: 'warning' }
    )
  } catch { return }
  bulkDeleting.value = true
  try {
    const results = await Promise.allSettled(ids.map(id => deleteBugApi(id)))
    const successCount = results.filter(item => item.status === 'fulfilled').length
    const failedCount = results.length - successCount
    if (successCount > 0) ElMessage.success(`${DT.toast.bulkDeleteSuccessPrefix} ${successCount} ${DT.toast.bulkDeleteSuccessSuffix}`)
    if (failedCount > 0) ElMessage.error(`${DT.toast.bulkDeleteFailedPrefix} ${failedCount} ${DT.toast.bulkDeleteFailedSuffix}`)
    await loadFilterOptions(); await loadData(); cancelBulkActionMode()
  } finally { bulkDeleting.value = false }
}

const loadFilterOptions = async () => {
  await runAsync(async () => {
    const options = await getBugFilterOptions()
    createdByOptions.value = options?.created_by || []
    statusOptions.value = options?.status || []
  }, { onError: () => { createdByOptions.value = []; statusOptions.value = [] } })
}

const clearTestFilter = () => router.push({ path: '/bugs' })

const openExportDialog = () => {
  if (!pagination.value.total) { ElMessage.warning(DT.toast.noDataToExport); return }
  exportArea.value = filters.value.verification_zone || 'all'
  exportTopN.value = Math.min(30, Math.max(1, pagination.value.total))
  showExportDialog.value = true
}

const escapeCsvCell = (value) => {
  const text = String(value ?? '')
  if (text.includes('"') || text.includes(',') || text.includes('\n')) return `"${text.replaceAll('"', '""')}"`
  return text
}

const downloadCsv = (rows, areaKey) => {
  const headers = ['CR Number', 'Title', 'Status', 'Created By', 'CR Assignee', 'Created On', 'Software Image Integration Build']
  const lines = [headers.join(',')]
  rows.forEach(item => {
    lines.push([
      item.external_cr_number || '', item.title || '', item.status || '',
      item.created_by || '', item.cr_assignee || '', item.cr_created_on || '',
      item.software_image_integration_build || ''
    ].map(escapeCsvCell).join(','))
  })
  const blob = new Blob(['\uFEFF' + lines.join('\n')], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url; link.download = `bugs_${areaKey}_top_${rows.length}.csv`
  document.body.appendChild(link); link.click(); document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

const handleExportTopN = async ({ area, topN }) => {
  const limit = Math.max(1, Number(topN || 1))
  await runAsync(async () => {
    const data = await queryBugs({ ...buildQueryParams({ page: 1, pageSize: limit }), skip: 0, limit, verification_zone: area || 'all' })
    const rows = data?.items || []
    downloadCsv(rows, area || 'all')
    showExportDialog.value = false
    ElMessage.success(`${DT.toast.exportSuccessPrefix} ${rows.length} ${DT.toast.exportSuccessSuffix}`)
  }, { loadingRef: exporting, errorMessage: DT.toast.exportFailed })
}

const toBugUpdatePayload = (row, patch = {}) => ({
  test_progress_id: row.test_progress_id || null, work_task_id: row.work_task_id || null,
  external_cr_number: row.external_cr_number || '', created_by: row.created_by || '',
  cr_assignee: row.cr_assignee || '', cr_created_on: row.cr_created_on || '',
  software_image_integration_build: row.software_image_integration_build || '',
  title: row.title || '', severity: row.severity || 'medium', status: row.status || 'other',
  ...patch
})

const markBugVerified = async (row) => {
  const bugId = Number(row?.id)
  if (!bugId || isVerifying(row)) return
  verifyingMap.value[bugId] = true
  await runAsync(async () => {
    await delay(1000)
    await updateBug(row.id, toBugUpdatePayload(row, { status: 'verified' }))
    ElMessage.success(DT.toast.movedToVerified)
    await loadFilterOptions(); await loadData()
  }, { errorMessage: DT.toast.saveFailed, onFinally: () => { verifyingMap.value[bugId] = false } })
}

const loadReferenceOptions = async () => {
  await runAsync(async () => {
    const [tests, tasks] = await Promise.all([getTestProgressList({ limit: 500 }), getWorkTasks()])
    testOptions.value = tests || []; workTaskOptions.value = tasks || []
  }, { onError: () => { testOptions.value = []; workTaskOptions.value = [] } })
}

const importCsvBugs = async () => {
  if (!csvFileInput.value) return
  csvFileInput.value.value = ''; csvFileInput.value.click()
}

const handleCsvFileSelected = async (event) => {
  const file = event?.target?.files?.[0]
  if (!file) return
  await runAsync(async () => {
    const result = await importBugsFromCsvFile(file)
    ElMessage.success(`${file.name}: imported ${result.imported}, updated ${result.updated}, skipped ${result.skipped}`)
    await loadFilterOptions(); await loadData()
  }, { loadingRef: importingCsv, errorMessage: DT.toast.importFailed, onFinally: () => { if (event?.target) event.target.value = '' } })
}

const getTableRowClassName = ({ row }) => {
  const created = row?.cr_created_on ? new Date(row.cr_created_on) : null
  if (!created || Number.isNaN(created.getTime())) return ''
  const diffDays = Math.floor((new Date().getTime() - created.getTime()) / 86400000)
  return diffDays > 14 && getStatusBucket(row.status) !== 'fixed' ? 'stale-cr-row' : ''
}

const openCreateBugDialog = () => {
  editingBug.value = null; bugBuildOptions.value = []; bugForm.value = createEmptyBugForm(); showCreateDialog.value = true
}

const editBug = (bug) => {
  editingBug.value = bug
  bugBuildOptions.value = getBugBuildOptions(bug)
  bugForm.value = {
    test_progress_id: bug.test_progress_id, work_task_id: bug.work_task_id || null,
    external_cr_number: bug.external_cr_number || '', created_by: bug.created_by || '',
    cr_assignee: bug.cr_assignee || '', cr_created_on: bug.cr_created_on || '',
    software_image_integration_build: bug.software_image_integration_build || '',
    title: bug.title, severity: bug.severity, status: bug.status
  }
  showCreateDialog.value = true
}

const saveBug = async () => {
  await runAsync(async () => {
    if (editingBug.value) {
      await updateBug(editingBug.value.id, bugForm.value)
      ElMessage.success(DT.toast.updateSuccess)
    } else {
      await createBug(bugForm.value)
      ElMessage.success(DT.toast.createSuccess)
    }
    showCreateDialog.value = false; editingBug.value = null; bugBuildOptions.value = []
    bugForm.value = createEmptyBugForm()
    await loadFilterOptions(); loadData()
  }, { errorMessage: DT.toast.saveFailed })
}

const deleteBug = async (id) => {
  try {
    await ElMessageBox.confirm(DT.toast.deleteConfirmContent, DT.toast.deleteConfirmTitle, {
      confirmButtonText: BTCommon.confirm, cancelButtonText: BTCommon.cancel, type: 'warning'
    })
    await deleteBugApi(id)
    ElMessage.success(DT.toast.deleteSuccess)
    await loadFilterOptions(); loadData()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error(DT.toast.deleteFailed)
  }
}

onMounted(() => { loadReferenceOptions(); loadFilterOptions(); loadData() })

watch(() => route.query.testId, () => { resetPage(); loadData() })

watch(
  () => [filters.value.verification_zone, filters.value.status, filters.value.created_by],
  () => { resetPage(); loadData() }
)
</script>

<style scoped>
.bugs-container { width: 100%; }
.csv-file-input { display: none; }
.bug-chart-card { margin-bottom: 24px; }

.bugs-container :deep(.stale-cr-row > td.el-table__cell) {
  background: rgba(239, 68, 68, 0.14) !important;
}

.bugs-list-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>

<template>
  <div class="page-shell detail-container">
    <section class="page-hero detail-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">{{ LT.heroEyebrow }}</div>
        <h2 class="page-hero__title">{{ LT.heroTitle }}</h2>
        <p class="page-hero__desc">{{ DT.hero }}</p>
      </div>
      <div class="page-hero__actions">
        <el-button v-if="canCreateOrEditTest()" class="btn-style-4" @click="openEditDialog">{{ BT.edit }}</el-button>
        <el-button v-if="canEditBug()" class="btn-style-2" @click="goToBugs">{{ BT.manageBugs }}</el-button>
      </div>
    </section>

    <el-card v-loading="loading" class="section-card detail-card">
      <template v-if="testDetail">
        <div class="detail-header">
          <div>
            <h2>{{ testDetail.fr_number || '-' }}: {{ testDetail.test_name }}</h2>
            <p class="detail-subtitle">{{ testDetail.model_name || LT.noFeatureSummary }}</p>
          </div>
          <div class="inline-stats">
            <div class="glass-pill">
              <span>{{ LT.status }}: </span>
              <el-tag :type="getStatusType(testDetail.status)" size="small">
                {{ getStatusText(testDetail.status) }}
              </el-tag>
            </div>
            <div class="glass-pill">{{ LT.createdOn }} {{ formatDateTimeText(testDetail.created_at) }}</div>
          </div>
        </div>

        <div class="metrics-grid detail-metrics">
          <MetricCard
            :label="LT.metrics.currentProgress"
            :value="`${testDetail.progress}%`"
            :meta="DT.metricsMeta.currentProgress"
            accent="blue"
            size="sm"
          />
          <MetricCard
            :label="LT.metrics.passedTotal"
            :value="`${testDetail.passed_cases}/${testDetail.total_cases}`"
            :meta="DT.metricsMeta.passedTotal"
            accent="green"
            size="sm"
          />
          <MetricCard
            :label="LT.metrics.linkedBugs"
            :value="testDetail.bugs?.length || 0"
            :meta="DT.metricsMeta.linkedBugs"
            accent="red"
            size="sm"
          />
          <MetricCard
            :label="LT.metrics.estimatedManday"
            :value="formatManday(testDetail.estimated_hours)"
            :meta="DT.metricsMeta.estimatedManday"
            accent="purple"
            size="sm"
          />
        </div>

        <el-card class="section-card detail-inner-card">
          <template #header>
            <div class="section-title">
              <div class="section-title__main">
                <h3>{{ LT.section.featureConfig }}</h3>
                <span class="section-title__meta">{{ DT.sectionMeta.featureConfig }}</span>
              </div>
            </div>
          </template>
          <el-descriptions :column="1" border class="detail-info">
            <el-descriptions-item :label="LT.info.featureSummary">
              <div class="description-text">{{ testDetail.model_name || '-' }}</div>
            </el-descriptions-item>
            <el-descriptions-item :label="LT.info.frNumber">
              <div class="description-text">{{ testDetail.fr_number || '-' }}</div>
            </el-descriptions-item>
            <el-descriptions-item :label="LT.info.detailedDescription">
              <div class="description-text">{{ testDetail.description || '-' }}</div>
            </el-descriptions-item>
            <el-descriptions-item :label="LT.info.configMethod">
              <div class="description-text">{{ testDetail.config_method || '-' }}</div>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="section-card detail-inner-card">
          <template #header>
            <div class="section-title">
              <div class="section-title__main">
                <h3>{{ LT.section.stageStats }}</h3>
                <span class="section-title__meta">{{ DT.sectionMeta.stageStats }}</span>
              </div>
            </div>
          </template>
          <el-descriptions :column="2" border class="detail-info">
            <el-descriptions-item :label="LT.info.status">{{ getStatusText(testDetail.status) }}</el-descriptions-item>
            <el-descriptions-item :label="LT.info.testers">{{ testDetail.test_owners || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="LT.info.developers">{{ testDetail.developers || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="LT.info.estimatedManday">{{ formatManday(testDetail.estimated_hours) }}</el-descriptions-item>
            <el-descriptions-item :label="LT.info.startDate">{{ getStartDate(testDetail) }}</el-descriptions-item>
            <el-descriptions-item :label="LT.info.completionDate">{{ getCompletionDate(testDetail) }}</el-descriptions-item>
            <el-descriptions-item :label="LT.info.l0">
              <div class="case-stats">
                <span class="pass-count">{{ testDetail.l0_passed_cases }}</span>
                <span class="sep">/</span>
                <span class="fail-count">{{ getStageFailed(testDetail, 'l0') }}</span>
                <span class="sep">/</span>
                <span class="total-count">{{ testDetail.l0_total_cases }}</span>
              </div>
            </el-descriptions-item>
            <el-descriptions-item :label="LT.info.l0DueDate">
              <span :class="`due-date-text due-date-text--${getStageDeadlineLevel(testDetail, 'l0')}`">
                {{ formatDueDate(testDetail.l0_due_date) }}
              </span>
            </el-descriptions-item>
            <el-descriptions-item :label="LT.info.l2">
              <div class="case-stats">
                <span class="pass-count">{{ testDetail.l2_passed_cases }}</span>
                <span class="sep">/</span>
                <span class="fail-count">{{ getStageFailed(testDetail, 'l2') }}</span>
                <span class="sep">/</span>
                <span class="total-count">{{ testDetail.l2_total_cases }}</span>
              </div>
            </el-descriptions-item>
            <el-descriptions-item :label="LT.info.l2DueDate">
              <span :class="`due-date-text due-date-text--${getStageDeadlineLevel(testDetail, 'l2')}`">
                {{ formatDueDate(testDetail.l2_due_date) }}
              </span>
            </el-descriptions-item>
            <el-descriptions-item :label="LT.info.l4">
              <div class="case-stats">
                <span class="pass-count">{{ testDetail.l4_passed_cases }}</span>
                <span class="sep">/</span>
                <span class="fail-count">{{ getStageFailed(testDetail, 'l4') }}</span>
                <span class="sep">/</span>
                <span class="total-count">{{ testDetail.l4_total_cases }}</span>
              </div>
            </el-descriptions-item>
            <el-descriptions-item :label="LT.info.l4DueDate">
              <span :class="`due-date-text due-date-text--${getStageDeadlineLevel(testDetail, 'l4')}`">
                {{ formatDueDate(testDetail.l4_due_date) }}
              </span>
            </el-descriptions-item>
            <el-descriptions-item :label="LT.info.overall">
              <div class="case-stats">
                <span class="pass-count">{{ testDetail.passed_cases }}</span>
                <span class="sep">/</span>
                <span class="fail-count">{{ getTotalFailed(testDetail) }}</span>
                <span class="sep">/</span>
                <span class="total-count">{{ testDetail.total_cases }}</span>
              </div>
            </el-descriptions-item>
            <el-descriptions-item :label="LT.info.progress">
              <el-progress :percentage="testDetail.progress" :status="getProgressStatus(testDetail.status)" style="width: 200px" />
            </el-descriptions-item>
            <el-descriptions-item :label="LT.info.createdAt">{{ formatDateTimeText(testDetail.created_at) }}</el-descriptions-item>
            <el-descriptions-item :label="LT.info.updatedAt">{{ formatDateTimeText(testDetail.updated_at) || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card id="linked-bugs-section" class="section-card detail-inner-card">
          <template #header>
            <div class="section-title">
              <div class="section-title__main">
                <h3>{{ LT.section.linkedBugs }} ({{ testDetail.bugs?.length || 0 }})</h3>
                <span class="section-title__meta">{{ DT.sectionMeta.linkedBugs }}</span>
              </div>
              <div v-if="canEditBug()" class="bug-bulk-toolbar">
                <template v-if="!bulkVerifyMode">
                  <el-button class="btn-style-2" @click="enterBulkVerifyMode">{{ BT.bulkVerify }}</el-button>
                </template>
                <template v-else>
                  <el-button class="btn-style-3" @click="cancelBulkVerifyMode">{{ BTCommon.cancel }}</el-button>
                  <el-button
                    class="btn-style-2"
                    :disabled="!totalSelectedCount"
                    :loading="bulkVerifying"
                    @click="confirmBulkVerify"
                  >
                    {{ BT.confirmBulkVerify }} ({{ totalSelectedCount }})
                  </el-button>
                </template>
              </div>
            </div>
          </template>
          <div class="bug-zone-stack">
            <section class="bug-zone-item">
              <div class="bug-zone-item__title">{{ LT.bugZones.pendingBuild }} ({{ allPendingBuildBugs.length }})</div>
              <BugTable
                :bugs="pendingBuildBugs"
                :empty-text="DT.tableEmptyBugs"
                :show-actions="canEditBug() || canDeleteBug()"
                :show-verify-action="canEditBug()"
                :editable="canEditBug()"
                :deletable="canDeleteBug()"
                :enable-selection="bulkVerifyMode"
                :clear-selection-key="bugTableSelectionResetKey"
                :is-verifying="isVerifying"
                :row-class-name="getBugTableRowClassName"
                @selection-change="handlePendingBuildSelectionChange"
                @verify="markBugVerified"
                @edit="editBug"
                @delete="deleteBug"
              />
              <div v-if="allPendingBuildBugs.length > BUG_ZONE_PAGE_SIZE" class="bug-zone-pagination">
                <el-pagination
                  :current-page="pendingBuildPage"
                  :page-size="BUG_ZONE_PAGE_SIZE"
                  :total="allPendingBuildBugs.length"
                  layout="total, prev, pager, next"
                  @current-change="pendingBuildPage = $event"
                />
              </div>
            </section>

            <section class="bug-zone-item">
              <div class="bug-zone-item__title">{{ LT.bugZones.pendingVerification }} ({{ allPendingVerificationBugs.length }})</div>
              <BugTable
                :bugs="pendingVerificationBugs"
                :empty-text="DT.tableEmptyBugs"
                :show-actions="canEditBug() || canDeleteBug()"
                :show-verify-action="canEditBug()"
                :editable="canEditBug()"
                :deletable="canDeleteBug()"
                :enable-selection="bulkVerifyMode"
                :clear-selection-key="bugTableSelectionResetKey"
                :is-verifying="isVerifying"
                :row-class-name="getBugTableRowClassName"
                @selection-change="handlePendingVerificationSelectionChange"
                @verify="markBugVerified"
                @edit="editBug"
                @delete="deleteBug"
              />
              <div v-if="allPendingVerificationBugs.length > BUG_ZONE_PAGE_SIZE" class="bug-zone-pagination">
                <el-pagination
                  :current-page="pendingVerificationPage"
                  :page-size="BUG_ZONE_PAGE_SIZE"
                  :total="allPendingVerificationBugs.length"
                  layout="total, prev, pager, next"
                  @current-change="pendingVerificationPage = $event"
                />
              </div>
            </section>

            <section class="bug-zone-item">
              <div class="bug-zone-item__title">{{ LT.bugZones.verified }} ({{ allVerifiedBugs.length }})</div>
              <BugTable
                :bugs="verifiedBugs"
                :empty-text="DT.tableEmptyBugs"
                :show-actions="canEditBug() || canDeleteBug()"
                :show-verify-action="canEditBug()"
                :editable="canEditBug()"
                :deletable="canDeleteBug()"
                :enable-selection="bulkVerifyMode"
                :clear-selection-key="bugTableSelectionResetKey"
                :is-verifying="isVerifying"
                :row-class-name="getBugTableRowClassName"
                @selection-change="handleVerifiedSelectionChange"
                @verify="markBugVerified"
                @edit="editBug"
                @delete="deleteBug"
              />
              <div v-if="allVerifiedBugs.length > BUG_ZONE_PAGE_SIZE" class="bug-zone-pagination">
                <el-pagination
                  :current-page="verifiedPage"
                  :page-size="BUG_ZONE_PAGE_SIZE"
                  :total="allVerifiedBugs.length"
                  layout="total, prev, pager, next"
                  @current-change="verifiedPage = $event"
                />
              </div>
            </section>
          </div>
        </el-card>

        <el-dialog
          v-model="showBugDialog"
          :title="LTBug.dialog.editTitle"
          width="600px"
        >
          <el-form :model="bugForm" label-width="100px">
            <el-form-item :label="LTBug.form.crNumber">
              <el-input v-model="bugForm.external_cr_number" :placeholder="DTBug.placeholders.optionalCrNumber" />
            </el-form-item>
            <el-form-item :label="LTBug.form.testTask">
              <el-select v-model="bugForm.test_progress_id" clearable filterable :placeholder="DTBug.placeholders.noFrKeyword" style="width: 100%">
                <el-option
                  v-for="item in testOptions"
                  :key="item.id"
                  :label="`${item.fr_number || LTBug.form.noFr} | ${item.test_name}`"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item :label="LTBug.form.workTask">
              <el-select v-model="bugForm.work_task_id" clearable filterable :placeholder="DTBug.placeholders.optionalManualLink" style="width: 100%">
                <el-option
                  v-for="task in workTaskOptions"
                  :key="task.id"
                  :label="`${task.task_key} | ${task.task_name}`"
                  :value="task.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item :label="LTBug.form.title">
              <el-input v-model="bugForm.title" />
            </el-form-item>
            <el-form-item :label="LTBug.form.createdBy">
              <el-input v-model="bugForm.created_by" />
            </el-form-item>
            <el-form-item :label="LTBug.form.crAssignee">
              <el-input v-model="bugForm.cr_assignee" />
            </el-form-item>
            <el-form-item :label="LTBug.form.createdOn">
              <el-input v-model="bugForm.cr_created_on" :placeholder="DTBug.placeholders.createdOnFormat" />
            </el-form-item>
            <el-form-item :label="LTBug.form.build">
              <el-select
                v-if="bugBuildOptions.length"
                v-model="bugForm.software_image_integration_build"
                clearable
                filterable
                :placeholder="DTBug.placeholders.selectFromAvailableImages"
                style="width: 100%"
              >
                <el-option
                  v-for="image in bugBuildOptions"
                  :key="image"
                  :label="image"
                  :value="image"
                />
              </el-select>
              <el-input v-else v-model="bugForm.software_image_integration_build" :placeholder="DTBug.placeholders.softwareBuild" />
            </el-form-item>
            <el-form-item :label="LTBug.form.status">
              <el-select v-model="bugForm.status">
                <el-option :label="LTBug.statusOptions.fixed" value="fixed" />
                <el-option :label="LTBug.statusOptions.analysis" value="analysis" />
                <el-option :label="LTBug.statusOptions.other" value="other" />
                <el-option :label="LTBug.statusOptions.verified" value="verified" />
                <el-option :label="LTBug.statusOptions.discarded" value="discarded" />
              </el-select>
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button class="btn-style-3" @click="showBugDialog = false">{{ BTCommon.cancel }}</el-button>
            <el-button class="btn-style-2" @click="saveBug">{{ BTCommon.save }}</el-button>
          </template>
        </el-dialog>
      </template>
    </el-card>

    <TestCreateDialog
      v-model="showEditDialog"
      :form="editForm"
      :is-editing="true"
      :owner-options="ownerOptions"
      @save="saveEdit"
    />
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import BugTable from '../components/bugs/BugTable.vue'
import MetricCard from '../components/common/MetricCard.vue'
import TestCreateDialog from '../components/testProgress/TestCreateDialog.vue'
import { getTestProgressDetail, getTestProgressList, updateTestProgress } from '../api/testProgress'
import { updateBug, deleteBug as deleteBugApi } from '../api/bugs'
import { getWorkTasks } from '../api/workTasks'
import { canEditBug, canDeleteBug, canCreateOrEditTest } from '../stores/auth'
import { LabelText } from '../texts/LabelText'
import { ButtonText } from '../texts/ButtonText'
import { DescriptionText } from '../texts/DescriptionText'
import { getStatusBucket, getVerificationZone } from '../utils/bugDisplay'
import { formatDate, formatDateTime, formatManday } from '../utils/formatters'
import { getTaskProgressStatus, getTaskStatusTagType, getTaskStatusText } from '../utils/taskStatus'
import { useAsyncAction } from '../composables/useAsyncAction'

const route = useRoute()
const router = useRouter()
const LT = LabelText.testDetail
const LTBug = LabelText.bugs
const BT = ButtonText.testDetail
const BTCommon = ButtonText.common
const DT = DescriptionText.testDetail
const DTBug = DescriptionText.bugs
const { runAsync } = useAsyncAction()
const loading = ref(false)
const testDetail = ref(null)
const DAYS_TO_WARNING = 3
const showBugDialog = ref(false)
const showEditDialog = ref(false)
const editingBug = ref(null)
const ownerOptions = ref([])
const editForm = ref({})
const verifyingMap = ref({})
const testOptions = ref([])
const workTaskOptions = ref([])
const bugBuildOptions = ref([])

// ── Bulk verify state ────────────────────────────────────────────────────────
const bulkVerifyMode = ref(false)
const bulkVerifying = ref(false)
const bugTableSelectionResetKey = ref(0)
const pendingBuildSelectedIds = ref([])
const pendingVerificationSelectedIds = ref([])
const verifiedSelectedIds = ref([])
const totalSelectedCount = computed(
  () => pendingBuildSelectedIds.value.length + pendingVerificationSelectedIds.value.length + verifiedSelectedIds.value.length
)

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

const linkedBugs = computed(() => testDetail.value?.bugs || [])
const allPendingBuildBugs = computed(() => linkedBugs.value.filter((row) => getVerificationZone(row, { includeDiscardedZone: false }) === 'waiting_build'))
const allPendingVerificationBugs = computed(() => linkedBugs.value.filter((row) => getVerificationZone(row, { includeDiscardedZone: false }) === 'pending_verification'))
const allVerifiedBugs = computed(() => linkedBugs.value.filter((row) => getVerificationZone(row, { includeDiscardedZone: false }) === 'verified'))

// ── Per-zone pagination ───────────────────────────────────────────────────────
const BUG_ZONE_PAGE_SIZE = 30
const pendingBuildPage = ref(1)
const pendingVerificationPage = ref(1)
const verifiedPage = ref(1)

const pendingBuildBugs = computed(() => {
  const start = (pendingBuildPage.value - 1) * BUG_ZONE_PAGE_SIZE
  return allPendingBuildBugs.value.slice(start, start + BUG_ZONE_PAGE_SIZE)
})
const pendingVerificationBugs = computed(() => {
  const start = (pendingVerificationPage.value - 1) * BUG_ZONE_PAGE_SIZE
  return allPendingVerificationBugs.value.slice(start, start + BUG_ZONE_PAGE_SIZE)
})
const verifiedBugs = computed(() => {
  const start = (verifiedPage.value - 1) * BUG_ZONE_PAGE_SIZE
  return allVerifiedBugs.value.slice(start, start + BUG_ZONE_PAGE_SIZE)
})

const resetZonePages = () => {
  pendingBuildPage.value = 1
  pendingVerificationPage.value = 1
  verifiedPage.value = 1
}

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

const loadDetail = async () => {
  const id = route.params.id
  if (!id) return
  await runAsync(async () => {
    testDetail.value = await getTestProgressDetail(id)
    resetZonePages()
  }, {
    loadingRef: loading,
    errorMessage: DT.toast.loadFailed
  })
}

const openEditDialog = () => {
  if (!testDetail.value) return
  const d = testDetail.value
  editForm.value = {
    fr_number: d.fr_number || '',
    test_name: d.test_name || '',
    model_name: d.model_name || '',
    description: d.description || '',
    config_method: d.config_method || '',
    test_owners_list: d.test_owners ? d.test_owners.split(',').map(s => s.trim()).filter(Boolean) : [],
    developers: d.developers || '',
    status: d.status || 'not_started',
    l0_passed_cases: d.l0_passed_cases ?? 0,
    l0_failed_cases: d.l0_failed_cases ?? 0,
    l0_total_cases: d.l0_total_cases ?? 0,
    l0_due_date: d.l0_due_date || null,
    l2_passed_cases: d.l2_passed_cases ?? 0,
    l2_failed_cases: d.l2_failed_cases ?? 0,
    l2_total_cases: d.l2_total_cases ?? 0,
    l2_due_date: d.l2_due_date || null,
    l4_passed_cases: d.l4_passed_cases ?? 0,
    l4_failed_cases: d.l4_failed_cases ?? 0,
    l4_total_cases: d.l4_total_cases ?? 0,
    l4_due_date: d.l4_due_date || null,
    start_date: d.start_date || null,
    completion_date: d.completion_date || null
  }
  ownerOptions.value = editForm.value.test_owners_list
  showEditDialog.value = true
}

const saveEdit = async () => {
  const id = route.params.id
  if (!id) return
  await runAsync(async () => {
    const payload = {
      ...editForm.value,
      test_owners: (editForm.value.test_owners_list || []).join(', ')
    }
    delete payload.test_owners_list
    await updateTestProgress(id, payload)
    ElMessage.success(DTBug.toast.updateSuccess)
    showEditDialog.value = false
    await loadDetail()
  }, { errorMessage: DTBug.toast.saveFailed })
}

const goToBugs = () => {
  const el = document.getElementById('linked-bugs-section')
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const getStatusType = (status) => getTaskStatusTagType(status)

const getStatusText = (status) => getTaskStatusText(status)

const getProgressStatus = (status) => getTaskProgressStatus(status)

const getStageFailed = (row, stage) => {
  const explicit = row?.[`${stage}_failed_cases`]
  if (explicit !== undefined && explicit !== null) {
    return Number(explicit)
  }
  const total = Number(row?.[`${stage}_total_cases`] ?? 0)
  const passed = Number(row?.[`${stage}_passed_cases`] ?? 0)
  return Math.max(0, total - passed)
}

const getTotalFailed = (row) => {
  if (row?.failed_cases !== undefined && row?.failed_cases !== null) {
    return Number(row.failed_cases)
  }
  const total = Number(row?.total_cases ?? 0)
  const passed = Number(row?.passed_cases ?? 0)
  return Math.max(0, total - passed)
}

const parseDateOnly = (value) => {
  if (!value) return null
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return null
  d.setHours(0, 0, 0, 0)
  return d
}

const getStageRemaining = (row, stage) => {
  const total = Number(row?.[`${stage}_total_cases`] ?? 0)
  const passed = Number(row?.[`${stage}_passed_cases`] ?? 0)
  const failed = Number(getStageFailed(row, stage))
  return Math.max(0, total - passed - failed)
}

const getStageDeadlineLevel = (row, stage) => {
  const dueDate = parseDateOnly(row?.[`${stage}_due_date`])
  if (!dueDate) return 'normal'
  if (getStageRemaining(row, stage) <= 0) return 'normal'

  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const daysDiff = Math.floor((dueDate.getTime() - today.getTime()) / 86400000)
  if (daysDiff < 0) return 'danger'
  if (daysDiff <= DAYS_TO_WARNING) return 'warning'
  return 'normal'
}

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))
const isVerifying = (row) => Boolean(verifyingMap.value?.[Number(row?.id)])

const getBugTableRowClassName = ({ row }) => {
  const created = row?.cr_created_on ? new Date(row.cr_created_on) : null
  if (!created || Number.isNaN(created.getTime())) return ''
  const now = new Date()
  const diffDays = Math.floor((now.getTime() - created.getTime()) / 86400000)
  if (diffDays > 14 && getStatusBucket(row.status) !== 'fixed') {
    return 'stale-cr-row'
  }
  return ''
}

const loadReferenceOptions = async () => {
  await runAsync(async () => {
    const [tests, tasks] = await Promise.all([
      getTestProgressList({ limit: 500 }),
      getWorkTasks()
    ])
    testOptions.value = tests || []
    workTaskOptions.value = tasks || []
  }, {
    onError: () => {
      testOptions.value = []
      workTaskOptions.value = []
    }
  })
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
  if (!bugId || isVerifying(row)) return

  verifyingMap.value[bugId] = true
  await runAsync(async () => {
    await delay(1000)
    await updateBug(bugId, toBugUpdatePayload(row, { status: 'verified' }))
    ElMessage.success(DTBug.toast.movedToVerified)
    await loadDetail()
  }, {
    errorMessage: DTBug.toast.saveFailed,
    onFinally: () => {
      verifyingMap.value[bugId] = false
    }
  })
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
    title: bug.title || '',
    severity: bug.severity || 'medium',
    status: bug.status || 'other'
  }
  showBugDialog.value = true
}

const saveBug = async () => {
  if (!editingBug.value?.id) return

  await runAsync(async () => {
    await updateBug(editingBug.value.id, bugForm.value)
    ElMessage.success(DTBug.toast.updateSuccess)
    showBugDialog.value = false
    editingBug.value = null
    bugBuildOptions.value = []
    await loadDetail()
  }, {
    errorMessage: DTBug.toast.saveFailed
  })
}

const deleteBug = async (id) => {
  try {
    await ElMessageBox.confirm(DTBug.toast.deleteConfirmContent, DTBug.toast.deleteConfirmTitle, {
      confirmButtonText: BTCommon.confirm,
      cancelButtonText: BTCommon.cancel,
      type: 'warning'
    })
    await deleteBugApi(id)
    ElMessage.success(DTBug.toast.deleteSuccess)
    await loadDetail()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error?.response?.data?.detail || DTBug.toast.deleteFailed)
    }
  }
}

const formatDueDate = (dateString) => {
  return formatDate(dateString, { emptyText: '-' })
}

const formatDateTimeText = (dateString) => formatDateTime(dateString)

const getStartDate = (row) => {
  return formatDueDate(row?.start_date)
}

const getCompletionDate = (row) => {
  return formatDueDate(row?.completion_date)
}

// ── Bulk verify logic ────────────────────────────────────────────────────────
const enterBulkVerifyMode = () => {
  bulkVerifyMode.value = true
  pendingBuildSelectedIds.value = []
  pendingVerificationSelectedIds.value = []
  verifiedSelectedIds.value = []
  bugTableSelectionResetKey.value += 1
}

const cancelBulkVerifyMode = () => {
  bulkVerifyMode.value = false
  pendingBuildSelectedIds.value = []
  pendingVerificationSelectedIds.value = []
  verifiedSelectedIds.value = []
  bugTableSelectionResetKey.value += 1
}

const handlePendingBuildSelectionChange = (rows) => {
  if (!bulkVerifyMode.value) return
  pendingBuildSelectedIds.value = (rows || []).map(r => Number(r.id)).filter(id => Number.isFinite(id))
}

const handlePendingVerificationSelectionChange = (rows) => {
  if (!bulkVerifyMode.value) return
  pendingVerificationSelectedIds.value = (rows || []).map(r => Number(r.id)).filter(id => Number.isFinite(id))
}

const handleVerifiedSelectionChange = (rows) => {
  if (!bulkVerifyMode.value) return
  verifiedSelectedIds.value = (rows || []).map(r => Number(r.id)).filter(id => Number.isFinite(id))
}

const confirmBulkVerify = async () => {
  const allIds = [
    ...pendingBuildSelectedIds.value,
    ...pendingVerificationSelectedIds.value,
    ...verifiedSelectedIds.value
  ]
  if (!allIds.length) { ElMessage.warning(DTBug.toast.selectBugsToVerify); return }

  const allBugs = linkedBugs.value
  const bugMap = new Map(allBugs.map(b => [Number(b.id), b]))

  try {
    await ElMessageBox.confirm(
      `${DTBug.toast.bulkVerifyConfirmPrefix} ${allIds.length} ${DTBug.toast.bulkVerifyConfirmSuffix}`,
      DTBug.toast.bulkVerifyConfirmTitle,
      { confirmButtonText: BTCommon.confirm, cancelButtonText: BTCommon.cancel, type: 'warning' }
    )
  } catch { return }

  bulkVerifying.value = true
  try {
    const results = await Promise.allSettled(allIds.map(id => {
      const bug = bugMap.get(Number(id))
      if (!bug) return Promise.reject(new Error(`Bug ${id} not found`))
      return updateBug(id, toBugUpdatePayload(bug, { status: 'verified' }))
    }))
    const successCount = results.filter(r => r.status === 'fulfilled').length
    const failedCount = results.length - successCount
    if (successCount > 0) ElMessage.success(`${DTBug.toast.bulkVerifySuccessPrefix} ${successCount} ${DTBug.toast.bulkVerifySuccessSuffix}`)
    if (failedCount > 0) ElMessage.error(`${DTBug.toast.bulkVerifyFailedPrefix} ${failedCount} ${DTBug.toast.bulkVerifyFailedSuffix}`)
    await loadDetail()
    cancelBulkVerifyMode()
  } finally {
    bulkVerifying.value = false
  }
}

onMounted(() => {
  loadReferenceOptions()
  loadDetail()
})
</script>
<style scoped src="../styles/detail-shared.css"></style>
<style scoped>
.bug-bulk-toolbar {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.bug-zone-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid rgba(148, 163, 184, 0.12);
}
</style>

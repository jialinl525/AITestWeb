<template>
  <div class="page-shell detail-container">
    <section class="page-hero detail-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">{{ LT.heroEyebrow }}</div>
        <h2 class="page-hero__title">{{ LT.heroTitle }}</h2>
        <p class="page-hero__desc">{{ DT.hero }}</p>
      </div>
      <div class="page-hero__actions">
        <el-button @click="goBack">{{ BT.backToList }}</el-button>
        <el-button v-if="canEditBug()" type="primary" @click="goToBugs">{{ BT.manageBugs }}</el-button>
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
          <article class="metric-card accent-blue">
            <div class="metric-card__label">{{ LT.metrics.currentProgress }}</div>
            <div class="metric-card__value">{{ testDetail.progress }}%</div>
            <div class="metric-card__meta">{{ DT.metricsMeta.currentProgress }}</div>
          </article>
          <article class="metric-card accent-green">
            <div class="metric-card__label">{{ LT.metrics.passedTotal }}</div>
            <div class="metric-card__value">{{ testDetail.passed_cases }}/{{ testDetail.total_cases }}</div>
            <div class="metric-card__meta">{{ DT.metricsMeta.passedTotal }}</div>
          </article>
          <article class="metric-card accent-red">
            <div class="metric-card__label">{{ LT.metrics.linkedBugs }}</div>
            <div class="metric-card__value">{{ testDetail.bugs?.length || 0 }}</div>
            <div class="metric-card__meta">{{ DT.metricsMeta.linkedBugs }}</div>
          </article>
          <article class="metric-card accent-purple">
            <div class="metric-card__label">{{ LT.metrics.estimatedManday }}</div>
            <div class="metric-card__value metric-card__value--small">{{ formatManday(testDetail.estimated_hours) }}</div>
            <div class="metric-card__meta">{{ DT.metricsMeta.estimatedManday }}</div>
          </article>
        </div>

        <div class="detail-people" v-if="testDetail.test_owners || testDetail.developers">
          <span class="people-item"><strong>{{ LT.people.frNumber }}: </strong>{{ testDetail.fr_number || '-' }}</span>
          <span class="people-item"><strong>{{ LT.people.testers }}: </strong>{{ testDetail.test_owners || '-' }}</span>
          <span class="people-item"><strong>{{ LT.people.developers }}: </strong>{{ testDetail.developers || '-' }}</span>
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

        <el-card class="section-card detail-inner-card">
          <template #header>
            <div class="section-title">
              <div class="section-title__main">
                <h3>{{ LT.section.linkedBugs }} ({{ testDetail.bugs?.length || 0 }})</h3>
                <span class="section-title__meta">{{ DT.sectionMeta.linkedBugs }}</span>
              </div>
            </div>
          </template>
          <div class="bug-zone-stack">
            <section class="bug-zone-item">
              <div class="bug-zone-item__title">{{ LT.bugZones.pendingBuild }} ({{ pendingBuildBugs.length }})</div>
              <BugTable
                :bugs="pendingBuildBugs"
                :empty-text="DT.tableEmptyBugs"
                :show-actions="canEditBug() || canDeleteBug()"
                :show-verify-action="canEditBug()"
                :editable="canEditBug()"
                :deletable="canDeleteBug()"
                :is-verifying="isVerifying"
                :row-class-name="getBugTableRowClassName"
                @verify="markBugVerified"
                @edit="editBug"
                @delete="deleteBug"
              />
            </section>

            <section class="bug-zone-item">
              <div class="bug-zone-item__title">{{ LT.bugZones.pendingVerification }} ({{ pendingVerificationBugs.length }})</div>
              <BugTable
                :bugs="pendingVerificationBugs"
                :empty-text="DT.tableEmptyBugs"
                :show-actions="canEditBug() || canDeleteBug()"
                :show-verify-action="canEditBug()"
                :editable="canEditBug()"
                :deletable="canDeleteBug()"
                :is-verifying="isVerifying"
                :row-class-name="getBugTableRowClassName"
                @verify="markBugVerified"
                @edit="editBug"
                @delete="deleteBug"
              />
            </section>

            <section class="bug-zone-item">
              <div class="bug-zone-item__title">{{ LT.bugZones.verified }} ({{ verifiedBugs.length }})</div>
              <BugTable
                :bugs="verifiedBugs"
                :empty-text="DT.tableEmptyBugs"
                :show-actions="canEditBug() || canDeleteBug()"
                :show-verify-action="canEditBug()"
                :editable="canEditBug()"
                :deletable="canDeleteBug()"
                :is-verifying="isVerifying"
                :row-class-name="getBugTableRowClassName"
                @verify="markBugVerified"
                @edit="editBug"
                @delete="deleteBug"
              />
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
            <el-button class="btn-style-2" type="primary" @click="saveBug">{{ BTCommon.save }}</el-button>
          </template>
        </el-dialog>
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import BugTable from '../components/bugs/BugTable.vue'
import { getTestProgressDetail, getTestProgressList } from '../api/testProgress'
import { updateBug, deleteBug as deleteBugApi } from '../api/bugs'
import { getWorkTasks } from '../api/workTasks'
import { canEditBug, canDeleteBug } from '../stores/auth'
import { LabelText } from '../texts/LabelText'
import { ButtonText } from '../texts/ButtonText'
import { DescriptionText } from '../texts/DescriptionText'
import { getStatusBucket, getVerificationZone } from '../utils/bugDisplay'
import { formatDate, formatDateTime, formatManday } from '../utils/formatters'
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
const editingBug = ref(null)
const verifyingMap = ref({})
const testOptions = ref([])
const workTaskOptions = ref([])
const bugBuildOptions = ref([])

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
const pendingBuildBugs = computed(() => linkedBugs.value.filter((row) => getVerificationZone(row, { includeDiscardedZone: false }) === 'waiting_build'))
const pendingVerificationBugs = computed(() => linkedBugs.value.filter((row) => getVerificationZone(row, { includeDiscardedZone: false }) === 'pending_verification'))
const verifiedBugs = computed(() => linkedBugs.value.filter((row) => getVerificationZone(row, { includeDiscardedZone: false }) === 'verified'))

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
  }, {
    loadingRef: loading,
    errorMessage: DT.toast.loadFailed
  })
}

const goBack = () => {
  router.push('/test-progress')
}

const goToBugs = () => {
  router.push({ path: '/bugs', query: { testId: route.params.id } })
}

const getStatusType = (status) => {
  const map = { pending: 'info', running: 'warning', completed: 'success', failed: 'danger' }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = LT.statusText
  return map[status] || status
}

const getProgressStatus = (status) => {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  return null
}

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

onMounted(() => {
  loadReferenceOptions()
  loadDetail()
})
</script>
<style scoped src="../styles/detail-shared.css"></style>

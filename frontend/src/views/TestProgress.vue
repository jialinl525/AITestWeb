<template>
  <div class="page-shell test-progress-container">
    <section class="page-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">{{ LT.heroEyebrow }}</div>
        <h2 class="page-hero__title">{{ LT.heroTitle }}</h2>
        <p class="page-hero__desc">{{ DT.hero }}</p>
      </div>
      <div class="page-hero__actions">
        <div class="glass-pill">{{ LT.pills.testTasks }} {{ overviewStats.total }}</div>
        <div class="glass-pill">{{ LT.pills.averageProgress }} {{ overviewStats.avgProgress }}%</div>
        <el-button v-if="canCreateOrEditTest()" type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          {{ BT.newTest }}
        </el-button>
      </div>
    </section>

    <el-card class="section-card progress-overview-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>{{ LT.overviewTitle }}</h3>
            <span class="section-title__meta">{{ DT.sectionMeta.overview }}</span>
          </div>
          <div class="inline-stats muted-text">{{ LT.inline.totalCases }} {{ overviewStats.totalCases }}</div>
        </div>
      </template>

      <div class="progress-overview-panels">
        <section class="overview-panel overview-panel--tasks">
          <div class="overview-panel__header">
            <div>
              <div class="overview-panel__eyebrow">Test Tasks</div>
              <h4 class="overview-panel__title">Execution status by task</h4>
            </div>
          </div>
          <div class="metrics-grid progress-overview-metrics progress-overview-metrics--tasks">
            <article class="metric-card accent-white">
              <div class="metric-card__label">Total Tasks</div>
              <div class="metric-card__value">{{ overviewStats.total }}</div>
              <div class="metric-card__meta">{{ DT.metricsMeta.total }}</div>
            </article>
            <article class="metric-card accent-yellow">
              <div class="metric-card__label">In Progress</div>
              <div class="metric-card__value">{{ overviewStats.inprogress }}</div>
              <div class="metric-card__meta">{{ DT.metricsMeta.running }}</div>
            </article>
            <article class="metric-card accent-green">
              <div class="metric-card__label">Completed</div>
              <div class="metric-card__value">{{ overviewStats.completed }}</div>
              <div class="metric-card__meta">{{ DT.metricsMeta.completed }}</div>
            </article>
          </div>
        </section>

        <section class="overview-panel overview-panel--cases">
          <div class="overview-panel__header">
            <div>
              <div class="overview-panel__eyebrow">Test Cases</div>
              <h4 class="overview-panel__title">Execution outcome by case</h4>
            </div>
          </div>
          <div class="metrics-grid progress-overview-metrics progress-overview-metrics--cases">
            <article class="metric-card accent-white">
              <div class="metric-card__label">Total Cases</div>
              <div class="metric-card__value">{{ overviewStats.totalCases }}</div>
              <div class="metric-card__meta">All tracked verification cases</div>
            </article>
            <article class="metric-card accent-green">
              <div class="metric-card__label">{{ LT.summary.passed }}</div>
              <div class="metric-card__value">{{ overviewStats.passedCases }}({{ overviewStats.passedRate }}%)</div>
              <div class="metric-card__meta">Validated successfully</div>
            </article>
            <article class="metric-card accent-red">
              <div class="metric-card__label">{{ LT.summary.failed }}</div>
              <div class="metric-card__value">{{ overviewStats.failedCases }}({{ overviewStats.failedRate }}%)</div>
              <div class="metric-card__meta">Need fix or retest</div>
            </article>
          </div>
        </section>
      </div>
    </el-card>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>{{ LT.listTitle }}</h3>
            <span class="section-title__meta">{{ DT.sectionMeta.list }}</span>
          </div>
          <div class="inline-stats muted-text">{{ filteredTestProgressList.length }} {{ LT.inline.records }}</div>
        </div>
      </template>

      <el-table
        :data="paginatedTestProgressList"
        v-loading="loading"
        stripe
        class="test-progress-table"
        style="width: 100%"
        :fit="true"
        table-layout="auto"
        :row-class-name="getTableRowClassName"
      >
        <el-table-column :label="LT.table.taskInfo" min-width="220">
          <template #default="{ row }">
            <div class="task-info-cell">
              <div class="task-info-cell__fr">{{ row.fr_number || '-' }}</div>
              <button
                v-if="row.id"
                type="button"
                class="task-info-cell__name task-info-cell__name--link"
                @click="viewDetail(row.id)"
              >
                {{ row.test_name || '-' }}
              </button>
              <div v-else class="task-info-cell__name">{{ row.test_name || '-' }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="LT.table.risk" width="96">
          <template #default="{ row }">
            <el-tag :type="getRiskTagType(row)" size="small">
              {{ getRiskText(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="LT.table.status" width="104">
          <template #default="{ row }">
            <el-tag :type="getTaskStatusTagType(row.status)" size="small">
              {{ getTaskStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="LT.table.currentStage" min-width="204">
          <template #default="{ row }">
            <div class="case-stats-wrap">
              <div class="case-stats" :title="`Stage ${getCurrentStageKey(row).toUpperCase()} | Pass ${getCurrentStagePassed(row)} / Fail ${getCurrentStageFailed(row)} / Total ${getCurrentStageTotal(row)}`">
                <span class="total-count">{{ getCurrentStageKey(row).toUpperCase() }}</span>
                <span class="sep">:</span>
                <span class="pass-count">{{ getCurrentStagePassed(row) }}</span>
                <span class="sep">/</span>
                <span class="fail-count">{{ getCurrentStageFailed(row) }}</span>
                <span class="sep">/</span>
                <span class="total-count">{{ getCurrentStageTotal(row) }}</span>
              </div>
              <div class="due-date-text" :class="`due-date-text--${getCurrentStageDeadlineLevel(row)}`">
                {{ DT.helper.dueDatePrefix }} {{ formatDueDate(getCurrentStageDueDate(row)) }}
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="LT.table.total" min-width="140">
          <template #default="{ row }">
            <div class="case-stats" :title="`Pass ${row.passed_cases} / Fail ${getTotalFailed(row)} / Total ${row.total_cases}`">
              <span class="pass-count">{{ row.passed_cases }}</span>
              <span class="sep">/</span>
              <span class="fail-count">{{ getTotalFailed(row) }}</span>
              <span class="sep">/</span>
              <span class="total-count">{{ row.total_cases }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="LT.table.progress" min-width="132">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :status="getTaskProgressStatus(row.status)" :stroke-width="10" />
          </template>
        </el-table-column>
        <el-table-column :label="LT.table.testers" min-width="128">
          <template #default="{ row }">
            <span class="people-cell" :title="row.test_owners">{{ row.test_owners || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="LT.table.actions" min-width="166">
          <template #default="{ row }">
            <div class="table-action-group">
              <el-button size="small" @click="viewDetail(row.id)">{{ BT.details }}</el-button>
              <el-button size="small" @click="viewBugs(row.id)">{{ BT.bugs }}</el-button>
              <el-button v-if="canCreateOrEditTest()" size="small" type="primary" @click="editTest(row)">{{ BTCommon.edit }}</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <div class="list-pagination">
        <el-pagination
          v-if="filteredTestProgressList.length > pageSize"
          background
          layout="prev, pager, next"
          :page-size="pageSize"
          :total="filteredTestProgressList.length"
          :current-page="currentPage"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="showCreateDialog"
      :title="editingTest ? LT.dialog.editTitle : LT.dialog.newTitle"
      width="560px"
    >
      <el-form :model="testForm" label-width="120px">
        <el-form-item :label="LT.form.frNumber">
          <el-input v-model="testForm.fr_number" :placeholder="DT.placeholders.frExample" />
        </el-form-item>
        <el-form-item :label="LT.form.testName">
          <el-input v-model="testForm.test_name" :placeholder="DT.placeholders.testName" />
        </el-form-item>
        <el-form-item :label="LT.form.featureSummary">
          <el-input v-model="testForm.model_name" :placeholder="DT.placeholders.featureSummary" />
        </el-form-item>
        <el-form-item :label="LT.form.detailedDescription">
          <el-input v-model="testForm.description" type="textarea" :rows="4" :placeholder="DT.placeholders.detailDescription" />
        </el-form-item>
        <el-form-item :label="LT.form.configMethod">
          <el-input v-model="testForm.config_method" type="textarea" :rows="3" :placeholder="DT.placeholders.configMethod" />
        </el-form-item>
        <el-form-item :label="LT.form.testers">
          <el-select
            v-model="testForm.test_owners_list"
            multiple
            filterable
            allow-create
            default-first-option
            style="width: 100%"
            :placeholder="DT.placeholders.testers"
          >
            <el-option
              v-for="owner in ownerOptions"
              :key="owner"
              :label="owner"
              :value="owner"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="LT.form.developers">
          <el-input v-model="testForm.developers" :placeholder="DT.placeholders.developers" />
        </el-form-item>
        <el-form-item :label="LT.form.status">
          <el-select v-model="testForm.status" style="width: 100%">
            <el-option
              v-for="status in TASK_STATUS_OPTIONS"
              :key="status"
              :label="status"
              :value="status"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="LT.form.l0Cases">
          <el-input-number v-model="testForm.l0_passed_cases" :min="0" size="small" style="width: 88px" />
          <span class="form-divider">/</span>
          <el-input-number v-model="testForm.l0_failed_cases" :min="0" size="small" style="width: 88px" />
          <span class="form-divider">/</span>
          <el-input-number v-model="testForm.l0_total_cases" :min="0" size="small" style="width: 88px" />
        </el-form-item>
        <el-form-item :label="LT.form.l0DueDate">
          <el-date-picker
            v-model="testForm.l0_due_date"
            type="date"
            value-format="YYYY-MM-DD"
            :placeholder="DT.placeholders.l0DueDate"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="LT.form.l2Cases">
          <el-input-number v-model="testForm.l2_passed_cases" :min="0" size="small" style="width: 88px" />
          <span class="form-divider">/</span>
          <el-input-number v-model="testForm.l2_failed_cases" :min="0" size="small" style="width: 88px" />
          <span class="form-divider">/</span>
          <el-input-number v-model="testForm.l2_total_cases" :min="0" size="small" style="width: 88px" />
        </el-form-item>
        <el-form-item :label="LT.form.l2DueDate">
          <el-date-picker
            v-model="testForm.l2_due_date"
            type="date"
            value-format="YYYY-MM-DD"
            :placeholder="DT.placeholders.l2DueDate"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="LT.form.l4Cases">
          <el-input-number v-model="testForm.l4_passed_cases" :min="0" size="small" style="width: 88px" />
          <span class="form-divider">/</span>
          <el-input-number v-model="testForm.l4_failed_cases" :min="0" size="small" style="width: 88px" />
          <span class="form-divider">/</span>
          <el-input-number v-model="testForm.l4_total_cases" :min="0" size="small" style="width: 88px" />
        </el-form-item>
        <el-form-item :label="LT.form.l4DueDate">
          <el-date-picker
            v-model="testForm.l4_due_date"
            type="date"
            value-format="YYYY-MM-DD"
            :placeholder="DT.placeholders.l4DueDate"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item>
          <span class="form-helper">{{ DT.helper.inputFormat }}</span>
        </el-form-item>
        <el-form-item :label="LT.form.progress" v-if="calcProgress !== null">
          <span class="progress-hint">{{ DT.helper.autoProgressPrefix }}: {{ calcProgress }}%</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">{{ BTCommon.cancel }}</el-button>
        <el-button type="primary" @click="saveTest">{{ BTCommon.save }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { LabelText } from '../texts/LabelText'
import { ButtonText } from '../texts/ButtonText'
import { DescriptionText } from '../texts/DescriptionText'
import { useAsyncAction } from '../composables/useAsyncAction'
import { formatDate } from '../utils/formatters'
import { getTaskProgressStatus, getTaskStatusTagType, getTaskStatusText, normalizeTaskStatus, TASK_STATUS_OPTIONS } from '../utils/taskStatus'
import { getTestProgressList, createTestProgress, updateTestProgress } from '../api/testProgress'
import { getMembers } from '../api/personnel'
import { canCreateOrEditTest } from '../stores/auth'

const router = useRouter()
const LT = LabelText.testProgress
const BT = ButtonText.testProgress
const BTCommon = ButtonText.common
const DT = DescriptionText.testProgress
const loading = ref(false)
const testProgressList = ref([])
const members = ref([])
const currentPage = ref(1)
const pageSize = 10
const showCreateDialog = ref(false)
const editingTest = ref(null)
const DAYS_TO_WARNING = 3
const { runAsync } = useAsyncAction()

const createDefaultTestForm = () => ({
  test_name: '',
  model_name: '',
  fr_number: '',
  description: '',
  config_method: '',
  status: 'Planning',
  l0_total_cases: 0,
  l0_passed_cases: 0,
  l0_failed_cases: 0,
  l0_due_date: null,
  l2_total_cases: 0,
  l2_passed_cases: 0,
  l2_failed_cases: 0,
  l2_due_date: null,
  l4_total_cases: 0,
  l4_passed_cases: 0,
  l4_failed_cases: 0,
  l4_due_date: null,
  estimated_hours: 0,
  test_owners_list: [],
  developers: ''
})

const testForm = ref(createDefaultTestForm())

const ownerOptions = computed(() => members.value.map(item => item.display_name || item.username))

const parsePeople = (value) => {
  if (!value) return []
  return value
    .replaceAll('，', ',')
    .split(',')
    .map(item => item.trim())
    .filter(Boolean)
}

const calcProgress = computed(() => {
  const l0t = testForm.value.l0_total_cases || 0
  const l0p = testForm.value.l0_passed_cases || 0
  const l2t = testForm.value.l2_total_cases || 0
  const l2p = testForm.value.l2_passed_cases || 0
  const l4t = testForm.value.l4_total_cases || 0
  const l4p = testForm.value.l4_passed_cases || 0
  const total = l0t + l2t + l4t
  if (total <= 0) return null
  const passed = l0p + l2p + l4p
  return Math.round(Math.min(100, (passed / total) * 100))
})

const parseRecentDate = (value) => {
  if (!value) return null
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return null
  date.setHours(0, 0, 0, 0)
  return date
}

const filteredTestProgressList = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const startDate = new Date(today)
  startDate.setDate(startDate.getDate() - 365)

  return testProgressList.value.filter(item => {
    const candidateDates = [
      parseRecentDate(item?.l4_due_date),
      parseRecentDate(item?.l2_due_date),
      parseRecentDate(item?.l0_due_date)
    ].filter(Boolean)

    return candidateDates.some(date => date >= startDate)
  })
})

const paginatedTestProgressList = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize
  return filteredTestProgressList.value.slice(startIndex, startIndex + pageSize)
})

const overviewStats = computed(() => {
  const total = filteredTestProgressList.value.length
  const inprogress = filteredTestProgressList.value.filter(item => normalizeTaskStatus(item.status) === 'Inprogress').length
  const completed = filteredTestProgressList.value.filter(item => normalizeTaskStatus(item.status) === 'Completed').length
  const totalCases = filteredTestProgressList.value.reduce((sum, item) => sum + (item.total_cases || 0), 0)
  const passedCases = filteredTestProgressList.value.reduce((sum, item) => sum + (item.passed_cases || 0), 0)
  const failedCases = filteredTestProgressList.value.reduce((sum, item) => sum + getTotalFailed(item), 0)
  const untestedCases = Math.max(0, totalCases - passedCases - failedCases)
  const avgProgress = total
    ? Math.round(filteredTestProgressList.value.reduce((sum, item) => sum + (item.progress || 0), 0) / total)
    : 0

  return {
    total,
    inprogress,
    completed,
    totalCases,
    passedCases,
    failedCases,
    untestedCases,
    avgProgress,
    passedRate: totalCases ? Math.round((passedCases / totalCases) * 100) : 0,
    passRate: totalCases ? Math.round((passedCases / totalCases) * 100) : 0,
    failedRate: totalCases ? Math.round((failedCases / totalCases) * 100) : 0
  }
})


const loadData = async () => {
  await runAsync(
    async () => {
      const data = await getTestProgressList()
      testProgressList.value = data
      currentPage.value = 1
    },
    {
      loadingRef: loading,
      errorMessage: DT.toast.loadFailed,
    }
  )
}

const loadMembers = async () => {
  try {
    members.value = await getMembers()
  } catch {
    members.value = []
  }
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

const isStageCompleted = (row, stage) => {
  const total = Number(row?.[`${stage}_total_cases`] ?? 0)
  const passed = Number(row?.[`${stage}_passed_cases`] ?? 0)
  if (total <= 0) return false
  return passed >= total
}

const getCurrentStageKey = (row) => {
  if (isStageCompleted(row, 'l2')) return 'l4'
  if (isStageCompleted(row, 'l0')) return 'l2'
  return 'l0'
}

const getCurrentStagePassed = (row) => {
  const stage = getCurrentStageKey(row)
  return Number(row?.[`${stage}_passed_cases`] ?? 0)
}

const getCurrentStageTotal = (row) => {
  const stage = getCurrentStageKey(row)
  return Number(row?.[`${stage}_total_cases`] ?? 0)
}

const getCurrentStageFailed = (row) => {
  const stage = getCurrentStageKey(row)
  return getStageFailed(row, stage)
}

const getCurrentStageDueDate = (row) => {
  const stage = getCurrentStageKey(row)
  return row?.[`${stage}_due_date`] ?? null
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

const getCurrentStageDeadlineLevel = (row) => {
  const stage = getCurrentStageKey(row)
  return getStageDeadlineLevel(row, stage)
}

const getTaskRiskLevel = (row) => {
  const levels = ['l0', 'l2', 'l4'].map(stage => getStageDeadlineLevel(row, stage))
  if (levels.includes('danger')) return 'danger'
  if (levels.includes('warning')) return 'warning'
  return 'normal'
}

const getRiskText = (row) => {
  const level = getTaskRiskLevel(row)
  if (level === 'danger') return LT.riskText.overdue
  if (level === 'warning') return LT.riskText.atRisk
  return LT.riskText.normal
}

const getRiskTagType = (row) => {
  const level = getTaskRiskLevel(row)
  if (level === 'danger') return 'danger'
  if (level === 'warning') return 'warning'
  return 'success'
}

const getTableRowClassName = ({ row }) => {
  const level = getTaskRiskLevel(row)
  if (level === 'danger') return 'risk-row-danger'
  if (level === 'warning') return 'risk-row-warning'
  return ''
}

const formatDueDate = (dateString) => {
  return formatDate(dateString)
}

const handlePageChange = (page) => {
  currentPage.value = page
}

const viewDetail = (testId) => {
  router.push({ path: `/test-progress/${testId}` })
}

const viewBugs = (testId) => {
  router.push({ path: '/bugs', query: { testId } })
}

const editTest = (test) => {
  editingTest.value = test
  testForm.value = {
    test_name: test.test_name,
    model_name: test.model_name,
    fr_number: test.fr_number || '',
    description: test.description || '',
    config_method: test.config_method || '',
    status: normalizeTaskStatus(test.status),
    l0_total_cases: test.l0_total_cases ?? 0,
    l0_passed_cases: test.l0_passed_cases ?? 0,
    l0_failed_cases: test.l0_failed_cases ?? 0,
    l0_due_date: test.l0_due_date || null,
    l2_total_cases: test.l2_total_cases ?? 0,
    l2_passed_cases: test.l2_passed_cases ?? 0,
    l2_failed_cases: test.l2_failed_cases ?? 0,
    l2_due_date: test.l2_due_date || null,
    l4_total_cases: test.l4_total_cases ?? 0,
    l4_passed_cases: test.l4_passed_cases ?? 0,
    l4_failed_cases: test.l4_failed_cases ?? 0,
    l4_due_date: test.l4_due_date || null,
    estimated_hours: Number(test.estimated_hours || 0),
    test_owners_list: parsePeople(test.test_owners || ''),
    developers: test.developers || ''
  }
  showCreateDialog.value = true
}

const saveTest = async () => {
  try {
    const { test_owners_list, ...restForm } = testForm.value
    const payload = {
      ...restForm,
      test_owners: (test_owners_list || []).join(',')
    }

    if (editingTest.value) {
      await updateTestProgress(editingTest.value.id, payload)
      ElMessage.success(DT.toast.updateSuccess)
    } else {
      await createTestProgress(payload)
      ElMessage.success(DT.toast.createSuccess)
    }
    showCreateDialog.value = false
    editingTest.value = null
    testForm.value = createDefaultTestForm()
    loadData()
  } catch (error) {
    ElMessage.error(DT.toast.saveFailed)
  }
}

onMounted(() => {
  loadData()
  loadMembers()
})
</script>

<style scoped>
.test-progress-container {
  width: 100%;
}

.progress-hint {
  color: rgba(148, 163, 184, 0.9);
  font-size: 14px;
}

.form-divider {
  margin: 0 8px;
  color: rgba(148, 163, 184, 0.8);
}

.form-helper {
  color: rgba(148, 163, 184, 0.86);
  font-size: 12px;
}

.task-info-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
  line-height: 1.35;
}

.task-info-cell__fr {
  display: inline-flex;
  align-items: center;
  align-self: flex-start;
  padding: 2px 8px;
  border-radius: 999px;
  color: #67e8f9;
  background: rgba(34, 211, 238, 0.16);
  border: 1px solid rgba(34, 211, 238, 0.38);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.02em;
  word-break: break-word;
}

.task-info-cell__name {
  color: #f8fafc;
  font-weight: 600;
  word-break: break-word;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.task-info-cell__name--link {
  appearance: none;
  border: none;
  background: transparent;
  padding: 0;
  text-align: left;
  cursor: pointer;
  text-decoration: underline;
  text-decoration-color: rgba(125, 211, 252, 0.5);
  text-underline-offset: 2px;
}

.task-info-cell__name--link:hover {
  color: #7dd3fc;
  text-decoration-color: rgba(125, 211, 252, 0.9);
}

.task-info-cell__name--link:focus-visible {
  outline: 2px solid rgba(125, 211, 252, 0.7);
  outline-offset: 2px;
  border-radius: 4px;
}

.people-cell {
  display: inline-block;
  white-space: normal;
  word-break: break-word;
  line-height: 1.35;
}

.table-action-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.case-stats {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: 600;
}

.case-stats-wrap {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.due-date-text {
  font-size: 12px;
  color: rgba(148, 163, 184, 0.9);
}

.due-date-text--warning {
  color: #f59e0b;
}

.due-date-text--danger {
  color: #ef4444;
}

.pass-count {
  color: #34d399;
}

.fail-count {
  color: #fb7185;
}

.total-count {
  color: #e2e8f0;
}

.sep {
  color: rgba(148, 163, 184, 0.78);
}

.progress-overview-card {
  margin-bottom: 24px;
}

.progress-overview-panels {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 20px;
}

.overview-panel {
  padding: 12px;
  border-radius: 16px;
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.88), rgba(15, 23, 42, 0.74));
  border: 1px solid rgba(148, 163, 184, 0.16);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.overview-panel--tasks {
  border-color: rgba(96, 165, 250, 0.24);
}

.overview-panel--cases {
  border-color: rgba(45, 212, 191, 0.24);
}

.overview-panel__header {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
  text-align: center;
}

.overview-panel__eyebrow {
  color: rgba(148, 163, 184, 0.92);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 4px;
  text-align: center;
}

.overview-panel__title {
  margin: 0;
  color: #f8fafc;
  font-size: 15px;
  font-weight: 700;
  text-align: center;
}

.progress-overview-metrics {
  margin-bottom: 0;
}

.progress-overview-metrics--tasks {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.progress-overview-metrics--cases {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.accent-cyan {
  --metric-accent: #22d3ee;
}

.accent-rose {
  --metric-accent: #fb7185;
}

.accent-sky {
  --metric-accent: #60a5fa;
}

.test-progress-container :deep(.metric-card) {
  padding: 12px 10px;
  min-height: 112px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
}

.test-progress-container :deep(.metric-card__label) {
  text-align: center;
  font-size: 13px;
  font-weight: 700;
  color: rgba(226, 232, 240, 0.95);
  margin-bottom: 10px;
}

.test-progress-container :deep(.metric-card__value) {
  text-align: center;
  font-size: 20px;
  font-weight: 700;
  line-height: 1.2;
}


.test-progress-container :deep(.metric-card__meta) {
  text-align: center;
  font-size: 12px;
  margin-top: 10px;
}

.test-progress-container :deep(.test-progress-table .cell) {
  white-space: normal;
}

.test-progress-container :deep(.risk-row-warning > td.el-table__cell) {
  background: rgba(245, 158, 11, 0.12) !important;
}

.test-progress-container :deep(.risk-row-danger > td.el-table__cell) {
  background: rgba(239, 68, 68, 0.12) !important;
}

.list-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

@media (max-width: 960px) {
  .progress-overview-panels {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 960px) {
  .progress-overview-metrics--tasks,
  .progress-overview-metrics--cases {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .overview-panel {
    padding: 10px;
  }
}
</style>

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

      <div class="metrics-grid progress-overview-metrics">
        <article class="metric-card accent-blue">
          <div class="metric-card__label">{{ LT.metrics.total }}</div>
          <div class="metric-card__value">{{ overviewStats.total }}</div>
          <div class="metric-card__meta">{{ DT.metricsMeta.total }}</div>
        </article>
        <article class="metric-card accent-orange">
          <div class="metric-card__label">{{ LT.metrics.running }}</div>
          <div class="metric-card__value">{{ overviewStats.running }}</div>
          <div class="metric-card__meta">{{ DT.metricsMeta.running }}</div>
        </article>
        <article class="metric-card accent-green">
          <div class="metric-card__label">{{ LT.metrics.completed }}</div>
          <div class="metric-card__value">{{ overviewStats.completed }}</div>
          <div class="metric-card__meta">{{ DT.metricsMeta.completed }}</div>
        </article>
        <article class="metric-card accent-purple">
          <div class="metric-card__label">{{ LT.metrics.passRate }}</div>
          <div class="metric-card__value">{{ overviewStats.passRate }}%</div>
          <div class="metric-card__meta">{{ DT.metricsMeta.passRate }}</div>
        </article>
      </div>

      <div class="progress-overview-grid">
        <v-chart class="progress-pie-chart" :option="progressPieOption" autoresize />
        <div class="progress-overview-summary">
          <div class="progress-summary-item progress-summary-item--passed">
            <span class="progress-summary-item__dot"></span>
            <div>
              <div class="progress-summary-item__label">{{ LT.summary.passed }}</div>
              <div class="progress-summary-item__value">{{ overviewStats.passedCases }}</div>
            </div>
          </div>
          <div class="progress-summary-item progress-summary-item--failed">
            <span class="progress-summary-item__dot"></span>
            <div>
              <div class="progress-summary-item__label">{{ LT.summary.failed }}</div>
              <div class="progress-summary-item__value">{{ overviewStats.failedCases }}</div>
            </div>
          </div>
          <div class="progress-summary-item progress-summary-item--untested">
            <span class="progress-summary-item__dot"></span>
            <div>
              <div class="progress-summary-item__label">{{ LT.summary.untested }}</div>
              <div class="progress-summary-item__value">{{ overviewStats.untestedCases }}</div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>{{ LT.listTitle }}</h3>
            <span class="section-title__meta">{{ DT.sectionMeta.list }}</span>
          </div>
          <div class="inline-stats muted-text">{{ testProgressList.length }} {{ LT.inline.records }}</div>
        </div>
      </template>

      <el-table
        :data="testProgressList"
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
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
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
            <el-progress :percentage="row.progress" :status="getProgressStatus(row.status)" :stroke-width="10" />
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
    </el-card>

    <!-- Create/Edit Dialog -->
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
            <el-option :label="LT.statusText.pending" value="pending" />
            <el-option :label="LT.statusText.running" value="running" />
            <el-option :label="LT.statusText.completed" value="completed" />
            <el-option :label="LT.statusText.failed" value="failed" />
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
  status: 'pending',
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

const overviewStats = computed(() => {
  const total = testProgressList.value.length
  const running = testProgressList.value.filter(item => item.status === 'running').length
  const completed = testProgressList.value.filter(item => item.status === 'completed').length
  const totalCases = testProgressList.value.reduce((sum, item) => sum + (item.total_cases || 0), 0)
  const passedCases = testProgressList.value.reduce((sum, item) => sum + (item.passed_cases || 0), 0)
  const failedCases = testProgressList.value.reduce((sum, item) => sum + getTotalFailed(item), 0)
  const untestedCases = Math.max(0, totalCases - passedCases - failedCases)
  const avgProgress = total
    ? Math.round(testProgressList.value.reduce((sum, item) => sum + (item.progress || 0), 0) / total)
    : 0

  return {
    total,
    running,
    completed,
    totalCases,
    passedCases,
    failedCases,
    untestedCases,
    avgProgress,
    passRate: totalCases ? Math.round((passedCases / totalCases) * 100) : 0
  }
})

const progressPieOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} ({d}%)'
  },
  legend: {
    bottom: 0,
    left: 'center',
    icon: 'circle',
    textStyle: {
      color: 'rgba(226, 232, 240, 0.9)'
    }
  },
  series: [
    {
      type: 'pie',
      radius: ['52%', '74%'],
      center: ['50%', '44%'],
      avoidLabelOverlap: true,
      label: {
        show: true,
        color: '#f8fafc',
        formatter: '{b}\n{d}%'
      },
      labelLine: {
        lineStyle: {
          color: 'rgba(148, 163, 184, 0.7)'
        }
      },
      itemStyle: {
        borderColor: 'rgba(8, 15, 33, 0.92)',
        borderWidth: 4
      },
      data: [
        {
          value: overviewStats.value.passedCases,
          name: LT.summary.passed,
          itemStyle: { color: '#34d399' }
        },
        {
          value: overviewStats.value.failedCases,
          name: LT.summary.failed,
          itemStyle: { color: '#fb7185' }
        },
        {
          value: overviewStats.value.untestedCases,
          name: LT.summary.untested,
          itemStyle: { color: '#60a5fa' }
        }
      ]
    }
  ]
}))

const loadData = async () => {
  await runAsync(
    async () => {
      const data = await getTestProgressList()
      testProgressList.value = data
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

const getStatusType = (status) => {
  const map = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger'
  }
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
    status: test.status,
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

.progress-overview-metrics {
  margin-bottom: 18px;
}

.progress-overview-grid {
  display: grid;
  grid-template-columns: minmax(280px, 1.1fr) minmax(220px, 0.9fr);
  gap: 24px;
  align-items: center;
}

.progress-pie-chart {
  height: 320px;
  width: 100%;
}

.progress-overview-summary {
  display: grid;
  gap: 14px;
}

.progress-summary-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.72);
  border: 1px solid rgba(148, 163, 184, 0.16);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.progress-summary-item__dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  flex-shrink: 0;
}

.progress-summary-item--passed .progress-summary-item__dot {
  background: #34d399;
  box-shadow: 0 0 16px rgba(52, 211, 153, 0.5);
}

.progress-summary-item--failed .progress-summary-item__dot {
  background: #fb7185;
  box-shadow: 0 0 16px rgba(251, 113, 133, 0.45);
}

.progress-summary-item--untested .progress-summary-item__dot {
  background: #60a5fa;
  box-shadow: 0 0 16px rgba(96, 165, 250, 0.45);
}

.progress-summary-item__label {
  color: rgba(148, 163, 184, 0.86);
  font-size: 13px;
  margin-bottom: 4px;
}

.progress-summary-item__value {
  color: #f8fafc;
  font-size: 24px;
  font-weight: 700;
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

@media (max-width: 960px) {
  .progress-overview-grid {
    grid-template-columns: 1fr;
  }

  .progress-pie-chart {
    height: 280px;
  }
}
</style>

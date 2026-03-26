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
      <TestOverviewPanel :stats="overviewStats" />
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

      <TestProgressTable
        :tasks="paginatedTestProgressList"
        :loading="loading"
        :can-edit="canCreateOrEditTest()"
        :total="filteredTestProgressList.length"
        :page-size="pageSize"
        :current-page="currentPage"
        @view="viewDetail"
        @view-bugs="viewBugs"
        @edit="editTest"
        @page-change="handlePageChange"
      />
    </el-card>

    <TestCreateDialog
      v-model="showCreateDialog"
      :form="testForm"
      :is-editing="Boolean(editingTest)"
      :owner-options="ownerOptions"
      @save="saveTest"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import TestOverviewPanel from '../components/testProgress/TestOverviewPanel.vue'
import TestProgressTable from '../components/testProgress/TestProgressTable.vue'
import TestCreateDialog from '../components/testProgress/TestCreateDialog.vue'
import { LabelText } from '../texts/LabelText'
import { ButtonText } from '../texts/ButtonText'
import { DescriptionText } from '../texts/DescriptionText'
import { useAsyncAction } from '../composables/useAsyncAction'
import { normalizeTaskStatus } from '../utils/taskStatus'
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
  return value.replaceAll('，', ',').split(',').map(item => item.trim()).filter(Boolean)
}

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

const getTotalFailed = (item) => {
  if (item?.failed_cases !== undefined && item?.failed_cases !== null) return Number(item.failed_cases)
  const total = Number(item?.total_cases ?? 0)
  const passed = Number(item?.passed_cases ?? 0)
  return Math.max(0, total - passed)
}

const overviewStats = computed(() => {
  const total = filteredTestProgressList.value.length
  const inprogress = filteredTestProgressList.value.filter(item => normalizeTaskStatus(item.status) === 'Inprogress').length
  const completed = filteredTestProgressList.value.filter(item => normalizeTaskStatus(item.status) === 'Completed').length
  const totalCases = filteredTestProgressList.value.reduce((sum, item) => sum + (item.total_cases || 0), 0)
  const passedCases = filteredTestProgressList.value.reduce((sum, item) => sum + (item.passed_cases || 0), 0)
  const failedCases = filteredTestProgressList.value.reduce((sum, item) => sum + getTotalFailed(item), 0)
  const avgProgress = total
    ? Math.round(filteredTestProgressList.value.reduce((sum, item) => sum + (item.progress || 0), 0) / total)
    : 0
  return {
    total, inprogress, completed, totalCases, passedCases, failedCases, avgProgress,
    passedRate: totalCases ? Math.round((passedCases / totalCases) * 100) : 0,
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
    { loadingRef: loading, errorMessage: DT.toast.loadFailed }
  )
}

const loadMembers = async () => {
  try { members.value = await getMembers() } catch { members.value = [] }
}

const handlePageChange = (page) => { currentPage.value = page }

const viewDetail = (testId) => router.push({ path: `/test-progress/${testId}` })
const viewBugs = (testId) => router.push({ path: '/bugs', query: { testId } })

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
    const payload = { ...restForm, test_owners: (test_owners_list || []).join(',') }
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
  } catch {
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

.progress-overview-card {
  margin-bottom: 24px;
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
</style>

<template>
  <div class="page-shell test-progress-container">
    <section class="page-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">Test Operations</div>
        <h2 class="page-hero__title">测试进度总览</h2>
        <p class="page-hero__desc">聚合查看各测试任务状态、用例通过情况与人员协作信息，让整体推进节奏和风险暴露更加清晰。</p>
      </div>
      <div class="page-hero__actions">
        <div class="glass-pill">测试任务 {{ overviewStats.total }}</div>
        <div class="glass-pill">平均进度 {{ overviewStats.avgProgress }}%</div>
        <el-button v-if="canCreateOrEditTest()" type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建测试
        </el-button>
      </div>
    </section>

    <el-card class="section-card progress-overview-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>总体测试进度分布</h3>
            <span class="section-title__meta">从所有任务中汇总通过、失败与未测用例，快速识别当前推进健康度</span>
          </div>
          <div class="inline-stats muted-text">总用例 {{ overviewStats.totalCases }}</div>
        </div>
      </template>

      <div class="metrics-grid progress-overview-metrics">
        <article class="metric-card accent-blue">
          <div class="metric-card__label">总测试数</div>
          <div class="metric-card__value">{{ overviewStats.total }}</div>
          <div class="metric-card__meta">当前视图已纳入全部测试任务</div>
        </article>
        <article class="metric-card accent-orange">
          <div class="metric-card__label">运行中</div>
          <div class="metric-card__value">{{ overviewStats.running }}</div>
          <div class="metric-card__meta">正在执行中的测试任务</div>
        </article>
        <article class="metric-card accent-green">
          <div class="metric-card__label">已完成</div>
          <div class="metric-card__value">{{ overviewStats.completed }}</div>
          <div class="metric-card__meta">已交付完成的测试项</div>
        </article>
        <article class="metric-card accent-purple">
          <div class="metric-card__label">用例通过率</div>
          <div class="metric-card__value">{{ overviewStats.passRate }}%</div>
          <div class="metric-card__meta">基于当前列表的总体通过情况</div>
        </article>
      </div>

      <div class="progress-overview-grid">
        <v-chart class="progress-pie-chart" :option="progressPieOption" autoresize />
        <div class="progress-overview-summary">
          <div class="progress-summary-item progress-summary-item--passed">
            <span class="progress-summary-item__dot"></span>
            <div>
              <div class="progress-summary-item__label">已通过</div>
              <div class="progress-summary-item__value">{{ overviewStats.passedCases }}</div>
            </div>
          </div>
          <div class="progress-summary-item progress-summary-item--failed">
            <span class="progress-summary-item__dot"></span>
            <div>
              <div class="progress-summary-item__label">已失败</div>
              <div class="progress-summary-item__value">{{ overviewStats.failedCases }}</div>
            </div>
          </div>
          <div class="progress-summary-item progress-summary-item--untested">
            <span class="progress-summary-item__dot"></span>
            <div>
              <div class="progress-summary-item__label">未测试</div>
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
            <h3>测试任务列表</h3>
            <span class="section-title__meta">按状态、通过率和负责人信息查看当前测试推进情况</span>
          </div>
          <div class="inline-stats muted-text">共 {{ testProgressList.length }} 条记录</div>
        </div>
      </template>

      <el-table :data="testProgressList" v-loading="loading" stripe :row-class-name="getTableRowClassName">
        <el-table-column prop="fr_number" label="FR号码" width="130" show-overflow-tooltip>
          <template #default="{ row }">
            <span>{{ row.fr_number || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="test_name" label="测试名称" width="180" show-overflow-tooltip />
        <el-table-column label="风险" width="100">
          <template #default="{ row }">
            <el-tag :type="getRiskTagType(row)" size="small">
              {{ getRiskText(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="L0" width="220">
          <template #default="{ row }">
            <div class="case-stats-wrap">
              <div class="case-stats" :title="`Pass ${row.l0_passed_cases} / Fail ${getStageFailed(row, 'l0')} / Total ${row.l0_total_cases}`">
                <span class="pass-count">{{ row.l0_passed_cases }}</span>
                <span class="sep">/</span>
                <span class="fail-count">{{ getStageFailed(row, 'l0') }}</span>
                <span class="sep">/</span>
                <span class="total-count">{{ row.l0_total_cases }}</span>
              </div>
              <div class="due-date-text" :class="`due-date-text--${getStageDeadlineLevel(row, 'l0')}`">
                完成日期: {{ formatDueDate(row.l0_due_date) }}
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="L2" width="220">
          <template #default="{ row }">
            <div class="case-stats-wrap">
              <div class="case-stats" :title="`Pass ${row.l2_passed_cases} / Fail ${getStageFailed(row, 'l2')} / Total ${row.l2_total_cases}`">
                <span class="pass-count">{{ row.l2_passed_cases }}</span>
                <span class="sep">/</span>
                <span class="fail-count">{{ getStageFailed(row, 'l2') }}</span>
                <span class="sep">/</span>
                <span class="total-count">{{ row.l2_total_cases }}</span>
              </div>
              <div class="due-date-text" :class="`due-date-text--${getStageDeadlineLevel(row, 'l2')}`">
                完成日期: {{ formatDueDate(row.l2_due_date) }}
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="L4" width="220">
          <template #default="{ row }">
            <div class="case-stats-wrap">
              <div class="case-stats" :title="`Pass ${row.l4_passed_cases} / Fail ${getStageFailed(row, 'l4')} / Total ${row.l4_total_cases}`">
                <span class="pass-count">{{ row.l4_passed_cases }}</span>
                <span class="sep">/</span>
                <span class="fail-count">{{ getStageFailed(row, 'l4') }}</span>
                <span class="sep">/</span>
                <span class="total-count">{{ row.l4_total_cases }}</span>
              </div>
              <div class="due-date-text" :class="`due-date-text--${getStageDeadlineLevel(row, 'l4')}`">
                完成日期: {{ formatDueDate(row.l4_due_date) }}
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="总计" width="200">
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
        <el-table-column label="进度" width="160">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :status="getProgressStatus(row.status)" :stroke-width="10" />
          </template>
        </el-table-column>
        <el-table-column label="测试负责人" width="130">
          <template #default="{ row }">
            <span :title="row.test_owners">{{ row.test_owners || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="开发人员" width="130">
          <template #default="{ row }">
            <span :title="row.developers">{{ row.developers || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row.id)">查看详情</el-button>
            <el-button size="small" @click="viewBugs(row.id)">查看Bug</el-button>
            <el-button v-if="canCreateOrEditTest()" size="small" type="primary" @click="editTest(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingTest ? '编辑测试' : '新建测试'"
      width="560px"
    >
      <el-form :model="testForm" label-width="120px">
        <el-form-item label="FR号码">
          <el-input v-model="testForm.fr_number" placeholder="例如：FR-2026-001" />
        </el-form-item>
        <el-form-item label="测试名称">
          <el-input v-model="testForm.test_name" placeholder="请输入测试名称" />
        </el-form-item>
        <el-form-item label="功能描述">
          <el-input v-model="testForm.model_name" placeholder="简述FR功能" />
        </el-form-item>
        <el-form-item label="具体描述">
          <el-input v-model="testForm.description" type="textarea" :rows="4" placeholder="功能的具体描述" />
        </el-form-item>
        <el-form-item label="配置方式">
          <el-input v-model="testForm.config_method" type="textarea" :rows="3" placeholder="功能的配置方式" />
        </el-form-item>
        <el-form-item label="测试负责人">
          <el-input v-model="testForm.test_owners" placeholder="多人请用逗号分隔，如：张三,李四" />
        </el-form-item>
        <el-form-item label="开发人员">
          <el-input v-model="testForm.developers" placeholder="多人请用逗号分隔，如：王五,赵六" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="testForm.status" style="width: 100%">
            <el-option label="待开始" value="pending" />
            <el-option label="运行中" value="running" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item label="L0 用例">
          <el-input-number v-model="testForm.l0_passed_cases" :min="0" size="small" style="width: 88px" />
          <span class="form-divider">/</span>
          <el-input-number v-model="testForm.l0_failed_cases" :min="0" size="small" style="width: 88px" />
          <span class="form-divider">/</span>
          <el-input-number v-model="testForm.l0_total_cases" :min="0" size="small" style="width: 88px" />
        </el-form-item>
        <el-form-item label="L0完成日期">
          <el-date-picker
            v-model="testForm.l0_due_date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="请选择L0完成日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="L2 用例">
          <el-input-number v-model="testForm.l2_passed_cases" :min="0" size="small" style="width: 88px" />
          <span class="form-divider">/</span>
          <el-input-number v-model="testForm.l2_failed_cases" :min="0" size="small" style="width: 88px" />
          <span class="form-divider">/</span>
          <el-input-number v-model="testForm.l2_total_cases" :min="0" size="small" style="width: 88px" />
        </el-form-item>
        <el-form-item label="L2完成日期">
          <el-date-picker
            v-model="testForm.l2_due_date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="请选择L2完成日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="L4 用例">
          <el-input-number v-model="testForm.l4_passed_cases" :min="0" size="small" style="width: 88px" />
          <span class="form-divider">/</span>
          <el-input-number v-model="testForm.l4_failed_cases" :min="0" size="small" style="width: 88px" />
          <span class="form-divider">/</span>
          <el-input-number v-model="testForm.l4_total_cases" :min="0" size="small" style="width: 88px" />
        </el-form-item>
        <el-form-item label="L4完成日期">
          <el-date-picker
            v-model="testForm.l4_due_date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="请选择L4完成日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item>
          <span class="form-helper">输入格式：Pass / Fail / Total（未测 = Total - Pass - Fail，不计入失败）</span>
        </el-form-item>
        <el-form-item label="进度" v-if="calcProgress !== null">
          <span class="progress-hint">自动计算：{{ calcProgress }}%</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTest">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getTestProgressList, createTestProgress, updateTestProgress } from '../api/testProgress'
import { canCreateOrEditTest } from '../stores/auth'

const router = useRouter()
const loading = ref(false)
const testProgressList = ref([])
const showCreateDialog = ref(false)
const editingTest = ref(null)
const DAYS_TO_WARNING = 3

const testForm = ref({
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
  test_owners: '',
  developers: ''
})

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
          name: '已通过',
          itemStyle: { color: '#34d399' }
        },
        {
          value: overviewStats.value.failedCases,
          name: '已失败',
          itemStyle: { color: '#fb7185' }
        },
        {
          value: overviewStats.value.untestedCases,
          name: '未测试',
          itemStyle: { color: '#60a5fa' }
        }
      ]
    }
  ]
}))

const loadData = async () => {
  loading.value = true
  try {
    const data = await getTestProgressList()
    testProgressList.value = data
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
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
  const map = {
    pending: '待开始',
    running: '运行中',
    completed: '已完成',
    failed: '失败'
  }
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

const getTaskRiskLevel = (row) => {
  const levels = ['l0', 'l2', 'l4'].map(stage => getStageDeadlineLevel(row, stage))
  if (levels.includes('danger')) return 'danger'
  if (levels.includes('warning')) return 'warning'
  return 'normal'
}

const getRiskText = (row) => {
  const level = getTaskRiskLevel(row)
  if (level === 'danger') return '超期'
  if (level === 'warning') return '临期'
  return '正常'
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

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

const formatDueDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  if (Number.isNaN(date.getTime())) return '-'
  return date.toLocaleDateString('zh-CN')
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
    test_owners: test.test_owners || '',
    developers: test.developers || ''
  }
  showCreateDialog.value = true
}

const saveTest = async () => {
  try {
    if (editingTest.value) {
      await updateTestProgress(editingTest.value.id, testForm.value)
      ElMessage.success('更新成功')
    } else {
      await createTestProgress(testForm.value)
      ElMessage.success('创建成功')
    }
    showCreateDialog.value = false
    editingTest.value = null
    testForm.value = {
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
      test_owners: '',
      developers: ''
    }
    loadData()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

onMounted(() => {
  loadData()
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

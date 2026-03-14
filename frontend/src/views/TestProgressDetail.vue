<template>
  <div class="page-shell detail-container">
    <section class="page-hero detail-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">Task Detail</div>
        <h2 class="page-hero__title">测试任务详情</h2>
        <p class="page-hero__desc">查看单个测试任务的功能说明、配置方式、当前状态、进度拆解与关联缺陷，适合做深度跟踪和协同交接。</p>
      </div>
      <div class="page-hero__actions">
        <el-button @click="goBack">返回列表</el-button>
        <el-button v-if="canEditBug()" type="primary" @click="goToBugs">管理Bug</el-button>
      </div>
    </section>

    <el-card v-loading="loading" class="section-card detail-card">
      <template v-if="testDetail">
        <div class="detail-header">
          <div>
            <h2>{{ testDetail.test_name }}</h2>
            <p class="detail-subtitle">{{ testDetail.model_name || '暂无功能描述' }}</p>
            <p class="detail-subtitle">FR号码：{{ testDetail.fr_number || '-' }}</p>
          </div>
          <div class="inline-stats">
            <div class="glass-pill">
              <span>状态：</span>
              <el-tag :type="getStatusType(testDetail.status)" size="small">
                {{ getStatusText(testDetail.status) }}
              </el-tag>
            </div>
            <div class="glass-pill">创建于 {{ formatDate(testDetail.created_at) }}</div>
          </div>
        </div>

        <div class="metrics-grid detail-metrics">
          <article class="metric-card accent-blue">
            <div class="metric-card__label">当前进度</div>
            <div class="metric-card__value">{{ testDetail.progress }}%</div>
            <div class="metric-card__meta">按通过用例自动汇总</div>
          </article>
          <article class="metric-card accent-green">
            <div class="metric-card__label">总通过/总用例</div>
            <div class="metric-card__value">{{ testDetail.passed_cases }}/{{ testDetail.total_cases }}</div>
            <div class="metric-card__meta">包含 L0 / L2 / L4 所有统计</div>
          </article>
          <article class="metric-card accent-red">
            <div class="metric-card__label">关联 Bug</div>
            <div class="metric-card__value">{{ testDetail.bugs?.length || 0 }}</div>
            <div class="metric-card__meta">当前测试任务关联的问题数</div>
          </article>
          <article class="metric-card accent-purple">
            <div class="metric-card__label">最近更新时间</div>
            <div class="metric-card__value metric-card__value--small">{{ formatDate(testDetail.updated_at) || '未更新' }}</div>
            <div class="metric-card__meta">用于判断任务最近活跃度</div>
          </article>
        </div>

        <div class="detail-people" v-if="testDetail.test_owners || testDetail.developers">
          <span class="people-item"><strong>FR号码：</strong>{{ testDetail.fr_number || '-' }}</span>
          <span class="people-item"><strong>测试负责人：</strong>{{ testDetail.test_owners || '-' }}</span>
          <span class="people-item"><strong>开发人员：</strong>{{ testDetail.developers || '-' }}</span>
        </div>

        <el-card class="section-card detail-inner-card">
          <template #header>
            <div class="section-title">
              <div class="section-title__main">
                <h3>功能与配置信息</h3>
                <span class="section-title__meta">沉淀任务背景、功能描述与配置方式，便于追踪与交接</span>
              </div>
            </div>
          </template>
          <el-descriptions :column="1" border class="detail-info">
            <el-descriptions-item label="功能描述（简述FR）">
              <div class="description-text">{{ testDetail.model_name || '-' }}</div>
            </el-descriptions-item>
            <el-descriptions-item label="FR号码">
              <div class="description-text">{{ testDetail.fr_number || '-' }}</div>
            </el-descriptions-item>
            <el-descriptions-item label="功能具体描述">
              <div class="description-text">{{ testDetail.description || '-' }}</div>
            </el-descriptions-item>
            <el-descriptions-item label="配置方式">
              <div class="description-text">{{ testDetail.config_method || '-' }}</div>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="section-card detail-inner-card">
          <template #header>
            <div class="section-title">
              <div class="section-title__main">
                <h3>阶段统计与任务状态</h3>
                <span class="section-title__meta">每个阶段按 Pass/Fail/Total 展示，未测不会计入 Fail</span>
              </div>
            </div>
          </template>
          <el-descriptions :column="2" border class="detail-info">
            <el-descriptions-item label="状态">{{ getStatusText(testDetail.status) }}</el-descriptions-item>
            <el-descriptions-item label="测试负责人">{{ testDetail.test_owners || '-' }}</el-descriptions-item>
            <el-descriptions-item label="开发人员">{{ testDetail.developers || '-' }}</el-descriptions-item>
            <el-descriptions-item label="L0（Pass/Fail/Total)">
              <div class="case-stats">
                <span class="pass-count">{{ testDetail.l0_passed_cases }}</span>
                <span class="sep">/</span>
                <span class="fail-count">{{ getStageFailed(testDetail, 'l0') }}</span>
                <span class="sep">/</span>
                <span class="total-count">{{ testDetail.l0_total_cases }}</span>
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="L0完成日期">
              <span :class="`due-date-text due-date-text--${getStageDeadlineLevel(testDetail, 'l0')}`">
                {{ formatDueDate(testDetail.l0_due_date) }}
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="L2（Pass/Fail/Total)">
              <div class="case-stats">
                <span class="pass-count">{{ testDetail.l2_passed_cases }}</span>
                <span class="sep">/</span>
                <span class="fail-count">{{ getStageFailed(testDetail, 'l2') }}</span>
                <span class="sep">/</span>
                <span class="total-count">{{ testDetail.l2_total_cases }}</span>
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="L2完成日期">
              <span :class="`due-date-text due-date-text--${getStageDeadlineLevel(testDetail, 'l2')}`">
                {{ formatDueDate(testDetail.l2_due_date) }}
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="L4（Pass/Fail/Total)">
              <div class="case-stats">
                <span class="pass-count">{{ testDetail.l4_passed_cases }}</span>
                <span class="sep">/</span>
                <span class="fail-count">{{ getStageFailed(testDetail, 'l4') }}</span>
                <span class="sep">/</span>
                <span class="total-count">{{ testDetail.l4_total_cases }}</span>
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="L4完成日期">
              <span :class="`due-date-text due-date-text--${getStageDeadlineLevel(testDetail, 'l4')}`">
                {{ formatDueDate(testDetail.l4_due_date) }}
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="总计（Pass/Fail/Total)">
              <div class="case-stats">
                <span class="pass-count">{{ testDetail.passed_cases }}</span>
                <span class="sep">/</span>
                <span class="fail-count">{{ getTotalFailed(testDetail) }}</span>
                <span class="sep">/</span>
                <span class="total-count">{{ testDetail.total_cases }}</span>
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="进度">
              <el-progress :percentage="testDetail.progress" :status="getProgressStatus(testDetail.status)" style="width: 200px" />
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDate(testDetail.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="更新时间">{{ formatDate(testDetail.updated_at) || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="section-card detail-inner-card">
          <template #header>
            <div class="section-title">
              <div class="section-title__main">
                <h3>关联 Bug（{{ testDetail.bugs?.length || 0 }}）</h3>
                <span class="section-title__meta">关联问题跟踪与处理状态一览</span>
              </div>
            </div>
          </template>
          <div class="bugs-section">
            <el-table :data="testDetail.bugs || []" stripe empty-text="暂无Bug">
              <el-table-column prop="title" label="标题" width="220" />
              <el-table-column prop="severity" label="严重程度" width="130">
                <template #default="{ row }">
                  <el-tag :type="getSeverityType(row.severity)" size="small">
                    {{ getSeverityText(row.severity) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="130">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)" size="small">
                    {{ getBugStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="assigned_to" label="负责人" width="140" />
              <el-table-column prop="description" label="描述" show-overflow-tooltip />
            </el-table>
          </div>
        </el-card>
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getTestProgressDetail } from '../api/testProgress'
import { canEditBug } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const testDetail = ref(null)
const DAYS_TO_WARNING = 3

const loadDetail = async () => {
  const id = route.params.id
  if (!id) return
  loading.value = true
  try {
    testDetail.value = await getTestProgressDetail(id)
  } catch (error) {
    ElMessage.error('加载详情失败')
  } finally {
    loading.value = false
  }
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
  const map = { pending: '待开始', running: '运行中', completed: '已完成', failed: '失败' }
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

const getSeverityType = (severity) => {
  const map = { critical: 'danger', high: 'warning', medium: 'info', low: '' }
  return map[severity] || 'info'
}

const getSeverityText = (severity) => {
  const map = { critical: '严重', high: '高', medium: '中', low: '低' }
  return map[severity] || severity
}

const getBugStatusText = (status) => {
  const map = { open: '待处理', in_progress: '处理中', resolved: '已解决', closed: '已关闭' }
  return map[status] || status
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

onMounted(() => loadDetail())
</script>

<style scoped>
.detail-container {
  width: 100%;
}

.detail-card {
  margin-top: 0;
}

.detail-inner-card {
  margin-bottom: 16px;
}

.detail-inner-card:last-child {
  margin-bottom: 0;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.detail-header h2 {
  margin: 0;
  font-size: 26px;
}

.detail-subtitle {
  margin: 8px 0 0;
  color: rgba(226, 232, 240, 0.72);
  font-size: 14px;
  line-height: 1.6;
}

.detail-people {
  display: flex;
  gap: 32px;
  padding: 12px 16px;
  margin-bottom: 16px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 14px;
}

.people-item {
  font-size: 14px;
}

.due-date-text {
  color: rgba(148, 163, 184, 0.9);
}

.due-date-text--warning {
  color: #f59e0b;
  font-weight: 600;
}

.due-date-text--danger {
  color: #ef4444;
  font-weight: 600;
}

.detail-info {
  margin-bottom: 0;
}

.detail-container :deep(.detail-inner-card.el-card) {
  background: rgba(8, 15, 28, 0.78) !important;
  border-color: rgba(148, 163, 184, 0.14) !important;
}

.detail-container :deep(.detail-inner-card .el-card__header) {
  background: rgba(255, 255, 255, 0.02) !important;
}

.detail-container :deep(.detail-info.el-descriptions) {
  --el-descriptions-table-border: rgba(148, 163, 184, 0.14);
  --el-descriptions-item-bordered-label-background: rgba(148, 163, 184, 0.1);
  --el-descriptions-item-bordered-content-background: rgba(255, 255, 255, 0.02);
}

.detail-container :deep(.detail-info .el-descriptions__label.el-descriptions__cell.is-bordered-label) {
  background: rgba(148, 163, 184, 0.1) !important;
  color: #f8fafc !important;
}

.detail-container :deep(.detail-info .el-descriptions__content.el-descriptions__cell.is-bordered-content) {
  background: rgba(255, 255, 255, 0.02) !important;
  color: #e2e8f0 !important;
}

.bugs-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
}

.description-text {
  white-space: pre-wrap;
  line-height: 1.6;
}

.detail-metrics {
  margin-bottom: 20px;
}

.metric-card__value--small {
  font-size: 20px;
  line-height: 1.4;
}

.case-stats {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: 600;
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

@media (max-width: 768px) {
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .detail-header .inline-stats {
    width: 100%;
  }

  .detail-people {
    flex-direction: column;
    gap: 10px;
  }
}
</style>

<template>
  <div class="page-shell detail-container">
    <section class="page-hero detail-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">Task Detail</div>
        <h2 class="page-hero__title">Test Task Details</h2>
        <p class="page-hero__desc">Review one test task in depth, including feature notes, configuration, current status, progress breakdown, and linked defects for follow-up and handoff.</p>
      </div>
      <div class="page-hero__actions">
        <el-button @click="goBack">Back to List</el-button>
        <el-button v-if="canEditBug()" type="primary" @click="goToBugs">Manage Bugs</el-button>
      </div>
    </section>

    <el-card v-loading="loading" class="section-card detail-card">
      <template v-if="testDetail">
        <div class="detail-header">
          <div>
            <h2>{{ testDetail.test_name }}</h2>
            <p class="detail-subtitle">{{ testDetail.model_name || 'No feature summary yet' }}</p>
            <p class="detail-subtitle">FR Number: {{ testDetail.fr_number || '-' }}</p>
          </div>
          <div class="inline-stats">
            <div class="glass-pill">
              <span>Status: </span>
              <el-tag :type="getStatusType(testDetail.status)" size="small">
                {{ getStatusText(testDetail.status) }}
              </el-tag>
            </div>
            <div class="glass-pill">Created on {{ formatDate(testDetail.created_at) }}</div>
          </div>
        </div>

        <div class="metrics-grid detail-metrics">
          <article class="metric-card accent-blue">
            <div class="metric-card__label">Current Progress</div>
            <div class="metric-card__value">{{ testDetail.progress }}%</div>
            <div class="metric-card__meta">Calculated automatically from passed cases</div>
          </article>
          <article class="metric-card accent-green">
            <div class="metric-card__label">Passed / Total Cases</div>
            <div class="metric-card__value">{{ testDetail.passed_cases }}/{{ testDetail.total_cases }}</div>
            <div class="metric-card__meta">Includes all L0 / L2 / L4 statistics</div>
          </article>
          <article class="metric-card accent-red">
            <div class="metric-card__label">Linked Bugs</div>
            <div class="metric-card__value">{{ testDetail.bugs?.length || 0 }}</div>
            <div class="metric-card__meta">Issues currently linked to this test task</div>
          </article>
          <article class="metric-card accent-purple">
            <div class="metric-card__label">Estimated Manday</div>
            <div class="metric-card__value metric-card__value--small">{{ Number(testDetail.estimated_hours || 0).toFixed(1) }} manday</div>
            <div class="metric-card__meta">Shown on the detail page only</div>
          </article>
        </div>

        <div class="detail-people" v-if="testDetail.test_owners || testDetail.developers">
          <span class="people-item"><strong>FR Number: </strong>{{ testDetail.fr_number || '-' }}</span>
          <span class="people-item"><strong>Testers: </strong>{{ testDetail.test_owners || '-' }}</span>
          <span class="people-item"><strong>Developers: </strong>{{ testDetail.developers || '-' }}</span>
        </div>

        <el-card class="section-card detail-inner-card">
          <template #header>
            <div class="section-title">
              <div class="section-title__main">
                <h3>Feature and Configuration</h3>
                <span class="section-title__meta">Capture task background, feature details, and configuration notes for tracking and handoff.</span>
              </div>
            </div>
          </template>
          <el-descriptions :column="1" border class="detail-info">
            <el-descriptions-item label="Feature Summary (FR Brief)">
              <div class="description-text">{{ testDetail.model_name || '-' }}</div>
            </el-descriptions-item>
            <el-descriptions-item label="FR Number">
              <div class="description-text">{{ testDetail.fr_number || '-' }}</div>
            </el-descriptions-item>
            <el-descriptions-item label="Detailed Description">
              <div class="description-text">{{ testDetail.description || '-' }}</div>
            </el-descriptions-item>
            <el-descriptions-item label="Configuration Method">
              <div class="description-text">{{ testDetail.config_method || '-' }}</div>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="section-card detail-inner-card">
          <template #header>
            <div class="section-title">
              <div class="section-title__main">
                <h3>Stage Statistics and Task Status</h3>
                <span class="section-title__meta">Each stage is shown as Pass/Fail/Total, and untested cases are not counted as failures.</span>
              </div>
            </div>
          </template>
          <el-descriptions :column="2" border class="detail-info">
            <el-descriptions-item label="Status">{{ getStatusText(testDetail.status) }}</el-descriptions-item>
            <el-descriptions-item label="Testers">{{ testDetail.test_owners || '-' }}</el-descriptions-item>
            <el-descriptions-item label="Developers">{{ testDetail.developers || '-' }}</el-descriptions-item>
            <el-descriptions-item label="Estimated Manday">{{ Number(testDetail.estimated_hours || 0).toFixed(1) }} manday</el-descriptions-item>
            <el-descriptions-item label="Start Date">{{ getStartDate(testDetail) }}</el-descriptions-item>
            <el-descriptions-item label="Completion Date">{{ getCompletionDate(testDetail) }}</el-descriptions-item>
            <el-descriptions-item label="L0 (Pass/Fail/Total)">
              <div class="case-stats">
                <span class="pass-count">{{ testDetail.l0_passed_cases }}</span>
                <span class="sep">/</span>
                <span class="fail-count">{{ getStageFailed(testDetail, 'l0') }}</span>
                <span class="sep">/</span>
                <span class="total-count">{{ testDetail.l0_total_cases }}</span>
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="L0 Due Date">
              <span :class="`due-date-text due-date-text--${getStageDeadlineLevel(testDetail, 'l0')}`">
                {{ formatDueDate(testDetail.l0_due_date) }}
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="L2 (Pass/Fail/Total)">
              <div class="case-stats">
                <span class="pass-count">{{ testDetail.l2_passed_cases }}</span>
                <span class="sep">/</span>
                <span class="fail-count">{{ getStageFailed(testDetail, 'l2') }}</span>
                <span class="sep">/</span>
                <span class="total-count">{{ testDetail.l2_total_cases }}</span>
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="L2 Due Date">
              <span :class="`due-date-text due-date-text--${getStageDeadlineLevel(testDetail, 'l2')}`">
                {{ formatDueDate(testDetail.l2_due_date) }}
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="L4 (Pass/Fail/Total)">
              <div class="case-stats">
                <span class="pass-count">{{ testDetail.l4_passed_cases }}</span>
                <span class="sep">/</span>
                <span class="fail-count">{{ getStageFailed(testDetail, 'l4') }}</span>
                <span class="sep">/</span>
                <span class="total-count">{{ testDetail.l4_total_cases }}</span>
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="L4 Due Date">
              <span :class="`due-date-text due-date-text--${getStageDeadlineLevel(testDetail, 'l4')}`">
                {{ formatDueDate(testDetail.l4_due_date) }}
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="Overall (Pass/Fail/Total)">
              <div class="case-stats">
                <span class="pass-count">{{ testDetail.passed_cases }}</span>
                <span class="sep">/</span>
                <span class="fail-count">{{ getTotalFailed(testDetail) }}</span>
                <span class="sep">/</span>
                <span class="total-count">{{ testDetail.total_cases }}</span>
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="Progress">
              <el-progress :percentage="testDetail.progress" :status="getProgressStatus(testDetail.status)" style="width: 200px" />
            </el-descriptions-item>
            <el-descriptions-item label="Created At">{{ formatDate(testDetail.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="Updated At">{{ formatDate(testDetail.updated_at) || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="section-card detail-inner-card">
          <template #header>
            <div class="section-title">
              <div class="section-title__main">
                <h3>Linked Bugs ({{ testDetail.bugs?.length || 0 }})</h3>
                <span class="section-title__meta">An overview of linked issues and their processing state.</span>
              </div>
            </div>
          </template>
          <div class="bugs-section">
            <el-table :data="testDetail.bugs || []" stripe empty-text="No linked bugs">
              <el-table-column prop="external_cr_number" label="CR Number" width="130" />
              <el-table-column prop="title" label="Title" min-width="280" show-overflow-tooltip />
              <el-table-column prop="status" label="Status" width="120">
                <template #default="{ row }">
                  <el-tag :type="getBugStatusType(row.status)" size="small">
                    {{ getBugStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_by" label="Created By" width="120" />
              <el-table-column prop="cr_assignee" label="CR Assignee" width="130" />
              <el-table-column prop="cr_created_on" label="Created On" width="180">
                <template #default="{ row }">{{ formatDate(row.cr_created_on) || '-' }}</template>
              </el-table-column>
              <el-table-column prop="software_image_integration_build" label="Software Image Integration Build" min-width="250" show-overflow-tooltip />
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
    ElMessage.error('Failed to load details')
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
  const map = { pending: 'Pending', running: 'Running', completed: 'Completed', failed: 'Failed' }
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

const getBugStatusType = (status) => {
  const map = { fixed: 'success', analysis: 'warning', other: 'info' }
  return map[status] || 'info'
}

const getSeverityText = (severity) => {
  const map = { critical: 'Critical', high: 'High', medium: 'Medium', low: 'Low' }
  return map[severity] || severity
}

const getBugStatusText = (status) => {
  const map = { fixed: 'Fixed', analysis: 'Analysis', other: 'Other' }
  return map[status] || status
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('en-CA')
}

const formatDueDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  if (Number.isNaN(date.getTime())) return '-'
  return date.toLocaleDateString('en-CA')
}

const getStartDate = (row) => {
  return formatDueDate(row?.start_date)
}

const getCompletionDate = (row) => {
  return formatDueDate(row?.completion_date)
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
  position: relative;
  margin-bottom: 16px;
}

.detail-inner-card:last-child {
  margin-bottom: 0;
}

.detail-inner-card + .detail-inner-card {
  margin-top: 20px;
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
  border-color: rgba(148, 163, 184, 0.3) !important;
  box-shadow: inset 0 0 0 1px rgba(56, 189, 248, 0.08), 0 12px 28px rgba(2, 8, 23, 0.28);
}

.detail-container :deep(.detail-inner-card .el-card__header) {
  background: rgba(255, 255, 255, 0.02) !important;
  border-bottom: 1px solid rgba(148, 163, 184, 0.32) !important;
  box-shadow: inset 0 -1px 0 rgba(56, 189, 248, 0.2);
}

.detail-container :deep(.detail-inner-card .el-card__body) {
  border-top: 1px solid rgba(15, 23, 42, 0.6);
}

.detail-container :deep(.detail-info.el-descriptions) {
  --el-descriptions-table-border: rgba(148, 163, 184, 0.28);
  --el-descriptions-item-bordered-label-background: rgba(148, 163, 184, 0.1);
  --el-descriptions-item-bordered-content-background: rgba(255, 255, 255, 0.03);
}

.detail-container :deep(.detail-info .el-descriptions__label.el-descriptions__cell.is-bordered-label) {
  background: rgba(148, 163, 184, 0.1) !important;
  color: #f8fafc !important;
  font-weight: 700;
  border-right: 2px solid rgba(148, 163, 184, 0.36) !important;
  border-top: 1px solid rgba(148, 163, 184, 0.32) !important;
  border-bottom: 1px solid rgba(148, 163, 184, 0.32) !important;
  box-shadow: inset -1px 0 0 rgba(56, 189, 248, 0.24);
}

.detail-container :deep(.detail-info .el-descriptions__row > .el-descriptions__cell.is-bordered-label:not(:first-child)) {
  border-left: 2px solid rgba(148, 163, 184, 0.34) !important;
}

.detail-container :deep(.detail-info .el-descriptions__row:first-child > .el-descriptions__cell.is-bordered-label) {
  border-top-color: rgba(125, 211, 252, 0.45) !important;
}

.detail-container :deep(.detail-info .el-descriptions__row:last-child > .el-descriptions__cell.is-bordered-label) {
  border-bottom-color: rgba(125, 211, 252, 0.45) !important;
}

.detail-container :deep(.detail-info .el-descriptions__content.el-descriptions__cell.is-bordered-content) {
  background: rgba(255, 255, 255, 0.02) !important;
  color: #e2e8f0 !important;
  border-top: 1px solid rgba(148, 163, 184, 0.3) !important;
  border-bottom: 1px solid rgba(148, 163, 184, 0.3) !important;
  border-left: 1px solid rgba(148, 163, 184, 0.24) !important;
}

.detail-container :deep(.detail-info .el-descriptions__row > .el-descriptions__cell.is-bordered-content:nth-child(4)) {
  border-left: 2px solid rgba(148, 163, 184, 0.34) !important;
}

.detail-container :deep(.detail-info .el-descriptions__row:first-child > .el-descriptions__cell.is-bordered-content) {
  border-top-color: rgba(125, 211, 252, 0.45) !important;
}

.detail-container :deep(.detail-info .el-descriptions__row:last-child > .el-descriptions__cell.is-bordered-content) {
  border-bottom-color: rgba(125, 211, 252, 0.45) !important;
}

.detail-container :deep(.detail-info .el-descriptions__row) {
  border-bottom: 1px solid rgba(148, 163, 184, 0.22) !important;
}

.detail-container :deep(.detail-info .el-descriptions__row:last-child) {
  border-bottom: none !important;
}

.detail-container :deep(.detail-inner-card .el-table th.el-table__cell) {
  border-bottom: 1px solid rgba(148, 163, 184, 0.3) !important;
}

.detail-container :deep(.detail-inner-card .el-table td.el-table__cell) {
  border-bottom: 1px solid rgba(148, 163, 184, 0.18) !important;
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

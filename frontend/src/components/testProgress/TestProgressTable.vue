<template>
  <div>
    <el-table
      :data="tasks"
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
              @click="emit('view', row.id)"
            >
              {{ row.test_name || '-' }}
            </button>
            <div v-else class="task-info-cell__name">{{ row.test_name || '-' }}</div>
          </div>
        </template>
      </el-table-column>

      <el-table-column :label="LT.table.risk" width="96">
        <template #default="{ row }">
          <el-tag :type="getRiskTagType(row)" size="small">{{ getRiskText(row) }}</el-tag>
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
              {{ DT.helper.dueDatePrefix }} {{ formatDate(getCurrentStageDueDate(row)) }}
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
            <el-button size="small" @click="emit('view', row.id)">{{ BT.details }}</el-button>
            <el-button size="small" @click="emit('view-bugs', row.id)">{{ BT.bugs }}</el-button>
            <el-button v-if="canEdit" size="small" type="primary" @click="emit('edit', row)">{{ BTCommon.edit }}</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <div class="list-pagination">
      <el-pagination
        v-if="total > pageSize"
        background
        layout="prev, pager, next"
        :page-size="pageSize"
        :total="total"
        :current-page="currentPage"
        @current-change="emit('page-change', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { LabelText } from '../../texts/LabelText'
import { ButtonText } from '../../texts/ButtonText'
import { DescriptionText } from '../../texts/DescriptionText'
import { formatDate } from '../../utils/formatters'
import { getTaskProgressStatus, getTaskStatusTagType, getTaskStatusText } from '../../utils/taskStatus'

defineProps({
  tasks: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  canEdit: { type: Boolean, default: false },
  total: { type: Number, default: 0 },
  pageSize: { type: Number, default: 10 },
  currentPage: { type: Number, default: 1 }
})

const emit = defineEmits(['view', 'view-bugs', 'edit', 'page-change'])

const LT = LabelText.testProgress
const BT = ButtonText.testProgress
const BTCommon = ButtonText.common
const DT = DescriptionText.testProgress

const DAYS_TO_WARNING = 3

const getStageFailed = (row, stage) => {
  const explicit = row?.[`${stage}_failed_cases`]
  if (explicit !== undefined && explicit !== null) return Number(explicit)
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

const getCurrentStagePassed = (row) => Number(row?.[`${getCurrentStageKey(row)}_passed_cases`] ?? 0)
const getCurrentStageTotal = (row) => Number(row?.[`${getCurrentStageKey(row)}_total_cases`] ?? 0)
const getCurrentStageFailed = (row) => getStageFailed(row, getCurrentStageKey(row))
const getCurrentStageDueDate = (row) => row?.[`${getCurrentStageKey(row)}_due_date`] ?? null

const getTotalFailed = (row) => {
  if (row?.failed_cases !== undefined && row?.failed_cases !== null) return Number(row.failed_cases)
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

const getCurrentStageDeadlineLevel = (row) => getStageDeadlineLevel(row, getCurrentStageKey(row))

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
</script>

<style scoped>
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

.due-date-text--warning { color: #f59e0b; }
.due-date-text--danger { color: #ef4444; }

.pass-count { color: #34d399; }
.fail-count { color: #fb7185; }
.total-count { color: #e2e8f0; }
.sep { color: rgba(148, 163, 184, 0.78); }

.list-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>

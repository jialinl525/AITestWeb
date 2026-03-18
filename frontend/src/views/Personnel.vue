<template>
  <div class="page-shell personnel-container">
    <section class="page-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">{{ LT.heroEyebrow }}</div>
        <h2 class="page-hero__title">{{ LT.heroTitle }}</h2>
        <p class="page-hero__desc">
          {{ DT.hero }}
        </p>
      </div>
      <div class="page-hero__actions">
        <div class="glass-pill">{{ LT.pills.members }} {{ members.length }}</div>
        <div class="glass-pill">{{ LT.pills.tasks }} {{ totalTasks }}</div>
        <div class="glass-pill">{{ LT.pills.mandays }} {{ totalHours }} manday</div>
        <div class="glass-pill">{{ LT.pills.overlaps }} {{ totalOverlaps }}</div>
        <el-button @click="loadData">{{ BTCommon.refresh }}</el-button>
      </div>
    </section>

    <div class="metrics-grid">
      <article class="metric-card accent-blue">
        <div class="metric-card__label">{{ LT.metrics.members }}</div>
        <div class="metric-card__value">{{ members.length }}</div>
        <div class="metric-card__meta">{{ DT.metricsMeta.members }}</div>
      </article>
      <article class="metric-card accent-green">
        <div class="metric-card__label">{{ LT.metrics.avgTasks }}</div>
        <div class="metric-card__value">{{ averageTasks }}</div>
        <div class="metric-card__meta">{{ DT.metricsMeta.avgTasks }}</div>
      </article>
      <article class="metric-card accent-orange">
        <div class="metric-card__label">{{ LT.metrics.totalManday }}</div>
        <div class="metric-card__value">{{ totalHours }} manday</div>
        <div class="metric-card__meta">{{ DT.metricsMeta.totalManday }}</div>
      </article>
      <article class="metric-card accent-red">
        <div class="metric-card__label">{{ LT.metrics.overlapGroups }}</div>
        <div class="metric-card__value">{{ totalOverlaps }}</div>
        <div class="metric-card__meta">{{ DT.metricsMeta.overlapGroups }}</div>
      </article>
    </div>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>{{ LT.sectionTitle }}</h3>
            <span class="section-title__meta">{{ DT.sectionMeta }}</span>
          </div>
        </div>
      </template>

      <el-table
        ref="workloadTableRef"
        :data="workload"
        stripe
        class="full-width-table"
        style="width: 100%"
        :fit="true"
        table-layout="auto"
        @expand-change="handleExpandChange"
        @row-click="handleRowClickDebug"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="member-task-grid">
              <div class="member-task-grid__head" :class="{ 'member-task-grid__head--readonly': !canCreateOrEditTest() }">
                <div>{{ LT.table.task }}</div>
                <div>{{ LT.table.partDescription }}</div>
                <div>{{ LT.table.startDate }}</div>
                <div>{{ LT.table.endDate }}</div>
                <div>{{ LT.table.status }}</div>
                <div>{{ LT.table.progress }}</div>
                <div>{{ LT.table.allocatedManday }}</div>
                <div v-if="canCreateOrEditTest()">{{ LT.table.actions }}</div>
              </div>

              <div v-if="!normalizeTaskRows(row.tasks).length" class="member-task-grid__empty">No tasks</div>

              <div
                v-for="task in normalizeTaskRows(row.tasks)"
                :key="task._row_key"
                class="member-task-grid__row"
                :class="{ 'member-task-grid__row--readonly': !canCreateOrEditTest() }"
              >
                <div class="member-task-grid__cell member-task-grid__cell--task" :title="formatTaskName(task)">{{ formatTaskName(task) }}</div>
                <div class="member-task-grid__cell" :title="getPartDescription(task)">{{ getPartDescription(task) }}</div>
                <div class="member-task-grid__cell">{{ formatDate(task.start_date) }}</div>
                <div class="member-task-grid__cell">{{ formatDate(task.end_date) }}</div>
                <div class="member-task-grid__cell">{{ formatStatus(task.status) }}</div>
                <div class="member-task-grid__cell">{{ formatProgress(task.progress) }}</div>
                <div class="member-task-grid__cell">{{ formatManday(task.estimated_hours) }}</div>
                <div v-if="canCreateOrEditTest()" class="member-task-grid__cell member-task-grid__cell--actions">
                  <el-button v-if="task.task_kind === 'test'" size="small" @click="openAllocationDialog(task)">{{ BT.allocateManday }}</el-button>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column :label="LT.table.member" min-width="220">
          <template #default="{ row }">
            <button
              type="button"
              class="member-link"
              @click="viewMemberDetail(row.user_id)"
            >
              {{ row.display_name }}
            </button>
          </template>
        </el-table-column>
        <el-table-column prop="username" :label="LT.table.username" min-width="180" />
        <el-table-column prop="task_count" :label="LT.table.taskCount" min-width="120" />
        <el-table-column :label="LT.table.completedTasks" min-width="120">
          <template #default="{ row }">{{ getCompletedTasks(row) }}</template>
        </el-table-column>
        <el-table-column prop="overlap_count" :label="LT.table.overlapGroups" min-width="130">
          <template #default="{ row }">
            <el-tag :type="getOverlapTagType(row.overlap_count)">{{ row.overlap_count || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_estimated_hours" :label="LT.table.allocatedManday" min-width="140">
          <template #default="{ row }">{{ Number(row.total_estimated_hours || 0).toFixed(1) }} manday</template>
        </el-table-column>
        <el-table-column label="Detail" width="120">
          <template #default="{ row }">
            <el-button size="small" @click.stop="toggleExpand(row)">{{ isExpanded(row.user_id) ? 'Collapse' : 'Expand' }}</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="section-card runtime-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>Runtime Diagnostics</h3>
            <span class="section-title__meta">Captured frontend errors and expand events for debugging</span>
          </div>
          <el-button size="small" @click="clearDiagnostics">Clear Logs</el-button>
        </div>
      </template>
      <div v-if="runtimeDiagnostics.length" class="runtime-log-list">
        <div v-for="item in runtimeDiagnostics" :key="item.id" class="runtime-log-item">
          <div class="runtime-log-item__meta">{{ item.ts }} | {{ item.type }}</div>
          <pre class="runtime-log-item__content">{{ item.message }}</pre>
        </div>
      </div>
      <div v-else class="muted-text">No runtime logs yet. Trigger dropdown interaction to capture events.</div>
    </el-card>

    <el-dialog v-model="showAllocationDialog" :title="`${LT.dialog.taskMandayAllocation} - ${allocationTask.test_name || ''}`" width="980px">
      <div class="muted-text allocation-summary">{{ LT.dialog.totalTaskManday }}: {{ Number(allocationTask.total_estimated_hours || 0).toFixed(1) }} manday</div>
      <el-table :data="allocationRows" size="small" stripe>
        <el-table-column :label="LT.dialog.tester" min-width="260">
          <template #default="{ row: item }">
            <el-select v-model="item.user_id" filterable style="width: 100%" :placeholder="DT.placeholders.selectMember">
              <el-option
                v-for="member in members"
                :key="member.id"
                :label="member.display_name || member.username"
                :value="member.id"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column :label="LT.dialog.allocatedManday" width="180">
          <template #default="{ row: item }">
            <el-input-number v-model="item.allocated_hours" :min="0" :step="0.5" :precision="1" style="width: 140px" />
          </template>
        </el-table-column>
        <el-table-column :label="LT.dialog.partDescription" min-width="300">
          <template #default="{ row: item }">
            <el-input
              v-model="item.part_description"
              type="textarea"
              :rows="2"
              resize="none"
              maxlength="300"
              show-word-limit
              :placeholder="DT.placeholders.partDescriptionExample"
            />
          </template>
        </el-table-column>
        <el-table-column :label="LT.dialog.actions" width="100">
          <template #default="{ $index }">
            <el-button type="danger" link @click="removeAllocationRow($index)">{{ BTCommon.delete }}</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="allocation-toolbar">
        <el-button @click="addAllocationRow">{{ BT.addAllocationRow }}</el-button>
      </div>
      <template #footer>
        <el-button @click="showAllocationDialog = false">{{ BTCommon.cancel }}</el-button>
        <el-button type="primary" :loading="savingAllocation" @click="saveAllocation">{{ BT.saveAllocation }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onErrorCaptured, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { LabelText } from '../texts/LabelText'
import { ButtonText } from '../texts/ButtonText'
import { DescriptionText } from '../texts/DescriptionText'
import {
  getMembers,
  getWorkload,
  getTaskAllocations,
  updateTaskAllocations
} from '../api/personnel'
import { canCreateOrEditTest } from '../stores/auth'

const router = useRouter()
const LT = LabelText.personnel
const BT = ButtonText.personnel
const BTCommon = ButtonText.common
const DT = DescriptionText.personnel
const members = ref([])
const workload = ref([])
const workloadTableRef = ref(null)
const expandedUserIds = ref([])
const runtimeDiagnostics = ref([])
let runtimeSeed = 0

const showAllocationDialog = ref(false)
const savingAllocation = ref(false)

const allocationTask = ref({
  test_id: null,
  test_name: '',
  total_estimated_hours: 0
})
const allocationRows = ref([])

const totalHours = computed(() => {
  const sum = workload.value.reduce((acc, item) => acc + Number(item.total_estimated_hours || 0), 0)
  return Number(sum.toFixed(1))
})

const totalTasks = computed(() => {
  const taskIds = new Set()
  workload.value.forEach(item => {
    ;(item.tasks || []).forEach(task => taskIds.add(`${task.task_kind || 'test'}-${task.id}`))
  })
  return taskIds.size
})

const totalOverlaps = computed(() => {
  return workload.value.reduce((sum, item) => sum + Number(item.overlap_count || 0), 0)
})

const averageTasks = computed(() => {
  if (!members.value.length) return 0
  const sum = workload.value.reduce((acc, item) => acc + Number(item.task_count || 0), 0)
  return Number((sum / members.value.length).toFixed(1))
})

const getCompletedTasks = (row) => {
  return (row.tasks || []).filter(task => String(task.status || '').toLowerCase() === 'completed').length
}

const getOverlapTagType = (count) => {
  const num = Number(count || 0)
  if (num >= 5) return 'danger'
  if (num >= 3) return 'warning'
  return 'success'
}

const formatDate = (value) => {
  if (!value) return '-'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return '-'
  return d.toLocaleDateString('en-CA')
}

const formatStatus = (value) => {
  const text = String(value || '').trim()
  return text || '-'
}

const formatProgress = (value) => {
  const num = Number(value)
  if (!Number.isFinite(num)) return '0%'
  return `${num.toFixed(0)}%`
}

const formatManday = (value) => {
  const num = Number(value)
  if (!Number.isFinite(num)) return '0.0 manday'
  return `${num.toFixed(1)} manday`
}

const getPartDescription = (task) => {
  const text = String(task?.part_description || '').trim()
  if (text) return text
  return DT?.fallback?.unassignedPart || '-'
}

const formatTaskName = (task) => {
  const taskLabel = String(task?.task_label || '').trim()
  if (taskLabel) return taskLabel

  const frNumber = String(task?.fr_number || '').trim()
  const testName = String(task?.test_name || '').trim()
  if (frNumber && testName) return `${frNumber} | ${testName}`
  if (frNumber) return frNumber
  return testName || '-'
}

const normalizeTaskRows = (tasks) => {
  try {
    if (!Array.isArray(tasks)) return []
    return tasks.map((task, index) => ({
      ...task,
      _row_key: `${task?.task_kind || 'test'}-${task?.id ?? 'na'}-${index}`
    }))
  } catch (error) {
    pushRuntimeLog('normalizeTaskRows', formatError(error))
    return []
  }
}

const formatError = (error) => {
  if (!error) return 'Unknown error'
  if (typeof error === 'string') return error
  const name = error?.name ? `${error.name}: ` : ''
  const message = error?.message || String(error)
  const stack = error?.stack ? `\n${error.stack}` : ''
  return `${name}${message}${stack}`
}

const pushRuntimeLog = (type, message) => {
  runtimeSeed += 1
  runtimeDiagnostics.value.unshift({
    id: `${Date.now()}-${runtimeSeed}`,
    ts: new Date().toLocaleString('en-CA'),
    type,
    message: String(message || '')
  })
  if (runtimeDiagnostics.value.length > 30) {
    runtimeDiagnostics.value = runtimeDiagnostics.value.slice(0, 30)
  }
}

const isExpanded = (userId) => expandedUserIds.value.includes(Number(userId))

const handleExpandChange = (row, expandedRows) => {
  expandedUserIds.value = (expandedRows || []).map(item => Number(item?.user_id)).filter(Number.isFinite)
  pushRuntimeLog(
    'expand-change',
    `user_id=${row?.user_id ?? 'unknown'}, expandedCount=${(expandedRows || []).length}, taskCount=${(row?.tasks || []).length}`
  )
}

const handleRowClickDebug = (row, column) => {
  pushRuntimeLog('row-click', `user_id=${row?.user_id ?? 'unknown'}, column=${column?.label || column?.type || 'unknown'}`)
}

const toggleExpand = (row) => {
  try {
    if (!workloadTableRef.value || !row) return
    const target = Number(row.user_id)
    const expanded = isExpanded(target)
    workloadTableRef.value.toggleRowExpansion(row, !expanded)
    pushRuntimeLog('toggleExpand', `user_id=${target}, next=${!expanded}`)
  } catch (error) {
    pushRuntimeLog('toggleExpand-error', formatError(error))
  }
}

const clearDiagnostics = () => {
  runtimeDiagnostics.value = []
}

const onGlobalError = (event) => {
  const err = event?.error || event?.message || event
  pushRuntimeLog('window.error', formatError(err))
}

const onUnhandledRejection = (event) => {
  pushRuntimeLog('unhandledrejection', formatError(event?.reason || event))
}

onErrorCaptured((error, _instance, info) => {
  pushRuntimeLog('vue.errorCaptured', `${info || 'no-info'}\n${formatError(error)}`)
  return false
})

const viewMemberDetail = (userId) => {
  router.push({ path: `/personnel/${userId}` })
}

const loadData = async () => {
  try {
    const [memberData, workloadData] = await Promise.all([getMembers(), getWorkload()])
    members.value = memberData
    workload.value = workloadData
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || DT.toast.loadFailed)
  }
}

const openAllocationDialog = async (task) => {
  try {
    const detail = await getTaskAllocations(task.id)
    allocationTask.value = {
      test_id: detail.test_id,
      test_name: detail.test_name,
      total_estimated_hours: detail.total_estimated_hours
    }
    allocationRows.value = (detail.allocations || []).map(item => ({
      user_id: item.user_id,
      allocated_hours: Number(item.allocated_hours || 0),
      part_description: item.part_description || ''
    }))
    if (!allocationRows.value.length) {
      allocationRows.value.push({ user_id: null, allocated_hours: 0, part_description: '' })
    }
    showAllocationDialog.value = true
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || DT.toast.loadTaskAllocationsFailed)
  }
}

const addAllocationRow = () => {
  allocationRows.value.push({ user_id: null, allocated_hours: 0, part_description: '' })
}

const removeAllocationRow = (index) => {
  allocationRows.value.splice(index, 1)
  if (!allocationRows.value.length) {
    allocationRows.value.push({ user_id: null, allocated_hours: 0, part_description: '' })
  }
}

const saveAllocation = async () => {
  if (!allocationTask.value.test_id) return

  const normalized = allocationRows.value
    .filter(item => item.user_id && Number(item.allocated_hours || 0) > 0)
    .map(item => ({
      user_id: Number(item.user_id),
      allocated_hours: Number(item.allocated_hours || 0),
      part_description: (item.part_description || '').trim()
    }))

  const userIds = normalized.map(item => item.user_id)
  if (new Set(userIds).size !== userIds.length) {
    ElMessage.warning(DT.toast.duplicateTester)
    return
  }

  savingAllocation.value = true
  try {
    await updateTaskAllocations(allocationTask.value.test_id, { allocations: normalized })
    ElMessage.success(DT.toast.saveSuccess)
    showAllocationDialog.value = false
    await loadData()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || DT.toast.saveFailed)
  } finally {
    savingAllocation.value = false
  }
}

onMounted(() => {
  window.addEventListener('error', onGlobalError)
  window.addEventListener('unhandledrejection', onUnhandledRejection)
  loadData()
})

onBeforeUnmount(() => {
  window.removeEventListener('error', onGlobalError)
  window.removeEventListener('unhandledrejection', onUnhandledRejection)
})
</script>

<style scoped>
.personnel-container {
  width: 100%;
}

.full-width-table {
  width: 100%;
}

.personnel-container :deep(.full-width-table .el-table__inner-wrapper) {
  width: 100% !important;
}

.personnel-container :deep(.full-width-table .el-scrollbar__view) {
  width: 100% !important;
}

.member-task-grid {
  margin: 10px 0;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 12px;
  overflow: hidden;
}

.member-task-grid__head,
.member-task-grid__row {
  display: grid;
  grid-template-columns: 2.1fr 1.5fr 1fr 1fr 0.9fr 0.8fr 0.9fr 0.9fr;
  gap: 0;
}

.member-task-grid__head--readonly,
.member-task-grid__row--readonly {
  grid-template-columns: 2.2fr 1.6fr 1fr 1fr 0.9fr 0.8fr 0.9fr;
}

.member-task-grid__head {
  background: rgba(255, 255, 255, 0.04);
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
}

.member-task-grid__head > div {
  padding: 10px 8px;
  font-size: 12px;
  font-weight: 700;
  color: rgba(226, 232, 240, 0.9);
}

.member-task-grid__row {
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
}

.member-task-grid__row:last-child {
  border-bottom: none;
}

.member-task-grid__cell {
  padding: 10px 8px;
  font-size: 13px;
  color: rgba(226, 232, 240, 0.92);
  word-break: break-word;
}

.member-task-grid__cell--task {
  font-weight: 600;
}

.member-task-grid__cell--actions {
  display: flex;
  align-items: center;
}

.member-task-grid__empty {
  padding: 12px;
  color: rgba(148, 163, 184, 0.9);
  font-size: 13px;
}

.member-link {
  appearance: none;
  border: none;
  background: transparent;
  padding: 0;
  margin: 0;
  color: #7dd3fc;
  font-weight: 700;
  text-align: left;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.member-link:hover {
  color: #bae6fd;
}

.member-link:focus-visible {
  outline: 2px solid rgba(125, 211, 252, 0.7);
  outline-offset: 2px;
  border-radius: 4px;
}

.overlap-panel {
  width: 100%;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid rgba(148, 163, 184, 0.2);
}

.overlap-panel__title {
  font-size: 13px;
  margin-bottom: 8px;
  color: rgba(148, 163, 184, 0.92);
}

.allocation-summary {
  margin-bottom: 10px;
}

.allocation-toolbar {
  margin-top: 10px;
}

.runtime-card {
  margin-top: 16px;
}

.runtime-log-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 360px;
  overflow: auto;
}

.runtime-log-item {
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 10px;
  padding: 10px;
  background: rgba(15, 23, 42, 0.55);
}

.runtime-log-item__meta {
  font-size: 12px;
  color: rgba(148, 163, 184, 0.9);
  margin-bottom: 6px;
}

.runtime-log-item__content {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  color: rgba(226, 232, 240, 0.94);
  font-size: 12px;
  line-height: 1.5;
}
</style>

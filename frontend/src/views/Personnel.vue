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
        <div class="glass-pill">Test FR {{ totalTestTasks }}</div>
        <div class="glass-pill">Other Tasks {{ totalOtherTasks }}</div>
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

    <el-card v-if="canManagePersonnel" class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>Personnel Management</h3>
            <span class="section-title__meta">Only the admin account can create or delete users</span>
          </div>
          <div class="user-admin-actions">
            <el-button @click="loadManagementData">Refresh Users</el-button>
            <el-button type="primary" @click="openCreateUserDialog">New Member</el-button>
          </div>
        </div>
      </template>

      <el-table :data="managedUsers" stripe>
        <el-table-column prop="username" label="Username" min-width="160" />
        <el-table-column prop="display_name" label="Display Name" min-width="180" />
        <el-table-column prop="role" label="Role" min-width="120" />
        <el-table-column label="Status" min-width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? 'Active' : 'Inactive' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="140" fixed="right">
          <template #default="{ row }">
            <el-popconfirm title="Delete this user?" @confirm="handleDeleteUser(row)">
              <template #reference>
                <el-button type="danger" link>Delete</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

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
                <div>Current Task</div>
                <div>{{ LT.table.partDescription }}</div>
                <div>{{ LT.table.startDate }}</div>
                <div>{{ LT.table.endDate }}</div>
                <div>{{ LT.table.status }}</div>
                <div>{{ LT.table.progress }}</div>
                <div>{{ LT.table.allocatedManday }}</div>
                <div v-if="canCreateOrEditTest()">{{ LT.table.actions }}</div>
              </div>

              <div v-if="!getVisibleTaskRows(row).length" class="member-task-grid__empty">No tasks</div>

              <template v-for="group in getTaskGroups(row)" :key="group.key">
                <div v-if="group.tasks.length" class="member-task-group-title">{{ group.label }}</div>
                <div
                  v-for="task in group.tasks"
                  :key="task._row_key"
                  class="member-task-grid__row"
                  :class="{ 'member-task-grid__row--readonly': !canCreateOrEditTest() }"
                >
                  <div class="member-task-grid__cell member-task-grid__cell--task" :title="formatTaskName(task)">{{ formatTaskName(task) }}</div>
                  <div class="member-task-grid__cell" :title="getPartDescription(task)">{{ getPartDescription(task) }}</div>
                  <div class="member-task-grid__cell">{{ formatDate(task.start_date) }}</div>
                  <div class="member-task-grid__cell">{{ formatDate(task.end_date) }}</div>
                  <div class="member-task-grid__cell">
                    <el-tag size="small" :type="getTaskStatusTagType(task.status)">{{ getTaskStatusText(task.status) }}</el-tag>
                  </div>
                  <div class="member-task-grid__cell">{{ formatProgress(task.progress) }}</div>
                  <div class="member-task-grid__cell">{{ formatManday(task.estimated_hours) }}</div>
                  <div v-if="canCreateOrEditTest()" class="member-task-grid__cell member-task-grid__cell--actions">
                    <el-button v-if="task.task_kind === 'test'" size="small" @click="openAllocationDialog(task)">{{ BT.allocateManday }}</el-button>
                  </div>
                </div>
              </template>
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
        <el-table-column :label="LT.table.taskCount" min-width="180">
          <template #default="{ row }">
            <div>{{ row.task_count }}</div>
            <div class="task-count-breakdown">FR {{ row.test_task_count || 0 }} / Other {{ row.other_task_count || 0 }}</div>
          </template>
        </el-table-column>
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

    <el-dialog v-model="showCreateUserDialog" title="Create Member" width="620px">
      <el-form :model="createUserForm" label-width="120px">
        <el-form-item label="Username">
          <el-input v-model="createUserForm.username" maxlength="64" show-word-limit />
        </el-form-item>
        <el-form-item label="Display Name">
          <el-input v-model="createUserForm.display_name" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="Password">
          <el-input v-model="createUserForm.password" type="password" show-password maxlength="100" />
        </el-form-item>
        <el-form-item label="Role">
          <el-select v-model="createUserForm.role" style="width: 100%">
            <el-option label="Viewer" value="viewer" />
            <el-option label="Manager" value="manager" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateUserDialog = false">Cancel</el-button>
        <el-button type="primary" :loading="savingUser" @click="handleCreateUser">Create</el-button>
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
import { formatDate, formatManday as formatMandayValue, formatPercent } from '../utils/formatters'
import { getTaskStatusTagType, getTaskStatusText } from '../utils/taskStatus'
import { formatTaskLabel } from '../utils/taskDisplay'
import {
  getMembers,
  getWorkload,
  getTaskAllocations,
  updateTaskAllocations,
  getUsers,
  createUser,
  deleteUser
} from '../api/personnel'
import { canCreateOrEditTest, canManagePersonnelUsers } from '../stores/auth'

const router = useRouter()
const LT = LabelText.personnel
const BT = ButtonText.personnel
const BTCommon = ButtonText.common
const DT = DescriptionText.personnel
const members = ref([])
const workload = ref([])
const workloadTableRef = ref(null)
const expandedUserIds = ref([])
const managedUsers = ref([])

const showAllocationDialog = ref(false)
const savingAllocation = ref(false)
const showCreateUserDialog = ref(false)
const savingUser = ref(false)
const createUserForm = ref({
  username: '',
  display_name: '',
  password: '123456',
  role: 'viewer'
})

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

const totalTestTasks = computed(() => {
  return workload.value.reduce((sum, item) => sum + Number(item.test_task_count || 0), 0)
})

const totalOtherTasks = computed(() => {
  return workload.value.reduce((sum, item) => sum + Number(item.other_task_count || 0), 0)
})

const totalOverlaps = computed(() => {
  return workload.value.reduce((sum, item) => sum + Number(item.overlap_count || 0), 0)
})

const canManagePersonnel = computed(() => canManagePersonnelUsers())

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

const formatProgress = (value) => {
  return formatPercent(value)
}

const formatManday = (value) => {
  return formatMandayValue(value)
}

const getPartDescription = (task) => {
  const text = String(task?.part_description || '').trim()
  if (text) return text
  return DT?.fallback?.unassignedPart || '-'
}

const formatTaskName = (task) => {
  return formatTaskLabel(task)
}

const normalizeTaskRows = (tasks) => {
  try {
    if (!Array.isArray(tasks)) return []
    return tasks.map((task, index) => ({
      ...task,
      _row_key: `${task?.task_kind || 'test'}-${task?.id ?? 'na'}-${index}`
    }))
  } catch (_error) {
    return []
  }
}

const toDateTime = (value, endOfDay = false) => {
  if (!value) return null
  const normalized = typeof value === 'string' && value.length <= 10
    ? `${value}${endOfDay ? 'T23:59:59' : 'T00:00:00'}`
    : value
  const date = new Date(normalized)
  return Number.isNaN(date.getTime()) ? null : date
}

const isTaskVisibleInPersonnelList = (task) => {
  const now = new Date()
  const windowStart = new Date(now)
  windowStart.setDate(windowStart.getDate() - 14)
  windowStart.setHours(0, 0, 0, 0)

  const windowEnd = new Date(now)
  windowEnd.setDate(windowEnd.getDate() + 14)
  windowEnd.setHours(23, 59, 59, 999)

  const startDate = toDateTime(task?.start_date || task?.period_start, false)
  const endDate = toDateTime(task?.end_date || task?.period_end || task?.start_date || task?.period_start, true)

  const isOngoing = startDate && endDate && startDate <= now && endDate >= now
  const startsSoon = startDate && startDate >= windowStart && startDate <= windowEnd
  const endsSoon = endDate && endDate >= windowStart && endDate <= windowEnd

  return Boolean(isOngoing || startsSoon || endsSoon)
}

const getVisibleTaskRows = (row) => {
  const normalized = normalizeTaskRows(row?.tasks)
  return normalized
    .filter(isTaskVisibleInPersonnelList)
    .sort((first, second) => {
      const firstStart = first?.start_date || first?.period_start || '9999-12-31'
      const secondStart = second?.start_date || second?.period_start || '9999-12-31'
      if (firstStart !== secondStart) return String(firstStart).localeCompare(String(secondStart))
      return String(first?.task_label || first?.test_name || '').localeCompare(String(second?.task_label || second?.test_name || ''))
    })
}

const getTaskGroups = (row) => {
  const visibleTasks = getVisibleTaskRows(row)
  return [
    {
      key: 'test',
      label: 'Test FR',
      tasks: visibleTasks.filter(task => task.task_kind === 'test')
    },
    {
      key: 'other',
      label: 'Other Tasks',
      tasks: visibleTasks.filter(task => task.task_kind !== 'test')
    }
  ]
}

const isExpanded = (userId) => expandedUserIds.value.includes(Number(userId))

const handleExpandChange = (_row, expandedRows) => {
  expandedUserIds.value = (expandedRows || []).map(item => Number(item?.user_id)).filter(Number.isFinite)
}

const handleRowClickDebug = () => {}

const toggleExpand = (row) => {
  if (!workloadTableRef.value || !row) return
  const target = Number(row.user_id)
  const expanded = isExpanded(target)
  workloadTableRef.value.toggleRowExpansion(row, !expanded)
}

const viewMemberDetail = (userId) => {
  router.push({ path: `/personnel/${userId}` })
}

const resetCreateUserForm = () => {
  createUserForm.value = {
    username: '',
    display_name: '',
    password: '123456',
    role: 'viewer'
  }
}

const loadManagementData = async () => {
  if (!canManagePersonnel.value) return
  try {
    const users = await getUsers()
    managedUsers.value = users
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to load personnel management data')
  }
}

const openCreateUserDialog = () => {
  resetCreateUserForm()
  showCreateUserDialog.value = true
}

const handleCreateUser = async () => {
  const username = (createUserForm.value.username || '').trim()
  const password = String(createUserForm.value.password || '')
  if (!username) {
    ElMessage.warning('Username is required')
    return
  }
  if (password.length < 6) {
    ElMessage.warning('Password must be at least 6 characters')
    return
  }

  savingUser.value = true
  try {
    await createUser({
      username,
      display_name: (createUserForm.value.display_name || '').trim() || username,
      password,
      role: createUserForm.value.role || 'viewer',
      is_active: true
    })
    ElMessage.success('User created successfully')
    showCreateUserDialog.value = false
    await loadData()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to create user')
  } finally {
    savingUser.value = false
  }
}

const handleDeleteUser = async (user) => {
  const userId = Number(user?.id)
  if (!userId) return
  try {
    await deleteUser(userId)
    ElMessage.success('User deleted successfully')
    await loadData()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to delete user')
  }
}

const loadData = async () => {
  try {
    const [memberData, workloadData] = await Promise.all([getMembers(), getWorkload()])
    members.value = memberData
    workload.value = workloadData
    if (canManagePersonnel.value) {
      await loadManagementData()
    } else {
      managedUsers.value = []
    }
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
  loadData()
})

onBeforeUnmount(() => {})
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

.member-task-group-title {
  padding: 10px 12px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: rgba(125, 211, 252, 0.96);
  background: rgba(59, 130, 246, 0.08);
  border-top: 1px solid rgba(148, 163, 184, 0.12);
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

.task-count-breakdown {
  margin-top: 4px;
  font-size: 12px;
  color: rgba(148, 163, 184, 0.9);
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

.user-admin-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}


</style>

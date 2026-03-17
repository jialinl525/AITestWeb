<template>
  <div class="page-shell personnel-container">
    <section class="page-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">People Dashboard</div>
        <h2 class="page-hero__title">Personnel Task and Manday Dashboard</h2>
        <p class="page-hero__desc">
          Personnel data is injected by the backend. This page focuses on task completion, manday allocation,
          and overlap risk across the L0 to L4 time window.
        </p>
      </div>
      <div class="page-hero__actions">
        <div class="glass-pill">Members {{ members.length }}</div>
        <div class="glass-pill">Tasks {{ totalTasks }}</div>
        <div class="glass-pill">Mandays {{ totalHours }} manday</div>
        <div class="glass-pill">Overlaps {{ totalOverlaps }}</div>
        <el-button @click="loadData">Refresh</el-button>
      </div>
    </section>

    <div class="metrics-grid">
      <article class="metric-card accent-blue">
        <div class="metric-card__label">Members</div>
        <div class="metric-card__value">{{ members.length }}</div>
        <div class="metric-card__meta">Active test members</div>
      </article>
      <article class="metric-card accent-green">
        <div class="metric-card__label">Avg. Tasks per Member</div>
        <div class="metric-card__value">{{ averageTasks }}</div>
        <div class="metric-card__meta">Average based on current members</div>
      </article>
      <article class="metric-card accent-orange">
        <div class="metric-card__label">Total Allocated Mandays</div>
        <div class="metric-card__value">{{ totalHours }} manday</div>
        <div class="metric-card__meta">Summed from task manday allocations</div>
      </article>
      <article class="metric-card accent-red">
        <div class="metric-card__label">Overlap Groups</div>
        <div class="metric-card__value">{{ totalOverlaps }}</div>
        <div class="metric-card__meta">Overlapping pairs in the L0-L4 window</div>
      </article>
    </div>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>Task Completion and Manday Allocation by Member</h3>
            <span class="section-title__meta">Expand to view task details and overlap information</span>
          </div>
        </div>
      </template>

      <el-table :data="workload" stripe class="full-width-table" style="width: 100%" :fit="true" table-layout="auto">
        <el-table-column type="expand">
          <template #default="{ row }">
            <el-table :data="row.tasks" size="small" stripe class="inner-task-table full-width-table" style="width: 100%" :fit="true" table-layout="auto">
              <el-table-column prop="fr_number" label="FR" min-width="120" />
              <el-table-column prop="test_name" label="Task" min-width="220" />
              <el-table-column prop="part_description" label="Part Description" min-width="260" show-overflow-tooltip>
                <template #default="{ row: task }">{{ task.part_description || '-' }}</template>
              </el-table-column>
              <el-table-column label="L0-L4 Range" min-width="220">
                <template #default="{ row: task }">{{ formatDateRange(task.period_start, task.period_end) }}</template>
              </el-table-column>
              <el-table-column label="L0/L2/L4 Dates" min-width="260">
                <template #default="{ row: task }">{{ formatStageDates(task) }}</template>
              </el-table-column>
              <el-table-column prop="status" label="Status" min-width="120" />
              <el-table-column prop="progress" label="Progress" min-width="120">
                <template #default="{ row: task }">{{ Number(task.progress || 0).toFixed(0) }}%</template>
              </el-table-column>
              <el-table-column prop="estimated_hours" label="Allocated Manday" min-width="140">
                <template #default="{ row: task }">{{ Number(task.estimated_hours || 0).toFixed(1) }} manday</template>
              </el-table-column>
              <el-table-column v-if="canCreateOrEditTest()" label="Actions" min-width="120">
                <template #default="{ row: task }">
                  <el-button size="small" @click="openAllocationDialog(task)">Allocate Manday</el-button>
                </template>
              </el-table-column>
            </el-table>

            <div class="overlap-panel">
              <div class="overlap-panel__title">Date Overlaps (L0 to L4 Window)</div>
              <div v-if="!row.overlap_count" class="muted-text">No overlaps</div>
              <el-table v-else :data="row.overlaps" size="small" stripe class="full-width-table" style="width: 100%" :fit="true" table-layout="auto">
                <el-table-column label="Task A" min-width="160">
                  <template #default="{ row: overlap }">{{ overlap.task_name_1 }} (#{{ overlap.task_id_1 }})</template>
                </el-table-column>
                <el-table-column label="Task B" min-width="160">
                  <template #default="{ row: overlap }">{{ overlap.task_name_2 }} (#{{ overlap.task_id_2 }})</template>
                </el-table-column>
                <el-table-column label="Overlap Range" min-width="180">
                  <template #default="{ row: overlap }">{{ formatDateRange(overlap.overlap_start, overlap.overlap_end) }}</template>
                </el-table-column>
                <el-table-column label="Overlap Days" min-width="100">
                  <template #default="{ row: overlap }">{{ overlap.overlap_days }}</template>
                </el-table-column>
              </el-table>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="display_name" label="Member" min-width="200" />
        <el-table-column prop="username" label="Username" min-width="180" />
        <el-table-column prop="task_count" label="Task Count" min-width="120" />
        <el-table-column label="Completed Tasks" min-width="120">
          <template #default="{ row }">{{ getCompletedTasks(row) }}</template>
        </el-table-column>
        <el-table-column prop="overlap_count" label="Overlap Groups" min-width="130">
          <template #default="{ row }">
            <el-tag :type="getOverlapTagType(row.overlap_count)">{{ row.overlap_count || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_estimated_hours" label="Allocated Manday" min-width="140">
          <template #default="{ row }">{{ Number(row.total_estimated_hours || 0).toFixed(1) }} manday</template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showAllocationDialog" :title="`Task Manday Allocation - ${allocationTask.test_name || ''}`" width="980px">
      <div class="muted-text allocation-summary">Total Task Manday: {{ Number(allocationTask.total_estimated_hours || 0).toFixed(1) }} manday</div>
      <el-table :data="allocationRows" size="small" stripe>
        <el-table-column label="Tester" min-width="260">
          <template #default="{ row: item }">
            <el-select v-model="item.user_id" filterable style="width: 100%" placeholder="Select a member">
              <el-option
                v-for="member in members"
                :key="member.id"
                :label="member.display_name || member.username"
                :value="member.id"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="Allocated Manday" width="180">
          <template #default="{ row: item }">
            <el-input-number v-model="item.allocated_hours" :min="0" :step="0.5" :precision="1" style="width: 140px" />
          </template>
        </el-table-column>
        <el-table-column label="Part Description" min-width="300">
          <template #default="{ row: item }">
            <el-input
              v-model="item.part_description"
              type="textarea"
              :rows="2"
              resize="none"
              maxlength="300"
              show-word-limit
              placeholder="Example: login module regression + API smoke tests"
            />
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100">
          <template #default="{ $index }">
            <el-button type="danger" link @click="removeAllocationRow($index)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="allocation-toolbar">
        <el-button @click="addAllocationRow">Add Allocation Row</el-button>
      </div>
      <template #footer>
        <el-button @click="showAllocationDialog = false">Cancel</el-button>
        <el-button type="primary" :loading="savingAllocation" @click="saveAllocation">Save Manday Allocation</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  getMembers,
  getWorkload,
  getTaskAllocations,
  updateTaskAllocations
} from '../api/personnel'
import { canCreateOrEditTest } from '../stores/auth'

const members = ref([])
const workload = ref([])

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
    ;(item.tasks || []).forEach(task => taskIds.add(task.id))
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
  return (row.tasks || []).filter(task => task.status === 'completed').length
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

const formatDateRange = (start, end) => {
  if (!start && !end) return '-'
  if (!start || !end) return `${formatDate(start || end)}`
  return `${formatDate(start)} ~ ${formatDate(end)}`
}

const formatStageDates = (task) => {
  return `L0 ${formatDate(task.l0_due_date)} / L2 ${formatDate(task.l2_due_date)} / L4 ${formatDate(task.l4_due_date)}`
}

const loadData = async () => {
  try {
    const [memberData, workloadData] = await Promise.all([getMembers(), getWorkload()])
    members.value = memberData
    workload.value = workloadData
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to load personnel data')
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
    ElMessage.error(error?.response?.data?.detail || 'Failed to load task allocations')
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
    ElMessage.warning('The same tester cannot be assigned more than once')
    return
  }

  savingAllocation.value = true
  try {
    await updateTaskAllocations(allocationTask.value.test_id, { allocations: normalized })
    ElMessage.success('Manday allocation updated')
    showAllocationDialog.value = false
    await loadData()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to save allocation')
  } finally {
    savingAllocation.value = false
  }
}

onMounted(() => {
  loadData()
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

.inner-task-table {
  margin: 10px 0;
  width: 100%;
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
</style>

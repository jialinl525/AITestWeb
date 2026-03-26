<template>
  <div class="page-shell personnel-container">
    <section class="page-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">{{ LT.heroEyebrow }}</div>
        <h2 class="page-hero__title">{{ LT.heroTitle }}</h2>
        <p class="page-hero__desc">{{ DT.hero }}</p>
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
      <MetricCard :label="LT.metrics.members" :value="members.length" :meta="DT.metricsMeta.members" accent="blue" />
      <MetricCard :label="LT.metrics.avgTasks" :value="averageTasks" :meta="DT.metricsMeta.avgTasks" accent="green" />
      <MetricCard :label="LT.metrics.totalManday" :value="`${totalHours} manday`" :meta="DT.metricsMeta.totalManday" accent="orange" />
      <MetricCard :label="LT.metrics.overlapGroups" :value="totalOverlaps" :meta="DT.metricsMeta.overlapGroups" accent="red" />
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
      <PersonnelWorkloadTable
        :workload="workload"
        :can-edit="canCreateOrEditTest()"
        @view-member="viewMemberDetail"
        @open-allocation="openAllocationDialog"
      />
    </el-card>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>Task Timeline</h3>
            <span class="section-title__meta">Bar height ∝ allocated manday</span>
          </div>
        </div>
      </template>
      <PersonnelGanttChart
        :workload="workload"
        :view-mode="ganttViewMode"
        @update:view-mode="ganttViewMode = $event"
        @view-member="viewMemberDetail"
      />
    </el-card>

    <PersonnelAllocationDialog
      v-model="showAllocationDialog"
      :task="allocationTask"
      :rows="allocationRows"
      :members="members"
      :saving="savingAllocation"
      @save="saveAllocation"
      @add-row="addAllocationRow"
      @remove-row="removeAllocationRow"
    />

    <PersonnelCreateUserDialog
      v-model="showCreateUserDialog"
      :form="createUserForm"
      :saving="savingUser"
      @save="handleCreateUser"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import MetricCard from '../components/common/MetricCard.vue'
import PersonnelWorkloadTable from '../components/personnel/PersonnelWorkloadTable.vue'
import PersonnelGanttChart from '../components/personnel/PersonnelGanttChart.vue'
import PersonnelAllocationDialog from '../components/personnel/PersonnelAllocationDialog.vue'
import PersonnelCreateUserDialog from '../components/personnel/PersonnelCreateUserDialog.vue'
import { LabelText } from '../texts/LabelText'
import { ButtonText } from '../texts/ButtonText'
import { DescriptionText } from '../texts/DescriptionText'
import {
  getMembers, getWorkload, getTaskAllocations, updateTaskAllocations,
  getUsers, createUser, deleteUser
} from '../api/personnel'
import { canCreateOrEditTest, canManagePersonnelUsers } from '../stores/auth'

const router = useRouter()
const LT = LabelText.personnel
const BTCommon = ButtonText.common
const DT = DescriptionText.personnel

const members = ref([])
const workload = ref([])
const managedUsers = ref([])
const ganttViewMode = ref('active')

const showAllocationDialog = ref(false)
const savingAllocation = ref(false)
const showCreateUserDialog = ref(false)
const savingUser = ref(false)

const createUserForm = ref({ username: '', display_name: '', password: '123456', role: 'viewer' })
const allocationTask = ref({ test_id: null, test_name: '', total_estimated_hours: 0 })
const allocationRows = ref([])

const canManagePersonnel = computed(() => canManagePersonnelUsers())

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

const totalTestTasks = computed(() =>
  workload.value.reduce((sum, item) => sum + Number(item.test_task_count || 0), 0)
)

const totalOtherTasks = computed(() =>
  workload.value.reduce((sum, item) => sum + Number(item.other_task_count || 0), 0)
)

const totalOverlaps = computed(() =>
  workload.value.reduce((sum, item) => sum + Number(item.overlap_count || 0), 0)
)

const averageTasks = computed(() => {
  if (!members.value.length) return 0
  const sum = workload.value.reduce((acc, item) => acc + Number(item.task_count || 0), 0)
  return Number((sum / members.value.length).toFixed(1))
})

const viewMemberDetail = (userId) => router.push({ path: `/personnel/${userId}` })

const loadManagementData = async () => {
  if (!canManagePersonnel.value) return
  try {
    managedUsers.value = await getUsers()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to load personnel management data')
  }
}

const openCreateUserDialog = () => {
  createUserForm.value = { username: '', display_name: '', password: '123456', role: 'viewer' }
  showCreateUserDialog.value = true
}

const handleCreateUser = async () => {
  const username = (createUserForm.value.username || '').trim()
  const password = String(createUserForm.value.password || '')
  if (!username) { ElMessage.warning('Username is required'); return }
  if (password.length < 6) { ElMessage.warning('Password must be at least 6 characters'); return }
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

onMounted(() => { loadData() })
</script>

<style scoped>
.personnel-container { width: 100%; }
.user-admin-actions { display: flex; align-items: center; gap: 8px; }
</style>

<template>
  <div class="page-shell detail-container">
    <section class="page-hero detail-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">{{ LT.heroEyebrow }}</div>
        <h2 class="page-hero__title">{{ LT.heroTitle }}</h2>
        <p class="page-hero__desc">{{ DT.hero }}</p>
      </div>
      <div class="page-hero__actions">
        <el-button v-if="canEditPersonnelProfile() && memberDetail" type="primary" @click="openProfileEditDialog">
          Edit Profile
        </el-button>
        <el-button @click="goBack">{{ BT.backToList }}</el-button>
      </div>
    </section>

    <el-card v-loading="loading" class="section-card detail-card">
      <template v-if="memberDetail">
        <div class="detail-header">
          <div>
            <h2>{{ memberDetail.display_name }}</h2>
            <p class="detail-subtitle">{{ LT.profile.username }}: {{ memberDetail.username }}</p>
            <p class="detail-subtitle">{{ LT.profile.email }}: {{ memberDetail.email || '-' }}</p>
          </div>
        </div>

        <div class="metrics-grid detail-metrics">
          <article class="metric-card accent-blue">
            <div class="metric-card__label">{{ LT.metrics.taskCount }}</div>
            <div class="metric-card__value">{{ memberDetail.task_count || 0 }}</div>
          </article>
          <article class="metric-card accent-green">
            <div class="metric-card__label">{{ LT.metrics.completedTasks }}</div>
            <div class="metric-card__value">{{ completedTasks }}</div>
          </article>
          <article class="metric-card accent-red">
            <div class="metric-card__label">{{ LT.metrics.overlapGroups }}</div>
            <div class="metric-card__value">{{ memberDetail.overlap_count || 0 }}</div>
          </article>
          <article class="metric-card accent-purple">
            <div class="metric-card__label">{{ LT.metrics.totalManday }}</div>
            <div class="metric-card__value">{{ formatManday(memberDetail.total_estimated_hours) }}</div>
          </article>
        </div>

        <el-card class="section-card detail-inner-card">
          <template #header>
            <div class="section-title">
              <div class="section-title__main">
                <h3>{{ LT.section.profile }}</h3>
                <span class="section-title__meta">{{ DT.sectionMeta.profile }}</span>
              </div>
            </div>
          </template>
          <el-descriptions :column="1" border class="detail-info detail-info--ratio">
            <el-descriptions-item :label="LT.profile.displayName">{{ memberDetail.display_name || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="LT.profile.username">{{ memberDetail.username || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="LT.profile.email">{{ memberDetail.email || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="LT.metrics.overlapGroups">{{ memberDetail.overlap_count || 0 }}</el-descriptions-item>
            <el-descriptions-item :label="LT.profile.responsibilities">
              <div class="profile-multiline">{{ memberDetail.responsibilities || '-' }}</div>
            </el-descriptions-item>
            <el-descriptions-item :label="LT.profile.specialtyTasks">
              <div class="profile-multiline">{{ memberDetail.specialty_tasks || '-' }}</div>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="section-card detail-inner-card">
          <template #header>
            <div class="section-title">
              <div class="section-title__main">
                <h3>{{ LT.section.tasks }}</h3>
                <span class="section-title__meta">{{ DT.sectionMeta.tasks }}</span>
              </div>
            </div>
          </template>

          <el-table :data="memberDetail.tasks || []" :row-key="taskRowKey" stripe>
            <el-table-column :label="LTP.table.task" min-width="280" show-overflow-tooltip>
              <template #default="{ row }">
                <button type="button" class="task-link" @click="goToTask(row)">{{ formatTaskName(row) }}</button>
              </template>
            </el-table-column>
            <el-table-column prop="part_description" :label="LTP.table.partDescription" min-width="220" show-overflow-tooltip>
              <template #default="{ row }">{{ row.part_description || DT.fallback.unassignedPart }}</template>
            </el-table-column>
            <el-table-column :label="LTP.table.startDate" min-width="140">
              <template #default="{ row }">{{ formatDate(row.start_date) }}</template>
            </el-table-column>
            <el-table-column :label="LTP.table.endDate" min-width="140">
              <template #default="{ row }">{{ formatDate(row.end_date) }}</template>
            </el-table-column>
            <el-table-column prop="status" :label="LTP.table.status" min-width="120" />
            <el-table-column prop="progress" :label="LTP.table.progress" min-width="120">
              <template #default="{ row }">{{ formatPercent(row.progress) }}</template>
            </el-table-column>
            <el-table-column prop="estimated_hours" :label="LTP.table.allocatedManday" min-width="130">
              <template #default="{ row }">{{ formatManday(row.estimated_hours) }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </template>
    </el-card>

    <el-dialog v-model="showProfileEditDialog" title="Edit Member Profile" width="640px">
      <el-form :model="profileForm" label-width="150px">
        <el-form-item :label="LT.profile.displayName">
          <el-input v-model="profileForm.display_name" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item :label="LT.profile.email">
          <el-input v-model="profileForm.email" maxlength="120" show-word-limit />
        </el-form-item>
        <el-form-item :label="LT.profile.responsibilities">
          <el-input
            v-model="profileForm.responsibilities"
            type="textarea"
            :rows="4"
            resize="none"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
        <el-form-item :label="LT.profile.specialtyTasks">
          <el-input
            v-model="profileForm.specialty_tasks"
            type="textarea"
            :rows="4"
            resize="none"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showProfileEditDialog = false">Cancel</el-button>
        <el-button type="primary" :loading="savingProfile" @click="saveProfile">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getWorkloadByUser, updateUser } from '../api/personnel'
import { LabelText } from '../texts/LabelText'
import { ButtonText } from '../texts/ButtonText'
import { DescriptionText } from '../texts/DescriptionText'
import { canEditPersonnelProfile } from '../stores/auth'
import { formatDate, formatManday, formatPercent } from '../utils/formatters'
import { formatTaskLabel } from '../utils/taskDisplay'

const route = useRoute()
const router = useRouter()

const LT = LabelText.personnelDetail
const LTP = LabelText.personnel
const BT = ButtonText.personnel
const DT = DescriptionText.personnelDetail

const loading = ref(false)
const memberDetail = ref(null)
const showProfileEditDialog = ref(false)
const savingProfile = ref(false)
const profileForm = ref({
  display_name: '',
  email: '',
  responsibilities: '',
  specialty_tasks: ''
})

const completedTasks = computed(() => {
  return (memberDetail.value?.tasks || []).filter(task => String(task.status || '').toLowerCase() === 'completed').length
})

const formatTaskName = (task) => {
  return formatTaskLabel(task)
}

const taskRowKey = (task) => `${task?.task_kind || 'test'}-${task?.id || 'na'}`

const goBack = () => {
  router.push('/personnel')
}

const openProfileEditDialog = () => {
  if (!memberDetail.value) return
  profileForm.value = {
    display_name: memberDetail.value.display_name || '',
    email: memberDetail.value.email || '',
    responsibilities: memberDetail.value.responsibilities || '',
    specialty_tasks: memberDetail.value.specialty_tasks || ''
  }
  showProfileEditDialog.value = true
}

const saveProfile = async () => {
  if (!memberDetail.value?.user_id) return

  savingProfile.value = true
  try {
    const payload = {
      display_name: (profileForm.value.display_name || '').trim(),
      email: (profileForm.value.email || '').trim(),
      responsibilities: (profileForm.value.responsibilities || '').trim(),
      specialty_tasks: (profileForm.value.specialty_tasks || '').trim()
    }
    await updateUser(Number(memberDetail.value.user_id), payload)
    ElMessage.success('Member profile updated')
    showProfileEditDialog.value = false
    await loadDetail()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to update member profile')
  } finally {
    savingProfile.value = false
  }
}

const goToTask = (task) => {
  if (!task?.id) return
  if (task.task_kind === 'work_task') {
    router.push({ path: `/work-tasks/${task.id}` })
    return
  }
  router.push({ path: `/test-progress/${task.id}` })
}

const loadDetail = async () => {
  const userId = Number(route.params.id)
  if (!userId) return

  loading.value = true
  try {
    memberDetail.value = await getWorkloadByUser(userId)
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || DT.toast.loadFailed)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDetail()
})
</script>
<style scoped src="../styles/detail-shared.css"></style>

<style scoped>
.profile-multiline {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}

:deep(.detail-info--ratio .el-descriptions__table) {
  width: 100%;
  table-layout: fixed;
}

:deep(.detail-info--ratio .el-descriptions__label.is-bordered-label) {
  width: 25%;
}

:deep(.detail-info--ratio .el-descriptions__content.is-bordered-content) {
  width: 75%;
}
</style>

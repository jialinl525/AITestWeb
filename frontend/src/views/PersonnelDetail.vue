<template>
  <div class="page-shell detail-container">
    <section class="page-hero detail-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">{{ LT.heroEyebrow }}</div>
        <h2 class="page-hero__title">{{ LT.heroTitle }}</h2>
        <p class="page-hero__desc">{{ DT.hero }}</p>
      </div>
      <div class="page-hero__actions">
        <el-button @click="goBack">{{ BT.backToList }}</el-button>
      </div>
    </section>

    <el-card v-loading="loading" class="section-card detail-card">
      <template v-if="memberDetail">
        <div class="detail-header">
          <div>
            <h2>{{ memberDetail.display_name }}</h2>
            <p class="detail-subtitle">{{ LT.profile.username }}: {{ memberDetail.username }}</p>
          </div>
          <div class="inline-stats">
            <div class="glass-pill">{{ LT.profile.editable }}: {{ memberDetail.can_edit_test ? 'Yes' : 'No' }}</div>
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
            <div class="metric-card__value">{{ Number(memberDetail.total_estimated_hours || 0).toFixed(1) }} manday</div>
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
          <el-descriptions :column="2" border class="detail-info">
            <el-descriptions-item :label="LT.profile.displayName">{{ memberDetail.display_name || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="LT.profile.username">{{ memberDetail.username || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="LT.profile.editable">{{ memberDetail.can_edit_test ? 'Yes' : 'No' }}</el-descriptions-item>
            <el-descriptions-item :label="LT.metrics.overlapGroups">{{ memberDetail.overlap_count || 0 }}</el-descriptions-item>
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
              <template #default="{ row }">{{ Number(row.progress || 0).toFixed(0) }}%</template>
            </el-table-column>
            <el-table-column prop="estimated_hours" :label="LTP.table.allocatedManday" min-width="130">
              <template #default="{ row }">{{ Number(row.estimated_hours || 0).toFixed(1) }} manday</template>
            </el-table-column>
          </el-table>
        </el-card>
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getWorkloadByUser } from '../api/personnel'
import { LabelText } from '../texts/LabelText'
import { ButtonText } from '../texts/ButtonText'
import { DescriptionText } from '../texts/DescriptionText'

const route = useRoute()
const router = useRouter()

const LT = LabelText.personnelDetail
const LTP = LabelText.personnel
const BT = ButtonText.personnel
const DT = DescriptionText.personnelDetail

const loading = ref(false)
const memberDetail = ref(null)

const completedTasks = computed(() => {
  return (memberDetail.value?.tasks || []).filter(task => String(task.status || '').toLowerCase() === 'completed').length
})

const formatDate = (value) => {
  if (!value) return '-'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return '-'
  return d.toLocaleDateString('en-CA')
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

const taskRowKey = (task) => `${task?.task_kind || 'test'}-${task?.id || 'na'}`

const goBack = () => {
  router.push('/personnel')
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

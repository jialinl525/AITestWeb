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
      <template v-if="taskDetail">
        <div class="detail-header">
          <div>
            <h2>{{ taskDetail.task_name }}</h2>
            <p class="detail-subtitle">{{ taskDetail.task_summary || DT.fallback.noSummary }}</p>
          </div>
          <div class="inline-stats">
            <div class="glass-pill">{{ LT.metrics.status }}: {{ taskDetail.status || '-' }}</div>
            <div class="glass-pill">{{ LT.metrics.type }}: {{ taskDetail.task_type || '-' }}</div>
          </div>
        </div>

        <div class="metrics-grid detail-metrics">
          <article class="metric-card accent-green">
            <div class="metric-card__label">{{ LT.metrics.status }}</div>
            <div class="metric-card__value">{{ taskDetail.status || '-' }}</div>
          </article>
          <article class="metric-card accent-blue">
            <div class="metric-card__label">{{ LT.metrics.type }}</div>
            <div class="metric-card__value metric-card__value--small">{{ taskDetail.task_type || '-' }}</div>
          </article>
          <article class="metric-card accent-orange">
            <div class="metric-card__label">{{ LT.metrics.progress }}</div>
            <div class="metric-card__value">{{ Number(taskDetail.progress || 0).toFixed(0) }}%</div>
          </article>
          <article class="metric-card accent-purple">
            <div class="metric-card__label">{{ LT.metrics.assignee }}</div>
            <div class="metric-card__value metric-card__value--small">{{ taskDetail.assignee_display_name || DT.fallback.unassigned }}</div>
          </article>
          <article class="metric-card accent-orange">
            <div class="metric-card__label">{{ LT.metrics.estimatedManday }}</div>
            <div class="metric-card__value">{{ Number(taskDetail.estimated_hours || 0).toFixed(1) }} manday</div>
          </article>
        </div>

        <el-card class="section-card detail-inner-card">
          <template #header>
            <div class="section-title">
              <div class="section-title__main">
                <h3>{{ LT.section.basicInfo }}</h3>
                <span class="section-title__meta">{{ DT.sectionMeta.basicInfo }}</span>
              </div>
            </div>
          </template>
          <el-descriptions :column="2" border class="detail-info">
            <el-descriptions-item :label="LT.info.taskName">{{ taskDetail.task_name || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="LT.info.taskType">{{ taskDetail.task_type || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="LT.info.taskSummary">{{ taskDetail.task_summary || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="LT.info.status">{{ taskDetail.status || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="LT.info.progress">{{ Number(taskDetail.progress || 0).toFixed(0) }}%</el-descriptions-item>
            <el-descriptions-item :label="LT.info.estimatedManday">{{ Number(taskDetail.estimated_hours || 0).toFixed(1) }} manday</el-descriptions-item>
            <el-descriptions-item :label="LT.info.startDate">{{ formatDate(taskDetail.start_date) }}</el-descriptions-item>
            <el-descriptions-item :label="LT.info.endDate">{{ formatDate(taskDetail.end_date) }}</el-descriptions-item>
            <el-descriptions-item :label="LT.info.assignee">{{ taskDetail.assignee_display_name || DT.fallback.unassigned }}</el-descriptions-item>
            <el-descriptions-item :label="LT.info.createdAt">{{ formatDateTime(taskDetail.created_at) }}</el-descriptions-item>
            <el-descriptions-item :label="LT.info.updatedAt">{{ formatDateTime(taskDetail.updated_at) || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="section-card detail-inner-card">
          <template #header>
            <div class="section-title">
              <div class="section-title__main">
                <h3>{{ LT.section.detail }}</h3>
                <span class="section-title__meta">{{ DT.sectionMeta.detail }}</span>
              </div>
            </div>
          </template>
          <el-descriptions :column="1" border class="detail-info">
            <el-descriptions-item :label="LT.info.taskDetail">
              <div class="description-text">{{ taskDetail.task_detail || DT.fallback.noDetail }}</div>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getWorkTaskById } from '../api/workTasks'
import { LabelText } from '../texts/LabelText'
import { ButtonText } from '../texts/ButtonText'
import { DescriptionText } from '../texts/DescriptionText'
import { formatDate, formatDateTime } from '../utils/formatters'

const route = useRoute()
const router = useRouter()
const LT = LabelText.workTaskDetail
const BT = ButtonText.workTaskDetail
const DT = DescriptionText.workTaskDetail

const loading = ref(false)
const taskDetail = ref(null)

const loadDetail = async () => {
  const id = route.params.id
  if (!id) return
  loading.value = true
  try {
    taskDetail.value = await getWorkTaskById(id)
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || DT.toast.loadFailed)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/work-tasks')
}

onMounted(() => {
  loadDetail()
})
</script>
<style scoped src="../styles/detail-shared.css"></style>

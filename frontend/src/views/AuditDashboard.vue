<template>
  <div class="page-shell audit-page">
    <section class="page-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">{{ LT.heroEyebrow }}</div>
        <h2 class="page-hero__title">{{ LT.heroTitle }}</h2>
        <p class="page-hero__desc">{{ DT.hero }}</p>
      </div>
      <div class="page-hero__actions">
        <el-date-picker
          v-model="rangeDate"
          type="daterange"
          :start-placeholder="LT.filters.startDate"
          :end-placeholder="LT.filters.endDate"
          value-format="YYYY-MM-DD"
          unlink-panels
        />
        <el-button @click="refreshAll" :loading="loadingSummary">{{ BTCommon.refresh }}</el-button>
      </div>
    </section>

    <div class="metrics-grid">
      <article class="metric-card accent-blue">
        <div class="metric-card__label">{{ LT.metrics.totalAccess }}</div>
        <div class="metric-card__value">{{ selectedSummary.total_access }}</div>
        <div class="metric-card__meta">{{ LT.selectedDay }} {{ selectedDay }}</div>
      </article>
      <article class="metric-card accent-green">
        <div class="metric-card__label">{{ LT.metrics.uniqueIps }}</div>
        <div class="metric-card__value">{{ selectedSummary.unique_ips }}</div>
        <div class="metric-card__meta">{{ DT.metricsMeta.uniqueIps }}</div>
      </article>
      <article class="metric-card accent-orange">
        <div class="metric-card__label">{{ LT.metrics.loginSuccessRate }}</div>
        <div class="metric-card__value">{{ loginSuccessRate }}%</div>
        <div class="metric-card__meta">{{ LT.metrics.loginAttempts }} {{ selectedSummary.login_attempts }}</div>
      </article>
      <article class="metric-card accent-red">
        <div class="metric-card__label">{{ LT.metrics.managerWrites }}</div>
        <div class="metric-card__value">{{ selectedSummary.manager_write_actions }}</div>
        <div class="metric-card__meta">{{ DT.metricsMeta.managerWrites }}</div>
      </article>
    </div>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>{{ LT.section.dailyTrend }}</h3>
            <span class="section-title__meta">{{ DT.sectionMeta.dailyTrend }}</span>
          </div>
        </div>
      </template>
      <div class="daily-grid">
        <v-chart class="chart-panel" :option="dailyTrendOption" autoresize />
        <el-table :data="dailySummary" stripe height="320" @row-click="selectSummaryDay" class="full-width-table">
          <el-table-column prop="day" :label="LT.table.day" min-width="120" />
          <el-table-column prop="total_access" :label="LT.table.totalAccess" min-width="110" />
          <el-table-column prop="unique_ips" :label="LT.table.uniqueIps" min-width="95" />
          <el-table-column prop="login_attempts" :label="LT.table.logins" min-width="90" />
          <el-table-column prop="manager_write_actions" :label="LT.table.managerWrites" min-width="120" />
        </el-table>
      </div>
    </el-card>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>{{ LT.section.loginIpStats }}</h3>
            <span class="section-title__meta">{{ DT.sectionMeta.loginIpStats }}</span>
          </div>
        </div>
      </template>
      <div class="daily-grid">
        <v-chart class="chart-panel" :option="loginIpOption" autoresize />
        <el-table :data="loginIpStats" v-loading="loadingDetail" stripe height="320" class="full-width-table">
          <el-table-column prop="client_ip" :label="LT.table.clientIp" min-width="160" />
          <el-table-column prop="total_logins" :label="LT.table.loginAttempts" min-width="100" />
          <el-table-column prop="successful_logins" :label="LT.table.loginSuccess" min-width="100" />
          <el-table-column prop="failed_logins" :label="LT.table.loginFailed" min-width="100" />
        </el-table>
      </div>
    </el-card>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>{{ LT.section.accessTop }}</h3>
            <span class="section-title__meta">{{ DT.sectionMeta.accessTop }}</span>
          </div>
        </div>
      </template>
      <div class="daily-grid">
        <v-chart class="chart-panel" :option="accessTopOption" autoresize />
        <el-table :data="accessTop" v-loading="loadingDetail" stripe height="320" class="full-width-table">
          <el-table-column prop="method" :label="LT.table.method" min-width="90" />
          <el-table-column prop="path" :label="LT.table.path" min-width="260" show-overflow-tooltip />
          <el-table-column prop="access_count" :label="LT.table.accessCount" min-width="100" />
        </el-table>
      </div>
    </el-card>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>{{ LT.section.adminActions }}</h3>
            <span class="section-title__meta">{{ DT.sectionMeta.adminActions }}</span>
          </div>
          <div class="toolbar-panel">
            <el-input
              v-model="adminUserFilter"
              clearable
              style="width: 240px"
              :placeholder="LT.filters.adminUsername"
              @keyup.enter="refreshAdminActions"
            />
            <el-button @click="refreshAdminActions">{{ BTCommon.search }}</el-button>
          </div>
        </div>
      </template>
      <el-table :data="adminActionRows" v-loading="loadingActions" stripe class="full-width-table">
        <el-table-column prop="created_at" :label="LT.table.time" min-width="170" />
        <el-table-column prop="username" :label="LT.table.username" min-width="110" />
        <el-table-column prop="client_ip" :label="LT.table.clientIp" min-width="130" />
        <el-table-column prop="method" :label="LT.table.method" min-width="80" />
        <el-table-column prop="path" :label="LT.table.path" min-width="250" show-overflow-tooltip />
        <el-table-column prop="action_summary" :label="LT.table.action" min-width="160" show-overflow-tooltip />
        <el-table-column prop="status_code" :label="LT.table.status" min-width="90" />
        <el-table-column prop="action_payload" :label="LT.table.payload" min-width="300" show-overflow-tooltip />
      </el-table>
      <div class="audit-pagination">
        <el-pagination
          background
          layout="total, prev, pager, next, sizes"
          :total="adminActionTotal"
          :current-page="adminPage"
          :page-size="adminPageSize"
          :page-sizes="[20, 50, 100]"
          @current-change="handleAdminPageChange"
          @size-change="handleAdminPageSizeChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { LabelText } from '../texts/LabelText'
import { DescriptionText } from '../texts/DescriptionText'
import { ButtonText } from '../texts/ButtonText'
import { formatDateTime } from '../utils/formatters'
import {
  getAuditAccessTop,
  getAuditAdminActions,
  getAuditDailySummary,
  getAuditLoginIpStats,
} from '../api/audit'

const LT = LabelText.audit
const DT = DescriptionText.audit
const BTCommon = ButtonText.common

const loadingSummary = ref(false)
const loadingDetail = ref(false)
const loadingActions = ref(false)

const todayText = new Date().toISOString().slice(0, 10)
const rangeDate = ref([todayText, todayText])
const selectedDay = ref(todayText)

const dailySummary = ref([])
const loginIpStats = ref([])
const accessTop = ref([])

const adminUserFilter = ref('')
const adminActionRows = ref([])
const adminActionTotal = ref(0)
const adminPage = ref(1)
const adminPageSize = ref(20)

const selectedSummary = computed(() => {
  return dailySummary.value.find((item) => item.day === selectedDay.value) || {
    total_access: 0,
    unique_ips: 0,
    login_attempts: 0,
    login_success: 0,
    manager_write_actions: 0,
  }
})

const loginSuccessRate = computed(() => {
  const attempts = Number(selectedSummary.value.login_attempts || 0)
  const success = Number(selectedSummary.value.login_success || 0)
  if (!attempts) return 0
  return Math.round((success / attempts) * 10000) / 100
})

const dailyTrendOption = computed(() => {
  const labels = dailySummary.value.map((item) => item.day)
  return {
    tooltip: { trigger: 'axis' },
    legend: { data: [LT.chart.totalAccess, LT.chart.managerWrites] },
    grid: { left: 40, right: 20, top: 38, bottom: 40 },
    xAxis: { type: 'category', data: labels },
    yAxis: { type: 'value' },
    series: [
      {
        name: LT.chart.totalAccess,
        type: 'bar',
        data: dailySummary.value.map((item) => item.total_access),
        itemStyle: { color: '#60a5fa' },
      },
      {
        name: LT.chart.managerWrites,
        type: 'bar',
        data: dailySummary.value.map((item) => item.manager_write_actions),
        itemStyle: { color: '#fb7185' },
      },
    ],
  }
})

const loginIpOption = computed(() => {
  return {
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [
      {
        type: 'pie',
        radius: ['40%', '72%'],
        data: loginIpStats.value.map((item) => ({
          name: item.client_ip || LT.fallback.unknownIp,
          value: item.total_logins,
        })),
      },
    ],
  }
})

const accessTopOption = computed(() => {
  const top = accessTop.value.slice(0, 10)
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 20, bottom: 90 },
    xAxis: {
      type: 'category',
      data: top.map((item) => `${item.method} ${item.path}`),
      axisLabel: {
        rotate: 30,
        formatter: (value) => String(value || '').slice(0, 40),
      },
    },
    yAxis: { type: 'value' },
    series: [
      {
        type: 'bar',
        data: top.map((item) => item.access_count),
        itemStyle: { color: '#34d399' },
      },
    ],
  }
})

const formatActionRows = (rows) => {
  return (rows || []).map((item) => ({
    ...item,
    created_at: formatDateTime(item.created_at),
  }))
}

const refreshDailySummary = async () => {
  loadingSummary.value = true
  try {
    const [startDate, endDate] = rangeDate.value || []
    const summary = await getAuditDailySummary({
      start_date: startDate,
      end_date: endDate,
    })
    dailySummary.value = summary || []

    if (!dailySummary.value.find((item) => item.day === selectedDay.value)) {
      selectedDay.value = dailySummary.value[dailySummary.value.length - 1]?.day || endDate || todayText
    }
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || DT.toast.loadSummaryFailed)
  } finally {
    loadingSummary.value = false
  }
}

const refreshDailyDetails = async () => {
  loadingDetail.value = true
  try {
    const [ipRows, accessRows] = await Promise.all([
      getAuditLoginIpStats(selectedDay.value),
      getAuditAccessTop(selectedDay.value, 30),
    ])
    loginIpStats.value = ipRows || []
    accessTop.value = accessRows || []
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || DT.toast.loadDetailFailed)
  } finally {
    loadingDetail.value = false
  }
}

const refreshAdminActions = async () => {
  loadingActions.value = true
  try {
    const data = await getAuditAdminActions({
      day: selectedDay.value,
      username: adminUserFilter.value || undefined,
      skip: (adminPage.value - 1) * adminPageSize.value,
      limit: adminPageSize.value,
    })
    adminActionTotal.value = Number(data?.total || 0)
    adminActionRows.value = formatActionRows(data?.items || [])
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || DT.toast.loadActionsFailed)
  } finally {
    loadingActions.value = false
  }
}

const refreshAll = async () => {
  await refreshDailySummary()
  await Promise.all([refreshDailyDetails(), refreshAdminActions()])
}

const selectSummaryDay = (row) => {
  if (!row?.day) return
  selectedDay.value = row.day
  adminPage.value = 1
  refreshDailyDetails()
  refreshAdminActions()
}

const handleAdminPageChange = (page) => {
  adminPage.value = page
  refreshAdminActions()
}

const handleAdminPageSizeChange = (size) => {
  adminPageSize.value = size
  adminPage.value = 1
  refreshAdminActions()
}

onMounted(() => {
  refreshAll()
})
</script>

<style scoped>
.audit-page {
  width: 100%;
}

.daily-grid {
  display: grid;
  grid-template-columns: 1.05fr 1fr;
  gap: 16px;
  align-items: stretch;
}

.chart-panel {
  width: 100%;
  min-height: 320px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.03);
  padding: 8px;
}

.audit-pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 1200px) {
  .daily-grid {
    grid-template-columns: 1fr;
  }
}
</style>

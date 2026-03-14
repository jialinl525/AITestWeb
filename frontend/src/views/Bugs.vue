<template>
  <div class="page-shell bugs-container">
    <section class="page-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">Risk Tracking</div>
        <h2 class="page-hero__title">Bug 风险追踪面板</h2>
        <p class="page-hero__desc">从严重程度、处理状态到责任人分配，统一管理问题闭环，快速识别高风险缺陷和待推进事项。</p>
      </div>
      <div class="page-hero__actions">
        <div v-if="route.query.testId" class="glass-pill">当前筛选测试 ID：{{ route.query.testId }}</div>
        <el-button v-if="route.query.testId" @click="clearTestFilter">返回全部Bug</el-button>
        <el-button v-if="canCreateBug()" type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建Bug
        </el-button>
      </div>
    </section>

    <div class="metrics-grid">
      <article class="metric-card accent-blue">
        <div class="metric-card__label">总Bug数</div>
        <div class="metric-card__value">{{ bugStats.total || 0 }}</div>
        <div class="metric-card__meta">全部生命周期内的问题记录</div>
      </article>
      <article class="metric-card accent-red">
        <div class="metric-card__label">待处理</div>
        <div class="metric-card__value">{{ bugStats.by_status?.open || 0 }}</div>
        <div class="metric-card__meta">尚未进入执行修复阶段</div>
      </article>
      <article class="metric-card accent-orange">
        <div class="metric-card__label">处理中</div>
        <div class="metric-card__value">{{ bugStats.by_status?.in_progress || 0 }}</div>
        <div class="metric-card__meta">当前正在跟进的问题项</div>
      </article>
      <article class="metric-card accent-green">
        <div class="metric-card__label">已解决</div>
        <div class="metric-card__value">{{ bugStats.by_status?.resolved || 0 }}</div>
        <div class="metric-card__meta">已完成修复并等待验证</div>
      </article>
    </div>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>筛选与搜索</h3>
            <span class="section-title__meta">按状态和严重程度聚焦重点问题</span>
          </div>
        </div>
      </template>

      <el-form :inline="true" class="filter-form">
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable>
            <el-option label="待处理" value="open" />
            <el-option label="处理中" value="in_progress" />
            <el-option label="已解决" value="resolved" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item label="严重程度">
          <el-select v-model="filters.severity" placeholder="全部" clearable>
            <el-option label="严重" value="critical" />
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">筛选</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>Bug 列表</h3>
            <span class="section-title__meta">共 {{ bugsList.length }} 条记录，支持快速编辑与删除</span>
          </div>
        </div>
      </template>
      <el-table :data="bugsList" v-loading="loading" stripe>
        <el-table-column prop="title" label="标题" width="200" />
        <el-table-column prop="description" label="描述" width="300" show-overflow-tooltip />
        <el-table-column prop="severity" label="严重程度" width="120">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)">
              {{ getSeverityText(row.severity) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assigned_to" label="负责人" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button v-if="canEditBug()" size="small" @click="editBug(row)">编辑</el-button>
            <el-button v-if="canDeleteBug()" size="small" type="danger" @click="deleteBug(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingBug ? '编辑Bug' : '新建Bug'"
      width="600px"
    >
      <el-form :model="bugForm" label-width="100px">
        <el-form-item label="测试ID">
          <el-input-number v-model="bugForm.test_progress_id" :min="1" />
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="bugForm.title" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input type="textarea" v-model="bugForm.description" :rows="4" />
        </el-form-item>
        <el-form-item label="严重程度">
          <el-select v-model="bugForm.severity">
            <el-option label="严重" value="critical" />
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="bugForm.status">
            <el-option label="待处理" value="open" />
            <el-option label="处理中" value="in_progress" />
            <el-option label="已解决" value="resolved" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人">
          <el-input v-model="bugForm.assigned_to" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveBug">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getBugsList, createBug, updateBug, deleteBug as deleteBugApi, getBugStats, getBugsByTest } from '../api/bugs'
import { canCreateBug, canEditBug, canDeleteBug } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const bugsList = ref([])
const bugStats = ref({})
const showCreateDialog = ref(false)
const editingBug = ref(null)

const filters = ref({
  status: null,
  severity: null
})

const bugForm = ref({
  test_progress_id: null,
  title: '',
  description: '',
  severity: 'medium',
  status: 'open',
  assigned_to: ''
})

const loadData = async () => {
  loading.value = true
  try {
    let data
    
    // 如果URL中有testId参数，加载该测试的bugs
    if (route.query.testId) {
      data = await getBugsByTest(route.query.testId)
    } else {
      const params = {}
      if (filters.value.status) params.status = filters.value.status
      if (filters.value.severity) params.severity = filters.value.severity
      data = await getBugsList(params)
    }
    
    bugsList.value = data
    
    // 加载统计信息
    const stats = await getBugStats()
    bugStats.value = stats
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    status: null,
    severity: null
  }
  loadData()
}

const clearTestFilter = () => {
  router.push({ path: '/bugs' })
}

const getSeverityType = (severity) => {
  const map = {
    critical: 'danger',
    high: 'warning',
    medium: 'info',
    low: ''
  }
  return map[severity] || 'info'
}

const getSeverityText = (severity) => {
  const map = {
    critical: '严重',
    high: '高',
    medium: '中',
    low: '低'
  }
  return map[severity] || severity
}

const getStatusType = (status) => {
  const map = {
    open: 'danger',
    in_progress: 'warning',
    resolved: 'success',
    closed: 'info'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    open: '待处理',
    in_progress: '处理中',
    resolved: '已解决',
    closed: '已关闭'
  }
  return map[status] || status
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

const editBug = (bug) => {
  editingBug.value = bug
  bugForm.value = {
    test_progress_id: bug.test_progress_id,
    title: bug.title,
    description: bug.description,
    severity: bug.severity,
    status: bug.status,
    assigned_to: bug.assigned_to || ''
  }
  showCreateDialog.value = true
}

const saveBug = async () => {
  try {
    if (editingBug.value) {
      await updateBug(editingBug.value.id, bugForm.value)
      ElMessage.success('更新成功')
    } else {
      await createBug(bugForm.value)
      ElMessage.success('创建成功')
    }
    showCreateDialog.value = false
    editingBug.value = null
    bugForm.value = {
      test_progress_id: null,
      title: '',
      description: '',
      severity: 'medium',
      status: 'open',
      assigned_to: ''
    }
    loadData()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const deleteBug = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个Bug吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteBugApi(id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadData()
})

watch(() => route.query.testId, () => {
  loadData()
})
</script>

<style scoped>
.bugs-container {
  width: 100%;
}

.filter-form {
  margin-bottom: 0;
}

@media (max-width: 768px) {
  .filter-form :deep(.el-form-item) {
    margin-right: 0;
    width: 100%;
  }
}
</style>

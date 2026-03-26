<template>
  <el-card class="section-card">
    <template #header>
      <div class="section-title">
        <div class="section-title__main">
          <h3>Model List</h3>
          <span class="section-title__meta">Only latest test-time data is shown for each model name</span>
        </div>
        <div class="compare-toolbar">
          <el-button type="primary" @click="$emit('compare')">{{ BT.compareModels }}</el-button>
          <template v-if="canManage">
            <el-button type="warning" @click="$emit('update-model')">Update Model</el-button>
            <el-button type="success" @click="$emit('new-model')">New Model</el-button>
          </template>
        </div>
      </div>
    </template>
    <el-table :data="modelList" v-loading="loading" stripe table-layout="fixed" class="model-list-table">
      <el-table-column prop="model_name" label="Model Name" align="center" header-align="center">
        <template #default="{ row }">
          <button type="button" class="model-link-btn" @click="$emit('go-detail', row.model_name)">
            {{ row.model_name }}
          </button>
        </template>
      </el-table-column>
      <el-table-column prop="test_version" label="Test Version" align="center" header-align="center" show-overflow-tooltip />
      <el-table-column prop="model_size" label="Model Size" align="center" header-align="center" show-overflow-tooltip />
      <el-table-column prop="source" label="Source" align="center" header-align="center" show-overflow-tooltip />
      <el-table-column prop="test_date" label="Test Time" align="center" header-align="center">
        <template #default="{ row }">{{ formatDateTime(row.test_date) }}</template>
      </el-table-column>
      <el-table-column v-if="canManage" label="Actions" align="center" header-align="center">
        <template #default="{ row }">
          <div class="row-actions">
            <el-button size="small" @click="$emit('edit', row)">Update</el-button>
            <el-button size="small" type="danger" plain @click="$emit('delete', row)">Delete</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { ButtonText } from '../../texts/ButtonText'

const BT = ButtonText.kpi

defineProps({
  modelList: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  canManage: { type: Boolean, default: false }
})

defineEmits(['compare', 'update-model', 'new-model', 'go-detail', 'edit', 'delete'])

const formatDateTime = (value) => {
  if (!value) return '-'
  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? '-' : d.toLocaleString('en-US')
}
</script>

<style scoped>
.compare-toolbar { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }

.row-actions { display: inline-flex; align-items: center; justify-content: center; gap: 8px; }

.model-link-btn {
  appearance: none; border: none; background: transparent;
  display: inline-block; width: 100%; margin: 0; padding: 0;
  color: #7dd3fc; cursor: pointer; font-weight: 700;
  text-align: center; text-decoration: underline; text-underline-offset: 2px;
}
.model-link-btn:hover { color: #bae6fd; }
.model-link-btn:focus-visible { outline: 2px solid rgba(125, 211, 252, 0.75); outline-offset: 2px; border-radius: 4px; }
</style>

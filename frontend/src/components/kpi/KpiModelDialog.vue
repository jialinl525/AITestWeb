<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    :title="isEditing ? 'Edit Model (Latest Test Run)' : 'New Model Test Run'"
    width="760px"
  >
    <el-form :model="modelForm" label-width="170px" class="model-dialog-form">
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item label="Model Category">
            <el-select v-model="modelForm.model_category" style="width: 100%">
              <el-option v-for="key in modelCategories" :key="key" :label="key" :value="key" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Model Name">
            <el-input v-model="modelForm.model_name" :disabled="isEditing" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item label="Source"><el-input v-model="modelForm.source" /></el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Model Size"><el-input v-model="modelForm.model_size" /></el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="Description">
        <el-input v-model="modelForm.description" type="textarea" :rows="2" />
      </el-form-item>
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item label="Test Time">
            <el-date-picker v-model="modelForm.test_date" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Test Platform"><el-input v-model="modelForm.test_platform" /></el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item label="Test Version"><el-input v-model="modelForm.test_version" /></el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Test Condition">
            <el-input v-model="modelForm.test_condition" type="textarea" :rows="2" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="12">
        <el-col v-for="metric in formMetrics" :key="metric.value" :span="24">
          <el-form-item :label="metric.label">
            <el-input-number
              v-model="modelForm.metrics[metric.value]"
              :min="getMetricMin(metric.value)"
              :max="getMetricMax(metric.value)"
              :step="0.01" :precision="2"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    <template #footer>
      <el-button @click="$emit('update:visible', false)">Cancel</el-button>
      <el-button v-if="canManage" type="primary" :loading="saving" @click="$emit('save')">Save</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { isAccuracyMetric, getMetricMin, getMetricMax } from '../../utils/kpiMetrics'

defineProps({
  visible: { type: Boolean, default: false },
  isEditing: { type: Boolean, default: false },
  modelForm: { type: Object, required: true },
  modelCategories: { type: Array, default: () => [] },
  formMetrics: { type: Array, default: () => [] },
  saving: { type: Boolean, default: false },
  canManage: { type: Boolean, default: false }
})

defineEmits(['update:visible', 'save'])
</script>

<style scoped>
.model-dialog-form :deep(.el-form-item__label) { white-space: nowrap; }
</style>

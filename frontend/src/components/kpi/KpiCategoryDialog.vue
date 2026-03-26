<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    :title="isEditing ? 'Edit Model Type' : 'New Model Type'"
    width="960px"
  >
    <el-form :model="categoryForm" label-width="170px" class="model-dialog-form">
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item label="Model Type Key">
            <el-input v-model="categoryForm.key" :disabled="isEditing" placeholder="For example: Noise Suppression" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Display Label">
            <el-input v-model="categoryForm.label" placeholder="Displayed title" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="Function Description">
        <el-input v-model="categoryForm.description" type="textarea" :rows="3" placeholder="What this model type is used for" />
      </el-form-item>
      <el-form-item label="Typical Implementation">
        <el-input v-model="categoryForm.implementation_notes" type="textarea" :rows="4" placeholder="How this model type is commonly implemented" />
      </el-form-item>
      <div class="category-editor-head">
        <div>
          <h4 class="category-editor-head__title">Parameters</h4>
          <p class="category-editor-head__desc">Define the metrics shown in charts, forms, and descriptions.</p>
        </div>
        <el-button type="primary" plain @click="addMetricRow">Add Parameter</el-button>
      </div>
      <div class="category-editor-list">
        <section
          v-for="(metric, index) in categoryForm.metrics"
          :key="`category-metric-${index}`"
          class="category-editor-item"
        >
          <div class="category-editor-item__toolbar">
            <strong>Parameter {{ index + 1 }}</strong>
            <el-button type="danger" link @click="removeMetricRow(index)">Remove</el-button>
          </div>
          <el-row :gutter="12">
            <el-col :span="8">
              <el-form-item label="Metric Key" label-width="120px">
                <el-input v-model="metric.key" placeholder="For example: snr_score" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="Label" label-width="120px">
                <el-input v-model="metric.label" placeholder="Display name" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="Unit" label-width="120px">
                <el-input v-model="metric.unit" placeholder="For example: ms / % / W" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="12">
            <el-col :span="8">
              <el-form-item label="Direction" label-width="120px">
                <el-select v-model="metric.direction" style="width: 100%">
                  <el-option label="Higher is better" value="higher" />
                  <el-option label="Lower is better" value="lower" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="16">
              <el-form-item label="Chart Roles" label-width="120px">
                <el-select v-model="metric.chart_roles" multiple collapse-tags collapse-tags-tooltip style="width: 100%">
                  <el-option label="ladder" value="ladder" />
                  <el-option label="scatter" value="scatter" />
                  <el-option label="table" value="table" />
                  <el-option label="form" value="form" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="Definition" label-width="120px">
            <el-input v-model="metric.definition" type="textarea" :rows="3" placeholder="Explain what this parameter means" />
          </el-form-item>
        </section>
      </div>
    </el-form>
    <template #footer>
      <el-button @click="$emit('update:visible', false)">Cancel</el-button>
      <el-button type="primary" :loading="saving" @click="$emit('save')">Save</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ElMessage } from 'element-plus'

const props = defineProps({
  visible: { type: Boolean, default: false },
  isEditing: { type: Boolean, default: false },
  categoryForm: { type: Object, required: true },
  saving: { type: Boolean, default: false }
})

defineEmits(['update:visible', 'save'])

const createEmptyMetric = () => ({
  key: '', label: '', unit: '', direction: 'higher',
  chart_roles: ['ladder', 'table', 'form'], definition: ''
})

const addMetricRow = () => {
  props.categoryForm.metrics.push(createEmptyMetric())
}

const removeMetricRow = (index) => {
  if ((props.categoryForm.metrics || []).length <= 1) {
    ElMessage.warning('At least one parameter is required')
    return
  }
  props.categoryForm.metrics.splice(index, 1)
}
</script>

<style scoped>
.model-dialog-form :deep(.el-form-item__label) { white-space: nowrap; }
.category-editor-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin: 10px 0 14px; }
.category-editor-head__title { margin: 0; color: #f8fafc; font-size: 16px; }
.category-editor-head__desc { margin: 6px 0 0; color: rgba(148, 163, 184, 0.82); font-size: 13px; }
.category-editor-list { display: flex; flex-direction: column; gap: 14px; }
.category-editor-item { padding: 16px; border-radius: 16px; border: 1px solid rgba(148, 163, 184, 0.14); background: rgba(255, 255, 255, 0.03); }
.category-editor-item__toolbar { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 12px; }
</style>

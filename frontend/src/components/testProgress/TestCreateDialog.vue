<template>
  <el-dialog
    :model-value="modelValue"
    :title="isEditing ? LT.dialog.editTitle : LT.dialog.newTitle"
    width="560px"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <el-form :model="form" label-width="120px">
      <el-form-item :label="LT.form.frNumber">
        <el-input v-model="form.fr_number" :placeholder="DT.placeholders.frExample" />
      </el-form-item>
      <el-form-item :label="LT.form.testName">
        <el-input v-model="form.test_name" :placeholder="DT.placeholders.testName" />
      </el-form-item>
      <el-form-item :label="LT.form.featureSummary">
        <el-input v-model="form.model_name" :placeholder="DT.placeholders.featureSummary" />
      </el-form-item>
      <el-form-item :label="LT.form.detailedDescription">
        <el-input v-model="form.description" type="textarea" :rows="4" :placeholder="DT.placeholders.detailDescription" />
      </el-form-item>
      <el-form-item :label="LT.form.configMethod">
        <el-input v-model="form.config_method" type="textarea" :rows="3" :placeholder="DT.placeholders.configMethod" />
      </el-form-item>
      <el-form-item :label="LT.form.testers">
        <el-select
          v-model="form.test_owners_list"
          multiple
          filterable
          allow-create
          default-first-option
          style="width: 100%"
          :placeholder="DT.placeholders.testers"
        >
          <el-option v-for="owner in ownerOptions" :key="owner" :label="owner" :value="owner" />
        </el-select>
      </el-form-item>
      <el-form-item :label="LT.form.developers">
        <el-input v-model="form.developers" :placeholder="DT.placeholders.developers" />
      </el-form-item>
      <el-form-item :label="LT.form.status">
        <el-select v-model="form.status" style="width: 100%">
          <el-option v-for="status in TASK_STATUS_OPTIONS" :key="status" :label="status" :value="status" />
        </el-select>
      </el-form-item>

      <!-- L0 -->
      <el-form-item :label="LT.form.l0Cases">
        <el-input-number v-model="form.l0_passed_cases" :min="0" size="small" style="width: 88px" />
        <span class="form-divider">/</span>
        <el-input-number v-model="form.l0_failed_cases" :min="0" size="small" style="width: 88px" />
        <span class="form-divider">/</span>
        <el-input-number v-model="form.l0_total_cases" :min="0" size="small" style="width: 88px" />
      </el-form-item>
      <el-form-item :label="LT.form.l0DueDate">
        <el-date-picker v-model="form.l0_due_date" type="date" value-format="YYYY-MM-DD" :placeholder="DT.placeholders.l0DueDate" style="width: 100%" />
      </el-form-item>

      <!-- L2 -->
      <el-form-item :label="LT.form.l2Cases">
        <el-input-number v-model="form.l2_passed_cases" :min="0" size="small" style="width: 88px" />
        <span class="form-divider">/</span>
        <el-input-number v-model="form.l2_failed_cases" :min="0" size="small" style="width: 88px" />
        <span class="form-divider">/</span>
        <el-input-number v-model="form.l2_total_cases" :min="0" size="small" style="width: 88px" />
      </el-form-item>
      <el-form-item :label="LT.form.l2DueDate">
        <el-date-picker v-model="form.l2_due_date" type="date" value-format="YYYY-MM-DD" :placeholder="DT.placeholders.l2DueDate" style="width: 100%" />
      </el-form-item>

      <!-- L4 -->
      <el-form-item :label="LT.form.l4Cases">
        <el-input-number v-model="form.l4_passed_cases" :min="0" size="small" style="width: 88px" />
        <span class="form-divider">/</span>
        <el-input-number v-model="form.l4_failed_cases" :min="0" size="small" style="width: 88px" />
        <span class="form-divider">/</span>
        <el-input-number v-model="form.l4_total_cases" :min="0" size="small" style="width: 88px" />
      </el-form-item>
      <el-form-item :label="LT.form.l4DueDate">
        <el-date-picker v-model="form.l4_due_date" type="date" value-format="YYYY-MM-DD" :placeholder="DT.placeholders.l4DueDate" style="width: 100%" />
      </el-form-item>

      <el-form-item>
        <span class="form-helper">{{ DT.helper.inputFormat }}</span>
      </el-form-item>
      <el-form-item v-if="calcProgress !== null" :label="LT.form.progress">
        <span class="progress-hint">{{ DT.helper.autoProgressPrefix }}: {{ calcProgress }}%</span>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="emit('update:modelValue', false)">{{ BTCommon.cancel }}</el-button>
      <el-button type="primary" @click="emit('save')">{{ BTCommon.save }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed } from 'vue'
import { LabelText } from '../../texts/LabelText'
import { ButtonText } from '../../texts/ButtonText'
import { DescriptionText } from '../../texts/DescriptionText'
import { TASK_STATUS_OPTIONS } from '../../utils/taskStatus'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  form: { type: Object, required: true },
  isEditing: { type: Boolean, default: false },
  ownerOptions: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue', 'save'])

const LT = LabelText.testProgress
const BTCommon = ButtonText.common
const DT = DescriptionText.testProgress

const calcProgress = computed(() => {
  const l0t = props.form.l0_total_cases || 0
  const l0p = props.form.l0_passed_cases || 0
  const l2t = props.form.l2_total_cases || 0
  const l2p = props.form.l2_passed_cases || 0
  const l4t = props.form.l4_total_cases || 0
  const l4p = props.form.l4_passed_cases || 0
  const total = l0t + l2t + l4t
  if (total <= 0) return null
  return Math.round(Math.min(100, ((l0p + l2p + l4p) / total) * 100))
})
</script>

<style scoped>
.form-divider {
  margin: 0 8px;
  color: rgba(148, 163, 184, 0.8);
}

.form-helper {
  color: rgba(148, 163, 184, 0.86);
  font-size: 12px;
}

.progress-hint {
  color: rgba(148, 163, 184, 0.9);
  font-size: 14px;
}
</style>

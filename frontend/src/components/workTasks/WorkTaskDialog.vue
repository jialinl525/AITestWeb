<template>
  <el-dialog
    :model-value="modelValue"
    :title="isEditing ? LT.dialog.editTitle : LT.dialog.newTitle"
    width="760px"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <el-form :model="form" label-width="110px">
      <el-form-item :label="LT.form.taskType" required>
        <el-select v-model="form.task_type" style="width: 100%" :placeholder="DT.placeholders.selectType">
          <el-option v-for="item in taskTypeOptions" :key="item" :label="item" :value="item" />
        </el-select>
      </el-form-item>
      <el-form-item :label="LT.form.taskName" required>
        <el-input v-model="form.task_name" :placeholder="DT.placeholders.taskName" />
      </el-form-item>
      <el-form-item :label="LT.form.taskSummary">
        <el-input v-model="form.task_summary" type="textarea" :rows="2" maxlength="300" show-word-limit />
      </el-form-item>
      <el-form-item :label="LT.form.taskDetail">
        <el-input v-model="form.task_detail" type="textarea" :rows="4" maxlength="1000" show-word-limit />
      </el-form-item>
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item :label="LT.form.startDate">
            <el-date-picker v-model="form.start_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item :label="LT.form.endDate">
            <el-date-picker v-model="form.end_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item :label="LT.form.estimatedManday">
            <el-input-number v-model="form.estimated_hours" :min="0" :step="0.5" :precision="1" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item :label="LT.form.progress">
            <el-input-number v-model="form.progress" :min="0" :max="100" :step="1" :precision="0" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item :label="LT.form.status" required>
            <el-select v-model="form.status" style="width: 100%" :placeholder="DT.placeholders.selectStatus">
              <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item :label="LT.form.assignee">
            <el-select v-model="form.assignee_user_id" clearable style="width: 100%" :placeholder="DT.placeholders.optional">
              <el-option
                v-for="member in members"
                :key="member.id"
                :label="member.display_name || member.username"
                :value="member.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <template #footer>
      <el-button @click="emit('update:modelValue', false)">{{ BTCommon.cancel }}</el-button>
      <el-button type="primary" :loading="saving" @click="emit('save')">{{ BTCommon.save }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { LabelText } from '../../texts/LabelText'
import { ButtonText } from '../../texts/ButtonText'
import { DescriptionText } from '../../texts/DescriptionText'

defineProps({
  modelValue: { type: Boolean, default: false },
  form: { type: Object, required: true },
  isEditing: { type: Boolean, default: false },
  saving: { type: Boolean, default: false },
  taskTypeOptions: { type: Array, default: () => [] },
  statusOptions: { type: Array, default: () => [] },
  members: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue', 'save'])

const LT = LabelText.workTasks
const BTCommon = ButtonText.common
const DT = DescriptionText.workTasks
</script>

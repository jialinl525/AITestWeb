<template>
  <el-dialog
    :model-value="modelValue"
    :title="isEditing ? LT.dialog.editTitle : LT.dialog.newTitle"
    width="600px"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <el-form :model="form" label-width="100px">
      <el-form-item :label="LT.form.crNumber">
        <el-input v-model="form.external_cr_number" :placeholder="DT.placeholders.optionalCrNumber" />
      </el-form-item>
      <el-form-item :label="LT.form.testTask">
        <el-select v-model="form.test_progress_id" clearable filterable :placeholder="DT.placeholders.noFrKeyword" style="width: 100%">
          <el-option
            v-for="item in testOptions"
            :key="item.id"
            :label="`${item.fr_number || 'No FR'} | ${item.test_name}`"
            :value="item.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item :label="LT.form.workTask">
        <el-select v-model="form.work_task_id" clearable filterable :placeholder="DT.placeholders.optionalManualLink" style="width: 100%">
          <el-option
            v-for="task in workTaskOptions"
            :key="task.id"
            :label="`${task.task_key} | ${task.task_name}`"
            :value="task.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item :label="LT.form.title">
        <el-input v-model="form.title" />
      </el-form-item>
      <el-form-item :label="LT.form.createdBy">
        <el-input v-model="form.created_by" />
      </el-form-item>
      <el-form-item :label="LT.form.crAssignee">
        <el-input v-model="form.cr_assignee" />
      </el-form-item>
      <el-form-item :label="LT.form.createdOn">
        <el-input v-model="form.cr_created_on" :placeholder="DT.placeholders.createdOnFormat" />
      </el-form-item>
      <el-form-item :label="LT.form.build">
        <el-select
          v-if="buildOptions.length"
          v-model="form.software_image_integration_build"
          clearable
          filterable
          :placeholder="DT.placeholders.selectFromAvailableImages"
          style="width: 100%"
        >
          <el-option v-for="image in buildOptions" :key="image" :label="image" :value="image" />
        </el-select>
        <el-input v-else v-model="form.software_image_integration_build" :placeholder="DT.placeholders.softwareBuild" />
      </el-form-item>
      <el-form-item :label="LT.form.status">
        <el-select v-model="form.status">
          <el-option :label="LT.statusOptions.fixed" value="fixed" />
          <el-option :label="LT.statusOptions.analysis" value="analysis" />
          <el-option :label="LT.statusOptions.other" value="other" />
          <el-option :label="LT.statusOptions.verified" value="verified" />
          <el-option :label="LT.statusOptions.discarded" value="discarded" />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button class="btn-style-3" @click="emit('update:modelValue', false)">{{ BTCommon.cancel }}</el-button>
      <el-button class="btn-style-2" type="primary" @click="emit('save')">{{ BTCommon.save }}</el-button>
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
  buildOptions: { type: Array, default: () => [] },
  testOptions: { type: Array, default: () => [] },
  workTaskOptions: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue', 'save'])

const LT = LabelText.bugs
const BTCommon = ButtonText.common
const DT = DescriptionText.bugs
</script>

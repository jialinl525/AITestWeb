<template>
  <el-dialog
    :model-value="modelValue"
    :title="`${LT.dialog.taskMandayAllocation} - ${task.test_name || ''}`"
    width="980px"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="muted-text allocation-summary">{{ LT.dialog.totalTaskManday }}: {{ Number(task.total_estimated_hours || 0).toFixed(1) }} manday</div>
    <el-table :data="rows" size="small" stripe>
      <el-table-column :label="LT.dialog.tester" min-width="260">
        <template #default="{ row: item }">
          <el-select v-model="item.user_id" filterable style="width: 100%" :placeholder="DT.placeholders.selectMember">
            <el-option
              v-for="member in members"
              :key="member.id"
              :label="member.display_name || member.username"
              :value="member.id"
            />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column :label="LT.dialog.allocatedManday" width="180">
        <template #default="{ row: item }">
          <el-input-number v-model="item.allocated_hours" :min="0" :step="0.5" :precision="1" style="width: 140px" />
        </template>
      </el-table-column>
      <el-table-column :label="LT.dialog.partDescription" min-width="300">
        <template #default="{ row: item }">
          <el-input
            v-model="item.part_description"
            type="textarea"
            :rows="2"
            resize="none"
            maxlength="300"
            show-word-limit
            :placeholder="DT.placeholders.partDescriptionExample"
          />
        </template>
      </el-table-column>
      <el-table-column :label="LT.dialog.actions" width="100">
        <template #default="{ $index }">
          <el-button type="danger" link @click="emit('remove-row', $index)">{{ BTCommon.delete }}</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="allocation-toolbar">
      <el-button @click="emit('add-row')">{{ BT.addAllocationRow }}</el-button>
    </div>
    <template #footer>
      <el-button @click="emit('update:modelValue', false)">{{ BTCommon.cancel }}</el-button>
      <el-button type="primary" :loading="saving" @click="emit('save')">{{ BT.saveAllocation }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { LabelText } from '../../texts/LabelText'
import { ButtonText } from '../../texts/ButtonText'
import { DescriptionText } from '../../texts/DescriptionText'

defineProps({
  modelValue: { type: Boolean, default: false },
  task: { type: Object, default: () => ({}) },
  rows: { type: Array, default: () => [] },
  members: { type: Array, default: () => [] },
  saving: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'save', 'add-row', 'remove-row'])

const LT = LabelText.personnel
const BT = ButtonText.personnel
const BTCommon = ButtonText.common
const DT = DescriptionText.personnel
</script>

<style scoped>
.allocation-summary { margin-bottom: 10px; }
.allocation-toolbar { margin-top: 10px; }
</style>

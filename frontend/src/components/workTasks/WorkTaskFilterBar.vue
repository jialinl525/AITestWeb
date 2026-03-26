<template>
  <div class="toolbar-panel task-toolbar">
    <el-input
      :model-value="filters.keyword"
      :placeholder="DT.placeholders.search"
      clearable
      style="width: 280px"
      @update:model-value="emit('update:filters', { ...filters, keyword: $event })"
    />
    <el-select
      :model-value="filters.task_type"
      :placeholder="DT.placeholders.taskType"
      clearable
      style="width: 180px"
      @update:model-value="emit('update:filters', { ...filters, task_type: $event })"
    >
      <el-option v-for="item in taskTypeOptions" :key="item" :label="item" :value="item" />
    </el-select>
    <el-select
      :model-value="filters.status"
      :placeholder="DT.placeholders.taskStatus"
      clearable
      style="width: 150px"
      @update:model-value="emit('update:filters', { ...filters, status: $event })"
    >
      <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
    </el-select>
    <el-select
      :model-value="filters.assignee_user_id"
      :placeholder="DT.placeholders.assignee"
      clearable
      style="width: 180px"
      @update:model-value="emit('update:filters', { ...filters, assignee_user_id: $event })"
    >
      <el-option
        v-for="member in members"
        :key="member.id"
        :label="member.display_name || member.username"
        :value="member.id"
      />
    </el-select>
    <el-button @click="emit('search')">{{ BTCommon.search }}</el-button>
    <el-button @click="emit('reset')">{{ BTCommon.reset }}</el-button>
    <el-button v-if="canCreate" type="primary" @click="emit('create')">{{ BT.newTask }}</el-button>
  </div>
</template>

<script setup>
import { ButtonText } from '../../texts/ButtonText'
import { DescriptionText } from '../../texts/DescriptionText'

defineProps({
  filters: { type: Object, required: true },
  taskTypeOptions: { type: Array, default: () => [] },
  statusOptions: { type: Array, default: () => [] },
  members: { type: Array, default: () => [] },
  canCreate: { type: Boolean, default: false }
})

const emit = defineEmits(['update:filters', 'search', 'reset', 'create'])

const BT = ButtonText.workTasks
const BTCommon = ButtonText.common
const DT = DescriptionText.workTasks
</script>

<style scoped>
.task-toolbar {
  margin-bottom: 14px;
}
</style>

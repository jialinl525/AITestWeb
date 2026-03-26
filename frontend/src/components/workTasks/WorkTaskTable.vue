<template>
  <div>
    <el-table
      :data="tasks"
      v-loading="loading"
      stripe
      class="full-width-table"
      style="width: 100%"
      table-layout="auto"
    >
      <el-table-column prop="task_name" :label="LT.table.taskName" min-width="220" show-overflow-tooltip>
        <template #default="{ row }">
          <button
            v-if="row.id"
            type="button"
            class="task-name-link"
            @click="emit('view', row.id)"
          >
            {{ row.task_name || '-' }}
          </button>
          <span v-else>{{ row.task_name || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="task_type" :label="LT.table.taskType" min-width="150" />
      <el-table-column prop="task_summary" :label="LT.table.taskSummary" min-width="220" show-overflow-tooltip>
        <template #default="{ row }">{{ row.task_summary || '-' }}</template>
      </el-table-column>
      <el-table-column :label="LT.table.startDate" min-width="120">
        <template #default="{ row }">{{ formatDate(row.start_date) }}</template>
      </el-table-column>
      <el-table-column :label="LT.table.status" min-width="120">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="LT.table.progress" min-width="110">
        <template #default="{ row }">{{ formatPercent(row.progress) }}</template>
      </el-table-column>
      <el-table-column :label="LT.table.assignee" min-width="150">
        <template #default="{ row }">{{ row.assignee_display_name || '-' }}</template>
      </el-table-column>
      <el-table-column v-if="canEdit" :label="LT.table.actions" min-width="150" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="emit('edit', row)">{{ BTCommon.edit }}</el-button>
          <el-button link type="danger" @click="emit('delete', row)">{{ BTCommon.delete }}</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="list-pagination">
      <el-pagination
        v-if="total > pageSize"
        background
        layout="prev, pager, next"
        :page-size="pageSize"
        :total="total"
        :current-page="currentPage"
        @current-change="emit('page-change', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { LabelText } from '../../texts/LabelText'
import { ButtonText } from '../../texts/ButtonText'
import { formatDate, formatPercent } from '../../utils/formatters'

defineProps({
  tasks: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  canEdit: { type: Boolean, default: false },
  total: { type: Number, default: 0 },
  pageSize: { type: Number, default: 10 },
  currentPage: { type: Number, default: 1 }
})

const emit = defineEmits(['view', 'edit', 'delete', 'page-change'])

const LT = LabelText.workTasks
const BTCommon = ButtonText.common

const statusTagType = (status) => {
  if (status === 'Completed') return 'success'
  if (status === 'In Progress') return 'warning'
  if (status === 'Paused') return 'danger'
  return 'info'
}
</script>

<style scoped>
.full-width-table {
  width: 100%;
}

.task-name-link {
  appearance: none;
  border: none;
  background: transparent;
  padding: 0;
  margin: 0;
  color: #7dd3fc;
  font-weight: 700;
  cursor: pointer;
  text-align: left;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.task-name-link:hover {
  color: #bae6fd;
}

.task-name-link:focus-visible {
  outline: 2px solid rgba(125, 211, 252, 0.7);
  outline-offset: 2px;
  border-radius: 4px;
}

.list-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>

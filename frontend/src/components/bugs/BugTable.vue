<template>
  <el-table
    ref="tableRef"
    :data="bugs"
    :empty-text="emptyText"
    :row-class-name="resolveRowClassName"
    :row-key="resolveRowKey"
    v-loading="loading"
    stripe
    @selection-change="handleSelectionChange"
  >
    <el-table-column v-if="enableSelection" type="selection" width="52" />

    <el-table-column prop="external_cr_number" label="CR Number" width="160">
      <template #default="{ row }">
        <a
          v-if="row.external_cr_number"
          :href="getCrLink(row.external_cr_number)"
          target="_blank"
          rel="noopener noreferrer"
          class="cr-link"
        >
          {{ row.external_cr_number }}
        </a>
        <span v-else>-</span>
      </template>
    </el-table-column>

    <el-table-column prop="title" label="Title" min-width="340">
      <template #default="{ row }">
        <el-tooltip
          :content="row.title || ''"
          placement="top-start"
          effect="dark"
          :show-after="120"
        >
          <div class="title-cell-ellipsis">{{ row.title || '-' }}</div>
        </el-tooltip>
      </template>
    </el-table-column>

    <el-table-column prop="status" label="Status" width="120">
      <template #default="{ row }">
        <el-tag :type="getStatusType(row.status)">
          {{ getStatusText(row.status) }}
        </el-tag>
      </template>
    </el-table-column>

    <el-table-column prop="created_by" label="Created By" width="130" />
    <el-table-column prop="cr_assignee" label="CR Assignee" width="130" />

    <el-table-column prop="cr_created_on" label="Created On" width="180">
      <template #default="{ row }">
        {{ formatBugDateTime(row.cr_created_on) }}
      </template>
    </el-table-column>

    <el-table-column
      prop="software_image_integration_build"
      label="Software Image Integration Build"
      min-width="260"
      show-overflow-tooltip
    >
      <template #default="{ row }">
        <span
          class="build-cell"
          :class="{ 'is-pending-confirmation': isPendingConfirmationBuild(row.software_image_integration_build) }"
          :title="isPendingConfirmationBuild(row.software_image_integration_build) ? 'Click to select image' : ''"
          @click.stop="handleBuildCellClick(row)"
        >
          {{ row.software_image_integration_build || '-' }}
        </span>
      </template>
    </el-table-column>

    <el-table-column v-if="showActions" label="Actions" width="250">
      <template #default="{ row }">
        <el-button
          v-if="editable && showVerifyAction && isPendingVerification(row)"
          size="small"
          type="success"
          :loading="isVerifying(row)"
          :disabled="isVerifying(row)"
          @click="emit('verify', row)"
        >
          Verify Pass
        </el-button>
        <el-button v-if="editable" size="small" @click="emit('edit', row)">Edit</el-button>
        <el-button v-if="deletable && !hideDeleteAction" size="small" type="danger" @click="emit('delete', row.id)">Delete</el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup>
import { ref, watch } from 'vue'
import {
  formatBugDateTime,
  getCrLink,
  getStatusText,
  getStatusType,
  isPendingVerification
} from '../../utils/bugDisplay'

const props = defineProps({
  bugs: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  emptyText: {
    type: String,
    default: 'No data'
  },
  showActions: {
    type: Boolean,
    default: false
  },
  showVerifyAction: {
    type: Boolean,
    default: true
  },
  editable: {
    type: Boolean,
    default: false
  },
  deletable: {
    type: Boolean,
    default: false
  },
  enableSelection: {
    type: Boolean,
    default: false
  },
  hideDeleteAction: {
    type: Boolean,
    default: false
  },
  clearSelectionKey: {
    type: Number,
    default: 0
  },
  isVerifying: {
    type: Function,
    default: () => false
  },
  rowClassName: {
    type: Function,
    default: null
  }
})

const emit = defineEmits(['verify', 'edit', 'delete', 'quick-pick-build', 'selection-change'])

const tableRef = ref(null)

const isPendingConfirmationBuild = (value) => String(value || '').trim().toLowerCase() === 'pending confirmation'

const resolveRowKey = (row) => row?.id

const handleSelectionChange = (rows) => {
  emit('selection-change', rows)
}

const handleBuildCellClick = (row) => {
  if (!isPendingConfirmationBuild(row?.software_image_integration_build)) {
    return
  }
  emit('quick-pick-build', row)
}

const resolveRowClassName = (payload) => {
  if (typeof props.rowClassName === 'function') {
    return props.rowClassName(payload)
  }
  return ''
}

watch(
  () => props.clearSelectionKey,
  () => {
    if (tableRef.value?.clearSelection) {
      tableRef.value.clearSelection()
    }
  }
)
</script>

<style scoped>
.cr-link {
  color: #7dd3fc;
  text-decoration: none;
  font-weight: 600;
}

.cr-link:hover {
  text-decoration: underline;
}

.title-cell-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.build-cell {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.build-cell.is-pending-confirmation {
  cursor: pointer;
  color: #fbbf24;
  font-weight: 700;
  text-decoration: underline dotted;
  text-underline-offset: 2px;
}
</style>

<template>
  <div class="bug-list-toolbar">
    <template v-if="!bulkActionMode">
      <el-button v-if="canEdit" class="btn-style-3" type="success" plain @click="emit('enter-verify')">{{ BT.verifyBugs }}</el-button>
      <el-button v-if="canDelete" class="btn-style-3" type="danger" plain @click="emit('enter-delete')">{{ BT.deleteBugs }}</el-button>
    </template>
    <template v-else>
      <el-button class="btn-style-3" @click="emit('cancel')">{{ BTCommon.cancel }}</el-button>
      <el-button
        v-if="bulkActionMode === 'verify'"
        class="btn-style-2"
        type="success"
        :disabled="!selectedCount"
        :loading="bulkVerifying"
        @click="emit('confirm-verify')"
      >
        {{ LT.toolbar.confirmVerify }} ({{ selectedCount }})
      </el-button>
      <el-button
        v-else-if="bulkActionMode === 'delete'"
        class="btn-style-2"
        type="danger"
        :disabled="!selectedCount"
        :loading="bulkDeleting"
        @click="emit('confirm-delete')"
      >
        {{ LT.toolbar.confirmDelete }} ({{ selectedCount }})
      </el-button>
    </template>
  </div>
</template>

<script setup>
import { LabelText } from '../../texts/LabelText'
import { ButtonText } from '../../texts/ButtonText'

defineProps({
  bulkActionMode: { type: String, default: '' },
  selectedCount: { type: Number, default: 0 },
  canEdit: { type: Boolean, default: false },
  canDelete: { type: Boolean, default: false },
  bulkVerifying: { type: Boolean, default: false },
  bulkDeleting: { type: Boolean, default: false }
})

const emit = defineEmits(['enter-verify', 'enter-delete', 'cancel', 'confirm-verify', 'confirm-delete'])

const LT = LabelText.bugs
const BT = ButtonText.bugs
const BTCommon = ButtonText.common
</script>

<style scoped>
.bug-list-toolbar {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
</style>

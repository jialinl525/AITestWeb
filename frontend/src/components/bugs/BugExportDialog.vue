<template>
  <el-dialog
    :model-value="modelValue"
    :title="LT.dialog.exportTopNTitle"
    width="420px"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <el-form label-width="120px">
      <el-form-item :label="LT.dialog.exportArea">
        <el-select v-model="localArea" style="width: 100%">
          <el-option :label="LT.verificationOptions.all" value="all" />
          <el-option :label="LT.verificationOptions.waitingBuild" value="waiting_build" />
          <el-option :label="LT.verificationOptions.pendingVerification" value="pending_verification" />
          <el-option :label="LT.verificationOptions.verified" value="verified" />
          <el-option :label="LT.verificationOptions.discarded" value="discarded" />
        </el-select>
      </el-form-item>
      <el-form-item :label="LT.dialog.rowsToExport">
        <el-input-number
          v-model="localTopN"
          :min="1"
          :max="Math.max(1, total)"
          :step="1"
          controls-position="right"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button class="btn-style-3" @click="emit('update:modelValue', false)">{{ BTCommon.cancel }}</el-button>
      <el-button class="btn-style-2" type="primary" :loading="exporting" @click="emit('export', { area: localArea, topN: localTopN })">{{ BT.export }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { LabelText } from '../../texts/LabelText'
import { ButtonText } from '../../texts/ButtonText'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  area: { type: String, default: 'all' },
  topN: { type: Number, default: 30 },
  total: { type: Number, default: 0 },
  exporting: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'export'])

const LT = LabelText.bugs
const BT = ButtonText.bugs
const BTCommon = ButtonText.common

const localArea = ref(props.area)
const localTopN = ref(props.topN)

watch(() => props.area, (v) => { localArea.value = v })
watch(() => props.topN, (v) => { localTopN.value = v })
</script>

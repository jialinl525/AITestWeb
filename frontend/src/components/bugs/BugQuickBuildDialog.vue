<template>
  <el-dialog
    :model-value="modelValue"
    :title="LT.dialog.quickBuildTitle"
    width="520px"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <el-form label-width="120px">
      <el-form-item :label="LT.dialog.quickBuildCrNumber">
        <span>{{ bug?.external_cr_number || '-' }}</span>
      </el-form-item>
      <el-form-item :label="LT.dialog.quickBuildBugTitle">
        <span class="quick-build-title">{{ bug?.title || '-' }}</span>
      </el-form-item>
      <el-form-item :label="LT.dialog.quickBuildAvailableImage">
        <el-select
          v-model="localSelection"
          filterable
          :placeholder="DT.placeholders.selectImage"
          style="width: 100%"
        >
          <el-option
            v-for="image in options"
            :key="`quick-build-${image}`"
            :label="image"
            :value="image"
          />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button class="btn-style-3" @click="emit('update:modelValue', false)">{{ BTCommon.cancel }}</el-button>
      <el-button class="btn-style-2" type="primary" :loading="saving" @click="emit('save', localSelection)">{{ BTCommon.save }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { LabelText } from '../../texts/LabelText'
import { ButtonText } from '../../texts/ButtonText'
import { DescriptionText } from '../../texts/DescriptionText'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  bug: { type: Object, default: null },
  options: { type: Array, default: () => [] },
  selection: { type: String, default: '' },
  saving: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'save'])

const LT = LabelText.bugs
const BTCommon = ButtonText.common
const DT = DescriptionText.bugs

const localSelection = ref(props.selection)

watch(() => props.selection, (v) => { localSelection.value = v })
watch(() => props.options, (v) => { if (v.length && !localSelection.value) localSelection.value = v[0] })
</script>

<style scoped>
.quick-build-title {
  line-height: 1.6;
  word-break: break-word;
}
</style>

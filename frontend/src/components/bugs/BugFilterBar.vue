<template>
  <el-form :inline="true" class="filter-form">
    <el-form-item :label="LT.filter.verification">
      <el-select v-model="localFilters.verification_zone" class="filter-select" style="width: 180px" popper-class="bugs-filter-popper">
        <el-option :label="LT.verificationOptions.all" value="all" />
        <el-option :label="LT.verificationOptions.waitingBuild" value="waiting_build" />
        <el-option :label="LT.verificationOptions.pendingVerification" value="pending_verification" />
        <el-option :label="LT.verificationOptions.verified" value="verified" />
        <el-option :label="LT.verificationOptions.discarded" value="discarded" />
      </el-select>
    </el-form-item>
    <el-form-item :label="LT.filter.status">
      <el-select v-model="localFilters.status" class="filter-select" :placeholder="DT.placeholders.all" clearable popper-class="bugs-filter-popper">
        <el-option v-for="status in statusOptions" :key="status" :label="status" :value="status" />
      </el-select>
    </el-form-item>
    <el-form-item :label="LT.filter.createdBy">
      <el-select
        v-model="localFilters.created_by"
        class="filter-select"
        :placeholder="DT.placeholders.all"
        clearable
        filterable
        popper-class="bugs-filter-popper"
      >
        <el-option v-for="name in createdByOptions" :key="name" :label="name" :value="name" />
      </el-select>
    </el-form-item>
    <el-form-item>
      <el-button class="btn-style-3" @click="emit('reset')">{{ BTCommon.reset }}</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { reactive, watch } from 'vue'
import { LabelText } from '../../texts/LabelText'
import { ButtonText } from '../../texts/ButtonText'
import { DescriptionText } from '../../texts/DescriptionText'

const props = defineProps({
  filters: { type: Object, required: true },
  statusOptions: { type: Array, default: () => [] },
  createdByOptions: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:filters', 'reset'])

const LT = LabelText.bugs
const BTCommon = ButtonText.common
const DT = DescriptionText.bugs

const localFilters = reactive({ ...props.filters })

watch(localFilters, (val) => {
  emit('update:filters', { ...val })
})

watch(() => props.filters, (val) => {
  Object.assign(localFilters, val)
}, { deep: true })
</script>

<style scoped>
.filter-form { margin-bottom: 0; }
.filter-select { min-width: 180px; }

:deep(.bugs-filter-popper .el-select-dropdown__item) {
  white-space: nowrap;
}
</style>

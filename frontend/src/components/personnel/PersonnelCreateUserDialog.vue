<template>
  <el-dialog
    :model-value="modelValue"
    title="Create Member"
    width="620px"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <el-form :model="form" label-width="120px">
      <el-form-item label="Username">
        <el-input v-model="form.username" maxlength="64" show-word-limit />
      </el-form-item>
      <el-form-item label="Display Name">
        <el-input v-model="form.display_name" maxlength="100" show-word-limit />
      </el-form-item>
      <el-form-item label="Password">
        <el-input v-model="form.password" type="password" show-password maxlength="100" />
      </el-form-item>
      <el-form-item label="Role">
        <el-select v-model="form.role" style="width: 100%">
          <el-option label="Viewer" value="viewer" />
          <el-option label="Manager" value="manager" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="emit('update:modelValue', false)">Cancel</el-button>
      <el-button type="primary" :loading="saving" @click="emit('save')">Create</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
defineProps({
  modelValue: { type: Boolean, default: false },
  form: { type: Object, required: true },
  saving: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'save'])
</script>

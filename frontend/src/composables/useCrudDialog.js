import { computed, ref } from 'vue'

export const useCrudDialog = (createDefaultForm, mapEditForm = null) => {
  const showDialog = ref(false)
  const editingId = ref(null)
  const form = ref(createDefaultForm())
  const isEditing = computed(() => Boolean(editingId.value))

  const resetForm = () => {
    form.value = createDefaultForm()
  }

  const openCreateDialog = () => {
    editingId.value = null
    resetForm()
    showDialog.value = true
  }

  const openEditDialog = (row) => {
    editingId.value = row?.id ?? null
    form.value = mapEditForm ? mapEditForm(row) : { ...createDefaultForm(), ...(row || {}) }
    showDialog.value = true
  }

  const closeDialog = () => {
    showDialog.value = false
  }

  return {
    showDialog,
    editingId,
    isEditing,
    form,
    resetForm,
    openCreateDialog,
    openEditDialog,
    closeDialog
  }
}

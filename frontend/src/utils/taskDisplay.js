export const formatTaskLabel = (task, options = {}) => {
  const emptyText = options.emptyText ?? '-'
  const taskLabel = String(task?.task_label || '').trim()
  if (taskLabel) return taskLabel

  const frNumber = String(task?.fr_number || '').trim()
  const testName = String(task?.test_name || '').trim()
  if (frNumber && testName) return `${frNumber} | ${testName}`
  if (frNumber) return frNumber
  return testName || emptyText
}

export const TASK_STATUS_OPTIONS = [
  'Planning',
  'Inprogress',
  'Completed',
  'Paused',
  'Failed'
]

export function normalizeTaskStatus(value) {
  const raw = String(value || '').trim().toLowerCase()
  if (['planning', 'planned', 'plan', 'pending'].includes(raw)) return 'Planning'
  if (['in progress', 'inprogress', 'running', 'ongoing'].includes(raw)) return 'Inprogress'
  if (['completed', 'complete', 'done'].includes(raw)) return 'Completed'
  if (['paused', 'pause', 'hold', 'on hold'].includes(raw)) return 'Paused'
  if (['failed', 'fail'].includes(raw)) return 'Failed'
  return String(value || '').trim() || '-'
}

export function getTaskStatusText(value) {
  return normalizeTaskStatus(value)
}

export function getTaskStatusTagType(value) {
  const normalized = normalizeTaskStatus(value)
  if (normalized === 'Planning') return 'primary'
  if (normalized === 'Inprogress') return 'warning'
  if (normalized === 'Completed') return 'success'
  if (normalized === 'Paused') return 'info'
  if (normalized === 'Failed') return 'danger'
  return 'info'
}

export function getTaskProgressStatus(value) {
  const normalized = normalizeTaskStatus(value)
  if (normalized === 'Completed') return 'success'
  if (normalized === 'Failed') return 'exception'
  return null
}

export const formatDate = (value, options = {}) => {
  const emptyText = options.emptyText ?? '-'
  const locale = options.locale ?? 'en-CA'

  if (!value) return emptyText
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return emptyText
  return date.toLocaleDateString(locale)
}

export const formatDateTime = (value, options = {}) => {
  const emptyText = options.emptyText ?? ''
  const locale = options.locale ?? 'en-CA'

  if (!value) return emptyText
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return emptyText
  return date.toLocaleString(locale)
}

export const formatPercent = (value, options = {}) => {
  const digits = Number.isFinite(options.digits) ? options.digits : 0
  const emptyText = options.emptyText ?? '0%'

  const numeric = Number(value)
  if (!Number.isFinite(numeric)) return emptyText
  return `${numeric.toFixed(digits)}%`
}

export const formatManday = (value, options = {}) => {
  const digits = Number.isFinite(options.digits) ? options.digits : 1
  const emptyText = options.emptyText ?? '0.0 manday'
  const suffix = options.suffix ?? ' manday'

  const numeric = Number(value)
  if (!Number.isFinite(numeric)) return emptyText
  return `${numeric.toFixed(digits)}${suffix}`
}

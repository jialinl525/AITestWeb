export const normalizeTextToken = (value) => String(value || '').trim().toLowerCase().replace(/\s|_|-/g, '')

export const hasValidBuild = (value) => {
  const text = String(value || '').trim().toLowerCase()
  if (!text) return false
  return !['na', 'n/a', '-', 'null', 'none'].includes(text)
}

export const isVerifiedStatus = (status) => normalizeTextToken(status) === 'verified'
export const isDiscardedStatus = (status) => normalizeTextToken(status) === 'discarded'

export const getVerificationZone = (row, options = {}) => {
  const includeDiscardedZone = options.includeDiscardedZone !== false

  if (includeDiscardedZone && isDiscardedStatus(row?.status)) return 'discarded'
  if (isVerifiedStatus(row?.status)) return 'verified'
  if (hasValidBuild(row?.software_image_integration_build)) return 'pending_verification'
  return 'waiting_build'
}

export const isPendingVerification = (row, options = {}) => getVerificationZone(row, options) === 'pending_verification'

export const getStatusBucket = (status) => {
  const text = normalizeTextToken(status)
  if (['inprogress', 'build', 'closed', 'duplicate', 'fixed', 'resolved', 'verified', 'cannotduplicate'].includes(text)) {
    return 'fixed'
  }
  if (['open', 'analysis'].includes(text)) {
    return 'analysis'
  }
  return 'other'
}

export const getStatusType = (status) => {
  const map = {
    fixed: 'success',
    analysis: 'warning',
    other: 'info'
  }
  return map[getStatusBucket(status)] || 'info'
}

export const getStatusText = (status) => String(status || 'other')

export const formatBugDateTime = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('en-US')
}

export const getCrLink = (crNumber) => `https://orbit/CR/${encodeURIComponent(crNumber)}`

import api from './index'

export const getAuditDailySummary = (params = {}) => api.get('/audit/daily-summary', { params })

export const getAuditLoginIpStats = (day) => api.get('/audit/login-ip-stats', { params: { day } })

export const getAuditAccessTop = (day, limit = 20) => api.get('/audit/access-top', { params: { day, limit } })

export const getAuditAdminActions = (params = {}) => api.get('/audit/admin-actions', { params })

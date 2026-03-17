import api from './index'

export const getWorkTasks = (params) => api.get('/work-tasks', { params })

export const createWorkTask = (data) => api.post('/work-tasks', data)

export const updateWorkTask = (id, data) => api.put(`/work-tasks/${id}`, data)

export const deleteWorkTask = (id) => api.delete(`/work-tasks/${id}`)

export const getWorkTaskMeta = () => api.get('/work-tasks/meta')

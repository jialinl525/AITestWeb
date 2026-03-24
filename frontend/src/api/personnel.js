import api from './index'

export const getUsers = () => api.get('/personnel/users')

export const getMembers = () => api.get('/personnel/members')

export const createUser = (data) => api.post('/personnel/users', data)

export const updateUser = (id, data) => api.put(`/personnel/users/${id}`, data)

export const deleteUser = (id) => api.delete(`/personnel/users/${id}`)

export const getWorkload = () => api.get('/personnel/workload')

export const getWorkloadByUser = (userId) => api.get(`/personnel/workload/${userId}`)

export const getPersonnelSummary = () => api.get('/personnel/summary')

export const getTaskAllocations = (testId) => api.get(`/personnel/task-allocations/${testId}`)

export const updateTaskAllocations = (testId, data) => api.put(`/personnel/task-allocations/${testId}`, data)

import api from './index'

export const getTestProgressList = (params = {}) => {
  return api.get('/test-progress/', { params })
}

export const getTestProgress = (id) => {
  return api.get(`/test-progress/${id}`)
}

export const getTestProgressDetail = (id) => {
  return api.get(`/test-progress/${id}/detail`)
}

export const createTestProgress = (data) => {
  return api.post('/test-progress/', data)
}

export const updateTestProgress = (id, data) => {
  return api.put(`/test-progress/${id}`, data)
}

export const getTestProgressByModel = (modelName) => {
  return api.get(`/test-progress/model/${modelName}`)
}

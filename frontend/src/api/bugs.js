import api from './index'

export const getBugsList = (params = {}) => {
  return api.get('/bugs/', { params })
}

export const getBug = (id) => {
  return api.get(`/bugs/${id}`)
}

export const createBug = (data) => {
  return api.post('/bugs/', data)
}

export const updateBug = (id, data) => {
  return api.put(`/bugs/${id}`, data)
}

export const deleteBug = (id) => {
  return api.delete(`/bugs/${id}`)
}

export const getBugsByTest = (testId) => {
  return api.get(`/bugs/test/${testId}`)
}

export const getBugStats = () => {
  return api.get('/bugs/stats/summary')
}

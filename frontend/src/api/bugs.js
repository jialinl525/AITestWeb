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

export const queryBugs = (params = {}) => {
  return api.get('/bugs/query', { params })
}

export const getBugStats = () => {
  return api.get('/bugs/stats/summary')
}

export const getBugCsvFields = (filePath) => {
  const params = filePath ? { file_path: filePath } : {}
  return api.get('/bugs/import/csv/fields', { params })
}

export const getBugFilterOptions = () => {
  return api.get('/bugs/filters/options')
}

export const importBugsFromCsv = (payload = {}) => {
  return api.post('/bugs/import/csv', payload)
}

export const importBugsFromCsvFile = (file, limit = 0) => {
  const formData = new FormData()
  formData.append('file', file)
  if (limit > 0) {
    formData.append('limit', String(limit))
  }
  return api.post('/bugs/import/csv/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

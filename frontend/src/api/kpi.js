import api from './index'

export const getKPIMetrics = (params = {}) => {
  return api.get('/kpi/metrics', { params })
}

export const createKPIMetric = (data) => {
  return api.post('/kpi/metrics', data)
}

export const getKPIModelLatestList = (params = {}) => {
  return api.get('/kpi/models/latest', { params })
}

export const getKPIModelVersions = (modelName, params = {}) => {
  return api.get(`/kpi/models/${encodeURIComponent(modelName)}/versions`, { params })
}

export const getKPIModelDetail = (modelName, params = {}) => {
  return api.get(`/kpi/models/${encodeURIComponent(modelName)}/detail`, { params })
}

export const createKPIModel = (data) => {
  return api.post('/kpi/models', data)
}

export const updateKPILatestModel = (modelName, data) => {
  return api.put(`/kpi/models/${encodeURIComponent(modelName)}/latest`, data)
}

export const deleteKPIModel = (modelName, params = {}) => {
  return api.delete(`/kpi/models/${encodeURIComponent(modelName)}`, { params })
}

export const getModelsPerformance = (modelCategory = null) => {
  return api.get('/kpi/models/performance', {
    params: { model_category: modelCategory }
  })
}

export const getLadderChartData = (metricName = 'accuracy_total', modelCategory = null) => {
  return api.get('/kpi/chart/ladder', {
    params: { metric_name: metricName, model_category: modelCategory }
  })
}

export const getScatterChartData = (xMetric = 'power_consumption', yMetric = 'latency', modelCategory = null) => {
  return api.get('/kpi/chart/scatter', {
    params: { x_metric: xMetric, y_metric: yMetric, model_category: modelCategory }
  })
}

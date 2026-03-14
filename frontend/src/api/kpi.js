import api from './index'

export const getKPIMetrics = (params = {}) => {
  return api.get('/kpi/metrics', { params })
}

export const createKPIMetric = (data) => {
  return api.post('/kpi/metrics', data)
}

export const getModelsPerformance = (modelCategory = null) => {
  return api.get('/kpi/models/performance', {
    params: { model_category: modelCategory }
  })
}

export const getLadderChartData = (metricName = 'accuracy_overall', modelCategory = null) => {
  return api.get('/kpi/chart/ladder', {
    params: { metric_name: metricName, model_category: modelCategory }
  })
}

export const getScatterChartData = (xMetric = 'power_consumption', yMetric = 'latency', modelCategory = null) => {
  return api.get('/kpi/chart/scatter', {
    params: { x_metric: xMetric, y_metric: yMetric, model_category: modelCategory }
  })
}

import axios from 'axios'
import { ElMessage } from 'element-plus'
import { userRole, currentUsername } from '../stores/auth'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor: add user identity headers for permission checks.
api.interceptors.request.use(
  config => {
    config.headers['X-User-Role'] = userRole.value
    config.headers['X-User-Name'] = currentUsername.value || ''
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor.
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response?.status === 403) {
      ElMessage.warning(error.response.data?.detail || 'Insufficient permissions')
    }
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default api

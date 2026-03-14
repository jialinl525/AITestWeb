import axios from 'axios'
import { ElMessage } from 'element-plus'
import { userRole } from '../stores/auth'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加用户角色头用于权限校验
api.interceptors.request.use(
  config => {
    config.headers['X-User-Role'] = userRole.value
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response?.status === 403) {
      ElMessage.warning(error.response.data?.detail || '权限不足')
    }
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default api

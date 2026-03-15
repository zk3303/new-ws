import axios from 'axios'

const API_BASE = '/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000
})

api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 首页统计
export const dashboardAPI = {
  getStats: () => api.get('/api/dashboard/stats'),
  getPumps: () => api.get('/api/pumps'),
}

// 泵房
export const pumpAPI = {
  getList: () => api.get('/api/pumps'),
  getDetail: (id) => api.get(`/api/pump/${id}`),
  getTrend: (id, hours = 24) => api.get(`/api/trend/${id}?hours=${hours}`),
}

// 告警
export const alarmAPI = {
  getList: (params = {}) => api.get('/api/alarms', { params }),
  getDetail: (id) => api.get(`/api/alarm/${id}`),
  getWorkers: (id) => api.get(`/api/alarm/${id}/workers`),
  dispatch: (alarmId, workerId) => api.post(`/api/alarm/${alarmId}/dispatch?worker_id=${workerId}`),
  complete: (id) => api.post(`/api/alarm/${id}/complete`),
}

// 设备
export const deviceAPI = {
  getList: (params = {}) => api.get('/api/devices', { params }),
  getDetail: (id) => api.get(`/api/device/${id}`),
}

// 运维
export const workerAPI = {
  getList: (params = {}) => api.get('/api/workers', { params }),
  getDetail: (id) => api.get(`/api/worker/${id}`),
}

export const workorderAPI = {
  getList: (params = {}) => api.get('/api/workorders', { params }),
}

// 能耗
export const energyAPI = {
  getReport: (period = 'week') => api.get(`/api/energy?period=${period}`),
}

export default api

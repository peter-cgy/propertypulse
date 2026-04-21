import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 添加token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 房产相关API
export const propertyApi = {
  // 搜索房产
  search: async (address: string) => {
    const response = await api.get('/api/properties/search', {
      params: { address },
    })
    return response.data
  },

  // 获取房产详情
  getDetail: async (propertyId: string) => {
    const response = await api.get(`/api/properties/${propertyId}`)
    return response.data
  },
}

// 用户相关API
export const authApi = {
  // 注册
  register: async (email: string, password: string, name: string) => {
    const response = await api.post('/api/auth/register', {
      email,
      password,
      name,
    })
    return response.data
  },

  // 登录
  login: async (email: string, password: string) => {
    const response = await api.post('/api/auth/login', {
      email,
      password,
    })
    return response.data
  },

  // 获取当前用户信息
  getMe: async () => {
    const response = await api.get('/api/auth/me')
    return response.data
  },
}

// 报告相关API
export const reportApi = {
  // 生成报告
  generate: async (propertyId: string) => {
    const response = await api.post('/api/reports/generate', { propertyId })
    return response.data
  },

  // 获取报告列表
  getList: async () => {
    const response = await api.get('/api/reports')
    return response.data
  },

  // 下载报告
  download: async (reportId: string) => {
    const response = await api.get(`/api/reports/${reportId}/download`, {
      responseType: 'blob',
    })
    return response.data
  },
}

export default api

import axios, { AxiosRequestConfig, AxiosHeaders, AxiosRequestHeaders } from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const request = axios.create({
  baseURL: 'http://localhost:5000',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    console.log('Request URL:', config.url)
    console.log('Request Method:', config.method)
    console.log('Request Headers:', config.headers)
    console.log('Request Data:', config.data)
    console.log('Request Params:', config.params)
    
    // 如果是登录请求，不需要添加 token
    if (config.url?.includes('/api/auth/login')) {
      return config
    }
    
    const token = localStorage.getItem('token')
    if (token) {
      // 确保 headers 存在
      if (!config.headers) {
        config.headers = new AxiosHeaders({
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }) as AxiosRequestHeaders
      }
      
      // 确保 token 包含 Bearer 前缀
      const tokenWithBearer = token.startsWith('Bearer ') ? token : `Bearer ${token}`
      config.headers['Authorization'] = tokenWithBearer.trim()
      console.log('添加 token 到请求头:', config.headers['Authorization'])
      return config
    } else {
      console.warn('未找到 token')
      // 如果不是登录请求且没有 token，重定向到登录页面
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login'
      }
      return Promise.reject(new Error('未找到登录凭证，请重新登录'))
    }
  },
  error => {
    console.log('Request Error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    console.log('Response Status:', response.status)
    console.log('Response Data:', response.data)
    
    // 如果响应类型是 blob，直接返回响应
    if (response.config.responseType === 'blob') {
      return response
    }
    
    // 统一处理响应格式
    if (response.data && typeof response.data === 'object') {
      // 如果响应数据已经包含了 code 字段，说明是后端的标准响应格式
      if ('code' in response.data) {
        return response
      }
      // 否则，将响应数据包装成标准格式
      return {
        ...response,
        data: {
          code: response.status === 200 ? 200 : 500,
          message: '',
          data: response.data
        }
      }
    }
    
    return response
  },
  error => {
    console.log('完整错误信息:', error)
    console.log('响应状态:', error.response?.status)
    console.log('响应数据:', error.response?.data)
    console.log('请求配置:', error.config)
    
    if (error.response?.status === 401 || 
        (error.response?.status === 422 && 
         error.response?.data?.msg?.includes('Authorization'))) {
      // 清除本地存储的 token
      localStorage.removeItem('token')
      // 重定向到登录页面
      window.location.href = '/login'
      return Promise.reject(new Error('登录已过期或无效，请重新登录'))
    }
    
    // 包装错误响应为标准格式
    if (error.response?.data) {
      return Promise.reject({
        ...error,
        response: {
          ...error.response,
          data: {
            code: error.response.status,
            message: error.response.data.message || error.response.data.msg || error.message,
            data: null
          }
        }
      })
    }
    
    if (error.message === 'Network Error') {
      ElMessage.error('网络连接失败，请检查网络设置和后端服务是否正常运行')
    } else {
      ElMessage.error(error.response?.data?.message || error.response?.data?.msg || error.message || '请求失败')
    }
    return Promise.reject(error)
  }
)

// 创建自定义请求方法来处理特殊情况
export const requestWithoutErrorMsg = async (config: AxiosRequestConfig) => {
  try {
    const response = await request(config)
    return response
  } catch (error: any) {
    if (error.response?.status === 404) {
      return {
        data: {
          code: 200,
          data: null,
          message: '未找到相关数据'
        }
      }
    }
    return Promise.reject(error)
  }
}

export default request 
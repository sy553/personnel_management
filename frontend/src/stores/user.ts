import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login } from '@/api/user'
import type { LoginData, LoginResponse } from '@/api/user'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref<LoginResponse['user'] | null>(
    localStorage.getItem('userInfo') ? JSON.parse(localStorage.getItem('userInfo')!) : null
  )

  const loginAction = async (loginData: LoginData) => {
    try {
      const res = await login(loginData)
      console.log('Login response:', res)
      
      // 检查响应数据
      if (!res.data) {
        throw new Error('登录响应数据为空')
      }

      // 检查 access_token
      if (!res.data.access_token) {
        throw new Error('未获取到访问令牌')
      }

      // 保存 token
      const tokenValue = `Bearer ${res.data.access_token}`
      token.value = tokenValue
      localStorage.setItem('token', tokenValue)
      
      // 保存用户信息
      if (res.data.user) {
        userInfo.value = res.data.user
        localStorage.setItem('userInfo', JSON.stringify(res.data.user))
      }
      
      console.log('Saved token:', tokenValue)
      console.log('Saved user info:', res.data.user)
      ElMessage.success('登录成功')
      return res.data
    } catch (error: any) {
      console.error('Login action error:', error)
      const errorMessage = error.response?.data?.message || error.message || '登录失败'
      ElMessage.error(errorMessage)
      throw error
    }
  }

  const logout = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    window.location.href = '/login'
  }

  return {
    token,
    userInfo,
    loginAction,
    logout
  }
}) 
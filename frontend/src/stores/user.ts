import { defineStore } from 'pinia'
import { login } from '@/api/user'
import type { LoginData } from '@/api/user'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(localStorage.getItem('userInfo') ? JSON.parse(localStorage.getItem('userInfo')!) : null)

  const loginAction = async (loginData: LoginData) => {
    try {
      const res = await login(loginData)
      
      if (res.code !== 200 || !res.data) {
        throw new Error(res.message || '登录失败')
      }

      // 保存 token
      const tokenValue = `Bearer ${res.data.token}`
      token.value = tokenValue
      localStorage.setItem('token', tokenValue)
      
      // 保存用户信息
      if (res.data.user) {
        userInfo.value = res.data.user
        localStorage.setItem('userInfo', JSON.stringify(res.data.user))
      }
      
      ElMessage.success(res.message || '登录成功')
      return res.data
    } catch (error: any) {
      console.error('Login action error:', error)
      ElMessage.error(error.message || '登录失败')
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
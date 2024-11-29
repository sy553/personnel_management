import request from '@/utils/request'
import type { ApiResponse } from '@/types/api'

export interface LoginData {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  user: {
    id: number
    username: string
    email: string
    is_active: boolean
    created_at: string
    updated_at: string
    role: {
      id: number
      name: string
      description: string
      permissions: string[]
    }
  }
}

// 登录
export const login = (data: LoginData) => {
  return request<LoginResponse>({
    url: '/api/auth/login',
    method: 'POST',
    data
  })
}

// 登出
export const logout = () => {
  return request({
    url: '/api/auth/logout',
    method: 'POST'
  })
}

export interface EmployeeForm {
  employeeNo: string
  name: string
  gender: string
  birthday: string
  phone: string
  email: string
  idCard: string
  departmentId: number
  position: string
  entryDate: string
  baseSalary: number
  bankAccount: string
  bankName: string
  notes?: string
}

export function addEmployee(data: EmployeeForm) {
  return request({
    url: '/api/employee',
    method: 'post',
    data
  })
}

// 获取部门列表
export function getDepartmentList() {
  return request({
    url: '/api/department/all',  // 移除多余的路径前缀
    method: 'get'
  })
}
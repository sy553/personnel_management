import request from '@/utils/request'

export interface LoginData {
  username: string
  password: string
}

export interface LoginResponse {
  code: number
  data: {
    token: string
    user: {
      id: number
      username: string
      name: string
      role: string
      [key: string]: any
    }
  }
  message: string
}

export function login(data: LoginData) {
  return request<LoginResponse>({
    url: '/auth/login',
    method: 'post',
    data
  })
}

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
import request from '@/utils/request'
import type { Department } from '@/types/employee'
import type { ApiResponse } from '@/types/api'

export interface DepartmentListData {
  departments: Department[]
  total: number
}

// 获取部门列表
export const getDepartmentList = () => {
  return request<ApiResponse<DepartmentListData>>({
    url: '/api/department/list',
    method: 'GET'
  })
}

// 获取部门详情
export const getDepartmentDetail = (id: number) => {
  return request<ApiResponse<Department>>({
    url: `/api/department/${id}`,
    method: 'GET'
  })
}

// 创建部门
export const createDepartment = (data: Omit<Department, 'id'>) => {
  return request<ApiResponse<Department>>({
    url: '/api/department',
    method: 'POST',
    data
  })
}

// 更新部门
export const updateDepartment = (id: number, data: Partial<Department>) => {
  return request<ApiResponse<Department>>({
    url: `/api/department/${id}`,
    method: 'PUT',
    data
  })
}

// 删除部门
export const deleteDepartment = (id: number) => {
  return request<ApiResponse<null>>({
    url: `/api/department/${id}`,
    method: 'DELETE'
  })
} 
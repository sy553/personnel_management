import request from '@/utils/request'
import type { Department, ApiResponse } from '@/types/employee'

// 获取部门列表
export const getDepartmentList = () => {
  return request<ApiResponse<Department[]>>({
    url: '/department/list',
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })
}

// 获取部门详情
export const getDepartmentDetail = (id: number) => {
  return request<ApiResponse<Department>>({
    url: `/api/department/${id}`,
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })
}

// 创建部门
export const createDepartment = (data: Omit<Department, 'id'>) => {
  return request<ApiResponse<Department>>({
    url: '/api/department',
    method: 'POST',
    data,
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })
}

// 更新部门
export const updateDepartment = (id: number, data: Partial<Department>) => {
  return request<ApiResponse<Department>>({
    url: `/api/department/${id}`,
    method: 'PUT',
    data,
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })
}

// 删除部门
export const deleteDepartment = (id: number) => {
  return request<ApiResponse<null>>({
    url: `/api/department/${id}`,
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })
} 
import request from '@/utils/request'
import type { Department } from '@/types/employee'
import type { ApiResponse } from '@/types/api'

export interface DepartmentListResponse {
  departments: Department[]
  total: number
}

// 获取部门列表
export const getDepartmentList = () => {
  return request<ApiResponse<DepartmentListResponse>>({
    url: '/api/department/list',
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })
} 
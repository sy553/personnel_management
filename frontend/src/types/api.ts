// API响应的通用接口
export interface ApiResponse<T> {
  code: number
  data: T
  message?: string
}

// API错误响应接口
export interface ApiError {
  code: number
  message: string
  detail?: any
}

// 部门列表响应接口
export interface DepartmentListResponse {
  departments: Department[]
  total: number
}

// 分页响应接口
export interface PaginatedResponse<T> {
  code: number
  data: T[]
  total: number
  current_page: number
  pages: number
  message?: string
}

// 导入类型
import type { Department } from './employee' 
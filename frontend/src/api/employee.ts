import request from '@/utils/request'
import type { 
  Employee, 
  EducationHistory, 
  TrainingRecord, 
  WorkExperience,
  PositionChange,
  RewardPunishment,
  Contract,
  Attachment,
  Department,
  ApiResponse 
} from '@/types/employee'

export interface EmployeeListParams {
  page: string
  pageSize: string
  name?: string
  department?: string
  status?: string
}

interface EmployeeListData {
  data: Employee[]
  total: number
  current_page: number
  pages: number
}

// 获取员工列表
export const getEmployeeList = (params: EmployeeListParams) => {
  // 确保必需的参数存在
  if (!params.page || !params.pageSize) {
    throw new Error('页码和每页条数是必需的参数')
  }

  // 过滤掉空值
  const filteredParams = Object.fromEntries(
    Object.entries(params).filter(([_, value]) => {
      if (value === undefined || value === null) return false
      if (typeof value === 'string' && !value.trim()) return false
      return true
    })
  )
  
  console.log('过滤后的参数:', filteredParams)
  
  return request<ApiResponse<EmployeeListData>>({
    url: '/api/employee/list',
    method: 'GET',
    params: filteredParams,
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })
}

// 获取员工详情
export const getEmployeeDetail = (employeeNo: string) => {
  return request<ApiResponse<Employee>>({
    url: `/api/employee/detail/${employeeNo}`,
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })
}

// 更新员工详情
export const updateEmployeeDetail = (employeeNo: string, data: Partial<Employee>) => {
  return request<ApiResponse<Employee>>({
    url: `/api/employee/detail/${employeeNo}`,
    method: 'PUT',
    data,
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })
}

// 添加员工教育经历
export const addEmployeeEducation = (employeeNo: string, data: Omit<EducationHistory, 'id'>) => {
  return request<ApiResponse<EducationHistory>>({
    url: `/api/employee/${employeeNo}/education`,
    method: 'POST',
    data,
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })
}

// 更新员工教育经历
export const updateEmployeeEducation = (employeeNo: string, educationId: number, data: Omit<EducationHistory, 'id'>) => {
  return request<ApiResponse<EducationHistory>>({
    url: `/api/employee/${employeeNo}/education/${educationId}`,
    method: 'PUT',
    data,
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })
}

// 删除员工教育经历
export const deleteEmployeeEducation = (employeeNo: string, educationId: number) => {
  return request<ApiResponse<null>>({
    url: `/api/employee/${employeeNo}/education/${educationId}`,
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })
}

// 添加员工培训记录
export const addEmployeeTraining = (employeeNo: string, data: Omit<TrainingRecord, 'id'>) => {
  return request<ApiResponse<TrainingRecord>>({
    url: `/api/employee/${employeeNo}/training`,
    method: 'POST',
    data,
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })
}

// 更新员工培训记录
export const updateEmployeeTraining = (employeeNo: string, trainingId: number, data: Omit<TrainingRecord, 'id'>) => {
  return request<ApiResponse<TrainingRecord>>({
    url: `/api/employee/${employeeNo}/training/${trainingId}`,
    method: 'PUT',
    data,
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })
}

// 删除员工培训记录
export const deleteEmployeeTraining = (employeeNo: string, trainingId: number) => {
  return request<ApiResponse<null>>({
    url: `/api/employee/${employeeNo}/training/${trainingId}`,
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })
}

// 添加员工合同
export const addEmployeeContract = (employeeNo: string, data: FormData) => {
  return request<ApiResponse<Contract>>({
    url: `/api/employee/${employeeNo}/contract`,
    method: 'POST',
    data,
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 更新员工合同
export const updateEmployeeContract = (employeeNo: string, data: FormData) => {
  return request<ApiResponse<Contract>>({
    url: `/api/employee/${employeeNo}/contract`,
    method: 'PUT',
    data,
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 预览员工合同
export const previewEmployeeContract = (employeeNo: string) => {
  return request<ApiResponse<{ url: string }>>({
    url: `/api/employee/${employeeNo}/contract/preview`,
    method: 'GET',
    responseType: 'blob',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })
}

// 下载员工合同
export const downloadEmployeeContract = (employeeNo: string) => {
  return request<ApiResponse<Blob>>({
    url: `/api/employee/${employeeNo}/contract/download`,
    method: 'GET',
    responseType: 'blob',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })
}


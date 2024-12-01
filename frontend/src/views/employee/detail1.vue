<template>
  <div class="employee-detail" v-loading="loading">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>员工详情</span>
          <div class="header-actions">
            <el-button @click="handleBack">
              <el-icon><Back /></el-icon>返回
            </el-button>
          </div>
        </div>
      </template>

      <!-- 基本信息 -->
      <BasicInfoComponent
        v-if="employee"
        :employee="employee"
        @update:basic="handleBasicUpdate"
      />

      <!-- 工作信息 -->
      <WorkInfoComponent
        v-if="employee"
        :employee="employee"
        :departments="departments"
        @update:work="handleWorkUpdate"
      />

      <!-- 合同信息 -->
      <ContractInfoComponent
        v-if="employee"
        :employee="employee"
        @update:contract="handleContractUpdate"
      />

      <!-- 教育经历 -->
      <EducationHistoryComponent
        v-if="employee"
        :employee="employee"
        @add="handleEducationUpdate"
        @update="handleEducationEdit"
        @delete="handleEducationDelete"
      />

      <!-- 工作经历 -->
      <WorkExperienceComponent
        v-if="employee"
        :employee="employee"
        @add="handleExperienceAdd"
        @update="handleExperienceEdit"
        @delete="handleExperienceDelete"
      />

      <!-- 培训记录 -->
      <TrainingRecordComponent
        v-if="employee"
        :employee="employee"
        :records="employee.training"
        @update:training="handleTrainingUpdate"
        @delete:training="handleTrainingDelete"
      />

      <!-- 职位变动 -->
      <PositionChangeComponent
        v-if="employee"
        :employee="employee"
        :history="employee.position_changes || []"
        @update:position="handlePositionUpdate"
      />

      <!-- 奖惩记录 -->
      <RewardPunishmentComponent
        v-if="employee"
        :employee="employee"
        :records="employee.reward_punishments || []"
        @update:reward="handleRewardUpdate"
      />

      <!-- 附件列表 -->
      <AttachmentListComponent
        v-if="employee && uploadUrl"
        :attachments="employee.attachments || []"
        :employee-status="employee.status"
        :upload-url="uploadUrl"
        :upload-headers="uploadHeaders"
        @preview="handleAttachmentPreview"
        @download="handleAttachmentDownload"
        @delete="handleAttachmentDelete"
        @add="handleAttachmentsUpdate"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back } from '@element-plus/icons-vue'
import { getEmployeeDetail, updateEmployeeDetail, addEmployeeEducation, updateEmployeeEducation, deleteEmployeeEducation, addEmployeeTraining, updateEmployeeTraining, deleteEmployeeTraining } from '@/api/employee'
import { getDepartmentList } from '@/api/department'
import type { 
  Employee, 
  Contract, 
  EducationHistory, 
  TrainingRecord,
  WorkExperience as WorkExperienceType,
  PositionChange as PositionChangeType,
  RewardPunishment as RewardPunishmentType,
  Attachment,
  Department
} from '@/types/employee'

// 导入所有组件
import BasicInfoComponent from '@/components/employee/BasicInfo.vue'
import WorkInfoComponent from '@/components/employee/WorkInfo.vue'
import ContractInfoComponent from '@/components/employee/ContractInfo.vue'
import EducationHistoryComponent from '@/components/employee/EducationHistory.vue'
import WorkExperienceComponent from '@/components/employee/WorkExperience.vue'
import TrainingRecordComponent from '@/components/employee/TrainingRecord.vue'
import PositionChangeComponent from '@/components/employee/PositionChange.vue'
import RewardPunishmentComponent from '@/components/employee/RewardPunishment.vue'
import AttachmentListComponent from '@/components/employee/AttachmentList.vue'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const employee = ref<Employee | null>(null)
const departments = ref<Department[]>([])

// 计算上传相关的属性
const uploadHeaders = computed(() => ({
  'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
}))

// 计算上传 URL
const uploadUrl = computed(() => 
  employee.value ? `/api/employee/${employee.value.employee_no}/attachments/upload` : ''
)

// 加载部门列表
const loadDepartments = async () => {
  try {
<<<<<<< HEAD
    console.log('开始加载部门列表')
    const response = await getDepartmentList()
    console.log('部门列表响应:', response)
    
    if (response.code === 200) {
      departments.value = response.data.departments
      console.log('加载到的部门列表:', departments.value)
    } else {
      console.error('部门列表响应格式错误:', response)
      throw new Error(response.message || '加载部门列表失败')
    }
  } catch (error) {
    console.error('加载部门列表失败:', error)
    ElMessage.warning('部门列表加载失败，可能影响部门选择功能')
=======
    const res = await getDepartmentList()
    if (res.code === 200) {
      departments.value = res.data
    } else {
      throw new Error(res.message)
    }
  } catch (error) {
    console.error('加载部门列表失败:', error)
    ElMessage.error('加载部门列表失败：' + error.message)
>>>>>>> affba6b97d4c5bcc7a35d4ae0adb7ce3b2706e97
  }
}

// 加载员工信息
const loadEmployee = async () => {
  const employeeNo = route.params.id as string
  if (!employeeNo) {
    ElMessage.error('员工编号不能为空')
    router.push('/employee/list')
    return
  }

  try {
    loading.value = true
    console.log('开始加载员工信息:', employeeNo)
    const response = await getEmployeeDetail(employeeNo)
    console.log('员工详情响应:', response)
    
    if (response.code === 200 && response.data) {
      // 确保所有数组字段都有默认值，避免 undefined 错误
      employee.value = {
        ...response.data,
        education_history: response.data.education_history || [],
        work_experience: response.data.work_experience || [],
        training_records: response.data.training_records || [],
        position_changes: response.data.position_changes || [],
        reward_punishments: response.data.reward_punishments || [],
        contracts: response.data.contracts || [],
        attachments: response.data.attachments || []
      }
      console.log('处理后的员工数据:', employee.value)
    } else {
      console.error('员工详情响应错误:', response)
      throw new Error(response.message || '加载员工信息失败')
    }
  } catch (error) {
    console.error('加载员工信息失败:', error)
    const errorMessage = (error as AxiosError)?.response?.data?.message 
      || (error as Error).message 
      || '加载员工信息失败'
    console.error('错误详情:', {
      message: errorMessage,
      response: (error as AxiosError)?.response,
      data: (error as AxiosError)?.response?.data
    })
    ElMessage.error(errorMessage)
    router.push('/employee/list')
  } finally {
    loading.value = false
  }
}

// 返回列表
const handleBack = () => {
  router.back()
}

// 更新员工信息
const updateEmployee = async (updatedData: Partial<Employee>) => {
  if (!employee.value?.employee_no) return

  try {
    loading.value = true
    console.log('更新数据:', {
      employeeNo: employee.value.employee_no,
      updatedData
    })
    
    const response = await updateEmployeeDetail(employee.value.employee_no, updatedData)
    
    if (response.code === 200) {
      ElMessage.success('更新成功')
      // 更新本地数据
      if (employee.value) {
        Object.assign(employee.value, updatedData)
      }
      // 重新加载员工信息以确保数据同步
      await loadEmployee()
    } else {
      console.error('更新响应错误:', response)
      throw new Error(response.message || '更新失败')
    }
  } catch (error) {
    console.error('更新员工信息失败:', error)
    const errorDetails = {
      status: (error as AxiosError)?.response?.status,
      data: (error as AxiosError)?.response?.data,
      message: (error as Error).message,
      requestData: (error as AxiosError)?.config?.data
    }
    console.error('错误详情:', errorDetails)
    
    const errorMessage = (error as AxiosError)?.response?.data?.message 
      || (error as Error).message 
      || '更新失败'
    ElMessage.error(errorMessage)
    throw error
  } finally {
    loading.value = false
  }
}

// 处理基本信息更新
const handleBasicUpdate = (data: Partial<Employee>) => {
  console.log('基本信息更新:', data)
  updateEmployee(data)
}

// 工作信息更新
const handleWorkUpdate = async (workInfo: Partial<Employee>) => {
  await updateEmployee(workInfo)
  // 重新加载员工信息以确保显示最新数据
  await loadEmployee()
}

// 合同相关处理函数
const handleContractUpdate = async (contractData: Partial<Contract>) => {
  if (!employee.value) return
  
  try {
    // 构造更新数据，将合同数据转换为正确的格式
    const updateData: Partial<Employee> = {
      contract_number: contractData.number,
      contract_type: contractData.type,
      contract_duration: Number(contractData.duration),
      contract_start_date: contractData.start_date,
      contract_end_date: contractData.end_date,
      contract_sign_date: contractData.sign_date,
      contract_status: contractData.status
    }
    
    // 过滤掉 undefined 值
    Object.keys(updateData).forEach(key => {
      if (updateData[key as keyof typeof updateData] === undefined) {
        delete updateData[key as keyof typeof updateData]
      }
    })
    
    console.log('更新合同数据:', updateData)
    await updateEmployee(updateData)
    // 重新加载员工信息以确保显示最新数据
    await loadEmployee()
  } catch (error) {
    console.error('更新同信息失败:', error)
    throw error // 向上传递错误，让组件处理
  }
}

// 教育经历相关处理函数
const handleEducationUpdate = async (education: Omit<EducationHistory, 'id'>) => {
  if (!employee.value?.employee_no) return
  
  try {
    console.log('添加教育经历:', education)
    loading.value = true
    const result = await addEmployeeEducation(employee.value.employee_no, education)
    
    if (result.code === 200 && result.data) {
      ElMessage.success('添加教育经历成功')
      // 重新加载员工信息以获取最新数据
      await loadEmployee()
    } else {
      throw new Error(result.message || '添加失败')
    }
  } catch (error) {
    console.error('添加教育经历失败:', error)
    ElMessage.error(error instanceof Error ? error.message : '添加失败')
  } finally {
    loading.value = false
  }
}

// 处理教育经历编辑
const handleEducationEdit = async (id: number, education: Omit<EducationHistory, 'id'>) => {
  if (!employee.value?.employee_no) return
  
  try {
    console.log('更新教育经历:', { id, education })
    loading.value = true
    const result = await updateEmployeeEducation(employee.value.employee_no, id, education)
    
    if (result.code === 200 && result.data) {
      ElMessage.success('更新教育经历成功')
      // 重新加载员工信息以获取最新数据
      await loadEmployee()
    } else {
      throw new Error(result.message || '更新失败')
    }
  } catch (error) {
    console.error('更新教育经历失败:', error)
    ElMessage.error(error instanceof Error ? error.message : '更新失败')
  } finally {
    loading.value = false
  }
}

// 处理教育经历删除
const handleEducationDelete = async (id: number) => {
  if (!employee.value?.employee_no) return
  
  try {
    loading.value = true
    const response = await deleteEmployeeEducation(employee.value.employee_no, id)
    
    if (response.code === 200) {
      ElMessage.success('删除教育经历成功')
      // 重新加载员工信息以获取最新数据
      await loadEmployee()
    } else {
      throw new Error(response.message || '删除失败')
    }
  } catch (error) {
    console.error('删除教育经历失败:', error)
    ElMessage.error(error instanceof Error ? error.message : '删除失败')
  } finally {
    loading.value = false
  }
}

// 工作经历相关处理函数
const handleExperienceAdd = async (experience: Omit<WorkExperienceType, 'id'>) => {
  if (!employee.value?.employee_no) return
  
  try {
    loading.value = true
    const newExperience: WorkExperienceType = {
      id: Date.now().toString(),
      ...experience
    }
    const updatedExperience = [...(employee.value.work_experience || []), newExperience]
    
    await updateEmployee({ work_experience: updatedExperience })
    ElMessage.success('添加工作经历成功')
  } catch (error) {
    console.error('添加工作经历失败:', error)
    ElMessage.error('添加工作经历失败')
  } finally {
    loading.value = false
  }
}

const handleExperienceEdit = async (id: string, experience: Omit<WorkExperienceType, 'id'>) => {
  if (!employee.value?.employee_no) return
  
  try {
    loading.value = true
    const updatedExperience = employee.value.work_experience.map(item =>
      item.id === id ? { ...item, ...experience } : item
    )
    
    await updateEmployee({ work_experience: updatedExperience })
    ElMessage.success('更新工作经历成功')
  } catch (error) {
    console.error('更新工作经历失败:', error)
    ElMessage.error('更新工作经历失败')
  } finally {
    loading.value = false
  }
}

const handleExperienceDelete = async (id: string) => {
  if (!employee.value?.employee_no) return
  
  try {
    loading.value = true
    const updatedExperience = employee.value.work_experience.filter(item => item.id !== id)
    
    await updateEmployee({ work_experience: updatedExperience })
    ElMessage.success('删除工作经历成功')
  } catch (error) {
    console.error('删除工作经历失败:', error)
    ElMessage.error('删除工作经历失败')
  } finally {
    loading.value = false
  }
}

// 培训记录相关处理函数
const handleTrainingUpdate = (training: Training[]) => {
  if (employee.value) {
    updateEmployee({ training })
  }
}

const handleTrainingDelete = (trainingId: string) => {
  if (employee.value) {
    const training = employee.value.training.filter(
      item => item.id.toString() !== trainingId
    )
    updateEmployee({ training })
  }
}

// 职位变动相关处理函数
const handlePositionUpdate = (position_changes: PositionChangeType[]) => {
  if (employee.value) {
    updateEmployee({ position_changes })
  }
}

// 奖惩记录相关处理函数
const handleRewardUpdate = (reward_punishments: RewardPunishmentType[]) => {
  if (employee.value) {
    updateEmployee({ reward_punishments })
  }
}

// 附件相关处理函数
const handleAttachmentsUpdate = (files: File[]) => {
  console.log('添加附件:', files)
  // 实现文件上传辑
}

const handleAttachmentPreview = (attachment: Attachment) => {
  // 实现预览逻辑
  console.log('预览件:', attachment)
}

const handleAttachmentDownload = (attachment: Attachment) => {
  // 实现下载逻辑
  console.log('下载附件:', attachment)
}

const handleAttachmentDelete = (attachment: Attachment) => {
  if (employee.value) {
    const attachments = employee.value.attachments?.filter(
      item => item.id !== attachment.id
    ) || []
    updateEmployee({ attachments })
  }
}

// 处理培训记录相关操作
const handleAddTraining = async (training: Omit<Training, 'id'>) => {
  if (!employee.value?.employee_no) return
  
  try {
    loading.value = true
    const response = await addEmployeeTraining(employee.value.employee_no, training)
    
    if (response.code === 200) {
      ElMessage.success('添加培训记录成功')
      // 重新加载员工信息以获取最新数据
      await loadEmployee()
    } else {
      throw new Error(response.message || '添加失败')
    }
  } catch (error) {
    console.error('添加培训记录失败:', error)
    ElMessage.error(error instanceof Error ? error.message : '添加失败')
  } finally {
    loading.value = false
  }
}

const handleUpdateTraining = async (id: number, training: Omit<Training, 'id'>) => {
  if (!employee.value?.employee_no) return
  
  try {
    loading.value = true
    const response = await updateEmployeeTraining(employee.value.employee_no, id, training)
    
    if (response.code === 200) {
      ElMessage.success('更新培训记录成功')
      // 重新加载员工信息以获取最新数据
      await loadEmployee()
    } else {
      throw new Error(response.message || '更新失败')
    }
  } catch (error) {
    console.error('更新培训记录失败:', error)
    ElMessage.error(error instanceof Error ? error.message : '更新失败')
  } finally {
    loading.value = false
  }
}

const handleDeleteTraining = async (id: number) => {
  if (!employee.value?.employee_no) return
  
  try {
    loading.value = true
    const response = await deleteEmployeeTraining(employee.value.employee_no, id)
    
    if (response.code === 200) {
      ElMessage.success('删除培训记录成功')
      // 重新加载员工信息以获取最新数据
      await loadEmployee()
    } else {
      throw new Error(response.message || '删除失败')
    }
  } catch (error) {
    console.error('删除培训记录失败:', error)
    ElMessage.error(error instanceof Error ? error.message : '删除失败')
  } finally {
    loading.value = false
  }
}

// 添加生命周期钩子
onMounted(async () => {
  try {
    loading.value = true
    await Promise.all([
      loadDepartments(),
      loadEmployee()
    ])
  } catch (error) {
    console.error('初始化数据失败:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.employee-detail {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: bold;
}

.mt-20 {
  margin-top: 20px;
}

:deep(.el-descriptions) {
  margin-bottom: 20px;
}
</style> 
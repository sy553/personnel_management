<template>
  <el-descriptions :column="1" border>
    <template #title>
      <div class="section-title">
        <el-icon><Document /></el-icon>
        合同信息
        <div class="contract-buttons" v-if="employee.status === 'active'">
          <el-button 
            type="primary" 
            link 
            @click="handleAddContract"
          >
            <el-icon><Plus /></el-icon>
            添加合同
          </el-button>
        </div>
      </div>
    </template>
    <el-descriptions-item>
      <div v-if="!employee.contract" class="no-data">
        暂无合同信息
      </div>
      <div v-else>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="合同编号">{{ employee.contract.number }}</el-descriptions-item>
          <el-descriptions-item label="合同类型">{{ employee.contract.type }}</el-descriptions-item>
          <el-descriptions-item label="合同期限">{{ employee.contract.duration }}年</el-descriptions-item>
          <el-descriptions-item label="开始日期">{{ employee.contract.start_date }}</el-descriptions-item>
          <el-descriptions-item label="结束日期">{{ employee.contract.end_date }}</el-descriptions-item>
          <el-descriptions-item label="签订日期">{{ employee.contract.sign_date }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getContractStatusType(employee.contract.status)">
              {{ getContractStatusLabel(employee.contract.status) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        <div class="contract-actions mt-10">
          <el-button 
            type="primary" 
            link
            @click="handlePreviewContract"
          >
            预览合同
          </el-button>
          <el-button 
            type="primary" 
            link
            @click="handleDownloadContract"
          >
            下载合同
          </el-button>
        </div>
      </div>
    </el-descriptions-item>
  </el-descriptions>

  <!-- 合同表单对话框 -->
  <el-dialog
    v-model="contractDialogVisible"
    :title="contractFormMode === 'add' ? '添加合同' : '编辑合同'"
    width="500px"
    @close="handleDialogClose"
  >
    <el-form
      ref="contractFormRef"
      :model="contractForm"
      :rules="contractRules"
      label-width="100px"
    >
      <el-form-item label="合同编号" prop="number">
        <el-input v-model="contractForm.number" />
      </el-form-item>
      <el-form-item label="合同类型" prop="type">
        <el-select v-model="contractForm.type" placeholder="请选择合同类型">
          <el-option label="固定期限" value="fixed_term" />
          <el-option label="无固定期限" value="non_fixed_term" />
          <el-option label="实习" value="internship" />
          <el-option label="试用期" value="probation" />
        </el-select>
      </el-form-item>
      <el-form-item label="合同期限" prop="duration">
        <el-input-number v-model="contractForm.duration" :min="0" :max="100" />
      </el-form-item>
      <el-form-item label="开始日期" prop="start_date">
        <el-date-picker
          v-model="contractForm.start_date"
          type="date"
          placeholder="选择开始日期"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      <el-form-item label="结束日期" prop="end_date">
        <el-date-picker
          v-model="contractForm.end_date"
          type="date"
          placeholder="选择结束日期"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      <el-form-item label="签订日期" prop="sign_date">
        <el-date-picker
          v-model="contractForm.sign_date"
          type="date"
          placeholder="选择签订日期"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      <el-form-item label="合同状态" prop="status">
        <el-select v-model="contractForm.status" placeholder="请选择合同状态">
          <el-option label="生效中" value="active" />
          <el-option label="已到期" value="expired" />
          <el-option label="已终止" value="terminated" />
        </el-select>
      </el-form-item>
      <el-form-item label="合同文件" prop="file">
        <el-upload
          class="contract-upload"
          :auto-upload="false"
          :show-file-list="true"
          :limit="1"
          accept=".pdf"
          :on-change="handleFileChange"
          :on-exceed="handleExceed"
          :on-remove="handleRemove"
        >
          <template #trigger>
            <el-button type="primary">选择文件</el-button>
          </template>
          <template #tip>
            <div class="el-upload__tip">
              只能上传 PDF 文件
            </div>
          </template>
        </el-upload>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="contractDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="saving">
          确定
        </el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 合同预览对话框 -->
  <el-dialog
    v-model="previewVisible"
    title="合同预览"
    width="80%"
    class="preview-dialog"
  >
    <div class="preview-container">
      <iframe
        v-if="previewUrl"
        :src="previewUrl"
        class="preview-frame"
      ></iframe>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Document, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { Employee, Contract } from '@/types/employee'
import type { FormInstance } from 'element-plus'
import { previewEmployeeContract, downloadEmployeeContract } from '@/api/employee'
import { UploadFile } from 'element-plus'
import { addEmployeeContract, updateEmployeeContract } from '@/api/employee'

const props = defineProps<{
  employee: Employee
}>()

const emit = defineEmits<{
  (e: 'update:contract', contract: Contract): void
  (e: 'preview', url: string): void
  (e: 'download', contract: Contract): void
}>()

// 合同状态
const getContractStatusType = (status?: string) => {
  const typeMap: Record<string, string> = {
    active: 'success',
    expired: 'warning',
    terminated: 'danger'
  }
  return typeMap[status || ''] || 'info'
}

const getContractStatusLabel = (status?: string) => {
  const labelMap: Record<string, string> = {
    active: '生效中',
    expired: '已到期',
    terminated: '已终止'
  }
  return labelMap[status || ''] || '未知'
}

// 对话框状态
const contractDialogVisible = ref(false)
const contractFormMode = ref<'add' | 'edit'>('add')
const saving = ref(false)
const previewVisible = ref(false)
const previewUrl = ref('')

// 表单
const contractFormRef = ref<FormInstance>()
const contractForm = reactive({
  number: '',
  type: '',
  duration: 0,
  start_date: '',
  end_date: '',
  sign_date: '',
  status: 'active'
})

// 表单验证规则
const contractRules = {
  number: [{ required: true, message: '请输入合同编号', trigger: 'blur' }],
  type: [{ required: true, message: '请选择合同类型', trigger: 'change' }],
  duration: [{ required: true, message: '请输入合同期限', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }],
  sign_date: [{ required: true, message: '请选择签订日期', trigger: 'change' }],
  status: [{ required: true, message: '请选择合同状态', trigger: 'change' }]
}

// 文件上传相关
const contractFile = ref<File | null>(null)

const handleFileChange = (file: UploadFile) => {
  if (file.raw && file.raw.type === 'application/pdf') {
    contractFile.value = file.raw
  } else {
    ElMessage.warning('请上传 PDF 格式的文件')
    return false
  }
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个合同文件')
}

const handleRemove = () => {
  contractFile.value = null
}

// 处理添加合同
const handleAddContract = () => {
  contractFormMode.value = 'add'
  Object.assign(contractForm, {
    number: '',
    type: '',
    duration: 0,
    start_date: '',
    end_date: '',
    sign_date: '',
    status: 'active'
  })
  contractDialogVisible.value = true
}

// 处理对话框关闭
const handleDialogClose = () => {
  contractFormRef.value?.resetFields()
  contractFile.value = null
}

// 处理表单提交
const handleSubmit = async () => {
  if (!contractFormRef.value) return
  
  try {
    await contractFormRef.value.validate()
    saving.value = true
    
    // 检查所有必填字段
    const requiredFields = ['number', 'type', 'duration', 'start_date', 'end_date', 'sign_date', 'status'] as const
    type FormField = keyof typeof contractForm
    const missingFields = requiredFields.filter(field => !contractForm[field as FormField])
    if (missingFields.length > 0) {
      throw new Error(`缺少必填字段: ${missingFields.join(', ')}`)
    }
    
    // 构造表单数据
    const formData = new FormData()
    formData.append('number', contractForm.number.trim())
    formData.append('type', contractForm.type)
    formData.append('duration', contractForm.duration.toString())
    formData.append('start_date', contractForm.start_date)
    formData.append('end_date', contractForm.end_date)
    formData.append('sign_date', contractForm.sign_date)
    formData.append('status', contractForm.status)
    
    if (contractFile.value) {
      formData.append('file', contractFile.value)
    }
    
    // 打印表单数据，用于调试
    formData.forEach((value, key) => {
      console.log(`${key}:`, value)
    })
    
    let response
    if (contractFormMode.value === 'add') {
      response = await addEmployeeContract(props.employee.employee_no, formData)
    } else {
      if (!props.employee.contract?.id) {
        throw new Error('合同ID不存在')
      }
      response = await updateEmployeeContract(props.employee.employee_no, props.employee.contract.id, formData)
    }
    
    // 触发更新事件，确保只传递合同数据部分
    if (response && response.code === 200 && response.data) {
      emit('update:contract', {
        id: response.data.id,
        number: response.data.number,
        type: response.data.type,
        duration: response.data.duration,
        start_date: response.data.start_date,
        end_date: response.data.end_date,
        sign_date: response.data.sign_date,
        status: response.data.status,
        file_url: response.data.file_url
      })
      ElMessage.success(`${contractFormMode.value === 'add' ? '添加' : '更新'}合同成功`)
      contractDialogVisible.value = false
    } else {
      throw new Error(response?.message || '保存失败')
    }
  } catch (error: any) {
    console.error('保存合同信息失败:', error)
    // 显示后端返回的具体错误信息
    const errorMessage = error.response?.data?.message || error.message || '保存失败'
    if (error.response?.data?.detail) {
      console.error('错误详情:', error.response.data.detail)
    }
    ElMessage.error(errorMessage)
  } finally {
    saving.value = false
  }
}

// 处理合同预览
const handlePreviewContract = async () => {
  if (!props.employee.contract) {
    ElMessage.warning('暂无合同文件')
    return
  }
  
  try {
    const response = await previewEmployeeContract(props.employee.employee_no)
    const blob = new Blob([response.data], { type: 'application/pdf' })
    previewUrl.value = window.URL.createObjectURL(blob)
    previewVisible.value = true
  } catch (error) {
    console.error('预览合同失败:', error)
    ElMessage.error('预览合同失败')
  }
}

// 处理合同下载
const handleDownloadContract = async () => {
  if (!props.employee.contract) {
    ElMessage.warning('暂无合同文件')
    return
  }
  
  try {
    const response = await downloadEmployeeContract(props.employee.employee_no)
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `contract_${props.employee.employee_no}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('下载合同失败:', error)
    ElMessage.error('下载合同失败')
  }
}
</script>

<style scoped>
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: bold;
}

.contract-buttons {
  margin-left: auto;
}

.contract-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 10px;
}

.no-data {
  text-align: center;
  color: #909399;
  padding: 20px 0;
}

.preview-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.preview-container {
  height: 600px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
}

.preview-frame {
  width: 100%;
  height: 100%;
  border: none;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.mt-10 {
  margin-top: 10px;
}
</style> 
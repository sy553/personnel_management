<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="500px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      style="max-width: 460px"
    >
      <el-form-item label="合同类型" prop="contract_type">
        <el-select v-model="form.contract_type" style="width: 100%">
          <el-option label="正式合同" value="正式合同" />
          <el-option label="实习合同" value="实习合同" />
          <el-option label="临时合同" value="临时合同" />
          <el-option label="项目合同" value="项目合同" />
        </el-select>
      </el-form-item>
      <el-form-item label="开始日期" prop="start_date">
        <el-date-picker
          v-model="form.start_date"
          type="date"
          style="width: 100%"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      <el-form-item label="结束日期" prop="end_date">
        <el-date-picker
          v-model="form.end_date"
          type="date"
          style="width: 100%"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      <el-form-item label="合同状态" prop="status">
        <el-select v-model="form.status" style="width: 100%">
          <el-option label="生效中" value="生效中" />
          <el-option label="已到期" value="已到期" />
          <el-option label="已终止" value="已终止" />
        </el-select>
      </el-form-item>
      <el-form-item label="备注" prop="remarks">
        <el-input
          v-model="form.remarks"
          type="textarea"
          :rows="2"
        />
      </el-form-item>
      <el-form-item label="合同文件" prop="file">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          accept=".pdf,.doc,.docx"
          :on-change="handleFileChange"
          :on-exceed="handleExceed"
          :on-remove="handleRemove"
        >
          <template #trigger>
            <el-button type="primary">选择文件</el-button>
          </template>
          <template #tip>
            <div class="el-upload__tip">
              只能上传 PDF/Word 文件
            </div>
          </template>
        </el-upload>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          确定
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, UploadProps, UploadInstance } from 'element-plus'
import type { ContractForm } from '@/types/employee'

interface Props {
  visible: boolean
  title?: string
  initialData?: Partial<ContractForm>
}

const props = withDefaults(defineProps<Props>(), {
  title: '添加合同',
  initialData: () => ({})
})

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'submit', form: ContractForm): void
}>()

const loading = ref(false)
const formRef = ref<FormInstance>()
const uploadRef = ref<UploadInstance>()

const form = ref<ContractForm>({
  contract_type: '',
  start_date: '',
  end_date: '',
  status: '',
  remarks: '',
  file: undefined
})

const rules = {
  contract_type: [{ required: true, message: '请选择合同类型', trigger: 'change' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }],
  status: [{ required: true, message: '请选择合同状态', trigger: 'change' }],
  file: [{ required: true, message: '请上传合同文件', trigger: 'change' }]
}

// 处理文件变更
const handleFileChange: UploadProps['onChange'] = (uploadFile) => {
  if (uploadFile.raw) {
    form.value.file = uploadFile.raw
  }
}

// 处理文件超出限制
const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

// 处理文件移除
const handleRemove = () => {
  form.value.file = undefined
}

// 处理对话框关闭
const handleClose = () => {
  formRef.value?.resetFields()
  uploadRef.value?.clearFiles()
  form.value = {
    contract_type: '',
    start_date: '',
    end_date: '',
    status: '',
    remarks: '',
    file: undefined
  }
  emit('update:visible', false)
}

// 处理表单提交
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate((valid, fields) => {
    if (valid) {
      emit('submit', form.value)
    } else {
      console.error('表单验证失败:', fields)
    }
  })
}

// 监听 props 变化，更新表单数据
watch(
  () => props.initialData,
  (newVal) => {
    if (newVal) {
      form.value = {
        ...form.value,
        ...newVal
      }
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-upload-list) {
  width: 100%;
}

:deep(.el-upload) {
  width: 100%;
}

:deep(.el-upload-list__item) {
  transition: none !important;
}
</style> 
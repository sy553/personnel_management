<template>
  <el-descriptions border>
    <template #title>
      <div class="section-title">
        <el-icon><Trophy /></el-icon>
        培训记录
        <el-button
          type="primary"
          size="small"
          @click="handleAdd"
          :loading="loading"
        >
          添加培训记录
        </el-button>
      </div>
    </template>
    <el-descriptions-item>
      <div v-if="!employee.training_records?.length" class="no-data">
        暂无培训记录
      </div>
      <el-table v-else :data="employee.training_records" style="width: 100%">
        <el-table-column prop="training_name" label="培训名称" min-width="150" />
        <el-table-column prop="training_type" label="培训类型" width="120" />
        <el-table-column label="培训时间" width="200">
          <template #default="{ row }">
            {{ row.start_date }} 至 {{ row.end_date }}
          </template>
        </el-table-column>
        <el-table-column prop="trainer" label="培训讲师" width="120" />
        <el-table-column prop="result" label="培训结果" width="100" />
        <el-table-column prop="remarks" label="备注" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              @click="handleEdit(row)"
              :loading="loading"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              link
              @click="handleDelete(row)"
              :loading="loading"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-descriptions-item>
  </el-descriptions>

  <!-- 培训记录表单对话框 -->
  <el-dialog
    v-model="dialogVisible"
    :title="formMode === 'add' ? '添加培训记录' : '编辑培训记录'"
    width="500px"
    @close="handleDialogClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      style="max-width: 460px"
    >
      <el-form-item label="培训名称" prop="training_name">
        <el-input v-model="form.training_name" />
      </el-form-item>
      <el-form-item label="培训类型" prop="training_type">
        <el-select v-model="form.training_type" style="width: 100%">
          <el-option label="入职培训" value="入职培训" />
          <el-option label="技能培训" value="技能培训" />
          <el-option label="管理培训" value="管理培训" />
          <el-option label="专业培训" value="专业培训" />
          <el-option label="其他培训" value="其他培训" />
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
      <el-form-item label="培训讲师" prop="trainer">
        <el-input v-model="form.trainer" />
      </el-form-item>
      <el-form-item label="培训结果" prop="result">
        <el-select v-model="form.result" style="width: 100%">
          <el-option label="通过" value="通过" />
          <el-option label="未通过" value="未通过" />
          <el-option label="优秀" value="优秀" />
        </el-select>
      </el-form-item>
      <el-form-item label="备注" prop="remarks">
        <el-input
          v-model="form.remarks"
          type="textarea"
          :rows="2"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          确定
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Trophy } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { Employee, TrainingRecord } from '@/types/employee'

const props = defineProps<{
  employee: Employee
}>()

const emit = defineEmits<{
  (e: 'add', training: Omit<TrainingRecord, 'id' | 'employee_no'>): void
  (e: 'update', id: number, training: Omit<TrainingRecord, 'id' | 'employee_no'>): void
  (e: 'delete', id: number): void
}>()

const loading = ref(false)
const dialogVisible = ref(false)
const formMode = ref<'add' | 'edit'>('add')
const currentId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const form = ref({
  training_name: '',
  training_type: '',
  start_date: '',
  end_date: '',
  trainer: '',
  result: '',
  remarks: ''
})

const rules: FormRules = {
  training_name: [{ required: true, message: '请输入培训名称', trigger: 'blur' }],
  training_type: [{ required: true, message: '请选择培训类型', trigger: 'change' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }],
  trainer: [{ required: true, message: '请输入培训讲师', trigger: 'blur' }],
  result: [{ required: true, message: '请选择培训结果', trigger: 'change' }]
}

// 处理添加按钮点击
const handleAdd = () => {
  formMode.value = 'add'
  currentId.value = null
  form.value = {
    training_name: '',
    training_type: '',
    start_date: '',
    end_date: '',
    trainer: '',
    result: '',
    remarks: ''
  }
  dialogVisible.value = true
}

// 处理编辑按钮点击
const handleEdit = (row: TrainingRecord) => {
  formMode.value = 'edit'
  form.value = {
    training_name: row.training_name,
    training_type: row.training_type,
    start_date: row.start_date,
    end_date: row.end_date,
    trainer: row.trainer,
    result: row.result,
    remarks: row.remarks || ''
  }
  currentId.value = row.id
  dialogVisible.value = true
}

// 处理删除按钮点击
const handleDelete = (row: TrainingRecord) => {
  ElMessageBox.confirm(
    '确定要删除这条培训记录吗？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(() => {
      emit('delete', row.id)
    })
    .catch(() => {
      // 用户点击取消按钮
    })
}

// 处理对话框关闭
const handleDialogClose = () => {
  formRef.value?.resetFields()
}

// 处理表单提交
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate((valid, fields) => {
    if (valid) {
      const trainingData = {
        training_name: form.value.training_name,
        training_type: form.value.training_type,
        start_date: form.value.start_date,
        end_date: form.value.end_date,
        trainer: form.value.trainer,
        result: form.value.result,
        remarks: form.value.remarks || undefined
      }
      
      if (formMode.value === 'add') {
        emit('add', trainingData)
      } else if (currentId.value !== null) {
        emit('update', currentId.value, trainingData)
      }
      
      dialogVisible.value = false
    } else {
      console.error('表单验证失败:', fields)
    }
  })
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

.section-title .el-button {
  margin-left: auto;
}

.no-data {
  text-align: center;
  color: #909399;
  padding: 24px;
}

:deep(.el-descriptions__body) {
  background-color: transparent;
}
</style> 
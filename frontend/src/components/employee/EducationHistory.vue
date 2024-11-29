<template>
  <el-descriptions border>
    <template #title>
      <div class="section-title">
        <el-icon><School /></el-icon>
        教育经历
        <el-button
          type="primary"
          size="small"
          @click="handleAdd"
          :loading="loading"
        >
          添加教育经历
        </el-button>
      </div>
    </template>
    <el-descriptions-item>
      <div v-if="!employee.education_history?.length" class="no-data">
        暂无教育经历记录
      </div>
      <el-table v-else :data="employee.education_history" style="width: 100%">
        <el-table-column prop="start_date" label="开始日期" width="120" />
        <el-table-column prop="end_date" label="结束日期" width="120" />
        <el-table-column prop="school" label="学校" />
        <el-table-column prop="major" label="专业" />
        <el-table-column prop="degree" label="学历" width="100" />
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

  <!-- 教育经历表单对话框 -->
  <el-dialog
    v-model="dialogVisible"
    :title="formMode === 'add' ? '添加教育经历' : '编辑教育经历'"
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
      <el-form-item label="学校" prop="school">
        <el-input v-model="form.school" />
      </el-form-item>
      <el-form-item label="专业" prop="major">
        <el-input v-model="form.major" />
      </el-form-item>
      <el-form-item label="学历" prop="degree">
        <el-select v-model="form.degree" style="width: 100%">
          <el-option label="高中" value="高中" />
          <el-option label="专科" value="专科" />
          <el-option label="本科" value="本科" />
          <el-option label="硕士" value="硕士" />
          <el-option label="博士" value="博士" />
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
import { School } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { Employee, EducationHistory } from '@/types/employee'

const props = defineProps<{
  employee: Employee
}>()

const emit = defineEmits<{
  (e: 'add', education: Omit<EducationHistory, 'id' | 'employee_no'>): void
  (e: 'update', id: number, education: Omit<EducationHistory, 'id' | 'employee_no'>): void
  (e: 'delete', id: number): void
}>()

const loading = ref(false)
const dialogVisible = ref(false)
const formMode = ref<'add' | 'edit'>('add')
const currentId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const form = ref({
  school: '',
  major: '',
  degree: '',
  start_date: '',
  end_date: '',
  remarks: ''
})

const rules: FormRules = {
  school: [{ required: true, message: '请输入学校名称', trigger: 'blur' }],
  major: [{ required: true, message: '请输入专业名称', trigger: 'blur' }],
  degree: [{ required: true, message: '请选择学历', trigger: 'change' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }]
}

// 处理添加按钮点击
const handleAdd = () => {
  formMode.value = 'add'
  currentId.value = null
  form.value = {
    school: '',
    major: '',
    degree: '',
    start_date: '',
    end_date: '',
    remarks: ''
  }
  dialogVisible.value = true
}

// 处理编辑按钮点击
const handleEdit = (row: EducationHistory) => {
  formMode.value = 'edit'
  form.value = {
    school: row.school,
    major: row.major,
    degree: row.degree,
    start_date: row.start_date,
    end_date: row.end_date,
    remarks: row.remarks || ''
  }
  currentId.value = row.id
  dialogVisible.value = true
}

// 处理删除按钮点击
const handleDelete = (row: EducationHistory) => {
  ElMessageBox.confirm(
    '确定要删除这条教育经历记录吗？',
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
      const educationData = {
        school: form.value.school,
        major: form.value.major,
        degree: form.value.degree,
        start_date: form.value.start_date,
        end_date: form.value.end_date,
        remarks: form.value.remarks || undefined
      }
      
      if (formMode.value === 'add') {
        emit('add', educationData)
      } else if (currentId.value !== null) {
        emit('update', currentId.value, educationData)
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
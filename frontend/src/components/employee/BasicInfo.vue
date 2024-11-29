<template>
  <div class="basic-info">
    <el-descriptions :column="3" border>
      <template #title>
        <div class="section-title">
          <el-icon><User /></el-icon>
          基本信息
          <div class="action-buttons" v-if="employee.status === 'active'">
            <el-button type="primary" link @click="handleEdit">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
          </div>
        </div>
      </template>
      
      <el-descriptions-item label="工号">{{ employee.employee_no }}</el-descriptions-item>
      <el-descriptions-item label="姓名">{{ employee.name }}</el-descriptions-item>
      <el-descriptions-item label="性别">{{ genderLabel[employee.gender] }}</el-descriptions-item>
      <el-descriptions-item label="出生日期">{{ employee.birth_date }}</el-descriptions-item>
      <el-descriptions-item label="手机号">{{ employee.phone }}</el-descriptions-item>
      <el-descriptions-item label="邮箱">{{ employee.email }}</el-descriptions-item>
      <el-descriptions-item label="身份证号">{{ employee.id_card }}</el-descriptions-item>
      <el-descriptions-item label="部门">{{ employee.department?.name }}</el-descriptions-item>
      <el-descriptions-item label="职位">{{ employee.position }}</el-descriptions-item>
      <el-descriptions-item label="状态">
        <el-tag :type="employee.status === 'active' ? 'success' : 'info'">
          {{ employee.status === 'active' ? '在职' : '离职' }}
        </el-tag>
      </el-descriptions-item>
    </el-descriptions>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="编辑基本信息"
      width="500px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="form.gender">
            <el-radio label="male">男</el-radio>
            <el-radio label="female">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="出生日期" prop="birth_date">
          <el-date-picker
            v-model="form.birth_date"
            type="date"
            placeholder="选择出生日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="身份证号" prop="id_card">
          <el-input v-model="form.id_card" />
        </el-form-item>
        <el-form-item label="部门" prop="department">
          <el-select v-model="form.department" placeholder="请选择部门">
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="职位" prop="position">
          <el-input v-model="form.position" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="saving">
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Edit } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import type { Employee, Department } from '@/types/employee'
import { getDepartmentList } from '@/api/common'
import type { ApiResponse } from '@/types/api'

interface DepartmentListResponse {
  departments: Department[]
  total: number
}

const props = defineProps<{
  employee: Employee
}>()

const emit = defineEmits<{
  (e: 'update:basic', data: Partial<Employee>): void
}>()

const genderLabel: Record<'male' | 'female', string> = {
  male: '男',
  female: '女'
}

// 对话框状态
const dialogVisible = ref(false)
const saving = ref(false)
const formRef = ref<FormInstance>()
const departments = ref<Department[]>([])

const form = reactive({
  name: '',
  gender: 'male' as const,
  birth_date: '',
  phone: '',
  email: '',
  id_card: '',
  department: null as number | null,
  position: ''
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  birth_date: [{ required: true, message: '请选择出生日期', trigger: 'change' }],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  id_card: [
    { required: true, message: '请输入身份证号', trigger: 'blur' },
    { pattern: /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/, message: '请输入正确的身份证号', trigger: 'blur' }
  ],
  department: [{ required: true, message: '请选择部门', trigger: 'change' }],
  position: [{ required: true, message: '请输入职位', trigger: 'blur' }]
}

// 加载部门列表
const loadDepartments = async () => {
  try {
    const response = await getDepartmentList()
    if (response.data.code === 200) {
      departments.value = response.data.data.departments
      console.log('部门列表:', departments.value)
    }
  } catch (error) {
    console.error('加载部门列表失败:', error)
    ElMessage.error('加载部门列表失败')
  }
}

const handleEdit = () => {
  // 先加载部门列表
  loadDepartments()
  
  Object.assign(form, {
    name: props.employee.name,
    gender: props.employee.gender,
    birth_date: props.employee.birth_date,
    phone: props.employee.phone,
    email: props.employee.email,
    id_card: props.employee.id_card,
    department: props.employee.department?.id || null,
    position: props.employee.position
  })
  dialogVisible.value = true
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    // 获取选中的部门
    const selectedDepartment = departments.value.find(d => d.id === form.department)
    
    // 准备更新的数据
    const updateData: Partial<Employee> = {
      name: form.name,
      gender: form.gender,
      birth_date: form.birth_date,
      phone: form.phone,
      email: form.email,
      id_card: form.id_card,
      position: form.position,
      department: selectedDepartment || undefined
    }
    
    // 过滤掉空值
    Object.keys(updateData).forEach(key => {
      if (updateData[key as keyof typeof updateData] === undefined) {
        delete updateData[key as keyof typeof updateData]
      }
    })
    
    emit('update:basic', updateData)
    dialogVisible.value = false
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

onMounted(() => {
  loadDepartments()
})
</script>

<style scoped>
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: bold;
}

.action-buttons {
  margin-left: auto;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 
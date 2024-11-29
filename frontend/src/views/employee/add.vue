<template>
  <div class="employee-add">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>新增员工</span>
        </div>
      </template>
      
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="100px"
        class="employee-form"
      >
        <!-- 基本信息 -->
        <div class="form-section">
          <h3>基本信息</h3>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="工号" prop="employee_no" required>
                <el-input 
                  v-model="formData.employee_no" 
                  placeholder="请输入工号" 
                  maxlength="20"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="姓名" prop="name">
                <el-input v-model="formData.name" placeholder="请输入姓名" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="性别" prop="gender">
                <el-select v-model="formData.gender" placeholder="请选择性别">
                  <el-option label="男" value="male" />
                  <el-option label="女" value="female" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="出生日期" prop="birth_date">
                <el-date-picker
                  v-model="formData.birth_date"
                  type="date"
                  placeholder="选择日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="手机号" prop="phone">
                <el-input v-model="formData.phone" placeholder="请输入手机号" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="邮箱" prop="email">
                <el-input v-model="formData.email" placeholder="请输入邮箱" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="身份证号" prop="id_card">
                <el-input v-model="formData.id_card" placeholder="请输入身份证号" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 工作信息 -->
        <div class="form-section">
          <h3>工作信息</h3>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="部门" prop="department_id">
                <el-select v-model="formData.department_id" placeholder="请选择部门">
                  <el-option
                    v-for="item in departmentList"
                    :key="item.id"
                    :label="item.name"
                    :value="item.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="职位" prop="position">
                <el-input v-model="formData.position" placeholder="请输入职位" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="入职日期" prop="entry_date">
                <el-date-picker
                  v-model="formData.entry_date"
                  type="date"
                  placeholder="选择日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="基本工资" prop="base_salary">
                <el-input-number 
                  v-model="formData.base_salary" 
                  :min="0" 
                  :precision="2" 
                  :step="1000"
                  placeholder="请输入基本工资"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="银行账号" prop="bank_account">
                <el-input v-model="formData.bank_account" placeholder="请输入银行账号" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="开户银行" prop="bank_name">
                <el-input v-model="formData.bank_name" placeholder="请输入开户银行" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 备注 -->
        <div class="form-section">
          <h3>其他信息</h3>
          <el-row>
            <el-col :span="24">
              <el-form-item label="备注" prop="notes">
                <el-input
                  v-model="formData.notes"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入备注信息"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 表单操作 -->
        <div class="form-actions">
          <el-button @click="handleCancel">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            保存
          </el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { addEmployee, getDepartmentList } from '@/api/employee'
import type { EmployeeForm, Department } from '@/api/employee'

const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)
const departmentList = ref<Department[]>([])

// 表单数据
const formData = reactive<EmployeeForm>({
  employee_no: '',      // 工号
  name: '',            // 姓名
  gender: '',          // 性别
  birth_date: '',      // 出生日期
  phone: '',           // 手机号
  email: '',           // 邮箱
  id_card: '',         // 身份证号
  department_id: 0,    // 部门ID
  position: '',        // 职位
  entry_date: '',      // 入职日期
  base_salary: 0,      // 基本工资
  bank_account: '',    // 银行账号
  bank_name: '',       // 开户银行
  notes: '',           // 备注
  status: 'active'     // 状态
})

// 表单验证规则
const rules = reactive<FormRules>({
  employee_no: [
    { required: true, message: '请输入工号', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ],
  birth_date: [
    { required: true, message: '请选择出生日期', trigger: 'change' }
  ],
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
  department_id: [
    { required: true, message: '请选择部门', trigger: 'change' }
  ],
  position: [
    { required: true, message: '请输入职位', trigger: 'blur' }
  ],
  entry_date: [
    { required: true, message: '请选择入职日期', trigger: 'change' }
  ],
  base_salary: [
    { required: true, message: '请输入基本工资', trigger: 'blur' }
  ],
  bank_account: [
    { required: true, message: '请输入银行账号', trigger: 'blur' }
  ],
  bank_name: [
    { required: true, message: '请输入开户银行', trigger: 'blur' }
  ]
})

// 获取部门列表
const fetchDepartmentList = async () => {
  try {
    const res = await getDepartmentList()
    departmentList.value = res.data?.departments || []
  } catch (error) {
    console.error('获取部门列表失败:', error)
    ElMessage.error('获取部门列表失败')
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    await addEmployee(formData)
    ElMessage.success('添加成功')
    router.push('/employee/list')
  } catch (error: any) {
    const errorMsg = error.response?.data?.error
    if (errorMsg === 'ID card number already exists') {
      ElMessage.error('身份证号已存在，请检查后重试')
    } else {
      ElMessage.error('添加失败：' + (errorMsg || '未知错误'))
    }
  }
}

// 取消
const handleCancel = () => {
  router.back()
}

onMounted(() => {
  fetchDepartmentList()
})
</script>

<style scoped>
.employee-add {
  padding: 20px;
}

.form-section {
  margin-bottom: 30px;
}

.form-section h3 {
  margin: 0 0 20px;
  padding-left: 10px;
  border-left: 4px solid #409EFF;
  font-size: 16px;
}

.form-actions {
  margin-top: 30px;
  text-align: center;
}

.employee-form {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
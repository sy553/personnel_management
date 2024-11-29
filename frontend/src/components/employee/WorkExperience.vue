<template>
  <el-descriptions :column="1" border>
    <template #title>
      <div class="section-title">
        <el-icon><Collection /></el-icon>
        工作经历
        <div class="title-actions">
          <el-button
            v-if="employee.status === 'active'"
            type="primary"
            link
            @click="handleAdd"
          >
            <el-icon><Plus /></el-icon>
            添加工作经历
          </el-button>
        </div>
      </div>
    </template>
    <el-descriptions-item>
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="3" animated />
      </div>
      <div v-else>
        <div v-if="!experienceList?.length" class="no-data">
          暂无工作经历记录
        </div>
        <el-table v-else :data="experienceList" style="width: 100%">
          <el-table-column prop="start_date" label="开始日期" width="120" />
          <el-table-column prop="end_date" label="结束日期" width="120" />
          <el-table-column prop="company" label="公司名称" />
          <el-table-column prop="position" label="职位" width="150" />
          <el-table-column prop="description" label="工作描述" show-overflow-tooltip />
          <el-table-column 
            label="操作" 
            width="150" 
            fixed="right"
            v-if="employee.status === 'active'"
          >
            <template #default="{ row }">
              <el-button type="primary" link @click="handleEdit(row)">
                编辑
              </el-button>
              <el-button type="danger" link @click="handleDelete(row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-descriptions-item>
  </el-descriptions>

  <!-- 工作经历表单对话框 -->
  <el-dialog
    v-model="dialogVisible"
    :title="formMode === 'add' ? '添加工作经历' : '编辑工作经历'"
    width="500px"
    @close="handleDialogClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="开始日期" prop="start_date">
        <el-date-picker
          v-model="form.start_date"
          type="date"
          placeholder="选择开始日期"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      <el-form-item label="结束日期" prop="end_date">
        <el-date-picker
          v-model="form.end_date"
          type="date"
          placeholder="选择结束日期"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      <el-form-item label="公司名称" prop="company">
        <el-input v-model="form.company" />
      </el-form-item>
      <el-form-item label="职位" prop="position">
        <el-input v-model="form.position" />
      </el-form-item>
      <el-form-item label="工作描述" prop="description">
        <el-input 
          v-model="form.description" 
          type="textarea" 
          :rows="3"
        />
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
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Collection, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'
import type { Employee, WorkExperience } from '@/types/employee'

const props = defineProps<{
  employee: Employee
}>()

const emit = defineEmits<{
  (e: 'add', experience: Omit<WorkExperience, 'id'>): void
  (e: 'update', id: number, experience: Omit<WorkExperience, 'id'>): void
  (e: 'delete', id: number): void
}>()

// 状态相关
const dialogVisible = ref(false)
const saving = ref(false)
const currentId = ref<number | null>(null)
const formRef = ref<FormInstance>()

// 表单数据
const form = reactive({
  company: '',
  position: '',
  start_date: '',
  end_date: '',
  description: ''
})

// 表单验证规则
const rules = {
  company: [{ required: true, message: '请输入公司名称', trigger: 'blur' }],
  position: [{ required: true, message: '请输入职位', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }]
}

// 处理添加
const handleAdd = () => {
  currentId.value = null
  Object.assign(form, {
    company: '',
    position: '',
    start_date: '',
    end_date: '',
    description: ''
  })
  dialogVisible.value = true
}

// 处理编辑
const handleEdit = (row: WorkExperience) => {
  Object.assign(form, {
    company: row.company,
    position: row.position,
    start_date: row.start_date,
    end_date: row.end_date,
    description: row.description || ''
  })
  currentId.value = row.id
  dialogVisible.value = true
}

// 处理删除
const handleDelete = async (row: WorkExperience) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条工作经历吗？',
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    emit('delete', row.id)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除工作经历失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 处理表单提交
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    saving.value = true
    
    const experienceData = {
      company: form.company,
      position: form.position,
      start_date: form.start_date,
      end_date: form.end_date,
      description: form.description || undefined
    }
    
    if (currentId.value === null) {
      emit('add', experienceData)
    } else {
      emit('update', currentId.value, experienceData)
    }
    
    dialogVisible.value = false
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    saving.value = false
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

.title-actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.loading-container {
  padding: 20px;
}

.no-data {
  text-align: center;
  color: #909399;
  padding: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-button--link) {
  padding: 4px 8px;
}

:deep(.el-form-item__content) {
  flex-wrap: nowrap;
}
</style> 
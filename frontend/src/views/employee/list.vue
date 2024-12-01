<template>
  <div class="employee-list">
    <!-- 搜索表单 -->
    <el-form :inline="true" class="search-form">
      <el-form-item label="姓名">
        <el-input
          v-model="searchForm.name"
          placeholder="请输入姓名"
          clearable
        />
      </el-form-item>
      <el-form-item label="部门">
        <el-select
          v-model="searchForm.department"
          placeholder="请选择部门"
          clearable
        >
          <el-option
            v-for="dept in departments"
            :key="dept.id"
            :label="dept.name"
            :value="dept.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select
          v-model="searchForm.status"
          placeholder="请选择状态"
          clearable
        >
          <el-option label="在职" value="active" />
          <el-option label="离职" value="inactive" />
          <el-option label="已退休" value="resigned" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="handleReset">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </el-form-item>
    </el-form>

    <!-- 工具栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增员工
      </el-button>
    </div>

    <!-- 员工列表 -->
    <el-table
      v-loading="loading"
      :data="employeeList"
      style="width: 100%"
      border
    >
      <el-table-column prop="employee_no" label="工号" width="120" />
      <el-table-column prop="name" label="姓名" width="120" />
      <el-table-column prop="department.name" label="部门" width="120" />
      <el-table-column prop="position" label="职位" width="120" />
      <el-table-column prop="phone" label="手机号" width="120" />
      <el-table-column prop="email" label="邮箱" min-width="180" />
      <el-table-column prop="entry_date" label="入职日期" width="120" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="handleEdit(row)">
            编辑
          </el-button>
          <el-button type="primary" link @click="handleView(row)">
            详情
          </el-button>
          <el-button 
            v-if="row.status === 'active'"
            type="danger" 
            link 
            @click="handleDelete(row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Edit, Delete, View } from '@element-plus/icons-vue'
import { getEmployeeList } from '@/api/employee'
import type { EmployeeListParams } from '@/api/employee'
import { getDepartmentList } from '@/api/department'
import type { Employee, Department } from '@/types/employee'

const router = useRouter()
const loading = ref(false)
const departments = ref<Department[]>([])

// 分页参数
const pagination = ref({
  page: 1,
  pageSize: 10,
  total: 0
})

// 搜索参数
const searchForm = ref({
  name: '',
  department: undefined as number | undefined,
  status: undefined as string | undefined
})

// 员工列表
const employeeList = ref<Employee[]>([])

// 加载部门列表
const loadDepartments = async () => {
  try {
    const response = await getDepartmentList()
    if (response.data.code === 200) {
      departments.value = response.data.data.departments
      console.log('部门列表:', departments.value)
    } else {
      ElMessage.error(response.data.message || '加载部门列表失败')
    }
  } catch (error: any) {
    console.error('加载部门列表失败:', error)
    ElMessage.error(error.response?.data?.message || '加载部门列表失败')
  }
}

// 加载员工列表
const loadEmployeeList = async () => {
  try {
    loading.value = true
    
    const params: EmployeeListParams = {
      page: pagination.value.page.toString(),
      pageSize: pagination.value.pageSize.toString()
    }
    
    // 添加搜索参数（如果有值）
    if (searchForm.value.name.trim()) {
      params.name = searchForm.value.name.trim()
    }
    
    if (typeof searchForm.value.department === 'number') {
      params.department = searchForm.value.department.toString()
    }
    
    if (searchForm.value.status) {
      params.status = searchForm.value.status
    }
    
    console.log('请求参数:', params)
    
    const response = await getEmployeeList(params)
    console.log('API完整响应:', JSON.stringify(response, null, 2))
    
    if (response.code === 200 && response.data) {
      // 检查数据结构
      console.log('数据结构:', {
        hasItems: 'items' in response.data,
        hasData: 'data' in response.data,
        dataType: response.data.data ? typeof response.data.data : 'undefined',
        totalValue: response.data.total
      })
      
      // 根据实际数据结构获取列表数据
      employeeList.value = response.data.data || response.data.items || []
      pagination.value.total = response.data.total || 0
      
      console.log('最终员工列表:', employeeList.value)
      console.log('最终总数:', pagination.value.total)
    } else {
      ElMessage.error(response.message || '加载失败')
    }
  } catch (error: any) {
    console.error('加载员工列表失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 获取状态标签
const getStatusLabel = (status: string) => {
  const statusMap: Record<string, string> = {
    active: '在职',
    inactive: '离职',
    resigned: '已退休'
  }
  return statusMap[status] || status
}

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    active: 'success',
    inactive: 'info',
    resigned: 'danger'
  }
  return typeMap[status] || ''
}

// 处理搜索
const handleSearch = () => {
  pagination.value.page = 1
  loadEmployeeList()
}

// 处理重置
const handleReset = () => {
  searchForm.value = {
    name: '',
    department: undefined,
    status: undefined
  }
  pagination.value.page = 1
  loadEmployeeList()
}

// 处理页码变化
const handlePageChange = (page: number) => {
  pagination.value.page = page
  loadEmployeeList()
}

// 处理每页条数变化
const handleSizeChange = (size: number) => {
  pagination.value.pageSize = size
  pagination.value.page = 1
  loadEmployeeList()
}

// 处理添加员工
const handleAdd = () => {
  router.push('/employee/add')
}

// 处理查看详情
const handleView = (row: Employee) => {
  router.push(`/employee/detail1/${row.employee_no}`)
}

// 处理编辑
const handleEdit = (row: Employee) => {
  router.push(`/employee/edit/${row.employee_no}`)
}

// 处理删除
const handleDelete = async (row: Employee) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除该员工吗？此操作不可恢复',
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: 实现删除功能
    ElMessage.success('删除成功')
    loadEmployeeList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除员工失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 初始化
onMounted(() => {
  loadDepartments()
  loadEmployeeList()
})
</script>

<style scoped>
.employee-list {
  padding: 20px;
}

.search-form {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #fff;
  border-radius: 4px;
}

.toolbar {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style> 
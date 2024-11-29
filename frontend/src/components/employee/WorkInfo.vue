<template>
  <el-descriptions
    :column="3"
    border
  >
    <template #title>
      <div class="section-title">
        <el-icon><Briefcase /></el-icon>
        工作信息
      </div>
    </template>
    <el-descriptions-item label="部门">{{ employee.department?.name }}</el-descriptions-item>
    <el-descriptions-item label="职位">{{ employee.position }}</el-descriptions-item>
    <el-descriptions-item label="入职日期">{{ employee.hire_date }}</el-descriptions-item>
    <el-descriptions-item label="员工状态">{{ employee.status }}</el-descriptions-item>
    <el-descriptions-item label="备注" :span="2">{{ employee.remarks || '-' }}</el-descriptions-item>
  </el-descriptions>
</template>

<script setup lang="ts">
import { Briefcase } from '@element-plus/icons-vue'
import type { Employee } from '@/types/employee'

defineProps<{
  employee: Employee
}>()
</script>

<style scoped>
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: bold;
}
</style> 
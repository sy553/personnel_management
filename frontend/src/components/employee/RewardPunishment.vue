<template>
  <el-descriptions :column="1" border>
    <template #title>
      <div class="section-title">
        <el-icon><Medal /></el-icon>
        奖惩记录
      </div>
    </template>
    <el-descriptions-item>
      <div v-if="!records.length" class="no-data">
        暂无奖惩记录
      </div>
      <el-table v-else :data="records" style="width: 100%">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'reward' ? 'success' : 'danger'">
              {{ row.type === 'reward' ? '奖励' : '处罚' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }">
            <span :class="row.type === 'reward' ? 'text-success' : 'text-danger'">
              {{ formatCurrency(row.amount) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="原因" />
        <el-table-column prop="approver" label="审批人" width="120" />
      </el-table>
    </el-descriptions-item>
  </el-descriptions>
</template>

<script setup lang="ts">
import { Medal } from '@element-plus/icons-vue'
import type { RewardPunishment } from '@/types/employee'

defineProps<{
  records: RewardPunishment[]
}>()

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2
  }).format(amount)
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

.no-data {
  text-align: center;
  color: #909399;
  padding: 20px 0;
}

.text-success {
  color: #67C23A;
}

.text-danger {
  color: #F56C6C;
}
</style> 
<template>
  <el-timeline>
    <el-timeline-item
      v-for="(item, index) in history"
      :key="index"
      :timestamp="item.change_date"
      placement="top"
    >
      <el-card class="position-change-card">
        <div class="position-change-content">
          <div class="before">
            <span class="label">原职位：</span>
            <span>{{ item.old_position }}</span>
          </div>
          <el-icon class="arrow"><ArrowRight /></el-icon>
          <div class="after">
            <span class="label">新职位：</span>
            <span>{{ item.new_position }}</span>
          </div>
        </div>
        <div class="change-reason">
          <span class="label">变更原因：</span>
          <span>{{ item.change_reason }}</span>
        </div>
        <div class="remarks" v-if="item.remarks">
          <span class="label">备注：</span>
          <span>{{ item.remarks }}</span>
        </div>
      </el-card>
    </el-timeline-item>
  </el-timeline>
</template>

<script setup lang="ts">
import { ArrowRight } from '@element-plus/icons-vue'
import type { PositionChange } from '@/types/employee'

defineProps<{
  history: PositionChange[]
}>()
</script>

<style scoped>
.position-change-card {
  margin-bottom: 10px;
}

.position-change-content {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 10px;
}

.before,
.after {
  flex: 1;
}

.label {
  color: #909399;
  margin-right: 8px;
}

.arrow {
  color: #409EFF;
  flex-shrink: 0;
}

.change-reason,
.remarks {
  margin-top: 8px;
  font-size: 14px;
}
</style> 
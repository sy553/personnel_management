<template>
  <div class="sidebar">
    <div class="logo">
      <h1 class="title">人事管理系统</h1>
    </div>
    <el-menu
      :default-active="activeMenu"
      class="menu"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409EFF"
      router
    >
      <el-menu-item index="/dashboard">
        <el-icon><Monitor /></el-icon>
        <template #title>首页</template>
      </el-menu-item>
      
      <el-sub-menu index="/employee">
        <template #title>
          <el-icon><User /></el-icon>
          <span>员工管理</span>
        </template>
        <el-menu-item index="/employee/list">员工列表</el-menu-item>
        <el-menu-item index="/employee/add">添加员工</el-menu-item>
      </el-sub-menu>
      
      <el-sub-menu index="/salary">
        <template #title>
          <el-icon><Money /></el-icon>
          <span>薪资管理</span>
        </template>
        <el-menu-item index="/salary/list">薪资列表</el-menu-item>
        <el-menu-item index="/salary/calculate">薪资计算</el-menu-item>
      </el-sub-menu>
      
      <el-sub-menu index="/budget">
        <template #title>
          <el-icon><Wallet /></el-icon>
          <span>预算管理</span>
        </template>
        <el-menu-item index="/budget/list">预算列表</el-menu-item>
        <el-menu-item index="/budget/analysis">预算分析</el-menu-item>
      </el-sub-menu>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Monitor, User, Money, Wallet } from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style scoped>
.sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2b2f3a;
}

.title {
  color: #fff;
  font-size: 16px;
  margin: 0;
  white-space: nowrap;
}

.menu {
  flex: 1;
  border-right: none;
}

:deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
}

:deep(.el-sub-menu__title) {
  height: 50px;
  line-height: 50px;
}
</style> 
<template>
  <div class="dashboard">
    <!-- 数据概览卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="data-card">
          <template #header>
            <div class="card-header">
              <span>员工总数</span>
              <el-icon class="icon"><UserFilled /></el-icon>
            </div>
          </template>
          <div class="card-value">{{ statistics.employeeCount }}</div>
          <div class="card-footer">
            较上月 
            <span :class="statistics.employeeGrowth >= 0 ? 'up' : 'down'">
              {{ Math.abs(statistics.employeeGrowth) }}%
            </span>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="data-card">
          <template #header>
            <div class="card-header">
              <span>本月薪资支出</span>
              <el-icon class="icon"><Money /></el-icon>
            </div>
          </template>
          <div class="card-value">¥{{ formatNumber(statistics.totalSalary) }}</div>
          <div class="card-footer">
            较上月 
            <span :class="statistics.salaryGrowth >= 0 ? 'up' : 'down'">
              {{ Math.abs(statistics.salaryGrowth) }}%
            </span>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="data-card">
          <template #header>
            <div class="card-header">
              <span>预算使用率</span>
              <el-icon class="icon"><Wallet /></el-icon>
            </div>
          </template>
          <div class="card-value">{{ statistics.budgetUsage }}%</div>
          <div class="card-footer">
            剩余预算 ¥{{ formatNumber(statistics.remainingBudget) }}
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="data-card">
          <template #header>
            <div class="card-header">
              <span>部门数量</span>
              <el-icon class="icon"><HomeFilled /></el-icon>
            </div>
          </template>
          <div class="card-value">{{ statistics.departmentCount }}</div>
          <div class="card-footer">
            共{{ statistics.activeEmployeeCount }}名在职员工
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>部门人员分布</span>
            </div>
          </template>
          <div ref="pieChartRef" class="chart"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>薪资支出趋势</span>
            </div>
          </template>
          <div ref="lineChartRef" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { UserFilled, Money, Wallet, HomeFilled } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import type { EChartsType } from 'echarts'

// 统计数据
const statistics = ref({
  employeeCount: 156,
  employeeGrowth: 5.2,
  totalSalary: 1256800,
  salaryGrowth: -2.3,
  budgetUsage: 85.6,
  remainingBudget: 235600,
  departmentCount: 8,
  activeEmployeeCount: 152
})

// 格式化数字
const formatNumber = (num: number) => {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

// 图表实例
let pieChart: EChartsType | null = null
let lineChart: EChartsType | null = null
const pieChartRef = ref<HTMLElement>()
const lineChartRef = ref<HTMLElement>()

// 初始化饼图
const initPieChart = () => {
  if (!pieChartRef.value) return
  
  pieChart = echarts.init(pieChartRef.value)
  pieChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center'
    },
    series: [
      {
        type: 'pie',
        radius: ['50%', '70%'],
        avoidLabelOverlap: false,
        label: {
          show: false
        },
        data: [
          { value: 35, name: '技术部' },
          { value: 28, name: '销售部' },
          { value: 24, name: '市场部' },
          { value: 15, name: '人事部' },
          { value: 12, name: '财务部' }
        ]
      }
    ]
  })
}

// 初始化折线图
const initLineChart = () => {
  if (!lineChartRef.value) return
  
  lineChart = echarts.init(lineChartRef.value)
  lineChart.setOption({
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月']
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}k'
      }
    },
    series: [
      {
        data: [1150, 1280, 1150, 1300, 1260, 1257],
        type: 'line',
        smooth: true,
        areaStyle: {}
      }
    ]
  })
}

// 监听窗口大小变化
const handleResize = () => {
  pieChart?.resize()
  lineChart?.resize()
}

onMounted(() => {
  initPieChart()
  initLineChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  pieChart?.dispose()
  lineChart?.dispose()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.data-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .icon {
      font-size: 20px;
      color: #909399;
    }
  }
  
  .card-value {
    font-size: 24px;
    font-weight: bold;
    margin: 10px 0;
  }
  
  .card-footer {
    font-size: 14px;
    color: #909399;
    
    .up {
      color: #67C23A;
    }
    
    .down {
      color: #F56C6C;
    }
  }
}

.chart-row {
  margin-top: 20px;
}

.chart {
  height: 300px;
}
</style> 
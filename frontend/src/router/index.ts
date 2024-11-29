import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layout/index.vue'

const routes = [
  {
    path: '/login',
    component: () => import('@/views/login/index.vue')
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '首页' }
      }
    ]
  },
  {
    path: '/employee',
    component: Layout,
    redirect: '/employee/list',
    children: [
      {
        path: 'list',
        name: 'EmployeeList',
        component: () => import('@/views/employee/list.vue'),
        meta: { title: '员工列表' }
      },
      {
        path: 'add',
        name: 'EmployeeAdd',
        component: () => import('@/views/employee/add.vue'),
        meta: { title: '新增员工' }
      },
      {
        path: 'detail1/:id',
        name: 'EmployeeDetail',
        component: () => import('@/views/employee/detail1.vue'),
        meta: {
          title: '员工详情',
          requiresAuth: true
        }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.path === '/login' && token) {
    next('/dashboard')
    return
  }
  
  if (to.path !== '/login' && !token) {
    next('/login')
    return
  }
  
  next()
})

export default router
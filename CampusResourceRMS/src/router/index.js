// index.js

import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('@/components/Login.vue')
    },
    {
      path: '/home',
      component: () => import('@/components/Home.vue')
    },
    {
      path: '/about',
      component: () => import('@/components/About.vue')
    },
    {
      path: '/userdashboard',
      component: () => import('@/components/UserDashboard.vue')
    }
    // 可以根据您的需要添加更多路由
  ]
})

export default router

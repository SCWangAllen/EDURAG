import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/templates',
    name: 'Templates',
    component: () => import('../views/Templates.vue')
  },
  {
    path: '/documents', 
    name: 'Documents',
    component: () => import('../views/Documents.vue')
  },
  {
    path: '/questions',
    name: 'Questions',
    component: () => import('../views/Questions.vue')
  },
  {
    path: '/generate',
    name: 'Generate',
    component: () => import('../views/Generate.vue')
  },
  {
    path: '/exam-paper',
    name: 'ExamPaper',
    component: () => import('../views/ExamPaper.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 添加路由守衛來調試
router.beforeEach((to, from, next) => {
  console.log('Router navigating from', from.path, 'to', to.path)
  next()
})

router.afterEach((to) => {
  console.log('Router navigated to', to.path)
})

export default router
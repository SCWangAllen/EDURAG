import { createRouter, createWebHistory } from 'vue-router'

// 頁面組件
import Dashboard from '../views/Dashboard.vue'
import Templates from '../views/Templates.vue'
import Documents from '../views/Documents.vue'
import Generate from '../views/Generate.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/templates',
    name: 'Templates',
    component: Templates
  },
  {
    path: '/documents', 
    name: 'Documents',
    component: Documents
  },
  {
    path: '/generate',
    name: 'Generate', 
    component: Generate
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
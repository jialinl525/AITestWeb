import { createRouter, createWebHistory } from 'vue-router'
import TestProgress from '../views/TestProgress.vue'
import TestProgressDetail from '../views/TestProgressDetail.vue'
import Bugs from '../views/Bugs.vue'
import KPI from '../views/KPI.vue'
import Personnel from '../views/Personnel.vue'
import WorkTasks from '../views/WorkTasks.vue'

const routes = [
  {
    path: '/',
    redirect: '/test-progress'
  },
  {
    path: '/test-progress',
    name: 'TestProgress',
    component: TestProgress
  },
  {
    path: '/test-progress/:id',
    name: 'TestProgressDetail',
    component: TestProgressDetail
  },
  {
    path: '/bugs',
    name: 'Bugs',
    component: Bugs
  },
  {
    path: '/kpi',
    name: 'KPI',
    component: KPI
  },
  {
    path: '/personnel',
    name: 'Personnel',
    component: Personnel
  },
  {
    path: '/work-tasks',
    name: 'WorkTasks',
    component: WorkTasks
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

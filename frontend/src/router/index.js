import { createRouter, createWebHistory } from 'vue-router'
import TestProgress from '../views/TestProgress.vue'
import TestProgressDetail from '../views/TestProgressDetail.vue'
import Bugs from '../views/Bugs.vue'
import KPI from '../views/KPI.vue'
import KPIModelDetail from '../views/KPIModelDetail.vue'
import Personnel from '../views/Personnel.vue'
import PersonnelDetail from '../views/PersonnelDetail.vue'
import WorkTasks from '../views/WorkTasks.vue'
import WorkTaskDetail from '../views/WorkTaskDetail.vue'
import { canViewAllPages } from '../stores/auth'

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
    path: '/kpi/models/:modelName',
    name: 'KPIModelDetail',
    component: KPIModelDetail
  },
  {
    path: '/personnel',
    name: 'Personnel',
    component: Personnel
  },
  {
    path: '/personnel/:id',
    name: 'PersonnelDetail',
    component: PersonnelDetail
  },
  {
    path: '/work-tasks',
    name: 'WorkTasks',
    component: WorkTasks
  },
  {
    path: '/work-tasks/:id',
    name: 'WorkTaskDetail',
    component: WorkTaskDetail
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const VIEWER_ALLOWED_ROUTES = new Set(['TestProgress', 'TestProgressDetail', 'KPI', 'KPIModelDetail'])

router.beforeEach((to) => {
  if (canViewAllPages()) {
    return true
  }
  if (VIEWER_ALLOWED_ROUTES.has(String(to.name || ''))) {
    return true
  }
  return { path: '/test-progress' }
})

export default router

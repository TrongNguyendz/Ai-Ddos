import { createRouter, createWebHistory } from 'vue-router'

const LoginView = () => import('../pages/LoginView.vue')
const MainView = () => import('../pages/MainView.vue')

// Các view con sẽ được load bên trong MainView
const OverviewView = () => import('../views/OverviewView.vue')
const LiveFlowsView = () => import('../views/LiveFlowsView.vue')
const AnalyticsView = () => import('../views/AnalyticsView.vue')
const AlertsView = () => import('../views/AlertsView.vue')
const RulesView = () => import('../views/RulesView.vue')

const routes = [
  {
    path: '/login',
    component: LoginView,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: MainView,           // Layout chính (có sidebar)
    meta: { requiresAuth: true },
    children: [
      { path: '', component: OverviewView, meta: { title: 'Tổng Quan' } },
      { path: 'live-flows', component: LiveFlowsView, meta: { title: 'Live Flows' } },
      { path: 'analytics', component: AnalyticsView, meta: { title: 'Phân Tích' } },
      { path: 'alerts', component: AlertsView, meta: { title: 'Cảnh Báo' } },
      { path: 'rules', component: RulesView, meta: { title: 'Quy Tắc' } },
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

// Route Guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true'

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } 
  else if (to.path === '/login' && isAuthenticated) {
    next('/')
  } 
  else {
    next()
  }
})

export default router
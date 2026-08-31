import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import PublicLayout from '../layouts/PublicLayout.vue'
import ResearchLayout from '../layouts/ResearchLayout.vue'
import AdminLayout from '../layouts/AdminLayout.vue'
import HomeView from '../views/HomeView.vue'
import ReaderView from '../views/reader/ReaderView.vue'
import SearchView from '../views/search/SearchView.vue'
import HeritageView from '../views/heritage/HeritageView.vue'
import LoginView from '../views/LoginView.vue'
import DeniedView from '../views/DeniedView.vue'
import ResearchHomeView from '../views/research/ResearchHomeView.vue'
import AdminHomeView from '../views/admin/AdminHomeView.vue'
import { useAuthStore } from '../stores/auth'
import { ADMIN_ROLES, RESEARCH_ROLES } from '../types/auth'
import { requireAnyRole } from './guards'

/**
 * Router (shared file: P2-01 created the public-only shell; P2-02 extends it
 * with the guarded research/admin surfaces). Public routes stay anonymous
 * and read-only; research/admin routes require authentication plus the
 * matching role (deny-by-default — P2-02-AC-01/02).
 */
export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: PublicLayout,
    meta: { publicOnly: true },
    children: [
      { path: '', name: 'home', component: HomeView },
      { path: 'reader', name: 'reader', component: ReaderView },
      { path: 'search', name: 'search', component: SearchView },
      { path: 'heritage', name: 'heritage', component: HeritageView },
      { path: 'login', name: 'login', component: LoginView },
      { path: 'denied', name: 'denied', component: DeniedView },
    ],
  },
  {
    path: '/research',
    component: ResearchLayout,
    meta: { requiresAuth: true, roles: RESEARCH_ROLES },
    beforeEnter: [requireAnyRole(RESEARCH_ROLES)],
    children: [{ path: '', name: 'research-home', component: ResearchHomeView }],
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, roles: ADMIN_ROLES },
    beforeEnter: [requireAnyRole(ADMIN_ROLES)],
    children: [{ path: '', name: 'admin-home', component: AdminHomeView }],
  },
]

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to) => {
  const store = useAuthStore()
  if (to.meta.publicOnly === true) {
    return true
  }
  if (to.meta.requiresAuth === true && store.isAuthenticated) {
    return true
  }
  return { name: 'login', query: { redirect: to.fullPath } }
})

export default router

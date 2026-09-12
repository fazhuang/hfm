import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import PublicLayout from '../layouts/PublicLayout.vue'
import ResearchLayout from '../layouts/ResearchLayout.vue'
import AdminLayout from '../layouts/AdminLayout.vue'
import HomeView from '../views/HomeView.vue'
import ReaderView from '../views/reader/ReaderView.vue'
import ReaderDocView from '../views/reader/ReaderDocView.vue'
import SearchView from '../views/search/SearchView.vue'
import HeritageView from '../views/heritage/HeritageView.vue'
import MediaLibraryView from '../views/library/MediaLibraryView.vue'
import PersonDetailView from '../views/persons/PersonDetailView.vue'
import WorkDetailView from '../views/works/WorkDetailView.vue'
import YanView from '../views/yan/YanView.vue'
import WorksView from '../views/works/WorksView.vue'
import ArchiveView from '../views/archive/ArchiveView.vue'
import JiayiView from '../views/jiayi/JiayiView.vue'
import AboutView from '../views/AboutView.vue'
import LoginView from '../views/LoginView.vue'
import DeniedView from '../views/DeniedView.vue'
import ResearchHomeView from '../views/research/ResearchHomeView.vue'
import ResearchSearchView from '../views/research/ResearchSearchView.vue'
import ResearchEntityView from '../views/research/ResearchEntityView.vue'
import AdminHomeView from '../views/admin/AdminHomeView.vue'
import AuditLogView from '../views/admin/AuditLogView.vue'
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
      { path: 'reader/:id', name: 'reader-doc', component: ReaderDocView },
      { path: 'search', name: 'search', component: SearchView },
      { path: 'heritage', name: 'heritage', component: HeritageView },
      { path: 'library', name: 'library', component: MediaLibraryView },
      { path: 'persons/:id', name: 'person', component: PersonDetailView },
      { path: 'works/:id', name: 'work', component: WorkDetailView },
      { path: 'yan', name: 'yan', component: YanView },
      { path: 'works', name: 'works', component: WorksView },
      { path: 'archive', name: 'archive', component: ArchiveView },
      { path: 'jiayi', name: 'jiayi', component: JiayiView },
      { path: 'about', name: 'about', component: AboutView },
      { path: 'login', name: 'login', component: LoginView },
      { path: 'denied', name: 'denied', component: DeniedView },
    ],
  },
  {
    path: '/research',
    component: ResearchLayout,
    meta: { requiresAuth: true, roles: RESEARCH_ROLES },
    beforeEnter: [requireAnyRole(RESEARCH_ROLES)],
    children: [
      { path: '', name: 'research-home', component: ResearchHomeView },
      { path: 'search', name: 'research-search', component: ResearchSearchView },
      {
        path: 'entity/:type/:id',
        name: 'research-entity',
        component: ResearchEntityView,
      },
    ],
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, roles: ADMIN_ROLES },
    beforeEnter: [requireAnyRole(ADMIN_ROLES)],
    children: [
      { path: '', name: 'admin-home', component: AdminHomeView },
      { path: 'audit', name: 'admin-audit', component: AuditLogView },
    ],
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

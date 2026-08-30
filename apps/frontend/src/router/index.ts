import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import PublicLayout from '../layouts/PublicLayout.vue'
import HomeView from '../views/HomeView.vue'

/**
 * Public-only router (P2-01 public frontend foundation).
 *
 * Anonymous-first: every route is public and read-only; no research/admin
 * route is registered here (P2-02 adds them behind guards). The global guard
 * enforces that public routes never require authentication and that unknown
 * guarded namespaces are unreachable (P2-01-AC-01/03).
 */
export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: PublicLayout,
    meta: { publicOnly: true },
    children: [
      {
        path: '',
        name: 'home',
        component: HomeView,
      },
    ],
  },
]

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to) => {
  // Public surfaces are anonymous and read-only: never require auth, and
  // fail-closed on any route that is not explicitly public.
  if (to.meta.publicOnly === true) {
    return true
  }
  return { name: 'home' }
})

export default router

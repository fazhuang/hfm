/**
 * Route guards (P2-02 research/admin frontend foundation).
 *
 * requireAuth: unauthenticated → login with redirect back (AC-01).
 * requireAnyRole: authenticated but wrong role → default-deny (AC-02).
 */
import type { NavigationGuard } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import type { Role } from '../types/auth'

export function requireAuth(): NavigationGuard {
  return (to) => {
    const store = useAuthStore()
    if (!store.isAuthenticated) {
      return { name: 'login', query: { redirect: to.fullPath } }
    }
    return true
  }
}

export function requireAnyRole(roles: readonly Role[]): NavigationGuard {
  return () => {
    const store = useAuthStore()
    if (!store.hasAnyRole(roles)) {
      return { name: 'denied' }
    }
    return true
  }
}

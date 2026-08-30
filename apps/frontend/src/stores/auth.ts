/**
 * Auth store (P2-02 research/admin frontend foundation).
 *
 * In-memory session state (token + user). 401 handling revokes the session
 * so the next guarded navigation redirects to login (P2-02-AC-04).
 */
import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { AuthRevokedError, authApi } from '../services/auth'
import type { AuthUser, Role } from '../types/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const user = ref<AuthUser | null>(null)

  const isAuthenticated = computed(() => token.value !== null && user.value !== null)

  function hasRole(role: Role): boolean {
    return user.value?.roles.includes(role) ?? false
  }

  function hasAnyRole(roles: readonly Role[]): boolean {
    return roles.some(hasRole)
  }

  function hasPermission(permission: string): boolean {
    return user.value?.permissions.includes(permission) ?? false
  }

  async function login(username: string, password: string): Promise<void> {
    const response = await authApi.login(username, password)
    token.value = response.token
    user.value = response.user
  }

  async function logout(): Promise<void> {
    try {
      await authApi.logout(token.value)
    } finally {
      token.value = null
      user.value = null
    }
  }

  /** 401 token-revocation handling: drop the session (default-deny). */
  function revoke(): void {
    token.value = null
    user.value = null
  }

  /** Wrap a promise, converting 401 into a revoked session (AC-04). */
  async function withRevocation<T>(action: () => Promise<T>): Promise<T> {
    try {
      return await action()
    } catch (err) {
      if (err instanceof AuthRevokedError) {
        revoke()
      }
      throw err
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    hasRole,
    hasAnyRole,
    hasPermission,
    login,
    logout,
    revoke,
    withRevocation,
  }
})

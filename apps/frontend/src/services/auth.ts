/**
 * Auth API client (P2-02 research/admin frontend foundation).
 *
 * Talks to the accepted auth namespace (`/api/v1/auth/*`). A 401 response is
 * surfaced as AuthRevokedError so the store can drop the token and redirect
 * to login (P2-02-AC-04 token revocation).
 */
import type { LoginResponse } from '../types/auth'

export class AuthRevokedError extends Error {
  constructor(message = 'session revoked') {
    super(message)
    this.name = 'AuthRevokedError'
  }
}

async function postJson<T>(path: string, body: unknown, token?: string | null): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers.Authorization = `Bearer ${token}`
  const response = await fetch(path, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  })
  if (response.status === 401) {
    throw new AuthRevokedError()
  }
  if (!response.ok) {
    throw new Error(`auth request failed: ${response.status}`)
  }
  return (await response.json()) as T
}

export const authApi = {
  login(username: string, password: string): Promise<LoginResponse> {
    return postJson<LoginResponse>('/api/v1/auth/login', { username, password })
  },
  logout(token?: string | null): Promise<unknown> {
    return postJson<unknown>('/api/v1/auth/logout', {}, token)
  },
}

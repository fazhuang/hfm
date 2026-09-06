/**
 * Auth API client (P2-02 research/admin frontend foundation).
 *
 * Talks to the accepted auth namespace (`/api/v1/auth/*`). A 401 response is
 * surfaced as AuthRevokedError so the store can drop the token and redirect
 * to login (P2-02-AC-04 token revocation).
 *
 * ND-1 B05 (existing-auth contract repair): the authoritative backend login
 * response is the shared `api_response` envelope
 * `{success, timestamp, message, data:{ok, token, user_id, role}}` (see
 * `hfm.utils.response.api_response` / the mounted `/api/v1/auth/login`
 * route). This client adapts that envelope into the existing `LoginResponse`
 * consumed by the store; there is no top-level `token`/`user` field on the
 * wire. The adapter is strict: only a successful envelope whose data carries a
 * nonempty token, a nonempty user_id and one member of the frozen `ROLES` is
 * accepted; anything else throws so authentication state is never written.
 */
import { ROLES, type LoginResponse, type Role } from '../types/auth'

export class AuthRevokedError extends Error {
  constructor(message = 'session revoked') {
    super(message)
    this.name = 'AuthRevokedError'
  }
}

/** Error for an unparseable / out-of-contract login payload. */
export class InvalidLoginResponseError extends Error {
  constructor(message = 'invalid login response') {
    super(message)
    this.name = 'InvalidLoginResponseError'
  }
}

/** Backend login envelope data (authoritative api_response data payload). */
interface LoginEnvelopeData {
  ok?: unknown
  token?: unknown
  user_id?: unknown
  role?: unknown
}

function isApiEnvelope(body: unknown): body is { success: boolean; data: unknown } {
  if (body === null || typeof body !== 'object') return false
  const candidate = body as { success?: unknown; data?: unknown }
  return 'success' in candidate && 'data' in candidate
}

/** Strict adapter from the backend envelope to the existing LoginResponse. */
export function adaptLoginResponse(body: unknown): LoginResponse {
  if (!isApiEnvelope(body) || body.success !== true || body.data === null) {
    throw new InvalidLoginResponseError('login response is not a success envelope')
  }
  const data = body.data as LoginEnvelopeData
  if (data === null || typeof data !== 'object') {
    throw new InvalidLoginResponseError('login envelope data missing')
  }
  if (data.ok !== true) {
    throw new InvalidLoginResponseError('login envelope not ok')
  }
  if (typeof data.token !== 'string' || data.token.length === 0) {
    throw new InvalidLoginResponseError('login envelope token missing')
  }
  if (typeof data.user_id !== 'string' || data.user_id.length === 0) {
    throw new InvalidLoginResponseError('login envelope user_id missing')
  }
  if (typeof data.role !== 'string' || !(ROLES as readonly string[]).includes(data.role)) {
    throw new InvalidLoginResponseError('login envelope role unknown')
  }
  return {
    token: data.token,
    user: {
      id: data.user_id,
      roles: [data.role as Role],
      // Permissions are never granted client-side; the server authorizes from
      // the verified token/database (default deny) and no production caller
      // consumes client permissions today.
      permissions: [],
    },
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
    return postJson<unknown>('/api/v1/auth/login', { username, password }).then(adaptLoginResponse)
  },
  logout(token?: string | null): Promise<unknown> {
    return postJson<unknown>('/api/v1/auth/logout', {}, token)
  },
}

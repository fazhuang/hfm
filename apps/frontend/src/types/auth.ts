/**
 * Auth/RBAC types (P2-02 research/admin frontend foundation).
 *
 * Mirrors the frozen identity model (HFM-PHASE1-ADR-07 / identity.py): five
 * seeded roles, deny-by-default permission set.
 */

export const ROLES = [
  'ANONYMOUS_VISITOR',
  'STUDENT_RESEARCHER',
  'SCHOLAR_RESEARCHER',
  'CONTENT_REVIEWER',
  'SYSTEM_ADMIN',
] as const

export type Role = (typeof ROLES)[number]

/** Roles allowed to reach the research workspace surface. */
export const RESEARCH_ROLES: readonly Role[] = ['STUDENT_RESEARCHER', 'SCHOLAR_RESEARCHER']

/** Roles allowed to reach the admin/publication surface. */
export const ADMIN_ROLES: readonly Role[] = ['CONTENT_REVIEWER', 'SYSTEM_ADMIN']

export interface AuthUser {
  id: string
  roles: Role[]
  permissions: string[]
}

export interface LoginResponse {
  token: string
  user: AuthUser
}

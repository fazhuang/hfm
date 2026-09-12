/**
 * Auth-flow browser E2E — real Chromium over mocked auth API (P2-02).
 *
 * Proves the frozen auth acceptance criteria in a real browser DOM:
 *  - login success (role-aware redirect to the guarded surface);
 *  - login failure (visible, accessible error feedback — role="alert");
 *  - anonymous deny on /research and /admin (redirect to login);
 *  - role matrix (researcher → denied on /admin; reviewer → admin; admin → both);
 *  - logout (session dropped + next guarded nav sends to login);
 *  - session expiry / token revocation (401 → revoke → redirect to login);
 *  - permission errors surface visible, accessible feedback.
 *
 * The auth API is mocked at the network layer (same pattern as
 * ui11-research.spec.ts); navigation, store logic and redirects run in real
 * Chromium. No new auth framework is introduced.
 *
 * WR00-B2-E2E-R1 auth-contract alignment:
 *   OLD_ASSERTION_INTENT (7 tests): a login mock of the historical top-level
 *     shape { token, user } authenticated the user into the guarded surface.
 *   CURRENT_SYSTEM_CONTRACT: the frozen backend login response is the strict
 *     api_response envelope {success,timestamp,message,data:{ok,token,
 *     user_id,role}}; services/auth.ts adaptLoginResponse REJECTS the old
 *     top-level shape by design (ND-1 B05) — product code must not regress to
 *     the old format.
 *   WHY_OLD_MOCK_WAS_STALE: the mocks predated the strict-envelope adapter, so
 *     every success mock returned a body the adapter refuses → no session.
 *   NEW_ASSERTION_INTENT: identical business semantics (authenticated user
 *     state, role-aware redirect, token handling, logout, protected routes),
 *     with the login transport mocked to the current strict envelope. The old
 *     top-level response format is never re-allowed by product code.
 */
import { expect, test } from '@playwright/test'

type Role =
  | 'ANONYMOUS_VISITOR'
  | 'STUDENT_RESEARCHER'
  | 'SCHOLAR_RESEARCHER'
  | 'CONTENT_REVIEWER'
  | 'SYSTEM_ADMIN'

/** Strict login envelope as returned by POST /api/v1/auth/login (ND-1 B05). */
function loginEnvelope(role: Role, userId: string, token: string): unknown {
  return {
    success: true,
    timestamp: '2026-01-01T00:00:00.000Z',
    message: 'ok',
    data: { ok: true, token, user_id: userId, role },
  }
}

async function mockLogin(
  page: import('@playwright/test').Page,
  body: unknown,
  status = 200,
): Promise<void> {
  await page.route('**/api/v1/auth/login', (route) =>
    route.fulfill({
      status,
      contentType: 'application/json',
      body: JSON.stringify(body),
    }),
  )
}

async function fillAndSubmit(page: import('@playwright/test').Page): Promise<void> {
  await page.getByLabel('用户名').fill('researcher')
  await page.getByLabel('密码').fill('pw')
  await page.getByRole('button', { name: '登录' }).click()
}

test('auth-flow: login success as researcher lands on /research', async ({ page }) => {
  // NEW mock: strict envelope data {ok, token, user_id, role} (old {token,user}
  // top-level shape is rejected by the product adapter). Intent unchanged:
  // a successful researcher login lands on the guarded research surface.
  await mockLogin(page, loginEnvelope('STUDENT_RESEARCHER', 'u-r', 'tok-r'))
  await page.goto('/login')
  await fillAndSubmit(page)
  await page.waitForURL(/\/research/)
  await expect(page.getByRole('heading', { name: '研究工作台' })).toBeVisible()
})

test('auth-flow: login redirect honors `redirect` query for guarded target', async ({ page }) => {
  await mockLogin(page, loginEnvelope('SYSTEM_ADMIN', 'u-a', 'tok-a'))
  await page.goto('/admin')
  await page.waitForURL(/\/login/)
  await page.getByLabel('用户名').fill('admin')
  await page.getByLabel('密码').fill('pw')
  await page.getByRole('button', { name: '登录' }).click()
  await page.waitForURL(/\/admin/)
  await expect(page.getByRole('heading', { name: '发布管理' })).toBeVisible()
})

test('auth-flow: login failure shows visible, accessible error feedback', async ({ page }) => {
  // Error body follows the current envelope (success:false + message); the
  // client only keys off HTTP 401, and the visible role="alert" feedback is
  // asserted below.
  await mockLogin(
    page,
    { success: false, message: 'invalid credentials', data: null },
    401,
  )
  await page.goto('/login')
  await fillAndSubmit(page)
  // SPA stays on /login and renders a role="alert" error.
  const alert = page.getByRole('alert')
  await expect(alert).toBeVisible()
  await expect(alert).toContainText('登录失败')
  // No navigation to a guarded surface on failure.
  await expect(page).not.toHaveURL(/\/research/)
})

test('auth-flow: anonymous /research and /admin deny (redirect to login)', async ({ page }) => {
  await page.goto('/research')
  await page.waitForURL(/\/login/)
  expect(new URL(page.url()).pathname).toBe('/login')
  await page.goto('/admin')
  await page.waitForURL(/\/login/)
  expect(new URL(page.url()).pathname).toBe('/login')
})

test('auth-flow: role matrix — researcher denied /admin (default-deny)', async ({ page }) => {
  // Anonymous /admin -> ?redirect=/admin; after login the client-side push
  // re-evaluates requireAnyRole(ADMIN_ROLES) in the SAME session -> /denied.
  await mockLogin(page, loginEnvelope('STUDENT_RESEARCHER', 'u-r', 'tok-r'))
  await page.goto('/admin')
  await page.waitForURL(/\/login/)
  await page.getByLabel('用户名').fill('researcher')
  await page.getByLabel('密码').fill('pw')
  await page.getByRole('button', { name: '登录' }).click()
  await page.waitForURL(/\/(denied|login)/)
  await expect(page.getByRole('heading', { name: '无权限访问' })).toBeVisible()
})

test('auth-flow: role matrix — scholar researcher reaches /research, denied /admin', async ({
  page,
}) => {
  await mockLogin(page, loginEnvelope('SCHOLAR_RESEARCHER', 'u-s', 'tok-s'))
  await page.goto('/research')
  await page.waitForURL(/\/login/)
  await page.getByLabel('用户名').fill('scholar')
  await page.getByLabel('密码').fill('pw')
  await page.getByRole('button', { name: '登录' }).click()
  await page.waitForURL(/\/research/)
  await expect(page.getByRole('heading', { name: '研究工作台' })).toBeVisible()
  // Scholar is not an admin: same-session /admin guard -> /denied.
  await mockLogin(page, loginEnvelope('SCHOLAR_RESEARCHER', 'u-s', 'tok-s'))
  await page.goto('/admin')
  await page.waitForURL(/\/login/)
  await page.getByLabel('用户名').fill('scholar')
  await page.getByLabel('密码').fill('pw')
  await page.getByRole('button', { name: '登录' }).click()
  await page.waitForURL(/\/(denied|login)/)
  await expect(page.getByRole('heading', { name: '无权限访问' })).toBeVisible()
})

test('auth-flow: role matrix — admin reaches the publish console and audit-log gate', async ({
  page,
}) => {
  await mockLogin(page, loginEnvelope('SYSTEM_ADMIN', 'u-a', 'tok-a'))
  await page.route('**/api/v1/admin/**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ reconciliations: [], entries: [] }),
    }),
  )
  await page.goto('/admin')
  await page.waitForURL(/\/login/)
  await page.getByLabel('用户名').fill('admin')
  await page.getByLabel('密码').fill('pw')
  await page.getByRole('button', { name: '登录' }).click()
  await page.waitForURL(/\/admin/)
  await expect(page.getByRole('heading', { name: '发布管理' })).toBeVisible()
})

test('auth-flow: logout drops the session; guarded nav redirects to login', async ({ page }) => {
  await mockLogin(page, loginEnvelope('STUDENT_RESEARCHER', 'u-r', 'tok-r'))
  await page.route('**/api/v1/auth/logout', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: '{}' }),
  )
  await page.goto('/research')
  await page.waitForURL(/\/login/)
  await page.getByLabel('用户名').fill('researcher')
  await page.getByLabel('密码').fill('pw')
  await page.getByRole('button', { name: '登录' }).click()
  await page.waitForURL(/\/research/)
  await expect(page.getByRole('heading', { name: '研究工作台' })).toBeVisible()
  // Logout button lives in the research layout header.
  await page.getByRole('button', { name: '退出登录' }).click()
  // After logout, a guarded nav must bounce to login.
  await page.goto('/research')
  await page.waitForURL(/\/login/)
  expect(new URL(page.url()).pathname).toBe('/login')
})

test('auth-flow: token revocation (401) drops the session and sends to login', async ({ page }) => {
  await mockLogin(page, loginEnvelope('STUDENT_RESEARCHER', 'u-r', 'tok-r'))
  await page.goto('/research')
  await page.waitForURL(/\/login/)
  await page.getByLabel('用户名').fill('researcher')
  await page.getByLabel('密码').fill('pw')
  await page.getByRole('button', { name: '登录' }).click()
  await page.waitForURL(/\/research/)
  // A protected API returns 401 → the store revokes the session.
  await page.route('**/api/v1/research/search', (route) =>
    route.fulfill({ status: 401, contentType: 'application/json', body: '{}' }),
  )
  await page.goto('/research/search')
  await page.waitForURL(/\/login/)
  expect(new URL(page.url()).pathname).toBe('/login')
})

test('auth-flow: permission error surfaces visible, accessible feedback', async ({ page }) => {
  // An admin action that the backend denies must produce a role="alert" message.
  await mockLogin(page, loginEnvelope('CONTENT_REVIEWER', 'u-c', 'tok-c'))
  await page.route('**/api/v1/admin/publication/publish', (route) =>
    route.fulfill({ status: 403, contentType: 'application/json', body: '{}' }),
  )
  await page.goto('/admin')
  await page.waitForURL(/\/login/)
  await page.getByLabel('用户名').fill('reviewer')
  await page.getByLabel('密码').fill('pw')
  await page.getByRole('button', { name: '登录' }).click()
  await page.waitForURL(/\/admin/)
  await expect(page.getByRole('heading', { name: '发布管理' })).toBeVisible()
  await page.getByRole('button', { name: '发布演示条目' }).click()
  await expect(page.getByRole('alert')).toBeVisible()
})

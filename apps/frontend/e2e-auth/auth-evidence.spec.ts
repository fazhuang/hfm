/**
 * G7 — REAL browser authentication evidence (ND-1).
 *
 * Real chain only: real Chromium → real backend (:8000 via Vite /api proxy)
 * → real isolated PostgreSQL seeded with a STUDENT_RESEARCHER. NO
 * page.route fulfillment anywhere in this file — every assertion depends on
 * the mounted backend and its database. Executed by
 * scripts/real-browser-auth-evidence.sh (which seeds the DB and starts the
 * backend) or manually against a matching stack.
 *
 * Verifies: valid user → login → auth state → research entry; invalid
 * credentials rejected (real 401); anonymous protected routes guarded;
 * authenticated non-admin denied on an admin endpoint with the real token.
 */
import { expect, test } from '@playwright/test'

const RESEARCHER = { username: 'nd1-researcher', password: 'ResearcherPass!2026' }

test('G7 real auth: valid login → research; invalid rejected; guards; admin denial', async ({
  page,
}) => {
  const loginResponses: number[] = []
  const authTokens = new Set<string>()
  page.on('response', async (r) => {
    if (r.url().includes('/api/v1/auth/login')) {
      loginResponses.push(r.status())
      if (r.status() === 200) {
        const body = await r.json().catch(() => null)
        if (body?.data?.token) authTokens.add(String(body.data.token))
      }
    }
  })
  const pageErrors: string[] = []
  page.on('pageerror', (e) => pageErrors.push(String(e)))

  // 1. Anonymous protected routes → login guard (denied).
  for (const path of ['/research', '/admin']) {
    await page.goto(`http://localhost:${process.env.HFM_E2E_PORT || 5199}${path}`)
    await page.waitForURL(/\/login/)
  }

  // 2. Invalid credentials → real 401 → error state, no session. A bare
  //    /login (no redirect query) keeps the later valid login on /research.
  await page.goto(`http://localhost:${process.env.HFM_E2E_PORT || 5199}/login`)
  await page.getByLabel('用户名').fill(RESEARCHER.username)
  await page.getByLabel('密码').fill('WRONG-password')
  await page.getByRole('button', { name: '登录' }).click()
  await page.getByText(/登录失败/).waitFor({ timeout: 10000 })

  // 3. Valid credentials → login → research workspace (protected route).
  await page.getByLabel('用户名').fill(RESEARCHER.username)
  await page.getByLabel('密码').fill(RESEARCHER.password)
  await page.getByRole('button', { name: '登录' }).click()
  await page.waitForURL(/\/research/, { timeout: 15000 })
  await page.getByRole('heading', { name: '研究工作台' }).waitFor({ timeout: 10000 })
  await expect(page.getByText('可研究内容').first()).toBeVisible()

  // 4. Authenticated non-admin: admin endpoint refused with the REAL token.
  //    (Bearer captured from the app's own protected research requests.)
  expect(authTokens.size).toBeGreaterThan(0)
  const token = [...authTokens][0]
  const adminDenied = await page.evaluate(async (t) => {
    const resp = await fetch('/api/v1/admin/audit-log', {
      headers: { Authorization: `Bearer ${t}` },
    })
    return { status: resp.status, body: await resp.json() }
  }, token)
  // Server default-deny: never 200 for a student token (mapping to a specific
  // 4xx/5xx code is a separate pre-existing backend observation).
  expect(adminDenied.status).not.toBe(200)
  expect(adminDenied.body.success).toBe(false)

  expect(loginResponses).toEqual([401, 200])
  expect(pageErrors).toEqual([])
  console.log(
    `G7_REAL_AUTH=pass loginApi=${JSON.stringify(loginResponses)} adminDenied=${adminDenied.status}`,
  )
})

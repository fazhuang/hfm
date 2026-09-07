import { execFileSync } from 'node:child_process'
import { defineConfig } from '@playwright/test'

/**
 * G7 real-browser auth evidence config (ND-1) — same fail-closed harness
 * contract as the default config, but scoped to ./e2e-auth (excluded from
 * the standard 88-test suite). testDir stays outside ./e2e so the canonical
 * suite count is unchanged. Run via scripts/real-browser-auth-evidence.sh.
 */
const E2E_PORT = Number(process.env.HFM_E2E_PORT || 5199)
const E2E_BASE = process.env.HFM_E2E_BASE || `http://localhost:${E2E_PORT}`

let targetSha = ''
try {
  targetSha = execFileSync('git', ['-C', process.cwd(), 'rev-parse', 'HEAD'], {
    encoding: 'utf8',
  }).trim()
} catch {
  targetSha = 'unknown'
}
const expectedSha = process.env.HFM_E2E_TARGET_SHA
if (expectedSha && expectedSha !== targetSha) {
  throw new Error(
    `HARNESS_TARGET_SHA_MISMATCH expected=${expectedSha} current=${targetSha} ` +
      '(bind HFM_E2E_TARGET_SHA to the checkout under test)',
  )
}

export default defineConfig({
  testDir: './e2e-auth',
  timeout: 30_000,
  retries: 0,
  use: { baseURL: E2E_BASE, headless: true },
  webServer: {
    command: `pnpm dev --port ${E2E_PORT} --strictPort`,
    url: E2E_BASE,
    reuseExistingServer: false,
    timeout: 60_000,
    env: { ...process.env, HFM_TARGET_SHA: targetSha },
  },
})

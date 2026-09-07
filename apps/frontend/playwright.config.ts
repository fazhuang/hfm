import { execFileSync } from 'node:child_process'
import { defineConfig } from '@playwright/test'

/**
 * P2-01 browser E2E harness (P1-01/P1-02 correction; ND-1 H01 + RV-01).
 * Real Chromium navigation over the public portal with mocked public-API
 * routes — jsdom is not used; assertions run in the actual browser DOM.
 *
 * ND-1 H01 (test-harness hardening): the harness NEVER silently reuses a
 * foreign server. webServer starts THIS repository's Vite on an explicit
 * port with --strictPort and reuseExistingServer:false; if any other process
 * already occupies the port the run FAILS BEFORE NAVIGATION with a clear
 * bind error instead of testing a foreign process's code. Only the process
 * started by this run is ever used or stopped.
 *
 * ND-1 RV-01 (target identity): the config BINDS the launched source SHA.
 * The current checkout SHA is computed at load; when HFM_E2E_TARGET_SHA is
 * provided it must equal that SHA or the run aborts before any server start
 * (HARNESS_TARGET_SHA_MISMATCH). The launched Vite inherits HFM_TARGET_SHA so
 * runtime gate scripts and later reuse checks can prove the process env
 * matches the intended source. Static-file serving binds the release
 * manifest.json source SHA (see docs/operations/ND1-RELEASE-QUALIFICATION.md).
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
  testDir: './e2e',
  timeout: 30_000,
  retries: 0,
  use: {
    baseURL: E2E_BASE,
    headless: true,
  },
  webServer: {
    command: `pnpm dev --port ${E2E_PORT} --strictPort`,
    url: E2E_BASE,
    reuseExistingServer: false,
    timeout: 60_000,
    env: {
      ...process.env,
      HFM_TARGET_SHA: targetSha,
    },
  },
})

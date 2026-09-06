import { defineConfig } from '@playwright/test'

/**
 * P2-01 browser E2E harness (P1-01/P1-02 correction; ND-1 H01 hardening).
 * Real Chromium navigation over the public portal with mocked public-API
 * routes — jsdom is not used; assertions run in the actual browser DOM.
 *
 * ND-1 H01 (test-harness hardening): the harness NEVER silently reuses a
 * foreign server. webServer starts THIS repository's Vite on an explicit
 * port with --strictPort and reuseExistingServer:false; if any other process
 * already occupies the port the run FAILS BEFORE NAVIGATION with a clear
 * bind error instead of testing a foreign process's code. Only the process
 * started by this run is ever used or stopped. Alternate explicit ports are
 * supported consistently via HFM_E2E_PORT / HFM_E2E_BASE (and CF01_BASE in
 * golden-runtime.spec.ts), so an occupied default port can be overridden
 * without touching this file.
 */
const E2E_PORT = Number(process.env.HFM_E2E_PORT || 5199)
const E2E_BASE = process.env.HFM_E2E_BASE || `http://localhost:${E2E_PORT}`

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
  },
})

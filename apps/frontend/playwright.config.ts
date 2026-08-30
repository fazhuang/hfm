import { defineConfig } from '@playwright/test'

/**
 * P2-01 browser E2E harness (P1-01/P1-02 correction).
 * Real Chromium navigation over the public portal with mocked public-API
 * routes — jsdom is not used; assertions run in the actual browser DOM.
 */
export default defineConfig({
  testDir: './e2e',
  timeout: 30_000,
  retries: 0,
  use: {
    baseURL: 'http://localhost:5199',
    headless: true,
  },
  webServer: {
    command: 'pnpm dev --port 5199 --strictPort',
    url: 'http://localhost:5199',
    reuseExistingServer: true,
    timeout: 60_000,
  },
})

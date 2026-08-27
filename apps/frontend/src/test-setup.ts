/**
 * Vitest global setup — jsdom polyfills (migrated Batch 3 asset — PORT).
 *
 * Source: HFB `apps/frontend/src/test-setup.ts` @ `03755b5`.
 * jsdom does not implement window.matchMedia; provide a stub that reports
 * no media-query matches. Individual tests can override via vi.fn().
 */
import { vi } from 'vitest'

if (typeof window !== 'undefined') {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  })
}

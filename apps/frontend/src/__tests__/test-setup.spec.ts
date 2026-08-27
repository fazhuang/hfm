import { describe, expect, it } from 'vitest'

describe('vitest jsdom test setup (migrated Batch 3 asset)', () => {
  it('provides a window.matchMedia stub', () => {
    expect(typeof window.matchMedia).toBe('function')
    const mql = window.matchMedia('(prefers-color-scheme: dark)')
    expect(mql.matches).toBe(false)
    expect(mql.media).toBe('(prefers-color-scheme: dark)')
    expect(typeof mql.addEventListener).toBe('function')
  })
})

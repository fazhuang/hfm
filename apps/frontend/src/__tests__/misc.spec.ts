import { describe, expect, it, vi } from 'vitest'
import { generateId, sleep } from '../utils/misc'

describe('generic utilities (migrated Batch 1 asset)', () => {
  it('sleep resolves after the given delay', async () => {
    vi.useFakeTimers()
    const promise = sleep(100)
    const marker = vi.fn()
    void promise.then(marker)
    await vi.advanceTimersByTimeAsync(100)
    expect(marker).toHaveBeenCalledTimes(1)
    vi.useRealTimers()
  })

  it('generateId returns an alphanumeric id of the requested length', () => {
    expect(generateId()).toHaveLength(21)
    expect(generateId()).toMatch(/^[A-Za-z0-9]+$/)
    expect(generateId(8)).toHaveLength(8)
    expect(generateId(0)).toBe('')
  })
})

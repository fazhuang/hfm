import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { useToast } from '../composables/useToast'

describe('useToast (migrated Batch 2 asset)', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    // clear the module-level global toast state between tests
    const { toasts, dismiss } = useToast()
    toasts.value.forEach((t) => dismiss(t.id))
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('shows a toast and returns its id', () => {
    const { toasts, show } = useToast()
    const id = show('hello')
    expect(toasts.value).toHaveLength(1)
    expect(toasts.value[0]?.message).toBe('hello')
    expect(toasts.value[0]?.variant).toBe('info')
    expect(id).toMatch(/^hfm-toast-/)
  })

  it('dismisses a toast immediately', () => {
    const { toasts, show, dismiss } = useToast()
    const id = show('x')
    dismiss(id)
    expect(toasts.value).toHaveLength(0)
  })

  it('auto-dismisses after the configured duration', () => {
    const { toasts, show } = useToast()
    show('auto', { duration: 100 })
    expect(toasts.value).toHaveLength(1)
    vi.advanceTimersByTime(101)
    expect(toasts.value).toHaveLength(0)
  })

  it('variant helpers set the correct variant', () => {
    const { toasts, success, error, warning, info } = useToast()
    success('s')
    error('e')
    warning('w')
    info('i')
    expect(toasts.value.map((t) => t.variant)).toEqual(['success', 'error', 'warning', 'info'])
  })
})

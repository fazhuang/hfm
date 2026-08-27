import { beforeEach, describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'

/**
 * jsdom in this Vitest setup does not expose localStorage; provide a
 * minimal in-memory Storage mock (standard browser-API emulation).
 */
function installLocalStorageMock(): void {
  const store = new Map<string, string>()
  const mock: Storage = {
    get length() {
      return store.size
    },
    key: (index: number) => Array.from(store.keys())[index] ?? null,
    getItem: (key: string) => store.get(key) ?? null,
    setItem: (key: string, value: string) => {
      store.set(key, String(value))
    },
    removeItem: (key: string) => {
      store.delete(key)
    },
    clear: () => {
      store.clear()
    },
  }
  Object.defineProperty(window, 'localStorage', { value: mock, configurable: true, writable: true })
}

/**
 * useTheme keeps module-level singleton state, so each test re-imports the
 * module to observe the initialization-time read of localStorage.
 */
async function loadFreshTheme() {
  vi.resetModules()
  return await import('../composables/useTheme')
}

describe('useTheme (migrated Batch 2 asset)', () => {
  beforeEach(() => {
    installLocalStorageMock()
    document.documentElement.classList.remove('dark')
  })

  it('defaults to auto when no preference is stored', async () => {
    window.localStorage.clear()
    const mod = await loadFreshTheme()
    expect(mod.useTheme().theme.value).toBe('auto')
  })

  it('loads a persisted theme', async () => {
    window.localStorage.setItem('hfm-theme', 'light')
    const mod = await loadFreshTheme()
    expect(mod.useTheme().theme.value).toBe('light')
  })

  it('setTheme updates state, persists, and applies the dark class', async () => {
    window.localStorage.clear()
    const mod = await loadFreshTheme()
    const { theme, setTheme } = mod.useTheme()
    setTheme('dark')
    await nextTick()
    expect(theme.value).toBe('dark')
    expect(window.localStorage.getItem('hfm-theme')).toBe('dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })
})

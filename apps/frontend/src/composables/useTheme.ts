/**
 * useTheme — Theme composable (migrated Batch 2 asset — ADAPT).
 *
 * Source: HFB `apps/frontend/src/composables/useTheme.ts` @ `03755b5`.
 * Adapted: storage key `hfb-theme` → `hfm-theme`; optional-chaining guards on
 * the system-preference listener so the module is safe in test/jsdom
 * environments that lack a full MediaQueryList implementation.
 */
import { ref, watchEffect } from 'vue'

export type Theme = 'light' | 'dark' | 'auto'

const THEME_STORAGE_KEY = 'hfm-theme'
const DARK_CLASS = 'dark'

const theme = ref<Theme>(loadTheme())

function loadTheme(): Theme {
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY)
    if (stored === 'light' || stored === 'dark' || stored === 'auto') {
      return stored
    }
  } catch {
    // localStorage unavailable
  }
  return 'auto'
}

function resolveTheme(value: Theme): 'light' | 'dark' {
  if (value === 'auto') {
    if (
      typeof window !== 'undefined' &&
      window.matchMedia?.('(prefers-color-scheme: dark)')?.matches
    ) {
      return 'dark'
    }
    return 'light'
  }
  return value
}

export function useTheme() {
  watchEffect(() => {
    const resolved = resolveTheme(theme.value)
    document.documentElement.classList.toggle(DARK_CLASS, resolved === 'dark')
  })

  function setTheme(value: Theme): void {
    theme.value = value
    try {
      localStorage.setItem(THEME_STORAGE_KEY, value)
    } catch {
      // ignore
    }
  }

  return {
    theme,
    setTheme,
  }
}

/**
 * Watch system preference changes when theme is 'auto'.
 * Optional chaining guards environments without a MediaQueryList listener.
 */
if (typeof window !== 'undefined') {
  const mql = window.matchMedia?.('(prefers-color-scheme: dark)')
  mql?.addEventListener?.('change', () => {
    if (theme.value === 'auto') {
      document.documentElement.classList.toggle(DARK_CLASS, mql.matches)
    }
  })
}

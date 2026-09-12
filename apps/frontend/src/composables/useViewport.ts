/**
 * Viewport breakpoint hook (P2-01 responsive foundation, AC-05; extended at
 * UI-01 with xl/2xl tiers for ≥1440 content and exhibition-ready canvases).
 *
 * Reports the largest matching breakpoint token so surfaces can switch
 * layout at the responsive matrix (sm/md/lg/xl/2xl). Testable with the
 * jsdom matchMedia stub from test-setup.ts.
 */
import { onMounted, onUnmounted, ref } from 'vue'

export type Breakpoint = 'sm' | 'md' | 'lg' | 'xl' | '2xl'

export const BREAKPOINTS: Readonly<Record<Breakpoint, number>> = {
  sm: 480,
  md: 768,
  lg: 1024,
  xl: 1440,
  '2xl': 1920,
}

function queryFor(breakpoint: Breakpoint): string {
  return `(min-width: ${BREAKPOINTS[breakpoint]}px)`
}

export function currentBreakpoint(): Breakpoint {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
    return 'sm'
  }
  // Largest matching breakpoint wins (descending check).
  if (window.matchMedia(queryFor('2xl')).matches) return '2xl'
  if (window.matchMedia(queryFor('xl')).matches) return 'xl'
  if (window.matchMedia(queryFor('lg')).matches) return 'lg'
  if (window.matchMedia(queryFor('md')).matches) return 'md'
  return 'sm'
}

export function useViewport(): { breakpoint: ReturnType<typeof ref<Breakpoint>> } {
  const breakpoint = ref<Breakpoint>(currentBreakpoint())
  const listeners: Array<() => void> = []
  onMounted(() => {
    for (const name of Object.keys(BREAKPOINTS) as Breakpoint[]) {
      const mql = window.matchMedia(queryFor(name))
      const handler = () => {
        breakpoint.value = currentBreakpoint()
      }
      mql.addEventListener('change', handler)
      listeners.push(() => mql.removeEventListener('change', handler))
    }
  })
  onUnmounted(() => {
    for (const remove of listeners) remove()
  })
  return { breakpoint }
}

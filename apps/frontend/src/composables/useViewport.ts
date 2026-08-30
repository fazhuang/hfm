/**
 * Viewport breakpoint hook (P2-01 responsive foundation, AC-05).
 *
 * Reports the largest matching breakpoint token so surfaces can switch
 * layout at the responsive matrix (sm/md/lg). Testable with the jsdom
 * matchMedia stub from test-setup.ts.
 */
import { onMounted, onUnmounted, ref } from 'vue'

export type Breakpoint = 'sm' | 'md' | 'lg'

export const BREAKPOINTS: Readonly<Record<Breakpoint, number>> = {
  sm: 480,
  md: 768,
  lg: 1024,
}

function queryFor(breakpoint: Breakpoint): string {
  return `(min-width: ${BREAKPOINTS[breakpoint]}px)`
}

export function currentBreakpoint(): Breakpoint {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
    return 'sm'
  }
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

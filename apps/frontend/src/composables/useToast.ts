/**
 * useToast — Toast notification composable (migrated Batch 2 asset — ADAPT).
 *
 * Source: HFB `apps/frontend/src/composables/useToast.ts` @ `03755b5`.
 * Adapted: `hfb-toast-` id prefix → `hfm-toast-`; removed HFB provider naming.
 */
import { ref } from 'vue'

export interface Toast {
  id: string
  message: string
  variant: 'info' | 'success' | 'warning' | 'error'
  title?: string
  duration: number
  closable: boolean
  createdAt: number
}

// Global shared state
const toasts = ref<Array<Toast>>([])
let _id = 0

export interface ToastOptions {
  variant?: 'info' | 'success' | 'warning' | 'error'
  duration?: number
  title?: string
  closable?: boolean
}

export function useToast() {
  function show(message: string, options: ToastOptions = {}): string {
    const id = `hfm-toast-${++_id}`
    const toast: Toast = {
      id,
      message,
      variant: options.variant || 'info',
      title: options.title,
      duration: options.duration ?? 4000,
      closable: options.closable ?? true,
      createdAt: Date.now(),
    }
    toasts.value.push(toast)

    if (toast.duration > 0) {
      setTimeout(() => dismiss(id), toast.duration)
    }

    return id
  }

  function dismiss(id: string) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  function success(message: string, options?: ToastOptions) {
    return show(message, { ...options, variant: 'success' })
  }

  function error(message: string, options?: ToastOptions) {
    return show(message, { ...options, variant: 'error' })
  }

  function warning(message: string, options?: ToastOptions) {
    return show(message, { ...options, variant: 'warning' })
  }

  function info(message: string, options?: ToastOptions) {
    return show(message, { ...options, variant: 'info' })
  }

  return { toasts, show, dismiss, success, error, warning, info }
}

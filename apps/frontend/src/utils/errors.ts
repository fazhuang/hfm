/**
 * Generic API error normalization (migrated Batch 3 asset — PORT).
 *
 * Source: HFB `apps/frontend/src/api/client.ts` (ApiErrorDetail /
 * getApiErrorDetail) @ `03755b5`. Extracted from the axios client file;
 * the helper itself has zero axios coupling. No domain semantics.
 */

export interface ApiErrorDetail {
  status?: number
  message?: string
}

/**
 * Extract { status, message } from an unknown thrown value without `any`.
 * Falls back to the error's own `message` when no response body is present.
 */
export function getApiErrorDetail(e: unknown): ApiErrorDetail {
  if (typeof e !== 'object' || e === null) return {}
  const err = e as {
    response?: {
      status?: number
      data?: { message?: string; detail?: string }
    }
    message?: string
  }
  const body = err.response?.data
  const bodyMsg = body?.message || body?.detail
  return {
    status: err.response?.status,
    message: bodyMsg || err.message,
  }
}

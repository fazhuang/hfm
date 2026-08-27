/**
 * Generic utility helpers (migrated Batch 1 asset — PORT).
 *
 * Source: HFB `packages/utils/src/index.ts` @ `03755b5` (sleep / generateId).
 * No domain coupling; @hfb namespace removed.
 */

/** Delay execution for a given number of milliseconds. */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

/**
 * Generate a random ID (crypto-safe when available).
 */
export function generateId(length: number = 21): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  const randomValues =
    typeof crypto !== 'undefined'
      ? crypto.getRandomValues(new Uint8Array(length))
      : Array.from({ length }, () => Math.floor(Math.random() * 256))
  return Array.from(randomValues, (v) => chars[v % chars.length]!).join('')
}

/**
 * usePublicWorks — WorksView async enrichment with graceful degradation (GAP-02).
 *
 * On mount the view asks the real backend for /api/v1/public/works through
 * the existing public API layer (services/api.ts fetchPublicWorks). The page
 * ALWAYS renders immediately from the static WORK_COLLECTION fallback; this
 * composable only supplies the real published works and a source marker:
 *   source === 'backend'  → request succeeded and carried non-empty works
 *   source === 'fallback' → request failed/timed out/empty → static list
 *
 * Failures never surface raw errors to the UI and never block rendering.
 * Pagination is deferred: page 1 (page_size 20) already covers the current
 * published corpus; the total is exposed for a future pager.
 */
import { onMounted, ref } from 'vue'
import { fetchPublicWorks } from '../services/api'
import type { WorkSummary } from '../types/public'

export type WorksDataSource = 'backend' | 'fallback'

export const WORKS_REQUEST_TIMEOUT_MS = 4000

export function usePublicWorks(fetcher: typeof fetchPublicWorks = fetchPublicWorks) {
  const source = ref<WorksDataSource>('fallback')
  const works = ref<WorkSummary[]>([])
  const total = ref(0)
  const failed = ref(false)

  async function load(): Promise<void> {
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), WORKS_REQUEST_TIMEOUT_MS)
    try {
      const payload = await fetcher(1, controller.signal)
      works.value = payload.works ?? []
      total.value = payload.total ?? 0
      // The source marker is truthful to VISIBLE participation: 'backend' only
      // when the real payload actually carries non-empty works for the page.
      source.value = works.value.length > 0 ? 'backend' : 'fallback'
      failed.value = works.value.length === 0
    } catch {
      // Graceful degradation: the static WORK_COLLECTION remains the page.
      source.value = 'fallback'
      failed.value = true
      works.value = []
      total.value = 0
    } finally {
      clearTimeout(timer)
    }
  }

  onMounted(() => {
    void load()
  })

  return { source, works, total, failed, load }
}

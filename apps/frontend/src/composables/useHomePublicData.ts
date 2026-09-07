/**
 * useHomePublicData (REM-02) — homepage async enrichment with graceful
 * degradation.
 *
 * On mount the orchestrator asks the real backend for /api/v1/public/home
 * through the existing public API layer (services/api.ts fetchPublicHome).
 * The page ALWAYS renders immediately from the frozen projection; this
 * composable only supplies the typed enrichment and a source marker:
 *   source === 'backend'  → request succeeded and payload was mapped
 *   source === 'fallback' → request failed/timed out/invalid → static page
 *
 * Failures never surface raw errors to the UI and never block rendering.
 */
import { onMounted, ref } from 'vue'
import { fetchPublicHome } from '../services/api'
import {
  type HomePublicEnrichment,
  emptyHomeEnrichment,
  mapPublicHomeToEnrichment,
} from '../data/homePublicEnrichment'

export type HomeDataSource = 'backend' | 'fallback'

export const HOME_REQUEST_TIMEOUT_MS = 4000

export function useHomePublicData(fetcher: typeof fetchPublicHome = fetchPublicHome) {
  const source = ref<HomeDataSource>('fallback')
  const enrichment = ref<HomePublicEnrichment>(emptyHomeEnrichment())
  const failed = ref(false)

  async function load(): Promise<void> {
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), HOME_REQUEST_TIMEOUT_MS)
    try {
      const payload = await fetcher(controller.signal)
      enrichment.value = mapPublicHomeToEnrichment(payload)
      source.value = 'backend'
      failed.value = false
    } catch {
      // Graceful degradation: the static homepage projection remains the page.
      source.value = 'fallback'
      failed.value = true
      enrichment.value = emptyHomeEnrichment()
    } finally {
      clearTimeout(timer)
    }
  }

  onMounted(() => {
    void load()
  })

  return { source, enrichment, failed, load }
}

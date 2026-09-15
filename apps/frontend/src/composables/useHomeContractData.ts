/**
 * useHomeContractData — HFM-FRONTEND-CONTENT-CONTRACT v1 §3/§4 data layer.
 *
 * The homepage's T0 (published public projection) fetches, one per contract
 * block, each carrying an explicit `source` marker:
 *   'backend'  → the T0 fetch succeeded; the block renders real DB content
 *   'fallback' → T0 unavailable (backend down / data not published); the block
 *                degrades to its declared T1 customer-material projection and
 *                MUST render a visible fallback note (contract §2 R3 / D3).
 *
 * Failures never throw and never block rendering.
 */
import { onMounted, ref, type Ref } from 'vue'
import {
  fetchPublicHeritage,
  fetchPublicHome,
  fetchPublicPerson,
  fetchPublicWork,
  fetchPublicWorkEditions,
} from '../services/api'
import { CORE_PERSON_ENTITY_ID } from '../config/corePerson'
import type { EditionSummary, HomeProjection, PublicPerson, WorkDetail } from '../types/public'

export type DataSource = 'backend' | 'fallback'

export interface BlockData<T> {
  source: DataSource
  data: T | null
}

/** Canonical ids the contract blocks bind to (DB truth). */
export const CONTRACT_WORK_ID = 'WORK-JIAYI'

function empty<T>(): Ref<BlockData<T>> {
  return ref<BlockData<T>>({ source: 'fallback', data: null }) as Ref<BlockData<T>>
}

export function useHomeContractData() {
  const home = empty<HomeProjection>()
  const person = empty<PublicPerson>()
  const work = empty<WorkDetail>()
  const editions = empty<EditionSummary[]>()
  const heritage = empty<unknown[]>()

  async function load<T>(target: Ref<BlockData<T>>, fetcher: () => Promise<T>): Promise<void> {
    try {
      const data = await fetcher()
      target.value = { source: 'backend', data }
    } catch {
      target.value = { source: 'fallback', data: null }
    }
  }

  onMounted(() => {
    void Promise.all([
      load(home, () => fetchPublicHome()),
      load(person, () => fetchPublicPerson(CORE_PERSON_ENTITY_ID)),
      load(work, () => fetchPublicWork(CONTRACT_WORK_ID)),
      load(editions, () => fetchPublicWorkEditions(CONTRACT_WORK_ID).then((r) => r.editions)),
      load(heritage, () => fetchPublicHeritage().then((r) => r.projects)),
    ])
  })

  return { home, person, work, editions, heritage }
}

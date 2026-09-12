<script setup lang="ts">
/**
 * PersonDetailView — CF-03 Person Archive (recovery runtime).
 *
 * The production person archive is rebuilt on the real Golden chain:
 *
 *   PostgreSQL → FastAPI /api/v1/public/persons/:id → Vite /api proxy
 *     → PersonDetailView → CF-02 DHObjectLayout/stateMapping → browser render
 *
 * Data source policy (CF-03):
 *   - the ONLY runtime source is GET /api/v1/public/persons/:id — no local
 *     fixture, no hard-coded Huangfu Mi object, no searchIndex, no donor
 *     static object as runtime data;
 *   - API DATA → PROJECTION → PRESENTATION; the view never invents a domain
 *     fact for visual completeness;
 *   - a field missing from the real projection is presented as ABSENT /
 *     PARTIAL / UNKNOWN — never fabricated.
 *
 * Ownership boundary (CF-03 §8):
 *   - this view owns: route parameter, data-loading orchestration, API state
 *     (loading / ready / not-found / error), person-specific projection and
 *     page composition;
 *   - CF-02 primitives own: presentation, state display, metadata layout and
 *     the status/provenance band. They do no fetching and no person logic.
 *
 * Page states are discriminated (CF-03 §7):
 *   - 404 (ApiError status 404) → dedicated NOT_FOUND presentation;
 *   - other ApiError / network failure → dedicated ERROR presentation;
 *   - a missing optional field is never a page failure;
 *   - an /api HTML fallback would surface through the CF-01 gate monitors.
 */
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ApiError, fetchPublicPerson } from '../../services/api'
import type { PersonAssertion, PersonEvent, PublicPerson } from '../../types/public'
import DHObjectLayout from '../../components/primitives/DHObjectLayout.vue'
import ErrorState from '../../components/states/ErrorState.vue'
import LoadingState from '../../components/states/LoadingState.vue'

defineOptions({ name: 'PersonDetailView' })

type PageStatus = 'loading' | 'ready' | 'not-found' | 'error'

/* Structural mirrors of the DHObjectLayout slot contract (presentation only). */
type PersonRegion = 'header' | 'context' | 'evidence' | 'relations'
type PersonSlotState = 'PRESENT' | 'ABSENT_OPTIONAL' | 'INCOMPLETE_WITH_EVIDENCE_STATE'
interface PersonSlot {
  state: PersonSlotState
  status?: string
  statusLabel?: string
  note?: string
}
interface MetaItem {
  label?: string
  value: string
}

const route = useRoute()
const status = ref<PageStatus>('loading')
const person = ref<PublicPerson | null>(null)
const errorMessage = ref<string | null>(null)

/** Regional IA labels for the person archive (CF-02 regionLabels override). */
const regionLabels = {
  header: '人物档案',
  context: '生平',
  evidence: '史料依据',
  relations: '关联',
} as const

/** Publication-state label map (publication_status from the real API). The API
 * emits enum-style uppercase values (e.g. PUBLISHED); normalization is
 * case-insensitive so the presentation survives contract casing changes. */
const PUBLICATION_LABELS: Record<string, string> = {
  PUBLISHED: '已发布',
  DRAFT: '草稿',
  WITHDRAWN: '已撤回',
}

const identityName = computed<string>(() => person.value?.name_zh?.trim() ?? '')
const events = computed<PersonEvent[]>(() => person.value?.events ?? [])
const assertions = computed<PersonAssertion[]>(() => person.value?.assertions ?? [])

/** Only fields actually present in the real projection are shown. */
const identityMeta = computed<MetaItem[]>(() => {
  const p = person.value
  if (p === null) return []
  const meta: MetaItem[] = []
  const push = (label: string, raw: string | null | undefined): void => {
    const value = raw?.trim()
    if (value !== undefined && value !== '') meta.push({ label, value })
  }
  push('拼音', p.name_pinyin)
  push('朝代', p.dynasty)
  push('字', p.courtesy_name)
  push('号', p.pseudonym)
  return meta
})

/**
 * Region slot projection:
 *   - data present        → PRESENT (slot content renders);
 *   - known empty depth   → INCOMPLETE_WITH_EVIDENCE_STATE with a PARTIAL
 *                           status band + static note (never a live region);
 *   - no region concept   → ABSENT_OPTIONAL (collapses, no empty card).
 */
function depthSlot(kind: string, count: number): PersonSlot {
  if (count > 0) return { state: 'PRESENT' }
  return {
    state: 'INCOMPLETE_WITH_EVIDENCE_STATE',
    status: 'PARTIAL',
    note: `${kind}信息暂未收录。`,
  }
}

const archiveSlots = computed<Record<PersonRegion, PersonSlot>>(() => ({
  header: { state: 'PRESENT' },
  context: depthSlot('生平编年', events.value.length),
  evidence: depthSlot('史料断言', assertions.value.length),
  relations: { state: 'ABSENT_OPTIONAL' },
}))

/** Record-level publication state is shown only when the API provides it. */
const publicationNote = computed<string>(() => {
  const p = person.value
  if (p === null) return ''
  const raw = p.publication_status
  if (raw === undefined || raw === null || raw === '') return ''
  const normalized = raw.toUpperCase()
  const label = PUBLICATION_LABELS[normalized] ?? raw
  return `档案发布状态：${label}`
})

async function loadPerson(entityId: string): Promise<void> {
  status.value = 'loading'
  person.value = null
  errorMessage.value = null
  try {
    const record = await fetchPublicPerson(entityId)
    if (record === null || record === undefined) {
      status.value = 'not-found'
      return
    }
    person.value = record
    status.value = 'ready'
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) {
      status.value = 'not-found'
      return
    }
    errorMessage.value =
      err instanceof ApiError && err.message !== '' ? err.message : '人物资料加载失败，请稍后重试。'
    status.value = 'error'
  }
}

onMounted(() => {
  void loadPerson(String(route.params.id ?? ''))
})

watch(
  () => route.params.id,
  (id) => {
    void loadPerson(String(id ?? ''))
  },
)
</script>

<template>
  <section
    class="person-page"
    :aria-label="`人物档案${identityName !== '' ? '：' + identityName : ''}`"
  >
    <p class="person-page__back">
      <a class="back-link" href="/">← 返回首页</a>
    </p>

    <LoadingState v-if="status === 'loading'" label="正在加载人物档案…" />

    <template v-else-if="status === 'not-found'">
      <div class="person-page__state" data-page-state="not-found">
        <h1 class="person-page__state-title">未找到该人物档案</h1>
        <p class="person-page__state-text">
          该档案不存在或尚未发布。请返回<a class="back-link" href="/">首页</a>继续浏览。
        </p>
      </div>
    </template>

    <div v-else-if="status === 'error'" data-page-state="error">
      <ErrorState :message="errorMessage ?? '人物资料加载失败，请稍后重试。'" />
    </div>

    <template v-else>
      <DHObjectLayout
        class="person-archive"
        :title="identityName !== '' ? identityName : '未命名人物'"
        :title-tag="1"
        :meta="identityMeta"
        :slots="archiveSlots"
        :region-labels="regionLabels"
      >
        <!-- 生平: renders ONLY real API events (region PRESENT). -->
        <template v-if="events.length > 0" #context>
          <ul class="person-events" data-primitive="person-events" aria-label="生平事件">
            <li v-for="event in events" :key="event.event_id" class="person-events__item">
              <span class="person-events__role">{{ event.role }}</span>
              <span v-if="event.description" class="person-events__description">
                {{ event.description }}
              </span>
            </li>
          </ul>
        </template>

        <!-- 史料依据: renders ONLY real API assertions (region PRESENT). -->
        <template v-if="assertions.length > 0" #evidence>
          <ul class="person-assertions" data-primitive="person-assertions" aria-label="史料断言">
            <li v-for="assertion in assertions" :key="assertion.id" class="person-assertions__item">
              <p class="person-assertions__value">
                {{ assertion.value }}
              </p>
              <p class="person-assertions__meta">
                <span v-if="assertion.predicate" class="person-assertions__predicate">
                  {{ assertion.predicate }}
                </span>
                <span v-if="assertion.confidence" class="person-assertions__confidence">
                  {{ assertion.confidence }}
                </span>
                <span
                  v-if="Array.isArray(assertion.evidence_ids) && assertion.evidence_ids.length > 0"
                  class="person-assertions__evidence"
                  >证据 ×{{ assertion.evidence_ids.length }}</span
                >
              </p>
            </li>
          </ul>
        </template>
      </DHObjectLayout>

      <p
        v-if="publicationNote !== ''"
        class="person-page__publication"
        data-record-publication="true"
      >
        {{ publicationNote }}
      </p>
    </template>
  </section>
</template>

<style scoped>
.person-page {
  max-width: var(--hfm-content-max);
  margin: 0 auto;
}

.person-page__back {
  margin: 0 0 var(--hfm-space-4);
}

.back-link {
  color: var(--hfm-color-interactive);
  text-decoration: none;
}

.person-page__state {
  padding: var(--hfm-space-12) var(--hfm-space-6);
  text-align: center;
}

.person-page__state-title {
  font-size: var(--hfm-text-2xl);
  margin: 0 0 var(--hfm-space-3);
}

.person-page__state-text {
  color: var(--hfm-color-text-secondary);
  margin: 0;
}

.person-page__publication {
  margin-top: var(--hfm-space-4);
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

/* 生平 events (context region content). */
.person-events {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-2);
}

.person-events__item {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2) var(--hfm-space-4);
  padding: var(--hfm-space-2) 0;
  font-size: var(--hfm-text-sm);
}

.person-events__role {
  font-weight: 600;
  color: var(--hfm-color-text);
}

.person-events__description {
  color: var(--hfm-color-text-secondary);
}

/* 史料依据 assertions (evidence region content). */
.person-assertions {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-3);
}

.person-assertions__item {
  padding: var(--hfm-space-3) var(--hfm-space-4);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
}

.person-assertions__value {
  margin: 0 0 var(--hfm-space-2);
  line-height: var(--hfm-leading-reading);
}

.person-assertions__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2) var(--hfm-space-3);
  align-items: center;
  margin: 0;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.person-assertions__predicate {
  padding: 2px var(--hfm-space-2);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-canvas);
}

.person-assertions__evidence {
  font-weight: 600;
  color: var(--hfm-color-text-secondary);
}
</style>

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
import Timeline from '../../components/Timeline.vue'
import { mediaBytesUrl } from '../../services/media'
import type { TimelineEvent } from '../../types/timeline'
import {
  CORE_PERSON_DATES,
  CORE_PERSON_DEFINITION,
  CORE_PERSON_ENTITY_ID,
  CORE_PERSON_IDENTITIES,
  CORE_PERSON_LIFE_PHASES,
  CORE_PERSON_NAME,
  CORE_PERSON_PORTRAIT_MEDIA_ID,
  CORE_PERSON_WORKS,
} from '../../config/corePerson'
import { HOURAN_TABLES } from '../../data/houranTables'

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

/**
 * 核心人物（皇甫谧）走叙事长页；其余人物沿用通用档案版式。
 *
 * 门户的定位是信息展示，其人模块的判据是「外行看得懂」。因此核心人物页由
 * 定位 / 画像 / 年表 / 传略 / 延伸 五段构成，按宪章 §3.1。通用版式保留给
 * 其余 16 位人物——他们只有档案数据，没有叙事可讲。
 */
const isCorePerson = computed<boolean>(() => route.params.id === CORE_PERSON_ENTITY_ID)

/** 画像：只存资产 id，地址由 services/media.ts 构造。 */
const portraitUrl = mediaBytesUrl(CORE_PERSON_PORTRAIT_MEDIA_ID)

/** 人生四阶段 → 年表节点。阶段说明放进 description。 */
const lifePhases = computed<TimelineEvent[]>(() =>
  CORE_PERSON_LIFE_PHASES.map((phase, index) => ({
    id: `phase-${index + 1}`,
    title: phase.title,
    description: phase.note,
  })),
)
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
      <!-- 核心人物：叙事长页（宪章 §3.1 五段） -->
      <template v-if="isCorePerson">
        <header class="core-hero">
          <div class="core-hero__text">
            <p class="hfm-eyebrow">西晋 · 数字人文</p>
            <h1 class="core-hero__name">{{ CORE_PERSON_NAME }}</h1>
            <p class="core-hero__dates">{{ CORE_PERSON_DATES }}</p>
            <p class="core-hero__definition">{{ CORE_PERSON_DEFINITION }}</p>
            <ul class="core-hero__identities" aria-label="身份">
              <li v-for="identity in CORE_PERSON_IDENTITIES" :key="identity">
                {{ identity }}
              </li>
            </ul>
          </div>
          <figure class="core-hero__portrait">
            <img :src="portraitUrl" :alt="`${CORE_PERSON_NAME}画像`" />
            <figcaption>{{ CORE_PERSON_NAME }}画像 · 客户提供资料</figcaption>
          </figure>
        </header>

        <section class="core-section" aria-labelledby="core-life-heading">
          <h2 id="core-life-heading" class="core-section__title">生平</h2>
          <Timeline :events="lifePhases" label="人生阶段" />
        </section>

        <section class="core-section" aria-labelledby="core-reception-heading">
          <h2 id="core-reception-heading" class="core-section__title">历代与当代</h2>
          <p class="core-section__lede">
            后世对皇甫谧的评价，以及今日以他命名的影视、著述与机构（据客户资料整理）。
          </p>
          <div
            v-for="table in HOURAN_TABLES"
            :key="table.id"
            class="core-table-block"
          >
            <h3 class="core-table-block__title">{{ table.label }}</h3>
            <!-- 窄屏下表格横向滚动；滚动区必须可聚焦，否则键盘用户够不到
                 （axe: scrollable-region-focusable）。 -->
            <div
              class="core-table-wrap"
              tabindex="0"
              role="region"
              :aria-label="`${table.label}表格，可横向滚动`"
            >
              <table class="core-table">
                <thead>
                  <tr>
                    <th v-for="col in table.columns" :key="col" scope="col">{{ col }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, i) in table.rows" :key="i">
                    <td v-for="(cell, j) in row" :key="j">{{ cell }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <section class="core-section" aria-labelledby="core-more-heading">
          <h2 id="core-more-heading" class="core-section__title">延伸阅读</h2>
          <ul class="core-more">
            <li v-for="work in CORE_PERSON_WORKS" :key="work.title">
              <a class="core-more__link" :href="work.href">{{ work.title }}</a>
              <span class="core-more__note">{{ work.note }}</span>
            </li>
          </ul>
        </section>
      </template>

      <!-- 其余人物：通用档案版式 -->
      <DHObjectLayout
        v-else
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

/* ---------- 核心人物叙事长页（P-7） ----------
   判据是「外行看得懂」：字号、行距、留白优先于信息密度。
   画像与定位文并排，窄屏堆叠。 */

.core-hero {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--hfm-space-6);
  margin-bottom: var(--hfm-space-12);
}
@media (min-width: 768px) {
  .core-hero {
    grid-template-columns: minmax(0, 1fr) minmax(0, 20rem);
    align-items: start;
    gap: var(--hfm-space-8);
  }
}
.core-hero__name {
  margin: var(--hfm-space-2) 0 0;
  font-family: var(--hfm-font-display);
  font-size: var(--hfm-text-4xl);
  letter-spacing: var(--hfm-tracking-display);
  color: var(--hfm-color-text);
}
.core-hero__dates {
  margin: var(--hfm-space-2) 0 0;
  font-family: var(--hfm-font-numeric);
  font-size: var(--hfm-text-lg);
  color: var(--hfm-color-text-muted);
  letter-spacing: 0.08em;
}
.core-hero__definition {
  margin: var(--hfm-space-5) 0 0;
  max-width: var(--hfm-reader-max);
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-lg);
  line-height: var(--hfm-leading-reading);
  color: var(--hfm-color-text-secondary);
}
.core-hero__identities {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2) var(--hfm-space-3);
  margin: var(--hfm-space-5) 0 0;
  padding: 0;
  list-style: none;
}
.core-hero__identities li {
  padding: var(--hfm-space-1) var(--hfm-space-3);
  font-size: var(--hfm-text-xs);
  letter-spacing: var(--hfm-tracking-display);
  color: var(--hfm-color-text-secondary);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
}
.core-hero__portrait {
  margin: 0;
}
.core-hero__portrait img {
  display: block;
  width: 100%;
  height: auto;
  border: 1px solid var(--hfm-color-border);
}
.core-hero__portrait figcaption {
  margin-top: var(--hfm-space-2);
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.core-section {
  margin-bottom: var(--hfm-space-16);
}
.core-section__title {
  margin: 0 0 var(--hfm-space-5);
  padding-bottom: var(--hfm-space-3);
  font-family: var(--hfm-font-heading);
  font-size: var(--hfm-text-2xl);
  letter-spacing: var(--hfm-tracking-display);
  color: var(--hfm-color-text);
  border-bottom: 1px solid var(--hfm-color-border);
}
.core-section__lede {
  margin: 0 0 var(--hfm-space-6);
  max-width: var(--hfm-reader-max);
  font-size: var(--hfm-text-sm);
  line-height: var(--hfm-leading-normal);
  color: var(--hfm-color-text-muted);
}

.core-table-block {
  margin-bottom: var(--hfm-space-8);
}
.core-table-block__title {
  margin: 0 0 var(--hfm-space-3);
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-lg);
  letter-spacing: 0.06em;
  color: var(--hfm-color-text);
}
/* 表格允许横滚，页面本身不横滚。 */
.core-table-wrap {
  overflow-x: auto;
}
.core-table-wrap:focus-visible {
  outline: 2px solid var(--hfm-color-interactive);
  outline-offset: 2px;
}
.core-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--hfm-text-sm);
  line-height: var(--hfm-leading-normal);
}
.core-table th,
.core-table td {
  padding: var(--hfm-space-3);
  text-align: left;
  vertical-align: top;
  border-bottom: 1px solid var(--hfm-color-border);
}
.core-table th {
  font-family: var(--hfm-font-heading);
  font-size: var(--hfm-text-xs);
  font-weight: normal;
  letter-spacing: var(--hfm-tracking-display);
  color: var(--hfm-color-text-muted);
  white-space: nowrap;
}
.core-table td {
  color: var(--hfm-color-text-secondary);
}
/* 首列序号与次列主体不换行挤压，末列说明给足宽度。 */
.core-table td:first-child {
  color: var(--hfm-color-text-muted);
  white-space: nowrap;
}

.core-more {
  margin: 0;
  padding: 0;
  list-style: none;
}
.core-more li {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--hfm-space-3);
  padding: var(--hfm-space-3) 0;
  border-bottom: 1px solid var(--hfm-color-border);
}
.core-more__link {
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-base);
  color: var(--hfm-color-text);
  text-decoration: none;
  border-bottom: 1px solid var(--hfm-color-border-strong);
}
.core-more__link:hover {
  color: var(--hfm-color-interactive);
}
.core-more__note {
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}
</style>

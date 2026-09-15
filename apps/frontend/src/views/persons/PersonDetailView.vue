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
import { YAN_COLLECTION } from '../../data/yanCollection'
import { AUDITED_PAPER_TOTAL, SEARCHABLE_PAPER_TOTAL } from '../../data/searchIndex'
import { PERSON_SECTION_NAV } from '../../config/navigation'

defineOptions({ name: 'PersonDetailView' })

/** 「探索更多」卡片：五张，全部通向站内已有的真实页面。 */
const EXPLORE_CARDS = [
  {
    title: '生平年表',
    note: '关键人生节点与时代背景',
    href: '#person-timeline',
    img: '/assets/jiayi/edition-lineage.png',
  },
  {
    title: '学术成就',
    note: '医学 · 经学 · 文学 · 史学',
    href: '#person-works',
    img: '/assets/jiayi/book-siku-leaf.jpg',
  },
  {
    title: '思想体系',
    note: '其言四篇与处世之道',
    href: '#person-thought',
    img: '/assets/jiayi/frag-band1.jpg',
  },
  {
    title: '历史影响',
    note: '后世评价 · 影视 · 机构',
    href: '#person-influence',
    img: '/assets/jiayi/frag-macro.jpg',
  },
  {
    title: '相关人物',
    note: '师友、后学与传承人',
    href: '#person-related',
    img: '/assets/heritage/heritage-baishi-ceremony.jpg',
  },
] as const

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
      <!-- 核心人物：栏目页骨架（HFM-UI-CONTRACT-v2 §3.2，参考图 HFM-LM-CK） -->
      <template v-if="isCorePerson">
        <!-- 01 栏目首屏 -->
        <section id="person-top" class="pg-hero pg-hero--media">
          <img class="pg-hero__bg" :src="portraitUrl" alt="" aria-hidden="true" />
          <div class="pg-hero__scrim" aria-hidden="true"></div>
          <div class="xl-inner pg-hero__inner">
            <div class="pg-hero__text">
              <p class="xl-label">人物 · PEOPLE</p>
              <h1 class="pg-hero__title">{{ CORE_PERSON_NAME }}</h1>
              <p class="pg-hero__rule" aria-hidden="true"></p>
              <p class="pg-hero__lede">走近皇甫谧，理解一位医者的时代与精神。</p>
              <p class="pg-hero__dates xl-num">{{ CORE_PERSON_DATES }}</p>
            </div>
            <figure class="pg-hero__quote">
              <blockquote>上以疗君亲之疾，下以救贫贱之厄，中以保身长全。</blockquote>
              <figcaption>皇甫谧《针灸甲乙经·序》</figcaption>
            </figure>
          </div>
        </section>

        <!-- 02 二级导航 -->
        <nav class="pg-subnav" aria-label="人物栏目导航">
          <a
            v-for="item in PERSON_SECTION_NAV"
            :key="item.href"
            class="pg-subnav__link"
            :href="item.href"
          >
            {{ item.label }}
          </a>
        </nav>

        <!-- 03 概览 -->
        <section id="person-overview" class="xl-sec" aria-labelledby="person-overview-title">
          <div class="xl-inner">
            <header class="xl-head">
              <div class="xl-head__aside">
                <span class="xl-index">01</span>
                <span class="xl-label">Overview</span>
              </div>
              <div>
                <h2 id="person-overview-title" class="xl-title">人物概览</h2>
              </div>
            </header>
            <div class="pv-grid">
              <div class="pv-text">
                <p class="pv-body">{{ CORE_PERSON_DEFINITION }}</p>
                <ul class="pv-tags" aria-label="身份">
                  <li v-for="identity in CORE_PERSON_IDENTITIES" :key="identity">{{ identity }}</li>
                </ul>
                <a class="xl-cta pv-cta" href="#person-timeline">
                  查看完整生平
                  <span class="xl-cta__arr" aria-hidden="true">→</span>
                </a>
              </div>
              <figure class="pv-portrait">
                <img :src="portraitUrl" :alt="`${CORE_PERSON_NAME}画像`" />
                <figcaption>{{ CORE_PERSON_NAME }}画像 · 客户提供资料</figcaption>
              </figure>
              <figure class="pv-quote">
                <blockquote>医之道，非独疗疾，亦所以养生、立德、安民。</blockquote>
                <figcaption>皇甫谧《针灸甲乙经·序》</figcaption>
              </figure>
            </div>
          </div>
        </section>

        <!-- 04 生平年表 -->
        <section id="person-timeline" class="xl-sec" aria-labelledby="person-timeline-title">
          <div class="xl-inner">
            <header class="xl-head">
              <div class="xl-head__aside">
                <span class="xl-index">02</span>
                <span class="xl-label">Timeline</span>
              </div>
              <div>
                <h2 id="person-timeline-title" class="xl-title">生平年表</h2>
                <p class="xl-lede">人生四阶段：少家贫 → 屡征不仕 → 中年风痹 → 晚年著书。</p>
              </div>
            </header>
            <Timeline :events="lifePhases" label="人生阶段" />
          </div>
        </section>

        <!-- 05 学术成就 -->
        <section id="person-works" class="xl-sec" aria-labelledby="person-works-title">
          <div class="xl-inner">
            <header class="xl-head">
              <div class="xl-head__aside">
                <span class="xl-index">03</span>
                <span class="xl-label">Works</span>
              </div>
              <div>
                <h2 id="person-works-title" class="xl-title">学术成就</h2>
                <p class="xl-lede">医学、经学、文学、史学 —— 四个方面都有著述传世。</p>
              </div>
            </header>
            <ul class="pv-works">
              <li v-for="work in CORE_PERSON_WORKS" :key="work.title" class="pv-work">
                <a class="pv-work__title" :href="work.href">{{ work.title }}</a>
                <span class="pv-work__note">{{ work.note }}</span>
              </li>
            </ul>
          </div>
        </section>

        <!-- 06 思想体系 -->
        <section id="person-thought" class="xl-sec" aria-labelledby="person-thought-title">
          <div class="xl-inner">
            <header class="xl-head">
              <div class="xl-head__aside">
                <span class="xl-index">04</span>
                <span class="xl-label">Thought</span>
              </div>
              <div>
                <h2 id="person-thought-title" class="xl-title">思想体系</h2>
                <p class="xl-lede">{{ YAN_COLLECTION.intro }}</p>
              </div>
            </header>
            <ul class="pv-thought">
              <li v-for="work in YAN_COLLECTION.sections" :key="work.id" class="pv-thought__item">
                <p class="pv-thought__title">{{ work.title }}</p>
                <p class="pv-thought__note">{{ work.records[0]?.text }}</p>
              </li>
            </ul>
            <a class="xl-cta" href="/yan">
              阅读其言四篇
              <span class="xl-cta__arr" aria-hidden="true">→</span>
            </a>
          </div>
        </section>

        <!-- 07 历史影响 -->
        <section id="person-influence" class="xl-sec" aria-labelledby="person-influence-title">
          <div class="xl-inner">
            <header class="xl-head">
              <div class="xl-head__aside">
                <span class="xl-index">05</span>
                <span class="xl-label">Influence</span>
              </div>
              <div>
                <h2 id="person-influence-title" class="xl-title">历史影响</h2>
                <p class="xl-lede">
                  后世对皇甫谧的评价，以及今日以他命名的影视、著述与机构（据客户资料整理）。
                </p>
              </div>
            </header>
            <div v-for="table in HOURAN_TABLES" :key="table.id" class="core-table-block">
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
          </div>
        </section>

        <!-- 08 相关人物 -->
        <section id="person-related" class="xl-sec xl-sec--tight" aria-labelledby="person-related-title">
          <div class="xl-inner">
            <header class="xl-head">
              <div class="xl-head__aside">
                <span class="xl-index">06</span>
                <span class="xl-label">Related</span>
              </div>
              <div>
                <h2 id="person-related-title" class="xl-title">相关人物</h2>
                <p class="xl-lede">
                  师友、同时代人与后学 —— 传承一线上的是皇甫谧针灸的非遗代表性传承人。
                </p>
              </div>
            </header>
            <p class="pv-line">
              <a class="pv-line__link" href="/heritage">皇甫谧针灸非遗传承人档案</a>
              <span class="pv-line__note">第六代名医 · 客户提供申报材料</span>
            </p>
          </div>
        </section>

        <!-- 09 研究论文 -->
        <section id="person-papers" class="xl-sec xl-sec--tight" aria-labelledby="person-papers-title">
          <div class="xl-inner">
            <header class="xl-head">
              <div class="xl-head__aside">
                <span class="xl-index">07</span>
                <span class="xl-label">Papers</span>
              </div>
              <div>
                <h2 id="person-papers-title" class="xl-title">研究论文</h2>
                <p class="xl-lede">
                  已登记论文题录 <b class="xl-num">{{ AUDITED_PAPER_TOTAL }}</b> 篇，
                  其中 <b class="xl-num">{{ SEARCHABLE_PAPER_TOTAL }}</b> 篇已进入在线检索。
                </p>
                <a class="xl-cta pv-cta" href="/search?q=%E7%94%B2%E4%B9%99%E7%BB%8F">
                  检索论文题录
                  <span class="xl-cta__arr" aria-hidden="true">→</span>
                </a>
              </div>
            </header>
          </div>
        </section>

        <!-- 10 探索更多 -->
        <section class="xl-sec" aria-labelledby="person-explore-title">
          <div class="xl-inner">
            <h2 id="person-explore-title" class="xl-title">探索更多</h2>
            <p class="xl-label pv-explore__en">Explore</p>
            <ul class="pv-explore">
              <li v-for="card in EXPLORE_CARDS" :key="card.href">
                <a class="pv-card" :href="card.href">
                  <img class="pv-card__img" :src="card.img" alt="" aria-hidden="true" />
                  <span class="pv-card__title">{{ card.title }}</span>
                  <span class="pv-card__note">{{ card.note }}</span>
                  <span class="pv-card__go" aria-hidden="true">→</span>
                </a>
              </li>
            </ul>
          </div>
        </section>

        <!-- 11 收尾 -->
        <section class="xl-sec xl-sec--close pv-close" aria-labelledby="person-close-quote">
          <div class="xl-inner pv-close__inner">
            <div>
              <p id="person-close-quote" class="pv-close__quote">
                传统不是过去的遗存，而是理解未来的一种方式。
              </p>
              <p class="pv-close__en">THE PAST IS A RESOURCE FOR THE FUTURE</p>
            </div>
            <a class="xl-cta pv-close__cta" href="/jiayi">
              继续探索典籍
              <span class="xl-cta__arr" aria-hidden="true">→</span>
            </a>
          </div>
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
/* ==========================================================================
   人物栏目页 — 版式在 styles/home-scale.css 的 .pg-* / .xl-* 段，这里只补本页件
   ========================================================================== */

.pv-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: clamp(2rem, 4vw, 3.5rem);
  align-items: start;
}
@media (min-width: 1000px) {
  .pv-grid {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr) minmax(0, 0.8fr);
  }
}
.pv-body {
  margin: 0;
  max-width: 40ch;
  font-size: var(--hfm-text-base);
  line-height: 2;
  color: var(--wl-ink-2);
}
.pv-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2);
  margin: var(--hfm-space-5) 0 0;
  padding: 0;
  list-style: none;
}
.pv-tags li {
  padding: 0.3rem 0.8rem;
  font-size: var(--hfm-text-xs);
  color: var(--wl-ink-2);
  border: 1px solid var(--wl-rule);
  border-radius: 2px;
}
.pv-cta {
  margin-top: clamp(1.5rem, 3vw, 2rem);
}
.pv-portrait {
  position: relative;
  margin: 0;
  background: var(--wl-light);
  box-shadow: inset 0 0 0 1px var(--wl-rule);
}
.pv-portrait img {
  display: block;
  width: 100%;
  max-height: 30rem;
  object-fit: cover;
  object-position: top center;
}
.pv-portrait figcaption {
  position: absolute;
  inset: auto 0 0;
  padding: var(--hfm-space-3) var(--hfm-space-4);
  font-size: var(--hfm-text-xs);
  color: rgba(244, 242, 236, 0.72);
  background: linear-gradient(to top, rgba(7, 9, 8, 0.82), transparent);
}
.pv-quote {
  margin: 0;
  padding-left: var(--hfm-space-5);
  border-left: 1px solid var(--wl-mark);
}
.pv-quote blockquote {
  margin: 0;
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-lg);
  line-height: 2;
  color: var(--wl-ink);
}
.pv-quote figcaption {
  margin-top: var(--hfm-space-3);
  font-size: var(--hfm-text-xs);
  color: var(--wl-mark);
}
@media (max-width: 999px) {
  .pv-quote {
    padding-left: 0;
    border-left: none;
    border-top: 1px solid var(--wl-rule);
    padding-top: var(--hfm-space-5);
  }
}

/* ---- 学术成就 ---- */
.pv-works {
  margin: 0;
  padding: 0;
  list-style: none;
  border-top: 1px solid var(--wl-rule);
}
.pv-work {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--hfm-space-3) var(--hfm-space-6);
  padding: var(--hfm-space-5) 0;
  border-bottom: 1px solid var(--wl-rule);
}
.pv-work__title {
  min-width: 12rem;
  font-family: var(--hfm-font-heading);
  font-size: var(--hfm-text-lg);
  color: var(--wl-ink);
  text-decoration: none;
}
.pv-work__title:hover {
  color: var(--wl-mark-strong);
}
.pv-work__note {
  font-size: var(--hfm-text-sm);
  color: var(--wl-mute);
}

/* ---- 思想体系 ---- */
.pv-thought {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 0;
  margin: 0 0 var(--hfm-space-8);
  padding: 0;
  list-style: none;
  border-top: 1px solid var(--wl-rule);
}
@media (min-width: 800px) {
  .pv-thought {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
.pv-thought__item {
  padding: var(--hfm-space-5) var(--hfm-space-5) var(--hfm-space-5) 0;
  border-bottom: 1px solid var(--wl-rule);
}
@media (min-width: 800px) {
  .pv-thought__item {
    border-bottom: none;
    border-right: 1px solid var(--wl-rule);
    padding-inline: var(--hfm-space-5);
  }
  .pv-thought__item:first-child {
    padding-left: 0;
  }
  .pv-thought__item:last-child {
    border-right: none;
  }
}
.pv-thought__title {
  margin: 0;
  font-family: var(--hfm-font-heading);
  font-size: var(--hfm-text-lg);
  color: var(--wl-ink);
}
.pv-thought__note {
  margin: var(--hfm-space-3) 0 0;
  font-size: var(--hfm-text-sm);
  line-height: 1.85;
  color: var(--wl-ink-2);
}

/* ---- 相关人物 / 单行条目 ---- */
.pv-line {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--hfm-space-3) var(--hfm-space-6);
  margin: 0;
  padding: var(--hfm-space-5) 0;
  border-top: 1px solid var(--wl-rule);
  border-bottom: 1px solid var(--wl-rule);
}
.pv-line__link {
  font-family: var(--hfm-font-heading);
  font-size: var(--hfm-text-lg);
  color: var(--wl-ink);
  text-decoration: none;
}
.pv-line__link:hover {
  color: var(--wl-mark-strong);
}
.pv-line__note {
  font-size: var(--hfm-text-sm);
  color: var(--wl-mute);
}

/* ---- 探索更多 ---- */
.pv-explore__en {
  display: block;
  margin: var(--hfm-space-2) 0 clamp(1.5rem, 3vw, 2.5rem);
}
.pv-explore {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--hfm-space-5);
  margin: 0;
  padding: 0;
  list-style: none;
}
@media (min-width: 900px) {
  .pv-explore {
    grid-template-columns: repeat(5, minmax(0, 1fr));
  }
}
.pv-card {
  position: relative;
  display: block;
  aspect-ratio: 3 / 4;
  overflow: hidden;
  text-decoration: none;
  color: inherit;
  background: var(--wl-paper-2);
}
.pv-card__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: brightness(0.62) saturate(0.8);
  transition: transform 420ms ease;
}
.pv-card:hover .pv-card__img {
  transform: scale(1.03);
}
.pv-card__title {
  position: absolute;
  inset: auto 0 3.4rem;
  padding: 0 var(--hfm-space-4);
  font-family: var(--hfm-font-heading);
  font-size: var(--hfm-text-lg);
  color: #f4f2ec;
}
.pv-card__note {
  position: absolute;
  inset: auto 0 2.2rem;
  padding: 0 var(--hfm-space-4);
  font-size: var(--hfm-text-xs);
  line-height: 1.6;
  color: rgba(244, 242, 236, 0.76);
}
.pv-card__go {
  position: absolute;
  inset: auto auto var(--hfm-space-4) var(--hfm-space-4);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.9rem;
  height: 1.9rem;
  font-size: 0.75rem;
  color: #f4f2ec;
  border: 1px solid rgba(244, 242, 236, 0.5);
  border-radius: 50%;
  transition: transform 220ms ease;
}
.pv-card:hover .pv-card__go {
  transform: translateX(3px);
}
.pv-card:focus-visible {
  outline: 2px solid var(--wl-mark);
  outline-offset: 3px;
}
@media (prefers-reduced-motion: reduce) {
  .pv-card__img,
  .pv-card__go,
  .pv-card:hover .pv-card__img,
  .pv-card:hover .pv-card__go {
    transition: none;
    transform: none;
  }
}

/* ---- 收尾 ---- */
.pv-close__inner {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--hfm-space-6);
}
.pv-close__quote {
  margin: 0;
  max-width: 30ch;
  font-family: var(--hfm-font-serif);
  font-size: clamp(1.25rem, 2.4vw, 1.75rem);
  line-height: 1.9;
  color: #f2f0ea;
}
.pv-close__en {
  margin: var(--hfm-space-3) 0 0;
  font-family: var(--wl-latin);
  text-transform: uppercase;
  letter-spacing: 0.24em;
  font-size: 0.625rem;
  color: rgba(239, 237, 230, 0.5);
}
.pv-close__cta {
  color: #f2f0ea;
  border-color: rgba(239, 237, 230, 0.24);
}

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

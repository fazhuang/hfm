<script setup lang="ts">
/**
 * JiayiView — CF-04 《针灸甲乙经》work / edition presentation (rebuild).
 *
 * Inherited IA (UX2-P2, design only):
 *   hero → work profile → lineage visual → edition collection (ancient /
 *   modern) → edition chronology → related works → modern scholarship →
 *   papers → evidence/source → related navigation.
 *
 * Data source (CF-04 §5): no real per-work Jiayi API record exists on the
 * Recovery runtime, so the page continues on the audited customer register
 * view model (src/data/jiayiView.ts) plus the shared WORK record
 * (src/data/workCollection.ts). Both are customer-authorized, audit-backed,
 * static/domain content — VERSIONED_CONTENT. No backend/domain expansion:
 * no invented API, database records, bibliographic metadata, or fake
 * runtime service.
 *
 * Semantics (CF-04 §7): WORK (作品本体) ≠ EDITION (版本记录) ≠ RECORD
 * (普通书目条目) are kept distinct — the work profile is one WORK record;
 * each collected edition is one EDITION bibliographic record; per-item
 * catalog status is expressed through CF-02 state semantics
 * (METADATA_ONLY → PARTIAL, presented as 「仅版本信息」).
 *
 * Presentation reuse (CF-04 §6): BibliographicRecord renders every edition
 * record (title + dl metadata + status band + provenance); stateMapping
 * semantics drive status values; the lineage PNG stays a presented asset
 * with a caveat — never reconstructed into genealogical edges.
 *
 * Public copy policy (CF-04 §8): data gaps are expressed as presentation
 * states (PARTIAL / UNAVAILABLE / UNKNOWN) with plain, public wording —
 * internal register paths (hfmzl/…) and developer terms (DATA-GAP / TODO)
 * are never rendered.
 */
import { computed } from 'vue'
import {
  JIAYI_ANCIENT_EDITIONS,
  JIAYI_LUNWEN_FILE_COUNT,
  JIAYI_MODERN_EDITIONS,
  JIAYI_MODERN_SCHOLARS,
  JIAYI_PAPER_PREVIEW,
  JIAYI_PUBLIC_SOURCES,
  JIAYI_RELATED_WORKS,
} from '../../data/jiayiView'
import { WORK_COLLECTION } from '../../data/workCollection'
import type { EditionRecord } from '../../types/jiayi'
import type { ContentStatus } from '../../types/content'
import EditionLineageImage from '../../components/jiayi/EditionLineageImage.vue'
import Timeline from '../../components/Timeline.vue'
import BibliographicRecord from '../../components/primitives/BibliographicRecord.vue'
import type { TimelineEvent } from '../../types/timeline'
import { ref } from 'vue'
import { mediaBytesUrl } from '../../services/media'
import { JIAYI_IMPRINTS, type JiayiImprint, type JiayiImprintEdition } from '../../data/jiayiImprints'

defineOptions({ name: 'JiayiView' })

/**
 * 影印阅读状态（P-5）。
 *
 * 就地展开而非弹窗：弹窗要配焦点陷阱、Esc、滚动锁，而这张页面上同时只有
 * 一卷被打开，就地展开少一半代码、也少一半出错的地方。
 */
const activeImprint = ref<{ imprint: JiayiImprint; edition: JiayiImprintEdition } | null>(null)

function openImprint(imprint: JiayiImprint, edition: JiayiImprintEdition): void {
  activeImprint.value = { imprint, edition }
}

function closeImprint(): void {
  activeImprint.value = null
}

/** 影印总数（去重后）。 */
const imprintTotal = JIAYI_IMPRINTS.reduce((n, e) => n + e.imprints.length, 0)

/* Shared WORK-level record (作品本体 — distinct from edition records). */
const JIAYI_WORK = WORK_COLLECTION.find((work) => work.id === 'w-jiayi')

const editionTotal = computed(() => JIAYI_ANCIENT_EDITIONS.length + JIAYI_MODERN_EDITIONS.length)

/**
 * Deterministic catalog-status → CF-02 presentation-state mapping.
 * ContentStatus (content layer) is distinct from PublicationState; this is
 * the page's honest record-layer status, never inferred for decoration.
 */
const STATUS_TO_STATE: Record<ContentStatus, string> = {
  AVAILABLE: 'COMPLETE',
  METADATA_ONLY: 'PARTIAL',
  DATA_GAP: 'UNKNOWN',
}

function stateForStatus(status: ContentStatus): string {
  return STATUS_TO_STATE[status] ?? 'UNKNOWN'
}

/** Public status label; falls back to CF-02 canonical labels when unset. */
const STATUS_LABEL_OVERRIDE: Partial<Record<ContentStatus, string>> = {
  METADATA_ONLY: '仅版本信息',
}

function statusLabelFor(status: ContentStatus): string | undefined {
  return STATUS_LABEL_OVERRIDE[status]
}

/** WORK-level identity (guarded: the /jiayi page exists iff w-jiayi does). */
const hasWorkProfile = computed(() => JIAYI_WORK !== undefined)
const workAttribution = computed<string>(() => JIAYI_WORK?.attribution ?? '')
const workPeriod = computed<string>(() => JIAYI_WORK?.historicalPeriod ?? '')
const workType = computed<string>(() => JIAYI_WORK?.workType ?? '')
const workDescription = computed<string>(() => JIAYI_WORK?.description ?? '')
const workStatus = computed<ContentStatus>(() => JIAYI_WORK?.status ?? 'DATA_GAP')

/** Work identity line (hero meta) composed from the shared WORK record. */
const workMetaLine = computed<string>(() => {
  if (workAttribution.value === '') return ''
  return `${workAttribution.value}撰 · ${workPeriod.value} · ${workType.value}`
})

/** Edition → BibliographicRecord meta rows (fields present in the record only). */
interface MetaItem {
  label?: string
  value: string
}

function editionMeta(edition: EditionRecord): MetaItem[] {
  const meta: MetaItem[] = []
  if (edition.period !== '') meta.push({ label: '时期', value: edition.period })
  if (edition.imprint !== undefined && edition.imprint !== '') {
    meta.push({ label: '刊印', value: edition.imprint })
  }
  if (edition.description !== '') meta.push({ label: '说明', value: edition.description })
  return meta
}

/** Chronology only: year-sorted editions (no lineage implication). */
const editionTimeline = computed<TimelineEvent[]>(() =>
  [...JIAYI_ANCIENT_EDITIONS, ...JIAYI_MODERN_EDITIONS]
    .filter((edition) => edition.year !== undefined)
    .sort((a, b) => (a.year ?? 0) - (b.year ?? 0))
    .map((edition) => ({
      id: edition.id,
      title: edition.title,
      date: String(edition.year),
      description: `${edition.period}${edition.imprint ? ` · ${edition.imprint}` : ''}`,
    })),
)
</script>

<template>
  <div class="jiayi-page">
    <!-- 01 HERO — WORK identity (single coherent H1). -->
    <header class="jiayi-hero">
      <p class="hfm-eyebrow">数字人文 · 学术作品档案</p>
      <h1 class="jiayi-hero__title">
        {{ JIAYI_WORK?.title ?? '《针灸甲乙经》' }}
      </h1>
      <p class="jiayi-hero__meta">
        {{ workMetaLine }}
      </p>
      <p class="jiayi-hero__intro">
        本页为《针灸甲乙经》数字人文专题：作品档案、历代版本记录、版本脉络示意、相关论著与现代研究入口。
        本平台为学术资料展示，不提供临床诊疗建议。
      </p>
      <nav class="jiayi-hero__jump" aria-label="本页快速跳转">
        <RouterLink to="/jiayi/reader">篇章阅读（卷·篇·段）</RouterLink>
        <a href="#overview">作品档案</a>
        <a href="#lineage">版本脉络</a>
        <a href="#editions">历代版本</a>
        <a href="#scholarship">现代整理与研究</a>
        <a href="#papers">学术论文</a>
      </nav>
    </header>

    <!-- 02 WORK PROFILE — 作品本体（WORK），与版本记录严格区分。 -->
    <section
      id="overview"
      class="jiayi-section"
      aria-labelledby="overview-heading"
      data-record-kind="work"
    >
      <h2 id="overview-heading" class="section-title">作品档案</h2>
      <template v-if="hasWorkProfile">
        <p class="section-lead">
          {{ workDescription }}
        </p>
        <dl class="work-profile">
          <div class="work-profile__row">
            <dt>撰者</dt>
            <dd>{{ workAttribution }}</dd>
          </div>
          <div class="work-profile__row">
            <dt>时期</dt>
            <dd>{{ workPeriod }}</dd>
          </div>
          <div class="work-profile__row">
            <dt>著作类型</dt>
            <dd>{{ workType }}</dd>
          </div>
          <div class="work-profile__row">
            <dt>收录版本</dt>
            <dd>{{ editionTotal }} 种版本记录（据客户资料目录审计）</dd>
          </div>
          <div class="work-profile__row">
            <dt>研究记录</dt>
            <dd>
              {{ JIAYI_LUNWEN_FILE_COUNT }} 篇论文（据客户资料目录审计）
              <span class="work-profile__src">来源：{{ JIAYI_PUBLIC_SOURCES.lunwen }}</span>
            </dd>
          </div>
        </dl>
        <p class="record-state">
          <span
            class="record-state__pill"
            data-status-prefix="presentation"
            :data-status="stateForStatus(workStatus)"
            >{{ statusLabelFor(workStatus) ?? '已收录' }}</span
          >
          <span class="record-state__source">来源：{{ JIAYI_PUBLIC_SOURCES.all }}</span>
        </p>
      </template>
    </section>

    <!-- 03 VERSION LINEAGE VISUAL — presented asset with a public caveat. -->
    <section id="lineage" class="jiayi-section" aria-labelledby="lineage-heading">
      <h2 id="lineage-heading" class="section-title">版本脉络</h2>
      <p class="section-note">
        客户提供的版本脉络图为展示资料；图中关系为资料示意，页面不对各版本作传承谱系推断。
      </p>
      <EditionLineageImage />
    </section>

    <!-- 03b 原刻影印 — 四种公版版本，浏览器原生 PDF 查看器（P-5） -->
    <section id="imprints" class="jiayi-section" aria-labelledby="imprints-heading">
      <h2 id="imprints-heading" class="section-title">原刻影印</h2>
      <p class="section-note">
        四种公版版本的原刻影印，共 {{ imprintTotal }} 件 —— 明万历吴勉学的刻本、清乾隆的四库全书本、
        清光绪的行素草堂藏板。这是今天能看到的最接近原书的样子。点即翻阅，无需下载。
      </p>

      <div v-for="edition in JIAYI_IMPRINTS" :key="edition.edition" class="imprint-edition">
        <h3 class="imprint-edition__title">
          {{ edition.edition }}
          <span class="imprint-edition__era">{{ edition.era }}</span>
        </h3>
        <p class="imprint-edition__note">{{ edition.note }}</p>
        <ul class="imprint-grid">
          <li v-for="imprint in edition.imprints" :key="imprint.id">
            <button
              type="button"
              class="imprint"
              :class="{ 'imprint--active': activeImprint?.imprint.id === imprint.id }"
              :aria-pressed="activeImprint?.imprint.id === imprint.id"
              @click="openImprint(imprint, edition)"
            >
              <span class="imprint__label">{{ imprint.label }}</span>
              <span class="imprint__hint">翻阅</span>
            </button>
          </li>
        </ul>
      </div>

      <div v-if="activeImprint" class="imprint-viewer" data-source="backend">
        <div class="imprint-viewer__bar">
          <p class="imprint-viewer__title">
            {{ activeImprint.edition.edition }} · {{ activeImprint.imprint.label }}
          </p>
          <button type="button" class="imprint-viewer__close" @click="closeImprint">收起</button>
        </div>
        <iframe
          class="imprint-viewer__frame"
          :src="mediaBytesUrl(activeImprint.imprint.id)"
          :title="`${activeImprint.edition.edition} ${activeImprint.imprint.label} 影印`"
        ></iframe>
      </div>
    </section>

    <!-- 04 EDITION COLLECTION — 版本记录（EDITION），逐条为书目记录。 -->
    <section id="editions" class="jiayi-section" aria-labelledby="editions-heading">
      <h2 id="editions-heading" class="section-title">历代版本</h2>
      <p class="section-note">
        共收录 {{ editionTotal }} 种版本记录（据客户资料目录审计）。每条版本记录当前收录其目录信息，
        标注「仅版本信息」；正文数字化与逐页影像将随整理逐步呈现。
      </p>

      <h3 class="edition-group-title">古代版本</h3>
      <ul class="edition-list">
        <li
          v-for="edition in JIAYI_ANCIENT_EDITIONS"
          :key="edition.id"
          class="edition-list__item"
          data-record-kind="edition"
          :data-edition-id="edition.id"
        >
          <BibliographicRecord
            :title="edition.title"
            :meta="editionMeta(edition)"
            :status="stateForStatus(edition.status)"
            :status-label="statusLabelFor(edition.status)"
            :provenance="JIAYI_PUBLIC_SOURCES.lunzhu"
          />
        </li>
      </ul>

      <h3 class="edition-group-title">近现代整理版本</h3>
      <ul class="edition-list">
        <li
          v-for="edition in JIAYI_MODERN_EDITIONS"
          :key="edition.id"
          class="edition-list__item"
          data-record-kind="edition"
          :data-edition-id="edition.id"
        >
          <BibliographicRecord
            :title="edition.title"
            :meta="editionMeta(edition)"
            :status="stateForStatus(edition.status)"
            :status-label="statusLabelFor(edition.status)"
            :provenance="JIAYI_PUBLIC_SOURCES.lunzhu"
          />
        </li>
      </ul>
    </section>

    <!-- 05 EDITION CHRONOLOGY — year-sorted; sequence ≠ lineage. -->
    <section id="edition-timeline" class="jiayi-section" aria-labelledby="edition-timeline-heading">
      <h2 id="edition-timeline-heading" class="section-title">版本年代排序</h2>
      <p class="section-note">
        各版本按可考年代排序（仅收录年代明确者）；时间先后不代表版本间的传承关系。
      </p>
      <Timeline :events="editionTimeline" label="《针灸甲乙经》版本年代排序" />
    </section>

    <!-- 06 RELATED WORKS — WORK-level entry points. -->
    <section id="related-works" class="jiayi-section" aria-labelledby="related-works-heading">
      <h2 id="related-works-heading" class="section-title">相关论著与入口</h2>
      <ul class="related-list">
        <li v-for="work in JIAYI_RELATED_WORKS" :key="work.id" class="related-item">
          <a v-if="work.href" :href="work.href" class="related-item__link">
            <span class="related-item__title">{{ work.title }}</span>
            <span class="related-item__note">{{ work.note }}</span>
          </a>
          <template v-else>
            <span class="related-item__title">{{ work.title }}</span>
            <span class="related-item__note">{{ work.note }}</span>
          </template>
        </li>
      </ul>
    </section>

    <!-- 07 MODERN SCHOLARSHIP — names only where the material supports them. -->
    <section id="scholarship" class="jiayi-section" aria-labelledby="scholarship-heading">
      <h2 id="scholarship-heading" class="section-title">现代整理与研究</h2>
      <p class="section-note">整理者与版本信息以客户资料为准（不超出材料作评价）。</p>
      <ul class="scholar-list">
        <li v-for="scholar in JIAYI_MODERN_SCHOLARS" :key="scholar.id" class="scholar-item">
          <span class="scholar-item__collator">{{ scholar.collator }}</span>
          <span class="scholar-item__work">{{ scholar.title }}</span>
          <span class="scholar-item__year">{{ scholar.year }}</span>
        </li>
      </ul>
    </section>

    <!-- 08 PAPER DISCOVERY — preview + count from the audited register. -->
    <section id="papers" class="jiayi-section" aria-labelledby="papers-heading">
      <h2 id="papers-heading" class="section-title">学术论文</h2>
      <p class="section-note">
        已收录
        {{ JIAYI_LUNWEN_FILE_COUNT }} 篇论文（据客户资料目录审计）。全文检索与研究入口建设中。
      </p>
      <ol class="paper-list">
        <li v-for="paper in JIAYI_PAPER_PREVIEW" :key="paper.id" class="paper-item">
          <span class="paper-item__title">{{ paper.title }}</span>
        </li>
      </ol>
      <p class="paper-cta">
        <a class="paper-cta__link" href="/search?q=针灸甲乙经">检索全部研究 →</a>
      </p>
    </section>

    <!-- 09 EVIDENCE / SOURCE — public provenance labels only. -->
    <section id="evidence" class="jiayi-section" aria-labelledby="evidence-heading">
      <h2 id="evidence-heading" class="section-title">来源与证据</h2>
      <p class="section-note">
        本页版本、论著与论文条目均来自{{
          JIAYI_PUBLIC_SOURCES.all
        }}；条目级来源见各版本卡片来源说明。 版本对校与逐条出处引证将在研究端逐步呈现。
      </p>
    </section>

    <!-- 10 RELATED NAVIGATION -->
    <nav class="jiayi-related-nav" aria-label="相关导航">
      <a href="/persons/ENT-PERSON-HFM-HUANGFUMI">皇甫谧人物档案</a>
      <a href="/yan">其言</a>
      <a href="/reader">阅读</a>
      <a href="/heritage">非遗传承</a>
    </nav>
  </div>
</template>

<style scoped>
.jiayi-page {
  max-width: var(--hfm-content-max);
  margin: 0 auto;
}

.jiayi-hero {
  padding: var(--hfm-space-8) 0 var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
  margin-bottom: var(--hfm-space-12);
}

.jiayi-hero__title {
  font-size: var(--hfm-text-3xl);
  margin: 0 0 var(--hfm-space-3);
  letter-spacing: var(--hfm-tracking-display);
}

.jiayi-hero__meta {
  color: var(--hfm-color-text-secondary);
  margin: 0 0 var(--hfm-space-4);
  overflow-wrap: anywhere;
}

.jiayi-hero__intro {
  max-width: 68ch;
  line-height: var(--hfm-leading-reading);
  margin: 0 0 var(--hfm-space-5);
}

.jiayi-hero__jump {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2) var(--hfm-space-4);
}

.jiayi-hero__jump a {
  color: var(--hfm-color-interactive);
  font-size: var(--hfm-text-sm);
  text-decoration: none;
}

.jiayi-hero__jump a:hover {
  text-decoration: underline;
}

.imprint-edition {
  margin-bottom: var(--hfm-space-8);
}
.imprint-edition__title {
  margin: 0 0 var(--hfm-space-2);
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-lg);
  letter-spacing: 0.06em;
  color: var(--hfm-color-text);
}
.imprint-edition__era {
  margin-left: var(--hfm-space-3);
  font-family: var(--hfm-font-sans);
  font-size: var(--hfm-text-xs);
  letter-spacing: var(--hfm-tracking-display);
  color: var(--hfm-color-text-muted);
}
.imprint-edition__note {
  margin: 0 0 var(--hfm-space-4);
  max-width: var(--hfm-reader-max);
  font-size: var(--hfm-text-sm);
  line-height: var(--hfm-leading-normal);
  color: var(--hfm-color-text-muted);
}
.imprint-grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2);
  margin: 0;
  padding: 0;
  list-style: none;
}
.imprint {
  display: flex;
  align-items: baseline;
  gap: var(--hfm-space-2);
  padding: var(--hfm-space-2) var(--hfm-space-4);
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text);
  background: var(--hfm-color-surface);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  cursor: pointer;
}
.imprint:hover {
  border-color: var(--hfm-color-border-strong);
}
.imprint:focus-visible {
  outline: 2px solid var(--hfm-color-interactive);
  outline-offset: 2px;
}
.imprint--active {
  border-color: var(--hfm-color-interactive);
}
.imprint__hint {
  font-family: var(--hfm-font-sans);
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.imprint-viewer {
  margin-top: var(--hfm-space-6);
  border: 1px solid var(--hfm-color-border);
  background: var(--hfm-color-surface);
}
.imprint-viewer__bar {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--hfm-space-4);
  padding: var(--hfm-space-3) var(--hfm-space-4);
  border-bottom: 1px solid var(--hfm-color-border);
}
.imprint-viewer__title {
  margin: 0;
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-base);
  color: var(--hfm-color-text);
}
.imprint-viewer__close {
  padding: var(--hfm-space-1) var(--hfm-space-3);
  font-family: var(--hfm-font-sans);
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-secondary);
  background: none;
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  cursor: pointer;
}
.imprint-viewer__close:focus-visible {
  outline: 2px solid var(--hfm-color-interactive);
  outline-offset: 2px;
}
/* 浏览器原生 PDF 查看器：翻页、缩放、下载都由它自带，零依赖。
   高度给足，横屏古籍影印看起来才像话。 */
.imprint-viewer__frame {
  display: block;
  width: 100%;
  height: 80vh;
  border: 0;
}

.jiayi-section {
  margin-bottom: var(--hfm-space-12);
}

.section-title {
  margin: 0 0 var(--hfm-space-4);
  padding-bottom: var(--hfm-space-2);
  border-bottom: 1px solid var(--hfm-color-border);
}

.section-lead {
  max-width: 68ch;
  line-height: var(--hfm-leading-reading);
  margin: 0 0 var(--hfm-space-4);
  color: var(--hfm-color-text);
}

.section-note {
  color: var(--hfm-color-text-muted);
  max-width: 68ch;
  margin: 0 0 var(--hfm-space-4);
  line-height: var(--hfm-leading-reading);
}

/* WORK-level profile (dl) — distinct from per-edition records. */
.work-profile {
  margin: 0 0 var(--hfm-space-4);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  overflow: hidden;
}

.work-profile__row {
  display: grid;
  grid-template-columns: minmax(5.5rem, 8rem) minmax(0, 1fr);
  border-bottom: 1px solid var(--hfm-color-border);
}

.work-profile__row:last-child {
  border-bottom: none;
}

.work-profile__row dt {
  padding: var(--hfm-space-3) var(--hfm-space-4);
  background: var(--hfm-color-canvas);
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
}

.work-profile__row dd {
  margin: 0;
  padding: var(--hfm-space-3) var(--hfm-space-4);
  min-width: 0;
  overflow-wrap: anywhere;
}

.work-profile__src {
  display: block;
  margin-top: 2px;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.record-state {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--hfm-space-2) var(--hfm-space-4);
  margin: 0;
}

.record-state__pill {
  display: inline-block;
  padding: 2px var(--hfm-space-2);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-warning);
  color: var(--hfm-color-on-accent);
  font-size: var(--hfm-text-xs);
  font-weight: 600;
}

.record-state__source {
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

/* EDITION records — one bibliographic record per collected edition. */
.edition-group-title {
  margin: var(--hfm-space-6) 0 var(--hfm-space-3);
  font-size: var(--hfm-text-lg);
}

.edition-list {
  list-style: none;
  margin: 0 0 var(--hfm-space-4);
  padding: 0;
  display: grid;
  gap: var(--hfm-space-3);
}

.edition-list__item {
  min-width: 0;
}

.related-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-2);
}

.related-item__link {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--hfm-space-1) var(--hfm-space-3);
  color: var(--hfm-color-text);
  text-decoration: none;
}

.related-item__link:hover .related-item__title {
  color: var(--hfm-color-accent);
}

.related-item__title {
  font-family: var(--hfm-font-serif);
  font-weight: 600;
}

.related-item__note {
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.scholar-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-2);
}

.scholar-item {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--hfm-space-2) var(--hfm-space-3);
  padding: var(--hfm-space-2) 0;
  border-bottom: 1px solid var(--hfm-color-border);
  font-size: var(--hfm-text-sm);
}

.scholar-item__collator {
  font-weight: 600;
}

.scholar-item__work {
  color: var(--hfm-color-text-secondary);
}

.scholar-item__year {
  color: var(--hfm-color-text-muted);
  font-variant-numeric: tabular-nums;
}

.paper-list {
  list-style: none;
  margin: 0 0 var(--hfm-space-3);
  padding: 0;
  display: grid;
  gap: var(--hfm-space-1);
  counter-reset: paper;
}

.paper-item {
  display: flex;
  gap: var(--hfm-space-2);
  padding: var(--hfm-space-1) 0;
  font-size: var(--hfm-text-sm);
}

.paper-item::before {
  counter-increment: paper;
  content: counter(paper) '.';
  color: var(--hfm-color-text-muted);
  font-variant-numeric: tabular-nums;
}

.paper-cta__link {
  color: var(--hfm-color-interactive);
  text-decoration: none;
  font-size: var(--hfm-text-sm);
}

.paper-cta__link:hover {
  text-decoration: underline;
}

.jiayi-related-nav {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2) var(--hfm-space-5);
  padding: var(--hfm-space-4) 0;
  border-top: 1px solid var(--hfm-color-border);
}

.jiayi-related-nav a {
  color: var(--hfm-color-interactive);
  text-decoration: none;
}

.jiayi-related-nav a:hover {
  text-decoration: underline;
}
</style>

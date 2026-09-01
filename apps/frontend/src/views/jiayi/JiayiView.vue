<script setup lang="ts">
/**
 * JiayiView — FLAGSHIP-02 《针灸甲乙经》核心学术界面 (UI-08).
 *
 * DIGITAL SCHOLARLY WORK PROFILE:
 *   HERO → WORK OVERVIEW → VERSION LINEAGE VISUAL → EDITION COLLECTION →
 *   EDITION TIMELINE（chronology，非 lineage）→ RELATED WORKS →
 *   MODERN SCHOLARSHIP → PAPER DISCOVERY → EVIDENCE → RELATED NAVIGATION.
 *
 * Data policy: everything rendered comes from the audited customer register
 * (src/data/jiayiView.ts). Chronology is sorted by year; NO genealogical
 * edges are fabricated (JIAYI_EDITION_RELATIONS remains DATA-GAP). No
 * clinical expression.
 */
import { computed } from 'vue'
import {
  JIAYI_ANCIENT_EDITIONS,
  JIAYI_LUNWEN_FILE_COUNT,
  JIAYI_LUNZHU_FILE_COUNT,
  JIAYI_MODERN_EDITIONS,
  JIAYI_MODERN_SCHOLARS,
  JIAYI_PAPER_PREVIEW,
  JIAYI_PUBLIC_SOURCES,
  JIAYI_RELATED_WORKS,
} from '../../data/jiayiView'
import type { EditionRecord } from '../../types/jiayi'
import { presentationLabel, resolvePresentationState } from '../../presentation/stateMapping'
import type { TimelineEvent } from '../../types/timeline'
import BibliographicRecord from '../../components/primitives/BibliographicRecord.vue'
import EditionLineageImage from '../../components/jiayi/EditionLineageImage.vue'
import Timeline from '../../components/Timeline.vue'

defineOptions({ name: 'JiayiView' })

const editionCount = computed(() => JIAYI_ANCIENT_EDITIONS.length + JIAYI_MODERN_EDITIONS.length)

/* ---- UX2-P2: edition → BibliographicRecord props via the G1-C state mapping ----
 * Every edition is METADATA_ONLY (存目) per the U-05 disposition (no digitized
 * resource flag exists; no fake 阅读 CTA). The source label is the public
 * source projection (JIAYI_PUBLIC_SOURCES.lunzhu) — internal register paths
 * are never rendered. No genealogy edges are introduced (NB-03). */
function toRecordProps(edition: EditionRecord) {
  const state = resolvePresentationState({ contentStatus: edition.status, hasMetadata: true })
  return {
    title: edition.title,
    year: edition.period,
    edition: edition.imprint,
    kind: edition.editionType === 'ancient' ? '古代版本' : '近现代整理',
    source: JIAYI_PUBLIC_SOURCES.lunzhu,
    status: state,
    statusLabel: presentationLabel(state, { excerpt: true }),
    description: edition.description,
  }
}

/** Chronology only: year-sorted editions (no lineage implication). */
const editionTimeline = computed<TimelineEvent[]>(() =>
  [...JIAYI_ANCIENT_EDITIONS, ...JIAYI_MODERN_EDITIONS]
    .filter((e) => e.year !== undefined)
    .sort((a, b) => (a.year ?? 0) - (b.year ?? 0))
    .map((e) => ({
      id: e.id,
      title: e.title,
      date: String(e.year),
      description: `${e.period}${e.imprint ? ` · ${e.imprint}` : ''}`,
    })),
)
</script>

<template>
  <section class="jiayi" aria-labelledby="jiayi-heading">
    <!-- 01 HERO -->
    <header class="jiayi-hero">
      <p class="hfm-eyebrow">数字人文 · 学术作品档案</p>
      <h1 id="jiayi-heading" class="jiayi-hero__title">《针灸甲乙经》</h1>
      <p class="jiayi-hero__meta">皇甫谧撰 · 西晋 · 针灸学专著 · 中国现存最早的针灸学典籍之一</p>
      <p class="jiayi-hero__intro">
        本页为《针灸甲乙经》数字人文专题：作品档案、历代版本、版本脉络、相关论著、现代整理研究与学术论文。
        本平台为学术资料展示，不提供临床诊疗建议。
      </p>
      <nav class="jiayi-hero__jump" aria-label="本页快速跳转">
        <a href="#overview">作品档案</a>
        <a href="#lineage">版本脉络</a>
        <a href="#editions">历代版本</a>
        <a href="#scholarship">现代整理与研究</a>
        <a href="#papers">学术论文</a>
      </nav>
    </header>

    <!-- 02 WORK OVERVIEW -->
    <section id="overview" class="jiayi-section" aria-labelledby="overview-heading">
      <h2 id="overview-heading" class="section-title">作品档案</h2>
      <dl class="work-profile">
        <div class="work-profile__row">
          <dt>书名</dt>
          <dd>《针灸甲乙经》（又称《黄帝三部针灸甲乙经》）</dd>
        </div>
        <div class="work-profile__row">
          <dt>撰者</dt>
          <dd>皇甫谧（西晋）</dd>
        </div>
        <div class="work-profile__row">
          <dt>时期</dt>
          <dd>西晋</dd>
        </div>
        <div class="work-profile__row">
          <dt>著作类型</dt>
          <dd>针灸学专著（文献整理编纂）</dd>
        </div>
        <div class="work-profile__row">
          <dt>平台收录版本</dt>
          <dd>
            {{ editionCount }} 种版本记录（据客户资料目录审计）
            <span class="work-profile__src">来源：{{ JIAYI_LUNZHU_FILE_COUNT }} 件论著文件</span>
          </dd>
        </div>
        <div class="work-profile__row">
          <dt>研究记录</dt>
          <dd>
            {{ JIAYI_LUNWEN_FILE_COUNT }} 篇论文（据客户资料目录审计）
            <span class="work-profile__src">来源：{{ JIAYI_PUBLIC_SOURCES.lunwen }}</span>
          </dd>
        </div>
      </dl>
    </section>

    <!-- 03 VERSION LINEAGE VISUAL -->
    <section id="lineage" class="jiayi-section" aria-labelledby="lineage-heading">
      <h2 id="lineage-heading" class="section-title">版本脉络</h2>
      <p class="section-note">
        客户提供的版本脉络图（正式展示资产）。图中关系为资料示意；结构化版本关系未建模（DATA-GAP），
        不据此推断未经证据确认的版本继承关系。
      </p>
      <p class="lineage-state">
        <span class="hfm-status" data-status="UNSTRUCTURED_OR_INCOMPLETE">版本关系整理中</span>
      </p>
      <EditionLineageImage />
    </section>

    <!-- 04 EDITION COLLECTION -->
    <section id="editions" class="jiayi-section" aria-labelledby="editions-heading">
      <h2 id="editions-heading" class="section-title">历代版本</h2>

      <h3 class="edition-group-title">古代版本</h3>
      <ul class="edition-collection">
        <li v-for="edition in JIAYI_ANCIENT_EDITIONS" :key="edition.id" class="edition-card">
          <BibliographicRecord v-bind="toRecordProps(edition)" />
        </li>
      </ul>

      <h3 class="edition-group-title">近现代整理版本</h3>
      <ul class="edition-collection">
        <li v-for="edition in JIAYI_MODERN_EDITIONS" :key="edition.id" class="edition-card">
          <BibliographicRecord v-bind="toRecordProps(edition)" />
        </li>
      </ul>
    </section>

    <!-- 05 EDITION TIMELINE (chronology only) -->
    <section id="edition-timeline" class="jiayi-section" aria-labelledby="edition-timeline-heading">
      <h2 id="edition-timeline-heading" class="section-title">版本年代排序</h2>
      <p class="section-note">
        按年代排序（chronology），仅收录年代明确者；时间排序不表示版本继承关系（chronology ≠
        lineage）。
      </p>
      <Timeline :events="editionTimeline" label="《针灸甲乙经》版本年代排序" />
    </section>

    <!-- 06 RELATED WORKS -->
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

    <!-- 07 MODERN SCHOLARSHIP -->
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

    <!-- 08 PAPER DISCOVERY -->
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

    <!-- 09 EVIDENCE / CITATION -->
    <section id="evidence" class="jiayi-section" aria-labelledby="evidence-heading">
      <h2 id="evidence-heading" class="section-title">来源与证据</h2>
      <p class="evidence-note">
        本页版本、论著与论文条目均来自{{ JIAYI_PUBLIC_SOURCES.all }}， 逐条来源见各卡片说明。详细
        Evidence / Citation（版本对校、出处引证）将在研究端与内容准入后逐步呈现。
      </p>
    </section>

    <!-- 10 RELATED NAVIGATION -->
    <nav class="jiayi-related-nav" aria-label="相关导航">
      <a href="/persons/person-huangfu-mi">皇甫谧人物档案</a>
      <a href="/yan">其言</a>
      <a href="/reader">阅读</a>
      <a href="/heritage">非遗传承</a>
    </nav>
  </section>
</template>

<style scoped>
.jiayi {
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

.jiayi-section {
  margin-bottom: var(--hfm-space-12);
}

.section-title {
  margin: 0 0 var(--hfm-space-4);
  padding-bottom: var(--hfm-space-2);
  border-bottom: 1px solid var(--hfm-color-border);
}

.section-note {
  color: var(--hfm-color-text-muted);
  max-width: 68ch;
  margin: 0 0 var(--hfm-space-4);
}

.work-profile {
  margin: 0;
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  overflow: hidden;
}

.work-profile__row {
  display: grid;
  grid-template-columns: 8rem 1fr;
  gap: var(--hfm-space-4);
  padding: var(--hfm-space-3) var(--hfm-space-4);
  border-bottom: 1px solid var(--hfm-color-border);
}

.work-profile__row:last-child {
  border-bottom: none;
}

.work-profile__row dt {
  color: var(--hfm-color-text-muted);
  font-weight: 600;
}

.work-profile__row dd {
  margin: 0;
  line-height: var(--hfm-leading-normal);
}

.work-profile__src {
  display: block;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.edition-group-title {
  font-size: var(--hfm-text-lg);
  margin: var(--hfm-space-6) 0 var(--hfm-space-3);
  color: var(--hfm-color-text);
}

.edition-collection {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-3);
}

.edition-card {
  /* plain list wrapper — BibliographicRecord owns the record presentation */
  list-style: none;
  margin: 0;
  padding: var(--hfm-space-2) 0;
  border-bottom: 1px solid var(--hfm-color-border);
}

.edition-card:last-child {
  border-bottom: none;
}

/* UX2-P2: DATA-GAP state (版本关系整理中) above the lineage visual */
.lineage-state {
  margin: 0 0 var(--hfm-space-3);
}

.related-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-2);
}

.related-item {
  display: flex;
  justify-content: space-between;
  gap: var(--hfm-space-3);
  padding: var(--hfm-space-3) var(--hfm-space-4);
  border-bottom: 1px solid var(--hfm-color-border);
}

.related-item__link {
  display: flex;
  justify-content: space-between;
  gap: var(--hfm-space-3);
  width: 100%;
  text-decoration: none;
  color: var(--hfm-color-text);
}

.related-item__link:hover .related-item__title {
  color: var(--hfm-color-accent);
}

.related-item__title {
  font-weight: 600;
}

.related-item__note {
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
  white-space: nowrap;
}

.scholar-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-2);
}

.scholar-item {
  display: grid;
  grid-template-columns: 7rem 1fr auto;
  gap: var(--hfm-space-3);
  align-items: baseline;
  padding: var(--hfm-space-3) var(--hfm-space-4);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
}

.scholar-item__collator {
  font-weight: 600;
  color: var(--hfm-color-accent);
}

.scholar-item__work {
  color: var(--hfm-color-text);
}

.scholar-item__year {
  color: var(--hfm-color-text-muted);
  font-variant-numeric: tabular-nums;
  font-size: var(--hfm-text-sm);
}

.paper-list {
  list-style: none;
  margin: 0 0 var(--hfm-space-4);
  padding: 0;
  display: grid;
  gap: var(--hfm-space-1);
}

.paper-item {
  padding: var(--hfm-space-2) var(--hfm-space-4);
  border-bottom: 1px solid var(--hfm-color-border);
  display: flex;
  align-items: baseline;
  gap: var(--hfm-space-3);
}

.paper-item::before {
  content: '';
  width: 0.375rem;
  height: 0.375rem;
  border-radius: 50%;
  background: var(--hfm-color-accent);
  flex-shrink: 0;
}

.paper-item__title {
  line-height: var(--hfm-leading-normal);
}

.paper-cta__link {
  color: var(--hfm-color-interactive);
  font-weight: 600;
  text-decoration: none;
}

.paper-cta__link:hover {
  text-decoration: underline;
}

.evidence-note {
  color: var(--hfm-color-text-secondary);
  max-width: 68ch;
  line-height: var(--hfm-leading-reading);
}

.evidence-note code {
  font-family: var(--hfm-font-sans);
  font-size: var(--hfm-text-sm);
  background: var(--hfm-color-canvas);
  padding: 0 var(--hfm-space-1);
  border-radius: var(--hfm-radius-sm);
}

.jiayi-related-nav {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-4);
  margin-top: var(--hfm-space-8);
  padding-top: var(--hfm-space-4);
  border-top: 1px solid var(--hfm-color-border);
}

.jiayi-related-nav a {
  color: var(--hfm-color-interactive);
  text-decoration: none;
  font-size: var(--hfm-text-sm);
}

.jiayi-related-nav a:hover {
  text-decoration: underline;
}

@media (max-width: 767px) {
  .work-profile__row {
    grid-template-columns: 1fr;
    gap: var(--hfm-space-1);
  }

  .scholar-item {
    grid-template-columns: 1fr;
    gap: var(--hfm-space-1);
  }

  .related-item {
    flex-direction: column;
    gap: var(--hfm-space-1);
  }

  .related-item__note {
    white-space: normal;
  }
}
</style>

<script setup lang="ts">
/**
 * YanView — 其言 (UI-06) Digital Quotation / Text Collection.
 *
 * 皇甫谧言论与文本选编（据客户正式材料其言.docx）。内容忠实取自客户文稿：
 * 集引言 + 四篇说明（《三都赋》序 / 玄守论 / 释劝论 / 笃终论）+ 辑佚补充。
 * 四篇全文未见于客户文稿；P-8a（2026-09-15）依公版文献录入，见 data/yanTexts.ts。
 * 页面呈现正文 + 底本/参校出处 + 校勘记；校记中的异文一律照录，不擅自择善。
 * 正文以 data-source="static" 标明为编辑录入的静态内容，非后台准入投影 ——
 * 即：它已可读，但尚未经内容准入管线。这两件事必须分开说，不得含糊。
 * 主题标签为展示分类（PRESENTATION_CLASSIFICATION），非史料原始分类。
 */
import { YAN_COLLECTION } from '../../data/yanCollection'
import { YAN_FULL_TEXTS } from '../../data/yanTexts'
import { segmentForGlosses, type YanRun } from '../../data/yanGlosses'
import { useTextDirection } from '../../composables/useTextDirection'

defineOptions({ name: 'YanView' })

/** 该节的全文（若有）。 */
const fullTextOf = (id: string) => YAN_FULL_TEXTS[id]

const { direction, toggleDirection } = useTextDirection()

/**
 * 注音分段结果按篇缓存。正文是静态数据，不会变，所以只需算一次；
 * 4149 字若每次重渲染都重新切分，翻页会有可感的迟滞。
 */
const runCache = new Map<string, YanRun[][]>()
function runsFor(id: string): YanRun[][] {
  let cached = runCache.get(id)
  if (!cached) {
    const text = YAN_FULL_TEXTS[id]
    cached = text ? text.paragraphs.map(segmentForGlosses) : []
    runCache.set(id, cached)
  }
  return cached
}

/** 可跳转的篇目（有全文者）。 */
const navigable = YAN_COLLECTION.sections.filter(
  (s) => s.fullTextStatus !== 'DATA_GAP' && YAN_FULL_TEXTS[s.id] !== undefined,
)
</script>

<template>
  <section class="yan" aria-labelledby="yan-heading">
    <!-- Hero -->
    <header class="yan-hero">
      <p class="hfm-eyebrow">数字人文 · 文本选编</p>
      <h1 id="yan-heading" class="yan-hero__title">{{ YAN_COLLECTION.title }}</h1>
      <p class="yan-hero__subtitle">{{ YAN_COLLECTION.subtitle }}</p>
    </header>

    <!-- Collection Introduction -->
    <section class="yan-section" aria-labelledby="intro-heading">
      <h2 id="intro-heading" class="section-title">选编说明</h2>
      <p class="yan-intro hfm-reading">{{ YAN_COLLECTION.intro }}</p>
      <p class="yan-source-note">
        来源：{{
          YAN_COLLECTION.source
        }}。上列为客户文稿的整理说明；四篇全文另依公版文献录入（见各篇"底本"
        与"校勘记"），与整理说明分列，不混为一谈。
      </p>
    </section>

    <!-- 篇目导航：四篇互跳 -->
    <nav v-if="navigable.length" class="yan-nav" aria-label="篇目与阅读版式">
      <h2 class="visually-hidden">篇目与阅读版式</h2>
      <ol class="yan-nav__list">
        <li v-for="s in navigable" :key="s.id">
          <a class="yan-nav__link" :href="`#${s.id}-section`">{{ s.title }}</a>
        </li>
      </ol>
      <!-- 版式是全局偏好，四篇同时切换，所以只放一个开关：
           每篇放一个会让人以为是逐篇设置。 -->
      <button
        type="button"
        class="yan-direction"
        :aria-pressed="direction === 'vertical'"
        @click="toggleDirection"
      >
        {{ direction === 'vertical' ? '切为横排' : '切为竖排' }}
      </button>
    </nav>

    <!-- Text / Quotation Collection (material structure: four sections) -->
    <section
      v-for="section in YAN_COLLECTION.sections"
      :id="`${section.id}-section`"
      :key="section.id"
      class="yan-section"
      :aria-labelledby="`${section.id}-heading`"
    >
      <h2 :id="`${section.id}-heading`" class="section-title">{{ section.title }}</h2>

      <!-- 全文：底本正文 + 出处 + 校勘记。
           data-source="static"：本块为编辑录入的静态内容，不经后台投影，
           与其言题录信息的来源性质一致（对照首页各块的 backend / fallback 标记）。 -->
      <div
        v-if="section.fullTextStatus !== 'DATA_GAP' && fullTextOf(section.id)"
        class="yan-fulltext"
        data-source="static"
      >
        <div
          class="yan-fulltext__body hfm-reading"
          :class="`yan-fulltext__body--${direction}`"
        >
          <p v-for="(para, i) in runsFor(section.id)" :key="i">
            <template v-for="(run, j) in para" :key="j">
              <ruby v-if="run.gloss" :title="run.gloss.gloss">
                {{ run.text }}<rt>{{ run.gloss.pinyin }}</rt>
              </ruby>
              <template v-else>{{ run.text }}</template>
            </template>
          </p>
        </div>

        <p class="yan-fulltext__provenance">
          <span class="yan-fulltext__label">底本</span>
          {{ fullTextOf(section.id).base.edition }}
          <template v-if="fullTextOf(section.id).collated.length">
            ｜<span class="yan-fulltext__label">参校</span>
            {{ fullTextOf(section.id).collated.map((c) => c.edition).join('、') }}
          </template>
        </p>

        <aside
          v-if="fullTextOf(section.id).variants.length"
          class="yan-apparatus"
          :aria-labelledby="`${section.id}-apparatus`"
        >
          <h3 :id="`${section.id}-apparatus`" class="yan-apparatus__title">
            校勘记 · {{ section.title }}
          </h3>
          <ol class="yan-apparatus__list">
            <li v-for="(v, i) in fullTextOf(section.id).variants" :key="i">
              <span class="yan-apparatus__base">{{ v.base }}</span>
              <span v-if="v.baseSuspect" class="yan-apparatus__flag">底本疑误</span>
              ——
              <span v-for="(r, j) in v.readings" :key="j">
                <template v-if="j > 0">；</template>{{ r.source }}作「{{ r.text }}」
              </span>
              。{{ v.note }}
            </li>
          </ol>
        </aside>

        <p v-if="fullTextOf(section.id).caveat" class="yan-fulltext__caveat">
          {{ fullTextOf(section.id).caveat }}
        </p>
      </div>

      <p v-else class="yan-fulltext-status" data-empty-state>
        本篇全文未录入 · 以下为题录与整理说明
      </p>

      <article v-for="record in section.records" :key="record.id" class="quotation">
        <p class="quotation__text hfm-reading">{{ record.text }}</p>

        <p v-if="record.sourceContext" class="quotation__context hfm-reading">
          {{ record.sourceContext }}
        </p>

        <ul class="quotation__meta">
          <li v-if="record.theme">
            <span class="quotation__meta-label">编辑主题（展示分类）</span>
            {{ record.theme }}
          </li>
          <li v-if="record.relatedPerson">
            <span class="quotation__meta-label">相关人物</span>
            {{ record.relatedPerson }}
          </li>
          <li v-if="record.relatedWork">
            <span class="quotation__meta-label">相关作品</span>
            {{ record.relatedWork }}
          </li>
          <li>
            <span class="quotation__meta-label">来源</span>
            {{ record.source }}
          </li>
        </ul>
      </article>
    </section>

    <!-- Supplement -->
    <section
      v-if="YAN_COLLECTION.supplement"
      class="yan-section"
      aria-labelledby="supplement-heading"
    >
      <h2 id="supplement-heading" class="section-title">辑佚补充</h2>
      <p class="yan-supplement hfm-reading">{{ YAN_COLLECTION.supplement }}</p>
    </section>

    <!-- Source -->
    <section class="yan-section" aria-labelledby="source-heading">
      <h2 id="source-heading" class="section-title">出处</h2>
      <p class="yan-source">
        文本依据：{{ YAN_COLLECTION.source }}。主题与节次按客户文稿结构整理；
        现代说明文字与原文说明以版面区分，不改变客户原文语义。
      </p>
    </section>

    <!-- Related -->
    <section class="yan-section" aria-labelledby="related-heading">
      <h2 id="related-heading" class="section-title">相关</h2>
      <ul class="related-list">
        <li class="related-item">
          <a class="related-item__link" href="/persons/ENT-PERSON-HFM-HUANGFUMI">皇甫谧人物档案</a>
        </li>
        <li class="related-item">
          <a class="related-item__link" href="/works">论著与研究</a>
        </li>
        <li class="related-item">
          <a class="related-item__link" href="/archive">数字档案</a>
        </li>
        <li class="related-item">
          <a class="related-item__link" href="/jiayi">《针灸甲乙经》</a>
        </li>
      </ul>
    </section>
  </section>
</template>

<style scoped>
.yan {
  max-width: var(--hfm-content-max);
  margin: 0 auto;
}

.yan-hero {
  padding: var(--hfm-space-8) 0 var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
  margin-bottom: var(--hfm-space-12);
}

.yan-hero__title {
  font-size: var(--hfm-text-3xl);
  margin: 0 0 var(--hfm-space-3);
  letter-spacing: var(--hfm-tracking-display);
}

.yan-hero__subtitle {
  color: var(--hfm-color-text-secondary);
  margin: 0;
}

.yan-section {
  margin-bottom: var(--hfm-space-12);
}

.section-title {
  margin: 0 0 var(--hfm-space-4);
  padding-bottom: var(--hfm-space-2);
  border-bottom: 1px solid var(--hfm-color-border);
}

.yan-intro,
.yan-supplement {
  margin: 0;
}

.yan-source-note {
  margin-top: var(--hfm-space-3);
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.yan-fulltext {
  margin: var(--hfm-space-6) 0 var(--hfm-space-8);
  max-width: var(--hfm-reader-max);
}
.yan-fulltext__body {
  font-family: var(--hfm-font-ancient);
  font-size: var(--hfm-text-lg);
  line-height: var(--hfm-leading-reading);
  letter-spacing: var(--hfm-tracking-ancient);
  color: var(--hfm-color-text);
}
.yan-fulltext__body p {
  margin: 0 0 var(--hfm-space-5);
  text-indent: 2em;
}

/* 竖排：古籍本来的形态。容器给固定高度并横向滚动，避免撑破页面。 */
.yan-fulltext__body--vertical {
  writing-mode: vertical-rl;
  max-height: min(70vh, 42rem);
  overflow-x: auto;
  overflow-y: hidden;
  padding-left: var(--hfm-space-3);
}
.yan-fulltext__body--vertical p {
  margin: 0 0 0 var(--hfm-space-5);
  text-indent: 2em;
}

/* 注音：只对生僻字出现，字号缩小、颜色减淡，不打断正文。 */
.yan-fulltext__body ruby {
  ruby-align: center;
}
.yan-fulltext__body rt {
  font-family: var(--hfm-font-sans);
  font-size: 0.5em;
  letter-spacing: 0;
  color: var(--hfm-color-text-muted);
}

/* 阅读工具条 */
.yan-fulltext__bar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: var(--hfm-space-3);
}
.yan-direction {
  padding: var(--hfm-space-1) var(--hfm-space-3);
  font-family: var(--hfm-font-sans);
  font-size: var(--hfm-text-xs);
  letter-spacing: var(--hfm-tracking-display);
  color: var(--hfm-color-text-secondary);
  background: none;
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  cursor: pointer;
}
.yan-direction:hover {
  color: var(--hfm-color-text);
  border-color: var(--hfm-color-border-strong);
}
.yan-direction:focus-visible {
  outline: 2px solid var(--hfm-color-interactive);
  outline-offset: 2px;
}

/* 篇目导航 */
.yan-nav {
  margin: 0 0 var(--hfm-space-8);
}
.yan-nav {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--hfm-space-3);
}
.yan-nav__list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2) var(--hfm-space-5);
  margin: 0;
  padding: 0;
  list-style: none;
}
.yan-nav__link {
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-secondary);
  text-decoration: none;
  border-bottom: 1px solid var(--hfm-color-border);
}
.yan-nav__link:hover {
  color: var(--hfm-color-text);
  border-bottom-color: var(--hfm-color-text);
}
.yan-fulltext__provenance,
.yan-fulltext__caveat {
  margin-top: var(--hfm-space-5);
  padding-top: var(--hfm-space-3);
  border-top: 1px solid var(--hfm-color-border);
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}
.yan-fulltext__label {
  color: var(--hfm-color-text-secondary);
  letter-spacing: 0.08em;
}
.yan-apparatus {
  margin-top: var(--hfm-space-5);
  padding: var(--hfm-space-4);
  background: var(--hfm-color-surface);
  border-left: 2px solid var(--hfm-color-border-strong);
}
.yan-apparatus__title {
  margin: 0 0 var(--hfm-space-3);
  font-family: var(--hfm-font-heading);
  font-size: var(--hfm-text-sm);
  letter-spacing: var(--hfm-tracking-display);
}
.yan-apparatus__list {
  margin: 0;
  padding-left: 1.2em;
  font-size: var(--hfm-text-sm);
  line-height: var(--hfm-leading-normal);
  color: var(--hfm-color-text-secondary);
}
.yan-apparatus__list li {
  margin-bottom: var(--hfm-space-2);
}
.yan-apparatus__base {
  color: var(--hfm-color-text);
  font-family: var(--hfm-font-ancient);
}
.yan-apparatus__flag {
  margin-left: var(--hfm-space-2);
  padding: 0 var(--hfm-space-1);
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-warning);
  border: 1px solid currentColor;
}
.yan-fulltext-status {
  margin: 0 0 var(--hfm-space-3);
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-warning);
}

.quotation {
  padding: var(--hfm-space-4) 0 var(--hfm-space-5);
  border-bottom: 1px solid var(--hfm-color-border);
}

.quotation__text {
  margin: 0;
}

.quotation__context {
  margin: var(--hfm-space-3) 0 0;
  color: var(--hfm-color-text-secondary);
}

.quotation__meta {
  list-style: none;
  margin: var(--hfm-space-3) 0 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2) var(--hfm-space-4);
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.quotation__meta-label {
  color: var(--hfm-color-text-muted);
  font-weight: 600;
}

.yan-source {
  color: var(--hfm-color-text-secondary);
  line-height: var(--hfm-leading-reading);
  max-width: 68ch;
  margin: 0;
}

.related-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-1);
}

.related-item {
  padding: var(--hfm-space-2) 0;
  border-bottom: 1px solid var(--hfm-color-border);
}

.related-item__link {
  color: var(--hfm-color-interactive);
  text-decoration: none;
}

.related-item__link:hover {
  text-decoration: underline;
}
</style>

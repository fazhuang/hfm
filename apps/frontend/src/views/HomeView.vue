<script setup lang="ts">
/**
 * HomeView — UI-03 flagship homepage.
 *
 * CONTEMPORARY CHINESE DIGITAL HUMANITIES PORTAL — 叙事首页，非功能拼盘：
 * Hero → 皇甫谧 → 《针灸甲乙经》 → 文献与史料 → 非遗活态传承 → 研究能力。
 * 全部内容来自既有已验证数据（homeProjection 选取/排序，零新领域事实）。
 * Search 连接 UI-10（/search?q=）；Research 为次级入口。
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  HOME_HERITAGE,
  HOME_HUANGFU,
  HOME_HUANGFU_DATE,
  HOME_HUANGFU_IDENTITIES,
  HOME_JIAYI,
  HOME_LITERATURE,
  HOME_METRICS,
  HOME_QUOTATION,
  HOME_RESEARCH_STEPS,
} from '../data/homeProjection'
import {
  presentationStatusLabel,
  resolvePresentationState,
  type PresentationState,
} from '../presentation/stateMapping'

defineOptions({ name: 'HomeView' })

const router = useRouter()
const searchInput = ref('')

/* UX2-P5 P1-01 correction — surfaced lineage/relation states route through
 * the shared P0 G1-C mapping. The data-status is the resolver output (the
 * fail-closed default for the unstructured rows, per the resolver contract:
 * rows 8/9/11 → UNSTRUCTURED_OR_INCOMPLETE); the public label flows through
 * the shared badge-label helper with the G1-C surface label (row 9
 * 版本关系整理中 / row 8 谱系整理中). No local mapping is duplicated; no
 * template literals for data-status or label. */
const jiayiLineageState: PresentationState = resolvePresentationState({ contentStatus: 'DATA_GAP' })
const heritageLineageState: PresentationState = resolvePresentationState({ contentStatus: 'DATA_GAP' })
const jiayiLineageLabel = presentationStatusLabel(jiayiLineageState, '版本关系整理中')
const heritageLineageLabel = presentationStatusLabel(heritageLineageState, '谱系整理中')

function onSearch(): void {
  const q = searchInput.value.trim()
  void router.push({ path: '/search', query: q ? { q } : {} })
}
</script>

<template>
  <div class="home">
    <!-- Hero -->
    <header class="home-hero" aria-labelledby="home-title">
      <p class="hfm-eyebrow">当代东方数字人文门户</p>
      <h1 id="home-title" class="home-hero__title">皇甫谧人文数字平台</h1>
      <p class="home-hero__subtitle">权威数字人文资料 · 古籍与研究 · 非遗活态传承</p>

      <div class="home-hero__person">
        <span class="home-hero__dates">皇甫谧 {{ HOME_HUANGFU_DATE }}</span>
      </div>
      <p class="home-hero__definition">{{ HOME_HUANGFU.lede }}</p>

      <div class="home-hero__actions">
        <a class="home-hero__cta" href="/persons/person-huangfu-mi">探索皇甫谧</a>
        <a class="home-hero__cta home-hero__cta--alt" href="/jiayi">进入《针灸甲乙经》</a>
        <a class="home-hero__link" href="/search">检索文献</a>
      </div>

      <form class="home-search" role="search" aria-label="平台内容检索" @submit.prevent="onSearch">
        <label class="visually-hidden" for="home-search-input">检索平台内容</label>
        <input
          id="home-search-input"
          v-model="searchInput"
          type="search"
          placeholder="检索人物、作品、版本、文献与论文…"
        />
        <button type="submit">检索</button>
      </form>
    </header>

    <!-- Metrics -->
    <dl class="home-metrics" aria-label="平台内容规模">
      <div v-for="metric in HOME_METRICS" :key="metric.label" class="home-metric">
        <dt>{{ metric.label }}</dt>
        <dd>
          <strong>{{ metric.value }}</strong>
          <span>{{ metric.note }}</span>
        </dd>
      </div>
    </dl>

    <!-- 皇甫谧 -->
    <section class="home-section home-section--person" aria-labelledby="feature-hfm-heading">
      <p class="hfm-eyebrow">人物档案</p>
      <h2 id="feature-hfm-heading" class="home-section__title">{{ HOME_HUANGFU.heading }}</h2>
      <ul class="home-tags" aria-label="多维身份">
        <li v-for="identity in HOME_HUANGFU_IDENTITIES" :key="identity">{{ identity }}</li>
      </ul>
      <p class="home-section__lede">{{ HOME_HUANGFU.lede }}</p>
      <ul class="home-links">
        <li v-for="item in HOME_HUANGFU.items" :key="item.href">
          <a :href="item.href" class="home-links__title">{{ item.title }}</a>
          <span v-if="item.meta" class="home-links__meta">{{ item.meta }}</span>
        </li>
      </ul>
      <p class="home-cta-row">
        <a class="home-cta" href="/persons/person-huangfu-mi">人物档案 →</a>
      </p>
    </section>

    <!-- 《针灸甲乙经》 -->
    <section class="home-section home-section--jiayi" aria-labelledby="feature-jiayi-heading">
      <p class="hfm-eyebrow">学术专题</p>
      <h2 id="feature-jiayi-heading" class="home-section__title">{{ HOME_JIAYI.heading }}</h2>
      <p class="home-section__lede">{{ HOME_JIAYI.lede }}</p>

      <figure class="home-lineage">
        <img :src="HOME_JIAYI.lineage.src" :alt="HOME_JIAYI.lineage.alt" />
        <figcaption>
          <span class="hfm-status" :data-status="jiayiLineageState">{{ jiayiLineageLabel }}</span>
          <span class="home-lineage__caption">版本脉络（客户资料）· 结构化版本关系整理中（DATA-GAP）</span>
        </figcaption>
      </figure>

      <ul class="home-editions" aria-label="代表版本">
        <li v-for="edition in HOME_JIAYI.editions" :key="edition.title">
          <span class="home-editions__title">{{ edition.title }}</span>
          <span class="home-editions__period"
            >{{ edition.period
            }}<template v-if="edition.imprint"> · {{ edition.imprint }}</template></span
          >
        </li>
      </ul>
      <p class="home-cta-row">
        <a class="home-cta" :href="HOME_JIAYI.cta.href">{{ HOME_JIAYI.cta.label }} →</a>
      </p>
    </section>

    <!-- 文献与史料 -->
    <section
      class="home-section home-section--literature"
      aria-labelledby="feature-literature-heading"
    >
      <p class="hfm-eyebrow">文献与史料</p>
      <h2 id="feature-literature-heading" class="home-section__title">
        {{ HOME_LITERATURE.heading }}
      </h2>
      <p class="home-section__lede">{{ HOME_LITERATURE.lede }}</p>

      <blockquote class="home-quote">
        <p>{{ HOME_QUOTATION.text }}</p>
        <footer>
          —— {{ HOME_QUOTATION.attribution }}《{{ HOME_QUOTATION.source }}》（后论 · 历史评价）
        </footer>
      </blockquote>

      <ul class="home-links">
        <li v-for="item in HOME_LITERATURE.items" :key="item.href">
          <a :href="item.href" class="home-links__title">{{ item.title }}</a>
          <span v-if="item.meta" class="home-links__meta">{{ item.meta }}</span>
        </li>
      </ul>
    </section>

    <!-- 非遗活态传承 -->
    <section class="home-section home-section--heritage" aria-labelledby="feature-heritage-heading">
      <p class="hfm-eyebrow">非遗活态传承</p>
      <h2 id="feature-heritage-heading" class="home-section__title">{{ HOME_HERITAGE.heading }}</h2>
      <p class="home-section__lede">{{ HOME_HERITAGE.lede }}</p>
      <p class="home-state-line">
        <span class="hfm-status" :data-status="heritageLineageState">{{ heritageLineageLabel }}</span>
      </p>
      <ul class="home-links">
        <li v-for="item in HOME_HERITAGE.items" :key="item.title">
          <a :href="item.href" class="home-links__title">{{ item.title }}</a>
          <span v-if="item.meta" class="home-links__meta">{{ item.meta }}</span>
        </li>
      </ul>
      <p class="home-cta-row">
        <a class="home-cta" href="/heritage">非遗传承 →</a>
      </p>
    </section>

    <!-- Research Discovery -->
    <section
      class="home-section home-section--research"
      aria-labelledby="research-discovery-heading"
    >
      <p class="hfm-eyebrow">研究能力</p>
      <h2 id="research-discovery-heading" class="home-section__title">从资料到研究</h2>
      <ol class="home-steps">
        <li v-for="step in HOME_RESEARCH_STEPS" :key="step.label">
          <a :href="step.href">
            <strong>{{ step.label }}</strong>
            <span>{{ step.note }}</span>
          </a>
        </li>
      </ol>
      <p class="home-cta-row">
        <a class="home-cta" href="/research">进入研究工作台</a>
        <a class="home-cta home-cta--alt" href="/search?q=针灸甲乙经">检索全部文献</a>
      </p>
    </section>
  </div>
</template>

<style scoped>
.home {
  max-width: var(--hfm-content-max);
  margin: 0 auto;
}

/* Hero */
.home-hero {
  padding: var(--hfm-space-12) 0 var(--hfm-space-8);
  border-bottom: 1px solid var(--hfm-color-border);
}

.home-hero__title {
  font-size: var(--hfm-text-4xl);
  margin: 0 0 var(--hfm-space-3);
  letter-spacing: var(--hfm-tracking-display);
}

.home-hero__subtitle {
  font-size: var(--hfm-text-lg);
  color: var(--hfm-color-text-secondary);
  margin: 0 0 var(--hfm-space-5);
}

.home-hero__dates {
  font-family: var(--hfm-font-numeric);
  font-variant-numeric: tabular-nums;
  color: var(--hfm-color-heritage);
}

.home-hero__definition {
  max-width: 52ch;
  line-height: var(--hfm-leading-reading);
  margin: var(--hfm-space-3) 0 var(--hfm-space-5);
}

.home-hero__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--hfm-space-3);
}

.home-hero__cta {
  padding: var(--hfm-space-2) var(--hfm-space-5);
  border: 1px solid var(--hfm-color-accent);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-accent);
  color: var(--hfm-color-on-accent);
  font-weight: 600;
  text-decoration: none;
}

.home-hero__cta--alt {
  background: var(--hfm-color-surface);
  color: var(--hfm-color-accent);
}

.home-hero__link {
  color: var(--hfm-color-interactive);
  text-decoration: none;
}

.home-hero__link:hover {
  text-decoration: underline;
}

.home-search {
  display: flex;
  gap: var(--hfm-space-2);
  max-width: 34rem;
  margin-top: var(--hfm-space-6);
}

.home-search input {
  flex: 1;
  min-width: 0;
  padding: var(--hfm-space-2) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
}

.home-search button {
  padding: var(--hfm-space-2) var(--hfm-space-4);
  border: 1px solid var(--hfm-color-accent);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-accent);
  cursor: pointer;
  font-weight: 600;
}

/* Metrics */
.home-metrics {
  margin: var(--hfm-space-8) 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--hfm-space-2);
}

.home-metric {
  padding: var(--hfm-space-3);
  border-left: 3px solid var(--hfm-color-border-strong);
}

.home-metric dt {
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.home-metric dd {
  margin: 0;
  display: grid;
  gap: 2px;
}

.home-metric strong {
  font-size: var(--hfm-text-2xl);
  font-family: var(--hfm-font-numeric);
  font-variant-numeric: tabular-nums;
  color: var(--hfm-color-text);
}

.home-metric span {
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

/* Sections */
.home-section {
  padding: var(--hfm-space-12) 0;
  border-bottom: 1px solid var(--hfm-color-border);
}

.home-section__title {
  font-size: var(--hfm-text-3xl);
  margin: 0 0 var(--hfm-space-3);
}

.home-section__lede {
  max-width: 60ch;
  line-height: var(--hfm-leading-reading);
  color: var(--hfm-color-text-secondary);
  margin: 0 0 var(--hfm-space-5);
}

.home-tags {
  list-style: none;
  margin: 0 0 var(--hfm-space-4);
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2);
}

.home-tags li {
  padding: var(--hfm-space-1) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border-strong);
  border-radius: var(--hfm-radius-sm);
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-secondary);
}

.home-links {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-1);
}

.home-links li {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-3);
  align-items: baseline;
  padding: var(--hfm-space-2) 0;
  border-bottom: 1px solid var(--hfm-color-border);
}

.home-links__title {
  color: var(--hfm-color-interactive);
  text-decoration: none;
  font-weight: 600;
}

.home-links__title:hover {
  text-decoration: underline;
}

.home-links__meta {
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
}

.home-lineage {
  margin: 0 0 var(--hfm-space-5);
  padding: var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
}

.home-lineage img {
  display: block;
  width: 100%;
  height: auto;
  border-radius: var(--hfm-radius-sm);
}

.home-lineage figcaption {
  margin-top: var(--hfm-space-2);
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2);
  align-items: baseline;
}

.home-lineage__caption {
  margin: 0;
}

/* UX2-P5: surfaced presentation-state line (heritage PARTIAL lineage) */
.home-state-line {
  margin: 0 0 var(--hfm-space-4);
}

.home-editions {
  list-style: none;
  margin: 0 0 var(--hfm-space-5);
  padding: 0;
  display: grid;
  gap: var(--hfm-space-1);
}

.home-editions li {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-3);
  justify-content: space-between;
  padding: var(--hfm-space-2) 0;
  border-bottom: 1px solid var(--hfm-color-border);
}

.home-editions__title {
  font-weight: 600;
}

.home-editions__period {
  color: var(--hfm-color-heritage);
  font-size: var(--hfm-text-sm);
  font-variant-numeric: tabular-nums;
}

.home-quote {
  margin: 0 0 var(--hfm-space-5);
  padding: var(--hfm-space-4) var(--hfm-space-5);
  border-left: 3px solid var(--hfm-color-citation);
  background: var(--hfm-color-surface);
  border-radius: var(--hfm-radius-sm);
}

.home-quote p {
  margin: 0 0 var(--hfm-space-2);
  font-family: var(--hfm-font-serif);
  line-height: var(--hfm-leading-reading);
}

.home-quote footer {
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.home-steps {
  list-style: none;
  margin: 0 0 var(--hfm-space-5);
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--hfm-space-2);
}

.home-steps a {
  display: grid;
  gap: var(--hfm-space-1);
  padding: var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-text);
  text-decoration: none;
}

.home-steps a:hover {
  border-color: var(--hfm-color-citation);
}

.home-steps strong {
  color: var(--hfm-color-citation);
}

.home-steps span {
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-muted);
}

.home-cta-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-3);
  margin: var(--hfm-space-5) 0 0;
}

.home-cta {
  display: inline-block;
  padding: var(--hfm-space-1) var(--hfm-space-4);
  border: 1px solid var(--hfm-color-accent);
  border-radius: var(--hfm-radius-sm);
  color: var(--hfm-color-accent);
  font-weight: 600;
  text-decoration: none;
}

.home-cta--alt {
  border-color: var(--hfm-color-border-strong);
  color: var(--hfm-color-text-secondary);
}

.home-cta:hover {
  background: var(--hfm-color-accent);
  color: var(--hfm-color-on-accent);
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
}

@media (max-width: 767px) {
  .home-hero {
    padding: var(--hfm-space-8) 0 var(--hfm-space-6);
  }

  .home-hero__title {
    font-size: var(--hfm-text-3xl);
  }

  .home-section {
    padding: var(--hfm-space-8) 0;
  }

  .home-section__title {
    font-size: var(--hfm-text-2xl);
  }
}
</style>

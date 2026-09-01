<script setup lang="ts">
/**
 * YanView — 其言 (UI-06) Digital Quotation / Text Collection.
 *
 * 皇甫谧言论与文本选编（据客户正式材料其言.docx）。内容忠实取自客户文稿：
 * 集引言 + 四篇说明（《三都赋》序 / 玄守论 / 释劝论 / 笃终论）+ 辑佚补充。
 * 四篇全文未见于客户文稿 → 明确 DATA_GAP，页面不虚构全文、不润色成"名言"。
 * 主题标签为展示分类（PRESENTATION_CLASSIFICATION），非史料原始分类。
 */
import { YAN_COLLECTION } from '../../data/yanCollection'

defineOptions({ name: 'YanView' })
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
        }}。本文为整理说明文本；四篇古典全文整理中（未见于客户文稿，不虚构）。
      </p>
    </section>

    <!-- Text / Quotation Collection (material structure: four sections) -->
    <section
      v-for="section in YAN_COLLECTION.sections"
      :id="`${section.id}-section`"
      :key="section.id"
      class="yan-section"
      :aria-labelledby="`${section.id}-heading`"
    >
      <h2 :id="`${section.id}-heading`" class="section-title">{{ section.title }}</h2>

      <p v-if="section.fullTextStatus === 'DATA_GAP'" class="yan-fulltext-status" role="status">
        全文整理中（客户文稿为整理说明，未含全文）
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
          <a class="related-item__link" href="/persons/person-huangfu-mi">皇甫谧人物档案</a>
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

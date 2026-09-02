<script setup lang="ts">
/**
 * HomeKnowledgeSection — accepted homepage Section 04 (Knowledge S4-B Refined).
 *
 * WP-02A STRUCTURAL SHELL ONLY. Semantic root + h2 + knowledge-layer counts
 * (derived from inventory/search: 56 / 6 / 19 / 92 / 515 / 5) + research path.
 * No final visual fidelity (no manuscript leaf figure/figcaption, no
 * transformation-zone absolute geometry, no fixed 1240 height) — that belongs
 * to WP-04. NOTE: the WP-04/04C invalid <figcaption>-under-<div> is a WP-04
 * defect, not present here (this structural shell uses no <figure>/<figcaption>).
 */
import { HOME_KNOWLEDGE, HOME_CHAPTERS, HOME_RESEARCH_STEPS } from '../../data/homeProjection'

defineOptions({ name: 'HomeKnowledgeSection' })
</script>

<template>
  <section
    id="home-knowledge"
    class="home-section home-section--knowledge"
    aria-labelledby="home-knowledge-title"
  >
    <p class="home-eyebrow">
      <span class="home-eyebrow__no">{{ HOME_CHAPTERS.knowledge.no }}</span
      >{{ HOME_CHAPTERS.knowledge.label }}
    </p>
    <h2 id="home-knowledge-title" class="home-section__title">{{ HOME_KNOWLEDGE.headline }}</h2>

    <ol class="home-knowledge__list">
      <li v-for="item in HOME_KNOWLEDGE.structure" :key="item.title" class="home-knowledge__node">
        <span class="home-knowledge__node-title">{{ item.title }}</span>
        <span class="home-knowledge__node-role">{{ item.role }}</span>
        <span class="home-knowledge__node-note">{{ item.note }}</span>
      </li>
    </ol>

    <dl class="home-knowledge__counts" aria-label="平台知识层 · 可检索记录">
      <div class="home-knowledge__count">
        <dt>条可检索记录</dt>
        <dd>{{ HOME_KNOWLEDGE.searchable }}</dd>
      </div>
      <div class="home-knowledge__count">
        <dt>类内容</dt>
        <dd>{{ HOME_KNOWLEDGE.categories }}</dd>
      </div>
      <div class="home-knowledge__count">
        <dt>版本记录</dt>
        <dd>{{ HOME_KNOWLEDGE.editions }}</dd>
      </div>
      <div class="home-knowledge__count">
        <dt>论著资料</dt>
        <dd>{{ HOME_KNOWLEDGE.lunzhu }}</dd>
      </div>
      <div class="home-knowledge__count">
        <dt>学术论文</dt>
        <dd>{{ HOME_KNOWLEDGE.lunwen }}</dd>
      </div>
      <div class="home-knowledge__count">
        <dt>已结构化题录</dt>
        <dd>{{ HOME_KNOWLEDGE.structured }}</dd>
      </div>
    </dl>

    <ol class="home-steps" aria-label="研究路径 · 从检索到引用">
      <li v-for="step in HOME_RESEARCH_STEPS" :key="step.label" class="home-step">
        <a :href="step.href">
          <strong>{{ step.label }}</strong>
          <span>{{ step.note }}</span>
        </a>
      </li>
    </ol>

    <p class="home-cta-row">
      <a class="home-cta" :href="HOME_KNOWLEDGE.cta.href">{{ HOME_KNOWLEDGE.cta.label }} →</a>
    </p>
  </section>
</template>

<style scoped>
/* WP-02A STRUCTURAL SHELL ONLY. */
.home-section--knowledge {
  padding: var(--hfm-space-12) var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
}
.home-knowledge__list {
  list-style: none;
  padding: 0;
}
.home-knowledge__node {
  display: grid;
  gap: var(--hfm-space-1);
  padding: var(--hfm-space-3) 0;
  border-top: 1px solid var(--hfm-color-border);
}
.home-knowledge__counts {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--hfm-space-4);
  margin: var(--hfm-space-6) 0;
}
.home-knowledge__count dd {
  font-family: var(--hfm-font-display);
  font-size: var(--hfm-text-2xl);
  margin: var(--hfm-space-1) 0;
}
.home-steps {
  list-style: none;
  padding: 0;
}
.home-step a {
  display: block;
  padding: var(--hfm-space-3) 0;
  border-top: 1px solid var(--hfm-color-border);
}
.home-step span {
  display: block;
  color: var(--hfm-color-text-muted);
}
</style>

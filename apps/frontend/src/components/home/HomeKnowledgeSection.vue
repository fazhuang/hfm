<script setup lang="ts">
/**
 * HomeKnowledgeSection — homepage Section 04 (知识对象 / Knowledge S4-B).
 *
 * CF-07 STRUCTURAL SHELL ONLY. Semantic <section id="home-knowledge"> root +
 * h2 + the platform's real knowledge categories (mirror of the six search
 * facet types) + a count register derived from contentInventory / searchIndex
 * + the 检索→阅读→来源→引用 research path (existing HOME_RESEARCH_STEPS).
 * No final visual fidelity — that belongs to the visual work packages.
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
    <p class="hfm-eyebrow">
      <span class="home-chapter__no">{{ HOME_CHAPTERS.knowledge.no }}</span
      >{{ HOME_CHAPTERS.knowledge.label }}
    </p>
    <h2 id="home-knowledge-title" class="home-section__title">
      {{ HOME_KNOWLEDGE.headline }}
    </h2>
    <p class="home-section__lede">
      {{ HOME_KNOWLEDGE.lede }}
    </p>

    <ul class="home-knowledge__categories" aria-label="平台知识对象类别">
      <li
        v-for="category in HOME_KNOWLEDGE.categories"
        :key="category.title"
        class="home-knowledge__category"
      >
        <span class="home-knowledge__category-title">{{ category.title }}</span>
        <span class="home-knowledge__category-note">{{ category.note }}</span>
      </li>
    </ul>

    <dl class="home-knowledge__register" aria-label="平台内容规模 · 数据来源审计">
      <div v-for="row in HOME_KNOWLEDGE.register" :key="row.label" class="home-knowledge__row">
        <dt>{{ row.label }}</dt>
        <dd>
          <strong>{{ row.value }}</strong>
          <span>{{ row.note }}</span>
        </dd>
      </div>
    </dl>

    <ol class="home-knowledge__steps" aria-label="研究路径 · 从检索到引用">
      <li v-for="step in HOME_RESEARCH_STEPS" :key="step.label" class="home-knowledge__step">
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
/* CF-07 STRUCTURAL SHELL ONLY. */
.home-chapter__no {
  margin-right: 0.6em;
  color: var(--hfm-color-text-muted);
  font-variant-numeric: tabular-nums;
}

.home-section--knowledge {
  padding: var(--hfm-space-12) var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
}

.home-knowledge__categories {
  list-style: none;
  margin: var(--hfm-space-4) 0 0;
  padding: 0;
}

.home-knowledge__category {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-3);
  align-items: baseline;
  padding: var(--hfm-space-2) 0;
  border-top: 1px solid var(--hfm-color-border);
}

.home-knowledge__category-title {
  font-weight: 600;
  min-width: 4em;
}

.home-knowledge__category-note {
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
}

.home-knowledge__register {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--hfm-space-2);
  margin: var(--hfm-space-6) 0;
}

.home-knowledge__row {
  padding: var(--hfm-space-3);
  border-left: 3px solid var(--hfm-color-border-strong);
}

.home-knowledge__row dt {
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.home-knowledge__row dd {
  margin: 0;
  display: grid;
  gap: 2px;
}

.home-knowledge__row strong {
  font-size: var(--hfm-text-2xl);
  font-family: var(--hfm-font-numeric, var(--hfm-font-sans));
  font-variant-numeric: tabular-nums;
}

.home-knowledge__row span {
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.home-knowledge__steps {
  list-style: none;
  margin: 0;
  padding: 0;
}

.home-knowledge__step a {
  display: block;
  padding: var(--hfm-space-3) 0;
  border-top: 1px solid var(--hfm-color-border);
  text-decoration: none;
  color: var(--hfm-color-text);
}

.home-knowledge__step a:hover {
  color: var(--hfm-color-accent-hover);
}

.home-knowledge__step strong {
  color: var(--hfm-color-citation);
}

.home-knowledge__step span {
  display: block;
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
}

.home-cta-row {
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

.home-cta:hover {
  background: var(--hfm-color-accent);
  color: var(--hfm-color-on-accent);
}
</style>

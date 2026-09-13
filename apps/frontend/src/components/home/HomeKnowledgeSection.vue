<script setup lang="ts">
/**
 * HomeKnowledgeSection — Section 04 (知识对象). 《刻度》 ledger voice:
 * the structured-knowledge register (counts from the single inventory source)
 * rendered as ruled account lines, plus the six facet categories.
 */
import { HOME_KNOWLEDGE, HOME_CHAPTERS } from '../../data/homeProjection'

defineOptions({ name: 'HomeKnowledgeSection' })
</script>

<template>
  <section id="home-knowledge" class="xl-sec" aria-labelledby="home-knowledge-title">
    <div class="xl-inner">
      <header class="xl-head">
        <div class="xl-head__aside">
          <span class="xl-index">{{ HOME_CHAPTERS.knowledge.no }}</span>
          <span class="xl-label">Knowledge</span>
        </div>
        <div>
          <h2 id="home-knowledge-title" class="xl-title">{{ HOME_KNOWLEDGE.headline }}</h2>
          <p class="xl-lede">{{ HOME_KNOWLEDGE.lede }}</p>
        </div>
      </header>

      <ul class="knowledge__register xl-rows">
        <li
          v-for="(row, i) in HOME_KNOWLEDGE.register"
          :key="row.label"
          class="xl-row knowledge__register-row"
        >
          <span class="xl-row__index">{{ String(i + 1).padStart(2, '0') }}</span>
          <div class="xl-row__body knowledge__register-body">
            <span class="knowledge__register-label">{{ row.label }}</span>
            <span class="knowledge__register-value xl-num">{{ row.value }}</span>
            <span class="knowledge__register-note">{{ row.note }}</span>
          </div>
        </li>
      </ul>

      <ul class="knowledge__categories">
        <li
          v-for="(category, i) in HOME_KNOWLEDGE.categories"
          :key="category.title"
          class="knowledge__category"
        >
          <span class="knowledge__category-no xl-num">{{ String(i + 1).padStart(2, '0') }}</span>
          <h3 class="knowledge__category-title">{{ category.title }}</h3>
          <p class="knowledge__category-note">{{ category.note }}</p>
        </li>
      </ul>

      <div class="knowledge__foot">
        <p class="knowledge__types">
          <span class="xl-label">Facets</span> {{ HOME_KNOWLEDGE.knowledgeTypes }}
        </p>
        <a class="home-knowledge__act knowledge__cta xl-go" :href="HOME_KNOWLEDGE.cta.href">
          {{ HOME_KNOWLEDGE.cta.label }}
          <span class="home-knowledge__act-arr knowledge__cta-arr xl-go__arr" aria-hidden="true"
            >→</span
          >
        </a>
      </div>
    </div>
  </section>
</template>

<style scoped>
.knowledge__register {
  margin: 0 0 var(--hfm-space-12);
}
.knowledge__register-body {
  display: grid;
  grid-template-columns: minmax(7rem, 0.4fr) 5rem minmax(0, 1fr);
  gap: var(--hfm-space-5);
  align-items: baseline;
}
.knowledge__register-label {
  font-size: var(--hfm-text-base);
  color: var(--wl-ink-2);
}
.knowledge__register-value {
  font-size: var(--hfm-text-3xl);
  line-height: 1;
  color: var(--wl-ink);
}
.knowledge__register-note {
  font-size: var(--hfm-text-xs);
  color: var(--wl-mute);
}
.knowledge__categories {
  list-style: none;
  margin: 0 0 var(--hfm-space-8);
  padding: 0;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0 var(--hfm-space-8);
}
.knowledge__category {
  padding: var(--hfm-space-5) 0;
  border-top: 1px solid var(--wl-rule);
}
.knowledge__category-no {
  display: block;
  margin-bottom: var(--hfm-space-3);
  font-size: var(--hfm-text-sm);
  color: var(--wl-mark);
}
.knowledge__category-title {
  margin: 0 0 var(--hfm-space-1);
  font-family: var(--hfm-font-heading);
  font-size: var(--hfm-text-xl);
  font-weight: 500;
  color: var(--wl-ink);
}
.knowledge__category-note {
  margin: 0;
  font-size: var(--hfm-text-sm);
  line-height: 1.7;
  color: var(--wl-mute);
}
.knowledge__foot {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--hfm-space-6);
  padding-top: var(--hfm-space-5);
  border-top: 1px solid var(--wl-rule);
}
.knowledge__types {
  margin: 0;
  font-size: var(--hfm-text-sm);
  color: var(--wl-mute);
}
@media (max-width: 900px) {
  .knowledge__register-body {
    grid-template-columns: 1fr;
    gap: var(--hfm-space-2);
  }
  .knowledge__categories {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 599px) {
  .knowledge__categories {
    grid-template-columns: 1fr;
  }
}
</style>

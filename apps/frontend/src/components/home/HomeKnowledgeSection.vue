<script setup lang="ts">
/**
 * HomeKnowledgeSection — homepage Section 04 (知识对象 / structured knowledge).
 *
 * REDESIGN: an editorial head, a six-row knowledge register (counts derive from
 * contentInventory / searchIndex — single source), and the six knowledge
 * categories as a quiet editorial grid. CTA into the research workbench.
 *
 * CONTRACT PRESERVED (ui03_home.spec.ts): <section id="home-knowledge"> with the
 * single H2 「从古籍文字，到可探索的知识。」 and the real /research/search route.
 */
import { HOME_KNOWLEDGE, HOME_CHAPTERS } from '../../data/homeProjection'

defineOptions({ name: 'HomeKnowledgeSection' })
</script>

<template>
  <section id="home-knowledge" class="knowledge" aria-labelledby="home-knowledge-title">
    <div class="knowledge__inner">
      <header class="knowledge__head">
        <p class="knowledge__eyebrow">
          <span class="knowledge__no">{{ HOME_CHAPTERS.knowledge.no }}</span
          >{{ HOME_CHAPTERS.knowledge.label }}
        </p>
        <h2 id="home-knowledge-title" class="knowledge__title">{{ HOME_KNOWLEDGE.headline }}</h2>
        <p class="knowledge__lede">{{ HOME_KNOWLEDGE.lede }}</p>
      </header>

      <dl class="knowledge__register">
        <div
          v-for="row in HOME_KNOWLEDGE.register"
          :key="row.label"
          class="knowledge__register-row"
        >
          <dt class="knowledge__register-label">{{ row.label }}</dt>
          <dd class="knowledge__register-value">{{ row.value }}</dd>
          <dd class="knowledge__register-note">{{ row.note }}</dd>
        </div>
      </dl>

      <ul class="knowledge__categories">
        <li
          v-for="category in HOME_KNOWLEDGE.categories"
          :key="category.title"
          class="knowledge__category"
        >
          <h3 class="knowledge__category-title">{{ category.title }}</h3>
          <p class="knowledge__category-note">{{ category.note }}</p>
        </li>
      </ul>

      <div class="knowledge__foot">
        <p class="knowledge__types">
          <span class="knowledge__types-label">知识类型</span>{{ HOME_KNOWLEDGE.knowledgeTypes }}
        </p>
        <a class="home-knowledge__act knowledge__cta" :href="HOME_KNOWLEDGE.cta.href">
          {{ HOME_KNOWLEDGE.cta.label }} <span class="home-knowledge__act-arr knowledge__cta-arr" aria-hidden="true">→</span>
        </a>
      </div>
    </div>
  </section>
</template>

<style scoped>
.knowledge {
  background: var(--hfm-color-surface);
  padding: var(--hfm-space-24) var(--hfm-space-6);
}
.knowledge__inner {
  max-width: var(--hfm-content-max);
  margin: 0 auto;
}
.knowledge__head {
  max-width: 44rem;
  margin-bottom: var(--hfm-space-12);
}
.knowledge__eyebrow {
  margin: 0 0 var(--hfm-space-4);
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.4em;
  color: var(--hfm-color-heritage);
}
.knowledge__no {
  color: var(--hfm-color-text-muted);
  margin-right: 0.5em;
}
.knowledge__title {
  margin: 0 0 var(--hfm-space-4);
  font-family: var(--hfm-font-heading);
  font-weight: 500;
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  line-height: var(--hfm-leading-tight);
  color: var(--hfm-color-text);
}
.knowledge__lede {
  margin: 0;
  font-size: var(--hfm-text-lg);
  line-height: var(--hfm-leading-normal);
  color: var(--hfm-color-text-secondary);
}

/* register */
.knowledge__register {
  margin: 0 0 var(--hfm-space-12);
  border-top: 1px solid var(--hfm-color-border-strong);
}
.knowledge__register-row {
  display: grid;
  grid-template-columns: 8rem 6rem 1fr;
  gap: var(--hfm-space-4);
  align-items: baseline;
  padding: var(--hfm-space-4) 0;
  border-bottom: 1px solid var(--hfm-color-border);
}
.knowledge__register-label {
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-secondary);
}
.knowledge__register-value {
  margin: 0;
  font-family: var(--hfm-font-numeric);
  font-size: var(--hfm-text-xl);
  color: var(--hfm-color-text);
}
.knowledge__register-note {
  margin: 0;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

/* categories */
.knowledge__categories {
  list-style: none;
  margin: 0 0 var(--hfm-space-12);
  padding: 0;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--hfm-space-6);
}
.knowledge__category {
  padding-top: var(--hfm-space-4);
  border-top: 1px solid var(--hfm-color-border);
}
.knowledge__category-title {
  margin: 0 0 var(--hfm-space-1);
  font-family: var(--hfm-font-heading);
  font-size: var(--hfm-text-lg);
  font-weight: 500;
  color: var(--hfm-color-text);
}
.knowledge__category-note {
  margin: 0;
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-muted);
}

/* foot */
.knowledge__foot {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--hfm-space-6);
  padding-top: var(--hfm-space-6);
  border-top: 1px solid var(--hfm-color-border);
}
.knowledge__types {
  margin: 0;
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-muted);
}
.knowledge__types-label {
  margin-right: var(--hfm-space-3);
  letter-spacing: 0.2em;
}
.knowledge__cta {
  min-height: 24px;
  display: inline-flex;
  align-items: center;
  gap: var(--hfm-space-2);
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.1em;
  color: var(--hfm-color-accent);
  text-decoration: none;
}
.knowledge__cta-arr {
  transition: transform 0.18s ease;
}
.knowledge__cta:hover .knowledge__cta-arr {
  transform: translateX(3px);
}

@media (max-width: 1023px) {
  .knowledge__categories {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 599px) {
  .knowledge {
    padding: var(--hfm-space-16) var(--hfm-space-4);
  }
  .knowledge__register-row {
    grid-template-columns: 1fr;
    gap: var(--hfm-space-1);
  }
  .knowledge__categories {
    grid-template-columns: 1fr;
  }
}
</style>

<script setup lang="ts">
/**
 * HomeEvidenceSection — homepage Section 05 (史料证据 / Evidence S5-C).
 *
 * CF-07 STRUCTURAL SHELL ONLY. Semantic <section id="home-evidence"> root +
 * h2 + ONE real scholarly witness (the 房玄龄等《晋书》 quotation from
 * HOME_QUOTATION) + claim/出处/争议 honesty + a source register derived from
 * the real 其传 · 史料来源整理 document (reader/qichuan section headings).
 * Nothing is invented: the dispute (建安/正始 两说) is the one documented in
 * that same real document. No final visual fidelity — that belongs to the
 * visual work packages.
 */
import { HOME_EVIDENCE, HOME_CHAPTERS } from '../../data/homeProjection'

defineOptions({ name: 'HomeEvidenceSection' })

const quotation = HOME_EVIDENCE.quotation
</script>

<template>
  <section
    id="home-evidence"
    class="home-section home-section--evidence"
    aria-labelledby="home-evidence-title"
  >
    <p class="hfm-eyebrow">
      <span class="home-chapter__no">{{ HOME_CHAPTERS.evidence.no }}</span
      >{{ HOME_CHAPTERS.evidence.label }}
    </p>
    <h2 id="home-evidence-title" class="home-section__title">
      {{ HOME_EVIDENCE.headline }}
    </h2>
    <p class="home-section__lede">
      {{ HOME_EVIDENCE.lede }}
    </p>

    <div class="home-evidence__arg" aria-label="论证示例：结论 → 出处 → 争议">
      <p class="home-evidence__claim">
        <span class="home-evidence__tag">{{ HOME_EVIDENCE.claim.label }}</span>
        <strong>{{ HOME_EVIDENCE.claim.text }}</strong>
        <span class="home-evidence__note">{{ HOME_EVIDENCE.claim.note }}</span>
      </p>

      <blockquote class="home-quote">
        <p class="home-quote__text">
          {{ quotation.text }}
        </p>
        <cite class="home-quote__source">
          {{ HOME_EVIDENCE.sourceLabel }} · {{ quotation.attribution }} — {{ quotation.source }}
        </cite>
      </blockquote>

      <p class="home-evidence__dispute">
        <span class="home-evidence__tag">{{ HOME_EVIDENCE.dispute.label }}</span>
        <strong>{{ HOME_EVIDENCE.dispute.text }}</strong>
        <span class="home-evidence__note">{{ HOME_EVIDENCE.dispute.note }}</span>
      </p>
    </div>

    <div class="home-evidence__sources" aria-label="出处类型 · 录自其传史料来源整理">
      <p class="home-evidence__sources-k">出处类型</p>
      <ul class="home-evidence__sources-list">
        <li v-for="source in HOME_EVIDENCE.sources" :key="source.title">
          <a :href="source.href">{{ source.title }}</a>
        </li>
      </ul>
    </div>

    <p class="home-cta-row">
      <a class="home-cta" :href="HOME_EVIDENCE.cta.href">{{ HOME_EVIDENCE.cta.label }} →</a>
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

.home-section--evidence {
  padding: var(--hfm-space-12) var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
}

.home-evidence__arg {
  margin: var(--hfm-space-4) 0;
}

.home-evidence__claim,
.home-evidence__dispute {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-3);
  align-items: baseline;
  margin: 0 0 var(--hfm-space-4);
}

.home-evidence__tag {
  font-weight: 600;
  color: var(--hfm-color-heritage);
}

.home-evidence__note {
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
}

.home-quote {
  margin: 0 0 var(--hfm-space-4);
  padding: var(--hfm-space-4) var(--hfm-space-5);
  border-left: 3px solid var(--hfm-color-citation);
  background: var(--hfm-color-surface);
  border-radius: var(--hfm-radius-sm);
}

.home-quote__text {
  margin: 0 0 var(--hfm-space-2);
  font-family: var(--hfm-font-serif);
  line-height: var(--hfm-leading-reading);
}

.home-quote__source {
  display: block;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
  font-style: normal;
}

.home-evidence__sources {
  margin: var(--hfm-space-4) 0;
}

.home-evidence__sources-k {
  margin: 0 0 var(--hfm-space-2);
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
  letter-spacing: 0.08em;
}

.home-evidence__sources-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--hfm-space-1);
}

.home-evidence__sources-list li {
  padding: var(--hfm-space-1) 0;
  border-top: 1px solid var(--hfm-color-border);
}

.home-evidence__sources-list a {
  text-decoration: none;
}

.home-evidence__sources-list a:hover {
  text-decoration: underline;
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

<script setup lang="ts">
/**
 * HomeEvidenceSection — homepage Section 05 (史料证据 / evidence).
 *
 * REDESIGN: the evidence ledger — an editorial head; the claim beside its
 * honestly-stated dispute; a real attributed 《晋书》 quotation; the source
 * register derived from the qichuan document; a 《后论》 CTA.
 *
 * CONTRACT PRESERVED (ui03_home.spec.ts): <section id="home-evidence"> with the
 * single H2 「每一个结论，都回到它的出处。」; real /reader/qichuan and
 * /reader/houlun routes; no <footer> element anywhere on the homepage.
 */
import { HOME_EVIDENCE, HOME_CHAPTERS } from '../../data/homeProjection'

defineOptions({ name: 'HomeEvidenceSection' })
</script>

<template>
  <section id="home-evidence" class="evidence" aria-labelledby="home-evidence-title">
    <div class="evidence__inner">
      <header class="evidence__head">
        <p class="evidence__eyebrow">
          <span class="evidence__no">{{ HOME_CHAPTERS.evidence.no }}</span
          >{{ HOME_CHAPTERS.evidence.label }}
        </p>
        <h2 id="home-evidence-title" class="evidence__title">{{ HOME_EVIDENCE.headline }}</h2>
        <p class="evidence__lede">{{ HOME_EVIDENCE.lede }}</p>
      </header>

      <div class="evidence__ledger">
        <div class="evidence__cell evidence__cell--claim">
          <p class="evidence__cell-label">{{ HOME_EVIDENCE.claim.label }}</p>
          <p class="evidence__cell-text">{{ HOME_EVIDENCE.claim.text }}</p>
          <p class="evidence__cell-note">{{ HOME_EVIDENCE.claim.note }}</p>
        </div>
        <div class="evidence__cell evidence__cell--dispute">
          <p class="evidence__cell-label">{{ HOME_EVIDENCE.dispute.label }}</p>
          <p class="evidence__cell-text">{{ HOME_EVIDENCE.dispute.text }}</p>
          <p class="evidence__cell-note">{{ HOME_EVIDENCE.dispute.note }}</p>
        </div>
      </div>

      <blockquote class="evidence__quote">
        <p class="evidence__quote-text">{{ HOME_EVIDENCE.quotation.text }}</p>
        <p class="evidence__quote-src">
          —— {{ HOME_EVIDENCE.quotation.attribution }} ·
          <cite class="evidence__quote-cite">{{ HOME_EVIDENCE.quotation.source }}</cite>
        </p>
      </blockquote>

      <div class="evidence__foot">
        <div class="evidence__sources">
          <p class="evidence__sources-label">{{ HOME_EVIDENCE.sourceLabel }}</p>
          <ul class="evidence__sources-list">
            <li v-for="source in HOME_EVIDENCE.sources" :key="source.title">
              <a class="evidence__source-link" :href="source.href">{{ source.title }}</a>
            </li>
          </ul>
        </div>
        <a class="home-evidence__act evidence__cta" :href="HOME_EVIDENCE.cta.href">
          {{ HOME_EVIDENCE.cta.label }} <span class="home-evidence__act-arr evidence__cta-arr" aria-hidden="true">→</span>
        </a>
      </div>
    </div>
  </section>
</template>

<style scoped>
.evidence {
  background: var(--hfm-color-canvas);
  padding: var(--hfm-space-24) var(--hfm-space-6);
}
.evidence__inner {
  max-width: var(--hfm-content-max);
  margin: 0 auto;
}
.evidence__head {
  max-width: 44rem;
  margin-bottom: var(--hfm-space-12);
}
.evidence__eyebrow {
  margin: 0 0 var(--hfm-space-4);
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.4em;
  color: var(--hfm-color-heritage);
}
.evidence__no {
  color: var(--hfm-color-text-muted);
  margin-right: 0.5em;
}
.evidence__title {
  margin: 0 0 var(--hfm-space-4);
  font-family: var(--hfm-font-heading);
  font-weight: 500;
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  line-height: var(--hfm-leading-tight);
  color: var(--hfm-color-text);
}
.evidence__lede {
  margin: 0;
  font-size: var(--hfm-text-lg);
  line-height: var(--hfm-leading-normal);
  color: var(--hfm-color-text-secondary);
}

/* claim / dispute ledger */
.evidence__ledger {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--hfm-space-8);
  margin-bottom: var(--hfm-space-12);
}
.evidence__cell {
  padding: var(--hfm-space-6);
  border: 1px solid var(--hfm-color-border);
  border-left-width: 3px;
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
}
.evidence__cell--claim {
  border-left-color: var(--hfm-color-evidence);
}
.evidence__cell--dispute {
  border-left-color: var(--hfm-color-warning);
}
.evidence__cell-label {
  margin: 0 0 var(--hfm-space-2);
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.24em;
  color: var(--hfm-color-text-muted);
}
.evidence__cell-text {
  margin: 0 0 var(--hfm-space-2);
  font-family: var(--hfm-font-heading);
  font-size: var(--hfm-text-xl);
  color: var(--hfm-color-text);
}
.evidence__cell-note {
  margin: 0;
  font-size: var(--hfm-text-sm);
  line-height: var(--hfm-leading-normal);
  color: var(--hfm-color-text-muted);
}

/* quotation */
.evidence__quote {
  margin: 0 0 var(--hfm-space-12);
  padding: var(--hfm-space-8);
  background: var(--hfm-color-surface);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
}
.evidence__quote-text {
  margin: 0 0 var(--hfm-space-4);
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-lg);
  line-height: var(--hfm-leading-reading);
  color: var(--hfm-color-text);
}
.evidence__quote-src {
  margin: 0;
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-muted);
}
.evidence__quote-cite {
  font-style: normal;
  color: var(--hfm-color-citation);
}

/* sources + cta */
.evidence__foot {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--hfm-space-8);
  padding-top: var(--hfm-space-6);
  border-top: 1px solid var(--hfm-color-border);
}
.evidence__sources-label {
  margin: 0 0 var(--hfm-space-3);
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.14em;
  color: var(--hfm-color-text-muted);
}
.evidence__sources-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-4);
}
.evidence__source-link {
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-secondary);
  text-decoration: none;
  border-bottom: 1px solid var(--hfm-color-border-strong);
}
.evidence__source-link:hover {
  color: var(--hfm-color-accent);
  border-color: var(--hfm-color-accent);
}
.evidence__cta {
  min-height: 24px;
  display: inline-flex;
  align-items: center;
  gap: var(--hfm-space-2);
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.1em;
  color: var(--hfm-color-accent);
  text-decoration: none;
}
.evidence__cta-arr {
  transition: transform 0.18s ease;
}
.evidence__cta:hover .evidence__cta-arr {
  transform: translateX(3px);
}
@media (max-width: 1023px) {
  .evidence__ledger {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 599px) {
  .evidence {
    padding: var(--hfm-space-16) var(--hfm-space-4);
  }
}
</style>

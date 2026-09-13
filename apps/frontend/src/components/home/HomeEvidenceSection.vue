<script setup lang="ts">
/**
 * HomeEvidenceSection — Section 05 (史料证据). 《刻度》 ledger voice:
 * the claim set beside its honestly-stated dispute, the real attributed
 * 《晋书》 witness, and the source register drawn from the qichuan document.
 */
import { HOME_EVIDENCE, HOME_CHAPTERS } from '../../data/homeProjection'

defineOptions({ name: 'HomeEvidenceSection' })
</script>

<template>
  <section id="home-evidence" class="xl-sec" aria-labelledby="home-evidence-title">
    <div class="xl-inner">
      <header class="xl-head">
        <div class="xl-head__aside">
          <span class="xl-index">{{ HOME_CHAPTERS.evidence.no }}</span>
          <span class="xl-label">Evidence</span>
        </div>
        <div>
          <h2 id="home-evidence-title" class="xl-title">{{ HOME_EVIDENCE.headline }}</h2>
          <p class="xl-lede">{{ HOME_EVIDENCE.lede }}</p>
        </div>
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
          <p class="evidence__sources-label xl-label">{{ HOME_EVIDENCE.sourceLabel }}</p>
          <ul class="evidence__sources-list">
            <li v-for="source in HOME_EVIDENCE.sources" :key="source.title">
              <a class="evidence__source-link" :href="source.href">{{ source.title }}</a>
            </li>
          </ul>
        </div>
        <a class="home-evidence__act evidence__cta xl-go" :href="HOME_EVIDENCE.cta.href">
          {{ HOME_EVIDENCE.cta.label }}
          <span class="home-evidence__act-arr evidence__cta-arr xl-go__arr" aria-hidden="true"
            >→</span
          >
        </a>
      </div>
    </div>
  </section>
</template>

<style scoped>
.evidence__ledger {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--hfm-space-6);
  margin-bottom: var(--hfm-space-8);
}
.evidence__cell {
  padding: var(--hfm-space-6);
  border: 1px solid var(--wl-rule);
  border-top-width: 3px;
  background: var(--wl-light);
}
.evidence__cell--claim {
  border-top-color: var(--wl-ink);
}
.evidence__cell--dispute {
  border-top-color: var(--wl-mark);
}
.evidence__cell-label {
  margin: 0 0 var(--hfm-space-2);
  font-family: var(--wl-latin);
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.24em;
  color: var(--wl-mute);
}
.evidence__cell-text {
  margin: 0 0 var(--hfm-space-2);
  font-family: var(--hfm-font-heading);
  font-size: var(--hfm-text-2xl);
  color: var(--wl-ink);
}
.evidence__cell-note {
  margin: 0;
  font-size: var(--hfm-text-sm);
  line-height: 1.85;
  color: var(--wl-ink-2);
}
.evidence__quote {
  margin: 0 0 var(--hfm-space-8);
  padding: var(--hfm-space-8) 0;
  border-top: 1px solid var(--wl-rule);
  border-bottom: 1px solid var(--wl-rule);
}
.evidence__quote-text {
  margin: 0 0 var(--hfm-space-4);
  max-width: 44ch;
  font-family: var(--hfm-font-serif);
  font-size: clamp(1.125rem, 2vw, 1.5rem);
  line-height: 2;
  color: var(--wl-ink);
}
.evidence__quote-src {
  margin: 0;
  font-size: var(--hfm-text-sm);
  color: var(--wl-mute);
}
.evidence__quote-cite {
  font-style: normal;
  color: var(--wl-mark);
}
.evidence__foot {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--hfm-space-8);
}
.evidence__sources-label {
  margin: 0 0 var(--hfm-space-3);
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
  color: var(--wl-ink-2);
  text-decoration: none;
  border-bottom: 1px solid var(--wl-rule);
}
.evidence__source-link:hover {
  color: var(--wl-mark);
  border-color: var(--wl-mark);
}
@media (max-width: 900px) {
  .evidence__ledger {
    grid-template-columns: 1fr;
  }
}
</style>

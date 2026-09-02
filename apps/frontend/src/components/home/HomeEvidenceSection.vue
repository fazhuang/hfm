<script setup lang="ts">
/**
 * HomeEvidenceSection — accepted homepage Section 05 (Evidence S5-C Refined).
 *
 * WP-02A STRUCTURAL SHELL ONLY. Semantic root + h2 + authoritative quotation
 * (房玄龄《晋书》 — no fabrication) + source register + claim↔dispute honesty.
 * No final visual fidelity (no nested 01/02/03 argument absolute geometry,
 * no fixed 1240 height) — that belongs to WP-04.
 */
import { HOME_EVIDENCE, HOME_CHAPTERS } from '../../data/homeProjection'

defineOptions({ name: 'HomeEvidenceSection' })
</script>

<template>
  <section
    id="home-evidence"
    class="home-section home-section--evidence"
    aria-labelledby="home-evidence-title"
  >
    <p class="home-eyebrow">
      <span class="home-eyebrow__no">{{ HOME_CHAPTERS.evidence.no }}</span
      >{{ HOME_CHAPTERS.evidence.label }}
    </p>
    <h2 id="home-evidence-title" class="home-section__title">{{ HOME_EVIDENCE.headline }}</h2>

    <blockquote class="home-quote">
      <p class="home-quote__text">{{ HOME_EVIDENCE.quotation.text }}</p>
      <cite class="home-quote__source"
        >{{ HOME_EVIDENCE.quotation.attribution }} — {{ HOME_EVIDENCE.quotation.source }}</cite
      >
    </blockquote>

    <div class="home-evidence__claim">
      <p class="home-evidence__conclusion">生卒年 {{ HOME_EVIDENCE.claim.number }}</p>
      <p class="home-evidence__note">{{ HOME_EVIDENCE.claim.note }}</p>
      <p class="home-evidence__dispute">{{ HOME_EVIDENCE.dispute }}</p>
    </div>

    <div class="home-evidence__sources" aria-label="出处类型 · 录自其传史料来源整理">
      <p v-for="source in HOME_EVIDENCE.sources" :key="source.title" class="home-evidence__source">
        <span class="home-evidence__source-title">{{ source.title }}</span>
        <span class="home-evidence__source-note">{{ source.note }}</span>
      </p>
    </div>

    <p class="home-cta-row">
      <a class="home-cta" :href="HOME_EVIDENCE.cta.href">{{ HOME_EVIDENCE.cta.label }} →</a>
    </p>
  </section>
</template>

<style scoped>
/* WP-02A STRUCTURAL SHELL ONLY. */
.home-section--evidence {
  padding: var(--hfm-space-12) var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
}
.home-quote__source {
  display: block;
  margin-top: var(--hfm-space-3);
  color: var(--hfm-color-text-secondary);
}
.home-evidence__sources {
  margin: var(--hfm-space-5) 0;
}
.home-evidence__source {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-3);
  padding: var(--hfm-space-2) 0;
  border-top: 1px solid var(--hfm-color-border);
}
.home-evidence__source-note,
.home-evidence__note,
.home-evidence__dispute {
  color: var(--hfm-color-text-muted);
}
</style>

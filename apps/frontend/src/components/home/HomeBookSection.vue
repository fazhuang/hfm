<script setup lang="ts">
/**
 * HomeBookSection — accepted homepage Section 03 (Book B1 Refined).
 *
 * WP-02A STRUCTURAL SHELL ONLY. Semantic root + h2 + book object + edition
 * preview + lineage data-status line (DATA-GAP honesty preserved). No final
 * visual fidelity (no monumental 150px title, no manuscript counterweight
 * asset, no fixed 1200 height) — that belongs to WP-03.
 */
import { HOME_BOOK, HOME_CHAPTERS, HOME_EDITIONS_TOTAL } from '../../data/homeProjection'
import {
  presentationStatusLabel,
  resolvePresentationState,
  type PresentationState,
} from '../../presentation/stateMapping'

defineOptions({ name: 'HomeBookSection' })

/* UX2-P5 P1-01: lineage relation state routes through the shared P0 G1-C
 * mapping (no local mapping, no template literals for data-status/label). */
const lineageState: PresentationState = resolvePresentationState({ contentStatus: 'DATA_GAP' })
const lineageLabel = presentationStatusLabel(lineageState, '版本关系整理中')
</script>

<template>
  <section id="home-book" class="home-section home-section--book" aria-labelledby="home-book-title">
    <p class="home-eyebrow">
      <span class="home-eyebrow__no">{{ HOME_CHAPTERS.book.no }}</span
      >{{ HOME_CHAPTERS.book.label }}
    </p>
    <h2 id="home-book-title" class="home-section__title">{{ HOME_BOOK.headline }}</h2>
    <p class="home-section__lede">{{ HOME_BOOK.book.lede }}</p>

    <p class="home-book__name">{{ HOME_BOOK.book.heading }}</p>
    <p class="home-book__note">版本记录 {{ HOME_EDITIONS_TOTAL }} 条</p>

    <figure class="home-lineage" aria-label="版本脉络">
      <img :src="HOME_BOOK.book.lineage.src" :alt="HOME_BOOK.book.lineage.alt" />
      <figcaption class="home-lineage__caption">
        版本脉络（客户资料）· 结构化版本关系整理中（DATA-GAP）
        <span class="hfm-status" :data-status="lineageState">{{ lineageLabel }}</span>
      </figcaption>
    </figure>

    <ul class="home-editions" aria-label="代表版本">
      <li v-for="edition in HOME_BOOK.book.editions" :key="edition.title" class="home-edition">
        <span class="home-edition__title">{{ edition.title }}</span>
        <span class="home-edition__period">{{ edition.period }}</span>
      </li>
    </ul>

    <p class="home-cta-row">
      <a class="home-cta" :href="HOME_BOOK.cta.href">{{ HOME_BOOK.cta.label }} →</a>
    </p>
  </section>
</template>

<style scoped>
/* WP-02A STRUCTURAL SHELL ONLY. */
.home-section--book {
  padding: var(--hfm-space-12) var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
}
.home-book__meta {
  margin: var(--hfm-space-4) 0;
}
.home-lineage img {
  max-width: 100%;
  height: auto;
}
.home-editions {
  list-style: none;
  padding: 0;
  margin: var(--hfm-space-4) 0;
}
.home-edition {
  display: flex;
  gap: var(--hfm-space-3);
  padding: var(--hfm-space-2) 0;
  border-top: 1px solid var(--hfm-color-border);
}
</style>

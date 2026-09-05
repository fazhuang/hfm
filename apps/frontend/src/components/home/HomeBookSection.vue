<script setup lang="ts">
/**
 * HomeBookSection — homepage Section 03 (一部书 / Book B1).
 *
 * CF-07 STRUCTURAL SHELL ONLY. Semantic <section id="home-book"> root + h2 +
 * the book object (HOME_JIAYI) with its edition preview and the honest
 * lineage data-status caption (DATA-GAP is preserved verbatim — it is the
 * accepted homepage transparency line and the E2E contract). No final visual
 * fidelity (no monumental title geometry / manuscript counterweight) — that
 * belongs to the visual work packages.
 */
import { HOME_BOOK, HOME_CHAPTERS } from '../../data/homeProjection'

defineOptions({ name: 'HomeBookSection' })

const book = HOME_BOOK.book
const editions = book.editions
</script>

<template>
  <section id="home-book" class="home-section home-section--book" aria-labelledby="home-book-title">
    <p class="hfm-eyebrow">
      <span class="home-chapter__no">{{ HOME_CHAPTERS.book.no }}</span
      >{{ HOME_CHAPTERS.book.label }}
    </p>
    <h2 id="home-book-title" class="home-section__title">
      {{ HOME_BOOK.headline }}
    </h2>
    <p class="home-section__lede">
      {{ book.lede }}
    </p>

    <p class="home-book__name">
      {{ book.heading }}
    </p>
    <p class="home-book__note">版本记录 {{ HOME_BOOK.editionsTotal }} 条（据客户资料审计）</p>

    <figure class="home-lineage" aria-label="版本脉络">
      <img class="home-lineage__img" :src="book.lineage.src" :alt="book.lineage.alt" />
      <figcaption class="home-lineage__caption">
        {{ HOME_BOOK.lineageCaption }}
      </figcaption>
    </figure>

    <ul class="home-book__editions" aria-label="代表版本">
      <li v-for="edition in editions" :key="edition.title" class="home-book__edition">
        <span class="home-book__edition-title">{{ edition.title }}</span>
        <span class="home-book__edition-period">{{ edition.period }}</span>
      </li>
    </ul>

    <p class="home-cta-row">
      <a class="home-cta" :href="HOME_BOOK.cta.href">{{ HOME_BOOK.cta.label }} →</a>
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

.home-section--book {
  padding: var(--hfm-space-12) var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
}

.home-book__name {
  font-family: var(--hfm-font-display);
  font-size: var(--hfm-text-2xl);
  margin: var(--hfm-space-4) 0 var(--hfm-space-2);
}

.home-book__note {
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
  margin: 0 0 var(--hfm-space-4);
}

.home-lineage {
  margin: 0 0 var(--hfm-space-5);
  max-width: 52rem;
}

.home-lineage__img {
  display: block;
  max-width: 100%;
  height: auto;
}

.home-lineage__caption {
  margin-top: var(--hfm-space-2);
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.home-book__editions {
  list-style: none;
  margin: 0;
  padding: 0;
}

.home-book__edition {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-3);
  justify-content: space-between;
  padding: var(--hfm-space-2) 0;
  border-top: 1px solid var(--hfm-color-border);
}

.home-book__edition-period {
  color: var(--hfm-color-heritage);
  font-size: var(--hfm-text-sm);
  font-variant-numeric: tabular-nums;
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

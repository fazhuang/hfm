<script setup lang="ts">
/**
 * HomeBookSection — homepage Section 03 (一部书 / the book as object).
 *
 * REDESIGN: the book as a documentary object — an editorial head, a two-column
 * body (book-leaf specimen + metadata/lineage), and a 古籍库 CTA. The lineage
 * caption honestly states 结构化版本关系整理中（DATA-GAP）.
 *
 * CONTRACT PRESERVED (ui03_home.spec.ts): <section id="home-book"> with the
 * single H2 「一部书，成为历史中的物。」; the section text carries 版本记录,
 * the audited edition count (contentInventory single source) and DATA-GAP; the
 * real /jiayi route; the edition-lineage.png + book-siku-leaf.jpg assets.
 */
import { HOME_BOOK, HOME_CHAPTERS } from '../../data/homeProjection'
import { INVENTORY_EDITION_RECORDS } from '../../data/contentInventory'

defineOptions({ name: 'HomeBookSection' })
</script>

<template>
  <section id="home-book" class="book" aria-labelledby="home-book-title">
    <div class="book__inner">
      <header class="book__head">
        <p class="book__eyebrow">
          <span class="book__no">{{ HOME_CHAPTERS.book.no }}</span>{{ HOME_CHAPTERS.book.label }}
        </p>
        <h2 id="home-book-title" class="book__title">{{ HOME_BOOK.headline }}</h2>
        <p class="book__lede">{{ HOME_BOOK.book.lede }}</p>
      </header>

      <div class="book__grid">
        <figure class="book__leaf">
          <img src="/assets/jiayi/book-siku-leaf.jpg" alt="" aria-hidden="true" />
          <figcaption class="home-book__title-glyphs book__leaf-cap">{{ HOME_BOOK.book.heading }}</figcaption>
        </figure>

        <div class="book__body">
          <div class="book__meta">
            <p class="book__meta-row">
              <span class="book__meta-line"
                ><b>版本记录</b> {{ INVENTORY_EDITION_RECORDS }} 条</span
              >
              <span class="book__meta-note">据客户资料目录审计</span>
            </p>
            <p class="book__meta-row">
              <span class="book__meta-line"><b>收录版本</b> {{ HOME_BOOK.editionsTotal }} 种</span>
              <span class="book__meta-note">平台已著录（历代刊本 / 近现代整理本）</span>
            </p>
          </div>

          <figure class="book__lineage">
            <img
              class="book__lineage-img"
              :src="HOME_BOOK.book.lineage.src"
              :alt="HOME_BOOK.book.lineage.alt"
            />
            <figcaption class="book__lineage-cap">{{ HOME_BOOK.lineageCaption }}</figcaption>
          </figure>

          <a class="home-book__act book__cta" :href="HOME_BOOK.cta.href">
            {{ HOME_BOOK.cta.label }} <span class="home-book__act-arr book__cta-arr" aria-hidden="true">→</span>
          </a>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.book {
  background: var(--hfm-color-canvas);
  padding: var(--hfm-space-24) var(--hfm-space-6);
}
.book__inner {
  max-width: var(--hfm-content-max);
  margin: 0 auto;
}
.book__head {
  max-width: 44rem;
  margin-bottom: var(--hfm-space-16);
}
.book__eyebrow {
  margin: 0 0 var(--hfm-space-4);
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.4em;
  color: var(--hfm-color-heritage);
}
.book__no {
  color: var(--hfm-color-text-muted);
  margin-right: 0.5em;
}
.book__title {
  margin: 0 0 var(--hfm-space-4);
  font-family: var(--hfm-font-heading);
  font-weight: 500;
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  line-height: var(--hfm-leading-tight);
  color: var(--hfm-color-text);
}
.book__lede {
  margin: 0;
  font-size: var(--hfm-text-lg);
  line-height: var(--hfm-leading-normal);
  color: var(--hfm-color-text-secondary);
}
.book__grid {
  display: grid;
  grid-template-columns: minmax(0, 0.85fr) minmax(0, 1.15fr);
  gap: var(--hfm-space-16);
  align-items: start;
}
.book__leaf {
  margin: 0;
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  overflow: hidden;
  background: var(--hfm-color-surface);
}
.book__leaf img {
  display: block;
  width: 100%;
  height: auto;
  filter: sepia(0.14) saturate(0.9) contrast(1.02);
}
.book__leaf-cap {
  padding: var(--hfm-space-3) var(--hfm-space-4);
  border-top: 1px solid var(--hfm-color-border);
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-secondary);
}
.book__body {
  min-width: 0;
}
.book__meta {
  margin: 0 0 var(--hfm-space-8);
}
.book__meta-row {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--hfm-space-4);
  margin: 0;
  padding: var(--hfm-space-4) 0;
  border-top: 1px solid var(--hfm-color-border);
}
.book__meta-line {
  font-family: var(--hfm-font-numeric);
  font-size: var(--hfm-text-xl);
  color: var(--hfm-color-text);
}
.book__meta-line b {
  font-weight: 500;
}
.book__meta-note {
  font-family: var(--hfm-font-sans);
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}
.book__lineage {
  margin: 0 0 var(--hfm-space-8);
}
.book__lineage-img {
  display: block;
  width: 100%;
  height: auto;
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
}
.book__lineage-cap {
  margin-top: var(--hfm-space-2);
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-warning);
}
.book__cta {
  display: inline-flex;
  align-items: center;
  gap: var(--hfm-space-2);
  padding: var(--hfm-space-3) var(--hfm-space-6);
  border: 1px solid var(--hfm-color-accent);
  border-radius: var(--hfm-radius-sm);
  color: var(--hfm-color-accent);
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.1em;
  text-decoration: none;
  transition: background 0.18s ease, color 0.18s ease;
}
.book__cta:hover {
  background: var(--hfm-color-accent);
  color: var(--hfm-color-on-accent);
}
.book__cta-arr {
  transition: transform 0.18s ease;
}
.book__cta:hover .book__cta-arr {
  transform: translateX(3px);
}
@media (max-width: 1023px) {
  .book__grid {
    grid-template-columns: 1fr;
    gap: var(--hfm-space-12);
  }
  .book__leaf {
    max-width: 28rem;
  }
}
@media (max-width: 599px) {
  .book {
    padding: var(--hfm-space-16) var(--hfm-space-4);
  }
}
</style>

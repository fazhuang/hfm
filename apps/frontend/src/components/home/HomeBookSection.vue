<script setup lang="ts">
/**
 * HomeBookSection — Section 03 (一部书). 《刻度》 ledger voice:
 * the book as a catalogued object — ruled header, specimen leaf, the audited
 * edition register (DATA-GAP honest) and the lineage plate.
 */
import { computed } from 'vue'
import { HOME_BOOK, HOME_CHAPTERS } from '../../data/homeProjection'
import { INVENTORY_EDITION_RECORDS } from '../../data/contentInventory'
import type { BlockData } from '../../composables/useHomeContractData'
import type { EditionSummary, WorkDetail } from '../../types/public'

defineOptions({ name: 'HomeBookSection' })

const props = defineProps<{
  work?: BlockData<WorkDetail> | null
  editions?: BlockData<EditionSummary[]> | null
}>()

/** T0 — the real published work + its edition count. */
const t0 = computed(() => {
  if (props.work?.source !== 'backend' || !props.work.data) return null
  return {
    title: props.work.data.title,
    category: props.work.data.category,
    editions: props.editions?.data?.length ?? 0,
  }
})
</script>

<template>
  <section id="home-book" class="xl-sec" aria-labelledby="home-book-title" :data-source="t0 ? 'backend' : 'fallback'">
    <div class="xl-inner">
      <header class="xl-head">
        <div class="xl-head__aside">
          <span class="xl-index">{{ HOME_CHAPTERS.book.no }}</span>
          <span class="xl-label">The Book</span>
        </div>
        <div>
          <h2 id="home-book-title" class="xl-title">{{ HOME_BOOK.headline }}</h2>
          <p class="xl-lede">{{ HOME_BOOK.book.lede }}</p>
        </div>
      </header>

      <!-- T0 — real published work + edition count -->
      <div v-if="t0" class="book__t0" data-source="backend">
        <p class="book__t0-row">
          <span class="book__meta-line"><b>著作</b> {{ t0.title }}</span>
          <span class="book__meta-note">{{ t0.category ?? '' }}</span>
        </p>
        <p class="book__t0-row">
          <span class="book__meta-line"><b>已发布版本</b> {{ t0.editions }} 种</span>
          <span class="book__meta-note">来自数据库（已发布投影）</span>
        </p>
      </div>
      <p v-else class="fallback-note" data-fallback-note>
        数据库作品投影暂不可用 · 以下为离线兜底（客户材料）
      </p>

      <div class="book__grid">
        <figure class="book__leaf">
          <img src="/assets/jiayi/book-siku-leaf.jpg" alt="" aria-hidden="true" />
          <figcaption class="home-book__title-glyphs book__leaf-cap">
            {{ HOME_BOOK.book.heading }}
          </figcaption>
        </figure>

        <div class="book__body">
          <p class="book__meta-row">
            <span class="book__meta-line"><b>版本记录</b> {{ INVENTORY_EDITION_RECORDS }} 条</span>
            <span class="book__meta-note">据客户资料目录审计</span>
          </p>
          <p class="book__meta-row">
            <span class="book__meta-line"><b>收录版本</b> {{ HOME_BOOK.editionsTotal }} 种</span>
            <span class="book__meta-note">平台已著录（历代刊本 / 近现代整理本）</span>
          </p>

          <figure class="book__lineage">
            <img
              class="book__lineage-img"
              :src="HOME_BOOK.book.lineage.src"
              :alt="HOME_BOOK.book.lineage.alt"
            />
            <figcaption class="book__lineage-cap">{{ HOME_BOOK.lineageCaption }}</figcaption>
          </figure>

          <a class="home-book__act book__cta xl-go" :href="HOME_BOOK.cta.href">
            {{ HOME_BOOK.cta.label }}
            <span class="home-book__act-arr book__cta-arr xl-go__arr" aria-hidden="true">→</span>
          </a>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.book__t0 {
  margin-bottom: var(--hfm-space-8);
}
.book__t0-row {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--hfm-space-4);
  margin: 0;
  padding: var(--hfm-space-3) 0;
  border-top: 1px solid var(--wl-rule);
}
.book__grid {
  display: grid;
  grid-template-columns: minmax(0, 0.8fr) minmax(0, 1.2fr);
  gap: clamp(2rem, 5vw, 4rem);
  align-items: start;
}
.book__leaf {
  margin: 0;
  border: 1px solid var(--wl-rule);
  overflow: hidden;
  background: var(--wl-light);
}
.book__leaf img {
  display: block;
  width: 100%;
  height: auto;
  filter: sepia(0.12) saturate(0.85) contrast(1.02);
}
.book__leaf-cap {
  padding: var(--hfm-space-3) var(--hfm-space-4);
  border-top: 1px solid var(--wl-rule);
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-sm);
  color: var(--wl-ink);
}
.book__body {
  min-width: 0;
}
.book__meta-row {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--hfm-space-4);
  margin: 0;
  padding: var(--hfm-space-4) 0;
  border-top: 1px solid var(--wl-rule);
}
.book__meta-line {
  font-family: var(--wl-latin);
  font-variant-numeric: tabular-nums;
  font-size: var(--hfm-text-2xl);
  color: var(--wl-ink);
}
.book__meta-line b {
  font-family: var(--hfm-font-sans);
  font-size: var(--hfm-text-sm);
  font-weight: 500;
  letter-spacing: 0.1em;
  color: var(--wl-mark);
  margin-right: var(--hfm-space-3);
}
.book__meta-note {
  font-size: var(--hfm-text-xs);
  color: var(--wl-mute);
}
.book__lineage {
  margin: var(--hfm-space-8) 0;
}
.book__lineage-img {
  display: block;
  width: 100%;
  height: auto;
  border: 1px solid var(--wl-rule);
}
.book__lineage-cap {
  margin-top: var(--hfm-space-2);
  font-size: var(--hfm-text-xs);
  color: var(--wl-mark);
}
@media (max-width: 900px) {
  .book__grid {
    grid-template-columns: 1fr;
  }
  .book__leaf {
    max-width: 26rem;
  }
}
</style>

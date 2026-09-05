<script setup lang="ts">
/**
 * HomeBookSection — homepage Section 03 (一部书 / Book B1, refined).
 *
 * CF-08: production visual fidelity for the accepted
 * HFM_HOMEPAGE_SECTION03_VISUAL_BASELINE_B1_REFINED composition (1440×1200).
 * Concept: THE BOOK AS MONUMENT — 一部书，成为历史中的物，with scholarly context
 * and an entry into the work/edition material.
 *  - header: 03 eyebrow · jump 人 → 著作 · monumental 《针灸甲乙经》 + quiet metadata
 *  - narrative block (h2) + supporting copy
 *  - ONE editorial action 进入古籍库 →
 *  - quiet evidence register (版本记录 19 · 论著资料 92 · 学术论文 515) + version
 *    provenance chain + lineage image with honest DATA-GAP caption
 *  - manuscript counterweight (book-siku-leaf.jpg) breaking TOP + RIGHT (decorative)
 *
 * DOMAIN SEMANTICS (CF-04): the home projection keeps WORK / EDITION /
 * BIBLIOGRAPHIC RECORD distinct — the "版本记录" register and the edition-chain
 * are EDITION counts, never a claim of 19 independent works; the book itself is
 * the single WORK object.
 */
import { HOME_BOOK, HOME_CHAPTERS, HOME_EDITIONS_TOTAL } from '../../data/homeProjection'
import { INVENTORY_LUNZHU_FILES, INVENTORY_LUNWEN_FILES } from '../../data/contentInventory'

defineOptions({ name: 'HomeBookSection' })

const lunzhuCount = INVENTORY_LUNZHU_FILES
const lunwenCount = INVENTORY_LUNWEN_FILES
const versions = HOME_BOOK.book.editions
</script>

<template>
  <section id="home-book" class="home-section home-section--book" aria-labelledby="home-book-title">
    <div class="home-book__grain" aria-hidden="true" />
    <div class="home-book__inner">
      <!-- header -->
      <p class="home-book__eyebrow">
        <span class="home-book__no">{{ HOME_CHAPTERS.book.no }}</span
        >{{ HOME_CHAPTERS.book.label }}
      </p>
      <p class="home-book__jump">人 → 著作</p>

      <!-- monumental title + quiet metadata -->
      <div class="home-book__title">
        <p class="home-book__title-glyphs">
          {{ HOME_BOOK.book.heading }}
        </p>
        <p class="home-book__title-meta">
          <b>西晋 · 皇甫谧 编撰</b> · 十二卷 · 中国现存最早的针灸学典籍之一
        </p>
      </div>

      <!-- narrative block -->
      <div class="home-book__narr">
        <h2 id="home-book-title" class="home-book__narr-heading">
          {{ HOME_BOOK.headline }}
        </h2>
        <p class="home-book__narr-copy">
          平台收录其历代版本、版本脉络、论著与研究资料——从一种记载，到一套可读、可查、可回溯其出处的知识对象。
        </p>
      </div>

      <!-- ONE editorial action -->
      <a class="home-book__act" :href="HOME_BOOK.cta.href"
        ><span class="home-book__act-label">{{ HOME_BOOK.cta.label }}</span>
        <span class="home-book__act-arr" aria-hidden="true">→</span></a
      >

      <!-- quiet evidence + version provenance (one scholarly register) -->
      <div class="home-book__register">
        <p class="home-book__evidence">
          <span
            ><b>版本记录 {{ HOME_EDITIONS_TOTAL }}</b> 条</span
          ><span class="home-book__sep">·</span>
          <span
            ><b>论著资料 {{ lunzhuCount }}</b> 件</span
          ><span class="home-book__sep">·</span>
          <span
            ><b>学术论文 {{ lunwenCount }}</b> 篇（题录）</span
          >
        </p>
        <div class="home-book__provenance">
          <p class="home-book__prov-header"><b>版本脉络</b><span>客户资料 · 原生排版呈现</span></p>
          <p class="home-book__prov-chain">
            <template v-for="(edition, i) in versions" :key="edition.title">
              <b>{{ edition.title }}</b
              ><span v-if="i < versions.length - 1" class="home-book__chain-sep">·</span>
            </template>
            <span class="home-book__chain-tail">→ 平台数字整理</span>
          </p>
        </div>

        <!-- lineage image with honest DATA-GAP caption -->
        <figure class="home-lineage" aria-label="版本脉络">
          <img :src="HOME_BOOK.book.lineage.src" :alt="HOME_BOOK.book.lineage.alt" />
          <figcaption class="home-lineage__caption">
            {{ HOME_BOOK.lineageCaption }}
          </figcaption>
        </figure>
      </div>
    </div>

    <!-- manuscript counterweight — breaks TOP + RIGHT, LEFT dissolves (decorative) -->
    <figure class="home-book__manuscript" aria-hidden="true">
      <img src="/assets/jiayi/book-siku-leaf.jpg" alt="" />
    </figure>
    <p class="home-book__manuscript-caption" aria-hidden="true">
      <b>《针灸甲乙经》 · 四库全书本</b><br />清乾隆《四库全书》抄本 · 客户资料 · 结构化整理中
    </p>
  </section>
</template>

<style scoped>
/* ===== Section 03 Book (B1 Refined) — production fidelity, 1440×1200 ===== */
.home-section--book {
  position: relative;
  overflow: hidden;
  min-height: 1200px;
  margin-inline: calc(-1 * var(--hfm-space-6));
  background:
    radial-gradient(
      1050px 680px at 88% -8%,
      color-mix(in srgb, var(--hfm-color-heritage) 6%, transparent) 0%,
      transparent 62%
    ),
    radial-gradient(
      760px 540px at -4% 112%,
      color-mix(in srgb, var(--hfm-color-accent) 4.5%, transparent) 0%,
      transparent 60%
    ),
    var(--hfm-color-canvas);
}
.home-book__grain {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.05;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='240' height='240'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
.home-book__inner {
  position: relative;
  max-width: 1272px;
  margin: 0 auto;
  width: 100%;
  height: 100%;
}

.home-book__eyebrow {
  position: absolute;
  left: 0;
  top: 120px;
  font-size: 11px;
  letter-spacing: 0.42em;
  color: var(--hfm-color-heritage);
  margin: 0;
}
.home-book__no {
  color: var(--hfm-color-text-muted);
  margin-right: 0.5em;
}
.home-book__jump {
  position: absolute;
  right: 0;
  top: 120px;
  font-size: 12px;
  letter-spacing: 0.26em;
  color: var(--hfm-color-text-muted);
  margin: 0;
}

.home-book__title {
  position: absolute;
  left: 0;
  top: 184px;
}
.home-book__title-glyphs {
  font-family: var(--hfm-font-display);
  font-weight: 500;
  letter-spacing: 0.02em;
  line-height: 1.02;
  font-size: 150px;
  color: var(--hfm-color-text);
  margin: 0;
}
.home-book__title-meta {
  margin-top: 24px;
  font-size: 14px;
  letter-spacing: 0.2em;
  color: var(--hfm-color-text-secondary);
}
.home-book__title-meta b {
  color: var(--hfm-color-text);
  font-weight: 500;
}

.home-book__narr {
  position: absolute;
  left: 0;
  top: 492px;
  width: 640px;
}
.home-book__narr-heading {
  font-family: var(--hfm-font-heading);
  font-weight: 500;
  font-size: 36px;
  letter-spacing: 0.08em;
  color: var(--hfm-color-text);
  margin: 0;
}
.home-book__narr-copy {
  margin-top: 24px;
  font-size: 15px;
  line-height: 2.05;
  color: var(--hfm-color-text-secondary);
  max-width: 56ch;
}

.home-book__act {
  position: absolute;
  left: 0;
  top: 736px;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  font-size: 13.5px;
  letter-spacing: 0.18em;
  color: var(--hfm-color-text);
  text-decoration: none;
}
.home-book__act-arr {
  color: var(--hfm-color-accent);
  font-family: var(--hfm-font-serif);
  font-size: 15px;
}
.home-book__act-label {
  border-bottom: 1px solid var(--hfm-color-border-strong);
  padding-bottom: 4px;
}

.home-book__register {
  position: absolute;
  left: 0;
  bottom: 56px;
  width: 820px;
  border-top: 1px solid var(--hfm-color-border);
  padding-top: 24px;
}
.home-book__evidence {
  display: flex;
  align-items: baseline;
  gap: 26px;
  font-size: 12px;
  letter-spacing: 0.08em;
  color: var(--hfm-color-text-muted);
  margin: 0;
}
.home-book__evidence span {
  white-space: nowrap;
}
.home-book__evidence b {
  font-family: var(--hfm-font-display);
  font-weight: 500;
  font-size: 15px;
  color: var(--hfm-color-text-secondary);
  letter-spacing: 0.04em;
  margin-right: 6px;
}
.home-book__sep {
  color: var(--hfm-color-border-strong);
}
.home-book__prov-header {
  display: flex;
  align-items: baseline;
  gap: 14px;
  font-size: 11px;
  letter-spacing: 0.26em;
  color: var(--hfm-color-text-muted);
  margin: 26px 0 0;
}
.home-book__prov-header b {
  font-family: var(--hfm-font-display);
  font-size: 14px;
  font-weight: 500;
  color: var(--hfm-color-text);
  letter-spacing: 0.08em;
}
.home-book__prov-chain {
  margin-top: 12px;
  font-size: 12.5px;
  letter-spacing: 0.06em;
  color: var(--hfm-color-text-secondary);
  line-height: 2;
}
.home-book__prov-chain b {
  font-family: var(--hfm-font-display);
  font-weight: 500;
  color: var(--hfm-color-text);
  letter-spacing: 0.04em;
}
.home-book__chain-sep {
  margin: 0 8px;
  color: var(--hfm-color-border-strong);
}
.home-book__chain-tail {
  color: var(--hfm-color-accent);
  letter-spacing: 0.04em;
  white-space: nowrap;
}

.home-lineage {
  margin: 16px 0 0;
}
.home-lineage img {
  max-width: 240px;
  height: auto;
  display: block;
}
.home-lineage__caption {
  margin-top: 8px;
  font-size: 10.5px;
  letter-spacing: 0.1em;
  color: var(--hfm-color-text-muted);
}

.home-book__manuscript {
  position: absolute;
  left: 1120px;
  top: -200px;
  width: 470px;
  height: 1300px;
  overflow: hidden;
  pointer-events: none;
  margin: 0;
}
.home-book__manuscript img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 14%;
  filter: sepia(0.15) saturate(0.86) contrast(1.03);
  -webkit-mask-image:
    linear-gradient(90deg, transparent 0, #000 130px),
    linear-gradient(180deg, #000 0, #000 calc(100% - 110px), transparent 100%);
  mask-image:
    linear-gradient(90deg, transparent 0, #000 130px),
    linear-gradient(180deg, #000 0, #000 calc(100% - 110px), transparent 100%);
  -webkit-mask-composite: source-in;
  mask-composite: intersect;
}
.home-book__manuscript-caption {
  position: absolute;
  left: 1120px;
  top: 1046px;
  width: 280px;
  text-align: left;
  font-size: 10px;
  letter-spacing: 0.14em;
  color: var(--hfm-color-text-muted);
}
.home-book__manuscript-caption b {
  font-family: var(--hfm-font-display);
  font-weight: 500;
  font-size: 12.5px;
  color: var(--hfm-color-text-secondary);
  letter-spacing: 0.1em;
}

/* ===== Responsive (CF-08): reflow below 1200px. ===== */
@media (max-width: 1199px) {
  .home-section--book {
    min-height: auto;
    margin-inline: 0;
    padding: var(--hfm-space-12) var(--hfm-space-5);
  }
  .home-book__inner {
    max-width: none;
    height: auto;
  }
  .home-book__eyebrow {
    position: static;
  }
  .home-book__jump {
    position: static;
    margin-top: var(--hfm-space-2);
  }
  .home-book__title {
    position: static;
    margin-top: var(--hfm-space-5);
  }
  .home-book__title-glyphs {
    font-size: clamp(48px, 10vw, 150px);
  }
  .home-book__title-meta {
    font-size: 13px;
  }
  .home-book__narr {
    position: static;
    width: auto;
    margin-top: var(--hfm-space-5);
  }
  .home-book__narr-heading {
    font-size: clamp(24px, 5vw, 36px);
  }
  .home-book__act {
    position: static;
    margin-top: var(--hfm-space-4);
  }
  .home-book__register {
    position: static;
    width: auto;
    margin-top: var(--hfm-space-5);
  }
  .home-book__manuscript {
    position: static;
    width: 200px;
    height: 220px;
    margin: var(--hfm-space-5) 0 0;
  }
  .home-book__manuscript-caption {
    position: static;
    width: auto;
    max-width: 20rem;
    margin: var(--hfm-space-3) 0 0;
  }
}

@media (max-width: 599px) {
  .home-section--book {
    padding: var(--hfm-space-8) var(--hfm-space-4);
  }
  .home-book__evidence {
    flex-wrap: wrap;
    gap: 12px;
  }
}
</style>

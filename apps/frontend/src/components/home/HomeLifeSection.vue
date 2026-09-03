<script setup lang="ts">
/**
 * HomeLifeSection — accepted homepage Section 02 (Life L2 Refined).
 *
 * WP-04: production visual fidelity for the frozen HFM_HOMEPAGE_SECTION02_VISUAL_BASELINE_L2_REFINED
 * composition (1440×1240). Concept: A LIFE DESCENDS THROUGH TIME, WHILE THE TEXT HE LEFT SURVIVES
 * BESIDE IT. LEFT — 皇甫谧的一生 / 215 → 282 descending the axis (narrative rhythm, not a stack);
 * RIGHT — one approved Siku manuscript column entering the page.
 *  - header: 02 eyebrow · 82px two-line headline · intro (seated right, no collision)
 *  - descending vertical axis with restrained junction marks
 *  - 104px date anchors 215 / 282 (derived from HOME_LIFE.dates)
 *  - four narrative-rhythm stages (from HOME_LIFE.stages)
 *  - manuscript column (frag-band1.jpg) breaking TOP + page boundary, LEFT dissolve
 *  - consolidated scholarly source register (其传 · 史料来源整理 + 阅读全文 → + claim)
 * SEMANTICS: h2 (no H1). DATA: stages/dates/intro from HOME_LIFE (no hardcoded authority).
 * ASSET: frag-band1.jpg (production path, SHA-verified).
 */
import { HOME_LIFE, HOME_CHAPTERS } from '../../data/homeProjection'

defineOptions({ name: 'HomeLifeSection' })

const stages = HOME_LIFE.stages
const dateParts = HOME_LIFE.dates.split('—')
const yearStart = dateParts[0] ?? ''
const yearEnd = dateParts[1] ?? ''
const claimText = `其传考据另载建安 / 正始两说（《晋书》等史料）；平台以 ${HOME_LIFE.dates} 为准并明示争议存在（见「史料依据」）。`
</script>

<template>
  <section id="home-life" class="home-section home-section--life" aria-labelledby="home-life-title">
    <div class="home-life__grain" aria-hidden="true"></div>
    <div class="home-life__inner">
      <!-- header: compact left title block + intro at right -->
      <div class="home-life__head">
        <p class="home-eyebrow">
          <span class="home-eyebrow__no">{{ HOME_CHAPTERS.life.no }}</span
          >{{ HOME_CHAPTERS.life.label }}
        </p>
        <h2 id="home-life-title" class="home-life__statement">{{ HOME_LIFE.headline }}</h2>
        <p class="home-life__intro">{{ HOME_LIFE.intro }}</p>
      </div>

      <!-- descending life axis -->
      <div class="home-life__axis" aria-hidden="true"></div>
      <span class="home-life__junction home-life__junction--open" aria-hidden="true"></span>
      <span class="home-life__junction home-life__junction--p1" aria-hidden="true"></span>
      <span class="home-life__junction home-life__junction--p2" aria-hidden="true"></span>
      <span class="home-life__junction home-life__junction--p3" aria-hidden="true"></span>
      <span class="home-life__junction home-life__junction--p4" aria-hidden="true"></span>
      <span class="home-life__junction home-life__junction--close" aria-hidden="true"></span>

      <!-- date anchors -->
      <div class="home-life__anchor home-life__anchor--a">{{ yearStart }}<span class="home-life__anchor-cap">生于乱世</span></div>
      <div class="home-life__anchor home-life__anchor--b">{{ yearEnd }}<span class="home-life__anchor-cap">终于著述</span></div>

      <!-- life stages (narrative rhythm, unequal) -->
      <div v-for="(stage, i) in stages" :key="stage.title" class="home-life__stage" :class="'home-life__stage--' + (i + 1)">
        <span class="home-life__stage-name">{{ stage.title }}</span>
        <p class="home-life__stage-note">{{ stage.note }}</p>
      </div>

      <!-- manuscript column — partially-visible marginal band (decorative) -->
      <figure class="home-life__manuscript" aria-hidden="true">
        <img src="/assets/jiayi/frag-band1.jpg" alt="" />
      </figure>

      <!-- consolidated scholarly source register -->
      <div class="home-life__register">
        <div class="home-life__register-row">
          <b>其传 · 史料来源整理</b>
          <span class="home-life__register-src">本源史料 / 地方志 / 类书 · 全文已整理</span>
          <a class="home-life__register-go" href="/reader/qichuan">阅读全文 →</a>
        </div>
        <p class="home-life__register-meta">《针灸甲乙经》四库全书本 · 清乾隆 · 卷一 · 客户授权资料<span class="home-life__register-sep">｜</span>{{ claimText }}</p>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* ===== Section 02 Life (L2 Refined) — production fidelity, 1440×1240 ===== */
.home-section--life {
  position: relative;
  overflow: hidden;
  min-height: 1240px;
  background:
    radial-gradient(980px 640px at 90% -8%, color-mix(in srgb, var(--hfm-color-heritage) 5%, transparent) 0%, transparent 62%),
    radial-gradient(700px 520px at -4% 114%, color-mix(in srgb, var(--hfm-color-accent) 4%, transparent) 0%, transparent 60%),
    var(--hfm-color-canvas);
}
.home-life__grain {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.05;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='240' height='240'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
.home-life__inner {
  position: relative;
  max-width: 1272px;
  margin: 0 auto;
  width: 100%;
  height: 100%;
}

/* header */
.home-life__head {
  position: absolute;
  left: 0;
  top: 130px;
  width: 1272px;
}
.home-life__statement {
  font-family: var(--hfm-font-heading);
  font-weight: 500;
  font-size: 82px;
  line-height: 1.2;
  letter-spacing: 0.04em;
  color: var(--hfm-color-text);
  margin: 32px 0 0;
  /* natural two-line wrap (no <br>) so the accessible heading name stays clean */
  max-width: 9ch;
}
/* intro — seated right of the headline (no collision) */
.home-life__intro {
  position: absolute;
  left: 560px;
  top: 44px;
  width: 360px;
  max-width: 34ch;
  font-size: 15px;
  line-height: 2.1;
  color: var(--hfm-color-text-secondary);
  margin: 0;
}
.home-life__intro b {
  color: var(--hfm-color-text);
  font-weight: 600;
}

/* axis */
.home-life__axis {
  position: absolute;
  left: 130px;
  top: 470px;
  width: 1px;
  height: 550px;
  background: linear-gradient(180deg, var(--hfm-color-border-strong) 0, var(--hfm-color-text) 10%, var(--hfm-color-text) 90%, var(--hfm-color-border-strong) 100%);
}
.home-life__junction {
  position: absolute;
  left: 126px;
  width: 9px;
  height: 9px;
  border-radius: 50%;
  border: 1px solid var(--hfm-color-text);
  background: var(--hfm-color-canvas);
}
.home-life__junction--open {
  top: 466px;
}
.home-life__junction--p1 {
  top: 562px;
}
.home-life__junction--p2 {
  top: 686px;
}
.home-life__junction--p3 {
  top: 802px;
}
.home-life__junction--p4 {
  top: 896px;
}
.home-life__junction--close {
  top: 1016px;
}

/* date anchors — large temporal anchors, NOT hero scale */
.home-life__anchor {
  position: absolute;
  left: 34px;
  font-family: var(--hfm-font-display);
  font-weight: 500;
  line-height: 1;
  color: var(--hfm-color-text);
  font-variant-numeric: tabular-nums;
}
.home-life__anchor--a {
  top: 408px;
  font-size: 104px;
}
.home-life__anchor--b {
  top: 962px;
  font-size: 104px;
}
.home-life__anchor-cap {
  display: block;
  margin-top: 14px;
  font-family: var(--hfm-font-sans);
  font-weight: 400;
  font-size: 12px;
  letter-spacing: 0.3em;
  color: var(--hfm-color-text-muted);
}

/* stages — descending, narrative rhythm (unequal) */
.home-life__stage {
  position: absolute;
  left: 210px;
  font-family: var(--hfm-font-display);
  color: var(--hfm-color-text);
}
.home-life__stage-name {
  font-weight: 500;
  line-height: 1.2;
}
.home-life__stage-note {
  font-family: var(--hfm-font-sans);
  font-weight: 400;
  color: var(--hfm-color-text-secondary);
  line-height: 1.9;
  margin-top: 12px;
  max-width: 36ch;
}
/* 求学悟道 — slightly stronger opening */
.home-life__stage--1 {
  top: 540px;
}
.home-life__stage--1 .home-life__stage-name {
  font-size: 46px;
}
.home-life__stage--1 .home-life__stage-note {
  font-size: 13px;
}
/* 拒仕治学 — restrained */
.home-life__stage--2 {
  top: 664px;
}
.home-life__stage--2 .home-life__stage-name {
  font-size: 33px;
  color: var(--hfm-color-text-secondary);
}
.home-life__stage--2 .home-life__stage-note {
  font-size: 12.5px;
}
/* 久病研医 — stronger turning point */
.home-life__stage--3 {
  top: 780px;
}
.home-life__stage--3 .home-life__stage-name {
  font-size: 44px;
}
.home-life__stage--3 .home-life__stage-note {
  font-size: 12.5px;
}
/* 著书传世 — strong final stage aligned toward the manuscript */
.home-life__stage--4 {
  top: 874px;
  width: 700px;
}
.home-life__stage--4 .home-life__stage-name {
  font-size: 47px;
}
.home-life__stage--4 .home-life__stage-note {
  font-size: 12.5px;
}

/* manuscript — ONE fragment, breaks TOP + page boundary, LEFT dissolves (decorative) */
.home-life__manuscript {
  position: absolute;
  right: -80px;
  top: -180px;
  width: 300px;
  height: 1520px;
  overflow: hidden;
  pointer-events: none;
  margin: 0;
}
.home-life__manuscript img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 26%;
  filter: sepia(0.15) saturate(0.86) contrast(1.03);
  -webkit-mask-image: linear-gradient(90deg, transparent 0, #000 120px);
  mask-image: linear-gradient(90deg, transparent 0, #000 120px);
}

/* consolidated scholarly source register */
.home-life__register {
  position: absolute;
  left: 0;
  bottom: 52px;
  width: 1272px;
  border-top: 1px solid var(--hfm-color-border);
  padding-top: 22px;
}
.home-life__register-row {
  display: flex;
  align-items: baseline;
  gap: 18px;
  font-size: 13px;
  color: var(--hfm-color-text-secondary);
}
.home-life__register-row b {
  font-family: var(--hfm-font-display);
  font-size: 17px;
  letter-spacing: 0.06em;
  color: var(--hfm-color-text);
}
.home-life__register-src {
  font-size: 12px;
  color: var(--hfm-color-text-muted);
  letter-spacing: 0.02em;
}
.home-life__register-go {
  color: var(--hfm-color-accent);
  letter-spacing: 0.1em;
  white-space: nowrap;
}
.home-life__register-meta {
  margin-top: 8px;
  font-size: 11.5px;
  letter-spacing: 0.02em;
  color: var(--hfm-color-text-muted);
  line-height: 1.8;
}
.home-life__register-sep {
  margin: 0 10px;
  color: var(--hfm-color-border-strong);
}
</style>

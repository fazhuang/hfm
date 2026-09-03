<script setup lang="ts">
/**
 * HomeHeroSection — accepted homepage Section 01 (Hero H3 Refined).
 *
 * WP-04: production visual fidelity for the frozen HFM_HOMEPAGE_HERO_VISUAL_BASELINE_H3_REFINED
 * composition (1440×900). Reconciles:
 *  - VISUAL: museum-grade editorial hero — 190px 皇甫谧 monument (decorative aria-hidden),
 *    kicker, statement, roles, ONE editorial action, bottom note, manuscript specimen
 *    (frag-macro.jpg) breaking TOP+RIGHT with LEFT dissolve, grain/halo, archive guide-line.
 *  - SEMANTICS: exactly ONE H1 = the platform name (皇甫谧人文数字平台), rendered as the quiet
 *    top-right register (per the artboard `reg-hfm`); the 皇甫谧 name monument is aria-hidden
 *    decorative (no duplicate accessible heading). Heading order preserved.
 *  - SEARCH: subordinate (HomeView owns page-level state); presentational via props; the
 *    `#home-search-input` browser contract preserved (E2E).
 * DATA: identity/dates/definition from HOME_HERO + CORE_PERSON_*. ASSET: frag-macro.jpg
 * (production path, SHA-verified).
 */
import { HOME_HERO, HOME_CHAPTERS } from '../../data/homeProjection'
import { CORE_PERSON_DATES } from '../../config/corePerson'

defineOptions({ name: 'HomeHeroSection' })

interface Props {
  searchValue?: string
  onSearch?: () => void
  searchLabel?: string
}

const props = defineProps<Props>()
const emit = defineEmits<{ (e: 'update:searchValue', value: string): void }>()

const dates = CORE_PERSON_DATES
</script>

<template>
  <section id="home-hero" class="home-section home-section--hero" aria-labelledby="home-hero-title">
    <div class="home-hero__grain" aria-hidden="true"></div>
    <div class="home-hero__gline" aria-hidden="true"></div>

    <!-- H1 — quiet top-right platform register (single H1) -->
    <h1 id="home-hero-title" class="home-hero__reg">{{ HOME_HERO.title }}</h1>

    <!-- label block -->
    <p class="home-eyebrow home-hero__idx">
      <span class="home-eyebrow__no">{{ HOME_CHAPTERS.hero.no }}</span
      >{{ HOME_CHAPTERS.hero.label }}
    </p>
    <p class="home-hero__kicker">魏晋 · 公元 {{ dates }}</p>

    <!-- the name — 190px monument (decorative; H1 = platform name) -->
    <p class="home-hero__name" aria-hidden="true">
      <span class="home-hero__glyph">皇</span><span class="home-hero__glyph">甫</span><span class="home-hero__glyph">谧</span>
    </p>
    <div class="home-hero__rule" aria-hidden="true"></div>

    <p class="home-hero__statement">针灸学专著《针灸甲乙经》的编纂者，世称“针灸鼻祖”。</p>
    <p class="home-hero__roles">西晋 · 医学家 · 文学家 · 史学家</p>

    <a class="home-hero__act" href="/persons/person-huangfu-mi">进入人物档案 <span class="home-hero__act-arr">→</span></a>

    <p class="home-hero__bottom-note">
      <b>皇甫谧 · 人文数字档案</b>
      <span>其传 / 其言 / 后论 · 史料来源整理</span>
    </p>

    <!-- specimen: manuscript detail, breaking TOP + RIGHT, LEFT dissolves (decorative) -->
    <figure class="home-hero__specimen" aria-hidden="true">
      <img src="/assets/jiayi/frag-macro.jpg" alt="" />
    </figure>
    <div class="home-hero__spec-caption" aria-hidden="true">
      <span class="home-hero__spec-title">《针灸甲乙经》</span>
      <span class="home-hero__spec-sub">四库全书本 · 卷一 · 清乾隆抄本 · 客户授权资料</span>
    </div>

    <!-- search — SUBORDINATE functionality (HomeView owns state; browser contract intact) -->
    <form
      v-if="searchLabel"
      class="home-search"
      role="search"
      :aria-label="searchLabel"
      @submit.prevent="props.onSearch"
    >
      <label class="visually-hidden" for="home-search-input">检索平台内容</label>
      <input
        id="home-search-input"
        :value="props.searchValue"
        class="home-search__input"
        type="search"
        placeholder="检索平台内容"
        @input="emit('update:searchValue', ($event.target as HTMLInputElement).value)"
      />
      <button class="home-search__submit" type="submit">检索</button>
    </form>
  </section>
</template>

<style scoped>
/* ===== Section 01 Hero (H3 Refined) — production fidelity, 1440×900 ===== */
.home-section--hero {
  position: relative;
  overflow: hidden;
  min-height: 900px;
  background:
    radial-gradient(900px 600px at 92% -6%, color-mix(in srgb, var(--hfm-color-heritage) 6%, transparent) 0%, transparent 60%),
    radial-gradient(640px 460px at 0% 108%, color-mix(in srgb, var(--hfm-color-accent) 4%, transparent) 0%, transparent 60%),
    var(--hfm-color-canvas);
}

.home-hero__grain {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.05;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='240' height='240'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

/* gallery guide-line — the only structural line */
.home-hero__gline {
  position: absolute;
  left: 88px;
  top: 0;
  bottom: 0;
  width: 1px;
  background: linear-gradient(180deg, var(--hfm-color-border-strong) 0 14%, rgba(207, 196, 176, 0) 30%);
}

/* H1 — quiet top-right platform register */
.home-hero__reg {
  position: absolute;
  right: 60px;
  top: 56px;
  text-align: right;
  font-size: 10px;
  letter-spacing: 0.34em;
  font-weight: 400;
  line-height: 2.1;
  color: var(--hfm-color-text-muted);
  margin: 0;
}

/* label block (uses foundation .home-eyebrow role, heritage accent) */
.home-hero__idx {
  position: absolute;
  left: 132px;
  top: 120px;
  font-size: 10.5px;
  letter-spacing: 0.42em;
  margin: 0;
}
.home-hero__kicker {
  position: absolute;
  left: 130px;
  top: 206px;
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 12px;
  letter-spacing: 0.34em;
  color: var(--hfm-color-heritage);
  white-space: nowrap;
  margin: 0;
}
.home-hero__kicker::before {
  content: "";
  width: 26px;
  height: 1px;
  background: var(--hfm-color-heritage);
  flex: none;
}

/* 皇甫谧 — 190px monument (primary visual event; decorative) */
.home-hero__name {
  position: absolute;
  left: 126px;
  top: 252px;
  display: flex;
  align-items: baseline;
  font-family: var(--hfm-font-display);
  font-weight: 500;
  line-height: 1;
  color: var(--hfm-color-text);
  margin: 0;
}
.home-hero__glyph {
  font-size: 190px;
  letter-spacing: 0;
}
.home-hero__glyph + .home-hero__glyph {
  margin-left: 16px;
}

.home-hero__rule {
  position: absolute;
  left: 130px;
  top: 470px;
  width: 560px;
  height: 1px;
  background: var(--hfm-color-border);
}

.home-hero__statement {
  position: absolute;
  left: 130px;
  top: 514px;
  width: 480px;
  font-size: 14px;
  line-height: 2.1;
  color: var(--hfm-color-text-secondary);
  margin: 0;
}
.home-hero__roles {
  position: absolute;
  left: 130px;
  top: 594px;
  font-size: 11.5px;
  letter-spacing: 0.3em;
  color: var(--hfm-color-text-muted);
  margin: 0;
}

.home-hero__act {
  position: absolute;
  left: 130px;
  top: 676px;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  font-size: 13.5px;
  letter-spacing: 0.18em;
  color: var(--hfm-color-text);
  text-decoration: none;
}
.home-hero__act-arr {
  color: var(--hfm-color-accent);
  font-family: var(--hfm-font-serif);
  font-size: 15px;
}
.home-hero__act:hover .home-hero__act-arr {
  transform: translateX(4px);
}
.home-hero__act-arr {
  transition: transform 0.2s ease;
}

.home-hero__bottom-note {
  position: absolute;
  left: 88px;
  bottom: 30px;
  display: flex;
  gap: 26px;
  font-size: 9.5px;
  letter-spacing: 0.3em;
  color: var(--hfm-color-text-muted);
  margin: 0;
}
.home-hero__bottom-note b {
  color: var(--hfm-color-text-secondary);
  font-weight: 500;
  letter-spacing: 0.2em;
}

/* specimen — 244px, breaks TOP + RIGHT, LEFT dissolves (decorative) */
.home-hero__specimen {
  position: absolute;
  right: -36px;
  top: -64px;
  width: 244px;
  z-index: 2;
  pointer-events: none;
  margin: 0;
}
.home-hero__specimen img {
  width: 100%;
  height: auto;
  display: block;
  filter: sepia(0.16) saturate(0.88) contrast(1.03);
  transform: rotate(1.1deg);
  -webkit-mask-image: linear-gradient(90deg, transparent 0, #000 70px), linear-gradient(0deg, transparent 0, #000 46px);
  mask-image: linear-gradient(90deg, transparent 0, #000 70px), linear-gradient(0deg, transparent 0, #000 46px);
  -webkit-mask-composite: source-in;
  mask-composite: intersect;
  box-shadow: 0 30px 52px -30px rgba(90, 64, 26, 0.34);
}
.home-hero__spec-caption {
  position: absolute;
  right: 64px;
  top: 470px;
  width: 244px;
  text-align: left;
  z-index: 2;
  line-height: 1.9;
}
.home-hero__spec-title {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding-top: 8px;
  border-top: 1px solid var(--hfm-color-border-strong);
  font-family: var(--hfm-font-serif);
  font-weight: 500;
  font-size: 12.5px;
  letter-spacing: 0.1em;
  color: var(--hfm-color-text-secondary);
}
.home-hero__spec-sub {
  display: block;
  margin-top: 7px;
  font-size: 10px;
  letter-spacing: 0.12em;
  color: var(--hfm-color-text-muted);
}

/* search — SUBORDINATE, quiet, non-dominant */
.home-search {
  position: absolute;
  left: 130px;
  top: 782px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  max-width: 20rem;
}
.home-search__input {
  width: 12rem;
  background: transparent;
  border: none;
  border-bottom: 1px solid var(--hfm-color-border-strong);
  padding: 0.25rem 0;
  font: inherit;
  font-size: 12px;
  letter-spacing: 0.08em;
  color: var(--hfm-color-text);
}
.home-search__input::placeholder {
  color: var(--hfm-color-text-muted);
}
.home-search__submit {
  background: none;
  border: none;
  padding: 0;
  font: inherit;
  font-size: 12px;
  letter-spacing: 0.16em;
  color: var(--hfm-color-text-muted);
  cursor: pointer;
}
.home-search__submit:hover {
  color: var(--hfm-color-text);
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: -1px;
  padding: 0;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>

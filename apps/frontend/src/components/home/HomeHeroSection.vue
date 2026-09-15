<script setup lang="ts">
/**
 * HomeHeroSection — Section 01 (《刻度 / THE SCALE》).
 *
 * A ruled opening: a marginal index · latin label · the person's dates on a
 * hairline; the 皇甫谧 monument in serif; the platform statement and the one
 * editorial action; the derived 刻度带 (XlScaleBand); the manuscript specimen
 * with its real provenance caption; the quiet search line.
 *
 * The single H1 is the platform name, rendered as a quiet register (the
 * monument is a non-heading decorative block). #home-search-input is the only
 * homepage search input.
 */
import { computed } from 'vue'
import { HOME_HERO } from '../../data/homeProjection'
import { CORE_PERSON_DATES } from '../../config/corePerson'
import type { BlockData } from '../../composables/useHomeContractData'
import type { HomeProjection } from '../../types/public'
import XlScaleBand from './XlScaleBand.vue'

defineOptions({ name: 'HomeHeroSection' })

interface Props {
  searchValue?: string
  onSearch?: () => void
  searchLabel?: string
  block?: BlockData<HomeProjection> | null
}
const props = defineProps<Props>()

/** T0 platform register — real published counts (contract §4 block 01). */
const counts = computed(() => {
  const c = props.block?.data?.counts
  if (!c || props.block?.source !== 'backend') return null
  if (c.works + c.persons + c.c_terms + c.heritage_projects <= 0) return null
  return [
    { label: '已发布著作', value: c.works },
    { label: '已发布人物', value: c.persons },
    { label: '已发布术语', value: c.c_terms },
  ]
})
const emit = defineEmits<{ (e: 'update:searchValue', value: string): void }>()
const dates = CORE_PERSON_DATES
</script>

<template>
  <section id="home-hero" class="hero" aria-labelledby="home-hero-title" :data-source="counts ? 'backend' : 'fallback'">
    <div class="hero__inner">
      <p class="hero__bar">
        <span class="xl-index">00</span>
        <span class="xl-label">HUANGFU MI · DIGITAL HUMANITIES</span>
        <span class="xl-num hero__bar-date">公元 {{ dates }}</span>
      </p>

      <h1 id="home-hero-title" class="hero__brand">{{ HOME_HERO.title }}</h1>

      <!-- T0 platform register (real published counts) -->
      <dl v-if="counts" class="hero__counts" data-source="backend">
        <div v-for="c in counts" :key="c.label" class="hero__count">
          <dt class="xl-label">{{ c.label }}</dt>
          <dd class="xl-num hero__count-value">{{ c.value }}</dd>
        </div>
      </dl>

      <p class="home-hero__name hero__name" aria-hidden="true">
        <span class="home-hero__glyph">皇</span><span class="home-hero__glyph">甫</span
        ><span class="home-hero__glyph">谧</span>
      </p>

      <div class="hero__body">
        <div class="hero__col">
          <p class="hero__statement">{{ HOME_HERO.definition }}</p>
          <p class="hero__roles">西晋 · 医学家 · 文学家 · 史学家</p>

          <div class="hero__acts">
            <a class="home-hero__act hero__act" href="/persons/ENT-PERSON-HFM-HUANGFUMI">
              进入人物档案 <span class="home-hero__act-arr hero__act-arr" aria-hidden="true">→</span>
            </a>
            <a class="hero__act hero__act--ghost" href="/jiayi">
              进入《针灸甲乙经》 <span class="hero__act-arr" aria-hidden="true">→</span>
            </a>
          </div>

          <form
            v-if="searchLabel"
            class="home-search hero__search"
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
        </div>

        <div class="hero__aside">
          <XlScaleBand class="hero__band" />
          <figure class="hero__specimen">
            <img src="/assets/jiayi/frag-macro.jpg" alt="" aria-hidden="true" />
          </figure>
          <figcaption class="home-hero__spec-caption hero__caption">
            <span class="hero__caption-title">《针灸甲乙经》</span>
            <span class="hero__caption-sub">四库全书本 · 卷一 · 清乾隆抄本 · 客户授权资料</span>
          </figcaption>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero {
  background: var(--wl-paper);
  color: var(--wl-ink);
  padding: clamp(2.5rem, 6vw, 5rem) var(--hfm-space-6) clamp(3.5rem, 9vw, 7rem);
}
.hero__inner {
  max-width: 78rem;
  margin: 0 auto;
}

/* ---- ruled top bar ---- */
.hero__bar {
  display: grid;
  grid-template-columns: 4.5rem 1fr auto;
  gap: var(--hfm-space-6);
  align-items: baseline;
  margin: 0 0 clamp(2rem, 5vw, 3.5rem);
  padding-top: var(--hfm-space-4);
  border-top: 1px solid var(--wl-rule);
  font-size: var(--hfm-text-sm);
}
.hero__bar-date {
  color: var(--wl-mute);
  font-size: var(--hfm-text-sm);
}

/* ---- the platform register (single H1, quiet) ---- */
.hero__counts {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-8);
  margin: 0 0 var(--hfm-space-6);
}
.hero__count dt {
  margin-bottom: var(--hfm-space-1);
}
.hero__count-value {
  margin: 0;
  font-size: var(--hfm-text-2xl);
  color: var(--wl-ink);
}
.hero__brand {
  margin: 0 0 var(--hfm-space-6);
  font-family: var(--wl-latin);
  font-weight: 400;
  font-size: 0.75rem;
  letter-spacing: 0.42em;
  text-transform: uppercase;
  color: var(--wl-mute);
}

/* ---- the monument ---- */
.hero__name {
  display: flex;
  margin: 0 0 clamp(2rem, 5vw, 3.5rem);
  font-family: var(--hfm-font-display);
  font-weight: 500;
  line-height: 0.98;
  letter-spacing: 0.02em;
  color: var(--wl-ink);
}
.home-hero__glyph {
  font-size: clamp(4.5rem, 15vw, 12rem);
}
.home-hero__glyph + .home-hero__glyph {
  margin-left: 0.06em;
}

/* ---- body: editorial column + instrument aside ---- */
.hero__body {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(0, 0.75fr);
  gap: clamp(2rem, 6vw, 5rem);
  align-items: start;
  padding-top: var(--hfm-space-6);
  border-top: 1px solid var(--wl-rule);
}
.hero__statement {
  margin: 0 0 var(--hfm-space-4);
  max-width: 34ch;
  font-size: clamp(1.0625rem, 1.6vw, 1.375rem);
  line-height: 1.95;
  color: var(--wl-ink);
}
.hero__roles {
  margin: 0 0 var(--hfm-space-8);
  font-family: var(--wl-latin);
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.2em;
  color: var(--wl-mute);
}
.hero__acts {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-3);
  margin-bottom: var(--hfm-space-8);
}
.hero__act {
  display: inline-flex;
  align-items: center;
  gap: var(--hfm-space-2);
  min-height: 40px;
  padding: 0 var(--hfm-space-5);
  border: 1px solid var(--wl-ink);
  background: var(--wl-ink);
  color: var(--wl-paper);
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.1em;
  text-decoration: none;
  transition: background 0.18s ease, color 0.18s ease, border-color 0.18s ease;
}
.hero__act:hover {
  background: var(--wl-mark);
  border-color: var(--wl-mark);
}
.hero__act--ghost {
  background: transparent;
  color: var(--wl-ink);
  border-color: var(--wl-rule);
}
.hero__act--ghost:hover {
  background: transparent;
  color: var(--wl-mark);
  border-color: var(--wl-mark);
}
.hero__act-arr {
  transition: transform 0.18s ease;
}
.hero__act:hover .hero__act-arr {
  transform: translateX(3px);
}

/* ---- quiet search line ---- */
.hero__search {
  display: flex;
  align-items: center;
  gap: var(--hfm-space-2);
  max-width: 24rem;
  border-bottom: 1px solid var(--wl-rule);
}
.home-search__input {
  flex: 1;
  min-width: 0;
  background: transparent;
  border: none;
  padding: var(--hfm-space-2) 0;
  font: inherit;
  font-size: var(--hfm-text-sm);
  color: var(--wl-ink);
}
.home-search__input::placeholder {
  color: var(--wl-mute);
}
.home-search__input:focus {
  outline: none;
}
.home-search__submit {
  min-height: 24px;
  background: none;
  border: none;
  padding: var(--hfm-space-2);
  font: inherit;
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.14em;
  color: var(--wl-mark);
  cursor: pointer;
}

/* ---- instrument aside ---- */
.hero__aside {
  display: flex;
  flex-direction: column;
  gap: var(--hfm-space-5);
}
.hero__band {
  color: var(--wl-ink);
}
.hero__specimen {
  margin: 0;
  border: 1px solid var(--wl-rule);
  overflow: hidden;
}
.hero__specimen img {
  display: block;
  width: 100%;
  height: auto;
  filter: sepia(0.12) saturate(0.85) contrast(1.02);
}
.hero__caption {
  padding-top: var(--hfm-space-3);
  border-top: 1px solid var(--wl-rule);
}
.hero__caption-title {
  display: block;
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-base);
  letter-spacing: 0.06em;
  color: var(--wl-ink);
}
.hero__caption-sub {
  display: block;
  margin-top: var(--hfm-space-1);
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.08em;
  color: var(--wl-mute);
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

@media (max-width: 900px) {
  .hero__body {
    grid-template-columns: 1fr;
  }
  .hero__aside {
    max-width: 26rem;
  }
}
@media (max-width: 599px) {
  .hero {
    padding: var(--hfm-space-8) var(--hfm-space-4) var(--hfm-space-12);
  }
  .hero__bar {
    grid-template-columns: 2.75rem 1fr;
    row-gap: var(--hfm-space-2);
  }
  .hero__bar-date {
    grid-column: 2;
  }
  .hero__acts {
    flex-direction: column;
    align-items: stretch;
  }
  .hero__act {
    justify-content: center;
  }
}
</style>

<script setup lang="ts">
/**
 * HomeHeroSection — homepage Section 01 (Hero).
 *
 * REDESIGN (方案3 · 当代东方数字人文): replaces the previous absolutely-positioned
 * 1440×900 artboard composition with a responsive editorial hero — a two-column
 * grid (editorial text column + documentary book-specimen column) that reflows
 * to a single column on narrow viewports. Warm canvas + restrained bronze /
 * cinnabar accents; generous whitespace; serif display for the name.
 *
 * ACCEPTED CONTRACT PRESERVED (ui03_home.spec.ts):
 *  - exactly one H1 = the platform brand 皇甫谧人文数字平台;
 *  - #home-hero section id; .home-hero__name is decorative (aria-hidden, not a
 *    heading); .home-hero__spec-caption is real content (contains 四库全书本);
 *  - one #home-search-input inside form.home-search[role=search], placeholder
 *    检索平台内容, wired to /search via HomeView props.
 *
 * DATA: HOME_HERO + CORE_PERSON_* (no new facts). The specimen caption is the
 * provenance of the real production asset.
 */
import { HOME_HERO } from '../../data/homeProjection'
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
  <section id="home-hero" class="hero" aria-labelledby="home-hero-title">
    <div class="hero__grid">
      <!-- ===== editorial text column ===== -->
      <div class="hero__text">
        <p class="hero__eyebrow">
          <span class="hero__eyebrow-rule" aria-hidden="true"></span>
          魏晋 · 公元 {{ dates }}
        </p>

        <h1 id="home-hero-title" class="hero__brand">{{ HOME_HERO.title }}</h1>

        <!-- the name — decorative monument (the H1 carries the platform brand) -->
        <p class="home-hero__name hero__name" aria-hidden="true">皇甫谧</p>

        <p class="hero__statement">{{ HOME_HERO.definition }}</p>
        <p class="hero__roles">西晋 · 医学家 · 文学家 · 史学家</p>

        <div class="hero__actions">
          <a class="hero__cta" href="/persons/person-huangfu-mi">
            进入人物档案 <span class="hero__cta-arr" aria-hidden="true">→</span>
          </a>
          <a class="hero__cta hero__cta--ghost" href="/jiayi">
            进入《针灸甲乙经》 <span class="hero__cta-arr" aria-hidden="true">→</span>
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

      <!-- ===== documentary specimen column ===== -->
      <figure class="hero__visual">
        <div class="hero__visual-frame">
          <img
            class="hero__visual-img"
            src="/assets/jiayi/frag-macro.jpg"
            alt=""
            aria-hidden="true"
          />
        </div>
        <figcaption class="home-hero__spec-caption hero__caption">
          <span class="hero__caption-title">《针灸甲乙经》</span>
          <span class="hero__caption-sub">四库全书本 · 卷一 · 清乾隆抄本 · 客户授权资料</span>
        </figcaption>
      </figure>
    </div>
  </section>
</template>

<style scoped>
.hero {
  background: var(--hfm-color-canvas);
  padding: var(--hfm-space-24) var(--hfm-space-6) var(--hfm-space-16);
}
.hero__grid {
  max-width: var(--hfm-content-max-wide);
  margin: 0 auto;
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 0.85fr);
  gap: var(--hfm-space-16);
  align-items: center;
}

/* ---- text column ---- */
.hero__text {
  min-width: 0;
}
.hero__eyebrow {
  display: flex;
  align-items: center;
  gap: var(--hfm-space-3);
  margin: 0 0 var(--hfm-space-6);
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.3em;
  color: var(--hfm-color-heritage);
}
.hero__eyebrow-rule {
  width: 2rem;
  height: 1px;
  background: var(--hfm-color-heritage);
}
.hero__brand {
  margin: 0 0 var(--hfm-space-4);
  font-size: var(--hfm-text-lg);
  font-weight: 400;
  letter-spacing: 0.26em;
  color: var(--hfm-color-text-secondary);
}
.hero__name {
  margin: 0 0 var(--hfm-space-6);
  font-family: var(--hfm-font-display);
  font-size: clamp(4rem, 12vw, 8.5rem);
  font-weight: 500;
  line-height: 1.02;
  letter-spacing: 0.04em;
  color: var(--hfm-color-ink, var(--hfm-color-text));
}
.hero__statement {
  margin: 0 0 var(--hfm-space-3);
  max-width: 34ch;
  font-size: var(--hfm-text-lg);
  line-height: var(--hfm-leading-normal);
  color: var(--hfm-color-text);
}
.hero__roles {
  margin: 0 0 var(--hfm-space-8);
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.24em;
  color: var(--hfm-color-text-muted);
}

/* ---- actions ---- */
.hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-4);
  margin-bottom: var(--hfm-space-8);
}
.hero__cta {
  display: inline-flex;
  align-items: center;
  gap: var(--hfm-space-2);
  padding: var(--hfm-space-3) var(--hfm-space-6);
  border: 1px solid var(--hfm-color-accent);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-accent);
  color: var(--hfm-color-on-accent);
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.12em;
  text-decoration: none;
  transition: background 0.18s ease, border-color 0.18s ease;
}
.hero__cta:hover {
  background: var(--hfm-color-accent-hover);
  border-color: var(--hfm-color-accent-hover);
}
.hero__cta--ghost {
  background: transparent;
  border-color: var(--hfm-color-border-strong);
  color: var(--hfm-color-text);
}
.hero__cta--ghost:hover {
  background: transparent;
  border-color: var(--hfm-color-accent);
  color: var(--hfm-color-accent);
}
.hero__cta-arr {
  font-family: var(--hfm-font-serif);
  transition: transform 0.18s ease;
}
.hero__cta:hover .hero__cta-arr {
  transform: translateX(3px);
}

/* ---- search ---- */
.hero__search {
  display: flex;
  align-items: center;
  gap: var(--hfm-space-2);
  max-width: 26rem;
  padding-bottom: var(--hfm-space-1);
  border-bottom: 1px solid var(--hfm-color-border-strong);
}
.home-search__input {
  flex: 1;
  min-width: 0;
  background: transparent;
  border: none;
  padding: var(--hfm-space-1) 0;
  font: inherit;
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.06em;
  color: var(--hfm-color-text);
}
.home-search__input::placeholder {
  color: var(--hfm-color-text-muted);
}
.home-search__input:focus {
  outline: none;
}
.home-search__submit {
  background: none;
  border: none;
  padding: var(--hfm-space-1) var(--hfm-space-2);
  font: inherit;
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.16em;
  color: var(--hfm-color-accent);
  cursor: pointer;
}

/* ---- visual column ---- */
.hero__visual {
  margin: 0;
  min-width: 0;
}
.hero__visual-frame {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
}
.hero__visual-img {
  display: block;
  width: 100%;
  height: auto;
  filter: sepia(0.14) saturate(0.9) contrast(1.02);
}
.hero__caption {
  margin-top: var(--hfm-space-4);
  padding-top: var(--hfm-space-3);
  border-top: 1px solid var(--hfm-color-border-strong);
}
.hero__caption-title {
  display: block;
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-base);
  letter-spacing: 0.08em;
  color: var(--hfm-color-text);
}
.hero__caption-sub {
  display: block;
  margin-top: var(--hfm-space-1);
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.1em;
  color: var(--hfm-color-text-muted);
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

/* ---- responsive ---- */
@media (max-width: 1023px) {
  .hero__grid {
    grid-template-columns: 1fr;
    gap: var(--hfm-space-12);
  }
  .hero__visual {
    order: -1;
    max-width: 26rem;
  }
}
@media (max-width: 599px) {
  .hero {
    padding: var(--hfm-space-16) var(--hfm-space-4) var(--hfm-space-12);
  }
  .hero__name {
    font-size: clamp(3.5rem, 22vw, 5rem);
  }
  .hero__actions {
    flex-direction: column;
    align-items: stretch;
  }
  .hero__cta {
    justify-content: center;
  }
  .home-search__submit {
    min-height: 24px;
    min-width: 24px;
  }
}
</style>

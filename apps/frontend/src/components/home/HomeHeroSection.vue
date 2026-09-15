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
import { CORE_PERSON_DATES, CORE_PERSON_PORTRAIT_MEDIA_ID } from '../../config/corePerson'
import { mediaBytesUrl } from '../../services/media'
import type { BlockData } from '../../composables/useHomeContractData'
import type { HomeProjection } from '../../types/public'

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

/**
 * 展柜里的主展板 —— 客户提供的皇甫谧画像，经公开媒体接口取原件。
 * 这是首页**唯一**有史实地位的人物影像；其余展板放的是真实书影与脉络图，
 * 四件都是客户材料，没有一件是生成的。
 */
const portraitUrl = mediaBytesUrl(CORE_PERSON_PORTRAIT_MEDIA_ID)
</script>

<template>
  <section
    id="home-hero"
    class="hero"
    aria-labelledby="home-hero-title"
    :data-source="counts ? 'backend' : 'fallback'"
  >
    <!-- 整屏氛围底：客户提供的皇甫谧画像，整幅铺满，向左压暗。
         画像本身是工笔设色，细节足、尺幅够，撑得起整屏 —— 不需要另造一张图。
         图为纯装饰（文字已表意），故 aria-hidden。 -->
    <div class="hero__bleed">
      <img class="hero__bleed-img" :src="portraitUrl" alt="" aria-hidden="true" />
      <div class="hero__scrim" aria-hidden="true"></div>
    </div>

    <div class="hero__inner">
      <p class="hero__bar">
        <span class="xl-index">00</span>
        <span class="xl-label">HUANGFU MI · DIGITAL HUMANITIES</span>
        <span class="xl-num hero__bar-date">公元 {{ dates }}</span>
      </p>

      <div class="hero__text">
        <h1 id="home-hero-title" class="hero__brand">{{ HOME_HERO.title }}</h1>
        <p class="hero__statement">{{ HOME_HERO.subtitle }}</p>

        <div class="hero__acts">
          <a class="hero__act" href="/persons/ENT-PERSON-HFM-HUANGFUMI">
            走进皇甫谧
            <span class="home-hero__act-arr hero__act-arr" aria-hidden="true">→</span>
          </a>
          <a class="hero__act hero__act--ghost" href="/jiayi">
            阅读《针灸甲乙经》
            <span class="home-hero__act-arr hero__act-arr" aria-hidden="true">→</span>
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

        <!-- T0 平台登记（真实已发布计数），一行安静的底注 -->
        <dl v-if="counts" class="hero__counts" data-source="backend">
          <div v-for="c in counts" :key="c.label" class="hero__count">
            <dt class="xl-label">{{ c.label }}</dt>
            <dd class="xl-num hero__count-value">{{ c.value }}</dd>
          </div>
        </dl>
      </div>
    </div>

  </section>
</template>

<style scoped>
/* ==========================================================================
   Hero — 整屏氛围底
   ==========================================================================
   画像整幅铺满，向左压暗；文字压在暗部。
   参考图的首屏是一整张场景；我们没有场景照片，但有客户提供的工笔画像 ——
   它本身细节足够，铺满一屏成立。不另造图。
   ========================================================================== */

.hero {
  position: relative;
  background: var(--wl-paper);
  color: var(--wl-ink);
  padding: 0 var(--hfm-space-6);
}

/* ---- 氛围底 ---- */
.hero__bleed {
  position: absolute;
  inset: 0 0 auto;
  height: min(88vh, 52rem);
  overflow: hidden;
  pointer-events: none;
}
.hero__bleed-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  /* 人物在右，视线向左 —— 与文字方向一致。 */
  object-position: 72% 18%;
}
/* 压暗：左重（压字）右轻（留人物），下重（接下一段）。
   不用大面积发光，只把暗部推够，让暖白字在图上立住。 */
.hero__scrim {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(
      to right,
      rgba(7, 9, 8, 0.96) 0%,
      rgba(7, 9, 8, 0.88) 34%,
      rgba(7, 9, 8, 0.45) 62%,
      rgba(7, 9, 8, 0.35) 100%
    ),
    linear-gradient(to bottom, rgba(7, 9, 8, 0.5) 0%, transparent 26%, rgba(7, 9, 8, 0.9) 100%);
}

.hero__inner {
  position: relative;
  max-width: 78rem;
  margin: 0 auto;
  padding: clamp(2rem, 5vw, 3.5rem) 0 clamp(3rem, 6vw, 4.5rem);
  min-height: min(88vh, 52rem);
  display: flex;
  flex-direction: column;
}

.hero__bar {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--hfm-space-2) var(--hfm-space-4);
  margin: 0;
  padding-top: var(--hfm-space-4);
  border-top: 1px solid var(--wl-rule);
}
.hero__bar-date {
  margin-left: auto;
  color: var(--wl-ink-2);
}

/* 文字块落在首屏下半，压在最暗的一带 */
.hero__text {
  margin-top: auto;
  max-width: 38rem;
}
.hero__brand {
  margin: 0;
  font-family: var(--hfm-font-display);
  font-weight: 500;
  font-size: clamp(2rem, 4.6vw, 3.5rem);
  line-height: 1.22;
  letter-spacing: 0.015em;
  color: #f6f4ee;
  text-shadow: 0 2px 24px rgba(7, 9, 8, 0.7);
}
.hero__statement {
  margin: clamp(1rem, 2.4vw, 1.5rem) 0 0;
  max-width: 26ch;
  font-family: var(--hfm-font-serif);
  font-size: clamp(1rem, 1.5vw, 1.3rem);
  line-height: 1.9;
  color: #e8e5dc;
  text-shadow: 0 1px 16px rgba(7, 9, 8, 0.8);
}

.hero__acts {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-3);
  margin: clamp(1.5rem, 3vw, 2rem) 0 0;
}
.hero__act {
  display: inline-flex;
  align-items: baseline;
  gap: var(--hfm-space-2);
  padding: 0.7rem 1.4rem;
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-base);
  letter-spacing: 0.05em;
  text-decoration: none;
  border: 1px solid var(--wl-mark);
  border-radius: 2px;
  background: var(--wl-mark);
  color: #14100b;
}
.hero__act--ghost {
  background: rgba(15, 18, 17, 0.6);
  color: #f6f4ee;
  border-color: rgba(239, 237, 230, 0.42);
}
.hero__act:focus-visible {
  outline: 2px solid var(--wl-mark-strong);
  outline-offset: 3px;
}
.hero__act-arr {
  transition: transform 220ms ease;
}
.hero__act:hover .hero__act-arr {
  transform: translateX(3px);
}

.hero__search {
  display: flex;
  align-items: center;
  gap: var(--hfm-space-2);
  margin: clamp(1.25rem, 2.5vw, 1.75rem) 0 0;
  max-width: 24rem;
  padding: 0 var(--hfm-space-3);
  background: rgba(11, 14, 13, 0.72);
  border: 1px solid rgba(239, 237, 230, 0.28);
  border-radius: 2px;
}
.home-search__input {
  flex: 1;
  min-width: 0;
  padding: var(--hfm-space-3) 0;
  font: inherit;
  font-size: var(--hfm-text-sm);
  color: #f6f4ee;
  background: transparent;
  border: none;
}
.home-search__input::placeholder {
  color: rgba(246, 244, 238, 0.62);
}
.home-search__input:focus {
  outline: none;
}
.hero__search:focus-within {
  border-color: var(--wl-mark);
}
.home-search__submit {
  min-height: 24px;
  padding: var(--hfm-space-2);
  font: inherit;
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.14em;
  color: var(--wl-mark-strong);
  background: none;
  border: none;
  cursor: pointer;
}
.home-search__submit:focus-visible {
  outline: 2px solid var(--wl-mark);
  outline-offset: 2px;
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

.hero__counts {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-4) var(--hfm-space-6);
  margin: clamp(1.75rem, 3.5vw, 2.5rem) 0 0;
}
.hero__count-value {
  margin: 0.15rem 0 0;
  font-family: var(--wl-latin);
  font-variant-numeric: tabular-nums;
  font-size: var(--hfm-text-lg);
  line-height: 1;
  color: #e8e5dc;
}

/* 入口带：落在实底上 */
.hero__entries {
  position: relative;
  max-width: 78rem;
  margin: 0 auto;
  border-top: 1px solid var(--wl-rule);
  border-bottom: 1px solid var(--wl-rule);
}

@media (max-width: 700px) {
  /* 窄屏：画像横铺会把人裁掉，改为偏上取景，压暗加重。 */
  .hero__bleed {
    height: 100%;
  }
  .hero__bleed-img {
    object-position: 62% 12%;
  }
  .hero__scrim {
    background: linear-gradient(
      to bottom,
      rgba(7, 9, 8, 0.72) 0%,
      rgba(7, 9, 8, 0.86) 42%,
      rgba(7, 9, 8, 0.97) 100%
    );
  }
  .hero__inner {
    min-height: 82vh;
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero__act-arr {
    transition: none;
  }
  .hero__act:hover .hero__act-arr {
    transform: none;
  }
}
</style>

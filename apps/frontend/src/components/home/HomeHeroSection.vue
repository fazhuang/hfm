<script setup lang="ts">
/**
 * HomeHeroSection — 首页首屏（HFM-UI-CONTRACT-v2 §3.1 段 01）。
 *
 * 骨架照参考图 `HFM-SY-CK.png`：整幅展厅影像铺底，左上英文小标，左下标题与
 * 定位、两个动作，右上引文卡，右下地点与题词，底部滚动提示与 `01 02 03`
 * 分页刻度。
 *
 * 影像是客户提供的皇甫谧画像（经公开媒体接口取原件）。参考图的首屏是一张
 * 展厅实景照，我们没有那一张 —— 用真画像而不是找一张别的图顶上。
 * 图为装饰（文字已表意），故 aria-hidden。
 *
 * 分页刻度是**静态位置标记**：本轮没做轮播，不把它做成能点的样子。
 */
import { computed } from 'vue'
import { HOME_HERO } from '../../data/homeProjection'
import { CORE_PERSON_PORTRAIT_MEDIA_ID } from '../../config/corePerson'
import { mediaBytesUrl } from '../../services/media'
import type { BlockData } from '../../composables/useHomeContractData'
import type { HomeProjection } from '../../types/public'

defineOptions({ name: 'HomeHeroSection' })

const props = defineProps<{ block?: BlockData<HomeProjection> | null }>()

/** 真实已发布计数；取不到就不渲染，不显示 0（契约 §5.6）。 */
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

const portraitUrl = mediaBytesUrl(CORE_PERSON_PORTRAIT_MEDIA_ID)
</script>

<template>
  <section id="home-hero" class="hero" aria-labelledby="home-hero-title">
    <div class="hero__bleed">
      <img class="hero__bleed-img" :src="portraitUrl" alt="" aria-hidden="true" />
      <div class="hero__scrim" aria-hidden="true"></div>
    </div>

    <div class="hero__inner">
      <div class="hero__top">
        <p class="hero__kicker">
          <span v-for="(line, i) in HOME_HERO.kicker" :key="line" :class="{ 'hero__kicker--first': i === 0 }">
            {{ line }}
          </span>
        </p>

        <figure class="hero__quote">
          <blockquote class="hero__quote-text">{{ HOME_HERO.quote.text }}</blockquote>
          <figcaption class="hero__quote-src">{{ HOME_HERO.quote.source }}</figcaption>
        </figure>
      </div>

      <div class="hero__text">
        <h1 id="home-hero-title" class="hero__title">{{ HOME_HERO.title }}</h1>
        <p class="hero__lede">{{ HOME_HERO.subtitle }}</p>

        <div class="hero__acts">
          <a class="hero__act" :href="HOME_HERO.primary[0].href">
            {{ HOME_HERO.primary[0].label }}
            <span class="hero__arr" aria-hidden="true">→</span>
          </a>
          <a class="hero__act hero__act--ghost" :href="HOME_HERO.primary[1].href">
            <span class="hero__play" aria-hidden="true">▶</span>
            {{ HOME_HERO.primary[1].label }}
          </a>
        </div>

        <dl v-if="counts" class="hero__counts">
          <div v-for="c in counts" :key="c.label" class="hero__count">
            <dt class="xl-label">{{ c.label }}</dt>
            <dd class="xl-num hero__count-value">{{ c.value }}</dd>
          </div>
        </dl>
      </div>

      <div class="hero__foot">
        <p class="hero__place">
          <span class="hero__place-zh">{{ HOME_HERO.place.zh }}</span>
          <span class="hero__place-en">{{ HOME_HERO.place.en }}</span>
        </p>
        <p class="hero__motto">
          <span v-for="m in HOME_HERO.motto" :key="m">{{ m }}</span>
        </p>
      </div>

      <div class="hero__scale">
        <p class="hero__scroll">
          <span>SCROLL</span>
          <span class="hero__scroll-line" aria-hidden="true"></span>
        </p>
        <p class="hero__pager" aria-hidden="true">
          <span v-for="(s, i) in HOME_HERO.scale" :key="s" :class="{ 'is-on': i === 0 }">{{ s }}</span>
        </p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero {
  position: relative;
  background: var(--wl-paper);
  color: var(--wl-ink);
  padding: 0 var(--hfm-space-6);
}

.hero__bleed {
  position: absolute;
  inset: 0 0 auto;
  height: min(92vh, 56rem);
  overflow: hidden;
  pointer-events: none;
}
.hero__bleed-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: 72% 18%;
  /* 画像底色是浅绢，直接铺会读成一张亮底的画，而不是展厅。
     压暗 + 略去饱和，让它落进暗场；文字对比度由下面这层 scrim 兜底。 */
  filter: brightness(0.5) contrast(1.08) saturate(0.72);
}
/* 压暗：左重（压字）右轻（留人物），下重（接下一段）。 */
.hero__scrim {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(
      to right,
      rgba(7, 9, 8, 0.92) 0%,
      rgba(7, 9, 8, 0.78) 34%,
      rgba(7, 9, 8, 0.5) 64%,
      rgba(7, 9, 8, 0.46) 100%
    ),
    linear-gradient(to bottom, rgba(7, 9, 8, 0.6) 0%, rgba(7, 9, 8, 0.2) 26%, rgba(7, 9, 8, 0.95) 100%);
}

.hero__inner {
  position: relative;
  max-width: 78rem;
  margin: 0 auto;
  padding: clamp(1.5rem, 3vw, 2.5rem) 0 clamp(1.5rem, 3vw, 2rem);
  min-height: min(92vh, 56rem);
  display: flex;
  flex-direction: column;
}

/* ---- 顶行：英文小标 │ 引文卡 ---- */
.hero__top {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--hfm-space-6);
}
.hero__kicker {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  margin: 0;
  font-family: var(--wl-latin);
  text-transform: uppercase;
  letter-spacing: 0.3em;
  font-size: 0.625rem;
  line-height: 1.7;
  color: rgba(239, 237, 230, 0.62);
}
.hero__kicker--first {
  margin-bottom: var(--hfm-space-2);
  font-size: 0.8125rem;
  letter-spacing: 0.34em;
  color: #f2f0ea;
}
.hero__quote {
  max-width: 19rem;
  margin: 0;
  padding: var(--hfm-space-4) var(--hfm-space-5);
  text-align: right;
  background: linear-gradient(to left, rgba(7, 9, 8, 0.72), rgba(7, 9, 8, 0));
}
.hero__quote-text {
  margin: 0;
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-base);
  line-height: 2;
  color: rgba(239, 237, 230, 0.9);
  text-shadow: 0 1px 14px rgba(7, 9, 8, 0.8);
}
.hero__quote-src {
  margin-top: var(--hfm-space-2);
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.08em;
  color: rgba(220, 171, 116, 0.92);
}

/* ---- 主文字块 ---- */
.hero__text {
  margin-top: auto;
  max-width: 40rem;
}
.hero__title {
  margin: 0;
  font-family: var(--hfm-font-display);
  font-weight: 500;
  font-size: clamp(2.25rem, 5.4vw, 4.25rem);
  line-height: 1.15;
  letter-spacing: 0.03em;
  color: #f6f4ee;
  text-shadow: 0 2px 26px rgba(7, 9, 8, 0.72);
}
.hero__lede {
  margin: clamp(1rem, 2.4vw, 1.5rem) 0 0;
  font-family: var(--hfm-font-serif);
  font-size: clamp(1rem, 1.5vw, 1.25rem);
  line-height: 1.9;
  color: #e8e5dc;
  text-shadow: 0 1px 16px rgba(7, 9, 8, 0.8);
}

.hero__acts {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--hfm-space-5);
  margin: clamp(1.5rem, 3vw, 2.25rem) 0 0;
}
.hero__act {
  display: inline-flex;
  align-items: center;
  gap: var(--hfm-space-3);
  padding: 0.75rem 1.5rem;
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-base);
  letter-spacing: 0.06em;
  text-decoration: none;
  color: #f6f4ee;
  border: 1px solid rgba(239, 237, 230, 0.42);
  border-radius: 2px;
  background: rgba(15, 18, 17, 0.55);
}
.hero__act:hover {
  border-color: var(--wl-mark);
  color: #fff;
}
.hero__act--ghost {
  padding-inline: 0;
  border-color: transparent;
  background: none;
}
.hero__play {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  font-size: 0.7rem;
  color: var(--wl-mark-strong);
  border: 1px solid rgba(220, 171, 116, 0.55);
  border-radius: 50%;
}
.hero__act:focus-visible {
  outline: 2px solid var(--wl-mark-strong);
  outline-offset: 3px;
}
.hero__arr {
  transition: transform 220ms ease;
}
.hero__act:hover .hero__arr {
  transform: translateX(3px);
}

.hero__counts {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-4) var(--hfm-space-7);
  margin: clamp(1.75rem, 3.5vw, 2.5rem) 0 0;
}
.hero__count-value {
  margin: 0.15rem 0 0;
  font-size: var(--hfm-text-lg);
  line-height: 1;
  color: #e8e5dc;
}

/* ---- 右下：地点与题词 ---- */
.hero__foot {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: flex-end;
  gap: var(--hfm-space-4) var(--hfm-space-8);
  margin-top: clamp(2rem, 4vw, 3rem);
  text-align: right;
}
.hero__place {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  margin: 0;
}
.hero__place-zh {
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-lg);
  letter-spacing: 0.16em;
  color: #f2f0ea;
}
.hero__place-en {
  font-family: var(--wl-latin);
  text-transform: uppercase;
  letter-spacing: 0.28em;
  font-size: 0.625rem;
  color: rgba(239, 237, 230, 0.55);
}
.hero__motto {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  margin: 0;
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.1em;
  color: rgba(239, 237, 230, 0.78);
}

/* ---- 底部：滚动提示 │ 分页刻度 ---- */
.hero__scale {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--hfm-space-6);
  margin-top: var(--hfm-space-6);
  padding-top: var(--hfm-space-4);
}
.hero__scroll {
  display: flex;
  align-items: center;
  gap: var(--hfm-space-3);
  margin: 0;
  font-family: var(--wl-latin);
  text-transform: uppercase;
  letter-spacing: 0.3em;
  font-size: 0.5625rem;
  color: rgba(239, 237, 230, 0.5);
}
.hero__scroll-line {
  display: block;
  width: 3.5rem;
  height: 1px;
  background: rgba(239, 237, 230, 0.28);
}
.hero__pager {
  display: flex;
  gap: var(--hfm-space-5);
  margin: 0;
  font-family: var(--wl-latin);
  font-variant-numeric: tabular-nums;
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.1em;
  color: rgba(239, 237, 230, 0.66);
}
.hero__pager .is-on {
  color: #f2f0ea;
  padding-bottom: 0.3rem;
  border-bottom: 1px solid var(--wl-mark);
}

@media (max-width: 900px) {
  .hero__quote {
    display: none;
  }
  .hero__foot {
    justify-content: flex-start;
    text-align: left;
  }
}

@media (max-width: 700px) {
  .hero__bleed {
    height: 100%;
  }
  .hero__bleed-img {
    object-position: 62% 12%;
  }
  .hero__scrim {
    background: linear-gradient(
      to bottom,
      rgba(7, 9, 8, 0.74) 0%,
      rgba(7, 9, 8, 0.88) 42%,
      rgba(7, 9, 8, 0.97) 100%
    );
  }
  .hero__inner {
    min-height: 84vh;
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero__arr {
    transition: none;
  }
  .hero__act:hover .hero__arr {
    transform: none;
  }
}
</style>

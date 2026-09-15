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
import { HOME_DOMAINS, HOME_HERO } from '../../data/homeProjection'
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
    <div class="hero__inner">
      <!-- 刻度带：边栏序号 · 拉丁标签 · 生卒 -->
      <p class="hero__bar">
        <span class="xl-index">00</span>
        <span class="xl-label">HUANGFU MI · DIGITAL HUMANITIES</span>
        <span class="xl-num hero__bar-date">公元 {{ dates }}</span>
      </p>

      <div class="hero__stage">
        <!-- 左：叙述与入口 -->
        <div class="hero__text">
          <h1 id="home-hero-title" class="hero__brand">{{ HOME_HERO.title }}</h1>
          <p class="hero__statement">{{ HOME_HERO.definition }}</p>
          <p class="hero__roles">西晋 · 医学家 · 文学家 · 史学家</p>

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

          <!-- T0 平台登记（真实已发布计数） -->
          <dl v-if="counts" class="hero__counts" data-source="backend">
            <div v-for="c in counts" :key="c.label" class="hero__count">
              <dt class="xl-label">{{ c.label }}</dt>
              <dd class="xl-num hero__count-value">{{ c.value }}</dd>
            </div>
          </dl>
        </div>

        <!-- 右：展柜。四件真实材料，一件一件立着，光从上方来。 -->
        <div class="hero__vitrine">
          <figure class="hero__plate hero__plate--primary">
            <img :src="portraitUrl" alt="皇甫谧画像（客户提供资料）" />
            <figcaption>
              <span class="hero__plate-title">皇甫谧</span>
              <span class="hero__plate-note">画像 · 客户提供资料</span>
            </figcaption>
          </figure>

          <div class="hero__plates">
            <figure class="hero__plate">
              <img src="/assets/jiayi/frag-macro.jpg" alt="《针灸甲乙经》书影局部" />
              <figcaption>
                <span class="hero__plate-title">《针灸甲乙经》</span>
                <span class="hero__plate-note">书影 · 客户授权资料</span>
              </figcaption>
            </figure>
            <figure class="hero__plate">
              <img src="/assets/jiayi/book-siku-leaf.jpg" alt="四库全书本书叶" />
              <figcaption>
                <span class="hero__plate-title">四库全书本</span>
                <span class="hero__plate-note">书叶 · 客户授权资料</span>
              </figcaption>
            </figure>
          </div>
        </div>
      </div>

      <!-- 四入口带（参考图 §2）：四个真实目的地，等分，细线分格。
           契约要求首页是「五个真实目的地的预览墙」，这一带就是那句话的形状。 -->
      <nav class="xl-entries hero__entries" aria-label="主要探索入口">
        <a
          v-for="d in HOME_DOMAINS.domains"
          :key="d.no"
          class="xl-entry"
          :href="d.href"
        >
          <svg class="xl-entry__mark" viewBox="0 0 32 32" fill="none" aria-hidden="true">
            <rect x="6" y="5" width="20" height="22" stroke="currentColor" stroke-width="1.2" />
            <path d="M11 11h10M11 16h10M11 21h6" stroke="currentColor" stroke-width="1.2" />
          </svg>
          <span class="xl-entry__en">{{ d.en }}</span>
          <p class="xl-entry__title">{{ d.title }}</p>
          <p class="xl-entry__note">{{ d.key }}</p>
          <span class="xl-entry__go">{{ d.cta }} →</span>
        </a>
      </nav>
    </div>
  </section>
</template>

<style scoped>
/* ==========================================================================
   Hero — 数字展厅入口
   ==========================================================================
   构图：左侧叙述与入口，右侧展柜。
   光从上方来（一道极弱的顶光，只给方向感），展板立在这个光里。
   圆角压到 0——展板是展板，不是卡片。
   ========================================================================== */

.hero {
  position: relative;
  background: var(--wl-paper);
  color: var(--wl-ink);
  padding: clamp(1.5rem, 4vw, 3rem) var(--hfm-space-6) clamp(3rem, 7vw, 6rem);
  overflow: hidden;
}
/* 顶光：不用大面积发光，只在画布上缘压一道极弱的暖光。 */
.hero::before {
  content: '';
  position: absolute;
  inset: 0 0 auto;
  height: 60%;
  background: radial-gradient(
    120% 100% at 50% 0%,
    var(--wl-glow) 0%,
    transparent 62%
  );
  pointer-events: none;
}
.hero__inner {
  position: relative;
  max-width: 78rem;
  margin: 0 auto;
}
/* 入口带压在 Hero 下缘，与首屏连成一体（参考图里它属于展厅入口，不是独立一段）。 */
.hero__entries {
  margin-top: clamp(3rem, 6vw, 5rem);
}

.hero__bar {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--hfm-space-2) var(--hfm-space-4);
  margin: 0 0 clamp(2rem, 5vw, 3.5rem);
  padding-top: var(--hfm-space-4);
  border-top: 1px solid var(--wl-rule);
}
.hero__bar-date {
  margin-left: auto;
  color: var(--wl-mute);
}

.hero__stage {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: clamp(2.5rem, 5vw, 4rem);
  align-items: start;
}
@media (min-width: 900px) {
  .hero__stage {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1.05fr);
    gap: clamp(2.5rem, 4vw, 4.5rem);
  }
}

/* ---- 左：叙述 ---- */
.hero__brand {
  margin: 0;
  font-family: var(--hfm-font-display);
  font-weight: 500;
  font-size: clamp(2rem, 4.4vw, 3.4rem);
  line-height: 1.24;
  letter-spacing: 0.015em;
  color: var(--wl-ink);
}
.hero__statement {
  margin: clamp(1.25rem, 3vw, 2rem) 0 0;
  max-width: 30ch;
  font-family: var(--hfm-font-serif);
  font-size: clamp(1rem, 1.4vw, 1.25rem);
  line-height: 1.95;
  color: var(--wl-ink-2);
}
.hero__roles {
  margin: var(--hfm-space-4) 0 0;
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.14em;
  color: var(--wl-mute);
}

.hero__acts {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-3);
  margin: clamp(1.75rem, 3.5vw, 2.5rem) 0 0;
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
  /* 主行动：展厅里的唯一实心件。青铜是这套配色里唯一的强调色。 */
  background: var(--wl-mark);
  color: #14100b;
}
.hero__act--ghost {
  background: transparent;
  color: var(--wl-ink);
  border-color: var(--wl-rule);
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
  margin: clamp(1.75rem, 3.5vw, 2.5rem) 0 0;
  max-width: 24rem;
  border-bottom: 1px solid var(--wl-rule);
}
.home-search__input {
  flex: 1;
  min-width: 0;
  padding: var(--hfm-space-2) 0;
  font: inherit;
  font-size: var(--hfm-text-sm);
  color: var(--wl-ink);
  background: transparent;
  border: none;
}
.home-search__input::placeholder {
  color: var(--wl-mute);
}
.home-search__input:focus {
  outline: none;
}
.home-search__submit {
  min-height: 24px;
  padding: var(--hfm-space-2);
  font: inherit;
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.14em;
  color: var(--wl-mark);
  background: none;
  border: none;
  cursor: pointer;
}
/* 仅对读屏可见。此前定义在本组件的样式块里，被整块替换时误删。 */
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
  gap: var(--hfm-space-5) var(--hfm-space-8);
  margin: clamp(2rem, 4vw, 3rem) 0 0;
  padding-top: var(--hfm-space-5);
  border-top: 1px solid var(--wl-rule);
}
.hero__count-value {
  margin: 0.2rem 0 0;
  font-size: clamp(1.5rem, 2.6vw, 2rem);
  line-height: 1;
  color: var(--wl-ink);
}

/* ---- 右：展柜 ----
   主展板立在前，两件副展板退后半步，刻度带压在底下。
   纵深靠**位移 + 明度差 + 阴影**，不靠发光。 */
/* 展柜：宽屏三件并排（画像立左，两件书影叠右），窄屏改为画像通栏 + 书影并排。
   宽屏不竖向堆叠是因为竖排会把首屏撑到 1400px 以上，读者第一屏看不到 CTA。
   移动端不沿用"缩小版桌面"：两窄列的标题会全部断行，等于没有可读性。 */
.hero__vitrine {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: var(--hfm-space-4);
  align-items: start;
}
.hero__plates {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--hfm-space-4);
}
@media (min-width: 700px) {
  .hero__vitrine {
    grid-template-columns: minmax(0, 1.55fr) minmax(0, 1fr);
  }
  .hero__plates {
    grid-column: 2;
    grid-row: 1;
    grid-template-columns: minmax(0, 1fr);
  }
}
.hero__plate {
  margin: 0;
  background: var(--wl-light);
  border: 1px solid var(--wl-rule);
  border-radius: 1px;
  overflow: hidden;
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.4),
    0 18px 40px -24px rgba(0, 0, 0, 0.9);
}
.hero__plate img {
  display: block;
  width: 100%;
  height: auto;
}
.hero__plate figcaption {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--hfm-space-3);
  padding: var(--hfm-space-3) var(--hfm-space-4);
  border-top: 1px solid var(--wl-rule);
}
/* 窄栏里侧排会断行；副展板的说明改为竖排。 */
.hero__plates .hero__plate figcaption {
  flex-direction: column;
  align-items: flex-start;
  gap: 0.2rem;
}
.hero__plate-title {
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-base);
  color: var(--wl-ink);
}
.hero__plate-note {
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.06em;
  color: var(--wl-mute);
}
/* 主展板：画像。它是整页唯一有史实地位的人物影像。 */
.hero__plate--primary {
  background: var(--wl-paper-2);
}
.hero__plate--primary img {
  aspect-ratio: 1 / 1;
  object-fit: cover;
  object-position: top center;
}
.hero__plates img {
  aspect-ratio: 3 / 2;
  object-fit: cover;
}
/* 副展板退后半步：略降明度、略缩，形成前后关系。 */
.hero__plates .hero__plate {
  opacity: 0.88;
  transition:
    opacity 320ms ease,
    transform 320ms ease;
}
.hero__plates .hero__plate:hover {
  opacity: 1;
  transform: translateY(-3px);
}

@media (prefers-reduced-motion: reduce) {
  .hero__act-arr,
  .hero__plates .hero__plate {
    transition: none;
  }
  .hero__act:hover .hero__act-arr,
  .hero__plates .hero__plate:hover {
    transform: none;
  }
}
</style>

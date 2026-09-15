<script setup lang="ts">
/**
 * HomeClassicsSection — 首页段 03「皇甫谧与《针灸甲乙经》」（契约 v2 §3.1 段 03）。
 *
 * 参考图 `HFM-SY-CK.png` 的这一段是：左文字 + 中实物书叶 + 右引文卡。
 * 书叶是客户的公版原刻影印（四库全书本），不是配图。
 *
 * 参考图右下有一对前后翻页控件。**这里没有做** —— 我们只有一张书叶图，
 * 做一对翻不动或翻出同一张的箭头等于假控件（契约 §5.6）。
 */
import { HOME_CLASSICS } from '../../data/homeProjection'

defineOptions({ name: 'HomeClassicsSection' })

const LEAF = '/assets/jiayi/book-siku-leaf.jpg'
</script>

<template>
  <section id="home-classics" class="xl-sec" aria-labelledby="home-classics-title">
    <div class="xl-inner">
      <div class="cls">
        <div class="cls__text">
          <h2 id="home-classics-title" class="cls__title">{{ HOME_CLASSICS.title }}</h2>
          <p class="cls__en">{{ HOME_CLASSICS.en }}</p>
          <p class="cls__body">{{ HOME_CLASSICS.body }}</p>
          <a class="cls__cta xl-cta" :href="HOME_CLASSICS.cta.href">
            {{ HOME_CLASSICS.cta.label }}
            <span class="xl-cta__arr" aria-hidden="true">→</span>
          </a>
        </div>

        <figure class="cls__plate">
          <p class="cls__spine" aria-hidden="true">针灸甲乙经</p>
          <img class="cls__leaf" :src="LEAF" alt="《针灸甲乙经》四库全书本原刻书叶" />
          <figcaption class="cls__caption">{{ HOME_CLASSICS.plateCaption }}</figcaption>
        </figure>

        <figure class="cls__quote">
          <blockquote>{{ HOME_CLASSICS.quote.text }}</blockquote>
          <figcaption>{{ HOME_CLASSICS.quote.source }}</figcaption>
        </figure>
      </div>
    </div>
  </section>
</template>

<style scoped>
.cls {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: clamp(2rem, 4vw, 3.5rem);
  align-items: start;
}
@media (min-width: 1000px) {
  .cls {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1.5fr) minmax(0, 0.8fr);
  }
}
.cls__text {
  align-self: start;
}

.cls__title {
  margin: 0;
  font-family: var(--hfm-font-heading);
  font-weight: 500;
  font-size: clamp(1.6rem, 3.4vw, 2.4rem);
  line-height: 1.35;
  color: var(--wl-ink);
}
.cls__en {
  margin: var(--hfm-space-3) 0 0;
  font-family: var(--wl-latin);
  text-transform: uppercase;
  letter-spacing: 0.26em;
  font-size: 0.625rem;
  color: var(--wl-mute);
}
.cls__body {
  margin: var(--hfm-space-5) 0 0;
  max-width: 40ch;
  font-size: var(--hfm-text-base);
  line-height: 2;
  color: var(--wl-ink-2);
}
/* 按钮外观来自 styles/home-scale.css 的 .xl-cta，这里只补本段的间距。 */
.cls__cta {
  margin-top: clamp(1.5rem, 3vw, 2rem);
}

/* ---- 书叶：竖排书名 + 影印 ---- */
.cls__plate {
  position: relative;
  display: flex;
  align-items: stretch;
  gap: var(--hfm-space-4);
  margin: 0;
  padding: clamp(1rem, 2vw, 1.5rem);
  background: var(--wl-light);
  box-shadow: inset 0 0 0 1px var(--wl-rule);
}
.cls__spine {
  margin: 0;
  writing-mode: vertical-rl;
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-lg);
  letter-spacing: 0.3em;
  color: var(--wl-ink-2);
  user-select: none;
}
.cls__leaf {
  flex: 1;
  min-width: 0;
  max-height: 34rem;
  object-fit: contain;
  object-position: center;
}
.cls__caption {
  position: absolute;
  inset: auto 0 0;
  padding: var(--hfm-space-3) var(--hfm-space-4);
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.08em;
  color: rgba(244, 242, 236, 0.72);
  background: linear-gradient(to top, rgba(7, 9, 8, 0.82), transparent);
}

/* ---- 引文卡 ---- */
.cls__quote {
  margin: 0;
  padding-left: var(--hfm-space-5);
  border-left: 1px solid var(--wl-mark);
}
.cls__quote blockquote {
  margin: 0;
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-lg);
  line-height: 2;
  color: var(--wl-ink);
}
.cls__quote figcaption {
  margin-top: var(--hfm-space-3);
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.08em;
  color: var(--wl-mark);
}

@media (max-width: 999px) {
  .cls__quote {
    padding-left: 0;
    border-left: none;
    border-top: 1px solid var(--wl-rule);
    padding-top: var(--hfm-space-5);
  }
}
</style>

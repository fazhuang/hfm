<script setup lang="ts">
/**
 * InteractiveView — 栏目页「互动」(/interactive)。
 *
 * HFM-UI-CONTRACT-v2 §3.2 栏目页骨架。**本页没有内容可放**：数字展厅、
 * 大屏与沉浸式内容在治理上仍是 DEFERRED（CR-019 / P1-DISPLAY），后端也没有
 * 任何互动投影。所以这一页如实说明现状与延后项，不放占位图、不放假交互
 * （契约 §5.6：不做假能力）。
 */
defineOptions({ name: 'InteractiveView' })

const DEFERRED: readonly { title: string; en: string; note: string }[] = [
  {
    title: '数字展厅',
    en: 'DIGITAL EXHIBITION',
    note: '按展线组织典籍、影像与实物，供线下大屏或触摸屏浏览。',
  },
  {
    title: '沉浸式内容',
    en: 'IMMERSIVE',
    note: '场景化的历史空间重建，属远期设想，需要专门的采集与制作。',
  },
  {
    title: '互动讲解',
    en: 'GUIDED TOURS',
    note: '围绕人物、典籍与传承脉络的导览式浏览路径。',
  },
]
</script>

<template>
  <div class="page">
    <section class="pg-hero">
      <div class="xl-inner">
        <p class="xl-label">INTERACTIVE</p>
        <h1 class="pg-hero__title">互动</h1>
        <p class="pg-hero__rule" aria-hidden="true"></p>
        <p class="pg-hero__lede">
          让典籍不只被读，也能被走近 —— 展厅、沉浸与导览，是这个栏目要放的东西。
        </p>
      </div>
    </section>

    <section class="xl-sec" aria-labelledby="ix-title">
      <div class="xl-inner">
        <header class="xl-head">
          <div class="xl-head__aside">
            <span class="xl-index">01</span>
            <span class="xl-label">STATUS</span>
          </div>
          <div>
            <h2 id="ix-title" class="xl-title">本栏目尚未开放</h2>
            <p class="xl-lede">
              互动内容需要线下设备与专门制作，尚未纳入建设范围。以下三项是已登记、尚未开工的方向。
            </p>
          </div>
        </header>

        <ul class="ix-list">
          <li v-for="d in DEFERRED" :key="d.en" class="ix-item">
            <p class="ix-item__en">{{ d.en }}</p>
            <h3 class="ix-item__title">{{ d.title }}</h3>
            <p class="ix-item__note">{{ d.note }}</p>
            <p class="ix-item__state">未开工</p>
          </li>
        </ul>

        <p class="ix-note">
          已经可用的浏览入口：<a href="/persons/ENT-PERSON-HFM-HUANGFUMI">人物</a> ·
          <a href="/jiayi">典籍</a> · <a href="/knowledge">知识图谱</a> ·
          <a href="/library">数字资源</a>。
        </p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.page {
  background: var(--wl-paper);
  color: var(--wl-ink);
}

/* 栏目页首屏版式在 styles/home-scale.css 的「栏目页首屏」段，全站共用。 */

.ix-list {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 0;
  margin: 0;
  padding: 0;
  list-style: none;
  border-top: 1px solid var(--wl-rule);
}
@media (min-width: 800px) {
  .ix-list {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
.ix-item {
  padding: var(--hfm-space-6) var(--hfm-space-6) var(--hfm-space-6) 0;
  border-bottom: 1px solid var(--wl-rule);
}
@media (min-width: 800px) {
  .ix-item {
    border-bottom: none;
    border-right: 1px solid var(--wl-rule);
    padding-inline: var(--hfm-space-6);
  }
  .ix-item:first-child {
    padding-left: 0;
  }
  .ix-item:last-child {
    border-right: none;
  }
}
.ix-item__en {
  margin: 0;
  font-family: var(--wl-latin);
  text-transform: uppercase;
  letter-spacing: 0.22em;
  font-size: 0.625rem;
  color: var(--wl-mute);
}
.ix-item__title {
  margin: var(--hfm-space-3) 0 0;
  font-family: var(--hfm-font-heading);
  font-weight: 500;
  font-size: var(--hfm-text-xl);
  color: var(--wl-ink);
}
.ix-item__note {
  margin: var(--hfm-space-3) 0 0;
  font-size: var(--hfm-text-sm);
  line-height: 1.85;
  color: var(--wl-ink-2);
}
.ix-item__state {
  margin: var(--hfm-space-4) 0 0;
  font-family: var(--wl-latin);
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.18em;
  color: var(--wl-mark);
}

.ix-note {
  margin: clamp(2.5rem, 5vw, 3.5rem) 0 0;
  padding-top: var(--hfm-space-5);
  border-top: 1px solid var(--wl-rule);
  font-size: var(--hfm-text-sm);
  line-height: 1.9;
  color: var(--wl-mute);
}
.ix-note a {
  color: var(--wl-ink-2);
  text-decoration: underline;
  text-underline-offset: 3px;
}
.ix-note a:hover {
  color: var(--wl-mark-strong);
}
</style>

<script setup lang="ts">
/**
 * HomeLifeSection — Section 02 (一生). 《刻度》 ledger voice:
 * ruled header + four numbered life entries + the source register.
 */
import { HOME_LIFE, HOME_CHAPTERS } from '../../data/homeProjection'

defineOptions({ name: 'HomeLifeSection' })
</script>

<template>
  <section id="home-life" class="xl-sec" aria-labelledby="home-life-title">
    <div class="xl-inner">
      <header class="xl-head">
        <div class="xl-head__aside">
          <span class="xl-index">{{ HOME_CHAPTERS.life.no }}</span>
          <span class="xl-label">Biography</span>
        </div>
        <div>
          <h2 id="home-life-title" class="xl-title">{{ HOME_LIFE.headline }}</h2>
          <p class="xl-lede">{{ HOME_LIFE.intro }}</p>
        </div>
      </header>

      <figure class="life__manuscript" aria-hidden="true">
        <img src="/assets/jiayi/frag-band1.jpg" alt="" aria-hidden="true" />
      </figure>

      <ol class="life__stages xl-rows">
        <li v-for="(stage, i) in HOME_LIFE.stages" :key="stage.title" class="xl-row life__stage">
          <span class="xl-row__index">{{ String(i + 1).padStart(2, '0') }}</span>
          <div class="xl-row__body">
            <h3 class="life__stage-name">{{ stage.title }}</h3>
            <p class="life__stage-note">{{ stage.note }}</p>
          </div>
        </li>
      </ol>

      <div class="life__foot">
        <ul class="life__items">
          <li v-for="item in HOME_LIFE.items" :key="item.title" class="life__item">
            <a class="life__item-link" :href="item.href">{{ item.title }}</a>
            <span class="life__item-meta">{{ item.meta }}</span>
          </li>
        </ul>
        <div class="life__aside">
          <p class="life__dates"><span class="xl-label">Dates</span> {{ HOME_LIFE.dates }}</p>
          <a class="life__cta xl-go" :href="HOME_LIFE.cta.href">
            {{ HOME_LIFE.cta.label }}
            <span class="life__cta-arr xl-go__arr" aria-hidden="true">→</span>
          </a>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.life__manuscript {
  margin: 0 0 var(--hfm-space-8);
  border: 1px solid var(--wl-rule);
  overflow: hidden;
}
.life__manuscript img {
  display: block;
  width: 100%;
  height: clamp(9rem, 22vw, 15rem);
  object-fit: cover;
  filter: sepia(0.12) saturate(0.85) contrast(1.02);
}
.life__stage-name {
  margin: 0 0 var(--hfm-space-2);
  font-family: var(--hfm-font-heading);
  font-size: var(--hfm-text-2xl);
  font-weight: 500;
  color: var(--wl-ink);
}
.life__stage-note {
  margin: 0;
  max-width: 52ch;
  font-size: var(--hfm-text-base);
  line-height: 1.9;
  color: var(--wl-ink-2);
}
.life__foot {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--hfm-space-8);
  margin-top: var(--hfm-space-8);
}
.life__items {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-8);
}
.life__item {
  display: flex;
  flex-direction: column;
  gap: var(--hfm-space-1);
}
.life__item-link {
  font-size: var(--hfm-text-base);
  color: var(--wl-ink);
  text-decoration: none;
  border-bottom: 1px solid var(--wl-rule);
  padding-bottom: 2px;
}
.life__item-link:hover {
  color: var(--wl-mark);
  border-color: var(--wl-mark);
}
.life__item-meta {
  font-family: var(--wl-latin);
  font-size: var(--hfm-text-xs);
  color: var(--wl-mute);
}
.life__aside {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: var(--hfm-space-3);
}
.life__dates {
  margin: 0;
  font-family: var(--wl-latin);
  font-variant-numeric: tabular-nums;
  font-size: var(--hfm-text-sm);
  color: var(--wl-ink-2);
}
@media (max-width: 599px) {
  .life__aside {
    align-items: flex-start;
  }
}
</style>

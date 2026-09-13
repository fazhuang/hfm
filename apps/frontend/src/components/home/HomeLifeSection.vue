<script setup lang="ts">
/**
 * HomeLifeSection — homepage Section 02 (一生 / the life).
 *
 * REDESIGN: editorial life narrative on the warm canvas — a head (eyebrow,
 * H2, intro, dates), an ordered four-stage life axis, the source-entry list
 * (其传 / 其言 / 后论), and a person-archive CTA. Replaces the previous
 * absolutely-positioned timeline composition.
 *
 * CONTRACT PRESERVED (ui03_home.spec.ts): <section id="home-life"> with the
 * single H2 「从带经而农，到著书传世。」; real CTA targets
 * /persons/ENT-PERSON-HFM-HUANGFUMI, /reader/qichuan, /yan, /reader/houlun.
 * DATA: HOME_LIFE (CORE_PERSON_LIFE_PHASES) — no new facts.
 */
import { HOME_LIFE, HOME_CHAPTERS } from '../../data/homeProjection'

defineOptions({ name: 'HomeLifeSection' })
</script>

<template>
  <section id="home-life" class="life" aria-labelledby="home-life-title">
    <div class="home-life__inner life__inner">
      <header class="life__head">
        <p class="life__eyebrow">
          <span class="life__no">{{ HOME_CHAPTERS.life.no }}</span>{{ HOME_CHAPTERS.life.label }}
        </p>
        <h2 id="home-life-title" class="life__title">{{ HOME_LIFE.headline }}</h2>
        <p class="life__intro">{{ HOME_LIFE.intro }}</p>
      </header>

      <figure class="life__manuscript" aria-hidden="true">
        <img src="/assets/jiayi/frag-band1.jpg" alt="" aria-hidden="true" />
      </figure>

      <ol class="life__stages">
        <li v-for="(stage, i) in HOME_LIFE.stages" :key="stage.title" class="life__stage">
          <p class="life__stage-no" aria-hidden="true">{{ String(i + 1).padStart(2, '0') }}</p>
          <h3 class="life__stage-name">{{ stage.title }}</h3>
          <p class="life__stage-note">{{ stage.note }}</p>
        </li>
      </ol>

      <div class="life__foot">
        <ul class="life__items">
          <li v-for="item in HOME_LIFE.items" :key="item.title" class="life__item">
            <a class="life__item-link" :href="item.href">{{ item.title }}</a>
            <span class="life__item-meta">{{ item.meta }}</span>
          </li>
        </ul>
        <p class="life__dates">
          <span class="life__dates-label">生卒</span>{{ HOME_LIFE.dates }}
        </p>
        <a class="life__cta" :href="HOME_LIFE.cta.href">
          {{ HOME_LIFE.cta.label }} <span class="life__cta-arr" aria-hidden="true">→</span>
        </a>
      </div>
    </div>
  </section>
</template>

<style scoped>
.life {
  background: var(--hfm-color-surface);
  padding: var(--hfm-space-24) var(--hfm-space-6);
}
.life__inner {
  max-width: var(--hfm-content-max);
  margin: 0 auto;
}
.life__head {
  max-width: 44rem;
  margin-bottom: var(--hfm-space-16);
}
.life__eyebrow {
  margin: 0 0 var(--hfm-space-4);
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.4em;
  color: var(--hfm-color-heritage);
}
.life__no {
  color: var(--hfm-color-text-muted);
  margin-right: 0.5em;
}
.life__title {
  margin: 0 0 var(--hfm-space-4);
  font-family: var(--hfm-font-heading);
  font-weight: 500;
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  line-height: var(--hfm-leading-tight);
  color: var(--hfm-color-text);
}
.life__intro {
  margin: 0;
  font-size: var(--hfm-text-lg);
  line-height: var(--hfm-leading-normal);
  color: var(--hfm-color-text-secondary);
}
.life__manuscript {
  margin: 0 0 var(--hfm-space-12);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  overflow: hidden;
}
.life__manuscript img {
  display: block;
  width: 100%;
  height: clamp(10rem, 24vw, 16rem);
  object-fit: cover;
  filter: sepia(0.14) saturate(0.9) contrast(1.02);
}

/* four-stage life axis */
.life__stages {
  list-style: none;
  margin: 0 0 var(--hfm-space-16);
  padding: 0;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--hfm-space-8);
}
.life__stage {
  padding-top: var(--hfm-space-5);
  border-top: 1px solid var(--hfm-color-border-strong);
}
.life__stage-no {
  margin: 0 0 var(--hfm-space-3);
  font-family: var(--hfm-font-numeric);
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-heritage);
}
.life__stage-name {
  margin: 0 0 var(--hfm-space-2);
  font-family: var(--hfm-font-heading);
  font-size: var(--hfm-text-xl);
  font-weight: 500;
  color: var(--hfm-color-text);
}
.life__stage-note {
  margin: 0;
  font-size: var(--hfm-text-sm);
  line-height: var(--hfm-leading-normal);
  color: var(--hfm-color-text-muted);
}

/* source entries + cta */
.life__foot {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--hfm-space-8);
  padding-top: var(--hfm-space-8);
  border-top: 1px solid var(--hfm-color-border);
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
  color: var(--hfm-color-text);
  text-decoration: none;
  border-bottom: 1px solid var(--hfm-color-border-strong);
  padding-bottom: 2px;
}
.life__item-link:hover {
  color: var(--hfm-color-accent);
  border-color: var(--hfm-color-accent);
}
.life__item-meta {
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}
.life__dates {
  margin: 0;
  font-family: var(--hfm-font-numeric);
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-muted);
}
.life__dates-label {
  margin-right: var(--hfm-space-2);
  letter-spacing: 0.2em;
}
.life__cta {
  min-height: 24px;
  display: inline-flex;
  align-items: center;
  gap: var(--hfm-space-2);
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.1em;
  color: var(--hfm-color-accent);
  text-decoration: none;
}
.life__cta-arr {
  transition: transform 0.18s ease;
}
.life__cta:hover .life__cta-arr {
  transform: translateX(3px);
}

@media (max-width: 1023px) {
  .life__stages {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 599px) {
  .life {
    padding: var(--hfm-space-16) var(--hfm-space-4);
  }
  .life__stages {
    grid-template-columns: 1fr;
  }
  .life__foot {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>

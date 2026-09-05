<script setup lang="ts">
/**
 * HomeLifeSection — homepage Section 02 (一生 / Life L2).
 *
 * CF-07 STRUCTURAL SHELL ONLY. Semantic <section id="home-life"> root + h2 +
 * the verified life-phase stages (CORE_PERSON_LIFE_PHASES) + person-archive
 * entries. No final visual fidelity (no manuscript band / axis geometry) —
 * that belongs to the visual work packages.
 */
import { HOME_LIFE, HOME_CHAPTERS } from '../../data/homeProjection'

defineOptions({ name: 'HomeLifeSection' })

const stages = HOME_LIFE.stages
const items = HOME_LIFE.items ?? []
</script>

<template>
  <section id="home-life" class="home-section home-section--life" aria-labelledby="home-life-title">
    <p class="hfm-eyebrow">
      <span class="home-chapter__no">{{ HOME_CHAPTERS.life.no }}</span
      >{{ HOME_CHAPTERS.life.label }}
    </p>
    <h2 id="home-life-title" class="home-section__title">
      {{ HOME_LIFE.headline }}
    </h2>
    <p class="home-section__lede">
      {{ HOME_LIFE.intro }}
    </p>

    <ol class="home-life__stages" aria-label="生平四阶段">
      <li v-for="(stage, index) in stages" :key="stage.title" class="home-life__stage">
        <span class="home-life__index">{{ String(index + 1).padStart(2, '0') }}</span>
        <h3 class="home-life__stage-title">
          {{ stage.title }}
        </h3>
        <p class="home-life__stage-note">
          {{ stage.note }}
        </p>
      </li>
    </ol>

    <ul class="home-life__archive" aria-label="人物档案入口">
      <li v-for="item in items" :key="item.title" class="home-life__row">
        <a class="home-life__row-title" :href="item.href">{{ item.title }}</a>
        <span v-if="item.meta" class="home-life__row-meta">{{ item.meta }}</span>
      </li>
    </ul>

    <p class="home-cta-row">
      <a class="home-cta" :href="HOME_LIFE.cta.href">{{ HOME_LIFE.cta.label }} →</a>
    </p>
  </section>
</template>

<style scoped>
/* CF-07 STRUCTURAL SHELL ONLY. */
.home-chapter__no {
  margin-right: 0.6em;
  color: var(--hfm-color-text-muted);
  font-variant-numeric: tabular-nums;
}

.home-section--life {
  padding: var(--hfm-space-12) var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
}

.home-life__stages {
  list-style: none;
  margin: var(--hfm-space-6) 0 0;
  padding: 0;
}

.home-life__stage {
  display: grid;
  grid-template-columns: auto 1fr;
  column-gap: var(--hfm-space-4);
  padding: var(--hfm-space-3) 0;
  border-top: 1px solid var(--hfm-color-border);
}

.home-life__stage-title {
  margin: 0;
}

.home-life__stage-note {
  grid-column: 2;
  margin: var(--hfm-space-1) 0 0;
  color: var(--hfm-color-text-secondary);
}

.home-life__index {
  color: var(--hfm-color-text-muted);
  font-family: var(--hfm-font-numeric, var(--hfm-font-sans));
  font-variant-numeric: tabular-nums;
}

.home-life__archive {
  list-style: none;
  margin: var(--hfm-space-6) 0 0;
  padding: 0;
}

.home-life__row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-3);
  align-items: baseline;
  padding: var(--hfm-space-2) 0;
  border-top: 1px solid var(--hfm-color-border);
}

.home-life__row-title {
  font-weight: 600;
  text-decoration: none;
}

.home-life__row-meta {
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
}

.home-cta-row {
  margin: var(--hfm-space-5) 0 0;
}

.home-cta {
  display: inline-block;
  padding: var(--hfm-space-1) var(--hfm-space-4);
  border: 1px solid var(--hfm-color-accent);
  border-radius: var(--hfm-radius-sm);
  color: var(--hfm-color-accent);
  font-weight: 600;
  text-decoration: none;
}

.home-cta:hover {
  background: var(--hfm-color-accent);
  color: var(--hfm-color-on-accent);
}
</style>

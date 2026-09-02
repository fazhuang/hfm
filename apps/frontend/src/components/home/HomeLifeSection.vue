<script setup lang="ts">
/**
 * HomeLifeSection — accepted homepage Section 02 (Life L2 Refined).
 *
 * WP-02A STRUCTURAL SHELL ONLY. Semantic root + h2 + derived life stages.
 * No final visual fidelity (no manuscript band asset, no vertical-axis absolute
 * geometry, no fixed 1240 height) — that belongs to WP-03.
 */
import { HOME_LIFE, HOME_CHAPTERS } from '../../data/homeProjection'

defineOptions({ name: 'HomeLifeSection' })

const stages = HOME_LIFE.stages
</script>

<template>
  <section id="home-life" class="home-section home-section--life" aria-labelledby="home-life-title">
    <p class="home-eyebrow">
      <span class="home-eyebrow__no">{{ HOME_CHAPTERS.life.no }}</span
      >{{ HOME_CHAPTERS.life.label }}
    </p>
    <h2 id="home-life-title" class="home-section__title">{{ HOME_LIFE.headline }}</h2>
    <p class="home-section__lede">{{ HOME_LIFE.intro }}</p>

    <ol class="home-life__stages">
      <li v-for="(stage, index) in stages" :key="stage.title" class="home-life__stage">
        <span class="home-life__index">{{ String(index + 1).padStart(2, '0') }}</span>
        <h3 class="home-life__stage-title">{{ stage.title }}</h3>
        <p class="home-life__stage-note">{{ stage.note }}</p>
      </li>
    </ol>
  </section>
</template>

<style scoped>
/* WP-02A STRUCTURAL SHELL ONLY. */
.home-section--life {
  padding: var(--hfm-space-12) var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
}
.home-life__stages {
  list-style: none;
  padding: 0;
  margin: var(--hfm-space-6) 0;
}
.home-life__stage {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-3);
  padding: var(--hfm-space-4) 0;
  border-top: 1px solid var(--hfm-color-border);
}
.home-life__index {
  color: var(--hfm-color-text-muted);
  font-variant-numeric: tabular-nums;
}
.home-life__stage-title {
  margin: 0;
}
</style>

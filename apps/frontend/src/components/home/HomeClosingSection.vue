<script setup lang="ts">
/**
 * HomeClosingSection — Section 08 (结语). 《刻度》 ledger voice:
 * a ruled close carrying the platform identity as a NON-heading signature.
 * Not a footer — AppFooter owns the global footer.
 */
import { HOME_CLOSING, HOME_CHAPTERS } from '../../data/homeProjection'
import XlScaleBand from './XlScaleBand.vue'

defineOptions({ name: 'HomeClosingSection' })
</script>

<template>
  <section id="home-closing" class="closing xl-sec--dark" aria-label="平台结语">
    <div class="closing__inner">
      <p class="closing__bar">
        <span class="xl-index">{{ HOME_CHAPTERS.closing.no }}</span>
        <span class="xl-label">Colophon</span>
      </p>
      <XlScaleBand class="closing__band" />
      <p class="home-closing__name closing__name">{{ HOME_CLOSING.name }}</p>
      <p class="closing__subtitle">{{ HOME_CLOSING.subtitle }}</p>
    </div>
  </section>
</template>

<style scoped>
.closing {
  color: var(--wl-ink);
  padding: clamp(4rem, 10vw, 9rem) var(--hfm-space-6);
}
.closing__inner {
  max-width: 78rem;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}
.closing__bar {
  display: flex;
  gap: var(--hfm-space-6);
  margin: 0 0 var(--hfm-space-8);
  padding-top: var(--hfm-space-4);
  border-top: 1px solid var(--wl-rule);
  width: 100%;
  justify-content: center;
}
.closing__band {
  color: var(--wl-ink);
  width: min(38rem, 100%);
  margin-bottom: var(--hfm-space-8);
}
.closing__name {
  margin: 0;
  font-family: var(--hfm-font-display);
  font-weight: 500;
  font-size: clamp(2rem, 6vw, 4rem);
  line-height: 1.2;
  letter-spacing: 0.02em;
  color: var(--wl-ink);
}
.closing__subtitle {
  margin: var(--hfm-space-5) 0 0;
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.18em;
  color: var(--wl-mute);
}
</style>

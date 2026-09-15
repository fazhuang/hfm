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
  <section
    id="home-closing"
    class="xl-sec xl-sec--close"
    aria-label="平台结语"
    data-source="static"
  >
    <div class="xl-inner">
      <div class="xl-close">
        <p class="xl-close__quote">
          传统不是过去的遗存，<br />而是理解未来的一种方式。
        </p>
        <p class="xl-close__en">The Past Is A Resource For The Future</p>
        <p class="home-closing__name closing__name">{{ HOME_CLOSING.name }}</p>
        <p class="closing__subtitle">{{ HOME_CLOSING.subtitle }}</p>
        <a class="home-closing__act xl-close__act" href="/search">
          检索全站已发布内容
          <span class="home-closing__act-arr xl-go__arr" aria-hidden="true">→</span>
        </a>
      </div>
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
.closing__search-entry {
  margin: var(--hfm-space-6) 0 0;
}
.closing__subtitle {
  margin: var(--hfm-space-5) 0 0;
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.18em;
  color: var(--wl-mute);
}
</style>

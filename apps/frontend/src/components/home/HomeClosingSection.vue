<script setup lang="ts">
/**
 * HomeClosingSection — homepage Section 08 (quiet institutional close).
 *
 * REDESIGN: keeps the accepted composition (eyebrow → thin rule → platform
 * identity → subtitle, centered, generous negative space) but drops the fixed
 * 900px artboard and negative-margin hacks for a responsive, token-driven
 * close consistent with the redesigned hero.
 *
 * CONTRACT PRESERVED (ui03_home.spec.ts): <section id="home-closing">,
 * aria-label 平台结语, and .home-closing__name = 皇甫谧人文数字平台 as a
 * NON-heading <p> (the hero H1 is the only heading carrying the brand). This
 * is not a footer — AppFooter owns the global footer.
 */
import { HOME_CLOSING, HOME_CHAPTERS } from '../../data/homeProjection'

defineOptions({ name: 'HomeClosingSection' })
</script>

<template>
  <section id="home-closing" class="closing" aria-label="平台结语">
    <div class="closing__inner">
      <p class="closing__eyebrow">
        <span class="closing__no">{{ HOME_CHAPTERS.closing.no }}</span
        >{{ HOME_CHAPTERS.closing.label }}
      </p>

      <div class="closing__rule" aria-hidden="true"></div>

      <!-- platform identity — quiet signature (non-heading, P1-01) -->
      <p class="home-closing__name closing__name">{{ HOME_CLOSING.name }}</p>
      <p class="closing__subtitle">{{ HOME_CLOSING.subtitle }}</p>
    </div>
  </section>
</template>

<style scoped>
.closing {
  background: var(--hfm-color-canvas);
  padding: var(--hfm-space-32) var(--hfm-space-6);
}
.closing__inner {
  max-width: var(--hfm-content-max);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}
.closing__eyebrow {
  margin: 0 0 var(--hfm-space-12);
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.42em;
  color: var(--hfm-color-heritage);
}
.closing__no {
  color: var(--hfm-color-text-muted);
  margin-right: 0.5em;
}
.closing__rule {
  width: 100%;
  max-width: 40rem;
  height: 1px;
  background: var(--hfm-color-border);
}
.closing__name {
  margin: var(--hfm-space-12) 0 0;
  font-family: var(--hfm-font-display);
  font-weight: 500;
  font-size: clamp(2rem, 6vw, 4.25rem);
  line-height: 1.16;
  letter-spacing: 0.02em;
  color: var(--hfm-color-text);
}
.closing__subtitle {
  margin: var(--hfm-space-6) 0 0;
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.22em;
  color: var(--hfm-color-text-muted);
}
@media (max-width: 599px) {
  .closing {
    padding: var(--hfm-space-24) var(--hfm-space-4);
  }
  .closing__subtitle {
    letter-spacing: 0.14em;
  }
}
</style>

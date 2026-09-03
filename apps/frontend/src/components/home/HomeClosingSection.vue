<script setup lang="ts">
/**
 * HomeClosingSection — accepted homepage Section 08 (Closing S8-A) + AppFooter integration boundary.
 *
 * WP-05: production visual fidelity for the frozen
 * HFM_HOMEPAGE_SECTION08_VISUAL_BASELINE_S8A composition — the quiet
 * institutional close. 叙事至此，归于平台. Reduced density: a single thin rule
 * announces the end of the long-form narrative; then the large platform
 * identity + the approved subtitle, with strong negative space. No spectacle.
 *
 * OWNERSHIP (WP-01/WP-02 decision): HomeClosingSection owns ONLY the accepted
 * closing composition (platform identity + subtitle + quiet transition). It does
 * NOT duplicate AppFooter's global responsibilities — co-construction signature,
 * positioning statement, legal navigation, copyright. Those remain the single
 * semantic <footer> (AppFooter), which renders immediately after this section.
 *
 * The platform identity is a NON-heading <p>: the single H1 (hero) is the only
 * heading carrying 皇甫谧人文数字平台, and the accepted closing register is a
 * signature, not a heading (P1-01). The section is landmarked via aria-label.
 */
import { HOME_CLOSING, HOME_CHAPTERS } from '../../data/homeProjection'

defineOptions({ name: 'HomeClosingSection' })
</script>

<template>
  <section id="home-closing" class="home-section home-section--closing" aria-label="平台结语">
    <div class="home-closing__grain" aria-hidden="true"></div>
    <div class="home-closing__inner">
      <p class="home-eyebrow home-closing__eyebrow">
        <span class="home-eyebrow__no">{{ HOME_CHAPTERS.closing.no }}</span
        >{{ HOME_CHAPTERS.closing.label }}
      </p>

      <!-- a single thin rule announces the end of the narrative -->
      <div class="home-closing__rule" aria-hidden="true"></div>

      <!-- platform identity — quiet signature (non-heading, P1-01) -->
      <p class="home-closing__name">{{ HOME_CLOSING.name }}</p>
      <p class="home-closing__subtitle">{{ HOME_CLOSING.subtitle }}</p>
    </div>
  </section>
</template>

<style scoped>
/* ===== Section 08 Closing (S8-A) — production fidelity, 1440×900 ===== */
.home-section--closing {
  position: relative;
  overflow: hidden;
  min-height: 900px;
  background:
    radial-gradient(
      1000px 640px at 86% -10%,
      color-mix(in srgb, var(--hfm-color-heritage) 5%, transparent) 0%,
      transparent 62%
    ),
    radial-gradient(
      720px 520px at -4% 116%,
      color-mix(in srgb, var(--hfm-color-accent) 4%, transparent) 0%,
      transparent 60%
    ),
    var(--hfm-color-canvas);
}
.home-closing__grain {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.04;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='240' height='240'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
.home-closing__inner {
  position: relative;
  max-width: 1272px;
  margin: 0 auto;
  width: 100%;
  height: 900px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}
.home-closing__eyebrow {
  position: absolute;
  left: 50%;
  top: 120px;
  transform: translateX(-50%);
  margin: 0;
}
.home-closing__rule {
  width: 640px;
  max-width: 80%;
  height: 1px;
  background: var(--hfm-color-border);
}
.home-closing__name {
  margin: 42px 0 0;
  font-family: var(--hfm-font-heading);
  font-weight: 500;
  font-size: 68px;
  line-height: 1.16;
  letter-spacing: 0.02em;
  color: var(--hfm-color-text);
}
.home-closing__subtitle {
  margin: 26px 0 0;
  font-size: 14px;
  letter-spacing: 0.22em;
  color: var(--hfm-color-text-muted);
}

/* ===== Mobile flow (max-width 1199px) ===== */
@media (max-width: 1199px) {
  .home-section--closing {
    min-height: 0;
  }
  .home-closing__inner {
    height: auto;
    min-height: 640px;
    padding: 120px 24px 96px;
  }
  .home-closing__name {
    font-size: clamp(34px, 9.5vw, 64px);
  }
  .home-closing__subtitle {
    font-size: 12.5px;
    letter-spacing: 0.18em;
    max-width: 90%;
  }
}

</style>

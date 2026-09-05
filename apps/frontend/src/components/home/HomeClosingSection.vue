<script setup lang="ts">
/**
 * HomeClosingSection — homepage Section 08 (Institutional Close S8-A).
 *
 * CF-07 STRUCTURAL SHELL ONLY.
 *
 * OWNERSHIP (accepted architecture): HomeClosingSection owns ONLY the closing
 * composition (platform identity + subtitle). It does NOT duplicate the
 * global semantic <footer>'s responsibilities — co-construction signature,
 * positioning statement, legal navigation (关于平台 / 版权与免责声明 /
 * 隐私说明) and copyright stay in AppFooter, which PublicLayout renders after
 * this section. No second © / legal nav / footer here.
 *
 * The platform identity is a NON-heading <p>: the single H1 (hero) is the
 * only heading carrying 皇甫谧人文数字平台. The section is landmarked via
 * aria-label="平台结语".
 */
import { HOME_CLOSING, HOME_CHAPTERS } from '../../data/homeProjection'

defineOptions({ name: 'HomeClosingSection' })
</script>

<template>
  <section id="home-closing" class="home-section home-section--closing" aria-label="平台结语">
    <p class="hfm-eyebrow">
      <span class="home-chapter__no">{{ HOME_CHAPTERS.closing.no }}</span
      >{{ HOME_CHAPTERS.closing.label }}
    </p>
    <p class="home-closing__name">
      {{ HOME_CLOSING.name }}
    </p>
    <p class="home-closing__subtitle">
      {{ HOME_CLOSING.subtitle }}
    </p>
  </section>
</template>

<style scoped>
/* CF-07 STRUCTURAL SHELL ONLY. The AppFooter renders immediately after this
   section (PublicLayout); no footer-level content is duplicated here. */
.home-chapter__no {
  margin-right: 0.6em;
  color: var(--hfm-color-text-muted);
  font-variant-numeric: tabular-nums;
}

.home-section--closing {
  padding: var(--hfm-space-16) var(--hfm-space-6);
  text-align: center;
}

.home-closing__name {
  font-family: var(--hfm-font-display);
  font-size: var(--hfm-text-2xl);
  margin: var(--hfm-space-2) 0;
}

.home-closing__subtitle {
  color: var(--hfm-color-text-muted);
  margin: 0;
}
</style>

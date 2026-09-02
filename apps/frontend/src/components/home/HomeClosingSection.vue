<script setup lang="ts">
/**
 * HomeClosingSection — accepted homepage Section 08 (Closing S8-A) + AppFooter integration boundary.
 *
 * WP-02 STRUCTURAL / ARCHITECTURE ONLY.
 *
 * OWNERSHIP (WP-01 decision): HomeClosingSection owns ONLY the accepted closing
 * composition (large platform identity + subtitle + quiet transition). It must
 * NOT duplicate AppFooter's global responsibilities — co-construction signature,
 * positioning statement, legal navigation (关于平台/版权与免责声明/隐私说明),
 * copyright line. Those remain the single semantic <footer> (AppFooter).
 *
 * The applied disposition: this section closes the narrative; AppFooter supplies
 * the global institutional/legal footer right after it. No second © / legal nav.
 */
import { HOME_CLOSING, HOME_CHAPTERS } from '../../data/homeProjection'

defineOptions({ name: 'HomeClosingSection' })
</script>

<template>
  <section id="home-closing" class="home-section home-section--closing" aria-label="平台结语">
    <p class="home-eyebrow">
      <span class="home-eyebrow__no">{{ HOME_CHAPTERS.closing.no }}</span
      >{{ HOME_CHAPTERS.closing.label }}
    </p>
    <!-- platform identity as a NON-heading signature — the single H1 (hero) is the only
         heading carrying 皇甫谧人文数字平台; a closing <p> avoids a duplicate accessible
         heading name (P1-01). The section is landmarked via aria-label="平台结语". -->
    <p class="home-closing__name">{{ HOME_CLOSING.name }}</p>
    <p class="home-closing__subtitle">{{ HOME_CLOSING.subtitle }}</p>
  </section>
</template>

<style scoped>
/* WP-02: minimal structural shell only. The AppFooter renders immediately after
   this section in HomeView; no footer-level content is duplicated here. */
.home-section--closing {
  padding: var(--hfm-space-16) var(--hfm-space-6);
  text-align: center;
}
.home-closing__name {
  font-family: var(--hfm-font-display);
  margin: var(--hfm-space-2) 0;
}
.home-closing__subtitle {
  color: var(--hfm-color-text-muted);
}
</style>

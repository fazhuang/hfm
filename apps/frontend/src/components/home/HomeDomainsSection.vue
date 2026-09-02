<script setup lang="ts">
/**
 * HomeDomainsSection — accepted homepage Section 07 (Four Domains S7-A Refined).
 *
 * WP-02 STRUCTURAL SHELL ONLY. Semantic root + h2 + four-domain navigation
 * entry structure (peer thresholds into the platform, each a real route).
 * Note: the accepted Section 07 does NOT include the removed
 * "NARRATIVE → USABLE ARCHIVE" line (final calibration P2-01). Full
 * four-threshold composition deferred to WP-05.
 */
import { HOME_DOMAINS, HOME_CHAPTERS } from '../../data/homeProjection'

defineOptions({ name: 'HomeDomainsSection' })
</script>

<template>
  <section
    id="home-domains"
    class="home-section home-section--domains"
    aria-labelledby="home-domains-title"
  >
    <p class="home-eyebrow">
      <span class="home-eyebrow__no">{{ HOME_CHAPTERS.domains.no }}</span
      >{{ HOME_CHAPTERS.domains.label }}
    </p>
    <h2 id="home-domains-title" class="home-section__title">{{ HOME_DOMAINS.headline }}</h2>
    <p class="home-section__lede">{{ HOME_DOMAINS.lede }}</p>

    <nav class="home-domains" aria-label="四域入口">
      <a
        v-for="domain in HOME_DOMAINS.domains"
        :key="domain.no"
        class="home-domain"
        :href="domain.href"
      >
        <span class="home-domain__no">{{ domain.no }}</span>
        <span class="home-domain__key">{{ domain.key }} · {{ domain.label }}</span>
        <span class="home-domain__title">{{ domain.title }}</span>
        <span class="home-domain__cta">{{ domain.cta }} →</span>
      </a>
    </nav>
  </section>
</template>

<style scoped>
/* WP-02: minimal structural shell only. */
.home-section--domains {
  padding: var(--hfm-space-12) var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
}
.home-domains {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-6);
  margin-top: var(--hfm-space-6);
}
.home-domain {
  display: flex;
  flex-direction: column;
  gap: var(--hfm-space-1);
  min-width: 12rem;
  flex: 1 1 12rem;
}
.home-domain__key,
.home-domain__cta {
  color: var(--hfm-color-text-muted);
}
.home-domain__title {
  font-family: var(--hfm-font-display);
  font-size: var(--hfm-text-2xl);
}
</style>

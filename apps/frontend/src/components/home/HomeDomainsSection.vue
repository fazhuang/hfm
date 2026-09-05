<script setup lang="ts">
/**
 * HomeDomainsSection — homepage Section 07 (研究导航 / Four Domains S7-A).
 *
 * CF-07 STRUCTURAL SHELL ONLY. Semantic <section id="home-domains"> root +
 * h2 + four editorial doors into ONE platform (人物档案 / 文献史料 / 医学知识 /
 * 活态传承), each anchored to a real route. The rejected "NARRATIVE → USABLE
 * ARCHIVE" rendered line is NOT part of this section and is not restored.
 * No final visual fidelity — that belongs to the visual work packages.
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
    <p class="hfm-eyebrow">
      <span class="home-chapter__no">{{ HOME_CHAPTERS.domains.no }}</span
      >{{ HOME_CHAPTERS.domains.label }}
    </p>
    <h2 id="home-domains-title" class="home-section__title">
      {{ HOME_DOMAINS.headline }}
    </h2>
    <p class="home-section__lede">
      {{ HOME_DOMAINS.lede }}
    </p>

    <ol class="home-domains" aria-label="四域入口">
      <li v-for="domain in HOME_DOMAINS.domains" :key="domain.no" class="home-domains__door">
        <a class="home-domains__door-link" :href="domain.href">
          <span class="home-domains__door-no">{{ domain.no }}</span>
          <span class="home-domains__door-key">{{ domain.key }} · {{ domain.en }}</span>
          <span class="home-domains__door-title">{{ domain.title }}</span>
          <span class="home-domains__door-cta">{{ domain.cta }} →</span>
        </a>
      </li>
    </ol>
  </section>
</template>

<style scoped>
/* CF-07 STRUCTURAL SHELL ONLY. */
.home-chapter__no {
  margin-right: 0.6em;
  color: var(--hfm-color-text-muted);
  font-variant-numeric: tabular-nums;
}

.home-section--domains {
  padding: var(--hfm-space-12) var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
}

.home-domains {
  list-style: none;
  margin: var(--hfm-space-6) 0 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--hfm-space-4);
}

.home-domains__door {
  border-top: 1px solid var(--hfm-color-border-strong);
  padding-top: var(--hfm-space-3);
}

.home-domains__door-link {
  display: flex;
  flex-direction: column;
  gap: var(--hfm-space-1);
  text-decoration: none;
  color: var(--hfm-color-text);
}

.home-domains__door-link:hover {
  color: var(--hfm-color-accent-hover);
}

.home-domains__door-no {
  color: var(--hfm-color-text-muted);
  font-family: var(--hfm-font-numeric, var(--hfm-font-sans));
  font-variant-numeric: tabular-nums;
}

.home-domains__door-key {
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.06em;
}

.home-domains__door-title {
  font-family: var(--hfm-font-display);
  font-size: var(--hfm-text-xl);
}

.home-domains__door-cta {
  color: var(--hfm-color-interactive);
  font-weight: 600;
  font-size: var(--hfm-text-sm);
}
</style>

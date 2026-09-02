<script setup lang="ts">
/**
 * HomeHeritageSection — accepted homepage Section 06 (Heritage S6-B Corrected).
 *
 * WP-02A STRUCTURAL SHELL ONLY. Semantic root + h2 + living-transmission person
 * data + PARTIAL-lineage honesty (第六代名医 · 刘君奇 · PARTIAL · 不虚构). No final
 * visual fidelity (no ceremony photo asset, no documentary-field absolute
 * geometry, no fixed 1240 height) — that belongs to WP-04.
 *
 * TEST CONTRACT (ux2_p5 P1-01): .home-state-line .hfm-status routes data-status
 * through the shared resolver/label (UNSTRUCTURED_OR_INCOMPLETE). Preserved.
 */
import { HOME_HERITAGE_LIVING, HOME_CHAPTERS } from '../../data/homeProjection'
import {
  presentationStatusLabel,
  resolvePresentationState,
  type PresentationState,
} from '../../presentation/stateMapping'

defineOptions({ name: 'HomeHeritageSection' })

const lineageState: PresentationState = resolvePresentationState({ contentStatus: 'DATA_GAP' })
const lineageLabel = presentationStatusLabel(lineageState, '谱系整理中')

const person = HOME_HERITAGE_LIVING.person
</script>

<template>
  <section
    id="home-heritage"
    class="home-section home-section--heritage"
    aria-labelledby="home-heritage-title"
  >
    <p class="home-eyebrow">
      <span class="home-eyebrow__no">{{ HOME_CHAPTERS.heritage.no }}</span
      >{{ HOME_CHAPTERS.heritage.label }}
    </p>
    <h2 id="home-heritage-title" class="home-section__title">
      {{ HOME_HERITAGE_LIVING.headline }}
    </h2>
    <p class="home-section__lede">{{ HOME_HERITAGE_LIVING.project }}</p>

    <div class="home-heritage__person">
      <h3 class="home-heritage__name">{{ person.name }}</h3>
      <p class="home-heritage__role">
        {{ person.generationTitle }} · {{ person.heritageRole }} · {{ person.institutionRole }}
      </p>
      <p class="home-heritage__bio">{{ person.biography }}</p>
      <p class="home-heritage__lineage-note">{{ HOME_HERITAGE_LIVING.lineageNote }}</p>
      <p class="home-state-line">
        <span class="hfm-status" :data-status="lineageState">{{ lineageLabel }}</span>
      </p>
    </div>

    <p class="home-cta-row">
      <a class="home-cta" :href="HOME_HERITAGE_LIVING.cta.href"
        >{{ HOME_HERITAGE_LIVING.cta.label }} →</a
      >
    </p>
  </section>
</template>

<style scoped>
/* WP-02A STRUCTURAL SHELL ONLY. */
.home-section--heritage {
  padding: var(--hfm-space-12) var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
}
.home-heritage__name {
  margin: 0;
}
.home-heritage__role,
.home-heritage__bio,
.home-heritage__lineage-note {
  color: var(--hfm-color-text-secondary);
}
.home-heritage__lineage-note {
  margin-bottom: 0;
}
</style>

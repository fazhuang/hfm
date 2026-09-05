<script setup lang="ts">
/**
 * HomeHeritageSection — homepage Section 06 (活态传承 / Heritage S6).
 *
 * CF-07 STRUCTURAL SHELL ONLY. Semantic <section id="home-heritage"> root +
 * h2 + living-transmission project line + documentary traces (existing
 * HOME_HERITAGE items) + the confirmed human carrier 刘君奇·第六代名医 with
 * the PARTIAL-lineage honesty state (shared CF-02 presentation label; no
 * fabricated intermediate generations). No final visual fidelity — that
 * belongs to the visual work packages.
 */
import { HOME_HERITAGE_LIVING, HOME_CHAPTERS } from '../../data/homeProjection'
import { presentationStatusLabel } from '../../presentation/stateMapping'

defineOptions({ name: 'HomeHeritageSection' })

const person = HOME_HERITAGE_LIVING.person
const traces = HOME_HERITAGE_LIVING.traces ?? []
/* The intermediate lineage gap is a REAL PARTIAL state (documented in the
 * heritage data layer); its public label goes through the shared CF-02
 * mapping — never the internal LINEAGE_STRUCTURING marker. */
const lineageLabel = presentationStatusLabel('PARTIAL', '谱系整理中')
</script>

<template>
  <section
    id="home-heritage"
    class="home-section home-section--heritage"
    aria-labelledby="home-heritage-title"
  >
    <p class="hfm-eyebrow">
      <span class="home-chapter__no">{{ HOME_CHAPTERS.heritage.no }}</span
      >{{ HOME_CHAPTERS.heritage.label }}
    </p>
    <h2 id="home-heritage-title" class="home-section__title">
      {{ HOME_HERITAGE_LIVING.headline }}
    </h2>
    <p class="home-section__lede">
      {{ HOME_HERITAGE_LIVING.project }}
    </p>

    <ul class="home-heritage__traces" aria-label="活态传承记录">
      <li v-for="trace in traces" :key="trace.title" class="home-heritage__trace">
        <a :href="trace.href" class="home-heritage__trace-title">{{ trace.title }}</a>
        <span v-if="trace.meta" class="home-heritage__trace-meta">{{ trace.meta }}</span>
      </li>
    </ul>

    <div class="home-heritage__person">
      <h3 class="home-heritage__name">
        {{ person.name }}
      </h3>
      <p class="home-heritage__role">
        {{ person.generationTitle }} · {{ person.heritageRole }} · {{ person.institutionRole }}
      </p>
      <p class="home-heritage__bio">
        {{ person.biography }}
      </p>
      <p class="home-heritage__lineage-note">
        {{ HOME_HERITAGE_LIVING.lineageNote
        }}<span class="home-state-line">
          <span class="hfm-status" data-status-prefix="presentation" data-status="PARTIAL">{{
            lineageLabel
          }}</span>
        </span>
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
/* CF-07 STRUCTURAL SHELL ONLY. */
.home-chapter__no {
  margin-right: 0.6em;
  color: var(--hfm-color-text-muted);
  font-variant-numeric: tabular-nums;
}

.home-section--heritage {
  padding: var(--hfm-space-12) var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
}

.home-heritage__traces {
  list-style: none;
  margin: var(--hfm-space-4) 0;
  padding: 0;
}

.home-heritage__trace {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-3);
  align-items: baseline;
  padding: var(--hfm-space-2) 0;
  border-top: 1px solid var(--hfm-color-border);
}

.home-heritage__trace-title {
  font-weight: 600;
  text-decoration: none;
}

.home-heritage__trace-meta {
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
}

.home-heritage__person {
  margin-top: var(--hfm-space-4);
}

.home-heritage__name {
  margin: 0;
}

.home-heritage__role,
.home-heritage__bio {
  color: var(--hfm-color-text-secondary);
}

.home-heritage__lineage-note {
  color: var(--hfm-color-text-secondary);
  font-size: var(--hfm-text-sm);
}

.home-state-line {
  margin-left: var(--hfm-space-2);
}

.home-cta-row {
  margin: var(--hfm-space-5) 0 0;
}

.home-cta {
  display: inline-block;
  padding: var(--hfm-space-1) var(--hfm-space-4);
  border: 1px solid var(--hfm-color-accent);
  border-radius: var(--hfm-radius-sm);
  color: var(--hfm-color-accent);
  font-weight: 600;
  text-decoration: none;
}

.home-cta:hover {
  background: var(--hfm-color-accent);
  color: var(--hfm-color-on-accent);
}
</style>

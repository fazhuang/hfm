<script setup lang="ts">
/**
 * CF-02 BibliographicRecord — minimal bibliographic display primitive.
 *
 * Presentation-only. It renders the bibliographic identity, metadata, edition /
 * publication information, and an optional status + provenance note. It does NOT
 * fetch data, orchestrate search, provide reader-navigation business logic, or
 * assume any API shape. The caller passes fully-resolved presentational data.
 *
 * Fields render only when present (no empty placeholders).
 * Status and provenance are read from real props (never invented for display).
 * Accessibility: semantic <article> + <dl>; status text is readable without
 * color alone; no invalid live-region semantics.
 */
import { presentationStatusLabel, type PresentationState } from '../../presentation/stateMapping'

interface BiblioMetaItem {
  label?: string
  value: string
}

const props = withDefaults(
  defineProps<{
    /** bibliographic identity (title). */
    title?: string
    /** secondary identity line, e.g. 作者/编校者. */
    author?: string
    /** edition / publication information. */
    edition?: string
    /** publication year. */
    year?: string
    /** arbitrary metadata items. */
    meta?: BiblioMetaItem[]
    /** optional presentation state (read from real props). */
    status?: PresentationState | string
    /** optional status label override. */
    statusLabel?: string
    /** optional provenance note (only real, caller-supplied provenance). */
    provenance?: string
  }>(),
  { title: '', author: '', edition: '', year: '', meta: () => [], status: '', statusLabel: '', provenance: '' },
)

function resolvedStatus(): PresentationState | string {
  return (props.status as PresentationState) || 'UNKNOWN'
}
</script>

<template>
  <article class="bib-record" data-primitive="bibliographic-record">
    <header class="bib-record__head">
      <p class="bib-record__title">{{ title || '（未命名文献）' }}</p>
      <p v-if="author" class="bib-record__author">{{ author }}</p>
    </header>

    <dl v-if="edition || year || meta.length" class="bib-record__meta">
      <div v-if="edition" class="bib-record__meta-row">
        <dt>版本</dt>
        <dd>{{ edition }}</dd>
      </div>
      <div v-if="year" class="bib-record__meta-row">
        <dt>年份</dt>
        <dd>{{ year }}</dd>
      </div>
      <div
        v-for="m in meta"
        :key="`${m.label}-${m.value}`"
        class="bib-record__meta-row"
      >
        <dt>{{ m.label }}</dt>
        <dd>{{ m.value }}</dd>
      </div>
    </dl>

    <p v-if="status" class="bib-record__status" data-status-prefix="presentation" :data-status="resolvedStatus()">
      {{ presentationStatusLabel(resolvedStatus(), statusLabel) }}
    </p>

    <p v-if="provenance" class="bib-record__provenance">
      {{ provenance }}
    </p>
  </article>
</template>

<style scoped>
.bib-record {
  border-top: 1px solid var(--hfm-color-border);
  border-bottom: 1px solid var(--hfm-color-border);
  padding: var(--hfm-space-4) 0;
}

.bib-record__head {
  margin-bottom: var(--hfm-space-2);
}

.bib-record__title {
  font-family: var(--hfm-font-heading);
  font-size: var(--hfm-text-lg);
  font-weight: 500;
  margin: 0;
  color: var(--hfm-color-text);
}

.bib-record__author {
  margin: var(--hfm-space-1) 0 0;
  color: var(--hfm-color-text-secondary);
  font-size: var(--hfm-text-sm);
}

.bib-record__meta {
  margin: var(--hfm-space-2) 0 0;
}

.bib-record__meta-row {
  display: flex;
  gap: var(--hfm-space-3);
  padding: 2px 0;
  font-size: var(--hfm-text-sm);
}

.bib-record__meta-row dt {
  color: var(--hfm-color-text-muted);
  min-width: 3ch;
}

.bib-record__meta-row dd {
  margin: 0;
  color: var(--hfm-color-text-secondary);
}

.bib-record__status {
  display: inline-block;
  margin: var(--hfm-space-2) 0 0;
  padding: 2px var(--hfm-space-2);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-warning);
  color: var(--hfm-color-text);
  font-size: var(--hfm-text-xs);
  font-weight: 600;
}

.bib-record__provenance {
  margin: var(--hfm-space-2) 0 0;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}
</style>

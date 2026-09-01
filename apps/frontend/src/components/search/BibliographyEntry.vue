<script setup lang="ts">
/**
 * BibliographyEntry — paper-result adapter aligned to the shared
 * BibliographicRecord primitive (UX2-P4 · G4-O-1 alignment).
 *
 * The paper search-result kind renders through the P0 BibliographicRecord
 * presentation (field hierarchy, degradation, presentation-state badge).
 * Discovery ≠ resource availability: no full-text/PDF/reader/download
 * affordance is invented; the record state is derived from the entry's
 * governed ContentStatus via the P0 G1-C mapping.
 */
import type { SearchIndexEntry } from '../../types/search'
import { presentationLabel, resolvePresentationState, type ContentStatus } from '../../presentation/stateMapping'
import BibliographicRecord from '../primitives/BibliographicRecord.vue'

defineOptions({ name: 'BibliographyEntry' })

const props = defineProps<{ entry: SearchIndexEntry }>()

function recordProps(): {
  title: string
  author: string | undefined
  year: string | undefined
  kind: string
  source: string | undefined
  status: string
  statusLabel: string
  description: string | undefined
  href: string | undefined
} {
  const state = resolvePresentationState({
    contentStatus: props.entry.status as ContentStatus | undefined,
    hasMetadata: true,
  })
  return {
    title: props.entry.title,
    author: props.entry.authors?.length ? props.entry.authors.join('；') : undefined,
    year: props.entry.year !== undefined ? String(props.entry.year) : undefined,
    kind: '论文',
    source: props.entry.sourceName,
    status: state,
    statusLabel: presentationLabel(state),
    description: props.entry.subtitle,
    href: props.entry.route,
  }
}
</script>

<template>
  <li class="bib-entry">
    <BibliographicRecord v-bind="recordProps()" />
  </li>
</template>

<style scoped>
.bib-entry {
  list-style: none;
  margin: 0;
  padding: var(--hfm-space-2) 0;
  border-bottom: 1px solid var(--hfm-color-border);
}

.bib-entry:last-child {
  border-bottom: none;
}
</style>

<script setup lang="ts">
/**
 * BibliographicRecord — UX2 shared scholarly record primitive (G1-A §2).
 *
 * Eligible kinds: classical work · edition · paper · search result ·
 * source citation. Field hierarchy (G1-A §2.2):
 *   Title → responsible person/entity → date or period → edition/publication
 *   → resource/document type → source/holding → presentation state →
 *   optional abstract/description → optional citation locator.
 *
 * Degradation (NB-06): a missing OPTIONAL field is omitted; a missing
 * authoritative field is NEVER synthesized. The locator prop carries only
 * document-level citation text supplied by the caller — the primitive never
 * invents 卷/页/版本号 (U-04 stays unresolved; page-level locator collapsed).
 * No CitationExport behavior exists in this primitive (export stays DEFERRED).
 */
import { computed } from 'vue'
import { presentationStatusLabel } from '../../presentation/stateMapping'

interface RecordMetaRow {
  label: string
  value: string
}

const props = withDefaults(
  defineProps<{
    title: string
    /** responsible person/entity. */
    author?: string
    /** date or period. */
    year?: string
    /** edition/publication information. */
    edition?: string
    /** resource/document type. */
    kind?: string
    /** source/holding institution (public source name only). */
    source?: string
    /** presentation status (a PresentationState or existing ContentStatus). */
    status?: string
    statusLabel?: string
    /** optional abstract/description. */
    description?: string
    /** optional document-level citation locator (caller-supplied text; U-04 page-level collapsed). */
    locator?: string
    href?: string
  }>(),
  {
    author: '',
    year: '',
    edition: '',
    kind: '',
    source: '',
    status: '',
    statusLabel: '',
    description: '',
    locator: '',
    href: '',
  },
)

const metaRows = computed<RecordMetaRow[]>(() => {
  const rows: RecordMetaRow[] = []
  if (props.author) rows.push({ label: '作者/整理者', value: props.author })
  if (props.year) rows.push({ label: '时期/年份', value: props.year })
  if (props.edition) rows.push({ label: '版本', value: props.edition })
  if (props.kind) rows.push({ label: '类型', value: props.kind })
  if (props.source) rows.push({ label: '来源', value: props.source })
  if (props.locator) rows.push({ label: '引用定位', value: props.locator })
  return rows
})

function badgeText(): string {
  return presentationStatusLabel(props.status || undefined, props.statusLabel || undefined)
}
</script>

<template>
  <div
    class="bib-record ux2-surface-paper"
    data-primitive="bib-record"
  >
    <p class="bib-record__title">
      <span
        v-if="status || statusLabel"
        class="hfm-status"
        :data-status="status || 'UNSTRUCTURED_OR_INCOMPLETE'"
      >
        {{ badgeText() }}
      </span>
      <a
        v-if="href"
        :href="href"
        class="bib-record__link"
      >{{ title }}</a>
      <template v-else>
        {{ title }}
      </template>
    </p>

    <dl
      v-if="metaRows.length > 0"
      class="bib-record__meta"
    >
      <template
        v-for="row in metaRows"
        :key="row.label"
      >
        <dt>{{ row.label }}</dt>
        <dd>{{ row.value }}</dd>
      </template>
    </dl>

    <p
      v-if="description"
      class="bib-record__desc"
    >
      {{ description }}
    </p>
  </div>
</template>

<style scoped>
.bib-record {
  padding: var(--hfm-space-2) 0;
}

.bib-record__title {
  font-family: var(--hfm-font-heading);
  font-weight: 600;
  margin: 0;
  padding-left: var(--hfm-space-5);
  text-indent: calc(-1 * var(--hfm-space-5));
}

.bib-record__title .hfm-status {
  margin-right: var(--hfm-space-2);
}

.bib-record__link {
  color: var(--hfm-color-interactive);
}

.bib-record__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-1) var(--hfm-space-5);
  margin: var(--hfm-space-1) 0 0;
  padding-left: var(--hfm-space-5);
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-muted);
}

.bib-record__meta dt {
  display: inline;
  font-weight: 600;
  color: var(--hfm-color-text-secondary);
}

.bib-record__meta dt::after {
  content: '：';
}

.bib-record__meta dd {
  display: inline;
  margin: 0;
}

.bib-record__desc {
  margin: var(--hfm-space-1) 0 0;
  padding-left: var(--hfm-space-5);
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-secondary);
}
</style>

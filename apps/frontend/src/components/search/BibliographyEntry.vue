<script setup lang="ts">
/**
 * BibliographyEntry — high-density academic paper result (UI-10).
 *
 * Fields render only when present. No product cards, no badge clutter.
 */
import type { SearchIndexEntry } from '../../types/search'
import SearchHighlight from './SearchHighlight.vue'

defineOptions({ name: 'BibliographyEntry' })

defineProps<{ entry: SearchIndexEntry; query: string }>()
</script>

<template>
  <li class="bib-entry">
    <p class="bib-entry__title">
      <a v-if="entry.route" :href="entry.route" class="bib-entry__link">
        <SearchHighlight :text="entry.title" :query="query" />
      </a>
      <template v-else><SearchHighlight :text="entry.title" :query="query" /></template>
    </p>
    <dl
      v-if="entry.authors || entry.year || entry.subtitle || entry.sourceName"
      class="bib-entry__meta"
    >
      <template v-if="entry.authors && entry.authors.length">
        <dt>作者/整理者</dt>
        <dd>{{ entry.authors.join('；') }}</dd>
      </template>
      <template v-if="entry.year">
        <dt>年份</dt>
        <dd>{{ entry.year }}</dd>
      </template>
      <template v-if="entry.subtitle">
        <dt>来源</dt>
        <dd>{{ entry.subtitle }}</dd>
      </template>
      <template v-if="entry.sourceName">
        <dt>资料</dt>
        <dd>{{ entry.sourceName }}</dd>
      </template>
    </dl>
  </li>
</template>

<style scoped>
.bib-entry {
  display: grid;
  gap: var(--hfm-space-1);
  padding: var(--hfm-space-3) var(--hfm-space-4);
  border-bottom: 1px solid var(--hfm-color-border);
}

.bib-entry__title {
  margin: 0;
  font-weight: 600;
  line-height: var(--hfm-leading-normal);
}

.bib-entry__link {
  color: var(--hfm-color-text);
  text-decoration: none;
}

.bib-entry__link:hover {
  color: var(--hfm-color-accent);
}

.bib-entry__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-1) var(--hfm-space-4);
  margin: 0;
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-muted);
}

.bib-entry__meta dt {
  display: inline;
  font-weight: 600;
}

.bib-entry__meta dd {
  display: inline;
  margin: 0;
}
</style>

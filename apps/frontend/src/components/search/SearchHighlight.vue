<script setup lang="ts">
/**
 * SearchHighlight — safe query highlighting (UI-10).
 *
 * Renders segments with <mark> around query matches. No v-html: text is
 * always rendered as text nodes, so screen readers read the untouched text
 * and XSS is impossible. Matches are case-insensitive; Chinese included.
 */
import { computed } from 'vue'

const props = defineProps<{ text: string; query: string }>()

const segments = computed<Array<{ hit: boolean; text: string }>>(() => {
  const q = props.query.trim().toLowerCase()
  if (!q) return [{ hit: false, text: props.text }]
  const lower = props.text.toLowerCase()
  const out: Array<{ hit: boolean; text: string }> = []
  let pos = 0
  let idx = lower.indexOf(q)
  while (idx !== -1) {
    if (idx > pos) out.push({ hit: false, text: props.text.slice(pos, idx) })
    out.push({ hit: true, text: props.text.slice(idx, idx + q.length) })
    pos = idx + q.length
    idx = lower.indexOf(q, pos)
  }
  if (pos < props.text.length) out.push({ hit: false, text: props.text.slice(pos) })
  return out.length > 0 ? out : [{ hit: false, text: props.text }]
})
</script>

<template>
  <span class="search-highlight">
    <template v-for="(seg, i) in segments" :key="i">
      <mark v-if="seg.hit" class="search-highlight__mark">{{ seg.text }}</mark>
      <template v-else>{{ seg.text }}</template>
    </template>
  </span>
</template>

<style scoped>
.search-highlight__mark {
  background: var(--hfm-color-success-surface);
  color: var(--hfm-color-success);
  padding: 0 0.125em;
  border-radius: 2px;
  font-weight: 600;
}
</style>

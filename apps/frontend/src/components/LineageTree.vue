<script setup lang="ts">
import type { LineageNode } from '../types/heritage'

defineProps<{ nodes: LineageNode[] }>()
</script>

<template>
  <ul class="lineage-tree" aria-label="传承谱系">
    <li v-for="node in nodes" :key="node.id" class="lineage-tree__node">
      <span class="lineage-tree__name">{{ node.name }}</span>
      <span v-if="node.officialName" class="lineage-tree__official">
        {{ node.officialName }}
      </span>
    </li>
  </ul>
</template>

<style scoped>
.lineage-tree {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-2);
}

.lineage-tree__node {
  display: grid;
  gap: var(--hfm-space-1);
  padding: var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
}

.lineage-tree__official {
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
}
</style>

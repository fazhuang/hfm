<script setup lang="ts">
/**
 * LineageGraph — 传承谱系（UI-09）。
 *
 * 仅渲染已确认节点；中间代（第二代至第五代）以显式 PARTIAL 占位呈现，
 * 不虚构人物或师承边。桌面为纵向线稿，移动端与读屏同为结构化列表语义
 * （非视觉图形）；每条确认节点带证据说明。
 */
import type { ConfirmedLineageNode } from '../../types/heritage'

defineOptions({ name: 'LineageGraph' })

defineProps<{ nodes: ConfirmedLineageNode[] }>()
</script>

<template>
  <ol class="lineage" aria-label="皇甫谧针灸传承谱系（已确认部分）">
    <li v-for="(node, i) in nodes" :key="node.id" class="lineage__node">
      <span class="lineage__rail" aria-hidden="true">
        <span v-if="i < nodes.length - 1" class="lineage__connector" aria-hidden="true"></span>
      </span>
      <div class="lineage__body" :class="{ 'lineage__body--gap': !node.generation }">
        <a v-if="node.href" :href="node.href" class="lineage__person">
          {{ node.person }}
        </a>
        <span v-else class="lineage__person">{{ node.person }}</span>
        <span v-if="node.generation" class="lineage__generation">{{ node.generation }}</span>
        <p v-if="node.role" class="lineage__role">{{ node.role }}</p>
        <p class="lineage__evidence">证据：{{ node.evidence }}</p>
      </div>
    </li>
  </ol>
</template>

<style scoped>
.lineage {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0;
}

.lineage__node {
  position: relative;
  display: grid;
  grid-template-columns: 2rem 1fr;
  gap: var(--hfm-space-3);
  padding: var(--hfm-space-3) 0;
}

.lineage__rail {
  position: relative;
  display: block;
  width: 1.5rem;
}

.lineage__node::before {
  content: '';
  position: absolute;
  left: 0.625rem;
  top: var(--hfm-space-4);
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
  background: var(--hfm-color-surface);
  border: 2px solid var(--hfm-color-accent);
  z-index: 1;
}

.lineage__connector {
  position: absolute;
  left: 0.968rem;
  top: var(--hfm-space-4);
  bottom: -2.2rem;
  width: 1px;
  background: var(--hfm-color-border-strong);
}

.lineage__body {
  padding: var(--hfm-space-1) 0;
}

.lineage__person {
  font-family: var(--hfm-font-serif);
  font-weight: 600;
  font-size: var(--hfm-text-lg);
  color: var(--hfm-color-text);
  text-decoration: none;
  margin-right: var(--hfm-space-2);
}

a.lineage__person:hover {
  color: var(--hfm-color-accent);
}

.lineage__generation {
  display: inline-block;
  padding: 2px var(--hfm-space-2);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-heritage);
  color: var(--hfm-color-on-heritage);
  font-size: var(--hfm-text-xs);
  font-weight: 600;
}

.lineage__body--gap .lineage__person {
  color: var(--hfm-color-text-muted);
  font-style: italic;
}

.lineage__role {
  margin: var(--hfm-space-1) 0 0;
  color: var(--hfm-color-text-secondary);
  font-size: var(--hfm-text-sm);
}

.lineage__evidence {
  margin: var(--hfm-space-1) 0 0;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}
</style>

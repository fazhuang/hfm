<script setup lang="ts">
/**
 * LineageGraph — CF-05 传承谱系（已确认节点 + 明确的 PARTIAL 表达）。
 *
 * 谱系仅渲染已确认节点；第二代至第五代中间代以正式 PARTIAL 数据状态呈现
 * （公开文案 + CF-02 stateMapping 标签），不作为错误、不做视觉占位、不虚构
 * 人物或师承边。桌面为纵向线稿，移动端与读屏保持同一结构化列表语义；节点
 * 状态有文字标签，不依赖颜色单独传达（CF-02 stateMapping）。
 *
 * PARTIAL 内部治理标记（LINEAGE_STRUCTURING）只存在于数据登记层，绝不出
 * 现在公开渲染文案中。
 */
import type { ConfirmedLineageNode } from '../../types/heritage'
import { presentationStatusLabel } from '../../presentation/stateMapping'

defineOptions({ name: 'LineageGraph' })

defineProps<{ nodes: ConfirmedLineageNode[] }>()

/** Public PARTIAL label/note — never the internal LINEAGE_STRUCTURING marker. */
const PARTIAL_LABEL = presentationStatusLabel('PARTIAL')
const PARTIAL_NOTE =
  '第二代至第五代中间代传承资料尚未完整收录，当前仅掌握部分传承信息；不作虚构整理。'

/** A confirmed person node has a generation; an explicit gap node does not. */
function isGap(node: ConfirmedLineageNode): boolean {
  return node.generation === undefined
}
</script>

<template>
  <ol class="lineage" aria-label="皇甫谧针灸传承谱系（已确认部分）">
    <li
      v-for="(node, i) in nodes"
      :key="node.id"
      class="lineage__node"
      :data-lineage-kind="isGap(node) ? 'partial-gap' : 'confirmed'"
    >
      <span class="lineage__rail" aria-hidden="true">
        <span v-if="i < nodes.length - 1" class="lineage__connector" aria-hidden="true"></span>
      </span>
      <div class="lineage__body" :class="{ 'lineage__body--gap': isGap(node) }">
        <!-- PARTIAL gap node: a real data state, explained in plain public copy. -->
        <template v-if="isGap(node)">
          <span class="lineage__person">{{ node.person }}</span>
          <span class="lineage__status" data-status-prefix="presentation" data-status="PARTIAL">{{
            PARTIAL_LABEL
          }}</span>
          <p v-if="node.role" class="lineage__role">{{ node.role }}</p>
          <p class="lineage__note">{{ PARTIAL_NOTE }}</p>
        </template>

        <!-- Confirmed node: person + generation + role + public evidence. -->
        <template v-else>
          <a v-if="node.href" :href="node.href" class="lineage__person">
            {{ node.person }}
          </a>
          <span v-else class="lineage__person">{{ node.person }}</span>
          <span v-if="node.generation" class="lineage__generation">{{ node.generation }}</span>
          <p v-if="node.role" class="lineage__role">{{ node.role }}</p>
          <p class="lineage__evidence">证据：{{ node.evidence }}</p>
        </template>
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
  grid-template-columns: 2rem minmax(0, 1fr);
  gap: var(--hfm-space-3);
  padding: var(--hfm-space-3) 0;
  min-width: 0;
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
  min-width: 0;
}

.lineage__person {
  font-family: var(--hfm-font-serif);
  font-weight: 600;
  font-size: var(--hfm-text-lg);
  color: var(--hfm-color-text);
  text-decoration: none;
  margin-right: var(--hfm-space-2);
  overflow-wrap: anywhere;
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

.lineage__status {
  display: inline-block;
  margin-left: var(--hfm-space-1);
  padding: 2px var(--hfm-space-2);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-warning);
  color: var(--hfm-color-text);
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
  overflow-wrap: anywhere;
}

.lineage__evidence {
  margin: var(--hfm-space-1) 0 0;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
  overflow-wrap: anywhere;
}

.lineage__note {
  margin: var(--hfm-space-1) 0 0;
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-secondary);
  line-height: var(--hfm-leading-normal);
}
</style>

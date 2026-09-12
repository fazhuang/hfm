<script setup lang="ts">
/**
 * EvidenceExplorer — UI-11 high-density evidence summary.
 * Maps existing ContentStatus to human labels; shows real source names +
 * citation availability. No invented governance states.
 */
import type { ResearchEvidenceSummary } from '../../types/research'

defineOptions({ name: 'EvidenceExplorer' })

defineProps<{ evidence: ResearchEvidenceSummary[] }>()

const STATUS_LABEL: Record<string, string> = {
  AVAILABLE: '已展示',
  METADATA_ONLY: '元数据已录',
  DATA_GAP: '整理中',
}
</script>

<template>
  <section class="evidence" aria-labelledby="evidence-heading">
    <h2 id="evidence-heading" class="evidence__title">Evidence</h2>
    <ul class="evidence__list">
      <li v-for="(item, i) in evidence" :key="i" class="evidence__item">
        <p class="evidence__source">{{ item.sourceName }}</p>
        <dl class="evidence__meta">
          <div>
            <dt>状态</dt>
            <dd>
              <span class="hfm-status" :data-status="item.contentStatus">
                {{ STATUS_LABEL[item.contentStatus] ?? item.contentStatus }}
              </span>
            </dd>
          </div>
          <div v-if="item.citationCount !== undefined">
            <dt>可引用条目</dt>
            <dd>{{ item.citationCount }}</dd>
          </div>
          <div v-if="item.note">
            <dt>说明</dt>
            <dd>{{ item.note }}</dd>
          </div>
        </dl>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.evidence {
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
  padding: var(--hfm-space-4);
}

.evidence__title {
  margin: 0 0 var(--hfm-space-3);
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-citation);
}

.evidence__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-3);
}

.evidence__item {
  display: grid;
  gap: var(--hfm-space-1);
  padding-bottom: var(--hfm-space-3);
  border-bottom: 1px solid var(--hfm-color-border);
}

.evidence__item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.evidence__source {
  margin: 0;
  font-weight: 600;
  font-size: var(--hfm-text-sm);
}

.evidence__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-1) var(--hfm-space-5);
  margin: 0;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.evidence__meta div {
  display: flex;
  gap: var(--hfm-space-1);
}

.evidence__meta dt {
  font-weight: 600;
}

.evidence__meta dd {
  margin: 0;
}

.evidence__status[data-status='DATA_GAP'] {
  background: var(--hfm-color-warning);
  color: var(--hfm-color-on-accent);
}
</style>

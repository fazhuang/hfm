<script setup lang="ts">
/**
 * Timeline — UI-05 line-art biography timeline component.
 *
 * Renders TimelineEvent[] as a vertical line with nodes; metadata
 * (date/place/person/source) inline; reduced-motion safe (static by
 * default). Keyboard: nodes are plain content; any embedded links stay
 * natively focusable. Parent renders the empty state when no events.
 */
import type { TimelineEvent } from '../types/timeline'

defineOptions({ name: 'Timeline' })

defineProps<{ events: TimelineEvent[]; label?: string }>()
</script>

<template>
  <ol class="timeline" :aria-label="label ?? '时间轴'">
    <li v-for="event in events" :key="event.id" class="timeline__node">
      <span class="timeline__marker" aria-hidden="true"></span>
      <div class="timeline__content">
        <p class="timeline__title">
          <span v-if="event.date" class="timeline__date">{{ event.date }}</span>
          {{ event.title }}
        </p>
        <dl v-if="event.place || event.person || event.source" class="timeline__meta">
          <template v-if="event.place">
            <dt>地点</dt>
            <dd>{{ event.place }}</dd>
          </template>
          <template v-if="event.person">
            <dt>人物</dt>
            <dd>{{ event.person }}</dd>
          </template>
          <template v-if="event.source">
            <dt>史料来源</dt>
            <dd>{{ event.source }}</dd>
          </template>
        </dl>
        <p v-if="event.description" class="timeline__desc">{{ event.description }}</p>
      </div>
    </li>
  </ol>
</template>

<style scoped>
.timeline {
  list-style: none;
  margin: 0;
  padding: 0;
  position: relative;
  display: grid;
  gap: var(--hfm-space-4);
}

.timeline::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0.375rem;
  width: 1px;
  background: var(--hfm-color-border-strong);
}

.timeline__node {
  position: relative;
  padding-left: var(--hfm-space-6);
}

.timeline__marker {
  position: absolute;
  left: 0;
  top: 0.3rem;
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
  background: var(--hfm-color-surface);
  border: 2px solid var(--hfm-color-accent);
}

.timeline__title {
  margin: 0 0 var(--hfm-space-1);
  font-weight: 600;
  font-family: var(--hfm-font-serif);
}

.timeline__date {
  display: inline-block;
  margin-right: var(--hfm-space-2);
  color: var(--hfm-color-heritage);
  font-variant-numeric: tabular-nums;
  font-size: var(--hfm-text-sm);
}

.timeline__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2) var(--hfm-space-4);
  margin: 0 0 var(--hfm-space-1);
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.timeline__meta dt {
  display: inline;
  font-weight: 600;
}

.timeline__meta dd {
  display: inline;
  margin: 0;
}

.timeline__desc {
  margin: 0;
  color: var(--hfm-color-text-secondary);
  line-height: var(--hfm-leading-reading);
  max-width: 60ch;
}
</style>

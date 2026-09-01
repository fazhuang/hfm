<script setup lang="ts">
/**
 * DHObjectLayout — UX2 shared presentation composition primitive (G1-A §1).
 *
 * Regions: Header · Context · Evidence · Relations (presentation slots, not
 * domain entities). Slot presence: PRESENT | ABSENT_OPTIONAL |
 * INCOMPLETE_WITH_EVIDENCE_STATE (G1-A §1.2).
 *   PRESENT                   → render from authoritative data.
 *   ABSENT_OPTIONAL           → collapse completely: no empty card, no
 *                               placeholder, no reserved spacing, no fake CTA.
 *   INCOMPLETE_WITH_EVIDENCE_STATE → stay visible with a meaningful
 *                               incompleteness note (role="status").
 *
 * Object title heading level follows the frozen N-F-1 production contract
 * (titleTag → resolveTitleTag in presentation/stateMapping.ts).
 * Relations render as text labels with explicit semantics only — no
 * connectors, arrows, or genealogy behavior is ever drawn.
 */
import { computed } from 'vue'
import { presentationStatusLabel, resolveTitleTag } from '../../presentation/stateMapping'

type DHObjectRegion = 'header' | 'context' | 'evidence' | 'relations'
type DHObjectSlotState = 'PRESENT' | 'ABSENT_OPTIONAL' | 'INCOMPLETE_WITH_EVIDENCE_STATE'
type DHObjectRelationSemantics = 'EXPLICIT_RELATION' | 'ASSOCIATED_CONTEXT' | 'CO_PRESENTED_ONLY'

interface DHObjectSlot {
  state: DHObjectSlotState
  /** presentation status for the badge (a PresentationState or existing ContentStatus). */
  status?: string
  statusLabel?: string
  /** explanatory text shown with INCOMPLETE_WITH_EVIDENCE_STATE. */
  note?: string
}

interface DHObjectMetaItem {
  label?: string
  value: string
}

interface DHObjectRelationItem {
  label: string
  href?: string
  sem: DHObjectRelationSemantics
}

interface RenderedRegion {
  region: DHObjectRegion
  slot: DHObjectSlot
}

const props = withDefaults(
  defineProps<{
    /** object title text. */
    title?: string
    /** N-F-1 production contract — see resolveTitleTag(). */
    titleTag?: number | 'none' | null
    /** header meta line items (e.g. dates · type). */
    meta?: DHObjectMetaItem[]
    /** per-region slot presence configuration. */
    slots: Partial<Record<DHObjectRegion, DHObjectSlot>>
    /** relations items (rendered as text labels with explicit semantics only). */
    relations?: DHObjectRelationItem[]
  }>(),
  { title: '', titleTag: null, meta: () => [], relations: () => [] },
)

const REGION_ORDER: readonly DHObjectRegion[] = ['header', 'context', 'evidence', 'relations']
const REGION_TITLES: Record<DHObjectRegion, string> = {
  header: '对象',
  context: '语境',
  evidence: '证据',
  relations: '关联',
}

const titleTagResolved = computed<string>(() => resolveTitleTag(props.titleTag))

/** Regions to render — ABSENT_OPTIONAL collapses completely (no container, no spacing). */
const renderedRegions = computed<RenderedRegion[]>(() =>
  REGION_ORDER.filter((region) => {
    const slot = props.slots[region]
    return slot !== undefined && slot.state !== 'ABSENT_OPTIONAL'
  }).map((region) => ({ region, slot: props.slots[region] as DHObjectSlot })),
)

function badgeStatus(slot: DHObjectSlot): string {
  return slot.status ?? 'UNSTRUCTURED_OR_INCOMPLETE'
}

function badgeLabel(slot: DHObjectSlot): string {
  return presentationStatusLabel(slot.status, slot.statusLabel)
}
</script>

<template>
  <article
    class="dh-object ux2-surface-paper"
    data-primitive="dh-object"
  >
    <section
      v-for="r in renderedRegions"
      :key="r.region"
      class="dh-object__slot"
      :class="{ 'ux2-surface-evidence': r.region === 'evidence' }"
      :data-slot="r.region"
      :data-slot-state="r.slot.state"
    >
      <p class="dh-object__slot-title">
        {{ REGION_TITLES[r.region] }}
      </p>

      <template v-if="r.region === 'header'">
        <div
          v-if="title !== '' || meta.length > 0"
          class="dh-object__header"
        >
          <component
            :is="titleTagResolved"
            class="dh-object__title"
          >
            {{ title }}
          </component>
          <span
            v-for="m in meta"
            :key="m.value"
            class="dh-object__meta"
          >
            <template v-if="m.label">{{ m.label }}&#160;</template>{{ m.value }}
          </span>
        </div>
      </template>

      <div
        v-if="r.slot.state === 'INCOMPLETE_WITH_EVIDENCE_STATE'"
        class="incomplete-note"
        role="status"
      >
        <span
          class="hfm-status"
          :data-status="badgeStatus(r.slot)"
        >{{ badgeLabel(r.slot) }}</span>
        <span
          v-if="r.slot.note"
          class="incomplete-note__text"
        >{{ r.slot.note }}</span>
      </div>

      <ul
        v-if="r.region === 'relations' && relations.length > 0"
        class="dh-object__relations"
      >
        <li
          v-for="item in relations"
          :key="`${item.label}-${item.sem}`"
          class="relation-item"
        >
          <a
            v-if="item.href"
            :href="item.href"
            class="relation-item__label"
          >{{ item.label }}</a>
          <span
            v-else
            class="relation-item__label"
          >{{ item.label }}</span>
          <span class="relation-item__sem">{{ item.sem }}</span>
        </li>
      </ul>

      <slot :name="r.region" />
    </section>
  </article>
</template>

<style scoped>
.dh-object {
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  padding: var(--hfm-space-5) var(--hfm-space-6);
}

.dh-object__slot {
  padding: var(--hfm-space-2) 0;
  border-bottom: 1px solid var(--hfm-color-border);
}

.dh-object__slot:last-child {
  border-bottom: none;
}

.dh-object__slot-title {
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
  margin: 0 0 var(--hfm-space-2);
  letter-spacing: 0.08em;
}

.dh-object__header {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2) var(--hfm-space-4);
  align-items: baseline;
}

.dh-object__title {
  font-size: var(--hfm-text-2xl);
  margin: 0;
}

.dh-object__meta {
  color: var(--hfm-color-text-secondary);
  font-size: var(--hfm-text-sm);
}

.dh-object__relations {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-1);
}

.relation-item {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2) var(--hfm-space-4);
  padding: var(--hfm-space-1) 0;
  font-size: var(--hfm-text-sm);
}

.relation-item__label {
  font-weight: 600;
}

.relation-item__sem {
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-azure);
}

.incomplete-note {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2);
  align-items: baseline;
  padding: var(--hfm-space-2) 0;
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-secondary);
}
</style>

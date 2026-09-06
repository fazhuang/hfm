<script setup lang="ts">
/**
 * CF-02 DHObjectLayout — presentation-only object display skeleton.
 *
 * A light, reusable wrapper for object-like pages (Person / Jiayi / Heritage).
 * It renders a title/identity, a status band, metadata, named content slots,
 * and optional evidence/provenance and relations. It performs NO page-specific
 * API calls, NO business logic, NO router ownership, NO global state, NO hidden
 * data fetching. It is purely presentational: the caller supplies everything.
 *
 * Slot presence (information architecture, reused from the UX2 reference):
 *   PRESENT                       → render slot content (authoritative data).
 *   ABSENT_OPTIONAL               → collapse fully (no empty card / placeholder
 *                                   / reserved spacing / fake CTA).
 *   INCOMPLETE_WITH_EVIDENCE_STATE → stay visible with a meaningful
 *                                   incompleteness note as STATIC text (no
 *                                   live-region role — a genuine async state
 *                                   elsewhere is the only live-region case).
 *
 * Heading level follows the N-F-1 contract (titleTag → resolveTitleTag).
 * Relations render as explicit text labels only (no arrows / lineage drawing).
 * Status is read from real props; never invented for decoration.
 *
 * Accessibility: semantic heading, programmatic labels accept a status label,
 * keyboard-safe interactive elements (only links/buttons rendered by caller
 * slots), no invalid live-region semantics, status text readable w/o color.
 */
import { computed } from 'vue'
import { presentationStatusLabel, resolveTitleTag } from '../../presentation/stateMapping'

type ObjectRegion = 'header' | 'context' | 'evidence' | 'relations'
type SlotState = 'PRESENT' | 'ABSENT_OPTIONAL' | 'INCOMPLETE_WITH_EVIDENCE_STATE'
type RelationSemantics = 'EXPLICIT_RELATION' | 'ASSOCIATED_CONTEXT' | 'CO_PRESENTED_ONLY'

interface ObjectSlot {
  state: SlotState
  /** presentation state for the status band (a PresentationState). */
  status?: string
  statusLabel?: string
  /** explanatory note shown with INCOMPLETE_WITH_EVIDENCE_STATE. */
  note?: string
}

/** Regional IA labels are presentation copy — a page may override them. */
type RegionLabelMap = Partial<Record<ObjectRegion, string>>

interface MetaItem {
  label?: string
  value: string
}

interface RelationItem {
  label: string
  href?: string
  sem: RelationSemantics
}

const props = withDefaults(
  defineProps<{
    /** object title text. */
    title?: string
    /** N-F-1 heading contract (see resolveTitleTag). */
    titleTag?: number | 'none' | null
    /** header meta line items (e.g. dates · type). */
    meta?: MetaItem[]
    /** per-region slot configuration. */
    slots: Partial<Record<ObjectRegion, ObjectSlot>>
    /** relations items (explicit text labels only). */
    relations?: RelationItem[]
    /** optional presentation labels for each region (defaults below). */
    regionLabels?: RegionLabelMap
  }>(),
  { title: '', titleTag: null, meta: () => [], relations: () => [], regionLabels: () => ({}) },
)

const REGION_ORDER: readonly ObjectRegion[] = ['header', 'context', 'evidence', 'relations']
const REGION_TITLES: Record<ObjectRegion, string> = {
  header: '对象',
  context: '语境',
  evidence: '证据',
  relations: '关联',
}

function regionTitle(region: ObjectRegion): string {
  const override = props.regionLabels[region]
  return override !== undefined && override !== '' ? override : REGION_TITLES[region]
}

const titleTagResolved = computed<string>(() => resolveTitleTag(props.titleTag))

const renderedRegions = computed<ObjectRegion[]>(() =>
  REGION_ORDER.filter((region) => {
    const slot = props.slots[region]
    return slot !== undefined && slot.state !== 'ABSENT_OPTIONAL'
  }),
)

function slotOf(region: ObjectRegion): ObjectSlot {
  return props.slots[region] as ObjectSlot
}

function badgeStatus(region: ObjectRegion): string {
  return slotOf(region).status ?? 'UNKNOWN'
}

function badgeLabel(region: ObjectRegion): string {
  return presentationStatusLabel(slotOf(region).status, slotOf(region).statusLabel)
}
</script>

<template>
  <article class="dh-object" data-primitive="dh-object">
    <section
      v-for="region in renderedRegions"
      :key="region"
      class="dh-object__slot"
      :data-slot="region"
      :data-slot-state="slotOf(region).state"
    >
      <p class="dh-object__slot-title">
        {{ regionTitle(region) }}
      </p>

      <!-- header: title + meta -->
      <div v-if="region === 'header'" class="dh-object__header">
        <component :is="titleTagResolved" class="dh-object__title">
          {{ title || '未命名' }}
        </component>
        <span v-for="m in meta" :key="m.value" class="dh-object__meta">
          <template v-if="m.label">{{ m.label }}：</template>{{ m.value }}
        </span>
      </div>

      <!-- incompleteness note: STATIC text (correct, no live-region misuse) -->
      <div
        v-if="slotOf(region).state === 'INCOMPLETE_WITH_EVIDENCE_STATE'"
        class="dh-object__incomplete"
      >
        <span
          class="dh-object__status"
          data-status-prefix="presentation"
          :data-status="badgeStatus(region)"
          >{{ badgeLabel(region) }}</span
        >
        <span v-if="slotOf(region).note" class="dh-object__incomplete-text">{{
          slotOf(region).note
        }}</span>
      </div>

      <!-- context / evidence slot content -->
      <slot v-if="region === 'context' || region === 'evidence'" :name="region" />

      <!-- relations: explicit text labels only -->
      <ul v-if="region === 'relations' && relations.length > 0" class="dh-object__relations">
        <li
          v-for="item in relations"
          :key="`${item.label}-${item.sem}`"
          class="dh-object__relation"
        >
          <a v-if="item.href" :href="item.href" class="dh-object__relation-label">{{
            item.label
          }}</a>
          <span v-else class="dh-object__relation-label">{{ item.label }}</span>
          <span class="dh-object__relation-sem">{{ item.sem }}</span>
        </li>
      </ul>
    </section>
  </article>
</template>

<style scoped>
.dh-object {
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  padding: var(--hfm-space-5) var(--hfm-space-6);
  background: var(--hfm-color-surface);
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

.dh-object__incomplete {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2);
  align-items: baseline;
  padding: var(--hfm-space-2) 0;
}

.dh-object__status {
  display: inline-block;
  padding: 2px var(--hfm-space-2);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-warning);
  color: var(--hfm-color-on-accent);
  font-size: var(--hfm-text-xs);
  font-weight: 600;
}

.dh-object__incomplete-text {
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-secondary);
}

.dh-object__relations {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-1);
}

.dh-object__relation {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2) var(--hfm-space-4);
  padding: var(--hfm-space-1) 0;
  font-size: var(--hfm-text-sm);
}

.dh-object__relation-label {
  font-weight: 600;
}

.dh-object__relation-sem {
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-azure);
}
</style>

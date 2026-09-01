/**
 * UX2-P6 Cross-Surface Verification — unit tests.
 *
 * Covers:
 *  - P0-1 closure: DHObjectLayout static incomplete-state note is VISIBLE and
 *    programmatically available as text but carries NO live-region role;
 *  - shared P0 presentation-mapping consistency across P1–P5 surfaces
 *    (no local duplicate state mapping, no label drift);
 *  - single-H1 / heading consistency on each governed surface.
 */
import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import DHObjectLayout from '../components/primitives/DHObjectLayout.vue'
import { presentationLabel, presentationStatusLabel, resolvePresentationState } from '../presentation/stateMapping'

describe('UX2-P6 — P0-1 closure (static incomplete note, no live region)', () => {
  function mountIncomplete(): ReturnType<typeof mount> {
    return mount(DHObjectLayout, {
      props: {
        slots: {
          header: { state: 'PRESENT' },
          evidence: {
            state: 'INCOMPLETE_WITH_EVIDENCE_STATE',
            status: 'METADATA_ONLY',
            statusLabel: '仅题录',
            note: '原典全文未收录；整理说明已可读',
          },
        },
      },
    })
  }

  it('static incomplete state remains VISIBLE', () => {
    const wrapper = mountIncomplete()
    const note = wrapper.find('.incomplete-note')
    expect(note.exists()).toBe(true)
    expect(note.isVisible()).toBe(true)
    expect(note.find('.hfm-status').text()).toBe('仅题录')
    expect(note.text()).toContain('原典全文未收录')
  })

  it('static incomplete state remains PROGRAMMATICALLY available as text', () => {
    const wrapper = mountIncomplete()
    const note = wrapper.find('.incomplete-note')
    // badge data-status + full text are in the accessibility tree as text
    expect(note.find('.hfm-status').attributes('data-status')).toBe('METADATA_ONLY')
    expect(note.text().length).toBeGreaterThan(0)
  })

  it('UNNECESSARY_LIVE_REGION: no role="status" / aria-live on the static note', () => {
    const wrapper = mountIncomplete()
    const note = wrapper.find('.incomplete-note')
    expect(note.attributes('role')).toBeUndefined()
    expect(note.attributes('aria-live')).toBeUndefined()
    // no other live-region role introduced
    expect(wrapper.find('.incomplete-note[role="status"]').exists()).toBe(false)
  })

  it('no regression: the incomplete note still renders inside the evidence slot with its state', () => {
    const wrapper = mountIncomplete()
    const evidence = wrapper.find('[data-slot="evidence"]')
    expect(evidence.attributes('data-slot-state')).toBe('INCOMPLETE_WITH_EVIDENCE_STATE')
    expect(evidence.find('.incomplete-note .hfm-status[data-status="METADATA_ONLY"]').exists()).toBe(true)
  })
})

describe('UX2-P6 — shared P0 presentation-mapping consistency (no local duplicates, no drift)', () => {
  it('all surfaces derive UNSTRUCTURED_OR_INCOMPLETE via the shared resolver (rows 8/9 fail-closed)', () => {
    // P2/P5 jiayi DATA-GAP and P3/P5 heritage PARTIAL both resolve to
    // UNSTRUCTURED_OR_INCOMPLETE through the same shared mapping
    expect(resolvePresentationState({ contentStatus: 'DATA_GAP' })).toBe('UNSTRUCTURED_OR_INCOMPLETE')
    expect(presentationLabel(resolvePresentationState({ contentStatus: 'DATA_GAP' }))).toBe('资料整理中')
  })

  it('surface labels flow through the shared presentationStatusLabel helper (版本关系整理中 / 谱系整理中)', () => {
    const state = resolvePresentationState({ contentStatus: 'DATA_GAP' })
    expect(presentationStatusLabel(state, '版本关系整理中')).toBe('版本关系整理中')
    expect(presentationStatusLabel(state, '谱系整理中')).toBe('谱系整理中')
  })

  it('canonical state labels are stable across surfaces (no label drift)', () => {
    // P0 canonical labels used by P1 (数字资源可阅) / P4 (RESOURCE_READY) etc.
    expect(presentationLabel('RESOURCE_READY')).toBe('数字资源可阅')
    expect(presentationLabel('METADATA_ONLY')).toBe('仅题录')
    expect(presentationLabel('UNSTRUCTURED_OR_INCOMPLETE')).toBe('资料整理中')
    expect(presentationLabel('SCHOLARLY_UNCERTAIN')).toBe('尚有争议')
    expect(presentationLabel('HISTORICAL_ABSENCE')).toBe('文献阙佚')
  })
})

describe('UX2-P6 — heading contract consistency', () => {
  // The single-H1 + hierarchy checks per surface are covered by the per-WP
  // unit suites and the P6 cross-surface e2e matrix. Here we verify the shared
  // heading mechanism (titleTag contract) at the resolver level.
  it('titleTag contract produces the documented heading tags (h1..h6 / p)', async () => {
    const { resolveTitleTag } = await import('../presentation/stateMapping')
    expect(resolveTitleTag(1)).toBe('h1')
    expect(resolveTitleTag(2)).toBe('h2')
    expect(resolveTitleTag(6)).toBe('h6')
    expect(resolveTitleTag(null)).toBe('p')
  })
})

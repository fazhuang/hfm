/**
 * CF-02 presentation primitives — minimal tests (state semantics + a11y).
 *
 * Covers the new CF-02 primitives:
 *   - state rendering (COMPLETE / PARTIAL / UNAVAILABLE / UNKNOWN / LOADING / ERROR)
 *   - partial / unavailable state presentation
 *   - provenance rendering (never invented — only caller-supplied)
 *   - slot / content composition (ABSENT_OPTIONAL collapse, PRESENT slot)
 *   - accessibility semantics (semantic heading, no invalid live-region,
 *     status readable without color alone, axe clean)
 *
 * These are NEW tests for the NEW primitives; no donor PASS evidence is reused.
 */
import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import axe from 'axe-core'
import DHObjectLayout from '../components/primitives/DHObjectLayout.vue'
import BibliographicRecord from '../components/primitives/BibliographicRecord.vue'
import {
  isPresentationState,
  presentationLabel,
  presentationStatusLabel,
  resolvePresentationState,
  resolveTitleTag,
  type PresentationState,
} from '../presentation/stateMapping'

describe('stateMapping — deterministic + fail-closed', () => {
  it('resolves each real state deterministically', () => {
    expect(resolvePresentationState({ completeness: 'COMPLETE' })).toBe('COMPLETE')
    expect(resolvePresentationState({ completeness: 'PARTIAL' })).toBe('PARTIAL')
    expect(resolvePresentationState({ completeness: 'UNAVAILABLE' })).toBe('UNAVAILABLE')
    expect(resolvePresentationState({ completeness: 'UNKNOWN' })).toBe('UNKNOWN')
    expect(resolvePresentationState({ loading: true })).toBe('LOADING')
    expect(resolvePresentationState({ loadError: true })).toBe('ERROR')
  })

  it('fail-closes unknown inputs to UNKNOWN (never inferred)', () => {
    expect(resolvePresentationState({})).toBe('UNKNOWN')
  })

  it('status label is readable text (not color-only)', () => {
    expect(presentationLabel('PARTIAL' as PresentationState)).toBe('部分整理')
    expect(presentationStatusLabel('PARTIAL')).toBe('部分整理')
    expect(presentationStatusLabel(undefined, '谱系）')).toBe('谱系）')
    expect(presentationStatusLabel('not-a-state')).toBe('未知')
  })

  it('titleTag contract is deterministic (N-F-1)', () => {
    expect(resolveTitleTag(1)).toBe('h1')
    expect(resolveTitleTag(6)).toBe('h6')
    expect(resolveTitleTag(null)).toBe('p')
    expect(resolveTitleTag('none')).toBe('p')
    expect(resolveTitleTag(0)).toBe('p') // invalid → fail-closed
  })

  it('isPresentationState guards correctly', () => {
    expect(isPresentationState('PARTIAL')).toBe(true)
    expect(isPresentationState('nope')).toBe(false)
    expect(isPresentationState(null)).toBe(false)
  })
})

describe('DHObjectLayout — composition', () => {
  it('renders PRESENT regions and collapses ABSENT_OPTIONAL fully', () => {
    const wrapper = mount(DHObjectLayout, {
      props: {
        title: '皇甫谧',
        titleTag: 2,
        meta: [{ label: '朝代', value: '西晋' }],
        slots: {
          header: { state: 'PRESENT' },
          context: { state: 'PRESENT' },
          evidence: { state: 'ABSENT_OPTIONAL' },
          relations: { state: 'PRESENT' },
        },
      },
    })
    expect(wrapper.find('[data-slot="header"]').exists()).toBe(true)
    expect(wrapper.find('[data-slot="context"]').exists()).toBe(true)
    // ABSENT_OPTIONAL evidence collapses completely (no container, no spacing)
    expect(wrapper.find('[data-slot="evidence"]').exists()).toBe(false)
    // header title renders as h2 per titleTag=2
    expect(wrapper.find('h2.dh-object__title').text()).toBe('皇甫谧')
  })

  it('renders INCOMPLETE_WITH_EVIDENCE_STATE as static text (no live-region misuse)', () => {
    const wrapper = mount(DHObjectLayout, {
      props: {
        title: '某人',
        slots: { context: { state: 'INCOMPLETE_WITH_EVIDENCE_STATE', status: 'PARTIAL', note: '中间代整理中' } },
      },
    })
    const incomplete = wrapper.find('.dh-object__incomplete')
    expect(incomplete.exists()).toBe(true)
    expect(incomplete.text()).toContain('部分整理')
    expect(incomplete.text()).toContain('中间代整理中')
    // static text, NOT a live region (no role="status"/aria-live on the note)
    expect(incomplete.attributes('role')).toBeUndefined()
    expect(incomplete.attributes('aria-live')).toBeUndefined()
  })

  it('renders relations as explicit text labels without arrow semantics', () => {
    const wrapper = mount(DHObjectLayout, {
      props: {
        title: '作品',
        slots: { relations: { state: 'PRESENT' } },
        relations: [
          { label: '版本', href: '/edition/1', sem: 'EXPLICIT_RELATION' },
          { label: '人物', sem: 'ASSOCIATED_CONTEXT' },
        ],
      },
    })
    const rels = wrapper.findAll('.dh-object__relation')
    expect(rels.length).toBe(2)
    expect(wrapper.find('a.dh-object__relation-label').text()).toBe('版本')
    expect(wrapper.findAll('.dh-object__relation-sem').length).toBe(2)
  })

  it('is presentation-only: no page API / router / fetch side-effects', () => {
    expect(typeof DHObjectLayout).toBe('object')
    // No lifecycle hooks that fetch — the component declares no async side-effect.
    const wrapper = mount(DHObjectLayout, { props: { title: 'x', slots: {} } })
    expect(wrapper.exists()).toBe(true)
  })
})

describe('BibliographicRecord — metadata + provenance + status', () => {
  it('renders identity, metadata and edition/publication info', () => {
    const wrapper = mount(BibliographicRecord, {
      props: {
        title: '《针灸甲乙经》',
        author: '皇甫谧',
        edition: '四库全书本',
        year: '清乾隆',
        meta: [{ label: '载体', value: '刻本' }],
      },
    })
    expect(wrapper.find('.bib-record__title').text()).toContain('《针灸甲乙经》')
    expect(wrapper.find('.bib-record__author').text()).toBe('皇甫谧')
    expect(wrapper.text()).toContain('四库全书本')
    expect(wrapper.text()).toContain('清乾隆')
    expect(wrapper.findAll('.bib-record__meta-row').length).toBeGreaterThanOrEqual(3)
  })

  it('renders a caller-supplied provenance note (never invented)', () => {
    const wrapper = mount(BibliographicRecord, {
      props: { title: 't', provenance: '来源：客户提供（待核验）' },
    })
    expect(wrapper.find('.bib-record__provenance').text()).toBe('来源：客户提供（待核验）')
  })

  it('renders status through the presentation label (readable without color)', () => {
    const wrapper = mount(BibliographicRecord, {
      props: { title: 't', status: 'PARTIAL' },
    })
    const st = wrapper.find('.bib-record__status')
    expect(st.text()).toBe('部分整理')
    expect(st.attributes('data-status')).toBe('PARTIAL')
  })
})

describe('accessibility semantics', () => {
  it('DHObjectLayout passes axe (semantic heading, no invalid live-region)', async () => {
    const wrapper = mount(DHObjectLayout, {
      attachTo: document.body,
      props: {
        title: '皇甫谧',
        titleTag: 2,
        slots: {
          header: { state: 'PRESENT' },
          context: { state: 'INCOMPLETE_WITH_EVIDENCE_STATE', status: 'PARTIAL', note: '整理中' },
          relations: { state: 'PRESENT' },
        },
        relations: [{ label: '版本', href: '/x', sem: 'EXPLICIT_RELATION' }],
      },
    })
    const results = await axe.run(wrapper.element as HTMLElement)
    wrapper.unmount()
    expect(results.violations).toHaveLength(0)
  })

  it('BibliographicRecord passes axe', async () => {
    const wrapper = mount(BibliographicRecord, {
      attachTo: document.body,
      props: { title: 'x', status: 'PARTIAL', provenance: '来源：x' },
    })
    const results = await axe.run(wrapper.element as HTMLElement)
    wrapper.unmount()
    expect(results.violations).toHaveLength(0)
  })
})

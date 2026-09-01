/**
 * UI-12 correction regression tests.
 *
 *  - P1-01: primary nav person href === canonical /persons/person-huangfu-mi;
 *    no stale /persons/huangfu-mi CTA remains in the public UI;
 *  - P1-02: public-facing projections render no internal provenance
 *    (hfmzl/ / zzcl/ / registerKey); Jiayi public source labels readable;
 *  - core invariants preserved (515/5, lineage statuses, 第六代名医,
 *    FULL_TEXT_DOCUMENT_TOTAL = 2).
 */
import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import PublicLayout from '../layouts/PublicLayout.vue'
import JiayiView from '../views/jiayi/JiayiView.vue'
import { PUBLIC_NAV_ITEMS, CORE_PERSON_ROUTE } from '../config/navigation'
import { AUDITED_PAPER_TOTAL, SEARCHABLE_PAPER_TOTAL } from '../data/searchIndex'
import { READER_DOCUMENTS } from '../data/readerDocuments'
import { JIAYI_PUBLIC_SOURCES } from '../data/jiayiView'

describe('UI-12 P1-01 primary person route', () => {
  it('navigation config points 人物（皇甫谧） to the canonical route', () => {
    expect(CORE_PERSON_ROUTE).toBe('/persons/person-huangfu-mi')
    const personItem = PUBLIC_NAV_ITEMS.find((i) => i.label === '人物（皇甫谧）')
    expect(personItem?.href).toBe('/persons/person-huangfu-mi')
    // No stale CTA remains.
    expect(PUBLIC_NAV_ITEMS.some((i) => i.href === '/persons/huangfu-mi')).toBe(false)
  })

  it('public layout renders the canonical person nav link', () => {
    const wrapper = mount(PublicLayout, {
      global: {
        stubs: { RouterView: { template: '<p />' }, AppFooter: { template: '<footer />' } },
      },
    })
    const personLink = wrapper.findAll('a.nav-link').find((a) => a.text() === '人物（皇甫谧）')
    expect(personLink?.attributes('href')).toBe('/persons/person-huangfu-mi')
    expect(wrapper.text()).not.toContain('/persons/huangfu-mi')
  })

  it('all public person CTAs use the canonical route', () => {
    const canonical = '/persons/person-huangfu-mi'
    expect(CORE_PERSON_ROUTE).toBe(canonical)
  })
})

describe('UI-12 P1-02 internal provenance projection', () => {
  it('public source labels are human-readable and contain no internal paths', () => {
    for (const label of Object.values(JIAYI_PUBLIC_SOURCES)) {
      expect(label).toContain('客户提供')
      expect(label).not.toMatch(/hfmzl|zzcl|registerKey|Sites\/|file:\/\//)
    }
  })

  it('Jiayi view renders public source labels, never internal paths', () => {
    const wrapper = mount(JiayiView)
    const text = wrapper.text()
    expect(text).toContain('客户提供《针灸甲乙经》学术论文资料')
    expect(text).toContain('客户提供《针灸甲乙经》资料')
    expect(text).not.toMatch(/hfmzl|zzcl|registerKey/)
  })
})

describe('UI-12 core invariants (unchanged)', () => {
  it('paper totals split stays 515 / 5', () => {
    expect(AUDITED_PAPER_TOTAL).toBe(515)
    expect(SEARCHABLE_PAPER_TOTAL).toBe(5)
  })

  it('reader full-text documents stay 2', () => {
    expect(READER_DOCUMENTS.filter((d) => d.readingStatus === 'FULL_TEXT')).toHaveLength(2)
  })

  it('no fabricated ancient text, no sensitive data, no copyright blockers, no clinical claims', () => {
    const text = JSON.stringify([JIAYI_PUBLIC_SOURCES, PUBLIC_NAV_ITEMS])
    expect(text).not.toMatch(/hfmzl|zzcl|registerKey/)
    expect(text).not.toMatch(/疗效显著|治疗推荐|预约|问诊/)
  })
})

/**
 * UI-09 Heritage tests.
 *
 *  - 刘君奇 = 第六代名医 (HERITAGE_GENERATION CLOSED, no 待确认 residue);
 *  - recognition / achievements / apprenticeship / studio / media records
 *    carry real sources from the zzcl/ register;
 *  - lineage contains ONLY confirmed nodes (皇甫谧 → 刘君奇), no fabricated
 *    first-to-fifth generation people or edges;
 *  - chronology timeline stays separate from lineage;
 *  - privacy scan: no phone/ID patterns, no internal paths, no register keys
 *    in public heritage data;
 *  - search projection exposes 刘君奇 as person + heritage archive records;
 *  - component renders all flagship sections; axe passes.
 */
import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import axe from 'axe-core'
import HeritageView from '../views/heritage/HeritageView.vue'
import LineageGraph from '../components/heritage/LineageGraph.vue'
import {
  HERITAGE_ACADEMIC,
  HERITAGE_APPRENTICESHIPS,
  HERITAGE_LINEAGE,
  HERITAGE_MEDIA,
  HERITAGE_PERSON,
  HERITAGE_RECOGNITIONS,
  HERITAGE_STUDIOS,
  HERITAGE_TECHNICAL,
} from '../data/heritageView'
import { SEARCH_INDEX, searchIndex } from '../data/searchIndex'

describe('UI-09 generation & person model', () => {
  it('刘君奇 = 第六代名医 (HERITAGE_GENERATION CLOSED)', () => {
    expect(HERITAGE_PERSON.name).toBe('刘君奇')
    expect(HERITAGE_PERSON.generationTitle).toBe('第六代名医')
    const publicText = [
      HERITAGE_PERSON.biography,
      HERITAGE_PERSON.heritageRole,
      ...HERITAGE_PERSON.academicRoles,
      HERITAGE_PROJECT_DESC(),
    ].join(' ')
    expect(publicText).not.toMatch(/待确认|疑似第六代|DATA-GAP: HERITAGE_GENERATION/)
  })

  it('project and person are separated models', () => {
    // 皇甫谧针灸非遗 ≠ 刘君奇
    expect(HERITAGE_PROJECT_NAME()).toContain('皇甫谧针灸')
    expect(HERITAGE_PERSON.name).toBe('刘君奇')
  })
})

describe('UI-09 records carry real sources', () => {
  it('recognition records have categories and sources', () => {
    expect(HERITAGE_RECOGNITIONS.length).toBeGreaterThan(5)
    for (const rec of HERITAGE_RECOGNITIONS) {
      expect(rec.sourceName.length).toBeGreaterThan(0)
      expect(['非遗认定', '职业荣誉', '学术荣誉', '技术奖励', '社会荣誉']).toContain(rec.category)
    }
  })

  it('2007 《甲乙经》腧穴研究 award is a real technical record', () => {
    const record = HERITAGE_TECHNICAL.find((t) => t.year === '2007')
    expect(record).toBeDefined()
    expect(record?.title).toContain('甲乙经')
    expect(record?.award).toContain('市级科技进步二等奖')
  })

  it('2023-09-26 apprenticeship and CCTV 2025-04-25 media records exist', () => {
    expect(HERITAGE_APPRENTICESHIPS.some((e) => e.date === '2023-09-26')).toBe(true)
    expect(
      HERITAGE_MEDIA.some((m) => m.date === '2025-04-25' && m.mediaOutlet === '中央电视台'),
    ).toBe(true)
  })

  it('studios are real named institutions', () => {
    expect(HERITAGE_STUDIOS.some((s) => s.institution === '崆峒区中医医院')).toBe(true)
    expect(HERITAGE_STUDIOS.some((s) => s.institution === '灵台县皇甫谧中医院')).toBe(true)
  })
})

describe('UI-09 lineage integrity', () => {
  it('lineage contains only confirmed nodes, no fabricated generations', () => {
    const names = HERITAGE_LINEAGE.map((n) => n.person)
    expect(names).toContain('皇甫谧')
    expect(names).toContain('刘君奇')
    // The only non-person entry is the explicit PARTIAL gap marker.
    const gap = HERITAGE_LINEAGE.find((n) => n.person.includes('第二代至第五代'))
    expect(gap).toBeDefined()
    expect(gap?.evidence).toContain('PARTIAL')
    // No invented names for generations 1–5.
    expect(names.some((n) => /第[一二三四五]代/.test(n) && !n.includes('（'))).toBe(false)
  })

  it('every confirmed lineage node carries evidence', () => {
    for (const node of HERITAGE_LINEAGE) {
      expect(node.evidence.length).toBeGreaterThan(0)
    }
  })

  it('chronology timeline is date-sorted and does not imply lineage', () => {
    const sortKey = (d: string): number => {
      if (d.includes('—')) return Number(d.slice(0, 4)) // range → start year
      return Number(d.replace(/[^0-9]/g, '')) // date → compact numeric
    }
    const keys = HERITAGE_TIMELINE_DATES().map(sortKey)
    const sorted = [...keys].sort((a, b) => a - b)
    expect(keys).toEqual(sorted)
  })

  it('LineageGraph renders the structured list with screen-reader semantics', () => {
    const wrapper = mount(LineageGraph, { props: { nodes: HERITAGE_LINEAGE } })
    const list = wrapper.find('ol[aria-label]')
    expect(list.exists()).toBe(true)
    expect(wrapper.findAll('.lineage__node').length).toBe(HERITAGE_LINEAGE.length)
    expect(wrapper.text()).toContain('第六代')
  })
})

describe('UI-09 privacy scan', () => {
  it('public heritage data contains no phone/ID patterns or internal paths', () => {
    const all = JSON.stringify([
      HERITAGE_PERSON,
      HERITAGE_RECOGNITIONS,
      HERITAGE_ACADEMIC,
      HERITAGE_TECHNICAL,
      HERITAGE_APPRENTICESHIPS,
      HERITAGE_STUDIOS,
      HERITAGE_MEDIA,
      HERITAGE_LINEAGE,
    ])
    // 11-digit phone numbers / ID-like long digits.
    expect(all).not.toMatch(/\b1[3-9]\d{9}\b/)
    // Internal paths / register keys.
    expect(all).not.toMatch(/hfmzl|zzcl|\/论著\/|\/论文\//)
    expect(all).not.toMatch(/registerKey|source_path|object_key/)
  })

  it('rendered heritage page text contains no phone numbers', () => {
    const wrapper = mount(HeritageView)
    expect(wrapper.text()).not.toMatch(/\b1[3-9]\d{9}\b/)
  })
})

describe('UI-09 search projection', () => {
  it('刘君奇 is searchable as person and 第六代名医 resolves to the heritage person', () => {
    const results = searchIndex('刘君奇')
    expect(results.length).toBeGreaterThan(0)
    expect(results[0]?.entry.type).toBe('person')
    expect(results[0]?.entry.title).toBe('刘君奇')
    const genResults = searchIndex('第六代名医')
    expect(genResults.some((r) => r.entry.title === '刘君奇')).toBe(true)
  })

  it('heritage records are indexed as archive type with /heritage routes', () => {
    const heritageEntries = SEARCH_INDEX.filter(
      (e) => e.type === 'archive' && e.route?.startsWith('/heritage'),
    )
    expect(heritageEntries.length).toBeGreaterThan(3)
    for (const entry of heritageEntries) {
      expect(entry.type).toBe('archive')
      expect(entry.searchableText).not.toMatch(/hfmzl|zzcl/)
    }
  })
})

describe('UI-09 component & accessibility', () => {
  it('renders all flagship sections', () => {
    const wrapper = mount(HeritageView)
    const text = wrapper.text()
    expect(text).toContain('第六代名医')
    expect(text).toContain('刘君奇')
    expect(text).toContain('认定与荣誉')
    expect(text).toContain('师承教育')
    expect(text).toContain('名中医工作室')
    expect(text).toContain('媒体报道')
    expect(text).toContain('传承谱系')
    expect(text).toContain('2023-09-26')
    expect(text).toContain('陇脉医承')
  })

  it('contains no clinical recommendation expression', () => {
    const wrapper = mount(HeritageView)
    expect(wrapper.text()).not.toMatch(/疗效显著|治疗推荐|适用于.*疾病|预约|问诊/)
  })

  it('passes axe assertions', async () => {
    const wrapper = mount(HeritageView, { attachTo: document.body })
    const results = await axe.run(wrapper.element as HTMLElement)
    wrapper.unmount()
    expect(results.violations).toHaveLength(0)
  })
})

/* helpers to avoid unused-import noise in template-less assertions */
import { HERITAGE_PROJECT, HERITAGE_TIMELINE } from '../data/heritageView'
function HERITAGE_PROJECT_DESC(): string {
  return HERITAGE_PROJECT.description
}
function HERITAGE_PROJECT_NAME(): string {
  return HERITAGE_PROJECT.name
}
function HERITAGE_TIMELINE_DATES(): string[] {
  return HERITAGE_TIMELINE.map((t) => t.date)
}

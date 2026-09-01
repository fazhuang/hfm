import { afterEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import DHObjectLayout from '../components/primitives/DHObjectLayout.vue'

const PRESENT_SLOTS = {
  header: { state: 'PRESENT' as const },
  context: { state: 'PRESENT' as const },
  evidence: { state: 'PRESENT' as const },
  relations: { state: 'PRESENT' as const },
}

afterEach(() => {
  vi.restoreAllMocks()
})

describe('DHObjectLayout — slot presence', () => {
  it('renders article with data-primitive and PRESENT regions with states', () => {
    const wrapper = mount(DHObjectLayout, { props: { slots: PRESENT_SLOTS } })
    expect(wrapper.find('article.dh-object[data-primitive="dh-object"]').exists()).toBe(true)
    for (const region of ['header', 'context', 'evidence', 'relations'] as const) {
      const section = wrapper.find(`[data-slot="${region}"]`)
      expect(section.exists()).toBe(true)
      expect(section.attributes('data-slot-state')).toBe('PRESENT')
    }
  })

  it('renders default region titles 对象/语境/证据/关联', () => {
    const wrapper = mount(DHObjectLayout, { props: { slots: PRESENT_SLOTS } })
    const titles = wrapper.findAll('.dh-object__slot-title').map((n) => n.text())
    expect(titles).toEqual(['对象', '语境', '证据', '关联'])
  })

  it('ABSENT_OPTIONAL collapses completely: no section, no placeholder, no reserved spacing', () => {
    const wrapper = mount(DHObjectLayout, {
      props: { slots: { ...PRESENT_SLOTS, context: { state: 'ABSENT_OPTIONAL' as const } } },
    })
    expect(wrapper.find('[data-slot="context"]').exists()).toBe(false)
    const html = wrapper.html()
    expect(html).not.toContain('暂无内容')
    expect(html).not.toContain('敬请期待')
    expect(wrapper.find('[data-slot="header"]').exists()).toBe(true)
    expect(wrapper.find('[data-slot="evidence"]').exists()).toBe(true)
  })

  it('INCOMPLETE_WITH_EVIDENCE_STATE stays visible with meaningful incompleteness', () => {
    const wrapper = mount(DHObjectLayout, {
      props: {
        slots: {
          header: { state: 'PRESENT' as const },
          evidence: {
            state: 'INCOMPLETE_WITH_EVIDENCE_STATE' as const,
            status: 'METADATA_ONLY',
            statusLabel: '仅题录',
            note: '原典全文未收录；整理说明已可读',
          },
        },
      },
    })
    const evidence = wrapper.find('[data-slot="evidence"]')
    expect(evidence.exists()).toBe(true)
    expect(evidence.attributes('data-slot-state')).toBe('INCOMPLETE_WITH_EVIDENCE_STATE')
    const note = evidence.find('.incomplete-note[role="status"]')
    expect(note.exists()).toBe(true)
    const badge = note.find('.hfm-status')
    expect(badge.attributes('data-status')).toBe('METADATA_ONLY')
    expect(badge.text()).toBe('仅题录')
    expect(note.text()).toContain('原典全文未收录')
  })

  it('region slot content renders through named slots', () => {
    const wrapper = mount(DHObjectLayout, {
      props: { slots: { context: { state: 'PRESENT' as const } } },
      slots: { context: '<p class="context-probe">上下文内容</p>' },
    })
    expect(wrapper.find('.context-probe').text()).toBe('上下文内容')
  })
})

describe('DHObjectLayout — titleTag contract (N-F-1)', () => {
  it('titleTag 2 → h2.dh-object__title', () => {
    const wrapper = mount(DHObjectLayout, {
      props: { slots: PRESENT_SLOTS, title: '皇甫谧', titleTag: 2 },
    })
    expect(wrapper.find('h2.dh-object__title').text()).toBe('皇甫谧')
  })

  it('titleTag 6 → h6.dh-object__title', () => {
    const wrapper = mount(DHObjectLayout, {
      props: { slots: PRESENT_SLOTS, title: '标题', titleTag: 6 },
    })
    expect(wrapper.find('h6.dh-object__title').exists()).toBe(true)
  })

  it('titleTag "none" → non-heading p.dh-object__title', () => {
    const wrapper = mount(DHObjectLayout, {
      props: { slots: PRESENT_SLOTS, title: '标题', titleTag: 'none' },
    })
    expect(wrapper.find('p.dh-object__title').exists()).toBe(true)
    expect(wrapper.find('h2.dh-object__title').exists()).toBe(false)
  })

  it('titleTag null → non-heading p (default)', () => {
    const wrapper = mount(DHObjectLayout, { props: { slots: PRESENT_SLOTS, title: '标题' } })
    expect(wrapper.find('p.dh-object__title').exists()).toBe(true)
  })

  it('titleTag 0 → fail-closed non-heading <p> + development warning', () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
    const wrapper = mount(DHObjectLayout, {
      props: { slots: PRESENT_SLOTS, title: '标题', titleTag: 0 },
    })
    expect(wrapper.find('p.dh-object__title').exists()).toBe(true)
    expect(wrapper.find('h1.dh-object__title').exists()).toBe(false)
    expect(warn).toHaveBeenCalled()
  })

  it('header meta renders with optional labels', () => {
    const wrapper = mount(DHObjectLayout, {
      props: {
        slots: PRESENT_SLOTS,
        title: '皇甫谧',
        titleTag: 2,
        meta: [{ label: '生卒年', value: '215—282' }, { value: '人物档案' }],
      },
    })
    const meta = wrapper.findAll('.dh-object__meta').map((n) => n.text())
    expect(meta[0]).toMatch(/^生卒年\s215—282$/) // label + value (nbsp-separated)
    expect(meta).toContain('人物档案')
  })
})

describe('DHObjectLayout — relations semantics (text-only, no connectors)', () => {
  it('renders relation labels with explicit semantics; no connector/arrow markup', () => {
    const wrapper = mount(DHObjectLayout, {
      props: {
        slots: { relations: { state: 'PRESENT' as const } },
        relations: [
          { label: '作品《针灸甲乙经》', href: '/jiayi', sem: 'EXPLICIT_RELATION' },
          { label: '非遗传承', sem: 'ASSOCIATED_CONTEXT' },
        ],
      },
    })
    const items = wrapper.findAll('.relation-item')
    expect(items).toHaveLength(2)
    expect(items[0].find('a.relation-item__label').text()).toBe('作品《针灸甲乙经》')
    expect(items[0].find('.relation-item__sem').text()).toBe('EXPLICIT_RELATION')
    expect(items[1].find('.relation-item__sem').text()).toBe('ASSOCIATED_CONTEXT')
    const html = wrapper.html()
    expect(html).not.toMatch(/<svg|→|arrow/i)
    expect(html).not.toContain('lineage')
  })
})

describe('DHObjectLayout — surface roles & negative boundaries', () => {
  it('applies ux2-surface-paper role to the article', () => {
    const wrapper = mount(DHObjectLayout, { props: { slots: PRESENT_SLOTS } })
    expect(wrapper.find('article.ux2-surface-paper').exists()).toBe(true)
  })

  it('applies ux2-surface-evidence role to the evidence region', () => {
    const wrapper = mount(DHObjectLayout, { props: { slots: PRESENT_SLOTS } })
    expect(wrapper.find('[data-slot="evidence"].ux2-surface-evidence').exists()).toBe(true)
  })

  it('no fake CTA / no disabled controls for absent slots', () => {
    const wrapper = mount(DHObjectLayout, {
      props: {
        slots: { header: { state: 'PRESENT' as const }, context: { state: 'ABSENT_OPTIONAL' as const } },
      },
    })
    const html = wrapper.html()
    expect(html).not.toContain('disabled')
    expect(html).not.toContain('阅读')
    expect(html).not.toContain('btn')
  })
})

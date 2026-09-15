/**
 * 其人模块叙事长页（P-7）。
 *
 * 核心人物（皇甫谧）走宪章 §3.1 的五段：定位 / 画像 / 年表 / 传略 / 延伸；
 * 其余人物走通用档案版式。这里钉住两条：
 *   1. 核心人物页确实渲染了叙事各段与后论四表；
 *   2. 两者互斥——核心人物页不再落到档案版式，其余人物也不误入叙事页。
 */

import { afterEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import axe from 'axe-core'

import PersonDetailView from '../views/persons/PersonDetailView.vue'
import { CORE_PERSON_ENTITY_ID } from '../config/corePerson'
import { HOURAN_TABLES } from '../data/houranTables'
import type { PublicPerson } from '../types/public'

const mountedWrappers: ReturnType<typeof mount>[] = []

afterEach(() => {
  for (const wrapper of mountedWrappers.splice(0)) wrapper.unmount()
  vi.restoreAllMocks()
})

const PERSON: PublicPerson = {
  entity_id: CORE_PERSON_ENTITY_ID,
  name_zh: '皇甫谧',
  name_pinyin: 'Huangfu Mi',
  courtesy_name: '士安',
  pseudonym: '玄晏先生',
  dynasty: '西晋',
  publication_status: 'PUBLISHED',
  assertions: [],
  events: [],
}

function envelope(data: unknown): { ok: true; status: 200; json: () => Promise<unknown> } {
  return { ok: true, status: 200, json: () => Promise.resolve({ data }) }
}

async function mountPerson(routeId: string): Promise<ReturnType<typeof mount>> {
  vi.stubGlobal(
    'fetch',
    vi.fn(() => Promise.resolve(envelope({ ...PERSON, entity_id: routeId }))),
  )
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/persons/:id', component: PersonDetailView }],
  })
  router.push(`/persons/${routeId}`)
  await router.isReady()
  const wrapper = mount(PersonDetailView, {
    attachTo: document.body,
    global: { plugins: [router] },
  })
  mountedWrappers.push(wrapper)
  await vi.waitFor(() => {
    expect(wrapper.find('h1').exists()).toBe(true)
  })
  return wrapper
}

describe('P-7 其人叙事长页', () => {
  it('核心人物渲染定位段：姓名、生卒、定义、四重身份', async () => {
    const wrapper = await mountPerson(CORE_PERSON_ENTITY_ID)
    const text = wrapper.text()
    expect(wrapper.find('.core-hero__name').text()).toBe('皇甫谧')
    expect(text).toContain('215—282')
    expect(text).toContain('针灸鼻祖')
    expect(wrapper.findAll('.core-hero__identities li').map((n) => n.text())).toEqual([
      '医学家',
      '文学家',
      '史学家',
      '学者',
    ])
  })

  it('画像指向已发布媒体资产的字节端点', async () => {
    const wrapper = await mountPerson(CORE_PERSON_ENTITY_ID)
    const src = wrapper.find('.core-hero__portrait img').attributes('src') ?? ''
    expect(src).toMatch(/\/api\/v1\/public\/media\/[^/]+\/bytes$/)
    // 有图必须有无障碍替代文本，且说清是画像。
    expect(wrapper.find('.core-hero__portrait img').attributes('alt')).toContain('皇甫谧')
  })

  it('年表渲染人生四阶段', async () => {
    const wrapper = await mountPerson(CORE_PERSON_ENTITY_ID)
    const nodes = wrapper.findAll('.timeline__node')
    expect(nodes).toHaveLength(4)
    expect(nodes.map((n) => n.text()).join('')).toContain('求学悟道')
    expect(nodes.map((n) => n.text()).join('')).toContain('著书传世')
  })

  it('传略渲染后论四表，行数与数据源完全一致', async () => {
    const wrapper = await mountPerson(CORE_PERSON_ENTITY_ID)
    const blocks = wrapper.findAll('.core-table-block')
    expect(blocks).toHaveLength(HOURAN_TABLES.length)
    expect(blocks.map((b) => b.find('.core-table-block__title').text())).toEqual([
      '论其人',
      '演其人',
      '讲其人',
      '冠其名',
    ])
    const expected = HOURAN_TABLES.reduce((n, t) => n + t.rows.length, 0)
    expect(wrapper.findAll('.core-table tbody tr')).toHaveLength(expected)
    expect(expected).toBe(48)
  })

  it('延伸段给出其言与甲乙经入口', async () => {
    const wrapper = await mountPerson(CORE_PERSON_ENTITY_ID)
    const hrefs = wrapper.findAll('.core-more__link').map((a) => a.attributes('href'))
    expect(hrefs).toContain('/yan')
    expect(hrefs).toContain('/jiayi')
  })

  it('核心人物页不落档案版式——门户不做论证', async () => {
    const wrapper = await mountPerson(CORE_PERSON_ENTITY_ID)
    expect(wrapper.find('.dh-object__title').exists()).toBe(false)
    expect(wrapper.find('[data-primitive="person-assertions"]').exists()).toBe(false)
  })

  it('其余人物仍走档案版式，不误入叙事页', async () => {
    const wrapper = await mountPerson('ENT-PERSON-WU-MIANXUE')
    expect(wrapper.find('.dh-object__title').exists()).toBe(true)
    expect(wrapper.find('.core-hero__name').exists()).toBe(false)
    expect(wrapper.find('.core-table').exists()).toBe(false)
  })

  it('叙事长页通过 axe 无障碍检查', async () => {
    const wrapper = await mountPerson(CORE_PERSON_ENTITY_ID)
    const results = await axe.run(wrapper.element as HTMLElement)
    expect(results.violations, JSON.stringify(results.violations.map((v) => v.id))).toHaveLength(0)
  })
})

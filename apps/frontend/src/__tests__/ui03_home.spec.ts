// mypy: disable-error-code="import-untyped,import-not-found"
/**
 * Homepage contract tests — HFM-FRONTEND-CONTENT-CONTRACT v1 §4.
 *
 * The homepage is the customer 5-link navigation's entry surface: hero +
 * 人物 / 其言 / 《针灸甲乙经》 / 非遗传承 + institutional close. Each block
 * binds a T0 published projection and must carry a source marker; T1 fallbacks
 * must be visibly labelled. No fabricated content, no clinical surface, no
 * internal register paths.
 */
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { flushPromises } from '@vue/test-utils'
import axe from 'axe-core'
import HomeView from '../views/HomeView.vue'
import { HOME_BOOK, HOME_HERITAGE_LIVING, HOME_HERO } from '../data/homeProjection'
import { INVENTORY_EDITION_RECORDS } from '../data/contentInventory'
import { CORE_PERSON_ENTITY_ID } from '../config/corePerson'

const SECTION_IDS = ['home-hero', 'home-person', 'home-yan', 'home-book', 'home-heritage', 'home-closing']
const H2_SET = ['皇甫谧', '其言', HOME_BOOK.headline, HOME_HERITAGE_LIVING.headline]

const STUB = { template: '<div />' }
function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: STUB },
      { path: '/search', component: STUB },
    ],
  })
}

/** Flush the contract data layer + render. */
async function mountHome(router = makeRouter(), attach = false) {
  const wrapper = mount(HomeView, {
    attachTo: attach ? document.body : undefined,
    global: { plugins: [router] },
  })
  await flushPromises()
  return wrapper
}

const okResponse = (data: unknown) => ({
  ok: true,
  status: 200,
  json: async () => ({ success: true, data }),
})

beforeEach(() => {
  // Default: backend unavailable → every block degrades to its labelled T1 fallback.
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')))
})
afterEach(() => vi.unstubAllGlobals())

describe('homepage contract — structure (§4)', () => {
  it('renders the hero + four content blocks + close, in order', async () => {
    const wrapper = await mountHome()
    const ids = wrapper.findAll('section[id^="home-"]').map((s) => s.attributes('id'))
    expect(ids).toEqual(SECTION_IDS)
  })

  it('renders exactly one H1 and the contract H2 set', async () => {
    const wrapper = await mountHome()
    expect(wrapper.findAll('h1')).toHaveLength(1)
    expect(wrapper.find('h1').text()).toBe('皇甫谧人文数字平台')
    expect(wrapper.findAll('h2').map((h) => h.text())).toEqual(H2_SET)
    expect(wrapper.find('.home-closing__name').text()).toBe('皇甫谧人文数字平台')
  })

  it('renders real CTA route targets', async () => {
    const wrapper = await mountHome()
    const hrefs = wrapper.findAll('a').map((a) => a.attributes('href'))
    for (const target of [
      `/persons/${CORE_PERSON_ENTITY_ID}`,
      '/yan',
      '/jiayi',
      '/heritage',
      '/search',
    ]) {
      expect(hrefs, target).toContain(target)
    }
  })

  it('preserves the single #home-search-input contract (owned by HomeView)', async () => {
    const wrapper = await mountHome()
    const hero = wrapper.find('#home-hero')
    expect(hero.find('form.home-search').attributes('role')).toBe('search')
    expect(wrapper.findAll('#home-search-input')).toHaveLength(1)
    expect(hero.find('#home-search-input').attributes('placeholder')).toBe('检索平台内容')
  })

  it('closing is a section, never a second global footer', async () => {
    const wrapper = await mountHome()
    expect(wrapper.findAll('footer')).toHaveLength(0)
    expect(wrapper.find('#home-closing').element.tagName).toBe('SECTION')
  })

  it('passes axe assertions', async () => {
    const wrapper = await mountHome(makeRouter(), true)
    const results = await axe.run(wrapper.element as HTMLElement)
    wrapper.unmount()
    expect(results.violations).toHaveLength(0)
  })
})

describe('homepage contract — T0/T1 source discipline (§2 R3, §3)', () => {
  it('marks every block with a data-source and shows labelled fallbacks when T0 is unavailable', async () => {
    const wrapper = await mountHome()
    for (const id of SECTION_IDS) {
      expect(wrapper.find(`#${id}`).attributes('data-source'), id).toBeTruthy()
    }
    // T1 fallbacks are VISIBLE (never silent).
    const notes = wrapper.findAll('[data-fallback-note]')
    expect(notes.length).toBeGreaterThanOrEqual(3)
    expect(wrapper.find('#home-person').text()).toContain('离线兜底')
    expect(wrapper.find('#home-heritage').text()).toContain('离线兜底')
    expect(wrapper.find('#home-yan').text()).toContain('已依公版文献录入')
  })

  it('renders T0 person assertions when the published projection arrives', async () => {
    const fetchMock = vi.fn((url: string) => {
      if (url.includes('/public/persons/')) {
        return Promise.resolve(
          okResponse({
            entity_id: CORE_PERSON_ENTITY_ID,
            name_zh: '皇甫谧',
            name_pinyin: null,
            courtesy_name: null,
            pseudonym: null,
            dynasty: null,
            publication_status: 'PUBLISHED',
            assertions: [
              { id: 'a1', predicate: '医学地位', value: '针灸鼻祖', object_entity_id: null, editorial_status: 'draft', confidence: 'medium' },
            ],
            events: [],
          }),
        )
      }
      if (url.includes('/public/home')) return Promise.resolve(okResponse({ works: [], counts: { works: 14, persons: 17, heritage_projects: 0, c_terms: 30 } }))
      if (url.includes('/public/works/')) return Promise.resolve(okResponse({ work_id: 'WORK-JIAYI', title: '针灸甲乙经', dynasty: null, category: 'classic', publication_status: 'PUBLISHED', rights_status: 'public_domain', editions: [] }))
      if (url.includes('/public/heritage')) return Promise.resolve(okResponse({ projects: [], total: 0 }))
      return Promise.resolve(okResponse({}))
    })
    vi.stubGlobal('fetch', fetchMock)
    const wrapper = await mountHome()

    expect(wrapper.find('#home-person').attributes('data-source')).toBe('backend')
    expect(wrapper.find('#home-person').text()).toContain('针灸鼻祖')
    expect(wrapper.findAll('#home-person [data-fallback-note]')).toHaveLength(0)
    // hero T0 register
    expect(wrapper.find('#home-hero').text()).toContain('已发布著作')
    expect(wrapper.find('#home-hero').text()).toContain('14')
  })
})

describe('homepage contract — integrity', () => {
  it('reuses core-person data; the hero definition is not invented', () => {
    expect(HOME_HERO.definition).toContain('针灸甲乙经')
    expect(HOME_HERO.personName).toBe('皇甫谧')
  })

  it('carries no clinical claims and no internal register paths', async () => {
    const wrapper = await mountHome()
    const text = wrapper.text()
    expect(text).not.toMatch(/hfmzl|zzcl|registerKey|DATA-GAP|TODO/)
    expect(text).not.toMatch(/疗效显著|治疗推荐|适用于.*疾病|预约|问诊/)
  })

  it('the audited edition count is a number from the single inventory source', () => {
    expect(String(INVENTORY_EDITION_RECORDS)).toMatch(/^\d+$/)
  })
})

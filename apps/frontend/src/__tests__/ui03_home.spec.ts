/**
 * UI-03 Homepage tests (CF-07 8-section structural shell).
 *
 *  - home projection reuses existing domain data (no duplicated models);
 *  - metric integrity: 515/5 split, counts from contentInventory;
 *  - invariants: Jiayi lineage DATA-GAP, Heritage lineage PARTIAL, 刘君奇
 *    第六代名医, no fabricated ancient text, no clinical claims, no internal
 *    paths;
 *  - CF-07 structural contract: eight sections exist in exact order with the
 *    accepted ids, single H1 + section H2 set, closing identity is a
 *    non-heading signature (no second global footer), search state stays
 *    owned by HomeView (hero is props/events), removed NARRATIVE→USABLE
 *    ARCHIVE line stays absent, no duplicate ids, axe passes.
 */
import { describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import axe from 'axe-core'
import HomeView from '../views/HomeView.vue'
import {
  HOME_BOOK,
  HOME_CLOSING,
  HOME_DOMAINS,
  HOME_EVIDENCE,
  HOME_HERITAGE,
  HOME_HERITAGE_LIVING,
  HOME_HERO,
  HOME_HUANGFU,
  HOME_JIAYI,
  HOME_KNOWLEDGE,
  HOME_LIFE,
  HOME_METRICS,
  HOME_QUOTATION,
} from '../data/homeProjection'
import {
  INVENTORY_EDITION_RECORDS,
  INVENTORY_LUNWEN_FILES,
  INVENTORY_LUNZHU_FILES,
} from '../data/contentInventory'
import { READER_DOCUMENTS, getReaderDocument } from '../data/readerDocuments'
import { SEARCHABLE_PAPER_TOTAL, SEARCH_INDEX } from '../data/searchIndex'

const SECTION_IDS = [
  'home-hero',
  'home-life',
  'home-book',
  'home-knowledge',
  'home-evidence',
  'home-heritage',
  'home-domains',
  'home-closing',
]

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

function mountHome(router = makeRouter()) {
  return mount(HomeView, { global: { plugins: [router] } })
}

describe('UI-03 brand & hero', () => {
  it('unique H1 carries the platform brand', () => {
    const wrapper = mountHome()
    const h1 = wrapper.findAll('h1')
    expect(h1).toHaveLength(1)
    expect(h1[0]?.text()).toBe('皇甫谧人文数字平台')
    // CF-08 kicker carries the person dates (215—282) from corePerson projection.
    expect(wrapper.text()).toContain('公元 215—282')
  })

  it('hero definition reuses core-person data (no new person facts)', () => {
    expect(HOME_HERO.definition).toContain('针灸甲乙经')
    expect(HOME_HERO.personName).toBe('皇甫谧')
    expect(HOME_HERO.primary.map((c) => c.label)).toEqual(['探索皇甫谧', '进入《针灸甲乙经》'])
  })

  it('hero renders the single platform-name H1 (accepted Section 01)', () => {
    const wrapper = mountHome()
    expect(wrapper.find('h1').text()).toBe('皇甫谧人文数字平台')
    expect(wrapper.find('#home-hero').attributes('id')).toBe('home-hero')
  })

  it('CF-08 hero renders the accepted H3 composition (monument, kicker, statement, roles, CTA, register)', () => {
    const wrapper = mountHome()
    const hero = wrapper.find('#home-hero')
    // Decorative 190px name monument is aria-hidden and is NOT a heading.
    expect(hero.find('.home-hero__name').exists()).toBe(true)
    expect(hero.find('.home-hero__name').attributes('aria-hidden')).toBe('true')
    expect(hero.findAll('h2')).toHaveLength(0) // hero has no h2; H1 is the only heading.
    // Statement + roles + ONE editorial action + quiet platform register.
    expect(hero.text()).toContain('针灸学专著《针灸甲乙经》的编纂者')
    expect(hero.text()).toContain('西晋 · 医学家 · 文学家 · 史学家')
    expect(hero.text()).toContain('进入人物档案')
    // Provenance spec-caption (real content) stays in the accessibility tree.
    expect(hero.find('.home-hero__spec-caption').exists()).toBe(true)
    expect(hero.find('.home-hero__spec-caption').attributes('aria-hidden')).toBeUndefined()
    expect(hero.text()).toContain('四库全书本')
  })

  it('CF-10-style search boundary: the search interface is in the hero and stays wired to /search', () => {
    const wrapper = mountHome()
    const hero = wrapper.find('#home-hero')
    expect(hero.find('#home-search-input').exists()).toBe(true)
    expect(hero.find('form.home-search').attributes('role')).toBe('search')
    // Only ONE homepage search input (hero); the header search lives in PublicLayout.
    expect(wrapper.findAll('#home-search-input')).toHaveLength(1)
  })
})

describe('UI-03 metric integrity (single source, unchanged)', () => {
  it('counts come from contentInventory (single source), never hardcoded', () => {
    expect(HOME_METRICS.find((m) => m.label === '版本记录')?.value).toBe(
      String(INVENTORY_EDITION_RECORDS),
    )
    expect(HOME_METRICS.find((m) => m.label === '论著资料')?.value).toBe(
      String(INVENTORY_LUNZHU_FILES),
    )
    expect(HOME_METRICS.find((m) => m.label === '学术论文')?.value).toBe(
      String(INVENTORY_LUNWEN_FILES),
    )
    expect(HOME_METRICS.find((m) => m.label === 'Reader 全文')?.value).toBe(
      String(READER_DOCUMENTS.length),
    )
  })

  it('515/5 split is never confused', () => {
    const paper = HOME_METRICS.find((m) => m.label === '学术论文')!
    expect(paper.value).toBe('515')
    expect(paper.note).toContain('已结构化题录 5 条')
    expect(paper.note).not.toContain('可在线检索')
  })

  it('CF-07 knowledge register derives from the same single source', () => {
    const register = HOME_KNOWLEDGE.register
    const byLabel = (label: string) => register.find((r) => r.label === label)!
    expect(byLabel('论著资料').value).toBe(String(INVENTORY_LUNZHU_FILES))
    expect(byLabel('学术论文').value).toBe(String(INVENTORY_LUNWEN_FILES))
    expect(byLabel('学术论文').note).toContain(`已结构化题录 ${SEARCHABLE_PAPER_TOTAL} 条`)
    expect(byLabel('可检索记录').value).toBe(String(SEARCH_INDEX.length))
    // 19 editions are never described as 19 works.
    expect(byLabel('学术论文').note).not.toMatch(/可在线检索/)
    expect(JSON.stringify(register)).not.toMatch(/部著作|部作品/)
  })
})

describe('UI-03 invariants (unchanged facts)', () => {
  it('Jiayi lineage stays DATA-GAP on the homepage', () => {
    expect(HOME_JIAYI.lineage.alt).toContain('DATA-GAP')
    expect(HOME_BOOK.lineageCaption).toContain('DATA-GAP')
    expect(JSON.stringify(HOME_JIAYI)).not.toMatch(/STRUCTURED_LINEAGE_COMPLETE|版本谱系已结构化/)
  })

  it('Heritage lineage stays PARTIAL and 刘君奇 第六代名医 holds', () => {
    expect(HOME_HERITAGE.lede).toContain('PARTIAL')
    expect(HOME_HERITAGE.lede).toContain('第六代名医')
    expect(HOME_HERITAGE.lede).toContain('刘君奇')
    expect(HOME_HERITAGE.lede).not.toMatch(/待确认|疑似第六代/)
    expect(HOME_HERITAGE_LIVING.person.generationTitle).toBe('第六代名医')
    expect(HOME_HERITAGE_LIVING.lineageNote).not.toMatch(/待确认|疑似第六代/)
  })

  it('quotation is a real 后论 quote with attribution (no fabricated slogan)', () => {
    expect(HOME_QUOTATION.attribution).toContain('房玄龄')
    expect(HOME_QUOTATION.source).toBe('《晋书》')
    expect(HOME_QUOTATION.text).toContain('皇甫谧素履幽贞')
  })

  it('no fabricated ancient text, no clinical claims, no internal paths', () => {
    const text = JSON.stringify([
      HOME_HERO,
      HOME_HUANGFU,
      HOME_JIAYI,
      HOME_METRICS,
      HOME_QUOTATION,
      HOME_LIFE,
      HOME_KNOWLEDGE,
      HOME_EVIDENCE,
      HOME_HERITAGE_LIVING,
      HOME_DOMAINS,
      HOME_CLOSING,
    ])
    expect(text).not.toMatch(/hfmzl|zzcl|registerKey/)
    expect(text).not.toMatch(/疗效显著|治疗推荐|适用于.*疾病|预约|问诊/)
    // No invented full classical text.
    expect(text).not.toContain('玄守论曰')
    expect(text).not.toContain('笃终论曰')
  })
})

describe('UI-03 CF-07 homepage renders the accepted 8-section structure', () => {
  it('renders all eight homepage sections in order hero → … → closing', () => {
    const wrapper = mountHome()
    const ids = wrapper.findAll('section').map((s) => s.attributes('id'))
    expect(ids).toEqual(SECTION_IDS)
  })

  it('renders exactly one H1, the accepted section H2 set, unique ids, no duplicate section ids', () => {
    const wrapper = mountHome()
    expect(wrapper.findAll('h1')).toHaveLength(1)
    const headings = wrapper.findAll('h2').map((h) => h.text())
    expect(headings).toEqual([
      '从带经而农，到著书传世。',
      '一部书，成为历史中的物。',
      '从古籍文字，到可探索的知识。',
      '每一个结论，都回到它的出处。',
      '一千七百年之后，传承仍在继续。',
      '四域探索',
    ])
    /* P1-01: the closing platform identity is a NON-heading <p> so only the
       hero H1 carries 皇甫谧人文数字平台 as a heading. */
    expect(headings).not.toContain('皇甫谧人文数字平台')
    expect(wrapper.find('.home-closing__name').text()).toBe('皇甫谧人文数字平台')

    const ids = wrapper.findAll('[id]').map((el) => el.attributes('id'))
    expect(new Set(ids).size).toBe(ids.length) // no duplicate ids anywhere
  })

  it('renders real CTA route targets (no fake links)', () => {
    const wrapper = mountHome()
    const hrefs = wrapper.findAll('a').map((a) => a.attributes('href'))
    for (const target of [
      '/persons/person-huangfu-mi',
      '/reader/qichuan',
      '/yan',
      '/reader/houlun',
      '/jiayi',
      '/archive',
      '/heritage',
      '/research/search',
    ]) {
      expect(hrefs, target).toContain(target)
    }
  })

  it('keeps data-status honesty on the book (DATA-GAP) and heritage (PARTIAL) sections', () => {
    const wrapper = mountHome()
    expect(wrapper.find('#home-book').text()).toContain('版本记录')
    expect(wrapper.find('#home-book').text()).toContain(String(INVENTORY_EDITION_RECORDS))
    expect(wrapper.find('#home-book').text()).toContain('DATA-GAP')
    const heritageStatus = wrapper.find('#home-heritage .hfm-status')
    expect(heritageStatus.attributes('data-status')).toBe('PARTIAL')
    expect(heritageStatus.text()).toContain('谱系整理中')
    expect(wrapper.find('#home-heritage').text()).toContain('第六代名医')
    expect(wrapper.find('#home-heritage').text()).toContain('刘君奇')
  })

  it('Section 07 never restores the rejected NARRATIVE → USABLE ARCHIVE line', () => {
    const wrapper = mountHome()
    expect(wrapper.find('#home-domains').text()).not.toMatch(/NARRATIVE|USABLE ARCHIVE/)
    expect(wrapper.text()).not.toMatch(/USABLE ARCHIVE/)
  })

  it('Section 08 closing is a section — never a second global footer', () => {
    const wrapper = mountHome()
    // No footer element anywhere inside the homepage view (AppFooter is global in PublicLayout).
    expect(wrapper.findAll('footer')).toHaveLength(0)
    const closing = wrapper.find('#home-closing')
    expect(closing.element.tagName).toBe('SECTION')
    // The closing duplicates none of the global footer responsibilities.
    const closingText = closing.text()
    expect(closingText).not.toMatch(/版权与免责声明|隐私说明|关于平台|仅供皇甫谧学术研究/)
  })

  it('evidence source register derives from the real qichuan document', () => {
    const qichuan = getReaderDocument('qichuan')
    expect(qichuan).toBeDefined()
    const headings = qichuan!.sections.map((s) => s.heading)
    expect(HOME_EVIDENCE.sources.map((s) => s.title)).toEqual(headings)
    expect(HOME_EVIDENCE.sources.length).toBeGreaterThanOrEqual(6)
    // The documented dispute (建安 / 正始) exists in the same real document.
    expect(JSON.stringify(qichuan)).toContain('建安')
    expect(JSON.stringify(qichuan)).toContain('正始')
  })

  it('search form is a props/events boundary owned by HomeView (single search state)', () => {
    const router = makeRouter()
    const pushSpy = vi.spyOn(router, 'push').mockResolvedValue(undefined as never)
    const wrapper = mountHome(router)

    const hero = wrapper.find('#home-hero')
    const form = hero.find('form.home-search')
    const input = hero.find('#home-search-input')
    expect(form.exists()).toBe(true)
    expect(input.exists()).toBe(true)
    expect(hero.find('#home-search-input').attributes('placeholder')).toBe('检索平台内容')

    // Only ONE search input on the homepage page body (hero) — the header
    // search lives in PublicLayout, not in HomeView.
    expect(wrapper.findAll('#home-search-input')).toHaveLength(1)

    input.setValue('皇甫谧')
    form.trigger('submit')
    expect(pushSpy).toHaveBeenCalledWith({ path: '/search', query: { q: '皇甫谧' } })
  })

  it('renders 第六代名医 on the homepage', () => {
    const wrapper = mountHome()
    expect(wrapper.text()).toContain('第六代名医')
    expect(wrapper.text()).toContain('刘君奇')
  })

  it('passes axe assertions', async () => {
    const wrapper = mount(HomeView, {
      attachTo: document.body,
      global: { plugins: [makeRouter()] },
    })
    const results = await axe.run(wrapper.element as HTMLElement)
    wrapper.unmount()
    expect(results.violations).toHaveLength(0)
  })
})

describe('UI-03 CF-08 Sections 01–04 production contract', () => {
  it('Section 02 Life renders the accepted two-plane documentary form (4 stages, dated anchors)', () => {
    const wrapper = mountHome()
    const life = wrapper.find('#home-life')
    expect(life.findAll('.home-life__stage')).toHaveLength(4)
    expect(life.findAll('.home-life__junction')).toHaveLength(6)
    expect(life.findAll('.home-life__anchor')).toHaveLength(2)
    expect(life.text()).toContain('215')
    expect(life.text()).toContain('282')
    // Narrative plane + documentary/register plane both present.
    expect(life.find('.home-life__register').exists()).toBe(true)
    expect(life.find('.home-life__register-row').exists()).toBe(true)
  })

  it('Section 03 Book keeps WORK ≠ EDITION (no false 19-works claim)', () => {
    const wrapper = mountHome()
    const book = wrapper.find('#home-book')
    // Edition record register shows the EDITION count, never a work count.
    expect(book.text()).toContain('版本记录')
    expect(book.text()).toContain(String(INVENTORY_EDITION_RECORDS))
    expect(book.text()).not.toMatch(/部著作|部作品/)
    // Single WORK object heading + edition chain + lineage entry preserved.
    expect(book.find('.home-book__title-glyphs').text()).toBe('《针灸甲乙经》')
    expect(book.findAll('.home-book__prov-chain b').length).toBeGreaterThanOrEqual(4)
    expect(book.find('.home-lineage img').attributes('src')).toContain('edition-lineage.png')
  })

  it('Section 04 Knowledge derives every count from data and keeps taxonomy + evidence register', () => {
    expect(HOME_KNOWLEDGE.searchable).toBe(SEARCH_INDEX.length)
    expect(HOME_KNOWLEDGE.categoriesCount).toBe(HOME_KNOWLEDGE.categories.length)
    expect(HOME_KNOWLEDGE.editions).toBe(INVENTORY_EDITION_RECORDS)
    expect(HOME_KNOWLEDGE.lunzhu).toBe(INVENTORY_LUNZHU_FILES)
    expect(HOME_KNOWLEDGE.lunwen).toBe(INVENTORY_LUNWEN_FILES)
    expect(HOME_KNOWLEDGE.structured).toBe(SEARCHABLE_PAPER_TOTAL)

    const wrapper = mountHome()
    const knowledge = wrapper.find('#home-knowledge')
    expect(knowledge.findAll('.home-knowledge__prim-item')).toHaveLength(3)
    expect(knowledge.text()).toContain('版本记录')
    // No invented corpus/evidence count is displayed beyond the real ones.
    expect(knowledge.text()).not.toMatch(/\d+\s*万|99\s*%|100\s*%|\.\d+\s*%/)
  })

  it('Sections 01–04 each carry their accepted section id (no dupes, correct order)', () => {
    const wrapper = mountHome()
    const ids = wrapper.findAll('section').map((s) => s.attributes('id'))
    expect(ids.slice(0, 4)).toEqual(['home-hero', 'home-life', 'home-book', 'home-knowledge'])
    expect(ids).toEqual(SECTION_IDS)
  })

  it('production assets (manuscripts/lineage) are referenced at real paths', () => {
    // Hero specimen + life manuscript + book/knowledge leaf reference the authorized assets.
    const wrapper = mountHome()
    const srcs = wrapper
      .findAll('img')
      .map((i) => i.attributes('src'))
      .filter((s): s is string => !!s)
    for (const src of [
      '/assets/jiayi/frag-macro.jpg',
      '/assets/jiayi/frag-band1.jpg',
      '/assets/jiayi/book-siku-leaf.jpg',
      '/assets/jiayi/edition-lineage.png',
    ]) {
      expect(srcs).toContain(src)
    }
  })
})

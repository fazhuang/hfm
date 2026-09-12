/**
 * UI-11 Research Workbench tests.
 *
 *  - projections reuse existing domain data (no duplicated models/index);
 *  - entity research views resolve for person/work/edition/archive/paper/
 *    heritage/reader;
 *  - invariants: 515/5 paper split, Jiayi lineage DATA-GAP, Heritage lineage
 *    PARTIAL, 刘君奇 第六代名医;
 *  - no internal paths, no fabricated evidence states/citations/activity;
 *  - RBAC guard stays intact (requireAnyRole unchanged);
 *  - components: ResearchLayout, ResearchEntityView, EvidenceExplorer + axe.
 */
import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import axe from 'axe-core'
import { researchEntity, researchScopeSummary } from '../data/researchProjection'
import { SEARCH_INDEX, AUDITED_PAPER_TOTAL, SEARCHABLE_PAPER_TOTAL } from '../data/searchIndex'
import { requireAnyRole } from '../router/guards'
import { RESEARCH_ROLES } from '../types/auth'
import ResearchLayout from '../layouts/ResearchLayout.vue'
import ResearchEntityView from '../views/research/ResearchEntityView.vue'
import EvidenceExplorer from '../components/research/EvidenceExplorer.vue'
import ResearchBreadcrumb from '../components/research/ResearchBreadcrumb.vue'

describe('UI-11 research projection & domain reuse', () => {
  it('resolves entity research views from existing domain data', () => {
    expect(researchEntity('person', 'person-huangfu-mi')?.title).toBe('皇甫谧')
    expect(researchEntity('person', 'person-liujunqi')?.title).toBe('刘君奇')
    expect(researchEntity('work', 'w-jiayi')?.title).toBe('《针灸甲乙经》')
    expect(researchEntity('work', 'w-diwangshiji')?.title).toBe('《帝王世纪》')
    expect(researchEntity('edition', 'yitong-zhengmai-1601')?.title).toContain('医统正脉')
    expect(researchEntity('archive', 'a-jiayi-lunzhu')?.title).toContain('论著')
    expect(researchEntity('paper', 'p1')?.title).toBeTruthy()
    expect(researchEntity('heritage', 'liujunqi')?.title).toContain('非遗')
    expect(researchEntity('reader', 'houlun')?.title).toContain('后论')
    expect(researchEntity('reader', 'nope')).toBeUndefined()
  })

  it('no second search index — reuses UI-10 SEARCH_INDEX', () => {
    expect(SEARCH_INDEX.length).toBeGreaterThan(30)
    // Research projection returns view-models, never domain model shapes.
    const jiayi = researchEntity('work', 'w-jiayi')!
    expect(jiayi).not.toHaveProperty('editionCount')
    expect(jiayi).not.toHaveProperty('workType')
    expect(jiayi).not.toHaveProperty('editionType')
    const huangfu = researchEntity('person', 'person-huangfu-mi')!
    expect(huangfu).not.toHaveProperty('assertions')
  })

  it('515/5 paper invariant is preserved in research scope', () => {
    expect(AUDITED_PAPER_TOTAL).toBe(515)
    expect(SEARCHABLE_PAPER_TOTAL).toBe(5)
    const summary = researchScopeSummary()
    const paper = summary.find((s) => s.label.includes('论文'))
    expect(paper?.value).toContain('5')
    expect(paper?.value).toContain('515')
  })

  it('Jiayi lineage stays DATA-GAP and Heritage lineage stays PARTIAL', () => {
    const jiayi = researchEntity('work', 'w-jiayi')!
    expect(jiayi.evidence.length).toBeGreaterThan(0)
    // researchProjection does not claim structured lineage.
    expect(JSON.stringify(jiayi)).not.toMatch(/STRUCTURED_LINEAGE_COMPLETE/)
    const heritage = researchEntity('heritage', 'liujunqi')!
    expect(JSON.stringify(heritage)).toContain('PARTIAL')
  })

  it('刘君奇 第六代名医 fact is preserved in research projection', () => {
    const liu = researchEntity('person', 'person-liujunqi')!
    expect(JSON.stringify(liu)).toContain('第六代名医')
    expect(JSON.stringify(liu)).not.toMatch(/待确认|疑似第六代/)
  })

  it('no internal paths or fabricated evidence states in projections', () => {
    const all = JSON.stringify([
      researchEntity('person', 'person-huangfu-mi'),
      researchEntity('work', 'w-jiayi'),
      researchEntity('heritage', 'liujunqi'),
      researchEntity('reader', 'houlun'),
      researchScopeSummary(),
    ])
    expect(all).not.toMatch(/hfmzl|zzcl|registerKey/)
    // Only mapped ContentStatus values appear.
    expect(all).not.toMatch(/VERIFIED|TRUSTED|OFFICIAL|HIGH_CONFIDENCE/)
  })

  it('citation projection is real (houlun 12 citations)', () => {
    const houlun = researchEntity('reader', 'houlun')!
    const citation = houlun.evidence.find((e) => e.citationCount !== undefined)
    expect(citation?.citationCount).toBe(12)
  })
})

describe('UI-11 RBAC guard intact', () => {
  it('requireAnyRole still returns the deny redirect for missing roles', () => {
    setActivePinia(createPinia())
    const guard = requireAnyRole(RESEARCH_ROLES)
    // NavigationGuard(to, from, next) — pass minimal args; store has no user.
    const result = guard({} as never, {} as never, () => undefined)
    expect(result).toEqual({ name: 'denied' })
  })
})

describe('UI-11 components', () => {
  function mountResearchLayout(): ReturnType<typeof mount> {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/research',
          component: ResearchLayout,
          children: [{ path: '', component: { template: '<p>home</p>' } }],
        },
      ],
    })
    router.push('/research')
    return mount(ResearchLayout, { global: { plugins: [createPinia(), router] } })
  }

  it('research layout renders sidebar, breadcrumb and main', () => {
    const wrapper = mountResearchLayout()
    expect(wrapper.find('nav[aria-label="研究导航"]').exists()).toBe(true)
    expect(wrapper.find('nav[aria-label="面包屑"]').exists()).toBe(true)
    expect(wrapper.find('#main-content').exists()).toBe(true)
  })

  it('evidence explorer maps ContentStatus without invented states', () => {
    const wrapper = mount(EvidenceExplorer, {
      props: {
        evidence: [
          {
            sourceName: '客户提供：后论文稿（docx）',
            contentStatus: 'AVAILABLE' as const,
            citationCount: 12,
          },
          { sourceName: '客户提供：甲乙经论著资料', contentStatus: 'METADATA_ONLY' as const },
        ],
      },
    })
    expect(wrapper.text()).toContain('已展示')
    expect(wrapper.text()).toContain('元数据已录')
    expect(wrapper.text()).toContain('12')
    expect(wrapper.text()).not.toMatch(/VERIFIED|TRUSTED|OFFICIAL/)
  })

  it('research entity view renders a work research view with public link', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/research/entity/:type/:id', component: ResearchEntityView }],
    })
    await router.push('/research/entity/work/w-jiayi')
    await router.isReady()
    const wrapper = mount(ResearchEntityView, { global: { plugins: [router] } })
    expect(wrapper.find('h1').text()).toBe('《针灸甲乙经》')
    expect(wrapper.text()).toContain('研究视图')
    expect(wrapper.text()).toContain('查看公众页')
  })

  it('research entity view handles unknown entity', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/research/entity/:type/:id', component: ResearchEntityView }],
    })
    await router.push('/research/entity/work/zzz')
    await router.isReady()
    const wrapper = mount(ResearchEntityView, { global: { plugins: [router] } })
    expect(wrapper.text()).toContain('未找到该实体')
  })

  it('breadcrumb reflects IA, not file paths', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/research/entity/work/:id', component: { template: '<p />' } }],
    })
    await router.push('/research/entity/work/w-jiayi')
    await router.isReady()
    const wrapper = mount(ResearchBreadcrumb, { global: { plugins: [router] } })
    expect(wrapper.text()).toContain('研究工作台')
    expect(wrapper.text()).toContain('作品')
    expect(wrapper.text()).not.toContain('src/')
  })
})

describe('UI-11 accessibility', () => {
  it('passes axe on the research entity view', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/research/entity/:type/:id', component: ResearchEntityView }],
    })
    await router.push('/research/entity/heritage/liujunqi')
    await router.isReady()
    const wrapper = mount(ResearchEntityView, {
      attachTo: document.body,
      global: { plugins: [router] },
    })
    const results = await axe.run(wrapper.element as HTMLElement)
    wrapper.unmount()
    expect(results.violations).toHaveLength(0)
  })
})

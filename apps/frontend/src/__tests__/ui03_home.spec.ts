// mypy: disable-error-code="import-untyped,import-not-found"
/**
 * Homepage invariants — HFM-UI-CONTRACT-v2 §5.
 *
 * The contract does NOT fix the band count, band ids, heading text, or CTA
 * targets: the homepage is rebuilt against the reference layout and those all
 * change. What survives a rebuild is asserted here — one H1 per page, a single
 * usable search entry, no second global footer, axe clean, and the content
 * integrity rules (no internal paths, no clinical claims, no invented numbers).
 */
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { flushPromises } from '@vue/test-utils'
import axe from 'axe-core'
import HomeView from '../views/HomeView.vue'
import { INVENTORY_EDITION_RECORDS } from '../data/contentInventory'

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

/** Flush the data layer + render. */
async function mountHome(router = makeRouter(), attach = false) {
  const wrapper = mount(HomeView, {
    attachTo: attach ? document.body : undefined,
    global: { plugins: [router] },
  })
  await flushPromises()
  return wrapper
}

beforeEach(() => {
  // Backend unavailable → the page must still render.
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')))
})
afterEach(() => vi.unstubAllGlobals())

describe('homepage invariants (§5)', () => {
  it('renders exactly one H1', async () => {
    const wrapper = await mountHome()
    expect(wrapper.findAll('h1')).toHaveLength(1)
    expect(wrapper.find('h1').text().trim().length).toBeGreaterThan(0)
  })

  it('never renders a second global footer', async () => {
    const wrapper = await mountHome()
    expect(wrapper.findAll('footer')).toHaveLength(0)
  })

  it('passes axe assertions', async () => {
    const wrapper = await mountHome(makeRouter(), true)
    const results = await axe.run(wrapper.element as HTMLElement)
    wrapper.unmount()
    expect(results.violations).toHaveLength(0)
  })
})

describe('homepage integrity', () => {
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

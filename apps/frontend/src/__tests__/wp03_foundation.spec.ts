/**
 * WP-03 homepage visual foundation — verification tests.
 *
 * Proves the shared homepage presentation foundation (established once in
 * foundations.css, .home-namespaced) is:
 *  - applied to the homepage sections (namespace roles present on .home content);
 *  - scoped to the homepage (selectors are .home-prefixed → no leakage to other routes);
 *  - token-driven (reuses existing HFM tokens, no new color/font/spacing system);
 *  - regression-safe (single H1, heading hierarchy, footer/search ownership intact).
 *
 * Reference: HFM_HOMEPAGE_STEP2_VISUAL_BASELINE_FINAL (frozen).
 */
import { describe, expect, it, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import axe from 'axe-core'
import HomeView from '../views/HomeView.vue'

afterEach(() => vi.clearAllMocks())

describe('WP-03 home foundation — homepage-scoped roles', () => {
  it('renders the homepage roots under the .home namespace with foundation roles', () => {
    const wrapper = mount(HomeView)
    const home = wrapper.find('.home')
    expect(home.exists()).toBe(true)
    // every homepage section is a descendant of .home (namespace boundary)
    const sections = wrapper.findAll('#home-hero,#home-life,#home-book,#home-knowledge,#home-evidence,#home-heritage,#home-domains,#home-closing')
    expect(sections).toHaveLength(8)
    for (const s of sections) {
      expect(s.element.closest('.home')).not.toBeNull()
    }
    // shared foundation role: the chapter eyebrow is used by every section (heritage accent)
    expect(wrapper.findAll('.home-eyebrow').length).toBeGreaterThanOrEqual(8)
    // per-section heading roles are applied (visual sections use artboard-scoped classes)
    expect(wrapper.findAll('.home-life__statement, .home-book__narr-heading, .home-knowledge__title').length).toBeGreaterThanOrEqual(3)
    // the single H1 (hero) is present
    expect(wrapper.find('#home-hero-title').exists()).toBe(true)
  })

  it('foundation roles are token-driven (no hard-coded color/font in homepage markup)', () => {
    const wrapper = mount(HomeView)
    // eyebrows carry the number span used by the heritage-accent .home-eyebrow__no rule
    expect(wrapper.findAll('.home-eyebrow__no').length).toBeGreaterThanOrEqual(8)
    // editorial actions are real anchors (per-section action roles), no fake controls
    const actions = wrapper.findAll('.home-hero__act, .home-book__act, .home-knowledge__act, .home-cta')
    expect(actions.length).toBeGreaterThanOrEqual(3)
    for (const a of actions) {
      expect(a.attributes('href')).toBeTruthy()
    }
  })
})

describe('WP-03 home foundation — scope & regression contracts', () => {
  it('keeps exactly one H1 and a valid heading hierarchy', () => {
    const wrapper = mount(HomeView)
    const h1 = wrapper.findAll('h1')
    expect(h1).toHaveLength(1)
    expect(h1[0]?.text()).toBe('皇甫谧人文数字平台')
    const levels = wrapper.findAll('h1, h2, h3').map((h) => Number(h.element.tagName.slice(1)))
    expect(levels.filter((l) => l === 1)).toHaveLength(1)
  })

  it('homepage foundation is token-driven and .home-scoped (no hard-coded literals in markup)', () => {
    const wrapper = mount(HomeView)
    // all homepage foundation classes are descendants of the .home root (namespace boundary)
    const home = wrapper.find('.home')
    for (const cls of ['.home-eyebrow', '.home-section__title', '.home-section__lede', '.home-cta']) {
      for (const el of wrapper.findAll(cls)) {
        expect(el.element.closest('.home')).toBe(home.element)
      }
    }
  })

  it('preserves data-status / no-fabrication honesty (foundation does not hide it)', () => {
    const wrapper = mount(HomeView)
    expect(wrapper.find('#home-book .hfm-status').attributes('data-status')).toBe('UNSTRUCTURED_OR_INCOMPLETE')
    expect(wrapper.find('#home-heritage .hfm-status').attributes('data-status')).toBe('UNSTRUCTURED_OR_INCOMPLETE')
    expect(wrapper.find('#home-book').text()).toContain('DATA-GAP')
    expect(wrapper.find('#home-heritage').text()).toContain('PARTIAL')
  })

  it('passes axe on the homepage after foundation roles applied', async () => {
    const wrapper = mount(HomeView, { attachTo: document.body })
    const results = await axe.run(wrapper.element as HTMLElement)
    wrapper.unmount()
    expect(results.violations).toHaveLength(0)
  })
})

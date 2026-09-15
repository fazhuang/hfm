/**
 * UI-02 Global Shell / Navigation tests.
 *
 *  - main navigation renders every configured target;
 *  - mobile drawer toggles, Escape closes it, focus returns to the toggle;
 *  - skip link targets #main-content (a11y, P10).
 */
import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import PublicLayout from '../layouts/PublicLayout.vue'
import { PUBLIC_NAV_ITEMS } from '../config/navigation'

function mountLayout(): ReturnType<typeof mount> {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      {
        path: '/',
        component: PublicLayout,
        meta: { publicOnly: true },
        children: [{ path: '', name: 'home', component: { template: '<p>home</p>' } }],
      },
    ],
  })
  router.push('/')
  return mount(PublicLayout, {
    global: {
      plugins: [router],
      stubs: { RouterView: { template: '<p>view</p>' } },
    },
  })
}

describe('UI-02 main navigation', () => {
  // 导航项由 HFM-UI-CONTRACT-v2 §2 定义，重构期间会变。此处只固定不变量：
  // 有导航、每项有标签与目标、标签互不重复。
  it('renders a non-empty main nav with unique, labelled targets', () => {
    const wrapper = mountLayout()
    const nav = wrapper.find('nav[aria-label="Public navigation"]')
    const links = nav.findAll('a.nav-link')
    expect(links.length).toBeGreaterThan(0)
    expect(links).toHaveLength(PUBLIC_NAV_ITEMS.length)
    const labels = links.map((l) => l.text())
    expect(labels.every((l) => l.trim().length > 0)).toBe(true)
    expect(new Set(labels).size).toBe(labels.length)
    expect(PUBLIC_NAV_ITEMS.every((i) => i.href.startsWith('/'))).toBe(true)
  })

  it('marks the current route with aria-current=page (active state)', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/',
          component: PublicLayout,
          meta: { publicOnly: true },
          children: [{ path: '', name: 'home', component: { template: '<p>home</p>' } }],
        },
        {
          path: '/jiayi',
          component: PublicLayout,
          meta: { publicOnly: true },
          children: [{ path: '', name: 'jiayi', component: { template: '<p>jiayi</p>' } }],
        },
      ],
    })
    router.push('/jiayi')
    await router.isReady()
    const wrapper = mount(PublicLayout, {
      global: { plugins: [router], stubs: { RouterView: { template: '<p>view</p>' } } },
    })
    const nav = wrapper.find('nav[aria-label="Public navigation"]')
    const active = nav.find('a[aria-current="page"]')
    expect(active.exists()).toBe(true)
    expect(active.text()).toBe('典籍')
    // Active indicator must not rely on color alone: underline class present.
    expect(active.classes()).toContain('nav-link--active')
  })

  it('keeps search and the workbench entry out of the main nav (header utility area)', () => {
    const wrapper = mountLayout()
    const nav = wrapper.find('nav[aria-label="Public navigation"]')
    expect(nav.text()).not.toContain('进入研究工作台')
    expect(wrapper.find('form.header-search').exists()).toBe(true)
    expect(wrapper.find('a.header-workbench').text()).toContain('进入研究工作台')
  })

  it('renders a skip link targeting #main-content', () => {
    const wrapper = mountLayout()
    const skip = wrapper.find('a.skip-link')
    expect(skip.exists()).toBe(true)
    expect(skip.attributes('href')).toBe('#main-content')
  })
})

describe('UI-02 mobile drawer', () => {
  it('opens on toggle and closes on Escape, restoring focus to the toggle', async () => {
    const wrapper = mountLayout()
    const nav = wrapper.find('nav[aria-label="Public navigation"]')
    const toggle = wrapper.find('button.nav-toggle')

    expect(nav.classes()).not.toContain('public-shell__nav--open')
    await toggle.trigger('click')
    expect(nav.classes()).toContain('public-shell__nav--open')
    expect(toggle.attributes('aria-expanded')).toBe('true')

    await nav.trigger('keydown', { key: 'Escape' })
    expect(nav.classes()).not.toContain('public-shell__nav--open')
    expect(toggle.attributes('aria-expanded')).toBe('false')
  })

  it('toggles closed on a second click', async () => {
    const wrapper = mountLayout()
    const nav = wrapper.find('nav[aria-label="Public navigation"]')
    const toggle = wrapper.find('button.nav-toggle')

    await toggle.trigger('click')
    expect(nav.classes()).toContain('public-shell__nav--open')
    await toggle.trigger('click')
    expect(nav.classes()).not.toContain('public-shell__nav--open')
  })
})

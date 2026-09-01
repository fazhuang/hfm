/**
 * UI-02 Global Shell / Navigation tests.
 *
 *  - main navigation exposes exactly the customer-mandated 5 links;
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
  it('exposes exactly the customer-mandated 5 main-nav links', () => {
    const wrapper = mountLayout()
    const nav = wrapper.find('nav[aria-label="Public navigation"]')
    const links = nav.findAll('a.nav-link')
    expect(links).toHaveLength(5)
    const labels = links.map((l) => l.text())
    expect(labels).toEqual([
      '首页',
      '人物（皇甫谧）',
      '其言',
      '《针灸甲乙经》',
      '皇甫谧针灸非遗的传承',
    ])
    expect(PUBLIC_NAV_ITEMS).toHaveLength(5)
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
          path: '/heritage',
          component: PublicLayout,
          meta: { publicOnly: true },
          children: [{ path: '', name: 'heritage', component: { template: '<p>heritage</p>' } }],
        },
      ],
    })
    router.push('/heritage')
    await router.isReady()
    const wrapper = mount(PublicLayout, {
      global: { plugins: [router], stubs: { RouterView: { template: '<p>view</p>' } } },
    })
    const nav = wrapper.find('nav[aria-label="Public navigation"]')
    const active = nav.find('a[aria-current="page"]')
    expect(active.exists()).toBe(true)
    expect(active.text()).toBe('皇甫谧针灸非遗的传承')
    // Active indicator must not rely on color alone: underline class present.
    expect(active.classes()).toContain('nav-link--active')
  })

  it('keeps search + login out of the main nav (header utility area)', () => {
    const wrapper = mountLayout()
    const nav = wrapper.find('nav[aria-label="Public navigation"]')
    expect(nav.text()).not.toContain('登录')
    expect(wrapper.find('form.header-search').exists()).toBe(true)
    expect(wrapper.find('a.header-login').text()).toBe('登录')
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

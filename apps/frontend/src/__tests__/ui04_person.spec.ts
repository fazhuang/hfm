/**
 * UI-04 Huangfu Mi Profile (FLAGSHIP-01) tests.
 *
 *  - hero renders name + core-person confirmed anchors (dates / definition);
 *  - identity tags, life-phase timeline, works entries render for the core
 *    person with content not yet admitted (empty states elsewhere);
 *  - evidenced assertions expose evidence badges (P8);
 *  - movies render from the media projection;
 *  - axe passes on the flagship page.
 */
import { afterEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import axe from 'axe-core'
import PersonDetailView from '../views/persons/PersonDetailView.vue'

const PERSON = {
  entity_id: 'person-huangfu-mi',
  name_zh: '皇甫谧',
  name_pinyin: 'Huángfǔ Mì',
  courtesy_name: '士安',
  pseudonym: '玄晏先生',
  dynasty: '西晋',
  publication_status: 'published',
  assertions: [
    {
      id: 'a1',
      predicate: '身份',
      value: '针灸学专著《针灸甲乙经》的编纂者',
      object_entity_id: null,
      editorial_status: 'published',
      confidence: 'high',
      evidence_ids: ['ev-1'],
    },
  ],
  events: [],
}

const MEDIA = {
  items: [
    {
      id: 'm1',
      name: '《针灸鼻祖皇甫谧》第1集 大器晚成',
      category: 'movie',
      mime_type: 'video/mp4',
      byte_size: 1024,
      license_basis: '客户提供资料（已授权公开）',
      restriction: null,
      object_key: 'movies/huangfu-mi-1.mpg',
    },
  ],
  total: 1,
}

function stubFetch(): void {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockImplementation((url: string) => {
      const envelope = (data: unknown) => ({
        ok: true,
        status: 200,
        json: async () => ({ success: true, data }),
      })
      if (String(url).includes('/persons/')) return Promise.resolve(envelope(PERSON))
      if (String(url).includes('/media')) return Promise.resolve(envelope(MEDIA))
      return Promise.resolve(envelope(null))
    }),
  )
}

const mountedWrappers: ReturnType<typeof mount>[] = []

afterEach(() => {
  while (mountedWrappers.length > 0) {
    mountedWrappers.pop()?.unmount()
  }
  vi.unstubAllGlobals()
})

async function mountPerson(attach = false): Promise<ReturnType<typeof mount>> {
  stubFetch()
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      {
        path: '/persons/:id',
        component: PersonDetailView,
        children: [],
      },
    ],
  })
  router.push('/persons/person-huangfu-mi')
  await router.isReady()
  const wrapper = mount(PersonDetailView, {
    attachTo: attach ? document.body : undefined,
    global: { plugins: [router] },
  })
  mountedWrappers.push(wrapper)
  await vi.waitFor(() => {
    expect(wrapper.find('h1.person-hero__name').exists()).toBe(true)
  })
  return wrapper
}

describe('UI-04 flagship profile — hero & confirmed anchors', () => {
  it('renders the hero with name, dates and definition for the core person', async () => {
    const wrapper = await mountPerson()
    expect(wrapper.find('h1.person-hero__name').text()).toBe('皇甫谧')
    expect(wrapper.find('.person-hero__dates').text()).toBe('215—282')
    expect(wrapper.find('.person-hero__definition').text()).toContain('针灸甲乙经')
  })

  it('renders four identity tags', async () => {
    const wrapper = await mountPerson()
    const tags = wrapper.findAll('.identity-tag').map((t) => t.text())
    expect(tags).toEqual(['医学家', '文学家', '史学家', '学者'])
  })

  it('renders the life-phase timeline for the core person (content not yet admitted)', async () => {
    const wrapper = await mountPerson()
    const titles = wrapper.findAll('.timeline__title').map((t) => t.text())
    expect(titles).toEqual(['求学悟道', '拒仕治学', '久病研医', '著书传世'])
  })

  it('renders works entries linking to /yan and /jiayi', async () => {
    const wrapper = await mountPerson()
    const hrefs = wrapper.findAll('.work-card__link').map((l) => l.attributes('href'))
    expect(hrefs).toContain('/yan')
    expect(hrefs).toContain('/jiayi')
  })
})

describe('UI-04 flagship profile — evidence & media', () => {
  it('exposes evidenced assertions with evidence badges (P8)', async () => {
    const wrapper = await mountPerson()
    const badge = wrapper.find('.evidence-badge')
    expect(badge.exists()).toBe(true)
    expect(badge.text()).toContain('证据')
  })

  it('renders movies from the media projection', async () => {
    const wrapper = await mountPerson()
    expect(wrapper.find('.movie-card__title').text()).toContain('针灸鼻祖皇甫谧')
  })
})

describe('UI-04 flagship profile — accessibility', () => {
  it('passes axe assertions', async () => {
    const wrapper = await mountPerson(true)
    const results = await axe.run(wrapper.element as HTMLElement)
    expect(results.violations).toHaveLength(0)
  })
})

/**
 * CF-03 Person Archive tests (rebuilt on the recovery runtime).
 *
 * The production page consumes GET /api/v1/public/persons/:id through
 * fetchPublicPerson — never a fixture, a hard-coded Huangfu Mi object or the
 * searchIndex. These tests stub ONLY the fetch transport (unit boundary);
 * the browser-level real chain (Browser → Vite proxy → FastAPI → PostgreSQL
 * → JSON → visible 皇甫谧 content) is proven by the CF-01 golden spec that
 * runs inside FAST_RUNTIME_GATE.
 *
 * P-7 note: the CORE person (ENT-PERSON-HFM-HUANGFUMI) now renders the
 * portal's narrative page instead of the archive layout, so these archive
 * tests drive a NON-core id. The narrative path has its own spec
 * (p7_person_narrative.spec.ts). Nothing was dropped: the archive layout is
 * still what every one of the other 16 admitted persons renders.
 *
 * Coverage (CF-03 §12):
 *   - successful API load / non-core person render;
 *   - partial & missing optional fields are never a page failure;
 *   - 404 is discriminated from a generic server/network error;
 *   - loading state is programmatically exposed;
 *   - CF-02 primitive integration (DHObjectLayout + stateMapping status band).
 */
import { afterEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import axe from 'axe-core'
import PersonDetailView from '../views/persons/PersonDetailView.vue'
import type { PublicPerson } from '../types/public'

const PERSON: PublicPerson = {
  entity_id: 'ENT-PERSON-HFM-HUANGFUMI',
  name_zh: '皇甫谧',
  name_pinyin: 'Huangfu Mi',
  courtesy_name: '士安',
  pseudonym: '玄晏先生',
  dynasty: '西晋',
  publication_status: 'published',
  assertions: [],
  events: [],
}

type FetchHandler = (url: string) => Promise<unknown> | unknown

function envelope(data: unknown): { ok: true; status: 200; json: () => Promise<unknown> } {
  return { ok: true, status: 200, json: async () => ({ success: true, data }) }
}

function stubFetch(handler: FetchHandler): void {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockImplementation((url: string) => {
      const out = handler(String(url))
      return out instanceof Promise ? out : Promise.resolve(out)
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

/** 非核心人物：走通用档案版式。 */
const ARCHIVE_PERSON_ID = 'ENT-PERSON-WU-MIANXUE'

async function mountPerson(
  handler: FetchHandler,
  routeId = ARCHIVE_PERSON_ID,
): Promise<ReturnType<typeof mount>> {
  stubFetch(handler)
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      {
        path: '/persons/:id',
        component: PersonDetailView,
      },
    ],
  })
  router.push(`/persons/${routeId}`)
  await router.isReady()
  const wrapper = mount(PersonDetailView, {
    attachTo: document.body,
    global: { plugins: [router] },
  })
  mountedWrappers.push(wrapper)
  return wrapper
}

async function mountPersonOk(payload = PERSON): Promise<ReturnType<typeof mount>> {
  const wrapper = await mountPerson(() => envelope(payload))
  await vi.waitFor(() => {
    expect(wrapper.find('h1.dh-object__title').exists()).toBe(true)
  })
  return wrapper
}

function findAll(page: ReturnType<typeof mount>, selector: string): string[] {
  return page.findAll(selector).map((node) => node.text())
}

describe('CF-03 person archive — real-API identity & metadata', () => {
  it('renders identity + metadata from the person API', async () => {
    const wrapper = await mountPersonOk()
    expect(wrapper.find('h1.dh-object__title').text()).toBe('皇甫谧')
    const meta = findAll(wrapper, '.dh-object__meta')
    expect(meta.some((text) => text.includes('Huangfu Mi'))).toBe(true)
    expect(meta.some((text) => text.includes('西晋'))).toBe(true)
    expect(meta.some((text) => text.includes('字：士安'))).toBe(true)
    expect(meta.some((text) => text.includes('号：玄晏先生'))).toBe(true)
  })

  it('shows the CF-02 completeness band for an identity-only record (PARTIAL)', async () => {
    const wrapper = await mountPersonOk()
    expect(wrapper.find('[data-primitive="dh-object"]').exists()).toBe(true)
    const band = wrapper.find('.dh-object__incomplete')
    expect(band.exists()).toBe(true)
    // stateMapping presentationStatusLabel('PARTIAL') → '部分整理'
    expect(wrapper.find('.dh-object__status').text()).toBe('部分整理')
    expect(wrapper.find('.dh-object__status').attributes('data-status')).toBe('PARTIAL')
    // Missing depth is stated honestly; no invented content, no empty sections.
    expect(wrapper.find('[data-primitive="person-events"]').exists()).toBe(false)
    expect(wrapper.find('[data-primitive="person-assertions"]').exists()).toBe(false)
    expect(wrapper.find('.person-page__publication').text()).toContain('已发布')
  })

  it('treats missing optional fields as absence, never as a failure', async () => {
    const minimal: PublicPerson = {
      entity_id: 'ENT-PERSON-HFM-HUANGFUMI',
      name_zh: '皇甫谧',
      name_pinyin: null,
      courtesy_name: null,
      pseudonym: null,
      dynasty: null,
      publication_status: '',
      assertions: [],
      events: [],
    }
    const wrapper = await mountPersonOk(minimal)
    expect(wrapper.find('h1.dh-object__title').text()).toBe('皇甫谧')
    // No invented 朝代/字/号 and no publication line when the API is silent.
    expect(findAll(wrapper, '.dh-object__meta')).toHaveLength(0)
    expect(wrapper.find('.person-page__publication').exists()).toBe(false)
    expect(wrapper.find('[data-page-state="error"]').exists()).toBe(false)
  })

  it('renders depth content when the real API supplies events and assertions', async () => {
    const rich: PublicPerson = {
      ...PERSON,
      events: [
        { event_id: 'e1', role: '早慧好学', description: '出身安定皇甫氏，家道中落后仍勤学不辍。' },
        { event_id: 'e2', role: '拒仕治学', description: null },
      ],
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
    }
    const wrapper = await mountPersonOk(rich)
    // Regions become PRESENT and render real API rows.
    expect(wrapper.find('[data-slot="context"]').attributes('data-slot-state')).toBe('PRESENT')
    expect(wrapper.find('[data-slot="evidence"]').attributes('data-slot-state')).toBe('PRESENT')
    const events = findAll(wrapper, '.person-events__role')
    expect(events).toEqual(['早慧好学', '拒仕治学'])
    expect(wrapper.find('.person-assertions__value').text()).toContain('针灸甲乙经')
    expect(wrapper.find('.person-assertions__meta').text()).toContain('证据 ×1')
    // No PARTIAL band once real depth content is present.
    expect(wrapper.find('.dh-object__incomplete').exists()).toBe(false)
  })
})

describe('CF-03 person archive — discriminated page states', () => {
  it('exposes a programmatically understandable loading state', async () => {
    let resolve!: (value: unknown) => void
    const pending = new Promise((r) => {
      resolve = r
    })
    const wrapper = await mountPerson(() => pending)
    const loading = wrapper.find('[role="status"]')
    expect(loading.exists()).toBe(true)
    expect(wrapper.find('h1.dh-object__title').exists()).toBe(false)
    resolve(envelope(PERSON))
    await vi.waitFor(() => {
      expect(wrapper.find('h1.dh-object__title').text()).toBe('皇甫谧')
    })
  })

  it('shows a dedicated NOT_FOUND page on a real 404 (never a generic error)', async () => {
    const wrapper = await mountPerson(() => ({ ok: false, status: 404 }))
    await vi.waitFor(() => {
      expect(wrapper.find('[data-page-state="not-found"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-page-state="not-found"] h1').text()).toBe('未找到该人物档案')
    expect(wrapper.find('[data-page-state="error"]').exists()).toBe(false)
    expect(wrapper.find('[role="alert"]').exists()).toBe(false)
  })

  it('shows a distinct ERROR state on a server failure (500 != empty record)', async () => {
    const wrapper = await mountPerson(() => ({ ok: false, status: 500 }))
    await vi.waitFor(() => {
      expect(wrapper.find('[data-page-state="error"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-page-state="error"] [role="alert"]').exists()).toBe(true)
    expect(wrapper.find('[data-page-state="not-found"]').exists()).toBe(false)
  })

  it('shows a distinct ERROR state on a transport/network failure', async () => {
    const wrapper = await mountPerson(() => {
      throw new TypeError('Failed to fetch')
    })
    await vi.waitFor(() => {
      expect(wrapper.find('[data-page-state="error"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-page-state="error"]').text()).toContain('人物资料加载失败')
  })
})

describe('CF-03 person archive — CF-02 primitive integration & accessibility', () => {
  it('composes DHObjectLayout with a single coherent H1 (N-F-1 contract)', async () => {
    const wrapper = await mountPersonOk()
    const headings = wrapper.findAll('h1')
    expect(headings).toHaveLength(1)
    expect(headings[0].classes()).toContain('dh-object__title')
    // The header region is PRESENT and carries the archive IA label override.
    expect(wrapper.find('[data-slot="header"]').attributes('data-slot-state')).toBe('PRESENT')
    expect(wrapper.find('[data-slot="header"] .dh-object__slot-title').text()).toBe('人物档案')
    expect(wrapper.find('[data-slot="context"] .dh-object__slot-title').text()).toBe('生平')
    expect(wrapper.find('[data-slot="evidence"] .dh-object__slot-title').text()).toBe('史料依据')
  })

  it('reloads the real API when the route id changes', async () => {
    const ids: string[] = []
    const handler: FetchHandler = (url) => {
      ids.push(url)
      const id = url.split('/').pop()
      return envelope(id === ARCHIVE_PERSON_ID ? PERSON : { ...PERSON, name_zh: '某人物' })
    }
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/persons/:id', component: PersonDetailView }],
    })
    stubFetch(handler)
    router.push(`/persons/${ARCHIVE_PERSON_ID}`)
    await router.isReady()
    const wrapper = mount(PersonDetailView, {
      attachTo: document.body,
      global: { plugins: [router] },
    })
    mountedWrappers.push(wrapper)
    await vi.waitFor(() => {
      expect(wrapper.find('h1.dh-object__title').text()).toBe('皇甫谧')
    })
    router.push('/persons/person-other')
    await router.isReady()
    await vi.waitFor(() => {
      expect(wrapper.find('h1.dh-object__title').text()).toBe('某人物')
    })
    expect(ids.filter((url) => url.includes('/persons/'))).toHaveLength(2)
  })

  it('passes axe on the rendered archive page', async () => {
    const wrapper = await mountPersonOk()
    const results = await axe.run(wrapper.element as HTMLElement)
    const messages = results.violations.map((v) => v.id)
    expect(messages).toEqual([])
  })
})

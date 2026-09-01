/**
 * UX2-P1 Person Archive — DHObjectLayout + G1-C states + F-5 coverage tests.
 *
 * Covers the UX2-P1 contract: DHObjectLayout regions/states render on the
 * person page; G1-C presentation states (RESOURCE_READY / SCHOLARLY_UNCERTAIN /
 * METADATA_ONLY / ABSENT_OPTIONAL); F-5 Life Events / Historical Assessments
 * (后论) / Archival Media from real data; heading hierarchy; negative
 * boundaries (no fabrication, no Later Scholarship, no synthesized facts).
 */
import { afterEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import axe from 'axe-core'
import PersonDetailView from '../views/persons/PersonDetailView.vue'
import { ARCHIVE_RECORDS } from '../data/archiveInventory'
import { INVENTORY_MOVIES } from '../data/contentInventory'

const PERSON = {
  entity_id: 'person-huangfu-mi',
  name_zh: '皇甫谧',
  name_pinyin: 'Huángfǔ Mì',
  courtesy_name: '士安',
  pseudonym: '玄晏先生',
  dynasty: '西晋',
  publication_status: 'published',
  assertions: [],
  events: [],
}

/** Deterministic projection of the AUTHORITATIVE archiveInventory a-movies
 *  record (客户提供：皇甫谧电影资料 → 《皇甫谧一》《针灸鼻祖皇甫谧》第 1 集
 *  大器晚成; INVENTORY_MOVIES = 2). The F-5 test explicitly binds this fixture
 *  to that source — no arbitrary test-only MEDIA objects are accepted as proof. */
const MEDIA = {
  items: [
    {
      id: 'm1',
      name: '《皇甫谧一》',
      category: 'movie',
      mime_type: 'video/mp4',
      byte_size: 1024,
      license_basis: '客户提供资料（已授权公开）',
      restriction: null,
      object_key: 'movies/huangfu-mi-1.mpg',
    },
    {
      id: 'm2',
      name: '《针灸鼻祖皇甫谧》第 1 集 大器晚成',
      category: 'movie',
      mime_type: 'video/mp4',
      byte_size: 2048,
      license_basis: '客户提供资料（已授权公开）',
      restriction: null,
      object_key: 'movies/huangfu-mi-2.mpg',
    },
  ],
  total: 2,
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
    routes: [{ path: '/persons/:id', component: PersonDetailView, children: [] }],
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

describe('UX2-P1 — DHObjectLayout regions & slot states', () => {
  it('renders the DHObjectLayout with context/evidence/relations regions and correct slot states', async () => {
    const wrapper = await mountPerson()
    const layout = wrapper.find('[data-primitive="dh-object"]')
    expect(layout.exists()).toBe(true)
    // header ABSENT_OPTIONAL collapses completely (hero owns the object title)
    expect(wrapper.find('[data-slot="header"]').exists()).toBe(false)
    expect(wrapper.find('[data-slot="context"]').attributes('data-slot-state')).toBe(
      'INCOMPLETE_WITH_EVIDENCE_STATE',
    )
    expect(wrapper.find('[data-slot="evidence"]').attributes('data-slot-state')).toBe(
      'INCOMPLETE_WITH_EVIDENCE_STATE',
    )
    expect(wrapper.find('[data-slot="relations"]').attributes('data-slot-state')).toBe('PRESENT')
  })

  it('context region renders the SCHOLARLY_UNCERTAIN note (生卒年争议) with role=status', async () => {
    const wrapper = await mountPerson()
    const note = wrapper.find('[data-slot="context"] .incomplete-note[role="status"]')
    expect(note.exists()).toBe(true)
    expect(note.find('.hfm-status').attributes('data-status')).toBe('SCHOLARLY_UNCERTAIN')
    expect(note.find('.hfm-status').text()).toBe('尚有争议')
    expect(note.text()).toContain('建安/正始')
  })

  it('evidence region renders the METADATA_ONLY note (四论原典全文未收录)', async () => {
    const wrapper = await mountPerson()
    const note = wrapper.find('[data-slot="evidence"] .incomplete-note[role="status"]')
    expect(note.exists()).toBe(true)
    expect(note.find('.hfm-status').attributes('data-status')).toBe('METADATA_ONLY')
    expect(note.text()).toContain('原典全文未收录')
  })

  it('context slot content renders works + 史料整理 (real data)', async () => {
    const wrapper = await mountPerson()
    const rows = wrapper.findAll('.object-context__row').map((r) => r.text())
    expect(rows.some((r) => r.includes('《针灸甲乙经》'))).toBe(true)
    expect(rows.some((r) => r.includes('其传（史料来源整理）'))).toBe(true)
  })

  it('evidence slot renders the generic 后论 aggregate (no 《晋书》 misattribution) and the docx archive items', async () => {
    const wrapper = await mountPerson()
    const items = wrapper.findAll('.object-evidence__item')
    expect(items).toHaveLength(3)
    const text = items.map((i) => i.text()).join(' ')
    expect(text).toContain('后论 · 论其人（历代评价引文 12 条')
    expect(text).toContain('出处逐条标注')
    expect(text).toContain('citation available')
    expect(text).toContain('其传文稿')
    expect(text).toContain('后论文稿')
    // P0-02 fail-on-defective: the aggregate 12-条 count must never be
    // attributed to 《晋书》 (the 论其人 citations are heterogeneous)
    expect(text).not.toMatch(/《晋书》[^（]*（[^）]*12[^）]*条）/)
    expect(text).not.toMatch(/《晋书》[^（]*（后论引文 \d+ 条）/)
  })

  it('relations region renders explicit semantics (no connector markup)', async () => {
    const wrapper = await mountPerson()
    const sems = wrapper.findAll('.relation-item__sem').map((n) => n.text())
    expect(sems).toContain('EXPLICIT_RELATION')
    expect(sems).toContain('ASSOCIATED_CONTEXT')
    expect(sems).not.toContain('lineage')
    // relations are text labels only — no svg/connector/line markup (text
    // arrows like “阅读全文 →” are legitimate affordances, not connectors)
    const html = wrapper.html()
    expect(html).not.toMatch(/<svg|connector|arrow/)
  })
})

describe('UX2-P1 — F-5 coverage from real data', () => {
  it('Life Events: 生平 timeline renders the four confirmed life phases', async () => {
    const wrapper = await mountPerson()
    const titles = wrapper.findAll('.timeline__title').map((t) => t.text())
    expect(titles).toEqual(['求学悟道', '拒仕治学', '久病研医', '著书传世'])
  })

  it('Historical Assessments: 后论 section renders houlun FULL_TEXT content with 全文已整理', async () => {
    const wrapper = await mountPerson()
    const section = wrapper.find('[aria-labelledby="afterwords-heading"]')
    const badge = section.find('.hfm-status')
    expect(badge.exists()).toBe(true)
    expect(badge.attributes('data-status')).toBe('RESOURCE_READY')
    expect(badge.text()).toBe('全文已整理')
    expect(section.text()).toContain('后论 · 历史评价汇编')
    expect(section.find('a[href="/reader/houlun"]').exists()).toBe(true)
  })

  it('其传 section renders qichuan FULL_TEXT content with 全文已整理', async () => {
    const wrapper = await mountPerson()
    const section = wrapper.find('[aria-labelledby="biography-heading"]')
    const badge = section.find('.hfm-status')
    expect(badge.attributes('data-status')).toBe('RESOURCE_READY')
    expect(badge.text()).toBe('全文已整理')
    expect(section.text()).toContain('其传 · 史料来源整理')
    expect(section.find('a[href="/reader/qichuan"]').exists()).toBe(true)
  })

  it('Archival Media: 影像资料 renders movies from the media projection', async () => {
    const wrapper = await mountPerson()
    const titles = wrapper.findAll('.movie-card__title').map((n) => n.text())
    expect(titles.some((t) => t.includes('针灸鼻祖皇甫谧'))).toBe(true)
  })

  it('F-5 Archival Media — authoritative record exists with traceable provenance', () => {
    const archive = ARCHIVE_RECORDS.find((r) => r.id === 'a-movies')
    expect(archive).toBeDefined()
    expect(archive?.status).toBe('AVAILABLE')
    expect(archive?.sourceName).toContain('客户提供：皇甫谧电影资料')
    expect(INVENTORY_MOVIES).toBe(2)
    expect(archive?.count).toBe(INVENTORY_MOVIES)
  })

  it('F-5 Archival Media — the media projection is bound to the authoritative record (no synthetic fixture)', () => {
    const archive = ARCHIVE_RECORDS.find((r) => r.id === 'a-movies')
    expect(archive).toBeDefined()
    const strip = (s: string) => s.replace(/\s+/g, '')
    expect(MEDIA.items).toHaveLength(INVENTORY_MOVIES)
    for (const item of MEDIA.items) {
      expect(strip(archive!.description)).toContain(strip(item.name))
    }
  })

  it('F-5 Archival Media — projection reaches the person archive surface with correct presentation', async () => {
    const wrapper = await mountPerson()
    const titles = wrapper.findAll('.movie-card__title').map((n) => n.text())
    expect(titles).toEqual(['《皇甫谧一》', '《针灸鼻祖皇甫谧》第 1 集 大器晚成'])
    expect(wrapper.find('.movie-card__meta').text()).toContain('影视资料')
  })

  it('F-5 Later Scholarship is NOT added (DEFERRED)', async () => {
    const wrapper = await mountPerson()
    const text = wrapper.text()
    expect(text).not.toContain('现代学者研究')
    expect(text).not.toContain('Later Scholarship')
  })
})

describe('UX2-P1 — heading hierarchy & negative boundaries', () => {
  it('heading hierarchy: exactly one h1, no level skips', async () => {
    const wrapper = await mountPerson()
    const headings = wrapper.findAll('h1, h2, h3').map((h) => Number(h.element.tagName.slice(1)))
    expect(headings.filter((l) => l === 1)).toHaveLength(1)
    for (let i = 1; i < headings.length; i += 1) {
      expect(headings[i] - headings[i - 1]).toBeLessThanOrEqual(1)
    }
  })

  it('no fabricated historical facts or synthesized bibliographic values', async () => {
    const wrapper = await mountPerson()
    const text = wrapper.text()
    // synthesized citation locators (卷/页/章节 numbers) — never invented
    expect(text).not.toMatch(/第\s*\d+\s*(卷|页|章|节)/)
    expect(text).not.toContain('版本号')
    expect(text).not.toContain('馆藏')
  })

  it('passes axe assertions on the person page', async () => {
    const wrapper = await mountPerson(true)
    const results = await axe.run(wrapper.element as HTMLElement)
    expect(results.violations).toHaveLength(0)
  })
})

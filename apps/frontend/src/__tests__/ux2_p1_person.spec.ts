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
import { ARCHIVE_RECORDS, ARCHIVE_MEDIA_RECORDS } from '../data/archiveInventory'
import { projectPublicMedia } from '../data/mediaProjection'
import { INVENTORY_MOVIES } from '../data/contentInventory'
import { formatBytes } from '../services/media'

/**
 * F-5 Archival Media — production chain proof (P1-01 V4 closure).
 *
 * Chain under test (all production code/data paths):
 *   real customer media bytes (hfmzl/皇甫谧/皇甫谧电影/)
 *     → governed per-media source record (archiveInventory ARCHIVE_MEDIA_RECORDS)
 *     → production media projection (data/mediaProjection.projectPublicMedia)
 *     → runtime readback (PersonDetailView → fetchPublicMedia transport)
 *     → rendered archival media
 *
 * fsModule/MEDIA_SOURCE_DIR are used ONLY for fail-closed SOURCE-DRIFT
 * detection (the governed record's captured byte_size/sha256/filename must
 * still match the real files) — the projection itself is never test-derived.
 */
const fsModule = (await import('node:fs' as string)) as unknown as {
  readdirSync(path: string): string[]
  statSync(path: string): { size: number }
  createReadStream(path: string): NodeReadStream
}
const MEDIA_SOURCE_DIR = `${(globalThis as { process?: { cwd(): string } }).process?.cwd() ?? '.'}/../../hfmzl/皇甫谧/皇甫谧电影`

interface NodeReadStream {
  on(event: 'data', cb: (chunk: Uint8Array) => void): NodeReadStream
  on(event: 'end', cb: () => void): NodeReadStream
  on(event: 'error', cb: (err: Error) => void): NodeReadStream
}

/** SHA-256 of a real file (streamed; used only for source-drift detection). */
async function hashFileSha256(path: string): Promise<string> {
  const cryptoModule = (await import('node:crypto' as string)) as unknown as {
    createHash(algorithm: string): { update(data: Uint8Array): void; digest(encoding: string): string }
  }
  const hash = cryptoModule.createHash('sha256')
  await new Promise<void>((resolve, reject) => {
    const stream = fsModule.createReadStream(path)
    stream.on('data', (chunk: Uint8Array) => {
      hash.update(chunk)
    })
    stream.on('end', () => resolve())
    stream.on('error', reject)
  })
  return hash.digest('hex')
}

/** Production projection output (the same module the E2E imports). */
const MEDIA = projectPublicMedia('movie')
const MEDIA_ENVELOPE = { items: projectPublicMedia(), total: projectPublicMedia().length }

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
      if (String(url).includes('/media')) return Promise.resolve(envelope(MEDIA_ENVELOPE))
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

  it('Archival Media: 影像资料 renders movies from the real media projection', async () => {
    const wrapper = await mountPerson()
    const titles = wrapper.findAll('.movie-card__title').map((n) => n.text())
    expect(titles).toEqual(MEDIA.map((m) => m.name))
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

  it('F-5 Archival Media — governed per-media source records exist with mechanically captured fields', () => {
    const archive = ARCHIVE_RECORDS.find((r) => r.id === 'a-movies')
    expect(archive).toBeDefined()
    expect(ARCHIVE_MEDIA_RECORDS).toHaveLength(INVENTORY_MOVIES)
    const strip = (s: string) => s.replace(/\s+/g, '')
    for (const rec of ARCHIVE_MEDIA_RECORDS) {
      // source identity (object_key) + real filename + governed title
      expect(rec.id).toBe(rec.objectKey)
      expect(rec.objectKey).toContain('皇甫谧/皇甫谧电影/')
      expect(rec.filename).toMatch(/\.mpg$/)
      // governed title recorded in a-movies description / asset map
      expect(strip(archive!.description)).toContain(strip(rec.title))
      // mechanically captured bytes + checksum + MIME
      expect(rec.byteSize).toBeGreaterThan(0)
      expect(rec.sha256).toMatch(/^[0-9a-f]{64}$/)
      expect(rec.mimeType).toMatch(/^video\//)
      // governance license policy (asset-map row 57)
      expect(rec.licenseBasis).toBe('授权公开（存在文件才可播放）')
      // not yet imported into governed object storage (admission pending)
      expect(rec.importState).toBe('NOT_IMPORTED')
    }
  })

  it('F-5 Archival Media — production projection maps governed records to MediaAsset items (test-production equivalence)', () => {
    const projected = projectPublicMedia()
    expect(projected).toHaveLength(ARCHIVE_MEDIA_RECORDS.length)
    for (const rec of ARCHIVE_MEDIA_RECORDS) {
      const item = projected.find((p) => p.object_key === rec.objectKey)
      expect(item).toBeDefined()
      // every projected field traces to the governed record (no test-authored values)
      expect(item!.id).toBe(rec.id)
      expect(item!.name).toBe(rec.title)
      expect(item!.object_key).toBe(rec.objectKey)
      expect(item!.mime_type).toBe(rec.mimeType)
      expect(item!.byte_size).toBe(rec.byteSize)
      expect(item!.rights_holder).toBe(rec.rightsHolder)
      expect(item!.license_basis).toBe(rec.licenseBasis)
      expect(item!.category).toBe('movie')
      expect(item!.publication_state).toBe('published')
    }
    // backend category rule: object-key path containing 电影 → movie
    expect(projectPublicMedia('movie')).toHaveLength(ARCHIVE_MEDIA_RECORDS.length)
  })

  it(
    'F-5 Archival Media — fail-closed source-drift detection against the real media files',
    async () => {
      const realFiles = fsModule
        .readdirSync(MEDIA_SOURCE_DIR)
        .filter((f) => f.endsWith('.mpg') || f.endsWith('.mp4'))
      expect(realFiles).toHaveLength(INVENTORY_MOVIES)
      for (const rec of ARCHIVE_MEDIA_RECORDS) {
        const realPath = `${MEDIA_SOURCE_DIR}/${rec.filename}`
        // real file exists and the governed filename matches
        expect(realFiles).toContain(rec.filename)
        // byte size still matches the real file stat
        expect(fsModule.statSync(realPath).size).toBe(rec.byteSize)
        // checksum still matches the real file bytes
        const hash = await hashFileSha256(realPath)
        expect(hash).toBe(rec.sha256)
      }
    },
    120000,
  )

  it('F-5 Archival Media — runtime readback: rendered metadata matches the production projection', async () => {
    const wrapper = await mountPerson()
    const cards = wrapper.findAll('.movie-card')
    expect(cards).toHaveLength(MEDIA.length)
    const titles = wrapper.findAll('.movie-card__title').map((n) => n.text())
    expect(titles).toEqual(MEDIA.map((m) => m.name))
    const metas = wrapper.findAll('.movie-card__meta').map((n) => n.text())
    const rights = wrapper.findAll('.movie-card__rights').map((n) => n.text())
    for (let i = 0; i < MEDIA.length; i += 1) {
      expect(metas[i]).toContain('影视资料') // category label
      expect(metas[i]).toContain(formatBytes(MEDIA[i].byte_size)) // real size → formatBytes
      expect(rights[i]).toBe(MEDIA[i].license_basis) // governed license policy
    }
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

/**
 * searchIndex — deterministic frontend search projection (UI-10).
 *
 * Built ONCE at module load from the established content semantics
 * (core person / yanCollection / workCollection / jiayiView editions /
 * archiveInventory / paper preview). searchableText aggregates PUBLIC fields
 * only — internal provenance (registerKey, hfmzl/, zzcl/) is never included.
 *
 * Ranking (deterministic): exact title > title prefix > title includes >
 * name/author exact > metadata match > body match; stable tie-break by
 * type priority, year, title. Same query → same order, always.
 */
import type { FacetCount, SearchIndexEntry, SearchResult, SearchType } from '../types/search'
import {
  CORE_PERSON_DATES,
  CORE_PERSON_DEFINITION,
  CORE_PERSON_IDENTITIES,
  CORE_PERSON_NAME,
} from '../config/corePerson'
import { YAN_COLLECTION } from './yanCollection'
import { WORK_COLLECTION } from './workCollection'
import { JIAYI_ANCIENT_EDITIONS, JIAYI_MODERN_EDITIONS, JIAYI_PAPER_PREVIEW } from './jiayiView'
import { ARCHIVE_RECORDS } from './archiveInventory'
import {
  HERITAGE_APPRENTICESHIPS,
  HERITAGE_MEDIA,
  HERITAGE_PERSON,
  HERITAGE_PROJECT,
  HERITAGE_STUDIOS,
} from './heritageView'
import { READER_DOCUMENTS } from './readerDocuments'

/** Audited customer paper total (not searchable until structured). */
export const AUDITED_PAPER_TOTAL = 515

export const PAGE_SIZE = 10

const TYPE_ORDER: Record<SearchType, number> = {
  person: 0,
  work: 1,
  edition: 2,
  text: 3,
  archive: 4,
  paper: 5,
}

const TYPE_LABELS: Record<SearchType, string> = {
  person: '人物',
  text: '文本',
  work: '作品',
  edition: '版本',
  archive: '档案',
  paper: '论文',
}

function entry(
  id: string,
  type: SearchType,
  title: string,
  opts: {
    subtitle?: string
    year?: number
    authors?: string[]
    themes?: string[]
    relatedEntities?: string[]
    status: string
    sourceName?: string
    route?: string
    body: string[]
  },
): SearchIndexEntry {
  return {
    id,
    type,
    title,
    subtitle: opts.subtitle,
    year: opts.year,
    authors: opts.authors,
    themes: opts.themes,
    relatedEntities: opts.relatedEntities,
    status: opts.status,
    sourceName: opts.sourceName,
    route: opts.route,
    searchableText: [
      title,
      opts.subtitle ?? '',
      ...(opts.authors ?? []),
      ...(opts.themes ?? []),
      ...(opts.relatedEntities ?? []),
      ...opts.body,
    ]
      .join(' ')
      .replace(/\s+/g, ' ')
      .trim(),
  }
}

/** Build once at module load (not per render). */
export const SEARCH_INDEX: readonly SearchIndexEntry[] = (() => {
  const entries: SearchIndexEntry[] = []

  // PERSON — reuse UI-04 core-person data source (no new fact model).
  entries.push(
    entry('person-huangfu-mi', 'person', CORE_PERSON_NAME, {
      subtitle: `${CORE_PERSON_DATES} · 西晋`,
      themes: [...CORE_PERSON_IDENTITIES],
      relatedEntities: ['其传', '其言', '《针灸甲乙经》', '《帝王世纪》', '《高士传》'],
      status: 'AVAILABLE',
      route: '/persons/person-huangfu-mi',
      body: [CORE_PERSON_DEFINITION, '医学家', '文学家', '史学家', '学者', '针灸鼻祖'],
    }),
  )

  // PERSON — 传承人物 刘君奇（HERITAGE_GENERATION CLOSED）
  entries.push(
    entry('person-liujunqi', 'person', HERITAGE_PERSON.name, {
      subtitle: `${HERITAGE_PERSON.generationTitle} · ${HERITAGE_PERSON.heritageRole}`,
      themes: ['第六代名医', '非遗传承人', '皇甫谧针灸'],
      relatedEntities: ['皇甫谧针灸非遗', '师承教育', '名中医工作室'],
      status: 'AVAILABLE',
      route: '/heritage',
      body: [
        HERITAGE_PERSON.biography,
        HERITAGE_PERSON.professionalTitle,
        HERITAGE_PERSON.institutionRole,
        ...HERITAGE_PERSON.academicRoles,
      ],
    }),
  )

  // ARCHIVE — heritage project / events / studios / media (route → /heritage)
  entries.push(
    entry('heritage-project', 'archive', `皇甫谧针灸非遗（${HERITAGE_PERSON.generationTitle}）`, {
      subtitle: '非遗活态传承数字档案',
      relatedEntities: ['刘君奇', '皇甫谧针灸'],
      status: 'AVAILABLE',
      sourceName: '客户提供：非遗传承申报资料',
      route: '/heritage',
      body: [HERITAGE_PROJECT.description, '非遗传承', '传承人'],
    }),
  )
  for (const event of HERITAGE_APPRENTICESHIPS) {
    entries.push(
      entry(`heritage-${event.id}`, 'archive', event.title, {
        subtitle: `师承教育 · ${event.date}`,
        relatedEntities: ['刘君奇', '师承教育'],
        status: 'AVAILABLE',
        sourceName: event.sourceName,
        route: '/heritage#apprenticeship',
        body: [event.description, event.location ?? ''],
      }),
    )
  }
  for (const studio of HERITAGE_STUDIOS) {
    entries.push(
      entry(`heritage-${studio.id}`, 'archive', studio.name, {
        subtitle: studio.institution,
        relatedEntities: ['刘君奇', '名中医工作室'],
        status: 'AVAILABLE',
        sourceName: studio.sourceName,
        route: '/heritage#studios',
        body: [studio.description],
      }),
    )
  }
  for (const coverage of HERITAGE_MEDIA) {
    entries.push(
      entry(`heritage-${coverage.id}`, 'archive', coverage.title, {
        subtitle: `${coverage.mediaOutlet} · ${coverage.date}`,
        relatedEntities: ['刘君奇', '媒体报道'],
        status: 'AVAILABLE',
        sourceName: coverage.sourceName,
        route: '/heritage#media',
        body: [coverage.description],
      }),
    )
  }

  // TEXT — reader documents (real customer docx text → reader route)
  for (const doc of READER_DOCUMENTS) {
    entries.push(
      entry(`reader-${doc.id}`, 'text', doc.title, {
        subtitle: doc.textType,
        relatedEntities: doc.relatedEntities.map((r) => r.label),
        status: doc.contentStatus,
        sourceName: doc.source,
        route: `/reader/${doc.id}`,
        body: [doc.description, ...doc.sections.map((s) => s.heading), doc.subtitle],
      }),
    )
  }

  // TEXT — 其言 collection records (customer docx content).
  for (const section of YAN_COLLECTION.sections) {
    for (const record of section.records) {
      entries.push(
        entry(record.id, 'text', `其言 · ${record.section}`, {
          subtitle: record.theme,
          relatedEntities: record.relatedWork ? [record.relatedWork] : undefined,
          status: record.status,
          sourceName: record.source,
          route: '/yan',
          body: [record.text, record.sourceContext ?? '', section.title, '其言'],
        }),
      )
    }
  }

  // WORK — UI-06 work layer.
  for (const work of WORK_COLLECTION) {
    entries.push(
      entry(work.id, 'work', work.title, {
        subtitle: `${work.historicalPeriod} · ${work.workType}`,
        authors: work.attribution !== '—' ? [work.attribution] : undefined,
        themes: [work.workType],
        relatedEntities: work.note ? [work.note] : undefined,
        status: work.status,
        route: work.href ?? '/works',
        body: [work.description, work.note ?? ''],
      }),
    )
  }

  // EDITION — UI-08 audited edition collection (ancient + modern).
  for (const edition of [...JIAYI_ANCIENT_EDITIONS, ...JIAYI_MODERN_EDITIONS]) {
    entries.push(
      entry(edition.id, 'edition', edition.title, {
        subtitle: edition.period,
        authors: edition.imprint ? [edition.imprint] : undefined,
        relatedEntities: ['《针灸甲乙经》'],
        status: edition.status,
        sourceName: '客户提供：甲乙经论著资料',
        route: '/jiayi#editions',
        body: [edition.description, edition.imprint ?? '', '《针灸甲乙经》版本'],
      }),
    )
  }

  // ARCHIVE — UI-06 archive records (public source names only).
  for (const record of ARCHIVE_RECORDS) {
    entries.push(
      entry(record.id, 'archive', record.title, {
        subtitle: record.category,
        relatedEntities: record.href ? [] : undefined,
        status: record.status,
        sourceName: record.sourceName,
        route: record.href,
        body: [record.description, record.sourceName, '档案'],
      }),
    )
  }

  // PAPER — real structured preview titles only (audited total ≠ searchable).
  for (const paper of JIAYI_PAPER_PREVIEW) {
    entries.push(
      entry(paper.id, 'paper', paper.title, {
        subtitle: paper.note,
        relatedEntities: ['《针灸甲乙经》'],
        status: 'METADATA_ONLY',
        sourceName: '客户提供：甲乙经研究论文资料',
        route: '/jiayi#papers',
        body: ['论文', '《针灸甲乙经》', paper.note ?? ''],
      }),
    )
  }

  return entries
})()

/** Real structured paper records (≠ AUDITED_PAPER_TOTAL). */
export const SEARCHABLE_PAPER_TOTAL = SEARCH_INDEX.filter((e) => e.type === 'paper').length

function normalize(text: string): string {
  return text.trim().toLowerCase()
}

function rankScore(entry: SearchIndexEntry, query: string): number {
  const q = normalize(query)
  if (!q) return 0
  const title = normalize(entry.title)
  const authors = (entry.authors ?? []).map(normalize)
  const names = (entry.relatedEntities ?? []).map(normalize)
  // 1 exact title
  if (title === q) return 1000
  // 2 title prefix
  if (title.startsWith(q)) return 900
  // 3 title contains
  if (title.includes(q)) return 800
  // 4 person/author exact
  if (authors.some((a) => a === q)) return 700
  // 5 name / metadata match (subtitle, themes, related entities)
  if (
    normalize(entry.subtitle ?? '').includes(q) ||
    (entry.themes ?? []).some((t) => normalize(t).includes(q)) ||
    names.some((n) => n.includes(q))
  )
    return 500
  // 6 body match
  if (normalize(entry.searchableText).includes(q)) return 300
  return 0
}

/** Deterministic full search over the index (ranked, stable order). */
export function searchIndex(query: string, type?: SearchType | 'all'): SearchResult[] {
  const q = query.trim()
  if (!q) return []
  const scored = SEARCH_INDEX.map((entry) => ({ entry, score: rankScore(entry, q) }))
    .filter((s) => s.score > 0)
    .filter((s) => type === undefined || type === 'all' || s.entry.type === type)
  scored.sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score
    const tp = TYPE_ORDER[a.entry.type] - TYPE_ORDER[b.entry.type]
    if (tp !== 0) return tp
    if ((a.entry.year ?? 0) !== (b.entry.year ?? 0))
      return (a.entry.year ?? 0) - (b.entry.year ?? 0)
    return a.entry.title.localeCompare(b.entry.title, 'zh')
  })
  return scored.map((s, i) => ({ entry: s.entry, rank: i }))
}

/** Facet counts computed from the CURRENT result set (real counts). */
export function facetCounts(results: SearchResult[]): FacetCount[] {
  return (Object.keys(TYPE_LABELS) as SearchType[]).map((type) => ({
    type,
    label: TYPE_LABELS[type],
    count: results.filter((r) => r.entry.type === type).length,
  }))
}

export function searchTypeLabel(type: SearchType): string {
  return TYPE_LABELS[type]
}

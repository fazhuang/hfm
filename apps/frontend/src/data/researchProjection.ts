/**
 * researchProjection — UI-11 presentation projections over EXISTING domain
 * data. No second search index, no duplicated Work/Edition/Person models.
 * Evidence summaries map existing ContentStatus (AVAILABLE/METADATA_ONLY/
 * DATA_GAP) — no invented governance states. 515/5 paper invariant and
 * lineage statuses (Jiayi DATA-GAP, Heritage PARTIAL) are preserved.
 */
import type { ResearchEntityViewModel } from '../types/research'
import { CORE_PERSON_NAME, CORE_PERSON_DATES, CORE_PERSON_DEFINITION } from '../config/corePerson'
import { WORK_COLLECTION } from './workCollection'
import { JIAYI_ANCIENT_EDITIONS, JIAYI_MODERN_EDITIONS, JIAYI_PAPER_PREVIEW } from './jiayiView'
import { ARCHIVE_RECORDS, ARCHIVE_GROUPS } from './archiveInventory'
import {
  HERITAGE_PERSON,
  HERITAGE_RECOGNITIONS,
  HERITAGE_APPRENTICESHIPS,
  HERITAGE_MEDIA,
} from './heritageView'
import { READER_DOCUMENTS, getReaderDocument } from './readerDocuments'
import { AUDITED_PAPER_TOTAL, SEARCHABLE_PAPER_TOTAL } from './searchIndex'

const STATUS_LABEL: Record<string, string> = {
  AVAILABLE: '已展示',
  METADATA_ONLY: '元数据已录',
  DATA_GAP: '整理中',
}

function evidenceFrom(
  status: string,
  sourceName: string,
  citationCount?: number,
): ResearchEntityViewModel['evidence'][number] {
  return {
    sourceName,
    contentStatus: status as ResearchEntityViewModel['evidence'][number]['contentStatus'],
    citationCount,
    note: STATUS_LABEL[status],
  }
}

export function researchEntity(type: string, id: string): ResearchEntityViewModel | undefined {
  if (type === 'person') {
    if (id === 'person-huangfu-mi') {
      return {
        type: 'person',
        id,
        title: CORE_PERSON_NAME,
        subtitle: `${CORE_PERSON_DATES} · 西晋 · 医学家/文学家/史学家/学者`,
        metadata: [
          { label: '生卒年', value: CORE_PERSON_DATES },
          { label: '核心身份', value: '针灸鼻祖 · 《针灸甲乙经》作者' },
          { label: '权威定义', value: CORE_PERSON_DEFINITION },
        ],
        evidence: [evidenceFrom('AVAILABLE', '客户提供：其传文稿（docx）')],
        related: [
          { label: '作品：其言四篇', href: '/research/entity/work/w-sandufu' },
          { label: '作品：《针灸甲乙经》', href: '/research/entity/work/w-jiayi' },
          { label: '其传史料整理', href: '/research/entity/reader/qichuan' },
          { label: '后论·历史评价', href: '/research/entity/reader/houlun' },
          { label: '非遗传承（刘君奇）', href: '/research/entity/heritage/liujunqi' },
        ],
        publicLink: { label: '查看公众人物页', href: '/persons/person-huangfu-mi' },
      }
    }
    if (id === 'person-liujunqi') {
      return {
        type: 'person',
        id,
        title: HERITAGE_PERSON.name,
        subtitle: `${HERITAGE_PERSON.generationTitle} · ${HERITAGE_PERSON.heritageRole}`,
        metadata: [
          { label: '代际', value: '第六代名医（HERITAGE_GENERATION CLOSED）' },
          { label: '传承身份', value: HERITAGE_PERSON.heritageRole },
          { label: '职务', value: HERITAGE_PERSON.institutionRole },
          { label: '荣誉', value: HERITAGE_PERSON.professionalTitle },
        ],
        evidence: [evidenceFrom('AVAILABLE', '客户提供：非遗传承申报资料')],
        related: [
          { label: '非遗研究视图', href: '/research/entity/heritage/liujunqi' },
          { label: '皇甫谧', href: '/research/entity/person/person-huangfu-mi' },
        ],
        publicLink: { label: '查看公众非遗页', href: '/heritage' },
      }
    }
  }

  if (type === 'work') {
    const work = WORK_COLLECTION.find((w) => w.id === id)
    if (work) {
      return {
        type: 'work',
        id,
        title: work.title,
        subtitle: `${work.historicalPeriod} · ${work.workType}`,
        metadata: [
          { label: '撰者', value: work.attribution },
          { label: '时期', value: work.historicalPeriod },
          { label: '作品类型', value: work.workType },
          ...(work.editionCount !== undefined
            ? [{ label: '版本记录', value: `${work.editionCount} 种` }]
            : []),
        ],
        evidence: [
          evidenceFrom(
            work.status,
            work.href === '/archive' ? '客户提供：论著资料' : (work.note ?? '客户提供：论著资料'),
          ),
        ],
        related: [
          ...(work.id === 'w-jiayi'
            ? [{ label: '版本研究', href: '/research/entity/edition/yitong-zhengmai-1601' }]
            : []),
          { label: '检索论文', href: '/research/search?q=针灸甲乙经' },
        ],
        publicLink: work.href ? { label: '查看公众页', href: work.href } : undefined,
        description: work.description,
      }
    }
  }

  if (type === 'edition') {
    const edition = [...JIAYI_ANCIENT_EDITIONS, ...JIAYI_MODERN_EDITIONS].find((e) => e.id === id)
    if (edition) {
      return {
        type: 'edition',
        id,
        title: edition.title,
        subtitle: edition.period,
        metadata: [
          { label: '时期/年代', value: edition.period },
          ...(edition.imprint ? [{ label: '刊刻/整理', value: edition.imprint }] : []),
          {
            label: '版本类型',
            value: edition.editionType === 'ancient' ? '古代版本' : '近现代整理版本',
          },
          { label: '内容状态', value: STATUS_LABEL[edition.status] },
        ],
        evidence: [evidenceFrom(edition.status, '客户提供：甲乙经论著资料')],
        related: [{ label: '作品：《针灸甲乙经》', href: '/research/entity/work/w-jiayi' }],
        publicLink: { label: '查看公众甲乙经专题', href: '/jiayi#editions' },
        description: edition.description,
      }
    }
  }

  if (type === 'archive') {
    const record = ARCHIVE_RECORDS.find((r) => r.id === id)
    if (record) {
      const group = ARCHIVE_GROUPS.find((g) => g.category === record.category)
      return {
        type: 'archive',
        id,
        title: record.title,
        subtitle: group?.label ?? record.category,
        metadata: [
          { label: '记录类型', value: group?.label ?? '—' },
          { label: '公开来源', value: record.sourceName },
          ...(record.count !== undefined
            ? [{ label: '数量（审计）', value: `${record.count} 件` }]
            : []),
        ],
        evidence: [evidenceFrom(record.status, record.sourceName)],
        related: record.href ? [{ label: '进入档案记录', href: record.href }] : [],
        description: record.description,
      }
    }
  }

  if (type === 'paper') {
    // Papers: real structured preview titles only (audited total ≠ searchable).
    const paper = JIAYI_PAPER_PREVIEW.find((p) => p.id === id)
    if (paper) {
      return {
        type: 'paper',
        id,
        title: paper.title,
        subtitle: '论文题录（METADATA_ONLY）',
        metadata: [
          { label: '题录状态', value: '已结构化（可检索）' },
          { label: '论文总量（审计）', value: String(AUDITED_PAPER_TOTAL) },
          { label: '已结构化题录', value: String(SEARCHABLE_PAPER_TOTAL) },
        ],
        evidence: [evidenceFrom('METADATA_ONLY', '客户提供：甲乙经研究论文资料')],
        related: [{ label: '《针灸甲乙经》', href: '/research/entity/work/w-jiayi' }],
        publicLink: { label: '查看公众论文入口', href: '/jiayi#papers' },
      }
    }
  }

  if (type === 'heritage') {
    if (id === 'liujunqi') {
      return {
        type: 'heritage',
        id,
        title: '皇甫谧针灸非遗 · 刘君奇',
        subtitle: `${HERITAGE_PERSON.generationTitle} · ${HERITAGE_PERSON.heritageRole}`,
        metadata: [
          { label: '传承人物', value: HERITAGE_PERSON.name },
          { label: '代际', value: HERITAGE_PERSON.generationTitle },
          { label: '非遗项目', value: '皇甫谧针灸（市级非遗代表性项目）' },
          { label: '认定与荣誉', value: `${HERITAGE_RECOGNITIONS.length} 项（结构化）` },
          { label: '谱系状态', value: 'LINEAGE_STRUCTURING: PARTIAL（不虚构中间代）' },
        ],
        evidence: [
          evidenceFrom('AVAILABLE', '客户提供：非遗传承申报资料'),
          ...HERITAGE_MEDIA.slice(0, 1).map((m) =>
            evidenceFrom('AVAILABLE', `${m.mediaOutlet} · ${m.date}`),
          ),
        ],
        related: [
          { label: '师承教育', href: '/heritage#apprenticeship' },
          { label: '媒体报道', href: '/heritage#media' },
          { label: '传承人物', href: '/research/entity/person/person-liujunqi' },
        ],
        publicLink: { label: '查看公众非遗页', href: '/heritage' },
        items: [
          ...HERITAGE_RECOGNITIONS.slice(0, 6).map((r) => ({ title: r.title, meta: r.category })),
          ...HERITAGE_APPRENTICESHIPS.map((a) => ({ title: a.title, meta: a.date })),
        ],
      }
    }
  }

  if (type === 'reader') {
    const doc = getReaderDocument(id)
    if (doc) {
      return {
        type: 'reader',
        id,
        title: doc.title,
        subtitle: doc.textType,
        metadata: [
          { label: '阅读状态', value: doc.readingStatus },
          { label: '内容状态', value: STATUS_LABEL[doc.contentStatus] },
          { label: '来源', value: doc.source },
          ...(doc.attribution ? [{ label: '整理', value: doc.attribution }] : []),
        ],
        evidence: [
          evidenceFrom(doc.contentStatus, doc.source, doc.id === 'houlun' ? 12 : undefined),
        ],
        related: doc.relatedEntities.map((r) => ({ label: r.label, href: r.href })),
        publicLink: { label: '打开阅读', href: `/reader/${doc.id}` },
        description: doc.description,
      }
    }
  }

  return undefined
}

/** Research landing scope summary — real inventory only. */
export function researchScopeSummary(): Array<{ label: string; value: string; href?: string }> {
  return [
    {
      label: '人物档案',
      value: '2（皇甫谧 · 刘君奇）',
      href: '/research/entity/person/person-huangfu-mi',
    },
    { label: '作品', value: `${WORK_COLLECTION.length}`, href: '/research/entity/work/w-jiayi' },
    {
      label: '版本记录',
      value: `${JIAYI_ANCIENT_EDITIONS.length + JIAYI_MODERN_EDITIONS.length}`,
      href: '/research/entity/edition/yitong-zhengmai-1601',
    },
    { label: '档案记录', value: `${ARCHIVE_RECORDS.length}` },
    { label: '论文题录', value: `${SEARCHABLE_PAPER_TOTAL}（审计 ${AUDITED_PAPER_TOTAL}）` },
    { label: 'Reader 文档', value: `${READER_DOCUMENTS.length}` },
  ]
}

export { SEARCHABLE_PAPER_TOTAL, AUDITED_PAPER_TOTAL }

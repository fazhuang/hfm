import type { ArchiveCategoryGroup, ArchiveRecord } from '../types/archive'
import {
  INVENTORY_HFM_DOCX,
  INVENTORY_LINEAGE_PNG,
  INVENTORY_LUNWEN_FILES,
  INVENTORY_LUNZHU_FILES,
  INVENTORY_MOVIES,
} from './contentInventory'

/**
 * Archive inventory (UI-06) — 平台收录了什么（公共视角）。
 *
 * sourceName = 可理解的公开来源名；registerKey 仅作开发 provenance，
 * 公共 UI 不渲染内部绝对文件路径。
 */
export const ARCHIVE_RECORDS: ArchiveRecord[] = [
  {
    id: 'a-qichuan',
    title: '其传',
    category: 'hfm-person',
    sourceName: '客户提供：其传文稿（docx）',
    registerKey: 'hfmzl/皇甫谧/其传/其传.docx',
    description:
      '皇甫谧传记史料来源整理（本源史料 / 地方志 / 类书 / 现代考据 / 谱系 / 图像遗存）。',
    status: 'AVAILABLE',
    href: '/reader/qichuan',
  },
  {
    id: 'a-houlun',
    title: '后论',
    category: 'hfm-person',
    sourceName: '客户提供：后论文稿（docx）',
    registerKey: 'hfmzl/皇甫谧/后论/后论.docx',
    description: '后世评价汇编（论其人 / 演其人 / 讲其人 / 冠其名）。',
    status: 'AVAILABLE',
    href: '/reader/houlun',
  },
  {
    id: 'a-qiyan',
    title: '其言',
    category: 'hfm-works',
    sourceName: '客户提供：其言文稿（docx）',
    registerKey: 'hfmzl/皇甫谧/其言/其言.docx',
    description: '皇甫谧言论与文字选编（《三都赋》序、玄守论、释劝论、笃终论）。',
    status: 'AVAILABLE',
    href: '/yan',
  },
  {
    id: 'a-jiayi-lunzhu',
    title: '《针灸甲乙经》论著资料',
    category: 'jiayi-editions',
    sourceName: '客户提供：甲乙经论著资料（古籍版本 / 校注本 / 现代版）',
    registerKey: 'hfmzl/针灸甲乙经/论著/',
    description: '历代版本与相关论著，含医统正脉本、四库全书本、行素草堂本、校注本与现代整理本等。',
    count: INVENTORY_LUNZHU_FILES,
    status: 'METADATA_ONLY',
    href: '/jiayi',
  },
  {
    id: 'a-jiayi-lineage',
    title: '版本脉络图',
    category: 'jiayi-editions',
    sourceName: '客户提供：版本及各版本之间脉络联系图',
    registerKey: 'hfmzl/针灸甲乙经/版本及各版本之间脉络联系/',
    description: '《针灸甲乙经》版本脉络示意（正式展示资产；结构化关系 DATA-GAP）。',
    count: INVENTORY_LINEAGE_PNG,
    status: 'AVAILABLE',
    href: '/jiayi#lineage',
  },
  {
    id: 'a-lunwen',
    title: '学术论文',
    category: 'modern-research',
    sourceName: '客户提供：甲乙经研究论文资料',
    registerKey: 'hfmzl/针灸甲乙经/论文/',
    description: '《针灸甲乙经》研究论文（题录整理中；全文检索见后续检索功能）。',
    count: INVENTORY_LUNWEN_FILES,
    status: 'METADATA_ONLY',
    href: '/search?q=针灸甲乙经',
  },
  {
    id: 'a-movies',
    title: '皇甫谧影像资料',
    category: 'media',
    sourceName: '客户提供：皇甫谧电影资料',
    registerKey: 'hfmzl/皇甫谧/皇甫谧电影/',
    description: '《皇甫谧一》《针灸鼻祖皇甫谧》第 1 集 大器晚成。',
    count: INVENTORY_MOVIES,
    status: 'AVAILABLE',
  },
  {
    id: 'a-heritage',
    title: '皇甫谧针灸非遗资料',
    category: 'heritage',
    sourceName: '客户提供：非遗传承申报资料',
    registerKey: 'zzcl/',
    description: '非遗认定、证书、传承人物与师承教育资料（详细展示属非遗传承页）。',
    status: 'METADATA_ONLY',
    href: '/heritage',
  },
]

/* ==========================================================================
   Governed per-media source records (UX2-P1 F-5 closure)
   ==========================================================================
   One record per real customer media file — MEDIA_SOURCE_OF_TRUTH:
     hfmzl/皇甫谧/皇甫谧电影/皇甫谧一.mpg
     hfmzl/皇甫谧/皇甫谧电影/《针灸鼻祖皇甫谧》第1集 大器晚成.mpg
   recorded in the governance asset map (docs/design/HFM-CONTENT-ASSET-MAP.md
   rows 31/57: filenames + count 2 + license policy 授权公开（存在文件才可播放）)
   and the aggregate archive record `a-movies` above.

   Values are captured mechanically from the real files (byteSize = file stat,
   sha256 = hash of the real bytes, mimeType = detected MPEG program stream,
   title = governed asset-map title) or from frozen governance (licenseBasis).
   The fail-closed source-drift test re-verifies them against the real files.

   The media is NOT yet imported into backend object storage (importState
   NOT_IMPORTED; backend content admission is a separate phase). objectKey
   follows the existing registerKey source-path convention and the backend
   category rule (path containing 电影 → movie) — it is the governed source
   identity, not a fabricated storage key.
   ========================================================================== */
export interface MediaSourceRecord {
  /** stable source identity — MediaAsset unique identity (object_key). */
  id: string
  /** governed source register path (registerKey-relative + filename). */
  objectKey: string
  /** real source filename. */
  filename: string
  /** governed display title (asset map / a-movies recorded title). */
  title: string
  category: 'movie'
  /** captured from the real file (detected MPEG program stream). */
  mimeType: string
  /** captured from the real file stat. */
  byteSize: number
  /** captured from the real file bytes. */
  sha256: string
  rightsHolder: string
  /** governing rule: asset-map row 57 授权公开（存在文件才可播放）. */
  licenseBasis: string
  sourceName: string
  provenanceRef: string
  /** backend object-storage import state (admission pending). */
  importState: 'NOT_IMPORTED'
}

export const ARCHIVE_MEDIA_RECORDS: MediaSourceRecord[] = [
  {
    id: '皇甫谧/皇甫谧电影/皇甫谧一.mpg',
    objectKey: '皇甫谧/皇甫谧电影/皇甫谧一.mpg',
    filename: '皇甫谧一.mpg',
    title: '《皇甫谧一》',
    category: 'movie',
    mimeType: 'video/mpeg',
    byteSize: 1009262592,
    sha256: '1395a8b57ee998f71979dd5ba47c4ff50dad8fd121b27567e561e9f93085e0c0',
    rightsHolder: '客户提供',
    licenseBasis: '授权公开（存在文件才可播放）',
    sourceName: '客户提供：皇甫谧电影资料',
    provenanceRef: 'docs/design/HFM-CONTENT-ASSET-MAP.md row 31/57 · archiveInventory a-movies',
    importState: 'NOT_IMPORTED',
  },
  {
    id: '皇甫谧/皇甫谧电影/《针灸鼻祖皇甫谧》第1集 大器晚成.mpg',
    objectKey: '皇甫谧/皇甫谧电影/《针灸鼻祖皇甫谧》第1集 大器晚成.mpg',
    filename: '《针灸鼻祖皇甫谧》第1集 大器晚成.mpg',
    title: '《针灸鼻祖皇甫谧》第 1 集 大器晚成',
    category: 'movie',
    mimeType: 'video/mpeg',
    byteSize: 718133252,
    sha256: '14584639fef88bd95060e84fe4a80611385bf3b5fdbd6f0796470f0f350a97f1',
    rightsHolder: '客户提供',
    licenseBasis: '授权公开（存在文件才可播放）',
    sourceName: '客户提供：皇甫谧电影资料',
    provenanceRef: 'docs/design/HFM-CONTENT-ASSET-MAP.md row 31/57 · archiveInventory a-movies',
    importState: 'NOT_IMPORTED',
  },
]

export const ARCHIVE_GROUPS: ArchiveCategoryGroup[] = [
  {
    category: 'hfm-person',
    label: '皇甫谧人物资料',
    description: '传记、言论与后世论述文稿（docx）。',
    records: ARCHIVE_RECORDS.filter((r) => r.category === 'hfm-person'),
  },
  {
    category: 'hfm-works',
    label: '皇甫谧著作',
    description: '其言文稿（其言.docx）。',
    records: ARCHIVE_RECORDS.filter((r) => r.category === 'hfm-works'),
  },
  {
    category: 'jiayi-editions',
    label: '《针灸甲乙经》版本资料',
    description: '历代版本、论著与版本脉络图。',
    records: ARCHIVE_RECORDS.filter((r) => r.category === 'jiayi-editions'),
  },
  {
    category: 'modern-research',
    label: '现代研究资料',
    description: '学术论文（题录整理中）。',
    records: ARCHIVE_RECORDS.filter((r) => r.category === 'modern-research'),
  },
  {
    category: 'media',
    label: '影像资料',
    description: '皇甫谧相关影视资料。',
    records: ARCHIVE_RECORDS.filter((r) => r.category === 'media'),
  },
  {
    category: 'heritage',
    label: '非遗资料',
    description: '非遗认定、证书与传承资料（详细展示见非遗传承页）。',
    records: ARCHIVE_RECORDS.filter((r) => r.category === 'heritage'),
  },
]

export const ARCHIVE_DOCX_COUNT = INVENTORY_HFM_DOCX

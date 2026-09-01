import type { WorkRecord } from '../types/work'
import { YAN_SOURCE_NAME } from './yanCollection'

/**
 * WORK 层（UI-06）— 作品目录。Work ≠ Edition ≠ ArchiveRecord。
 *
 * 作品与版本信息均来自客户材料审计：古籍版本目录（hfmzl/针灸甲乙经/论著）
 * 与其言 docx。帝王世纪/高士传的版本来自客户目录（帝王世纪/高士传 文件夹）。
 */
export const WORK_COLLECTION: WorkRecord[] = [
  {
    id: 'w-jiayi',
    title: '《针灸甲乙经》',
    workType: '针灸学专著（文献整理编纂）',
    attribution: '皇甫谧',
    historicalPeriod: '西晋',
    description: '皇甫谧所撰针灸学专著，中国现存最早的针灸学典籍之一。',
    editionCount: 19,
    href: '/jiayi',
    note: '版本脉络 · 历代版本 · 论著 · 论文（见《针灸甲乙经》专题）',
    status: 'AVAILABLE',
    kind: 'canonical',
  },
  {
    id: 'w-diwangshiji',
    title: '《帝王世纪》',
    workType: '史部撰述（辑佚）',
    attribution: '皇甫谧',
    historicalPeriod: '西晋',
    description: '皇甫谧所撰史书，久佚，后人辑佚。客户资料含《帝王世纪》中华书局等版本与辑佚资料。',
    editionCount: 2,
    href: '/archive',
    note: '版本资料见数字档案',
    status: 'METADATA_ONLY',
    kind: 'compilation',
  },
  {
    id: 'w-gaoshizhuan',
    title: '《高士传》',
    workType: '人物传记（辑佚）',
    attribution: '皇甫谧',
    historicalPeriod: '西晋',
    description: '皇甫谧所撰高士传记。客户资料含《高士传》中华书局 1985 年版。',
    editionCount: 1,
    href: '/archive',
    note: '版本资料见数字档案',
    status: 'METADATA_ONLY',
    kind: 'compilation',
  },
  {
    id: 'w-sandufu',
    title: '《三都赋》序',
    workType: '序文',
    attribution: '皇甫谧（为左思《三都赋》作序）',
    historicalPeriod: '西晋',
    description: '皇甫谧为左思《三都赋》所作序言，是皇甫谧文学思想代表文献。',
    href: '/yan',
    note: '见其言',
    status: 'AVAILABLE',
    kind: 'essay',
  },
  {
    id: 'w-xuanshou',
    title: '《玄守论》',
    workType: '论说',
    attribution: '皇甫谧',
    historicalPeriod: '西晋',
    description: '安贫乐道、拒绝出仕的论说文，反映魏晋隐逸思潮。',
    href: '/yan',
    note: '见其言',
    status: 'AVAILABLE',
    kind: 'essay',
  },
  {
    id: 'w-shiquan',
    title: '《释劝论》',
    workType: '论说',
    attribution: '皇甫谧',
    historicalPeriod: '西晋',
    description: '申明不愿赴官立场，辨析出仕与隐居，研究皇甫谧处世思想的核心文本。',
    href: '/yan',
    note: '见其言',
    status: 'AVAILABLE',
    kind: 'essay',
  },
  {
    id: 'w-duzhong',
    title: '《笃终论》',
    workType: '论说',
    attribution: '皇甫谧',
    historicalPeriod: '西晋',
    description: '薄葬思想名篇，主张简约丧葬，体现魏晋生死观。',
    href: '/yan',
    note: '见其言',
    status: 'AVAILABLE',
    kind: 'essay',
  },
  {
    id: 'w-houlun',
    title: '后论（历史评价）',
    workType: '后世论述',
    attribution: '后世学者（整理中）',
    historicalPeriod: '—',
    description: '后世对皇甫谧的论述与历史评价（客户资料：后论）。',
    href: '/archive',
    note: '整理中，见数字档案',
    status: 'METADATA_ONLY',
    kind: 'related-material',
  },
]

/** 论著来源名（公共展示）。 */
export const WORK_SOURCE_NAME = YAN_SOURCE_NAME.replace('：其言文稿（docx）', '：其言/论著资料')

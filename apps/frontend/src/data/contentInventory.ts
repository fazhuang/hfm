/**
 * contentInventory — single view-model source for audited content counts
 * (UI-06). Counts originate from the audited customer material register
 * (hfmzl/) and the UI-08 edition collection; other pages consume them here
 * instead of hardcoding divergent numbers.
 */
import {
  JIAYI_ANCIENT_EDITIONS,
  JIAYI_LUNWEN_FILE_COUNT,
  JIAYI_LUNZHU_FILE_COUNT,
  JIAYI_MODERN_EDITIONS,
} from './jiayiView'

/** 论著文件数（客户目录审计；源头 jiayiView） */
export const INVENTORY_LUNZHU_FILES = JIAYI_LUNZHU_FILE_COUNT

/** 学术论文数（客户目录审计；源头 jiayiView） */
export const INVENTORY_LUNWEN_FILES = JIAYI_LUNWEN_FILE_COUNT

/** 版本记录数（UI-08 编辑集合：古代 + 近现代整理） */
export const INVENTORY_EDITION_RECORDS =
  JIAYI_ANCIENT_EDITIONS.length + JIAYI_MODERN_EDITIONS.length

/** 影视资料数（客户目录审计：皇甫谧一.mpg、《针灸鼻祖皇甫谧》第 1 集） */
export const INVENTORY_MOVIES = 2

/** 人物文稿 docx 数（其传 / 其言 / 后论） */
export const INVENTORY_HFM_DOCX = 3

/** 版本脉络图（客户 PNG，web 派生展示） */
export const INVENTORY_LINEAGE_PNG = 1

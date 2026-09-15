/**
 * 门户两个陈列段的数据完整性（P-5 影印 / P-6 非遗陈列）。
 *
 * 这两份数据是从生产库导出的，最容易出的错是**同一件东西出现两次**、
 * 或者**列出了没有发布的东西**。两条都钉在这里。
 */

import { describe, expect, it } from 'vitest'

import { JIAYI_IMPRINTS } from '../data/jiayiImprints'
import { HERITAGE_COLLECTION } from '../data/heritageCollection'

describe('P-5 原刻影印', () => {
  it('四个公版版本齐备', () => {
    expect(JIAYI_IMPRINTS.map((e) => e.edition)).toEqual([
      '针灸甲乙经》四库全书本清乾隆',
      '针灸甲乙经》医统正脉全书明万历29年吴勉学（1601）',
      '甲乙经》五车楼藏板（明万历吴勉学）',
      '甲乙经》行素草堂藏板清光绪',
    ])
  })

  it('共 21 件，与去重后的实测一致', () => {
    const total = JIAYI_IMPRINTS.reduce((n, e) => n + e.imprints.length, 0)
    expect(total).toBe(21)
  })

  it('媒体 id 不重复', () => {
    const ids = JIAYI_IMPRINTS.flatMap((e) => e.imprints.map((i) => i.id))
    expect(new Set(ids).size).toBe(ids.length)
  })

  it('同一版本内卷次按数字序，且标签已去掉版本名与重复标记', () => {
    const four = JIAYI_IMPRINTS[0].imprints.map((i) => i.label)
    expect(four).toEqual(['卷一', '卷二', '卷三', '卷四五', '卷六', '卷七', '卷八九', '卷十至十二'])
    for (const edition of JIAYI_IMPRINTS) {
      for (const imprint of edition.imprints) {
        // 标签不该再带版本名，也不该带「(2)」这类重复副本标记。
        expect(imprint.label).not.toContain('藏板')
        expect(imprint.label).not.toContain('全书本')
        expect(imprint.label).not.toMatch(/\(\d+\)/)
        // 台账原名必须保留，供逐件核对。
        expect(imprint.filename.endsWith('.pdf')).toBe(true)
      }
    }
  })
})

describe('P-6 非遗成果陈列', () => {
  it('四类齐备，共 28 件（只含已发布者）', () => {
    expect(HERITAGE_COLLECTION.map((g) => g.category)).toEqual([
      '05 技术成果',
      '06 媒体报道',
      '07 带徒传技与工作室成果',
      '10场地及设施设备',
    ])
    expect(HERITAGE_COLLECTION.reduce((n, g) => n + g.items.length, 0)).toBe(28)
  })

  it('媒体 id 不重复', () => {
    const ids = HERITAGE_COLLECTION.flatMap((g) => g.items.map((i) => i.id))
    expect(new Set(ids).size).toBe(ids.length)
  })

  it('每件都有封面路径；非 PDF 以类型标签代替', () => {
    for (const group of HERITAGE_COLLECTION) {
      for (const item of group.items) {
        expect(item.cover, item.name).toMatch(/^\/assets\/heritage\/.+\.jpg$/)
        expect(['pdf', 'docx', 'doc']).toContain(item.kind)
      }
    }
  })

  it('每一类都有说明，不留空标题', () => {
    for (const group of HERITAGE_COLLECTION) {
      expect(group.note.length, group.category).toBeGreaterThan(8)
    }
  })
})

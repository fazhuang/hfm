/**
 * 后论四表的数据完整性（P-2）。
 *
 * 数据是从 docx 表格转出来的，最容易出的错是行列错位（合并单元格、空行、
 * 列数不齐）。这里把「每行与表头等长」「四表齐备」钉死；任何一条被删改、
 * 任何一行错位，立刻失败。
 */

import { describe, expect, it } from 'vitest'

import { HOURAN_SOURCE, HOURAN_TABLES } from '../data/houranTables'

/** P-2 转换时实测的行数（不含表头）。 */
const EXPECTED_ROWS: Record<string, number> = {
  'lun-qiren': 12,
  'yan-qiren': 8,
  'jiang-qiren': 13,
  'guan-qiming': 15,
}

const EXPECTED_LABELS = ['论其人', '演其人', '讲其人', '冠其名']

describe('后论四表', () => {
  it('四个类目齐备且顺序与客户文档一致', () => {
    expect(HOURAN_TABLES.map((t) => t.label)).toEqual(EXPECTED_LABELS)
  })

  it('每表行数与本轮转换一致', () => {
    for (const table of HOURAN_TABLES) {
      expect(table.rows.length, `${table.label} 行数`).toBe(EXPECTED_ROWS[table.id])
    }
  })

  it('每行与表头等长，没有错位或空缺行', () => {
    for (const table of HOURAN_TABLES) {
      expect(table.columns.length, `${table.label} 表头`).toBeGreaterThan(1)
      for (const [i, row] of table.rows.entries()) {
        expect(row.length, `${table.label} 第 ${i + 1} 行列数`).toBe(table.columns.length)
        // 首列是序号，末列是说明，这两列不该为空——空了说明表格解析吞了内容。
        expect(row[0].trim(), `${table.label} 第 ${i + 1} 行序号为空`).not.toBe('')
        expect(
          row[row.length - 1].trim(),
          `${table.label} 第 ${i + 1} 行末列为空`,
        ).not.toBe('')
      }
    }
  })

  it('标注了来源，未把客户材料说成平台自撰', () => {
    expect(HOURAN_SOURCE).toContain('客户提供')
  })

  it('保留原始评价文字与出处，未做改写', () => {
    // 抽两条带明确出处的，确认原话与评价者都在。
    const lun = HOURAN_TABLES.find((t) => t.id === 'lun-qiren')
    const sources = lun?.rows.map((r) => r[1]) ?? []
    expect(sources).toContain('晋武帝司马炎')
    expect(sources.some((s) => s.includes('《晋书》'))).toBe(true)
    // 至少有一条保留引号内的原文，而不是只留转述。
    expect(lun?.rows.some((r) => r[2].includes('“') && r[2].includes('”'))).toBe(true)
  })
})

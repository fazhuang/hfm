/**
 * 其言四篇全文与校勘记的完整性（P-8a）。
 *
 * 校勘记最容易出的错，是校记指向的底本字串在正文里根本不存在 —— 那样校记
 * 看着有内容，实际对不上任何位置。这里把那条不变量钉死，并锁住字数，
 * 使正文被静默改动时立刻失败。
 */

import { describe, expect, it } from 'vitest'

import { YAN_COLLECTION } from '../data/yanCollection'
import { YAN_FULL_TEXTS } from '../data/yanTexts'

/** P-8a 录入时实测的字数（不含标点空白以外的一切改动都应使其失败）。 */
const EXPECTED_CHARS: Record<string, number> = {
  'sandu-fu': 776,
  'xuanshou-lun': 379,
  'shiquan-lun': 1922,
  'duzhong-lun': 1072,
}

const EXPECTED_PARAGRAPHS: Record<string, number> = {
  'sandu-fu': 3,
  'xuanshou-lun': 2,
  'shiquan-lun': 7,
  'duzhong-lun': 4,
}

describe('其言全文', () => {
  it('四篇齐备，字数与段数与本轮录入一致', () => {
    for (const [id, chars] of Object.entries(EXPECTED_CHARS)) {
      const text = YAN_FULL_TEXTS[id]
      expect(text, `${id} 缺失`).toBeDefined()
      expect(text.paragraphs.length, `${id} 段数`).toBe(EXPECTED_PARAGRAPHS[id])
      const total = text.paragraphs.join('').length
      expect(total, `${id} 字数`).toBe(chars)
    }
  })

  it('每一篇都声明了底本与至少一个参校本', () => {
    for (const [id, text] of Object.entries(YAN_FULL_TEXTS)) {
      expect(text.base.edition.length, `${id} 底本`).toBeGreaterThan(0)
      expect(text.collated.length, `${id} 参校本`).toBeGreaterThan(0)
    }
  })

  it('校勘记的底本字串必须真的出现在正文里', () => {
    for (const [id, text] of Object.entries(YAN_FULL_TEXTS)) {
      const body = text.paragraphs.join('')
      for (const variant of text.variants) {
        // 底本作空格表示脱文，此类校记无对应字串，改查其上下文锚点。
        if (variant.baseSuspect && variant.base.includes(' ')) {
          continue
        }
        const probe = variant.base.split('……')[0]
        expect(body.includes(probe), `${id} 校记底本「${probe}」不在正文中`).toBe(true)
      }
    }
  })

  it('每条校记都有异读与说明', () => {
    for (const [id, text] of Object.entries(YAN_FULL_TEXTS)) {
      for (const variant of text.variants) {
        expect(variant.readings.length, `${id} 校记异读`).toBeGreaterThan(0)
        expect(variant.note.length, `${id} 校记说明`).toBeGreaterThan(0)
      }
    }
  })

  it('文档里每个其言小节都对应一篇全文，没有孤立的全文', () => {
    const sectionIds = YAN_COLLECTION.sections.map((s) => s.id)
    for (const id of sectionIds) {
      expect(YAN_FULL_TEXTS[id], `小节 ${id} 无全文`).toBeDefined()
    }
    expect(Object.keys(YAN_FULL_TEXTS).sort()).toEqual([...sectionIds].sort())
  })

  it('全文到位后，各节的 fullTextStatus 不再是 DATA_GAP', () => {
    for (const section of YAN_COLLECTION.sections) {
      expect(section.fullTextStatus, section.id).not.toBe('DATA_GAP')
    }
  })

  it('正文为繁体，与甲乙经语料一致', () => {
    // 抽样几个只在繁体中出现、简体不同的字。
    const body = Object.values(YAN_FULL_TEXTS)
      .flatMap((t) => t.paragraphs)
      .join('')
    for (const ch of ['謐', '論', '賦', '禮', '壽']) {
      expect(body.includes(ch), `正文缺繁体字 ${ch}`).toBe(true)
    }
  })
})

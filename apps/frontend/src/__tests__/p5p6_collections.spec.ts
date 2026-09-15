/**
 * 门户两个陈列段的前端规则（P-5 影印 / P-6 非遗陈列）。
 *
 * 件目清单已改为**从公开接口现取**，不再固化在前端 —— 固化会让已下架的件
 * 仍以名称出现在页面上。所以这里测的是**留在前端的纯规则**：卷次怎么解析、
 * 怎么排序、版本怎么归、封面怎么查。
 *
 * 这些规则错一个，页面就会把「卷四五」排到「卷六」后面、或者把某件挂错封面 ——
 * 都是看不出来但确实错的结果。
 */

import { describe, expect, it } from 'vitest'

import {
  JIAYI_EDITIONS,
  editionOf,
  volumeLabel,
  volumeOrder,
} from '../data/jiayiImprints'
import {
  HERITAGE_CATEGORY_NOTES,
  HERITAGE_COVERS,
  HERITAGE_ROOT,
  heritageCategory,
  heritageKind,
} from '../data/heritageCollection'

describe('P-5 影印：卷次解析', () => {
  it('版本齐备且顺序固定', () => {
    expect(JIAYI_EDITIONS.map((e) => e.era)).toEqual([
      '清·乾隆',
      '明·万历二十九年（1601）',
      '明·万历',
      '清·光绪',
    ])
  })

  it('「卷四五」是第 4 卷，不是第 45 卷', () => {
    expect(volumeOrder('卷四五')).toBe(4)
    expect(volumeOrder('卷一二')).toBe(1)
    expect(volumeOrder('卷三四')).toBe(3)
    expect(volumeOrder('卷八九')).toBe(8)
  })

  it('「卷十至十二」从第 10 卷起算', () => {
    expect(volumeOrder('卷十至十二')).toBe(10)
    expect(volumeOrder('卷五-七')).toBe(5)
  })

  it('册次用数字排', () => {
    expect(volumeOrder('第1册')).toBe(1)
    expect(volumeOrder('第10册')).toBe(10)
  })

  it('四库全书本的卷次按数字序 —— 字符串序会把卷十排到卷三前面', () => {
    const labels = ['卷一', '卷二', '卷三', '卷四五', '卷六', '卷七', '卷八九', '卷十至十二']
    expect([...labels].sort((a, b) => volumeOrder(a) - volumeOrder(b))).toEqual(labels)
  })

  it('由 object_key 归入正确版本，非本族返回 undefined', () => {
    const key = '针灸甲乙经/论著/《针灸甲乙经》四库全书本清乾隆/《针灸甲乙经》四库全书本卷一.pdf'
    expect(editionOf(key)?.era).toBe('清·乾隆')
    expect(editionOf('针灸甲乙经/论文/针灸甲乙经/19-神志病治疗思路浅析.pdf')).toBeUndefined()
    expect(editionOf('非遗佐证/06 媒体报道/1、xxx.pdf')).toBeUndefined()
  })

  it('卷次标签去掉版本名与重复副本标记', () => {
    const folder = '《针灸甲乙经》四库全书本清乾隆'
    expect(
      volumeLabel(`针灸甲乙经/论著/${folder}/《针灸甲乙经》四库全书本卷一.pdf`, folder),
    ).toBe('卷一')
    // 台账里「卷十至十二」有两份逐字节相同的文件，第二份带 (2)。
    // 两份必须解析出**同一个标签**，页面才能据此去重。
    const a = volumeLabel(`针灸甲乙经/论著/${folder}/《针灸甲乙经》四库全书本卷十至十二.pdf`, folder)
    const b = volumeLabel(
      `针灸甲乙经/论著/${folder}/《针灸甲乙经》四库全书本卷十至十二 (2).pdf`,
      folder,
    )
    expect(a).toBe(b)
    expect(a).toBe('卷十至十二')
  })

  it('册次标签统一为「第N册」', () => {
    const folder = '《针灸甲乙经》医统正脉全书明万历29年吴勉学（1601）'
    expect(volumeLabel(`x/${folder}/《针灸甲乙经》医统正脉全书3.pdf`, folder)).toBe('第3册')
  })
})

describe('P-6 非遗陈列：查表与判别', () => {
  it('封面查表的键是媒体 id，值是 public 下的 jpg 路径', () => {
    const entries = Object.entries(HERITAGE_COVERS)
    expect(entries.length).toBeGreaterThan(20)
    for (const [id, cover] of entries) {
      expect(id).toMatch(/^[0-9a-f-]{36}$/)
      expect(cover).toMatch(/^\/assets\/heritage\/[0-9a-f-]{36}\.jpg$/)
      // 键与值是同一件东西 —— 挂错封面看不出来，但确实错。
      expect(cover).toContain(id)
    }
  })

  it('每个类目都有说明，不留空标题', () => {
    expect(Object.keys(HERITAGE_CATEGORY_NOTES).length).toBe(4)
    for (const [category, note] of Object.entries(HERITAGE_CATEGORY_NOTES)) {
      expect(note.length, category).toBeGreaterThan(8)
    }
  })

  it('陈列只收非遗佐证一族', () => {
    expect(HERITAGE_ROOT).toBe('非遗佐证/')
    expect(
      '非遗佐证/06 媒体报道/1、协助中央广播电视台华语环球节目纪录片部拍摄《杏林繁华》工作方案.pdf'.startsWith(
        HERITAGE_ROOT,
      ),
    ).toBe(true)
    // 研究侧的论文不属于这一族，不该进陈列。
    expect('针灸甲乙经/论文/针灸甲乙经/19-神志病治疗思路浅析.pdf'.startsWith(HERITAGE_ROOT)).toBe(false)
  })

  it('由 object_key 取类目名', () => {
    expect(heritageCategory('非遗佐证/05 技术成果/1、市级科研成果奖证书复印件/刘君奇 科研列表.docx')).toBe(
      '05 技术成果',
    )
    expect(heritageCategory('非遗佐证/10场地及设施设备/场地及设施设备.pdf')).toBe('10场地及设施设备')
    expect(heritageCategory('没有斜杠')).toBe('')
  })

  it('展示类型由 mime 与扩展名共同判定', () => {
    expect(heritageKind('application/pdf', 'a.pdf')).toBe('pdf')
    expect(
      heritageKind('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'a.docx'),
    ).toBe('docx')
    expect(heritageKind('application/msword', 'a.doc')).toBe('doc')
    // .doc 的 mime 与扩展名都要能兜住
    expect(heritageKind('application/octet-stream', 'a.doc')).toBe('doc')
  })
})

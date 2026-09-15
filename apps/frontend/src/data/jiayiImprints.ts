/**
 * 《针灸甲乙经》原刻影印 — 四种公版版本（P-5）
 *
 * 来源：客户提供 `hfmzl/针灸甲乙经/论著/` 下的公版原刻/抄本影印，已登记为
 * 公开媒体资产（`access_scope='public'`、`publication_state='published'`）。
 *
 * 这是**当代读者能看到的最接近原书的东西**：明万历吴勉学的刻本、清乾隆的
 * 四库全书本、清光绪的行素草堂藏板。分组名沿用客户台账的目录名；`filename`
 * 保留台账原名以便逐件核对，`label` 只作阅读用的卷次标记。
 *
 * **去重**：客户台账里「四库全书本卷十至十二」有两份逐字节相同的文件
 * （sha256 与字节数完全一致，`01a099de-360b…` 与 `01a099de-367e…`）。
 * 同一份内容按两卷展示会让人误以为有两种东西，故只保留一条。两行都仍留在
 * 数据库里、都仍可通过公开接口访问，这里只是不在页面上重复列出。
 *
 * 阅读方式：`/api/v1/public/media/{id}/bytes` 交给浏览器原生 PDF 查看器，
 * 不引入 PDF 渲染库（见执行规划 §3.3）。
 *
 * **件目清单不在这里。**与非遗陈列同理：哪些件能公开是随发布状态变的，
 * 写死在前端会让下架的件仍以名称出现在页面上。本文件只留**不随发布状态变**
 * 的两样 —— 四个版本的编辑说明，以及由台账文件名推导卷次标记的规则。
 */
export interface JiayiEditionMeta {
  /** 台账目录名。既是展示名，也是匹配 object_key 的键。 */
  folder: string
  /** 时代。 */
  era: string
  /** 一句话说明。 */
  note: string
}

/** 四个公版版本。顺序即页面顺序：官修本在前，刻本按年代。 */
export const JIAYI_EDITIONS: readonly JiayiEditionMeta[] = [
  {
    folder: '《针灸甲乙经》四库全书本清乾隆',
    era: '清·乾隆',
    note: '清乾隆间《四库全书》所收本，九卷，是现存最通行的官修本之一。',
  },
  {
    folder: '《针灸甲乙经》医统正脉全书明万历29年吴勉学（1601）',
    era: '明·万历二十九年（1601）',
    note: '明万历吴勉学辑刻《医统正脉全书》所收本，五册，为现存较早的刻本。',
  },
  {
    folder: '《甲乙经》五车楼藏板（明万历吴勉学）',
    era: '明·万历',
    note: '明万历五车楼藏板本，四册，与医统正脉同出吴勉学一系，可对照两刻异同。',
  },
  {
    folder: '《甲乙经》行素草堂藏板清光绪',
    era: '清·光绪',
    note: '清光绪行素草堂藏板本，四册，按卷装订。',
  },
]

const _CN: Record<string, number> = {
  一: 1, 二: 2, 三: 3, 四: 4, 五: 5, 六: 6, 七: 7, 八: 8, 九: 9, 十: 10,
}

function _cnToNum(s: string): number {
  if (!s) return 0
  if (s === '十') return 10
  if (s.includes('十')) {
    const [a, b] = s.split('十')
    return (a ? (_CN[a] ?? 1) : 1) * 10 + (b ? (_CN[b] ?? 0) : 0)
  }
  return _CN[s] ?? 99
}

/**
 * 卷次排序键。取「卷」后**首个**卷号 —— 「卷四五」是第 4 卷不是第 45 卷，
 * 按字符串排会全乱。
 */
export function volumeOrder(label: string): number {
  const m = /卷([一二三四五六七八九十]+)/.exec(label)
  if (m) {
    const s = m[1]
    if (s.includes('十')) return _cnToNum(s.split('至')[0])
    return _CN[s[0]] ?? 99
  }
  const digits = /(\d+)/.exec(label)
  return digits ? Number(digits[1]) : 99
}

/** 由 object_key 找出所属版本；不属于四个公版版本则返回 undefined。 */
export function editionOf(objectKey: string): JiayiEditionMeta | undefined {
  return JIAYI_EDITIONS.find((e) => objectKey.includes(e.folder))
}

/**
 * 由台账文件名推导卷次标记 —— 「卷一」「第2册」。
 * 版本名与重复副本的「(2)」标记一并去掉：版本已是独立字段，重复副本不另立一条。
 */
export function volumeLabel(objectKey: string, folder: string): string {
  let stem = objectKey.split('/').pop() ?? objectKey
  stem = stem.replace(/\.pdf$/i, '')
  for (const p of ['《针灸甲乙经》', '《甲乙经》']) stem = stem.replace(p, '')
  stem = stem.replace(folder.replace(/^《|》$/g, ''), '').trim()
  // 目录名带时代（如「清乾隆」），文件名常常不带，故再按关键词兜一次。
  stem = stem.replace(/^(四库全书本|医统正脉全书|五车楼藏板|行素草堂藏板清光绪)/, '').trim()
  stem = stem.replace(/\s*\(\d+\)\s*$/, '').trim()
  return /^\d+$/.test(stem) ? `第${stem}册` : stem
}

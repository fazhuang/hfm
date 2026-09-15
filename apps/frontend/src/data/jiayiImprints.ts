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
 */
export interface JiayiImprint {
  /** 媒体资产 id。 */
  id: string
  /** 卷次/册次标记，如「卷一」「第2册」。 */
  label: string
  /** 客户台账文件名，用于与源目录逐件核对。 */
  filename: string
}

export interface JiayiImprintEdition {
  /** 版本名，取自客户台账的目录名。 */
  edition: string
  /** 时代。 */
  era: string
  /** 一句话说明。 */
  note: string
  imprints: readonly JiayiImprint[]
}

export const JIAYI_IMPRINTS: readonly JiayiImprintEdition[] = [
  {
    edition: '针灸甲乙经》四库全书本清乾隆',
    era: '清·乾隆',
    note: '清乾隆间《四库全书》所收本，九卷，是现存最通行的官修本之一。',
    imprints: [
      { id: '01a099de-3400-7bc0-8b44-c7130a7bc2ef', label: '卷一', filename: '《针灸甲乙经》四库全书本卷一.pdf' },
      { id: '01a099de-34f7-7a52-a36d-8f3160d01448', label: '卷二', filename: '《针灸甲乙经》四库全书本卷二.pdf' },
      { id: '01a099de-34a8-77e9-8ce1-d6ee936963c8', label: '卷三', filename: '《针灸甲乙经》四库全书本卷三.pdf' },
      { id: '01a099de-36f1-7117-9ab9-fa658f46cf39', label: '卷四五', filename: '《针灸甲乙经》四库全书本卷四五.pdf' },
      { id: '01a099de-3596-7ca7-a130-a3bebf1b0b51', label: '卷六', filename: '《针灸甲乙经》四库全书本卷六.pdf' },
      { id: '01a099de-3443-7832-a3ca-5f87e7aff471', label: '卷七', filename: '《针灸甲乙经》四库全书本卷七.pdf' },
      { id: '01a099de-3553-77fc-8602-1d0d90f431c6', label: '卷八九', filename: '《针灸甲乙经》四库全书本卷八九.pdf' },
      { id: '01a099de-360b-7618-87dc-4b22deee0634', label: '卷十至十二', filename: '《针灸甲乙经》四库全书本卷十至十二 (2).pdf' },
    ],
  },
  {
    edition: '针灸甲乙经》医统正脉全书明万历29年吴勉学（1601）',
    era: '明·万历二十九年（1601）',
    note: '明万历吴勉学辑刻《医统正脉全书》所收本，五册，为现存较早的刻本。',
    imprints: [
      { id: '01a099de-31a9-7707-ad16-0c587c14bcd1', label: '第1册', filename: '《针灸甲乙经》医统正脉全书1.pdf' },
      { id: '01a099de-3237-7db5-a674-44aaa3af6ce5', label: '第2册', filename: '《针灸甲乙经》医统正脉全书2.pdf' },
      { id: '01a099de-32a8-7722-956b-1b6cb17b8cfa', label: '第3册', filename: '《针灸甲乙经》医统正脉全书3.pdf' },
      { id: '01a099de-333a-74cd-870d-fd1a8d1e35cb', label: '第4册', filename: '《针灸甲乙经》医统正脉全书4.pdf' },
      { id: '01a099de-33ac-73b1-be8b-311eeb187f84', label: '第5册', filename: '《针灸甲乙经》医统正脉全书5.pdf' },
    ],
  },
  {
    edition: '甲乙经》五车楼藏板（明万历吴勉学）',
    era: '明·万历',
    note: '明万历五车楼藏板本，四册，与医统正脉同出吴勉学一系，可对照两刻异同。',
    imprints: [
      { id: '01a099de-2e3c-7845-b748-e6413bdae840', label: '第1册', filename: '《甲乙经》五车楼藏板1.pdf' },
      { id: '01a099de-2b1c-74ef-b64c-61e93885e486', label: '第2册', filename: '《甲乙经》五车楼藏板 2.pdf' },
      { id: '01a099de-2c37-78c7-a8b2-c5f9a2d02515', label: '第3册', filename: '《甲乙经》五车楼藏板 3.pdf' },
      { id: '01a099de-2d36-74fd-803e-57629e8d1c46', label: '第4册', filename: '《甲乙经》五车楼藏板 4.pdf' },
    ],
  },
  {
    edition: '甲乙经》行素草堂藏板清光绪',
    era: '清·光绪',
    note: '清光绪行素草堂藏板本，四册，按卷装订。',
    imprints: [
      { id: '01a099de-2eb0-72a2-aa43-47730ef24986', label: '卷一二', filename: '《甲乙经》行素草堂藏板清光绪卷一二.pdf' },
      { id: '01a099de-2f1e-76ea-b8de-6cc147c48f9a', label: '卷三四', filename: '《甲乙经》行素草堂藏板清光绪卷三四.pdf' },
      { id: '01a099de-2faa-7398-ac1e-69418d13a94e', label: '卷五-七', filename: '《甲乙经》行素草堂藏板清光绪卷五-七.pdf' },
      { id: '01a099de-303d-768a-a135-2c170aadf20e', label: '卷八-十二', filename: '《甲乙经》行素草堂藏板清光绪卷八-十二.pdf' },
    ],
  },
]

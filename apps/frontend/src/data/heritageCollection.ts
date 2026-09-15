/**
 * 非遗传承成果 — 公众门户陈列（P-6）
 *
 * 来源：客户提供 `hfmzl/非遗佐证/`，其中分级为 P1 的部分已发布
 * （`access_scope='public'`、`publication_state='published'`），本文件逐件对应。
 *
 * **只收已发布的 28 件。**P2 35 件与 P3 4 件仍在库中保持 draft，不在本文件内 ——
 * 页面陈列的是能公开的东西，不是"客户给过的全部东西"。
 *
 * 封面：由每件 PDF 的首页渲染为 JPEG（420px 宽，q82，共约 900 KB），存放于
 * `public/assets/heritage/`。`.docx` / `.doc` 无封面，以类型标签代替 —— 浏览器
 * 本来也不内嵌显示这两种格式。
 *
 * 原件不经任何改动；页面只读取公开媒体接口
 * `/api/v1/public/media/{id}/bytes`。
 */
export type HeritageKind = 'pdf' | 'docx' | 'doc'

export interface HeritageItem {
  /** 媒体资产 id。 */
  id: string
  /** 台账文件名。 */
  name: string
  kind: HeritageKind
  /** 封面路径（仅 PDF 有）。 */
  cover: string
}

export interface HeritageGroup {
  category: string
  note: string
  items: readonly HeritageItem[]
}

export const HERITAGE_COLLECTION: readonly HeritageGroup[] = [
  {
    category: '05 技术成果',
    note: '科研获奖、发表论文与课题立项结题材料 —— 传承人的学术成果本身。',
    items: [
      {
        id: '01a099de-62d9-745e-9564-2825587c1a23',
        name: '刘君奇 科研列表.docx',
        kind: 'docx',
        cover: '/assets/heritage/01a099de-62d9-745e-9564-2825587c1a23.jpg',
      },
      {
        id: '01a099de-632a-7a17-a8b7-8579885f9794',
        name: '刘君奇发表论文清单.docx',
        kind: 'docx',
        cover: '/assets/heritage/01a099de-632a-7a17-a8b7-8579885f9794.jpg',
      },
      {
        id: '01a099de-6313-734a-85c6-5ef810edde32',
        name: '（封面）中药外敷联合针刺治疗膝关节骨性关节炎的临床疗效及对关节疼痛的影响.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-6313-734a-85c6-5ef810edde32.jpg',
      },
      {
        id: '01a099de-6318-7eb0-b0a7-b8a67d0c3e91',
        name: '（正文）中药外敷联合针刺治疗膝关节骨性关节炎的临床疗效及对关节疼痛的影响.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-6318-7eb0-b0a7-b8a67d0c3e91.jpg',
      },
      {
        id: '01a099de-631e-7f47-9ff6-4c43083ca78a',
        name: '（目录）中药外敷联合针刺治疗膝关节骨性关节炎的临床疗效及对关节疼痛的影响.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-631e-7f47-9ff6-4c43083ca78a.jpg',
      },
      {
        id: '01a099de-6327-7b99-b839-263e65e3d02d',
        name: '（首页）中药外敷联合针刺治疗膝关节骨性关节炎的临床疗效及对关节疼痛的影响.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-6327-7b99-b839-263e65e3d02d.jpg',
      },
      {
        id: '01a099de-6331-7551-9967-31fcd1011fad',
        name: '封面.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-6331-7551-9967-31fcd1011fad.jpg',
      },
      {
        id: '01a099de-6366-7c77-8cb7-b30366e4cbff',
        name: '目录.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-6366-7c77-8cb7-b30366e4cbff.jpg',
      },
      {
        id: '01a099de-636c-7681-bd0b-7c8056153f18',
        name: '首页.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-636c-7681-bd0b-7c8056153f18.jpg',
      },
      {
        id: '01a099de-6339-7d9d-9c36-c4eb23888e94',
        name: '正文1.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-6339-7d9d-9c36-c4eb23888e94.jpg',
      },
      {
        id: '01a099de-6341-76e3-9d88-c2b5868dc27e',
        name: '正文2.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-6341-76e3-9d88-c2b5868dc27e.jpg',
      },
      {
        id: '01a099de-6349-7f83-9962-3ece62705c60',
        name: '正文3.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-6349-7f83-9962-3ece62705c60.jpg',
      },
      {
        id: '01a099de-6351-7fe4-bbe8-22354f3a13ff',
        name: '正文4.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-6351-7fe4-bbe8-22354f3a13ff.jpg',
      },
      {
        id: '01a099de-6357-74fe-89de-7a8416f53e1c',
        name: '正文5.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-6357-74fe-89de-7a8416f53e1c.jpg',
      },
      {
        id: '01a099de-635e-73d2-a38d-ca39507aeaad',
        name: '正文6.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-635e-73d2-a38d-ca39507aeaad.jpg',
      },
    ],
  },
  {
    category: '06 媒体报道',
    note: '央视、甘肃卫视等媒体对皇甫谧针灸的报道与拍摄证明。',
    items: [
      {
        id: '01a099de-6380-7ec9-a769-ac6e8051fb32',
        name: '1、协助中央广播电视台华语环球节目纪录片部拍摄《杏林繁华》工作方案.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-6380-7ec9-a769-ac6e8051fb32.jpg',
      },
      {
        id: '01a099de-6383-75b4-8932-3fb563a12d78',
        name: '2、央视《魅力中国城》栏目参与证明材料.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-6383-75b4-8932-3fb563a12d78.jpg',
      },
      {
        id: '01a099de-6387-7a42-b223-66d0768a3d24',
        name: '崆峒区.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-6387-7a42-b223-66d0768a3d24.jpg',
      },
      {
        id: '01a099de-638a-73c0-a18e-55147882fbd3',
        name: '灵台县.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-638a-73c0-a18e-55147882fbd3.jpg',
      },
      {
        id: '01a099de-638d-7c8a-aa76-d076a39537e1',
        name: '甘肃卫视.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-638d-7c8a-aa76-d076a39537e1.jpg',
      },
      {
        id: '01a099de-6391-7310-87cc-6d742ba939d3',
        name: '甘肃卫视等栏目宣传报道截图或链接.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-6391-7310-87cc-6d742ba939d3.jpg',
      },
      {
        id: '01a099de-6395-7ef6-b285-8be789353ccf',
        name: '静宁县.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-6395-7ef6-b285-8be789353ccf.jpg',
      },
      {
        id: '01a099de-6399-7bfd-895a-fe105128b96f',
        name: '中央电视台拍摄函.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-6399-7bfd-895a-fe105128b96f.jpg',
      },
      {
        id: '01a099de-639b-70e1-8c69-d1ce59c97a51',
        name: '央视图片证明材料.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-639b-70e1-8c69-d1ce59c97a51.jpg',
      },
    ],
  },
  {
    category: '07 带徒传技与工作室成果',
    note: '名中医工作室、师承教育拜山的制度与教学材料。',
    items: [
      {
        id: '01a099de-63cf-792c-bd11-96f1e5d380db',
        name: '师承教育教学大纲.doc',
        kind: 'doc',
        cover: '/assets/heritage/01a099de-63cf-792c-bd11-96f1e5d380db.jpg',
      },
      {
        id: '01a099de-63d2-7a0d-9166-c88ca2e39170',
        name: '师承教育讲座(3).docx',
        kind: 'docx',
        cover: '/assets/heritage/01a099de-63d2-7a0d-9166-c88ca2e39170.jpg',
      },
      {
        id: '01a099de-63d4-788a-bf55-0dc50dc94f4b',
        name: '皇甫谧针灸学院中医师承制教学实施办法(3).docx',
        kind: 'docx',
        cover: '/assets/heritage/01a099de-63d4-788a-bf55-0dc50dc94f4b.jpg',
      },
    ],
  },
  {
    category: '10场地及设施设备',
    note: '传习场所与设施设备的影像记录。',
    items: [
      {
        id: '01a099de-6401-742f-9852-928105059f04',
        name: '场地及设施设备.pdf',
        kind: 'pdf',
        cover: '/assets/heritage/01a099de-6401-742f-9852-928105059f04.jpg',
      },
    ],
  },
]

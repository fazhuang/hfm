/**
 * 非遗传承 — 类别说明与封面查表（P-6）
 *
 * **清单本身不在这里。**陈列的件目由 `HeritageView` 从公开接口
 * `GET /api/v1/public/media` 现取 —— 因为"哪些能公开"是随发布状态变的，
 * 写死在前端会有一个后果：某件在库里被下架后，接口不再返回它，**但页面上
 * 它的名称和首页图还在**。那等于前端绕过了发布闸门（宪章 §2「受控资产层：
 * 通过公开 API 读取，受 access_scope 约束」）。
 *
 * 本文件只留两样**不随发布状态变**的东西：
 *
 * 1. `HERITAGE_CATEGORY_NOTES` —— 每个类目的编辑说明，属叙事层；
 * 2. `HERITAGE_COVERS` —— id 到封面图的查表。封面是 PDF 首页渲染出的静态
 *    文件（420px JPEG q82，存 `public/assets/heritage/`）。接口不返回缩略图，
 *    所以只能按 id 查；**查不到的件不显示图，退回类型标签** —— 新增的件
 *    不会是空白，也不会因此连带显示不该显示的东西。
 *
 * 已知残留：封面文件本身在构建产物里，被下架的件其封面仍可按 URL 取到。
 * 要彻底消除，需把封面也登记为媒体资产、经由接口下发（属生产写库，未做）。
 */
export type HeritageKind = 'pdf' | 'docx' | 'doc'

/** 台账目录名 → 该类目的编辑说明。 */
export const HERITAGE_CATEGORY_NOTES: Readonly<Record<string, string>> = {
  '05 技术成果': '科研获奖、发表论文与课题立项结题材料 —— 传承人的学术成果本身。',
  '06 媒体报道': '央视、甘肃卫视等媒体对皇甫谧针灸的报道与拍摄证明。',
  '07 带徒传技与工作室成果': '名中医工作室、师承教育拜山的制度与教学材料。',
  '10场地及设施设备': '传习场所与设施设备的影像记录。',
}

/** 媒体资产 id → 封面图路径。命中的才显示封面。 */
export const HERITAGE_COVERS: Readonly<Record<string, string>> = {
  '01a099de-62d9-745e-9564-2825587c1a23': '/assets/heritage/01a099de-62d9-745e-9564-2825587c1a23.jpg',
  '01a099de-632a-7a17-a8b7-8579885f9794': '/assets/heritage/01a099de-632a-7a17-a8b7-8579885f9794.jpg',
  '01a099de-6313-734a-85c6-5ef810edde32': '/assets/heritage/01a099de-6313-734a-85c6-5ef810edde32.jpg',
  '01a099de-6318-7eb0-b0a7-b8a67d0c3e91': '/assets/heritage/01a099de-6318-7eb0-b0a7-b8a67d0c3e91.jpg',
  '01a099de-631e-7f47-9ff6-4c43083ca78a': '/assets/heritage/01a099de-631e-7f47-9ff6-4c43083ca78a.jpg',
  '01a099de-6327-7b99-b839-263e65e3d02d': '/assets/heritage/01a099de-6327-7b99-b839-263e65e3d02d.jpg',
  '01a099de-6331-7551-9967-31fcd1011fad': '/assets/heritage/01a099de-6331-7551-9967-31fcd1011fad.jpg',
  '01a099de-6366-7c77-8cb7-b30366e4cbff': '/assets/heritage/01a099de-6366-7c77-8cb7-b30366e4cbff.jpg',
  '01a099de-636c-7681-bd0b-7c8056153f18': '/assets/heritage/01a099de-636c-7681-bd0b-7c8056153f18.jpg',
  '01a099de-6339-7d9d-9c36-c4eb23888e94': '/assets/heritage/01a099de-6339-7d9d-9c36-c4eb23888e94.jpg',
  '01a099de-6341-76e3-9d88-c2b5868dc27e': '/assets/heritage/01a099de-6341-76e3-9d88-c2b5868dc27e.jpg',
  '01a099de-6349-7f83-9962-3ece62705c60': '/assets/heritage/01a099de-6349-7f83-9962-3ece62705c60.jpg',
  '01a099de-6351-7fe4-bbe8-22354f3a13ff': '/assets/heritage/01a099de-6351-7fe4-bbe8-22354f3a13ff.jpg',
  '01a099de-6357-74fe-89de-7a8416f53e1c': '/assets/heritage/01a099de-6357-74fe-89de-7a8416f53e1c.jpg',
  '01a099de-635e-73d2-a38d-ca39507aeaad': '/assets/heritage/01a099de-635e-73d2-a38d-ca39507aeaad.jpg',
  '01a099de-6380-7ec9-a769-ac6e8051fb32': '/assets/heritage/01a099de-6380-7ec9-a769-ac6e8051fb32.jpg',
  '01a099de-6383-75b4-8932-3fb563a12d78': '/assets/heritage/01a099de-6383-75b4-8932-3fb563a12d78.jpg',
  '01a099de-6387-7a42-b223-66d0768a3d24': '/assets/heritage/01a099de-6387-7a42-b223-66d0768a3d24.jpg',
  '01a099de-638a-73c0-a18e-55147882fbd3': '/assets/heritage/01a099de-638a-73c0-a18e-55147882fbd3.jpg',
  '01a099de-638d-7c8a-aa76-d076a39537e1': '/assets/heritage/01a099de-638d-7c8a-aa76-d076a39537e1.jpg',
  '01a099de-6391-7310-87cc-6d742ba939d3': '/assets/heritage/01a099de-6391-7310-87cc-6d742ba939d3.jpg',
  '01a099de-6395-7ef6-b285-8be789353ccf': '/assets/heritage/01a099de-6395-7ef6-b285-8be789353ccf.jpg',
  '01a099de-6399-7bfd-895a-fe105128b96f': '/assets/heritage/01a099de-6399-7bfd-895a-fe105128b96f.jpg',
  '01a099de-639b-70e1-8c69-d1ce59c97a51': '/assets/heritage/01a099de-639b-70e1-8c69-d1ce59c97a51.jpg',
  '01a099de-63cf-792c-bd11-96f1e5d380db': '/assets/heritage/01a099de-63cf-792c-bd11-96f1e5d380db.jpg',
  '01a099de-63d2-7a0d-9166-c88ca2e39170': '/assets/heritage/01a099de-63d2-7a0d-9166-c88ca2e39170.jpg',
  '01a099de-63d4-788a-bf55-0dc50dc94f4b': '/assets/heritage/01a099de-63d4-788a-bf55-0dc50dc94f4b.jpg',
  '01a099de-6401-742f-9852-928105059f04': '/assets/heritage/01a099de-6401-742f-9852-928105059f04.jpg',
}

/** 由 mime type 与文件名判断展示类型。 */
export function heritageKind(mime: string, name: string): HeritageKind {
  if (mime === 'application/pdf') return 'pdf'
  if (name.toLowerCase().endsWith('.docx')) return 'docx'
  return 'doc'
}

/** 非遗佐证的台账根目录 —— 只有这一族的材料进本页陈列。 */
export const HERITAGE_ROOT = '非遗佐证/'

/** 从 object_key 取类目名（第二段）。 */
export function heritageCategory(objectKey: string): string {
  const parts = objectKey.split('/')
  return parts.length > 1 ? parts[1] : ''
}

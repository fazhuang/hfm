# HFM 设计资源参考与利用方案

状态：执行参考，不是新功能授权  
目标执行者：Pi  适用项目：HFM Vue 前端

## 1. 执行边界

截图中的链接仅作为设计资源推荐清单，不构成“安装依赖、复制代码、重做首页或替换设计系统”的指令。

本方案只允许：

- 参考页面结构、交互模式、动效节奏和字体/图标候选；
- 在现有 Vue 组件、路由、数据投影和 HFM tokens 上做最小增量；
- 先形成参考记录，再决定是否实现。

本方案不允许：

- 引入 React/Next.js 组件到 Vue 页面；
- 直接复制站点截图、商业模板、第三方页面代码或未审阅 SVG；
- 为一次视觉效果新增 UI 框架、动画库或图标库；
- 改写 HFM 的内容权威性、证据状态、路由和数据模型。

基线文件：

- `apps/frontend/src/views/HomeView.vue`
- `apps/frontend/src/components/home/HomeHeroSection.vue`
- `apps/frontend/src/styles/tokens.css`
- `apps/frontend/src/data/homeProjection.ts`

## 2. 资源分级

### A 级：优先使用

| 资源 | 地址 | 用法 | HFM 落点 |
| --- | --- | --- | --- |
| Component Gallery | <https://component.gallery/> | 查询真实设计系统中的组件行为、状态和命名；不复制整套实现 | 研究端 Table、Tree、Popover、Modal、Carousel；知识图谱节点详情 |
| 60fps | <https://60fps.design/> | 参考 Search、Scroll、Graph、Loading、Reveal、Tabs 等交互节奏 | 首页滚动提示、检索状态、研究端加载/展开、图谱过渡 |
| Landing Love | <https://www.landing.love/> | 参考 Hero、长页面节奏、图片与文字编排 | 首页八段叙事结构的视觉校准 |

### B 级：按需使用

| 资源 | 地址 | 用法 | 限制 |
| --- | --- | --- | --- |
| UNCUT | <https://uncut.wtf/> | 仅筛选英文字体或展示字体候选 | 必须确认中文覆盖、性能、字体许可；正文继续使用 HFM 中文字体栈 |
| Hugeicons | <https://github.com/hugeicons/hugeicons> | 只有在现有图标不足时，挑选少量免费图标 | 免费图标与 Pro 图标分开；不引入完整图标包，不使用 Pro 源文件 |
| Mobbin | <https://mobbin.com/> | 参考真实产品的搜索、阅读器、资料库和移动端流程 | 只作 UX 研究，不作为代码或资产来源 |
| Rebrand Gallery | <https://rebrand.gallery/> | 参考品牌识别、Logo、色彩和视觉语言 | 不替换 HFM“当代东方数字人文”方向 |

### C 级：仅作远期参考

| 资源 | 地址 | 原因 |
| --- | --- | --- |
| Curations Supply | <https://curations.supply/> | 设计资源目录，可继续发现资料，但不是运行时依赖 |
| SaaSPO | <https://saaspo.com/> | 适合 SaaS 营销、定价和产品页；只能参考研究端的信息组织，不适合作为 HFM 主视觉 |
| Sleek | <https://sleek.design/> | 可生成移动端概念稿，但主要输出面向 Figma/HTML/React，不直接并入 Vue |

## 3. Pi 执行顺序

### P0：只读勘察

1. 阅读 HFM 当前首页、研究端和 tokens 文件。
2. 从 A 级资源各选 3 个与 HFM 相关的模式，记录：
   - 使用场景；
   - 交互状态；
   - 可迁移到 Vue 的最小实现；
   - 与现有 HFM 组件的对应关系。
3. 不改代码、不安装依赖、不提交截图中的第三方素材。

产物：`docs/design/HFM-DESIGN-RESOURCE-REVIEW.md`。

### P1：选择一个最小试点

优先选择研究端的一个已有需求，例如：

- 搜索结果筛选状态；
- 证据链展开/收起；
- Tree/谱系节点详情；
- 加载、空态或错误态。

试点规则：

- 复用已有组件和 CSS tokens；
- 优先 CSS、原生 HTML 和 Vue 状态；
- 不新增 npm 依赖，除非现有实现确实无法满足需求；
- 保持键盘操作、焦点环、Escape、移动端触控和 reduced-motion。

### P2：实现与验证

Pi 只有在 P1 选定一个试点后才能改代码。实现后至少运行：

```bash
cd apps/frontend
npm run typecheck
npm run lint
npm run test
npm run build
```

涉及用户流程时，再运行对应 Playwright 测试，并记录桌面和移动视口结果。

### P3：独立复核

复核内容：

- 是否仍使用现有 HFM tokens，而非硬编码第二套颜色/间距/圆角；
- 是否新增了不必要依赖；
- 是否改变了既有路由、搜索行为、数据状态或权威内容；
- 是否满足键盘、对比度、reduced-motion 和窄屏布局；
- 是否能说明参考来源只是设计参考，而非未经审阅的第三方代码复制。

没有通过上述复核，不得称为已验收或可发布。

## 4. 推荐的最小试点

首个试点建议选“研究端证据链展开/收起”或“搜索结果筛选状态”，理由是：

- 与 Component Gallery、60fps 的参考类型直接匹配；
- 不需要新增页面、后端接口或数据库字段；
- 可以复用现有状态组件、tokens 和无障碍约束；
- 容易通过一个小范围浏览器测试证明行为没有回归。

不建议首个试点选择首页整体重做、字体全面替换、全局图标库迁移或新增动效框架。

## 5. Pi 输出格式

Pi 完成勘察或试点后，按以下格式汇报：

```text
资源：
参考页面/模式：
HFM 对应组件或路由：
是否新增依赖：否 / 是（名称与原因）
是否修改数据、路由或 API：否 / 是（说明）
实现文件：
验证命令：
验证结果：
已知限制：
```

结论只使用以下状态之一：`REFERENCE_ONLY`、`IMPLEMENTED_UNVERIFIED`、`IMPLEMENTED_VERIFIED`、`BLOCKED`。

## 6. 停止条件

遇到以下情况立即停止扩展范围并回报：

- 需要新增框架或大型第三方 UI 库；
- 需要修改后端、数据库、权限或内容权威性；
- 需要复制外部站点代码或下载未审阅资产；
- 现有 HFM 组件已经能满足需求；
- 视觉参考与可考证、克制、中文阅读优先的 HFM 方向冲突。

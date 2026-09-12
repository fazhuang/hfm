# HFM-HOMEPAGE-RUNTIME-MAP.md — 首页组件树与运行时数据流解构

## 1. 首页组件树 (`HomeView.vue`)

```text
HomeView.vue (Orchestrator, 拥有页面级搜索状态及路由跳转)
│
├── 01. HomeHeroSection.vue (Hero 横幅、平台定位与全局主检索框)
├── 02. HomeLifeSection.vue (皇甫谧生平纪年、四阶段轨迹与年谱图景)
├── 03. HomeBookSection.vue (《针灸甲乙经》一部书、传世版本与论著/论文概貌)
├── 04. HomeKnowledgeSection.vue (知识对象结构化拆解：卷/篇/穴位/条文/病候)
├── 05. HomeEvidenceSection.vue (史料证据链、名家品评引文与考据)
├── 06. HomeHeritageSection.vue (皇甫谧针灸术活态非遗、传承谱系与代表性名医)
├── 07. HomeDomainsSection.vue (六大核心领域研究导航卡片)
└── 08. HomeClosingSection.vue (学术机构声明、学术赞誉收尾)
```

---

## 2. 每个 Section 的真实数据源分析

| Section 编号与名称 | 组件文件 | 引入的数据模块 | 真实数据来源分类 | 是否直连后端 API |
|---|---|---|---|---|
| **01 Hero** | `HomeHeroSection.vue` | `homeProjection.HOME_HERO`, `config/corePerson.CORE_PERSON_DATES` | 静态数据 / 配置 | 否 |
| **02 一生** | `HomeLifeSection.vue` | `homeProjection.HOME_LIFE`, `homeProjection.HOME_CHAPTERS` | 静态数据 / Projection | 否 |
| **03 一部书** | `HomeBookSection.vue` | `homeProjection.HOME_BOOK`, `contentInventory.ts` (论著/论文文件数统计) | 静态资产盘点 / Projection | 否 |
| **04 知识对象** | `HomeKnowledgeSection.vue` | `homeProjection.HOME_KNOWLEDGE`, `HOME_RESEARCH_STEPS` | 静态数据 / 预设知识结构 | 否 |
| **05 史料证据** | `HomeEvidenceSection.vue` | `homeProjection.HOME_EVIDENCE`, `homeProjection.HOME_QUOTATION` | 静态典籍考据 Projection | 否 |
| **06 活态传承** | `HomeHeritageSection.vue` | `homeProjection.HOME_HERITAGE_LIVING`, `presentationStatusLabel` | 静态传承事实 / Projection | 否 |
| **07 研究导航** | `HomeDomainsSection.vue` | `homeProjection.HOME_DOMAINS` | 静态导航配置 | 否 |
| **08 机构收尾** | `HomeClosingSection.vue` | `homeProjection.HOME_CLOSING` | 静态文本 | 否 |

---

## 3. 首页数据来源量化事实

- **后端 API 驱动 Sections** (`API_BACKED_SECTIONS`): **0**
- **前端配置驱动 Sections** (`CONFIG_BACKED_SECTIONS`): **1** (Hero 引用了 `corePerson.ts`)
- **纯前端静态/Projection 驱动 Sections** (`STATIC_SECTIONS`): **7**
- **混合驱动 Sections** (`MIXED_SECTIONS`): **0**

### 事实判定结论：
> **当前 HFM 首页全部 8 个 Section 100% 由前端静态 TypeScript 数据与确定性 Projection (`homeProjection.ts`) 驱动，在渲染时完全无需向后端发起任何网络请求。**
> 虽然后端提供了 `/api/v1/public/home` 接口，但前端 `HomeView` 及其子组件未接入该接口，属于“前后端各自独立实现，前端优先保证高可用与离线确定性呈现”。

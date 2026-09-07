# HFM-SEARCH-REALITY.md — 搜索与跨域检索能力事实审计

## 1. 核心问题回答

| 审计维度 | 当前事实 | 证据来源 |
|---|---|---|
| **后端搜索 API 是否存在？** | 是 (`GET /api/v1/public/search`, `GET /api/v1/research/search`) | `apps/backend/src/hfm/api/v1/phase1.py:150` |
| **搜索是否基于数据库索引？** | 后端基于 `Entity` 表进行 ILIKE 模糊查询与已发布校验；前端同时内置了静态分词与倒排索引 | `apps/backend/src/hfm/phase1/search.py`, `apps/frontend/src/data/searchIndex.ts` |
| **支持的检索实体类型** | 人物 (person)、作品 (work)、版本 (edition)、文献文本 (text)、非遗 (heritage)、论文 (paper) | `apps/frontend/src/types/search.ts` |
| **前端分面筛选 (Facets)** | 支持按上述实体类别分类过滤，并实时展示分面命中数量计数 | `apps/frontend/src/views/search/SearchView.vue:180` |
| **分页机制** | 支持服务端与客户端双重分页 (`page`, `page_size`)，非法范围由后端 fail-closed 返回 400 | `phase1.py:158`, `SearchView.vue` |
| **空状态与异常处理** | 输入为空时展示建议词与检索边界提示；无匹配时展示优雅 Empty State；网络异常展示明确重试提示 | `SearchView.vue` |
| **论文检索现状** | **明确为 PARTIAL**。虽然学术论文总量审计有 515 篇，但当前结构化可检索的论文题录为 10 条（精选样本），未虚构假索引 | `searchIndex.ts:SEARCHABLE_PAPER_TOTAL = 10` |

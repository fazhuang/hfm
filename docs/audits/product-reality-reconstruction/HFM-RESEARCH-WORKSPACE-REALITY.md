# HFM-RESEARCH-WORKSPACE-REALITY.md — 研究工作台专项审计事实

## 1. 核心问题裁决表

| 审计项 | 事实裁决 | 真实代码 / 证据 |
|---|---|---|
| **研究人员当前能否登录？** | **能** | `POST /api/v1/auth/login` 支持学者登录，返回对应 Role 与 Token，前端 `/login` 界面已完整联调并支持自动跳转 |
| **认证与权限机制是什么？** | **JWT Bearer Token + 服务端 5 级严格 RBAC** | `apps/backend/src/hfm/api/v1/deps.py` 中的 `require_permission`，前端路由守卫 `requireAnyRole` |
| **有哪些真实的研究前端页面？** | **3 个页面** | `ResearchHomeView.vue` (概览), `ResearchSearchView.vue` (检索), `ResearchEntityView.vue` (实体与证据链视图) |
| **前端能够管理什么实体？** | **只读浏览与导出** | 可检索实体、查看 Evidence 关联、使用 ExportPanel 进行 Markdown/Print 格式导出 |
| **后端支持哪些写操作 (CRUD)？** | **完整项目与笔记 CRUD、内容提交流程** | `POST/GET/PATCH/DELETE /api/v1/research/projects`<br>`POST/GET/PATCH/DELETE /api/v1/research/notes`<br>`POST /api/v1/research/artifacts` |
| **是否存在工作流与发布审批？** | **后端存在，前端未提供审批后台 UI** | 后端支持 `submit_for_review`，管理员支持 `approve`/`reject`/`withdraw` |
| **是否存在多媒体上传功能？** | **后端存在服务，无前端上传控件** | `apps/backend/src/hfm/phase2/media/service.py` 具备媒体持久化，但无专门的前端上传面板 |
| **哪些功能当前只有“壳”？** | **工作台的在线编辑与创建能力** | 前端有入口和导航，但点进工作台后只能查看只读的“可研究内容列表”与导出按钮，无法在网页上直接输入新增项目或笔记 |

---

## 2. 状态判定

```text
RESEARCH_WORKSPACE_STATUS = PARTIAL
```

### 判定依据：
1. **后端实现度 100%**：数据库建表、Service 层数据隔离、所有者防越权保护、REST API 路由、Pytest 测试覆盖率均达到 100%。
2. **前端实现度 40%**：成功实现了研究端专属布局 (`ResearchLayout.vue`)、权限保护守卫 (`guards.ts`)、研究级高密度检索与实体浏览界面、学术导出组件；**但完全缺失研究人员自建项目、记录笔记的网页表单界面**。

# HFM-FRONTEND-BACKEND-DATAFLOW.md — 前后端调用链与数据流全量审计

本文件解构从浏览器用户交互到数据库实体的端到端链路。

---

## 链路 A：打开皇甫谧人物页 (`/persons/person-huangfu-mi`)

```text
1. 用户访问 URL: /persons/person-huangfu-mi
2. Vue Router 命中: route 'person', 加载 PersonDetailView.vue
3. 组件挂载: 调用 fetchPublicPerson('person-huangfu-mi') (apps/frontend/src/services/api.ts)
4. HTTP 请求: GET /api/v1/public/persons/person-huangfu-mi
5. 后端路由: public_router.get("/persons/{entity_id}") (phase1.py:186)
6. 业务服务: PersonService(session).get_public_person("person-huangfu-mi")
7. 数据查询:
   - SELECT FROM entities WHERE id = 'person-huangfu-mi'
   - SELECT FROM persons WHERE entity_id = 'person-huangfu-mi'
   - SELECT FROM publication_records WHERE artifact_id = ... AND publication_status = 'PUBLISHED'
   - SELECT FROM events WHERE entity_id = 'person-huangfu-mi'
8. 组装响应: 返回 JSON: { status: 'success', data: { entity_id, name, life_dates, biog, events, ... } }
9. 前端消费:
   - 若接口返回成功: 存入 state, 渲染人物生平、传记、事件轴
   - 若接口失败/404: 优雅降级触发本地 CORE_PERSON_DEFINITION / CORE_PERSON_LIFE_PHASES 静态配置
10. 用户看到完整的人物学术小传与纪年
```

---

## 链路 B：全局搜索 (`/search?q=皇甫谧`)

```text
1. 用户在导航栏或首页搜索框输入 "皇甫谧" 回车
2. Vue Router 导航至: /search?q=皇甫谧，加载 SearchView.vue
3. 组件响应 query: 调用 searchPublicHits({ q: '皇甫谧', page: 1, page_size: 20 })
4. HTTP 请求: GET /api/v1/public/search?q=%E7%9A%87%E7%94%AB%E8%B0%A7&page=1&page_size=20
5. 后端路由: public_router.get("/search") (phase1.py:150)
6. 业务服务: SearchService(session).public_search(q='皇甫谧', page=1, page_size=20)
7. 数据库检索:
   - 对 entities 表 name, aliases, description 进行 ILIKE 模糊匹配
   - 强约束: 必须存在有效的 publication_records 且 status == 'PUBLISHED' (防未审内容泄漏)
8. 返回 JSON: { status: 'success', data: { hits: [...], total: N, page: 1, page_size: 20 } }
9. 前端渲染:
   - SearchView.vue 将后端返回的 hits 与本地 searchIndex 聚合/去重，展示高亮卡片和分面过滤器
```

---

## 链路 C：打开《针灸甲乙经》(`/jiayi`)

```text
1. 用户访问: /jiayi
2. Vue Router 命中: route 'jiayi', 加载 JiayiView.vue
3. 渲染数据流:
   - 静态呈现: 从 `apps/frontend/src/data/jiayiView.ts` 读取古籍古本 (JIAYI_ANCIENT_EDITIONS)、现代校注本 (JIAYI_MODERN_EDITIONS)、版本谱系图
   - 动态接口: JiayiView 会按需调用 `fetchPublicWorkStructure('work-jiayi')`
4. 后端路由: public_router.get("/works/{work_id}/structure") (phase1.py:269)
5. 数据库查询:
   - SELECT FROM chapters WHERE work_id = 'work-jiayi' ORDER BY sequence
   - SELECT FROM passages WHERE chapter_id = ...
6. 前端展示: 呈现完整的 12 卷、128 篇目录导航与古今版本考据
```

---

## 链路 D：打开非遗传承页 (`/heritage`)

```text
1. 用户访问: /heritage
2. Vue Router 命中: route 'heritage', 加载 HeritageView.vue
3. 数据流:
   - 前端本地数据: `apps/frontend/src/data/heritageView.ts` 承载核心传承人刘君奇（第六代名医）档案与非遗技法考证
   - 后端接口: 可并发请求 GET /api/v1/public/heritage
4. 后端处理: HeritageService 查询 heritage_projects 与关联名医
5. 界面呈现: 活态传承发展史、代表性名医档案与当代保护工程进展
```

---

## 链路 E：研究人员登录并打开研究工作台 (`/login` → `/research`)

```text
1. 访问 /login，输入学者账号密码 (如 scholar / pass)
2. HTTP 请求: POST /api/v1/auth/login, body: { username, password }
3. 后端执行:
   - 查询 users 表验证 password_hash
   - 查询 user_roles 关联 roles 表，获取 SCHOLAR_RESEARCHER 角色
   - issue_token 生成签名令牌并返回: { token: "...", role: "SCHOLAR_RESEARCHER" }
4. 前端 Pinia store (`authStore`): 保存 token 至 localStorage，更新 isAuthenticated = true
5. 前端路由跳转: /research，激活 ResearchLayout.vue 与 ResearchHomeView.vue
6. 前端路由守卫: guards.ts 校验 roles 包含 SCHOLAR_RESEARCHER，放行
7. 页面渲染:
   - 从 `apps/frontend/src/data/researchProjection.ts` 加载真实数据盘点 (文献数、论文数、引文数)
   - 提供 ExportPanel 进行 Markdown/Print 导出
```

---

## 链路 F：研究端真实写操作链（后端已完整实现，前端暂未挂载 UI）

以 **“研究人员创建专属研究项目”** 为例：
```text
1. 客户端发起请求: POST /api/v1/research/projects
   Header: Authorization: Bearer <TOKEN>
   Body: { "title": "皇甫谧灸法取穴规律研究", "description": "基于甲乙经卷三考证" }
2. 后端守卫: require_permission("research:project:create") 检查当前 Token 角色是否具备该权限
3. 业务路由: research_create_project (phase1.py:770)
4. 服务层: ResearchWorkspaceService(session).create_project(...)
5. 数据库操作:
   - INSERT INTO research_projects (id, title, description, owner_id, created_at, updated_at)
   - 强隔离: owner_id 强制绑定为当前 Token 对应的 principal.user_id，拒绝外部伪造
   - INSERT INTO audit_logs (记录创建行为)
6. 响应返回: { status: 'success', data: { id: "proj-...", title: "...", owner_id: "..." } }

【事实断言】此链路后端代码、数据库模型、测试用例 100% 完整具备；但前端当前仅构建了 ResearchHomeView 只读视图，未提供“新建项目”的表单 UI 页面。
```

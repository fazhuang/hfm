# HFM Phase 1 ADR-01 — Deployment Topology & Public/Research Separation

- **ADR-ID**: ADR-01
- **Title**: Physical Deployment Topology with Strict Logical Public/Research Separation
- **Status**: `ACCEPTED`
- **Date**: 2026-08-29
- **Governance Baseline**: `29c5b856f221a12bac9de13e1a5043c5d05208e2`
- **Classification**: `PRE_IMPLEMENTATION_BLOCKING` $\rightarrow$ `RESOLVED`
- **Affected Work Packages**: `P1-11` (Public Portal), `P1-12` (Research Experience)

---

## 1. Context (背景)

客户确认需求 (CR-004, CR-009) 明确要求构建“面向社会公众的互联网公开门户”与“面向校内研究人员的研究后台”双层体验，且明确参观者为第一优先级用户。架构边界契约 (AB-02, AB-05, AB-10) 严格规定公开门户仅可访问经审核发布的投射快照，研究后台需经过严格鉴权与权限管控。

在 Phase 1 阶段，甘肃医学院与灵台县示范中心处于平台首期建设阶段，用户流量、并发规模及运维团队资源均具有校园与中小型学术平台特征。架构选型需在满足严格逻辑隔离与安全防线的前提下，避免过早引入微服务拆分带来的分布式运维负担与数据一致性同步开销。

---

## 2. Evidence (现有事实与证据)

1. **代码库现状 (NPG-003 CAP-001/002)**: 当前 HFM 拥有单一的 FastAPI 后端服务骨架 (`apps/backend`) 与基于 Vue 3 + Vite 的前端应用 (`apps/frontend`)，持久层基于单一 PostgreSQL 数据库。
2. **客户需求 (CR-009, CR-010)**: 客户确认逻辑双层架构方向，但未要求物理多集群或分布式微服务部署。
3. **架构边界 (AB-02, AB-15)**: 明确公开端与研究端在数据投射与授权表面上必须隔离，但允许共享受控的核心内容库与数据层。

---

## 3. Options Considered (备选方案评估)

| 方案 | 架构描述 | 复杂度 | 运维成本 | 隔离性 | 一致性保障 | 综合评价 |
| --- | --- | --- | --- | --- | --- | --- |
| **Option A: 物理完全分离架构 (Physical Multi-Service Split)** | 部署独立的 Public Backend 与 Research Backend 物理进程，配合独立的网关与数据库/读写分离集群。 | 极高 | 极高 | 物理级 | 跨服务数据同步与发布撤回存在延迟和一致性风险 | 过度设计，显著增加首期工程风险 |
| **Option B: 单体模块化部署 + 严格逻辑与鉴权隔离 (Single Deployable Modular System - 选定)** | 单一 FastAPI 应用部署，内部划分为严格隔离的路由命名空间 (`/api/v1/public/*` 与 `/api/v1/research/*`)，共享经过发布状态机过滤的单一 PostgreSQL 数据库，前端构建为统一或分包部署的 SPA。 | 最低 | 最低 | 逻辑/强鉴权隔离 | 单库事务保障发布与撤回原子生效，零同步延迟 | **最简充分，完全满足 Phase 1 需求** |
| **Option C: 物理网关 + 内部微服务群 (API Gateway + Microservices)** | 引入 Kong/Envoy 网关，后端拆分为 Auth、Content、Search、Reader、Portal 独立服务。 | 高 | 高 | 进程级 | 分布式事务与跨服务链路追踪成本高 | 严重违背最简原则 |

---

## 4. Decision (决策内容)

**决定采用 Option B：单体模块化部署架构，配合严格的逻辑隔离、路由命名空间隔离与视图模型隔离。**

1. **部署拓扑 (Deployment Topology)**:
   - 生产部署形态为：**1 个 Nginx 反向代理与静态资源服务器 + 1 个 FastAPI (Uvicorn) 后端服务实例 + 1 个 PostgreSQL 数据库实例**。
   - 所有静态资源与前端页面由 Nginx 统一代理分发，根据 URL 路径路由至公开门户或校内研究工作台视图。
2. **信任与鉴权边界 (Trust & Auth Boundaries)**:
   - `/api/v1/public/*`: 面向公众互联网的匿名公开接口，绝对不挂载任何强制认证拦截器，支持公众无门槛访问。
   - `/api/v1/research/*` 及 `/api/v1/admin/*`: 校内研究与管理接口，强制挂载 `Bearer` JWT 认证与 RBAC 权限校验依赖。
3. **数据投射与发布隔离边界 (Publication Exposure Boundary)**:
   - 公开接口只允许查询 `publication_status = 'PUBLISHED'` 且 `rights_status` 合规的数据投射。
   - 研究接口支持根据用户身份与租户权限查询草稿、研究笔记与富证据链条。
4. **未来平滑演进路径 (Future Split Path)**:
   - 保持模块化代码结构 (`hfm.api.public` 与 `hfm.api.research` 零直接耦合，统一通过底层 Service/Repository 通信)。
   - 后续若公众端访问量激增，可直接在 Nginx 层将 `/api/v1/public/*` 请求分流至独立的公开只读只读副本容器，无需重构业务代码。

---

## 5. Rationale (决策理由)

1. **奥卡姆剃刀与最简充分**: 避免在 Phase 1 引入微服务服务发现、RPC、分布式配置与跨服务网络调用的复杂性，最大化聚焦于 14 个核心工作包的业务领域能力建设。
2. **事务原子性与撤回可观测性**: 典籍发布与紧急下架撤回（AB-07, AC-09）可在单数据库内实现毫秒级原子事务更新，杜绝分布式缓存或跨服务数据同步不一致导致的“下架后公众端仍可抓取”的安全风险。
3. **环境与测试一致性**: 开发、CI 测试与生产环境完全对称，单元测试与端到端集成测试（Vitest, Pytest）可轻量级快速执行。

---

## 6. Consequences (决策影响)

### 正向影响 (Positive)
- 极大简化基础设施部署与运维监控要求。
- 研发团队无需处理分布式事务与跨服务追踪，开发与测试效率最大化。
- 本地开发与 CI 流程简单快速，单条 `docker compose` 即可启动完整环境。

### 负向影响与权衡 (Trade-offs & Mitigations)
- **代码级隔离纪律要求**: 若开发人员疏忽，可能在 public 接口中误用未经审查的 ORM 实体。
  - *缓解措施*: 通过 ADR-05 规定的专用 Pydantic View Model 序列化白名单与自动化负向渗透测试用例强制杜绝。

---

## 7. Required Guards (必须执行的架构守卫)

1. **Guard-01**: 禁止公开路由 (`/api/v1/public/*`) 直接返回 ORM 模型实例，必须经由 `Public*Response` Pydantic Schema 进行白名单序列化。
2. **Guard-02**: 禁止在同一 API 路由中通过参数动态切换公开/私有视图模式（严禁 `?is_public=true` 模式），必须采用明确的 URL 命名空间物理隔离。
3. **Guard-03**: Nginx 配置与后端 CORS 配置必须明确区分公开资源跨域策略与研究端凭证策略。

---

## 8. Acceptance Tests (验收测试矩阵)

| 测试用例 ID | 测试目标 | 验证方法 | 预期结果 |
| --- | --- | --- | --- |
| `TEST-ADR01-01` | 公开端匿名访问连通性 | 模拟未携带 Authorization 头的 HTTP GET 请求访问 `/api/v1/public/works` | 返回 200 OK 及已发布典籍列表 |
| `TEST-ADR01-02` | 研究端未认证拦截 | 模拟未携带 Token 访问 `/api/v1/research/projects` | 返回 401 Unauthorized |
| `TEST-ADR01-03` | 独立部署拓扑冒烟测试 | 单容器/单进程启动 FastAPI 并通过健康检查 | `/health`, `/live`, `/ready` 全部返回 200 OK |

---

## 9. Reversal & Escalation Conditions (反转与升格条件)

出现以下任一事实时，本 ADR 必须重新打开评估是否升格为物理多服务分离：
1. 公开门户公网流量达到单机 Nginx/FastAPI 瓶颈（CPU > 80% 持续且单节点无法纵向扩展）。
2. 校方网络安全合规部门出具正式的书面硬性要求，明确规定公开门户服务器与校内研究数据库必须跨物理隔离网段（DMZ 与内网完全物理切断）。

---

## 10. Affected Work Packages (受影响工作包)

- **P1-00**: 治理契约与变更控制。
- **P1-11**: Public Portal（公开门户集成）。
- **P1-12**: Research Experience（研究工作台集成）。

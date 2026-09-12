# HFM Phase 1 — Frontier-2 Implementation Evidence（P1-02 / P1-08 / P1-09 / P1-10）

Date: 2026-08-29 · Phase 1 — Frontier-2 Implementation Evidence
Execution baseline: `a49ed5225422b41409fecaefd12d3f14ee0606c8` · P1-00/P1-01 Acceptance: `ac8b0f23…`
Accepted implementation head: `14ce98e…` · Branch: `phase1/frontier-2-p1-02-p1-08-p1-09-p1-10`
证据契约：HFM-PHASE1-EVIDENCE-CONTRACT-v1.md（E-02 / E-08 / E-09 / E-10）

## 实施范围

```text
P1-02 — Evidence / Citation / Source / Provenance（fail-closed 证据链）
P1-08 — Unified Search（ADR-02 PostgreSQL 原生；发布/RBAC 谓词）
P1-09 — Publication / Review / Withdrawal（显式发布状态边界）
P1-10 — Identity / RBAC（ADR-07 HFM 原生 5 角色）
实施顺序 P1-02 → P1-10 → P1-09 → P1-08（仅实施排序，不改 DAG）
未实施任何其他 WP / Display / AI / 3D / VR / XR / Virtual Training / clinical。
```

## WP-ID P1-10 — Identity / RBAC（ADR-07）

| 项 | 内容 |
| --- | --- |
| Acceptance Criterion | deny-by-default roles and separation of duties enforced（E-10） |
| Implementation Files | `src/hfm/models/identity.py` + `src/hfm/phase1/auth.py` + `src/hfm/api/v1/deps.py` |
| Migration Files | `alembic/versions/0010_p1_frontier2.py`（users/roles/user_roles/role_permissions） |
| Test Files | `tests/test_phase1_rbac.py`（10 项） |
| Verification Command | `cd apps/backend && ../../.venv/bin/pytest tests/test_phase1_rbac.py -q` |
| Observed Result | 10 passed（含 default deny / token revocation / tamper / permission matrix） |
| Negative Tests | 匿名零权限；篡改 token 拒绝；token_version 递增后旧 token 401；researcher 无发布权限 |
| Evidence Paths | `docs/audit/HFM-PHASE1-FRONTIER2-P1-02-P1-08-P1-09-P1-10-IMPLEMENTATION.md` |

要点：5 角色冻结矩阵（ANONYMOUS_VISITOR/STUDENT_RESEARCHER/SCHOLAR_RESEARCHER/CONTENT_REVIEWER/SYSTEM_ADMIN）；scrypt 加盐哈希（stdlib，无新依赖）；HMAC 签名无状态 token + token_version 即时撤销（Guard-03）；默认拒绝；无 HFB 凭证迁移。

## WP-ID P1-09 — Publication / Review / Withdrawal

| 项 | 内容 |
| --- | --- |
| Acceptance Criterion | review→approve→publish→withdraw→rollback states observable; no publish without approval（E-09） |
| Implementation Files | `src/hfm/models/publication.py` + `src/hfm/phase1/publication.py` + `src/hfm/api/v1/phase1.py`（admin/publication 端点） |
| Migration Files | `0010_p1_frontier2.py`（publication_records） |
| Test Files | `tests/test_phase1_publication.py`（9 项） |
| Verification Command | `cd apps/backend && ../../.venv/bin/pytest tests/test_phase1_publication.py -q` |
| Observed Result | 9 passed（全生命周期 / 非法流转拒绝 / 未授权拒绝 / SoD / admission 不自动发布） |
| Negative Tests | PENDING_REVIEW→PUBLISHED 非法；scholar 发布拒绝；scholar 撤回拒绝；自审自发拒绝；非 ADMITTED 不可提交 |
| Evidence Paths | 同上 |

要点：admission（P1-01）≠ approval ≠ published ≠ withdrawn；公开可见性唯一由 PUBLISHED 定义；SoD（reviewer != creator，Guard-02）；撤回不销毁历史（审计字段保留）。

## WP-ID P1-02 — Evidence / Citation / Source / Provenance

| 项 | 内容 |
| --- | --- |
| Acceptance Criterion | SourceRef→Evidence→Citation chain resolves to HFM targets; no orphan（E-02） |
| Implementation Files | `src/hfm/models/evidence.py`（+artifact_id 绑定）+ `src/hfm/phase1/evidence_chain.py` + research evidence-chain API |
| Migration Files | `0010_p1_frontier2.py`（evidences.artifact_id） |
| Test Files | `tests/test_phase1_evidence_chain.py`（6 项） |
| Verification Command | `cd apps/backend && ../../.venv/bin/pytest tests/test_phase1_evidence_chain.py -q` |
| Observed Result | 6 passed（链解析 / 孤儿引用拒绝 / 无证据引文拒绝 / 完整性报告零孤儿） |
| Negative Tests | 孤儿 citation；无证据 backing；证据锚点缺失；引用不存在 |
| Evidence Paths | 同上 |

要点：fail-closed 全链解析（Citation→Assertion→Evidence→SourceRef→Source；直接证据边）；无证据 backing 的引文拒绝；Evidence 锚点 DB CHECK 保持；HFB ID 仅作迁移元数据（legacy_source_key）。

## WP-ID P1-08 — Unified Search（ADR-02）

| 项 | 内容 |
| --- | --- |
| Acceptance Criterion | public filters published; research filters authorized; result retains source context（E-08） |
| Implementation Files | `src/hfm/phase1/search.py` + `src/hfm/api/v1/phase1.py`（public/research/admin search） |
| Migration Files | `0010_p1_frontier2.py`（PostgreSQL-only pg_trgm GIN + 复合 B-Tree） |
| Test Files | `tests/test_phase1_search.py`（6 项） |
| Verification Command | `cd apps/backend && ../../.venv/bin/pytest tests/test_phase1_search.py -q` |
| Observed Result | 6 passed（中文检索 / 草稿与撤回不出现在公开检索 / 研究需认证 / 参数不可提权 / 分页总数正确） |
| Negative Tests | draft absent；withdrawn absent；匿名不可经查询参数提权；research 未认证拒绝 |
| Evidence Paths | 同上 |

要点：公开谓词硬注入（仅 PUBLISHED artifact 链上的 passage）；研究端需认证；admin 需 content:review；ILIKE 中文子串（PG 与 SQLite 测试路径均可）；pg_trgm/GIN 仅 PG（迁移按 dialect 守卫）；无 ES/外部分布式；无临床排序。

## 回归

```text
pytest: 291 passed / 0 failed / 1 warning（P3 既有）
mypy: PASS（120 source files）· Ruff: PASS · Ruff Format: PASS（131 files）
Frontend: ESLint PASS · Prettier PASS · vue-tsc PASS · Vitest 24 passed · Build PASS
Runtime: /health /ready /version /live /config 200 · X-Request-ID PASS
Alembic: 0010 (head)（0001→0010 链 + downgrade 门禁测试 PASS）
API: /api/v1/auth|admin|public|research 共 11 路由（ADR-05 三命名空间）
```

## 边界确认

```text
- 未实施 P1-03…P1-07、P1-11…P1-13；未实施 Display/AI/3D/VR/XR/Virtual Training/clinical
- 无生产 HFB 导入（NOT PERFORMED）；无 HFB runtime 依赖；无 HFB 凭证/角色迁移；未执行 M5
- CD-7: NONEXISTENT
- 未修改任何冻结治理工件；ADR-01/02/05/06/07 未被实施变更
- 冻结 Phase 0.4 表未被破坏性迁移
```

## 完成判定

```text
P1-02 = PASS · P1-08 = PASS · P1-09 = PASS · P1-10 = PASS（各自独立证据）
```

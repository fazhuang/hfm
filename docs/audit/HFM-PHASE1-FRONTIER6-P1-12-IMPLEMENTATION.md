# HFM Phase 1 — Frontier-6 P1-12 Implementation Evidence（研究工作台 · 角色矩阵修复）

Date: 2026-09-01 · Phase 1 — Frontier-6 P1-12 Implementation Evidence（REMEDIATION）
Execution baseline: `31c882145150dbae0da66573b275f8f5dbb7348c`（Frontier-5 Acceptance Archive）
Branch: `phase1/frontier-6-p1-12`
证据契约：HFM-PHASE1-EVIDENCE-CONTRACT-v1.md（E-12）

## 历史与拒绝记录（不抹除）

```text
P1-12 首次候选（6ea014858f6aa22bd7bededf009965837c375776）= REJECTED
拒绝根因：ADR-07 ROLE-MATRIX AUTHORIZATION MISMATCH
  1. 原实现以单一宽权限 project:create 门禁整个研究工作台 CRUD 表面；
  2. STUDENT_RESEARCHER 因此获得项目 CRUD 能力；
  3. 冻结 ADR-07 将 STUDENT_RESEARCHER 限定为个人研读笔记/书签；
  4. 学术研究项目能力属于 SCHOLAR_RESEARCHER；
  5. 其余 P1-12 审计项全部通过。
本次为针对根因的修复候选（保留拒绝候选历史，不改写历史）。
```

## 冻结 ADR-07 精确角色矩阵（§4.1/§4.2，权威来源：docs/governance/adr/HFM-PHASE1-ADR-07-IDENTITY-RBAC.md + src/hfm/models/identity.py）

| 角色 | 研究空间能力（ADR-07 明文） | 本实施映射 |
| --- | --- | --- |
| ANONYMOUS_VISITOR | 仅公开已发布内容；零写入 | 全部拒绝（默认拒绝） |
| STUDENT_RESEARCHER | 查阅典籍与证据链；**创建个人研读笔记与书签**（仅个人工作区） | `research:note:*`（create/read/update/delete）授权；**项目全部拒绝** |
| SCHOLAR_RESEARCHER | **创建学术研究项目**、提交校勘断言提案与引文标注；无最终发布权 | `research:project:*`（create/read/update/delete）授权；保留 `research:note:*` |
| CONTENT_REVIEWER | 内容准入审核、断言审查、发布审批/撤回/回滚 | 研究空间全部拒绝（不因存在其他权限而获得） |
| SYSTEM_ADMIN | 账号生命周期、角色分配、系统健康、审计日志 | 冻结全码映射 `frozenset(PERMISSION_CODES)`（含新 research:* 码） |

新增规范权限码（最小必需，直接可溯至 ADR-07 §4.1 角色矩阵，§4.2 原子码模式）：

```text
research:project:create / read / update / delete  — SCHOLAR_RESEARCHER（+ SYSTEM_ADMIN 全码）
research:note:create / read / update / delete     — STUDENT_RESEARCHER + SCHOLAR_RESEARCHER（+ SYSTEM_ADMIN 全码）
```

## 修复实施（RBAC-only，无 schema 变更）

- **替换**：原 `project:create` 单一门禁（service `_require_research_principal` + 全部路由依赖）
  → **能力匹配**的规范权限码：每个方法/路由按操作类别校验对应 `research:*` 码；
- **身份与所有权**（保持原验收行为）：`owner_id` 恒来自认证 Principal，服务 API 无
  `owner_id` 入参；跨用户/猜测 ID 失败关闭（KeyError → 404，无存在性泄露）；
  权限（role）与所有权（object）相互独立、**两者必须同时通过**；
- **服务层强制**（非仅路由层）：每个外部可达操作在 service 内再次校验 Principal
  权限（create/list/read/update/delete × project/note 共 10 个路径）；
- **规范 RBAC 集成**：仅扩展 `identity.py` 的 `PERMISSION_CODES` 与
  `ROLE_PERMISSIONS`（既有码与映射未删除；`project:create` 在已验收基线中为
  未使用死码，不再用于研究空间）；未建重复角色系统；
- **notes 不要求项目父级**（project_id 可选）：STUDENT 个人笔记无需项目即可存在，
  ADR-07 学生笔记能力可完整表达；学生笔记不得绑定他人项目（所有权校验拒绝）。

## WP-ID P1-12 — 认证研究工作台（修复候选）

| 项 | 内容 |
| --- | --- |
| Acceptance Criterion | authenticated workflow preserves ownership and richer evidence access（E-12）；no cross-user/tenant access or public exposure；ADR-07 角色矩阵精确 |
| Implementation Files（本次修复） | `src/hfm/models/identity.py`（+8 规范权限码与映射）+ `src/hfm/phase1/research_workspace.py`（能力匹配校验）+ `src/hfm/api/v1/phase1.py`（10 路由依赖逐操作匹配）+ `tests/test_phase1_research_workspace.py`（角色矩阵测试新增） |
| Migration Files | 无新增（修复为 RBAC-only；拓扑保持 0012 → 0013 single head，未创建 0014） |
| Verification Command | `cd apps/backend && ../../.venv/bin/pytest tests/test_phase1_research_workspace.py -q` |
| Observed Result | 21 passed（项目/笔记 CRUD + 级联 / 双用户隔离 / 猜测 ID / 匿名拒绝 / 学生笔记授权 / 学生项目拒绝 / 学者项目授权 / 学者笔记授权 / 审核员全拒绝 / 未映射角色拒绝 / 管理员全码语义 / 无客户端 owner_id / token 撤销 / 富证据与版本上下文 / 公开隔离 / 发布边界 / C 域安全 / 0013 迁移升级降级单头 / FK） |

## Role/Action 矩阵测试（test_phase1_research_workspace.py）

| 角色 | 操作 | 期望 | 测试 |
| --- | --- | --- | --- |
| STUDENT_RESEARCHER | note create/list/read/update/delete | ALLOW | `test_role_matrix_student_personal_notes_authorized` |
| STUDENT_RESEARCHER | project create/list/read/update/delete | DENY | `test_role_matrix_student_project_capability_denied` |
| SCHOLAR_RESEARCHER | project create/list/read/update/delete（自有对象） | ALLOW | `test_role_matrix_scholar_project_capability` |
| SCHOLAR_RESEARCHER | note create/read | ALLOW | `test_role_matrix_scholar_note_capability` |
| SCHOLAR_RESEARCHER | 另一学者项目/笔记（ownership） | DENY（404） | `test_two_user_isolation` |
| CONTENT_REVIEWER | project + note 全部 10 操作 | DENY | `test_role_matrix_reviewer_denied` |
| ANONYMOUS | 全部操作 | DENY | `test_anonymous_denied` |
| 未映射角色（MYSTERY_ROLE） | list/create | DENY（默认拒绝） | `test_role_matrix_unmapped_role_denied` |
| SYSTEM_ADMIN | project create/get | ALLOW（冻结全码） | `test_role_matrix_admin_semantics` |
| 撤销 token（token_version++） | 全部新路由 | DENY | `test_token_version_revocation_regression` |

## Ownership / IDOR 回归（保持，未弱化 404/403 fail-closed）

```text
User B → User A project read/update/delete = DENY（KeyError → 404）
User B → User A note read/update/delete = DENY
跨所有者 note 绑定他人 project = DENY（KeyError）
猜测有效格式 ID（全零 UUID）= DENY（404，无存在性泄露）
无客户端 owner_id（服务 API 无此参数；行 owner_id == Principal.user_id）
```

## Acceptance Criterion → Evidence 映射（修复后）

| Criterion | 实现文件 | 迁移 | 正向测试 | 负向测试 | 命令 | 观测结果 |
| --- | --- | --- | --- | --- | --- | --- |
| E-12 所有权隔离 | `phase1/research_workspace.py`（owner 过滤） | 0013 | CRUD 测试 | 双用户/猜测 ID | `pytest tests/test_phase1_research_workspace.py -q` | 21 passed |
| ADR-07 角色矩阵精确 | `models/identity.py` + `phase1/research_workspace.py` + `api/v1/phase1.py` | 0013 | 学者项目/学生笔记正向 | 学生项目拒绝/审核员拒绝/未映射拒绝 | 同上 | 矩阵逐项断言 |
| 权限能力匹配（拒绝宽门禁） | 10 方法/路由逐操作 `research:*` 码 | 0013 | 每操作独立校验 | 学生 5 项项目操作全拒 | 同上 | project:create 不再用于研究空间 |
| Deny-by-default | 默认拒绝 + 无权限码即拒 | 0013 | — | 匿名/未映射/撤销 token | 同上 | 全部 PermissionError |
| 富证据/版本上下文 | `phase1/reader.py` 复用 | 0013 | `test_research_evidence_and_version_context` | — | 同上 | 版本 + 证据链 |
| 公开隔离 | 公开谓词不变 | 0013 | `test_public_projection_excludes_workspace_state` | — | 同上 | 公开输出无 workspace |
| 0013 迁移（升级/降级/再升级/单头） | `alembic/versions/0013_*.py` | 0013 | 迁移测试 2 项 | — | 同上 | 0013 (head) single head |

## 回归

```text
pytest: 380 passed / 0 failed（此前 375 拒绝候选 + 角色矩阵修复净增 5）
mypy: PASS（143 source files）· 命令: cd apps/backend && ../../.venv/bin/mypy src tests
Ruff: PASS · Ruff Format: PASS（143 files already formatted）
Alembic: 0013 (head) single head（修复未创建 0014；RBAC-only）
migration gates（test_migrations.py）: 20 passed（已验收套件无回归）
聚焦回归（RBAC/auth/reader/search/evidence/publication/公开研究隔离/P1-02/07/08/09/10/13）:
全部包含于完整 380 passed；既有 RBAC（test_phase1_rbac.py）子集断言兼容新增权限码
```

## 边界确认

```text
- P1-11 零改动（已验收候选 6feeb16 保持）；P1-11 门户文件 0 进入本候选
- 未实施 Display/AI/3D/VR/XR/Virtual Training/clinical；deferred = 0
- 无生产 HFB 导入（NOT PERFORMED / NOT AUTHORIZED）；无 HFB runtime 依赖
- CD-7: NONEXISTENT
- 未修改任何冻结治理文档（Scope/DAG/Acceptance/Evidence/DoD/Boundary/Authorization/ADR）
  —— 仅扩展规范 RBAC 实现（identity.py）以表达冻结 ADR-07 矩阵（任务 §7 授权）
- 无 schema 变更（未创建 0014）
```

## 完成判定

```text
P1-12 = REMEDIATED IMPLEMENTATION CANDIDATE（修复验证完成；正式 ACCEPTED 判定权属 Codex）
历史拒绝候选 6ea01485… 保留为历史记录，未改写。
```

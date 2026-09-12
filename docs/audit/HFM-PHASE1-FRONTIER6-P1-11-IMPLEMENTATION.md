# HFM Phase 1 — Frontier-6 P1-11 Implementation Evidence（公开门户）

Date: 2026-09-01 · Phase 1 — Frontier-6 P1-11 Implementation Evidence
Execution baseline: `31c882145150dbae0da66573b275f8f5dbb7348c`（Frontier-5 Acceptance Archive）
Branch: `phase1/frontier-6-p1-11`
证据契约：HFM-PHASE1-EVIDENCE-CONTRACT-v1.md（E-11）

## 实施范围

```text
P1-11 — P1-PORTAL 公开门户（public approved-content portal）
目标（Acceptance Contract P1-11）：anonymous users see approved projection only
未实施 P1-12（独立候选，phase1/frontier-6-p1-12）；未实施 Display/AI/3D/VR/XR/
Virtual Training/clinical
未重新打开已验收 WP；P1-11 仅新增只读公开门户投影表面，不改动既有验收字节语义
```

## 架构要点（跨 WP 一致性）

- 门户 = **只读投影**，零 schema 变更（Alembic head 保持 `0012` 单头）；
  公开谓词与已验收 P1-07 reader / P1-08 search 一致：`PublicationRecord
  publication_status == 'PUBLISHED'` 绑定 `ContentArtifact.subject_entity_id`
  与记录实体（Work/Person/Heritage/C-term）匹配（P1-04/05/06/09 投影复用）；
- **失败关闭（fail-closed）**：DRAFT / 未发布 / 无 PUBLISHED 记录 / WITHDRAWN
  一律不返回；撤回即时生效（ADR-05 Guard-03：撤回后门户立即可见性消失，
  未发布 Work 的 editions 端点返回 404，不泄露存在性）；
- **白名单序列化（ADR-01/05 Guard）**：公开响应仅含公开字段
  （work_id/title/dynasty/category/edition_count/publication_status；
  edition_id/edition_name/era/publisher_block），绝不输出 entity_id、
  created_by、provenance、rights、evidence、relations、内部 hash；
- **无关系遍历（AB-14）**：门户不输出任何 relations/related 键；
- **无临床语义（AB-14）**：门户输出不包含 diagnosis/treatment/prescription/
  recommendation/主穴/配穴 表面；
- **复用已验收规范真值**：Source/SourceRef/Artifact/Version/Citation/Evidence/
  Publication/RBAC 全部复用，无重复真值存储（AB-03/AB-04）；
- 无 HFB runtime 依赖；无生产导入（NOT PERFORMED / NOT AUTHORIZED）。

## WP-ID P1-11 — 公开门户（Public Approved-Content Portal）

| 项 | 内容 |
| --- | --- |
| Acceptance Criterion | anonymous users see approved projection only（E-11）；no research/private/unpublished response |
| Implementation Files | `src/hfm/phase1/portal.py`（PortalService：home / works / work_editions）+ `src/hfm/api/v1/phase1.py`（public_router：`GET /api/v1/public/home`、`GET /api/v1/public/works`、`GET /api/v1/public/works/{work_id}/editions`） |
| Migration Files | 无（0012 保持 single head；门户为只读投影，无 schema 变更） |
| Test Files | `tests/test_phase1_portal.py`（14 项） |
| Verification Command | `cd apps/backend && ../../.venv/bin/pytest tests/test_phase1_portal.py -q` |
| Observed Result | 14 passed（home 已发布投影 / counts 仅已发布 / 未发布排除 / 无 PUBLISHED 记录排除 / works 列表仅已发布 / 撤回排除 / 撤回即时生效 / editions 白名单 / 未发布 404 / 猜测 ID 404 / 严格键集白名单 / 分页确定性 / 分页边界失败关闭 / 无关系遍历 / 无临床表面） |
| Negative Tests | 未发布 Work 不在 home/works；无 PUBLISHED 记录不在 home；WITHDRAWN 排除；撤回后 editions→None 且 home 计数归零；未发布 Work editions→None；随机 ID→None；响应键集精确白名单（无 entity_id/created_by/provenance/rights/evidence/relations）；分页 page<1、page_size<1 或 >100 拒绝；无 diagnosis/treatment/prescription/recommendation/主穴/配穴 表面 |

## Acceptance Criterion → Evidence 映射

| Criterion | 实现文件 | 迁移 | 正向测试 | 负向测试 | 命令 | 观测结果 |
| --- | --- | --- | --- | --- | --- | --- |
| E-11 匿名门户仅返回已批准投影 | `phase1/portal.py`（`home`/`works`/`work_editions` + `_published_subject_entities`） | 无 | `test_home_returns_published_projection`、`test_works_list_published_only`、`test_work_editions_published_work` | `test_home_excludes_unpublished`、`test_home_excludes_missing_publication`、`test_works_list_withdrawn_excluded`、`test_work_editions_unpublished_work_fail_closed` | `pytest tests/test_phase1_portal.py -q` | 14 passed；仅 PUBLISHED 绑定实体可见 |
| 撤回即时阻断（ADR-05 Guard-03） | `phase1/portal.py`（谓词每次查询实时计算） | 无 | — | `test_withdrawal_immediately_reflected` | 同上 | 撤回后 home/works/editions 全部即时不可见 |
| 严格字段白名单（ADR-01/05 Guard-01） | `phase1/portal.py`（`_serialize_work` + editions 序列化） | 无 | `test_strict_response_whitelist` | 同左（键集精确断言） | 同上 | 响应键集 == 公开白名单；无内部字段 |
| 猜测标识符无授权绕过 | `phase1/portal.py`（`work_editions` 先校验实体存在 + 已发布） | 无 | — | `test_work_editions_guessed_id_no_leak`、`test_work_editions_unpublished_work_fail_closed` | 同上 | 随机/未发布 ID → None（404） |
| 分页/排序确定性 | `phase1/portal.py`（`works` order_by created_at desc + id；limit/offset） | 无 | `test_pagination_deterministic` | `test_pagination_bounds_fail_closed` | 同上 | 同页两次逐字段相等；页间无重叠；非法分页拒绝 |
| AB-14 无关系遍历 | `phase1/portal.py`（输出键集封闭） | 无 | `test_no_relation_traversal` | 同左 | 同上 | 输出无 relations/related 键 |
| AB-14 无临床推荐语义 | `phase1/portal.py`（输出键集封闭） | 无 | `test_no_clinical_recommendation_surface` | 同左 | 同上 | 输出无 diagnosis/treatment/prescription/recommendation/主穴/配穴 |
| P1-04/05/06/09 集成（公开谓词一致） | `phase1/portal.py`（`_published_subject_entities` 复用） | 无 | home/works/editions 正向测试 | 撤回/未发布负向测试 | 同上 | 谓词与 reader/search 一致 |

## 回归

```text
pytest: 373 passed / 0 failed（此前 359 + P1-11 新增 14）
mypy: PASS（142 source files）· 命令: cd apps/backend && ../../.venv/bin/mypy src tests
Ruff: PASS · Ruff Format: PASS（142 files already formatted）
Alembic: 0012 (head) 保持 single head；无 schema 变更（SCHEMA_MIGRATION = 0）
migration gates（test_migrations.py）: 20 passed
聚焦回归（P1-02/04/05/07/08/09/10/13 + heritage + governance 相关）: 全部包含于
完整 373 passed；公开表面（search/reader/person/works/c-terms/heritage）无回归
```

## 边界确认

```text
- 未实施 P1-12（独立候选分支）；未实施 Display/AI/3D/VR/XR/Virtual Training/clinical
- 未重新打开已验收 WP；P1-11 仅新增只读门户投影表面，不改动既有验收字节语义
- 无生产 HFB 导入（NOT PERFORMED / NOT AUTHORIZED）；无 HFB runtime 依赖
- CD-7: NONEXISTENT
- 未修改任何冻结治理工件（Scope/DAG/Acceptance/Evidence/DoD/Boundary/Authorization/ADR）
- 无 schema 变更（head 保持 0012）——门户为只读投影
```

## 完成判定

```text
P1-11 = IMPLEMENTATION CANDIDATE（实施验证完成；正式 ACCEPTED 判定权属 Codex）
```

## 聚焦回归明细

```text
P1-11（test_phase1_portal.py）: 14 passed
migration gates（test_migrations.py）: 20 passed
完整 pytest: 373 passed / 0 failed
```

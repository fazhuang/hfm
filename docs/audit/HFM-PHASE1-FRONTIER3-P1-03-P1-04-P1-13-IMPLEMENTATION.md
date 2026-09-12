# HFM Phase 1 — Frontier-3 Implementation Evidence（P1-03 / P1-04 / P1-13）

Date: 2026-09-01 · Phase 1 — Frontier-3 Implementation Evidence
Execution baseline: `da9533923894fc5ff682238b1e0d9cdb0cd490dc`（Frontier-2 Acceptance）
Branch: `phase1/frontier-3-p1-03-p1-04-p1-13`
证据契约：HFM-PHASE1-EVIDENCE-CONTRACT-v1.md（E-03 / E-04 / E-13）

## 实施范围

```text
P1-03 — A 皇甫谧人物体系（person/event records expose evidence and publication state）
P1-04 — B 文献/思想体系（work/edition/version/passages preserve lineage and rights）
P1-13 — Versioning, audit and reconciliation closure（immutable lineage,
        batch metrics, reconciliation PASS recorded）
实施顺序 P1-13 基础服务 → P1-03 → P1-04（仅实施排序，不改 DAG）
未实施任何其他 WP / Display / AI / 3D / VR / XR / Virtual Training / clinical；
未重新打开已验收 P1-00/01/02/08/09/10（仅 P1-08 检索扩展、P1-09 审计集成等严格必需的最小集成）。
```

## 架构要点（跨 WP 一致性）

- 领域记录不建立任何并行的 Source/Evidence/Citation/Version/Publication/RBAC 真值存储：
  人物/著作的**发布投影**统一绑定到既有 P1-01 ContentArtifact（新增
  `content_artifacts.subject_entity_id → entities.id`），公开可见性唯一由
  P1-09 `publication_status == PUBLISHED` 决定（AB-03/AB-07）；
- Work 获得 typed-Entity 稳定身份（`works.entity_id`，I5，与 persons/events 骨架一致）；
- 人物传记事实 = 既有 CD-4 Assertion（subject=人物 Entity）+ CD-3 Evidence 链接；
  生平事件 = 既有 CD-6 Event + EventRelation（人物↔事件）；
- 版本谱系复用既有 CD-2 `versions.parent_version_id`（I2 不可变），P1-13 提供确定性
  链验证与摘要；变更审计写入新的 append-only `audit_log`；批次指标写入新的
  `reconciliation_runs`（PASS/FAIL，不可变）；
- 检索扩展复用 P1-08 SearchService（同一子系统，无第二检索子系统），公开端硬注入
  PUBLISHED 谓词，研究端需认证（ADR-02/05/07）。

## WP-ID P1-03 — A 皇甫谧人物体系

| 项 | 内容 |
| --- | --- |
| Acceptance Criterion | person/event records expose evidence and publication state（E-03） |
| Implementation Files | `src/hfm/phase1/person.py`（PersonService）+ `src/hfm/api/v1/phase1.py`（public/research persons 端点）+ `src/hfm/phase1/search.py`（person 检索集成） |
| Migration Files | `0011_p1_frontier3.py`（content_artifacts.subject_entity_id；persons.id 对齐） |
| Test Files | `tests/test_phase1_person.py`（11 项） |
| Verification Command | `cd apps/backend && ../../.venv/bin/pytest tests/test_phase1_person.py -q` |
| Observed Result | 11 passed（创建 / 非法关系拒绝 / 证据链 / provenance / 不可变 / 无隐式发布 / 公开可见性 / 撤回即时不可见 / 未授权拒绝 / 检索集成 / subject 绑定拒绝） |
| Negative Tests | 断言无值/无对象拒绝；事件关系空引用拒绝；缺失证据拒绝；未知人物拒绝；`invalid_subject_entity_binding` 准入拒绝；匿名创建/断言拒绝；未发布人物公开 404；撤回后公开投影消失 |
| Evidence Paths | `docs/audit/HFM-PHASE1-FRONTIER3-P1-03-P1-04-P1-13-IMPLEMENTATION.md` |

要点：人物记录=Entity(person)+Person（既有 CD-1 规范层）；传记事实=带证据链的
Assertion；公开投影仅暴露 PUBLISHED 且带证据的断言（每条公开主张均有证据，E-03）；
创建/准入绝不产生发布记录（无隐式发布）；变更经 P1-10 assertion:create 授权。

## WP-ID P1-04 — B 文献/思想体系

| 项 | 内容 |
| --- | --- |
| Acceptance Criterion | work/edition/version/passages preserve lineage and rights（E-04） |
| Implementation Files | `src/hfm/phase1/literature.py`（LiteratureService）+ `src/hfm/api/v1/phase1.py`（public/research works 端点）+ `src/hfm/models/work.py`（entity_id）+ `src/hfm/phase1/search.py`（work 发布谓词） |
| Migration Files | `0011_p1_frontier3.py`（works.entity_id UNIQUE；content_artifacts.subject_entity_id） |
| Test Files | `tests/test_phase1_literature.py`（11 项） |
| Verification Command | `cd apps/backend && ../../.venv/bin/pytest tests/test_phase1_literature.py -q` |
| Observed Result | 11 passed（结构 / 版本谱系 / Edition 同 Work / 跨 Work 绑定拒绝 / locator 可复现 / 无隐式发布 / 公开+权利投影 / 撤回 / 未授权拒绝 / 检索集成 / entity 不可变） |
| Negative Tests | 跨 Edition parent 拒绝；孤儿 parent 拒绝；跨 Work passage 版本绑定拒绝；空 title/正文拒绝；匿名变更拒绝；未发布/无实体绑定著作公开 404 |
| Evidence Paths | 同上 |

要点：复用 CD-2 FRBR（Work→Edition→Version→Chapter→Passage）；谱系约束
（Edition 同 Work parent、Version 同 Edition parent、Chapter 层级、Passage 跨 Work
版本一致性）；locator（Locator VO）可复现（E-04 引文定位）；rights_status 随
ContentArtifact 保留并在公开投影中暴露；未实现 Reader（P1-07 越界）。

## WP-ID P1-13 — Version / Audit / Reconciliation

| 项 | 内容 |
| --- | --- |
| Acceptance Criterion | immutable lineage, batch metrics, reconciliation PASS recorded（E-13） |
| Implementation Files | `src/hfm/phase1/version_audit.py`（AuditService / VersionLineageService / ReconciliationService）+ `src/hfm/models/audit.py` + `src/hfm/models/reconciliation.py` + `src/hfm/api/v1/phase1.py`（admin 端点）+ `src/hfm/phase1/publication.py`（审计集成） |
| Migration Files | `0011_p1_frontier3.py`（audit_log / reconciliation_runs） |
| Test Files | `tests/test_phase1_version_audit.py`（10 项） |
| Verification Command | `cd apps/backend && ../../.venv/bin/pytest tests/test_phase1_version_audit.py -q` |
| Observed Result | 10 passed（合法谱系 / 非法前驱拒绝 / 审计记录 / append-only / 对账 PASS / 失配 fail-closed / 未知 scope 拒绝 / batch scope / 禁止破坏性变更 / 历史保留） |
| Negative Tests | 孤儿 parent 拒绝；断链检测 raise；审计/对账记录不可改写；对账失配 raise ReconciliationMismatchError 且 FAIL 记录保留；未知 scope 拒绝 |
| Evidence Paths | 同上 |

要点：确定性谱系链（leaf→root）+ 规范摘要；append-only 审计日志（发布流转/准入/
领域创建均记录）；对账=count+规范化摘要比对，失配时记录 FAIL 并 fail-closed raise
（绝无 WARN-only 完成）；无事件溯源框架（最小实现）。

## 回归

```text
pytest: 324 passed / 0 failed / 1 warning（Starlette 既有弃用提示）
mypy: PASS（130 source files）· Ruff: PASS · Ruff Format: PASS（130 files）
Alembic: 0011 (head)（0001→0011 链 + upgrade/downgrade 门禁测试 PASS；
        persons.id 对齐列随 0011 添加/回退）
API 冒烟（SQLite 迁移库）：public persons/works 未发布 404 · public search 200 ·
        research/admin 匿名访问被拒绝（默认拒绝保持；500 为既有 PermissionError
        通用处理器行为，与已验收 P1-08/P1-10 API 一致）
```

## 边界确认

```text
- 未实施 P1-05、P1-06、P1-07、P1-11、P1-12；未实施 Display/AI/3D/VR/XR/Virtual Training/clinical
- 未重新打开已验收 WP；P1-08 检索扩展与 P1-09 审计集成为本前沿严格必需的最小集成
- 无生产 HFB 导入（NOT PERFORMED / NOT AUTHORIZED）；无 HFB runtime 依赖；未执行 M5
- CD-7: NONEXISTENT
- 未修改任何冻结治理工件（Scope/DAG/Acceptance/Evidence/DoD/Boundary/Authorization/ADR）
- 冻结 Phase 0.4 表未被破坏性迁移；persons.id 为对齐既有 ORM 的加法修复（可回退）
```

## 完成判定

```text
P1-03 = PASS · P1-04 = PASS · P1-13 = PASS（各自独立证据）
```

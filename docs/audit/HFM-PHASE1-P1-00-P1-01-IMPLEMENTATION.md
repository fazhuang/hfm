# HFM Phase 1 — P1-00 + P1-01 Implementation Evidence

Date: 2026-08-29 · Phase 1 — Implementation Evidence（P1-00 Governance / P1-01 Content Admission）
Execution baseline: `a49ed5225422b41409fecaefd12d3f14ee0606c8` · Branch: `phase1/p1-00-p1-01`
证据契约：HFM-PHASE1-EVIDENCE-CONTRACT-v1.md（E-00 / E-01）

## 实施范围

```text
P1-00 — Phase 1 Governance / Contract Enforcement（DAG 前置门禁 + 追踪矩阵 + 负向守卫）
P1-01 — Content Admission / Canonical Content Core（ContentArtifact 准入层）
仅实现已授权前沿；未实施任何下游 WP。
```

## WP-ID P1-00 — Governance / Contract Enforcement

| 项 | 内容 |
| --- | --- |
| Acceptance Criterion | every IN scope maps once to WP/DAG/criterion/DoD; no unauthorized WP or scope expansion（E-00） |
| Test/Evidence | `tests/test_phase1_governance.py`（13 项） |
| Result | PASS |
| Artifact/Path | `apps/backend/src/hfm/phase1/governance.py`（WP 注册 + 36 边 DAG + 前置门禁 + 负向守卫 + 追踪矩阵） |
| Verification command | `cd apps/backend && ../../.venv/bin/pytest tests/test_phase1_governance.py -q`（13 passed） |

证据明细（E-00 / DOD-01 / DOD-02 / DOD-11）：

```text
DAG shape:      14 nodes / 36 edges / acyclic / 0 unreachable / 0 deferred / 0 rejected（validate_dag）
Traceability:   14/14 IN items mapped once; 0 orphan scope; 0 orphan WP; 0 duplicate（verify_traceability）
DAG gating:     blocking predecessors enforced（P1-01←P1-00; P1-02←P1-00,P1-01; P1-11←P1-07..P1-13 …）
Unauthorized:   PASS 拒绝未满足阻断前置的 WP；未知 WP/状态拒绝（complete 守卫）
Negative:       CD-7 NONEXISTENT; Production HFB Import NOT AUTHORIZED; 无 DEFERRED/REJECTED 为正向 WP;
                Phase 0.4 baseline 0167b17 保持（negative_guards）
契约注记:       冻结 DAG 对 P1-09 的阻断前置仅为 P1-00（36 边契约权威）；Inventory 的
                Preconditions 列为输入清单而非 DAG 门禁 — 实施与冻结 DAG 逐边一致（编码自文档提取）。
```

## WP-ID P1-01 — Content Admission / Canonical Content Core

| 项 | 内容 |
| --- | --- |
| Acceptance Criterion | invalid provenance/rights is rejected; admitted content has source/version state; no metadata-only admission（E-01） |
| Test/Evidence | `tests/test_content_admission.py`（12 项）+ 迁移测试 `test_migration_0009_content_artifacts` |
| Result | PASS |
| Artifact/Path | `apps/backend/src/hfm/models/content_artifact.py` + `apps/backend/src/hfm/repositories/content_artifact.py` + `apps/backend/alembic/versions/0009_p1_content_admission.py` |
| Verification command | `cd apps/backend && ../../.venv/bin/pytest tests/test_content_admission.py -q`（12 passed） |

证据明细（E-01 fail-closed；AB-06；AB invariant 1/5）：

```text
Valid admission:      source+version+hash+provenance+rights+validation recorded → ADMITTED
Fail-closed:          5 类拒绝全部可观测（rejection log = artifact 行 + reason）:
                      missing_source_provenance / metadata_only_admission /
                      invalid_provenance / unknown_rights / invalid_version_binding
Malformed input:      source_id 缺失 → ValueError（fail-closed raise）
Metadata-only:        content=b"" → REJECTED metadata_only_admission（CHECK: admitted 须有 hash）
Unknown rights:       RightsStatus.UNKNOWN → REJECTED（AB invariant 5: unknown rights never admitted）
Idempotency:          UNIQUE(source_id, content_hash) + 幂等返回既有记录（1 记录）
Immutability:         source/content_hash/admission_state/rejection_reason immutable（I4 @validates + update 拒绝）
No publication:       模型无 approved/published/public_visible/release 字段（ADMITTED ≠ APPROVED ≠ PUBLISHED，P1-09）
No HFB dependency:    模块零 hfb 引用（测试断言）
DB constraints:       ck_content_artifacts_rejection_has_reason / source_present /
                      content_hash_present / uq_source_hash（迁移门禁验证）
```

## 回归

```text
pytest: 260 passed / 0 failed / 1 warning（P3 Starlette/httpx — 既有，未修复）
mypy: PASS（107 source files）· Ruff: PASS · Ruff Format: PASS（117 files）
Frontend: ESLint PASS · Prettier PASS · vue-tsc PASS · Vitest 24 passed · Build PASS
Alembic head: 0009（0001→0009 链 + downgrade 门禁测试 PASS）
```

## 边界确认

```text
- 未实施 P1-02…P1-13、未实施 Display/AI/3D/VR/XR/Virtual Training/clinical recommendation
- 无生产 HFB 导入（NOT PERFORMED）；无 HFB runtime 依赖；无 HFB FK/身份复制；未执行 M5
- CD-7: NONEXISTENT
- 未修改任何冻结治理工件（docs/governance/HFM-PHASE1-* 与 Phase 0.4 全部未动）
- ADR-01/02/05/06/07 均未被实施变更
```

## 完成判定

```text
P1-00 = PASS（E-00 证据齐全：14/14 追踪、36 边 DAG 验证、前置门禁、负向守卫）
P1-01 = PASS（E-01 证据齐全：fail-closed 拒绝 5 类 + 幂等 + immutable + 无发布语义）
```

# HFM Phase 0.4 — CORE-COMPLETION Evidence（修正版）

Date: 2026-08-28 · Phase 0.4 — Core Domain Completion Work Package（CORE-COMPLETION dry-run，修正后）
性质：COMPLETION EVIDENCE PACKAGE（修正候选 — 待 Codex 复验；非冻结；非 actual import）
机器可读证据：`artifacts/audit/hfm-phase0.4-core-completion.json`

## 0. 失败候选超期声明（§25-26）

```text
Failed Previous Candidate:
e26598f3be8b3e8b9decd902c9a5e929f0e59e2a

Previous Acceptance:
FAIL

Correction Reasons:
C1 synthetic absent-field assertion（biography）
C2 Edition.file_path 冒充 SourceRef.page_location
dedup identity 不足（work_title, version_name）

本证据包明确超期并取代 e26598f 的执行证据；不宣称 e26598f 曾被接受。
```

## 1. Execution Identity

```text
Work Package:
CORE-COMPLETION（非 CD-7；不扩展 Frozen CD 序列）

Task Type:
CANDIDATE CORRECTION（after Codex substantive acceptance FAIL）

Candidate Status:
CORRECTED / AWAITING CODEX ACCEPTANCE
```

## 2. Governing Baselines

```text
Governance Baseline:
00ed3ff244578d975c2748fa9d85a8d14e4c7c37

Implementation Baseline:
d08e343dbbc52dedfcbd5bba69918e6a4b74256d

Source Baseline:
03755b57ec0e4c8023d1447619f7d6ead9e44d73

Original Core Domain Contract Baseline:
366df69715613022326eb7a3c06ae7f145ebacb9
```

## 3. Authorization Boundary

```text
AUTHORIZED: CORE-COMPLETION tooling / tests / execution evidence 修正（3 个已接受 P1 阻塞）

NOT AUTHORIZED: CD-7 / Phase 1 / new Core scope / actual import / governance revision /
new runtime models / Alembic migrations
```

## 4. Frozen Source Identity

```text
HFB Snapshot:
03755b57ec0e4c8023d1447619f7d6ead9e44d73

Source Artifact:
apps/frontend/src/data/huangfu_mi_exhibition.json（git-tracked at snapshot）

Source SHA256:
94467890f99ebe7d77e1498d04238d460cf80c5cc1ef5b66892397d4a9062cdb

Mutable HFB Used:
NO

hfb_dev.db Used:
NO

Actual source candidate breakdown:
Person actual applicable fields:   4（birth_year / death_year / birth_place / dynasty）
Edition-derived records:          92
SourceRef.page_location rows:      0
Citation rows:                     0
Source universe:                   96（4 + 92）
```

## 5. Isolation Method

```text
Isolation Mode:
disposable temporary SQLite（tempfile，运行后删除）

Persistent State After Dry-Run:
NONE

Production Database Modified:
NO

Production Records Imported:
0

Actual Persistent HFB Import:
NO
```

## 6. Migration Path

```text
extract（快照追踪文件，sha256 校验）
→ validate（C1 字段存在性 + Edition schema 校验）
→ transform（C1 真实字段 → Assertion；C2/C3 规则由单测覆盖，快照 0 行）
→ dry-run（一次性 SQLite target 写入转换候选 + 删除）
→ reconciliation（六计数 + 宇宙核算 + 候选集 sha256）
```

## 7. Reconciliation Schema

```text
Required Schema（Migration Strategy §6）:
source / accepted / transformed / rejected / duplicate / target

Scope:
六字段 = 转换类（C1+C2+C3）；源宇宙 = 转换源 + 非转换保留 Edition（§13）

Equations（修正后）:
transformation scope: source = accepted + rejected + duplicate（4 = 4 + 0 + 0）
accept_transform:     accepted = transformed（4 = 4）
target:               target = transformed − duplicate_consumed（4 = 4 − 0）
universe:             source_universe = transformation_source + preserved_non_transforming
                      （96 = 4 + 92）
```

## 8. Run A Results

```text
source:      4
accepted:    4
transformed: 4
rejected:    0
duplicate:   0
target:      4

by class:
C1 PERSON_BIO:      source=4  accepted=4  transformed=4  rejected=0 duplicate=0 target=4
C2 SOURCE_REF_LOCATOR: source=0 accepted=0 transformed=0 rejected=0 duplicate=0 target=0
C3 CITATION_TARGET: source=0 accepted=0 transformed=0 rejected=0 duplicate=0 target=0

source_universe: 96
edition_preserved: 92
observed target rows: 4
```

## 9. Run B Results

```text
与 Run A 逐项一致（six counts / candidate_set_sha256 / rejections / duplicates / target state）
```

## 10. Reconciliation Analysis

```text
Reconciliation:
PASS

C1 Corrected:
  4 actual person fields transformed → 4 assertion candidates
  synthetic absent-field candidates = 0（无 biography 合成主张）

C2 Corrected:
  real SourceRef.page_location rows = 0 → real transformations = 0
  Edition.file_path substitution = 0（Edition 永不进入 C2 路径）
  transformation rule verified by deterministic tests（真实 page_location fixture）

C3:
  real rows = 0；zero-row rule verified by tests（Codex 已接受）

Edition Contract Role:
  source-preservation candidate — non-transforming（Frozen Strategy §7 未定义
  Edition 转换类）；92 条验证后保留为源证据；不计入 C2、不进入转换 target
```

## 11. Rejection Analysis

```text
Rejected: 0
Rejection Rules（确定性，测试覆盖）: missing_source_record_id / missing_work_title /
missing_version_name / missing_file_path / non_numeric_size_mb
异常不计入 rejected（fail-closed，§23）。
```

## 12. Duplicate Analysis

```text
Duplicates: 0（转换类与保留类均无）

Duplicate Identity Rule（P1-3 修正）:
source-grounded = migration_version | source_sha256 | source_record_id
（Edition = edition.id 不可变源身份；非 (work_title, version_name) 部分元组）

Semantics:
相同逻辑迁移候选 → 相同 identity；合法不同源记录（同 title/version/publisher/year 而 id 不同）
→ 不折叠；确定性、与遍历顺序无关。
```

## 13. Hash / Checksum Evidence

```text
Hash Algorithm: SHA-256（hfm.core.hashing — 仓库既定）
Source Hash: 94467890f99ebe7d77e1498d04238d460cf80c5cc1ef5b66892397d4a9062cdb
Candidate Set SHA256（修正后）: 94179e7e11a95612…（与失败候选 916784ac… 不同 — 候选宇宙已变）
Preservation Manifest SHA256: 见机器可读证据
Manifest: NOT REQUIRED（契约未要求 manifest）
```

## 14. Reproducibility Evidence

```text
Reproducibility:
PASS（Run A == Run B；归一化比较排除 timestamps/temp db paths/run ids；
比较 six counts / candidate identities / candidate-set hash / rejections / duplicates / target state）
```

## 15. Idempotency Evidence（§22 — 同 target 强证明）

```text
Same-target idempotency（Strategy §5）:
Application 1 on disposable target:  4 rows
Application 2 on SAME target:        new rows = 0
Final target:                        4 rows

机制: candidate_id PRIMARY KEY + INSERT OR IGNORE；same source snapshot +
same migration version → same target state；重复执行不产生重复记录。
```

## 16. Failure-Semantics Evidence

```text
Unhandled Migration Errors: 0
Silent Failure Paths: 0（fail-closed：异常 → 错误记录 + 非零退出）
测试: test_fail_closed
```

## 17. Inventory Completion Evidence

```text
Frozen Inventory Assets: 28
Frozen Dispositions Preserved: 28/28（未重估）
COMPLETION_IMPLEMENTATION_REQUIRED: 0
Inventory Completion Evidence: PASS
（无 post-phase deferred 资产被实现为 runtime；CA-025 义务经 C1 legacy_governance 标记满足）
```

## 18. Canonical Boundary Regression

```text
Unauthorized Canonical Expansion: NO
New Core Runtime Models: 0
New SQLAlchemy Domain Models: 0
New Alembic Migrations: 0
CA-026: BRIDGE_FROZEN（opaque created_by 未变；无 User/Auth/RBAC）
Identity/Auth Expansion: NO
SourceRef: CLOSED（未重开）
```

## 19. I1-I6 Regression

```text
I1 Provenance: PASS（修正后实质证明 — 每个候选携带 source_artifact + 真实 source_field/
source_record_id + migration_rule；C1 仅真实字段；Edition 保留候选带源记录 id）
I2 Version Reproducibility: PASS（回归）
I3 Assertion Coexistence: PASS（回归）
I4 No Silent Overwrite: PASS（回归）
I5 Stable Identity: PASS（确定性 uuid5 候选 identity；回归）
I6 HFB Independence: PASS（completion 模块零 hfb 引用；runtime 无 HFB 依赖）
```

## 20. Test Regression

```text
CORE-COMPLETION tests（修正后）: 24 passed / 0 failed / 0 skipped
Backend regression: 235 passed / 0 failed / 1 warning（P3 Starlette/httpx — 既有，未修复）
mypy: PASS（101 source files）· Ruff: PASS · Ruff Format: PASS（110 files）
Frontend: ESLint PASS · Prettier PASS · vue-tsc PASS · Vitest 24 passed · Build PASS
Runtime: /health /ready /version /live /config 200 · X-Request-ID PASS · /config 零敏感
```

## 21. Phase Boundary

```text
Phase 1 Leakage: NO
Actual persistent import: NO
CD-7: NONEXISTENT
```

## 22. Definition-of-Done Matrix（独立重建，§42）

| Requirement（DoD） | Owner | Evidence | Result |
| --- | --- | --- | --- |
| Schema/model complete | CD-0…CD-6 | 迁移 0001-0008 + 批验收归档 | PASS |
| Migration complete | CD-0…CD-6（schema）+ CORE-COMPLETION（data dry-run） | Alembic 链完整；修正 dry-run 执行 | PASS |
| Service/API complete | Core 冻结范围 | CD 报告（Service/API 0）+ 系统端点 | PASS |
| Tests complete | 各批 + CORE-COMPLETION | 235 passed（含 24 修正测试） | PASS |
| Provenance complete（I1） | CD-3/4/6 + CORE-COMPLETION | I1 实质证明（真实字段溯源） | PASS |
| Version reproducibility complete（I2） | CD-2/5 | I2 PASS + 回归 | PASS |
| No HFB runtime dependency（I6） | 全批 | I6 PASS + 扫描 | PASS |
| Data migration dry-run complete | CORE-COMPLETION | 修正 dry-run（reconciliation/reproducibility/idempotency 全 PASS） | PASS |
| Regression green | 全批 | 235 passed + 前端全过 | PASS |

```text
Definition of Done Requirements: 9
Definition of Done Passed: 9
Definition of Done Blocked: 0
Definition of Done: PASS（作为修正候选；待 Codex 复验）
```

## 23. Completion Candidate Status

```text
Failed Previous Candidate: e26598f（ACCEPTANCE FAIL）
New CORE-COMPLETION Candidate: 修正提交 SHA（待记录）

CORE-COMPLETION:
CORRECTED / AWAITING CODEX ACCEPTANCE

DATA MIGRATION DRY-RUN:
EXECUTED / PASS（修正后）

RECONCILIATION:
PASS

Reproducibility: PASS
Same-Target Idempotency: PASS（second application new rows = 0）
Hash/Checksum: PASS（sha256）

PHASE 0.4 COMPLETION EVIDENCE:
NEW CANDIDATE / NOT ACCEPTED

PHASE 0.4 COMPLETION FREEZE:
NOT AUTHORIZED

CD-7:
NONEXISTENT / NOT AUTHORIZED

PHASE 1:
NOT AUTHORIZED

Frozen Governance Semantic Changes:
0
```

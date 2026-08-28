# HFM Phase 0.4 — CORE-COMPLETION Evidence

Date: 2026-08-28 · Phase 0.4 — Core Domain Completion Work Package（CORE-COMPLETION dry-run）
性质：COMPLETION EVIDENCE PACKAGE（CANDIDATE — 待 Codex 验收；非冻结；非 actual import）
机器可读证据：`artifacts/audit/hfm-phase0.4-core-completion.json`

## 1. Execution Identity

```text
Work Package:
CORE-COMPLETION（非 CD-7；不扩展 Frozen CD 序列）

Task Type:
PHASE 0.4 COMPLETION EVIDENCE EXECUTION（data migration dry-run + reconciliation）

Candidate Status:
IMPLEMENTED / AWAITING CODEX ACCEPTANCE
```

## 2. Governing Baselines

```text
Governance Baseline:
00ed3ff244578d975c2748fa9d85a8d14e4c7c37（Phase 0.4 Amended Contract Baseline）

Implementation Baseline:
d08e343dbbc52dedfcbd5bba69918e6a4b74256d（CD-6 Implementation Baseline）

Source Baseline:
03755b57ec0e4c8023d1447619f7d6ead9e44d73（HFB Source Snapshot）

Original Core Domain Contract Baseline:
366df69715613022326eb7a3c06ae7f145ebacb9
```

## 3. Authorization Boundary

```text
AUTHORIZED: inspect frozen sources · isolated dry-run · reconciliation ·
reproducibility · idempotency · hash/checksum（适用处）· evidence artifacts · 必要测试

NOT AUTHORIZED: new Core models · EntityRelation/Place 实现 · User/Auth/RBAC ·
Phase 1 · CD-7 · actual production HFB import · live HFM DB mutation
```

## 4. Frozen Source Identity

```text
Source Artifact:
apps/frontend/src/data/huangfu_mi_exhibition.json @ 03755b57…

Source Type:
HFB 快照内已追踪数据文件（git-tracked at snapshot；非 untracked hfb_dev.db —
后者被 source-integrity 规则排除：gitignored 可变工作数据，§2 禁止）

Source sha256:
94467890f99ebe7d77e1498d04238d460cf80c5cc1ef5b66892397d4a9062cdb

Source Bytes:
385132

Current HFB HEAD:
03755b57ec0e4c8023d1447619f7d6ead9e44d73（== snapshot；本机工作树数据未使用）

Current HFB HEAD Used:
NO（仅使用快照追踪文件）

Source Records:
persons=1（person_overview，含 5 个单值传记字段）
editions=92（classical_editions）
citations=0（快照内无可追踪 citation-shaped 记录；untracked DB 排除 → C3 诚实为 0；
映射规则由单测覆盖）
```

## 5. Isolation Method

```text
Isolation Mode:
disposable temporary SQLite（tempfile，运行后删除）

Persistent State After Dry-Run:
NONE

Production Database Modified:
NO

Production Database Records Imported:
0

Actual Persistent HFB Import:
NO
```

## 6. Migration Path

```text
extract（快照追踪文件，sha256 校验）
→ validate（确定性规则：C2 schema/类型/引用完整性）
→ transform（C1/C2/C3 冻结规则，Migration Strategy §7）
→ dry-run（一次性 SQLite target 写入候选 + 删除）
→ reconciliation（六计数 + 候选集 sha256）
```

## 7. Reconciliation Schema

```text
Required Reconciliation Schema（Migration Strategy §6）:
source      — 考虑的候选源记录总数
accepted    — 契约下准入转换的源记录
transformed — 成功转换为 target-form 候选的源记录
rejected    — 确定性规则拒绝的源记录
duplicate   — 按策略检测的重复记录
target      — dry-run 产出的最终 target 候选记录

Record Unit:
源记录 = 原子 claim（C1 单值字段 / C2 edition / C3 citation）；候选与源 1:1
```

## 8. Run A Results

```text
source:      97
accepted:    97
transformed: 97
rejected:    0
duplicate:   0
target:      97

by class:
C1 PERSON_BIO:       source=5  accepted=5  transformed=5  rejected=0 duplicate=0 target=5
C2 VERSION_LOCATOR:  source=92 accepted=92 transformed=92 rejected=0 duplicate=0 target=92
C3 CITATION_TARGET:  source=0  accepted=0  transformed=0  rejected=0 duplicate=0 target=0
```

## 9. Run B Results

```text
source:      97
accepted:    97
transformed: 97
rejected:    0
duplicate:   0
target:      97

by class: 与 Run A 逐项一致
```

## 10. Reconciliation Analysis

```text
Reconciliation:
PASS

Equations（契约派生，非发明）:
source = accepted + rejected + duplicate         → 97 = 97 + 0 + 0 ✓
accepted = transformed                           → 97 = 97 ✓
target = transformed − duplicate_consumed        → 97 = 97 − 0 ✓

Inventory Contractually Reconciled:
YES（28/28 disposition 未重估；COMPLETION_IMPLEMENTATION_REQUIRED = 0）
```

## 11. Rejection Analysis

```text
Rejected:
0

Rejection Rule（确定性，单元测试覆盖）:
missing_work_title / missing_version_name / missing_file_path /
absolute_or_remote_file_path / non_numeric_size_mb

Real-data rejection:
0（92 条 classical_editions 全部通过校验 — 真实结果，非伪造）

解释:
拒绝路径已由规则级测试验证（含 4 类原因的构造记录）；真实数据无违规记录。
异常/崩溃不作为普通 rejected 计数（§17；fail-closed 另见 §16）。
```

## 12. Duplicate Analysis

```text
Duplicates:
0

Duplicate Rule（确定性，Strategy §5 语义）:
去重 = migration version + source 哈希；记录级 key = (work_title, version_name)

Real-data duplicates:
0（92 条 (work_title, version_name) 均唯一 — 真实结果）

Duplicate 路径已由规则级测试验证（同 key → duplicate；不同 key → 非 duplicate）。
重复检测不依赖运行时顺序（key 为纯函数）。
```

## 13. Hash / Checksum Evidence

```text
Hash Algorithm:
SHA-256（仓库既定算法：hfm.core.hashing，migrated Batch 1 asset）

Source Artifact Hash:
sha256 = 94467890f99ebe7d77e1498d04238d460cf80c5cc1ef5b66892397d4a9062cdb

Candidate Set Hash（每 run，canonical JSON）:
Run A candidate_set_sha256 == Run B candidate_set_sha256
（见 artifacts/audit/hfm-phase0.4-core-completion.json）

Manifest:
NOT REQUIRED（契约未要求 manifest）
```

## 14. Reproducibility Evidence

```text
Reproducibility:
PASS

Comparison:
Run A == Run B（归一化比较 — §21）
  排除字段: timestamps / temp db paths / run ids（易变元数据，非实质数据）
  比较键: reconciliation / total / rejections / duplicates /
          candidate_set_sha256 / target_candidate_count
Same source identity + same transformation rules + same counts + same evidence output: YES
```

## 15. Idempotency Evidence

```text
Idempotency:
PASS

Evidence:
重跑（fresh disposable target）→ candidate id 集合逐项一致；
target 计数一致（97）；无新增/重复候选（candidate_id 为确定性 uuid5 派生）
semantics: same source snapshot + same migration version → same target state（Strategy §5）
不暗示 actual import。
```

## 16. Failure-Semantics Evidence

```text
Unhandled Migration Errors:
0

Silent Failure Paths:
0（fail-closed：任何解析/转换/DB 异常 → 错误记录 + 非零退出；异常不计入
accepted/transformed/rejected 普通路径）

测试: test_fail_closed / 非法 target_type → ValueError 传播
```

## 17. Inventory Completion Evidence

```text
Frozen Inventory Assets:
28

Final Dispositions Preserved:
28（未重估：IMPLEMENTED_CORE 15 / POST_PHASE_DEFERRED 11 / NON_RUNTIME_GOVERNANCE 1 /
BRIDGE_FROZEN 1 / COMPLETION_EVIDENCE 0 / COMPLETION_IMPLEMENTATION_REQUIRED 0）

Inventory Contractually Reconciled:
YES

Inventory Completion Evidence:
PASS（无 COMPLETION_IMPLEMENTATION_REQUIRED 资产；无 post-phase deferred 资产被意外实现；
CA-025 governance 义务经 dry-run evidence 满足 — LegacyProvenanceDecision.pending 治理标记
内嵌于 C1 assertion 候选）
```

## 18. Canonical Boundary Regression

```text
Unauthorized Canonical Expansion:
NO

新 runtime 模型:
0（未引入 EntityRelation / Place / Concept / Acupoint / Manifestation / Book /
ClassicalVersion / VersionRelation / Sentence / Token / Variant / TextUnit / Legacy
Provenance 的任何 runtime model）

CA-026:
BRIDGE_FROZEN（opaque created_by 语义未变；无 User/Auth/RBAC 引入）
Identity/Auth Expansion:
NO

SourceRef:
CLOSED（未重开/未重定义）
```

## 19. I1-I6 Regression

```text
I1 Provenance: PASS（事件证据链/Assertion 溯源回归；C1 候选内嵌 evidence 溯源）
I2 Version Reproducibility: PASS（C2 locator 内嵌 version 上下文；pinned 语义回归）
I3 Assertion Coexistence: PASS（CD-4 回归）
I4 No Silent Overwrite: PASS（CD-4/5/6 immutable 回归）
I5 Stable Identity: PASS（candidate id 确定性派生；CD-0..6 stable ID 回归）
I6 HFB Independence: PASS（completion 模块零 hfb 引用；runtime 无 HFB 依赖）
```

## 20. Test Regression

```text
CORE-COMPLETION semantics tests（新增）:
14 passed / 0 failed / 0 skipped

Full backend regression:
225 passed / 0 failed / 1 warning（P3 Starlette/httpx — 既有，未修复）

Command:
apps/backend: ../../.venv/bin/pytest（225 passed）
Ruff: PASS（110 files）· Ruff Format: PASS（110 files）· mypy: PASS（101 source files）
Frontend: ESLint PASS · Prettier PASS · vue-tsc PASS · Vitest 24 passed · Build PASS
```

## 21. Phase Boundary

```text
Phase 1 Leakage:
NO

Actual persistent HFB import:
NO

Public portal / publication snapshot / medical compliance / ICH media / teaching / Auth/RBAC:
NOT AUTHORIZED / NOT IMPLEMENTED

CD-7:
NONEXISTENT
```

## 22. Definition-of-Done Matrix

| Requirement（DoD） | Owner | Evidence | Result |
| --- | --- | --- | --- |
| Schema/model complete | CD-0…CD-6 | 迁移 0001-0008 + 各批验收归档 | PASS |
| Migration complete | CD-0…CD-6（schema）+ CORE-COMPLETION（data dry-run） | Alembic 链完整；本包 dry-run 执行 | PASS |
| Service/API complete | Core 冻结范围（Service 0 / API 0） | CD 实施报告（API Changes: 0 / Service Changes: 0）+ 系统端点 | PASS |
| Tests complete | 各批 + CORE-COMPLETION | 225 passed（含 14 新增） | PASS |
| Provenance complete（I1） | CD-3/4/6 | I1 PASS + 证据链测试 | PASS |
| Version reproducibility complete（I2） | CD-2/5 | I2 PASS + 回归 | PASS |
| No HFB runtime dependency（I6） | 全批 | I6 PASS + 扫描 | PASS |
| Data migration dry-run complete | **CORE-COMPLETION** | 本证据包（dry-run PASS / reconciliation PASS / reproducibility PASS / idempotency PASS） | PASS |
| Regression green | 全批 | 225 passed + 前端全过 | PASS |

```text
Definition of Done Requirements:
9

Definition of Done Passed:
9

Definition of Done Blocked:
0

Definition of Done:
PASS（作为 CORE-COMPLETION candidate；待 Codex 独立验收）
```

## 23. Completion Candidate Status

```text
CORE-COMPLETION:
IMPLEMENTED / AWAITING CODEX ACCEPTANCE

DATA MIGRATION DRY-RUN:
EXECUTED / PASS

RECONCILIATION:
PASS

Reproducibility:
PASS

Idempotency:
PASS

Hash/Checksum:
PASS（适用处；sha256）

PHASE 0.4 COMPLETION EVIDENCE:
CANDIDATE / NOT CLOSED

PHASE 0.4 COMPLETION FREEZE:
NOT AUTHORIZED

CD-7:
NONEXISTENT / NOT AUTHORIZED

PHASE 1:
NOT AUTHORIZED

Frozen Governance Semantic Changes:
0
```

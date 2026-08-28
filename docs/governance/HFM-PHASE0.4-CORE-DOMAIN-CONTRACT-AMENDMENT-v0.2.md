# HFM Phase 0.4 — Core Domain Contract Amendment v0.2

Status: GOVERNANCE CANDIDATE（待 Codex 独立验收；**未冻结**）· Date: 2026-08-28 · Phase 0.4
模式：`ORIGINAL FROZEN CONTRACT + EXPLICIT RECONCILIATION AMENDMENT = NEW CONTRACT CANDIDATE`
原 v0.1 Frozen 历史保持真实：**不通过原地修改把原合同制造成"从来没有冲突"**。

---

## 1. Amendment Identity

```text
Document:
docs/governance/HFM-PHASE0.4-CORE-DOMAIN-CONTRACT-AMENDMENT-v0.2.md

Amendment Type:
CONTRACT RECONCILIATION（仅治理语义修订）

Authorizing Scope:
GOVERNANCE CONTRACT AMENDMENT — AUTHORIZED
PRODUCTION CODE / TESTS / MIGRATIONS / DATA MIGRATION DRY-RUN / ACTUAL IMPORT / COMPLETION WORK PACKAGE:
NOT AUTHORIZED（本轮）

Candidate Status:
IMPLEMENTED / AWAITING CODEX ACCEPTANCE（非 ACCEPTED / 非 FROZEN / 非 BASELINE）
```

## 2. Original Contract Identity

```text
Core Domain Contract Baseline:
366df69715613022326eb7a3c06ae7f145ebacb9

Starting Implementation Baseline:
d08e343dbbc52dedfcbd5bba69918e6a4b74256d（CD-6 Implementation Baseline）

HFB Source Snapshot:
03755b57ec0e4c8023d1447619f7d6ead9e44d73

Original Contract Documents（v0.1，历史真实，不改写）:
docs/domain/HFM-CORE-DOMAIN-SCOPE-v0.1.md
docs/domain/HFM-CANONICAL-DOMAIN-MODEL-v0.1.md
docs/domain/HFM-ASSERTION-CONTRACT-v0.1.md
docs/domain/HFM-EVIDENCE-LINEAGE-CONTRACT-v0.1.md
docs/migration/hfb/HFM-PHASE0.4-CORE-ASSET-INVENTORY.md
docs/migration/hfb/HFM-CORE-DATA-MIGRATION-STRATEGY-v0.1.md
docs/migration/hfb/HFM-PHASE0.4-CORE-MIGRATION-DAG.md
docs/governance/HFM-CORE-DOMAIN-DEFINITION-OF-DONE.md
（自 366df69 起零修改 — 见 §52 diff 验证）
```

## 3. Triggering Audit Findings（如实记录，不淡化）

```text
Completion Final Audit:
BLOCK

Root-Cause Reconciliation Audit:
GOVERNANCE DECISION REQUIRED

CD Implementation Scope（Layer A）:
PASS

Frozen DAG:
EXHAUSTED（CD-0…CD-6 全部实现；无 CD-7 定义）

Inventory Closure（Layer B）:
FAIL

Definition of Done（Layer C）:
FAIL

Frozen Contract Internal Consistency:
FAIL

P0:
1 — Frozen Inventory / Canonical Model / DAG / DoD 未定义唯一、合法、可完成的 Phase 0.4 target

P1-1:
CONTRACT INTERNAL CONFLICT / DAG DESIGN OMISSION

P1-2:
DOD ASSIGNMENT OMISSION / EVIDENCE-ONLY GAP
```

## 4. Conflict Statement

原 v0.1 合同在以下语义上不一致（全部如实保留于原文档）：

1. **Inventory 与 DAG 不对齐**：28 个 CA asset 的 Frozen verdict（REUSE/EXTEND/ADAPT/NEW）与 DAG 的 6 个 CD 节点（CD-0…CD-6）不一一对应；Inventory 没有定义"每个 asset 的 Phase 0.4 completion 归属"。
2. **Canonical Model 与 DAG 不对齐**：Canonical Model §2 列出 13 个 atomic concepts（Place / Concept / Acupoint / Manifestation / Book / ClassicalVersion / VersionRelation / Sentence / Token / Variant / TextUnit / Legacy Provenance 等），DAG 未分配节点，无 completion 语义。
3. **DoD 无 execution owner**：DoD 要求 "Data migration dry-run complete"，但 DAG 无节点承担该 obligation；`CD-7` 不存在，无法挂载。
4. **CA-002 归属冲突**：Canonical Model 命名 EntityRelation（Entity↔Entity）；CD-1 排除 entity_relations 表；CD-6 仅实现 EventRelation；DAG 无剩余节点。
5. **CA-026 归属模糊**：CandidateExtraction→Assertion 桥（5 态候选管线）在 Core 中仅有 `created_by` 不透明引用占位，无正式治理裁决。
6. **"CD-0…CD-6 PASS ⇒ Phase 0.4 PASS" 推导无效**：缺少 Inventory / Canonical Boundary / DoD 三层闭合证明。

## 5. Governing Principles

```text
P1 历史真实: 原 v0.1 文档不可语义改写；Amendment 是叠加层，不是改写层。
P2 显式裁决: 所有冲突/歧义必须以 Final Disposition 显式解决，禁止 AMBIGUOUS/TBD/LATER/MAYBE。
P3 证据驱动: 每个裁决必须引用 Frozen evidence（原 Inventory verdict / DAG 节点 / Canonical 表 /
   Assertion 契约 §5 / Migration Strategy / DoD）。
P4 分离义务: runtime implementation 与 completion evidence 必须分离（尤其 CA-025）。
P5 生命周期归属: 未在本轮实现、也未授权的资产必须保留为未来受治理资产（POST_PHASE_DEFERRED），
   不得从历史 Inventory 删除，不得静默放弃。
P6 最小扩张: 本轮只修订治理语义；不新增 CD 节点、不新增 runtime 对象、不授权实现。
P7 不重写历史: CD-0…CD-6 保持有效冻结实现节点，不重新验收；过往 PASS 不因 Amendment 变成伪造历史。
```

## 6. Inventory Reconciliation（28 个 CA asset 最终裁决）

Final Disposition 语义（§10 授权集合）：

```text
IMPLEMENTED_CORE                — Phase 0.4 runtime requirement 已在 CD-0…CD-6 实现并验收
POST_PHASE_DEFERRED             — 非 Phase 0.4 completion runtime 要求；保留为未来受治理资产；
                                  本轮未授权；后续需显式授权
NON_RUNTIME_GOVERNANCE          — 治理层资产；Phase 0.4 不需要 runtime 对象
COMPLETION_EVIDENCE             — Phase 0.4 义务为 completion evidence（dry-run/reconciliation），
                                  非实现
BRIDGE_FROZEN                   — 桥占位（CA-026）已足够 Phase 0.4；未来身份绑定需另行治理
COMPLETION_IMPLEMENTATION_REQUIRED — 存在 mandatory missing runtime object（本轮无；需 Frozen evidence）
```

| CA ID | Frozen Asset | Original Verdict | Phase 0.4 Runtime Required? | Completion Required? | Final Disposition | Evidence |
| --- | --- | ---: | ---: | ---: | --- | --- |
| CA-001 | Entity + EntityType（+ AcademicRelation） | ADAPT | YES | — | IMPLEMENTED_CORE | CD-1 Entity/EntityType；关系语义由 CD-6 EventRelation + CD-4 RELATIONAL Assertion 承载（Assertion 契约 §5） |
| CA-002 | EntityRelation（graph，9 类） | REUSE | NO | — | POST_PHASE_DEFERRED | DAG 无节点；CD-1 Scope 明确排除 entity_relations 至 CD-6（Person/Event）；Assertion 契约 §5（9 类 → RELATIONAL Assertion）；见 §13-15 裁决 |
| CA-003 | Person | ADAPT | YES | — | IMPLEMENTED_CORE | CD-1 Person（entity_id 1:1；单值字段转写契约） |
| CA-004 | Event | NEW | YES | — | IMPLEMENTED_CORE | CD-6 Event（CA-004 即 CD-6 NEW） |
| CA-005 | Institution | REUSE | YES | — | IMPLEMENTED_CORE | CD-0 institutions |
| CA-006 | Concept / Acupoint（TCMEntity） | EXTEND | NO | — | POST_PHASE_DEFERRED | 专业领域模型（G1 边界）；CD-1 已登记 EntityType concept/acupoint 值（typed 登记）；Assertion 契约 G1：仅历史文本主张；Scope §6.3 |
| CA-007 | Work | REUSE | YES | — | IMPLEMENTED_CORE | CD-2 works |
| CA-008 | Edition / Manifestation | REUSE | YES（Edition） | — | IMPLEMENTED_CORE | CD-2 editions；Manifestation 概念见 §18 概念表（DAG CD-2 节点未含 → post-phase） |
| CA-009 | NormalizedText / 辑佚 | EXTEND | NO | — | POST_PHASE_DEFERRED | 细粒度文本归一化；DAG 无节点；Passage/Locator 覆盖 Phase 0.4 粒度 |
| CA-010 | Book | REUSE | NO | — | POST_PHASE_DEFERRED | HFB legacy naming；Work 承载其 Phase 0.4 语义（§24） |
| CA-011 | ClassicalVersion | EXTEND | NO | — | POST_PHASE_DEFERRED | Version 承载；edition_type/review_status 为 HFB 编辑字段（§24） |
| CA-012 | Version | REUSE | YES | — | IMPLEMENTED_CORE | CD-2 versions（is_formal_source / withdrawn_at / parent_version_id） |
| CA-013 | VersionRelation | REUSE | NO | — | POST_PHASE_DEFERRED | 版本谱系由 Version.parent_version_id 承载（I2 PASS）；独立关系表非 Phase 0.4 要求（§24） |
| CA-014 | Chapter | REUSE | YES | — | IMPLEMENTED_CORE | CD-2 chapters |
| CA-015 | Passage | REUSE | YES | — | IMPLEMENTED_CORE | CD-2 passages（trace_id UUIDv5 溯源） |
| CA-016 | Sentence / Token / Variant | ADAPT | NO | — | POST_PHASE_DEFERRED | 细粒度文本模型；Passage/Locator 覆盖 Phase 0.4 粒度；Variant 语义可由 TEXTUAL Assertion 承载（Assertion 契约 §5；§25） |
| CA-017 | Commentary | REUSE | NO | — | POST_PHASE_DEFERRED | DAG 无节点 |
| CA-018 | TEI 持久化 | REUSE | NO | — | POST_PHASE_DEFERRED | DAG 无节点 |
| CA-019 | Source（身份 + rights 元数据） | ADAPT | YES | — | IMPLEMENTED_CORE | CD-0 sources（identity/rights；准入状态机留治理） |
| CA-020 | SourceRef | REUSE | YES | — | IMPLEMENTED_CORE | CD-0 source_refs；**CLOSED**（§27：不再进入待实现列表） |
| CA-021 | Evidence | REUSE | YES | — | IMPLEMENTED_CORE | CD-3 evidences（Level 1-4 / taint / content_hash / I1） |
| CA-022 | Citation | ADAPT | YES | — | IMPLEMENTED_CORE | CD-5 citations（target=Assertion；撤回门禁；I2） |
| CA-023 | Assertion | NEW | YES | — | IMPLEMENTED_CORE | CD-4 assertions（I3/I4） |
| CA-024 | 学术污损（Taint） | REUSE | YES | — | IMPLEMENTED_CORE | CD-3 taint_status/source_withdrawn 级联（Lineage 契约 §2.5） |
| CA-025 | Legacy Provenance | REUSE | NO | YES（evidence） | NON_RUNTIME_GOVERNANCE | 数据迁移治理机制（LegacyProvenanceDecision 3 态 + is_effective）；**不创建 runtime 对象**（§17 分离原则）；其义务 = CORE-COMPLETION dry-run 的 COMPLETION_EVIDENCE 输入（§33-41） |
| CA-026 | CandidateExtraction → Assertion 桥 | ADAPT | NO（占位） | — | BRIDGE_FROZEN | Core 已含 `created_by` 不透明引用占位（CD-4）；无 User/Auth/RBAC；5 态候选管线属治理层/未来研究工作台（§28-29） |
| CA-027 | Document rights 元数据 | ADAPT | NO | — | POST_PHASE_DEFERRED | DAG 无节点；rights 元数据属未来 Document/G4 治理 |
| CA-028 | GenerationProof（replay） | REUSE | NO | — | POST_PHASE_DEFERRED | 研究回放；非 Publication Snapshot；DAG 无节点 |

```text
Frozen Inventory Assets:
28

Final Dispositions Assigned:
28

IMPLEMENTED_CORE:
15（CA-001/003/004/005/007/008/012/014/015/019/020/021/022/023/024）

POST_PHASE_DEFERRED:
11（CA-002/006/009/010/011/013/016/017/018/027/028）

NON_RUNTIME_GOVERNANCE:
1（CA-025）

BRIDGE_FROZEN:
1（CA-026）

COMPLETION_EVIDENCE:
0（作为独立 CA 行；该义务整体承载于 CORE-COMPLETION evidence 交付物，CA-025 为其治理机制）

COMPLETION_IMPLEMENTATION_REQUIRED:
0（本轮无 Frozen evidence 支撑的 mandatory missing runtime object）
```

## 7. Canonical Model Reconciliation

### 7.1 概念与 Runtime Object 分离（§19）

Canonical 文档中被命名的概念**不等于** mandatory standalone SQLAlchemy model。逐项判断 Frozen semantics，允许：`covered as semantic alias / represented by existing canonical object / post-phase specialized concept / non-runtime conceptual term` — 均须证据。

### 7.2 原子概念最终裁决（12 项，§18 清单）

| Concept | Phase 0.4 Canonical Runtime Requirement? | Covered by Existing Core Object? | Post-Phase? | Completion Implementation Required? | Final Ownership |
| --- | --- | --- | --- | --- | --- |
| Place | NO | EntityType.place 值已登记（CD-1）；无 Place model | YES | NO | POST_PHASE_DEFERRED（post-Phase governed domain extension；§20-22 裁决） |
| Concept | NO | EntityType.concept 值已登记 | YES | NO | POST_PHASE_DEFERRED（专业领域概念） |
| Acupoint | NO | EntityType.acupoint 值已登记；历史文本主张走 Assertion（G1） | YES | NO | POST_PHASE_DEFERRED（TCM 专业领域） |
| Manifestation | NO | Edition 承载 | YES | NO | POST_PHASE_DEFERRED（FRBR 中层；DAG CD-2 未含） |
| Book | NO | Work 承载 | YES | NO | POST_PHASE_DEFERRED（HFB legacy naming；§24） |
| ClassicalVersion | NO | Version 承载 | YES | NO | POST_PHASE_DEFERRED（§24） |
| VersionRelation | NO | Version.parent_version_id 承载（I2） | YES | NO | POST_PHASE_DEFERRED（§24） |
| Sentence | NO | Passage 覆盖 Phase 0.4 粒度 | YES | NO | POST_PHASE_DEFERRED（§25 细粒度文本模型） |
| Token | NO | Passage 覆盖 | YES | NO | POST_PHASE_DEFERRED（§25） |
| Variant | NO | TEXTUAL Assertion 承载（Assertion 契约 §5） | YES | NO | POST_PHASE_DEFERRED（§25） |
| TextUnit | NO（Locator 为 Phase 0.4 要求） | Locator（hfm.core.locator，CD-0/2）承载结构化定位 | YES（TextUnit model） | NO | Locator → IMPLEMENTED_CORE（语义已实现）；TextUnit 细粒度 model → POST_PHASE_DEFERRED |
| Legacy Provenance | NO | Source / SourceRef / Evidence 承载 I1 runtime 链 | YES（migration-only） | NO | NON_RUNTIME_GOVERNANCE（§26：migration-only / legacy mapping；不建新 runtime 对象） |

```text
Canonical Concepts Reconciled:
12

Canonical Concepts Ambiguous:
0
```

### 7.3 关键专项裁决

**Place（§20-22）**：Phase 0.4 completion runtime requirement = **NO**（DAG 无节点；Scope §6.3 未将 Place 建模列为 CD 节点；CD-1 已登记 EntityType.place 值供 typed 登记）。Final lifecycle ownership = **POST_PHASE_DEFERRED（post-Phase governed domain extension）**——不从合同"消失"；不进入 CORE-COMPLETION 实现。

**Concept / Acupoint / Manifestation（§23）**：属专业/后续领域模型（TCM、FRBR 中层），正式裁决 POST_PHASE_DEFERRED；不让 Phase 0.4 Completion 无限扩张。

**Book / ClassicalVersion / VersionRelation（§24）**：Phase 0.4 contract semantics 已由 Work / Edition / Version / Version lineage 完整承载；HFB legacy naming 不重复建模。

**Sentence / Token / Variant / TextUnit（§25）**：Passage / Chapter / Locator / Version 已覆盖 Phase 0.4 要求粒度；Variant 主张由 TEXTUAL Assertion 承载；细粒度文本模型 = POST_PHASE_DEFERRED。

**Legacy Provenance（§26）**：Source / SourceRef / Evidence 已承载 I1 runtime 链；CA asset 为 HFB migration compatibility → migration-only / legacy mapping，不建新 canonical runtime object。

## 8. CA-026 Bridge Decision（§28-29）

```text
CA-026 Final Disposition:
BRIDGE_FROZEN

裁决依据:
- CD-4 Assertion.created_by = nullable opaque core reference（CA-026 桥占位）已实现并验收
- User / Role / Permission / JWT / Reviewer / Publisher / AnonymousAccess: 未引入（Auth 红线）
- CandidateExtraction 5 态候选管线属治理层/未来研究层（Assertion 契约 §5：审核通过 → Assertion；治理链保留），非 Phase 0.4 runtime

BRIDGE_FROZEN 语义:
- opaque actor reference 对 Phase 0.4 足够
- 无 User model 要求
- 无 Auth/RBAC 要求
- 未来身份绑定（真实 User FK）需要另行显式治理授权
- Phase 1 G7 Separation of Duties: NOT IMPLEMENTED（红线保持）
```

## 9. Data Migration / DoD Reconciliation（§30-41）

### 9.1 三种义务正式区分（§31）

```text
Schema Migration:
CD-0…CD-6 Alembic 演进（0001…0008）— 已完成并逐批验收

Data Migration Dry-Run:
HFB → HFM candidate transformation/reconciliation 模拟（不写 live HFM DB）— REQUIRED（DoD MANDATORY）

Actual Data Import:
persistent production data import — NOT AUTHORIZED（本轮与 Phase 0.4 completion 均不要求）
```

### 9.2 正式裁决

```text
Actual HFB Data Import Required for Phase 0.4 Completion:
NO
（依据：DoD 仅要求 dry-run complete；Migration Strategy §3-4 流程在 dry-run 报告通过后才 commit/import；
Phase 0.4 Completion Freeze 在 actual import 之前；本 Amendment 不授权 actual import）

Dry-Run Required:
YES（DoD MANDATORY：Data migration dry-run complete）

Reconciliation Required:
YES（Migration Strategy §6 Reconciliation Contract）

Dry-Run Owner:
CORE-COMPLETION（非 CD 节点；原 DAG 无 owner）
```

### 9.3 Dry-Run 隔离执行模式（§37）

依据 Migration Strategy §1/§4（"禁止复制 HFB live DB 继续运行"、"dry-run 报告通过后才允许 commit/import"）：

```text
dry-run 不得改变 production/live HFM 状态
允许:
  - 隔离测试数据库（独立于 live HFM DB）
  - 临时一次性数据库
  - 事务回滚
禁止:
  - 直接写正式 HFM DB
  - 复用 HFB live DB
```

### 9.4 Dry-Run Source Identity（§38）

```text
HFB Source Snapshot:
03755b57ec0e4c8023d1447619f7d6ead9e44d73

禁止使用 HFB current HEAD。
```

### 9.5 Required Reconciliation Counts（§39）

按 Migration Strategy §6 Reconciliation Contract 原文：

```text
source count
accepted count
transformed count
rejected count
duplicate count
target count
hash/checksum（适用处 — §40）
```

禁止仅凭"脚本执行成功"判定。

### 9.6 Hash / Checksum Evidence（§40）

Migration Strategy §6 明确要求 `hash/checksum（适用处）` → 纳入 CORE-COMPLETION DoD，**仅适用处**；不自行扩大要求。

### 9.7 Idempotency（§41）

Migration Strategy §5 要求：`same source snapshot + same migration version → same target state`（幂等；按 migration version + source 哈希去重）。列为 CORE-COMPLETION acceptance gate；**不暗示 actual import**。

## 10. Completion Work Package Definition（§33-36）

### 10.1 治理标识

```text
CORE-COMPLETION
```

（固定标识；避免与 CD 编号混淆；**不是 CD-7**）

```text
CORE-COMPLETION:
not CD-7
does not extend the Frozen CD sequence（CD-0…CD-6 序列不变）
exists solely to close inventory / migration evidence / explicitly adjudicated omissions
before Phase 0.4 Completion Freeze
```

### 10.2 未来授权 Scope（精确定义；本轮 NOT AUTHORIZED）

```text
1. required governance/evidence assets（含 CA-025 机制的 dry-run 治理应用）
2. data migration dry-run（隔离模式；Snapshot 03755b5）
3. reconciliation（§6 计数 + hash/checksum 适用处）
4. idempotency evidence（Migration Strategy §5）
5. inventory closure evidence（28/28 disposition + completion evidence 汇总）
6. narrowly defined missing Core implementation — 仅当未来治理裁决确认存在
   mandatory missing runtime object（当前裁决：0）；禁止笼统授权 "finish whatever is missing"
```

### 10.3 禁止内容（§36）

```text
Phase 1: NOT AUTHORIZED
Actual production data import: NOT AUTHORIZED
Public portal: NOT AUTHORIZED
Publication snapshot: NOT AUTHORIZED
Medical compliance: NOT AUTHORIZED
Authentication/RBAC: NOT AUTHORIZED
ICH media: NOT AUTHORIZED
Teaching: NOT AUTHORIZED
```

## 11. Phase Boundary（§43/§47）

```text
Phase 1:
NOT AUTHORIZED（即使 Amendment 被 ACCEPTED 也不能自动开始）

Phase 0.4 Completion Freeze Gate（未来，非本轮）至少要求:
CD-0…CD-6: ACCEPTED / FROZEN
CORE-COMPLETION: ACCEPTED
Inventory: CLOSED UNDER AMENDED DISPOSITIONS
Canonical Boundary: CLOSED
Dry-Run: PASS
Reconciliation: PASS
Definition of Done: PASS
I1…I6: PASS
Phase 1 Leakage: NO
```

## 12. Invariant Preservation（§12/§45）

```text
I1 Provenance: PASS（保持；CD-0/3/4/6 链）
I2 Version Reproducibility: PASS（保持；CD-2/5）
I3 Assertion Coexistence: PASS（保持；CD-4）
I4 No Silent Overwrite: PASS（保持）
I5 Stable Identity: PASS（保持）
I6 HFB Independence: PASS（保持）

CD-0…CD-6:
ACCEPTED / FROZEN（有效冻结实现节点；不重新验收；过往 PASS 保持真实）
```

## 13. Supersession / Precedence Rules（§44）

```text
For issues explicitly adjudicated by this Amendment,
the amendment governs（v0.2 语义）。

For all untouched semantics,
the original v0.1 Frozen Contract remains authoritative。

CD-7:
NONEXISTENT IN ORIGINAL FROZEN DAG — 本 Amendment 不新增 CD-7；
未来 Core DAG 扩展须走独立 architecture change，不属于本轮 Completion reconciliation。
```

## 14. Acceptance Conditions（§54）

形成 candidate 的验收条件（全部满足）：

```text
All 28 CA assets: FINAL DISPOSITION ASSIGNED
All canonical concepts: FINAL PHASE OWNERSHIP ASSIGNED（12/12）
CA-002: NOT AMBIGUOUS（POST_PHASE_DEFERRED）
Place: NOT AMBIGUOUS（POST_PHASE_DEFERRED）
CA-026: NOT AMBIGUOUS（BRIDGE_FROZEN）
Actual import requirement: UNAMBIGUOUS（NO）
Dry-run requirement: UNAMBIGUOUS（YES，owner CORE-COMPLETION）
Dry-run owner: CORE-COMPLETION
CD-7: NONEXISTENT
Phase 1: NOT AUTHORIZED
Original frozen files: UNCHANGED
Internal consistency: PASS（§15 四门禁）
```

## 15. Authorization Boundary

```text
GOVERNANCE CONTRACT AMENDMENT:
AUTHORIZED（本轮）

PRODUCTION CODE / TEST / MIGRATION / DATA MIGRATION DRY-RUN / ACTUAL IMPORT:
NOT AUTHORIZED

COMPLETION WORK PACKAGE（CORE-COMPLETION）:
NOT AUTHORIZED

PHASE 0.4 COMPLETION FREEZE:
NOT AUTHORIZED

CD-7:
NONEXISTENT / NOT AUTHORIZED

PHASE 1:
NOT AUTHORIZED

Amendment Candidate Status:
IMPLEMENTED / AWAITING CODEX ACCEPTANCE
```

## 16. Amendment Traceability Matrix（§48）

| Audit Finding | Original Frozen Source | Conflict | Amendment Decision | Downstream Action |
| --- | --- | --- | --- | --- |
| CA-002 归属冲突 | CANONICAL §1/§2（EntityRelation ADAPT）+ CD-1 Scope（排除 entity_relations）+ CD-6（仅 EventRelation）+ DAG（无节点） | 命名 vs 实现 vs DAG | **POST_PHASE_DEFERRED**（generic EntityRelation 非 Phase 0.4 runtime 要求；EventRelation = 必需 Core relation；9 类关系由 RELATIONAL Assertion 承载） | 不实现；保留未来受治理资产 |
| CA-006 Concept/Acupoint | INVENTORY CA-006 EXTEND + SCOPE §6.3（G1） | verdict vs 实现 | **POST_PHASE_DEFERRED**（TCM 专业领域；EntityType 值已登记） | 不实现 |
| CA-009 NormalizedText | INVENTORY CA-009 EXTEND + DAG（无节点） | verdict vs DAG | **POST_PHASE_DEFERRED**（细粒度文本归一化） | 不实现 |
| CA-010 Book | INVENTORY CA-010 REUSE + CANONICAL §2 | naming vs Work | **POST_PHASE_DEFERRED**（Work 承载） | 不重复建模 |
| CA-011 ClassicalVersion | INVENTORY CA-011 EXTEND | verdict vs Version | **POST_PHASE_DEFERRED**（Version 承载） | 不重复建模 |
| CA-013 VersionRelation | INVENTORY CA-013 REUSE | 关系表 vs 谱系 | **POST_PHASE_DEFERRED**（parent_version_id 承载 I2） | 不实现 |
| CA-016 Sentence/Token/Variant | INVENTORY CA-016 ADAPT + ASSERTION §5 | 粒度 vs Passage | **POST_PHASE_DEFERRED**（TEXTUAL Assertion 承载 Variant 主张） | 不实现 |
| CA-017 Commentary | INVENTORY CA-017 REUSE + DAG（无节点） | verdict vs DAG | **POST_PHASE_DEFERRED** | 不实现 |
| CA-018 TEI | INVENTORY CA-018 REUSE + DAG（无节点） | verdict vs DAG | **POST_PHASE_DEFERRED** | 不实现 |
| CA-025 Legacy Provenance | INVENTORY CA-025 REUSE（数据迁移治理）+ DAG（无 owner） | owner 缺失 | **NON_RUNTIME_GOVERNANCE**（不建 runtime 对象；dry-run 治理机制） | CORE-COMPLETION 证据输入 |
| CA-027 Document rights | INVENTORY CA-027 ADAPT + DAG（无节点） | verdict vs DAG | **POST_PHASE_DEFERRED** | 不实现 |
| CA-028 GenerationProof | INVENTORY CA-028 REUSE + DAG（无节点） | verdict vs DAG | **POST_PHASE_DEFERRED**（非 Publication Snapshot） | 不实现 |
| Place 无节点 | CANONICAL §1/§2 + DAG（无节点）+ SCOPE §6.3 | 命名 vs DAG | **POST_PHASE_DEFERRED**（post-Phase governed domain extension；EntityType.place 值已登记） | 不实现 |
| Concept / Acupoint / Manifestation 无节点 | CANONICAL §2 + DAG | 命名 vs DAG | **POST_PHASE_DEFERRED**（专业/后续领域） | 不实现 |
| Book / ClassicalVersion / VersionRelation 重复 | CANONICAL §2 | naming vs 既有对象 | **covered by existing canonical objects**（Work/Edition/Version/lineage） | 不重复建模 |
| Sentence / Token / Variant / TextUnit 粒度 | CANONICAL §2 + DAG | 粒度 vs Passage/Locator | **POST_PHASE_DEFERRED**（TextUnit model）；Locator 已 IMPLEMENTED_CORE | 不实现 |
| Legacy Provenance 重复 | CANONICAL §2 + LINEAGE §1 | migration vs runtime | **NON_RUNTIME_GOVERNANCE**（migration-only / legacy mapping） | 不建新 runtime 对象 |
| CA-026 桥模糊 | ASSERTION §5 + CA-026 ADAPT | ownership 模糊 | **BRIDGE_FROZEN**（opaque created_by 足够；无 User/Auth；未来绑定需治理） | Phase 1 G7 不实现 |
| dry-run 无 owner | DOD（Data migration dry-run complete）+ DAG（无节点） | owner 缺失 | **CORE-COMPLETION**（非 CD 节点） | 未来授权执行 |
| reconciliation 计数 | MIGRATION §6 | 字段 vs 实现 | 六计数 + hash/checksum（适用处） | CORE-COMPLETION 验收 |
| DoD ownership | DOD + DAG | 义务 vs 节点 | DoD obligation 保留；owner = CORE-COMPLETION | 未来授权执行 |

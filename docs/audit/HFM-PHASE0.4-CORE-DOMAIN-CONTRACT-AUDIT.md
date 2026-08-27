# HFM Phase 0.4 — Core Domain Contract Audit

Date: 2026-08-27 · Phase 0.4 — Core Domain Contract Audit & Migration Planning（READ-ONLY）
起始基线：`f495fa07b73f5f1d75b1398f196beadf6618a6bb`
HFB Source Snapshot：`03755b57ec0e4c8023d1447619f7d6ead9e44d73`

## 1. 交付物

- `docs/domain/HFM-CORE-DOMAIN-SCOPE-v0.1.md`
- `docs/domain/HFM-ASSERTION-CONTRACT-v0.1.md`
- `docs/domain/HFM-EVIDENCE-LINEAGE-CONTRACT-v0.1.md`
- `docs/domain/HFM-CANONICAL-DOMAIN-MODEL-v0.1.md`
- `docs/migration/hfb/HFM-PHASE0.4-CORE-ASSET-INVENTORY.md`（CA-001…CA-028）
- `docs/migration/hfb/HFM-CORE-DATA-MIGRATION-STRATEGY-v0.1.md`
- `docs/migration/hfb/HFM-PHASE0.4-CORE-MIGRATION-DAG.md`（CD-0…CD-6）
- `docs/governance/HFM-CORE-DOMAIN-DEFINITION-OF-DONE.md`
- `docs/audit/HFM-PHASE0.4-CORE-DOMAIN-RISK-REGISTER.md`（P0×1 / P1×5 / P2×4 / P3×2）

## 2. 审计方法

- 治理材料核对：Frozen Reuse Matrix / Technical Baseline / BASELINE-MANAGEMENT / HFM-BOUNDARIES / B1–B4 全链 / Batch 4 Remaining Audit / ADR-0001。
- HFB 取证：DOMAIN-MAP v1.1（Model→Service→API→Test 调用链）+ 本轮实测（person/academic_evidence/passage/bibliographic/version 模型）。
- 核心原则保持：Entity→Assertion→Evidence→Source→Citation→Version；Research→editorial→Publication→snapshot→Portal（HFM-BOUNDARIES-v0.1）。

## 3. 八项裁定

```text
1. CORE DOMAIN SCOPE:
VALID
（Person/Work/Entity/Assertion/Source/Evidence/Citation/Version 覆盖；G1-G4/G7 排除边界明确）

2. HFB CORE ASSET INVENTORY:
COMPLETE
（CA-001…CA-028 全链取证；REUSE 16 / EXTEND 3 / ADAPT 7 / NEW 2 / DEPRECATE 0 / UNKNOWN 0）

3. HFM CANONICAL MODEL:
READY_FOR_REVIEW
（Entity/Person/Event/Work/Edition/Version/Passage/Source/SourceRef/Evidence/Assertion/Citation + I1-I6 + Stable ID 契约）

4. ASSERTION CONTRACT:
READY_FOR_REVIEW
（subject/predicate/value/type/evidence[]/provenance/version/editorial_status；冲突并存；不承担 Publication）

5. EVIDENCE LINEAGE CONTRACT:
READY_FOR_REVIEW
（Source→SourceRef→Evidence→Assertion→Citation；多对多；withdrawn 级联；hash/integrity）

6. CORE MIGRATION DAG:
ACYCLIC
（CD-0 Foundation/Source → CD-1 Entity → CD-2 Work/Text → CD-3 Evidence → CD-4 Assertion → CD-5 Citation → CD-6 Person/Event；无循环）

7. FIRST CORE IMPLEMENTATION BATCH:
CD-0
（RECOMMENDED，未授权：依赖最少、可独立验证、无 Phase 1/公众 API/媒体/SoD/AI）

8. CORE DOMAIN IMPLEMENTATION:
NOT AUTHORIZED
```

## 4. 关键结论

- **Assertion = NEW**（HFB 无统一模型；主张分散于 Variant/AcademicRelation/CandidateExtraction/GenerationProof）。
- **Event = NEW**（HFB Chronology DOC_ONLY）。
- **Person = ADAPT**（核心模型可复用；单值字段迁移必须转写为 Assertion — R-001 P0）。
- **Evidence/SourceRef = REUSE**（含 taint 与撤回级联）；**Citation = ADAPT**（target 统一为 Assertion）。
- **数据迁移**：Code Port 与 Data Import 双流独立；dry-run + idempotency + reconciliation 强制；禁止复制 live DB。
- **技术边界**：Graph DB/Neo4j/Event Sourcing/CQRS split/ES/Redis/Kafka/Microservices = FUTURE OPTION，不入 entry gate。

## 5. 授权状态（不得自行改变）

```text
CORE DOMAIN MIGRATION:
NOT AUTHORIZED

CD-0:
NOT AUTHORIZED

PHASE 1 BUSINESS CODING:
NOT AUTHORIZED
```

下一步：交 Codex 做 **HFM Phase 0.4 Core Domain Contract Acceptance**；通过后由独立治理提交冻结 Core Domain Contract，Pi 方可获得 CD-0 实施授权。

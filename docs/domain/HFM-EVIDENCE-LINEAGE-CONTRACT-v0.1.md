# HFM Evidence Lineage Contract v0.1

Status: Draft for Contract Review · Date: 2026-08-27 · Phase 0.4
依据：HFB `03755b5` 实测 — `SourceRef`/`Evidence`/`Citation` 模型（apps/backend/app/models/academic_evidence.py）。

## 1. 血缘链

```text
Source
  ↓ 物理/出版物身份（title/author/edition_info/url）
SourceRef
  ↓ 具体定位（locator；HFB 现为 page_location 字符串 → HFM EXTEND 结构化）
Evidence
  ↓ 论据（description + evidence_level + taint）
Assertion
  ↑ 主张（subject/predicate/value）
Citation
  → 引用（target = Assertion，+ evidence_id）
```

方向：Source → SourceRef → Evidence → Assertion（Evidence 也可直接挂系统内 Passage → 见 §6）。

## 2. 多对多关系（契约）

1. **Assertion 允许多个 Evidence？** YES — `evidence[]` 0..n；呈现按 evidence_level 加权。
2. **Evidence 支持多个 Assertion？** YES — Evidence 可被多条 Citation/Assertion 复用（HFB `Citation.evidence_id` FK CASCADE 已支持多 Citation 共享一 Evidence）。
3. **Citation 引用 Assertion 还是 Evidence？** HFM 契约：**Citation → Assertion**（可带 quote_text/note），并通过 Assertion 的 evidence[] 抵达 Evidence；保留 HFM Citation → Evidence 的直接边（与 HFB 兼容的引用强度表达）。
4. **SourceRef 与 Source 区别？** SourceRef = 物理出处身份 + 定位（title/author/edition_info/page_location/url）；Source = 来源准入记录（HFB `SourceAdmissionEntry` 三级状态机 — 治理语义，Core 只用其 identity/rights 元数据，不依赖准入状态机）。
5. **withdrawn Source 如何影响 Citation？** 级联：Source withdrawn → 相关 Evidence 标记 taint（HFB `AcademicTaintAuditLog` REUSE）→ Citation 拒绝引用（HFB `citation_persistence.py:387-389` 撤回引用拒绝 REUSE）；HFM 契约保持该级联语义。
6. **Evidence hash/integrity 位置？** HFM：Evidence 增加 `content_hash`（canonical hash — Batch 1 已迁移 `hfm.core.hashing`）与可选 artifact/文本定位；HFB 现有哈希在 candidate/promotion 层（治理），Core Evidence 需补 integrity 字段。
7. **immutable locator 如何保证？** 结构化 locator（work/edition/version/chapter/passage + 页/行）落库后不可变；内容变更走新版本（I2）。
8. **legacy HFB Evidence 如何迁入？** 经数据迁移 DTO（extract → validate → transform → dry-run → import）；`LegacyProvenanceDecision` 机制（3 态 + is_effective）为既有数据的治理依据（REUSE）。

## 3. HFB 资产复用表

| HFM 对象 | HFB 来源 | Verdict | 说明 |
| --- | --- | --- | --- |
| SourceRef | `models/academic_evidence.py::SourceRef` | **REUSE** + EXTEND（结构化 locator） | title/author/edition_info/url 复用；page_location 字符串 → Locator 对象 |
| Evidence | `models/academic_evidence.py::Evidence` | **REUSE** | evidence_level Level 1-4、source_ref_id、source_passage_id、taint 全复用 |
| Citation | `models/academic_evidence.py::Citation` | **ADAPT** | 多态 target → 统一 Assertion target；撤回拒绝逻辑复用 |
| Taint | `models/academic_taint.py` | **REUSE** | clean/source_withdrawn/quarantined + 审计日志 |
| Source（准入） | `models/source_admission.py::SourceAdmissionEntry` | 边界保留 | identity/rights 元数据入 Core；状态机留治理层 |

## 4. 边界

- Evidence 不得与 Publication Admission 再次耦合（HFB `candidate_publish_uow` 为治理路径，Core Evidence 独立）。
- Publication Snapshot / public projection 属 G3，不入本契约。

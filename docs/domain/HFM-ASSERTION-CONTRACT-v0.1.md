# HFM Assertion Contract v0.1

Status: Draft for Contract Review · Date: 2026-08-27 · Phase 0.4
依据：HFB `03755b5` 无统一 Assertion（主张分散于 Variant/AcademicRelation/CandidateExtraction/GenerationProof — DOMAIN-MAP §1.7 PARTIAL）→ HFM **NEW**。

## 1. 最小逻辑语义

```text
Assertion
├── id                       # stable identity (I5)
├── subject_entity           # Entity | Person | Work | Event | Place ...
├── predicate                # e.g. born_in / authored / studied_under / composed
├── value / object_entity    # literal 或指向另一 Entity
├── assertion_type           # BIOGRAPHICAL / TEXTUAL / RELATIONAL / HISTORICAL / ...
├── confidence/status        # 研究置信状态（非发布状态）
├── evidence[]               # 0..n Evidence（多证据并存）
├── provenance               # 录入者/来源/审计（actor + source + timestamp）
├── version                  # 内容版本 / Assertion Revision（I2）
├── editorial_status         # draft/reviewed/approved/withdrawn（研究编辑态，非公开发布态）
└── created/updated metadata
```

这是**逻辑契约**，不强制映射单一 ORM 表（允许 statement 表 + 结构化载荷 + 独立 evidence 链接表）。

## 2. 必须支持并存

```text
Assertion A: 皇甫谧 生于 公元215年（来源 S1，等级 L1）
Assertion B: 皇甫谧 生于 公元214年（来源 S2，等级 L3）
Assertion C: 皇甫谧 师承 席坦（来源 S3，等级 L2）
```

三者可同时存在；`subject + predicate` 不设唯一约束。消费方按 editorial_status / evidence 权重 / 版本选择呈现（I3 Assertion Coexistence）。

## 3. 不变量

- **I1 Provenance**：每条 Assertion 至少可追踪到 Evidence（或标注 `provenance_pending`）。
- **I2 Version Reproducibility**：Assertion 记录其来源 Content Version / Source Version，使引用可复现。
- **I4 No Silent Overwrite**：更新主张 = 新增/撤回 Assertion，禁止改写 `Entity.birth_year` 等唯一字段消灭历史主张（HFB Person 单值字段模型为此主要风险源 — 迁移时必须把现有单值字段转为 Assertion 而非复制）。
- **I5 Stable Identity**：Assertion id 稳定（UUIDv7 或内容哈希派生）。
- **I6 HFB Independence**：Assertion 语义独立于 HFB 实现。

## 4. 禁止承担 Publication

Assertion 契约**不得**包含：`published_page` / `public_snapshot` / `portal_visibility` / `release_version` / `rollback`。

仅允许：

```text
editorial/research status
publication eligibility 接口（占位，不实现）
```

Publication Layer（G3）另行消费。

## 5. 与 HFB 现有主张对象的映射（迁移输入）

| HFM Assertion 角色 | HFB 来源对象 | 处理 |
| --- | --- | --- |
| 人物生平主张 | `Person.birth_year/death_year/birth_place/dynasty/biography`（单值） | **转写为 Assertion**（带 evidence 溯源，不复制单值语义） |
| 学术关系主张 | `AcademicRelation`（subject/predicate/object + confidence） | **ADAPT** → Assertion（predicate 归一） |
| 文本/异文主张 | `Variant`（版本异文） | **ADAPT** → Textual Assertion |
| AI 抽取主张 | `CandidateExtraction`（候选 → 审核） | 治理链保留；审核通过后产生 Assertion |
| 知识图谱关系 | `EntityRelation`（9 类） | **ADAPT** → Assertion 或 Relation（按消费者） |

## 6. 测试计划（DoD 输入）

- conflicting Assertion 并存测试；
- No-silent-overwrite 测试（更新不覆盖历史）；
- provenance 完整链测试；
- editorial_status 转换测试；
- stable ID 幂等测试。

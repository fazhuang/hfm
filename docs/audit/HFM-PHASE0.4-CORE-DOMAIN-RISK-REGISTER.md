# HFM Phase 0.4 — Core Domain Risk Register

Status: Draft for Contract Review · Date: 2026-08-27 · Phase 0.4（READ-ONLY 审计，只记录不修复）

| ID | Level | Risk | Evidence | Mitigation Plan |
| --- | --- | --- | --- | --- |
| R-001 | P0 | HFB Person 单值字段模型与 Assertion 冲突（迁移时若复制单值字段将消灭历史主张，违反 I3/I4） | `models/person.py`（birth_year/death_year/birth_place/dynasty/biography 均为单值列） | 迁移规则强制：单值字段转写为 Assertion；Entity 表仅存身份/锚点字段 |
| R-002 | P1 | locator 不完整：`SourceRef.page_location` 为字符串，无卷/篇/页/行结构化 | `models/academic_evidence.py::SourceRef` | CD-0/CD-2 建立 TextUnit/Locator；迁移转换器拆分字符串 |
| R-003 | P1 | Citation 现解析 latest（`citation_persistence` 面向多态 target），版本固定可复现性不足（I2） | `citation_persistence.py` | CD-5 Citation 契约固定目标版本 + withdrawn 拒绝（复用既有逻辑） |
| R-004 | P1 | 跨版本 Passage 对齐无显式机制（version_id 可选，无对齐键） | `models/passage.py` | CD-2 定义版本对齐键（work+canonical locator 哈希） |
| R-005 | P1 | Evidence lineage 不完整：部分主张（Variant/AcademicRelation）无统一 Evidence 链 | DOMAIN-MAP §1.7 PARTIAL | CD-3/CD-4 建统一血缘；迁移时补齐 source_ref 引用 |
| R-006 | P2 | rights 迁移：`Document.copyright_status` 等字段与媒体权利（G4）边界需在迁移时分离 | `models/document.py` | CD-1/CD-5 仅迁移通用 rights 元数据；媒体权利全链留 G4 |
| R-007 | P1 | ID collision：HFB UUIDv7 保留 + NEW 对象新 ID，存在跨源冲突可能 | 多表 UUID 无全局唯一约束 | 迁移映射表（source_id → hfm_id）+ 幂等校验 |
| R-008 | P2 | HFB legacy coupling：迁移适配器可能演化为永久依赖 | 数据迁移策略 | 适配器生命周期限定迁移期；DoD I6 门禁 |
| R-009 | P2 | 循环依赖风险：Assertion↔Citation 反向引用 | DAG 设计 | 经 Evidence 间接表达，不建循环 FK（break strategy 已列） |
| R-010 | P1 | 隐藏 Auth 依赖：Evidence.creator_id / Citation 审计等均 FK 到 users | `models/academic_evidence.py`；HFB Auth REUSE 判定 | CD 批次内以 actor_id 占位（无 User 模型）；HFM Auth 重构（B4 §12 红线）后再接 |
| R-011 | P2 | 数据迁移 dry-run 缺失导致直接写正式库 | 迁移策略 | dry-run + reconciliation 报告强制门禁 |
| R-012 | P3 | `candidate_publish_uow`/`production_query_policy` 等治理路径与 Core 概念边界混淆 | BASELINE §5/§8 | 概念边界文档明确治理层 vs Core 层 |

## 汇总

```text
P0: 1
P1: 5
P2: 4
P3: 2
```

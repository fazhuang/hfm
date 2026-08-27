# HFM Phase 0.4 — Core Migration DAG

Status: Draft for Contract Review · Date: 2026-08-27 · Phase 0.4
依据：CA-001…CA-028 Inventory 依赖关系；批次为独立命名（CD-0…），不再使用 Batch 5+。

## DAG

```text
CD-0  Foundation identity / value objects + Source / SourceRef（身份、locator 基元、stable ID）
        │
CD-1  Entity + EntityType + Person（核心模型 ADAPT；单值字段声明为 Assertion 迁移输入）
        │
CD-2  Work / Edition / Version / Chapter / Passage + TextUnit/Locator（FRBR 层 + 结构化定位）
        │
CD-3  Evidence（+ lineage + content_hash）
        │
CD-4  Assertion（契约落地；含 HFB 主张对象映射）
        │
CD-5  Citation（target=Assertion；撤回引用语义）
        │
CD-6  Person/Event 关系（Event NEW + AcademicRelation ADAPT；依赖 CD-1 + CD-4）
```

无循环；若未来引入 Assertion→Citation 反向依赖，break strategy = 经 Evidence 间接表达，不建循环 FK。

## Node 明细

| Node | dependency | source assets（CA） | HFM target | migration type | test gate | data dependency | blocked-by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CD-0 | — | CA-019（identity）+ CA-020 + CA-005 | Source/SourceRef/Institution + stable ID + Locator 基元 | REUSE/EXTEND | unit + 稳定 ID 幂等 | source identity 导出 | — |
| CD-1 | CD-0 | CA-001 + CA-002 + CA-003 + CA-006 | Entity + EntityType + Person | ADAPT/REUSE/EXTEND | domain invariant + 单值字段转写断言 | person/entity 导出 | CD-0 |
| CD-2 | CD-1 | CA-007…CA-015 + CA-016 + CA-017 + CA-018 | Work/Edition/Version/Chapter/Passage + Locator | REUSE/EXTEND/ADAPT | 版本可复现 + locator 解析 | 古籍层级导出 | CD-1 |
| CD-3 | CD-2 | CA-021 + CA-024 + CA-028 | Evidence + taint + content_hash | REUSE | lineage + integrity | evidence/source_ref 导出 | CD-2 |
| CD-4 | CD-3 | CA-023（NEW）+ CA-026（桥） | Assertion 契约 | NEW/ADAPT | 冲突并存 + no-silent-overwrite + provenance | person 单值字段转写 | CD-3 |
| CD-5 | CD-4 | CA-022 + CA-027 | Citation（target=Assertion） | ADAPT | 撤回引用 + 版本固定 | citation 导出 | CD-4 |
| CD-6 | CD-1, CD-4 | CA-004（NEW）+ CA-001（relation） | Event + Person/Event 关系 | NEW/ADAPT | 事件证据链 + 时间区间 | 无（事件为新增） | CD-1, CD-4 |

## 垂直切片依赖映射

| MVP 切片 | 需要 Core 对象 | 边界 |
| --- | --- | --- |
| Ancient Text Slice | CD-0 + CD-1 + CD-2（Work/Version/Passage/Locator）+ CD-3 + CD-4 + CD-5 | 核心对象全覆盖 |
| Person Event Slice | CD-1（Person）+ CD-4（Assertion）+ CD-6（Event） | 事件 = NEW（Chronology DOC_ONLY） |
| ICH Video Slice | 仅 Core Entity 登记；视频/权利 = G4 | 不进入 Core |
| Publication Snapshot Slice | 消费 Core（研究层）；快照/投影 = G3 | 不进入 Core |

## 建议首个实现批次

**RECOMMENDED FIRST IMPLEMENTATION BATCH: CD-0**（依赖最少、可独立验证、无 Phase 1/公众 API/媒体/SoD/AI）。

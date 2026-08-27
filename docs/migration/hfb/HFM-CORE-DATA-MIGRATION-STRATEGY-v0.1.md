# HFM Core Data Migration Strategy v0.1

Status: Draft for Contract Review · Date: 2026-08-27 · Phase 0.4
HFB Source Snapshot：`03755b57ec0e4c8023d1447619f7d6ead9e44d73`

## 1. 总原则

```text
HFB DB/data
    ↓ extract
Migration DTO
    ↓ transform/validate
HFM Canonical Domain
    ↓ verify
HFM DB
```

**禁止**：复制 HFB live DB 继续运行；HFM live DB ↔ HFB live DB 共享。
HFB 数据仅作 **migration/import source**（Frozen 数据继承边界）。

## 2. 代码迁移流（独立于数据）

```text
HFB implementation
→ semantic audit（DOMAIN-MAP 证据链）
→ HFM adaptation（CD 批次内）
→ HFM tests
```

## 3. 数据导入流（独立于代码）

```text
HFB records
→ export（固定 snapshot 导出）
→ validation（schema/类型/引用完整性）
→ transformation（单值字段 → Assertion 转写、ID 映射、locator 结构化）
→ HFM import
→ reconciliation
```

## 4. Dry Run 强制

```text
extract → validate → transform → dry-run → reconciliation report → commit/import
```

禁止直接写正式 HFM DB；dry-run 报告通过后才允许 commit/import。

## 5. Idempotency

```text
same source snapshot + same migration version → same target state
```

迁移脚本必须幂等（按 migration version + source 哈希去重）；重复执行不产生重复记录。

## 6. Reconciliation Contract

迁移后必须可回答：

```text
source count
accepted count
transformed count
rejected count
duplicate count
target count
hash/checksum（适用处）
```

不允许仅凭「脚本执行成功」判定。

## 7. 关键转换规则（本轮审计确定）

- Person 单值字段（birth_year/death_year/birth_place/dynasty/biography/notable_works）→ **转写为 Assertion**（带 evidence 溯源；legacy 数据用 `LegacyProvenanceDecision` 治理标记，CA-025 REUSE）。
- `SourceRef.page_location` 字符串 → 结构化 Locator（work/edition/version/chapter/passage + 卷/篇/页/行）。
- Citation 多态 target（Variant/AcademicRelation/Passage）→ 统一 Assertion target（可追溯映射表）。
- ID：HFB UUIDv7 保留；NEW 对象（Assertion/Event/Locator）生成新 UUIDv7（I5）。

## 8. Legacy Compatibility

默认不为保持 HFB 内部 API 兼容增加 Legacy Layer；仅真实内容迁移需要时允许 **temporary migration adapter**，不得成为永久 runtime dependency。

# P6 设计 — 合订本多对多 Work 关联规则扩展（EDITION-HFM-A000541）

**任务**：HFM-P6-收尾 · 合订本（四书合刊）多对多 Work 关联规则扩展
**日期**：2026-09-13
**性质**：schema 设计草案 + 决策选项。**不擅自改 schema，不擅自新增著作**，待授权。
**对象**：`EDITION-HFM-A000541`《针灸甲乙经、伤寒论、金匮要略、温病学》精译.pdf（913 页）

---

## 1. 问题

当前 `editions.work_id` 是**单值非空外键**（1:N，见 `apps/backend/src/hfm/models/edition.py:34`）：

```text
editions.work_id  NOT NULL  FK → works.id   （一部版本只挂一部著作）
```

A000541 是「四书合刊」——一部物理版本内含四部独立经典，强行单 FK 挂靠会版本学失真（这正是其原 DEFER 理由：`MULTIPLE_CANONICAL_WORKS_CONTAINED`）。

## 2. 现状盘点（已查 `hfm_prod`）

- `works` = 14（`WORK-JIAYI` 针灸甲乙经存在；**伤寒论/金匮要略/温病学不在列**）
- `editions` = 87；A000541 未入库（DEFERRED 正确跳过）
- 迁移头 = `0015`；PWE 导入器冻结基线 `hfm_import_pwe.py`（87/5 计数）

## 3. Schema 草案（N:N 关联表）

新增关联表（**加法式，不改 `editions.work_id` 现有语义**）：

```sql
-- migration 0016（草案）
CREATE TABLE edition_works (
    id          UUID PRIMARY KEY,          -- BaseModel 主键
    edition_id  VARCHAR(36) NOT NULL REFERENCES editions(id) ON DELETE CASCADE,
    work_id     VARCHAR(36) NOT NULL REFERENCES works(id)    ON DELETE CASCADE,
    role        VARCHAR(40)  NULL,         -- 'primary' | 'contained'（可选标注）
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    UNIQUE (edition_id, work_id)
);
CREATE INDEX ix_edition_works_edition ON edition_works (edition_id);
CREATE INDEX ix_edition_works_work     ON edition_works (work_id);
```

对应模型 `EditionWork`（`apps/backend/src/hfm/models/edition.py` 旁新增），仓库 `EditionRepository` 增加合刊关系读写，`editions.work_id` 继续作「主作品」锚点。

**A000541 落库形态（若采用 Option 3）**：

```text
editions:  EDITION-HFM-A000541.work_id = WORK-JIAYI      （主作品锚点）
edition_works:
  (A000541, WORK-JIAYI,        'primary')
  (A000541, WORK-SHANGHANLUN,  'contained')
  (A000541, WORK-JINGUIYAOLUE, 'contained')
  (A000541, WORK-WENBINGXUE,   'contained')   ← 见 §4 歧义
```

## 4. 新增著作清单（若采用 Option 3）

| stable_id | 实体 stable_id | 著作 | 作者 | 疑点 |
| :--- | :--- | :--- | :--- | :--- |
| `WORK-SHANGHANLUN` | `ENT-WORK-SHANGHANLUN` | 伤寒论 | 张仲景（东汉） | 无（清晰） |
| `WORK-JINGUIYAOLUE` | `ENT-WORK-JINGUIYAOLUE` | 金匮要略 | 张仲景（东汉） | 无（清晰） |
| `WORK-WENBINGXUE` | `ENT-WORK-WENBINGXUE` | 温病学 | — | **「温病学」是学科非单书**，需目录/版权页确认具体文本（温病条辨？温热论？综论？） |

> ⚠️ 关键发现：「温病学」非单一著作，而是一学术流派。A000541 若走多对多，须先 OCR 其目录/版权页确认第四部确切篇目，不能按书名机械新增。这进一步支持「A000541 需书目级考证后建模」。

## 5. 决策选项

| 选项 | 内容 | 代价 | 推荐 |
| :--- | :--- | :--- | :---: |
| **A** | **继续 DEFER**，待 A000541 目录/版权页 OCR 确认四书确切篇目后再决定建模 | 无 schema 变更，A000541 暂不入 editions | ✅ 推荐 |
| **B** | 以 `WORK-JIAYI` 为主作品**单 FK 强制挂靠**（注明合刊附录） | 零 schema，但版本学失真（原 DEFER 理由未消解） | 否 |
| **C** | 实现 §3 N:N schema + 新增 3 著作（伤寒论/金匮要略 + 温病学需先定本） | 迁移 0016 + 3 著作 + 温病学考证 | 仅当需精确多对多 |

> 注：选项 C 会改变 PWE 导入器的 `EXPECTED_MIGRATION_HEAD`（0015→0016）与 Work 冻结计数（14→17），属更大范围的治理变更，须与《P6-BACKFILL-PLAN》分离、单独授权。

## 6. 待授权清单

1. **A000541 建模方向**：选项 A / B / C 选一（推荐 A）。
2. 若选 C：授权新增 3 部著作 + 迁移 0016（多对多关联表）。
3. 若选 C：授权对 A000541 目录/版权页做 PaddleOCR，以确认「温病学」的确切文本（消除 §4 歧义）。
4. 新增著作的权利分类（伤寒论/金匮要略为古籍 `public_domain`；温病学据具体文本定）。

签署人 / 日期：__________________ / 2026-09-____

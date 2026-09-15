# 治理修订草案 · 迁移头取代 0017 → 0018

| 字段 | 值 |
| :--- | :--- |
| 状态 | **DRAFT · NOT IN FORCE** —— 未经授权方签署，不生效 |
| 目标文件 | `docs/governance/HFM-PHASE2-INVARIANT-SUPERSESSION-REGISTER-v1.md` |
| 触发 | P-1 已上生产库（`6023f0a`），`hfm_prod` @ alembic 0018 |
| 起草日期 | 2026-09-15 |
| 起草方 | 非治理方 —— 本草案**不修改**目标文件 |

---

## 1. 问题

登记册里有一条 **ACTIVE** 断言现在是**假的**：

```
ASSERTION_ID: ASN-SG-MIG-0017-HEAD
CLASS: C
STATUS: ACTIVE
RATIONALE: Current-state replacement: single linear Alembic head 0017, revisions 0001..0017, …
CURRENT_REPLACEMENT_TEST: apps/backend/tests/test_phase2_media.py::test_p2_current_migration_head_0017
```

`hfm_prod` 与 `main` 现在都在 0018，迁移链是 0001–0018。这是继"现状档案写 `hfm_prod @ 0017`"之后，第二处因本次推进而失真的记录，**而它是治理登记册，比现状档案更硬**。

## 2. 根因：登记册没有「迁移头推进」的程序

登记册的规则表写着：

| CLASS | 名称 | 取代资格 |
| :--- | :--- | :--- |
| H | Historical Snapshot | **YES** |
| C | **Current-State Invariant** | **NO** |

而 `ASN-SG-MIG-0017-HEAD` **就是 CLASS C**。

**这份登记册是在 0017 时创建的，从未经历过一次迁移头推进**，所以这个缺口此前没有暴露：

- 三条 CLASS H（`ASN-P200-MIG-0013-HEAD`、`ASN-P200-MIG-NO0014`、`ASN-P1RW-MIG-0013-HEAD`）指向唯一的 CLASS C 终点；
- 按设计，**推进 head 就是取代那个 C**，但规则表说 C 不可被取代。

矛盾之处：**机制上是支持的**。验证器（`verify-invariant-supersessions.py:524`）要求被取代条目具备 `REPLAY_KIND ∈ ("PYTEST",)` 与可用的回放测试 —— 它能取代任何条目，**包括 CLASS C**。所以是**正文的规则表**堵住了这条路，代码没有。

> 另一条路是「不加条目，把 C 解释为指向 head-agnostic 测试的指针」。**不推荐**：那样会丢掉"head 曾被推进到 0017"这个事实，而记录这类事实正是登记册存在的理由。

## 3. 逐字补丁（推荐方案）

### 3.1 规则表：CLASS C 的取代资格

**改** `## Invariant classes` 表内 C 行：

```diff
-| C | Current-State Invariant | Asserts the current tree state (e.g. current migration head = 0015) | NO | Always (active replacement assertions) |
+| C | Current-State Invariant | Asserts the current tree state (e.g. current migration head = 0015) | YES — only by a successor Class C asserting a later authorized head | Always (active replacement assertions) |
```

**新增**一句到 `## Invariant classes` 表下：

> 迁移头推进时的取代规则：当一次经授权的迁移使 head 前移，原 Class C 条目转 `SUPERSEDED`，`SUPERSEDED_BY_ASSERTION_ID` 指向新的 Class C；旧条目须补齐 `REPLAY_*`，其回放基线为它断言的那个 head 生效期间的提交，回放测试为当时断言该 head 的测试。

### 3.2 `ASN-SG-MIG-0017-HEAD`：转 SUPERSEDED 并补齐回放字段

```diff
  ASSERTION_ID: ASN-SG-MIG-0017-HEAD
  CLASS: C
- STATUS: ACTIVE
+ STATUS: SUPERSEDED
  HISTORICAL_TEST: N/A (current-state assertion, not a historical test)
  INTRODUCED_AT_BASELINE: affa612615a239abd2c24f486ea91bef3b8de049
  INTRODUCED_AT_ROLE: P2_REDACTION_PIPELINE_MIGRATION
  HISTORICAL_EXPECTATION: N/A
- SUPERSEDED_BY_ASSERTION_ID: N/A
+ SUPERSEDED_BY_ASSERTION_ID: ASN-SG-MIG-0018-HEAD
  AUTHORITY_TYPE: N/A
  AUTHORITY_ID: N/A
  AUTHORITY_DOCUMENT: N/A
  EFFECTIVE_FROM: affa612615a239abd2c24f486ea91bef3b8de049
- CURRENT_REPLACEMENT_TEST: apps/backend/tests/test_phase2_media.py::test_p2_current_migration_head_0017
- REPLAY_BASELINE: N/A
- REPLAY_BASELINE_ROLE: N/A
- REPLAY_KIND: N/A
- REPLAY_TEST: N/A
- RATIONALE: Current-state replacement: single linear Alembic head 0017, revisions 0001..0017, …
+ CURRENT_REPLACEMENT_TEST: apps/backend/tests/test_phase2_media.py::test_p2_current_migration_head
+ REPLAY_BASELINE: <待定 —— 见 §6>
+ REPLAY_BASELINE_ROLE: <待定 —— 见 §6>
+ REPLAY_KIND: PYTEST
+ REPLAY_TEST: tests/test_phase2_media.py::test_p2_current_migration_head_0017
+ RATIONALE: Current-state replacement: single linear Alembic head 0017, revisions 0001..0017, chain linear, authorized by governed supersession 0016->0017（…原文保留…）。**SUPERSEDED**：0018 经 P-1 授权推进 head（公开/研究分界写入数据库），原语料库 head 0017 的快照由 ASN-SG-MIG-0018-HEAD 取代。
```

> `REPLAY_*` 留待定值，因为**回放基线必须真实通过**才能写入（见 §6）。填一个没验证过的基线等于给登记册造假。

### 3.3 新增条目 `ASN-SG-MIG-0018-HEAD`

置于 `ASN-SG-MIG-0017-HEAD` 之后：

```
### ASN-SG-MIG-0018-HEAD

（code fence 内）
ASSERTION_ID: ASN-SG-MIG-0018-HEAD
CLASS: C
STATUS: ACTIVE
HISTORICAL_TEST: N/A (current-state assertion, not a historical test)
INTRODUCED_AT_BASELINE: 6023f0a0000000000000000000000000000000（应用时填实测 SHA）
INTRODUCED_AT_ROLE: <见 §6 —— 需授权方给出正式角色名>
HISTORICAL_EXPECTATION: N/A
SUPERSEDED_BY_ASSERTION_ID: N/A
AUTHORITY_TYPE: N/A
AUTHORITY_ID: N/A
AUTHORITY_DOCUMENT: N/A
EFFECTIVE_FROM: <应用时填实测 SHA>
CURRENT_REPLACEMENT_TEST: apps/backend/tests/test_phase2_media.py::test_p2_current_migration_head
REPLAY_BASELINE: N/A
REPLAY_BASELINE_ROLE: N/A
REPLAY_KIND: N/A
REPLAY_TEST: N/A
RATIONALE: Current-state replacement: single linear Alembic head 0018, revisions 0001..0018, chain linear, authorized by governed supersession 0017->0018（access-boundary + ledger-link schema evolution: media_assets.access_scope 把公开/研究的分界变成 schema 约束（默认 research，失败即关闭），并加 ledger_id 恢复 documents.source_asset_id 到 media_assets 的连接）。取代 ASN-SG-MIG-0017-HEAD。HFB M0-M7 executed = 0。
```

### 3.4 三条 CLASS H 条目的两处引用

三个条目（`ASN-P200-MIG-0013-HEAD`、`ASN-P200-MIG-NO0014`、`ASN-P1RW-MIG-0013-HEAD`）各有两行需改：

```diff
- SUPERSEDED_BY_ASSERTION_ID: ASN-SG-MIG-0017-HEAD
+ SUPERSEDED_BY_ASSERTION_ID: ASN-SG-MIG-0018-HEAD

- CURRENT_REPLACEMENT_TEST: apps/backend/tests/test_phase2_media.py::test_p2_current_migration_head_0017
+ CURRENT_REPLACEMENT_TEST: apps/backend/tests/test_phase2_media.py::test_p2_current_migration_head
```

> **为什么测试要改名**：原名把版本号写进标识符，于是**每推进一次 head 就要改一次名字，并连带打断登记册与 `infra/scripts/test-release-gate-precheck.sh` 的按名引用**。这是同一族缺陷的第三处（前两处：闸门脚本硬编码 head、operator 脚本钉死版本号）。改成不带版本号的稳定名后，此后只需改测试体内的断言。

### 3.5 尾部计数

```diff
- DECLARED_TOTAL: 10
+ DECLARED_TOTAL: 11
  DECLARED_CLASS_H: 3
  DECLARED_CLASS_P: 3
- DECLARED_CLASS_C: 1
+ DECLARED_CLASS_C: 2
  DECLARED_CLASS_B: 2
  DECLARED_CLASS_A: 1
  DECLARED_ACTIVE: 7
- DECLARED_SUPERSEDED: 3
+ DECLARED_SUPERSEDED: 4
```

校验：3+3+2+2+1 = **11** ✓ ；7+4 = **11** ✓ ；ACTIVE 不变（旧 C 转出、新 C 转入，各一）✓

### 3.6 尾部链描述

```diff
- Supersession chain: ASN-P200-MIG-0013-HEAD, ASN-P200-MIG-NO0014, ASN-P1RW-MIG-0013-HEAD
- → ASN-SG-MIG-0017-HEAD (no cycles; each resolves to exactly one ACTIVE terminal).
+ Supersession chain: ASN-P200-MIG-0013-HEAD, ASN-P200-MIG-NO0014, ASN-P1RW-MIG-0013-HEAD
+ → ASN-SG-MIG-0017-HEAD → ASN-SG-MIG-0018-HEAD
+ (no cycles; each resolves to exactly one ACTIVE terminal, ASN-SG-MIG-0018-HEAD).
```

## 4. 需同步的代码与脚本

| 文件 | 改动 |
| :--- | :--- |
| `apps/backend/tests/test_phase2_media.py` | `test_p2_current_migration_head_0017` → `test_p2_current_migration_head`；函数体注释里"登记册按名引用"那段随之更新 |
| `infra/scripts/test-release-gate-precheck.sh` | 两处节点引用（第 76、86 行）改为新名 |

**必须与登记册改动同一提交**，否则登记册会指向一个不存在的节点，其防护变成空转却仍然报 PASS。

## 5. 顺带发现的既有不准确

`ASN-SG-MIG-0017-HEAD` 的 `INTRODUCED_AT_BASELINE` 写作 `affa612`，但**该基线的 head 是 0016**，测试名也是 `test_p2_current_migration_head_0016`（`git ls-tree affa612 apps/backend/alembic/versions/` 末项为 `0016_research_annotations.py`）。该条目应当是更晚的提交引入的。**建议授权方一并核实**。

## 6. 应用前必须补齐或验证的项

| # | 项 | 为什么不能凭空填 |
| :--- | :--- | :--- |
| 1 | `REPLAY_BASELINE` | 两个硬约束：验证器要求它是 `EFFECTIVE_FROM` 的**祖先**（`is_ancestor`，`:461`），且该提交上回放测试**真能跑过**（在隔离 worktree 里实跑）。填错即 FAIL |
| 2 | `REPLAY_BASELINE_ROLE` 与新条目的 `INTRODUCED_AT_ROLE` | 验证器只在角色名**已存在于** `BASELINE_ROLES`（`:118`）时才校验其绑定的提交。**新角色名会被静默接受、绑定检查不发生** —— 所以新角色名需授权方定义并**同时加入 `BASELINE_ROLES`**，否则字段形同虚设 |
| 3 | 应用时的实测 SHA | 草案写作时 P-1 尚未提交 |
| 4 | 跑通验证器 | `verify-invariant-supersessions.py` 须 `PASS`，含回放与替换测试的**实跑**（当前登记册为 3 次回放 + 2 次替换测试） |

> §6 各项的判据取自 `scripts/verify-invariant-supersessions.py` 的实际代码，非其文档描述。两者若有出入，以代码为准。

## 7. 需授权方裁定

1. **是否采纳方案 A**（新增后继 C 条目），还是选择"不加条目、C 改为 head-agnostic"的方案 B。
2. **CLASS C 取代资格那一行规则**是否照 §3.1 修订。
3. **新的 `INTRODUCED_AT_ROLE` 叫什么** —— 本次推进的正式角色名。
4. §5 那处既有不准确是否一并更正。

---

> 本草案**不修改**目标登记册，也不代表其中任何改动已获批准。应用需授权方按治理流程签署。

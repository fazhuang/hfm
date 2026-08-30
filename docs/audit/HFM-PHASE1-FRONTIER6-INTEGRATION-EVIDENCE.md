# HFM Phase 1 — Frontier-6 Integration Evidence（P1-11 + P1-12 受控集成）

Date: 2026-09-01 · Phase 1 — Frontier-6 Controlled Integration（P1-11 + P1-12）
Authoritative starting baseline: `31c882145150dbae0da66573b275f8f5dbb7348c`（Frontier-5 Acceptance Archive）
Integration branch: `phase1/frontier-6-integration`
证据契约：HFM-PHASE1-EVIDENCE-CONTRACT-v1.md（E-11/E-12）

## 已验收候选（本集成仅搬运、不改写）

| WP | 已验收候选 SHA | 状态 |
| --- | --- | --- |
| P1-11 | `6feeb164a6e3eefa5d7c463e6e4a0899a339d95c` | ACCEPTED（public portal） |
| P1-12 | `0ed47d648efa1478e999439333dc32d36e080831` | ACCEPTED（research workspace；含完整历史链 6ea0148 → 814b579 → 0ed47d6） |

## 集成方法

- 从权威基线 `31c8821` 创建干净集成分支 `phase1/frontier-6-integration`（tracked worktree clean 后开始；未从任一特性工作树携带残余状态）。
- 以 squash 方式按序应用 P1-11、P1-12 已验收最终候选至索引（`git merge --squash`，不产生中间提交），冲突后手工语义并集解析，全部门禁通过后以**单一原子提交**产出集成候选。
- 未 rebase、未 amend、未改写任何已验收候选历史；两个候选的原始提交与 SHA 在其原分支保持原样。

## 实际冲突

| 文件 | 分类 | 解析 |
| --- | --- | --- |
| `apps/backend/src/hfm/api/v1/phase1.py` | TEXTUAL_ONLY（预期） | 语义并集：保留 P1-11 公共门户 3 路由（`/public/home`、`/public/works`、`/public/works/{work_id}/editions`）+ `PortalService` 导入；同时保留 P1-12 研究工作台 10 路由（projects ×5、notes ×5）+ `ResearchWorkspaceService` 导入 + `_raise_workspace_error`。双方接受的表面全部保留，无 `--ours`/`--theirs` 整体丢弃。 |

无其他文件冲突；无迁移冲突；无路由重复注册（51 条路由路径全部唯一）。

## 集成授权语义增量

- 集成新增文件：`tests/test_phase1_frontier6_integration_boundary.py`（DoD-07 组合边界集成测试，仅测试集成行为，未改变任何已验收特性语义）。
- `phase1.py` 的并集是 P1-11 与 P1-12 各自接受内容的机械并集。
- 其余实现文件（portal.py、research_workspace 服务/模型、identity.py、0013 迁移、conftest.py、各测试、各 WP 实现证据）逐字节等于对应已验收候选。
- 结论：`INTEGRATION_AUTHORED_SEMANTIC_DELTA = 0`（仅上述集成专属测试与并集文件）。

## DoD-07 组合边界（集成专属测试）

同一数据集同时含已发布内容与私有研究工作台状态，验证：

- 匿名 principal 可访问公共门户，但研究工作台全部方法失败关闭（5/5 PermissionError）；
- 公共门户响应保持严格白名单（home/works/editions 键集精确），工作台项目/笔记内容、`owner_id`、research 元数据零泄露；
- 撤回（withdraw）立即移除公共可见性，即使相关研究工作台状态存在；工作台状态保持完好。

结果：`PUBLIC_TO_RESEARCH_LEAKAGE = 0`；`RESEARCH_TO_PUBLIC_LEAKAGE = 0`。

## 集成回归

| 套件 | 结果 |
| --- | --- |
| P1-11 聚焦（test_phase1_portal.py） | 14 PASS（= 已验收参考 14） |
| P1-12 聚焦（test_phase1_research_workspace.py） | 21 PASS（= 已验收参考 21） |
| DoD-07 集成边界（test_phase1_frontier6_integration_boundary.py） | 3 PASS |
| RBAC/auth + Evidence/Reader/Search/Publication/C-domain/Governance + 迁移前置回归批次 | 90 PASS（含 test_phase1_rbac.py、test_migrations.py、evidence chain、reader、search、publication、c_domain、governance、citation_evidence、evidence_provenance） |
| 全量 pytest | **397 passed / 0 failed** |
| Ruff check | PASS |
| Ruff format --check | PASS（160 files） |
| mypy（src tests） | Success: no issues found in 146 source files |

## 迁移

- P1-11 无迁移；P1-12 持有 `0013_p1_frontier6_research_workspace`。
- 拓扑：`0012 → 0013`，单一 Alembic head（`0013 (head)`）；无 0014、无合成合并迁移、无迁移改写。
- 迁移门禁（test_migrations.py 20 项 + P1-12 迁移 2 项：upgrade/downgrade-across-0013/upgrade-again/single-head/FK+checks）全部通过。

## C 域安全

- 集成树无临床推荐行为：diagnosis / treatment recommendation / decision support / 自动针灸处方 / 主穴配穴推荐 / personalized medical advice 均不存在（新增代码中的命中仅为 AB-14 否定声明注释）。`C_DOMAIN_CLINICAL_BEHAVIOR = 0`。

## HFB 运行时隔离

- HFB runtime 依赖新增 = 0（pyproject 依赖与基线一致；无依赖文件变更）。
- 生产环境 HFB Import：`NOT PERFORMED / NOT AUTHORIZED`（src/tests 源码 0 处 `import hfb`；树内命中仅为既有注释性引用与编译缓存）。

## 范围控制

- 冻结治理文档变更 = 0（Scope/DAG/Acceptance/Evidence/DoD/Boundary/Authorization/ADR 均未修改）。
- deferred 特性实现 = 0；未授权新增 = 0；CD-7 = NONEXISTENT（既有 governance 负向守卫确认）。
- 未启动任何后续 WP/frontier。

## 说明

本文件为 Frontier-6 集成证据，记录集成事实与门禁结果；正式 Frontier-6 ACCEPTED 判定权属 Codex，本文件不预先声明接受。

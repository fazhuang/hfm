# HFM-FINAL-DELIVERY-GATE.md — 三层独立交付门禁标准 (Delivery Gates)

---

## GATE-A: 软件发布门禁 (Software Release Gate)

**目标**：验证当前 Release Candidate (RC) 代码库作为一个高可用软件系统是否具备发布资格（无软件发布阻断项）。

| 检查项 | 验证方式 | 准入标准 | 当前状态 |
|---|---|---|---|
| **静态构建与类型检查** | `pnpm build && pnpm typecheck` | 零类型报错，顺利打包出 production bundle | **PASS** |
| **前端单元测试** | `pnpm --filter frontend test -- --run` | 235 个用例全部通过 | **PASS** |
| **后端单元/接口测试** | `pytest apps/backend/tests -q` | 682 个用例全部通过 | **PASS** |
| **运维测试与发布打包** | `pytest scripts/tests/ -q` | 51 个用例全部通过 | **PASS** |
| **数据库迁移一致性** | 升级到 HEAD `0014` 并执行回滚测试 | 迁移链无报错、无孤立版本 | **PASS** |
| **系统运行时健康探测** | `/health`, `/live`, `/version` 接口 | 返回 HTTP 200 + 预期 JSON | **PASS** |
| **R0 级发布阻断项** | 检查当前未解决的 R0 数量 | R0 = 0 (无任何发布阻断缺陷) | **PASS** |

> **裁决：GATE_A_SOFTWARE_RELEASE = PASS（当前 RC 无发布阻断项，SOFTWARE_RELEASE_READY = YES）。**
>
> *(注：REM-01 与 REM-02 属于 R1 级“交付必须但非发布阻断”功能，阻断的是 Gate B 客户最终交付，不阻断 Gate A 软件本身的发布可用资格。)*

---

## GATE-B: 客户交付门禁 (Customer Delivery Gate)

**目标**：验证向最终客户交付的成套软件、数据与文档资产是否完备（满足本期所有 R1 交付要求）。

| 检查项 | 验证方式 | 准入标准 | 当前状态 |
|---|---|---|---|
| **GATE-A 状态** | 检查 Gate A 状态 | 必须已处于 PASS 状态 | **PASS** |
| **最低可交付数据集 (MVDD)** | 抽检 8 大页面数据呈现 | 无空白页、无 404 碎链、骨干数据完整 | **PASS** |
| **生产环境初始化与安全** | `initialize-production.py` 演练 | 安全创建单管理员，无默认明文密码 | **PASS** |
| **部署与运维文档** | 核查 Runbook 与配置模版 | 具备详尽的从零启动与部署手册 | **PASS** |
| **REM-01: 工作台写 UI** | 检查在线项目/笔记表单及 API 联通 | 学者可在线新增项目与笔记并持久化 | **OPEN (待实现 REM-01)** |
| **REM-02: 首页后端接口接入** | 检查 HomeView 接口请求与降级 | 平滑接入 /public/home 并保持离线降级 | **OPEN (待实现 REM-02)** |
| **REM-03: 业务用户指南** | 核查业务图文手册 | 具备《用户与学者操作指南》 | **OPEN (待编撰 REM-03)** |

> **裁决：GATE_B_CUSTOMER_DELIVERY = OPEN (待完成 REM-01、REM-02、REM-03 三项 R1 交付工作后正式关闭)。**

---

## GATE-C: 内容深加工完成门禁 (Content Completion Gate)

**目标**：验证 515 篇当代学术论文全文与《针灸甲乙经》349 个穴位深度数字化加工是否全部完成。

| 检查项 | 验证方式 | 准入标准 | 当前状态 |
|---|---|---|---|
| **349 穴位全量入库** | 数据库查询 `c_domain_terms` 数量 | count >= 349，具备定位与主治 | **OPEN (属于 R2 交付后工作)** |
| **全本 128 篇经文条文入库**| 数据库查询 `passages` 数量 | 万条经文条文数字化完成并挂接卷篇 | **OPEN (属于 R2 交付后工作)** |
| **515 篇论文全文检索** | 数据库检索 `searchIndex` 论文数 | 可全文检索 515 篇当代核心期刊论文 | **OPEN (属于 R2 交付后工作)** |

> **根本裁决契约：**
>
> ```text
> GATE_C_CAN_REMAIN_OPEN_AFTER_GATE_B = YES
> ```
>
> **GATE-C 属于交付后持续内容运营轨，不阻断 GATE-A 与 GATE-B 的关闭，亦不阻断系统向客户的正式交付与结项演示。**

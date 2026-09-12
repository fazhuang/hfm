# HFM NPG-R1 治理输入冻结清单（Governance Input Manifest）

Status: GOVERNANCE INPUT FREEZE · Date: 2026-08-29 · Branch: `governance/next-phase-authorization`
用途：绑定 NPG-R1 治理输入工件（路径 + SHA-256 + 角色 + 权威等级 + 绑定状态）。

## 绑定基线

```text
Parent Baseline:
0167b1702dac13993a5206f63752eafcc8e5387e（HFM Phase 0.4 Completion Baseline）

Governance Branch:
governance/next-phase-authorization（自 0167b17 创建；仅承载治理/审计证据，非 Phase 1 实现）
```

## 工件登记（Artifact Register）

| 路径 | SHA-256 | 文档角色 | 权威等级 | 绑定状态 |
| --- | --- | --- | --- | --- |
| docs/governance/inputs/HFM-CLIENT-CONFIRMED-REQUIREMENTS-v1.md | `6130a25796f1f4c88fee993d5d39b3f6c6391027f4102855d4c9cc24dc37b453` | 客户需求源归档（CR-001…CR-010 L1 事实） | L1 | GOVERNANCE INPUT（冻结） |
| docs/governance/inputs/HFM-GEMINI-ORIGINAL-IMPLEMENTATION-PROPOSAL-v1.md | `a5e99532934a1ef91dffa65f0e35c6b1d2dbc8b6645ff17aa5e14f1e002c04eb` | Gemini 原始提案归档（A–R 枚举；非约束） | L3 | REFERENCE INPUT（非绑定） |
| docs/governance/HFM-CONTENT-ASSET-REQUEST-REGISTER-v1.md | `ac839ef477ba52a982979b9ad09af564ffbd0905bb0358a32fdc2bccc43f5311` | 内容资产请求登记（CA-01…CA-10 + G4B 阻塞分类） | L1/L2 派生 | GOVERNANCE INPUT（冻结） |
| docs/audit/HFM-NPG-000-BASELINE-INTEGRITY-AUDIT.md | `06b0e745ae6193f7d09fe1721f4bf9f7c48d31da4773b5be357fb4d07c374e7f` | 基线完整性审计 | L1（审计事实） | AUDIT REPORT（保留） |
| docs/audit/HFM-NPG-001-CUSTOMER-REQUIREMENT-AUTHORITY.md | `710af440b57f525c7500b5d0669f445199d9dafd14fd561e64f0848501d3e25d` | 客户需求权威登记 | L1/L2/L3 分层 | AUDIT REPORT（保留） |
| docs/audit/HFM-NPG-002-GEMINI-PROPOSAL-SEPARATION.md | `504f621b91d01daf38ca6b45a5edb86eec575e02749923f4a0f331845db60ab5` | Gemini 提案需求/设计分离审计 | L3 审计 | AUDIT REPORT（保留） |
| docs/audit/HFM-NPG-003-CURRENT-CAPABILITY-INVENTORY.md | `6df60d94f92195256399c06b24fdd05c66e81faf939575695accee660eb02b1b` | 现有能力盘点 | L1（事实） | AUDIT REPORT（保留） |
| docs/audit/HFM-NPG-004-HFB-ASSET-REUSE-AUDIT.md | `cc2a9501bec9a6461ab4d1e0264c1e20738dcde8e2688c9301eaa99d5dec2f2a` | HFB 资产复用审计 | L1/L2 | AUDIT REPORT（保留） |
| docs/audit/HFM-NPG-005-CONTENT-ASSET-GAP-ANALYSIS.md | `dabfeca6e7998bc5f51f12d8cf001988475297bef1699adf412ed4aa2f0622d5` | 内容资产缺口分析 | L1/L2 | AUDIT REPORT（保留） |
| docs/audit/HFM-NPG-BOUNDARY-REGISTER.md | `53e9b0ea57d10101001a33a1bf783e20291bc4da63e994bc715ca30d749fc837` | 边界登记 | L1/L2 | GOVERNANCE REGISTER（保留） |
| docs/audit/HFM-NPG-000-005-FACT-AUDIT-SUMMARY.md | `b2f473e89dcfaaa97e159d4487970df482d5dca7242f530338865178eaf31d0a` | NPG-000…005 事实审计摘要 | L1（审计事实） | AUDIT REPORT（保留） |

## 权威与绑定语义

```text
L1 = 客户显式确认事实（冻结为需求依据，不改写）
L2 = 必然派生（标注派生依据，不提升实现方案）
L3 = 设计/交付/技术提案（不具约束力；不提升为客户需求）

GOVERNANCE INPUT（冻结）:
- 客户需求源归档与内容资产登记 — 作为未来 Scope/ADR/验收的输入基座
- 修改须经治理流程，不得单方改写客户事实

REFERENCE INPUT（非绑定）:
- Gemini 提案归档 — 仅参考；显式声明不提升 Three.js/WebGL/WebXR/Neo4j/
  Elasticsearch/MinIO/WebSocket/ECharts/D3.js/720VR/8-week 为客户需求

AUDIT REPORT（保留）:
- 8 份 NPG 审计报告 + 边界登记 — 实质发现不得修改
```

## 完整性声明

```text
本清单在提交前对每个工件计算 SHA-256 并绑定；
提交后以 git 提交冻结工件内容；
后续任何工件内容变更将导致 SHA-256 漂移，须重新审计。
```

## 交叉引用

- 客户需求源：`docs/governance/inputs/HFM-CLIENT-CONFIRMED-REQUIREMENTS-v1.md`
- Gemini 提案归档：`docs/governance/inputs/HFM-GEMINI-ORIGINAL-IMPLEMENTATION-PROPOSAL-v1.md`
- 内容资产登记：`docs/governance/HFM-CONTENT-ASSET-REQUEST-REGISTER-v1.md`

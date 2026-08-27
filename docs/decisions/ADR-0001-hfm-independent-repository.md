# ADR-0001: HFM 采用独立仓库并选择性复用 HFB

Status: Accepted

## Context

HFB 已形成较成熟的皇甫谧研究平台能力，但 HFM 的产品目标已经扩展为：

- 公众文化传播
- 高校科研
- 教学辅助
- 非遗展示
- 政府成果展示
- 专业研究

HFM 与 HFB 在产品中心、信息架构、发布模式、媒体治理和公众访问模式上存在显著差异。

## Decision

HFM 建立独立 Git 仓库。

采用：

Architecture Greenfield + Capability Brownfield

HFB 作为：

- 技术能力来源
- 数据资产来源
- 研究成果来源
- 参考实现

而不是作为 HFM 必须继承的基础代码体。

所有 HFB 资产进入 HFM 前必须经过：

- REUSE
- EXTEND
- ADAPT
- DEPRECATE
- NEW

裁决。

## Consequences

HFM 可以独立设计：

- Domain Model
- Publication Architecture
- Public Portal
- Rights Governance
- Teaching Model
- Medical Compliance

同时避免重复开发 HFB 已成熟能力。

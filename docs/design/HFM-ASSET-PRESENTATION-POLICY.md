# HFM 资产展示政策 — Asset Presentation Policy

Status: DESIGN INPUT（UI-00 Design Baseline Closure v2 · 客户授权规则 + 隐私模型 · 不实施运行时代码）
Date: 2026-09-01 · 配套: HFM-CONTENT-ASSET-MAP / HFM-UI-CONTENT-MODEL
正式前提（客户声明，最高业务输入优先级）:

- 本项目客户提供资料统一视为**已经获得授权**，允许**全部公开发布**。
- 平台属于官方公益性文化传播平台；非商用、无盈利目的。
- 后续如产生版权问题，由客户自行后置解决。
- **项目开发阶段不再考虑客户材料版权问题。**

---

## 0. 授权规则（唯一事实）

```text
CUSTOMER_PROVIDED = TRUE
→ PUBLICATION_AUTHORIZATION = GRANTED
→ PUBLIC_VISIBILITY 默认 = PUBLIC
```

- 版权**不作为**开发约束、UI 阻塞、内容迁移阻塞或 WP Entry Gate。
- 例外边界（不得错误扩展）：**隐私、敏感个人信息、安全信息仍属独立治理问题**；
  "客户材料可公开" ≠ "所有个人信息均可无条件公开"。

---

## 1. 从开发工作流中取消的项（客户授权后）

以下项从 UI/开发工作流取消（不在开发准入条件、UI fail-closed、迁移阻塞、全文展示/播放/缩略图/搜索展示限制中继续出现）：

- 客户材料版权逐件核验
- `RIGHTS_CLASS` / `R0 / R1 / R2 / R3`
- `COPYRIGHT_PENDING` / `LICENSE_PENDING`
- 因版权状态产生的 `AUTHORIZED_PUBLIC` 中间状态
- 因版权状态导致的 public fail-closed
- 因版权问题禁止全文展示 / 禁止电影媒体播放 / 禁止缩略图 / 禁止搜索结果展示 / 阻塞内容迁移
- RIGHTS DATA-GAP
- 版权作为 UI-01 或后续 WP 的 Entry Gate

**处理方式**：若上述标识已用于其他正式治理语义（历史记录/迁移契约），**不得粗暴删除**；标记为 `NOT_REQUIRED_FOR_CUSTOMER_PROVIDED_ASSETS`，并附本客户授权规则说明。

---

## 2. 资产字段模型（保留）

客户资产统一按以下字段管理（替换原版权核验字段）：

| 字段 | 说明 | 默认值 |
| --- | --- | --- |
| ASSET | 资产标识/文件 | — |
| SOURCE | 来源（客户目录路径/批次） | — |
| ENTITY | 关联内容实体 | — |
| CONTENT_TYPE | 内容类型（传记/其言/论著/论文/证书/影像/媒体报道…） | — |
| PUBLIC_VISIBILITY | 公开可见性 | **PUBLIC**（除非存在明确 PRIVACY/SECURITY/GOVERNANCE 原因） |
| PRIVACY_CLASS | 隐私分级 | P0（见 §4） |
| UI_SURFACE | 目标 UI 面（旗舰页/列表/检索…） | — |
| EVIDENCE_STATUS | 证据状态（绑定/待绑定） | 待绑定 |

---

## 3. 论著/论文/影像展示策略（版权取消后）

| 资产 | 展示策略 |
| --- | --- |
| 论著 ≈100 件 | Work/Edition/BibliographicRecord 模型展示；数字资源按实际文件提供（有文件才给全文/预览） |
| 论文 ≈515 篇 | **BibliographicSearch**（题录检索 + filters + 高密度 Result List）；有全文 → 全文阅读入口；仅题录 → 题录。由实际资产决定，不制造不存在全文 |
| 电影/影像 2 部 | MediaRecord + 播放器（存在视频文件才可播放；无文件不伪造播放能力） |
| 版本脉络 PNG | 正式公共展示资产（图片允许公开）；结构化关系仍为 JIAYI_EDITION_RELATIONS [DATA-GAP] |

---

## 4. 隐私模型（与版权拆分，独立存在）

| 级 | 定义 | 适用示例 | UI 行为 |
| --- | --- | --- | --- |
| P0 | 普通公开内容 | 平台叙事、著作文本、公开成就描述 | 正常公开 |
| P1 | 职业/学术/公共身份信息 | 职称、学术兼职、公开荣誉、职务 | 正常公开（刘君奇档案主体） |
| P2 | 需要脱敏的个人信息 | 证书编号、签字、身份证号、私人电话、私人住址、银行账户、登录凭证 | 生成 public derivative（脱敏后）再公开 |
| P3 | 不应公共展示的敏感信息 | 法人证照原件、考评员名单、不动产证明、内部申报表、其他高风险个人识别信息 | 不进入公共投影；仅归档/按 RBAC 受限 |

### 4.1 脱敏处理管线

```text
SOURCE ASSET（原始材料，zzcl/hfmzl 原样保留）
   ↓ 必要时生成 PUBLIC DERIVATIVE（P2 脱敏：遮挡编号/签字/联系方式等）
PUBLIC PRESENTATION（UI 仅消费 public derivative）
```

- **不因材料中存在一个敏感字段而废弃整份材料**；按字段级脱敏最大化利用客户内容、最小化不必要个人信息暴露。
- zzcl 重点检查：证书、申报表、人员名单、法人资料、联系方式、身份证明、签字、其他个人信息。
- 此为本项目**开发阶段业务前提**；具体脱敏执行属内容准入实施 WP，不在本轮。

---

## 5. 与既有文档的一致性

- `HFM-CONTENT-ASSET-MAP.md §3 展示分级（A/B/C）` 的**版权维度**由本政策取代；保留其中的**隐私维度**（A/B/C 与 P0–P3 对齐：A≈P0/P1，B≈P2 脱敏后公开，C≈P3 归档）。
- `HFM-UI-DESIGN-AUDIT.md §12.1` 中"论著/论文多为第三方版权须逐件登记"表述由本政策取代（客户授权）；隐私脱敏要求保留。
- 原 RIGHTS 相关 [DATA-GAP] 一律从开发阻塞清单移除；RIGHTS 退出 UI-01 Entry Gate。

---

## 6. 边界声明

1. 本政策是**开发阶段业务前提**，不改变正式 Governance Baseline / Scope Register 判定。
2. "客户材料允许公开发布" ≠ 本轮立即执行正式内容迁移；迁移仍属后续实施 WP。
3. 版权取消不扩展到隐私：P2/P3 处理按独立治理执行。
4. 若后续出现**非客户来源**内容（第三方新增、用户上传），版权约束对该类内容恢复适用（组件 RightsState/RestrictedContentState 保留备用，但不得用于阻塞本批客户材料）。

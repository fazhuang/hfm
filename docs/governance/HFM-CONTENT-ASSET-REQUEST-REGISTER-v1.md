# HFM 内容资产请求登记 v1（Content Asset Request Register）

Status: GOVERNANCE INPUT · Date: 2026-08-29 · Branch: `governance/next-phase-authorization`
用途：将当前未知的客户内容条件转化为显式获取/核验项。
状态取值（仅允许）：`RECEIVED` / `PARTIAL` / `NOT_RECEIVED` / `CLIENT_CONFIRMATION_REQUIRED` / `RIGHTS_CONFIRMATION_REQUIRED` / `TECHNICAL_VALIDATION_REQUIRED`
阻塞分类（R1-G4B）：`PLATFORM_BLOCKER` / `CONTENT_IMPORT_BLOCKER` / `CONTENT_PUBLICATION_BLOCKER` / `ACCEPTANCE_BLOCKER` / `NON_BLOCKING`

> 规则：缺失内容文件**不自动**标记为 PLATFORM_BLOCKER；分类须依据对平台/导入/发布/验收的实际影响。客户确认“拥有”某资产 ≠ 文件已交付仓库（依 NPG-005 §1）。

## 登记字段（每个包均记录）

```text
PACKAGE-ID / Asset Name / Business Domain / Customer Confirmed Existing? /
Actual Files Received? / Expected Quantity / Actual Quantity / Format / Version /
Source / Provenance / Rights Holder / Internet Publication Allowed? /
Teaching Use Allowed? / Download Allowed? / Modification Allowed? /
Sensitive/Internal? / Digitization Required? / OCR Required? /
Normalization Required? / Evidence Complete? / Responsible Provider /
Blocking Effect / Status / Notes
```

---

## CA-01 皇甫谧人物生平与权威史料

| 字段 | 值 |
| --- | --- |
| PACKAGE-ID | CA-01 |
| Asset Name | 皇甫谧人物生平与权威史料 |
| Business Domain | A 皇甫谧人物档案 |
| Customer Confirmed Existing? | YES（客户确认有史料） |
| Actual Files Received? | NO |
| Expected Quantity | 未知（史料目录 + 逐条定位） |
| Actual Quantity | 0 |
| Format | 待定（原件/影印/PDF/文本） |
| Version | N/A |
| Source | 客户提供（书目/馆藏/取得方式待登记） |
| Provenance | 未登记 |
| Rights Holder | 未知 |
| Internet Publication Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Teaching Use Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Download Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Modification Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Sensitive/Internal? | 待确认（史料引用≠可公开全文） |
| Digitization Required? | CLIENT_CONFIRMATION_REQUIRED |
| OCR Required? | CLIENT_CONFIRMATION_REQUIRED |
| Normalization Required? | 是（人名/地名/纪年/异名） |
| Evidence Complete? | NO |
| Responsible Provider | 客户（史料目录与事件证据表） |
| Blocking Effect | CONTENT_IMPORT_BLOCKER |
| Status | CLIENT_CONFIRMATION_REQUIRED |
| Notes | 每条生平事件/主张须有页/卷/条级 SourceRef→Evidence 定位；HFM 现无内容记录，HFB 仅有展示叙述（NPG-005 §2） |

## CA-02 皇甫谧著作与辑佚文献

| 字段 | 值 |
| --- | --- |
| PACKAGE-ID | CA-02 |
| Asset Name | 皇甫谧著作与辑佚文献 |
| Business Domain | B 文献与思想体系 |
| Customer Confirmed Existing? | CLIENT_CONFIRMATION_REQUIRED（作品清单/存佚状态待确认） |
| Actual Files Received? | NO |
| Expected Quantity | 未知（作品 × 版本） |
| Actual Quantity | 0 |
| Format | 待定 |
| Version | 每件须登记版本/刻本/整理者 |
| Source | 客户 |
| Provenance | 未登记 |
| Rights Holder | 未知 |
| Internet Publication Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Teaching Use Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Download Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Modification Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Sensitive/Internal? | 待确认 |
| Digitization Required? | CLIENT_CONFIRMATION_REQUIRED |
| OCR Required? | CLIENT_CONFIRMATION_REQUIRED（全文场景） |
| Normalization Required? | 是（Work/Edition/Version 规范化） |
| Evidence Complete? | NO |
| Responsible Provider | 客户 |
| Blocking Effect | CONTENT_IMPORT_BLOCKER |
| Status | CLIENT_CONFIRMATION_REQUIRED |
| Notes | 现代校注/整理本权利可能非公版；全文与元数据分开验收（CR-007） |

## CA-03 《针灸甲乙经》版本资产

| 字段 | 值 |
| --- | --- |
| PACKAGE-ID | CA-03 |
| Asset Name | 《针灸甲乙经》版本资产 |
| Business Domain | B/C 文献与数字知识库 |
| Customer Confirmed Existing? | YES（客户确认有版本） |
| Actual Files Received? | NO |
| Expected Quantity | 未知（逐版本登记） |
| Actual Quantity | 0 |
| Format | 待定（实体/扫描/PDF/图像/OCR/文本） |
| Version | 每版本独立登记 |
| Source | 客户 |
| Provenance | 未登记（馆藏号/客户资产号/哈希） |
| Rights Holder | 未知（古籍影像可能公版；现代整理/校注本未必） |
| Internet Publication Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Teaching Use Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Download Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Modification Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Sensitive/Internal? | 待确认 |
| Digitization Required? | CLIENT_CONFIRMATION_REQUIRED |
| OCR Required? | TECHNICAL_VALIDATION_REQUIRED（取决于使用场景） |
| Normalization Required? | 是（Work→Edition→Version→Chapter→Passage；卷/篇定位） |
| Evidence Complete? | NO |
| Responsible Provider | 客户（逐件资产清单 + 样本 + 哈希 + 书目 + 权利） |
| Blocking Effect | CONTENT_IMPORT_BLOCKER |
| Status | CLIENT_CONFIRMATION_REQUIRED |
| Notes | **不接受“已有《针灸甲乙经》”作为充分证据**（见下） |

### CA-03 专项要求（SPECIAL REQUIREMENTS）

对每个版本必须登记：

- 版本名称（edition name）
- 出版方 / 来源机构（publisher / source institution）
- 出版年份（如适用）
- 载体状态：实体 / 扫描 / PDF / 图像 / OCR / 文本
- 完整性（completeness）
- 页数（如已知）
- 校勘状态（proofreading status）
- 版权 / 公有领域 / 授权状态
- 引用溯源（citation provenance）
- 是否允许公开展示
- 是否允许全文下载

> “已有《针灸甲乙经》”不足以证明：版本数量、载体、数字化状态、完整性、校勘、权利与展示许可均须逐件登记（依 NPG-005 §2/§4-1-2）。

## CA-04 《针灸甲乙经》篇章结构数据

| 字段 | 值 |
| --- | --- |
| PACKAGE-ID | CA-04 |
| Asset Name | 《针灸甲乙经》篇章结构数据（128 篇） |
| Business Domain | C 数字知识库 |
| Customer Confirmed Existing? | CLIENT_CONFIRMATION_REQUIRED（“12卷128篇”仅见展示文案） |
| Actual Files Received? | NO |
| Expected Quantity | 128 篇目记录（对账验收 128/128） |
| Actual Quantity | 0 |
| Format | 结构化数据（待定 schema） |
| Version | 绑定明确 Edition/Version |
| Source | 客户（目标版本目录） |
| Provenance | 未登记 |
| Rights Holder | 依所引版本 |
| Internet Publication Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Teaching Use Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Download Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Modification Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Sensitive/Internal? | 待确认 |
| Digitization Required? | 依版本状态 |
| OCR Required? | TECHNICAL_VALIDATION_REQUIRED |
| Normalization Required? | 是（版本差异不得压成单一目录） |
| Evidence Complete? | NO |
| Responsible Provider | 客户 |
| Blocking Effect | CONTENT_IMPORT_BLOCKER |
| Status | CLIENT_CONFIRMATION_REQUIRED |
| Notes | 128 篇结构化数据是否真实存在必须显式核验（见专项） |

## CA-05 穴位 / 经络 / 病证 / 刺灸法数据

| 字段 | 值 |
| --- | --- |
| PACKAGE-ID | CA-05 |
| Asset Name | 穴位 / 经络 / 病证 / 刺灸法数据（349 穴等） |
| Business Domain | C 数字知识库 |
| Customer Confirmed Existing? | CLIENT_CONFIRMATION_REQUIRED（“349穴”仅见文案/seed） |
| Actual Files Received? | NO |
| Expected Quantity | 349 穴（+经络/病证/刺灸法 待确认） |
| Actual Quantity | 0 |
| Format | 结构化数据 |
| Version | 绑定原文 Passage/SourceRef |
| Source | 客户 |
| Provenance | 未登记 |
| Rights Holder | 依所引版本/整理者 |
| Internet Publication Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Teaching Use Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Download Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Modification Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Sensitive/Internal? | 医学解释风险高 |
| Digitization Required? | CLIENT_CONFIRMATION_REQUIRED |
| OCR Required? | CLIENT_CONFIRMATION_REQUIRED |
| Normalization Required? | 是（历史/现代术语分层；异体字） |
| Evidence Complete? | NO |
| Responsible Provider | 客户 + 医学审校责任人（如数据存在） |
| Blocking Effect | CONTENT_IMPORT_BLOCKER |
| Status | CLIENT_CONFIRMATION_REQUIRED |
| Notes | 见专项：必须显式核验 128 篇/349 穴/经络/病证/刺灸法数据是否真实存在、关系人工或 AI 生成、证据源 |

### CA-04 / CA-05 专项要求（SPECIAL REQUIREMENTS）

显式核验（不得以展示文案/seed 替代）：

- 128 篇结构化数据是否真实存在
- 349 穴数据是否真实存在
- 经络数据是否存在
- 病证数据是否存在
- 刺灸法数据是否存在
- 关系为人工整理还是 AI 生成
- 每条结构化关系的证据来源

若文件不存在：`NOT_RECEIVED`；若仅声称存在而无证据：`CLIENT_CONFIRMATION_REQUIRED`。

## CA-06 皇甫谧针灸非遗正式项目资料

| 字段 | 值 |
| --- | --- |
| PACKAGE-ID | CA-06 |
| Asset Name | 皇甫谧针灸非遗正式项目资料（项目名称/级别/证书） |
| Business Domain | D 非遗传承体系 |
| Customer Confirmed Existing? | YES（非遗证书；正式项目名称与级别未确认） |
| Actual Files Received? | NO |
| Expected Quantity | 正式认定材料（证书/公告/编号） |
| Actual Quantity | 0 |
| Format | 扫描件/官方文件 |
| Version | N/A |
| Source | 政府/主管部门正式文件 |
| Provenance | 未登记 |
| Rights Holder | 颁发机构/持证主体 |
| Internet Publication Allowed? | CLIENT_CONFIRMATION_REQUIRED（证书图像/印章/个人信息风险高） |
| Teaching Use Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Download Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Modification Allowed? | 否（脱敏/水印派生另议） |
| Sensitive/Internal? | 是（印章、编号、个人信息） |
| Digitization Required? | 是 |
| OCR Required? | 否（字段登记即可） |
| Normalization Required? | 是（机构/项目 canonical name） |
| Evidence Complete? | NO |
| Responsible Provider | 示范中心/客户 |
| Blocking Effect | CONTENT_PUBLICATION_BLOCKER |
| Status | CLIENT_CONFIRMATION_REQUIRED |
| Notes | 见专项：正式项目名称/级别/审批机构/批准日期/项目编号/认定文件/官方公开来源/代表性传承人/授权展示范围均须核验；**不得**因存在“灵台县皇甫谧中医针灸传承创新示范中心”而推断非遗项目事实 |

## CA-07 传承人及传承谱系资料

| 字段 | 值 |
| --- | --- |
| PACKAGE-ID | CA-07 |
| Asset Name | 传承人及传承谱系资料 |
| Business Domain | D 非遗传承体系 |
| Customer Confirmed Existing? | YES（传承人资料） |
| Actual Files Received? | NO |
| Expected Quantity | 名单 + 关系表 + 逐人授权 |
| Actual Quantity | 0 |
| Format | 文本/照片/音视频（待登记） |
| Version | N/A |
| Source | 客户（官方认定/师承证明/访谈档案） |
| Provenance | 未登记 |
| Rights Holder | 各传承人本人/权利人 |
| Internet Publication Allowed? | CLIENT_CONFIRMATION_REQUIRED（个人信息/肖像风险极高） |
| Teaching Use Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Download Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Modification Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Sensitive/Internal? | 是（个人信息、肖像、关系争议） |
| Digitization Required? | CLIENT_CONFIRMATION_REQUIRED |
| OCR Required? | 否 |
| Normalization Required? | 是（人名消歧、关系方向、代际） |
| Evidence Complete? | NO |
| Responsible Provider | 客户（名单 + 关系表 + 证据 + 逐人授权） |
| Blocking Effect | CONTENT_PUBLICATION_BLOCKER |
| Status | CLIENT_CONFIRMATION_REQUIRED |
| Notes | 见专项：区分官方认定代表性传承人 / 机构指定传承人 / 教师从业者 / 学术谱系成员 / 口传谱系主张；每条谱系边最终须有 source + evidence + confidence/verification |

## CA-08 灵台县皇甫谧中医针灸传承创新示范中心资料

| 字段 | 值 |
| --- | --- |
| PACKAGE-ID | CA-08 |
| Asset Name | 示范中心资料（机构/职责/展示场景） |
| Business Domain | D 非遗传承体系 |
| Customer Confirmed Existing? | CLIENT_CONFIRMATION_REQUIRED（正式机构名称已确认 CR-006；运营资料待确认） |
| Actual Files Received? | NO |
| Expected Quantity | 机构介绍/职责/场景清单 |
| Actual Quantity | 0 |
| Format | 文本/图片 |
| Version | N/A |
| Source | 客户/中心 |
| Provenance | 未登记 |
| Rights Holder | 中心 |
| Internet Publication Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Teaching Use Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Download Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Modification Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Sensitive/Internal? | 待确认 |
| Digitization Required? | 视素材 |
| OCR Required? | 否 |
| Normalization Required? | 是（机构 canonical name） |
| Evidence Complete? | NO |
| Responsible Provider | 中心/客户 |
| Blocking Effect | NON_BLOCKING（机构名已确认；运营内容不影响平台骨架） |
| Status | CLIENT_CONFIRMATION_REQUIRED |
| Notes | 正式署名必须用完整官方名称；简称“皇甫谧针灸非遗传承中心”不得作注册实体名（CR-007） |

## CA-09 学校教学 / 科研 / 活动成果

| 字段 | 值 |
| --- | --- |
| PACKAGE-ID | CA-09 |
| Asset Name | 学校教学 / 科研 / 活动成果 |
| Business Domain | A/B/D 教学与研究 |
| Customer Confirmed Existing? | CLIENT_CONFIRMATION_REQUIRED（教学/研究场景已确认 CR-008/009；成果清单待确认） |
| Actual Files Received? | NO |
| Expected Quantity | 课程/成果/活动清单 |
| Actual Quantity | 0 |
| Format | 待定 |
| Version | N/A |
| Source | 皇甫谧学院/学校 |
| Provenance | 未登记 |
| Rights Holder | 学校/作者 |
| Internet Publication Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Teaching Use Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Download Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Modification Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Sensitive/Internal? | 待确认 |
| Digitization Required? | 视素材 |
| OCR Required? | 否 |
| Normalization Required? | 视内容 |
| Evidence Complete? | NO |
| Responsible Provider | 学院/客户 |
| Blocking Effect | NON_BLOCKING（不阻塞平台骨架） |
| Status | CLIENT_CONFIRMATION_REQUIRED |
| Notes | 教学/科研成果“汇聚”是否含全文未知（CR-007）；元数据与全文分开验收 |

## CA-10 图片 / 视频 / 证书 / 媒体版权与发布授权

| 字段 | 值 |
| --- | --- |
| PACKAGE-ID | CA-10 |
| Asset Name | 图片 / 视频 / 证书 / 媒体版权与发布授权 |
| Business Domain | A/B/C/D 全域展示 |
| Customer Confirmed Existing? | YES（校园活动照片等） |
| Actual Files Received? | NO |
| Expected Quantity | 逐件媒体 + 逐件授权 |
| Actual Quantity | 0 |
| Format | 原图/视频/扫描件（待登记） |
| Version | 原始 vs 派生（web-size）分离 |
| Source | 客户（摄影者/活动记录） |
| Provenance | 未登记 |
| Rights Holder | 摄影者/权利人/参与者 |
| Internet Publication Allowed? | RIGHTS_CONFIRMATION_REQUIRED（著作权+肖像权+未成年人风险） |
| Teaching Use Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Download Allowed? | CLIENT_CONFIRMATION_REQUIRED |
| Modification Allowed? | CLIENT_CONFIRMATION_REQUIRED（裁剪/水印派生另议） |
| Sensitive/Internal? | 是（肖像、未成年人、隐私） |
| Digitization Required? | 是 |
| OCR Required? | 否（证书字段登记） |
| Normalization Required? | 是（caption/alt text/活动元数据） |
| Evidence Complete? | NO |
| Responsible Provider | 客户（逐图授权或可证明的批量授权范围 + 撤回联系人） |
| Blocking Effect | CONTENT_PUBLICATION_BLOCKER |
| Status | RIGHTS_CONFIRMATION_REQUIRED |
| Notes | 见专项：媒体权利分类；UNKNOWN 不得发布 |

### CA-10 专项要求（SPECIAL REQUIREMENTS）

每件媒体资产须权利分类：

```text
PUBLIC_DOMAIN
CUSTOMER_OWNED
LICENSED
THIRD_PARTY_PERMISSION_REQUIRED
UNKNOWN
```

**UNKNOWN 不得发布。** 另须登记：摄影权、肖像主体、用途、期限、渠道、未成年人状态、撤回方式。

---

## R1-G4B — 平台 / 内容阻塞分类（Blocking Classification）

分类取值：`PLATFORM_BLOCKER` / `CONTENT_IMPORT_BLOCKER` / `CONTENT_PUBLICATION_BLOCKER` / `ACCEPTANCE_BLOCKER` / `NON_BLOCKING`

| 项 | 当前状态 | 阻塞分类 | 依据 |
| --- | --- | --- | --- |
| CA-01 史料 | CLIENT_CONFIRMATION_REQUIRED | CONTENT_IMPORT_BLOCKER | 人物/事件内容无法导入无证据链（I1） |
| CA-02 著作全文 | CLIENT_CONFIRMATION_REQUIRED | CONTENT_IMPORT_BLOCKER | 全文导入依赖版本与权利 |
| CA-03 版本资产 | CLIENT_CONFIRMATION_REQUIRED | CONTENT_IMPORT_BLOCKER | 逐件清单/权利未登记 |
| CA-04 篇章结构（128 篇） | CLIENT_CONFIRMATION_REQUIRED | CONTENT_IMPORT_BLOCKER | 结构化数据未交付 |
| CA-05 穴位/经络/病证/刺灸法 | CLIENT_CONFIRMATION_REQUIRED | CONTENT_IMPORT_BLOCKER | 数据未交付且存在医学边界 |
| CA-06 非遗项目资料 | CLIENT_CONFIRMATION_REQUIRED | CONTENT_PUBLICATION_BLOCKER | 未获正式认定证据与展示许可前不得公开 |
| CA-07 传承人资料 | CLIENT_CONFIRMATION_REQUIRED | CONTENT_PUBLICATION_BLOCKER | 个人信息/肖像未授权不得公开 |
| CA-08 示范中心资料 | CLIENT_CONFIRMATION_REQUIRED | NON_BLOCKING | 机构名已确认（CR-006）；运营内容不影响平台骨架 |
| CA-09 教学/科研成果 | CLIENT_CONFIRMATION_REQUIRED | NON_BLOCKING | 场景已确认；成果导入可后续补充 |
| CA-10 媒体版权 | RIGHTS_CONFIRMATION_REQUIRED | CONTENT_PUBLICATION_BLOCKER | UNKNOWN 不得发布 |

> 说明：缺失内容文件**不自动**为 PLATFORM_BLOCKER；平台骨架（双层架构、检索、阅读、谱系展示框架）可在内容准入前置的孤立验收面推进，但涉及公开的内容发布与内容导入在对应证据/授权补齐前不得验收为可公开状态。

## 交叉引用

- 资产缺口分析：`docs/audit/HFM-NPG-005-CONTENT-ASSET-GAP-ANALYSIS.md`
- 客户确认资产类别（CR-005）：`docs/governance/inputs/HFM-CLIENT-CONFIRMED-REQUIREMENTS-v1.md`
- 医学产品边界：`docs/governance/inputs/HFM-GEMINI-ORIGINAL-IMPLEMENTATION-PROPOSAL-v1.md`

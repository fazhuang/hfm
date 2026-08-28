# HFM NPG-5 — Customer Content Asset Inventory & Gap Analysis

Date: 2026-08-29
HFM baseline: `0167b1702dac13993a5206f63752eafcc8e5387e`
HFB reference snapshot: `03755b57ec0e4c8023d1447619f7d6ead9e44d73`

## 1. Evidence rules

- **CLIENT-CONFIRMED HAS** means the client states the asset family exists; it does not mean the files were delivered to this repository.
- **NOT FOUND** means no qualifying asset/evidence was found in the audited Git objects.
- **CLIENT CONFIRMATION REQUIRED** means the task does not supply the fact and it is not inferred from common knowledge or seed/display text.
- HFB static JSON, seed records, file paths, and narrative copy are leads only unless bound to SourceRef/Evidence and the actual asset.

Business domains:

- **A** 皇甫谧人物档案
- **B** 文献与思想体系
- **C** 《针灸甲乙经》数字知识库
- **D** 非遗传承体系

## 2. Asset and gap matrix

| ASSET-TYPE | Customer Has | Needed For | Required Metadata | Required Provenance | Required Evidence | Digitization Need | Normalization Need | Rights / Publication Risk | Current HFM Model Support | Gap | Next Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 《针灸甲乙经》版本实物/文件 | YES — CLIENT-CONFIRMED | B, C | 规范题名、责任者、版本/刻本、年代、卷册、馆藏/所有者、载体、文件清单、校勘/OCR状态 | 每件来源、取得方式、馆藏号/客户资产号、文件哈希 | 原件/扫描件 + 书目依据 + 授权 | CLIENT CONFIRMATION REQUIRED | Work→Edition→Version→Chapter→Passage；页码/卷篇定位 | High: 古籍影像可能公版，现代整理/校注本未必 | Strong canonical structure for Work/Edition/Version/Chapter/Passage/Source/Evidence/Citation | Exact count/status **NOT FOUND** in HFM. HFB has 87 metadata rows pointing to external files, not the files or rights proof | 客户提交逐件资产清单、样本文件、哈希、书目与权利依据 |
| 皇甫谧史料 | YES — CLIENT-CONFIRMED | A, B | 题名、作者、年代、版本、史料类型、涉及事件/主张 | 具体来源与页/卷/条定位；异说分别登记 | SourceRef→Evidence supporting each Assertion/Event | Scan/OCR/transcription status CLIENT CONFIRMATION REQUIRED | 人名、地名、纪年、事件、作品、异名 | Medium–High: 史料可引用不等于可公开全文 | Person/Event/Assertion/SourceRef/Evidence/Citation implemented | HFM has no content records. HFB exhibition narrative has five chronology entries but no field-level evidence chain; **NOT SUFFICIENT** | 客户提交史料目录与人物事件证据表；逐条标注来源定位 |
| 非遗证书 | YES — CLIENT-CONFIRMED | D | 证书名称、项目名称、级别、编号、颁发机构、日期、持证主体、有效状态 | 证书原件/核验渠道、客户提供记录 | 清晰扫描件 + 官方查询/文件 + 公开展示授权 | Scan/crop/redaction CLIENT CONFIRMATION REQUIRED | 机构/项目 canonical name；证书字段 | High: 证书图像、印章、个人信息、公开展示条件 | Source can hold basic identity/rights metadata; no governed media/publication model | Certificate file **NOT FOUND**; official heritage project name and level **CLIENT CONFIRMATION REQUIRED** | 客户提交证书扫描件、正式项目文件、公开展示许可和脱敏要求 |
| 传承人资料 | YES — CLIENT-CONFIRMED | D, A | 姓名、身份、称号/级别、师承关系、机构、时间、简介、联系方式分级 | 官方认定、师承证明、访谈/档案来源 | 每个人物与每条关系的证据；本人/权利人授权 | 照片/文本/音视频状态 CLIENT CONFIRMATION REQUIRED | Person/Institution/Event/relational Assertion；同名消歧 | Very high: 个人信息、肖像、履历和关系争议 | Person/Institution/Event/Assertion supports research facts; no consent/publication workflow | Names, count, genealogy and files **NOT FOUND**; completeness **CLIENT CONFIRMATION REQUIRED** | 客户提交传承人名单、关系表、证据和逐人发布授权 |
| 校园活动照片 | YES — CLIENT-CONFIRMED | A, D, 教学展示 | 文件名、活动名、时间、地点、主办方、摄影者、人物、说明、版本/裁切 | 原始文件、拍摄来源、活动记录 | 原图哈希、摄影授权、参与者肖像/隐私依据 | Original/derivative/web-size generation required | 人物、活动、日期、地点、caption、alt text | Very high: 著作权、肖像权、未成年人、隐私 | Source basic metadata only; no media binary/derivative/publication lifecycle | Photo files and authorizations **NOT FOUND** | 客户提交原图清单、授权范围、人物同意、未成年人规则和撤回联系人 |
| 人物生平事件结构化数据 | CLIENT CONFIRMATION REQUIRED | A | 事件类型、时间范围/精度、地点、参与者、事件说明、争议状态 | 每个事件至少一个可定位史料来源 | Event + historical Assertion + Evidence + Citation | 史料先数字化 | 纪年换算需保留原文与换算规则 | Medium: 错误叙述与“单一真相”风险 | Event temporal frame and evidence-backed Assertions implemented | HFB has five display chronology narratives but no canonical evidence chain; sufficient evidence **NOT FOUND** | 由客户史料建立事件证据清单；不从展示文案自动生成事实 |
| 皇甫谧作品全文 | CLIENT CONFIRMATION REQUIRED | B | 作品题名、存佚状态、版本、篇卷、全文载体、校勘状态 | 每份全文的版本/来源/馆藏/整理者 | 文件 + 页/篇定位 + 权利依据 | CLIENT CONFIRMATION REQUIRED | Work/Edition/Version/Chapter/Passage/variant | High for modern editions and transcriptions | Canonical text/version models implemented | HFM **NOT FOUND**; HFB JSON only lists external paths/metadata and narrative excerpts | 客户确认作品清单、哪些有全文、具体版本和权利状态 |
| 《针灸甲乙经》128 篇结构化数据 | CLIENT CONFIRMATION REQUIRED | C | 128 个篇目ID、卷次、篇名、顺序、所属版本、页码/起止位置 | 绑定一个明确 Edition/Version 和原始目录证据 | 128 records + reconciliation + source locators | 依版本状态 | 版本差异不得被压成单一目录 | High if copied from modern edition | Chapter/Passage model supports structure | Only “12卷128篇” appears in HFB seed/display prose; 128 records **NOT FOUND** | 客户提交目标版本目录；用 128/128 对账验收，保留版本差异 |
| 349 穴结构化数据 | CLIENT CONFIRMATION REQUIRED | C | 穴位ID、规范名/异名、归经、定位原文、主治原文、刺灸法原文、版本/篇/条定位 | 每个字段绑定原文 Passage/SourceRef | 349 entity records and field-level evidence, not a single summary claim | CLIENT CONFIRMATION REQUIRED | 名称、异体字、历史/现代术语分层 | Very high: treatment interpretation and clinical-use risk | EntityType `acupoint` + Assertion/Evidence can represent claims | Only “349穴” prose/seed claims found; 349 records **NOT FOUND** | 客户确认是否真实拥有数据、数据版本、字段与医学审校责任人 |
| 经络结构化数据 | CLIENT CONFIRMATION REQUIRED | C | 名称/异名、历史原文、关系、版本定位 | Passage/SourceRef per assertion | Dataset + evidence coverage report | CLIENT CONFIRMATION REQUIRED | 历史术语与现代标准分离 | High medical interpretation risk | No dedicated meridian entity type; generic Concept/Assertion possible but not frozen as a medical schema | Structured dataset **NOT FOUND** | 客户确认资产和目标语义；后续单独裁决模型，不自动扩 Core |
| 病证结构化数据 | CLIENT CONFIRMATION REQUIRED | C | 历史病证名、异名、原文描述、篇/条、时代/版本 | Passage/SourceRef per assertion | Dataset + expert review | CLIENT CONFIRMATION REQUIRED | 禁止直接映射成现代诊断而无依据 | Very high; may trigger clinical-product semantics | No dedicated disease/syndrome type by deliberate G1 boundary | Structured dataset **NOT FOUND** | 客户确认是否有数据；若有，仅按历史文献研究语义进入后续裁决 |
| 刺灸法结构化数据 | CLIENT CONFIRMATION REQUIRED | C | 方法名、原文、适用语境、禁忌原文、版本/篇/条 | Passage/SourceRef per assertion | Dataset + expert review + display boundary | CLIENT CONFIRMATION REQUIRED | 历史操作描述与现代教学/临床指导分离 | Very high; operational medical guidance risk | No dedicated technique model; generic concept/assertion only | Structured dataset **NOT FOUND** | 客户确认资产；当前不形成操作推荐或虚拟训练要求 |
| 非遗正式项目名称与级别 | CLIENT CONFIRMATION REQUIRED | D | 法定项目名称、类别、级别、批次、编号、认定时间、保护单位 | 政府/主管部门正式文件 | Certificate/official notice + verification URL if available | Documents should be scanned | 正式名与宣传名/机构名分离 | High reputational/legal risk | Institution/Source/Assertion can hold facts; publication workflow absent | Exact heritage item fact **NOT FOUND**; official organization name alone does not prove heritage project name/level | 客户提供正式认定材料；审校后再公开 |
| 传承谱系完整性 | CLIENT CONFIRMATION REQUIRED | D | 节点、关系、起止时间、依据、争议/缺失、公开状态 | 每条师承/传承关系的来源 | Coverage and unresolved-links report | Source documents may need digitization | 人名消歧、关系方向、代际、机构 | High: omission/错误关系 and personal dispute | Relational Assertion + Person/Event/Institution can represent evidence-backed relations | Complete genealogy **NOT FOUND** | 客户确认范围与完整性标准，列出未知/争议，不用常识补齐 |
| 传承人发布授权 | CLIENT CONFIRMATION REQUIRED | D | 授权人、素材、用途、渠道、期限、地域、撤回方式 | Signed consent/contract | Per-person authorization record | Scan and secure storage | Link authorization to exact asset versions | Very high privacy/likeness risk | Source authorization fields are too coarse for per-person/publication lifecycle | Authorization **NOT FOUND** | 客户提交逐人逐素材授权和撤回联系人 |
| 校园活动照片展示授权 | CLIENT CONFIRMATION REQUIRED | A, D | 摄影权、肖像主体、用途、期限、渠道、未成年人状态 | Contracts/consents/event notices | Per-photo rights record | Scan/derivative tracking | Bind rights to image hash | Very high | No media-rights lifecycle | Authorization **NOT FOUND** | 客户提交逐图授权或可证明的批量授权范围 |
| 非遗证书公开展示条件 | CLIENT CONFIRMATION REQUIRED | D | 可公开范围、遮盖字段、分辨率、水印、渠道、期限 | Holder/issuer authorization or applicable policy | Display approval record | Redacted public derivative may be needed | Original vs public derivative | High: seals, identifiers, personal information | Basic Source rights fields only | Public-display condition **NOT FOUND** | 客户确认是否可公开、是否脱敏/加水印、撤回机制 |

## 3. Required checks

| Check | Finding |
| --- | --- |
| 1. 人物事件是否已有足够史料证据 | **NOT FOUND** — HFB narrative chronology lacks field-level SourceRef/Evidence |
| 2. 皇甫谧作品全文是否实际齐备 | **CLIENT CONFIRMATION REQUIRED / NOT FOUND** |
| 3. 《针灸甲乙经》版本数量与数字化状态 | **CLIENT CONFIRMATION REQUIRED** — HFB has 87 metadata rows but no qualifying delivered-file inventory |
| 4. 128 篇结构化数据是否真实存在 | **NOT FOUND** — only prose claims |
| 5. 349 穴数据是否真实存在 | **NOT FOUND** — only prose/seed claims |
| 6. 经络/病证/刺灸法结构化数据是否存在 | **NOT FOUND** |
| 7. 非遗正式项目名称、级别是否有证据 | **NOT FOUND / CLIENT CONFIRMATION REQUIRED** |
| 8. 传承谱系是否完整 | **CLIENT CONFIRMATION REQUIRED** |
| 9. 传承人资料是否有发布授权 | **NOT FOUND** |
| 10. 校园活动照片是否有展示授权 | **NOT FOUND** |
| 11. 非遗证书是否具备公开展示条件 | **CLIENT CONFIRMATION REQUIRED / NOT FOUND** |
| 12. 客户必须补充哪些材料 | See §4 |

## 4. Client material request list

1. Master asset register with owner, contact, format, count, storage location, hash, digitization state, and intended use.
2. Exact 《针灸甲乙经》 version/file list, including which files are complete, OCRed, structured, collated, or only metadata.
3. 皇甫谧史料 catalogue plus page/volume locators for every proposed biography event and quotation.
4. 皇甫谧 works list with extant/lost/full-text status and rights for each chosen edition.
5. If claimed, actual 128-chapter and 349-acupoint datasets with record counts, schema, target version, and reconciliation evidence.
6. Any meridian, disease-pattern, and acupuncture-method datasets, with historical-source locators and expert review responsibility.
7. Official intangible-heritage certificate/notice establishing item name, level, number, holder/protection unit, and display conditions.
8. Inheritor register, genealogy relationships, supporting evidence, completeness statement, and per-person publication authorization.
9. Campus photo originals, captions, photographer copyright, portrait/underage consent, allowed channels, expiry, and withdrawal contact.
10. Certificate/photo public derivatives, redaction/watermark rules, and an authorized content approver for each institution.

## 5. Conclusion

The client has confirmed five asset families, but the audited repositories do not contain a publishable, provenance-complete delivery of those assets. HFM's canonical domain can represent much of the research evidence, versioning, events, and assertions, but it lacks media/publication workflows and intentionally does not freeze meridian/disease/technique clinical schemas. Content intake and evidence confirmation must precede scope commitments based on counts or immersive/clinical features.

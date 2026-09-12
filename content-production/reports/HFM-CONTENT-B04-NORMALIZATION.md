# HFM CONTENT-B04 — ACADEMIC NORMALIZATION REPORT

```text
BATCH=HFM-CONTENT-B04（NORMALIZATION & CONTENT OBJECT PRODUCTION）
CANONICAL_HEAD=2b372b3（未变）   HFM_PROD_WRITE=FORBIDDEN（未写入）
FOUNDATION=B01/B02/B03（corpus ledger/page-map/extracted-text/raw-ocr/OCR 样本）
```

## 1. 交付对象数量（真实计数）

```text
DOCUMENT_OBJECTS=675（667 PDF + 8 DOCX；DOC-<ASSET_ID> 稳定 ID）
PERSON_OBJECTS=17（PERSON-HFM-HUANGFUMI 主对象 + 16 相关/学人/传承人候选）
PERSON_FACTS=24（FACT_ID 稳定；均含 SOURCE_ASSET/LOCATION/QUOTE；CONFLICT 保留不裁决）
PERSON_EVENTS=14（时间线候选；模糊年代不作精确日期）
PERSON_RELATIONS=5
WORK_OBJECTS=14（含 WORK-JIAYI；古籍归属按 B01 规划文档候选、标 NEEDS_REVIEW/CONFLICT）
JIAYI_EDITIONS=92 资产行（版本类型经目录信号分类：FACSIMILE/MODERN/ANNOTATED/REPRINT/RESEARCH/UNKNOWN；
                    识别独立版本组≈7：医统正脉(1601)、五车楼(明万历)、行素草堂(清光绪)、四库全书(清)、
                    存存轩(清)、甲乙经全册、现代整理本系 —— 关系判定=UNKNOWN/待人工，未擅自并卷）
JIAYI_STRUCTURE_UNITS=0（无可靠机器卷/篇检测 → 如实置 0，未编造）
JIAYI_SOURCE_PAGE_LINKS=1,819（jiayi 资产在 corpus/page-map 的页级链接，含 ASSET/PAGE/SHA/文件）
EVIDENCE_OBJECTS=24（seed：全部源自 B01 后论/其言/其传带引文行）
PAPERS=473（Route A 学术论文资产；TITLE 文件名候选=provisional、作者/期刊=UNKNOWN 待核）
RESEARCH_TOPICS=5（语料关键词聚合，AUTO）
HERITAGE_OBJECTS=68（资产级候选；INHERITOR/ITEM/INSTITUTION/ACTIVITY 标注于说明）
HERITAGE_EVENTS=10（文件名年份事件候选）
KNOWLEDGE_OBJECT_CANDIDATES=26（腧穴/经络/病证/治法提及计数；DISCOVERY_ONLY）
CONFLICT_GROUPS=3（BIRTH_YEAR/PLACE_GULI/MEDIA_QINQIANG_YEAR；加 三都赋序 著者归属标注 CONFLICT）
```

## 2. 去重 / 实体解析 / 稳定 ID

```text
FILE != DOCUMENT != WORK != EDITION（严格分离）
SAME_DOCUMENT/SAME_WORK_DIFFERENT_FILE：文件夹级组（甲乙经全册1-4、医统正脉1-5、五车楼1-4、行素草堂卷册）列入 editions 资产行与
corpus/00-inventory/duplicate-groups.csv 互引；跨文件夹同题合并一律 UNCERTAIN_MATCH，不自动合并
canonical_name/aliases/source_forms 列保留繁体/异体/异称原始形态；未破坏原名
稳定 ID：PERSON-*/WORK-*/DOC-*/EVIDENCE-*/EDITION(资产引用 ASSET_ID)/PAPER-*/HERITAGE-*/HEVENT-*（不依赖行号）
ENTITY_RESOLUTION=PARTIAL（简繁/异称词典待扩充；已记录 source_forms）
```

## 3. 优先级与 PARTIAL/ENCRYPTED 收敛

```text
REVIEW_R0=4（皇甫谧核心事实证据 seed，先审）
REVIEW_R1=17（甲乙经版本/全册/结构 PARTIAL 文档，核心结构）
REVIEW_R2=0（A_TEXT 部分全部并入 R1/R3 口径；R2 元数据审随文档审）
REVIEW_R3=106（低优先扫描件 OCR 排队）
PARTIAL_CORE_BLOCKERS=17（大扫描版本/全册影像件全页 OCR 排队 → 阻塞“归一文本”，不阻塞整批生产）
UNIQUE_ENCRYPTED_ASSETS=384（队列行 384=唯一资产数，无重复队列记录）
ENCRYPTED_CORE_BLOCKERS=0（核心版本资产均无 encrypted 阻断；加密均权限型可提取/渲染）
RIGHTS/SOURCE：CUSTOMER_PROVIDED ≠ PUBLIC_DOMAIN；无逐件外部版权调查前置；明显风险信号（第三方/传播限制）→ RIGHTS_REVIEW
```

## 4. 产品问题答案

```text
PERSON_PROFILE_CONTENT_READY=PARTIAL（缺：核心事实/年谱的权威核校与卷页级第二来源；正式姓名别名规范审）
JIAYI_READER_CONTENT_READY=PARTIAL（缺：全册归一文本（17 核心扫描件 OCR/人工）、卷篇结构人工核对）
EVIDENCE_VIEW_CONTENT_READY=PARTIAL（缺：全量语料证据扩展（现 24 seed）+ 证据人工复核）
HERITAGE_CONTENT_READY=PARTIAL（缺：现场/材料核校；对象为文件级候选）
```

## 5. 边界

```text
STABLE_OBJECT_IDS=PASS（前缀稳定；行独立）
SOURCE_TRACEABILITY=PASS（对象→ASSET→页→SHA 可回溯，抽查见 QC）
RAW_ASSET_INTEGRITY=PASS（未改 hfmzl；B03 全量 667 SHA 复核 0 mismatch）
HFM_PROD_WRITTEN=NO
B04_PRODUCTION=PASS（对象层建成；正式内容仍非 import-ready）
approved-candidates/B04 候选包：由 CODE 后续将经 R0/R1 审核的对象（带稳定 ID+证据）复制为候选；本轮不生产 import package
```

报告见 `content-production/reports/HFM-CONTENT-B04-NORMALIZATION.md`；QC 见 `HFM-CONTENT-B04-QC.md`。

## R1 更正

```text
CSV_FILE_COUNT=18（B04 normalized 目录共 18 个 CSV；含 citations-candidates.csv）
```

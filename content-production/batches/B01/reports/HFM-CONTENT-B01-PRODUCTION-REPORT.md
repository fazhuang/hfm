# HFM CONTENT-B01 — GOLDEN SAMPLE PRODUCTION REPORT

```text
BATCH_TYPE=GOLDEN_SAMPLE
PURPOSE=VALIDATE_CONTENT_PRODUCTION_PIPELINE
CANONICAL_DATABASE=hfm_prod
HFM_PROD_WRITE=FORBIDDEN（本批未写入）
```

## 1. 范围与选择依据

依据 CONTENT-01 inventory（`content-production/00-inventory/customer-assets.csv`，689 文件，
含每文件 SHA256）选取 11 项：

| 类 | 资产 | 选择依据 |
| --- | --- | --- |
| A 皇甫谧核心 DOCX | HFM-A000003 其传 / HFM-A000004 其言 / HFM-A000005 后论 | 皇甫谧人物资料目录下三份核心文档（传记史料框架/存世文章框架/后世评价与作品设施汇总） |
| B 画像 | HFM-A000009 皇甫谧画像.jpeg | 高价值代表画像资产（目录唯一人像主图） |
| C 客户视频 | HFM-A000007 《针灸鼻祖皇甫谧》第1集 大器晚成.mpg；HFM-A000008 皇甫谧一.mpg | inventory VIDEO=2 的唯二视频资产 |
| D 甲乙经代表版本 | HFM-A000542–A000546 《针灸甲乙经》医统正脉全书（明万历29/1601 吴勉学）5 册 PDF（729 页） | 具明确版本信息（编者/年代/丛书本）与完整卷册结构的影印版本套；用于验证 影像页→OCR→结构→归一 链条 |

全部 11 项 SHA256 已与本机原文件重算比对一致（`BATCH-MANIFEST.csv`）。

## 2. 原始资料保护

```text
RAW_ROOT=hfmzl : READ_ONLY
MODIFY/RENAME/MOVE/DELETE/OVERWRITE_RAW = NONE（0 操作）
```

所有派生写入 `content-production/batches/B01/`。

## 3. 处理结果

### 3.1 人物（A：3 DOCX）

- 文本抽取（段落/表格保留索引）→ `person/extracted-text/`（3 文件）
- 候选事实表 → `person/person-facts.csv`（24 条；`CONFLICT_GROUP` 3 组）
- 年谱候选 → `person/person-timeline-candidates.csv`（14 条）
- 诚实说明：三份文档为**客户规划/资料框架文档**，非原始史料；所有“事实”为文档声称的
  候选事实（`SOURCE_TEXT/EXTRACTED_FACT` 分离），`REVIEW_STATUS` 默认
  `AUTO_EXTRACTED/NEEDS_REVIEW/CONFLICT`，未自动升级 `VERIFIED`，未 AI 补造原文没有的内容。

### 3.2 甲乙经（D：医统正脉全书 1601，5 册 729 页）

- 抽样 7 页（册1×5、册3×1、册5×1）完成 `SOURCE_PAGE → 300dpi PNG → RAW_OCR(chi_tra_vert)`：
  `jiayi/rendered-pages/`、`jiayi/raw-ocr/`、`jiayi/page-map.csv`
- `jiayi/structure.csv`：文件级（册/扫描页数）映射完成；**卷/篇标题未可靠检出**
  （影印木刻本在本地 tesseract 下辨识度过低，诚实判定，见 QC 报告）
- 四层分离约定已声明：`SOURCE_IMAGE / RAW_OCR / CORRECTED_TRANSCRIPTION(待做) /
  NORMALIZED_READING_TEXT(待做)`；本批未将任何“AI 润色”冒充原文。

### 3.3 画像（B）

- `images/image-assets.csv` + `images/derivatives/HFM-A000009_web.jpg`（1600px, q88）+
  `images/thumbs/HFM-A000009_thumb.jpg`（400px, q82）；原件未修改；
  RIGHTS_STATUS 保持 NEEDS_CUSTOMER_CONFIRMATION，派生图不因此获得公开发布资格。

### 3.4 视频（C）

- 技术探针：`video/probes/*-probe.json`
  - HFM-A000007：915.5s / mpeg / mpeg2video 720×576 / mp2 48k 2ch / 解码干净 / 场景切点 26 处
  - HFM-A000008：解码验证 ~109.8s（2746 帧 @25fps）；容器时长 N/A；解码报损伤
    （ac-tex damaged / MVs not available）
- 分段：`video/video-segments.csv`（35 段，含场景边界与 VAD 说话信号）
- 转写：`video/transcripts/TRANSCRIPT-STATUS.md` —— **本环境无中文 ASR 引擎**，
  TRANSCRIPTS_COMPLETE=NO（诚实记录，不伪造台词）
- 抽帧（`video/frames/`）已生成但**本会话模型不支持读图**，故所有画面内容字段保持
  NEEDS_REVIEW，未凭文件名臆测内容。

## 4. 来源/权利边界

```text
SOURCE_STATUS/RIGHTS_STATUS 未自动改变
B01 全部派生：SOURCE_STATUS=NEEDS_REVIEW 保持；RIGHTS_STATUS=NEEDS_CUSTOMER_CONFIRMATION 保持
RIGHTS_CLEAR=0（未根据加工完成自动清零）
```

## 5. Scale Decision（建议，供 Product Owner/Codex）

```text
PERSON_PIPELINE=PASS     （DOCX→文本→候选事实→时间线链条稳定；内容需人工/专家复核）
JIAYI_PIPELINE=ITERATE   （影印木刻本本地 OCR 不够稳定；需更强 OCR(PaddleOCR/高精度)或人工转录）
IMAGE_PIPELINE=PASS      （元数据+web/thumb 派生+哈希追踪链条稳定）
VIDEO_PIPELINE=ITERATE   （技术探针 PASS；转写与画面价值判断需 ASR+人工抽帧审看）

RECOMMENDED_BATCH_02=PERSON_P1 + JIAYI_TYPED_TEXT_BASELINE
ESTIMATED_ASSET_COUNT=约 60（P1 人物资料子集 + 少量有文本层的现代排版 PDF）
PROCESSING_METHOD=文本层抽取为主；木刻本转写采用人工/增强 OCR 双轨；视频增加 ASR 与抽帧审看
MANUAL_REVIEW_REQUIREMENT=人物事实/时间线全量人工复核；甲乙经卷目人工核对；视频转写人工校订
```

Batch 02 不自动启动。

## 6. 边界

```text
PRODUCT_SOURCE_CODE_CHANGED=NO
CANONICAL_PRODUCT_HEAD_UNCHANGED=YES（git HEAD 2b372b3 未动）
RAW_CUSTOMER_FILES_MODIFIED=NO
HFM_PROD_WRITTEN=NO
DATABASE_IMPORT/PRODUCTION_SEED/CUSTOMER_CONTENT_PUBLISH=NONE
```

内容生产工件未提交 Git（按仓库治理规则，等待内容批次治理决定与 Codex 验收）。

# HFM CONTENT-B01 — QC Report（OCR 抽样质量验证）

```text
BATCH=HFM-CONTENT-B01
SCOPE=《针灸甲乙经》医统正脉全书（明万历29/1601吴勉学）影像版 OCR 抽样
TOOL=tesseract（chi_tra_vert / psm 6 / 300dpi 灰度渲染）
```

## 1. 抽样清单（7 页，跨 3 册）

| 资产 | 册 | PDF页 | 类别（抽样意图） | OCR CJK 字符数 | 备注 |
| --- | --- | --- | --- | --- | --- |
| HFM-A000542 | 册1 | 1 | 书名/扉页类（短页） | 9 | 极低辨识 |
| HFM-A000542 | 册1 | 2 | 普通正文类（密集页） | 1216 | 有大量字符但噪声高 |
| HFM-A000542 | 册1 | 5 | 普通页 | 43 | 低辨识 |
| HFM-A000542 | 册1 | 8 | 普通页 | 125 | 低辨识 |
| HFM-A000542 | 册1 | 12 | 卷末/图版类（短页） | 7 | 极低辨识 |
| HFM-A000544 | 册3 | 15 | 跨册正文抽样 | 70 | 低辨识 |
| HFM-A000546 | 册5 | 20 | 跨册正文抽样 | 86 | 低辨识 |

`jiayi/page-map.csv` 为每页的 影像渲染↔RAW_OCR 一一映射（SOURCE_PAGE→OCR_TEXT 链成立）；
结构层级（卷/篇）未可靠检出（`jiayi/structure.csv`），全部 REVIEW_STATUS=NEEDS_REVIEW。

## 2. QC 观测（诚实记录，不以百分比虚构）

```text
OCR_SAMPLE_COUNT=7
CHARACTER_ERROR_OBSERVATIONS=高：密集页存在系统性误识与赘字（如高频错配字符"和/全/人/生"堆叠、
    数字与拉丁字母混入、竖排列序不稳定），推测源于木刻断笔+影印噪声+本地引擎局限
LAYOUT_ERRORS=存在：双栏/竖排换列边界不稳定（psm6 单块模式跨列串读；psm3 空输出）
PAGE_MAPPING_ERRORS=0（页级映射按 PDF 页码确定性完成）
UNREADABLE_REGIONS=多页接近不可读：页1/5/12 CJK 输出<50 字符（首字识别失败或图版页）
```

## 3. 结论

```text
OCR_PIPELINE_SUITABLE_FOR_SCALE=NO（当前本地 tesseract 对木刻影印本）
原因：RAW 层可产出，但 CORRECTED/NORMALIZED 层无法在不引入臆测的前提下自动建立；
四层（SOURCE_IMAGE/RAW_OCR/CORRECTED/NORMALIZED）不得混写——因此本批只落 RAW 层。
```

## 4. 推进建议（ITERATE 依据）

1. 木刻影印本：评估 PaddleOCR（中文古籍/竖排模型）或商业高精度 OCR，并用已核校底本做字准确率基准；
   短期可行替代=人工转写代表性页（封面/目录/卷一首）建立 CORRECTED/NORMALIZED 样例；
2. 结构检测：目录/卷首标题检测需在可靠文本之上进行（现 RAW 噪声不支持），建议 Batch 02 以
   有文本层的现代排版本先建立 卷/篇/章 结构基线，再回映影印本；
3. 页面影像：抽样渲染页已留存（rendered-pages/），可供人核 QC。

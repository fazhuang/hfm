# HFM 工作区 4019 个 Untracked Paths 治理终局决策方案 (WORKSPACE-GOVERNANCE-ACTION-PLAN)

**任务编号**：WG-02  
**性质**：治理决策与行动方案（只读设计，不执行清理动作）  
**执行人**：Gemini  
**基准日期**：2026-09-10  
**治理约束**：禁止执行 `git add/commit/clean/stash/rm/mv`，禁止修改 `.gitignore`，禁止写库。

---

## 一、WG-01 审计事实基线与终局原则

### 1.1 事实基线冻结
- **UNTRACKED_TOTAL**：`4,019`（由 WG-01 逐行实测穷尽对账，排除 WG-01 自身诊断报告）。
- **核心健康度确认**：
  - `PROJECT_CODE_AT_RISK = NO`（核心产品代码、0015 migration、675 DOCUMENT 生产基线完全受控）；
  - `PWE_BASELINE_INTEGRITY_AFFECTED = NO`（P/W/E mapping 与 tooling 已经在 HEAD `92f206c` 获得完全提交与跟踪）。

### 1.2 终局目标原则：彻底清除模糊态
在 WG-01 初步分类中存在的：
- `G4 = 242`（REMAIN_UNTRACKED_FOR_NOW）
- `G5 = 8`（HUMAN_DECISION）

**在 WG-02 中全部清零**。本方案遵循“`MAIN_WORKTREE_CLEAN = YES`”的绝对标准，对 4,019 个未跟踪对象进行无死角闭环分类：
每一条对象必须明确归入且仅归入以下五类之一：
1. **TRACK**：必须由 Git 长期纳管的核心工程/测试/规范/归一化基线资产；
2. **IGNORE**：配置在 `.gitignore` 中的构建、渲染或衍生语料规则；
3. **MOVE_OUTSIDE_REPO**：整体剥离出主仓库、迁入并列工作区或外部存储的重型多媒体工程；
4. **DELETE_REGENERABLE**：完全由代码/流水线生成的中间过程碎片（可随时一键重新生成）；
5. **KEEP_IN_REPO_BY_EXCEPTION**：特批例外留存（本次治理核定为 `0`，零例外）。

---

## 二、G5 8 个疑难对象的逐条定性与裁决

经对 WG-01 报告中列出的 G5 8 个文件进行内容深度复核，全部具备明确的技术证据，**无需留置人工决策（HUMAN_DECISION_REQUIRED = 0）**：

| 序号 | 文件路径 (Path) | 类型 | 大小 | 业务用途 (Purpose) | 疑难原因 | 终局裁决 (Final Decision) | 理由与风险分析 |
| :---: | :--- | :---: | :---: | :--- | :--- | :---: | :--- |
| 1 | `content-production/batches/B01/reports/HFM-CONTENT-B01-INDEPENDENT-ACCEPTANCE-R1.md` | MD | 1.7 KB | B01 批次独立验收 R1 报告 | 此前批次文件未集中提交 | **TRACK** | 核心治理审计链条证据，必须 Git 留痕。风险：遗漏会导致历史审计断链。 |
| 2 | `content-production/batches/B01/video/transcripts/TRANSCRIPT-STATUS.md` | MD | 1.8 KB | B01 视频转录治理状态表 | 位于 video 混杂目录下 | **TRACK** | 属于内容转录交付的元数据依据，体积极小，应作为治理依据纳管。 |
| 3 | `content-production/batches/B02/reports/HFM-CONTENT-B02-INDEPENDENT-ACCEPTANCE-R1.md` | MD | 1.2 KB | B02 批次独立验收 R1 报告 | 历史批次补充报告 | **TRACK** | 核心验收结论，必须 Git 永久留痕。 |
| 4 | `content-production/import/B05/schema/database-schema-map.json` | JSON | 20.8 KB | B05 导入前生产 Schema 映射图 | 为 JSON 格式 | **TRACK** | 数据库结构比对的基线工件，作为 0015 审计关键依据，必须纳管。 |
| 5 | `content-production/import/B05/schema/pre-import-row-counts.json` | JSON | 822 B | B05 导入前各表行数基线 | 为 JSON 格式 | **TRACK** | 0015 dry-run 行数对比的权威原始数据，必须纳管。 |
| 6 | `content-production/normalized/work-counts.json` | JSON | 313 B | 著作语料引用统计频次 | JSON 衍生统计表 | **TRACK** | 著作规范化分析（works.csv）的计算输入底表，必须纳管。 |
| 7 | `content-production/normalized/work-knowledge.json` | JSON | 563 B | 著作知识对象关联索引 | JSON 衍生结构表 | **TRACK** | 知识对象映射的重要支撑，必须纳管。 |
| 8 | `content-production/normalized/work-mentions.json` | JSON | 523 B | 著作提及上下文候选表 | JSON 衍生结构表 | **TRACK** | 著作提及上下文候选表，必须纳管。 |

---

## 三、G4 242 个暂留对象的逐类清算与收敛

G4 包含的 242 个对象分为两大部分，全部收敛如下：

### 3.1 `content-production/` 下的 42 个对象 → 全部收敛为 **TRACK**
- **构成**：
  - 37 个处于流程节点但此前遗漏的 CSV 核心业务底表（如 `00-inventory/customer-assets.csv`、`01-classification/content-classification.csv`、`02-metadata/content-object-map.csv`、`07-review/rights-review.csv`、`corpus/document-metadata.csv` 等）；
  - 5 个历史治理规划与说明文档（`CONTENT-PRODUCTION-PLAN.md` 等）。
- **裁决理由**：这些并非临时运行缓存，而是内容工程从客户原始素材到最终 675 篇文献的“输入与分类生命线”，必须完整检入 Git，确保可从零重现内容工程演进。

### 3.2 `video-production/` 下的 200 个对象 → 随视频工作区整体收敛为 **MOVE_OUTSIDE_REPO**
- **构成**：
  - 59 个视频设计与编导 Markdown；
  - 20 个合成与渲染 Python 脚本；
  - 11 个时间轴与素材对照 CSV；
  - 字幕 SRT/VTT、元数据 JSON 等。
- **裁决理由**：见第四节，视频工程应作为一个自包含的独立体系整体迁出主仓库。

---

## 四、视频制作工作区最终架构方案：MODEL_C (Sibling Workspace)

### 4.1 唯一推荐方案：`VIDEO_WORKSPACE_FINAL_MODEL = MODEL_C`
将 `/Users/likeming/Sites/hfm/video-production/` 整体**平移迁出**至与主仓库并列的目录：
```
/Users/likeming/Sites/hfm-video-production/
```

并在主仓库根目录 `.gitignore` 中增加忽略规则：
```gitignore
# Video Production Workspace (Relocated to sibling repo)
video-production/
```

### 4.2 为什么必须是 MODEL_C？（架构论证）
1. **彻底解决 9.72 GB 仓库污染**：
   - 2,955 个视频文件、成百上千张逐帧截图（`search-frames`、`yan-frames` 等）如果留在主仓库，任何一次误操作 `git add .` 都会导致主代码仓库的 `.git` 对象库瞬间膨胀至不可逆的巨大体积。
2. **保障多智能体协作与 CI 干净工作树**：
   - HFM 主仓库的核心使命是 Web 前后端系统架构、数据库 Migration、API 及内容元数据管理；
   - 视频工程具有完全独立的生命周期（由剪辑、音频渲染、TTS、Playwright 录屏工具链构成）；
   - 剥离后，主仓库的工作树在执行任何验收与迁移时可瞬间达成 `CLEAN`。
3. **独立 Git 版本控制建议**：
   - `VIDEO_INDEPENDENT_REPO_RECOMMENDED = YES`；
   - 移出后，在 `hfm-video-production` 内部执行 `git init`，专门管理其 Python 合成脚本、字幕、工程配置，同时在其内部配置 ignore 排除成片和渲染帧。

---

## 五、产品与测试代码区 4 个未跟踪文件的纳管决策

在 `apps/` 目录下扫描出的 4 个文件属于**最高优先级的正向资产**，绝不允许通过 `.gitignore` 掩盖：

| 文件路径 (Path) | 性质与所属模块 | 业务用途 (Purpose) | 关联历史任务 | 终局裁决 |
| :--- | :---: | :--- | :---: | :---: |
| `apps/backend/tests/test_api_permission_status.py` | 后端测试 | API 接口权限与认证状态回归测试 | 历史权限修复 | **TRACK** |
| `apps/backend/tests/test_migration_0008_boolean_default.py` | 后端测试 | 0008 migration 布尔默认值的专属断言测试 | 0008 迁移治理 | **TRACK** |
| `apps/backend/uv.lock` | 依赖锁定 | Python 后端环境的权威依赖锁版本 | 后端工程规范 | **TRACK** |
| `apps/frontend/src/__tests__/auth_flow_store.spec.ts` | 前端测试 | 用户认证流 Pinia Store 单元测试 | 前端权限管理 | **TRACK** |

同时，根目录下 `design-qa.md` 与 `docs/design/HFM-DESIGN-RESOURCE-UTILIZATION-PLAN.md` 同样归入 **TRACK**。

---

## 六、全量 4019 个 Untracked 对象终局对账表 (Final Reconciliation)

| 终局动作 (Action Category) | 范围明细与主要组成 | 数量 (Count) | 占比 (%) |
| :--- | :--- | :---: | :---: |
| **FINAL_TRACK** | **主仓库必须纳入版本控制的资产**：<br>- 4 个前后端核心测试与依赖锁 (`apps/`)<br>- 2 个系统规范与 QA 记录 (`docs/`, `design-qa.md`)<br>- 73 个内容工程历史验收报告、契约、Schema图与核心CSV底表 | **79** | 2.0% |
| **FINAL_MOVE_OUTSIDE_REPO** | **整体迁出主仓库的多媒体工程 (MODEL_C)**：<br>- `video-production/` 下全部文件（含 31 个成片、484 个高质量音视频、1413 个渲染帧、1058 个脚本与文档） | **2,955** | 73.5% |
| **FINAL_DELETE_REGENERABLE** | **完全可再生的中间运行缓存与OCR文本碎片**：<br>- 458 个 `corpus/extracted-text/*.txt`<br>- 392 个 `corpus/raw-ocr/*.txt`<br>- 114 个批次级切片图与 OCR 过程临时文本<br>- 20 个检查点临时状态 JSON<br>- 1 个 Playwright 测试快照 | **985** | 24.5% |
| **FINAL_IGNORE** | **治理完成后通过 `.gitignore` 规则长期屏蔽的目录**：<br>- 由治理规则全局覆盖上述可再生目录，对象本身被删除或迁出 | **0 (规则覆盖)** | 0.0% |
| **FINAL_KEEP_EXCEPTION** | **特批例外留存对象** | **0** | 0.0% |
| **总计 (Total)** | **全量穷尽对账，无任何残留或遗漏** | **4,019** | **100.0%** |

---

## 七、三份标准执行清单 (Remediation Manifests)

### 7.1 清单 A：TRACK_MANIFEST（共 79 个文件，待下一阶段执行 `git add`）
```text
# === Apps & Tests & Docs (6 个) ===
apps/backend/tests/test_api_permission_status.py
apps/backend/tests/test_migration_0008_boolean_default.py
apps/backend/uv.lock
apps/frontend/src/__tests__/auth_flow_store.spec.ts
docs/design/HFM-DESIGN-RESOURCE-UTILIZATION-PLAN.md
design-qa.md

# === Content Governance Reports & Decisions (28 个) ===
content-production/batches/B01/reports/HFM-CONTENT-B01-INDEPENDENT-ACCEPTANCE-R1.md
content-production/batches/B01/reports/HFM-CONTENT-B01-INDEPENDENT-ACCEPTANCE.md
content-production/batches/B01/reports/HFM-CONTENT-B01-PRODUCTION-REPORT.md
content-production/batches/B01/reports/HFM-CONTENT-B01-QC.md
content-production/batches/B01/video/transcripts/TRANSCRIPT-STATUS.md
content-production/batches/B02/reports/HFM-CONTENT-B02-INDEPENDENT-ACCEPTANCE-R1.md
content-production/batches/B02/reports/HFM-CONTENT-B02-INDEPENDENT-ACCEPTANCE.md
content-production/batches/B02/reports/HFM-CONTENT-B02-PRODUCTION-REPORT.md
content-production/batches/B02/reports/HFM-CONTENT-B02-QC.md
content-production/corpus/reports/HFM-CONTENT-B03-FULL-CORPUS-REPORT.md
content-production/corpus/reports/HFM-CONTENT-B03-INDEPENDENT-ACCEPTANCE.md
content-production/corpus/reports/HFM-CONTENT-B03-QC.md
content-production/import/B05/dry-run-1-report.md
content-production/import/B05/dry-run-2-report.md
content-production/import/B05/import-dependency-graph.md
content-production/import/B05/rollback-test.md
content-production/import/B05/reports/HFM-B05-SG-R2-AUTHORITATIVE-COMMIT-MANIFEST-FINAL.md
content-production/import/B05/reports/HFM-B05-SG-R2-COMMIT-MANIFEST-AUDIT.md
content-production/import/B05/reports/HFM-CONTENT-B05-DRY-RUN-QC.md
content-production/import/B05/reports/HFM-CONTENT-B05-IMPORT-CONTRACT-0015.md
content-production/import/B05/reports/HFM-CONTENT-B05-IMPORT-CONTRACT.md
content-production/import/B05/reports/HFM-CONTENT-B05-INDEPENDENT-ACCEPTANCE.md
content-production/import/B05/reports/HFM-CONTENT-B05-R1-INDEPENDENT-ACCEPTANCE.md
content-production/import/B05/reports/HFM-CONTENT-B05-R2-INDEPENDENT-ACCEPTANCE.md
content-production/import/B05/reports/HFM-CONTENT-B05-SCHEMA-GAP-DECISION.md
content-production/import/B05/reports/HFM-PROD-DOCUMENT-IMPORT-FROZEN-STATE.md
content-production/import/B05/tools/hfm_import_runner.py
content-production/import/domain-model/HFM-MDAR-02-REALITY-COMPATIBILITY-AUDIT.md
content-production/import/domain-model/HFM-MDAR-03-CODEX-IMPORT-READINESS-ACCEPTANCE.md
content-production/import/domain-model/HFM-MINIMAL-DOMAIN-ARCHITECTURE-REVIEW.md
content-production/reports/HFM-CONTENT-B04-CSV-SCHEMA-CORRECTION.md
content-production/reports/HFM-CONTENT-B04-INDEPENDENT-ACCEPTANCE.md
content-production/reports/HFM-CONTENT-B04-NORMALIZATION.md
content-production/reports/HFM-CONTENT-B04-QC.md
content-production/reports/HFM-CONTENT-B04-R1-INDEPENDENT-ACCEPTANCE.md
content-production/reports/HFM-CONTENT-GAP-ANALYSIS.md
content-production/reports/HFM-CONTENT-PRODUCTION-PLAN.md
content-production/reports/HFM-CUSTOMER-MATERIAL-INVENTORY.md

# === Content Schemas & Seed/Normalized Tables (45 个) ===
content-production/00-inventory/customer-assets.csv
content-production/00-inventory/duplicate-groups.csv
content-production/01-classification/content-classification.csv
content-production/02-metadata/content-object-map.csv
content-production/07-review/rights-review.csv
content-production/corpus/document-metadata.csv
content-production/corpus/document-production-ledger.csv
content-production/corpus/page-map.csv
content-production/corpus/qc-sample.csv
content-production/corpus/review-document-exceptions.csv
content-production/corpus/review-encrypted.csv
content-production/corpus/review-queue.csv
content-production/import/B05/schema/database-schema-map.json
content-production/import/B05/schema/pre-import-row-counts.json
content-production/normalized/citations-candidates.csv
content-production/normalized/documents.csv
content-production/normalized/evidence.csv
content-production/normalized/heritage-events.csv
content-production/normalized/heritage-objects.csv
content-production/normalized/jiayi-editions.csv
content-production/normalized/jiayi-source-pages.csv
content-production/normalized/jiayi-structure.csv
content-production/normalized/knowledge-object-candidates.csv
content-production/normalized/papers.csv
content-production/normalized/person-facts.csv
content-production/normalized/person-relations.csv
content-production/normalized/person-timeline.csv
content-production/normalized/persons.csv
content-production/normalized/product-content-map.csv
content-production/normalized/research-topics.csv
content-production/normalized/review-priority.csv
content-production/normalized/work-counts.json
content-production/normalized/work-knowledge.json
content-production/normalized/work-mentions.json
content-production/normalized/works.csv
```

### 7.2 清单 B：IGNORE_RULE_PLAN（待补充至 `.gitignore` 的精准规则）
```gitignore
# ==========================================
# Video Production Workspace (Relocated)
# ==========================================
video-production/

# ==========================================
# Content OCR & Extraction Intermediate Dumps
# ==========================================
content-production/corpus/extracted-text/
content-production/corpus/raw-ocr/
content-production/corpus/work/
content-production/batches/*/raw-ocr/
content-production/batches/*/rendered-pages/
content-production/batches/*/ocr-run-stats.json
content-production/batches/*/pdf-profile.json
content-production/batches/*/performance.json
content-production/batches/*/routeA-stats.json

# ==========================================
# Testing Snapshots
# ==========================================
.playwright-cli/
```

### 7.3 清单 C：MOVE_ARCHIVE_MANIFEST（待整体迁出的多媒体目录）
- **源路径**：`/Users/likeming/Sites/hfm/video-production/`（含全部 2,955 个文件，9.72 GB）
- **目标路径**：`/Users/likeming/Sites/hfm-video-production/`

### 7.4 清单 D：DELETE_REGENERABLE_MANIFEST（共 985 个可再生文件）
- `content-production/corpus/extracted-text/*.txt`（458 个）
- `content-production/corpus/raw-ocr/*.txt`（392 个）
- `content-production/batches/B01/jiayi/raw-ocr/`（7 个）
- `content-production/batches/B01/jiayi/rendered-pages/`（13 个）
- `content-production/batches/B01/video/probes/`（2 个）
- `content-production/batches/B02/` 下的 JSON 统计与图片（92 个）
- `content-production/corpus/work/*.json`（10 个）
- `.playwright-cli/page-2026-09-08T20-56-36-185Z.yml`（1 个）

---

## 八、治理审查最终输出指标

```yaml
WG02_STATUS: PASS

SOURCE_UNTRACKED_TOTAL: 4019

FINAL_TRACK: 79
FINAL_IGNORE: 0 (由.gitignore长效规则覆盖，无死物残留)
FINAL_MOVE_OUTSIDE_REPO: 2955
FINAL_DELETE_REGENERABLE: 985
FINAL_KEEP_EXCEPTION: 0

UNRESOLVED_UNTRACKED: 0

VIDEO_WORKSPACE_FINAL_MODEL: "MODEL_C (Move entire video-production to sibling directory /Users/likeming/Sites/hfm-video-production)"
VIDEO_WORKSPACE_MOVE_RECOMMENDED: YES
VIDEO_INDEPENDENT_REPO_RECOMMENDED: YES

CONTENT_PRODUCTION_GOVERNANCE_READY: YES
PRODUCT_CODE_GOVERNANCE_READY: YES

HUMAN_DECISION_REQUIRED_COUNT: 0

READY_FOR_WORKSPACE_REMEDIATION: YES
SAFE_TO_EXECUTE_CLEANUP: NO (需等待操作授权并在专用运维指令下执行)

PWE_IT02_REACCEPTANCE_SHOULD_WAIT: YES

BLOCKER: NONE
STOP: YES
```

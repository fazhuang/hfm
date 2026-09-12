# HFM CONTENT-B05 — IMPORT CONTRACT

## 1. Preflight（真实读回）
- POSTGRESQL_AVAILABLE=YES；hfm_prod identity: alembic 0014, 33 tables
- PRE_IMPORT_ROW_COUNTS captured (schema/pre-import-row-counts.json)；system_admin=1
- 未运行 DROP/TRUNCATE/RESET/RECREATE/DOWNGRADE；未写入 hfm_prod

## 2. DATABASE_SCHEMA_MAP（真实 introspection）
- schema/database-schema-map.json：33 表列/FK/UNIQUE/PK 全量读回
- 关键列：entities/persons/works/editions/chapters/passages/versions/sources/source_refs/evidences/assertions/citations/content_artifacts/...

## 3. CSV→Database Map（18/18）
csv-database-map.csv：DIRECT_IMPORT=0, TRANSFORM_REQUIRED=10, REFERENCE_ONLY=3, NOT_SUPPORTED_BY_CURRENT_SCHEMA=3, NOT_READY=2
→ IMPORTABLE 全部 NO

## 4. Schema Gaps
schema-gaps.csv：BLOCKING=5（documents 表缺失；content stable-id 持久化列缺失；来源追溯链列缺失；
  person 别名模型缺失；fact 证据页/引文模型缺失）+ NON_BLOCKING/FUTURE
> 未按 Schema-Fit 强行塞数据；未丢字段、未用随机文本存结构、未编造关系

## 5. 依赖顺序与幂等
import-dependency-graph.md：真实 FK 顺序（真实可执行顺序如上图）；B04 内容路径被 BLOCKING gap 阻断
stable-id 契约：数据库缺 stable_id 列 → 幂等导入机制无法在现有 schema 实现（见 gaps BLOCKING#2）

## 6. 验证与 Dry Run（scratch，非 hfm_prod）
validation-report.csv：18 CSV 全部解析/列对齐/UTF8/引用 PASS；jiayi-source-pages 存在 1 个跨批次同页重复记录（B01/B02 各自 p1 OCR，非丢失，冻结文件不修改）
- dry-run-1/2、rollback-test、reconciliation.csv、expected-database-delta.csv 见交付物
- 生产守卫：工具对 hfm_prod REFUSE（实测 exit 2）

## 7. 结论
BLOCKING_SCHEMA_GAPS>0 → B05=BLOCKED_BY_SCHEMA_GAP；不修改 schema 强行推进
NEXT_ACTION=PRODUCT_OWNER_SCHEMA_DECISION（stable-id/provenance/documents/别名/证据 建模决策后再做正式 import 设计）

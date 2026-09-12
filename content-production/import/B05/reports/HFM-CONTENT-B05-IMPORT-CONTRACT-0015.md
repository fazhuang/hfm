# HFM CONTENT-B05 — IMPORT CONTRACT 0015 (current-state reconciliation R1)

CONTRACT_ID: HFM-CONTENT-B05-IMPORT-CONTRACT-0015
GENERATED_AT: 2026-09-10 (B05-CONTRACT-RECONCILIATION-R1, re-executed on current HEAD)
SUPERSEDES_CONTRACT: HFM-CONTENT-B05-IMPORT-CONTRACT.md（历史 PRE_SG_R2 证据，保留不改）

CONTRACT_BASELINE: cdf23081b51578798de724f0e79a54349e42ded2
IMPLEMENTATION_COMMIT: bf303fe3056657b52c52a9174f7ea27cc5bf1bb5
GOVERNANCE_COMMIT: cdf23081b51578798de724f0e79a54349e42ded2
MIGRATION_HEAD: 0015

## 1. Current-state binding (measured, not copied)

- HEAD=cdf23081b51578798de724f0e79a54349e42ded2（A→B 线性闭包后）
- Alembic single head 0015 (revision 0015, down_revision 0014)；0015 新增仅 `documents` + `person_aliases` 两表及
  persons/works/editions/evidences 的 `stable_id` 唯一列；无任何重复 provenance 表
- hfm_prod 只读复核：alembic=0015；tables=35；system_admin=1；documents=0；person_aliases=0
- Scratch（本机新 sqlite，经提交的 alembic 0001→0015 迁移）：表集=35（34+alembic_version），与 hfm_prod 一致

## 2. SG01–SG05 逐项证据链（当前实现/mapping/tooling/dry-run 重新形成）

| SG | 判定 | 证据 |
| --- | --- | --- |
| SG01 Document entity | RESOLVED | `documents` 表存在（migration 0015 + ORM ContentDocument）；mapping target=documents 列一一对应（csv-database-map.csv DIRECT_IMPORT）；import path=package/documents.csv→documents 直插（本轮 dry-run 实测）；稳定来源链=每行 source_asset_id（675/675 有值）+ source_pages + sha256 |
| SG02 Stable ID persistence | RESOLVED | documents.stable_id 唯一索引 uq_documents_stable_id；persons/works/editions/evidences 均加 stable_id 唯一列（0015）；ORM unique=True；单元测试 test_content_document_stable_id_unique 证实 IntegrityError 持久化约束；非仅 CSV |
| SG03 Source traceability | RESOLVED | 复用既有 Source→SourceRef→Evidence→Citation 链，未新增重复 provenance schema（0015 仅新增 documents/person_aliases，实测表集证明）；evidence 需 source_ref_id 或 source_passage_id 锚点（DB CHECK）；import contract 可经 source_asset_id/source_pages → page identity → source/source_ref |
| SG04 Person aliases | RESOLVED | `person_aliases` 表存在（0015）+ ORM PersonAlias（alias/alias_type/source_asset_id/source_location，唯一约束 uq_person_aliases_person_alias_type）；mapping persons.csv 标注别名去向 person_aliases（SG-04）；import 路径=TRANSFORM 阶段 |
| SG05 Evidence page/citation | RESOLVED | SourceRef.locator 承载页身份；(ASSET_ID,PAGE)=页键（jiayi-source-pages REFERENCE_ONLY）；Evidence 经 source_ref_id/source_passage_id 锚定；Citation 链复用；无新表承载 page（SG-05 由映射承担，identity-policy 定义 canonical 选择） |

## 3. SOURCE_INPUTS / TARGET_OBJECTS / RULES（当前数据实测）

SOURCE_INPUTS: content-production/import/B05/package/documents.csv（= normalized/documents.csv 副本，676 行含表头）
TARGET_OBJECTS: documents（本阶段 dry-run 范围；persons/works/editions 为 transform 后续阶段，schema 已就绪）
STABLE_ID_RULES: DOCUMENT_ID=DOC-* 作为 documents.stable_id；唯一约束；重复则跳过（幂等）
SOURCE_TRACEABILITY_RULES: 每行保留 SOURCE_ASSET_ID / SOURCE_PAGES / SHA256 → source_asset 溯源
PAGE_IDENTITY_RULES: 键=(ASSET_ID,PAGE_NUMBER)；canonical 优先级 corpus canonical > B03 > B02 > B01；
   非 canonical 记录保留为 alternate provenance，不重复导入
DUPLICATE_POLICY: (ASSET,PAGE) 同键 → 1 canonical + N alternate；禁止重复对象
IDEMPOTENCY_POLICY: 按 stable_id 幂等 upsert-skip；RUN2 须 0 新增 0 更新
ROLLBACK_POLICY: 单事务导入；中途约束失败整体回滚，禁止部分态

## 4. Mapping evidence（本轮重新计算，基于当前数据）

IMPORTABLE_DOCUMENTS=675（0 重复 stable_id；0 缺真实 title）
IMPORTABLE_PERSONS=17（normalized/persons.csv，schema 就绪，transform/review 后续）
IMPORTABLE_WORKS=14（normalized/works.csv）
IMPORTABLE_EDITIONS=92（normalized/jiayi-editions.csv）
PAGE_ROWS=1819（normalized/jiayi-source-pages.csv 数据行）
UNIQUE_PAGE_KEYS=1818（(ASSET,PAGE) 去重键数）
DUPLICATE_PAGE_KEYS=1（A000542 p1 跨批次 B01/B02；policy 前）
DUPLICATES_AFTER_POLICY=0（canonical=B02，alternate=B01；与既有 identity-policy-check.csv 一致）
BLOCKING_SCHEMA_GAPS=0
BLOCKING_MAPPING_GAPS=0

## 5. Scratch Dry-run（本机 scratch sqlite，经提交 alembic 0001→0015；禁止使用 hfm_prod）

- RUN1（全新库）：RUN1_INSERTS=675，RUN1_UPDATES=0，POST_COUNT=675 → RUN1_IMPORT_SUCCESS=YES
- RUN2（同包重跑）：RUN2_NEW_INSERTS=0，RUN2_UNEXPECTED_UPDATES=0，POST_COUNT=675 → IDEMPOTENCY=PASS
- ROLLBACK：注入 mid-transaction 唯一约束失败 → 事务回滚，行数 675→675，部分行=0 → ROLLBACK=PASS
- UNEXPLAINED_DELTA=0；SOURCE_TRACEABILITY=PASS（675/675 携带 source_asset_id）
- 工具：content-production/import/B05/tools/hfm_import_dryrun_0015.py（evidence tooling，产品代码零改动）

## 6. PRODUCTION_DATABASE_DELTA

HFM_PROD_ALEMBIC_VERSION=0015；HFM_PROD_DOCUMENTS=0；HFM_PROD_PERSON_ALIASES=0
HFM_PROD_CUSTOMER_CONTENT_DELTA=0（本轮及此前均未向 hfm_prod 导入任何客户内容）

## 7. Gate

SG01=RESOLVED SG02=RESOLVED SG03=RESOLVED SG04=RESOLVED SG05=RESOLVED
BLOCKING_SCHEMA_GAPS=0 BLOCKING_MAPPING_GAPS=0
SCRATCH_DRY_RUN=PASS IDEMPOTENCY=PASS ROLLBACK=PASS SOURCE_TRACEABILITY=PASS
HFM_PROD_CUSTOMER_CONTENT_DELTA=0

B05_IMPORT_CONTRACT_STATUS=READY_FOR_ACCEPTANCE

PRODUCT_SOURCE_MODIFIED=NO（本轮未改 apps/backend、apps/frontend、migration、register、verifier）
HFM_PROD_WRITE=NO

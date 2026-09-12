# HFM CONTENT-B05 — IMPORT DEPENDENCY GRAPH（真实 FK 顺序）

## 真实数据库 FK 顺序（hfm_prod@0014 读回）

- entities(entity_type) → persons / works(entity_id) / events / heritage_projects / c_domain_terms
- works → editions → versions / chapters → passages(version_id)
- sources → source_refs → evidences(source_ref_id/source_passage_id)
- evidences ↔ assertions(assertion_evidences); citations(target_assertion_id/evidence_id)
- content_artifacts(source_id,subject_entity_id,version_id) → publication_records
- research_projects(owner) → research_notes

## B04 内容导入所需顺序（映射后）

DOC/SOURCE → sources → source_refs → evidences/assertions；entities → persons/works → editions → versions/chapters → passages
（documents 对象缺表；stable-id/标题双轨/别名/冲突/溯源持久化缺列）

## 结论

依赖 stable-id 持久化、溯源链、标题/作者双轨、别名、冲突组的路径均被 BLOCKING SCHEMA_GAP 阻断；
不存在可在不损失溯源前提下、仅用现有 33 表完成的 B04 内容导入路径 → 真实 INSERT 顺序暂不可执行，
先交 PRODUCT_OWNER_SCHEMA_DECISION。

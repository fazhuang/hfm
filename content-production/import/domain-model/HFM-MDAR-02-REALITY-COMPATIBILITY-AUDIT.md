# HFM MDAR-02 — REALITY COMPATIBILITY AUDIT

GENERATED_AT: 2026-09-10 (MINIMAL_DOMAIN_ARCHITECTURE_REVIEW stage 2; read-only audit)
BASELINE_HEAD: 5c7253dfd088c64fc991e951f04d196cb3ae1d74 (hfm-canonical)
MIGRATION_HEAD: 0015 (hfm_prod, single head)
Hfm_prod row state (read-only): entities=0 persons=0 works=0 editions=0 documents=675

Scope: pure reality check — no code/migration/CSV change; no DB write; no import. Answers "what still separates
PERSON/WORK/EDITION import from safe, per ARCH_DECISION_01–03 (Gemini minimal model)".

Evidence sources (all read-only): hfm_prod information_schema + FK introspection; committed alembic 0002/0003/0015;
content-production/normalized/{persons,works,jiayi-editions,papers}.csv; import/B05/package/documents.csv;
02-metadata/content-object-map.csv; MDAR-01 review doc.

## 1. entities 底座（真实 schema 事实）

| 对象 | 依赖 | 实测 |
| --- | --- | --- |
| entities | — | id PK, entity_type NOT NULL, name NOT NULL (0002); no stable_id column; hfm_prod entities=0 |
| persons | entities 强依赖 | persons.entity_id PK, FK -> entities.id **RESTRICT**, NOT NULL (0002); persons.stable_id unique (0015) |
| works | entities 弱依赖 | works.entity_id FK -> entities.id nullable; works.author_entity_id FK -> entities.id **nullable** SET NULL; works.stable_id unique (0015) |
| editions | entities **无** 依赖；强依赖 works | 无 entity_id 列；editions.work_id FK -> works.id NOT NULL (CASCADE); stable_id unique (0015); 无 document/asset 桥接列 |
| documents | — | 0015；无 edition_id / work_id 列（仅纯文本 edition 字符串） |

```
PERSON_ENTITY_DEPENDENCY=YES        （person 入库必须先建 entities row；否则 FK RESTRICT 阻断）
WORK_ENTITY_DEPENDENCY=OPTIONAL     （FK 允许空 entity_id/author_entity_id；领域锚定推荐建 work entity）
EDITION_ENTITY_DEPENDENCY=NO        （editions 不经 entities；只经 works.work_id NOT NULL）
ENTITY_BOOTSTRAP_SUPPORT=NONE       （唯一 importer hfm_import_documents.py 只写 documents；产品/工具无任何创建 entities 的代码路径）
ENTITY_BOOTSTRAP_GAP=REQUIRED       （persons=阻塞级；works=领域建议级；当前 entities=0 无引导手段）
```

## 2. editions.work_id（92 条数据现实）

```
EDITION_ROWS=92
EDITION_WITH_WORK_ID=0              （jiayi-editions.csv 表头 [EDITION_ID,ASSET_ID,TITLE,EDITION_TYPE,PAGES,
                                     RELATION_BASIS,RELATION_NOTE,REVIEW_STATUS] —— 无 WORK_ID 列；RELATION_BASIS 全空，
                                     RELATION_NOTE 全 "UNKNOWN"）
EDITION_WITHOUT_WORK_ID=92
EDITION_WORK_AUTO_RESOLVABLE=87     （仅凭标题关键字可唯一判属：WORK-JIAYI 82、WORK-DIWANG-SHIJI 4、WORK-GAOSHIZHUAN 1）
EDITION_WORK_AMBIGUOUS=1            （EDITION-HFM-A000541《针灸甲乙经、伤寒论、金匮要略、温病学》精译.pdf：多书合刊，
                                     单 work_id NOT NULL 无法承载，需合刊/丛书建模或人工裁定）
EDITION_WORK_UNRESOLVABLE=4         （EDITION-HFM-A000529~A000532：ASSET_ID 纯数字 10023266/67/68/23609.pdf，
                                     标题即文件名，无任何著录证据 → 需人工裁定归属）
```

相关细节：9 条不属标题明确《甲乙经》：4《帝王世纪》+1《高士传》+1 多书合刊 +4 数字代号；MDAR-01 同口径一致。

## 3. WORK ↔ EDITION 只读映射表（标题/文件名证据，非显式 ID）

| WORK_STABLE_ID | WORK_TITLE | MATCHED_EDITION_COUNT | MATCH_METHOD | CONFIDENCE | AMBIGUITY |
| --- | --- | --- | --- | --- | --- |
| WORK-JIAYI | 针灸甲乙经 | 82 | NORMALIZED_TITLE（标题含“甲乙（经）”） | HIGH | 0 |
| WORK-DIWANG-SHIJI | 帝王世纪 | 4 | NORMALIZED_TITLE | HIGH | 0 |
| WORK-GAOSHIZHUAN | 高士传 | 1 | NORMALIZED_TITLE | HIGH | 0 |
| （未决） | 多书合刊 1 | 1 | FILENAME 含多书名 | — | AMBIGUOUS（需裁定主 work 或丛书建模） |
| （未决） | 数字代号 PDF 4 | 4 | FILENAME（纯数字） | UNKNOWN | UNRESOLVABLE（人工） |
| 其余 11 个 WORK（列女/逸士/玄守/释劝/笃终/三都赋序/玄晏春秋/医统正脉丛书/皇甫谧研究集成/遗著集/皇甫谧针灸） | 0 | — | — | — | jiayi-editions 中无对应记录；现代书/论文的“版本/文档”需另建 |

## 4. PERSON : WORK（17 人，文本角色证据，无身份级外键）

persons.csv 无 WORK_ID/ENTITY 外键；works.csv 无 PERSON_ID 列。全部 person→work 关系只存在于
ROLE / AUTHOR_ORIGINAL 的规范化中文文本 → 机器可列名但不可直接 join（需 NORMALIZED_NAME / MANUAL_INFERENCE）。

```
PERSON_WORK_RELATIONS_FOUND=YES（仅文本层）
EXPLICIT_RELATIONS=（角色字符串点名作品）：皇甫谧-撰 JIAYI/DIWANG/GAOSHI/LIENV/YISHI（AUTHOR，部分“待权威核/学术争议”）；
  钱超尘+温长路-共主编 HUANGFUMI-YANJIU-JICHENG（EDITOR，2人→1作，单 author_entity_id 无法表达）；
  史星海-主编 YIZHU-JI（EDITOR）；李志锋-作者/非遗传承 皇甫谧针灸（AUTHOR/OTHER）；
  黄龙祥-作者 黄帝针灸甲乙经新校本（EDITOR/ANNOTATOR，对象偏向 EDITION 级）；
  李鼎+高树中-共著 甲乙经理论与实践（AUTHOR，多人）；王君-新校版作者（ANNOTATOR/EDITOR）；
  吴勉学-辑刊 医统正脉全书（COMPILER/PRINTER，丛书）
INFERRED_RELATIONS=需按名归一后才能成对（目前 0 条已机器确认成对）
AMBIGUOUS_RELATIONS=多主编/多作者（集成、理论与实践）、甲乙经著者学术争议（皇甫谧/王焘?待核）、三都赋序著者争议
UNKNOWN_ROLE_RELATIONS=评价者（司马炎/李巨来/钱熙祚/张法荣等）、亲属(姑母之子)/太守（梁柳）、非遗文件名（刘君奇）——
  这些“人”当前不与 14 WORK 形成 AUTHOR/EDITOR 语义关系
```

角色词表实测覆盖：AUTHOR、EDITOR、COMPILER/PRINTER、ANNOTATOR(校订/校注)；PROOFREADER 未见明确记录；其余归 OTHER/UNKNOWN。
无“把 UNKNOWN 硬写成 AUTHOR”的情况。

## 5. DOCUMENT 关系现实（675 已入库，零改动）

```
DOCUMENT_WITH_CLEAR_EDITION_RELATION=92   （documents.source_asset_id ∈ jiayi-editions ASSET_ID，1:1；仅资产层相等，
                                            数据库无 edition 桥接列）
DOCUMENT_WITH_CLEAR_WORK_RELATION=0        （无任何 machine 级 work 绑定；content-object-map PRIMARY_CATEGORY
                                            “04 针灸甲乙经”612 asset 仅主题归类，非对象 FK）
DOCUMENT_WITHOUT_REQUIRED_DOMAIN_RELATION=583（473 论文 papers.csv + 3 PLANNING_DOC + 其余现代专论；ARCH_DECISION_02
                                            允许其独立存在，不强制 work_id）
DOCUMENT_RELATION_AMBIGUOUS=0              （资产级映射无歧义；work 主题归类非身份级）
DIRECT_DOCUMENT_WORK_FK_REQUIRED=NO         （583 论文不强制；未来 R1 用关系表/可空列均可）
DIRECT_DOCUMENT_EDITION_FK_REQUIRED=NO      （92 本古籍需“挂靠机制”，关系表 R1 优先；R0 导入 P/W/E 不需要）
RELATION_TABLE_PREFERRED=YES                （doc 可对多对象多关系 N:M + 类型；直接 FK 仅适合单一强主链）
```

附：documents.csv DOCUMENT_TYPE 仅 PDF=672 / PLANNING_DOC=3 —— 领域种类(论文/版本/古籍影印)不存于 documents 表，
现实分类在 side 元数据（papers.csv=473、content-object-map）。此为“文档领域归类未持久化”的事实，非缺陷判定。

## 6. Forward Migration 最小范围（仅提案，禁止实施）

| 变更 | 级别 | 依据 |
| --- | --- | --- |
| entities bootstrap（导入前为 17 PERSON + 14 WORK 建 entity rows；entity_type/name/name_zh） | R0_REQUIRED | persons FK RESTRICT 硬阻断；works 领域锚定 |
| editions→work 数据补齐（87 标题可判 + 4 数字代号人工 + 1 合刊裁定 → 填 work_id） | R0_REQUIRED（数据+人工决策） | editions.work_id NOT NULL 硬约束 |
| EDITION 导入工具（products/import tooling；当前仅有 documents importer） | R0_REQUIRED | 无 edition/person/work importer 存在 |
| PERSON 导入工具（entities→persons→person_aliases 链路） | R0_REQUIRED | 同上；别名已由 0015 支持 |
| WORK 导入工具（entities→works；author 先留空或仅主笔，不折叠角色） | R0_REQUIRED | ARCH_DECISION_03 |
| person_work_role 关系表（AUTHOR/EDITOR/COMPILER/ANNOTATOR/PROOFREADER/OTHER） | R1_OPTIONAL | 多主编/多作者/角色不可压缩入 author_entity_id |
| works.author_entity_id 语义收紧或降级为“principal author”注释 | R1_OPTIONAL | 现为 1:1 单作者，域模型 N:M |
| document↔edition / document↔work 关系表 | R1_OPTIONAL | 92 挂靠 + 583 研究挂载 |
| canonical edition ↔ 物理分册聚合（卷册层次） | R2_FUTURE | ARCH_DECISION_01 冻结；92 保持 1:1 现状 |
| 丛书/合刊 WORK↔WORK、EDITION.lineage 源流 | R2_FUTURE | |
| documents.edition_id / work_id 直接列（NOT NULL 化） | NOT_NEEDED（R1 关系表更佳） | 675 冻结行不受影响；可空列亦可延后 |
| 放宽 editions.work_id 为 NULL | NOT_NEEDED（保持完整性，补数据而非放空） | |

---

## Verdict

DOCUMENT_BASELINE_PROTECTED=YES        （675 行/stable_id 未动；审计全程只读）
DOCUMENT_IDENTITY_CONFLICT=NO

ENTITY_BOOTSTRAP_READY=NO              （无任何 entities 创建路径；entities=0）
PERSON_DATA_COMPATIBILITY=PARTIAL      （ID 唯一/别名列就绪；阻断=entities bootstrap；角色仅文本需建模）
WORK_DATA_COMPATIBILITY=PARTIAL        （ID 唯一/WORK_TYPE 就绪；阻断=单作者列 vs 多角色、author 文本解析/争议）
EDITION_DATA_COMPATIBILITY=FAIL        （92/92 无 work_id；NOT NULL 约束直接拒绝 as-is 导入）
DOCUMENT_RELATION_COMPATIBILITY=PASS   （92 资产级 1:1 清楚；583 可独立——符合 ARCH_DECISION_02）

EDITION_WORK_MAPPING_COMPLETE=NO       （87 标题可判 + 1 合刊歧义 + 4 数字代号人工；无显式 ID）
PERSON_WORK_ROLE_MODEL_SUFFICIENT=NO   （现仅 works.author_entity_id 单作者；N:M 多角色需 R1 关系表）

R0_SCHEMA_CHANGES_REQUIRED=NONE        （0015 已具备 stable_id/别名/可空 author；P/W/E 导入本身无需新表/新列；
                                        R0 缺口是数据/工具/人工决策，非 schema）
R0_DATA_CHANGES_REQUIRED=YES           （entities bootstrap 31 行；editions.work_id 92 值；author 角色文本先保留不折叠）
R0_HUMAN_DECISIONS_REQUIRED=YES        （4 数字代号 edition 归属；1 合刊处理；皇甫谧著者争议标注；现代编纂书 WORK_TYPE 校核）

FORWARD_MIGRATION_MINIMUM_SCOPE=entities bootstrap + editions.work_id 数据补齐 + P/W/E import tooling + (R1) person_work_role / doc 关系表
PERSON_IMPORT_TECHNICALLY_READY=NO
WORK_IMPORT_TECHNICALLY_READY=NO
EDITION_IMPORT_TECHNICALLY_READY=NO

RECOMMENDED_NEXT_GATE=CODEX_IMPORT_READINESS_ACCEPTANCE（P/W/E 前向迁移设计与授权）
BLOCKER=EDITION_WORK_ID_DATA_GAP（92/92 缺失）+ PERSON_ENTITY_BOOTSTRAP_GAP + NO_PWE_IMPORT_TOOLING
STOP=YES

（本报告仅审计；未实施任何修复/迁移/导入/写入。）

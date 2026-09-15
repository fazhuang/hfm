# 事实底稿 · 研究平台宪章 v0.2

**用途**：列出宪章 v0.2 依赖的**每一条事实断言**，附可复制的复现命令与实测值。

**审计方必须独立复现。**任一条复现结果与"实测值"不符，即为审计发现。

**标记约定**（沿用项目既有惯例）：

| 标记 | 含义 |
| :--- | :--- |
| `[实测]` | 由命令直接取得，可复现 |
| `[复核]` | 他人取得、本人独立复核过 |
| `[未验证]` | 无证据，**不得当作事实使用** |

**基线**：`main` @ `fefb9ee` · 数据库 `hfm_prod` · 采集日期 2026-09-15

---

## E-01 段落编号方案已存在且完整

**断言**：HFM 已有格式为 `CH-JIAYI-V01-P01-D001` 的段落编号，覆盖 12 卷 / 149 章 / 1007 段，全部有值。宪章 §3 的地基即建立在此。

```bash
psql -d hfm_prod -tAc "select count(*) from passages"
psql -d hfm_prod -tAc "select id from passages order by id limit 3"
psql -d hfm_prod -tAc "select split_part(id,'-',3) vol, count(*) from passages group by 1 order by 1"
```

**实测值**：`1007` · `CH-JIAYI-V01-P01-D001 / -D002 / -D003` · V01–V12 共 12 组，各组计数 124/112/297/84/90/69/53/35/54/30/30/29 `[实测]`

> **审计注意**：宪章 §3 断言"编号已存在，只需暴露"。请检验该编号的**唯一性、连续性与永久性**（见 `AUDIT-BRIEF.md` Q1）。送审方**未验证**缺号 / 重号 / 跨卷冲突。

---

## E-02 章节结构与卷篇对应

**断言**：12 卷为顶层章节，共 149 章。

```bash
psql -d hfm_prod -tAc "select count(*) from chapters"
psql -d hfm_prod -tAc "select count(*) from chapters where parent_id is null"
psql -d hfm_prod -tAc "select id, title, parent_id from chapters order by id limit 8"
```

**实测值**：`149` · 顶层 `12` · `CH-JIAYI-V01 = 卷之一`，其子节点 `CH-JIAYI-V01-P01 = 精神五臟論第一` `[实测]`

---

## E-03 引文与原文断开

**断言**：`citations` 表 23 条，`passage_id` 全部为空。这是宪章 §3.1 与 §4 L3 的直接依据。

```bash
psql -d hfm_prod -tAc "select count(*) total, count(passage_id) linked from citations"
psql -d hfm_prod -tAc "select column_name from information_schema.columns where table_name='citations' order by ordinal_position"
```

**实测值**：`23 | 0`（total | linked）· 列含 `passage_id` `[实测]`

---

## E-04 版本层为空

**断言**：`passages.version_id` 1007 行全部为 NULL；`versions` 表 0 行。即版本层无数据基础。这是宪章 §3.3 与缺口 G-3 的依据。

```bash
psql -d hfm_prod -tAc "select count(*) filter (where version_id is null) null_vid, count(*) from passages"
psql -d hfm_prod -tAc "select count(*) from versions"
psql -d hfm_prod -tAc "select count(*) from editions"
```

**实测值**：`1007 | 1007` · `0` · `91`（editions 有 91，versions 为 0）`[实测]`

---

## E-05 Elasticsearch 可用且版本支持 kNN

**断言**：Elasticsearch 8.17.0 已在运行。宪章 §6.7「不新增 pgvector」的选型结论依赖此事实。

```bash
curl -s -m 3 http://localhost:9200/ | python3 -c "import sys,json;print(json.load(sys.stdin)['version']['number'])"
psql -d hfm_prod -tAc "select name, installed_version from pg_available_extensions where name like '%vector%'"
```

**实测值**：`8.17.0` · pgvector 查询返回空（**未安装**）`[实测]`

> **审计注意**：ES 8 是否**实际启用了** `dense_vector` 与 kNN，送审方**未验证**（只验证了版本号）。见 `AUDIT-BRIEF.md` Q3。

---

## E-06 冻结架构边界 AB-16

**断言**：项目冻结边界将 AI 列为 `FORBIDDEN_COUPLING`，不得给 Phase 1 core 增加依赖。

```bash
grep -n "AB-16" docs/governance/HFM-PHASE1-ARCHITECTURE-BOUNDARY-v1.md
```

**实测值**：`HFM-PHASE1-ARCHITECTURE-BOUNDARY-v1.md:38` — *"Display, HFB UI reuse, AI, 3D, VR, XR, and virtual training may not add dependencies to the Phase 1 core."* `[实测]`

---

## E-07 机器守卫的实际扫描范围

**断言**：守卫对禁用 import 的扫描**只覆盖 `src/hfm/phase2/`**，窄于治理规则 AB-16。宪章 §6.1 据此指出"绕过机器守卫不等于合规"。

```bash
grep -n "_FORBIDDEN_IMPORT_RE = \|AI_STATE = " apps/backend/src/hfm/phase2/guardrails.py
grep -n "phase2_root = \|scan_forbidden_markers(phase2_root" apps/backend/src/hfm/phase2/guardrails.py
```

**实测值**：正则定义于 `guardrails.py:40`，`AI_STATE = "DEFERRED"` 于 `:22`；扫描根 `phase2_root = src_root / "hfm" / "phase2"` 于 `:203`，调用点 `:209` `[实测]`

---

## E-08 资料分界 96 / 585

**断言**：681 件媒体资产按裁决分为 96 件公众门户 / 585 件研究平台。

```bash
# 门户侧
psql -d hfm_prod -tAc "select count(*) from media_assets where object_key like '针灸甲乙经/论著/%' and object_key ~ '四库全书本清乾隆|五车楼藏板|行素草堂藏板|医统正脉全书'"
psql -d hfm_prod -tAc "select count(*) from media_assets where object_key like '非遗佐证/%'"
psql -d hfm_prod -tAc "select count(*) from media_assets where object_key like '皇甫谧%'"
psql -d hfm_prod -tAc "select count(*) from media_assets where object_key like '针灸甲乙经/%' and object_key not like '针灸甲乙经/论文/%' and object_key not like '针灸甲乙经/论著/%'"
# 研究平台侧
psql -d hfm_prod -tAc "select count(*) from media_assets where object_key like '针灸甲乙经/论文/%'"
psql -d hfm_prod -tAc "select count(*) from media_assets where object_key like '针灸甲乙经/论著/%' and object_key !~ '四库全书本清乾隆|五车楼藏板|行素草堂藏板|医统正脉全书'"
# 总数
psql -d hfm_prod -tAc "select count(*) from media_assets"
```

**实测值**：公版原刻影印 `22` · 非遗佐证 `67` · 皇甫谧 `6` · 版本脉络图 `1` → 门户 `96`；论文 `515` · 现代出版物 `70` → 研究平台 `585`；总计 `681` `[实测]`

> **审计注意**：分界目前在数据模型上**无法强制**（`media_assets` 无访问范围字段），这是宪章 §7 的模型变更依据。`[实测]`
> **另注**：皇甫谧 6 件中 2 件为电影、4 件为文档与画像；宪章 §5 的门户清单合计 96 件，与此一致。

---

## E-09 研究平台前端规模

**断言**：研究平台前端仅 3 个视图、760 行。

```bash
ls apps/frontend/src/views/research/
wc -l apps/frontend/src/views/research/*.vue
```

**实测值**：`ResearchEntityView.vue` / `ResearchHomeView.vue` / `ResearchSearchView.vue`，合计 `760` 行 `[实测]`

---

## E-10 研究平台数据几乎全空

**断言**：研究相关的表在生产库中基本为 0 行。

```bash
psql -d hfm_prod -tAc "select 'projects',count(*) from research_projects union all select 'notes',count(*) from research_notes union all select 'annotations',count(*) from research_annotations"
psql -d hfm_prod -tAc "select column_name from information_schema.columns where table_name='research_annotations' order by ordinal_position"
```

**实测值**：projects `0` · notes `0` · annotations `0`；`research_annotations` 列含 `owner_id · passage_id · project_id · quote_text · start_offset · end_offset · note` `[实测]`

---

## E-11 `assertions` 表已具备冲突表达所需字段

**断言**：宪章 §9 决定 O-8 复用 `assertions`，依据是该表已有 `confidence` / `editorial_status` / `revision`。

```bash
psql -d hfm_prod -tAc "select column_name from information_schema.columns where table_name='assertions' order by ordinal_position"
psql -d hfm_prod -tAc "select count(*) from assertions"
```

**实测值**：`id · subject_entity_id · predicate · value · object_entity_id · assertion_type · confidence · editorial_status · created_by · revision · created_at · updated_at`；现存 `23` 条 `[实测]`

> **审计注意**：字段存在 **不等于** 该模型足以表达多源冲突。见 `AUDIT-BRIEF.md` Q7。

---

## E-12 文献元数据缺失

**断言**：675 条 `documents` 的 year / author / publication 全部为 `UNKNOWN`。这是缺口 G-4 的依据。

```bash
psql -d hfm_prod -tAc "select count(*) filter (where year::text='UNKNOWN'), count(*) from documents"
psql -d hfm_prod -tAc "select stable_id, title, author_original, publication, year from documents limit 3"
```

**实测值**：`675 | 675`；样本 `DOC-HFM-A000003 | 其传 | UNKNOWN | UNKNOWN | UNKNOWN` `[实测]`

---

## E-13 全文未复核

**断言**：675 条 `documents` 全部处于 `NEEDS_REVIEW`。这是缺口 G-6 的依据。

```bash
psql -d hfm_prod -tAc "select review_status, count(*) from documents group by 1"
```

**实测值**：`NEEDS_REVIEW | 675` `[实测]`

---

## E-14 知识底座规模

**断言**：宪章中引用的知识底座计数。

```bash
psql -d hfm_prod -tAc "select 'persons',count(*) from persons union all select 'works',count(*) from works union all select 'c_domain_terms',count(*) from c_domain_terms union all select 'c_domain_relations',count(*) from c_domain_relations union all select 'heritage_projects',count(*) from heritage_projects union all select 'heritage_relations',count(*) from heritage_relations union all select 'editions',count(*) from editions union all select 'chapters',count(*) from chapters union all select 'passages',count(*) from passages"
```

**实测值**：persons `17` · works `14` · c_domain_terms `30` · c_domain_relations `5` · heritage_projects `56` · heritage_relations `2` · editions `91` · chapters `149` · passages `1007` `[实测]`

> **审计注意**：`c_domain_relations` 仅 5 条、`heritage_relations` 仅 2 条 —— 宪章缺口 G-5「实体关联近乎空白」依据此。 `[实测]`

---

## E-15 技术栈版本

**断言**：宪章 §8 已知约束表中的技术栈现状。

```bash
psql -d hfm_prod -tAc "show server_version"
curl -s -m 3 http://localhost:9200/ | python3 -c "import sys,json;print(json.load(sys.stdin)['version']['number'])"
node -v
apps/backend/.venv/bin/python -V
```

**实测值**：PostgreSQL `16.14 (Homebrew)` · Elasticsearch `8.17.0` · Node `v26.7.0` · Python `3.13.13` `[实测]`

---

## E-16 研究内容与公开内容的访问隔离现状

**断言**：研究端点未登录返回 403。

```bash
for p in /api/v1/research/projects /api/v1/research/notes /api/v1/admin/audit-log; do
  printf "%-36s " "$p"; curl -s -o /dev/null -w "%{http_code}\n" -m 5 "http://127.0.0.1:8000$p"
done
```

**实测值**：三者均 `403` `[实测]`

> **审计注意**：403 只验证了**存在鉴权**，未验证是否存在**信息泄漏**（如通过错误信息、时序差异推断资源存在性）。见 `AUDIT-BRIEF.md` Q6。

---

## 复现环境要求

| 项 | 要求 |
| :--- | :--- |
| 仓库 | `github.com/fazhuang/hfm` @ `fefb9ee` |
| 数据库 | 本地 PostgreSQL，库名 `hfm_prod`，alembic `0017` |
| 服务 | 后端 `127.0.0.1:8000`、Elasticsearch `localhost:9200` |
| 无需 | 前端 dev server（E-08/E-14 等纯数据库断言不需要） |

**未复现即采信，是本次审计最需要避免的错误。**

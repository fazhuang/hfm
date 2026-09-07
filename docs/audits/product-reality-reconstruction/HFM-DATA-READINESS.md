# HFM-DATA-READINESS.md — 数据库就绪度与内容可用性事实审计

## 1. 五个层级的定义与事实裁决

| 级别 | 定义 | 当前状态 | 判定与证据 |
|---|---|---|---|
| **SCHEMA_EXISTS** | ORM 模型与数据库建表脚本存在 | **YES** | 28 个 ORM 模型与 14 个 Alembic 迁移脚本完整具备 |
| **MIGRATION_READY** | 能够从空库干净执行至最新 HEAD | **YES** | `alembic upgrade head` 通过测试套件 `test_migrations.py` 实测通过 |
| **BOOTSTRAP_EXISTS** | 具备生产必须的管理员与系统基线初始化程序 | **YES** | `scripts/initialize-production.py` 经 51 项测试验证，安全建立 SYSTEM_ADMIN |
| **RECOVERY_SEED_EXISTS** | 具备本地恢复最小数据集的注入脚本 | **YES** | `apps/backend/scripts/bootstrap_recovery.py` 存在（可注入皇甫谧基础实体） |
| **PRODUCTION_CONTENT_EXISTS** | 生产级全量学术典籍、论文全文与高精媒体数据 | **NO / PARTIAL** | 数据库中尚无导入全量 515 篇论文和《甲乙经》全部经文。生产内容主要依赖前端静态数据包 (`apps/frontend/src/data/`) |

---

## 2. 各业务表真实内容来源分析

| 数据表名 | 是否包含必需产品数据 | 数据来源机制 | 现状描述 |
|---|---|---|---|
| `roles` | 是 | `initialize-production.py` / `ensure_roles_seeded` | 冻结五角色，随初始化自动注入 |
| `users` | 是 | `initialize-production.py` / `/api/v1/auth` | 初始化建立 SYSTEM_ADMIN，其余动态创建 |
| `entities` | 部分 | `bootstrap_recovery.py` / 业务写入 | 仅具备基线种子皇甫谧，全量实体尚未由 ETL 批量入库 |
| `persons` | 部分 | 同上 | 包含皇甫谧核心纪年，其他历史人物待录入 |
| `works`, `editions` | 部分 | 前端静态常量驱动优先 | 生产主要依赖 `workCollection.ts` 与 `jiayiView.ts` |
| `chapters`, `passages` | 仅测试/样本文档 | 前端 `readerDocuments.ts` 承载 | 读者功能目前依赖前端本地解析的后论、其传文本 |
| `c_domain_terms` | 部分 | 前端静态搜索索引承载 | 穴位与经络以 `searchIndex.ts` 检索为主 |
| `heritage_projects` | 部分 | 前端 `heritageView.ts` 承载 | 刘君奇第六代名医等非遗档案在前端完整呈现 |
| `media_assets` | 样板/基线 | 运行时上传 / `apps/frontend/public/assets` | 静态图片放在前端 public 目录，数据库媒体记录需手动导入 |
| `research_projects` | 用户生成 | 研究人员登录后写入 | 初始为空，由研究员动态创建 |
| `content_artifacts` | 用户生成 | 研究人员提交流程 | 初始为空 |
| `publication_records`| 用户生成 | 管理员审核通过后产生 | 初始为空 |

---

## 3. 结论

当前 HFM 处于 **“架构与模式 100% 具备，生产运行依赖前端静态知识集，数据库具备完整 Schema 待内容批量导入”** 的状态。
即：系统可以立刻打包部署上线，公众用户能够浏览完整的学术内容（因为前端内置了高保真的离线 Projection），但 PostgreSQL 数据库本身并非处于海量内容预填充状态。

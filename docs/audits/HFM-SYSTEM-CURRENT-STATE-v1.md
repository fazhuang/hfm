# HFM 系统当前状态说明书 v1

**本文件性质**:系统现状的**单一权威描述**。回答「这套系统现在到底是什么样」以及「它有哪些已知风险与缺口」。

**取代**:`docs/audits/product-reality-reconstruction/`(22 份)与 `docs/audits/product-scope-resolution/`(8 份)
—— 那批文档冻结于 **2026-09-08**、产出于 `recovery/hfm-foundation` 分支 `1e9336e`。它们不是错的,
是**旧的**,且在两个方向上失真(见 §9 失效声明登记册)。本文件不修改它们,只取代其效力。

---

## 0. 审计基线与方法

```text
AUDIT_DATE    : 2026-09-14
BRANCH        : hfm-canonical
HEAD          : df6ed1b
WORKTREE      : CLEAN (0 改动)
PRODUCTION_DB : hfm_prod @ alembic 0017
```

**方法**:以**实际运行的系统、生产数据库、git 历史**为准。不采信文档自述。
每条事实标注验证方式:`[实测]` = 本人执行命令取得;`[复核]` = 他人取得、本人独立复核过关键结论;
`[未验证]` = 无证据,不得当作事实使用。

**维护规则**(本文件存在的意义就是对抗文档漂移):
1. 任何改变系统状态的提交,**必须在同一提交内**更新本文件受影响的小节与登记册。
2. 每条风险/缺口有稳定编号(`R-xx` / `G-xx` / `C-xx`),关闭时改为 `CLOSED (commit, 日期)`,**不删除**。
3. 新增风险必须在「证据」列给出可复现的命令或文件:行号。
4. 本文件**不得**出现无法复现的「已验证」。

---

## 1. 系统身份与交付形态

| 项 | 现状 |
| :--- | :--- |
| 系统 | 皇甫谧人文数字平台(HFM)—— 数字人文学术门户 + 研究后台 |
| **交付形态** | **本地可运行**。**未做公网部署** `[实测]` |
| 交付范围 | 见 `HFM-CUSTOMER-DELIVERY/03-DELIVERED-SCOPE.md`:公共门户 A1–A8、研究工作台 B1–B7 |
| **明确排除** | 后台内容与媒体运营工具(上传、审核界面);公网域名/证书/生产服务器 |

`infra/` 下 nginx 与 systemd **全部为 `.example`,零实例化**;无域名、无证书。P5(公网部署)未开始。 `[实测]`

---

## 2. 运行现状(实测)

本地三件套在跑:

```text
:8000  uvicorn hfm.main:app   启动于 2026-09-14 02:36 —— 早于本轮全部改动
:5173  vite dev server
hfm_prod  PostgreSQL @ alembic 0017
```

**公开接口实测**(经 `:5173` 代理与直连 `:8000` 双向确认):

| 端点 | HTTP | total |
| :--- | :--- | ---: |
| `/api/v1/public/works` | 200 | 14 |
| `/api/v1/public/persons` | 200 | 17 |
| `/api/v1/public/media` | 200 | 614 |
| `/api/v1/public/heritage` | 200 | 56 |
| `/api/v1/public/c-terms` | 200 | 30 |

前端首页 200,含应用挂载点,`/api` 代理贯通。**本地端到端可用。** `[实测]`

---

## 3. 代码构成

| 层 | 规模 |
| :--- | :--- |
| 后端 | 101 个 `.py`,12,535 行 |
| 前端 | 52 个 `.vue`,87 个 `.ts` |
| 运维脚本 | `scripts/` 30+ 个 operator 脚本 |
| 迁移 | 17 个 revision,`0001`–`0017`,**严格线性单头,每个 `downgrade()` 均有实体** `[复核]` |

**工具链实为绿色**(非抑制): `ruff check` / `ruff format --check` / `mypy` 全部通过。`[实测]`
前端 `lint` / `typecheck` / `build` 全部通过;`lint` 有 **1073 条 warning、0 error**。 `[实测]`

---

## 4. 数据现状(实测于 `hfm_prod`)

| 表 | 实测 | 说明 |
| :--- | ---: | :--- |
| `sources` | 120 | |
| `content_artifacts` | 117 | 全部 admitted/verified |
| `publication_records` | 117 | 全部 PUBLISHED |
| `documents` | **675** | **全部 `NEEDS_REVIEW`**,无一条通过复核 |
| `chapters` / `passages` | 149 / 1007 | 12 卷 + 137 篇 |
| `c_domain_terms` / `relations` | 30 / 5 | |
| `assertions` / `evidences` / `citations` | 23 / 23 / 23 | citations 的 `passage_id` 全为空 |
| `heritage_projects` / `relations` | 56 / 2 | relations 仅 2 条 |
| `media_assets` | 681 | 见 §5 |
| `editions` | 91 | |
| **`versions`** | **0** | 文本版本层不存在 |
| `events` / `institutions` / `research_*` / `reconciliation_runs` | **0** | schema 存在,无数据 |

**引用完整性优良**:681/681 个 `object_key` 文件存在,681/681 sha256 逐字节吻合;
反向仅 9 个非媒体文件未入库(6 个 `.DS_Store`、`.videothumbnail.db`、`.lnk`、1 个 `.zip`)。 `[复核]`

**语料**:`corpus/extracted-text/` 667 个文件 **0 个入版本控制**(`.gitignore:57`)。 `[实测]`

---

## 5. 媒体与隐私现状

```text
media_assets = 681
  P0  608 published
  P1   34  (6 published + 28 draft)
  P2   35  draft
  P3    4  draft
  derivatives (original_object_key IS NOT NULL) = 0
  redaction_token 非空 = 0
```

**隐私模型已是不变量**(5 条 CHECK 存在于生产 schema;明文反证:`UPDATE … privacy_class='P3' → published` 被拒)。 `[实测]`

**但授权位不是** —— 见 R-07。

---

## 6. 治理与授权现状

### 6.1 存在的授权工件

| 事项 | 工件 | 状态 |
| :--- | :--- | :--- |
| Phase 0.4 / Phase 1 治理与执行 | `HFM-PHASE1-*-AUTHORIZATION-v1.md` 等 | 存在,含 per-file SHA-256 授权清单 |
| 614 条媒体发布 | `content-production/07-review/media-publication-clearance.json` | 存在,计数与 DB 精确吻合 |
| P1 内容发布 | `publication-rights-manifest.json` | 存在 |

### 6.2 **无授权工件即执行的事项**

| 事项 | 现状 |
| :--- | :--- |
| **Phase 2 全部(P2-00 … P2-10)** | 每一份 `HFM-PHASE2-*.md` 自述 `GOVERNANCE CANDIDATE · NO IMPLEMENTATION AUTHORIZATION`;全仓搜不到 `PHASE_2_EXECUTION`。**14 个工作包已实现,迁移 0014–0017 已应用。** |
| P6 版本补录 `A000529–532` | **签批单空白**(见 C-04),roadmap 却记「已签批并执行」 |
| 28 条 P1 非遗项 | 分级为「直接公开」,但**无任何清关清单** |

### 6.3 **治理冲突(未裁决)**

仓库内同时存在两个互斥立场:

| | A 侧(2026-08-29,L1 源事实归档 + 请求登记册) | B 侧(2026-09-01,资产展示政策) |
| :--- | :--- | :--- |
| 发布授权 | `CLIENT_CONFIRMATION_REQUIRED` | `CUSTOMER_PROVIDED = TRUE → GRANTED` |
| 阻塞分类 | `CONTENT_PUBLICATION_BLOCKER` | 版权「不再作为开发约束」 |
| 逐件要求 | CR-005「逐件登记状态与权利」 | 「统一视为已授权」 |

**B 侧所依据的「客户声明」在全仓只有自引用链条** —— `HFM-ASSET-PRESENTATION-POLICY.md:7` 是源头,
`CONTENT-ASSET-MAP.md:73`、`UI-CONTENT-MODEL.md:8`、`media-publication-clearance.json:4` 均为引用;
**无任何客户原始文件**。该政策由 commit `329b983`(一个前端 UI 验收提交)引入。 `[实测]`

登记册与归档此后**从未修订**,今天仍带 8 处 `CONTENT_PUBLICATION_BLOCKER`。

> **本说明书不裁决此冲突。** 它直接决定 614 条已发布于公开 API 的资产是否有授权基础,须由授权方指向来源。

---

## 7. 验证现状

### 7.1 CI 实际执行(唯一 workflow:`release-gate.yml` → `release-gate.sh`)

```text
backend: ruff check · ruff format --check · mypy · pytest (578) · governance precheck
frontend: lint · typecheck · build
```

### 7.2 **从不执行**(约 457 项)

| 套件 | 规模 | 原因 |
| :--- | ---: | :--- |
| `scripts/tests/` | 16 文件 / 103 项 | 门禁从 `apps/backend` 跑 pytest,repo 根的 `scripts/tests` 永不被收集 |
| `apps/frontend/src/__tests__/` | 29 spec / 248 项 | 门禁不跑 `pnpm test` |
| `apps/frontend/e2e/` + `e2e-auth/` | 18 spec / 95 项 | 仅被 `golden-runtime-gate.sh`、`fast-runtime-gate.sh` 调用,两者均无 workflow 调用 |
| `test-release-gate-precheck.sh` | 11 个对抗用例 | 全仓零调用 |

合同要求(`HFM-PHASE2-WORK-PACKAGE-CONTRACT-v1.md` §P2-08)CI 基线为「lint/**type/test**/build」—— **交付的门禁缺 test**。 `[复核]`

### 7.3 验证不可复现的实例

- 「667 篇已抽取」的证据本体 `corpus/extracted-text/` **不在版本控制**
- P2 脱敏金丝雀的证据库(克隆库)**已删除**;生产库 `derivatives = 0`
- 一个测试写死 `/Users/likeming/Sites/hfb`,在 CI 中**静默跳过**

---

# 8. 风险登记册

> 风险 = 可能造成损害的事。`OPEN` / `ACCEPTED` / `CLOSED (commit, 日期)`

| ID | 级别 | 风险 | 证据 | 状态 |
| :--- | :--- | :--- | :--- | :--- |
| **R-01** | **CRITICAL** | **项目最硬的治理红线没有活的执行机制。** 冻结边界守卫是自证的:`GuardrailReport(clinical=CLINICAL_STATE,…)` 之后 `ok` 检查 `self.clinical == CLINICAL_STATE` —— 自己和自己比。七条负向边界(CLINICAL=REJECTED / AI·DISPLAY·XR=DEFERRED / CREDENTIAL_MIGRATION / HFB 导入 / M4–M7)全部不可失败。且该测试还被从 release gate 中 deselect。**在任何标记扫描覆盖不到的位置加一个诊断界面,所有守卫仍报 `ok`。** | `phase2/guardrails.py:219-227`、`:120-133`;`release-gate.sh:34-38` | OPEN |
| **R-02** | **CRITICAL** | **公开 API 上 614 条资产的授权依据不可审计。** 政策 §0 声称的「客户声明」在全仓只有自引用链条,无客户原始文件,且与项目自己的 L1 归档(要求逐件登记权利)冲突。 | §6.3 | OPEN |
| **R-03** | HIGH | **`publish-content.py` 默认写生产。** `--dry-run` 为 `action="store_true"` 且**无 `default=True`** → 默认 COMMIT。是脚本目录里**唯一**不倒向 dry-run 的写生产脚本(其余 12 个均 `default=True` + `--commit`),且**不要求任何授权清单**(对比 `publish-media.py` 的 `--clearance-file` 为 `required=True`)。roadmap 记载 P1 发布用的正是它。 | `scripts/publish-content.py:487-491` | OPEN |
| **R-04** | HIGH | **服务层 `PermissionError` → HTTP 500。** `error_handlers.py` 只注册 `DomainException`/`RequestValidationError`/`StarletteHTTPException`/兜底 `Exception`,而 `DomainException(BaseException)` 与 `PermissionError`(⊂`OSError`)无继承关系。7 个 service 裸抛 `PermissionError`。「已登录但权限不足」的请求得到 500,而不是 403。`deps.py:33-35` 的注释称此类泄漏**曾修过** —— 只修了依赖层。 | `core/error_handlers.py:153-156`;`phase1/{c_domain:353,literature:496,heritage:326,reader:136,publication:43}.py` | OPEN(机制已确认,未做运行时复现) |
| **R-05** | HIGH | **约 457 项测试从不执行。** 见 §7.2。同时 `BASELINE-MANAGEMENT.md:193` 声称「Vitest 全部 PASS」。这不是「质量尚可」,是**没有回归保护**。 | §7.2 | OPEN |
| **R-06** | HIGH | **`publish-content.py` 之外,所有 operator 脚本的授权靠约定。** 多数脚本 validate 目标库(DB 名 + 迁移头),但没有一个强制要求授权工件;`--clearance-file` 仅 `publish-media.py` 与 `publish-media-derivatives.py` 要求。 | `scripts/*.py` | OPEN |
| **R-07** | MEDIUM | **P2 授权位仅由服务层强制,数据库不管。** `ck_media_assets_p2_original_never_published` 对「P2 且是导数」的行恒真,**与授权位无关**。绕过 service 的 SQL 写入可发布无授权的 P2 导数。**本仓库的 `media/__init__.py:10` 声称这是数据库保证 —— 该表述超出 schema 实际。** | 生产 `pg_constraint`;`media/__init__.py:10` | OPEN |
| **R-08** | MEDIUM | **管理端建用户完全绕过密码策略。** `hash_password(body.get("password",""))` 直调,空密码/`123456`/与用户名相同均可建号。`auth.py:47-49` 自称 `MIN_PASSWORD_LENGTH` 是「SINGLE source」,此端点是未登记的第三条路径。 | `api/v1/phase1.py:162-164` | OPEN |
| **R-09** | MEDIUM | **发布状态机与职责分离只在 Python 里。** `PENDING_REVIEW → PUBLISHED`、`REJECTED → PUBLISHED`、`reviewed_by = creator_id` 均无数据库约束。任何直接 SQL 或未来 bug 写入列即绕过。 | `models/publication.py:168-173`;迁移 `0010:95-128` | OPEN |
| **R-10** | MEDIUM | **被测试的数据访问层不是生产运行的那层。** 8 个 `repositories/*.py` 仅被测试导入;生产 service 全部直接 `select()`。两层并存,**执行的是没被测试的那层**。 | `apps/backend/src/hfm/repositories/` | OPEN |
| **R-11** | MEDIUM | **公开 API 零 HTTP 级测试。** 32 条端点路径中 28 条无端到端测试,**包括全部 `/api/v1/public/*`**。公开 API 就是交付物本身,却无任何东西能抓住「新处理器漏了发布状态过滤」。 | `apps/backend/tests/` | OPEN |
| **R-12** | MEDIUM | **密钥扫描器失效。** `scripts/check-secrets.py` 实测 `SECRET_BOUNDARY=FAIL (27 findings)`,且**不在任何 CI 中**。(经逐条核实**无真实凭据入库**,22+ 为测试夹具,其余为本地一次性 Postgres 口令与占位 DSN。)控制项失效,非凭据泄漏。 | `scripts/check-secrets.py` | OPEN |
| **R-13** | MEDIUM | **导数 object_key 保留原文件名。** `DERIVATIVE_PREFIX + 原名`;`/public/media` 返回 `object_key` 与 basename。文档图像脱敏了,**文件名没脱敏**。 | `redact-media-derivative.py:685`;`api/v1/phase1.py:357-369` | OPEN |
| **R-14** | LOW | **生产库领先 main 两个迁移。** `hfm_prod` @0017,`main` 声明 head=0015。从 main 拉分支的人跑 operator 脚本会对生产库报 `database must be migrated at 0015` 而失败。 | `git ls-tree origin/main …versions/` | OPEN |
| **R-15** | LOW | **本机环境混乱。** 11 个 `hfm` 库,其中 10 个停在 alembic **0014**(缺 `documents` 等表);1 个 git worktree 已 prunable;`:8000` 跑着早于本轮全部改动的旧后端。 | `psql -lqt`;`git worktree list` | OPEN |

---

# 9. 缺口登记册

> 缺口 = 应当存在而缺失的东西。

| ID | 级别 | 缺口 | 证据 |
| :--- | :--- | :--- | :--- |
| **G-01** | HIGH | **媒体线没有用户入口。** 渲染 614 条资产的 `MediaLibraryView.vue`(路由 `/library`)**全站零入站链接**,不在导航,不在用户指南,不在交付清单。P3 的验收判据是「`/public/media` 返回数据」—— **一个没有调用者的端点满足了验收标准**。 | `grep "'/library'" apps/frontend/src` → 0(除 router 定义) |
| **G-02** | HIGH | **公网部署未做。** 无域名、无证书、无生产服务器;`infra/` 全为 `.example`。 | `find infra -name '*.conf' -not -name '*.example'` → 0 |
| **G-03** | HIGH | **`versions` 文本版本层为空(0 行)**,`editions` 有 91。版本感知的引用/归属无法工作。roadmap 自己也标此为未决。 | §4 |
| **G-04** | HIGH | **28 条 P1 非遗项标「直接公开」却无清关清单。** 政策 §4 定义 P1 = 正常公开,但无任何授权工件覆盖它们。 | `heritage-evidence-classification.csv`;`media-publication-clearance.json` 仅覆盖 614 |
| **G-05** | MEDIUM | **`heritage-derivative-clearance.json` 不存在** —— 而它是我交付的 `publish-media-derivatives.py` 的必需输入。管线**无法端到端运行**。 | `ls content-production/07-review/heritage-derivative-clearance.json` → No such file |
| **G-06** | MEDIUM | **Phase 2 无授权工件**(R-02 的治理侧)。见 §6.2。 | §6.2 |
| **G-07** | MEDIUM | **8 篇 `.docx` 从未处理**,以 `PARTIAL` / `NEEDS_REVIEW` 躺在生产库(`HFM-A000003/004/005/640/655/681/683/684`)。 | `documents` = 675 vs 台账 667 |
| **G-08** | MEDIUM | **台账溯源 209/667 行无法解析**(21 条 `A_TEXT` + 188 条 `B_OCR`,后者为 glob 形式)。文本都在,但台账不是可追溯的溯源记录。 | `corpus/document-production-ledger.csv` |
| **G-09** | MEDIUM | **语料不在版本控制。** 667 个文件被 gitignore;「已抽取」的证据本体不在仓库。 | `.gitignore:57` |
| **G-10** | MEDIUM | **4 个公开视图读静态数据而 live 端点已存在**:`HeritageView.vue`、`ReaderDocView.vue`、`ResearchSearchView.vue`、`ResearchEntityView.vue`。其中非遗页尤其割裂 —— **首页同源数据走 live,非遗页走静态。** | 各文件行号见 `[复核]` |
| **G-11** | LOW | **`content-production/` 5 个目录是空脚手架**(`03-text-extraction`、`04-entities`、`05-relations`、`06-media`、`09-import-packages`),无文件无 `.gitkeep`。 | `ls` |
| **G-12** | LOW | **8 张表 schema 存在 0 行**:`versions`、`events`、`event_assertions`、`event_relations`、`institutions`、`research_notes`、`research_annotations`、`research_projects`、`reconciliation_runs`。 | §4 |
| **G-13** | LOW | **1 个真实资产未登记**:`针灸甲乙经/论著/皇帝甲乙经/《黄帝针灸甲乙经新校本》黄龙祥1990.zip`。 | 681 vs 689 清单 |

---

# 10. 失效声明登记册

> 仓库中**当前仍然存在**的、与实测不符的声明。这些比缺失更危险 —— 它们会被当作事实使用。

| ID | 声明出处 | 声称 | 实测 | 状态 |
| :--- | :--- | :--- | :--- | :--- |
| **C-01** | `roadmap §4` | 「金丝雀已验证…发布后 derivative published」 | 生产库 `derivatives = 0`;证据库(克隆库)**已删除**,不可复现 | OPEN |
| **C-02** | `roadmap:352` | 「A000529–532 补录 ✅ **已签批**并执行」 | 签批单**空白**:四行 `[ ] 同意` 未勾,签署人栏 `__________________` | OPEN |
| **C-03** | `ND1-RELEASE-QUALIFICATION.md` | 当前运维权威文档,9 处版本号 | 8 行写 `0014` + **1 行写 `0017`** —— **自相矛盾**,其中 1 行是本轮改坏的 | OPEN |
| **C-04** | `HFM-FRONTEND-CONTENT-CONTRACT-v1.md` | 标 `EFFECTIVE`,称 `/heritage` 与 `/media` 「❌ 返回 0」 | 实测 56 与 614 | OPEN |
| **C-05** | `roadmap §1` 基线表 | sources 31/34、artifacts 31、pub_records 31、editions 87、documents 667 | **120 / 117 / 117 / 91 / 675** —— 7 行中 5 行过期 | OPEN |
| **C-06** | `BASELINE-MANAGEMENT.md:193` | 「Ruff/Ruff Format/mypy/pytest/ESLint/**Prettier**/vue-tsc/**Vitest**/Build 全部 PASS」 | Prettier 与 Vitest **不属于任何门禁** | OPEN |
| **C-07** | `GAP-MAP.md` / `IMPLEMENTATION-TRUTH-GAPS.csv` | `GAP-01` 研究工作台无写表单 | **已交付**(交付清单 B3–B6) | **已失效但仍在册** |
| **C-08** | 同上 | `GAP-02` 首页未接后端 | **已接**(`useHomeContractData`);但 G-10 的 4 个视图确有同类问题 | **部分失效** |
| **C-09** | `HFM-TEST-COVERAGE-REALITY.md` | 682 pytest + 235 vitest + 51 ops = 968 全绿 | 实测 578 / 248 / 103;**且 457 项从不执行**。该表把「本地跑过」表述为「已通过」而不区分 CI | OPEN |
| **C-10** | `REALITY-DASHBOARD.md` | `HEAD 1e9336e`、`BRANCH recovery/hfm-foundation`、`P0_GAPS = 0` | 非交付分支;本轮审计发现 2 项 CRITICAL | OPEN |
| **C-11** | `HFM-SYSTEM-REALITY.md:51,53` | `/library` 与 `/admin/audit` 均「**完全正常**」 | `/library` 无入口(G-01);`/admin/audit` 因前端 GET 撞后端 POST-only 而**无条件显示错误态** | OPEN |
| **C-12** | `media/__init__.py:10`(本轮引入) | 「P2 material reaches the public projection only as a redacted derivative」归为**数据库**保证 | 数据库只强制「已发布的 P2 行必须是导数」,**不强制授权位** | OPEN |

---

# 11. 本轮审计自身引入或未决的事项

诚实记录,供后续处理:

| # | 事项 | 性质 |
| :--- | :--- | :--- |
| A-1 | `media/__init__.py:10` 过度陈述数据库保证(= C-12) | 本轮引入,待修 |
| A-2 | `ND1-RELEASE-QUALIFICATION.md` 被我改成自相矛盾(= C-03 的一部分) | 本轮引入,待修 |
| A-3 | roadmap 「金丝雀已验证」不可复现(= C-01) | 本轮写入,待改为可复现措辞或补证据 |
| A-4 | `publish-media-derivatives.py` docstring 指向不存在的清单(= G-05) | 本轮引入,待显式标为阻塞项 |
| A-5 | 迁移头推进触及约 60 文件,我把版本号硬编码从 5 处扩到 6 处 | 本轮加深了一个既有设计缺陷 |
| A-6 | PR #7(`hfm-canonical` → `main`)处于 **OPEN / CLEAN / CI 绿**,**未合并** | 待决 |
| A-7 | 本说明书未裁决 §6.3 的治理冲突 | **超出我的职权** |

---

# 12. 一句话结论

**工程实现质量高**(引用完整性 681/681 逐字节吻合、隐私模型已成数据库不变量、迁移链干净、工具链真绿),
**但系统的「真」与「所述之真」之间存在系统性偏差** —— 文档漂移、验证不可复现、声明强度高于实现强度。

本轮审计最重的一条:**项目最硬的治理红线(R-01)目前没有活的执行机制。**

最需要授权方裁决的一条:**614 条已公开资产的授权依据(R-02)无法被审计。**

---

*本文件是描述,不是裁决。风险与缺口的处置需要授权方决定。*

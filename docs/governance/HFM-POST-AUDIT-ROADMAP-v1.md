# HFM 后续推进计划（Post-Audit Roadmap）— v1

**基准审计**：`HFM-INDEPENDENT-ARCHITECTURE-AUDIT.md`（2026-09-13，独立穿透式审计）
**状态**：`PASS_WITH_GAPS`；软件交付范围 COMPLETE；内容生产范围 NOT COMPLETE。
**治理前提**：`AUTO_NEXT_PHASE=FORBIDDEN`，每个阶段须经显式授权后方可启动。

---

## 0. 执行摘要

审计确认的真实状态一句话概括：**工程底座与权威元数据基线已建成且质量高，
但"数据 → 公众展示"的最后一步发布流水线从未通水，知识图谱层与全文层基本为空。**

推进主线按依赖关系排成 5 个阶段（P1–P5）+ 1 个收尾（P6）：

```text
P1 内容发布执行 ──────► 公众门户显示真实生产数据（关键路径，立即）
      │
      ├──► P2 结构化知识对象（全文抽取 + 篇章/穴点/证据链）──► 中医专科纵深
      │
      ├──► P3 非遗与多媒体资产入库 ─────────────────────────► 非遗专栏动态化
      │
      ├──► P4 研究工作台深化（在线阅读 + 标注 + 引文）──────► 深度科研闭环
      │
      └──► P5 公网部署（域名/证书/生产服务器/运维）────────► 正式发布
      （P2/P3/P4 相互独立，可并行；P5 依赖 P1 完成，且建议 P2/P3 至少部分就绪）

P6 收尾：5 条 DEFERRED 版本补录 + 合订本分类规则（R3，不阻塞）
```

**当前已完成（本次会话新增）**：P1 的工具链已就绪 —— `scripts/publish-content.py`
（受控幂等发布脚本）与 `scripts/tests/test_publish_content.py`（3 用例，隔离
Postgres@0015 真实测试）已合并 `main`，CI 全绿。**尚未对 `hfm_prod` 执行发布。**

---

## 1. 关键事实基线（来自审计，用于每阶段验收对照）

| 表 | 现状 | 阶段目标 |
| :--- | :--- | :--- |
| `sources` | 0 | P1 建立源注册表 |
| `content_artifacts` | 0 | P1 为 14 著作 + 17 人物生成工件 |
| `publication_records` | 0 | P1 生成 PUBLISHED 记录 |
| `documents` | 675（全文未抽取，磁盘 `extracted-text/` 空） | P2 全文落地 |
| `chapters` / `passages` | 0 / 0 | P2 《针灸甲乙经》篇章段落 |
| `c_domain_terms` / `c_domain_relations` | 0 / 0 | P2 经穴/词条 + 关系图谱 |
| `assertions` / `evidences` / `citations` | 0 / 0 / 0 | P2/P4 证据链 |
| `heritage_projects` / `heritage_relations` | 0 / 0 | P3 非遗项目 |
| `media_assets` | 0 | P3 媒体资产 |
| `versions` | 0（87 是 editions） | P6 具体文本版本层 |

---

## 2. P1 — 内容发布执行（关键路径，立即）

**目标**：使 `/api/v1/public/home`、`/works`、`/persons` 返回真实生产数据，
公众门户从静态 fallback 切换为真实数据。

**当前状态**：发布脚本已建并测试通过，但 `hfm_prod` 上 `sources` /
`content_artifacts` / `publication_records` 仍为 0。

### 2.1 工作项

1. **权利复核（前置阻断）**：对 14 著作 / 17 人物 / 87 版本逐条判定权利分类。
   - 古籍原文（《针灸甲乙经》等）→ `public_domain`
   - 客户提供的现代论文/材料 → `customer_owned` 或 `licensed` / `third_party_permission_required`
   - 产出：权利判定表（CSV，可复用 `content-production/07-review/rights-review.csv` 作为起点）。
2. **`sources` 注册表修复**：`content_artifacts.source_id → sources(id)` RESTRICT，
   当前 `sources` 空且与 `documents.source_asset_id`（675 行全有）脱节。
   - 发布脚本已用「每实体一个 canonical source」方案规避；文档级 source 注册是独立补强项。
3. **执行发布**：先 `--dry-run`（只读 + 回滚）预演，确认无误后正式 `--scope all`。
4. **前端连通（GAP-02）**：发布后 `WorksView` / `SearchView` / 首页目前主要读静态
   `WORK_COLLECTION` / `searchIndex`，需接入真实 `/api/v1/public/*` 分页流。
   - 首页已具备 `useHomePublicData` 优雅降级，发布后自动生效；其余页面需 UI 内容传播改造。

### 2.2 门禁

| | |
| :--- | :--- |
| **ENTRY** | 权利复核完成；`PWE_IMPORT_PHASE=CLOSED` 保持不变；发布脚本就绪（已满足） |
| **AUTHORIZED_SCOPE** | 权利判定表、发布脚本执行、前端 public API 接入、对应测试 |
| **FORBIDDEN_SCOPE** | 不改冻结的 PWE 映射基线/导入逻辑；不开放外网；不发布未经复核的内容 |
| **EXIT** | `/public/home` `/works` `/persons` 稳定返回生产数据；零草稿/私有数据泄露 |
| **AUTHORIZATION** | 需显式授权（权利复核结论 + 发布范围由授权方确认） |

---

## 3. P2 — 结构化知识对象（R2，工作量最大）

**目标**：填补「名实缺口」——`chapters`/`passages`/`c_domain_terms`/
`c_domain_relations`/`assertions`/`evidences`/`citations` 从 0 → 有真实数据。

### 3.1 工作项（按依赖）

1. **全文抽取（最大前置）**：675 篇文献当前磁盘 `extracted-text/`、`raw-ocr/`、
   `rendered-pages/` 全空。须真实执行 OCR/文本提取并落盘（`corpus/extracted-text/`）。
2. **《针灸甲乙经》篇章段落**：卷/篇/段结构化 → `chapters` + `passages`。
3. **经穴/词条知识对象**：`normalized/knowledge-object-candidates.csv`（已有 26 穴点
   候选）→ `c_domain_terms` + `c_domain_relations`。
4. **证据链**：`normalized/evidence.csv`（已有 24 条候选）→ `assertions` /
   `evidences` / `citations`。

### 3.2 门禁

| | |
| :--- | :--- |
| **ENTRY** | P1 完成（内容已发布，公众可感知增量）；全文抽取管道就绪 |
| **EXIT** | 《针灸甲乙经》篇章段落 + 经穴词条 + 关系图谱有真实数据，`/public/c-terms` 可查 |
| **AUTHORIZATION** | 需显式授权（中医结构化提取的范围与质量标准） |

---

## 4. P3 — 非遗与多媒体资产入库（R2）

**目标**：`heritage_projects` / `heritage_relations` / `media_assets` 从 0 → 有数据，
非遗专栏从静态映射层转为受控入库。

- 非遗佐证材料已就绪（`hfmzl/非遗佐证/` 68 文件）；媒体版权模型（P2-05）已完整。
- 工作项：非遗项目 + 传承谱系入库；媒体资产（图片/视频/PDF）带 rights 元数据入库。
- **ENTRY**：P1 完成；**EXIT**：`/public/heritage` `/public/media` 返回生产数据。

---

## 5. P4 — 研究工作台深化（R2/R3）

**目标**：研究者可对 675 篇文献做在线全文阅读 + 高亮标注 + 引文生成，形成深度科研闭环。

- 当前工作台仅「项目 + 笔记」闭环；后端 `assertions`/`evidence-chain` 端点已具备，
  缺前端交互界面与可标注正文。
- **ENTRY**：P2 全文抽取完成（否则无正文可标注）。

---

## 6. P5 — 公网部署（R4）

**目标**：从「本地可运行」→「公网生产」。

- 域名/证书、生产服务器、生产数据库、运维流程。
- `infra/nginx/*.example`、`infra/systemd/*.example` 需实例化为生产配置。
- **ENTRY**：P1 完成，P2/P3 至少部分就绪。

---

## 7. P6 — 收尾（R3，不阻塞）

- 5 条 `DEFERRED` 版本补录（缺失版权页 OCR 证据）。
- 合订本（如《针灸甲乙经、伤寒论…》四书合刊）多对多 Work 关联规则扩展。

---

## 8. 立即行动（本周）

1. **权利复核**：产出 14 著作 / 17 人物的权利判定表（P1 前置）。
2. **对 `hfm_prod` 跑 `--dry-run`**：验证发布脚本在真实 675/14/87 数据上的行为（只读、回滚、不落库）。
3. **P1 前端接入设计**：`WorksView`/`SearchView` 从静态数据切换到真实分页流的最小改造方案。

> 本计划随每阶段授权与完成情况更新；阶段间不自动启动，须逐段显式授权。

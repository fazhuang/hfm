# HFM 设计 Token 提案 — Design Tokens Proposal（CANDIDATE）

Status: DESIGN INPUT · **CANDIDATE（候选值，不直接覆盖现状 tokens.css）**
Date: 2026-08-31（UI-00 v2 语义方向更新 2026-09-01）· 实施节点: UI-01（Design Foundations）经设计评审后落盘
现状基线: `apps/frontend/src/styles/tokens.css`（40 行，机制保留、值重设计）

**v2 语义方向（客户/UI-00 收敛）**：`当代东方数字人文`。颜色语义方向 = 暖白 / 墨色 / 低饱和朱砂 / **土褐** / 铜金 / 青灰。本阶段确定 semantic direction，**暂不冻结最终 HEX**；下表为候选值，UI-01 经对比度验证与设计评审后定稿。

**契约**：本文件仅提出候选 token 架构与候选值。任何取值在 UI-01 通过设计评审与对比度验证前，不得写入代码。

---

## 0. Token 架构（三层）

```text
Primitive（原始值）──→ Semantic（语义）──→ Component（组件）
--hfm-pr-*               --hfm-color-*        --hfm-btn-*
--hfm-font-raw-*         --hfm-space-*        --hfm-card-*
                         --hfm-text-*         --hfm-table-*
                         --hfm-radius-*       --hfm-reader-*
                         --hfm-shadow-*
                         --hfm-bp-*
```

- 现有 `--hfm-*` 命名空间保留，语义层继续使用；新增 primitive 层供派生。
- 暗色模式 = 在 `.dark` 作用域覆盖 **semantic 层**，primitive 不动。

---

## 1. COLOR（候选）

### 1.1 核心命题

> 不以"大红 + 金色"等同于中国文化；建立暖白/米白、墨黑、低饱和朱砂、铜金/暗金、青灰的独立色彩系统（P3/P5）。

### 1.2 Semantic 色候选（浅色）

| Token | 候选值 | 角色 | 对比度目标（对底） |
| --- | --- | --- | --- |
| `--hfm-color-canvas` | `#f7f4ef`（暖米白） | 页面画布（存档纸色，非做旧） | — |
| `--hfm-color-surface` | `#ffffff` | 内容表面 | — |
| `--hfm-color-elevated` | `#ffffff` | 浮层/弹层（少用） | — |
| `--hfm-color-text` | `#1f1a16`（暖墨黑） | 主文字 | ≥ 12:1 |
| `--hfm-color-text-secondary` | `#4b4238` | 次级文字 | ≥ 7:1 |
| `--hfm-color-text-muted` | `#6f6557` | 元数据（对照现 `#78716c` 提对比） | ≥ 4.5:1 |
| `--hfm-color-border` | `#e2dcd2` | 边框/分隔线（暖灰） | 装饰性 |
| `--hfm-color-border-strong` | `#c9bfae` | 强调分隔线 | 装饰性 |
| `--hfm-color-accent` | `#a0402a`（低饱和朱砂） | 交互/强调（替换现紫 `#7c3aed`） | 正文用法 ≥ 4.5:1 |
| `--hfm-color-accent-hover` | `#8a3522` | 强调悬停 | — |
| `--hfm-color-heritage` | `#8a6a2f`（铜金/暗金） | 品牌/徽记/年份/分隔（P5 身份色） | 装饰/大字 ≥ 3:1 |
| `--hfm-color-ink` | `#1f1a16` | 古籍正文/标题（墨黑） | ≥ 12:1 |
| `--hfm-color-azure` | `#5c6b6f`（青灰） | 次要信息/标签/图谱节点 | ≥ 4.5:1（文字用法） |
| `--hfm-color-evidence` | `#2f5d50`（墨绿） | 证据/来源语义（P8） | ≥ 4.5:1 |
| `--hfm-color-citation` | `#4a5a8a`（靛青） | Citation/版本语义 | ≥ 4.5:1 |
| `--hfm-color-interactive` | `= accent` | 链接/按钮 | — |
| `--hfm-color-danger` | `#b3261e` | 错误/撤回 | ≥ 4.5:1 |
| `--hfm-color-warning` | `#8a5a00` | 警告（演示/未校对类提示） | ≥ 4.5:1 |
| `--hfm-color-success` | `#1e6b3c` | 成功 | ≥ 4.5:1 |
| `--hfm-color-on-accent` | `#ffffff` | 强调底上的文字 | ≥ 4.5:1 |

> 候选值以暖色系（米白/墨/朱/铜/青灰）锚定文化身份，与现 token 的纯中性 + 紫色形成根本区分。所有取值在 UI-01 用 WCAG 对比度工具逐项验证（P10）。

### 1.3 Dark 候选（墨黑画布）

| Token | 候选值 |
| --- | --- |
| canvas | `#16130f`（暖黑） |
| surface | `#1e1a15` |
| text | `#f2ece1`（暖白） |
| text-secondary | `#c9bfae` |
| text-muted | `#9c9284` |
| border | `#3a342b` |
| accent | `#cf6a4a`（提高明度朱砂） |
| heritage | `#c9a24b`（提高明度铜金） |

---

## 2. TYPOGRAPHY（候选）

### 2.1 字体策略（中文字体：系统可用性 / Web 性能 / 授权优先）

| 角色 | 候选栈 | 说明 |
| --- | --- | --- |
| Sans（UI/元数据/数据） | `system-ui, -apple-system, "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif` | 延续现栈 + 中文回退显式化 |
| Serif（标题/古籍/长文） | `"Songti SC", "SimSun", "Noto Serif CJK SC", serif` | 系统宋体优先；**不引入付费/自托管字体**（性能与授权）；Web 字体如未来引入须先审计授权与 WOFF2 体积 |
| Display（大标题/题名） | `serif 栈 + 字重/字距控制` | 不单独引入显示字体；用 500–700 字重 + 适度字距 |
| Numeric（年份/计数） | `"STIX Two Math", "Times New Roman", serif 数字（等宽数字特性）` | 时间轴年份用衬线数字；数据用 `font-variant-numeric: tabular-nums` |
| Ancient（古籍正文） | `serif 栈，18px/1.9，字距 0.02em` | 与正文同栈，靠字号/行距/颜色区分 |

### 2.2 字号 / 行高 / 字距 scale（候选）

| 角色 | 字号 | 行高 | 备注 |
| --- | --- | --- | --- |
| Display | 2.5–3.5rem（40–56px） | 1.15 | 首页 HERO/人物扉页 |
| Heading 1 | 1.75–2rem | 1.3 | 页面标题 |
| Heading 2 | 1.375rem | 1.4 | 区块标题 |
| Heading 3 | 1.125rem | 1.5 | 卡片标题 |
| Body | 1rem（16px） | 1.7–1.9 | 正文（P6） |
| Long-form | 1.0625–1.125rem（17–18px） | 1.9 | 阅读器/传记（P6） |
| Metadata | 0.8125rem（13px） | 1.5 | 元数据/出处 |
| Numeric | 1rem+ | tabular-nums | 统计/年份 |
| Citation | 0.8125rem | 1.6 | 引用块/出处行 |
| Ancient | 1.125rem（18px） | 1.9 | 古籍正文 |

字号档位（Primitive）：`xs 12 / sm 13 / base 16 / lg 18 / xl 22 / 2xl 28 / 3xl 40 / 4xl 56`（rem 化，基准 16px）。

---

## 3. SPACING（UI-01 定稿：保持 N×0.25rem 不变式，兼容既有组件）

**定稿说明**：Phase-2 代码已引用 `--hfm-space-5`（未定义，潜在缺陷）且 `--hfm-space-6=1.5rem` / `--hfm-space-8=2rem` 已被组件使用。为避免回归，保持 `space-N = N×0.25rem` 不变式，大节奏档位改用 `12/16/24/32` 命名（不占用既有 6/8 语义）：

```text
--hfm-space-0: 0
--hfm-space-1: 0.25rem   (4)
--hfm-space-2: 0.5rem    (8)
--hfm-space-3: 0.75rem   (12)
--hfm-space-4: 1rem      (16)
--hfm-space-5: 1.25rem   (20)  ← 已定义（修复引用未定义缺陷）
--hfm-space-6: 1.5rem    (24)
--hfm-space-7: 1.75rem   (28)  ← 已定义
--hfm-space-8: 2rem      (32)
--hfm-space-12: 3rem     (48)  ← 已定义（区块节奏）
--hfm-space-16: 4rem     (64)  ← 已定义（大区隔）
--hfm-space-24: 6rem     (96)  ← 已定义（首页大区隔）
--hfm-space-32: 8rem     (128) ← 已定义（展厅级）
```

规则：区块分隔用 12/16/24 档制造节奏；组件内部用 1–4 档。

---

## 4. RADIUS（候选，克制）

| Token | 值 | 用途 |
| --- | --- | --- |
| `--hfm-radius-none` | 0 | 阅读器正文、表格、引文 |
| `--hfm-radius-sm` | 0.25rem（4） | 输入、徽标、按钮 |
| `--hfm-radius-md` | 0.5rem（8） | 卡片（现 8，保持） |
| `--hfm-radius-lg` | 0.75rem（12）→ 建议降至 0.625rem（10） | 大面板（文化平台克制） |

**大圆角（>12px）不进入系统**；不出现 pill/胶囊按钮。

---

## 5. SHADOW（候选，零浮起原则）

| Token | 值 | 用途 |
| --- | --- | --- |
| `--hfm-shadow-none` | none | 默认（内容卡片无阴影） |
| `--hfm-shadow-overlay` | `0 2px 8px rgba(31,26,22,.12)` | 仅浮层/下拉/抽屉 |
| `--hfm-shadow-focus` | `0 0 0 3px rgba(160,64,42,.25)` | 焦点环（P10 可见焦点） |

规则：**卡片永不悬浮**；层级由边框/留白承担（审计 §11 判定保持）。

---

## 6. BORDER（候选）

| Token | 值 | 用途 |
| --- | --- | --- |
| `--hfm-border-1` | 1px solid `--hfm-color-border` | 卡片/列表 |
| `--hfm-border-strong` | 1px solid `--hfm-color-border-strong` | 区块强调/分隔 |
| `--hfm-border-reader` | 0（无边框）+ 分隔线 | 阅读器正文区 |
| `--hfm-divider` | 1px solid 淡化 border | 列表分隔线 |

---

## 7. BREAKPOINTS（候选，扩展）

| Token | 值 | 用途 |
| --- | --- | --- |
| `--hfm-bp-sm` | 480px | 现行保留 |
| `--hfm-bp-md` | 768px | 现行保留 |
| `--hfm-bp-lg` | 1024px | 现行保留 |
| `--hfm-bp-xl` | 1440px | **新增**：≥1440 内容 max-width 放大档 |
| `--hfm-bp-2xl` | 1920px | **新增**：大屏/展厅预留 |
| `--hfm-content-max` | 1200px（公共）/ 1400px（研究） | 内容容器上限（消除全宽拉伸） |
| `--hfm-reader-max` | 720px（≈ 中文 36 字/行） | 阅读列宽（P6） |

`useViewport` 同步扩展 xl/2xl（UI-12 实施）。

---

## 8. 语义色映射说明（P8 EVIDENCE VISIBLE）

| 语义 | Token | 出现位置（示例） |
| --- | --- | --- |
| Evidence / 来源 | `--hfm-color-evidence` | 人物页"史料证据"、reader 出处行 |
| Citation | `--hfm-color-citation` | 引用块、复制引用按钮 |
| Version | `--hfm-color-citation`（同族）或标签样式 | 版本选择器、版本徽标 |
| 交互 | `--hfm-color-accent` | 链接/按钮 |
| Heritage | `--hfm-color-heritage` | 品牌徽记、年份数字、政校共建署名带 |

---

## 9. 落盘路径（UI-01 实施契约）

1. 在 `tokens.css` 建立 primitive → semantic 两层；保留 `--hfm-*` 语义命名空间兼容现有组件。
2. 新增 `.dark` 语义覆盖（修复审计 §1 暗色失效）。
3. 每个颜色取值过 WCAG 对比度验证并记录（P10）。
4. 新 token 先灰度到 2–3 个页面（Home / Reader / 人物页）视觉验收，再全量替换。
5. 不引入任何新字体文件；仅调整字体栈顺序与角色定义。
6. 本提案的每个候选值在 UI-01 验收时若调整，须回写本文件（保持"候选→定稿"可追溯）。

---

## 10. UI-01 实施记录（2026-09-01，IMPLEMENTED）

- **定稿 HEX**：见 `tokens.css` 头注的 WCAG AA 对比度记录（浅色全部 ≥4.5；暗色全部 ≥4.5；on-accent 双主题 6.44 / 4.77）。
- **已落盘**：`tokens.css`（primitive→semantic→.dark 三层）、`foundations.css`（全局基础：body/标题衬线/链接/焦点环/reduced-motion/reading 类）、`main.ts` 引入、`useViewport` 扩展 xl/2xl（1440/1920）、AuditLog 徽标 token 化（移除硬编码 hex）。
- **定稿调整（回写）**：spacing 保持 N×0.25rem 不变式，大档位 12/16/24/32（§3）；`--hfm-text-sm` 0.875→0.8125rem（13px 元数据）；`--hfm-text-xl` 1.5→1.375rem；`--hfm-radius-lg` 12→10px；新增 `--hfm-space-5` 定义（修复引用未定义缺陷）。
- **验证**：typecheck ✓ · lint 0 errors ✓ · vitest 80/80 ✓ · build ✓ · e2e 10/10（含全断点无溢出 + axe）✓ · 计算样式断言：浅色 body #f7f4ef/#1f1a16/#a0402a、暗色 #16130f/#f2ece1/#cf6a4a（暗色模式真实生效）✓
- **视觉验收面**：首页（浅/暗截图）——人物页/Reader 视觉语言随 UI-04/UI-07 应用本 token 体系。

# HFM 设计 Token v2 — Design Tokens

Status: DESIGN INPUT（现状登记 + 收敛方案，非治理文档）· v2 · 2026-09-16
取代: v1 `CANDIDATE` 提案（浅色方向的候选值，未落盘即被方案六取代）
现行实现: `apps/frontend/src/styles/tokens.css`（194 行）· 首页版式层: `apps/frontend/src/styles/home-scale.css`

---

## 1. 现状：机制保留，值已落盘

v1 提案的**三层架构**已按原样实现，继续沿用：

```
Primitive（原始值） ──► Semantic（语义） ──► 页面 / 组件
--hfm-pr-*              --hfm-color-*
--hfm-font-*            --hfm-text-* · --hfm-leading-* · --hfm-tracking-*
                        --hfm-space-* · --hfm-radius-* · --hfm-shadow-*
```

v1 提案里"CANDIDATE、评审通过前不得写入代码"的限制**已解除**：值于 UI-01 落盘，含实测对比度记录（见 `tokens.css` 头部注释，WCAG 2.1 AA，最低 4.79:1）。

---

## 2. 现行两套语义层

### 2.1 浅色语义层 `--hfm-*`（全站默认）

| 类别 | 取值 |
| :--- | :--- |
| 画布 / 表面 | `--hfm-color-canvas` 暖米白 `#f7f4ef` · `--hfm-color-surface` `#ffffff` |
| 文字 | `text` 墨黑 `#1f1a16` · `secondary` `#4b4238` · `muted` `#6f6557` |
| 强调 | `accent` 低饱和朱砂 `#a0402a` · `heritage` 铜金 `#8a6a2f` |
| 语义 | `evidence` 墨绿 `#2f5d50` · `citation` 靛青 `#4a5a8a` · `danger` / `warning` / `success` |
| 暗色 | `.dark` 作用域覆盖语义层，primitive 不动 |

字号 8 级（12 → 56px）· 行距 3 级（含 `reading` 1.9）· 间距 13 级（4 → 128px）· 圆角 4 级 · 六个字体角色。

### 2.2 展厅语义层 `--wl-*`（首页专用）

| 角色 | 值 | 说明 |
| :--- | :--- | :--- |
| `--wl-deep` | `#070908` | 页面最深处（收尾暗带） |
| `--wl-paper` | `#0f1211` | 画布：近黑，偏墨绿，非纯黑 |
| `--wl-paper-2` | `#161a18` | 抬起面：卡片 / 行 |
| `--wl-light` | `#1e2320` | 展板面：玻璃展板、资料面板 |
| `--wl-ink` | `#efede6` | 主文字：暖白，非纯白 |
| `--wl-ink-2` | `#c9c5ba` | 次要文字 |
| `--wl-mute` | `#8a867c` | 三级：元数据、出处（画布上 ≈5.4:1） |
| `--wl-rule` | `rgba(239,237,230,.14)` | 发丝线 |
| `--wl-mark` | `#c08a4e` | **唯一强调色**：青铜 |
| `--wl-mark-strong` | `#dcab74` | 青铜高亮 |
| `--wl-glow` | `rgba(220,171,116,.08)` | 顶光，极弱 |

`--wl-*` 是**首页专用层**，只被 `components/home/*` 与 `home-scale.css` 使用；站点其余部分不受影响。

---

## 3. 已知缺陷：角色名与现实不符

`--wl-paper` / `--wl-light` 是**角色名**（画布 / 抬起面 / 展板面），沿用自浅色版本以免改动六个组件。在深色展厅下它们描述的是层级位置，**不再描述"纸"**。名字与取值已经脱节。

这是重构期间接受的临时状态，不构成阻碍——但收敛时必须一并改名。

---

## 4. 收敛方案（重构完成后执行）

目标：**一套语义层，两个模式**，而非两套调色板并存。

1. 把 `--wl-*` 的角色提升为语义层的深色取值，命名回归角色（`canvas` / `surface` / `elevated` / `text` / `rule` / `mark`），去掉 `paper` / `light` 这类材质名。
2. 浅色 `--hfm-*` 与展厅 `--wl-*` 合并为一份语义表；组件只引用语义层，不直接引用 primitive。
3. 强调色在全站收敛为**一个**（青铜）。朱砂与铜金在展厅方向下不再各自承担强调职责。
4. 收敛后重跑对比度实测并回写 `tokens.css` 头部记录。

**收敛前不新增任何第三套 token，不新增 token 文件。**

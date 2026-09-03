# 皇甫谧人文数字平台 HFM

HFM（Huangfu Mi Humanities Digital Platform）是面向高校、地方政府、
研究人员、教师、学生及公众建设的皇甫谧数字人文平台。

## 项目定位

本项目不是 HFB 皇甫谧研究平台的直接重构。

HFM 采用：

Architecture Greenfield + Capability Brownfield

即：

- 根据 HFM 客户需求重新设计领域架构；
- 最大化复用 HFB 已验证的数据资产、技术能力和研究成果；
- 不继承 HFB 不必要的历史兼容负担；
- 所有 HFB 能力必须经过 REUSE / EXTEND / ADAPT / DEPRECATE / NEW 裁决后进入 HFM。

## 核心建设方向

- 皇甫谧人物档案
- 皇甫谧著作与古籍
- 针灸历史文化与学术知识
- 非遗数字展示
- 教学辅助
- 专业研究
- 公众文化传播
- 政府与高校共建成果展示

## 当前状态

截至 HEAD `f73c1ad`（2026-09-03），Phase 0 / Phase 1 / Phase 2 均已验收并归档冻结；首页（Homepage）生产保真工作已推进至 WP-04（ACCEPTED / FROZEN）。

- **Phase 0**：COMPLETE / ARCHIVED / FROZEN（Engineering Skeleton · Selective Migration · Core Domain）
- **Phase 1**：COMPLETE — COMPLETION ACCEPTANCE ARCHIVE & FREEZE（Frontier-1…6；P1-00…P1-13）
- **Phase 2**：COMPLETE — COMPLETION ACCEPTANCE ARCHIVE & FREEZE（Completion Baseline `50572a4`）
- **Homepage Step 3**：WP-02 / WP-03 / WP-04 ACCEPTED / FROZEN（WP-04 @ `ab7b978`）
- **下一阶段**：Phase 3 须经独立准入/治理程序另行授权；WP-05 尚未启动

### Phase 0.4 完成详情（2026-08-28，历史事实）

- Architecture Baseline: **Frozen**（`7e109201e250dd5843add2249a24afa699766dd0`）
- Engineering Skeleton: **Frozen**（`5ba7662` 治理链，见 `docs/governance/BASELINE-MANAGEMENT.md`）
- Phase 0.3 Shared Asset Migration: **Complete / Frozen**（`f495fa0`）
- Core Domain Contract: **Accepted / Frozen**（`39b2a91`；v0.1 保持 HISTORICALLY FROZEN）
- Core Domain Contract Amendment v0.2: **Accepted / Frozen**（`6331dee`；28/28 Inventory disposition + 12/12 canonical ownership + CORE-COMPLETION 定义）
- **Core Domain: CD-0…CD-6 Accepted / Frozen**（`e1c33af` `7402ce5` `2288979` `6528ab0` `79cf3f7` `523294a` `7bb6e2e`）
- **CORE-COMPLETION: Accepted / Archived / Frozen**（Candidate `7960fb6`，FINAL VERDICT PASS；失败候选 `e26598f` FAIL 历史保留）
- **Phase 0.4 Completion Baseline: `0167b1702dac13993a5206f63752eafcc8e5387e`**（`docs: freeze phase 0.4 core completion`；DoD 9/9；Inventory 28/28 CLOSED；Completion Evidence CLOSED）
- Actual HFB production import: **NOT performed**（0 records；persistent state NONE）
- CD-7: **Nonexistent**

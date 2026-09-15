# 研究平台宪章 · 第三方审计包

**用途**：交付给独立审计方，用于审定 `HFM-RESEARCH-PLATFORM-CHARTER-v0.2` 是否可以作为研究平台的建设依据。

**送审日期**：2026-09-15
**审计基线**：`main` @ `fefb9ee`

---

## 1. 送审对象

| 文件 | 路径 |
| :--- | :--- |
| **送审方案** | [`../HFM-RESEARCH-PLATFORM-CHARTER-v0.2.md`](../HFM-RESEARCH-PLATFORM-CHARTER-v0.2.md) |
| 变更留档（对照用） | [`../HFM-RESEARCH-PLATFORM-CHARTER-v0.1-DRAFT.md`](../HFM-RESEARCH-PLATFORM-CHARTER-v0.1-DRAFT.md) |

## 2. 本包内容

| 文件 | 作用 | 使用者 |
| :--- | :--- | :--- |
| **`AUDIT-BRIEF.md`** | 审计任务书：范围、必答问题、判据、交付要求 | 审计方 |
| **`EVIDENCE-REGISTER.md`** | 事实底稿：宪章中每条事实断言 + 可复制复现命令 | 审计方 |
| **`BENCHMARK-REFERENCES.md`** | 对标来源与采纳记录 | 审计方 |
| **`AUDIT-REPORT-TEMPLATE.md`** | 审计报告回填模板 | 审计方 |

## 3. 审计方需要具备的能力

1. **数字人文 / 古籍数字化** —— 判断寻址层、标注模型、引证机制是否符合人文学术实践
2. **中文古典文献处理** —— 判断繁简、异体字、通假字对引文校验的影响
3. **系统架构** —— 判断检索层选型（Elasticsearch kNN vs pgvector）与数据模型设计
4. **独立性** —— 不得是本宪章的起草方

## 4. 使用方式

1. 先读 `AUDIT-BRIEF.md`，确认审计范围与必答问题。
2. 用 `EVIDENCE-REGISTER.md` 中的命令**独立复现**每一条事实断言。**不要采信本文档的结论** —— 复现结果与实测值不符的，即为审计发现。
3. 按 `AUDIT-REPORT-TEMPLATE.md` 出具报告。

## 5. 本包不包含什么

- **本包不含法律边界审计。**客户提供资料的权利归属由客户承担责任，已由项目方裁决，**不属于本次审计范围**。详见 `AUDIT-BRIEF.md` 第 6 节。
- 本包不含实现代码。方案尚未进入实现阶段。

## 6. 状态

审计完成并出具报告前，研究平台**不授权任何实现工作**。

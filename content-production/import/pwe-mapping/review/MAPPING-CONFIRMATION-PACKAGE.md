# HFM P/W/E 数据映射确认包说明书 (MAPPING-CONFIRMATION-PACKAGE)

**阶段**：DATA_MAPPING_AND_IMPORT_TOOLING_DESIGN  
**任务编号**：DMIT-02  
**日期**：2026-09-10  
**审查基线与范围**：
- `PERSON`: 17 条全部完成逐条身份、别名、实体底座及唯一性复核；
- `WORK`: 14 条全部完成著作本体、书名别名及类型审查复核；
- `EDITION`: 92 条全部完成文献特征、题名文本、单/多作品排他性及版权证据复核。

---

## 一、审核与确认原则 (Confirmation Principles)

1. **角色解耦原则**：
   - 确认 PERSON 自身客观身份（`PERSON_ID`、`CANONICAL_NAME`、`ALIASES`）与实体底座，不绑定未经终审的复杂人物著作学术角色（`PERSON:WORK` 留存于证据包）。
2. **分类不阻塞实体原则**：
   - 确认 WORK 著作本体存在（如《三都赋序》、《玄晏春秋》），不因次要分类学争鸣（如序言是否归为单独作品、佚书类型未知）阻塞著作基础注册。
3. **证据排他与反证排除原则 (EDITION)**：
   - 87 条高置信记录均经双重校验：
     - ① 题名包含明确经名（82 部含“甲乙”、4 部含“帝王世纪”、1 部含“高士传”）；
     - ② 逐条检查 14 WORK 书名全集，证实**不存在同时匹配两部及以上作品的情况（Multi-match Count = 0）**；
     - ③ 证实版本学特征（五车楼刻本、行素草堂刻本、四库全书本、黄龙祥校本等）与作品唯一吻合。
4. **疑点必 DEFER 原则**：
   - 5 条特殊记录（1 条四书合刊，4 条数字编号）无单一作品排他证据，严格维持 `DEFERRED`，坚决不猜测。
5. **状态流转授权与治理边界**：
   - 本阶段复核输出明确的 `recommendation = CONFIRM_RECOMMENDED`；
   - 基础映射表中的 `review_status` 保持 `REVIEW_REQUIRED`（特殊 4 条为 `DEFERRED`），等待下一 Gate 由治理负责人统一签署确认。

---

## 二、确认包复核结果统计矩阵

| 实体族 (Family) | 评估总数 (Total) | 推荐确认 (Confirm Rec.) | 仍需审查 (Review Req.) | 推荐延后 (Defer Rec.) | 推荐否决 (Reject Rec.) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **PERSON** | 17 | **17** (100%) | 0 | 0 | 0 |
| **WORK** | 14 | **14** (100%) | 0 | 0 | 0 |
| **EDITION** | 92 | **87** (94.6%) | 0 | **5** (5.4%) | 0 |

---

## 三、各审查产物关联索引

1. **人物复核明细表**：
   [`PERSON-CONFIRMATION-REVIEW.csv`](file:///users/likeming/sites/hfm/content-production/import/pwe-mapping/review/PERSON-CONFIRMATION-REVIEW.csv)
   包含 17 位人物的稳定标识、出处、别名、证据溯源及无碰撞结论。
2. **著作复核明细表**：
   [`WORK-CONFIRMATION-REVIEW.csv`](file:///users/likeming/sites/hfm/content-production/import/pwe-mapping/review/WORK-CONFIRMATION-REVIEW.csv)
   包含 14 部著作的本体依据、类型审查诊断及非阻塞性结论。
3. **版本复核明细表**：
   [`EDITION-CONFIRMATION-REVIEW.csv`](file:///users/likeming/sites/hfm/content-production/import/pwe-mapping/review/EDITION-CONFIRMATION-REVIEW.csv)
   包含 92 个版本的唯一匹配证据、候选作品、歧义度与分流处理。
4. **人工签批专单**：
   [`HUMAN-DECISION-SHEET.md`](file:///users/likeming/sites/hfm/content-production/import/pwe-mapping/review/HUMAN-DECISION-SHEET.md)
   针对 A000541 与 A000529~A000532 的专案复核意见与签批表格。

---

## 四、关于导入工具设计 (Import Tooling Design) 并行启动的判定

**裁决结论**：
```
IMPORT_TOOLING_DESIGN_CAN_START = YES
```

**理由与治理边界**：
1. **输入契约与数据结构已绝对冻结**：
   - 映射架构通过了实测与证据复核：17 Person、14 Work、87 Edition 形成了确定性无歧义的输入集；
   - 实体底座（`01-entity-bootstrap.csv`，31 实体）结构完全确立；
   - 契约规则明确冻结：`IMPORTER_CONSUMES_ONLY_CONFIRMED_ROWS = YES`。
2. **工程实现与数据确认解耦**：
   - 导入工具的代码设计与单元测试（在 scratch 内存库或临时环境中测试解析、事务回滚、外键完整性校验）可以即刻并行开展；
   - 工具设计本身不写入生产数据库，不执行生产导入；
   - 工具将内置状态过滤器，天然保障未签批（`REVIEW_REQUIRED`/`DEFERRED`）记录无法进入生产库。

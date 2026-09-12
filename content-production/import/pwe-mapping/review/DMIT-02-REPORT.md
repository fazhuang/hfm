# HFM P/W/E Mapping Confirmation Review 报告

**阶段**：DATA_MAPPING_AND_IMPORT_TOOLING_DESIGN  
**任务编号**：DMIT-02  
**日期**：2026-09-10  
**审查基线**：
- `MAPPING_CONTRACT_COMPLETE=YES`
- `IMPORTER_CONSUMES_ONLY_CONFIRMED_ROWS=YES`
- `DOCUMENT_BASELINE=675` (PROTECTED)
- `GOVERNANCE`: 本轮只复核证据并生成确认包，禁止修改代码、禁止修改 schema、禁止写库、禁止导入。

---

## 一、PERSON 17 条逐条复核

在 [`PERSON-CONFIRMATION-REVIEW.csv`](file:///users/likeming/sites/hfm/content-production/import/pwe-mapping/review/PERSON-CONFIRMATION-REVIEW.csv) 中完成逐条身份、别名、重名碰撞及实体底座复核：
1. **身份独立性与唯一性**：全部 17 位人物的 `PERSON_ID`、`CANONICAL_NAME` 在集合内唯一，无任何同名碰撞；
2. **溯源完整性**：17 条均具备明确规划文档、论文语料、正史记载或出版著录来源；
3. **实体底座对应**：17 条均在 `01-entity-bootstrap.csv` 中具备确定性的 `ENT-PERSON-*` 映射，满足 `persons.entity_id` 强外键要求；
4. **角色解耦判定**：严格遵循“人物本体身份确认与人物-著作学术角色解耦”原则。所有 17 条基础人物对象均判定为无歧义；
5. **复核建议**：`PERSON_CONFIRM_RECOMMENDED = 17`，`PERSON_REVIEW_REQUIRED = 0`，`PERSON_REJECT_RECOMMENDED = 0`。

---

## 二、WORK 14 条逐条复核与类型审查

在 [`WORK-CONFIRMATION-REVIEW.csv`](file:///users/likeming/sites/hfm/content-production/import/pwe-mapping/review/WORK-CONFIRMATION-REVIEW.csv) 中完成逐条著作本体及类型审查（WORK_TYPE_REVIEW）：
1. **著作本体明确性**：14 部著作在领域内均为独立明确的智力创作成果或文献集成物；
2. **分类争议非阻塞判定**：
   - 《三都赋序》（`WORK-SANDUFUXU`）：虽在文学史上存在皇甫谧撰或左思自托之争议，但该序言作为一篇独立传世文献作品的本体客观存在，学术争议属于篇目归属角色范畴，不阻塞 WORK 自身建立；
   - 《玄晏春秋》（`WORK-XUANYANCHUNQIU`）：虽现有语料直接文本未全，分类暂列 `UNKNOWN`，但作为晋唐书目著录的历史著作本体明确，类型待定不阻塞 R0 基础实体建立；
   - 经审查，**WORK_TYPE 争议对 R0 基础著作身份的阻塞数为 0**（`WORK_TYPE_BLOCKING_COUNT = 0`）；
3. **复核建议**：`WORK_CONFIRM_RECOMMENDED = 14`，`WORK_REVIEW_REQUIRED = 0`，`WORK_REJECT_RECOMMENDED = 0`。

---

## 三、EDITION 87 条高置信记录排他性复核

在 [`EDITION-CONFIRMATION-REVIEW.csv`](file:///users/likeming/sites/hfm/content-production/import/pwe-mapping/review/EDITION-CONFIRMATION-REVIEW.csv) 中对全部 87 条 `HIGH` 记录进行了严格排他校验：
1. **反证排除检查**：
   - 87 部版本的题名与文件名文本与 14 部候选 WORK 书名进行全量交叉匹配，**跨作品多重匹配数（Multi-match Count）为 0**；
   - 82 部包含“甲乙”，唯一对应 `WORK-JIAYI`；
   - 4 部包含“帝王世纪”，唯一对应 `WORK-DIWANG-SHIJI`；
   - 1 部包含“高士传”，唯一对应 `WORK-GAOSHIZHUAN`；
2. **版本源流真实性**：
   - 87 部记录中包含明万历吴勉学五车楼刻本、清光绪行素草堂刻本、清乾隆四库全书本、黄龙祥新校本等，其文献源流与各自所属著作完全闭合吻合；
3. **复核建议**：87 条记录具备充分、唯一且排他的文献证据，`EDITION_CONFIRM_RECOMMENDED = 87`。

---

## 四、5 条特殊记录人工审查与裁决维持

在 [`HUMAN-DECISION-SHEET.md`](file:///users/likeming/sites/hfm/content-production/import/pwe-mapping/review/HUMAN-DECISION-SHEET.md) 中完成深度立案：
1. **A000541**：四书合刊文献（包含甲乙经、伤寒论、金匮要略、温病学），在当前 R0 单作品外键约束下强行归属会导致学术失真，**复核建议维持 `DEFERRED`**；
2. **A000529 ~ A000532**：4 部纯数字编号扫描件，缺乏文本著录与版权页证据，严格遵守治理红线，坚决不猜测，**复核建议维持 `DEFERRED`**；
3. **资产保护确认**：上述 5 条记录对应的 `DOC-HFM-A000541`、`DOC-HFM-A000529~532` 已在生产库 675 基线中安全持久化，其版本挂接的延后处理对底层物理文献资产零影响。

---

## 五、导入工具设计 (Import Tooling Design) 启动判定

- **判定结果**：`IMPORT_TOOLING_DESIGN_CAN_START = YES`。
- **架构支撑**：
  - 经本次复核，PERSON 17 条、WORK 14 条、EDITION 87 条形成了 100% 闭合、零外键悬挂的候选导入集合；
  - 契约 `IMPORTER_CONSUMES_ONLY_CONFIRMED_ROWS = YES` 已明确固化，导入器逻辑可直接根据 `review_status == 'CONFIRMED'` 设计过滤防护网；
  - 工具开发与离线测试可以在 scratch 临时环境中并行开展，绝不触碰生产库。

---

## 六、报告汇总指标

```yaml
PERSON_TOTAL: 17
PERSON_CONFIRM_RECOMMENDED: 17
PERSON_REVIEW_REQUIRED: 0
PERSON_REJECT_RECOMMENDED: 0

WORK_TOTAL: 14
WORK_CONFIRM_RECOMMENDED: 14
WORK_REVIEW_REQUIRED: 0
WORK_REJECT_RECOMMENDED: 0
WORK_TYPE_BLOCKING_COUNT: 0

EDITION_TOTAL: 92
EDITION_CONFIRM_RECOMMENDED: 87
EDITION_REVIEW_REQUIRED: 0
EDITION_DEFER_RECOMMENDED: 5
EDITION_REJECT_RECOMMENDED: 0

A000541_RECOMMENDATION: DEFER_RECOMMENDED
A000529_RECOMMENDATION: DEFER_RECOMMENDED
A000530_RECOMMENDATION: DEFER_RECOMMENDED
A000531_RECOMMENDATION: DEFER_RECOMMENDED
A000532_RECOMMENDATION: DEFER_RECOMMENDED

IDENTITY_COLLISIONS: 0
MAPPING_AMBIGUITIES: 0 (在排除5条DEFER后)

IMPORT_TOOLING_DESIGN_CAN_START: YES

MAPPING_READY_FOR_ACCEPTANCE: YES

NEXT_RECOMMENDED_ACTION: "人工审阅 HUMAN-DECISION-SHEET.md 并对 17 Person / 14 Work / 87 Edition 执行最终签署授权；同时可启动导入工具的架构设计与离线验证"
BLOCKER: NONE
STOP: YES
```

# HFM-KNOWLEDGE-MODEL-REALITY.md — 《针灸甲乙经》知识模型与结构化现状

## 1. 维度状态核对表

| 知识对象维度 | MODELLED (数据模型设计) | API_EXPOSED (后端接口暴露) | UI_EXPOSED (前端界面展示) | DATA_POPULATED (数据完全填充) | 说明 |
|---|---|---|---|---|---|
| **卷 (Juan)** | YES (`Chapter.juan_number`) | YES (`/works/{id}/structure`) | YES (`JiayiView.vue`) | YES (12卷目录具备) | 前端静态与数据表均支持卷定义 |
| **篇 (Pian)** | YES (`Chapter.title`) | YES (`/works/{id}/structure`) | YES (`JiayiView.vue`) | YES (128篇完整篇名) | 结构清晰展示于《针灸甲乙经》专页 |
| **条文 (Passage)** | YES (`Passage.content`) | YES (`/reader/resolve`) | YES (`ReaderDocView.vue`) | PARTIAL | 读者系统当前精选了“后论”、“其传”条文，全书万条条文未全入库 |
| **穴位 (Acupoint)** | YES (`CDomainTerm.category='acupoint'`) | YES (`/c-terms/{id}`) | YES (首页知识图谱、检索卡片) | PARTIAL | 包含典型穴位定义，全量 349 穴未逐条录入 |
| **经络 (Meridian)** | YES (`CDomainTerm.category='meridian'`) | YES (`/c-terms/{id}`) | YES (首页知识展示) | PARTIAL | 仅构建核心经络分类与概念卡 |
| **病候 (Symptom)** | YES (`CDomainTerm.category='symptom'`) | YES (`/c-terms/{id}`) | YES (检索分面) | PARTIAL | 概念已定义，未建立全量主治矩阵 |
| **引用与证据链** | YES (`Citation`, `Evidence`) | YES (`/evidence-chain/{id}`) | YES (`EvidenceExplorer.vue`) | YES (12条高质量学术引文已挂接) | 结构化证据链在研究视图中可展开溯源 |

---

## 2. 结论

《针灸甲乙经》的**知识模型框架在软件层面已经完整构建**（包含了卷、篇、条文、术语、关系、引用链），前端专页已能够向公众呈现其完整的典籍体系与版本流变；但**知识库深加工填充率仍处于精选样本与框架阶段**，后续需要文献学专业人员进行整书数字化灌库。

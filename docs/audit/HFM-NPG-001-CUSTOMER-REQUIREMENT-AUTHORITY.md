# HFM NPG-1 — Customer Requirement Authority

Date: 2026-08-29
Authority source: client-confirmed requirements embedded in the NPG-0…NPG-5 audit instruction
Baseline context: `0167b1702dac13993a5206f63752eafcc8e5387e`

## 1. Authority rules

- **L1** — explicitly confirmed by the client in this task.
- **L2** — unavoidable implication of an L1 requirement, without fixing the implementation.
- **L3** — product, design, delivery, or technical proposal; not a customer fact.
- Disposition is one of **REQUIRED**, **DEFERRED**, **REJECTED**, **UNRESOLVED**.

Repository documents and AI proposals cannot elevate themselves above this register.

## 2. Requirement matrix

| REQ-ID | Source | Original Requirement | Requirement Type | Authority Level | Actor | Business Goal | Acceptance Relevance | Scope Implication | Evidence Needed | Ambiguity | Disposition | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CR-001 | Client §III.1 | 甘肃医学院与灵台县政府联合建设 | Stakeholder | L1 | 两建设方 | 明确项目主体 | 项目署名、治理、验收主体 | 双方责任边界须后续确认 | 联合建设文件、联系人、审批链 | 责任分工未给出 | REQUIRED | 不推导采购或运营主体 |
| CR-002 | Client §III.2 | 服务甘肃医学院皇甫谧学院 | Audience | L1 | 学院师生、研究人员 | 教学与研究 | 校内研究后台必须服务该机构 | 需要机构、人员与访问场景清单 | 组织证明、角色清单、使用流程 | 具体用户数未知 | REQUIRED | 不自动等于现有 HFB 角色模型 |
| CR-003 | Client §III.2 | 服务灵台县皇甫谧中医针灸传承创新示范中心 | Audience | L1 | 示范中心人员、参观者 | 文化展示与传承 | 正式名称、内容与展示场景 | 需中心内容责任人与发布审批 | 机构正式文件、名称证据 | 运营权限未知 | REQUIRED | 正式名称不可被简称替代 |
| CR-004 | Client §III.3 | 深度挖掘皇甫谧中医药文化 | Business goal | L1 | 研究者、参观者 | 文化研究与传播 | 人物、作品、思想内容可追溯 | 需史料、主张、证据与编辑流程 | 来源目录、证据定位、审校记录 | “深度”验收尺度未知 | REQUIRED | 不等于必须上知识图谱 |
| CR-005 | Client §III.3 | 传承弘扬皇甫谧针灸技艺 | Business goal | L1 | 参观者、学生、研究者 | 非遗与教学传播 | 内容须准确且非临床建议 | 需历史医学边界与内容审核 | 非遗依据、传承资料、医学审校 | 可展示到何种操作深度未知 | REQUIRED | 不授权虚拟临床实训 |
| CR-006 | Client §III.3 | 展示皇甫谧文化及针灸传承脉络 | Business goal | L1 | 参观者 | 形成可理解的传承叙事 | 传承节点必须有来源 | 需要人物、机构、事件、关系证据 | 谱系表、节点证据、争议说明 | 完整谱系未知 | REQUIRED | “谱系展示”不指定 Neo4j/D3 |
| CR-007 | Client §III.3 | 汇聚皇甫谧文化及《针灸甲乙经》研究成果 | Content goal | L1 | 研究者 | 研究成果聚合 | 文献元数据、来源、权限可核验 | 需要研究成果目录和准入标准 | 书目、全文权利、来源与版本 | “汇聚”是否含全文未知 | REQUIRED | 元数据与全文必须分开验收 |
| CR-008 | Client §III.3 | 服务学校特色课程教学 | Teaching goal | L1 | 学生、教师 | 教学支撑 | 教学使用场景与材料可复现 | 需课程、教师、学习任务清单 | 课程大纲、教学包、引用版本 | 课程与年级未知 | REQUIRED | 不自动要求 LMS 或智能推荐 |
| CR-009 | Client §III.3 | 服务中医药文化研究 | Research goal | L1 | 研究者 | 学术研究 | 研究数据与证据链可追溯 | 需要研究工作流与数据访问边界 | 研究任务、产出、审查要求 | 具体方法未知 | REQUIRED | 不等于临床研究系统 |
| CR-010 | Client §III.4 | 用户优先级：参观者 > 研究者 > 学生 | Priority | L1 | 三类用户 | 决定产品排序 | Scope 排序必须体现优先级 | 公开门户价值优先于复杂后台扩展 | 典型旅程、流量和设备场景 | 管理员等支撑角色未排序 | REQUIRED | 不是权限等级排序 |
| CR-011 | Client §III.5 | 客户已有《针灸甲乙经》版本 | Content asset | L1 | 内容提供方 | 版本展示、阅读、研究 | 必须盘点具体版本与状态 | 版本、载体、数字化与权利需逐件登记 | 资产清单、文件、书目信息、授权 | 数量和数字化状态未知 | REQUIRED | “拥有”不证明已交付仓库 |
| CR-012 | Client §III.5 | 客户已有皇甫谧史料 | Content asset | L1 | 内容提供方 | 人物档案 | 事件和主张须证据化 | 需原始史料目录与页码级定位 | 原件/影印、书目、证据定位 | 完整度未知 | REQUIRED | 仓库静态叙述不是替代证据 |
| CR-013 | Client §III.5 | 客户已有非遗证书 | Content asset | L1 | 示范中心 | 非遗权威展示 | 项目名称、级别、编号必须可核 | 需证书数字化和公开条件 | 扫描件、颁发机构、编号、授权 | 正式项目名称和级别未知 | REQUIRED | 本轮仓库未找到证书文件 |
| CR-014 | Client §III.5 | 客户已有传承人资料 | Content asset | L1 | 传承人、中心 | 传承谱系 | 身份、关系与发布授权须核验 | 需人物主数据、谱系证据、隐私授权 | 名单、履历、关系依据、同意书 | 完整性与授权未知 | REQUIRED | 不自动公开个人信息 |
| CR-015 | Client §III.5 | 客户已有校园活动照片 | Content asset | L1 | 学校、参与者 | 教学活动展示 | 图片权利与肖像授权必须可核 | 需媒体元数据和展示许可 | 原图、拍摄者、时间地点、授权 | 数量、质量、肖像权未知 | REQUIRED | HFM 当前无媒体发布模型 |
| CR-016 | Client §III.6 | 正式机构名称为“灵台县皇甫谧中医针灸传承创新示范中心” | Naming | L1 | 示范中心 | 官方识别 | 所有正式署名必须精确 | 需作为 canonical organization name | 正式文件或盖章材料 | 无 | REQUIRED | 不据常识改写 |
| CR-017 | Client §III.6 | “皇甫谧针灸非遗传承中心”仅作非正式简称/业务表述 | Naming boundary | L1 | 全体用户 | 防止机构误称 | 正式与显示别名须分离 | 数据模型需可区分 canonical name 和 alias | 内容规范、页面文案验收 | 别名使用场景未列举 | REQUIRED | 不得作为注册实体名 |
| CR-018 | Client §III.7 | 3D 人物为远期设想，非当前必验收 | Scope boundary | L1 | 参观者 | 远期沉浸体验 | 当前验收不得阻塞于此 | 当前 Scope 排除 | 未来独立需求与资产 | 未来形式未知 | DEFERRED | 不等于永久拒绝 |
| CR-019 | Client §III.7 | VR 展厅为远期设想，非当前必验收 | Scope boundary | L1 | 参观者 | 远期展陈 | 当前验收不得包含 | 当前 Scope 排除 | 未来场馆、设备与内容需求 | 设备未知 | DEFERRED | WebXR 也未被授权 |
| CR-020 | Client §III.7 | 虚拟针灸实训为远期设想，非当前必验收 | Scope and safety | L1 | 学生 | 远期教学 | 当前验收排除，未来需医学安全审查 | 不进入当前产品边界 | 教学目标、审校、安全责任 | 与临床训练边界未知 | DEFERRED | 高风险，不可由展示需求推导 |
| CR-021 | Client §III.8 | 公开互联网门户 + 校内研究后台双层架构 | Architecture requirement | L1 | 参观者、研究者、学生 | 公共传播与研究生产分离 | 两个表面必须分别验收 | 至少逻辑分层；物理部署待决定 | 两层用户旅程、内容流、权限与发布契约 | 物理拆分方式未知 | REQUIRED | 不等于必须两个仓库或两个数据库 |
| CR-022 | Client §III.9 | HFB/HFM 能力是否复用尚未决定，须逐项裁决 | Governance | L1 | 项目治理方 | 控制迁移风险 | 复用仅能是 candidate | 需资产级价值、耦合、成本、风险矩阵 | 固定快照、测试、许可、数据权属 | 最终裁决未授权 | UNRESOLVED | HFB 存在 ≠ HFM 必须复用 |
| DR-001 | L1 CR-010/021 | 公开门户需支持无需校内研究账户即可消费获准公开内容 | Access implication | L2 | 参观者 | 公开互联网服务 | 需定义匿名访问与公开内容边界 | 匿名只读面与后台授权面分离 | 访客旅程、公开 API/页面策略 | 是否允许账户增强未知 | REQUIRED | 不固定 JWT/Cookie 方案 |
| DR-002 | L1 CR-021 | 研究后台必须有与公开门户不同的写入、审核和可见性边界 | Governance implication | L2 | 研究者、编辑者 | 防止研究态直接公开 | 发布前需审校与隔离 | 需要研究态到公开态的明确契约 | 角色、状态、审批与撤回规则 | 具体 SoD 未确认 | REQUIRED | 不自动复用 HFB RBAC |
| DR-003 | L1 CR-011…015/021 | 客户内容公开前必须完成来源、权利和授权登记 | Compliance implication | L2 | 内容责任人 | 合法、可信发布 | 无权利证据不得公开全文/图片 | 需要资产准入与发布状态 | 授权书、许可、来源、撤回联系人 | 地方政策与合同未知 | REQUIRED | 未知权利资产仅能保守处理 |
| TP-001 | Gemini/technical option | Neo4j | Technology | L3 | 技术团队 | 图关系存储选项 | 非验收条件 | 仅在关系规模/查询证明后决策 | 负载、查询、运维成本 | 未决 | UNRESOLVED | HFM Core 明确列为 future option |
| TP-002 | Gemini/technical option | Elasticsearch | Technology | L3 | 技术团队 | 搜索扩展选项 | 非 L1 | 先定义检索规模与语言需求 | 索引规模、相关性、SLA | 未决 | UNRESOLVED | 不能由“全文检索”直接锁定 |
| TP-003 | Gemini/technical option | MinIO | Technology | L3 | 技术团队 | 对象存储选项 | 非 L1 | 媒体需求确定后选型 | 容量、备份、访问控制、运维 | 未决 | UNRESOLVED | “有图片/证书”只推导对象存储能力，不推导 MinIO |
| TP-004 | Gemini/technical option | Three.js | Technology | L3 | 技术团队 | 3D 渲染选项 | 当前非验收项 | 与 CR-018 一并延期 | 3D 资产、设备、性能与无障碍要求 | 未决 | DEFERRED | 不提升为当前要求 |
| TP-005 | Gemini/technical option | WebXR | Technology | L3 | 技术团队 | XR 交互选项 | 当前非验收项 | 与 CR-019/020 一并延期 | 设备矩阵、安全与替代体验 | 未决 | DEFERRED | 不提升为当前要求 |
| TP-006 | Gemini/technical option | WebSocket | Technology | L3 | 技术团队 | 实时通信选项 | 非 L1 | 只有实时协作/流式状态被确认才评估 | 并发、时延、断线恢复需求 | 未决 | UNRESOLVED | 普通页面不需要自动引入 |
| TP-007 | Gemini/technical option | ECharts | Technology | L3 | 技术团队 | 可视化选项 | 非 L1 | 按图表需求和既有依赖裁决 | 图表清单、无障碍、许可 | 未决 | UNRESOLVED | 传承谱系不必然使用图表库 |
| TP-008 | Gemini/technical option | D3.js | Technology | L3 | 技术团队 | 自定义可视化选项 | 非 L1 | 复杂定制可视化成立后评估 | 交互复杂度、维护成本 | 未决 | UNRESOLVED | 不与 ECharts 同时默认引入 |
| TP-009 | Gemini/technical option | 具体数据库表设计 | Detailed design | L3 | 技术团队 | 实现数据模型 | 非客户验收事实 | 须由权威域模型与用例驱动 | 字段、约束、迁移与权利模型 | 未决 | UNRESOLVED | Phase 1 schema 未授权 |
| TP-010 | Gemini estimate | 8 周工期 | Delivery estimate | L3 | 项目管理 | 排期 | 未获客户确认 | 需在资产盘点和 Scope 裁决后估算 | 人员、内容规模、验收和依赖 | 高 | UNRESOLVED | 不是需求 |
| TP-011 | Gemini product idea | “按病智能推荐主配穴” | Medical product proposal | L3 | 潜在学习者/患者 | 未确认 | 与当前数字人文定位冲突 | 治疗建议语义当前排除 | 医疗器械/互联网诊疗合规、临床责任、医学验证 | 极高 | REJECTED | 仅可另案讨论历史文献检索，不得输出临床建议 |

## 3. Authority finding

The L1 layer confirms stakeholders, audiences, goals, five content-asset families, user priority, the official organization name, the two-layer product direction, and explicit deferral of immersive functions. It does **not** confirm a database product, visualization library, real-time protocol, delivery duration, or clinical recommendation feature.

## 4. Open client decisions

1. Joint-governance ownership and final approvers.
2. Concrete visitor/researcher/student journeys and acceptance metrics.
3. Exact asset quantities, formats, digitization state, provenance, and rights.
4. Public editorial workflow, withdrawal policy, and research-to-public handoff.
5. Asset-by-asset HFB reuse decisions after the NPG-4 candidates are reviewed.

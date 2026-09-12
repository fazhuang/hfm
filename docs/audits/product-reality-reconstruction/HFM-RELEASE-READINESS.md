# HFM-RELEASE-READINESS.md — 最终发布就绪度事实判定

各就绪度维度独立裁决，不进行单一模糊的 PASS/FAIL 合并：

| 就绪度维度 | 状态判定 | 判定事实依据与证据 |
|---|---|---|
| **LOCAL_DEVELOPMENT_RUNTIME_READY** | **READY (就绪)** | Vite (5173) 与 Uvicorn (8000) 可秒级启动，前后端通信与降级兜底完备 |
| **LOCAL_ACCEPTANCE_READY** | **READY (就绪)** | 682 后端 pytest + 235 前端 vitest + 51 运维脚本测试实测 100% 通过 |
| **PUBLIC_PORTAL_READY** | **READY (就绪)** | 8 个首页板块、人物详情、甲乙经典籍、非遗名录、读者文献均完整呈现 |
| **RESEARCH_WORKSPACE_READY** | **PARTIAL (部分就绪)** | 鉴权/RBAC/高密检索/导出就绪；在线创建项目/笔记表单缺失 |
| **DATA_READY** | **PARTIAL (部分就绪)** | 核心生平纪年、典籍版本、非遗传承人数据就绪；全量论文与全书穴位未灌库 |
| **DEPLOYMENT_CONTRACT_READY** | **READY (就绪)** | 严苛验证器、初始化脚本、Nginx/Systemd 模版完备且有独立测试保障 |
| **PRODUCTION_ENVIRONMENT_READY** | **PENDING (待实际生产机提供)** | 代码与自动化脚本就绪，等待最终客户提供生产服务器、域名与公网 DB |
| **FINAL_CUSTOMER_DELIVERY_READY** | **SUBSTANTIALLY_READY (实质就绪)** | 具备向客户展示和交付完整学术数字门户的能力，明确标注二期深加工路线 |

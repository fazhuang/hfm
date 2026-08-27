# HFM Infra（骨架阶段）

本目录保留 HFM 基础设施的设计空间。按 Frozen Technical Baseline（`docs/architecture/HFM-TECHNOLOGY-BASELINE.md`）：

- **PostgreSQL**：JUSTIFIED — Phase 1 引入（本阶段无数据库）。
- **Elasticsearch / Redis / MinIO**：JUSTIFIED_WITH_CONDITIONS — 仅在目标需求或实测规模证明需要时引入；**不得**要求开发者为 `pnpm test` / 后端测试 / 前端构建启动这些服务。
- **Observability**：UNKNOWN / TO BE DECIDED — 本阶段仅使用基础 application logging；不引入 Prometheus / Grafana / OpenTelemetry / ELK / Loki / Sentry。

## Compose Profile 设计空间

未来如需要本地依赖，将以 Docker Compose **profile**（opt-in）方式提供（例如 `--profile infra`），默认 profile 为空，保证零依赖可运行。本阶段不创建 compose 文件。

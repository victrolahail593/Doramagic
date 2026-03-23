# Doramagic Race Brief

- Round: 5
- Module: `apps.preextract-api.read`
- Racer: Gemini (s3-gemini)
- Source Spec: `/Users/tang/Documents/vibecoding/Doramagic/docs/dev-plan-codex-module-specs.md`

## 模块职责

一句话职责：基于 FastAPI 提供只读 API，按领域查询预提取的知识快照（bricks/atoms/truth/deprecations/health）。

## 输入 Schema

#### 2.1 数据来源

API 不接收管线输入。它读取 snapshot_builder 写入磁盘的快照文件：

```
data/snapshots/
  {domain_id}/
    DOMAIN_BRICKS.json
    DOMAIN_TRUTH.md
    atoms.parquet        (可选)
    domain_map.sqlite    (可选)
    snapshot_manifest.json
```

#### 2.2 服务配置

```python
class ApiReadConfig(BaseModel):
    data_dir: str = "data/snapshots"
    host: str = "0.0.0.0"
    port: int = Field(default=8420, ge=1, le=65535)
    cors_origins: list[str] = ["*"]
```

可通过环境变量 `DORAMAGIC_API_DATA_DIR` 和 `DORAMAGIC_API_PORT` 覆盖。

## 输出 Schema

#### 3.1 端点与响应模型

| 端点 | 方法 | 响应模型 | 描述 |
|------|------|----------|------|
| `/domains` | GET | `DomainListResponse` | 列出已预提取的领域 |
| `/domains/{id}/bricks` | GET | `DomainBricksResponse` | 获取领域积木 |
| `/domains/{id}/truth` | GET | `DomainTruthResponse` | 获取领域真相 markdown |
| `/domains/{id}/atoms` | GET | `AtomQueryResponse` | 查询知识原子（支持过滤/分页） |
| `/domains/{id}/deprecations` | GET | `DeprecationListResponse` | 获取废弃事件 |
| `/domains/{id}/health/{project}` | GET | `HealthCheckResponse` | 项目体检 |
| `/health` | GET | `{"status": "ok"}` | 服务健康检查 |

```python
class DomainListItem(BaseModel):
    domain_id: str
    display_name: str
    project_count: int
    brick_count: int
    snapshot_version: str
    last_updated: str

class DomainListResponse(BaseModel):
    domains: list[DomainListItem]
    total_count: int

class DomainBricksResponse(BaseModel):
    domain_id: str
    snapshot_version: str
    bricks: list[DomainBrick]
    total_count: int

class DomainTruthResponse(BaseModel):
    domain_id: str
    snapshot_version: str
    truth_md: str

class AtomQueryParams(BaseModel):
    knowledge_type: KnowledgeType | None = None
    confidence_min: Confidence | None = None
    keyword: str | None = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

class AtomQueryResponse(BaseModel):
    domain_id: str
    snapshot_version: str
    atoms: list[KnowledgeAtom]
    total_count: int
    has_more: bool = False

class DeprecationListResponse(BaseModel):
    domain_id: str
    deprecations: list[DeprecationEvent]
    total_count: int

class HealthCheckResponse(BaseModel):
    domain_id: str
    project_id: str
    snapshot_version: str
    overall_status: Literal["healthy", "stale", "drifted", "unknown"]
    health_md: str
    brick_coverage: float
    stale_brick_count: int
```

#### 3.2 输出消费者

- Doramagic 终端（Phase A/B 注入 domain bricks）
- 用户直接调用（curl / 浏览器 / 前端）

## 验收标准

必须通过的测试用例：

1. 给定 Sim2 卡路里快照目录，`GET /domains` 返回包含 "calorie-tracking" 的列表。
2. `GET /domains/calorie-tracking/bricks` 返回至少 1 个 DomainBrick。
3. `GET /domains/calorie-tracking/truth` 返回非空 markdown。
4. `GET /domains/nonexistent/bricks` 返回 HTTP 404。
5. `GET /domains/calorie-tracking/atoms?knowledge_type=capability` 只返回 capability 类型。
6. `GET /health` 返回 `{"status": "ok"}`。

性能预期：

- 启动时间 < 3 秒
- 单个查询 < 100ms（本地数据）

不允许的行为：

- 修改 snapshot 文件
- 在查询端点中调用 LLM
- 缺少 CORS 配置
- 不处理 domain_id 不存在的情况

## 设计自由度

可自由发挥：

- FastAPI 路由组织方式（单文件 / router 拆分）
- 数据加载策略（全量内存 / 按需读取）
- atoms 过滤实现（内存筛选 / SQLite 查询）
- 额外的管理端点

必须严格遵守：

- 7 个端点的路径和响应模型
- HTTP 404 / 500 错误格式
- 只读语义
- CORS 开启

## Fixture 路径

- `data/fixtures/platform_rules.json`
- `data/fixtures/sim2_discovery_result.json`
- `data/fixtures/sim2_need_profile.json`
- `data/fixtures/sim2_repo_facts_calorie.json`
- `data/fixtures/sim2_snapshot_input.json`
- `data/fixtures/sim2_stage1_output_calorie.json`
- `data/fixtures/sim3_need_profile_flight.json`
- `data/fixtures/snapshots/calorie-tracking/DOMAIN_BRICKS.json`
- `data/fixtures/snapshots/calorie-tracking/DOMAIN_TRUTH.md`
- `data/fixtures/snapshots/calorie-tracking/snapshot_manifest.json`

## 交付清单

1. 模块代码
2. 单元测试
3. 至少 1 条基于 Sim2 或等价 fixture 的集成测试
4. `README.md`
5. `DECISIONS.md`

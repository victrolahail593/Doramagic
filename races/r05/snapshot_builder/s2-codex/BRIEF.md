# Doramagic Race Brief

- Round: 5
- Module: `domain-graph.snapshot_builder`
- Racer: Codex (s2-codex)
- Source Spec: `/Users/tang/Documents/vibecoding/Doramagic/docs/dev-plan-codex-module-specs.md`

## 模块职责

一句话职责：将多个项目的 fingerprint、compare 信号和 synthesis 结论聚合为一份领域知识快照（Domain Bricks + Atom Clusters + DOMAIN_TRUTH.md），供 API 存储和终端注入使用。

## 输入 Schema

#### 2.1 输入模型

```python
class SnapshotConfig(BaseModel):
    output_dir: str | None = None
    include_parquet: bool = True
    include_sqlite: bool = True
    min_support_for_brick: int = Field(default=2, ge=1)
    cluster_similarity_threshold: float = Field(default=0.75, ge=0, le=1)

class SnapshotBuilderInput(BaseModel):
    schema_version: str = "dm.snapshot-builder-input.v1"
    domain_id: str
    domain_display_name: str = ""
    fingerprints: list          # list[ProjectFingerprint]
    compare_output: dict        # CompareOutput 字典
    synthesis_report: dict      # SynthesisReportData 字典
    community_knowledge: dict = {}  # CommunityKnowledge 字典
    config: SnapshotConfig = SnapshotConfig()
```

说明：

- `fingerprints`、`compare_output`、`synthesis_report` 来自上游 phase_runner 的中间产物
- `community_knowledge` 来自 Phase D，可为空
- 使用 `dict` 而非强类型是为了避免循环导入，运行时用 Pydantic 验证

#### 2.2 输入来源

- phase_runner 输出目录下的 `project_fingerprint.json`、`comparison_result.json`、`synthesis_report.json`、`community_knowledge.json`
- 或手工构造（离线预提取场景）

#### 2.3 输入示例

```json
{
  "schema_version": "dm.snapshot-builder-input.v1",
  "domain_id": "calorie-tracking",
  "domain_display_name": "卡路里追踪",
  "fingerprints": ["... ProjectFingerprint 列表 ..."],
  "compare_output": {"domain_id": "calorie-tracking", "signals": ["..."], "metrics": {"..."}},
  "synthesis_report": {"consensus": ["..."], "selected_knowledge": ["..."]},
  "community_knowledge": {"skills": ["..."]},
  "config": {
    "min_support_for_brick": 2,
    "cluster_similarity_threshold": 0.75,
    "include_parquet": true,
    "include_sqlite": true
  }
}
```

## 输出 Schema

#### 3.1 输出模型

```python
class DomainBrick(BaseModel):
    brick_id: str
    domain_id: str
    knowledge_type: KnowledgeType
    statement: str
    confidence: Confidence
    signal: SignalKind
    source_project_ids: list[str]
    support_count: int = Field(ge=1)
    evidence_refs: list[EvidenceRef] = []
    tags: list[str] = []

class AtomCluster(BaseModel):
    cluster_id: str
    theme: str
    consensus_statement: str
    atom_ids: list[str]
    signal: SignalKind
    support_count: int = Field(ge=1)

class DeprecationEvent(BaseModel):
    event_id: str
    domain_id: str
    brick_id: str
    reason: str
    deprecated_at: str
    replacement_brick_id: str | None = None

class SnapshotStats(BaseModel):
    project_count: int = Field(ge=0)
    atom_count: int = Field(ge=0)
    cluster_count: int = Field(ge=0)
    brick_count: int = Field(ge=0)
    deprecation_count: int = Field(ge=0, default=0)
    coverage_ratio: float = Field(ge=0, le=1)

class DomainSnapshot(BaseModel):
    schema_version: str = "dm.domain-snapshot.v1"
    domain_id: str
    domain_display_name: str
    snapshot_version: str
    bricks: list[DomainBrick]
    atom_clusters: list[AtomCluster]
    deprecation_events: list[DeprecationEvent] = []
    stats: SnapshotStats

class SnapshotBuilderOutput(BaseModel):
    schema_version: str = "dm.snapshot-builder-output.v1"
    domain_id: str
    snapshot_version: str
    domain_bricks_path: str
    domain_truth_path: str
    atoms_parquet_path: str | None = None
    domain_map_sqlite_path: str | None = None
    snapshot_manifest_path: str
    stats: SnapshotStats
```

固定文件：

- `DOMAIN_BRICKS.json` — 领域积木列表
- `DOMAIN_TRUTH.md` — 领域真相 markdown
- `atoms.parquet` — 知识原子 parquet（可选）
- `domain_map.sqlite` — 图谱 SQLite（可选）
- `snapshot_manifest.json` — 快照元数据

#### 3.2 输出消费者

- `apps.preextract-api.read`（提供查询）
- `extraction.stage0`（注入 domain bricks 加速提取）
- `extraction.stage1_scan`（注入 domain bricks）

#### 3.3 输出示例

```json
{
  "schema_version": "dm.snapshot-builder-output.v1",
  "domain_id": "calorie-tracking",
  "snapshot_version": "2026-03-19T21:00:00Z",
  "domain_bricks_path": "data/snapshots/calorie-tracking/DOMAIN_BRICKS.json",
  "domain_truth_path": "data/snapshots/calorie-tracking/DOMAIN_TRUTH.md",
  "atoms_parquet_path": "data/snapshots/calorie-tracking/atoms.parquet",
  "domain_map_sqlite_path": "data/snapshots/calorie-tracking/domain_map.sqlite",
  "snapshot_manifest_path": "data/snapshots/calorie-tracking/snapshot_manifest.json",
  "stats": {
    "project_count": 3,
    "atom_count": 27,
    "cluster_count": 8,
    "brick_count": 12,
    "deprecation_count": 0,
    "coverage_ratio": 0.85
  }
}
```

## 验收标准

必须通过的测试用例：

1. Sim2 卡路里场景的 fingerprints + compare_output 能生成至少 3 个 bricks。
2. 当 min_support_for_brick=99（极高）时，bricks 为空，返回 degraded。
3. DOMAIN_TRUTH.md 必须包含领域名称和至少一个 brick 的描述。
4. DOMAIN_BRICKS.json 可被 json.loads 解析且符合 DomainBrick schema。
5. snapshot_manifest.json 包含 snapshot_version 和 stats。

性能预期：

- 5 个项目 × 30 atoms 的输入在 < 5 秒内完成（无 LLM 调用）

不允许的行为：

- 将 CONTESTED signal 的知识直接升级为 brick
- 生成空的 DOMAIN_TRUTH.md
- 不写 snapshot_manifest.json

## 设计自由度

可自由发挥：

- 聚类算法（简单字符串匹配 / TF-IDF / 语义哈希均可）
- DOMAIN_TRUTH.md 的 markdown 格式和章节结构
- atoms.parquet 的列定义
- domain_map.sqlite 的表结构
- brick 排序策略

必须严格遵守：

- DomainBrick / AtomCluster / SnapshotBuilderOutput 的 Pydantic schema
- brick_id 格式
- min_support_for_brick 阈值
- CONTESTED/DIVERGENT 不升级为 brick

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

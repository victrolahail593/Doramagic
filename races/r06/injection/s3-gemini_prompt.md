# 赛马任务: injection (选手: s3-gemini)

以下是完整的任务说明和所有需要的上下文。请直接开始编码。
所有输出文件写到: races/r06/injection/s3-gemini/

--- FILE: races/r06/injection/BRIEF.md ---
# Race Brief: 积木注入 (Brick Injection into Stage 1/2/3)

> **Race ID**: r06-injection
> **赛道**: E

## 任务

实现积木注入 Stage 1/2/3 的机制。当 Stage 0 检测到目标项目使用 Django/FastAPI/React 等框架时，自动加载对应积木，注入到后续 Stage 的 prompt 中。

## 核心逻辑

1. **框架检测**（Stage 0 已有 repo_facts.frameworks）→ 匹配积木库
2. **积木加载** → 从 `bricks/{framework}.jsonl` 读取 DomainBrick 对象
3. **注入 Stage 1** → 积木作为 domain_bricks 字段传入，告诉 LLM "你已经知道这些基线知识"
4. **注入 Stage 2/3** → 积木作为锚点减少搜索面

## 输入

- `repo_facts.json` 中的 `frameworks` 字段（如 `["Django", "React"]`）
- `bricks/` 目录下的 JSONL 文件

## 输出

- `domain_bricks.jsonl` 写入 `<output>/artifacts/`（合并后的积木，供 Stage 1 读取）
- 返回积木文本摘要（供注入 prompt）

## 接口

```python
def load_and_inject_bricks(
    frameworks: list[str],
    bricks_dir: str = "bricks/",
    output_dir: str = None,
) -> BrickInjectionResult:
    """
    匹配框架 → 加载积木 → 写入 artifacts → 返回注入文本。
    """

class BrickInjectionResult:
    bricks_loaded: int
    frameworks_matched: list[str]
    injection_text: str  # 供注入 Stage 1 prompt 的文本
    bricks_path: str     # domain_bricks.jsonl 的路径
```

## 注入文本格式

```
你已经知道以下框架基线知识（来自 Doramagic 积木库）：

[Django] ORM 使用声明式模型定义，自动生成 migration。
[Django] N+1 查询是最常见性能陷阱，用 select_related/prefetch_related。
[React] Hooks 必须在组件顶层调用，不能在条件/循环中。
...

你的任务是发现这个具体项目在基线之上的独特做法。不要重复以上知识。
```

## 纯确定性。无 LLM。

## Deliverables

输出到 `races/r06/injection/{your-racer-id}/`:
1. `brick_injection.py`
2. `tests/test_brick_injection.py`
3. `DECISIONS.md`

--- END FILE ---

--- FILE: packages/contracts/doramagic_contracts/domain_graph.py ---
"""领域图谱模型 — snapshot_builder 构建领域知识快照。"""

from __future__ import annotations

from typing import Optional, Literal

from pydantic import BaseModel, Field

from doramagic_contracts.base import (
    Confidence,
    EvidenceRef,
    KnowledgeAtom,
    KnowledgeType,
    SignalKind,
)


# --- Domain Brick ---


class DomainBrick(BaseModel):
    """领域积木 — 经过多项目验证的知识单元，可注入 Stage 0/1 加速提取。"""

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


# --- Atom Cluster ---


class AtomCluster(BaseModel):
    """原子簇 — 语义相近的知识原子聚类，附带共识声明。"""

    cluster_id: str
    theme: str
    consensus_statement: str
    atom_ids: list[str]
    signal: SignalKind
    support_count: int = Field(ge=1)


# --- Deprecation ---


class DeprecationEvent(BaseModel):
    """废弃事件 — 某个 brick 不再有效时的记录。"""

    event_id: str
    domain_id: str
    brick_id: str
    reason: str
    deprecated_at: str
    replacement_brick_id: Optional[str] = None


# --- Snapshot Stats ---


class SnapshotStats(BaseModel):
    """快照统计摘要。"""

    project_count: int = Field(ge=0)
    atom_count: int = Field(ge=0)
    cluster_count: int = Field(ge=0)
    brick_count: int = Field(ge=0)
    deprecation_count: int = Field(ge=0, default=0)
    coverage_ratio: float = Field(ge=0, le=1)


# --- Snapshot Builder I/O ---


class SnapshotConfig(BaseModel):
    """snapshot_builder 配置。"""

    output_dir: Optional[str] = None
    include_parquet: bool = True
    include_sqlite: bool = True
    min_support_for_brick: int = Field(default=2, ge=1)
    cluster_similarity_threshold: float = Field(default=0.75, ge=0, le=1)


class SnapshotBuilderInput(BaseModel):
    """snapshot_builder 输入。"""

    schema_version: str = "dm.snapshot-builder-input.v1"
    domain_id: str
    domain_display_name: str = ""
    fingerprints: list  # list[ProjectFingerprint] — 避免循环导入，运行时验证
    compare_output: dict  # CompareOutput 字典
    synthesis_report: dict  # SynthesisReportData 字典
    community_knowledge: dict = {}  # CommunityKnowledge 字典
    config: SnapshotConfig = SnapshotConfig()


class DomainSnapshot(BaseModel):
    """领域快照 — snapshot_builder 的核心输出数据。"""

    schema_version: str = "dm.domain-snapshot.v1"
    domain_id: str
    domain_display_name: str
    snapshot_version: str
    bricks: list[DomainBrick]
    atom_clusters: list[AtomCluster]
    deprecation_events: list[DeprecationEvent] = []
    stats: SnapshotStats


class SnapshotBuilderOutput(BaseModel):
    """snapshot_builder 输出 — 文件路径清单 + 快照数据。"""

    schema_version: str = "dm.snapshot-builder-output.v1"
    domain_id: str
    snapshot_version: str
    domain_bricks_path: str
    domain_truth_path: str
    atoms_parquet_path: Optional[str] = None
    domain_map_sqlite_path: Optional[str] = None
    snapshot_manifest_path: str
    stats: SnapshotStats

--- END FILE ---

--- FILE: packages/contracts/doramagic_contracts/base.py ---
"""基础共享模型 — 多个模块复用。"""

from __future__ import annotations

from typing import Optional, Literal

from pydantic import BaseModel, Field, HttpUrl

Priority = Literal["high", "medium", "low"]
Confidence = Literal["high", "medium", "low"]
CandidateType = Literal["github_repo", "community_skill", "tutorial", "use_case"]
SearchStatus = Literal["covered", "partial", "missing"]
KnowledgeType = Literal[
    "capability", "rationale", "constraint", "interface", "failure", "assembly_pattern"
]
SignalKind = Literal[
    "ALIGNED", "STALE", "MISSING", "ORIGINAL", "DRIFTED", "DIVERGENT", "CONTESTED"
]
NormativeForce = Literal["must", "should", "may", "observed"]

# --- 置信度体系 (v1.1) ---
EvidenceTag = Literal["CODE", "DOC", "COMMUNITY", "INFERENCE"]
Verdict = Literal["SUPPORTED", "CONTESTED", "WEAK", "REJECTED"]
PolicyAction = Literal["ALLOW_CORE", "ALLOW_STORY", "QUARANTINE"]


class RepoRef(BaseModel):
    """仓库引用。"""

    repo_id: str
    full_name: str
    url: HttpUrl
    default_branch: str
    commit_sha: str
    local_path: str


class EvidenceRef(BaseModel):
    """证据引用 — 支撑知识声明的具体来源。"""

    kind: Literal["file_line", "artifact_ref", "community_ref"]
    path: str
    start_line: Optional[int] = Field(default=None, ge=1)
    end_line: Optional[int] = Field(default=None, ge=1)
    snippet: Optional[str] = None
    artifact_name: Optional[str] = None
    source_url: Optional[str] = None
    evidence_tag: Optional[EvidenceTag] = None  # CODE/DOC/COMMUNITY/INFERENCE


class SearchDirection(BaseModel):
    direction: str
    priority: Priority


class NeedProfile(BaseModel):
    """用户需求结构化表示 — Phase A 输出，驱动整个管线。"""

    schema_version: str = "dm.need-profile.v1"
    raw_input: str
    keywords: list[str]
    intent: str
    search_directions: list[SearchDirection]
    constraints: list[str]
    quality_expectations: dict[str, str] = {}


class CandidateQualitySignals(BaseModel):
    stars: Optional[int] = Field(default=None, ge=0)
    forks: Optional[int] = Field(default=None, ge=0)
    last_updated: Optional[str] = None
    has_readme: bool = True
    issue_activity: Optional[str] = None
    license: Optional[str] = None


class DiscoveryCandidate(BaseModel):
    """候选项目。"""

    candidate_id: str
    name: str
    url: str
    type: CandidateType
    relevance: Priority
    contribution: str
    quick_score: float = Field(ge=0, le=10)
    quality_signals: CandidateQualitySignals
    selected_for_phase_c: bool = False
    selected_for_phase_d: bool = False


class SearchCoverageItem(BaseModel):
    direction: str
    status: SearchStatus
    notes: Optional[str] = None


class KnowledgeAtom(BaseModel):
    """知识原子 — 图谱的基本单位。"""

    atom_id: str
    knowledge_type: KnowledgeType
    subject: str
    predicate: str
    object: str
    scope: str
    normative_force: NormativeForce
    confidence: Confidence
    evidence_refs: list[EvidenceRef]
    source_card_ids: list[str]
    # 置信度体系 (v1.1)
    evidence_tags: list[EvidenceTag] = []
    verdict: Optional[Verdict] = None
    policy_action: Optional[PolicyAction] = None


class CommunitySignalItem(BaseModel):
    """结构化社区信号 — 带适用域约束。"""

    signal_id: str
    title: str
    description: str
    source_type: Literal["issue", "pr", "changelog", "security_advisory", "discussion"]
    source_ref: str  # Issue #123, CHANGELOG v2.0
    # 适用域约束
    applicable_versions: Optional[str] = None  # ">=2.0,<3.0" or None = all
    applicable_environments: list[str] = []  # ["linux", "docker"] or [] = all
    applicable_personas: list[str] = []  # ["beginner", "enterprise"] or [] = all
    is_exception_path: bool = False  # True = edge case, False = common path
    source_confidence: Confidence = "medium"


class CommunitySignals(BaseModel):
    issue_activity: Optional[str] = None
    pr_merge_velocity: Optional[str] = None
    changelog_frequency: Optional[str] = None
    sentiment: Optional[Literal["positive", "mixed", "controversial", "quiet"]] = None
    structured_signals: list[CommunitySignalItem] = []  # v1.1: 结构化信号


class ProjectFingerprint(BaseModel):
    """项目指纹 — 机器可比较的项目知识表示。"""

    schema_version: str = "dm.project-fingerprint.v1"
    project: RepoRef
    code_fingerprint: dict
    knowledge_atoms: list[KnowledgeAtom]
    soul_graph: dict
    community_signals: CommunitySignals

--- END FILE ---

## 关键约束
1. 不能 import anthropic / import openai / from google.generativeai
2. 所有 LLM 调用通过 LLMAdapter（如果需要 LLM 的话）
3. 纯确定性模块不需要 LLM
4. 输出路径: races/r06/injection/s3-gemini/

## 验收清单
- [ ] 主实现 .py 文件
- [ ] tests/ 目录下的测试文件
- [ ] DECISIONS.md 设计决策文档
- [ ] 所有测试通过
- [ ] 文件都在 races/r06/injection/s3-gemini/ 下（不要写到其他位置）
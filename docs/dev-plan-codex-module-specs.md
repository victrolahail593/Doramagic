# Doramagic 赛马模块接口规格

日期：2026-03-18  
版本：v0.1（供赛马开发使用）  
适用范围：Doramagic v5.3 开发手册 Part 3-4 补充  
目标：给 4 个赛马选手一份**可直接独立开发**的模块规格

## 0. 使用说明

本文只覆盖 8 个适合赛马的模块：

1. `extraction.stage1_scan`
2. `extraction.stage15_agentic`
3. `cross-project.compare`
4. `cross-project.discovery`
5. `cross-project.synthesis`
6. `skill-compiler.openclaw`
7. `platform-openclaw.validator`
8. `orchestration.phase_runner`

不在本文中的模块，例如 `contracts.artifacts`、`cross-project.fingerprint`、`evals.fixtures`、`platform_rules.json`、`racekit.workspace`，默认由 PM/架构师冻结后下发，不参加赛马。

## 1. 全局前提

### 1.1 冻结前提

在任何赛马轮开始前，以下内容必须冻结：

- artifact schema 版本号
- 文件命名
- 共享错误码
- `project_fingerprint.json` schema
- `platform_rules.json` 语义
- fixture 数据集和 golden case

任何选手不得擅自扩展上游输入 contract。需要新增字段时，必须在 `decisions.md` 中声明为“候选扩展”，不能写入正式输出。

### 1.2 共享 envelope

所有赛马模块都必须返回统一 envelope：

```python
from typing import Generic, Literal, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")

class RunMetrics(BaseModel):
    wall_time_ms: int = Field(ge=0)
    llm_calls: int = Field(ge=0)
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    estimated_cost_usd: float = Field(ge=0)
    retries: int = Field(ge=0, default=0)

class WarningItem(BaseModel):
    code: str
    message: str

class ModuleResultEnvelope(BaseModel, Generic[T]):
    schema_version: str = "dm.module-envelope.v1"
    module_name: str
    status: Literal["ok", "degraded", "blocked", "error"]
    error_code: str | None = None
    warnings: list[WarningItem] = []
    data: T | None = None
    metrics: RunMetrics
```

解释：

- `ok`: 输出完整可消费
- `degraded`: 输出可消费，但有功能降级
- `blocked`: 模块按 contract 执行，但前置条件不满足，无法继续
- `error`: 实现或运行异常，输出不可消费

### 1.3 共享错误码

所有模块只允许使用以下错误码：

| 错误码 | 含义 |
| --- | --- |
| `E_INPUT_INVALID` | 输入字段缺失或类型不合法 |
| `E_UPSTREAM_MISSING` | 上游 artifact 不存在 |
| `E_SCHEMA_MISMATCH` | 输入 schema version 不兼容 |
| `E_TIMEOUT` | 运行超时 |
| `E_RETRY_EXHAUSTED` | 重试后仍失败 |
| `E_BUDGET_EXCEEDED` | token / 调用 / 时间预算超标 |
| `E_NO_CANDIDATES` | discovery 找不到可用候选 |
| `E_NO_HYPOTHESES` | stage1.5 没有可验证假说 |
| `E_PLATFORM_VIOLATION` | skill 不符合 OpenClaw 规则 |
| `E_UNRESOLVED_CONFLICT` | synthesis 或 compiler 遇到未解决冲突 |
| `E_VALIDATION_BLOCKED` | validation 给出 BLOCKED |

### 1.4 共享基础模型

以下模型会在多个模块中复用。

```python
from typing import Literal
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

class RepoRef(BaseModel):
    repo_id: str
    full_name: str
    url: HttpUrl
    default_branch: str
    commit_sha: str
    local_path: str

class EvidenceRef(BaseModel):
    kind: Literal["file_line", "artifact_ref", "community_ref"]
    path: str
    start_line: int | None = Field(default=None, ge=1)
    end_line: int | None = Field(default=None, ge=1)
    snippet: str | None = None
    artifact_name: str | None = None
    source_url: str | None = None

class SearchDirection(BaseModel):
    direction: str
    priority: Priority

class NeedProfile(BaseModel):
    schema_version: str = "dm.need-profile.v1"
    raw_input: str
    keywords: list[str]
    intent: str
    search_directions: list[SearchDirection]
    constraints: list[str]
    quality_expectations: dict[str, str] = {}

class CandidateQualitySignals(BaseModel):
    stars: int | None = Field(default=None, ge=0)
    forks: int | None = Field(default=None, ge=0)
    last_updated: str | None = None
    has_readme: bool = True
    issue_activity: str | None = None
    license: str | None = None

class DiscoveryCandidate(BaseModel):
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
    notes: str | None = None

class CommunityKnowledgeItem(BaseModel):
    item_id: str
    name: str
    source: str
    kind: Literal["skill", "tutorial", "use_case"]
    capabilities: list[str]
    storage_pattern: str | None = None
    cron_pattern: str | None = None
    reusable_knowledge: list[str]

class CommunityKnowledge(BaseModel):
    schema_version: str = "dm.community-knowledge.v1"
    skills: list[CommunityKnowledgeItem] = []
    tutorials: list[CommunityKnowledgeItem] = []
    use_cases: list[CommunityKnowledgeItem] = []

class KnowledgeAtom(BaseModel):
    atom_id: str
    knowledge_type: KnowledgeType
    subject: str
    predicate: str
    object: str
    scope: str
    normative_force: Literal["must", "should", "may", "observed"]
    confidence: Confidence
    evidence_refs: list[EvidenceRef]
    source_card_ids: list[str]

class CommunitySignals(BaseModel):
    issue_activity: str | None = None
    pr_merge_velocity: str | None = None
    changelog_frequency: str | None = None
    sentiment: Literal["positive", "mixed", "controversial", "quiet"] | None = None

class ProjectFingerprint(BaseModel):
    schema_version: str = "dm.project-fingerprint.v1"
    project: RepoRef
    code_fingerprint: dict
    knowledge_atoms: list[KnowledgeAtom]
    soul_graph: dict
    community_signals: CommunitySignals
```

### 1.5 命名与落盘规则

这些部分严格遵守，不允许选手自由发挥：

- `need_profile.json`
- `discovery_result.json`
- `hypothesis_list.json`
- `hypotheses.jsonl`
- `exploration_log.jsonl`
- `claim_ledger.jsonl`
- `evidence_index.json`
- `context_digest.md`
- `comparison_result.json`
- `synthesis_report.json`
- `synthesis_report.md`
- `SKILL.md`
- `PROVENANCE.md`
- `LIMITATIONS.md`
- `validation_report.json`
- `run_manifest.json`

## 2. 更新后的赛马日历

### 2.1 新资源配置

当前资源为：

- PM / 架构评审：Opus
- 选手 1：Sonnet 子代理
- 选手 2：Codex
- 选手 3：Gemini
- 选手 4：GLM5

每轮可同时跑 2 条赛道，每条赛道 2 名选手 head-to-head。

### 2.2 更新后的轮次

因为恰好有 8 个赛马模块，所以推荐：

- `Round 0`: 非赛马冻结轮
- `Round 1-4`: 正式赛马轮，每轮 2 个模块

### 2.3 配对表

| 轮次 | 赛道 A | 选手 | 赛道 B | 选手 |
| --- | --- | --- | --- | --- |
| Round 0 | contracts / fixtures / fingerprint 冻结 | PM 主导，非赛马 | racekit / CI / baseline smoke | PM 主导，非赛马 |
| Round 1 | `extraction.stage1_scan` | Sonnet vs GLM5 | `extraction.stage15_agentic` | Codex vs Gemini |
| Round 2 | `cross-project.discovery` | Sonnet vs Gemini | `cross-project.compare` | Codex vs GLM5 |
| Round 3 | `cross-project.synthesis` | Sonnet vs Gemini | `skill-compiler.openclaw` | Codex vs GLM5 |
| Round 4 | `platform-openclaw.validator` | Sonnet vs GLM5 | `orchestration.phase_runner` | Codex vs Gemini |

### 2.4 为什么这样配

- `stage15_agentic` 和 `phase_runner` 是最强依赖编排模块，优先给 `Codex vs Gemini`
- `compare` 和 `compiler` 既要结构严谨又要集成平台规则，优先让 `GLM5` 参与，因为它在未来部署环境上
- `stage1_scan` 和 `validator` 偏规则化、偏稳态，适合 `Sonnet` 参与
- `synthesis` 需要较强权衡与可读表达，`Sonnet vs Gemini` 的差异性更大

### 2.5 更新后的时间线

| 阶段 | 时长 |
| --- | --- |
| Round 0 | 2-3 天 |
| Round 1 | 1.5-2 天 |
| Review 1 | 0.5 天 |
| Round 2 | 1.5-2 天 |
| Review 2 | 0.5 天 |
| Round 3 | 1.5-2 天 |
| Review 3 | 0.5 天 |
| Round 4 | 1.5-2 天 |
| Review 4 | 1 天 |

预估变化：

- 之前参考稿：终端首个可用版本 `12-16` 个工作日
- 现在改为 4 选手 / 2 并行赛道后：终端首个可用版本可压到 `10-13` 个工作日

压缩的原因不是减少模块，而是：

- 不再浪费第 3 名选手的空档
- 每轮恰好消化 2 个赛马模块
- Round 4 结束即可形成终端端到端闭环

## 3. 模块规格

---

## 3.1 `extraction.stage1_scan`

### 1. 模块名称与职责

一句话职责：在 Stage 0 的确定性事实之上做广度扫描，回答 Q1-Q7，并生成 Q8 假说列表，给 Stage 1.5 提供高价值探索入口。

### 2. 输入契约

#### 2.1 输入模型

```python
class RepoFacts(BaseModel):
    schema_version: str = "dm.repo-facts.v1"
    repo: RepoRef
    languages: list[str]
    frameworks: list[str]
    entrypoints: list[str]
    commands: list[str]
    storage_paths: list[str]
    dependencies: list[str]
    repo_summary: str

class Stage1ScanConfig(BaseModel):
    max_llm_calls: int = Field(default=8, ge=1, le=16)
    max_prompt_tokens: int = Field(default=24000, ge=1000)
    generate_hypotheses: bool = True
    include_domain_bricks: bool = False

class Stage1ScanInput(BaseModel):
    schema_version: str = "dm.stage1-scan-input.v1"
    repo_facts: RepoFacts
    domain_bricks: list[str] | None = None
    config: Stage1ScanConfig
```

#### 2.2 输入来源

- `repo_facts`：来自 Stage 0
- `domain_bricks`：可选，来自 API `GET /domains/{id}/bricks`
- `config`：由 phase runner 或 CLI 注入

#### 2.3 输入示例

来自 Sim2 卡路里场景，针对 `ai-calorie-counter`：

```json
{
  "schema_version": "dm.stage1-scan-input.v1",
  "repo_facts": {
    "schema_version": "dm.repo-facts.v1",
    "repo": {
      "repo_id": "acc",
      "full_name": "open-kbs/ai-calorie-counter",
      "url": "https://github.com/open-kbs/ai-calorie-counter",
      "default_branch": "main",
      "commit_sha": "abc123",
      "local_path": "/tmp/repos/ai-calorie-counter"
    },
    "languages": ["TypeScript"],
    "frameworks": ["Next.js"],
    "entrypoints": ["src/app/api/chat/route.ts"],
    "commands": ["npm run dev", "npm run build"],
    "storage_paths": ["data/", "messages/"],
    "dependencies": ["openai", "zod"],
    "repo_summary": "AI calorie tracking app with text/photo parsing and JSON contracts"
  },
  "domain_bricks": ["daily meal log", "macro delta"],
  "config": {
    "max_llm_calls": 8,
    "max_prompt_tokens": 24000,
    "generate_hypotheses": true,
    "include_domain_bricks": true
  }
}
```

### 3. 输出契约

#### 3.1 输出模型

```python
class Stage1Finding(BaseModel):
    finding_id: str
    question_key: Literal["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7"]
    knowledge_type: KnowledgeType
    title: str
    statement: str
    confidence: Confidence
    evidence_refs: list[EvidenceRef]

class Hypothesis(BaseModel):
    hypothesis_id: str
    statement: str
    reason: str
    priority: Priority
    search_hints: list[str]
    related_finding_ids: list[str] = []

class Stage1Coverage(BaseModel):
    answered_questions: list[str]
    partial_questions: list[str]
    uncovered_questions: list[str]

class Stage1ScanOutput(BaseModel):
    schema_version: str = "dm.stage1-scan-output.v1"
    repo: RepoRef
    findings: list[Stage1Finding]
    hypotheses: list[Hypothesis]
    coverage: Stage1Coverage
    recommended_for_stage15: bool
```

固定文件：

- `stage1_findings.json`
- `hypothesis_list.json`

#### 3.2 输出消费者

- `extraction.stage15_agentic`
- `extraction.stage3_cards`
- `orchestration.phase_runner`

#### 3.3 输出示例

```json
{
  "schema_version": "dm.stage1-scan-output.v1",
  "repo": {
    "repo_id": "acc",
    "full_name": "open-kbs/ai-calorie-counter",
    "url": "https://github.com/open-kbs/ai-calorie-counter",
    "default_branch": "main",
    "commit_sha": "abc123",
    "local_path": "/tmp/repos/ai-calorie-counter"
  },
  "findings": [
    {
      "finding_id": "Q2-ACC-001",
      "question_key": "Q2",
      "knowledge_type": "interface",
      "title": "LLM-as-Parser JSON contract",
      "statement": "The app converts food descriptions into structured JSON before downstream rendering.",
      "confidence": "high",
      "evidence_refs": [
        {
          "kind": "file_line",
          "path": "src/lib/parser.ts",
          "start_line": 18,
          "end_line": 42,
          "snippet": "return { type: 'food', calories, protein, carbs, fat }"
        }
      ]
    }
  ],
  "hypotheses": [
    {
      "hypothesis_id": "H-001",
      "statement": "Profile and daily budget are injected as compressed aggregates rather than raw history.",
      "reason": "This would match low-token conversational UX patterns.",
      "priority": "high",
      "search_hints": ["context", "summary", "today totals"],
      "related_finding_ids": ["Q2-ACC-001"]
    }
  ],
  "coverage": {
    "answered_questions": ["Q1", "Q2", "Q3", "Q5", "Q7"],
    "partial_questions": ["Q4", "Q6"],
    "uncovered_questions": []
  },
  "recommended_for_stage15": true
}
```

### 4. 行为契约

- 正常路径：输入完整 `repo_facts` 后，必须输出至少 7 条 findings，并按 priority 生成 3-8 条假说。
- 错误路径：
  - `repo_facts` 缺失关键字段：`blocked + E_INPUT_INVALID`
  - repo 太小、无足够复杂度：`degraded`，但仍输出 findings，`recommended_for_stage15=false`
- 幂等性：相同 commit、相同 config、temperature=0 时，输出的 `finding_id` 和 `hypothesis_id` 必须稳定。
- 超时/重试：
  - 单次超时 180 秒
  - 最多重试 1 次
  - 重试后仍失败返回 `error + E_TIMEOUT`

### 5. 验收标准

必须通过的测试用例：

1. 对 Sim2 的 `ai-calorie-counter`，能产出至少 1 条 `interface` 类 finding 和至少 1 条 `rationale` 类 finding。
2. 对极小 repo，能返回 `degraded` 而不是崩溃。
3. 对缺失 `commit_sha` 的输入，必须返回 `blocked + E_INPUT_INVALID`。

性能预期：

- 墙钟时间 `< 3 分钟 / repo`
- LLM 调用 `<= 8`
- 成本上限 `< $0.08 / repo`

不允许的行为：

- 直接输出无 evidence 的高置信度 finding
- 生成 0 条假说但仍标 `recommended_for_stage15=true`
- 修改 `repo_facts` 原字段含义

### 6. 设计自由度

可自由发挥：

- Q1-Q7 的内部 prompt
- finding 抽取顺序
- hypothesis ranking 算法
- 内部缓存结构

必须严格遵守：

- 输入输出 schema
- `stage1_findings.json` / `hypothesis_list.json` 文件名
- `finding_id` / `hypothesis_id` 的稳定生成
- 共享错误码

---

## 3.2 `extraction.stage15_agentic`

### 1. 模块名称与职责

一句话职责：基于 Stage 1 的高价值假说做工具驱动深挖，产出带 file:line 证据绑定的 claims 和 exploration 轨迹。

### 2. 输入契约

#### 2.1 输入模型

```python
class Stage15Budget(BaseModel):
    max_rounds: int = Field(default=5, ge=1, le=10)
    max_tool_calls: int = Field(default=30, ge=5, le=60)
    max_prompt_tokens: int = Field(default=60000, ge=5000)
    stop_after_no_gain_rounds: int = Field(default=2, ge=1, le=5)

class Stage15Toolset(BaseModel):
    allow_read_artifact: bool = True
    allow_list_tree: bool = True
    allow_search_repo: bool = True
    allow_read_file: bool = True
    allow_append_finding: bool = True

class Stage15AgenticInput(BaseModel):
    schema_version: str = "dm.stage15-input.v1"
    repo: RepoRef
    repo_facts: RepoFacts
    stage1_output: Stage1ScanOutput
    budget: Stage15Budget
    toolset: Stage15Toolset
```

#### 2.2 输入来源

- `repo` / `repo_facts`：Stage 0
- `stage1_output`：`extraction.stage1_scan`
- `budget`：phase runner 下发

#### 2.3 输入示例

```json
{
  "schema_version": "dm.stage15-input.v1",
  "repo": {
    "repo_id": "acc",
    "full_name": "open-kbs/ai-calorie-counter",
    "url": "https://github.com/open-kbs/ai-calorie-counter",
    "default_branch": "main",
    "commit_sha": "abc123",
    "local_path": "/tmp/repos/ai-calorie-counter"
  },
  "repo_facts": { "schema_version": "dm.repo-facts.v1", "languages": ["TypeScript"], "frameworks": ["Next.js"], "entrypoints": ["src/app/api/chat/route.ts"], "commands": ["npm run dev"], "storage_paths": ["data/"], "dependencies": ["openai"], "repo_summary": "AI calorie tracker", "repo": { "repo_id": "acc", "full_name": "open-kbs/ai-calorie-counter", "url": "https://github.com/open-kbs/ai-calorie-counter", "default_branch": "main", "commit_sha": "abc123", "local_path": "/tmp/repos/ai-calorie-counter" } },
  "stage1_output": {
    "schema_version": "dm.stage1-scan-output.v1",
    "repo": { "repo_id": "acc", "full_name": "open-kbs/ai-calorie-counter", "url": "https://github.com/open-kbs/ai-calorie-counter", "default_branch": "main", "commit_sha": "abc123", "local_path": "/tmp/repos/ai-calorie-counter" },
    "findings": [],
    "hypotheses": [
      {
        "hypothesis_id": "H-001",
        "statement": "Daily totals are injected as compressed context instead of raw history.",
        "reason": "Likely token-optimization pattern",
        "priority": "high",
        "search_hints": ["today totals", "summary", "context"],
        "related_finding_ids": []
      }
    ],
    "coverage": { "answered_questions": ["Q1"], "partial_questions": ["Q2"], "uncovered_questions": [] },
    "recommended_for_stage15": true
  },
  "budget": {
    "max_rounds": 5,
    "max_tool_calls": 30,
    "max_prompt_tokens": 60000,
    "stop_after_no_gain_rounds": 2
  },
  "toolset": {
    "allow_read_artifact": true,
    "allow_list_tree": true,
    "allow_search_repo": true,
    "allow_read_file": true,
    "allow_append_finding": true
  }
}
```

### 3. 输出契约

#### 3.1 输出模型

```python
class ExplorationLogEntry(BaseModel):
    step_id: str
    round_index: int = Field(ge=1)
    tool_name: Literal["read_artifact", "list_tree", "search_repo", "read_file", "append_finding"]
    tool_input: dict
    observation: str
    produced_evidence_refs: list[EvidenceRef] = []

class ClaimRecord(BaseModel):
    claim_id: str
    statement: str
    status: Literal["confirmed", "rejected", "pending", "inference"]
    confidence: Confidence
    hypothesis_id: str | None = None
    supporting_step_ids: list[str]
    evidence_refs: list[EvidenceRef]

class Stage15Summary(BaseModel):
    resolved_hypotheses: list[str]
    unresolved_hypotheses: list[str]
    termination_reason: Literal[
        "all_hypotheses_resolved", "no_information_gain", "budget_exhausted", "manual_skip"
    ]

class Stage15AgenticOutput(BaseModel):
    schema_version: str = "dm.stage15-output.v1"
    repo: RepoRef
    hypotheses_path: str
    exploration_log_path: str
    claim_ledger_path: str
    evidence_index_path: str
    context_digest_path: str
    promoted_claims: list[ClaimRecord]
    summary: Stage15Summary
```

固定文件：

- `hypotheses.jsonl`
- `exploration_log.jsonl`
- `claim_ledger.jsonl`
- `evidence_index.json`
- `context_digest.md`

#### 3.2 输出消费者

- `extraction.stage3_cards`
- `extraction.stage35_validate`
- `cross-project.fingerprint`
- `orchestration.phase_runner`

#### 3.3 输出示例

`claim_ledger.jsonl` 示例行：

```json
{
  "claim_id": "C-ACC-007",
  "statement": "The system injects today's aggregate nutrition totals instead of replaying the full meal history.",
  "status": "confirmed",
  "confidence": "high",
  "hypothesis_id": "H-001",
  "supporting_step_ids": ["S-003", "S-005"],
  "evidence_refs": [
    {
      "kind": "file_line",
      "path": "src/lib/context.ts",
      "start_line": 22,
      "end_line": 38,
      "snippet": "const summary = { calories, protein, carbs, fat };"
    }
  ]
}
```

`Stage15AgenticOutput` 摘要：

```json
{
  "schema_version": "dm.stage15-output.v1",
  "repo": {
    "repo_id": "acc",
    "full_name": "open-kbs/ai-calorie-counter",
    "url": "https://github.com/open-kbs/ai-calorie-counter",
    "default_branch": "main",
    "commit_sha": "abc123",
    "local_path": "/tmp/repos/ai-calorie-counter"
  },
  "hypotheses_path": "artifacts/stage15/hypotheses.jsonl",
  "exploration_log_path": "artifacts/stage15/exploration_log.jsonl",
  "claim_ledger_path": "artifacts/stage15/claim_ledger.jsonl",
  "evidence_index_path": "artifacts/stage15/evidence_index.json",
  "context_digest_path": "artifacts/stage15/context_digest.md",
  "promoted_claims": [
    {
      "claim_id": "C-ACC-007",
      "statement": "Daily aggregate context is injected into the LLM.",
      "status": "confirmed",
      "confidence": "high",
      "hypothesis_id": "H-001",
      "supporting_step_ids": ["S-003"],
      "evidence_refs": [
        { "kind": "file_line", "path": "src/lib/context.ts", "start_line": 22, "end_line": 38, "snippet": "const summary = ..." }
      ]
    }
  ],
  "summary": {
    "resolved_hypotheses": ["H-001"],
    "unresolved_hypotheses": [],
    "termination_reason": "all_hypotheses_resolved"
  }
}
```

### 4. 行为契约

- 正常路径：按假说 priority 顺序探索，所有 `confirmed` claim 必须带 `file:line` 级 evidence。
- 错误路径：
  - 无假说：`blocked + E_NO_HYPOTHESES`
  - 工具失败但可回退：继续，记录 warning，最终可 `degraded`
  - budget 用尽：返回 `degraded + E_BUDGET_EXCEEDED`
- 幂等性：
  - byte-for-byte 不强制
  - 但相同输入下，`claim_id`、`status`、主要 evidence path 必须稳定
- 超时/重试：
  - 单轮超时 90 秒
  - 总时长上限 10 分钟
  - 读文件类工具不重试；模型类步骤最多重试 1 次

### 5. 验收标准

必须通过的测试用例：

1. 对 Sim2 的 `ai-calorie-counter`，至少确认 1 条 `interface` 类深挖 claim，且带 file:line 证据。
2. 当某条假说被证伪时，`claim_ledger.jsonl` 必须写出 `rejected` 记录，而不是静默丢弃。
3. `check_claims_have_evidence()` 回放时，所有 `confirmed` claim 都能映射到 `exploration_log.jsonl` 的 step。

性能预期：

- 小项目默认 5 轮，大项目最多 10 轮
- 成本上限 `< $0.35 / repo`
- python-dotenv 类小 repo 应低于 `$0.15`

不允许的行为：

- `confirmed` claim 无 evidence
- 跳过 `exploration_log.jsonl`
- 直接修改 Stage 1 结果而不记录为新 claim

### 6. 设计自由度

可自由发挥：

- 假说调度策略
- 工具调用顺序
- information gain 判定算法
- `context_digest.md` 的压缩方式

必须严格遵守：

- 5 个工具名
- 5 个中间文件名
- `claim_id` 稳定性
- `confirmed` claim 的 evidence 约束

---

## 3.3 `cross-project.compare`

### 1. 模块名称与职责

一句话职责：对多个 `project_fingerprint.json` 做知识匹配与差异标注，产出 ALIGNED / MISSING / ORIGINAL / DRIFTED 等跨项目信号。

### 2. 输入契约

#### 2.1 输入模型

```python
class CompareConfig(BaseModel):
    exact_aligned_threshold: float = Field(default=0.92, ge=0, le=1)
    semantic_threshold: float = Field(default=0.80, ge=0, le=1)
    partial_threshold: float = Field(default=0.62, ge=0, le=1)
    missing_min_coverage: float = Field(default=0.60, ge=0, le=1)
    missing_min_independence: float = Field(default=0.55, ge=0, le=1)
    missing_min_support: int = Field(default=3, ge=1)

class CompareInput(BaseModel):
    schema_version: str = "dm.compare-input.v1"
    domain_id: str
    fingerprints: list[ProjectFingerprint]
    config: CompareConfig
```

#### 2.2 输入来源

- `fingerprints`：来自 `cross-project.fingerprint`
- `config`：由 PM 在 Round 0 冻结

#### 2.3 输入示例

```json
{
  "schema_version": "dm.compare-input.v1",
  "domain_id": "nutrition-calorie",
  "fingerprints": [
    {
      "schema_version": "dm.project-fingerprint.v1",
      "project": {
        "repo_id": "acc",
        "full_name": "open-kbs/ai-calorie-counter",
        "url": "https://github.com/open-kbs/ai-calorie-counter",
        "default_branch": "main",
        "commit_sha": "abc123",
        "local_path": "/tmp/repos/acc"
      },
      "code_fingerprint": {"commands": ["chat"], "deps": ["openai"]},
      "knowledge_atoms": [
        {
          "atom_id": "A-001",
          "knowledge_type": "interface",
          "subject": "food_input",
          "predicate": "parsed_as",
          "object": "json_contract",
          "scope": "runtime",
          "normative_force": "must",
          "confidence": "high",
          "evidence_refs": [{"kind": "file_line", "path": "src/parser.ts", "start_line": 18, "end_line": 42, "snippet": "return {...}"}],
          "source_card_ids": ["CC-001"]
        }
      ],
      "soul_graph": {},
      "community_signals": {"issue_activity": "low", "pr_merge_velocity": "fast", "changelog_frequency": "monthly", "sentiment": "positive"}
    }
  ],
  "config": {
    "exact_aligned_threshold": 0.92,
    "semantic_threshold": 0.80,
    "partial_threshold": 0.62,
    "missing_min_coverage": 0.60,
    "missing_min_independence": 0.55,
    "missing_min_support": 3
  }
}
```

### 3. 输出契约

#### 3.1 输出模型

```python
class CompareSignal(BaseModel):
    signal_id: str
    signal: SignalKind
    subject_project_ids: list[str]
    normalized_statement: str
    support_count: int = Field(ge=0)
    support_independence: float = Field(ge=0, le=1)
    match_score: float = Field(ge=0, le=1)
    evidence_refs: list[EvidenceRef]
    notes: str | None = None

class CompareMetrics(BaseModel):
    project_count: int = Field(ge=1)
    atom_count: int = Field(ge=0)
    aligned_count: int = Field(ge=0)
    missing_count: int = Field(ge=0)
    original_count: int = Field(ge=0)
    drifted_count: int = Field(ge=0)

class CompareOutput(BaseModel):
    schema_version: str = "dm.compare-output.v1"
    domain_id: str
    compared_projects: list[str]
    signals: list[CompareSignal]
    metrics: CompareMetrics
```

固定文件：

- `comparison_result.json`

#### 3.2 输出消费者

- `cross-project.synthesis`
- `domain-graph.snapshot_builder`
- 后续 `HEALTH_CHECK` / `SOUL_DIFF`

#### 3.3 输出示例

```json
{
  "schema_version": "dm.compare-output.v1",
  "domain_id": "nutrition-calorie",
  "compared_projects": ["acc", "foodyo", "ont"],
  "signals": [
    {
      "signal_id": "SIG-001",
      "signal": "ALIGNED",
      "subject_project_ids": ["foodyo", "ont"],
      "normalized_statement": "Food nutrition data is normalized per 100g before scaling.",
      "support_count": 2,
      "support_independence": 0.84,
      "match_score": 0.93,
      "evidence_refs": [
        { "kind": "file_line", "path": "nutrition_scale.kt", "start_line": 12, "end_line": 32, "snippet": "amount / 100" }
      ]
    },
    {
      "signal_id": "SIG-002",
      "signal": "ORIGINAL",
      "subject_project_ids": ["acc"],
      "normalized_statement": "Natural-language meal input is parsed directly into JSON by the LLM.",
      "support_count": 1,
      "support_independence": 1.0,
      "match_score": 0.41,
      "evidence_refs": [
        { "kind": "file_line", "path": "src/parser.ts", "start_line": 18, "end_line": 42, "snippet": "return {...}" }
      ]
    }
  ],
  "metrics": {
    "project_count": 3,
    "atom_count": 127,
    "aligned_count": 24,
    "missing_count": 6,
    "original_count": 8,
    "drifted_count": 2
  }
}
```

### 4. 行为契约

- 正常路径：
  - 先 lexical / semantic / structured 三层匹配
  - 再用阈值分类 signal
  - `MISSING` 必须满足 `coverage >= 0.60 + independence >= 0.55 + support >= 3`
  - `ORIGINAL` 必须做二次检索确认
- 错误路径：
  - 少于 2 个 fingerprint：`blocked + E_INPUT_INVALID`
  - fingerprint schema 不一致：`blocked + E_SCHEMA_MISMATCH`
- 幂等性：
  - 相同 fingerprints + 相同 config，`signal_id`、signal 数量、分类结果必须稳定
- 超时/重试：
  - 单次运行超时 120 秒
  - 算法不依赖外部 API，不允许无限重试
  - 最多重试 1 次

### 5. 验收标准

必须通过的测试用例：

1. Sim2 三项目比较时，必须至少识别出 1 条 `ALIGNED` 和 1 条 `ORIGINAL`。
2. 当输入 1 个 fingerprint 时，必须返回 `blocked + E_INPUT_INVALID`。
3. 当同一 atom 只是措辞变化时，不得误标为 `ORIGINAL`。

性能预期：

- 5 个项目、每项目 200 atom 情况下 `< 90 秒`
- 成本上限 `< $0.10`

不允许的行为：

- 在无二次检索下直接判 `ORIGINAL`
- 忽略 `community_signals`
- 动态改阈值但不记录

### 6. 设计自由度

可自由发挥：

- lexical / semantic / structured 的内部实现
- atom canonicalization 算法
- cluster 数据结构

必须严格遵守：

- 输入输出 schema
- 阈值默认值
- `comparison_result.json` 文件名
- `signals[].signal` 的合法枚举值

---

## 3.4 `cross-project.discovery`

### 1. 模块名称与职责

一句话职责：把用户模糊需求转换成 3-5 个高价值候选项目和 0-N 个社区资源，并明确覆盖了哪些搜索方向。

### 2. 输入契约

#### 2.1 输入模型

```python
class DiscoveryConfig(BaseModel):
    github_min_stars: int = Field(default=10, ge=0)
    github_max_candidates_per_direction: int = Field(default=10, ge=1, le=30)
    stale_months_threshold: int = Field(default=6, ge=1, le=24)
    top_k_final: int = Field(default=5, ge=1, le=10)
    allow_api_enrichment: bool = True

class ApiDomainHint(BaseModel):
    domain_id: str
    matched_keywords: list[str]
    domain_bricks: list[str] = []

class DiscoveryInput(BaseModel):
    schema_version: str = "dm.discovery-input.v1"
    need_profile: NeedProfile
    api_hint: ApiDomainHint | None = None
    config: DiscoveryConfig
```

#### 2.2 输入来源

- `need_profile`：Phase A
- `api_hint`：可选，来自 System B 查询

#### 2.3 输入示例

```json
{
  "schema_version": "dm.discovery-input.v1",
  "need_profile": {
    "schema_version": "dm.need-profile.v1",
    "raw_input": "我想要做一个记录食物卡路里的 skill",
    "keywords": ["食物", "卡路里", "记录", "追踪", "skill"],
    "intent": "构建一个通过消息记录饮食和计算热量的 OpenClaw AI skill",
    "search_directions": [
      {"direction": "AI 食物识别与卡路里估算", "priority": "high"},
      {"direction": "营养数据库与食物成分表", "priority": "high"},
      {"direction": "OpenClaw 社区已有的饮食/健康 skill", "priority": "high"},
      {"direction": "健康追踪应用的用户体验设计", "priority": "medium"}
    ],
    "constraints": [
      "OpenClaw 平台（SKILL.md 格式）",
      "消息驱动交互（Telegram/WhatsApp）",
      "中文用户支持",
      "本地存储优先（~/clawd/memory/）"
    ],
    "quality_expectations": {
      "accuracy": "常见食物卡路里估算误差 < 20%",
      "response_time": "< 10 秒",
      "language": "中文优先"
    }
  },
  "api_hint": null,
  "config": {
    "github_min_stars": 10,
    "github_max_candidates_per_direction": 10,
    "stale_months_threshold": 6,
    "top_k_final": 5,
    "allow_api_enrichment": true
  }
}
```

### 3. 输出契约

#### 3.1 输出模型

```python
class DiscoveryResult(BaseModel):
    schema_version: str = "dm.discovery-result.v1"
    candidates: list[DiscoveryCandidate]
    search_coverage: list[SearchCoverageItem]
    no_candidate_reason: str | None = None
```

固定文件：

- `discovery_result.json`

#### 3.2 输出消费者

- Phase C：读取 `selected_for_phase_c=true` 的 GitHub repo
- Phase D：读取 `selected_for_phase_d=true` 的社区资源
- `orchestration.phase_runner`

#### 3.3 输出示例

```json
{
  "schema_version": "dm.discovery-result.v1",
  "candidates": [
    {
      "candidate_id": "cand-acc",
      "name": "ai-calorie-counter",
      "url": "https://github.com/open-kbs/ai-calorie-counter",
      "type": "github_repo",
      "relevance": "high",
      "contribution": "AI 食物识别 + 卡路里估算的核心架构",
      "quick_score": 7.2,
      "quality_signals": {
        "stars": 128,
        "forks": 14,
        "last_updated": "2026-03-01",
        "has_readme": true,
        "issue_activity": "medium",
        "license": "MIT"
      },
      "selected_for_phase_c": true,
      "selected_for_phase_d": false
    },
    {
      "candidate_id": "cand-clawhub-calorie",
      "name": "calorie-counter",
      "url": "clawhub://cnqso/calorie-counter",
      "type": "community_skill",
      "relevance": "high",
      "contribution": "OpenClaw 原生卡路里追踪 skill，可直接参考格式",
      "quick_score": 6.8,
      "quality_signals": {
        "stars": null,
        "forks": null,
        "last_updated": null,
        "has_readme": true,
        "issue_activity": null,
        "license": null
      },
      "selected_for_phase_c": false,
      "selected_for_phase_d": true
    }
  ],
  "search_coverage": [
    {"direction": "AI 食物识别与卡路里估算", "status": "covered", "notes": "Found ACC"},
    {"direction": "营养数据库与食物成分表", "status": "covered", "notes": "Found OpenNutriTracker/FoodYou"},
    {"direction": "OpenClaw 社区已有的饮食/健康 skill", "status": "covered", "notes": "Found calorie-counter, diet-tracker"},
    {"direction": "健康追踪应用的用户体验设计", "status": "partial", "notes": "Need more UX-oriented examples"}
  ],
  "no_candidate_reason": null
}
```

### 4. 行为契约

- 正常路径：并行搜索每个 `search_direction`，输出 3-5 个候选，并明确 coverage。
- 错误路径：
  - 没找到候选：返回 `degraded + E_NO_CANDIDATES`，但 `search_coverage` 仍必须完整
  - API 不可用：忽略 `api_hint`，继续纯 GitHub / 社区搜索
- 幂等性：
  - 在相同查询时间窗下，候选排序应稳定
  - `candidate_id` 由 URL hash 生成，必须稳定
- 超时/重试：
  - 搜索总时长上限 5 分钟
  - 单数据源最多重试 2 次

### 5. 验收标准

必须通过的测试用例：

1. 对 Sim2 卡路里需求，必须至少返回 2 个 GitHub repo 和 1 个 community skill。
2. 当某方向没有候选时，`search_coverage` 必须显示 `partial` 或 `missing`，不能伪装为 `covered`。
3. API hint 缺失时，结果仍能独立产出。

性能预期：

- `< 5 分钟`
- 成本上限 `< $0.15`

不允许的行为：

- 静默丢掉某个 `search_direction`
- 不区分 `github_repo` 与 `community_skill`
- 直接把 stars 作为唯一排序信号

### 6. 设计自由度

可自由发挥：

- 搜索 query 组合
- coarse / fine ranking 策略
- 互补性评分方法

必须严格遵守：

- `need_profile.search_directions` 全覆盖
- `discovery_result.json` 文件名
- 候选类型枚举
- `selected_for_phase_c` / `selected_for_phase_d` 的明确标记

---

## 3.5 `cross-project.synthesis`

### 1. 模块名称与职责

一句话职责：把多个项目提取包、比较信号和社区知识综合成“可编译”的知识选择结果。

### 2. 输入契约

#### 2.1 输入模型

```python
class ExtractedProjectSummary(BaseModel):
    project_id: str
    repo: RepoRef
    top_capabilities: list[str]
    top_constraints: list[str]
    top_failures: list[str]
    evidence_refs: list[EvidenceRef]

class SynthesisInput(BaseModel):
    schema_version: str = "dm.synthesis-input.v1"
    need_profile: NeedProfile
    discovery_result: DiscoveryResult
    project_summaries: list[ExtractedProjectSummary]
    comparison_result: CompareOutput
    community_knowledge: CommunityKnowledge
```

#### 2.2 输入来源

- `need_profile`：Phase A
- `discovery_result`：Phase B
- `project_summaries`：Phase C 提取包摘要
- `comparison_result`：`cross-project.compare`
- `community_knowledge`：Phase D

#### 2.3 输入示例

```json
{
  "schema_version": "dm.synthesis-input.v1",
  "need_profile": {
    "schema_version": "dm.need-profile.v1",
    "raw_input": "我想要做一个记录食物卡路里的 skill",
    "keywords": ["食物", "卡路里", "记录"],
    "intent": "构建卡路里追踪 OpenClaw skill",
    "search_directions": [{"direction": "AI 食物识别与卡路里估算", "priority": "high"}],
    "constraints": ["OpenClaw 平台", "本地存储优先"],
    "quality_expectations": {"accuracy": "<20%"}
  },
  "discovery_result": {
    "schema_version": "dm.discovery-result.v1",
    "candidates": [],
    "search_coverage": [],
    "no_candidate_reason": null
  },
  "project_summaries": [
    {
      "project_id": "acc",
      "repo": {
        "repo_id": "acc",
        "full_name": "open-kbs/ai-calorie-counter",
        "url": "https://github.com/open-kbs/ai-calorie-counter",
        "default_branch": "main",
        "commit_sha": "abc123",
        "local_path": "/tmp/repos/acc"
      },
      "top_capabilities": ["LLM-as-Parser", "daily budget context injection"],
      "top_constraints": ["AI estimate uncertainty"],
      "top_failures": ["portion estimation drift"],
      "evidence_refs": []
    }
  ],
  "comparison_result": {
    "schema_version": "dm.compare-output.v1",
    "domain_id": "nutrition-calorie",
    "compared_projects": ["acc", "foodyo", "ont"],
    "signals": [],
    "metrics": {
      "project_count": 3,
      "atom_count": 127,
      "aligned_count": 24,
      "missing_count": 6,
      "original_count": 8,
      "drifted_count": 2
    }
  },
  "community_knowledge": {
    "schema_version": "dm.community-knowledge.v1",
    "skills": [],
    "tutorials": [],
    "use_cases": []
  }
}
```

### 3. 输出契约

#### 3.1 输出模型

```python
class SynthesisDecision(BaseModel):
    decision_id: str
    statement: str
    decision: Literal["include", "exclude", "option"]
    rationale: str
    source_refs: list[str]
    demand_fit: Priority

class SynthesisConflict(BaseModel):
    conflict_id: str
    category: Literal["semantic", "scope", "architecture", "dependency", "operational", "license"]
    title: str
    positions: list[str]
    recommended_resolution: str
    source_refs: list[str]

class SynthesisReportData(BaseModel):
    schema_version: str = "dm.synthesis-report.v1"
    consensus: list[SynthesisDecision]
    conflicts: list[SynthesisConflict]
    unique_knowledge: list[SynthesisDecision]
    selected_knowledge: list[SynthesisDecision]
    excluded_knowledge: list[SynthesisDecision]
    open_questions: list[str]
```

固定文件：

- `synthesis_report.json`：下游机器消费的 canonical 结果
- `synthesis_report.md`：给人读的镜像渲染

#### 3.2 输出消费者

- `skill-compiler.openclaw`
- `platform-openclaw.validator`
- `orchestration.phase_runner`

#### 3.3 输出示例

```json
{
  "schema_version": "dm.synthesis-report.v1",
  "consensus": [
    {
      "decision_id": "GCD-05",
      "statement": "Progress must be reported as consumed / goal / remaining.",
      "decision": "include",
      "rationale": "All community skills and multiple repos converge on this frame.",
      "source_refs": ["ACC", "ONT", "COM"],
      "demand_fit": "high"
    }
  ],
  "conflicts": [
    {
      "conflict_id": "CONFLICT-02",
      "category": "architecture",
      "title": "Storage format choice",
      "positions": ["Markdown daily log", "SQLite local DB", "JSON message history"],
      "recommended_resolution": "Use JSON + Markdown dual-track.",
      "source_refs": ["ACC", "COM/diet-tracker", "COM/calorie-counter"]
    }
  ],
  "unique_knowledge": [
    {
      "decision_id": "UNIQUE-01",
      "statement": "Use LLM-as-Parser for natural-language meal logging.",
      "decision": "include",
      "rationale": "High leverage and best fit for OpenClaw interaction style.",
      "source_refs": ["ACC"],
      "demand_fit": "high"
    }
  ],
  "selected_knowledge": [
    {
      "decision_id": "SEL-001",
      "statement": "Store profile separately from daily logs.",
      "decision": "include",
      "rationale": "Community consensus and configuration hygiene.",
      "source_refs": ["GCD-06"],
      "demand_fit": "high"
    }
  ],
  "excluded_knowledge": [
    {
      "decision_id": "EX-001",
      "statement": "Track 43 micronutrient fields in v1.",
      "decision": "exclude",
      "rationale": "Too heavy for the requested skill scope.",
      "source_refs": ["FoodYou"],
      "demand_fit": "low"
    }
  ],
  "open_questions": []
}
```

### 4. 行为契约

- 正常路径：
  - 至少输出 4 个区块：共识、冲突、独创、选择结果
  - 每条 `include` / `exclude` 都必须说明 why
- 错误路径：
  - `comparison_result` 缺失：`blocked + E_UPSTREAM_MISSING`
  - 冲突无法消解：`blocked + E_UNRESOLVED_CONFLICT`
- 幂等性：
  - 同一输入下，`decision_id` 和 `conflict_id` 必须稳定
  - Markdown 渲染可以有措辞差异，但 JSON canonical 结果必须稳定
- 超时/重试：
  - 单次上限 5 分钟
  - 最多重试 1 次

### 5. 验收标准

必须通过的测试用例：

1. Sim2 场景下，必须输出至少 1 条冲突和 1 条独创知识。
2. 任何 `selected_knowledge` 项都必须能追溯到 compare / project / community 三者之一。
3. 当存在未解决 license 冲突时，必须进入 `blocked`，不能默认 include。

性能预期：

- `< 5 分钟`
- 成本上限 `< $0.20`

不允许的行为：

- 只有结论，没有 rationale
- 直接把冲突静默吞掉
- 只输出 Markdown，没有结构化 JSON

### 6. 设计自由度

可自由发挥：

- 共识归纳写法
- 冲突分组策略
- 决策 rationale 的组织方式

必须严格遵守：

- `synthesis_report.json` 为 canonical 输出
- `synthesis_report.md` 必须与 JSON 同步
- 冲突类别枚举
- `include` / `exclude` / `option` 决策值

---

## 3.6 `skill-compiler.openclaw`

### 1. 模块名称与职责

一句话职责：把 `synthesis_report.json` 编译成可部署的 OpenClaw `SKILL.md` 及其伴随说明文件。

### 2. 输入契约

#### 2.1 输入模型

```python
class PlatformRules(BaseModel):
    schema_version: str = "dm.platform-rules.v1"
    allowed_tools: list[str]
    metadata_openclaw_whitelist: list[str]
    forbid_frontmatter_fields: list[str]
    storage_prefix: str

class SkillCompilerInput(BaseModel):
    schema_version: str = "dm.skill-compiler-input.v1"
    need_profile: NeedProfile
    synthesis_report: SynthesisReportData
    platform_rules: PlatformRules
```

#### 2.2 输入来源

- `need_profile`：Phase A
- `synthesis_report`：`cross-project.synthesis`
- `platform_rules`：Round 0 冻结

#### 2.3 输入示例

```json
{
  "schema_version": "dm.skill-compiler-input.v1",
  "need_profile": {
    "schema_version": "dm.need-profile.v1",
    "raw_input": "我想要做一个记录食物卡路里的 skill",
    "keywords": ["食物", "卡路里", "记录"],
    "intent": "构建卡路里追踪 OpenClaw skill",
    "search_directions": [],
    "constraints": ["OpenClaw 平台（SKILL.md 格式）", "本地存储优先（~/clawd/memory/）"],
    "quality_expectations": {}
  },
  "synthesis_report": {
    "schema_version": "dm.synthesis-report.v1",
    "consensus": [],
    "conflicts": [],
    "unique_knowledge": [],
    "selected_knowledge": [
      {
        "decision_id": "SEL-001",
        "statement": "Store profile separately from daily logs.",
        "decision": "include",
        "rationale": "Community consensus.",
        "source_refs": ["GCD-06"],
        "demand_fit": "high"
      }
    ],
    "excluded_knowledge": [],
    "open_questions": []
  },
  "platform_rules": {
    "schema_version": "dm.platform-rules.v1",
    "allowed_tools": ["exec", "read", "write"],
    "metadata_openclaw_whitelist": ["always", "emoji", "homepage", "skillKey", "primaryEnv", "os", "requires", "install"],
    "forbid_frontmatter_fields": ["cron"],
    "storage_prefix": "~/clawd/"
  }
}
```

### 3. 输出契约

#### 3.1 输出模型

```python
class SkillBuildManifest(BaseModel):
    schema_version: str = "dm.skill-build-manifest.v1"
    skill_name: str
    selected_decision_ids: list[str]
    omitted_decision_ids: list[str]
    platform_transformations: list[str]
    output_files: list[str]

class SkillCompilerOutput(BaseModel):
    schema_version: str = "dm.skill-compiler-output.v1"
    build_manifest: SkillBuildManifest
    skill_md_path: str
    provenance_md_path: str
    limitations_md_path: str
    readme_md_path: str
```

固定文件：

- `SKILL.md`
- `PROVENANCE.md`
- `LIMITATIONS.md`
- `README.md`
- `skill_build_manifest.json`

#### 3.2 输出消费者

- `platform-openclaw.validator`
- `orchestration.phase_runner`

#### 3.3 输出示例

```json
{
  "schema_version": "dm.skill-compiler-output.v1",
  "build_manifest": {
    "schema_version": "dm.skill-build-manifest.v1",
    "skill_name": "calorie-tracker",
    "selected_decision_ids": ["GCD-05", "GCD-06", "UNIQUE-01"],
    "omitted_decision_ids": ["EX-001"],
    "platform_transformations": [
      "mapped allowed-tools to exec/read/write",
      "removed cron from frontmatter",
      "normalized storage paths to ~/clawd/"
    ],
    "output_files": ["SKILL.md", "README.md", "PROVENANCE.md", "LIMITATIONS.md"]
  },
  "skill_md_path": "delivery/SKILL.md",
  "provenance_md_path": "delivery/PROVENANCE.md",
  "limitations_md_path": "delivery/LIMITATIONS.md",
  "readme_md_path": "delivery/README.md"
}
```

### 4. 行为契约

- 正常路径：
  - 从 `selected_knowledge` 编译出 `SKILL.md`
  - 把平台不支持但仍需要解释的内容写入 `README.md`
  - 所有来源映射写入 `PROVENANCE.md`
- 错误路径：
  - 有 unresolved conflict：`blocked + E_UNRESOLVED_CONFLICT`
  - 缺少 `platform_rules`：`blocked + E_UPSTREAM_MISSING`
- 幂等性：
  - 同一输入下，`skill_build_manifest.json` 必须稳定
  - `SKILL.md` 允许注释顺序不同，但 frontmatter 关键字段和 workflow 不得漂移
- 超时/重试：
  - 单次运行上限 3 分钟
  - 最多重试 1 次

### 5. 验收标准

必须通过的测试用例：

1. Sim2 场景能产出包含 `exec/read/write` 的合法 `SKILL.md`。
2. 当 synthesis 里有 `option` 但没有 resolution 时，编译器必须 `blocked`。
3. `PROVENANCE.md` 至少列出所有被采纳项目的 URL 和 license。

性能预期：

- `< 3 分钟`
- 成本上限 `< $0.10`

不允许的行为：

- 直接把 `cron` 留在 frontmatter
- 默默丢弃 `selected_knowledge`
- 未写 `PROVENANCE.md`

### 6. 设计自由度

可自由发挥：

- 模板组织
- workflow 文字风格
- README 编排

必须严格遵守：

- 输出文件名
- OpenClaw `allowed-tools` 和 metadata 白名单
- `~/clawd/` 路径规范
- `skill_build_manifest.json`

---

## 3.7 `platform-openclaw.validator`

### 1. 模块名称与职责

一句话职责：对 skill bundle 做 OpenClaw 静态校验和多维门控，返回 PASS / REVISE / BLOCKED。

### 2. 输入契约

#### 2.1 输入模型

```python
class SkillBundlePaths(BaseModel):
    skill_md_path: str
    readme_md_path: str
    provenance_md_path: str
    limitations_md_path: str

class ValidationInput(BaseModel):
    schema_version: str = "dm.validation-input.v1"
    need_profile: NeedProfile
    synthesis_report: SynthesisReportData
    skill_bundle: SkillBundlePaths
    platform_rules: PlatformRules
```

#### 2.2 输入来源

- `need_profile`：Phase A
- `synthesis_report`：Phase E
- `skill_bundle`：`skill-compiler.openclaw`
- `platform_rules`：Round 0 冻结

#### 2.3 输入示例

```json
{
  "schema_version": "dm.validation-input.v1",
  "need_profile": {
    "schema_version": "dm.need-profile.v1",
    "raw_input": "我想要做一个记录食物卡路里的 skill",
    "keywords": ["食物", "卡路里"],
    "intent": "构建卡路里 skill",
    "search_directions": [],
    "constraints": ["OpenClaw 平台"],
    "quality_expectations": {}
  },
  "synthesis_report": {
    "schema_version": "dm.synthesis-report.v1",
    "consensus": [],
    "conflicts": [],
    "unique_knowledge": [],
    "selected_knowledge": [],
    "excluded_knowledge": [],
    "open_questions": []
  },
  "skill_bundle": {
    "skill_md_path": "delivery/SKILL.md",
    "readme_md_path": "delivery/README.md",
    "provenance_md_path": "delivery/PROVENANCE.md",
    "limitations_md_path": "delivery/LIMITATIONS.md"
  },
  "platform_rules": {
    "schema_version": "dm.platform-rules.v1",
    "allowed_tools": ["exec", "read", "write"],
    "metadata_openclaw_whitelist": ["always", "emoji", "homepage", "skillKey", "primaryEnv", "os", "requires", "install"],
    "forbid_frontmatter_fields": ["cron"],
    "storage_prefix": "~/clawd/"
  }
}
```

### 3. 输出契约

#### 3.1 输出模型

```python
class ValidationCheck(BaseModel):
    name: Literal[
        "Consistency", "Completeness", "Traceability", "Platform Fit",
        "Conflict Resolution", "License", "Dark Trap Scan"
    ]
    passed: bool
    severity: Literal["blocking", "warning"]
    details: list[str]

class ValidationReport(BaseModel):
    schema_version: str = "dm.validation-report.v1"
    status: Literal["PASS", "REVISE", "BLOCKED"]
    checks: list[ValidationCheck]
    revise_instructions: list[str] = []
```

固定文件：

- `validation_report.json`

#### 3.2 输出消费者

- `orchestration.phase_runner`
- CLI / release 流程

#### 3.3 输出示例

```json
{
  "schema_version": "dm.validation-report.v1",
  "status": "REVISE",
  "checks": [
    {
      "name": "Platform Fit",
      "passed": false,
      "severity": "blocking",
      "details": ["Frontmatter contains forbidden field: cron"]
    },
    {
      "name": "License",
      "passed": false,
      "severity": "warning",
      "details": ["One source project license is unknown"]
    }
  ],
  "revise_instructions": [
    "Remove cron from SKILL.md frontmatter and move it to README installation notes."
  ]
}
```

### 4. 行为契约

- 正常路径：
  - 先跑确定性静态检查
  - 再做有限的 completeness / consistency 判定
  - 输出 PASS / REVISE / BLOCKED
- 错误路径：
  - skill 文件不存在：`blocked + E_UPSTREAM_MISSING`
  - 平台规则缺失：`blocked + E_UPSTREAM_MISSING`
- 幂等性：
  - 完全要求稳定；相同输入必须得到相同 `validation_report.json`
- 超时/重试：
  - Tier 1 静态检查 `< 5 秒`
  - 总体 `< 60 秒`
  - 不应依赖多次重试

### 5. 验收标准

必须通过的测试用例：

1. 当 `allowed-tools` 不是 `exec/read/write` 时，必须给出 blocking failure。
2. 当 `cron` 出现在 frontmatter 时，必须为 `REVISE` 或 `BLOCKED`，不能 PASS。
3. 当 `PROVENANCE.md` 缺少来源 URL 时，Traceability 必须失败。

性能预期：

- 静态部分 `< 5 秒`
- 总体 `< 60 秒`
- 成本上限 `< $0.03`

不允许的行为：

- 只给 PASS/BLOCKED，不给具体 check 细节
- 把 warning 当作 blocking，或反之
- 修改输入文件内容

### 6. 设计自由度

可自由发挥：

- check 执行顺序
- completeness / consistency 的内部判定逻辑
- revise instruction 生成方式

必须严格遵守：

- 7 项检查名
- `validation_report.json` schema
- OpenClaw 平台规则
- 不得自动修复输入文件

---

## 3.8 `orchestration.phase_runner`

### 1. 模块名称与职责

一句话职责：串起 Phase A-H 和 Stage 0-5，在允许降级的前提下把一次用户需求跑成完整交付包。

### 2. 输入契约

#### 2.1 输入模型

```python
class RunnerConfig(BaseModel):
    max_projects: int = Field(default=5, ge=1, le=7)
    enable_stage15: bool = True
    enable_api_enrichment: bool = True
    max_revise_loops: int = Field(default=2, ge=0, le=3)
    allow_degraded_delivery: bool = False

class RequestInput(BaseModel):
    raw_input: str | None = None
    need_profile_path: str | None = None

class PhaseRunnerInput(BaseModel):
    schema_version: str = "dm.phase-runner-input.v1"
    request: RequestInput
    config: RunnerConfig
```

说明：

- `request.raw_input` 和 `request.need_profile_path` 二选一，不能同时为空
- 若已提供 `need_profile_path`，Phase A 跳过

#### 2.2 输入来源

- 用户命令行请求
- 或已有 `need_profile.json`

#### 2.3 输入示例

```json
{
  "schema_version": "dm.phase-runner-input.v1",
  "request": {
    "raw_input": "我想要做一个记录食物卡路里的 skill",
    "need_profile_path": null
  },
  "config": {
    "max_projects": 5,
    "enable_stage15": true,
    "enable_api_enrichment": true,
    "max_revise_loops": 2,
    "allow_degraded_delivery": false
  }
}
```

### 3. 输出契约

#### 3.1 输出模型

```python
class PhaseStatus(BaseModel):
    phase: Literal["A", "B", "C", "D", "E", "F", "G", "H"]
    status: Literal["ok", "degraded", "blocked", "skipped"]
    artifact_paths: list[str] = []
    notes: list[str] = []

class DeliveryBundleManifest(BaseModel):
    skill_md_path: str
    readme_md_path: str
    provenance_md_path: str
    limitations_md_path: str
    validation_report_path: str

class PhaseRunnerOutput(BaseModel):
    schema_version: str = "dm.phase-runner-output.v1"
    run_id: str
    phases: list[PhaseStatus]
    delivery_bundle: DeliveryBundleManifest | None = None
    final_status: Literal["PASS", "REVISE", "BLOCKED"]
```

固定文件：

- `run_manifest.json`

#### 3.2 输出消费者

- `apps.terminal.cli`
- release / packaging
- 后续 API submit 流程

#### 3.3 输出示例

```json
{
  "schema_version": "dm.phase-runner-output.v1",
  "run_id": "run-20260318-calorie-001",
  "phases": [
    {"phase": "A", "status": "ok", "artifact_paths": ["runs/run-20260318-calorie-001/need_profile.json"], "notes": []},
    {"phase": "B", "status": "ok", "artifact_paths": ["runs/run-20260318-calorie-001/discovery_result.json"], "notes": []},
    {"phase": "C", "status": "ok", "artifact_paths": ["runs/run-20260318-calorie-001/projects/acc/"], "notes": []},
    {"phase": "D", "status": "ok", "artifact_paths": ["runs/run-20260318-calorie-001/community_knowledge.json"], "notes": []},
    {"phase": "E", "status": "ok", "artifact_paths": ["runs/run-20260318-calorie-001/synthesis_report.json", "runs/run-20260318-calorie-001/synthesis_report.md"], "notes": []},
    {"phase": "F", "status": "ok", "artifact_paths": ["runs/run-20260318-calorie-001/delivery/SKILL.md"], "notes": []},
    {"phase": "G", "status": "ok", "artifact_paths": ["runs/run-20260318-calorie-001/validation_report.json"], "notes": []},
    {"phase": "H", "status": "ok", "artifact_paths": ["runs/run-20260318-calorie-001/delivery/README.md"], "notes": []}
  ],
  "delivery_bundle": {
    "skill_md_path": "runs/run-20260318-calorie-001/delivery/SKILL.md",
    "readme_md_path": "runs/run-20260318-calorie-001/delivery/README.md",
    "provenance_md_path": "runs/run-20260318-calorie-001/delivery/PROVENANCE.md",
    "limitations_md_path": "runs/run-20260318-calorie-001/delivery/LIMITATIONS.md",
    "validation_report_path": "runs/run-20260318-calorie-001/validation_report.json"
  },
  "final_status": "PASS"
}
```

### 4. 行为契约

- 正常路径：
  - `A -> B -> (C,D 并行) -> E -> F -> G -> H`
  - 若 G 返回 `REVISE`，自动回到 F，最多 `max_revise_loops`
- 错误路径：
  - B 没有候选：返回 `blocked + E_NO_CANDIDATES`
  - C 某个项目提取失败：允许 `degraded`，只要剩余项目数量仍 `>= 2`
  - API 不可用：跳过 enrichment，继续本地工作
- 幂等性：
  - 相同 `raw_input`、相同选中项目和相同 commit 输入下，`run_manifest.json` 的 phase status 和 artifact 路径结构必须稳定
- 超时/重试：
  - 单次完整 run 上限 30 分钟
  - F/G revise 最多 2 轮
  - 外部查询重试受 discovery 自身策略约束

### 5. 验收标准

必须通过的测试用例：

1. Sim2 卡路里场景必须从 raw_input 跑到完整 delivery bundle。
2. 当 API 关闭时，仍必须成功跑完 A-H。
3. 当 G 返回 `REVISE` 时，必须回到 F，而不是整条管线从头重跑。

性能预期：

- 3-5 项目全流程 `< 30 分钟`
- 成本上限 `< $2.50 / run`

不允许的行为：

- 跳过 `validation_report.json`
- 某 phase 失败后静默继续，不记录在 `run_manifest.json`
- 在没有明确标记 `degraded` 的情况下忽略失败项目

### 6. 设计自由度

可自由发挥：

- phase orchestration 的内部状态机
- 并发实现
- artifact 目录组织细节

必须严格遵守：

- Phase 顺序
- `run_manifest.json`
- G 的 revise loop 上限
- API 可选、不依赖

## 4. 赛马评审时的统一清单

每个选手交付必须包含：

1. 模块代码
2. 单元测试
3. 至少 1 条基于 Sim2 或等价 fixture 的集成测试
4. `README.md`
5. `DECISIONS.md`

评审必须检查：

- schema 是否完全一致
- error path 是否按本文定义返回
- 性能是否在预算内
- 有没有偷改上游 / 下游 contract
- fixture 是否能复现

## 3.9 `domain-graph.snapshot_builder`

### 1. 模块名称与职责

一句话职责：将多个项目的 fingerprint、compare 信号和 synthesis 结论聚合为一份领域知识快照（Domain Bricks + Atom Clusters + DOMAIN_TRUTH.md），供 API 存储和终端注入使用。

### 2. 输入契约

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

### 3. 输出契约

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

### 4. 行为契约

- 正常路径：
  - 从 fingerprints 中收集所有 knowledge_atoms
  - 用 compare_output 的 signals 判断共识/分歧
  - 将 ALIGNED + 高 support 的原子升级为 DomainBrick
  - 语义相似的原子聚类为 AtomCluster
  - 生成 DOMAIN_TRUTH.md（markdown 格式的领域真相摘要）
  - 写入 DOMAIN_BRICKS.json、atoms.parquet、domain_map.sqlite
- 错误路径：
  - fingerprints 为空：返回 `blocked + E_INPUT_INVALID`
  - compare_output 格式错误：返回 `blocked + E_SCHEMA_MISMATCH`
  - 没有任何原子达到 min_support_for_brick：返回 `degraded`，bricks 为空列表
- Brick 生成规则：
  - 只有 support_count >= `min_support_for_brick` 的知识才能成为 brick
  - CONTESTED/DIVERGENT signal 的原子不生成 brick，记入 DOMAIN_TRUTH.md 的争议区
  - brick_id 格式：`B-{domain_id}-{sequence:03d}`
- 幂等性：
  - 相同输入产出相同 bricks（顺序可不同，但 brick_id 稳定）

### 5. 验收标准

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

### 6. 设计自由度

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

## 3.10 `apps.preextract-api.read`

### 1. 模块名称与职责

一句话职责：基于 FastAPI 提供只读 API，按领域查询预提取的知识快照（bricks/atoms/truth/deprecations/health）。

### 2. 输入契约

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

### 3. 输出契约

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

### 4. 行为契约

- 正常路径：
  - 启动时扫描 `data_dir`，发现所有 `{domain_id}/snapshot_manifest.json`
  - 响应只读查询，不修改任何文件
  - atoms 端点支持按 knowledge_type、confidence、keyword 过滤和分页
- 错误路径：
  - domain_id 不存在：返回 HTTP 404 `{"detail": "Domain not found: {id}"}`
  - snapshot 文件损坏：返回 HTTP 500 `{"detail": "Snapshot corrupted for domain: {id}"}`
  - health 端点 project 不存在：返回 `overall_status: "unknown"` + 空 health_md
- 热加载：
  - 支持 `POST /admin/reload`（可选）或启动时一次性加载
  - 不要求实时监听文件变化

### 5. 验收标准

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

### 6. 设计自由度

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

## 5. 最后建议

这 8 份规格里，真正不能漂移的不是 prompt，而是 4 件事：

1. artifact 名称
2. schema 结构
3. 错误码
4. phase 边界

只要这 4 件事冻结，4 个选手可以大胆发挥实现路径；如果这 4 件事没冻结，赛马最后会退化成“谁改 contract 更快谁赢”。

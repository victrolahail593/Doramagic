# 赛马任务: runner (选手: s3-gemini)

以下是完整的任务说明和所有需要的上下文。请直接开始编码。
所有输出文件写到: races/r06/runner/s3-gemini/

--- FILE: races/r06/runner/BRIEF.md ---
# Race Brief: Phase Runner (编排核心)

> **Race ID**: r06-runner
> **赛道**: G
> **重要**: 这是全管线的串联模块

## 任务

实现 Phase Runner：将所有已实现模块串联为完整的单项目提取管线（Stage 0 → Stage 1 → Stage 1.5 → Stage 2/3 → Stage 3.5 → Stage 4.5 → Stage 5）。

## 管线流程

```
输入: repo_url 或 local_path
  │
  ▼ Stage 0: 确定性提取
  │  → repo_facts.json + project_narrative
  │  → 框架检测 → 积木注入（如有）
  │
  ▼ Stage 1: 灵魂发现 (Q1-Q7 + WHY recoverability)
  │  → 00-soul.md + findings + hypotheses
  │
  ▼ Stage 1.5: Agentic Exploration (可选，adapter 存在时)
  │  → promoted_claims + exploration_log
  │
  ▼ Stage 2: 概念提取 → CC-*.md
  ▼ Stage 3: 规则提取 → DR-*.md
  │
  ▼ Stage 3.5: 验证 + 置信度标注 + DSD
  │  → evidence_tags + verdict + DSD report
  │
  ▼ Stage 4.5: Knowledge Compiler
  │  → compiled_knowledge.md
  │
  ▼ Stage 5: 组装
  │  → CLAUDE.md + .cursorrules + advisor-brief.md
  │
  输出: inject/ 目录
```

## 已实现的模块（你要调用的）

| 模块 | 路径 | 调用方式 |
|------|------|---------|
| Stage 1.5 Agentic | `packages/extraction/doramagic_extraction/stage15_agentic.py` | `run_stage15_agentic(input, adapter, router)` |
| Knowledge Compiler | `packages/extraction/doramagic_extraction/knowledge_compiler.py` | `compile_knowledge(output_dir, budget)` |
| Confidence System | `packages/extraction/doramagic_extraction/confidence_system.py` | `run_evidence_tagging(cards)` |
| DSD | `packages/extraction/doramagic_extraction/deceptive_source_detection.py` | `run_dsd_checks(cards, repo_facts, community_signals)` |
| 积木注入 | （待合并，假设接口如上 BRIEF） | `load_and_inject_bricks(frameworks, bricks_dir)` |
| Assemble | `skills/soul-extractor/scripts/assemble_output.py` | `assemble(output_dir)` |
| Validate | `skills/soul-extractor/scripts/validate_extraction.py` | `validate_all(output_dir)` |
| Extract Facts | `skills/soul-extractor/scripts/extract_repo_facts.py` | CLI: `--repo-path --output-dir` |

**Stage 1/2/3/4 仍由 LLM 通过 SKILL.md 指令执行**（在 OpenClaw 中）。Phase Runner 负责在模块之间传递数据和编排调用顺序。

## 接口

```python
def run_single_project_pipeline(
    repo_path: str,
    output_dir: str,
    adapter: LLMAdapter | None = None,
    router: CapabilityRouter | None = None,
    config: PipelineConfig | None = None,
) -> PipelineResult:
    """
    运行单项目完整提取管线。
    Stage 1/2/3/4 在 OpenClaw 中由 SKILL.md 驱动，不在此处调用。
    此函数编排 Stage 0 + Stage 1.5 + Stage 3.5 增强 + Stage 4.5 + Stage 5 的确定性部分。
    """

class PipelineConfig(BaseModel):
    enable_stage15: bool = True
    enable_bricks: bool = True
    enable_dsd: bool = True
    bricks_dir: str = "bricks/"
    knowledge_budget: int = 1800
    skip_assembly: bool = False

class PipelineResult(BaseModel):
    stages_completed: list[str]
    stages_skipped: list[str]
    stages_failed: list[str]
    output_dir: str
    inject_dir: str | None
    dsd_report: dict | None
    total_cards: int
    total_bricks_loaded: int
```

## 降级策略

| 场景 | 行为 |
|------|------|
| adapter=None | 跳过 Stage 1.5，其余正常 |
| bricks_dir 不存在 | 跳过积木注入，其余正常 |
| Stage 3.5 验证失败 | 记录 stages_failed，不继续到 Stage 4.5 |
| DSD 返回 SUSPICIOUS | 记录 WARNING，继续（不 BLOCK） |
| assemble 失败 | 记录 stages_failed，返回已有产出 |

## 模型无关

所有 LLM 调用通过 adapter。Stage 0/3.5/4.5/5 纯确定性。

## Deliverables

输出到 `races/r06/runner/{your-racer-id}/`:
1. `phase_runner.py` — 主编排实现
2. `tests/test_phase_runner.py` — 测试（mock adapter + fixture）
3. `DECISIONS.md`

--- END FILE ---

--- FILE: packages/contracts/doramagic_contracts/extraction.py ---
"""提取管线相关模型 — Stage 0/1/1.5/3/3.5。"""

from __future__ import annotations

from typing import Optional, Literal

from pydantic import BaseModel, Field

from doramagic_contracts.base import (
    Confidence,
    EvidenceRef,
    EvidenceTag,
    KnowledgeType,
    PolicyAction,
    Priority,
    RepoRef,
    Verdict,
)

# --- Stage 0 ---


class RepoFacts(BaseModel):
    """Stage 0 确定性提取输出。"""

    schema_version: str = "dm.repo-facts.v1"
    repo: RepoRef
    languages: list[str]
    frameworks: list[str]
    entrypoints: list[str]
    commands: list[str]
    storage_paths: list[str]
    dependencies: list[str]
    repo_summary: str
    project_narrative: str = ""  # v1.1: 50-100 词确定性叙事摘要，所有子代理共享上下文


# --- Stage 1 ---


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


class Stage1Finding(BaseModel):
    finding_id: str
    question_key: Literal["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7"]
    knowledge_type: KnowledgeType
    title: str
    statement: str
    confidence: Confidence
    evidence_refs: list[EvidenceRef]
    # 置信度体系 (v1.1)
    evidence_tags: list[EvidenceTag] = []
    verdict: Optional[Verdict] = None
    policy_action: Optional[PolicyAction] = None


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


class WHYRecoverability(BaseModel):
    """WHY 可恢复性评估 — Stage 1 Q6 前置判断。"""

    recoverable: bool
    reason: str
    confidence: Confidence = "medium"


class Stage1ScanOutput(BaseModel):
    schema_version: str = "dm.stage1-scan-output.v1"
    repo: RepoRef
    findings: list[Stage1Finding]
    hypotheses: list[Hypothesis]
    coverage: Stage1Coverage
    recommended_for_stage15: bool
    why_recoverability: Optional[WHYRecoverability] = None  # v1.1


# --- Stage 1.5 ---


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


class ExplorationLogEntry(BaseModel):
    step_id: str
    round_index: int = Field(ge=1)
    tool_name: Literal[
        "read_artifact", "list_tree", "search_repo", "read_file", "append_finding"
    ]
    tool_input: dict
    observation: str
    produced_evidence_refs: list[EvidenceRef] = []


class ClaimRecord(BaseModel):
    claim_id: str
    statement: str
    status: Literal["confirmed", "rejected", "pending", "inference"]
    confidence: Confidence
    hypothesis_id: Optional[str] = None
    supporting_step_ids: list[str]
    evidence_refs: list[EvidenceRef]
    # 置信度体系 (v1.1)
    evidence_tags: list[EvidenceTag] = []
    verdict: Optional[Verdict] = None
    policy_action: Optional[PolicyAction] = None


class Stage15Summary(BaseModel):
    resolved_hypotheses: list[str]
    unresolved_hypotheses: list[str]
    termination_reason: Literal[
        "all_hypotheses_resolved",
        "no_information_gain",
        "budget_exhausted",
        "manual_skip",
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

--- END FILE ---

--- FILE: packages/contracts/doramagic_contracts/envelope.py ---
"""统一返回 Envelope + 错误码 — 所有赛马模块必须遵守。"""

from __future__ import annotations

from typing import Optional, Generic, Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class RunMetrics(BaseModel):
    """模块运行指标。"""

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
    """所有赛马模块的统一返回格式。"""

    schema_version: str = "dm.module-envelope.v1"
    module_name: str
    status: Literal["ok", "degraded", "blocked", "error"]
    error_code: Optional[str] = None
    warnings: list[WarningItem] = []
    data: Optional[T] = None
    metrics: RunMetrics


# 统一错误码
class ErrorCodes:
    INPUT_INVALID = "E_INPUT_INVALID"
    UPSTREAM_MISSING = "E_UPSTREAM_MISSING"
    SCHEMA_MISMATCH = "E_SCHEMA_MISMATCH"
    TIMEOUT = "E_TIMEOUT"
    RETRY_EXHAUSTED = "E_RETRY_EXHAUSTED"
    BUDGET_EXCEEDED = "E_BUDGET_EXCEEDED"
    NO_CANDIDATES = "E_NO_CANDIDATES"
    NO_HYPOTHESES = "E_NO_HYPOTHESES"
    PLATFORM_VIOLATION = "E_PLATFORM_VIOLATION"
    UNRESOLVED_CONFLICT = "E_UNRESOLVED_CONFLICT"
    VALIDATION_BLOCKED = "E_VALIDATION_BLOCKED"

--- END FILE ---

--- FILE: packages/shared_utils/doramagic_shared_utils/llm_adapter.py ---
"""模型无关 LLM 调用适配器 — 统一不同 provider 的调用接口。

管线代码中不出现 anthropic.Client() 或 google.GenerativeAI()。
所有 LLM 调用通过此适配器。

用法:
    adapter = LLMAdapter()
    response = await adapter.generate("claude-opus-4-6", messages=[...])
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Optional, Sequence


@dataclass
class LLMMessage:
    """统一消息格式。"""

    role: str  # "system", "user", "assistant", "tool"
    content: str
    tool_call_id: Optional[str] = None
    tool_calls: Optional[list[dict]] = None


@dataclass
class LLMToolDefinition:
    """统一工具定义格式。"""

    name: str
    description: str
    parameters: dict  # JSON Schema


@dataclass
class LLMResponse:
    """统一响应格式。"""

    content: str
    model_id: str
    finish_reason: str = "stop"  # stop, tool_use, length, error
    tool_calls: list[dict] = field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0


def _provider_from_model_id(model_id: str) -> str:
    """从 model_id 推断 provider。也可通过 RoutingResult.provider 显式指定。"""
    prefixes = {
        "claude": "anthropic",
        "gpt": "openai",
        "o1": "openai",
        "o3": "openai",
        "o4": "openai",
        "gemini": "google",
        "glm": "zhipu",
        "minimax": "minimax",
    }
    model_lower = model_id.lower()
    for prefix, provider in prefixes.items():
        if model_lower.startswith(prefix):
            return provider
    return "unknown"


class LLMAdapter:
    """
    统一 LLM 调用接口。

    每个 provider 的具体实现延迟加载（首次调用时 import）。
    这样不依赖用户安装所有 SDK — 只需安装自己用的 provider 的 SDK。
    """

    def __init__(self, provider_override: Optional[str] = None, config: Any = None):
        if config is not None and hasattr(config, 'provider'):
            self._provider_override = config.provider
        else:
            self._provider_override = provider_override
        self._clients: dict[str, Any] = {}
        self._default_model: str = ""  # set by router or config

    def chat(
        self,
        messages: Sequence[LLMMessage],
        system: Optional[str] = None,
        *,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """同步调用接口 — S1-Sonnet 风格。内部 async 桥接。"""
        import asyncio
        model_id = self._default_model or "default"
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(
                    asyncio.run,
                    self.generate(model_id, messages, system=system, temperature=temperature, max_tokens=max_tokens)
                ).result()
        return asyncio.run(
            self.generate(model_id, messages, system=system, temperature=temperature, max_tokens=max_tokens)
        )

    async def generate(
        self,
        model_id: str,
        messages: Sequence[LLMMessage],
        *,
        provider: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        system: Optional[str] = None,
    ) -> LLMResponse:
        """统一文本生成接口。"""
        resolved_provider = provider or self._provider_override or _provider_from_model_id(model_id)
        return await self._dispatch(
            resolved_provider, model_id, messages,
            temperature=temperature, max_tokens=max_tokens, system=system,
        )

    async def generate_with_tools(
        self,
        model_id: str,
        messages: Sequence[LLMMessage],
        tools: Sequence[LLMToolDefinition],
        *,
        provider: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        system: Optional[str] = None,
    ) -> LLMResponse:
        """统一工具调用接口。对不支持 tool_use 的模型，回退到 prompt-based 工具选择。"""
        resolved_provider = provider or self._provider_override or _provider_from_model_id(model_id)
        return await self._dispatch_with_tools(
            resolved_provider, model_id, messages, tools,
            temperature=temperature, max_tokens=max_tokens, system=system,
        )

    async def _dispatch(
        self, provider: str, model_id: str, messages: Sequence[LLMMessage], **kwargs
    ) -> LLMResponse:
        """分发到具体 provider 实现。"""
        if provider == "anthropic":
            return await self._call_anthropic(model_id, messages, **kwargs)
        if provider == "openai":
            return await self._call_openai(model_id, messages, **kwargs)
        if provider == "google":
            return await self._call_google(model_id, messages, **kwargs)
        if provider == "mock":
            return self._call_mock(model_id, messages, **kwargs)
        raise NotImplementedError(
            f"Provider '{provider}' not implemented. "
            f"Supported: anthropic, openai, google, mock. "
            f"PRs welcome for: zhipu, minimax."
        )

    async def _dispatch_with_tools(
        self, provider: str, model_id: str, messages: Sequence[LLMMessage],
        tools: Sequence[LLMToolDefinition], **kwargs
    ) -> LLMResponse:
        """分发工具调用到具体 provider。"""
        if provider == "anthropic":
            return await self._call_anthropic_tools(model_id, messages, tools, **kwargs)
        if provider == "openai":
            return await self._call_openai_tools(model_id, messages, tools, **kwargs)
        if provider == "google":
            return await self._call_google_tools(model_id, messages, tools, **kwargs)
        if provider == "mock":
            return self._call_mock(model_id, messages, **kwargs)
        # 不支持工具的 provider → 回退到 prompt-based
        return await self._fallback_prompt_tools(provider, model_id, messages, tools, **kwargs)

    # --- Anthropic ---

    async def _call_anthropic(self, model_id: str, messages: Sequence[LLMMessage], **kwargs) -> LLMResponse:
        import anthropic
        client = self._get_or_create_client("anthropic", lambda: anthropic.AsyncAnthropic())
        api_messages = [{"role": m.role, "content": m.content} for m in messages if m.role != "system"]
        system_text = kwargs.get("system") or next((m.content for m in messages if m.role == "system"), None)
        resp = await client.messages.create(
            model=model_id,
            messages=api_messages,
            max_tokens=kwargs.get("max_tokens", 4096),
            temperature=kwargs.get("temperature", 0.0),
            system=system_text or "",
        )
        return LLMResponse(
            content=resp.content[0].text if resp.content else "",
            model_id=model_id,
            finish_reason=resp.stop_reason or "stop",
            prompt_tokens=resp.usage.input_tokens,
            completion_tokens=resp.usage.output_tokens,
        )

    async def _call_anthropic_tools(
        self, model_id: str, messages: Sequence[LLMMessage],
        tools: Sequence[LLMToolDefinition], **kwargs
    ) -> LLMResponse:
        import anthropic
        client = self._get_or_create_client("anthropic", lambda: anthropic.AsyncAnthropic())
        api_messages = [{"role": m.role, "content": m.content} for m in messages if m.role != "system"]
        system_text = kwargs.get("system") or next((m.content for m in messages if m.role == "system"), None)
        api_tools = [
            {"name": t.name, "description": t.description, "input_schema": t.parameters}
            for t in tools
        ]
        resp = await client.messages.create(
            model=model_id,
            messages=api_messages,
            tools=api_tools,
            max_tokens=kwargs.get("max_tokens", 4096),
            temperature=kwargs.get("temperature", 0.0),
            system=system_text or "",
        )
        tool_calls = []
        text_parts = []
        for block in resp.content:
            if block.type == "tool_use":
                tool_calls.append({"id": block.id, "name": block.name, "arguments": block.input})
            elif block.type == "text":
                text_parts.append(block.text)
        return LLMResponse(
            content="\n".join(text_parts),
            model_id=model_id,
            finish_reason="tool_use" if tool_calls else (resp.stop_reason or "stop"),
            tool_calls=tool_calls,
            prompt_tokens=resp.usage.input_tokens,
            completion_tokens=resp.usage.output_tokens,
        )

    # --- OpenAI ---

    async def _call_openai(self, model_id: str, messages: Sequence[LLMMessage], **kwargs) -> LLMResponse:
        import openai
        client = self._get_or_create_client("openai", lambda: openai.AsyncOpenAI())
        api_messages = [{"role": m.role, "content": m.content} for m in messages]
        resp = await client.chat.completions.create(
            model=model_id,
            messages=api_messages,
            max_tokens=kwargs.get("max_tokens", 4096),
            temperature=kwargs.get("temperature", 0.0),
        )
        choice = resp.choices[0]
        return LLMResponse(
            content=choice.message.content or "",
            model_id=model_id,
            finish_reason=choice.finish_reason or "stop",
            prompt_tokens=resp.usage.prompt_tokens if resp.usage else 0,
            completion_tokens=resp.usage.completion_tokens if resp.usage else 0,
        )

    async def _call_openai_tools(
        self, model_id: str, messages: Sequence[LLMMessage],
        tools: Sequence[LLMToolDefinition], **kwargs
    ) -> LLMResponse:
        import openai
        client = self._get_or_create_client("openai", lambda: openai.AsyncOpenAI())
        api_messages = [{"role": m.role, "content": m.content} for m in messages]
        api_tools = [
            {"type": "function", "function": {"name": t.name, "description": t.description, "parameters": t.parameters}}
            for t in tools
        ]
        resp = await client.chat.completions.create(
            model=model_id,
            messages=api_messages,
            tools=api_tools,
            max_tokens=kwargs.get("max_tokens", 4096),
            temperature=kwargs.get("temperature", 0.0),
        )
        choice = resp.choices[0]
        tool_calls = []
        if choice.message.tool_calls:
            import json as _json
            for tc in choice.message.tool_calls:
                tool_calls.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": _json.loads(tc.function.arguments),
                })
        return LLMResponse(
            content=choice.message.content or "",
            model_id=model_id,
            finish_reason="tool_use" if tool_calls else (choice.finish_reason or "stop"),
            tool_calls=tool_calls,
            prompt_tokens=resp.usage.prompt_tokens if resp.usage else 0,
            completion_tokens=resp.usage.completion_tokens if resp.usage else 0,
        )

    # --- Google ---

    async def _call_google(self, model_id: str, messages: Sequence[LLMMessage], **kwargs) -> LLMResponse:
        from google import genai
        client = self._get_or_create_client(
            "google",
            lambda: genai.Client(api_key=os.environ.get("GOOGLE_API_KEY", "")),
        )
        # Gemini uses a flat prompt or structured contents
        prompt_parts = []
        for m in messages:
            prompt_parts.append(m.content)
        combined = "\n\n".join(prompt_parts)
        resp = client.models.generate_content(
            model=model_id,
            contents=combined,
        )
        return LLMResponse(
            content=resp.text or "",
            model_id=model_id,
            prompt_tokens=getattr(resp, "prompt_token_count", 0) or 0,
            completion_tokens=getattr(resp, "candidates_token_count", 0) or 0,
        )

    async def _call_google_tools(
        self, model_id: str, messages: Sequence[LLMMessage],
        tools: Sequence[LLMToolDefinition], **kwargs
    ) -> LLMResponse:
        # Gemini tool calling — simplified; full impl would use google.genai tool objects
        # 回退到 prompt-based
        return await self._fallback_prompt_tools("google", model_id, messages, tools, **kwargs)

    # --- Mock (for testing) ---

    def _call_mock(self, model_id: str, messages: Sequence[LLMMessage], **kwargs) -> LLMResponse:
        return LLMResponse(
            content="[MOCK] This is a mock response for testing.",
            model_id=model_id,
            finish_reason="stop",
            prompt_tokens=100,
            completion_tokens=20,
        )

    # --- Fallback: prompt-based tool calling ---

    async def _fallback_prompt_tools(
        self, provider: str, model_id: str, messages: Sequence[LLMMessage],
        tools: Sequence[LLMToolDefinition], **kwargs
    ) -> LLMResponse:
        """对不支持原生工具调用的模型，将工具定义注入 system prompt。"""
        import json as _json
        tool_descriptions = []
        for t in tools:
            tool_descriptions.append(
                f"Tool: {t.name}\nDescription: {t.description}\n"
                f"Parameters: {_json.dumps(t.parameters, indent=2)}"
            )
        tool_prompt = (
            "You have access to the following tools. "
            "To use a tool, respond with a JSON object: "
            '{"tool": "tool_name", "arguments": {...}}\n\n'
            + "\n---\n".join(tool_descriptions)
        )
        augmented = [LLMMessage(role="system", content=tool_prompt)] + list(messages)
        return await self._dispatch(provider, model_id, augmented, **kwargs)

    # --- Client management ---

    def _get_or_create_client(self, key: str, factory):
        if key not in self._clients:
            self._clients[key] = factory()
        return self._clients[key]


# --- Config helper ---

@dataclass
class LLMAdapterConfig:
    """Simple config for adapter construction."""
    provider: str = "mock"
    model: str = ""
    api_key_env: str = ""


# --- Mock adapter for testing ---

class MockLLMAdapter(LLMAdapter):
    """Deterministic adapter for unit tests. No real LLM calls.

    Usage:
        adapter = MockLLMAdapter(responses=['{"tool": "read_file", ...}', ...])
        adapter = MockLLMAdapter(response_fn=lambda msgs, sys: '...')
        adapter = MockLLMAdapter()  # uses default_response
    """

    def __init__(
        self,
        responses: Optional[list] = None,
        response_fn: Any = None,
        default_response: str = '{"tool": "append_finding", "arguments": {"status": "pending", "statement": "mock"}}',
    ) -> None:
        super().__init__(provider_override="mock")
        self._responses = list(responses or [])
        self._response_fn = response_fn
        self._default = default_response
        self._call_index = 0
        self._default_model = "mock-model"

    def chat(
        self,
        messages: Sequence[LLMMessage],
        system: Optional[str] = None,
        **kwargs,
    ) -> LLMResponse:
        if self._response_fn is not None:
            content = self._response_fn(messages, system)
        elif self._call_index < len(self._responses):
            content = self._responses[self._call_index]
            self._call_index += 1
        else:
            content = self._default

        total_chars = sum(len(m.content) for m in messages) + len(system or "")
        prompt_tokens = max(10, total_chars // 4)
        completion_tokens = max(5, len(content) // 4)

        return LLMResponse(
            content=content,
            model_id="mock-model",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

    async def generate(self, model_id, messages, **kwargs):
        return self.chat(messages, system=kwargs.get("system"))

    def _call_mock(self, model_id, messages, **kwargs):
        return self.chat(messages, system=kwargs.get("system"))

--- END FILE ---

--- FILE: packages/shared_utils/doramagic_shared_utils/capability_router.py ---
"""模型无关能力路由器 — 管线绑定能力需求，不绑定模型品牌。

用法:
    router = CapabilityRouter.from_config("models.json")
    model_id = router.route(["deep_reasoning", "code_understanding"])
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence

# 管线使用的能力标签
CAPABILITY_DEEP_REASONING = "deep_reasoning"
CAPABILITY_STRUCTURED_EXTRACTION = "structured_extraction"
CAPABILITY_TOOL_CALLING = "tool_calling"
CAPABILITY_CODE_UNDERSTANDING = "code_understanding"

# S1-Sonnet 风格的任务标签（映射到能力标签）
TASK_TOOL_SELECTION = "tool_selection"
TASK_HYPOTHESIS_EVALUATION = "hypothesis_evaluation"
TASK_EVIDENCE_EXTRACTION = "evidence_extraction"
TASK_CLAIM_SYNTHESIS = "claim_synthesis"
TASK_GENERAL = "general"

_TASK_TO_CAPABILITIES = {
    TASK_TOOL_SELECTION: [CAPABILITY_TOOL_CALLING, CAPABILITY_CODE_UNDERSTANDING],
    TASK_HYPOTHESIS_EVALUATION: [CAPABILITY_DEEP_REASONING],
    TASK_EVIDENCE_EXTRACTION: [CAPABILITY_CODE_UNDERSTANDING],
    TASK_CLAIM_SYNTHESIS: [CAPABILITY_DEEP_REASONING],
    TASK_GENERAL: [CAPABILITY_STRUCTURED_EXTRACTION],
}

COST_TIER_ORDER = {"low": 0, "medium": 1, "high": 2}


@dataclass
class ModelDeclaration:
    """用户在 models.json 中声明的可用模型。"""

    model_id: str
    provider: str  # anthropic, google, openai, zhipu, minimax, ...
    capabilities: list[str]
    cost_tier: str = "medium"  # low, medium, high
    api_key_env: str = ""  # 环境变量名
    max_context_tokens: int = 128000
    supports_tool_use: bool = True

    def has_capabilities(self, required: Sequence[str]) -> bool:
        return all(cap in self.capabilities for cap in required)

    def capability_coverage(self, required: Sequence[str]) -> float:
        if not required:
            return 1.0
        matched = sum(1 for cap in required if cap in self.capabilities)
        return matched / len(required)


@dataclass
class RoutingResult:
    """路由结果。"""

    model_id: str
    provider: str
    is_degraded: bool = False  # True = 没有完美匹配，用了最接近的
    missing_capabilities: list[str] = field(default_factory=list)
    cost_tier: str = "medium"


class CapabilityRouter:
    """
    根据用户声明的可用模型和能力需求，选择最合适的模型。

    路由策略:
    - lowest_sufficient: 满足所有能力的最便宜模型
    - highest_available: 满足所有能力的最强模型
    - 如无完美匹配: 选覆盖最多能力的，标记 degraded
    """

    def __init__(
        self,
        models: list[ModelDeclaration] | None = None,
        preference: str = "lowest_sufficient",
        fallback_strategy: str = "degrade_and_warn",
        forced_adapter=None,  # S1-Sonnet 兼容：传入 adapter 后所有路由返回该 adapter
    ):
        self.models = models or []
        self.preference = preference
        self.fallback_strategy = fallback_strategy
        self._forced_adapter = forced_adapter

    @classmethod
    def from_config(cls, config_path: str | Path) -> CapabilityRouter:
        """从 models.json 配置文件加载。"""
        path = Path(config_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"models.json not found: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        models = [ModelDeclaration(**m) for m in data["available_models"]]
        return cls(
            models=models,
            preference=data.get("routing_preference", "lowest_sufficient"),
            fallback_strategy=data.get("fallback_strategy", "degrade_and_warn"),
        )

    def for_task(self, task: str):
        """S1-Sonnet 兼容接口：按任务标签返回 adapter。"""
        if self._forced_adapter is not None:
            return self._forced_adapter
        # 映射 task → capabilities → route → 构建简易 adapter
        caps = _TASK_TO_CAPABILITIES.get(task, [CAPABILITY_STRUCTURED_EXTRACTION])
        result = self.route(caps)
        # 返回一个带 _default_model 的标记对象
        from doramagic_shared_utils.llm_adapter import LLMAdapter
        adapter = LLMAdapter(provider_override=result.provider)
        adapter._default_model = result.model_id
        return adapter

    def route(self, required_capabilities: Sequence[str]) -> RoutingResult:
        """选择满足能力需求的最合适模型。"""
        # 找完美匹配
        perfect = [m for m in self.models if m.has_capabilities(required_capabilities)]

        if perfect:
            selected = self._select_by_preference(perfect)
            return RoutingResult(
                model_id=selected.model_id,
                provider=selected.provider,
                cost_tier=selected.cost_tier,
            )

        # 无完美匹配 — 降级
        if self.fallback_strategy == "degrade_and_warn":
            best = max(self.models, key=lambda m: m.capability_coverage(required_capabilities))
            missing = [cap for cap in required_capabilities if cap not in best.capabilities]
            return RoutingResult(
                model_id=best.model_id,
                provider=best.provider,
                is_degraded=True,
                missing_capabilities=missing,
                cost_tier=best.cost_tier,
            )

        # strict 模式：无匹配则报错
        raise RuntimeError(
            f"No model satisfies capabilities {required_capabilities}. "
            f"Available: {[(m.model_id, m.capabilities) for m in self.models]}"
        )

    def get_all_capable(self, required_capabilities: Sequence[str]) -> list[RoutingResult]:
        """返回所有满足能力需求的模型（用于 GDS 多模型融合）。"""
        results = []
        for m in self.models:
            if m.has_capabilities(required_capabilities):
                results.append(RoutingResult(
                    model_id=m.model_id,
                    provider=m.provider,
                    cost_tier=m.cost_tier,
                ))
        return results

    def route_for_stage(self, stage_name: str) -> RoutingResult:
        """按 Stage 名称路由 — 预定义的能力需求映射。"""
        stage_requirements = {
            "stage0": [],  # 确定性，无 LLM
            "stage1": [CAPABILITY_DEEP_REASONING, CAPABILITY_CODE_UNDERSTANDING],
            "stage1.5": [CAPABILITY_TOOL_CALLING, CAPABILITY_CODE_UNDERSTANDING],
            "stage2": [CAPABILITY_STRUCTURED_EXTRACTION],
            "stage3": [CAPABILITY_STRUCTURED_EXTRACTION],
            "stage3.5": [],  # 确定性验证
            "stage4": [CAPABILITY_DEEP_REASONING],
            "stage5": [],  # 确定性组装
            "phase_e": [CAPABILITY_DEEP_REASONING],  # 跨源权衡
            "phase_f": [CAPABILITY_STRUCTURED_EXTRACTION],  # 格式编译
        }
        caps = stage_requirements.get(stage_name, [])
        if not caps:
            # 确定性 stage，返回任意模型（不会实际调用）
            return RoutingResult(model_id="deterministic", provider="none")
        return self.route(caps)

    def _select_by_preference(self, candidates: list[ModelDeclaration]) -> ModelDeclaration:
        if self.preference == "lowest_sufficient":
            return min(candidates, key=lambda m: COST_TIER_ORDER.get(m.cost_tier, 1))
        if self.preference == "highest_available":
            return max(candidates, key=lambda m: COST_TIER_ORDER.get(m.cost_tier, 1))
        return candidates[0]

--- END FILE ---

## 关键约束
1. 不能 import anthropic / import openai / from google.generativeai
2. 所有 LLM 调用通过 LLMAdapter（如果需要 LLM 的话）
3. 纯确定性模块不需要 LLM
4. 输出路径: races/r06/runner/s3-gemini/

## 验收清单
- [ ] 主实现 .py 文件
- [ ] tests/ 目录下的测试文件
- [ ] DECISIONS.md 设计决策文档
- [ ] 所有测试通过
- [ ] 文件都在 races/r06/runner/s3-gemini/ 下（不要写到其他位置）
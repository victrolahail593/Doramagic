"""Agent Loop 核心逻辑 — 真实 LLM 驱动的探索循环。

设计要点:
1. 短轮次交互：每轮 fresh context，不依赖长对话记忆
2. 假说驱动：按 hypothesis_list 顺序探索
3. 三层 Budget 控制：rounds / tool_calls / tokens
4. 终止条件：所有假说解决 / budget 耗尽 / 连续无进展
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional, Sequence

import sys
_CONTRACTS_PATH = Path(__file__).parent.parent.parent.parent / "packages" / "contracts"
if str(_CONTRACTS_PATH) not in sys.path:
    sys.path.insert(0, str(_CONTRACTS_PATH))

_SHARED_PATH = Path(__file__).parent.parent.parent.parent / "packages" / "shared_utils"
if str(_SHARED_PATH) not in sys.path:
    sys.path.insert(0, str(_SHARED_PATH))

from doramagic_contracts.base import EvidenceRef
from doramagic_contracts.extraction import (
    ClaimRecord,
    ExplorationLogEntry,
    Hypothesis,
    Stage15AgenticInput,
    Stage15AgenticOutput,
    Stage15Summary,
    Stage1Finding,
)
from doramagic_contracts.envelope import (
    ErrorCodes,
    ModuleResultEnvelope,
    RunMetrics,
    WarningItem,
)

from doramagic_shared_utils.llm_adapter import LLMAdapter, LLMConfig, ToolCall, ToolResult as LLMToolResult

from .tools import (
    AgentContext,
    ToolExecutor,
    ToolResult,
    get_tool_schemas,
)
from .prompts import (
    SYSTEM_PROMPT,
    PromptContext,
    build_agent_prompt,
    build_context_digest_prompt,
    parse_llm_response,
)


# 优先级排序
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class AgentState:
    """Agent 循环状态。"""
    current_round: int = 0
    current_hypothesis_index: int = 0
    tool_calls_used: int = 0
    prompt_tokens_used: int = 0
    completion_tokens_used: int = 0
    llm_calls: int = 0
    consecutive_no_gain: int = 0
    resolved_hypotheses: list[str] = field(default_factory=list)
    unresolved_hypotheses: list[str] = field(default_factory=list)
    exploration_log: list[ExplorationLogEntry] = field(default_factory=list)
    claim_ledger: list[ClaimRecord] = field(default_factory=list)
    warnings: list[WarningItem] = field(default_factory=list)
    termination_reason: str = "unknown"
    budget_exceeded: bool = False


class AgentLoop:
    """真实 LLM 驱动的 Agent 探索循环。"""

    def __init__(
        self,
        input_data: Stage15AgenticInput,
        llm_adapter: LLMAdapter,
    ):
        self.input = input_data
        self.llm = llm_adapter
        self.state = AgentState()

        # 排序后的假说列表
        self.ordered_hypotheses = self._sort_hypotheses(input_data.stage1_output.hypotheses)

        # Agent 上下文
        repo_root = Path(input_data.repo.local_path).expanduser().resolve()
        self.ctx = AgentContext(
            repo_root=repo_root,
            repo_id=input_data.repo.repo_id,
            stage1_findings=input_data.stage1_output.findings,
            hypotheses=self.ordered_hypotheses,
            repo_facts=input_data.repo_facts.model_dump(),
            exploration_log=[],
            claim_ledger=[],
        )

        # 工具执行器
        self.executor = ToolExecutor(self.ctx)

        # 统计
        self.start_time = time.perf_counter()

    def _sort_hypotheses(self, hypotheses: Sequence[Hypothesis]) -> list[Hypothesis]:
        """按优先级排序假说。"""
        return sorted(
            list(hypotheses),
            key=lambda h: (PRIORITY_ORDER.get(h.priority, 99), h.hypothesis_id),
        )

    def _estimate_tokens(self, *parts: str) -> int:
        """估算 token 数量。"""
        total_chars = sum(len(p) for p in parts if p)
        return max(80, total_chars // 4)

    def _budget_exceeded(self) -> bool:
        """检查是否超出预算。"""
        if self.state.current_round >= self.input.budget.max_rounds:
            return True
        if self.state.tool_calls_used >= self.input.budget.max_tool_calls:
            return True
        if self.state.prompt_tokens_used >= self.input.budget.max_prompt_tokens:
            return True
        return False

    def _tool_enabled(self, tool_name: str) -> bool:
        """检查工具是否启用。"""
        toolset = self.input.toolset
        if tool_name == "read_artifact":
            return toolset.allow_read_artifact
        elif tool_name == "list_tree":
            return toolset.allow_list_tree
        elif tool_name == "search_repo":
            return toolset.allow_search_repo
        elif tool_name == "read_file":
            return toolset.allow_read_file
        elif tool_name == "append_finding":
            return toolset.allow_append_finding
        return False

    def _build_prompt_context(self) -> PromptContext:
        """构建 Prompt 上下文。"""
        # 当前假说
        current_hypothesis = None
        if self.state.current_hypothesis_index < len(self.ordered_hypotheses):
            current_hypothesis = self.ordered_hypotheses[self.state.current_hypothesis_index]

        # 待解决和已解决的假说
        pending = [
            h.hypothesis_id
            for h in self.ordered_hypotheses
            if h.hypothesis_id not in self.state.resolved_hypotheses
        ]

        # 最近的探索步骤
        recent_steps = [
            {
                "step_id": e.step_id,
                "tool_name": e.tool_name,
                "observation": e.observation[:200],
            }
            for e in self.state.exploration_log[-10:]
        ]

        # 最近的 claims
        recent_claims = [
            {
                "claim_id": c.claim_id,
                "status": c.status,
                "statement": c.statement[:100],
            }
            for c in self.state.claim_ledger[-5:]
        ]

        # 可用工具
        available_tools = []
        for tool_name in ["read_artifact", "list_tree", "search_repo", "read_file", "append_finding"]:
            if self._tool_enabled(tool_name):
                available_tools.append(tool_name)

        return PromptContext(
            repo_id=self.input.repo.repo_id,
            current_round=self.state.current_round,
            max_rounds=self.input.budget.max_rounds,
            current_hypothesis=current_hypothesis,
            pending_hypotheses=pending,
            resolved_hypotheses=self.state.resolved_hypotheses,
            recent_steps=recent_steps,
            recent_claims=recent_claims,
            repo_summary=self.input.repo_facts.repo_summary,
            entrypoints=self.input.repo_facts.entrypoints,
            available_tools=available_tools,
            tool_calls_used=self.state.tool_calls_used,
            max_tool_calls=self.input.budget.max_tool_calls,
        )

    def _create_tool_executor(self) -> Callable[[ToolCall], LLMToolResult]:
        """创建工具执行函数供 LLMAdapter 使用。"""
        def execute(tc: ToolCall) -> LLMToolResult:
            if not self._tool_enabled(tc.name):
                return LLMToolResult(
                    tool_call_id=tc.tool_call_id,
                    content=f"Tool '{tc.name}' is disabled.",
                    is_error=True,
                )

            if self._budget_exceeded():
                return LLMToolResult(
                    tool_call_id=tc.tool_call_id,
                    content="Budget exceeded. No more tool calls allowed.",
                    is_error=True,
                )

            result = self.executor.execute(tc.name, tc.arguments)

            # 记录探索步骤
            step_id = self.ctx.next_step_id()
            step = ExplorationLogEntry(
                step_id=step_id,
                round_index=self.state.current_round,
                tool_name=tc.name,
                tool_input=tc.arguments,
                observation=result.observation if result.success else (result.error_message or "Unknown error"),
                produced_evidence_refs=result.evidence_refs,
            )
            self.state.exploration_log.append(step)
            self.ctx.exploration_log = self.state.exploration_log

            # 更新统计
            self.state.tool_calls_used += 1
            tokens = self._estimate_tokens(
                json.dumps(tc.arguments, ensure_ascii=False),
                result.observation or "",
            )
            self.state.prompt_tokens_used += tokens

            return LLMToolResult(
                tool_call_id=tc.tool_call_id,
                content=result.observation if result.success else (result.error_message or "Tool execution failed"),
                is_error=not result.success,
            )

        return execute

    async def run_one_round(self) -> bool:
        """执行一轮探索循环。

        Returns:
            True 如果应该继续，False 如果应该终止
        """
        self.state.current_round += 1

        # 检查预算
        if self._budget_exceeded():
            self.state.budget_exceeded = True
            self.state.termination_reason = "budget_exhausted"
            return False

        # 检查是否有更多假说需要处理
        if self.state.current_hypothesis_index >= len(self.ordered_hypotheses):
            self.state.termination_reason = "all_hypotheses_resolved"
            return False

        # 构建 prompt
        prompt_ctx = self._build_prompt_context()
        user_prompt = build_agent_prompt(prompt_ctx)

        # 更新 token 统计
        self.state.prompt_tokens_used += self._estimate_tokens(SYSTEM_PROMPT, user_prompt)

        # 获取工具 schemas
        tool_schemas = get_tool_schemas(format="openai")

        # 调用 LLM
        try:
            response = await self.llm.chat(
                messages=[{"role": "user", "content": user_prompt}],
                tools=tool_schemas,
                system=SYSTEM_PROMPT,
            )
            self.state.llm_calls += 1

            # 更新 token 统计
            if response.usage:
                self.state.prompt_tokens_used += response.usage.get("prompt_tokens", 0)
                self.state.completion_tokens_used += response.usage.get("completion_tokens", 0)

            # 检查是否有工具调用
            tool_calls_raw = response.raw.get("tool_calls") if response.raw else None

            if tool_calls_raw:
                # 执行工具调用
                for tc_raw in tool_calls_raw:
                    tc = ToolCall(
                        tool_call_id=tc_raw["id"],
                        name=tc_raw["function"]["name"],
                        arguments=tc_raw["function"]["arguments"],
                    )

                    # 执行工具
                    executor = self._create_tool_executor()
                    result = executor(tc)

                    # 检查是否是 append_finding（可能改变假说状态）
                    if tc.name == "append_finding":
                        self._process_finding_result(tc.arguments)

                    if self._budget_exceeded():
                        self.state.budget_exceeded = True
                        break

                # 检查当前假说是否已解决
                self._check_hypothesis_resolved()

            else:
                # 没有工具调用，可能是总结或放弃
                parsed = parse_llm_response(response.content, None)

                if parsed["action"] == "summary":
                    # LLM 认为分析完成，移动到下一个假说
                    self._advance_hypothesis()

                elif parsed["action"] == "continue":
                    # LLM 还在想，再给一次机会
                    self.state.consecutive_no_gain += 1
                    if self.state.consecutive_no_gain >= self.input.budget.stop_after_no_gain_rounds:
                        self.state.termination_reason = "no_information_gain"
                        return False

            return True

        except Exception as e:
            self.state.warnings.append(WarningItem(
                code="W_LLM_ERROR",
                message=f"LLM call failed: {str(e)}",
            ))
            self.state.consecutive_no_gain += 1
            if self.state.consecutive_no_gain >= 2:
                return False
            return True

    def _process_finding_result(self, args: dict):
        """处理 append_finding 的结果。"""
        status = args.get("status", "pending")
        hypothesis_id = args.get("hypothesis_id")

        if status in ("confirmed", "rejected") and hypothesis_id:
            # 假说已解决
            if hypothesis_id not in self.state.resolved_hypotheses:
                self.state.resolved_hypotheses.append(hypothesis_id)
            self.state.consecutive_no_gain = 0

    def _check_hypothesis_resolved(self):
        """检查当前假说是否已解决。"""
        if self.state.current_hypothesis_index >= len(self.ordered_hypotheses):
            return

        current_hypothesis = self.ordered_hypotheses[self.state.current_hypothesis_index]

        # 检查是否有关这个假说的 confirmed 或 rejected claim
        for claim in self.state.claim_ledger:
            if claim.hypothesis_id == current_hypothesis.hypothesis_id:
                if claim.status in ("confirmed", "rejected"):
                    if current_hypothesis.hypothesis_id not in self.state.resolved_hypotheses:
                        self.state.resolved_hypotheses.append(current_hypothesis.hypothesis_id)
                    self._advance_hypothesis()
                    return

    def _advance_hypothesis(self):
        """移动到下一个假说。"""
        self.state.current_hypothesis_index += 1
        self.state.consecutive_no_gain = 0

    async def run(self) -> ModuleResultEnvelope[Stage15AgenticOutput]:
        """运行完整的 Agent Loop。"""
        # 没有假说，直接返回
        if not self.ordered_hypotheses:
            elapsed_ms = int((time.perf_counter() - self.start_time) * 1000)
            return ModuleResultEnvelope(
                module_name="extraction.stage15_agentic_real",
                status="blocked",
                error_code=ErrorCodes.NO_HYPOTHESES,
                data=None,
                metrics=RunMetrics(
                    wall_time_ms=max(elapsed_ms, 1),
                    llm_calls=0,
                    prompt_tokens=0,
                    completion_tokens=0,
                    estimated_cost_usd=0.0,
                ),
            )

        # 运行循环
        while True:
            should_continue = await self.run_one_round()
            if not should_continue:
                break

            # 检查终止条件
            if self.state.budget_exceeded:
                break

            if self.state.current_hypothesis_index >= len(self.ordered_hypotheses):
                self.state.termination_reason = "all_hypotheses_resolved"
                break

            if self.state.consecutive_no_gain >= self.input.budget.stop_after_no_gain_rounds:
                self.state.termination_reason = "no_information_gain"
                break

        # 计算未解决的假说
        self.state.unresolved_hypotheses = [
            h.hypothesis_id
            for h in self.ordered_hypotheses
            if h.hypothesis_id not in self.state.resolved_hypotheses
        ]

        # 写入中间文件
        self._write_artifacts()

        # 构建输出
        return self._build_output()

    def _write_artifacts(self):
        """写入中间文件。"""
        artifact_dir = self.ctx.repo_root / "artifacts" / "stage15"
        artifact_dir.mkdir(parents=True, exist_ok=True)

        # hypotheses.jsonl
        hypotheses_data = [h.model_dump() for h in self.ordered_hypotheses]
        with (artifact_dir / "hypotheses.jsonl").open("w", encoding="utf-8") as f:
            for h in hypotheses_data:
                f.write(json.dumps(h, ensure_ascii=False, sort_keys=True))
                f.write("\n")

        # exploration_log.jsonl
        with (artifact_dir / "exploration_log.jsonl").open("w", encoding="utf-8") as f:
            for entry in self.state.exploration_log:
                f.write(json.dumps(entry.model_dump(), ensure_ascii=False, sort_keys=True))
                f.write("\n")

        # claim_ledger.jsonl
        with (artifact_dir / "claim_ledger.jsonl").open("w", encoding="utf-8") as f:
            for claim in self.state.claim_ledger:
                f.write(json.dumps(claim.model_dump(), ensure_ascii=False, sort_keys=True))
                f.write("\n")

        # evidence_index.json
        evidence_index = {}
        for claim in self.state.claim_ledger:
            for evidence in claim.evidence_refs:
                key = f"{evidence.path}:{evidence.start_line}:{evidence.end_line}"
                if key not in evidence_index:
                    evidence_index[key] = {
                        "path": evidence.path,
                        "start_line": evidence.start_line,
                        "end_line": evidence.end_line,
                        "snippet": evidence.snippet,
                        "claim_ids": [],
                    }
                evidence_index[key]["claim_ids"].append(claim.claim_id)

        with (artifact_dir / "evidence_index.json").open("w", encoding="utf-8") as f:
            json.dump({
                "repo_id": self.input.repo.repo_id,
                "evidence_items": list(evidence_index.values()),
            }, f, ensure_ascii=False, indent=2, sort_keys=True)

        # context_digest.md
        confirmed = len([c for c in self.state.claim_ledger if c.status == "confirmed"])
        rejected = len([c for c in self.state.claim_ledger if c.status == "rejected"])
        pending = len([c for c in self.state.claim_ledger if c.status in ("pending", "inference")])

        digest = build_context_digest_prompt(
            repo_id=self.input.repo.repo_id,
            total_findings=len(self.input.stage1_output.findings),
            total_hypotheses=len(self.ordered_hypotheses),
            total_claims=len(self.state.claim_ledger),
            confirmed_claims=confirmed,
            rejected_claims=rejected,
            pending_claims=pending,
            tool_calls=self.state.tool_calls_used,
            termination_reason=self.state.termination_reason,
        )

        (artifact_dir / "context_digest.md").write_text(digest, encoding="utf-8")

    def _build_output(self) -> ModuleResultEnvelope[Stage15AgenticOutput]:
        """构建输出。"""
        elapsed_ms = int((time.perf_counter() - self.start_time) * 1000)

        # 确定状态
        if self.state.budget_exceeded:
            status = "degraded"
            error_code = ErrorCodes.BUDGET_EXCEEDED
            self.state.warnings.append(WarningItem(
                code=ErrorCodes.BUDGET_EXCEEDED,
                message="Stage 1.5 stopped after reaching budget limits.",
            ))
        elif self.state.unresolved_hypotheses:
            status = "ok"
            error_code = None
        else:
            status = "ok"
            error_code = None

        # promoted claims
        promoted_claims = [
            claim for claim in self.state.claim_ledger
            if claim.status == "confirmed"
        ]

        # 相对路径
        artifact_rel = "artifacts/stage15"
        output = Stage15AgenticOutput(
            repo=self.input.repo,
            hypotheses_path=f"{artifact_rel}/hypotheses.jsonl",
            exploration_log_path=f"{artifact_rel}/exploration_log.jsonl",
            claim_ledger_path=f"{artifact_rel}/claim_ledger.jsonl",
            evidence_index_path=f"{artifact_rel}/evidence_index.json",
            context_digest_path=f"{artifact_rel}/context_digest.md",
            promoted_claims=promoted_claims,
            summary=Stage15Summary(
                resolved_hypotheses=self.state.resolved_hypotheses,
                unresolved_hypotheses=self.state.unresolved_hypotheses,
                termination_reason=self.state.termination_reason,
            ),
        )

        # 估算成本（简单估算）
        estimated_cost = (
            self.state.prompt_tokens_used * 0.000003 +
            self.state.completion_tokens_used * 0.000015
        )

        return ModuleResultEnvelope(
            module_name="extraction.stage15_agentic_real",
            status=status,
            error_code=error_code,
            warnings=self.state.warnings,
            data=output,
            metrics=RunMetrics(
                wall_time_ms=max(elapsed_ms, 1),
                llm_calls=self.state.llm_calls,
                prompt_tokens=self.state.prompt_tokens_used,
                completion_tokens=self.state.completion_tokens_used,
                estimated_cost_usd=round(estimated_cost, 6),
                retries=0,
            ),
        )


async def run_stage15_agentic_real(
    input_data: Stage15AgenticInput,
    llm_config: Optional[LLMConfig] = None,
) -> ModuleResultEnvelope[Stage15AgenticOutput]:
    """运行真实的 Stage 1.5 Agent Loop。

    Args:
        input_data: Stage 1.5 输入
        llm_config: LLM 配置，如果为 None 则从环境变量读取

    Returns:
        ModuleResultEnvelope[Stage15AgenticOutput]
    """
    if llm_config is None:
        llm_config = LLMConfig.from_env("mock")

    adapter = LLMAdapter(llm_config)
    agent = AgentLoop(input_data, adapter)
    return await agent.run()
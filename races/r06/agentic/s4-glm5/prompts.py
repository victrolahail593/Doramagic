"""Agent Prompt 模板 — LLM 驱动的 Agent Loop 使用。

设计原则:
1. 短轮次交互：每轮 prompt 独立，不依赖长对话记忆
2. Fresh Context：每次都传入当前状态摘要
3. 假说驱动：明确当前要验证的假说
4. 工具引导：告知可用工具和推荐行动
"""

from __future__ import annotations

from typing import Any, Optional, Sequence
from dataclasses import dataclass

import sys
from pathlib import Path
_CONTRACTS_PATH = Path(__file__).parent.parent.parent.parent / "packages" / "contracts"
if str(_CONTRACTS_PATH) not in sys.path:
    sys.path.insert(0, str(_CONTRACTS_PATH))

from doramagic_contracts.extraction import (
    Hypothesis,
    Stage1Finding,
    ClaimRecord,
    ExplorationLogEntry,
)


@dataclass
class PromptContext:
    """构建 Prompt 所需的上下文。"""
    repo_id: str
    current_round: int
    max_rounds: int
    current_hypothesis: Optional[Hypothesis]
    pending_hypotheses: list[str]  # hypothesis_ids
    resolved_hypotheses: list[str]  # hypothesis_ids
    recent_steps: list[dict]  # 简化的 exploration log
    recent_claims: list[dict]  # 简化的 claim summaries
    repo_summary: str
    entrypoints: list[str]
    available_tools: list[str]
    tool_calls_used: int
    max_tool_calls: int


SYSTEM_PROMPT = """你是一个代码考古学家（Code Archaeologist），负责深入分析代码仓库，提取设计决策背后的知识。

你的任务：
1. 验证给定的假说（Hypothesis）—— 它们来自 Stage 1 的初步扫描
2. 通过工具调用收集证据，确定每个假说的状态：confirmed（确认）、rejected（反驳）、pending（待定）
3. 发现隐藏的知识，特别是 WHY（设计理由）和 UNSAID（隐含但未明说的知识）

工作原则：
- **假说驱动**：你的探索必须围绕给定的假说进行，不要漫无目的地搜索
- **证据优先**：每条 claim 必须有文件:行号 作为证据支撑
- **简洁高效**：每次只调用最必要的工具，避免重复搜索
- **诚实标注**：如果证据不足以确认假说，标注为 pending 或 inference

工具使用策略：
1. `read_artifact`: 首先了解已有的 Stage 1 发现和待验证假说
2. `list_tree`: 了解目录结构，定位相关代码位置
3. `search_repo`: 根据假说的 search_hints 搜索关键代码
4. `read_file`: 深入阅读关键文件，提取具体证据
5. `append_finding`: 记录你的发现和结论

响应格式：
当需要调用工具时，使用 function calling 格式。
当完成当前假说分析时，返回简短的总结说明。
"""


def build_agent_prompt(ctx: PromptContext) -> str:
    """构建 Agent 的 user prompt。"""
    lines = []

    # 当前轮次信息
    lines.append(f"=== Round {ctx.current_round}/{ctx.max_rounds} ===")
    lines.append(f"Tool calls: {ctx.tool_calls_used}/{ctx.max_tool_calls}")
    lines.append("")

    # 仓库概览
    lines.append("## Repository Overview")
    lines.append(f"- Repo: {ctx.repo_id}")
    lines.append(f"- Entrypoints: {', '.join(ctx.entrypoints[:5]) or 'N/A'}")
    lines.append(f"- Summary: {ctx.repo_summary[:500]}")
    lines.append("")

    # 当前假说
    if ctx.current_hypothesis:
        h = ctx.current_hypothesis
        lines.append("## Current Hypothesis to Verify")
        lines.append(f"**ID**: {h.hypothesis_id}")
        lines.append(f"**Priority**: {h.priority}")
        lines.append(f"**Statement**: {h.statement}")
        lines.append(f"**Reason**: {h.reason}")
        lines.append(f"**Search Hints**: {', '.join(h.search_hints)}")
        lines.append(f"**Related Findings**: {', '.join(h.related_finding_ids) or 'None'}")
        lines.append("")
        lines.append("**Your task**: Verify this hypothesis and determine its status.")
        lines.append("")

    # 进度摘要
    lines.append("## Progress Summary")
    lines.append(f"- Resolved hypotheses: {len(ctx.resolved_hypotheses)} ({', '.join(ctx.resolved_hypotheses[:5]) or 'none'})")
    lines.append(f"- Pending hypotheses: {len(ctx.pending_hypotheses)} ({', '.join(ctx.pending_hypotheses[:5]) or 'none'})")
    lines.append("")

    # 最近探索记录
    if ctx.recent_steps:
        lines.append("## Recent Exploration Steps (last 5)")
        for step in ctx.recent_steps[-5:]:
            lines.append(f"- [{step.get('step_id')}] {step.get('tool_name')}: {step.get('observation', '')[:100]}")
        lines.append("")

    # 最近 claim
    if ctx.recent_claims:
        lines.append("## Recent Claims (last 3)")
        for claim in ctx.recent_claims[-3:]:
            lines.append(f"- [{claim.get('claim_id')}] {claim.get('status')}: {claim.get('statement', '')[:80]}")
        lines.append("")

    # 可用工具
    lines.append("## Available Tools")
    for tool in ctx.available_tools:
        lines.append(f"- {tool}")
    lines.append("")

    # 行动提示
    lines.append("## Recommended Actions")
    if ctx.current_hypothesis:
        hints = ctx.current_hypothesis.search_hints
        if hints:
            lines.append(f"1. Use `search_repo` to find code related to: {', '.join(hints[:3])}")
        lines.append("2. Use `read_file` to examine specific files mentioned in evidence")
        lines.append("3. Use `append_finding` to record your conclusion about this hypothesis")
    else:
        lines.append("No more hypotheses to verify. Use `read_artifact` to review all findings.")
    lines.append("")

    return "\n".join(lines)


def build_context_digest_prompt(
    repo_id: str,
    total_findings: int,
    total_hypotheses: int,
    total_claims: int,
    confirmed_claims: int,
    rejected_claims: int,
    pending_claims: int,
    tool_calls: int,
    termination_reason: str,
) -> str:
    """构建 context_digest.md 的内容。"""
    return f"""# Stage 1.5 Context Digest

## Repository
- **Repo ID**: {repo_id}

## Exploration Summary
- **Stage 1 Findings**: {total_findings}
- **Hypotheses Explored**: {total_hypotheses}
- **Total Claims**: {total_claims}

## Claim Status Breakdown
- **Confirmed**: {confirmed_claims}
- **Rejected**: {rejected_claims}
- **Pending**: {pending_claims}

## Resource Usage
- **Tool Calls**: {tool_calls}

## Termination
- **Reason**: `{termination_reason}`

---
*Generated by Stage 1.5 Agentic Extraction*
"""


def parse_llm_response(response_content: str, tool_calls: Optional[list[dict]]) -> dict:
    """解析 LLM 响应，提取行动意图。

    Returns:
        {
            "action": "tool_call" | "summary" | "continue",
            "tool_name": str | None,
            "tool_args": dict | None,
            "summary": str | None,
        }
    """
    if tool_calls:
        # 有工具调用
        first_call = tool_calls[0]
        return {
            "action": "tool_call",
            "tool_name": first_call.get("name"),
            "tool_args": first_call.get("arguments", {}),
            "summary": None,
        }

    # 没有工具调用，检查文本内容
    content = response_content.strip().lower()

    # 检查是否是总结/完成信号
    completion_indicators = [
        "hypothesis verified",
        "analysis complete",
        "no more evidence",
        "conclusion:",
        "summary:",
        "final finding",
    ]

    for indicator in completion_indicators:
        if indicator in content:
            return {
                "action": "summary",
                "tool_name": None,
                "tool_args": None,
                "summary": response_content,
            }

    # 默认继续
    return {
        "action": "continue",
        "tool_name": None,
        "tool_args": None,
        "summary": response_content,
    }


# 工具选择引导 prompt 片段
TOOL_SELECTION_HINTS = """
When choosing which tool to use:

1. **read_artifact** - Use when you need context from Stage 1 findings or to review the current hypothesis list
   - Best for: Understanding what's already known, reviewing related findings

2. **list_tree** - Use when you need to understand the project structure
   - Best for: Finding where code might be located, understanding module organization

3. **search_repo** - Use when you need to find specific code patterns or keywords
   - Best for: Finding implementations, locating related code across files

4. **read_file** - Use when you have a specific file path and need to read its contents
   - Best for: Detailed examination of specific code, extracting exact evidence

5. **append_finding** - Use when you have enough evidence to make a claim about the hypothesis
   - Best for: Recording your conclusion (confirmed/rejected/pending) with supporting evidence

**Decision flow**:
- Start with `read_artifact` to understand context
- Use `search_repo` with the hypothesis's search_hints
- Use `read_file` on promising results
- Use `append_finding` when you have a clear conclusion
"""


def format_hypothesis_summary(hypotheses: Sequence[Hypothesis]) -> str:
    """格式化假说列表为可读摘要。"""
    lines = []
    for h in hypotheses:
        status_marker = ""
        lines.append(f"- [{h.hypothesis_id}] ({h.priority}) {h.statement}")
    return "\n".join(lines)


def format_findings_summary(findings: Sequence[Stage1Finding]) -> str:
    """格式化 findings 为可读摘要。"""
    lines = []
    for f in findings[:10]:
        lines.append(f"- [{f.finding_id}] {f.knowledge_type}: {f.title}")
        if f.statement:
            lines.append(f"  {f.statement[:100]}")
    return "\n".join(lines)
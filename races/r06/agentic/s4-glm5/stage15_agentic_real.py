"""Stage 1.5 真实 Agent Loop 实现 — LLM 驱动的假说验证探索。

与 mock 版本的区别:
1. 使用真实 LLM 调用（通过 LLMAdapter）
2. LLM 决定调用哪个工具，而非确定性规则
3. 支持多轮交互，直到假说解决或 budget 耗尽
4. 每轮 fresh context，不依赖长对话记忆

用法:
    from s4_glm5.stage15_agentic_real import run_stage15_agentic_real

    result = await run_stage15_agentic_real(input_data)
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Optional

# 确保可以导入 contracts 和 shared_utils
_CONTRACTS_PATH = Path(__file__).parent.parent.parent.parent / "packages" / "contracts"
if str(_CONTRACTS_PATH) not in sys.path:
    sys.path.insert(0, str(_CONTRACTS_PATH))

_SHARED_PATH = Path(__file__).parent.parent.parent.parent / "packages" / "shared_utils"
if str(_SHARED_PATH) not in sys.path:
    sys.path.insert(0, str(_SHARED_PATH))

from doramagic_contracts.extraction import (
    Stage15AgenticInput,
    Stage15AgenticOutput,
)
from doramagic_contracts.envelope import (
    ModuleResultEnvelope,
)

from doramagic_shared_utils.llm_adapter import LLMConfig

from .agent_loop import run_stage15_agentic_real as _run_stage15_agentic_real


__all__ = [
    "run_stage15_agentic_real",
    "run_stage15_agentic_real_sync",
]


async def run_stage15_agentic_real(
    input_data: Stage15AgenticInput,
    llm_config: Optional[LLMConfig] = None,
) -> ModuleResultEnvelope[Stage15AgenticOutput]:
    """运行真实的 Stage 1.5 Agent Loop。

    这是主入口函数，执行 LLM 驱动的假说验证探索。

    Args:
        input_data: Stage 1.5 输入，包含：
            - repo: 仓库引用
            - repo_facts: Stage 0 提取的事实
            - stage1_output: Stage 1 的输出（findings 和 hypotheses）
            - budget: 预算控制（max_rounds, max_tool_calls, max_prompt_tokens）
            - toolset: 工具启用配置
        llm_config: LLM 配置，如果为 None 则从环境变量读取。
            支持的 provider: anthropic, openai, mock

    Returns:
        ModuleResultEnvelope[Stage15AgenticOutput] 包含：
            - status: ok / degraded / blocked / error
            - data: Stage15AgenticOutput
                - promoted_claims: 已确认的知识声明
                - summary: 解决/未解决的假说列表
                - 中间文件路径
            - metrics: 运行指标（时间、token、成本）
            - warnings: 警告列表

    Example:
        ```python
        from doramagic_contracts.extraction import Stage15AgenticInput
        from doramagic_shared_utils.llm_adapter import LLMConfig

        # 准备输入
        input_data = Stage15AgenticInput(
            repo=repo_ref,
            repo_facts=repo_facts,
            stage1_output=stage1_output,
            budget=Stage15Budget(max_rounds=5, max_tool_calls=30),
            toolset=Stage15Toolset(),
        )

        # 运行 Agent Loop
        result = await run_stage15_agentic_real(
            input_data,
            llm_config=LLMConfig(provider="openai", model="gpt-4o"),
        )

        # 检查结果
        if result.status == "ok":
            for claim in result.data.promoted_claims:
                print(f"Confirmed: {claim.statement}")
        ```

    Notes:
        - 工具调用通过 LLMAdapter 统一管理，不直接导入 anthropic/openai
        - 中间文件写入 artifacts/stage15/ 目录
        - 支持 budget 控制，防止无限循环
        - 终止条件：所有假说解决 / budget 耗尽 / 连续无进展
    """
    return await _run_stage15_agentic_real(input_data, llm_config)


def run_stage15_agentic_real_sync(
    input_data: Stage15AgenticInput,
    llm_config: Optional[LLMConfig] = None,
) -> ModuleResultEnvelope[Stage15AgenticOutput]:
    """同步版本的 Stage 1.5 Agent Loop。

    适用于不支持 async 的调用场景。

    Args:
        input_data: Stage 1.5 输入
        llm_config: LLM 配置

    Returns:
        ModuleResultEnvelope[Stage15AgenticOutput]
    """
    return asyncio.run(run_stage15_agentic_real(input_data, llm_config))


# CLI 入口
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Stage 1.5 Agentic Extraction")
    parser.add_argument("--input", required=True, help="Path to input JSON file")
    parser.add_argument("--output", required=True, help="Path to output JSON file")
    parser.add_argument("--provider", default="mock", help="LLM provider (anthropic/openai/mock)")
    parser.add_argument("--model", default=None, help="Model name")

    args = parser.parse_args()

    # 读取输入
    with open(args.input, "r", encoding="utf-8") as f:
        input_dict = json.load(f)

    input_data = Stage15AgenticInput.model_validate(input_dict)

    # 配置 LLM
    llm_config = LLMConfig.from_env(args.provider)
    if args.model:
        llm_config.model = args.model

    # 运行
    result = run_stage15_agentic_real_sync(input_data, llm_config)

    # 写入输出
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(), f, ensure_ascii=False, indent=2)

    print(f"Stage 1.5 completed with status: {result.status}")
    if result.data:
        print(f"Resolved hypotheses: {len(result.data.summary.resolved_hypotheses)}")
        print(f"Unresolved hypotheses: {len(result.data.summary.unresolved_hypotheses)}")
        print(f"Termination reason: {result.data.summary.termination_reason}")
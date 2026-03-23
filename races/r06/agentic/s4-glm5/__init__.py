"""Stage 1.5 Agentic 提取 — s4-glm5 实现。

这是真实 LLM 驱动的 Agent Loop 实现，用于假说验证和深度探索。

主要组件:
- stage15_agentic_real: 主入口函数
- agent_loop: Agent 循环核心逻辑
- tools: 5 个工具的定义和实现
- prompts: LLM prompt 模板
"""

from .stage15_agentic_real import (
    run_stage15_agentic_real,
    run_stage15_agentic_real_sync,
)

from .tools import (
    ToolExecutor,
    ToolResult,
    AgentContext,
    get_tool_schemas,
)

from .agent_loop import (
    AgentLoop,
    AgentState,
)


__all__ = [
    # 主入口
    "run_stage15_agentic_real",
    "run_stage15_agentic_real_sync",
    # 工具
    "ToolExecutor",
    "ToolResult",
    "AgentContext",
    "get_tool_schemas",
    # Agent Loop
    "AgentLoop",
    "AgentState",
]


__version__ = "1.0.0"
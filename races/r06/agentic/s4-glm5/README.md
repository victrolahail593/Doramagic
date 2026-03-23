# Stage 1.5 Agentic 提取 — s4-glm5 实现

真实 LLM 驱动的 Agent Loop，用于假说验证和深度代码探索。

## 核心设计

### 混合架构

```
Stage 0 → Stage 1（广度扫描+假说生成）→ [Stage 1.5 Agent Loop] → Stage 2-3 → ...
```

Stage 1.5 是一个可选的深度探索阶段，通过 LLM Agent 验证 Stage 1 生成的假说。

### 假说驱动探索

Agent 的探索围绕 Stage 1 生成的 `hypothesis_list` 进行，不是自由漫游：

1. 每个假说包含：`statement`、`reason`、`priority`、`search_hints`
2. Agent 按优先级顺序处理假说
3. 每轮聚焦一个假说，直到确认或反驳

### 5 个工具

| 工具 | 用途 | 使用场景 |
|------|------|---------|
| `read_artifact` | 读取 Stage 0/1 产出 | 了解已有发现 |
| `list_tree` | 列出目录结构 | 定位代码位置 |
| `search_repo` | 搜索代码内容 | 按关键词找代码 |
| `read_file` | 读取文件内容 | 提取具体证据 |
| `append_finding` | 记录发现 | 输出 claim |

### Filesystem-as-Memory

中间文件存储在 `artifacts/stage15/`：

```
artifacts/stage15/
├── hypotheses.jsonl      # 待验证假说
├── exploration_log.jsonl # 工具调用记录
├── claim_ledger.jsonl    # 知识声明账本
├── evidence_index.json   # 证据索引
└── context_digest.md     # 当前理解摘要
```

### 三层 Budget 控制

```python
Stage15Budget(
    max_rounds=5,           # 最多 5 轮交互
    max_tool_calls=30,      # 最多 30 次工具调用
    max_prompt_tokens=60000, # 最多 60k prompt tokens
    stop_after_no_gain_rounds=2,  # 连续 2 轮无进展则停止
)
```

## 使用方法

### 基本用法

```python
from doramagic_contracts.extraction import (
    Stage15AgenticInput,
    Stage15Budget,
    Stage15Toolset,
)
from doramagic_shared_utils.llm_adapter import LLMConfig
from s4_glm5 import run_stage15_agentic_real

# 准备输入
input_data = Stage15AgenticInput(
    repo=repo_ref,
    repo_facts=repo_facts,
    stage1_output=stage1_output,
    budget=Stage15Budget(max_rounds=5),
    toolset=Stage15Toolset(),
)

# 运行 Agent Loop
result = await run_stage15_agentic_real(
    input_data,
    llm_config=LLMConfig(provider="openai", model="gpt-4o"),
)

# 检查结果
if result.status == "ok":
    print(f"Resolved: {len(result.data.summary.resolved_hypotheses)}")
    for claim in result.data.promoted_claims:
        print(f"  - {claim.statement}")
```

### 同步版本

```python
from s4_glm5 import run_stage15_agentic_real_sync

result = run_stage15_agentic_real_sync(input_data)
```

### CLI 使用

```bash
python -m s4_glm5.stage15_agentic_real \
    --input input.json \
    --output output.json \
    --provider openai \
    --model gpt-4o
```

## 配置选项

### Budget 配置

| 参数 | 默认值 | 范围 | 说明 |
|------|--------|------|------|
| `max_rounds` | 5 | 1-10 | 最大交互轮数 |
| `max_tool_calls` | 30 | 5-60 | 最大工具调用次数 |
| `max_prompt_tokens` | 60000 | 5000+ | 最大 prompt tokens |
| `stop_after_no_gain_rounds` | 2 | 1-5 | 无进展停止阈值 |

### Toolset 配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `allow_read_artifact` | True | 允许读取 Stage 1 产出 |
| `allow_list_tree` | True | 允许列出目录结构 |
| `allow_search_repo` | True | 允许搜索代码 |
| `allow_read_file` | True | 允许读取文件 |
| `allow_append_finding` | True | 允许追加发现 |

## 返回结构

```python
ModuleResultEnvelope(
    module_name="extraction.stage15_agentic_real",
    status="ok",  # ok / degraded / blocked / error
    data=Stage15AgenticOutput(
        promoted_claims=[...],  # 已确认的知识声明
        summary=Stage15Summary(
            resolved_hypotheses=["H-001", "H-002"],
            unresolved_hypotheses=["H-003"],
            termination_reason="all_hypotheses_resolved",
        ),
        # 中间文件路径
        hypotheses_path="artifacts/stage15/hypotheses.jsonl",
        exploration_log_path="artifacts/stage15/exploration_log.jsonl",
        ...
    ),
    metrics=RunMetrics(
        wall_time_ms=1500,
        llm_calls=5,
        prompt_tokens=12000,
        completion_tokens=3000,
        estimated_cost_usd=0.05,
    ),
)
```

## 设计约束

1. **LLM 调用必须通过 LLMAdapter** — 不直接 import anthropic/openai/google.generativeai
2. **Schema 使用 contracts 定义** — 使用 `doramagic_contracts.extraction` 中的模型
3. **短轮次交互** — 每轮 fresh context，不依赖长对话记忆
4. **假说驱动** — 探索围绕 hypothesis_list，不是自由漫游

## 与 Mock 版本的区别

| 方面 | Mock 版本 | 真实版本 |
|------|----------|---------|
| LLM 调用 | 无 | 通过 LLMAdapter |
| 工具选择 | 确定性规则 | LLM 决定 |
| 假说验证 | 基于已有 finding | 可探索新证据 |
| 适用场景 | 测试、Race 验证 | 生产环境 |

## 依赖

- `doramagic_contracts`: 数据模型定义
- `doramagic_shared_utils.llm_adapter`: LLM 统一调用接口

## 文件结构

```
s4-glm5/
├── __init__.py              # 模块入口
├── stage15_agentic_real.py  # 主入口函数
├── agent_loop.py            # Agent Loop 核心逻辑
├── tools.py                 # 5 个工具的定义和实现
├── prompts.py               # LLM prompt 模板
└── README.md                # 本文件
```
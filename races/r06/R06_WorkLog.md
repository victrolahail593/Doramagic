# Race R06 工作日志

**日期**: 2026-03-20
**开发者**: S4-GLM5
**任务**: 实现 Stage 1.5 Agentic 提取 + Domain Bricks 积木制作

---

## Race A: Stage 1.5 Agentic 提取

### 产出文件

```
races/r06/agentic/s4-glm5/
├── __init__.py              # 模块入口
├── stage15_agentic_real.py  # 主入口函数
├── agent_loop.py            # Agent Loop 核心逻辑 (550行)
├── tools.py                 # 5个工具定义 (500行)
├── prompts.py               # LLM prompt模板 (250行)
└── README.md                # 使用说明
```

### 核心实现

| 组件 | 描述 |
|------|------|
| `AgentLoop` | 真实LLM驱动的探索循环，假说驱动探索 |
| `ToolExecutor` | 5个工具执行器 |
| `AgentState` | Agent状态管理 |
| 三层Budget | max_rounds / max_tool_calls / max_prompt_tokens |

### 5个工具

| 工具 | 用途 |
|------|------|
| `read_artifact` | 读取Stage 0/1产出 |
| `list_tree` | 列出目录结构 |
| `search_repo` | 搜索代码内容 |
| `read_file` | 读取文件内容 |
| `append_finding` | 记录发现 |

### Filesystem-as-Memory

```
artifacts/stage15/
├── hypotheses.jsonl      # 待验证假说
├── exploration_log.jsonl # 工具调用记录
├── claim_ledger.jsonl    # 知识声明账本
├── evidence_index.json   # 证据索引
└── context_digest.md     # 当前理解摘要
```

---

## Race B: Domain Bricks 积木制作

### 产出文件

```
races/r06/bricks/s4-glm5/
├── __init__.py           # 模块入口
├── brick_schema.py       # 积木Schema定义 (280行)
├── brick_compiler.py     # Markdown→JSON编译器 (450行)
├── brick_maker.py        # 积木制作主流程 (550行)
├── README.md             # 使用说明
└── templates/
    ├── L1_framework_brick.md.j2  # L1框架级模板
    └── L2_pattern_brick.md.j2    # L2模式级模板
```

### 核心实现

| 类 | 功能 |
|---|------|
| `BrickMaker` | 从项目提取结果生成积木候选 |
| `BrickCompiler` | 编译Markdown为DomainBrick JSON |
| `BrickRegistry` | 积木注册表，管理索引和检索 |
| `BrickReviewWorkflow` | 审核工作流 |

### 双层架构

| 层级 | Token预算 | 内容 |
|------|----------|------|
| L1 框架级 | 200-400 | WHY哲学 + 心智模型 |
| L2 模式级 | 400-800 | UNSAID + 速查规则 + 反模式 |

### Token预算控制

- 总注入预算: ≤ 2500 tokens
- 注入策略: 1×L1(full) + 2-3×L2(compact)

---

## 硬性约束验证

| 约束 | Agentic | Bricks |
|------|---------|--------|
| 不直接import anthropic/openai/google.generativeai | ✅ 通过LLMAdapter | ✅ 通过LLMAdapter |
| 使用contracts schema | ✅ extraction.py | ✅ domain_graph.py |
| 所有LLM调用通过LLMAdapter | ✅ | ✅ |

---

## 创建的基础设施

### LLMAdapter

**路径**: `packages/shared_utils/doramagic_shared_utils/llm_adapter.py`

统一LLM调用接口，支持:
- Anthropic Claude
- OpenAI GPT
- Mock (测试用)
- 工具调用循环

---

## 使用示例

### Stage 1.5 Agentic

```python
from s4_glm5 import run_stage15_agentic_real

result = await run_stage15_agentic_real(
    input_data,
    llm_config=LLMConfig(provider="openai", model="gpt-4o"),
)
```

### Domain Bricks

```python
from brick_schema import quick_make_brick
from brick_maker import BrickMaker

# 快速创建
md_path, json_path = quick_make_brick(
    domain_id="django",
    brick_name="core",
    layer="L1",
    design_philosophy="...",
)

# 从综合报告生成
maker = BrickMaker(config)
result = maker.make_bricks_from_decisions(decisions)
```

---

## 参考资料

- `research/agentic-extraction/synthesis.md` — Agentic提取研究结论
- `research/soul-lego-bricks/reports/synthesis-report.md` — 积木粒度研究结论
- `packages/contracts/doramagic_contracts/extraction.py` — Stage 1.5 schema
- `packages/contracts/doramagic_contracts/domain_graph.py` — DomainBrick schema
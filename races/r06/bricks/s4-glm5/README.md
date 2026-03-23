# Domain Bricks — 积木制作流程

## 概述

Domain Bricks（领域积木）是经过多项目验证的知识单元，可注入 Soul Extractor 的 Stage 0/1 加速提取过程。

### 核心设计

```
┌─────────────────────────────────────────┐
│          Soul Lego Brick Library         │
│                                          │
│  源文件: Markdown + YAML frontmatter     │
│  编译产物: JSON (注入 LLM context)        │
│  索引: Vector + Metadata Filter          │
│                                          │
│  L1 框架级 (20-30 个)                     │
│    200-400 tokens, WHY 哲学 + 心智模型     │
│                                          │
│  L2 模式级 (60-100 个)                    │
│    400-800 tokens, UNSAID + 速查规则      │
│                                          │
│  总注入预算: ≤ 2500 tokens                │
│  注入策略: 1×L1(full) + 2-3×L2(compact)  │
└─────────────────────────────────────────┘
```

## 文件结构

```
races/r06/bricks/s4-glm5/
├── __init__.py           # 模块入口
├── brick_schema.py       # 积木 Schema 定义 (Markdown 源文件格式)
├── brick_compiler.py     # Markdown → JSON 编译器
├── brick_maker.py        # 积木制作主流程
├── README.md             # 本文件
└── templates/
    ├── L1_framework_brick.md.j2  # L1 框架级模板
    └── L2_pattern_brick.md.j2    # L2 模式级模板
```

## 使用方法

### 1. 快速创建积木

```python
from pathlib import Path
from brick_schema import quick_make_brick

# 创建 Django 核心积木
md_path, json_path = quick_make_brick(
    domain_id="django",
    brick_name="core",
    layer="L1",
    design_philosophy="Django follows the 'batteries included' philosophy...",
    mental_models="ORM acts as an in-memory representation of your database...",
    source_project_ids=["wger", "django-commerce"],
)

print(f"Created: {md_path}")
print(f"Compiled: {json_path}")
```

### 2. 从综合报告生成积木

```python
from brick_maker import BrickMaker, BrickMakerConfig

config = BrickMakerConfig(
    output_dir=Path("bricks"),
    llm_provider="mock",  # 生产环境使用 "anthropic"
)

maker = BrickMaker(config)
result = maker.make_bricks_from_decisions(
    decisions=synthesis_decisions,
    domain_id="django",
    project_ids=["wger", "django-commerce"],
)

for candidate in result.candidates:
    print(f"Created brick: {candidate.brick_id}")
    print(f"  Layer: {candidate.layer}")
    print(f"  Token estimate: {candidate.token_estimate}")
```

### 3. 编译积木

```python
from brick_compiler import BrickCompiler, RenderMode

compiler = BrickCompiler()

# 编译单个文件
result, json_path = compiler.compile_and_save(
    source_path=Path("bricks/django-core-L1.md"),
    mode=RenderMode.FULL,
)

# 编译目录下所有文件
results = compiler.compile_directory(
    source_dir=Path("bricks"),
    mode=RenderMode.COMPACT,
)
```

### 4. 使用积木注册表

```python
from brick_compiler import BrickRegistry

registry = BrickRegistry(Path("bricks"))

# 重建索引
index = registry.rebuild_index()

# 获取指定域的积木
django_bricks = registry.get_bricks_by_domain("django")

# 获取用于注入的积木（预算控制）
injection_bricks = registry.get_injection_bricks(
    domain_id="django",
    max_tokens=2500,
)
```

### 5. 生成注入上下文

```python
from brick_compiler import generate_brick_injection_context

# 从 JSON 文件列表生成注入上下文
json_paths = [
    Path("bricks/compiled/django-core-L1.json"),
    Path("bricks/compiled/django-orm-L2.json"),
]

context = generate_brick_injection_context(
    brick_paths=json_paths,
    max_tokens=2500,
    mode=RenderMode.COMPACT,
)

print(context)
```

## 积木源文件格式

积木源文件使用 Markdown + YAML frontmatter 格式：

```markdown
---
brick_id: django-core-L1
domain_id: django
layer: L1
knowledge_type: rationale
confidence: high
signal: ALIGNED
source_project_ids:
  - wger
  - django-commerce
support_count: 2
tags:
  - core
  - philosophy
---

# Design Philosophy

Django follows the "batteries included" philosophy, providing
comprehensive built-in features for common web development tasks.

# Mental Models

The ORM acts as an in-memory representation of your database schema,
allowing you to think in Python objects rather than SQL queries.

# Implications

This means you should leverage Django's built-in features whenever
possible, rather than reinventing the wheel.
```

## DomainBrick Schema

编译产物使用 `DomainBrick` schema（不可修改）：

```python
class DomainBrick(BaseModel):
    brick_id: str
    domain_id: str
    knowledge_type: KnowledgeType  # "capability", "rationale", "constraint", "interface", "failure", "assembly_pattern"
    statement: str
    confidence: Confidence  # "high", "medium", "low"
    signal: SignalKind  # "ALIGNED", "STALE", "MISSING", "ORIGINAL", "DRIFTED", "DIVERGENT", "CONTESTED"
    source_project_ids: list[str]
    support_count: int  # ≥ 1
    evidence_refs: list[EvidenceRef] = []
    tags: list[str] = []
```

## 审核工作流

```python
from brick_maker import BrickReviewWorkflow

workflow = BrickReviewWorkflow(Path("bricks"))

# 提交审核
workflow.submit_for_review(Path("bricks/django-core-L1.md"))

# 列出待审核积木
pending = workflow.list_pending()

# 批准积木
json_path = workflow.approve("django-core-L1")

# 拒绝积木
workflow.reject("django-core-L1", reason="Needs more specific examples")
```

## Token 预算控制

- **L1 框架级**: 200-400 tokens
  - 设计哲学
  - 心智模型
  - 代码影响

- **L2 模式级**: 400-800 tokens
  - UNSAID 知识
  - 速查规则
  - 反模式警示

- **总注入预算**: ≤ 2500 tokens
  - 1×L1 (完整版)
  - 2-3×L2 (压缩版)

## 关键约束

1. **不能直接 import anthropic/openai/google.generativeai**
   - 所有 LLM 调用必须通过 `LLMAdapter`

2. **必须使用 DomainBrick schema**
   - 定义在 `packages/contracts/doramagic_contracts/domain_graph.py`
   - 不可修改

3. **所有产物必须可被 Python 程序处理**
   - 源文件: Markdown + YAML
   - 编译产物: JSON
   - 索引: JSON

## 首批验证积木

| 积木 | 层级 | 预估 tokens | 理由 |
|------|------|------------|------|
| `django-core` | L1 | 350 | exp08 wger 数据可做 A/B 对照 |
| `django-orm` | L2 | 700 | UNSAID 密度最高，N+1/signals/migrations |

## 参考资料

- 研究报告: `research/soul-lego-bricks/reports/synthesis-report.md`
- DomainBrick Schema: `packages/contracts/doramagic_contracts/domain_graph.py`
- LLMAdapter: `packages/shared_utils/doramagic_shared_utils/llm_adapter.py`
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

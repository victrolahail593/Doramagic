# R07 Codex Brief — Doramagic 完整产品流水线

> **角色**：S2-Codex（框架健壮性专家）
> **目标**：实现 doramagic_pipeline.py + multi_extract.py + 端到端测试
> **输出路径**：`races/r07/pipeline/s2-codex/` 和 `races/r07/tests/s2-codex/`
> **硬约束**：所有文件只写到上述路径，不修改项目其他文件

---

## 项目背景

Doramagic 是 OpenClaw 生态中的「哆啦A梦」——用户说出模糊需求（如「帮我做一个记账 app」），Doramagic 从开源世界找最好的作业、提取智慧（WHY + UNSAID）、锻造可安装的 Skill。

**当前问题**：Python 核心引擎（24,646 行）和 SKILL.md 触发层是断开的。SKILL.md 会搜索项目、下载代码，但之后让 AI inline 完成所有提取工作——导致只能提取 1 个项目、无法调用 Bricks/Knowledge Compiler/跨项目综合。

**你的任务**：写一个桥接脚本 `doramagic_pipeline.py`，让 SKILL.md 通过 `exec python3` 调用它，完成 Phase C→H 的全部工作。

---

## 任务 M1：`doramagic_pipeline.py`

### 调用方式

```bash
python3 doramagic_pipeline.py \
  --need-profile /path/to/need_profile.json \
  --repos /path/to/repos.json \
  --run-dir /path/to/run_dir \
  --bricks-dir /path/to/bricks \
  --output /path/to/delivery
```

### 输入文件格式

**need_profile.json**：
```json
{
  "user_need": "我想做一个记账 app",
  "keywords": ["accounting", "finance", "budget"],
  "domain": "personal_finance"
}
```

**repos.json**：
```json
[
  {"name": "firefly-iii", "path": "/abs/path/to/firefly-iii", "stars": 16000, "url": "https://github.com/firefly-iii/firefly-iii"},
  {"name": "actual", "path": "/abs/path/to/actual", "stars": 14000, "url": "https://github.com/actualbudget/actual"}
]
```

### 内部流程

```
1. 读 need_profile.json + repos.json
2. 调 multi_extract.py → 并行提取 N 个项目 → List[PipelineResult]
3. 把 N 个 PipelineResult 转换为 SynthesisInput
4. 调 run_synthesis() → SynthesisReportData
5. 调 run_skill_compiler() → SKILL.md + PROVENANCE.md + LIMITATIONS.md
6. 写到 --output 目录
7. stdout 打印 JSON 摘要
```

### 降级策略（核心要求）

- **单 repo 提取失败**：跳过，继续其他 repo。至少 1 个成功才继续。
- **synthesis 失败**：降级为「最佳单项目」模式——选 total_cards 最多的那个 PipelineResult 直接编译。
- **skill_compiler 失败**：用 fallback 函数生成简化版 SKILL.md（最小可用）。
- **所有 repo 都失败**：exit 1，stdout 打印错误 JSON。

### stdout 输出格式

```json
{
  "status": "success",
  "repos_extracted": 3,
  "repos_failed": 1,
  "delivery": {
    "SKILL.md": {"path": "/abs/path", "size_bytes": 6200},
    "PROVENANCE.md": {"path": "/abs/path", "size_bytes": 2100},
    "LIMITATIONS.md": {"path": "/abs/path", "size_bytes": 1800}
  },
  "warnings": ["repo 'xyz' failed: timeout"]
}
```

---

## 任务 M2：`multi_extract.py`

### 函数签名

```python
def extract_multiple_repos(
    repos: list[dict],          # [{"name": str, "path": str, ...}]
    run_dir: str,               # 运行目录
    bricks_dir: str,            # 积木目录
    max_workers: int = 3,       # 并行度
    timeout_per_repo: int = 120, # 每 repo 超时秒数
) -> list[dict]:
    """
    返回 [{"name": str, "result": PipelineResult|None, "error": str|None}]
    """
```

### 内部逻辑

- 用 `concurrent.futures.ProcessPoolExecutor` 或 `ThreadPoolExecutor`
- 每个 repo 的输出写到 `{run_dir}/extractions/{repo_name}/`
- 用 `signal.alarm` 或 `executor` timeout 控制超时
- 捕获所有异常，失败的 repo 记录 error 但不 abort

### 已有函数（直接调用）

```python
# packages/orchestration/doramagic_orchestration/phase_runner.py
from doramagic_orchestration.phase_runner import run_single_project_pipeline, PipelineConfig, PipelineResult

result = run_single_project_pipeline(
    repo_path="/path/to/repo",
    output_dir="/path/to/output",
    adapter=None,      # None = 跳过需要 LLM 的 Stage
    router=None,
    config=PipelineConfig(
        enable_bricks=True,
        bricks_dir="/path/to/bricks",
        enable_dsd=True,
    ),
)
# result: PipelineResult(stages_completed, stages_skipped, stages_failed, output_dir, inject_dir, dsd_report, total_cards, total_bricks_loaded)
```

```python
# packages/cross_project/doramagic_cross_project/synthesis.py
from doramagic_cross_project import run_synthesis
from doramagic_contracts.cross_project import SynthesisInput

result = run_synthesis(SynthesisInput(
    comparison_result=...,
    project_summaries=...,
    community_knowledge=...,
    need_profile=...,
))
# result: ModuleResultEnvelope[SynthesisReportData]
```

```python
# packages/skill_compiler/doramagic_skill_compiler/compiler.py
from doramagic_skill_compiler import run_skill_compiler
from doramagic_contracts.skill_compiler import SkillCompilerInput

result = run_skill_compiler(SkillCompilerInput(
    platform_rules=...,
    synthesis_report=...,
    need_profile=...,
))
# result: ModuleResultEnvelope[SkillCompilerOutput]
```

### Contracts 参考

查阅 `packages/contracts/doramagic_contracts/` 下各模块了解完整 schema：
- `extraction.py` — PipelineResult, RepoFacts, SoulCard 等
- `cross_project.py` — SynthesisInput, SynthesisReportData, ComparisonResult 等
- `skill_compiler.py` — SkillCompilerInput, SkillCompilerOutput
- `common.py` — ModuleResultEnvelope, NeedProfile

### 关键约束

- **不 import anthropic / openai / google.generativeai**（模型无关）
- **Python 3.9+ 兼容**（远程 Mac mini 可能没有最新 Python）
- **所有路径用 pathlib.Path**
- **logging 用 structlog 或标准 logging**

---

## 任务 M4：端到端测试

### 文件：`test_e2e_pipeline.py`

```python
"""
用 data/fixtures/ 模拟完整 A→H 流程。
不需要 GitHub API，不需要 LLM API。
"""
import subprocess, json, pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[4]  # adjust as needed
FIXTURES = PROJECT_ROOT / "data" / "fixtures"

def test_pipeline_with_mock_data():
    """用 sim2 fixture 跑完整流程"""
    # 1. 构造 need_profile.json
    need = {"user_need": "calorie tracking app", "keywords": ["calorie", "nutrition"], "domain": "health"}

    # 2. 构造 repos.json — 指向 fixture 数据
    # 用 data/fixtures/snapshots/calorie-tracking/ 模拟一个已下载的 repo
    repos = [{"name": "calorie-tracking", "path": str(FIXTURES / "snapshots" / "calorie-tracking")}]

    # 3. 写临时文件
    # 4. 调 doramagic_pipeline.py as subprocess
    # 5. 断言：
    #    - exit code == 0
    #    - delivery/SKILL.md 存在且 ≥ 1KB
    #    - delivery/PROVENANCE.md 存在
    #    - delivery/LIMITATIONS.md 存在
    #    - stdout JSON 中 status == "success"

def test_pipeline_handles_empty_repos():
    """repos.json 为空列表 → exit 1 + 错误消息"""

def test_pipeline_handles_bad_repo_path():
    """某个 repo path 不存在 → 该 repo 跳过，其他继续"""
```

---

## 文件输出路径

```
races/r07/pipeline/s2-codex/
├── doramagic_pipeline.py       # M1
├── multi_extract.py            # M2
└── README.md                   # 使用说明

races/r07/tests/s2-codex/
├── test_e2e_pipeline.py        # M4
└── conftest.py                 # fixtures
```

---

## 验收标准

| # | 标准 | 通过条件 |
|---|------|---------|
| 1 | sim2 fixture 跑通 | `python3 doramagic_pipeline.py` exit 0，delivery/ 三个文件存在 |
| 2 | 空 repos 处理 | exit 1，stderr/stdout 有错误消息 |
| 3 | 坏 repo 降级 | 2 个 repo 中 1 个路径不存在，仍产出结果 |
| 4 | SKILL.md 质量 | ≥ 1KB，含 Purpose + Capabilities 两个 section |
| 5 | JSON 摘要 | stdout 是合法 JSON，含 status + delivery 字段 |
| 6 | 无外部 API 依赖 | 不 import anthropic/openai，不联网 |
| 7 | 测试通过 | `pytest races/r07/tests/s2-codex/ -v` 全绿 |

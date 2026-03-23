# Race Brief: Agentic 提取 (Stage 1.5)

> **Race ID**: r06-agentic
> **赛道**: A
> **选手**: S1-Sonnet vs S3-Gemini
> **预估**: 2-3 天
> **评审权重**: 假说解决率 25% + 证据绑定 25% + 代码质量 20% + 测试 15% + DECISIONS.md 15%

---

## 任务

将 `packages/extraction/doramagic_extraction/stage15_agentic.py` 从 **mock 实现**升级为**真实 Agent Loop**。

当前 mock 从 Stage 1 findings 确定性模拟工具调用，不读真实代码、不调 LLM。
你的任务是实现真实的假说驱动探索循环：LLM 决定用哪个工具 → 执行工具读真实代码 → 收集证据 → 评估假说。

---

## 输入契约（冻结，不可修改）

```python
class Stage15AgenticInput(BaseModel):
    schema_version: str = "dm.stage15-input.v1"
    repo: RepoRef           # 含 local_path，可访问真实代码文件
    repo_facts: RepoFacts   # Stage 0 确定性事实
    stage1_output: Stage1ScanOutput  # Stage 1 的 findings + hypotheses
    budget: Stage15Budget    # max_rounds=5, max_tool_calls=30, max_prompt_tokens=60000
    toolset: Stage15Toolset  # 5 个工具开关
```

**Fixture 路径**: `data/fixtures/` — 使用已有 fixture 或自行创建，但须提交。

---

## 输出契约（冻结，不可修改）

```python
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
```

5 个中间文件必须写入 `<repo_local_path>/artifacts/stage15/`:
- `hypotheses.jsonl`
- `exploration_log.jsonl`
- `claim_ledger.jsonl`
- `evidence_index.json`
- `context_digest.md`

---

## 集成接口（冻结，不可修改）

```python
# 上游调用方: phase_runner.py
result = run_stage15_agentic(input_data)

# 你必须暴露这个函数签名:
def run_stage15_agentic(
    input_data: Stage15AgenticInput,
    adapter: LLMAdapter | None = None,    # 模型无关 LLM 调用
    router: CapabilityRouter | None = None,  # 能力路由
) -> ModuleResultEnvelope[Stage15AgenticOutput]:
    ...

# 下游消费者: stage35_validate.py 消费 promoted_claims
# ClaimRecord 必须包含 evidence_refs (file:line) 和 supporting_step_ids
```

---

## 核心行为

```
LOOP:
  1. 从 hypotheses 中按 priority 排序取下一个假说
  2. 通过 LLMAdapter 调用 LLM，让 LLM 决定使用哪个工具验证该假说
  3. 执行工具调用:
     - read_file → 读真实代码文件 (Path(repo.local_path) / path)
     - search_repo → grep 代码 (关键词搜索)
     - list_tree → 列目录结构
     - read_artifact → 读 Stage 1 产出的中间文件
     - append_finding → 写入 claim_ledger
  4. 将工具结果反馈给 LLM，让 LLM 判断假说状态 (confirmed/rejected/pending)
  5. 如果 confirmed/rejected → 写入 claim_ledger，记录 evidence_refs
  6. 如果 pending → LLM 生成新的 search_hints，继续探索
  7. Budget 控制: 每轮后检查 tool_calls / prompt_tokens / rounds
  8. 停止条件: budget 用尽 / 所有假说已解决 / 连续 N 轮无信息增益
```

---

## 5 个工具的真实实现

```python
# read_file: 读目标仓库的真实代码
def tool_read_file(repo_local_path: str, file_path: str, start_line: int = 1, end_line: int = -1) -> str:
    full_path = Path(repo_local_path) / file_path
    lines = full_path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[start_line-1:end_line if end_line > 0 else len(lines)])

# search_repo: grep 代码
def tool_search_repo(repo_local_path: str, pattern: str, max_results: int = 10) -> list[dict]:
    # 使用 subprocess 调用 grep -rn 或 pathlib 遍历
    ...

# list_tree: 列目录
def tool_list_tree(repo_local_path: str, path: str = ".", depth: int = 3) -> str:
    ...

# read_artifact: 读 Stage 1 中间产物
def tool_read_artifact(repo_local_path: str, artifact_name: str) -> str:
    ...

# append_finding: 向 claim_ledger 追加
def tool_append_finding(claim: ClaimRecord, ledger_path: Path) -> None:
    ...
```

---

## 模型无关约束（硬性）

- ❌ 禁止 `import anthropic` / `import openai` / `import google.generativeai`
- ✅ 所有 LLM 调用通过 `LLMAdapter` 接口
- ✅ 能力需求: `tool_calling` + `code_understanding`
- ✅ 如果 adapter/router 为 None，使用默认 mock 行为（回退到现有确定性逻辑）
- ✅ 在 LLM 不支持 tool_calling 时，适配器已内置 prompt-based 回退

---

## 降级策略

| 场景 | 行为 |
|------|------|
| adapter=None | 回退到现有 mock 逻辑（确定性模拟） |
| LLM 调用失败 | 重试 1 次，仍失败则当前假说标记 pending，继续下一个 |
| Budget 超限 | 保存已有 claims，标记 termination_reason="budget_exhausted" |
| 所有工具禁用 | 回退到 mock 逻辑 |

---

## Deliverables

| # | 文件 | 说明 |
|---|------|------|
| 1 | `stage15_agentic.py` | 主实现（替换 mock） |
| 2 | `tests/test_stage15_agentic.py` | 单元测试（mock adapter + fixture） |
| 3 | `tests/test_stage15_integration.py` | 集成测试（用真实小仓库 fixture） |
| 4 | `DECISIONS.md` | 设计决策记录 |
| 5 | fixture 数据 | 如果新建了测试仓库 fixture |

---

## 设计自由区（赛马空间）

以下方面由你自由设计，PM 评审时会比较不同方案的优劣：

- **Prompt 策略**: 如何让 LLM 选择工具？system prompt 怎么写？
- **假说优先级调度**: 除了 priority 排序外，是否根据已有证据动态调整？
- **迭代深度控制**: 何时判定"无信息增益"？用什么指标？
- **证据质量评估**: 如何判断一个 file:line 引用是"强证据"还是"弱证据"？
- **上下文管理**: 多轮工具调用后如何压缩 context 防止超 token？

---

## 输出路径

```
races/r06/agentic/{your-racer-id}/
├── stage15_agentic.py
├── tests/
│   ├── test_stage15_agentic.py
│   └── test_stage15_integration.py
├── DECISIONS.md
└── fixtures/  (如有)
```

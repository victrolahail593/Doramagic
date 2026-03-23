# DECISIONS.md — Phase Runner (S1-Sonnet)

## 核心设计决策

### D1: 分层 import 策略 — 不在模块顶层导入提取模块

**决策**：所有外部模块（extraction、validate、assemble、brick_injector）通过 lazy import 函数（`_import_*`）按需加载，而非模块顶层直接 import。

**原因**：
- phase_runner.py 必须能在任何环境下导入（测试、CI、无 pydantic 的环境），即使依赖缺失也不崩溃。
- Lazy import 是测试中 mock 的最清洁注入点：`patch("phase_runner._import_extraction_modules", ...)` 即可完全控制依赖。
- 与 BRIEF 中"模型无关"原则一致：Phase Runner 本身不依赖任何 LLM SDK。

### D2: 降级策略表（严格遵循 BRIEF）

| 场景 | 实现 |
|------|------|
| `adapter=None` | `_run_stage15` 直接 skip，记录 `stages_skipped` |
| `bricks_dir` 不存在 | `_run_brick_injection` 检查 `os.path.isdir`，skip |
| Stage 3.5 验证失败 | `stage3.5_validate` 进入 `stages_failed`，Stage 4.5 和 5 进入 `stages_skipped`（不调用 compile_knowledge） |
| DSD SUSPICIOUS | 记录 WARNING log，继续执行（不 BLOCK），`dsd_report` 字段暴露给调用方判断 |
| assemble 失败 | `stage5` 进入 `stages_failed`，返回已有产出（`inject_dir=None`） |
| 任何 Exception | 全部 try/except + traceback.format_exc() 记录，不 re-raise |

### D3: Stage 0 幂等性

Stage 0（extract_repo_facts）检查 `artifacts/repo_facts.json` 是否已存在。如果存在，跳过 subprocess 调用并标记 `completed`。原因：
- 管线可重入（re-run after Stage 1-4 LLM 执行完成后）。
- 避免重复 subprocess 开销。

### D4: Stage 3.5 三步拆分

Stage 3.5 内部拆分为三个独立步骤，各自追踪：
1. `stage3.5_validate` — validate_all
2. `stage3.5_confidence` — run_evidence_tagging
3. `stage3.5_dsd` — run_dsd_checks

原因：每步都可能独立失败（比如 validate 模块不可用但 DSD 可用），拆分后调用方可精确诊断哪一步出问题。

### D5: Stage 3.5 validate 失败 → 同时 skip Stage 4.5 AND Stage 5

BRIEF 明确：`Stage 3.5 验证失败 → 记录 stages_failed，不继续到 Stage 4.5`。

实现：检查 `"stage3.5_validate" in stages_failed` 后，将 Stage 4.5 和 Stage 5 都加入 `stages_skipped`（因为 Stage 5 的 assemble 依赖 validation_report.json PASS 门）。

### D6: Stage 1.5 输入构建策略

Stage 1.5 需要 `Stage15AgenticInput`，其中包含 `Stage1ScanOutput`（Stage 1 的 LLM 执行结果）。

**问题**：Phase Runner 编排的是确定性部分；Stage 1 是 LLM 在 OpenClaw 中执行的，没有 JSON 输出文件。

**决策**：构建一个最小化的 `Stage1ScanOutput`（空 findings + hypotheses），让 Stage 1.5 的 agent loop 从零开始探索。这是合理的降级——Stage 1.5 agent loop 本身会自行生成假设（通过 `list_tree`/`search_repo`）。

**备选方案**：读取 `soul/00-soul.md` 解析出假设，但解析文本格式耦合度太高，不如让 agent loop 自主探索。

### D7: sys.path bootstrap 策略

Phase Runner 运行在 `races/r06/runner/s1-sonnet/` 目录，需要访问 4 个包目录：
- `packages/contracts/`
- `packages/shared_utils/`
- `packages/extraction/`
- `races/r06/injection/s1-sonnet/` (brick injector)

采用"向上查找 repo root"策略（检查 `packages/contracts/` 是否存在），支持从 worktree 和主仓库两种路径结构运行。

### D8: PipelineResult 不抛异常

`run_single_project_pipeline` 永远不抛异常，永远返回 `PipelineResult`。调用方通过检查 `stages_failed` 判断是否有问题。这与 BRIEF 中的降级策略一致，并使管线可作为库调用（不需要 try/except 包裹）。

## 与 BRIEF 的偏差

### 偏差 1: Stage 3.5 confidence tagging 不写回卡片文件

BRIEF 未明确说明是否要将 `evidence_tags`/`verdict` 写回 `.md` 文件。当前实现：只在内存中 tag，用于传递给 DSD，不修改磁盘上的卡片文件。

**原因**：写回文件需要 `inject_verdict_into_frontmatter`，增加复杂度且不是核心流程。Knowledge Compiler 的 `load_cards` 会直接读取 YAML frontmatter，如果 LLM 在 Stage 2/3 已经写入了 verdict 字段则自然利用。

**潜在风险**：DSD 依赖 `evidence_tags` 字段，但当前 Phase Runner 在内存中 tag 后直接传入 `run_dsd_checks`，不依赖文件持久化，所以 DSD 结果是正确的。

### 偏差 2: Brick injection 接口来自 r06/injection/s1-sonnet

BRIEF 说"待合并，假设接口如上"，当前使用的是 `races/r06/injection/s1-sonnet/brick_injection.py` 的 `load_and_inject_bricks`。如果合并后接口变化，只需修改 `_import_brick_injector()` 函数。

## 测试覆盖

共 23 个测试，覆盖：
- Helper 函数（`_load_repo_facts`, `_load_cards_as_dicts`）
- PipelineConfig 和 PipelineResult 模型
- Stage 0: 成功/脚本缺失/subprocess 失败/幂等性
- Brick injection: disabled/dir 缺失/成功
- Stage 1.5: adapter=None/disabled/success/failure
- Stage 3.5: validation pass/fail + DSD SUSPICIOUS 不 block + DSD disabled
- Stage 4.5: 成功/budget 参数/failure
- Stage 5: 成功/skip_assembly/failure
- 全管线 happy path
- 全降级：所有模块缺失不崩溃 + output_dir 自动创建

# Doramagic 研究成果全面落地方案

> **日期**: 2026-03-20
> **状态**: 方案完成，待 Tang 审核
> **范围**: 34% 部分落地 → 完整方案 + 39% 未落地 → 赛马落地
> **核心约束**: 模型无关（LLM-agnostic），用户环境复杂，不绑定任何特定大模型

---

# 第零部分：模型无关架构（总纲）

> Tang 明确要求：避免绑定死某种大模型，用户环境是复杂的。
> 这不是一个"加个配置项"就能解决的问题，而是贯穿全部设计的架构原则。

## 0.1 现状问题

当前代码中的模型绑定问题：

| 问题 | 位置 | 严重度 |
|------|------|--------|
| stage15_agentic.py 有 `_gemini` 硬编码变体 | packages/extraction/ | 高 |
| compiler.py 无 LLM 调用但 Stage 4 叙事隐含 Opus 假设 | STAGE-4-synthesis.md | 中 |
| dev-manual-v5.3 子代理表写死 "Opus/Sonnet" | docs/ | 中 |
| validate_extraction.py 纯确定性（OK） | scripts/ | 无 |
| assemble-output.sh 纯确定性（OK） | scripts/ | 无 |

## 0.2 模型无关架构设计

### 核心原则

```
模型无关 = 管线逻辑绑定"能力需求"，不绑定"模型品牌"
```

### 三层抽象

```
Layer 1: Capability Requirement（管线声明需要什么能力）
    ↓
Layer 2: Capability Router（根据用户环境映射到可用模型）
    ↓
Layer 3: LLM Provider Adapter（统一调用接口）
```

### Layer 1: 能力需求标签

每个 Stage 声明所需能力，不声明模型：

| 能力标签 | 含义 | 典型 Stage |
|---------|------|-----------|
| `deep_reasoning` | 需要长链推理、因果分析 | Stage 1 WHY, Stage 4 叙事, Phase E 综合 |
| `structured_extraction` | 结构化信息提取、格式遵循 | Stage 2/3 卡片, Phase F 编译 |
| `tool_calling` | 工具调用、迭代探索 | Stage 1.5 Agent Loop |
| `code_understanding` | 代码阅读理解 | Stage 0 辅助, Stage 1 scan |
| `deterministic` | 无需 LLM | Stage 0 脚本, Stage 3.5 验证, Stage 5 组装 |

### Layer 2: 能力路由器

```python
# capability_router.py — 确定性路由，零 LLM 调用

class CapabilityRouter:
    """
    根据用户声明的可用模型和能力需求，
    选择最合适的模型。
    """

    def __init__(self, available_models: list[ModelDeclaration]):
        """
        available_models 来自用户配置文件 models.json:
        [
          {"model_id": "claude-opus-4-6", "capabilities": ["deep_reasoning", "structured_extraction", "tool_calling", "code_understanding"], "cost_tier": "high"},
          {"model_id": "gemini-2.5-pro", "capabilities": ["deep_reasoning", "structured_extraction", "tool_calling"], "cost_tier": "medium"},
          {"model_id": "gpt-4.1", "capabilities": ["deep_reasoning", "structured_extraction"], "cost_tier": "high"},
          {"model_id": "minimax-01", "capabilities": ["structured_extraction"], "cost_tier": "low"}
        ]
        """
        self.models = available_models

    def route(self, required_capabilities: list[str], prefer_cost: str = "lowest_sufficient") -> str:
        """返回 model_id。如无满足所有能力的模型，降级到最接近的。"""
        # 1. 找满足所有能力的候选
        # 2. 按 cost_tier 排序（lowest_sufficient = 能力够用里最便宜的）
        # 3. 如无完美匹配，找覆盖最多能力的，附带 degraded 警告
        ...
```

### Layer 3: Provider Adapter

```python
# llm_adapter.py — 统一调用接口

class LLMAdapter:
    """
    统一不同 LLM 的调用方式。
    不在管线代码中出现 anthropic.Client() 或 google.GenerativeAI()。
    """

    async def generate(self, model_id: str, messages: list, **kwargs) -> LLMResponse:
        """统一接口，内部按 model_id 前缀分发到对应 provider。"""
        ...

    async def generate_with_tools(self, model_id: str, messages: list, tools: list, **kwargs) -> LLMResponse:
        """工具调用统一接口。对不支持 tool_calling 的模型，回退到 prompt-based 工具调用。"""
        ...
```

### 用户配置文件

用户只需维护一个 `models.json`：

```json
{
  "available_models": [
    {
      "model_id": "claude-opus-4-6",
      "provider": "anthropic",
      "capabilities": ["deep_reasoning", "structured_extraction", "tool_calling", "code_understanding"],
      "cost_tier": "high",
      "api_key_env": "ANTHROPIC_API_KEY"
    },
    {
      "model_id": "gemini-2.5-pro",
      "provider": "google",
      "capabilities": ["deep_reasoning", "structured_extraction", "tool_calling"],
      "cost_tier": "medium",
      "api_key_env": "GOOGLE_API_KEY"
    }
  ],
  "routing_preference": "lowest_sufficient",
  "fallback_strategy": "degrade_and_warn"
}
```

### 对现有代码的影响

| 组件 | 改造 |
|------|------|
| `stage15_agentic.py` / `_gemini.py` | 合并为一个文件，通过 adapter 调用 |
| STAGE-*.md Skill 指令 | 不变（Skill 指令是模型无关的，任何能读懂指令的 LLM 都能执行） |
| `phase_runner.py` / `_gemini.py` | 合并为一个文件，用 router 选模型 |
| scripts/*.py / *.sh | 不变（纯确定性） |
| contracts/ | 不变 |

### 赛马中的模型无关

赛马选手本身使用不同模型（Sonnet/Codex/Gemini/GLM5）开发代码——这没问题。
关键是：**赛马选手写出的代码不能硬编码调用某个模型**。
Brief 中明确：禁止 `import anthropic`、`import google.generativeai`、`import openai`。
所有 LLM 调用必须通过 `LLMAdapter` 接口。

---

# 第一部分：34% 部分落地 — 完整解决方案

## 识别部分落地项

审计中 34% 部分落地的项未逐一列出。基于代码库和研究资产的全面对比，以下 10 项为部分落地状态：

| # | 项 | 现状 | 差距 |
|---|---|------|------|
| P1 | Stage 0 project_narrative | repo_facts.json 存在 | 缺少 v3 反馈要求的 50-100 词叙事摘要 |
| P2 | DSD（欺骗性来源检测） | 暗雷体系 8 指标已定义 | validate_extraction.py 中未实现 |
| P3 | WHY 可恢复性判断 | 概念已定义在暗雷研究中 | Stage 1 指令中未集成 |
| P4 | Cross-project 包 | compare/synthesis/discovery mock 实现存在 | 非 mock、未接入产品主流程 |
| P5 | Platform rules 配置化 | validator.py 存在，PlatformRules 合约已定义 | 无 platform_rules.json 默认配置文件 |
| P6 | Race infrastructure | racekit/ 4 个文件存在 | 评审流程非自动化，选手隔离不够可靠 |
| P7 | Community signals 结构化 | collect-community-signals.py 存在 | 输出无 version/environment/persona 字段 |
| P8 | Stage 4 知识类型路由 | STAGE-4-synthesis.md 存在 | 所有知识用同一叙事格式，无类型路由 |
| P9 | assemble-output.sh 兼容性 | shell 脚本存在且功能完整 | MiniMax 等模型跳过 shell 直接用 Python 变体（缺 FEATURE INVENTORY） |
| P10 | _gemini/_sonnet 变体文件 | 多个 _gemini.py 变体存在 | 应合并为模型无关实现 |

---

## P1: Stage 0 project_narrative

### 现状
`extract_repo_facts.py` 输出 `repo_facts.json`，包含 languages/frameworks/entrypoints/commands 等确定性字段。contracts 中 `RepoFacts` 有 `repo_summary: str` 字段但无 `project_narrative`。

### 差距
v3-product-feedback.md 第 2 条：Stage 0 应加一个 50-100 词的项目叙事摘要作为所有后续子代理的共享上下文。Tang 确认必要，可确定性生成（模板 + repo_facts 关键字段），不需要 LLM。

### 完整方案

**1. 扩展 contracts**

在 `RepoFacts` 中新增字段：

```python
class RepoFacts(BaseModel):
    # ... existing fields ...
    project_narrative: str = ""  # 50-100 词确定性叙事摘要
```

**2. 实现确定性叙事生成**

在 `extract_repo_facts.py` 末尾新增函数：

```python
def generate_project_narrative(facts: dict) -> str:
    """
    确定性模板：无 LLM。
    从 repo_facts 的 languages, frameworks, entrypoints, commands, repo_summary
    组合出一段 50-100 词的叙事。
    """
    template = (
        "{name} is a {primary_lang} project"
        "{framework_clause}"
        " that {summary_clause}."
        " It provides {commands_clause}."
        " Key entry points: {entrypoints_clause}."
    )
    # ... 填充逻辑 ...
```

**3. Stage 1/2/3 输入注入**

在 STAGE-1-essence.md 的"## 输入"部分新增一行：
```
- 读取 <output>/artifacts/repo_facts.json 中的 project_narrative 字段作为项目背景
```

**工作量**: 约 2 小时，不需赛马。PM 直接实现。

---

## P2: DSD（欺骗性来源检测）

### 现状
dark-traps.md 定义了 8 项 DSD 检查指标：
1. Rationale Support Ratio
2. Temporal Conflict Score
3. Exception Dominance Ratio
4. Support-Desk Share
5. Public Context Completeness
6. Persona Divergence Score
7. Dependency Dominance Index
8. Narrative-Evidence Tension

validate_extraction.py 当前只做格式验证 + evidence traceability + fact-checking gate。不检查"证据是否在欺骗你"。

### 差距
从"有没有证据"升级到"证据是否欺骗你"。8 项指标全部是确定性可计算的（基于卡片 schema + repo_facts + community_signals 统计量），不需要 LLM。

### 完整方案

**新增 `deceptive_source_detection.py`**

```python
def run_dsd_checks(cards: list[dict], repo_facts: dict, community_signals: str) -> DSDReport:
    """
    8 项确定性检查，每项返回 score (0-1) + 是否触发 + 详细说明。
    总体状态：CLEAN / WARNING / SUSPICIOUS
    """
    checks = []

    # 1. Rationale Support Ratio
    # 比较 WHY 卡片中 reasoning_chain 有 code/doc/community 证据支撑的比例
    # 阈值：< 0.3 触发 WARNING

    # 2. Temporal Conflict Score
    # 检测同一 subject 的卡片是否引用了不同时代的证据
    # 方法：从 sources 中提取版本号/日期，检测跨度 > 2 major versions

    # 3. Exception Dominance Ratio
    # community_signals 中 "workaround"/"edge case"/"specific version" 占比
    # 阈值：> 0.6 触发 WARNING（异常路径主导）

    # 4. Support-Desk Share
    # community_signals 中 maintainer 回复占总回复的比例
    # 方法：统计 author 字段出现频率
    # 阈值：> 0.8 触发 WARNING（maintainer monologue）

    # 5. Public Context Completeness
    # 检查卡片 reasoning_chain 中 "inferred"/"推测" 等词占比
    # 阈值：> 0.4 触发 WARNING

    # 6. Persona Divergence Score
    # 检测不同 sources 的 persona 假设是否一致
    # 方法：提取 sources 中的环境假设，检测矛盾

    # 7. Dependency Dominance Index
    # repo_facts.dependencies 中核心功能依赖外部闭源服务的比例
    # 阈值：> 0.5 触发 WARNING（开源代码，闭源灵魂）

    # 8. Narrative-Evidence Tension
    # 检测 Stage 4 叙事中的断言是否都有卡片支撑
    # 方法：提取叙事中的断言句，匹配卡片 statement

    return DSDReport(checks=checks, overall_status=...)
```

**集成到 validate_extraction.py**

在 `validate_all()` 函数末尾新增：
```python
# --- DSD 检查（v1.1 new） ---
dsd_report = run_dsd_checks(report["cards"], repo_facts, community_signals)
report["dsd"] = dsd_report
# DSD 是 WARNING 不是 BLOCKING — 标注不阻断
```

**关键决策**: DSD 结果是 WARNING（标注），不是 BLOCKING（阻断）。原因：误报代价高于漏报，且 DSD 检查本身是新系统需要校准。

**工作量**: 约 1 天。可赛马但 ROI 不高，建议 PM 指定 Sonnet 实现。

---

## P3: WHY 可恢复性判断

### 现状
dark-traps.md 定义了管线保护第 1 条：Stage 1 应允许输出"WHY 无法从公开证据可靠重建"。
STAGE-1-essence.md 当前不包含此判断。

### 差距
Stage 1 Q6/Q7 目前强制要求回答。当项目属于"开源代码，闭源灵魂"（暗雷 #4）或"隐藏上下文"（暗雷 #5）时，强制回答导致幻觉 WHY。

### 完整方案

**修改 STAGE-1-essence.md**

在 Q6/Q7 约束部分新增：

```markdown
## WHY 可恢复性判断（在回答 Q6 之前）

在回答 Q6/Q7 之前，先评估 WHY 是否可从公开证据重建：

### 判断标准
- 代码中有 ADR (Architecture Decision Records) 或 `// because ...` 注释 → ✅ 可恢复
- README/CONTRIBUTING 中有设计哲学段落 → ✅ 可恢复
- Issues/PRs 中有设计决策讨论 → ✅ 可恢复（社区证据）
- 以上全无，但代码模式强烈暗示设计意图 → ⚠️ 可推断（标注置信度为 LOW）
- 代码是封装层/客户端，核心逻辑在闭源服务 → ❌ 不可恢复

### 输出
如果判断为不可恢复：
```
## 6. 设计哲学
[WHY_UNRECOVERABLE] 此项目的核心设计决策发生在公开代码之外（原因：[具体原因]）。
以下推测基于代码模式，置信度 LOW：...
```

## ⛔ Hard Gate 更新
- Q6 如标注 [WHY_UNRECOVERABLE]，不算 Hard Gate 失败
- 但必须给出具体原因和推测版本
```

**工作量**: 约 30 分钟改 STAGE-1-essence.md。不需赛马。

---

## P4: Cross-project 包从 mock 到真实

### 现状
- `compare.py` — 确定性 Union-Find + Jaccard + slot 匹配。逻辑完整，但输入来自固定 fixtures，未接真实提取输出。
- `synthesis.py` — 消费 compare signals + community knowledge，产出 synthesis_report。逻辑完整，但同样接 fixtures。
- `discovery.py` — 候选发现。mock 实现。

### 差距
这些模块是 System B（预提取管线）的核心，r05 赛马已经在跑。差距不在代码本身，而在：
1. compare/synthesis 没有真实数据跑过端到端
2. discovery 的 GitHub API 集成是 mock
3. 没有集成测试连通 extraction → fingerprint → compare → synthesis 全链路

### 完整方案

**不需要重写代码**。需要的是：

1. **真实数据冒烟测试**：用已有的 exp-seo-skills/ 4 个 SEO 项目的提取结果，转换为 `ProjectFingerprint` 格式，跑通 compare → synthesis 全链路

2. **discovery GitHub 集成**：实现真实 GitHub search API 调用（替换 mock），通过 `LLMAdapter` 做相关度评估（目前 mock 返回固定分数）

3. **集成测试**：
```python
def test_extraction_to_synthesis_e2e():
    """
    fixture: 2 个 SEO 项目的 repo_facts.json + Stage 1 output
    → fingerprint → compare → synthesis → 验证 synthesis_report 完整性
    """
```

**工作量**: 约 2-3 天。建议 r06 赛马中作为一个赛道。

---

## P5: Platform rules 配置化

### 现状
`PlatformRules` Pydantic model 已定义（allowed_tools, metadata_whitelist, storage_prefix 等）。
`validator.py` 使用硬编码的 OpenClaw 规则。
无默认配置文件。

### 差距
用户无法自定义平台规则。虽然 v1 只支持 OpenClaw，但架构应允许未来扩展到其他平台。

### 完整方案

**1. 创建默认配置**

`platform_rules.json`:
```json
{
  "schema_version": "dm.platform-rules.v1",
  "platform": "openclaw",
  "allowed_tools": ["exec", "read", "write"],
  "metadata_openclaw_whitelist": ["always", "emoji", "homepage", "skillKey", "primaryEnv", "os", "requires", "install"],
  "forbid_frontmatter_fields": ["cron"],
  "storage_prefix": "~/clawd/",
  "tool_name_mapping": {
    "Bash": "exec",
    "Read": "read",
    "Write": "write",
    "Execute": "exec"
  }
}
```

**2. 修改 validator.py**

```python
def load_platform_rules(config_path: str = None) -> PlatformRules:
    if config_path and Path(config_path).exists():
        return PlatformRules.model_validate_json(Path(config_path).read_text())
    # 内置 OpenClaw 默认值
    return PlatformRules()
```

**工作量**: 约 2 小时。PM 直接实现。

---

## P6: Race infrastructure 加固

### 现状
racekit/ 有 race_brief.py, race_config.py, race_review.py, race_workspace.py。
feedback_race_isolation.md 记录了两次文件覆盖事故。

### 差距
- 选手隔离不够可靠（Gemini 覆盖 Sonnet 输出）
- 评审流程手动
- 无自动化的选手输出收集

### 完整方案

**1. 强制路径隔离（已有方案，确保执行）**

Brief 模板强制：
```markdown
## 输出路径（硬性约束）
- 所有代码文件名必须包含选手标识：`{module}_{racer}.py`（例 `stage15_agentic_sonnet.py`）
- 或使用 git worktree 隔离（Sonnet 子代理用 `isolation: "worktree"`）
- 外部选手（Codex/Gemini/GLM5）：Brief 中指定选手命名的输出目录
```

**2. 评审自动化**

在 `race_review.py` 中新增：
```python
def auto_review_checklist(racer_output_dir: str) -> ReviewReport:
    """
    自动检查：
    1. 所有 deliverable 文件存在
    2. tests 全部通过
    3. 无 import anthropic / import openai / import google.generativeai（模型无关检查）
    4. contracts 兼容性（输入输出 schema 匹配）
    5. 代码行数在 Brief 范围内
    """
```

**工作量**: 约 3 小时。PM 实现。

---

## P7: Community signals 结构化

### 现状
`collect-community-signals.py` 输出 `community_signals.md`，包含 SIG-xxx 信号。
信号无 version/environment/persona 字段标注。

### 差距
v5 暗雷体系管线保护第 3 条：社区规则必须携带适用域约束。当前的 community_signals.md 是纯文本，无结构化适用域。

### 完整方案

**1. 定义结构化信号 schema**

```python
class CommunitySignal(BaseModel):
    signal_id: str  # SIG-001
    title: str
    description: str
    source_type: Literal["issue", "pr", "changelog", "security_advisory", "discussion"]
    source_ref: str  # Issue #123, CHANGELOG v2.0

    # 适用域约束（新增）
    applicable_versions: Optional[str] = None  # ">=2.0,<3.0" or None (all versions)
    applicable_environments: list[str] = []  # ["linux", "docker", "ci"] or [] (all)
    applicable_personas: list[str] = []  # ["beginner", "enterprise"] or [] (all)
    is_exception_path: bool = False  # True = 边缘情况，False = 常见路径
    confidence: Literal["high", "medium", "low"] = "medium"
```

**2. 修改 collect-community-signals.py**

在信号提取时，同时提取适用域信息（确定性规则）：
- 版本：从 CHANGELOG/Issue 中提取版本号
- 环境：从 Issue 标签/内容中提取 OS/环境信息
- 角色：从 Issue 内容中检测"beginner"/"advanced"等关键词
- 异常路径：检测 "workaround"/"edge case"/"specific" 等词

**3. 修改 STAGE-3-rules.md**

在社区陷阱卡模板中新增字段：
```markdown
applicable_versions: ">=2.0"
applicable_environments: ["docker", "kubernetes"]
is_exception_path: false
```

**工作量**: 约 1 天。可由 Sonnet 子代理实现。

---

## P8: Stage 4 知识类型路由

### 现状
STAGE-4-synthesis.md 要求统一输出 expert_narrative.md，所有知识类型用叙事格式。
5-challenges.md 第 2 条结论：应按知识类型路由格式。事实→结构化列表，规则→规则声明+因果注释，哲学/陷阱→纯叙事。

### 差距
Knowledge Compiler 的核心功能——按类型路由输出格式——未在 Stage 4/5 中实现。

### 完整方案

**修改 STAGE-4-synthesis.md（或新增 STAGE-4.5-compile.md）**

```markdown
# Stage 4.5: 知识编译

## 输入
- 所有卡片（CC-*/WF-*/DR-*）
- 00-soul.md（Q6 哲学 + Q7 心智模型）

## 编译规则

按知识类型分流输出格式：

### 事实类（WHAT/HOW）→ 结构化
- CC 概念卡 → 精简列表（概念名 + 一句话定义 + Is/IsNot 表最关键行）
- WF 工作流卡 → 步骤列表（Step 1→2→3，每步一行）

### 规则类（IF/THEN）→ 规则声明
- DR 代码规则 → `[SEVERITY] rule_title — IF condition THEN consequence`
- DR 社区陷阱 → `[SEVERITY] trap_title — 场景一句话 + "来源: Issue #N"`

### 哲学/心智模型（WHY）→ 叙事
- Q6 设计哲学 → 2-3 段叙事（保持 STAGE-4 现有风格）
- Q7 心智模型 → 1 段类比式叙事

### 陷阱（UNSAID）→ 警告格式
- 3 个因果链 → "为什么这样设计" 叙事（保持 STAGE-4 现有风格）
- 3 个踩坑故事 → "⚠️ 你会遇到" 警告格式（保持生动）

## Token 预算
- 结构化部分（事实 + 规则）：~50% 总预算
- 叙事部分（哲学 + 陷阱）：~40% 总预算
- 余量：10%
- 总预算：1500-2000 tokens（不含 FEATURE INVENTORY）

## 输出
写入 <output>/soul/compiled_knowledge.md
格式：CRITICAL RULES → CONCEPTS → WORKFLOWS → DESIGN PHILOSOPHY → TRAPS → REFERENCE
```

**修改 assemble-output.sh**

将 `cat "$NARRATIVE"` 替换为 `cat "$COMPILED_KNOWLEDGE"`（如果存在），fallback 到 `$NARRATIVE`。

**工作量**: 约 4 小时。不需赛马，PM 实现。

---

## P9: assemble-output.sh / assemble_output.py 统一

### 现状
- `assemble-output.sh`：功能完整，有 FEATURE INVENTORY、CRITICAL RULES、QUICK REFERENCE
- 多个 `assemble_output.py` 变体（skills/doramagic-s1/s2/s3）：Python 版但缺 FEATURE INVENTORY
- MiniMax 等模型跳过 shell 脚本直接调用 Python 版，导致 FEATURE INVENTORY 丢失

### 差距
两套组装逻辑不一致，导致产出质量因模型而异。

### 完整方案

**统一为 Python 实现**

将 `assemble-output.sh` 的全部逻辑移植到 `assemble_output.py`（soul-extractor 主版本）：

```python
def assemble_output(output_dir: str) -> AssemblyResult:
    """
    统一组装逻辑（Python，无 shell 依赖）：
    1. 检查 validation_report.json PASS
    2. 构建 CRITICAL RULES section（从 DR-*.md 卡片）
    3. 构建 FEATURE INVENTORY section（从 repo_facts.json）
    4. 构建 MODULE MAP section（从 module-map.md）
    5. 构建 EXPERT KNOWLEDGE section（从 expert_narrative.md 或 compiled_knowledge.md）
    6. 构建 COMMUNITY WISDOM section（从 community-wisdom.md）
    7. 构建 QUICK REFERENCE table（从所有 DR 卡片）
    8. 组装 CLAUDE.md
    9. 复制为 .cursorrules
    10. 生成 advisor-brief.md
    11. 生成 project_soul.md
    12. 运行 validate_output.py
    """
```

**保留 assemble-output.sh 作为包装**

```bash
#!/bin/bash
# 代理到 Python 实现
python3 "$(dirname "$0")/assemble_output.py" --output-dir "$1"
```

**工作量**: 约半天。PM 指定 Sonnet 实现。

---

## P10: _gemini/_sonnet 变体文件合并

### 现状
存在多个硬编码变体：
- `stage15_agentic.py` + `stage15_agentic_gemini.py`
- `phase_runner.py` + `phase_runner_gemini.py`
- `app.py` + `app_gemini.py` + `app_sonnet.py`
- `compare.py` → `synthesis_gemini.py`、`discovery_gemini.py`

### 差距
违反模型无关原则。代码重复。维护成本 N 倍。

### 完整方案

**逐步合并，通过 Capability Router 分发**

1. 对每对 `xxx.py` + `xxx_gemini.py`，提取差异部分
2. 差异通常是：prompt 模板格式、API 调用方式、输出解析
3. 将差异封装到 `LLMAdapter` 的 provider 层
4. 主文件通过 `CapabilityRouter.route()` 获取 model_id，通过 `LLMAdapter.generate()` 调用

**优先级排序**：
1. `phase_runner.py` — 编排核心，合并价值最高
2. `stage15_agentic.py` — Agent loop 核心
3. `app.py` — API 层，影响较小

**工作量**: 约 1-2 天。可在模型无关架构落地时一并完成。

---

# 第二部分：39% 未落地 — 赛马落地方案

## P0-1: Agentic 提取（Agent 动态读代码探索）

### 研究资产
- 三方综合报告：`research/agentic-extraction/synthesis.md`
- 5 个共识：混合架构（Stage 1.5 插入）、假说驱动、WHY/UNSAID 获益最大、3-5 工具最小集、优雅降级
- MVP 工具集：read_artifact / list_tree / search_repo / read_file / append_finding
- 5 个中间文件：hypotheses.jsonl / exploration_log.jsonl / claim_ledger.jsonl / evidence_index.json / context_digest.md

### 当前代码状态
`stage15_agentic.py` 是 **mock 实现**（docstring 明确写了"赛马阶段不接真实 LLM"）。
Contracts 已完整定义（Stage15AgenticInput/Output, Hypothesis, ClaimRecord, ExplorationLogEntry 等）。
mock 逻辑：从 Stage 1 findings 确定性模拟工具调用，不读真实代码。

### 差距
mock → 真实 Agent Loop：
1. 真实 LLM 驱动的假说评估和工具选择
2. 真实代码阅读（通过 read_file 工具读目标仓库文件）
3. 迭代深挖循环（假说→工具调用→证据收集→更新假说→继续）
4. Budget 控制（max_rounds, max_tool_calls, stop_after_no_gain）

### 赛马设计

**模块**: `extraction.stage15_agentic`（替换 mock 为真实实现）

**赛道**: 2 选手并行

**Brief 核心要求**:

```markdown
## 任务
实现真实的 Stage 1.5 Agentic Exploration Loop。

## 输入
- Stage15AgenticInput（来自 contracts，schema 已冻结）
  - stage1_output: Stage 1 的 findings + hypotheses
  - repo: RepoRef（含 local_path，可访问真实代码文件）
  - repo_facts: RepoFacts
  - budget: Stage15Budget
  - toolset: Stage15Toolset

## 输出
- Stage15AgenticOutput（来自 contracts，schema 已冻结）
  - promoted_claims: 经证据验证的知识声明
  - 5 个中间文件（hypotheses/exploration_log/claim_ledger/evidence_index/context_digest）

## 核心行为
1. 从 hypotheses 中按 priority 排序取下一个假说
2. 通过 LLMAdapter 调用 LLM，让 LLM 决定使用哪个工具验证该假说
3. 执行工具调用（read_file → 读真实代码文件，search_repo → grep 代码）
4. 将工具结果反馈给 LLM，让 LLM 判断假说是否得到证据支撑
5. 如果 confirmed/rejected，写入 claim_ledger
6. 如果 pending，生成新的 search_hints，继续探索
7. 循环直到 budget 用尽或所有假说已解决

## 模型无关约束
- 所有 LLM 调用通过 LLMAdapter 接口
- 能力需求：tool_calling + code_understanding
- 不允许 import anthropic / import openai / import google.generativeai
- 在 LLM 不支持 tool_calling 时，回退到 prompt-based 工具选择

## 降级策略
- LLM 失败 → 回退到 mock 逻辑（当前 stage15_agentic.py 的确定性逻辑）
- Budget 超限 → 保存已有 claims，标记 termination_reason = "budget_exhausted"

## 验收标准
1. fixtures 中的 2 个测试仓库（python-dotenv, wger）端到端通过
2. promoted_claims 中 confirmed 的 claim 必须有 file:line 证据
3. check_claims_have_evidence() 必须返回 True
4. 在 budget 为 5 rounds / 30 tool_calls 时完成
5. 不硬编码任何模型名
```

**评审重点**: 工具选择策略质量、证据绑定完整性、budget 控制精度、降级行为。

---

## P0-2: 积木系统（Building Blocks / Soul Lego Bricks）

### 研究资产
- 三方综合报告：`research/soul-lego-bricks/reports/synthesis-report.md`
- 共识：2 层结构（L1 框架级 200-400 tokens, L2 模式级 400-800 tokens），总注入 ≤2500 tokens
- Django 和 React 为最高优先级目标
- WHY 知识长保质期，UNSAID 知识 3-6 月衰减
- 包含反模式积木

### 当前代码状态
- contracts 中有 `DomainBrick` model（brick_id, domain_id, knowledge_type, statement, confidence, signal, source_project_ids, support_count, evidence_refs, tags）
- `Stage1ScanInput` 有 `domain_bricks: list[str] | None = None` 和 `include_domain_bricks: bool = False`
- 无实际积木数据
- 无积木制作流程
- 无积木注入 Stage 1/2/3 的实现

### 差距
1. 没有积木——L1/L2 积木数据不存在
2. 没有制作流程——如何从预提取数据生成积木
3. 没有注入机制——积木如何影响 Stage 1/2/3 提取质量

### 赛马设计

积木系统分两个赛道：

**赛道 A: 积木制作（Brick Forge）**

```markdown
## 任务
设计并实现积木制作流程：从已有研究资产和代码分析中，为 Django 框架生成 L1/L2 积木。

## 输出产物
1. brick_forge.py — 积木制作脚本
2. bricks/django/ — Django L1 + L2 积木（JSONL 格式，符合 DomainBrick schema）
3. bricks/react/ — React L1 + L2 积木（同上）

## L1 积木规范（框架级，200-400 tokens）
每个积木是一个 DomainBrick，knowledge_type 从以下选：
- capability: "Django 的 ORM 提供声明式模型定义，自动生成数据库 migration"
- rationale: "Django 选择 MTV 而非 MVC 是因为 view 在 Django 中是逻辑层不是展示层"
- constraint: "Django middleware 执行顺序影响安全行为，CSRF middleware 必须在 Session 之后"
- failure: "N+1 查询是 Django ORM 最常见性能陷阱，用 select_related/prefetch_related 解决"

## L2 积木规范（模式级，400-800 tokens）
更具体的最佳实践/反模式：
- "Django settings 应用 django-environ 管理，不要硬编码 SECRET_KEY"
- "Django 的 signals 是隐式耦合，社区共识是能用 explicit service layer 就不用 signal"

## 积木来源
1. 从 Django 官方文档的 design philosophies 提取（L1）
2. 从 Django community 高频 Issue/Stack Overflow 提取（L2）
3. 从已有 exp-seo-skills/ 等实验中复用提取结论

## 模型无关约束
- brick_forge.py 通过 LLMAdapter 调用 LLM 辅助提取
- 但积木本身是确定性产物（JSONL 文件），一旦生成不依赖 LLM
- 能力需求：deep_reasoning（理解框架设计哲学）

## 验收标准
1. Django L1 积木 ≥ 10 个，L2 积木 ≥ 20 个
2. React L1 积木 ≥ 8 个，L2 积木 ≥ 15 个
3. 每个积木有 evidence_refs（文档 URL 或代码引用）
4. 积木 statement 不超过 token 预算
5. 包含至少 3 个反模式积木（知识类型 = failure）
```

**赛道 B: 积木注入（Brick Injection）**

```markdown
## 任务
实现积木注入 Stage 1/2/3 的机制。

## 核心逻辑
1. Stage 0 框架检测（已有）→ 识别目标项目用了 Django/React/...
2. 匹配积木库 → 加载对应框架的 L1+L2 积木
3. 注入 Stage 1：积木作为 domain_bricks 传入，让 LLM 知道框架基线知识
4. 注入 Stage 2/3：积木作为锚点，减少搜索面（"你不需要重新发现 Django MTV 模式，这是框架基线"）

## 注入方式
在 STAGE-1-essence.md 的输入部分注入：
```
如果存在领域积木，你已经知道以下框架基线知识：
[积木内容]
你的任务是发现这个具体项目在基线之上的独特做法。
不要重复积木中已有的知识。
```

## 度量
- 无积木 vs 有积木的 A/B 对比（使用已有 benchmark 体系）
- 目标：有积木时 WHY 提取质量 +20%（Brick 效应）

## 验收标准
1. Stage 1 输入正确包含 domain_bricks
2. Stage 1 输出的 findings 不重复积木已有知识（overlap < 20%）
3. 有积木时 WHY 提取分数 ≥ 无积木时（不要求 +20%，但必须不下降）
4. 模型无关：通过 LLMAdapter 调用
```

---

## P0-3: Knowledge Compiler

### 研究资产
- v3 定义 §12：按知识类型路由格式，过滤置信度，U 型排序，≤2000 token
- v5 定义：typed objects path + narrative path
- 5-challenges.md §2：结论是"一天工程量"，风险已从高降到低
- v3-product-feedback.md：A/B 实验 14:14 平手，编译格式省 43% token 但不改变下游任务表现

### 当前代码状态
- `packages/skill_compiler/` 存在但是 **Phase F 的 Skill 组装器**（跨项目综合后编译为 OpenClaw Skill）
- 不是 **Stage 内部的知识格式编译器**
- Stage 4 STAGE-4-synthesis.md 全部用叙事格式，无类型路由

### 差距
需要区分两个 "compiler"：
1. **Stage-level Knowledge Compiler**（本项）：Stage 2/3 的卡片 → 按类型编译 → 注入 CLAUDE.md
2. **Phase-level Skill Compiler**（已有）：跨项目综合 → 编译为 OpenClaw SKILL.md

Stage-level compiler 不存在。

### 赛马设计

**模块**: `extraction.knowledge_compiler`（新模块，Stage 4.5 位置）

```markdown
## 任务
实现 Stage-level Knowledge Compiler：将提取的卡片按知识类型编译为不同格式的输出段落。

## 输入
- 所有卡片文件（CC-*/WF-*/DR-*）的 YAML frontmatter + body
- 00-soul.md（Q6/Q7）
- repo_facts.json（用于 FEATURE INVENTORY）

## 输出
compiled_knowledge.md — 替代 expert_narrative.md 作为 CLAUDE.md 的主内容

## 编译规则

| 知识类型 | 来源 | 编译格式 | Token 占比 |
|---------|------|---------|-----------|
| CRITICAL RULES | DR-* (CRITICAL/HIGH) | `[SEVERITY] title — IF/THEN rule` | ~15% |
| CONCEPTS | CC-* | `**ConceptName**: one-line definition. Is: X. IsNot: Y.` | ~10% |
| WORKFLOWS | WF-* | `Step 1 → Step 2 → Step 3` (one line per workflow) | ~10% |
| DESIGN PHILOSOPHY | Q6 | 2-3 paragraph narrative (preserve Stage 4 style) | ~15% |
| MENTAL MODEL | Q7 | 1 paragraph analogy narrative | ~5% |
| WHY CHAINS | Top 3 causal chains from DR-* rationale | Narrative "Why designed this way" | ~15% |
| TRAPS | DR-100+ community traps | ⚠️ warning format with Issue# | ~15% |
| FEATURE INVENTORY | repo_facts.json | Structured list | ~10% |
| QUICK REFERENCE | All DR-* | Table: rule | severity | ~5% |

## 排序（U 型）
1. 最危险的先（CRITICAL RULES）
2. 最有用的中（CONCEPTS → WORKFLOWS → FEATURE INVENTORY）
3. 最深的后（DESIGN PHILOSOPHY → MENTAL MODEL → WHY CHAINS → TRAPS）
4. 速查末（QUICK REFERENCE）

## Token 预算
总计 1500-2000 tokens。超预算时：
- 先砍 MEDIUM/LOW 规则
- 再砍 QUICK REFERENCE（只保留 CRITICAL/HIGH）
- 哲学/心智模型/陷阱不砍（核心价值）

## 置信度过滤
- confidence == REJECTED 的卡片不进入编译
- confidence == WEAK 的卡片加 [推测] 标注

## 模型无关约束
- 编译逻辑全部确定性（模板 + 提取 + 格式化），无 LLM 调用
- 纯 Python 实现

## 验收标准
1. 输入 python-dotenv 的卡片集 → 输出 compiled_knowledge.md
2. Token 数在 1500-2000 范围内
3. 包含所有 9 个段落
4. CRITICAL rules 排在最前
5. 不包含 REJECTED 的卡片
```

**评审重点**: 格式可读性、token 效率、U 型排序合理性。

---

## P1-4: 置信度四级体系

### 研究资产
- v3 §11：SUPPORTED / CONTESTED / WEAK / REJECTED
- policy_action：ALLOW_CORE / ALLOW_STORY / QUARANTINE
- Gemini confidence-system 报告：Evidence-Chain Tagging (ECT)
- 证据类型：[CODE] / [DOC] / [COMMUNITY] / [INFERENCE]
- 布尔代数：CODE AND DOC = Core Truth; COMMUNITY AND NOT DOC = Unsaid Knowledge; INFERENCE ONLY = Experimental Inference

### 当前代码状态
- DR 卡片有 `confidence: 0.98`（0-1 浮点数）
- validate_extraction.py 检查 confidence 是否在 [0, 1] 范围
- 无 verdict system、无 evidence chain tagging

### 差距
从单一浮点数 → 结构化置信度体系（证据链标签 + 确定性裁定）

### 赛马设计

**模块**: `extraction.confidence_system`（新模块，嵌入 Stage 3.5）

```markdown
## 任务
实现 Evidence-Chain Tagging + Deterministic Verdict System。

## 设计

### Step 1: 证据链标签（在卡片提取时）
每个 evidence_ref 自动标注类型：
- [CODE]: 来自代码文件引用 (evidence.kind == "file_line")
- [DOC]: 来自 README/docs 引用 (path contains "doc"/"README"/"guide")
- [COMMUNITY]: 来自 Issue/PR/CHANGELOG 引用 (evidence.kind == "community_ref")
- [INFERENCE]: LLM 推理（无直接证据）

### Step 2: 确定性裁定（在 Stage 3.5 验证时）
对每张卡片，根据证据组合判定 verdict：

| 证据组合 | Verdict | Policy Action |
|---------|---------|---------------|
| CODE + DOC | SUPPORTED | ALLOW_CORE |
| CODE + COMMUNITY | SUPPORTED | ALLOW_CORE |
| DOC + COMMUNITY | SUPPORTED | ALLOW_STORY |
| CODE only | SUPPORTED | ALLOW_CORE |
| COMMUNITY only (NOT DOC) | CONTESTED | ALLOW_STORY + 标注 "unsaid knowledge" |
| INFERENCE + any 1 corroboration | WEAK | ALLOW_STORY + 标注 [推测] |
| INFERENCE only | REJECTED | QUARANTINE |
| Contradicting evidence | CONTESTED | ALLOW_STORY + 标注冲突 |

### Step 3: 修改卡片 schema
在 YAML frontmatter 中新增：
```yaml
evidence_tags: [CODE, COMMUNITY]
verdict: SUPPORTED
policy_action: ALLOW_CORE
```

旧 `confidence: 0.98` 保留为 LLM 自评分（不参与 verdict 判定）。

## 模型无关
- 证据类型标注：确定性（路径匹配规则）
- Verdict 裁定：确定性（布尔代数，无 LLM）
- 纯 Python 实现

## 验收标准
1. python-dotenv 的 DR 卡片全部标注 evidence_tags + verdict
2. 至少 1 张卡片判定为 CONTESTED（社区陷阱通常是 COMMUNITY only）
3. validate_extraction.py 集成 verdict 检查
4. Knowledge Compiler 消费 verdict 做过滤
```

---

## P1-5: 社区规则适用域约束

### 差距
与 P7 (Community signals 结构化) 紧密关联。P7 解决信号输入端的结构化，P1-5 解决卡片输出端的约束标注。

### 赛马设计（与 P7 合并为一个赛道）

```markdown
## 任务
在 DR-100+ 社区陷阱卡中新增适用域字段，在 Stage 3.5 验证中检查适用域完整性。

## 卡片 schema 扩展
```yaml
# DR-101 示例
applicable_versions: ">=0.19.0"  # 此陷阱从 v0.19.0 开始存在
applicable_environments: []  # 空 = 所有环境
applicable_personas: ["beginner"]  # 初学者更容易踩
is_exception_path: false  # 不是边缘情况，是常见路径
source_confidence: high  # 来源可靠度
```

## STAGE-3-rules.md 修改
在社区陷阱卡模板中添加这些字段。
在约束中新增："每张 DR-100+ 卡片必须填写 applicable_versions（可以是 'all'）和 is_exception_path"。

## validate_extraction.py 修改
新增检查：
- DR-100+ 卡片必须有 applicable_versions 字段
- DR-100+ 卡片必须有 is_exception_path 字段
- 如果 is_exception_path == true，Knowledge Compiler 中降低优先级排序

## 验收标准
1. DR-100+ 卡片全部有适用域字段
2. validate_extraction.py 对缺失字段报错
3. Knowledge Compiler 优先输出 is_exception_path == false 的规则
```

---

## P1-6: 赛马资产整合

### 现状
packages/cross_project/ 有 compare.py / synthesis.py / discovery.py，packages/platform_openclaw/ 有 validator.py，packages/skill_compiler/ 有 compiler.py。这些是赛马产物，r05 正在跑。

### 差距
这些模块各自独立运行，未连通为产品主流程。需要 orchestration.phase_runner 把它们串起来。

### 赛马设计

**这是 orchestration.phase_runner 的职责**，已在 dev-manual-v5.3 §3.4 定义为"重点赛马 Round 4B"。

当前 phase_runner.py 存在但是 mock。落地时需要：

```markdown
## 任务
将 phase_runner.py 从 mock 升级为真实编排：
Phase A (need_profile) → Phase B (discovery) → Phase C (extraction × N) →
Phase D (community) → Phase E (compare + synthesis) → Phase F (skill_compiler) →
Phase G (validator) → Phase H (delivery)

## 核心约束
1. 每个 Phase 调用对应 packages/ 中的模块
2. Phase 之间通过文件传递（Filesystem-as-Memory）
3. 任何 Phase 失败 → 降级策略（见 dev-manual-v5.3 §2.2）
4. 所有 LLM 调用通过 CapabilityRouter + LLMAdapter

## 验收标准
1. need_profile.json → SKILL.md 全链路跑通（用 fixture 数据）
2. 单项目管线（Stage 0-5）独立可跑
3. 多项目管线（Phase A-H）至少 2 个项目跑通
4. 降级：Phase 失败时不 crash，记录 degraded 状态继续
```

---

## P1-7: FEATURE INVENTORY

### 差距
assemble-output.sh 有 FEATURE INVENTORY 但 Python 变体没有。与 P9 合并解决。

**解决方案**: P9 已覆盖。统一为 Python 实现后，FEATURE INVENTORY 逻辑自然包含。

---

## P2-8: 子代理模型路由

### 差距
dev-manual-v5.3 定义了子代理路由表但未实现。

### 解决方案
**由第零部分的模型无关架构覆盖。** CapabilityRouter + models.json 就是子代理模型路由的实现。

具体实现：
```python
# 在 phase_runner.py 中
class PhaseRunner:
    def __init__(self, router: CapabilityRouter, adapter: LLMAdapter):
        self.router = router
        self.adapter = adapter

    async def run_stage1(self, input: Stage1ScanInput):
        model = self.router.route(["deep_reasoning", "code_understanding"])
        # Stage 1 需要深度推理 → router 会选最强的可用模型
        ...

    async def run_stage2(self, input):
        model = self.router.route(["structured_extraction"])
        # Stage 2 结构化提取 → router 会选最便宜的够用模型
        ...
```

**工作量**: 包含在模型无关架构实现中，约 1 天。

---

## P2-9: 输出形态多样化

### 研究资产
v5-product-feedback.md 第 2 条：输出可以是 skill/报告/体检/对比/缝合地图多种形态。

### 设计方案（不赛马，架构预留）

```python
class OutputForm(Enum):
    SKILL_MD = "skill"  # 核心：注入 AI 的 CLAUDE.md / SKILL.md
    DOMAIN_TRUTH = "domain_truth"  # 衍生：领域真相报告
    HEALTH_CHECK = "health_check"  # 衍生：项目体检报告
    SOUL_DIFF = "soul_diff"  # 衍生：灵魂对比报告
    STITCH_MAP = "stitch_map"  # 衍生：缝合地图

class OutputRouter:
    """根据 need_profile 和管线产出，选择输出形态"""

    def route(self, need_profile: NeedProfile, pipeline_artifacts: dict) -> list[OutputForm]:
        """
        核心输出（SKILL_MD）总是生成。
        衍生输出根据数据可用性自动判断。
        """
        forms = [OutputForm.SKILL_MD]  # 始终包含

        if pipeline_artifacts.get("compare_output"):
            forms.append(OutputForm.SOUL_DIFF)
        if pipeline_artifacts.get("domain_snapshot"):
            forms.append(OutputForm.DOMAIN_TRUTH)
        # ... etc

        return forms
```

**当前优先级**: 低。架构预留接口，v1 只实现 SKILL_MD。
**工作量**: 接口定义 2 小时，每个新形态 1-2 天。

---

## P2-10: 热力图

### 研究资产
- heatmap-research.md：Treemap (项目概览) + Profile Heatmap (WHY 诊断)
- 技术选型：ECharts (首选) / D3.js / Plotly
- 参考产品：CodeScene, Structurizr, SonarQube

### 设计方案（后置，不赛马）

热力图是可视化层，依赖提取层数据完整。在 Stage 0-5 + Knowledge Compiler 稳定后实现。

**数据源**: module-map.md 模块划分 × 卡片知识密度 × Stage 1.5 探索深度

```python
def generate_heatmap_data(module_map: dict, cards: list, exploration_log: list) -> HeatmapData:
    """
    X 轴：模块
    Y 轴：知识类型 (capability/rationale/constraint/interface/failure)
    值：该模块该知识类型的卡片数量 + 探索深度
    """
```

**当前优先级**: 低。P2 后置。
**工作量**: 数据生成 1 天，可视化前端 2-3 天。

---

## P2-11: Homework Evaluation Harness

### 研究资产
good-homework-criteria.md（Codex 最重要输出）：
- 自动生成 10-20 benchmark 问题 → baseline score → assisted score → Lift

### 设计方案

```python
class HomeworkEvaluationHarness:
    """
    评估一个开源项目作为"作业"的价值。

    流程：
    1. 对候选项目自动生成 10-20 个 WHY 层问题
    2. 裸模型回答（baseline）
    3. 注入轻量提取结果后回答（assisted）
    4. Lift = assisted_score - baseline_score
    5. Lift 越高 → 项目作为作业的价值越高
    """

    async def evaluate(self, repo: RepoRef, adapter: LLMAdapter, router: CapabilityRouter) -> EvalResult:
        model = router.route(["deep_reasoning"])

        # 生成 benchmark 问题
        questions = await self._generate_questions(repo, model)

        # Baseline
        baseline_scores = await self._score_answers(questions, model, context=None)

        # Assisted（轻量提取 = Stage 0 + Stage 1 only）
        quick_extract = await self._quick_extract(repo)
        assisted_scores = await self._score_answers(questions, model, context=quick_extract)

        lift = mean(assisted_scores) - mean(baseline_scores)
        return EvalResult(lift=lift, ...)
```

**当前优先级**: 中低。Phase B (discovery) 的质量优化工具。
**工作量**: 约 2-3 天。可赛马。

---

## P2-12: 多轮去重 + GDS 多模型融合

### 研究资产
- why-extraction-conclusions.md：多轮去重 +0.2~0.3 (ROI 4星)，GDS 融合 +0.3~0.5 (ROI 3星)
- Sonnet 和 Gemini 高分 WHY 卡片几乎不重叠 → 融合有价值

### 设计方案

**多轮去重**:
```python
def deduplicate_findings(existing: list[Stage1Finding], new: list[Stage1Finding]) -> list[Stage1Finding]:
    """
    将新一轮提取的 findings 与已有 findings 去重。
    方法：statement 语义相似度 > 0.85 视为重复。
    重复的 finding 不进入后续管线，但更新 confidence（多次出现 → 提高置信度）。
    """
```

**GDS 多模型融合**:
```python
async def gds_fusion(repo: RepoRef, adapter: LLMAdapter, router: CapabilityRouter) -> list[Stage1Finding]:
    """
    Golden Data Set fusion：
    1. 用 2-3 个不同模型各跑一次 Stage 1
    2. 合并 findings（去重 + 互相校验）
    3. 多模型都提取到的 → confidence = high
    4. 只有一个模型提取到的 → confidence = low（但可能是独特洞察）
    """
    models = router.get_all_capable(["deep_reasoning"])

    all_findings = []
    for model in models[:3]:  # 最多 3 个模型
        findings = await run_stage1(repo, model, adapter)
        all_findings.append(findings)

    return merge_and_deduplicate(all_findings)
```

**当前优先级**: 中。Stage 1 质量优化。
**模型无关关键点**: GDS 融合天然需要多模型，与模型无关架构完美契合。

---

## P2-13: Stage 4 可选化 + 中间产物持久化

### 研究资产
- flywheel 文档：Stage 4 从必须变为可选，中间产物（卡片）变为持久化独立对象
- v4 产品定义确认

### 设计方案

**Stage 4 可选化**:
```python
class PipelineConfig(BaseModel):
    skip_stage4: bool = False  # 允许跳过叙事合成
    persist_intermediates: bool = True  # 默认持久化中间产物
```

当 `skip_stage4=True` 时：
- Knowledge Compiler 直接消费卡片，不经过 Stage 4 叙事
- CLAUDE.md 中无 EXPERT KNOWLEDGE 段（只有结构化段）
- 适用于场景：快速提取、Token 敏感环境、非叙事型输出

**中间产物持久化**:
- 当前卡片已经是持久化的（每张卡片一个 .md 文件）
- 需要做的是：让卡片成为**可独立消费**的产物（不仅是 Stage 4 的输入）
- 实现：卡片文件路径暴露在 delivery_bundle 中

```python
class DeliveryBundleManifest(BaseModel):
    # ... existing fields ...
    knowledge_cards_dir: Optional[str] = None  # 暴露卡片目录
```

**当前优先级**: 低。Knowledge Compiler 落地后自然可选化。
**工作量**: 约半天。

---

# 第三部分：赛马日历与执行计划

## Round 6 赛马规划

基于 dev-manual-v5.3 的 4 选手框架（S1-Sonnet, S2-Codex, S3-Gemini, S4-GLM5）：

### 前置工作（PM 完成，不赛马）

| # | 任务 | 工作量 | 产出 |
|---|------|--------|------|
| 0a | 模型无关架构：capability_router.py + llm_adapter.py | 1 天 | packages/shared_utils/ |
| 0b | models.json 默认配置 | 30 分钟 | 项目根目录 |
| 0c | P1 (project_narrative) | 2 小时 | extract_repo_facts.py + contracts |
| 0d | P3 (WHY recoverability) | 30 分钟 | STAGE-1-essence.md |
| 0e | P5 (platform_rules.json) | 2 小时 | 配置文件 + validator.py |
| 0f | P9 (assemble 统一) | 半天 | assemble_output.py |
| 0g | P10 (_gemini 合并) | 1-2 天 | 变体文件合并 |
| 0h | contracts 扩展（verdict, applicable_versions 等新字段） | 半天 | contracts/ |

### Round 6A（2 赛道并行）

| 赛道 | 模块 | 选手 | 预估 |
|------|------|------|------|
| 6A-1 | **Agentic 提取 (P0-1)** | S1-Sonnet vs S3-Gemini | 2-3 天 |
| 6A-2 | **积木制作 (P0-2 赛道A)** | S2-Codex vs S4-GLM5 | 2-3 天 |

### Round 6B（2 赛道并行）

| 赛道 | 模块 | 选手 | 预估 |
|------|------|------|------|
| 6B-1 | **Knowledge Compiler (P0-3)** | S1-Sonnet vs S2-Codex | 1-2 天 |
| 6B-2 | **置信度体系 + 适用域 (P1-4 + P1-5)** | S3-Gemini vs S4-GLM5 | 1-2 天 |

### Round 6C（2 赛道并行）

| 赛道 | 模块 | 选手 | 预估 |
|------|------|------|------|
| 6C-1 | **积木注入 (P0-2 赛道B)** | 最佳选手 from 6A | 1-2 天 |
| 6C-2 | **DSD 实现 (P2)** + **Community signals 结构化 (P7)** | 另外 2 选手 | 1-2 天 |

### Round 6D（整合）

| 任务 | 执行者 | 预估 |
|------|--------|------|
| Phase Runner 真实编排 (P1-6) | 全选手赛马 | 2-3 天 |
| 端到端集成测试 | PM + 最佳选手 | 1 天 |

### 总时间线

```
前置 (PM): 3-4 天
Round 6A:  2-3 天
Round 6B:  1-2 天
Round 6C:  1-2 天
Round 6D:  2-3 天
Buffer:    1-2 天
─────────────────
总计:      ~12-16 天
```

---

# 第四部分：模型无关检查清单

每个赛马 Brief 和 PM 实现必须通过以下检查：

- [ ] 无 `import anthropic` / `import openai` / `import google.generativeai`
- [ ] 所有 LLM 调用通过 `LLMAdapter` 接口
- [ ] Stage 声明能力需求（`deep_reasoning` / `structured_extraction` / `tool_calling`），不声明模型名
- [ ] models.json 中只有一个模型时仍能运行（降级但不 crash）
- [ ] models.json 中有多个模型时，按 `routing_preference` 选择
- [ ] 确定性组件（scripts, validator, assembler, compiler）无 LLM 依赖
- [ ] 测试可在纯 mock 模式下运行（不需要真实 API key）

---

# 附录：研究资产索引

| 研究成果 | 路径 | 落地项 |
|---------|------|--------|
| Agentic extraction synthesis | research/agentic-extraction/synthesis.md | P0-1 |
| Soul lego bricks synthesis | research/soul-lego-bricks/reports/synthesis-report.md | P0-2 |
| Confidence system (Gemini) | research/product-definition-v3/confidence-system-gemini.md | P1-4 |
| Cross-project intelligence | research/cross-project-intelligence/ | P1-6, P4 |
| Dark traps Top 10 | (memory: doramagic-dark-traps.md) | P2, P3 |
| Heatmap research | experiments/exp-why-extraction/heatmap-research-*.md | P2-10 |
| Good homework criteria | (memory: doramagic-good-homework-criteria.md) | P2-11 |
| WHY extraction conclusions | (memory: why-extraction-conclusions.md) | P2-12 |
| Flywheel & partial coverage | (memory: doramagic-flywheel-and-partial-coverage.md) | P2-13 |
| v3 product feedback | (memory: v3-product-feedback.md) | P1, P8 |
| v5 product feedback | (memory: v5-product-feedback.md) | P2-9 |
| 5 challenges | (memory: doramagic-5-challenges.md) | P8, P0-3 |

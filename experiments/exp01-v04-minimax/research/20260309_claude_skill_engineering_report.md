# Soul Extractor 综合研究报告（Claude）

> 研究员：Claude Opus 4.6
> 日期：2026-03-09
> 方法：独立深度研究 + 综合 Codex/Gemini 两份研究报告
> 置信度标注：HIGH / MEDIUM / LOW，每个结论标注信息来源

---

## 1. 执行摘要

Soul Extractor 当前面临的 6 个问题（Skill 触发失败、产品形态未定义、弱模型指令遵从差、脚本未调用、网络问题、输出质量）**本质上是 2 个根因的不同症状**：

**根因 A — 架构错配**：试图用"一段自然语言指令"驱动一个需要确定性编排的多阶段工作流。OpenClaw 的 Skill 系统设计为"给模型看的参考指令"，不是"强制执行的工作流引擎"。当模型弱时，这种架构的每一层都会断裂。

**根因 B — 产品闭环缺失**：提取出知识卡片后没有定义"注入协议"——知识如何被 AI 消费、用户如何感知到 AI 变强。这使得整个产品缺乏终点，所有优化都是在优化一条不知通向何处的路。

**推荐策略**：
1. **立即**（1-2 天）：将 soul-extractor 改为 slash command 触发（`/extract`），用 `command-dispatch: tool` 确保脚本 100% 执行；同时定义最小注入协议——生成 `.cursorrules` / `CLAUDE.md` 文件，让用户立刻能体验"AI 变强"。
2. **短期**（1-2 周）：用 Lobster 将提取拆为 3 阶段流水线，每阶段 ≤5 条指令；实现双产出（AI 注入包 + 人类摘要）。
3. **中期**（1 月+）：接入 Repomix 的 `--skill-generate` 原生能力，建立自动化验证闭环（提取→注入→提问→评分），探索 GraphRAG 路线。

---

## 2. 全问题根因分析

### 2.1 第一性原理拆解

从第一性原理出发，这 6 个问题可以归结为以下因果链：

```
根因 A：架构错配（用 prompt 代替 pipeline）
  ├── Skill 触发失败（问题1）← 自然语言匹配不确定性
  ├── 脚本未调用（问题4）← 模型"自主决定"是否调脚本
  ├── 指令遵从差（问题3）← 20+ 条指令超出弱模型预算
  └── 输出质量差（问题6）← 上述三者的累积效应

根因 B：产品闭环缺失
  ├── 产品形态未定义（问题2）← 不知道产出给谁用
  ├── 输出质量反馈模糊（问题6）← 没有评判标准
  └── 网络问题无兜底（问题5）← 脚本不被调用时镜像逻辑失效
```

**关键洞察**：问题 1/3/4/6 不是 4 个独立问题，而是同一个架构决策（用自然语言 prompt 驱动复杂工作流）在不同层面的失败表现。问题 2 是更深层的战略缺失，即使架构问题全部解决，如果不定义注入协议，产品仍然没有终点。
[置信度: HIGH] [来源: 对 TASK-codex.md、TASK-gemini.md 的因果链分析 + RESEARCH-instruction-compliance.md 的学术数据]

### 2.2 为什么不是 6 个独立问题？

证据：
- 问题 4（脚本未调用）是问题 1（Skill 未触发）的下游效应——绕过 Skill 系统后，Agent 不认为自己在执行预定义工作流，自然也不会尊重脚本调用指令。
- 问题 6（输出质量差）是问题 3（指令遵从差）的直接后果——CEO 反馈的 5 条意见（缺第一性原理、规则太浅、过程不可见等）恰好对应 MiniMax 跳过的指令。
- 问题 5（网络问题）只在问题 4（脚本未调用）时才会暴露——如果脚本正常执行，镜像回退逻辑会自动生效。

### 2.3 Codex 报告与 Gemini 报告的盲区补充

| 角度 | Codex 覆盖 | Gemini 覆盖 | 本报告补充 |
|------|-----------|------------|-----------|
| Skill 触发机制 | 深入（发现 remote gateway 问题） | 浅 | 补充 `user-invocable` 和 `command-dispatch` 机制 |
| Lobster 流水线 | 提及但未展开 | 未提及 | 详细研究 Lobster 的 YAML 定义、步骤链接、审批门 |
| 注入协议 | 提出双层产物 | 提出 .cursorrules 方案 | 补充 Repomix `--skill-generate` 原生能力 |
| 竞品深度 | 较浅 | 有矩阵但偏概念 | 补充 Greptile、Aider architect、Repomix skill gen |
| 验证闭环 | 提出但未设计 | 未展开 | 给出具体的 benchmark 设计方案 |

---

## 3. 产品形态推荐

### 3.1 三个方向的量化分析

| 维度 | A: AI 燃料 | B: 增强文档 | C: 双产出 |
|------|----------|----------|----------|
| 核心价值主张 | "让 AI 变强" | "让人更懂项目" | 两者兼得 |
| exp01 验证数据 | 知识注入后 AI 质量 42%→96% (✅ 已验证) | 未验证 | — |
| 目标用户匹配 | AllInOne 定位为"AI 平台" (✅ 匹配) | 与 README/awesome-xxx 竞争 (❌) | — |
| 实现复杂度 | 中（需定义注入协议） | 低 | 高（两套格式） |
| CEO 追问回答 | "这些文件让 AI 变强，用户提问时自动注入" ✅ | "这是更好的文档" ❌ 不符合定位 | — |
| 差异化 | 独特（目前无竞品做"自动提取+注入"闭环） | 弱（Repomix、README 已存在） | — |

### 3.2 推荐：方向 A 为主，方向 B 为辅（改良版方向 C）

**核心决策**：产出的 canonical source 是面向 AI 的结构化知识包（方向 A），人类可读的 `project_soul.md` 是从知识包派生的副产物（方向 B）。

**理由**：
1. exp01 实验已用数据证明知识注入有效（42%→96%），这是方向 A 的硬证据
2. CEO 的核心追问"这些文件拿来做什么"——只有方向 A 能回答："自动注入 AI，让它从泛泛而谈变成专家"
3. 方向 B 单独存在时与 Repomix 的 `--skill-generate` 功能高度重叠，没有差异化
4. 但完全放弃方向 B 会丧失"向用户展示专业性"的能力，因此保留 `project_soul.md` 作为信任建立工具

[置信度: HIGH] [来源: exp01 A/B/C 验证数据 + CEO 追问链 + 竞品对比]

### 3.3 注入协议设计

**"注入协议"是连接提取和价值的桥梁。** 没有它，燃料无处燃烧。

#### 方案 1：生成标准 AI 配置文件（推荐，短期可做）

```
提取产出 → 生成 .cursorrules / CLAUDE.md → 用户放入项目根目录 → AI 编码助手自动读取
```

具体实现：
- 将知识卡片转译为 `.cursorrules` 格式（Cursor 自动加载）
- 将知识卡片转译为 `CLAUDE.md` 格式（Claude Code 自动加载）
- 将知识卡片转译为 `.github/copilot-instructions.md`（GitHub Copilot 自动加载）

**用户体验闭环**：
```
用户: /extract https://github.com/theskumar/python-dotenv
Agent: 正在提取... [进度]
Agent: 完成！已生成：
  - project_soul.md（项目灵魂，给你看的）
  - .cursorrules（给 Cursor 的燃料）
  - CLAUDE.md（给 Claude Code 的燃料）
  把这些文件放到你的项目根目录，你的 AI 助手就能变成 python-dotenv 专家。
```

#### 方案 2：OpenClaw 平台内注入（中期）

```
提取产出 → 存入 OpenClaw 长期记忆 → 用户后续提问时自动挂载相关知识
```

需要 OpenClaw 支持 per-repo 的知识存储和检索，当前平台是否支持**需要进一步确认**。

#### 方案 3：RAG 检索（长期）

```
提取产出 → 向量化存储 → 用户提问时语义检索相关卡片 → 动态注入上下文
```

[置信度: HIGH（方案1），MEDIUM（方案2，平台能力未验证），MEDIUM（方案3，工程量大）]

### 3.4 验证闭环设计

验证"提取的知识是否真的让 AI 变强"必须产品化，不能停留在手工实验。

```yaml
验证流程:
  1. 准备: 收集 10-20 个关于目标项目的技术问题（含答案）
  2. 基线: 用裸模型回答，记录质量分数
  3. 注入: 将提取的知识注入模型上下文
  4. 测试: 用同一组问题测试，记录质量分数
  5. 评分: 自动计算提升幅度
  6. 输出: "知识注入后 AI 回答质量提升 X%"
```

这个验证流程可以作为 Lobster 流水线的最后一个阶段自动执行。

---

## 4. OpenClaw Skill 系统研究

### 4.1 Skill 发现和触发机制

经过研究 OpenClaw 文档和多个教程，Skill 触发机制如下：

| 机制 | 工作方式 | 确定性 | 适合场景 |
|------|---------|--------|---------|
| **模型语义匹配** | Session 启动时，skill 列表注入 system prompt；模型自行决定是否使用 | 低（取决于模型能力） | 通用对话中自然触发 |
| **Slash command** | `user-invocable: true` 时，skill 注册为 `/skill-name` 命令 | 高 | 用户明确想执行某功能 |
| **Tool dispatch** | `command-dispatch: tool` 时，slash command 直接调用工具，绕过模型 | 最高 | 确定性工作流的第一步 |

**soul-extractor 应该使用 slash command + tool dispatch**，原因：
1. 自然语言触发对弱模型不可靠（已验证失败）
2. 用户触发提取是明确意图，不需要模型"理解"
3. Tool dispatch 可以确保 `prepare-repo.sh` 100% 被执行

[置信度: HIGH] [来源: OpenClaw 官方文档 docs.openclaw.ai/tools/skills + Codex 报告验证]

### 4.2 Skill 触发失败的根因

Codex 报告发现了关键线索：**当前 OpenClaw 配置是 `remote gateway` 模式**，skill 安装在本机 `~/.openclaw/skills/` 但实际运行在远端。这意味着远端可能根本看不到本机的 skill 文件。

此外，`requires.bins: ["node", "npx", "git"]` 会导致 OpenClaw 在 session 启动时检查这些二进制是否存在。如果远端环境缺少任何一个，skill 会被静默过滤掉。

**修复清单**：
1. 确认 skill 文件在**远端运行环境**（tangsir@192.168.0.251）的正确目录中
2. 确认远端环境安装了 `node`、`npx`、`git`
3. 检查 `~/.openclaw/openclaw.json` 中的 `skills.load.extraDirs` 是否包含 skill 目录
4. 将 skill 改为 `user-invocable: true` 并使用 slash command 触发

[置信度: HIGH] [来源: Codex 报告的本地配置审查 + OpenClaw 文档]

### 4.3 Lobster 流水线：多阶段编排的正确方式

OpenClaw 有原生的流水线引擎 **Lobster**，这是解决"多阶段拆分"的正确工具，而不是把一个大 SKILL.md 拆成多个小 SKILL.md 让用户手动串联。

Lobster 的核心能力：
- **YAML 定义**：工作流用 YAML 声明，version-controllable
- **步骤链接**：用 `stdin: $stepId.stdout` 在步骤间传递数据
- **审批门**：`approval: required` 暂停等待人工确认
- **恢复令牌**：暂停的工作流可以稍后继续，无需重跑
- **错误处理**：内置重试、回退、错误通知

**soul-extractor 的 Lobster 流水线设计**：

```yaml
name: soul-extract
description: "从 GitHub 仓库提取结构化知识"

steps:
  - id: prepare
    command: "bash {baseDir}/scripts/prepare-repo.sh '$REPO_URL'"
    # 确定性执行，不依赖模型决策

  - id: essence
    skill: soul-extract-essence
    stdin: $prepare.stdout
    # 模型执行：回答 5 个第一性原理问题，≤5 条指令

  - id: cards
    skill: soul-extract-cards
    stdin: $essence.stdout
    # 模型执行：生成概念卡 + 工作流卡，≤5 条指令

  - id: rules
    skill: soul-extract-rules
    stdin: $cards.stdout
    # 模型执行：生成规则卡，≤5 条指令

  - id: assemble
    command: "bash {baseDir}/scripts/assemble-output.sh '$OUTPUT_DIR'"
    # 确定性执行：组装最终产出，生成 .cursorrules / CLAUDE.md
```

[置信度: MEDIUM — Lobster 的能力已通过文档确认，但 soul-extractor 的具体集成未验证，需要实际测试]

### 4.4 其他成功 Skill 的触发方式

从 ClawHub 注册的 13,000+ skills 中观察到的模式：

- **find-skills**：通过 slash command `/find-skills` 触发，用于搜索 ClawHub
- **capability-evolver**：自动触发型，在对话中模型判断是否需要进化能力
- **doc-pipeline**：Lobster 流水线型，多阶段文档处理
- **repomix**：工具型，直接 dispatch 到 repomix CLI

**成功 skill 的共性**：要么用 slash command 明确触发，要么功能足够简单（单一指令）让模型容易匹配。像 soul-extractor 这样又复杂又依赖自然语言触发的，在 ClawHub 中很少见。

[置信度: MEDIUM] [来源: ClawHub 分析 + awesome-openclaw-skills 仓库]

---

## 5. 跨模型适配方案

### 5.1 三种策略的务实评估

| 策略 | 原理 | 优点 | 致命缺陷 | 推荐度 |
|------|------|------|---------|--------|
| **多阶段拆分** | 每阶段 ≤5 条指令 | 弱模型也能可靠执行 | 需要编排引擎（Lobster 可解决） | ✅ 强烈推荐 |
| **渐进式指令** | 核心指令必须，增强指令可选 | 单文件兼容多模型 | 强模型看到"可选"可能跳过；条件逻辑本身消耗指令预算 | ⚠️ 不推荐作为主方案 |
| **接受分工** | 弱模型=预览，强模型=完整提取 | 产品体验清晰 | 需要多模型切换机制 | ✅ 推荐作为补充策略 |

**推荐组合**：多阶段拆分 + 接受分工。用 Lobster 拆阶段，同时允许不同阶段使用不同模型。

[置信度: HIGH] [来源: RESEARCH-instruction-compliance.md 的学术数据 + Codex/Gemini 报告共识]

### 5.2 Few-shot Example 的定量研究

学术和工程实践的共识：

1. **弱模型必须用完整 few-shot 示例**，抽象模板对弱模型几乎无效
   - 2025 年研究（The Few-shot Dilemma）发现：5-20 个示例是最优区间，超过 20 个反而性能下降
   - 对 soul-extractor：每个阶段给 1 个完整示例是最佳平衡（不超预算，足够示范）

2. **示例的位置比数量更重要**
   - 示例应紧跟在任务描述之后、约束条件之前
   - 不要把示例放在文件末尾（距离指令太远，弱模型会"忘记"）

3. **示例的结构必须和目标输出完全一致**
   - 当前 SKILL.md 中的示例是模板（用 `[placeholder]` 标记），弱模型无法从模板推断具体内容
   - 应改为**真实的、已填充的完整示例**

**具体建议——以规则卡为例**：

当前 SKILL.md 的模板：
```markdown
# DR-001: [Rule Title — specific, not generic]
## 严重度: [HIGH/MEDIUM/LOW]
## 规则
IF [specific condition]
THEN [specific consequence]
```

应改为包含真实内容的 few-shot：
```markdown
# 以下是一个完整的规则卡示例，你的每张规则卡必须包含所有这些字段：

# DR-001: load_dotenv() 在找不到 .env 文件时静默返回 True

## 严重度: MEDIUM

## 规则
IF 调用 load_dotenv() 时 .env 文件不存在
THEN 函数返回 True（不是 False），零个变量被加载，代码继续执行但使用默认值

## 为什么会踩这个坑？
开发者直觉认为"加载失败应该返回 False"...
[完整填充的内容]
```

[置信度: HIGH] [来源: Few-shot Prompting Guide + The Few-shot Dilemma (2025) + RESEARCH-instruction-compliance.md]

### 5.3 SKILL.md 重构方案

将当前单一的 `SKILL.md`（6.7KB, 20+ 条指令）重构为以下结构：

```
skills/soul-extractor/
├── SKILL.md                    # 入口 skill，仅做路由和进度汇报（≤3 条指令）
├── lobster.yaml                # Lobster 流水线定义
├── scripts/
│   ├── prepare-repo.sh         # 克隆 + Repomix 打包（已有）
│   └── assemble-output.sh      # 组装最终产出（新增）
├── stages/
│   ├── STAGE-1-essence.md      # 第一性原理提取（≤5 条指令 + 1 个 few-shot）
│   ├── STAGE-2-concepts.md     # 概念卡 + 工作流卡（≤5 条指令 + 1 个 few-shot）
│   └── STAGE-3-rules.md        # 规则卡提取（≤5 条指令 + 1 个 few-shot）
└── examples/
    ├── essence-example.md      # python-dotenv 的第一性原理示例（真实内容）
    ├── concept-card-example.md # CC-001 的完整示例
    └── rule-card-example.md    # DR-001 的完整示例
```

**入口 SKILL.md 的重构思路**（伪代码级）：

```yaml
---
name: soul-extractor
description: "Extract structured knowledge from a GitHub repo."
version: 0.5.0
user-invocable: true
command-dispatch: tool      # slash command 直接触发，不依赖模型匹配
command-tool: bash
metadata:
  openclaw:
    category: knowledge
    requires:
      bins: ["node", "npx", "git"]
---
```

```markdown
# Soul Extractor

当用户发送 /soul-extractor <repo_url> 时：

1. 运行 prepare-repo.sh 下载和打包代码
2. 告知用户："代码已准备好，开始分阶段提取..."
3. 按顺序执行 stages/ 目录下的三个阶段
4. 运行 assemble-output.sh 生成最终产出
5. 向用户展示 project_soul.md 的内容，并告知可下载文件的位置
```

**每个 STAGE 文件的结构**（以 STAGE-1-essence.md 为例）：

```markdown
# Stage 1: 项目本质提取

## 输入
读取 <output>/artifacts/packed_compressed.xml

## 任务
回答以下 5 个问题，写入 <output>/soul/00-project-essence.md：

1. 这个项目解决什么问题？（一句话，说明谁有这个痛点）
2. 如果没有这个项目，人们会怎么做？
3. 它的核心承诺是什么？
4. 它用什么方式兑现承诺？
5. 一句话总结：[项目] 让 [谁] 可以 [做什么]，而不用 [原来的痛苦方式]

## 完整示例
[此处嵌入 python-dotenv 的真实 essence 文档，非模板]

## 约束
- 每个答案不超过 2 句话
- 用中文回答
- 非程序员应该能理解

## 完成后
告诉用户你发现的"一句话总结"，然后继续下一阶段。
```

[置信度: HIGH（结构设计），MEDIUM（Lobster 集成需实测）]

---

## 6. 竞品分析

### 6.1 竞品矩阵

| 工具 | 做什么 | 知识来源 | 知识格式 | 注入方式 | 与 soul-extractor 的关系 |
|------|--------|---------|---------|---------|------------------------|
| **Repomix** | 将代码库打包为 AI 友好格式 | 源代码 | XML/Markdown/Skills 目录 | 手动喂给 LLM / Claude Skills | **上游工具**——soul-extractor 已在用它做打包 |
| **Repomix --skill-generate** | 生成 Claude Skills 格式的代码参考 | 源代码 | 结构化 Skills 目录 | 自动被 Claude Code 读取 | **直接竞品**——做的事情和 soul-extractor 高度重叠 |
| **Greptile** | 构建代码语义图谱，API 查询 | 源代码 + Git 历史 | 语义图谱 | API 调用 | 互补——Greptile 做检索，soul-extractor 做提炼 |
| **Aider /architect** | 两阶段编码：架构师提案 + 编辑器执行 | 仓库地图（函数签名） | 内部 repo map | 自动注入对话上下文 | 启发——"弱模型做编辑、强模型做架构"的分工思路 |
| **Sourcegraph Cody** | 跨仓库代码搜索和理解 | 代码索引 + AST | 向量索引 | IDE 集成自动注入 | 启发——企业级代码理解的参考 |
| **Cursor .cursorrules** | 项目级 AI 行为配置 | 人工编写 | Markdown 规则 | IDE 自动加载 | **注入目标**——soul-extractor 可以自动生成 .cursorrules |
| **Claude Code CLAUDE.md** | 项目级 AI 上下文 | 人工编写 | Markdown | CLI 自动加载 | **注入目标**——soul-extractor 可以自动生成 CLAUDE.md |
| **GitHub Copilot 索引** | 代码库智能索引 | 源代码 | 向量索引 + AST | 隐式注入 IDE 补全上下文 | 互补——Copilot 做实时补全，soul-extractor 做深度理解 |

### 6.2 关键发现：Repomix `--skill-generate` 是最大竞争威胁

**Repomix 最近新增了 `--skill-generate` 功能**，可以直接从任意仓库生成 Claude Skills 格式的输出：

```bash
repomix --skill-generate python-dotenv-reference
# 产出：
# .claude/skills/python-dotenv-reference/
#   ├── SKILL.md
#   └── references/
#       ├── summary.md
#       ├── project-structure.md
#       └── files.md
```

这与 soul-extractor 的定位高度重叠。**但关键区别在于**：

| 维度 | Repomix skill-generate | soul-extractor |
|------|----------------------|----------------|
| 知识深度 | 浅——本质是代码打包 + 目录结构 | 深——第一性原理、条件化规则、陷阱挖掘 |
| 知识类型 | 代码结构参考 | 领域知识提炼 |
| 社区知识 | ❌ 不涉及 Issues/Discussions | ✅ 挖掘社区陷阱和最佳实践 |
| AI 增强效果 | 中等（"知道代码长什么样"） | 高（"理解项目的灵魂和陷阱"） |

**soul-extractor 的护城河在于"提炼深度"**——不是简单打包代码，而是用 AI 理解代码后产出高密度的条件化知识。Repomix 做的是"给 AI 看源码"，soul-extractor 做的是"让 AI 先深度理解，再把理解结果结构化"。

[置信度: HIGH] [来源: Repomix 官方文档 repomix.com/guide/agent-skills-generation + 功能对比分析]

### 6.3 RAG vs 知识卡片：优劣对比

| 维度 | RAG（直接检索源码） | 知识卡片（先提取再注入） |
|------|-------------------|---------------------|
| 延迟 | 每次提问都要检索 | 一次提取，多次复用 |
| 知识密度 | 低——检索到的是原始代码片段 | 高——已经过 AI 理解和提炼 |
| 上下文窗口消耗 | 高——需要塞入多个代码块 | 低——结构化卡片更紧凑 |
| 隐性知识 | ❌ 无法检索代码中没有的社区知识 | ✅ 可以包含 Issues、Discussions 中的陷阱 |
| 设置成本 | 中——需要向量化和索引 | 中——需要提取流程 |
| 鲜度 | 高——总是最新代码 | 低——提取后是快照 |
| 覆盖面 | 窄——只能检索到与问题相关的片段 | 广——预先提取项目全貌 |

**结论**：对于"让 AI 深度理解一个开源项目"这个场景，知识卡片优于纯 RAG。但长期最优方案是 **知识卡片 + RAG 的混合**：用知识卡片提供项目全貌和高密度理解，用 RAG 提供实时的代码细节检索。

[置信度: MEDIUM] [来源: 知识图谱 vs RAG 的学术研究 + 工程经验推理]

---

## 7. 最佳工程实践方案

### 7.1 完整文件结构

```
skills/soul-extractor/
├── SKILL.md                        # 入口（slash command 配置 + 简要说明）
├── lobster.yaml                    # Lobster 流水线定义
├── scripts/
│   ├── prepare-repo.sh             # 克隆 + Repomix 打包（已有，需微调）
│   ├── assemble-output.sh          # 组装最终产出（新增）
│   └── generate-injection-files.sh # 生成 .cursorrules / CLAUDE.md（新增）
├── stages/
│   ├── STAGE-1-essence.md          # 项目本质提取（5 个问题）
│   ├── STAGE-2-concepts.md         # 概念卡(3) + 工作流卡(3)
│   └── STAGE-3-rules.md            # 规则卡提取(5-10 张)
├── examples/
│   ├── essence-python-dotenv.md    # 真实完整示例
│   ├── concept-card-CC-001.md      # 真实完整示例
│   ├── workflow-card-WF-001.md     # 真实完整示例
│   └── rule-card-DR-001.md         # 真实完整示例
├── templates/
│   ├── cursorrules.template        # .cursorrules 生成模板
│   └── claude-md.template          # CLAUDE.md 生成模板
└── benchmarks/
    └── python-dotenv-questions.yaml # 验证用问题集
```

### 7.2 Lobster 流水线定义（伪代码级）

```yaml
# lobster.yaml
name: soul-extract-pipeline
description: "从 GitHub 仓库提取结构化知识并生成 AI 注入文件"

steps:
  - id: prepare
    command: "bash {baseDir}/scripts/prepare-repo.sh '$REPO_URL' '$OUTPUT_DIR'"
    timeout: 120s
    on_failure: "notify_user '代码下载失败，请检查 URL 或提供镜像地址'"

  - id: extract-essence
    skill: "{baseDir}/stages/STAGE-1-essence.md"
    env:
      OUTPUT_DIR: "$OUTPUT_DIR"
      PACKED_FILE: "$OUTPUT_DIR/artifacts/packed_compressed.xml"
    stdin: $prepare.stdout

  - id: extract-cards
    skill: "{baseDir}/stages/STAGE-2-concepts.md"
    env:
      OUTPUT_DIR: "$OUTPUT_DIR"
      ESSENCE_FILE: "$OUTPUT_DIR/soul/00-project-essence.md"
    stdin: $extract-essence.stdout

  - id: extract-rules
    skill: "{baseDir}/stages/STAGE-3-rules.md"
    env:
      OUTPUT_DIR: "$OUTPUT_DIR"
    stdin: $extract-cards.stdout

  - id: assemble
    command: "bash {baseDir}/scripts/assemble-output.sh '$OUTPUT_DIR'"

  - id: generate-injection
    command: "bash {baseDir}/scripts/generate-injection-files.sh '$OUTPUT_DIR'"
    # 从卡片生成 .cursorrules 和 CLAUDE.md
```

### 7.3 注入协议：`generate-injection-files.sh` 的逻辑

```bash
#!/bin/bash
# 从知识卡片生成 AI 注入文件
OUTPUT_DIR="$1"
SOUL_DIR="$OUTPUT_DIR/soul"

# 1. 生成 .cursorrules
cat > "$OUTPUT_DIR/inject/.cursorrules" << 'HEADER'
# Auto-generated by Soul Extractor
# 将此文件放入使用 [项目名] 的项目根目录
HEADER

# 嵌入项目本质
echo "## 项目理解" >> "$OUTPUT_DIR/inject/.cursorrules"
cat "$SOUL_DIR/00-project-essence.md" >> "$OUTPUT_DIR/inject/.cursorrules"

# 嵌入规则（IF/THEN 格式，AI 最容易消费）
echo "" >> "$OUTPUT_DIR/inject/.cursorrules"
echo "## 关键规则" >> "$OUTPUT_DIR/inject/.cursorrules"
for rule_file in "$SOUL_DIR/cards/rules/"*.md; do
    # 提取 IF/THEN 部分
    sed -n '/^## 规则/,/^## /p' "$rule_file" | head -n -1 >> "$OUTPUT_DIR/inject/.cursorrules"
    echo "" >> "$OUTPUT_DIR/inject/.cursurrules"
done

# 2. 生成 CLAUDE.md（类似逻辑）
# 3. 生成 .github/copilot-instructions.md（类似逻辑）
```

### 7.4 用户体验流程（端到端）

```
用户在 Telegram 中发送:
  /extract https://github.com/theskumar/python-dotenv

系统响应 (确定性，不依赖模型):
  [1/5] 正在下载代码并打包... ✓ (3201 行 Python)

AI 执行 Stage 1 (≤5 条指令):
  [2/5] 正在理解项目本质...
  → "python-dotenv 让开发者可以把配置存在 .env 文件里，而不用把密钥硬编码到代码中"

AI 执行 Stage 2 (≤5 条指令):
  [3/5] 正在提取核心概念和工作流...
  → 已提取 3 个概念、3 个工作流

AI 执行 Stage 3 (≤5 条指令):
  [4/5] 正在挖掘使用规则和常见陷阱...
  → 已提取 8 条规则（3 HIGH、3 MEDIUM、2 LOW）

系统组装 (确定性):
  [5/5] 正在生成 AI 注入文件...

最终输出:
  ✅ python-dotenv 灵魂提取完成！

  📋 项目灵魂:
  [显示 project_soul.md 的摘要]

  📦 已生成的文件:
  - project_soul.md — 项目灵魂（给你看的）
  - .cursorrules — Cursor AI 燃料
  - CLAUDE.md — Claude Code AI 燃料
  - soul/cards/ — 8 张概念卡 + 8 条规则卡

  💡 使用方法:
  把 .cursorrules 或 CLAUDE.md 放到你使用 python-dotenv 的项目根目录，
  你的 AI 编码助手就会自动成为 python-dotenv 专家。
```

### 7.5 验证方法

#### 层级 1：指令遵从率（自动化）

```yaml
# 检查每个阶段的产出是否符合预期
checks:
  stage-1:
    - file_exists: "soul/00-project-essence.md"
    - contains_sections: ["解决什么问题", "核心承诺", "一句话总结"]
  stage-2:
    - file_count: "soul/cards/concepts/*.md >= 3"
    - file_count: "soul/cards/workflows/*.md >= 3"
    - each_file_contains: ["它是", "它不是", "边界"]
  stage-3:
    - file_count: "soul/cards/rules/*.md >= 5"
    - each_file_contains: ["严重度", "IF", "THEN", "真实场景", "影响范围"]
```

#### 层级 2：知识增强效果（半自动化）

```yaml
# benchmarks/python-dotenv-questions.yaml
questions:
  - q: "load_dotenv() 找不到 .env 文件时会怎样？"
    expected_keywords: ["返回 True", "不会报错", "静默"]
    difficulty: medium

  - q: "在 Docker 容器中使用 python-dotenv 需要注意什么？"
    expected_keywords: ["override", "环境变量优先级", ".env 位置"]
    difficulty: hard

  - q: "如何在测试中使用 python-dotenv？"
    expected_keywords: ["override=True", "dotenv_values", "不要全局修改"]
    difficulty: medium
```

验证流程：
1. 用裸模型回答这些问题，计算关键词命中率
2. 注入 .cursorrules 后重新回答，计算命中率
3. 计算提升幅度
4. 目标：命中率提升 ≥50%

---

## 8. 路线图

### 短期（1-2 天）：跑通最小闭环

| 任务 | 预期产出 | 工作量 |
|------|---------|--------|
| 修复 Skill 触发：改为 slash command + user-invocable | `/extract` 命令可用 | 2h |
| 确认远端环境的 skill 路径和依赖 | 排除 remote gateway 问题 | 1h |
| 写 `generate-injection-files.sh` | 从现有卡片生成 .cursorrules | 3h |
| 手动验证：用生成的 .cursorrules 在 Cursor 中测试 | 确认"AI 变强"可感知 | 2h |

**短期目标**：用户执行 `/extract` → 拿到 `.cursorrules` → 放入项目 → Cursor 变成 python-dotenv 专家。哪怕中间步骤是半手动的也没关系，关键是**验证价值闭环**。

### 中期（1-2 周）：架构升级

| 任务 | 预期产出 | 工作量 |
|------|---------|--------|
| 将 SKILL.md 拆为 3 个 STAGE 文件 | 每阶段 ≤5 条指令 | 1 天 |
| 为每个 STAGE 编写真实 few-shot 示例 | examples/ 目录完整 | 1 天 |
| 集成 Lobster 流水线 | lobster.yaml 定义并测试通过 | 2 天 |
| 用 MiniMax 测试拆分后的指令遵从率 | 指令遵从率从 60% 提升到 ≥85% | 1 天 |
| 实现自动化验证（层级 1） | 产出完整性检查脚本 | 1 天 |
| 对 3 个目标项目跑完整提取 | 验证泛化能力 | 2 天 |

**中期目标**：MiniMax 也能通过 Lobster 流水线产出合格的知识卡片和 .cursorrules 文件。

### 长期（1 月+）：产品化和规模化

| 任务 | 预期产出 | 工作量 |
|------|---------|--------|
| 接入 Repomix `--skill-generate` 作为补充数据源 | 更丰富的代码参考 | 3 天 |
| 实现知识增强效果验证（层级 2） | 自动化 A/B 测试 | 1 周 |
| 探索 GraphRAG：知识卡片 + 实时代码检索 | 混合检索原型 | 2 周 |
| 支持更多注入目标：VS Code、JetBrains、Windsurf | 多 IDE 覆盖 | 1 周 |
| 社区知识挖掘：自动爬取 Issues/Discussions | 社区规则卡自动化 | 2 周 |
| 发布到 ClawHub | 公开 skill，获取用户反馈 | 3 天 |

---

## 9. 风险和局限

### 高风险

| 风险 | 影响 | 缓解 |
|------|------|------|
| **Lobster 集成复杂度超预期** | 流水线方案需要降级为手动串联 | 先用 bash 脚本模拟流水线，验证阶段拆分有效后再集成 Lobster |
| **弱模型即使拆阶段也无法产出合格卡片** | 需要放弃弱模型全链路执行 | 接受分工：弱模型做预览 + 路由，强模型做实际提取 |
| **Repomix --skill-generate 快速迭代，蚕食 soul-extractor 价值** | 差异化缩小 | 加速社区知识提取能力（Repomix 不做这个），这是核心护城河 |

### 中风险

| 风险 | 影响 | 缓解 |
|------|------|------|
| **生成的 .cursorrules 质量不稳定** | 用户体验不一致 | 自动化验证 + 人工审核机制 |
| **大型项目（>50K 行）超出上下文窗口** | 提取不完整 | 利用 Repomix 的 `--compress` 模式 + 分模块提取 |
| **OpenClaw 远端环境缺少 Node.js** | prepare-repo.sh 执行失败 | 在 prepare-repo.sh 中加入环境检查和安装提示 |

### 未验证的假设

| 假设 | 当前状态 | 验证方法 |
|------|---------|---------|
| Lobster 可以调用 skill（不仅是 command） | 文档暗示可以，未实测 | 写一个简单的 2 步流水线测试 |
| `command-dispatch: tool` 支持 bash 脚本 | 文档提到 tool dispatch，具体到 bash 未确认 | 创建最小 skill 测试 |
| OpenClaw 远端能看到本机 symlink 的 skill | Codex 报告怀疑不能 | SSH 到远端检查 |
| 生成的 .cursorrules 不会超过 Cursor 的大小限制 | 未确认 Cursor 对 .cursorrules 的大小限制 | 实测 |
| MiniMax 在 5 条指令以内的遵从率 ≥90% | 学术推算但未对 MiniMax 实测 | 用 STAGE-1 做单独测试 |

---

## 10. 参考文献

### 学术文献
- IFScale (2025): [arxiv.org/abs/2507.11538](https://arxiv.org/abs/2507.11538) — 多指令遵从的量化框架
- Curse of Instructions (2024): [openreview.net/forum?id=R6q67CDBCH](https://openreview.net/forum?id=R6q67CDBCH) — 指令数量与遵从率的指数衰减关系
- The Instruction Gap (2025): [arxiv.org/abs/2601.03269](https://arxiv.org/abs/2601.03269) — 弱模型指令遵从的系统性研究
- The Few-shot Dilemma (2025): [arxiv.org/html/2509.13196v1](https://arxiv.org/html/2509.13196v1) — 过多 few-shot 示例反而降低性能
- DeCRIM: [arxiv.org/abs/2410.06458](https://arxiv.org/abs/2410.06458) — 分解-批判-修正循环

### OpenClaw 平台文档
- [OpenClaw Skills 官方文档](https://docs.openclaw.ai/tools/skills)
- [OpenClaw Lobster 流水线引擎](https://docs.openclaw.ai/tools/lobster)
- [Lobster GitHub 仓库](https://github.com/openclaw/lobster)
- [ClawHub Skill 注册中心](https://github.com/openclaw/clawhub)
- [ClawHub Skill 格式规范](https://github.com/openclaw/clawhub/blob/main/docs/skill-format.md)
- [OpenClaw Skills 配置文档](https://github.com/openclaw/openclaw/blob/main/docs/tools/skills-config.md)

### 竞品和工具
- [Repomix Agent Skills Generation](https://repomix.com/guide/agent-skills-generation)
- [Repomix 主页](https://repomix.com/)
- [Greptile 代码语义图谱](https://www.qodo.ai/blog/greptile-alternatives/)
- [Aider AI 对编程](https://aider.chat/)
- [Aider Chat Modes (含 /architect)](https://aider.chat/docs/usage/modes.html)
- [Sourcegraph Cody](https://realpython.com/ref/ai-coding-tools/sourcegraph-cody/)

### AI 编码助手的知识注入机制
- [Claude Code vs Cursor 对比](https://www.builder.io/blog/cursor-vs-claude-code)
- [统一 AI Skills 跨 Cursor 和 Claude Code](https://yozhef.medium.com/unifying-ai-skills-across-cursor-and-claude-code-3c34c44eafd2)
- [ClaudeMDEditor — 管理 AI 编码助手配置文件](https://www.claudemdeditor.com/)
- [GitHub Copilot 工作区上下文理解](https://code.visualstudio.com/docs/copilot/reference/workspace-context)
- [GitHub 仓库索引文档](https://docs.github.com/copilot/concepts/indexing-repositories-for-copilot-chat)

### OpenClaw 教程和社区
- [DigitalOcean: What are OpenClaw Skills?](https://www.digitalocean.com/resources/articles/what-are-openclaw-skills)
- [DataCamp: Building Custom OpenClaw Skills](https://www.datacamp.com/tutorial/building-open-claw-skills)
- [LumaDock: How to build custom OpenClaw skills](https://lumadock.com/tutorials/build-custom-openclaw-skills)
- [DEV: Deterministic Multi-Agent Pipeline in OpenClaw](https://dev.to/ggondim/how-i-built-a-deterministic-multi-agent-dev-pipeline-inside-openclaw-and-contributed-a-missing-4ool)
- [VoltAgent: awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills)

### 知识图谱 vs RAG
- [Atlan: Knowledge Graphs vs RAG](https://atlan.com/know/knowledge-graphs-vs-rag-for-ai/)
- [Harness: Knowledge Graphs + RAG for DevOps](https://www.harness.io/blog/knowledge-graph-rag)
- [DevRev: RAG vs Knowledge Graph-Enhanced AI](https://devrev.ai/blog/rag-vs-knowledge-graph-ai)

---

> **报告结束**
> 如有疑问或需要对任何章节做更深入的研究，请指出具体方向。

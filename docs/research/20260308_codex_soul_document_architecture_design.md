# AllInOne 灵魂文档双层结构设计报告

**日期**: 2026-03-08  
**角色**: AllInOne 系统架构师  
**性质**: v1 可落地规范优先，长期演进蓝图作为附录  
**目标文件**: `/Users/tangsir/Documents/openclaw/allinone/docs/research/20260308_codex_soul_document_architecture_design.md`

---

# 一、执行摘要

## 1.1 结论先行

AllInOne 的“灵魂文档”不应设计成两个大文件，而应设计成一个 **双层知识系统**：

- **全局灵魂（AllInOne Soul）**：定义 AllInOne 自己如何提取知识、如何验证质量、如何为用户服务、如何装配上下文。
- **项目灵魂（Project Soul）**：定义每个开源项目的结构知识、核心概念、约束、工作流、社区经验与踩坑记录。

最佳工程实践不是“父子 Markdown 继承”，而是：

- **全局灵魂 = control plane（治理层）**
- **项目灵魂 = knowledge plane（知识层）**
- **runtime assembler = execution plane（执行层）**

也就是说：

- 全局灵魂不直接替代项目知识，而是**治理项目知识如何生产、如何装配、如何被 LLM 消费**。
- 项目灵魂不直接等于 README 或源码摘要，而是**面向用户服务的项目最小充分知识体**。
- 运行时 context 不应是固定 prompt，而应是**按任务类型、token 预算、风险级别、命中模块动态组装**。

## 1.2 推荐方案

本报告推荐采用：

> **“主索引 + 卡片化主数据 + 运行时动态编排”的双层灵魂架构**

即：

- 全局层采用一组小而稳定的 Markdown 规范文件；
- 项目层采用 `project_soul.md + C1 知识卡片体系 + 证据/演化层`；
- 运行时通过 profile 和装配规则，按场景为 LLM 构建最小充分 context。

## 1.3 为什么不是单文件方案

虽然 `CLAUDE.md` 证明了 Markdown-first 的有效性，但 AllInOne 的问题比 Claude Code 更复杂：

- 需要同时支持平台级规范和项目级知识；
- 需要支持多项目、多版本、多来源证据；
- 需要支持卡片增量演化、质量验证和经验晋升；
- 需要长期维护而不演化成 prompt 垃圾堆。

因此，最佳实践不是“多层 Markdown 文件简单叠加”，而是：

- **Markdown 作为知识主数据**
- **Schema 作为结构约束**
- **Runtime 作为动态装配器**

## 1.4 v1 设计目标

v1 不追求图数据库或复杂知识图谱，而追求以下四点：

1. **对 LLM 友好**：Markdown-first，短段落，小卡片，显式规则。
2. **对人可维护**：目录清晰、diff 友好、版本可追踪。
3. **对系统可编排**：可做 lint、可做动态加载、可做 token 裁剪。
4. **对质量可验证**：能通过 A/B 评估验证“有灵魂”是否优于“无灵魂”。

---

# 二、设计必须遵守的工程原则

这部分不是抽象理念，而是整个架构的硬约束。后续所有文件结构、版本机制和 runtime 策略都以此为准。

## 2.1 Single Source of Truth

- 不允许同一知识在多个地方以不同说法重复维护。
- **项目灵魂** 是项目知识的一等主数据。
- **全局灵魂** 只定义平台级方法论、装配规则、质量标准、用户服务协议。
- 项目经验如果要上升为平台经验，必须经过抽象、验证、晋升，不能简单复制粘贴到全局层。

## 2.2 Authoring View ≠ Runtime View

- 人写的源文档与 LLM 运行时拿到的 context 不应完全等同。
- 最佳实践是：**Markdown 源文档作为 authoring source，运行时按规则编译成 context bundle**。
- 这样才能同时满足：
  - 人可读、可维护、可 diff
  - LLM 可裁剪、可热加载、可按 token 预算组装

## 2.3 Global Policy, Local Knowledge

- 全局灵魂负责回答：**怎么做**。
- 项目灵魂负责回答：**这个项目是什么、为什么这么做、有哪些坑**。
- 两层之间必须是**显式治理 + 显式覆盖**，而不是靠 prompt 中的隐性暗示。

## 2.4 Hot / Warm / Cold 分层

- 不是所有灵魂内容都应该一直进入 prompt。
- 必须按运行时价值分层：
  - **Hot**：始终加载，短、稳定、强约束
  - **Warm**：按任务或模块加载
  - **Cold**：按需检索，仅在必要时补入

## 2.5 Stable IDs Over File Paths

- 文件路径可以改，知识身份不能变。
- 每个全局规则、每张项目卡片、每条候选规则都必须有稳定 ID。
- 运行时引用优先使用 `id + title`，而不是纯路径。

## 2.6 Versioned Contracts

- 灵魂不是自由散文，而是有契约的知识系统。
- 至少需要两层版本：
  - `schema_version`：结构契约版本
  - `soul_version`：内容版本
- 项目层还需要 `source_version_window`，避免用旧魂回答新版本问题。

## 2.7 Append-Only Evidence, Curated Summary

- 原始观察、issue、PR、踩坑记录、讨论，应尽量保留原始证据。
- 但运行时给 LLM 的不应是原始聊天记录，而应是**提炼后的规则、工作流、概念与约束**。
- 即：
  - 证据层可追加
  - 运行时层必须压缩、提炼、去噪

## 2.8 Traceability Before Cleverness

- 高价值结论必须尽量可追溯。
- 优先追溯到：
  - 代码
  - 测试
  - 官方文档
  - Maintainer issue / PR / release note
  - 社区讨论
  - 实验记录
- 无法追溯的经验只能作为 hypothesis，不应进入高优先热区。

## 2.9 Deterministic Assembly

- 运行时装配不能靠“临场感觉”。
- 必须基于稳定因素：
  - 任务类型
  - 用户意图
  - token 预算
  - 模块命中
  - 历史有效性
- 同类请求应尽量得到相似的魂上下文，避免回答漂移。

## 2.10 Self-Evolution With Guardrails

- 灵魂必须能进化，但不能无限自污染。
- 每条新增经验都应至少经过：
  - 观察
  - 候选规则
  - 验证
  - 晋升
- 这样才能避免全局灵魂和项目灵魂变成经验碎片垃圾场。

---

# 三、全局灵魂（AllInOne Soul）内容结构设计

## 3.1 全局灵魂的角色定位

全局灵魂不是品牌宣言，也不是营销文案。它是 AllInOne 的 **平台级操作系统文档**。

它只做三件事：

1. 定义平台如何提取项目知识；
2. 定义平台如何验证灵魂质量；
3. 定义平台如何使用项目灵魂为用户服务。

它的设计标准是：

- 尽量短
- 尽量稳定
- 尽量强约束
- 尽量可被 LLM 直接执行

## 3.2 全局灵魂推荐结构

### `00_identity.md`

**作用**：定义 AllInOne 是什么、不是什么、核心承诺是什么。  
**要求**：只放平台长期稳定身份，不放具体 workflow 或易变策略。

**建议内容**：

- Mission
- Non-Goals
- Core Promise
- User Positioning

**示例**：

```md
---
id: G-IDENTITY-001
layer: global
type: identity
schema_version: 1
soul_version: 1.0.0
status: active
---

# AllInOne Identity

## Mission
Turn open-source projects into usable AI knowledge containers for non-technical users.

## Non-Goals
- Not a generic code assistant
- Not a source-code search engine
- Not a passive documentation mirror

## Core Promise
When the user asks about a project, answer with project-grounded knowledge, practical guidance, and explicit uncertainty.
```

### `10_operating_principles.md`

**作用**：定义平台级行为准则，相当于“宪法”。  
**要求**：只写高稳定性原则，不写战术级细节。

**建议包含原则**：

- LLM-first
- Faithfulness over fluency
- User-service over code-recital
- Evidence before assertion
- Extraction serves usage, not archive
- Prefer minimal sufficient context
- Separate knowledge authoring from runtime assembly

**示例**：

```md
## Principle: Faithfulness Over Fluency
When project soul is available, prefer a constrained, source-grounded answer over a more elegant but weakly grounded answer.

## Principle: Minimal Sufficient Context
Load the smallest soul context that can answer the user's request with confidence.
```

### `20_service_protocol.md`

**作用**：定义 LLM 应如何为用户服务。  
**地位**：这是运行时最关键的全局文件之一。

**建议固定小节**：

- User intent classification
- Response mode selection
- Clarification policy
- Uncertainty policy
- Evidence policy
- Action recommendation policy

**示例**：

```md
## Intent Classes
- explain_project
- compare_options
- debug_with_project_context
- onboarding
- architecture_review
- usage_guidance

## Uncertainty Policy
If project soul is incomplete or stale:
1. state uncertainty explicitly
2. answer with best known project-grounded subset
3. suggest the missing knowledge area
```

### `30_extraction_protocol.md`

**作用**：定义如何生成项目灵魂。  
**本质**：这是全局灵魂治理项目灵魂生产的核心文件。

**建议内容**：

- 输入源优先级
- 提取维度
- 卡片生成规则
- 证据等级定义
- 去重与合并规则
- 冲突处理规则

**建议输入源优先级**：

- `P0`：源码 / 测试 / 配置 / 官方文档
- `P1`：官方 issue / PR / release notes
- `P2`：高质量社区经验
- `P3`：二手博客 / 论坛总结

**示例**：

```md
## Extraction Rule: Prefer Executable Truth
If code behavior conflicts with prose docs, trust executable behavior first, then record the conflict.

## Evidence Levels
- E1: source code / tests / official docs
- E2: maintainer issue / PR / release note
- E3: repeated community reports
- E4: weak anecdotal evidence
```

### `40_quality_protocol.md`

**作用**：定义如何判断灵魂是否“有用”。  
**关键转向**：评估目标不是“提取得准不准”，而是“能不能更好服务用户”。

**建议包含**：

- Quality dimensions
- Acceptance thresholds
- Evaluation dataset shape
- Regression policy
- Demotion / deprecation policy

**推荐质量维度**：

- Faithfulness
- Task usefulness
- Actionability
- Retrieval precision
- Contradiction rate
- Staleness risk

**示例**：

```md
## Acceptance Rule
A project soul is production-ready only if it improves answer quality against the no-soul baseline on representative user tasks.

## Failure Rule
If a hot-loaded rule repeatedly causes wrong answers, demote it from hot zone before rewriting it.
```

### `50_runtime_assembly_policy.md`

**作用**：定义运行时如何把全局灵魂和项目灵魂编排成给 LLM 的 context。  
**地位**：这是双层灵魂的桥梁文件。

**建议包含**：

- Task → context recipe mapping
- Hot / Warm / Cold 加载规则
- Token budget policy
- Conflict resolution order
- Cache policy
- Freshness policy

**示例**：

```md
## Conflict Order
1. safety override
2. global service policy
3. project contract card
4. project decision rule
5. community heuristics

## Load Priority
Always load:
- global identity
- global service protocol summary
- project manifest
Load on demand:
- architecture cards
- workflow cards
- community pitfalls
```

### `60_evolution_protocol.md`

**作用**：定义全局灵魂如何自我进化。  
**目标**：像 `CLAUDE.md` 那样可积累经验，但避免经验堆积混乱。

**建议三层状态**：

- `observation`
- `candidate_rule`
- `promoted_rule`

**建议晋升门槛**：

```md
## Promotion Gate
A candidate global rule must satisfy:
- observed in at least 3 independent tasks or 2 projects
- improves quality or reduces repeated failure
- has no conflict with existing higher-priority rules
```

### `70_glossary_and_taxonomy.md`

**作用**：统一术语，减少运行时 prompt 漂移。  
**建议定义术语**：

- soul
- hot / warm / cold
- code-half-soul
- community-half-soul
- evidence
- contract
- workflow
- decision rule
- active module
- task class

## 3.3 全局灵魂统一格式规范

### 文件格式

- 主体使用 Markdown
- 文件头使用 YAML frontmatter
- 复杂枚举和规则表可用 YAML code block
- 不建议 JSON 作为主格式

### 统一 frontmatter 字段

```yaml
id: G-RUNTIME-001
layer: global
type: runtime_policy
schema_version: 1
soul_version: 1.2.0
status: active
owner: allinone-core
last_reviewed: 2026-03-08
change_type: minor
summary: Runtime assembly rules for combining global and project souls.
```

### 正文结构规范

建议所有全局文件统一以下结构：

- Purpose
- Rules / Policies
- Exceptions
- Examples
- Promotion / Deprecation Notes
- References

## 3.4 全局灵魂如何实现“自我进化”

全局灵魂不应直接接受任意经验写回正式规则，而应采用 **三段式演化机制**：

### 第一层：观察层

路径示例：

- `global/evolution/observations/2026-03-08-token-overload-on-large-projects.md`

内容记录：

- 问题现象
- 触发条件
- 失败样本
- 初步猜想

### 第二层：候选规则层

路径示例：

- `global/evolution/candidates/G-CAND-RUNTIME-003.md`

内容记录：

- 候选规则
- 适用范围
- 风险说明
- 验证计划
- 预期收益

### 第三层：正式规则层

经验证通过后，候选规则才进入正式文件，例如：

- `50_runtime_assembly_policy.md`
- `20_service_protocol.md`
- `40_quality_protocol.md`

候选文件随后标记为：

- `promoted`
- 或 `rejected`

### 这样做的工程收益

- 避免 `CLAUDE.md` 式经验碎片无限叠加
- 保留演化轨迹
- 支持 rollback
- 方便自动评估
- 方便 future automation 提案

---

# 四、项目灵魂（Project Soul）内容结构设计

## 4.1 项目灵魂的角色定位

项目灵魂不是源码摘要，也不是 README 增强版。它是：

> **“这个开源项目值得被 AI 用来服务用户的最小充分知识体。”**

它要回答四类问题：

1. 这个项目是什么，核心机制是什么；
2. 这个项目实际怎么工作；
3. 这个项目哪些地方容易踩坑；
4. 面向非技术用户，应该如何解释和指导。

## 4.2 项目灵魂的三层模型

### 第一层：项目总纲层（Manifest / Spine）

作用：

- 作为项目灵魂的入口文件
- 提供项目级摘要
- 提供加载地图
- 定义高风险区与盲区

它不是知识全集，只是 **runtime spine**。

### 第二层：知识卡片层（C1 Cards）

作用：

- 承载项目知识的主数据
- 作为运行时装配的主要知识单元
- 支持增量更新与版本化维护

### 第三层：证据与演化层（Evidence / Evolution）

作用：

- 保存证据、观察、社区讨论、候选规则
- 为项目灵魂的修订和晋升提供追溯依据

## 4.3 项目灵魂如何与 C1 知识卡片体系结合

本报告建议：

> **C1 卡片体系不是项目灵魂的附属物，而是项目灵魂的 canonical knowledge unit。**

保留并正式化五类卡片：

- `concept_card`
- `workflow_card`
- `decision_rule_card`
- `contract_card`
- `architecture_card`

### `concept_card`

**用途**：定义项目核心概念、关键对象、心智模型与术语边界。  
**运行时价值**：适合 `explain`、`onboarding`、`compare` 场景。

**示例**：

```md
---
id: P-whisperx-CONCEPT-001
project: whisperx
type: concept_card
schema_version: 1
soul_version: 1.0.0
status: active
confidence: high
evidence_level: E1
tags: [identity, mental-model]
---

# Concept: Intel Entry

## Definition
An intel entry is the core published information unit in WhisperX.

## Why It Matters
Most user-facing actions eventually create, transform, rank, or display intel entries.

## Boundaries
An intel entry is not the same as a comment, moderation log, or feed snapshot.

## User Explanation
For non-technical users, explain it as "the atomic content item the platform collects and shows."
```

### `workflow_card`

**用途**：定义系统流程、用户旅程、调试路径与典型调用链。  
**运行时价值**：适合 `how-to`、`debug`、`onboarding`、agent 规划场景。

### `decision_rule_card`

**用途**：定义系统在某种条件下应如何判断、如何路由、如何选择。  
**运行时价值**：对 LLM 非常高，因为它可将踩坑经验提炼为可执行规则。

适合承载：

- 优先级规则
- 路由规则
- 选择条件
- 冲突处理
- anti-pattern

### `contract_card`

**用途**：定义输入输出契约、不变量、状态机约束、数据模型边界。  
**运行时价值**：在高风险场景优先级应非常高，可显著降低幻觉建议。

### `architecture_card`

**用途**：定义模块边界、依赖关系、数据流、部署结构与关键 trade-off。  
**运行时价值**：适合 `architecture_review`、`deep explanation`、`complex debug`。

## 4.4 代码半魂与社区半魂如何组织

项目灵魂内部应明确拆成两个知识域，但共享同一套卡片模型。

### A. 代码半魂（Code Half-Soul）

**来源**：

- source code
- tests
- config
- docs
- release notes

**特征**：

- 高可信
- 高稳定
- 更接近事实层

**适合承载**：

- architecture
- contract
- core concept
- executable workflow
- code-backed decision rules

### B. 社区半魂（Community Half-Soul）

**来源**：

- issue
- PR discussion
- maintainer comments
- discussions
- high-quality blog / forum / tutorial

**特征**：

- 更接近经验层
- 噪声更高
- 但对真实使用帮助极大

**适合承载**：

- pitfalls
- migration notes
- version-specific gotchas
- hidden assumptions
- maintainer preference heuristics

### 组织原则

- 不建议按“代码/社区”做两套完全独立的文档体系。
- 建议按卡片类型组织，再用 `origin_domain`、`origin_sources`、`confidence`、`evidence_level` 等字段表达来源属性。
- 从运行时视角，真正重要的是“知识类型”和“证据强弱”，而不是目录名本身。

### 建议卡片补充字段

```yaml
origin_domain: code
origin_sources:
  - type: source_code
    ref: src/api/intel.ts
  - type: test
    ref: tests/intel.spec.ts
confidence: high
evidence_level: E1
freshness: current
```

社区卡片示例：

```yaml
origin_domain: community
origin_sources:
  - type: issue
    ref: github:owner/repo#123
  - type: discussion
    ref: github:owner/repo/discussions/45
confidence: medium
evidence_level: E2
freshness: version_bound
applies_to:
  - ">=2.1.0 <2.4.0"
```

## 4.5 项目总纲（Manifest）设计

每个项目都必须有一个非常短但非常强的入口文件，例如：

- `projects/<project-id>/project_soul.md`

它不替代卡片，只负责：

- 项目身份
- 版本覆盖范围
- 核心模块
- 必读卡片
- 高风险区域
- 已知盲区

**示例**：

```md
---
id: P-whisperx-MANIFEST-001
project: whisperx
type: project_manifest
schema_version: 1
soul_version: 1.4.0
status: active
last_reviewed: 2026-03-08
---

# Project Soul: WhisperX

## Identity
WhisperX is an anonymous intel publishing platform focused on intake, review, ranking, and presentation.

## Core Modules
- submission
- moderation
- intel feed
- entity extraction
- search

## Always-Load Cards
- P-whisperx-CONCEPT-001
- P-whisperx-CONTRACT-003
- P-whisperx-WORKFLOW-002

## Risk Zones
- moderation state transitions
- stale detail page rendering
- localization fallback behavior

## Known Blind Spots
- incomplete community knowledge for plugin ecosystem
- insufficient benchmark data for search relevance tuning
```

## 4.6 项目灵魂的版本管理

### 原则

不能只依赖 Git commit。最佳实践是：

> **Git 管文件版本，Soul 自己管理语义版本。**

### 建议三层版本

#### `schema_version`

- 表示卡片结构契约是否变化
- 例如 frontmatter 字段调整、模板升级、关系模型变化

#### `soul_version`

- 表示项目灵魂内容版本
- 例如：`1.4.0`
- 升级规则建议：
  - major：知识结构重大调整 / 核心认知改变
  - minor：新增高价值卡片 / 覆盖扩展
  - patch：修正错误 / 提高准确性 / 小幅更新

#### `source_version_window`

- 表示该灵魂适用于哪些项目上游版本
- 避免旧魂回答新版本问题

**示例**：

```yaml
schema_version: 1
soul_version: 1.4.0
source_version_window:
  project_versions: ">=2.0.0 <2.5.0"
  commit_range: "abc123..def456"
freshness_status: current
```

### 卡片级版本

- 每张卡片还应有 `card_version`
- 因为项目总版本变化时，不是所有卡片都会同步变化
- 有利于缓存、增量刷新和 diff

### 废弃机制

卡片不要直接删除，建议使用：

- `status: deprecated`
- `replaced_by: <card-id>`
- `deprecation_reason: ...`

## 4.7 项目灵魂的关系模型

为了让 runtime assembler 更聪明，每张卡建议增加轻量关系字段：

```yaml
relates_to:
  - P-whisperx-CONCEPT-001
depends_on:
  - P-whisperx-CONTRACT-003
explains:
  - submission-flow
supersedes:
  - P-whisperx-WORKFLOW-001
```

目标不是立即做图数据库，而是：

- 提升装配精准度
- 控制 token 扩散
- 为未来图谱化演进预留接口

## 4.8 项目灵魂的工程强约束

建议定死以下约束：

1. Manifest 必须短，目标 `1-2k tokens`
2. 单卡只讲一件事，one card, one decision surface
3. 社区经验默认不进入 hot zone
4. 每个项目必须明确 blind spots

---

# 五、双层关联机制设计

## 5.1 一句话模型

- **全局灵魂 = control plane**
- **项目灵魂 = knowledge plane**
- **runtime assembler = execution plane**

全局层定义规则，项目层提供知识，运行时按规则调度知识。

## 5.2 全局灵魂如何指导项目灵魂生成

### 统一抽取契约

全局灵魂必须提供统一的生成协议，强制所有项目灵魂遵守同一套：

- 卡片类型定义
- frontmatter 字段规范
- evidence 分级
- confidence 分级
- freshness 标注
- version window 标注

这样做的收益：

- 不同项目之间可比较
- 装配器无需为每个项目编写特殊逻辑
- 可以做自动 lint、自动 diff、自动评估

### 统一抽取顺序

建议由全局协议强制以下顺序：

1. 先读代码真相层：源码、测试、配置、官方文档
2. 再读官方解释层：issue、PR、release notes
3. 最后补社区经验层：教程、博客、讨论

### 统一入魂标准

应入魂的信息：

- 高频影响用户理解的问题
- 高频影响操作成功率的问题
- 容易误解的核心概念
- 稳定的架构边界
- 高价值踩坑经验
- 关键不变量与接口约束

不应入魂的信息：

- 一次性噪音
- 源码 trivia 罗列
- 无证据支持的猜测
- 与用户服务无关的低价值细节

### 统一完成标准

项目灵魂最小合格覆盖建议为：

- 1 个 project manifest
- 核心 concept cards
- 核心 workflow cards
- 至少一组 contract cards
- 至少一组 architecture cards
- 风险区与 blind spots

否则状态只能是：

- `draft`

## 5.3 全局灵魂如何指导 LLM 使用项目灵魂服务用户

### 先做任务分类

用户请求首先由全局灵魂的 service protocol 分类，例如：

- `explain`
- `onboarding`
- `compare`
- `debug`
- `architecture_review`
- `usage_guidance`
- `migration`
- `pitfall_resolution`

### 决定装配顺序

建议固定装配顺序：

1. global identity summary
2. global service rules
3. project manifest
4. project hot cards
5. task-relevant warm cards
6. cold evidence only if needed

### 冲突裁决规则

建议固定优先级：

1. safety / external-action policy
2. global service protocol
3. project contract cards
4. project decision rule cards
5. project workflow / architecture cards
6. community heuristics

### 回答行为协议

全局灵魂应要求运行时回答尽量包含：

- 当前判断基于哪些项目知识
- 哪部分是高置信事实
- 哪部分是经验性建议
- 是否存在 blind spot / freshness risk
- 对用户的下一步建议

### 不知道时怎么办

建议强制策略：

- 项目灵魂缺失时：明说覆盖不足，只回答高置信部分
- 项目灵魂过期时：标注 version risk
- 证据冲突时：优先引用代码与官方证据，将社区经验降级为条件性建议

## 5.4 项目经验如何反馈到全局灵魂

项目经验不应直接写进全局灵魂，而应经过：

1. **项目层观察**：先在项目层记录新坑、新规则、新 blind spot
2. **候选全局规则**：抽象成 candidate rule
3. **跨项目验证**：至少在多个任务或多个项目上验证
4. **正式晋升**：通过后才进入全局正式规则
5. **反向发布**：之后的新项目与旧项目 refresh 都遵循新规则

适合晋升为全局规则的例子：

- Manifest 必须保持极短
- Community pitfalls 不应默认进入 hot zone
- Contract cards 在 debug 场景优先于 workflow cards

不适合晋升为全局规则的例子：

- 某个项目的特定插件坑
- 某个 maintainer 的个人偏好

## 5.5 推荐数据流模型

建议把双层关系分成三条流：

### 生成流

- global extraction protocol
- → generate project soul
- → produce manifest + cards + evidence

### 服务流

- user request
- → global service protocol classifies task
- → runtime loads project soul slices
- → answer with global response policy

### 演化流

- runtime failures / success patterns
- → project observations
- → candidate global rules
- → validated promotion into global soul

这样可以避免生成逻辑、运行逻辑、演化逻辑混在一起。

---

# 六、具体文件结构设计

## 6.1 推荐目录布局

建议采用：

```text
allinone/
  soul/
    global/
      00_identity.md
      10_operating_principles.md
      20_service_protocol.md
      30_extraction_protocol.md
      40_quality_protocol.md
      50_runtime_assembly_policy.md
      60_evolution_protocol.md
      70_glossary_and_taxonomy.md

      evolution/
        observations/
        candidates/
        archive/

    projects/
      <project-id>/
        project_soul.md
        manifest/
          module_map.md
          load_profile.md
          blind_spots.md

        cards/
          code/
            concept/
            workflow/
            decision_rule/
            contract/
            architecture/
          community/
            concept/
            workflow/
            decision_rule/
            contract/
            architecture/

        evidence/
          code_refs/
          issues/
          prs/
          discussions/
          release_notes/
          external_notes/

        evolution/
          observations/
          candidates/
          archive/

        versions/
          changelog.md
          compatibility_matrix.md

    runtime/
      profiles/
        explain.yaml
        onboarding.yaml
        debug.yaml
        architecture_review.yaml
        compare.yaml
      compilers/
        assembly_rules.md
      cache/
        README.md

    schemas/
      global_frontmatter.schema.yaml
      project_frontmatter.schema.yaml
      card_frontmatter.schema.yaml
      runtime_profile.schema.yaml
```

## 6.2 目录设计 rationale

### `global/`

- 存放平台级灵魂
- 稳定、短、强约束
- 变更频率低但影响面大

### `projects/<project-id>/`

- 每个项目一个独立知识容器
- 便于独立 refresh、独立版本管理、独立 diff
- 为未来拆分 package 或 repo 预留空间

### `runtime/`

- 存放运行时装配规则，而不是知识本体
- 使 authoring data 与 runtime logic 解耦

### `schemas/`

- 虽然主格式是 Markdown，但 schema 仍然必要
- 便于做 lint、校验、版本兼容检查

## 6.3 文件命名规范

### 全局文件命名

- 使用数字前缀保证顺序稳定
- 示例：
  - `00_identity.md`
  - `10_operating_principles.md`
  - `20_service_protocol.md`

### 项目目录命名

- 使用稳定的 `project-id`
- 建议全小写、kebab-case
- 尽量与上游仓库主标识一致

### 卡片命名规范

建议使用：

```text
<card-id>__<slug>.md
```

例如：

- `P-whisperx-CONCEPT-001__intel-entry.md`
- `P-whisperx-WORKFLOW-003__submission-to-feed-flow.md`
- `P-whisperx-CONTRACT-002__intel-state-transition.md`
- `P-whisperx-DECISION-004__ranking-fallback-rule.md`
- `P-whisperx-ARCH-001__content-pipeline.md`

### 观察与候选规则命名

建议使用：

```text
<date>__<topic>.md
<candidate-id>__<topic>.md
```

例如：

- `2026-03-08__token-overload-in-large-projects.md`
- `G-CAND-RUNTIME-003__demote-community-cards-from-hot-zone.md`

## 6.4 文件模板

### 全局文件模板

```md
---
id: G-RUNTIME-001
layer: global
type: runtime_policy
schema_version: 1
soul_version: 1.2.0
status: active
owner: allinone-core
last_reviewed: 2026-03-08
summary: Runtime assembly rules for combining global and project souls.
---

# Runtime Assembly Policy

## Purpose
Define how global soul and project soul are composed into runtime context.

## Rules
- Always load global identity summary
- Always load service protocol summary
- Always load project manifest
- Load hot cards before warm cards
- Load cold evidence only on demand

## Exceptions
- If no project soul exists, use global fallback response mode

## Examples
### Example: explain_project
Load project manifest + concept cards + architecture summary.

## Deprecation Notes
None.

## References
- G-SERVICE-001
- G-QUALITY-001
```

### 项目 Manifest 模板

```md
---
id: P-whisperx-MANIFEST-001
project: whisperx
layer: project
type: project_manifest
schema_version: 1
soul_version: 1.4.0
status: active
source_version_window:
  project_versions: ">=2.0.0 <2.5.0"
freshness_status: current
last_reviewed: 2026-03-08
---

# Project Soul: WhisperX

## Identity
WhisperX is an anonymous intel publishing platform.

## User-Facing Summary
For non-technical users, it can be explained as a system for collecting, reviewing, ranking, and presenting anonymous intel.

## Core Modules
- submission
- moderation
- feed
- search
- localization

## Always-Load Cards
- P-whisperx-CONCEPT-001
- P-whisperx-CONTRACT-002
- P-whisperx-WORKFLOW-003

## High-Risk Zones
- state transition edge cases
- stale detail rendering
- i18n fallback mismatch

## Known Blind Spots
- limited plugin ecosystem coverage
- incomplete community knowledge after v2 refactor
```

### 通用卡片模板

```md
---
id: P-whisperx-CONCEPT-001
project: whisperx
layer: project
type: concept_card
schema_version: 1
card_version: 1.0.0
soul_version: 1.4.0
status: active
origin_domain: code
origin_sources:
  - type: source_code
    ref: src/intel/model.ts
confidence: high
evidence_level: E1
freshness: current
tags: [core, user-facing]
relates_to:
  - P-whisperx-WORKFLOW-003
---

# Concept: Intel Entry

## Definition
The primary content object shown to end users.

## Why It Matters
Most workflows and UI behaviors depend on this object.

## Boundaries
It is not a moderation log, raw submission payload, or derived feed snapshot.

## User Explanation
Explain it as the basic content unit the platform manages and displays.

## Operational Notes
Used by submission, ranking, and feed display workflows.

## References
- src/intel/model.ts
- tests/intel/model.spec.ts
```

### 社区经验卡模板

```md
---
id: P-whisperx-DECISION-009
project: whisperx
layer: project
type: decision_rule_card
schema_version: 1
card_version: 1.0.0
soul_version: 1.4.0
status: active
origin_domain: community
origin_sources:
  - type: issue
    ref: github:owner/repo#482
  - type: discussion
    ref: github:owner/repo/discussions/77
confidence: medium
evidence_level: E2
freshness: version_bound
applies_to:
  - ">=2.2.0 <2.4.0"
---

# Decision Rule: Prefer Manual Cache Refresh After Schema Drift

## Rule
If feed shape changes but UI behavior looks stale, check cache invalidation before assuming data corruption.

## Why
Multiple reports show stale rendering caused by cache mismatch rather than broken source records.

## Scope
Applies only to versions 2.2.x to 2.3.x.

## Risk
Do not generalize this as a permanent architecture rule.
```

### 观察文件模板

```md
---
id: P-whisperx-OBS-20260308-001
project: whisperx
type: observation
status: open
created_at: 2026-03-08
source_tasks:
  - debug-session-20260308-01
summary: Repeated confusion between content-state bugs and cache-staleness bugs.
---

# Observation: Cache Staleness Misdiagnosed as Data-State Bug

## What Happened
Three recent debugging tasks initially assumed state corruption.

## Evidence
- issue #482
- local regression note
- user report transcript

## Candidate Insight
A decision rule may be needed for triaging stale UI cases.

## Next Validation
Check whether this repeats across at least two more tasks.
```

## 6.5 辅助文件设计

建议每个项目至少再配三个辅助文件：

### `manifest/module_map.md`

- 说明模块边界与加载关系
- 用于 runtime 选择相关卡片簇

### `manifest/load_profile.md`

- 维护项目自己的 hot / warm / cold 建议
- 因为不同项目热点不同，不能完全依赖全局默认

示例：

```md
## Hot
- manifest
- core concept cards
- critical contract cards

## Warm
- primary workflows
- recent pitfalls
- architecture summaries

## Cold
- issue-derived heuristics
- deprecated cards
- deep evidence trails
```

### `manifest/blind_spots.md`

- 独立维护盲区
- 因为盲区会动态变化，而且对运行时信任边界十分关键

## 6.6 版本与变更文件

### `versions/changelog.md`

记录灵魂自身如何变化，不是上游源码 changelog。建议记录：

- 新增了哪些卡片
- 哪些卡片被废弃
- 哪些盲区被补齐
- 哪些版本窗口发生变化

### `versions/compatibility_matrix.md`

记录：

- 当前灵魂覆盖哪些上游版本区间
- 哪些模块覆盖较完整
- 哪些模块覆盖不足

这将直接帮助 runtime 判断当前回答能否高置信输出。

---

# 七、LLM 消费时的动态组装策略

## 7.1 运行时上下文的五层结构

建议每次给 LLM 的 soul context 由五层组成：

### 1. Global Core

包括：

- global identity 摘要
- operating principles 摘要
- service protocol 关键规则

特点：

- 极短
- 高稳定
- 几乎每次都加载

### 2. Project Spine

包括：

- project manifest
- blind spots 摘要
- load profile 摘要

作用：

- 提供项目心智模型
- 限定版本边界
- 显示盲区

### 3. Task Cards

这是主要知识负载区，按任务类型选择卡片簇，例如：

- explain → concept + architecture
- debug → contract + workflow + decision rules
- onboarding → concept + workflow
- migration → decision rules + compatibility + community pitfalls

### 4. Evidence Tail

用于高风险问题、冲突解释、深度追溯。默认不加载全量证据。

### 5. Session Memory Overlay

当前会话已讨论上下文的摘要，用于避免重复加载，提高连贯性。  
注意：这层不应污染正式 soul，只是 runtime overlay。

## 7.2 推荐装配流程

### Step 1: 识别任务类型

建议最小任务分类集：

- `explain_project`
- `onboarding`
- `how_to`
- `debug`
- `compare`
- `architecture_review`
- `migration`
- `pitfall_resolution`

### Step 2: 判断项目范围

判断：

- 是否指定项目
- 是否涉及多个项目
- 是否涉及版本窗口
- 是否为跨项目比较

### Step 3: 读取最小全局核心

始终加载：

- `global/00_identity.md` 摘要
- `global/20_service_protocol.md` 关键规则
- `global/50_runtime_assembly_policy.md` 关键规则

### Step 4: 读取项目脊柱

始终加载：

- `projects/<id>/project_soul.md`
- `manifest/blind_spots.md` 摘要
- `manifest/load_profile.md` 摘要

### Step 5: 按任务选择卡片簇

- `explain_project`
  - concept cards
  - architecture summary cards
- `onboarding`
  - concept cards
  - workflow cards
- `debug`
  - contract cards
  - workflow cards
  - relevant decision rule cards
- `migration`
  - compatibility matrix
  - version-bound decision rules
  - selected community pitfalls
- `architecture_review`
  - architecture cards
  - contract cards
  - major trade-off rules

### Step 6: 检查预算并裁剪

如果超过 token 预算，按以下顺序裁剪：

1. 去掉 cold evidence
2. 去掉低置信 community cards
3. 将 architecture / workflow 压缩成摘要
4. 保留 manifest、critical contracts、critical decision rules

### Step 7: 回答前一致性检查

至少检查：

- 当前回答是否超出 `source_version_window`
- 当前结论是否与 contract 冲突
- 当前建议是否落入 blind spot 区域

## 7.3 热加载 vs 冷加载判断逻辑

### Hot Load

始终进入 prompt，要求短、稳、强约束。

建议进入 hot 的内容：

- Global：
  - identity summary
  - service protocol summary
  - runtime policy summary
- Project：
  - project manifest
  - 1-3 张最高价值 concept / contract 卡
  - blind spots summary

进入 hot 的条件：

- 高频任务命中
- 错误代价高
- 内容稳定
- 高证据等级
- 对多数回答有帮助

### Warm Load

按任务类型和会话主题加载，典型包括：

- primary workflows
- architecture cards
- decision rules
- version-specific compatibility notes
- recently active module cards

### Cold Load

默认不进入 prompt，仅在需要时检索，典型包括：

- issue-derived heuristics
- deep evidence trails
- deprecated cards
- long migration notes
- low-confidence community 经验

## 7.4 Token 预算分配建议

### 小型请求：总预算 8k-12k

适用于：

- explain
- onboarding
- 单点 how-to

建议分配：

- 10% `global core`
- 15% `project spine`
- 55% `task cards`
- 10% `session overlay`
- 10% `response headroom`

### 中型请求：总预算 15k-30k

适用于：

- debug
- compare
- architecture explanation

建议分配：

- 8% `global core`
- 12% `project spine`
- 55% `task cards`
- 10% `evidence tail`
- 15% `response headroom`

### 大型请求：总预算 30k-80k

适用于：

- 深度架构评审
- 复杂迁移分析
- 多模块故障排查

建议分配：

- 5% `global core`
- 10% `project spine`
- 50% `task cards`
- 20% `evidence tail`
- 15% `response headroom`

### 硬约束

- `global core` 不超过总预算的 `10%`
- `project manifest + blind spots` 不超过 `15%`
- 至少保留 `15%` 给模型输出
- evidence 仅在复杂度和风险上升时扩容

## 7.5 动态裁剪策略

建议按价值顺序裁剪，而不是平均截断：

1. 去掉 cold evidence
2. 去掉低置信 community cards
3. 将 architecture cards 压缩成 summary
4. 将 workflow cards 压缩成 decision steps
5. 保留 contract cards 与 critical decision rules

原因：

- 少了 evidence tail，回答通常还能成立
- 少了 contract，回答很容易错
- 少了 blind spots，回答很容易假装完整

## 7.6 热加载与冷加载的判定因子

建议 runtime 同时考虑以下因素：

### 任务风险等级

- 高风险：debug、migration、架构修改建议
- 低风险：概念解释、快速介绍

### 模块活跃度

- 当前问题命中哪些模块
- 最近会话反复命中哪些模块
- 这些模块是否属于 risk zone

### 卡片历史有效性

- 哪些卡在类似任务中高频有效
- 哪些卡经常加载但贡献低

### 新鲜度与版本匹配

- 卡片版本窗口不匹配时应自动降级
- freshness 风险高时不宜进入 hot

### 冲突状态

- 一旦检测到代码半魂与社区半魂冲突：
  - 提升 evidence tail 权重
  - 降低社区 heuristics 的默认优先级

## 7.7 冷启动与热启动策略

### 冷启动（Cold Start）

适用：

- 新会话第一次进入项目
- 用户问题很泛
- 还不知道命中哪个模块

建议加载：

- global core
- project manifest
- top concept cards
- top contract card
- blind spots summary

### 热启动（Hot Start）

适用：

- 会话已经连续讨论同一项目
- 模块明确
- 已有 session overlay

建议：

- 复用已缓存的 global core / project spine
- 仅增量加载新的 task cards
- 避免重复加载已确认上下文

## 7.8 推荐 runtime profile 文件

例如：`runtime/profiles/debug.yaml`

```yaml
task: debug
load_order:
  - global_core
  - project_manifest
  - blind_spots_summary
  - critical_contract_cards
  - relevant_workflow_cards
  - decision_rule_cards
  - evidence_tail_if_conflict
budget:
  global_core_pct: 8
  project_spine_pct: 12
  task_cards_pct: 50
  evidence_pct: 15
  response_headroom_pct: 15
prune_order:
  - cold_evidence
  - low_confidence_community
  - architecture_summaries
hard_keep:
  - project_manifest
  - blind_spots_summary
  - critical_contract_cards
```

---

# 八、质量验证与治理建议

## 8.1 评估目标

灵魂文档的验证标准不是“内容好看”，而是：

> **加载灵魂后的 LLM，是否比未加载灵魂时更好地服务用户。**

## 8.2 推荐评估维度

- **Faithfulness**：回答是否基于灵魂内容，而非幻觉
- **Usefulness**：回答是否切中用户任务
- **Actionability**：回答是否给出明确下一步
- **Constraint awareness**：是否尊重 contract / blind spots / version window
- **Conciseness**：是否以最小充分上下文解决问题

## 8.3 A/B 评估方法

建议构建代表性任务集，对同一问题做两组测试：

- **A 组**：无灵魂上下文
- **B 组**：加载双层灵魂上下文

比较指标：

- 用户任务完成率
- 错误率
- 误导性建议率
- 追问次数
- 回答是否显式声明不确定性

## 8.4 治理建议

建议建立最小治理闭环：

1. 新项目 soul 先进入 `draft`
2. 通过最小覆盖检查后进入 `active`
3. 运行时监控高频失败模式
4. 失败模式进入 observation
5. 验证通过后更新项目 soul 或晋升为 global rule

---

# 九、v1 落地建议

## 9.1 v1 最小可落地实现

建议 v1 先实现以下能力，不要一开始上复杂图谱或数据库：

1. 建立 `global/` 文件集
2. 为单个重点项目建立 `project_soul.md + C1 cards`
3. 建立 `runtime/profiles/*.yaml`
4. 实现最小装配器：按任务类型拼 context
5. 建立最小质量评估：有魂 vs 无魂

## 9.2 v1 不建议做的事

v1 不建议：

- 一开始就上图数据库
- 一开始就自动从全网大规模抓社区经验
- 一开始就允许模型自动改写正式全局规则
- 一开始就把所有历史记录都纳入灵魂

## 9.3 v1 成功标准

如果以下条件满足，可视为 v1 成功：

1. 至少一个真实项目的灵魂能稳定服务多个用户任务
2. 有魂回答显著优于无魂回答
3. 灵魂文档在多人/多轮维护下仍保持清晰结构
4. runtime 能在受限 token 预算下稳定工作

---

# 十、长期蓝图（附录）

## 10.1 从文件系统向编译系统演进

长期来看，双层灵魂可从“静态文件集合”演进到“编译型知识系统”：

- Markdown 仍是 source of truth
- 编译器生成：
  - runtime bundles
  - summary caches
  - task-specific packs
  - coverage / staleness reports

## 10.2 从轻关系到知识图谱

当项目数量与卡片量上升后，可逐步增强：

- 从 `relates_to / depends_on / supersedes` 轻关系
- 演进到显式 graph index
- 最终支持跨项目概念对齐与经验复用

但前提是 v1 先证明 Markdown-first + card model 是有效的。

## 10.3 从人工晋升到半自动晋升

长期可引入：

- 自动发现高频 observation
- 自动生成 candidate rules
- 自动做回放评估
- 人工批准后晋升

核心原则仍应保持：

- **自动提案可以有，自动正式入魂必须慎重。**

---

# 十一、最终结论

AllInOne 的灵魂文档最佳实践，不应是“多层 Markdown 文件简单拼接”，而应是：

> **一个以 Markdown 为主数据、以 C1 卡片为知识单元、以全局协议为治理层、以 runtime assembler 为执行层的双层知识系统。**

具体来说：

- **全局灵魂**：定义平台如何提取知识、验证质量、服务用户、装配上下文、自我进化。
- **项目灵魂**：以 `project manifest + C1 cards + evidence/evolution` 构成项目最小充分知识体。
- **双层关联机制**：通过治理、编排、晋升三个机制实现闭环。
- **文件结构**：采用 `global/ + projects/ + runtime/ + schemas/` 布局。
- **运行时策略**：采用 hot / warm / cold 分层与 token 预算控制的动态组装机制。

这套设计的核心价值在于：

1. **对 LLM 友好**：结构化 Markdown、短卡片、显式规则、低噪声
2. **对人友好**：可读、可 diff、可 review、可版本化
3. **对工程友好**：可编排、可缓存、可评估、可演化
4. **对产品友好**：最终评判标准不是“抽取得像不像”，而是“能不能更好为用户服务”

换句话说：

AllInOne 不应只是“把项目知识存下来”，而应做到：

> **把项目知识变成可被 LLM 稳定调用、可持续演化、可验证有效的知识操作系统。**


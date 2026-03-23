# AllInOne 灵魂提取方案——全面汇总报告

**日期**: 2026-03-08
**数据源**: Gemini 提取方法论调研 + Codex 详细提取方案
**分析者**: Claude (Opus 4.6)

---

## 一、两份报告的角色

| | Gemini 报告 | Codex 报告 |
|---|---|---|
| **定位** | 学术+工业界前沿趋势 | 可落地的完整执行方案 |
| **深度** | 6.4KB，5 章概述 | 83.8KB，完整 prompt 模板+验证规则 |
| **核心贡献** | DSPy 范式、多模态提取、LLM-as-Judge 评估体系、级联路由降本 | 完整 prompt chain（鹰眼3步+深潜3层+社区3级+大仓库Map/Reduce+Judge） |

---

## 二、Gemini 的关键发现（前沿趋势）

### 2.1 从 Prompt Engineering 到 System Programming

Gemini 指出 2026 年最佳实践已经不是手写 prompt，而是用 **DSPy** 框架：
- **定义输入输出签名**（如 `ExtractArchitecture(code_chunk) -> list[ArchitecturalConstraint]`）
- **模块化思考**：用 `TypedChainOfThought` 强制 LLM 先推理再输出结构化数据（避免直接生成 JSON 导致的 10-15% 准确率惩罚）
- **MIPROv2 自动优化**：用强模型自动为弱模型生成最佳 Few-shot 示例和指令

**对 AllInOne 的启示**：v1 先用 Codex 的手写 prompt 跑通，v2 考虑用 DSPy 自动优化提取质量。

### 2.2 结构化输出的硬约束

- 用 Pydantic + JSON Schema 确保输出格式 100% 正确
- 加入断言（如"提取的组件名必须在源代码中出现过"），失败时自动让 LLM 自我修正

### 2.3 多模态提取

- 原生多模态模型（Gemini 2.0 / Llama 4）可直接处理视频/音频
- 但 AllInOne v1 不需要——聚焦 GitHub 代码+社区文本即可

### 2.4 冲突知识处理

当 Issue 结论与代码矛盾时：
- 代码基权重 1.0，Merged PR 0.9，Maintainer 评论 0.8，普通用户 workaround 0.4
- 每条知识必须打上 `confidence_score` 和 `conflict_resolution_reason`

### 2.5 LLM-as-Judge 评估

- **离散分类法**取代主观 1-10 分：`Fully Grounded` / `Incomplete` / `Hallucinated` / `Contradictory`
- **MINEA 范式**（大海捞多针）：人为注入罕见但合理的架构约束，测试提取引擎能否准确抓取
- **警惕评委偏见**：Judge Prompt 必须强调"只根据提供的 Context 评判，禁止引入外部知识"

### 2.6 级联路由降本

- **Tier 1（本地 8B/14B 模型）**：过滤 70% 低价值流量
- **Tier 2（Claude Haiku / GPT-4o-mini）**：标准总结任务
- **Tier 3（Opus / Sonnet / Gemini Pro）**：仅用于跨文件深层推断

---

## 三、Codex 的完整提取方案（核心）

### 3.1 六大工程原则

1. **先画像，后提取**：先知道仓库是什么，再决定怎么提取
2. **先鹰眼，后深潜**：先找到灵魂候选区，再精读
3. **先证据，后结论**：卡片必须可追溯
4. **先卡片，后汇总**：先产出独立可用知识对象，再做整体收敛
5. **先保守，再补全**：不确定就进 Gap Queue，不要强行脑补
6. **代码半魂优先保证真实性，社区半魂补充真实使用经验**

### 3.2 完整流水线总览

```
Repo Input
  → Repo Profile（仓库画像）
  → Eagle Eye Step 1（项目身份+核心概念）
  → Eagle Eye Step 2（核心模块+关系图）
  → Eagle Eye Step 3（Soul Locus 评分+深潜优先级）
  → Deep Dive Queue
  → L1 Deep Dive（概念提取 → concept_card）
  → L2 Deep Dive（流程提取 → workflow_card + contract_card）
  → L3 Deep Dive（决策提取 → decision_rule_card + architecture_card）
  → Community Pipeline（Tier 1→2→3 → 社区卡片）
  → Merge & Validate
  → Judge（质量门控）
  → Gap Queue（不确定内容管理）
  → Final Soul Cards
```

### 3.3 鹰眼阶段（3 步）

#### Step 1：识别项目身份和核心概念

- **输入**：repo_profile + Repomix --compress 输出
- **输出**：eagle_eye_identity.md
- **目标**：项目在解决什么问题、面向谁、5-10 个核心概念、每个概念的锚点文件
- **关键约束**：不允许发明实现细节，不确定就标 low confidence

#### Step 2：识别核心模块和模块关系

- **输入**：Step 1 输出 + Repomix --compress
- **输出**：eagle_eye_module_map.md
- **目标**：4-8 个核心模块（按职责划分，不是抄目录）、entrypoint/orchestrator/state owner、模块间关系
- **关键约束**：必须识别 Mermaid 关系图

#### Step 3：计算 Soul Locus Score

- **输入**：Step 1+2 输出 + Repomix --compress
- **输出**：eagle_eye_soul_locus.md + deep_dive_queue.yaml
- **评分维度**（8 维，满分 100）：

| 维度 | 权重 | 含义 |
|------|---:|------|
| Domain Centrality | 20% | 是否承载核心业务/领域概念 |
| Execution Influence | 15% | 是否影响主执行路径 |
| Orchestration Power | 15% | 是否编排多个模块/状态转换 |
| Data/State Gravity | 15% | 是否拥有关键数据结构/状态 |
| Rule Density | 10% | 是否包含显著条件判断/校验 |
| Boundary Importance | 10% | 是否是外部接口/持久层 |
| Cross-Module Bridge | 10% | 是否连接多个模块 |
| Concept Density | 5% | 是否高密度体现核心术语 |

**分数解释**：85-100 必须深潜 / 70-84 应该深潜 / 55-69 按需深潜 / <55 仅作上下文

#### 鹰眼合格标准（6 条硬规则）

1. 身份清晰——能用一句人话解释项目用途
2. 概念有锚点——每个核心概念绑定路径
3. 模块不是目录复述——按职责和边界划分
4. Soul Locus 有区分度——分数不能都挤在窄区间
5. 跨步骤一致——概念、模块、top loci 能互相对应
6. 存在不确定性声明——必须有 open questions

### 3.4 深潜阶段（3 层，严格分离）

#### L1：概念提取——做什么

- **输出**：concept_card（每个 locus 1-3 张）
- **内容**：定义、解决的问题、为什么重要、Is/Is Not/Out of Scope 边界、非技术用户解释、证据锚点
- **验收**：不是源码复述；必须有边界定义；必须有非技术解释；至少 1 个明确锚点

#### L2：流程提取——怎么流

- **输出**：workflow_card（1-2 张）+ contract_card（1-3 张）
- **workflow_card 内容**：触发器、前置条件、有序步骤、分支、状态转换、输出/副作用、失败模式
- **contract_card 内容**：输入输出契约、不变量、校验规则、状态转换约束、违约后果
- **验收**：workflow 必须有 Trigger + ordered steps + failure modes；contract 必须是约束不是流程，必须包含 invariant

#### L3：决策提取——为什么这么设计

- **输出**：decision_rule_card（1-3 张）+ architecture_card（1 张）
- **decision_rule_card 内容**：触发条件、决策行为、为什么可能存在、trade-off（优化什么/放弃什么）、证据强度（explicit/strong_inference/weak_hypothesis）
- **architecture_card 内容**：结构角色、职责、上下游依赖、结构模式、trade-off、非目标、推断边界
- **验收**：decision_rule 必须条件驱动+有 trade-off+区分证据强弱；architecture 必须回答结构角色+upstream/downstream+non-goals

#### 每个 locus 深潜完成最低标准

- 1-3 张 concept_card
- 1-2 张 workflow_card
- 1-3 张 contract_card
- 1-3 张 decision_rule_card
- 1 张 architecture_card
- 每张卡至少 1 个源码锚点

### 3.5 社区半魂提取（3 级漏斗）

#### 数据采集策略

**优先数据源**：GitHub Issues → PR review threads → Discussions → Release notes → 外部社区

**Issue 筛选规则**：
- comments >= 3
- 含代码块/stack trace
- 标题含技术关键词（bug/error/fail/unexpected/regression/performance/migration/workaround/cache/retry/timeout...）
- 标签命中（bug/question/performance/security/wontfix/stale...）
- 作者含 OWNER/MEMBER/COLLABORATOR

**排除**：bot 消息、+1/same here/thanks、纯 CI 日志、空模板

#### 长尾失败 Issue 专门保留

满足任一条件强制保留：
- label in {wontfix, stale, not planned} 且 comments >= 8
- 讨论时长 >= 14 天
- 至少一位 maintainer 解释 why-not
- 出现多个 workaround 候选
- 涉及高 Soul Locus 模块

**三种处理策略**：
- Maintainer 明确解释 why-not → decision_rule_card + architecture_card
- 多用户复现但无修复 → workflow_card（workaround）+ decision_rule_card
- 讨论很长但结论摇摆 → gap_note（不要硬写成正式规则）

#### 贡献者权重

| 角色 | 基线权重 |
|------|-------:|
| Owner/Maintainer | 1.00 |
| Member/Collaborator | 0.90 |
| 核心贡献者（merged PR > 20） | 0.80 |
| 常规贡献者 | 0.65 |
| 高质量外部报告者 | 0.55 |
| 普通外部用户 | 0.40 |
| 低质量噪音/bot | 0.10 |

**线程可信度公式**：
```
thread_credibility
= 0.40 * max_contributor_weight
+ 0.25 * reproducibility_score
+ 0.15 * consensus_score
+ 0.10 * resolution_signal
+ 0.10 * recency_factor
```

#### Tier 1（免费规则过滤）

- 纯规则：body_length >= 80 chars 或 comments >= 3、含技术关键词/代码块、语言在支持集合内
- 规则无法确定时交给本地小模型
- 决策：KEEP / REVIEW / REJECT

#### Tier 2（小模型分类）

- 打 relevance_score（0-100）
- 分类内容类型：root_cause_analysis / workaround / design_debate / migration_note / integration_bug / performance_issue / security_warning / docs_gap / usage_question / noise
- 通过线：>= 70 直接进 Tier 3；55-69 若关联高 Soul Locus 则进；< 55 除非长尾失败 issue

#### Tier 3（大模型提取卡片）

- 输出社区版知识卡片（在标准卡片上增加 origin_domain: community、thread_credibility、maintainer_signal、valid_for_versions 等字段）
- 如果线程有价值但不确定 → 输出 gap_note 而非强行写规则

### 3.6 大仓库处理方案

#### 四级阈值

| 仓库级别 | 标准 | 处理策略 |
|---------|------|---------|
| 小 | <= 80k 压缩 tokens，<= 500 文件 | 直接 Repomix → Eagle Eye → Deep Dive |
| 中 | 80k-220k tokens，500-1500 文件 | Repomix + 模块级 Eagle Eye + 有界 Deep Dive |
| 大 | 220k-600k tokens，1500-5000 文件 | Map/Reduce；必要时加 DeepWiki 索引 |
| 超大/Monorepo | > 600k tokens，> 5000 文件 | 先做 package graph / product slice，再分治 |

#### Map/Reduce 策略

- **Map**：每个模块 cluster 提取局部概念、流程、契约、决策、外部依赖
- **Reduce**：合并局部摘要为全局身份、全局模块图、全局 Soul Loci、冲突列表
- 有完整的 Map prompt + Reduce prompt 模板

#### Monorepo 分治

1. 做 package/service graph
2. 划分 product slices
3. 每个 slice 独立跑完整流水线
4. 最后补 monorepo-level integration cards

### 3.7 质量验证

#### LLM-as-Judge

- 五维评分：Faithfulness / Boundary Clarity / Reusability / Confidence Handling / Specificity
- 判决：PASS / REVISE / REJECT
- 有完整 Judge prompt 模板

#### 自动验证规则

- **格式检查**：YAML frontmatter 可解析、必填字段齐全、枚举值合法
- **引用验证**：ref 路径在 repo 中存在、thread_ref 格式合法
- **一致性检查**：跨卡片引用一致

#### Gap Queue

不确定的内容不强行写卡片，进入 Gap Queue 等待后续补充证据。

---

## 四、Gemini vs Codex 的互补关系

| 环节 | Gemini 的贡献 | Codex 的贡献 |
|------|-------------|-------------|
| Prompt 设计 | DSPy 自动优化范式（v2 用） | 手写完整 prompt chain（v1 用） |
| 输出控制 | Pydantic + JSON Schema + 断言 | YAML frontmatter + Markdown 模板 |
| 质量验证 | MINEA 注入测试、离散分类法 | Judge prompt + 自动规则 + Gap Queue |
| 冲突处理 | 信心度加权公式 | 贡献者权重 + 线程可信度公式 |
| 降本 | 级联路由（Tier 1/2/3 模型分级） | 四级仓库阈值 + Map/Reduce |
| 多模态 | 原生多模态提取（v2 用） | 不涉及 |

**结论**：Codex 方案是 v1 的执行骨架，Gemini 方案是 v2 的优化方向。

---

## 五、统一的证据和置信度体系

两份报告在这方面高度一致：

### 证据等级

| 等级 | 含义 | 来源 |
|------|------|------|
| E1 | 源码/测试/官方文档/schema/config | 代码半魂 |
| E2 | Maintainer issue/PR/release note | 两者皆有 |
| E3 | 高质量社区共识/多次复现 | 社区半魂 |
| E4 | 弱 anecdotal evidence | 社区半魂 |

### 推断强度

- `explicit`：代码/文档直接支持
- `strong_inference`：多重间接证据支持
- `weak_hypothesis`：有限证据，仅供参考

### 置信度

- `high` / `medium` / `low`

---

## 六、v1 执行路线

### 第一步：选择验证项目

建议用 WhisperX（Tangsir 自己的项目，~2840 行核心代码）作为第一个提取对象：
- 规模适中（小仓库级别）
- Tangsir 完全了解项目，可以判断提取质量
- 有真实的 Issues/讨论可以测试社区提取

### 第二步：代码半魂提取

1. `repomix --compress` WhisperX 代码
2. 跑 Eagle Eye 3 步（用 Codex 的 prompt 模板）
3. 按 Soul Locus 排名选 top 3-5 个 loci
4. 对每个 locus 跑 L1 → L2 → L3 深潜
5. 产出 concept_card + workflow_card + contract_card + decision_rule_card + architecture_card

### 第三步：社区半魂提取

1. 抓取 WhisperX 相关 Issues/Discussions
2. Tier 1 规则过滤
3. Tier 2 小模型分类
4. Tier 3 大模型提取社区卡片

### 第四步：质量验证

1. LLM-as-Judge 评估每张卡片
2. 自动格式/引用/一致性校验
3. 不合格的进 Gap Queue 或 REVISE

### 第五步：A/B 对比

- 同一问题分别问"有灵魂的 LLM"和"无灵魂的 LLM"
- 对比回答质量，验证灵魂提取是否真的有效

---

## 七、完整 Prompt 模板索引

Codex 报告提供了以下完整 prompt 模板（System Prompt + User Prompt + 输出模板 + 验收规则）：

| 阶段 | Prompt 数量 | 输出卡片类型 |
|------|-----------|------------|
| Eagle Eye Step 1 | 1 套 | eagle_eye_identity.md |
| Eagle Eye Step 2 | 1 套 | eagle_eye_module_map.md |
| Eagle Eye Step 3 | 1 套 | eagle_eye_soul_locus.md |
| L1 Deep Dive | 1 套 | concept_card |
| L2 Deep Dive | 1 套 | workflow_card + contract_card |
| L3 Deep Dive | 1 套 | decision_rule_card + architecture_card |
| Community Tier 1 | 1 套 | KEEP/REVIEW/REJECT JSON |
| Community Tier 2 | 1 套 | relevance_score + classification JSON |
| Community Tier 3 | 1 套 | 社区卡片 + gap_note |
| Map（大仓库） | 1 套 | cluster_summary.md |
| Reduce（大仓库） | 1 套 | 全局 Eagle Eye 报告 |
| Judge | 1 套 | judge_report.md |

**共 12 套完整 prompt 模板**，全部包含 System Prompt、User Prompt、输出模板和验收规则。

---

## 八、下一步行动

1. **确认本方案** → Tangsir 审核
2. **安装 Repomix** → `npm install -g repomix`
3. **选 WhisperX 做验证** → 走完整提取流水线
4. **评估结果** → A/B 对比验证灵魂是否有效
5. **迭代优化** → 基于实际结果调整 prompt 和验收标准

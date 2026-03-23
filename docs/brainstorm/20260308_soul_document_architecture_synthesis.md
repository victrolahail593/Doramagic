# AllInOne 灵魂文档双层架构——全面汇总报告

**日期**: 2026-03-08
**数据源**: Gemini 业界最佳实践调研 + Codex 架构设计报告
**分析者**: Claude (Opus 4.6)

---

## 一、两份报告的定位差异

| | Gemini 报告 | Codex 报告 |
|---|---|---|
| **角色** | 横向扫描——业界怎么做的 | 纵向设计——AllInOne 应该怎么做 |
| **深度** | 6.4KB，精简概述 | 44.7KB，完整可落地规范 |
| **价值** | 提供参考系和启发 | 提供具体架构和模板 |

**结论**：两份报告互补性极强。Gemini 告诉我们"行业走到了哪"，Codex 告诉我们"AllInOne 应该走到哪"。

---

## 二、业界现状（来自 Gemini）

### 2.1 各工具的上下文管理方案

| 工具 | 规则文件 | 格式 | 核心特性 |
|------|---------|------|---------|
| **Claude Code** | CLAUDE.md | 纯 Markdown | 4 层优先级（Managed > Local > Project > User），全量加载 |
| **Cursor** | .mdc (Markdown Config) | Markdown + YAML Frontmatter | **按需加载**（globs 匹配），Auto/Manual 触发模式 |
| **GitHub Copilot** | .github/copilot-instructions.md | Markdown | 支持 `applyTo` 路径级覆盖 |
| **Windsurf** | .windsurf/rules/ | 目录化规则 | 专注 Agent 动作约束 |
| **Cline** | .clinerules | 规则文件 | 复杂任务流（Plan-Act-Validate） |
| **Aider** | CONVENTIONS.md | Markdown | 专注代码风格和 Git 规范 |
| **AGENTS.md** | AGENTS.md | 开源标准 | Claude/Cursor/Gemini CLI 均支持，"给机器人看的 README" |

### 2.2 关键启发

1. **Cursor 的 .mdc 是当前最先进的实现**——用 YAML Frontmatter + globs 实现按需加载，比 CLAUDE.md 的全量加载聪明得多
2. **AGENTS.md 正在成为行业标准**——多工具互通，AllInOne 应兼容
3. **所有工具都用 Markdown**——业界共识，不是巧合
4. **CLAUDE.md 的主要局限是静态性**——200 行建议上限，过长会"Lost in the middle"

### 2.3 Gemini 对 AllInOne 的建议

- 全局灵魂存储于 `~/.allinone/soul.global.md`
- 项目灵魂使用 `SOUL.md` 或兼容 `AGENTS.md`
- 格式使用 **Markdown + YAML Frontmatter**
- AI 在任务结束后自动总结"新灵魂碎片"，询问用户是否持久化
- 灵魂文档应是**"运行态内存"**，而非死文档

---

## 三、Codex 架构设计核心思想

### 3.1 最重要的认知突破

Codex 报告提出了一个关键洞察，超越了"多层 CLAUDE.md"的思维：

> **全局灵魂 ≠ 父文件，项目灵魂 ≠ 子文件。**
> 它们不是继承关系，而是三个平面：
> - **全局灵魂 = Control Plane（治理层）**——定义规则
> - **项目灵魂 = Knowledge Plane（知识层）**——提供知识
> - **Runtime Assembler = Execution Plane（执行层）**——按规则调度知识

这意味着全局灵魂不"包含"项目知识，而是**治理**项目知识如何被生产、装配、消费和进化。

### 3.2 十大工程原则（硬约束）

| # | 原则 | 含义 |
|---|------|------|
| 1 | Single Source of Truth | 同一知识不在多处重复维护 |
| 2 | Authoring View ≠ Runtime View | 人写的源文档 ≠ LLM 拿到的 context |
| 3 | Global Policy, Local Knowledge | 全局管"怎么做"，项目管"是什么/为什么" |
| 4 | Hot / Warm / Cold 分层 | 不是所有灵魂都应进入 prompt |
| 5 | Stable IDs Over File Paths | 每张卡片有稳定 ID，不依赖路径 |
| 6 | Versioned Contracts | schema_version + soul_version + source_version_window |
| 7 | Append-Only Evidence, Curated Summary | 证据可追加，运行时必须提炼去噪 |
| 8 | Traceability Before Cleverness | 高价值结论必须可追溯到证据 |
| 9 | Deterministic Assembly | 运行时装配基于稳定因素，非临场感觉 |
| 10 | Self-Evolution With Guardrails | 进化有门槛：观察 → 候选 → 验证 → 晋升 |

---

## 四、全局灵魂（Control Plane）设计

### 4.1 七个核心文件

| 文件 | 职责 | 变更频率 |
|------|------|---------|
| `00_identity.md` | AllInOne 是什么、不是什么、核心承诺 | 极低 |
| `10_operating_principles.md` | 平台级行为"宪法"（LLM-first、忠实优于流畅等） | 低 |
| `20_service_protocol.md` | LLM 如何为用户服务（意图分类、不确定性策略、证据策略） | 中 |
| `30_extraction_protocol.md` | 如何生产项目灵魂（输入源优先级、卡片生成规则、证据分级） | 中 |
| `40_quality_protocol.md` | 如何判断灵魂"有用"（评估维度、准入标准、降级策略） | 中 |
| `50_runtime_assembly_policy.md` | 如何编排双层灵魂给 LLM（加载优先级、冲突裁决、token 预算） | 中高 |
| `60_evolution_protocol.md` | 全局灵魂如何自我进化（三层晋升：观察→候选→正式） | 低 |
| `70_glossary_and_taxonomy.md` | 统一术语，减少 prompt 漂移 | 低 |

### 4.2 统一格式

所有全局文件使用 **Markdown + YAML Frontmatter**：

```yaml
id: G-SERVICE-001
layer: global
type: service_protocol
schema_version: 1
soul_version: 1.2.0
status: active
owner: allinone-core
last_reviewed: 2026-03-08
```

### 4.3 自我进化机制（三段式）

```
观察层（observations/）→ 候选规则层（candidates/）→ 正式规则层（正式文件）
```

晋升门槛：
- 至少在 3 个独立任务或 2 个项目中观察到
- 能改善质量或减少重复失败
- 与现有高优先级规则无冲突

**收益**：避免 CLAUDE.md 式经验碎片无限叠加，保留演化轨迹，支持 rollback。

---

## 五、项目灵魂（Knowledge Plane）设计

### 5.1 三层模型

```
第一层：项目总纲（Manifest）—— 入口文件，极短（1-2k tokens）
  ↓
第二层：知识卡片（C1 Cards）—— 主数据，5 种卡片类型
  ↓
第三层：证据与演化（Evidence/Evolution）—— 可追溯、可追加
```

### 5.2 五种知识卡片

| 卡片类型 | 用途 | 适合场景 |
|---------|------|---------|
| `concept_card` | 核心概念、心智模型、术语边界 | explain、onboarding、compare |
| `workflow_card` | 系统流程、用户旅程、调试路径 | how-to、debug、onboarding |
| `decision_rule_card` | 条件判断、路由规则、anti-pattern | **对 LLM 最有价值**——踩坑经验变可执行规则 |
| `contract_card` | 输入输出契约、不变量、状态机约束 | 高风险场景优先，显著降低幻觉 |
| `architecture_card` | 模块边界、依赖关系、数据流、trade-off | 架构评审、深度解释 |

### 5.3 代码半魂 vs 社区半魂

**关键设计决策**：不按"代码/社区"建两套独立文档，而是**共享同一套卡片模型**，用元数据字段区分来源：

```yaml
# 代码半魂卡片
origin_domain: code
confidence: high
evidence_level: E1  # 源码/测试/官方文档

# 社区半魂卡片
origin_domain: community
confidence: medium
evidence_level: E2  # maintainer issue/PR
freshness: version_bound
applies_to: [">=2.1.0 <2.4.0"]
```

**好处**：
- 运行时按"知识类型"和"证据强弱"选择，而非按目录名
- 社区经验默认不进入 hot zone
- 代码事实与社区冲突时，运行时有明确裁决规则

### 5.4 版本管理（三层）

| 版本类型 | 管什么 | 示例 |
|---------|-------|------|
| `schema_version` | 卡片结构契约 | frontmatter 字段变化时递增 |
| `soul_version` | 灵魂内容版本 | 1.4.0（major/minor/patch 语义） |
| `source_version_window` | 适用于上游哪些版本 | `">=2.0.0 <2.5.0"` |

**加上卡片级 `card_version`**——因为项目总版本变化时不是所有卡片同步变化。

### 5.5 卡片关系模型（轻量级）

```yaml
relates_to: [P-whisperx-CONCEPT-001]
depends_on: [P-whisperx-CONTRACT-003]
explains: [submission-flow]
supersedes: [P-whisperx-WORKFLOW-001]
```

目标不是做图数据库，而是提升装配精准度和控制 token 扩散。为未来图谱化预留接口。

---

## 六、双层关联机制

### 6.1 三条数据流

| 流 | 方向 | 内容 |
|----|------|------|
| **生成流** | 全局 → 项目 | 全局 extraction protocol 指导项目灵魂生产 |
| **服务流** | 用户 → 全局 → 项目 → 回答 | 全局 service protocol 分类任务，runtime 加载项目灵魂切片 |
| **演化流** | 项目 → 全局 | 项目观察 → 候选全局规则 → 验证后晋升 |

### 6.2 全局如何治理项目灵魂生成

全局提供统一的：
- 卡片类型定义和 frontmatter 规范
- 证据分级（E1-E4）和置信度分级
- 抽取顺序：代码真相层 → 官方解释层 → 社区经验层
- 入魂标准（什么该入、什么不该入）
- 最小合格覆盖（1 个 manifest + 核心 cards + risk zones + blind spots）

### 6.3 全局如何指导 LLM 服务用户

1. **先分类**：用 service protocol 分类用户意图（explain/debug/compare/onboarding/migration...）
2. **再装配**：按任务类型选择卡片簇
3. **定裁决**：冲突时按固定优先级裁决（safety > global policy > contract > decision rule > community heuristics）
4. **管回答**：要求声明知识来源、置信度、盲区、不确定性

### 6.4 项目经验如何反馈全局

```
项目层观察 → 抽象为候选规则 → 跨项目验证 → 正式晋升 → 反向发布到新项目
```

适合晋升：Manifest 必须极短、社区经验不应默认进 hot zone
不适合晋升：某个项目的特定插件坑、某个 maintainer 的个人偏好

---

## 七、运行时动态组装策略

### 7.1 五层 Context 结构

| 层 | 内容 | 特点 |
|----|------|------|
| 1. Global Core | identity + service protocol + runtime policy 摘要 | 极短、高稳定、几乎每次加载 |
| 2. Project Spine | manifest + blind spots + load profile | 项目心智模型、版本边界、盲区 |
| 3. Task Cards | 按任务类型选择的卡片簇 | **主要知识负载区** |
| 4. Evidence Tail | 高风险时才加载的深度证据 | 默认不加载 |
| 5. Session Overlay | 当前会话上下文摘要 | 不污染正式 soul |

### 7.2 按任务类型选卡片

| 任务类型 | 加载卡片 |
|---------|---------|
| explain | concept + architecture |
| onboarding | concept + workflow |
| debug | contract + workflow + decision rules |
| compare | concept + architecture + community pitfalls |
| migration | compatibility + version-bound decision rules + community pitfalls |
| architecture_review | architecture + contract + trade-off rules |

### 7.3 Token 预算分配

| 请求规模 | 总预算 | Global Core | Project Spine | Task Cards | Evidence | 回答空间 |
|---------|--------|------------|---------------|------------|----------|---------|
| 小型（explain/onboarding） | 8k-12k | 10% | 15% | 55% | 0% | 20% |
| 中型（debug/compare） | 15k-30k | 8% | 12% | 55% | 10% | 15% |
| 大型（架构评审/迁移） | 30k-80k | 5% | 10% | 50% | 20% | 15% |

**硬约束**：
- Global Core 不超过总预算 10%
- Manifest + blind spots 不超过 15%
- 至少保留 15% 给模型输出

### 7.4 裁剪优先级（超预算时）

1. 去掉 cold evidence
2. 去掉低置信 community cards
3. 将 architecture cards 压缩为 summary
4. 将 workflow cards 压缩为 decision steps
5. **最后保留**：contract cards + critical decision rules + manifest + blind spots

**原因**：少了 evidence 回答通常还能成立；少了 contract 回答很容易错；少了 blind spots 回答很容易假装完整。

### 7.5 Hot / Warm / Cold 判定因素

| 因素 | Hot | Warm | Cold |
|------|-----|------|------|
| 任务命中频率 | 高 | 中 | 低 |
| 错误代价 | 高 | 中 | 低 |
| 内容稳定性 | 稳定 | 较稳定 | 可能过期 |
| 证据等级 | E1-E2 | E2-E3 | E3-E4 |
| 对多数回答有帮助 | 是 | 有条件 | 少数情况 |

---

## 八、具体文件结构

```
allinone/
  soul/
    global/                          # 全局灵魂（治理层）
      00_identity.md
      10_operating_principles.md
      20_service_protocol.md
      30_extraction_protocol.md
      40_quality_protocol.md
      50_runtime_assembly_policy.md
      60_evolution_protocol.md
      70_glossary_and_taxonomy.md
      evolution/
        observations/                # 观察记录
        candidates/                  # 候选规则
        archive/                     # 已处理的记录

    projects/                        # 项目灵魂（知识层）
      <project-id>/
        project_soul.md              # 项目总纲（Manifest）
        manifest/
          module_map.md              # 模块边界与加载关系
          load_profile.md            # Hot/Warm/Cold 建议
          blind_spots.md             # 已知盲区
        cards/
          code/                      # 代码半魂卡片
            concept/
            workflow/
            decision_rule/
            contract/
            architecture/
          community/                 # 社区半魂卡片
            concept/
            workflow/
            decision_rule/
            contract/
            architecture/
        evidence/                    # 证据追溯
          code_refs/
          issues/
          prs/
          discussions/
          release_notes/
          external_notes/
        evolution/                   # 项目级演化
          observations/
          candidates/
          archive/
        versions/
          changelog.md               # 灵魂自身变更记录
          compatibility_matrix.md    # 版本覆盖矩阵

    runtime/                         # 运行时装配（执行层）
      profiles/
        explain.yaml
        onboarding.yaml
        debug.yaml
        architecture_review.yaml
        compare.yaml
        migration.yaml
      compilers/
        assembly_rules.md            # 装配规则
      cache/

    schemas/                         # 结构约束
      global_frontmatter.schema.yaml
      project_frontmatter.schema.yaml
      card_frontmatter.schema.yaml
      runtime_profile.schema.yaml
```

---

## 九、业界最佳实践 vs Codex 设计的对比

### 9.1 AllInOne 超越业界的地方

| 维度 | 业界现状 | AllInOne 设计 |
|------|---------|-------------|
| 文档类型 | 规则文件（告诉 AI 怎么写代码） | **知识系统**（装载项目灵魂服务用户） |
| 加载方式 | 全量加载（CLAUDE.md）或路径匹配（Cursor） | **任务分类 → 动态装配 → token 预算控制** |
| 知识来源 | 人工编写 | **自动提取（代码+社区）+ 人工审核** |
| 进化机制 | 无（手动编辑） | **三段式晋升（观察→候选→验证→正式）** |
| 质量验证 | 无 | **A/B 评估（有魂 vs 无魂）** |
| 多项目支持 | 每项目独立规则文件 | **统一卡片模型 + 治理层 + 跨项目经验晋升** |

### 9.2 AllInOne 应借鉴业界的地方

| 来源 | 借鉴点 | 如何应用 |
|------|-------|---------|
| Cursor .mdc | YAML Frontmatter + 按需加载 | 卡片使用 YAML Frontmatter，runtime 按任务匹配 |
| AGENTS.md 标准 | 行业互通格式 | AllInOne 的项目灵魂兼容 AGENTS.md |
| CLAUDE.md | 纯 Markdown 对 LLM 最友好 | 主体格式用 Markdown，不用 JSON |
| Cursor | globs 路径匹配触发 | 卡片的 `relates_to` 字段实现类似功能 |

---

## 十、Gemini 与 Codex 的分歧点

### 分歧 1：全局灵魂的复杂度

| | Gemini | Codex |
|---|---|---|
| **方案** | 单文件 `~/.allinone/soul.global.md` | 7 个文件 + evolution 目录 |
| **逻辑** | 简单即美，参考 CLAUDE.md | 治理层需要结构化，单文件会膨胀 |

**我的判断**：Codex 的方案更合理。全局灵魂包含 identity、service protocol、extraction protocol、quality protocol、runtime policy、evolution protocol 六个不同职责，塞进一个文件会变成"CLAUDE.md 的问题放大版"。但 **v1 可以先从 2-3 个核心文件开始**（identity + service protocol + runtime policy），逐步扩展。

### 分歧 2：项目灵魂的命名

| | Gemini | Codex |
|---|---|---|
| **方案** | `SOUL.md` 或兼容 `AGENTS.md` | `project_soul.md` + 卡片目录 |

**我的判断**：对外展示可以兼容 AGENTS.md 标准（行业互通），内部存储用 Codex 的卡片体系（结构化、可装配）。

### 分歧 3：动态触发机制

| | Gemini | Codex |
|---|---|---|
| **方案** | 借鉴 Cursor 的 globs 按路径触发 | 按任务类型分类 + 卡片关系图 |

**我的判断**：AllInOne 不是 IDE 工具，没有"当前文件路径"概念。Codex 的任务分类方案更适合 AllInOne 的用户服务场景。

---

## 十一、质量验证方案

### 11.1 核心标准

> **加载灵魂后的 LLM，是否比未加载灵魂时更好地服务用户。**

### 11.2 A/B 评估方法

- **A 组**：无灵魂 context 的 LLM 回答
- **B 组**：加载双层灵魂 context 的 LLM 回答

比较指标：
1. 用户任务完成率
2. 错误率
3. 误导性建议率
4. 追问次数
5. 是否显式声明不确定性

### 11.3 治理闭环

```
新项目 soul → draft → 通过最小覆盖检查 → active → 运行时监控 → 失败进 observation → 验证后更新
```

---

## 十二、v1 落地路线

### 12.1 最小可落地实现

1. 建立 `global/` 核心文件（先做 identity + service protocol + runtime policy 三个）
2. 为 **一个真实项目**（建议 WhisperX）建立 `project_soul.md` + C1 知识卡片
3. 建立 `runtime/profiles/*.yaml`（先做 explain + debug 两个）
4. 实现最小装配器：按任务类型拼 context
5. 跑 A/B 评估：有魂 vs 无魂

### 12.2 v1 不做的事

- 不上图数据库
- 不自动大规模抓社区
- 不允许模型自动改写正式全局规则
- 不把所有历史记录纳入灵魂

### 12.3 v1 成功标准

1. 至少一个真实项目的灵魂能稳定服务多个用户任务
2. 有魂回答**显著优于**无魂回答
3. 灵魂文档多轮维护后仍保持清晰结构
4. runtime 在受限 token 预算下稳定工作

---

## 十三、与之前六方调研的衔接

| 之前的结论 | 本次设计如何落实 |
|-----------|---------------|
| C1 的知识卡片体系 | 作为项目灵魂的 canonical knowledge unit（五种卡片） |
| G2 的知识胶囊格式 | 融入卡片的 YAML Frontmatter（origin_sources、confidence、evidence_level） |
| 社区半魂是核心护城河 | 共享卡片模型，用 origin_domain 区分，默认不进 hot zone |
| 管道解耦、碎片可用 | 三层模型（manifest + cards + evidence），每层独立可用 |
| Repomix + LLM 提取 | 全局 extraction_protocol 定义提取流程 |
| Hot/Cold Memory 架构 | 扩展为 Hot/Warm/Cold 三层，有明确判定因素和 token 预算 |
| 技术栈用户可选 | 卡片和灵魂不绑定任何 LLM/向量 DB，纯 Markdown + YAML |
| 质量验证 | A/B 评估 + 治理闭环 + 晋升门槛 |

---

## 十四、下一步行动

1. **讨论并确认本设计方案**——这是产品的骨架，需要 Tangsir 拍板
2. **选择验证项目**——建议用 WhisperX 作为第一个项目灵魂
3. **编写全局灵魂核心文件**——先做 3 个（identity + service protocol + runtime policy）
4. **走完一次提取流程**——Repomix → LLM 鹰眼+深潜 → 生成知识卡片
5. **A/B 验证**——同一问题，有魂 vs 无魂，对比回答质量

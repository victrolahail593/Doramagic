# Doramagic 产品设计调整方案

本文针对当前 [docs/doramagic-product-dev-brief.md](./doramagic-product-dev-brief.md) 的 6 个结构性缺陷，给出一份可直接指导四路选手后续开发的统一调整方案。核心结论只有三条：

1. Doramagic 的最终产品形态不是 `python doramagic.py`，而是一个在 OpenClaw 上通过 `/dora` 触发的 Skill。
2. Doramagic 不应绑死任何特定 LLM SDK。AI 自身负责理解、分析、提炼、叙事；`exec` 脚本负责确定性 I/O、抓取、验证、组装。
3. 真正的验收环境不是本机命令行，而是 Mac mini `192.168.1.104` 上的真实 OpenClaw 运行环境；四路选手必须按命名空间隔离并行测试。

## 1. 产品形态调整

### 1.1 从 CLI 到 OpenClaw Skill

当前 Brief 把 Doramagic 定义成一个本地 Python CLI 工具，这与产品真实使用方式不一致。根据开发手册和上下文简报，Doramagic 的系统 A 本质上是一个 OpenClaw Skill：

- 用户入口是 OpenClaw 对话中的 `/dora`，不是 shell 里的 `python doramagic.py ...`
- 产品交付物是 `SKILL.md` 驱动的 Skill 包，而不是一个“要求用户自己装 Python 依赖再运行”的命令行程序
- Python 代码仍然保留，但身份应降级为 Skill 的后台执行脚本、确定性工具库、开发测试 harness

因此需要做一个关键区分：

- 产品形态：`SKILL.md` + 相关脚本/模板/validator，运行在 OpenClaw
- 开发形态：本地 Python 包、pytest、临时 CLI harness，仅用于研发和回归

`doramagic.py` 可以继续保留，但只能作为开发者 smoke test/CI harness，不再作为产品主入口写进 Brief。

### 1.2 新的产品边界

调整后，Doramagic 的边界应明确为：

- OpenClaw Skill 层：接收用户一句话需求，驱动整个 Phase A-H，最终把 `SKILL.md + PROVENANCE.md + LIMITATIONS.md` 交付给用户
- Python/脚本层：被 Skill 通过 `exec` 调用，用于完成确定性工作
- 可选增强层：`packages/preextract_api` 和 `packages/domain_graph` 作为系统 B，仅在命中预提取领域时提供增强，不是产品可用性的前置条件

### 1.3 `SKILL.md` 应该长什么样

建议 Doramagic 的 `SKILL.md` 采用与 `skills/soul-extractor/SKILL.md` 相同的 Skill 形态，但内容改成“产品编排器”而不是“单项目灵魂提取器”。示意结构如下：

```markdown
---
name: doramagic
description: >
  Doramagic：根据用户一句话需求，从真实开源项目中提取可复用知识，
  交付一个可直接用于 OpenClaw 的 Skill 包。
version: 2.0.0
user-invocable: true
allowed-tools: [exec, read, write]
tags: [doramagic, skill-generation, openclaw, knowledge-extraction]
metadata:
  openclaw:
    category: builder
    requires:
      bins: ["python3", "bash", "curl", "unzip"]
    storage_root: "~/clawd/doramagic/${namespace}"
---

# Doramagic

当用户通过 `/dora` 描述一个想要的能力时，执行以下流程：

## 工作原则

- 先用你自己的智能理解用户需求并形成 NeedProfile
- 需要网络、下载、解压、验证、组装时，一律通过 `exec` 调用本地脚本
- 不要在产品逻辑里绑定特定厂商 SDK；你自己就是执行分析的 AI
- 关键指令写在本文件或显式读取的 `stages/*.md` 中，不依赖 `SOUL.md`
- 所有运行数据写到 `~/clawd/doramagic/${namespace}/...`

## Phase A: 需求理解
- 将用户需求整理为 NeedProfile
- 明确目标用户、核心任务、约束、搜索关键词、排除项

## Phase B: 开源项目发现
- 通过 `exec` 运行 discovery/fetch 脚本
- 使用 GitHub Search API 搜索候选项目
- 下载 zip archive，不使用 `git clone`

## Phase C: 单项目提取
- 读取 `stages/STAGE-*.md` 并按其中方法分析代码库
- 确定性 facts 由脚本提取
- WHY / UNSAID / 设计哲学 / 叙事由你直接完成

## Phase D-E: 社区与跨项目综合
- 收集社区信号
- 调用 compare/synthesis 模块生成综合结论

## Phase F-G-H: 组装、校验、交付
- 通过编译脚本组装 `SKILL.md + PROVENANCE.md + LIMITATIONS.md`
- 运行 validator
- 向用户交付最终文件，并清楚说明局限
```

### 1.4 Brief 需要同步改写的地方

当前 Brief 中所有类似以下表述都应降级为“开发/测试说明”，不再作为产品定义：

- “创建 CLI 入口 `doramagic.py`”
- “最终验证：`python3 doramagic.py '...'` 端到端跑通”
- “用户通过 Python 命令调用产品”

新的表述应改为：

- “创建/维护 `skills/doramagic/SKILL.md` 作为产品主入口”
- “如需本地调试，可保留 `doramagic.py` 作为开发 harness”
- “最终验收以 OpenClaw 中 `/dora` 真实触发结果为准”

## 2. LLM 调用架构调整

### 2.1 总原则

当前 Brief 硬编码 `import anthropic; client = anthropic.Anthropic()` 是错误的，因为它把 Doramagic 产品能力和某一家模型供应商绑定了。Doramagic 运行在 OpenClaw 上时，AI 本身已经存在；产品要做的是定义“AI 负责什么”和“脚本负责什么”，而不是在产品内部再套一层厂商 SDK。

新的原则是：

- AI 自身智能负责理解、推理、归纳、判断、叙事
- `exec` 脚本负责确定性输入输出、结构化抽取、网络抓取、验证、文件落盘
- 是否使用 Claude/GPT/Gemini/GLM/MiniMax，是平台运行时选择，不是 Doramagic 产品契约的一部分

### 2.2 AI 自身智能 vs `exec` 脚本职责边界

| 阶段 | AI 自身智能负责 | `exec` 脚本负责 |
|------|----------------|----------------|
| Phase A 需求理解 | 将用户话术整理为 NeedProfile、识别真正任务、补足隐含约束、生成搜索策略 | 可选地把 NeedProfile 序列化为 JSON artifact |
| Phase B 项目发现 | 判断哪些项目真的 relevant、哪些只是表面相似、何时停止继续搜索 | 调 GitHub Search API、下载 zip、解压、生成 repo 清单和基本 metadata |
| Phase C 单项目提取 | 阅读代码、识别 WHY/UNSAID、抽取设计哲学、判断哪些模式是“灵魂”而非表层实现 | repo facts、文件树、依赖、入口点、统计信息、固定格式中间产物 |
| Phase D 社区采集 | 判断 issue/discussion 中哪些是高价值经验、哪些只是偶发噪声 | 拉取 issue/discussion/PR/comment/changelog 等原始材料 |
| Phase E 跨项目综合 | 解释项目之间的共识、争议、边界、可迁移规则，并产出最终 narrative | 运行 `compare.py` / `synthesis.py` 等结构化综合模块 |
| Phase F 交付物组装 | 决定最终表达重点、写清 trade-off、限制和适用条件 | 运行 compiler，把数据组装成 `SKILL.md` / `PROVENANCE.md` / `LIMITATIONS.md` |
| Phase G 验证 | 根据 validator 报告判断是修补、重试还是 blocked | 运行 `platform_openclaw.validator` 并输出结构化错误 |
| Phase H 交付 | 面向用户解释结果和风险 | 把最终文件写入 namespaced run 目录 |

### 2.3 对 Soul Extractor Prompt 的正确使用方式

`skills/soul-extractor/stages/STAGE-*.md` 是高价值的提取方法论资产，但它们的正确角色不是“喂给 Anthropic SDK 的外部 prompt”，而是：

- 作为 Doramagic Skill 在 Phase C 中显式读取的分析协议
- 作为 AI 的工作 rubric，指导 AI 如何阅读项目、如何提取 WHY、如何从素材合成叙事
- 作为研发资产继续演进，但不把具体厂商 SDK 写死进产品结构

换句话说，Prompt 资产保留，调用方式改变。

### 2.4 明确禁止事项

调整后的产品架构中应明确禁止以下做法：

- 在系统 A 的主路径中硬编码 Anthropic/Gemini/OpenAI/GLM 任一 SDK
- 把“知识提取”实现成“再调一次外部大模型 API”
- 让 Skill 依赖某个模型品牌名才能工作
- 把 Prompt 资产埋在 `SOUL.md` 等不可靠自动加载路径中

如果未来确实需要某个外部模型 API，那也应属于系统 B 或离线批处理工具，不属于 OpenClaw Skill 的核心产品契约。

## 3. 已有资产复用方案

调整后的原则不是推翻现有资产，而是重新定义它们在 Skill 架构中的角色。

### 3.1 `skills/soul-extractor/` 的新角色

`skills/soul-extractor/` 不再被视为“另一个独立产品”，而应被视为 Doramagic 的上游提取引擎资产库：

- `SKILL.md`：提供 Skill 形态和阶段化编排写法的参考模板
- `stages/STAGE-*.md`：作为 Phase C 的分析协议，直接复用其提问框架、审查节奏和输出 rubrics
- `scripts/prepare-repo.sh`：保留为 repo 下载/预处理 helper 的参考实现
- `scripts/assemble-output.sh`：其思路可迁移到 Doramagic 的最终交付物组装脚本

调整重点不是重写这些资产，而是把它们从“Claude 专用提取流水线”改造成“OpenClaw Skill 可调用的方法论+脚本库”。

### 3.2 `packages/` 模块的复用定位

| 资产 | 新架构中的角色 |
|------|----------------|
| `packages/contracts/` | 唯一可信的数据契约层。NeedProfile、Extraction、CrossProject、SkillBundle、Envelope 等都继续从这里定义 |
| `packages/extraction/` | 单项目提取的确定性/半确定性引擎。`stage0.py`、`stage1_scan.py`、`stage15_agentic.py` 继续复用，但其触发者从 CLI 改成 Skill + `exec` |
| `packages/cross_project/doramagic_cross_project/compare.py` | Phase E 的结构化比较引擎，继续作为“共识/分歧/缺失”判定器 |
| `packages/cross_project/doramagic_cross_project/synthesis.py` | Phase E 的综合引擎，继续生成跨项目 synthesis；AI 在其输出之上做最后叙事锻造 |
| `packages/skill_compiler/doramagic_skill_compiler/compiler.py` | Phase F 的确定性交付物编译器，用于把 synthesis 结果落成 `SKILL.md + PROVENANCE.md + LIMITATIONS.md` |
| `packages/platform_openclaw/doramagic_platform_openclaw/validator.py` | Phase G 的静态校验门，保留为最终放行/修订/阻断机制 |
| `packages/orchestration/doramagic_orchestration/phase_runner.py` | 从“最终产品入口”降级为内部编排 helper、本地 harness、测试驱动器 |
| `packages/community/` | 作为 Phase D 社区采集脚本的归宿地继续补齐，避免逻辑散落在 Skill 目录 |
| `packages/domain_graph/` | 系统 B 的图谱构建与快照生成能力，只作为增强层，不再强绑到每次实时生成流程 |
| `packages/preextract_api/` | 系统 B 的 API 服务。命中预提取领域时注入知识，未命中时 Doramagic 仍必须能工作 |
| `packages/doramagic_product/` 与根 `doramagic.py` | 保留为本地演示/回归 harness，不再代表最终产品形态 |

### 3.3 对首批预提取领域的影响

`docs/dev-context-briefing.md` 已明确首批预提取领域不包含“食谱/膳食”。这意味着：

- Doramagic 不能把系统 B 当成所有需求的必经之路
- 对于未覆盖领域，必须直接走“GitHub 搜索 -> zip 下载 -> 单项目提取 -> 跨项目综合”的主流程
- 命中预提取领域时，再把 `packages/preextract_api` / `packages/domain_graph` 作为加速器和质量增强器

### 3.4 对当前代码的重定义

对现有代码应采用“保留实现、修正定位”的策略：

- 不要求把已有 Python 管线全部删掉
- 要求把“谁是主入口、谁是后台 helper、谁是增强服务”重新标定清楚
- 所有面向用户的话术、文档、验收标准都改成 Skill-first

## 4. 测试环境方案

### 4.1 环境职责重新划分

测试环境必须分成两层：

- 本机：单元测试、模块测试、fixture 回归、bundle 预编译、validator dry-run
- Mac mini `192.168.1.104`：真实 OpenClaw 集成测试与最终验收

本机命令行只能回答“代码大体没坏”，不能回答“OpenClaw 用户真的能用”。因此后者必须上 Mac mini 做。

### 4.2 标准部署与测试流程

建议把 Doramagic 的真实测试流程统一为下面 7 步：

1. 在本机完成模块开发，并跑相关 `pytest`
2. 在本机生成/更新 namespaced Skill bundle
3. 将该选手的代码与 Skill 资源同步到 Mac mini 的隔离目录
4. 在 Mac mini 上注册或更新该 namespaced Skill
5. 在真实 OpenClaw 会话中用对应触发词执行 smoke case
6. 检查 `~/clawd/...` 下的 run artifacts、validator 报告和交付文件
7. 记录测试结果、失败原因和修订建议

### 4.3 Mac mini 上必须覆盖的场景

至少覆盖以下 4 类真实场景：

- 正常流：开源项目丰富、搜索结果明确、生成成功
- 稀疏流：候选项目不多，系统应触发降级或扩大搜索
- 非预提取领域：例如食谱类需求，应证明系统 B 缺席时产品仍可工作
- 校验失败流：validator 返回 `REVISE` 或 `BLOCKED` 时，Skill 能正确解释问题而不是静默失败

### 4.4 验收标准

Mac mini 上的验收不应再写成“CLI 跑通”，而应写成：

- 在 OpenClaw 中通过 `/dora` 或对应 namespaced trigger 成功触发
- 运行过程中仅使用平台允许的 `exec/read/write`
- 结果落盘到 `~/clawd/` 约定目录
- 最终产出 `SKILL.md + PROVENANCE.md + LIMITATIONS.md`
- validator 给出 `PASS` 或合理的 `REVISE/BLOCKED` 解释

## 5. 多选手隔离方案

四路选手必须能在同一台 Mac mini 上并行测试，且互不覆盖。隔离的关键不是只改一个目录名，而是把“代码、Skill 标识、运行数据、环境、临时文件、可选服务”全部 namespaced。

### 5.1 隔离命名空间

建议固定使用以下命名空间：

- `s1-sonnet`
- `s2-codex`
- `s3-gemini`
- `s4-glm5`

所有路径、Skill key、触发词、日志目录都从这个 namespace 派生。

### 5.2 需要隔离的对象

| 对象 | 隔离方案 |
|------|----------|
| 代码目录 | `~/Doramagic-racers/<namespace>/repo/` |
| Python 虚拟环境 | `~/Doramagic-racers/<namespace>/.venv/` |
| Skill bundle 目录 | `~/Doramagic-racers/<namespace>/skill/` 或 `~/clawd/skills/<namespace>/` |
| Skill key / 注册名 | `doramagic-<namespace>` |
| 用户触发词 | `/dora-s1`、`/dora-s2`、`/dora-s3`、`/dora-s4`；赛马结束后再收敛回 `/dora` |
| 运行数据根目录 | `~/clawd/doramagic/<namespace>/` |
| 运行时子目录 | `runs/`、`cache/`、`logs/`、`tmp/`、`artifacts/` 全部放在各自 namespace 下 |
| 环境变量文件 | `~/Doramagic-racers/<namespace>/.env` |
| 可选 wheel/package 名 | 若必须安装 wheel，distribution name 加后缀，如 `doramagic-s2-codex`；更推荐直接用各自 venv 运行，避免全局同名安装 |
| 可选 API/后台服务端口 | 如需并行起服务，给每个 namespace 独立端口或独立 service name |

### 5.3 推荐目录布局

推荐在 Mac mini 上采用统一布局：

```text
~/Doramagic-racers/
  s1-sonnet/
    repo/
    .venv/
    skill/
    logs/
  s2-codex/
    repo/
    .venv/
    skill/
    logs/
  s3-gemini/
    repo/
    .venv/
    skill/
    logs/
  s4-glm5/
    repo/
    .venv/
    skill/
    logs/

~/clawd/doramagic/
  s1-sonnet/{runs,cache,tmp,artifacts}
  s2-codex/{runs,cache,tmp,artifacts}
  s3-gemini/{runs,cache,tmp,artifacts}
  s4-glm5/{runs,cache,tmp,artifacts}
```

### 5.4 允许共享与禁止共享

可以共享的只有只读资产：

- 仓库中的 `packages/contracts/`
- 固定 fixtures
- 平台规则文档
- 只读的研究材料

禁止共享的包括：

- 同一个 `~/clawd/doramagic/` 裸目录
- 同一个触发词 `/dora`
- 同一个全局 Python 环境
- 同一个临时目录/缓存目录
- 同一个“默认输出文件名”但未带 namespace 的产物目录

### 5.5 并行测试时的操作规则

- 每位选手只能修改自己的 Mac mini 工作目录和 namespace 数据目录
- 任何会写共享位置的脚本都必须先改成 namespaced 路径
- 任何本来想安装成全局同名包的做法都必须取消或加后缀
- 任何文档里的示例命令都要显式带 namespace，直到赛马结束

## 6. 对四路选手的修正指令

### 6.1 对全体选手的统一修正

四路选手从现在起都应遵守以下统一指令：

1. 停止把 `python doramagic.py` 当作最终产品定义
2. 以 OpenClaw Skill 作为唯一产品形态，`SKILL.md` 为主入口
3. 停止在系统 A 主路径中硬编码任何特定 LLM SDK
4. 按“AI 负责智能、`exec` 负责确定性操作”的边界重构
5. 所有真实验收迁移到 Mac mini OpenClaw，且必须做 namespace 隔离

### 6.2 S1-Sonnet

S1 的重点应放在：

- 把产品主入口收敛到 `SKILL.md`，补齐 Skill 级指令设计
- 优先打磨 Prompt 资产如何在 OpenClaw 内部被显式读取和执行
- 配合 `skill_compiler`，把最终交付物编译成真正可装载的 Skill bundle

S1 不应再把核心价值放在“本机 CLI 操作体验”上。

### 6.3 S2-Codex

S2 当前已经有较完整的 Python 管线，因此修正重点是“降级 CLI 身份、升级 Skill 身份”：

- 保留现有 Python 编排和测试资产，但把它们重新定位为 helper/harness
- 移除或撤销所有把 Anthropic SDK 当作核心依赖的产品设计假设
- 把 `doramagic.py` 从产品入口降级为开发 smoke runner
- 把输出路径、缓存路径、日志路径改成严格 namespaced
- 补齐面向 OpenClaw 的 Skill 入口与 Mac mini 部署测试脚本

### 6.4 S3-Gemini

S3 的重点应放在模型无关化和发现/综合质量：

- 把 discovery、compare、synthesis 等能力放到 Skill-first 架构下重新挂载
- 明确哪些推理由 AI 直接完成，哪些结果要落到确定性模块
- 所有测试都增加 OpenClaw 真实触发验证，不只做本机推理链演示
- 适配 namespaced 触发词和存储路径

### 6.5 S4-GLM5

S4 由于直接位于 Mac mini 环境，重点应放在“真实部署与隔离基建”：

- 负责产出可重复的 Mac mini 部署/更新脚本
- 建立四个 namespace 的目录、日志、运行数据和触发词隔离模板
- 为真实 OpenClaw 测试提供标准 smoke case 和验收记录模板
- 若并行起系统 B 服务，确保服务名、端口、缓存目录也按 namespace 隔离

### 6.6 PM/评审层的最终判断标准

后续评审四路选手时，不再以“谁的 CLI 跑通了”作为优先标准，而应看以下四件事：

- 谁最清楚地把产品形态落成了 OpenClaw Skill
- 谁把 AI 与 `exec` 的职责边界定义得最稳
- 谁复用了最多现有资产且没有破坏 contracts/validator
- 谁在 Mac mini 的真实隔离环境中验证得最完整

---

一句话总结：Doramagic 不是“一个会调 Anthropic 的 Python CLI”，而是“一个运行在 OpenClaw 上、以 AI 自身智能为核心、以确定性脚本为支撑、可在 Mac mini 真实环境中验证交付的 Skill 产品”。

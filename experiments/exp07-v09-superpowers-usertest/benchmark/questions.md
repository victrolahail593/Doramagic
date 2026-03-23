# Soul Extractor v0.9 Benchmark: obra/superpowers

**目标仓库**: obra/superpowers v4.3.1
**题目数**: 10
**评分**: 每题 0-3 分（事实正确性 0-1 + 关键覆盖 0-1 + 无幻觉 0-1），总分 30

---

## 设计理解 (3 题)

### Q1: 为什么 Superpowers 强制 TDD 而不是可选？

**类型**: 设计理解
**问题**: Superpowers 框架为什么把 TDD（测试驱动开发）设计为 Iron Law（不可违反的铁律），而不是可选的最佳实践？背后的设计理由是什么？

**标准答案要点**:
- KP1: 因为 AI agent 容易"作弊"——先写代码再补测试，导致测试只验证"代码做了什么"而非"代码应该做什么"，丧失了测试的保护作用
- KP2: 先写测试迫使 AI 承认自己的无知（不知道正确行为是什么），打破 AI 自信幻觉
- KP3: tests-after 会立即通过（因为是根据已有代码写的），这证明不了任何东西；tests-first 会先失败（RED），证明测试有检测力

**反面要点**:
- AP1: 说 TDD 是为了"代码质量"或"减少 bug"（太泛，没抓住 AI 特有的原因）
- AP2: 说有例外情况可以跳过 TDD（Superpowers 明确规定无例外，除非是 throwaway prototype/config）

---

### Q2: Superpowers 的 skill 架构为什么选择按触发条件组合，而不是固定线性流程？

**类型**: 设计理解
**问题**: Superpowers 有 14 个 skill，它们不是按固定顺序执行的线性 pipeline，而是根据触发条件动态激活。为什么这样设计？

**标准答案要点**:
- KP1: 软件开发不是线性的——你可能在实现中途需要回去 brainstorming，或在 debugging 中发现需要新设计
- KP2: Skill 是可组合的模块——brainstorming → writing-plans → (subagent-driven OR executing-plans) → finishing，形成有向无环图而非线性链
- KP3: 每个 skill 有明确的触发条件（"Use when..."），AI agent 根据当前上下文判断激活哪个

**反面要点**:
- AP1: 说 skills 会自动激活或被系统自动调用（不会，需要 agent 显式通过 Skill tool 调用）
- AP2: 编造不存在的 skill 名称

---

### Q3: 为什么 Superpowers 的代码审查是双阶段的（spec compliance + code quality）？

**类型**: 设计理解
**问题**: 在 subagent-driven development 中，Superpowers 要求每个 task 完成后做两轮审查：先 spec compliance review，再 code quality review。为什么要分两阶段？一次审查不行吗？

**标准答案要点**:
- KP1: 因为 spec compliance（是否建了正确的东西）和 code quality（是否建得好）是正交维度——代码可以写得很优雅但不符合需求，也可以完全符合需求但写得很差
- KP2: 顺序必须是 spec 先、quality 后——如果代码不符合需求，评审代码质量没有意义（"代码干净但是错的"）
- KP3: 每轮审查有 review loop——发现问题 → 修复 → 重新审查，直到通过。不是一次性的

**反面要点**:
- AP1: 说顺序可以颠倒（不可以，spec 必须先于 quality）
- AP2: 说自审（self-review）可以替代正式审查（不能，两者都要做）

---

## 正确使用 (3 题)

### Q4: 我想用 Superpowers 开发一个新功能，从零到完成的完整流程是什么？

**类型**: 正确使用
**问题**: 假设我已经安装了 Superpowers，我想给我的项目加一个"用户认证"功能。从提出需求到代码合并，Superpowers 规定的完整流程是什么？列出每一步和对应的 skill。

**标准答案要点**:
- KP1: 第一步是 brainstorming（探索需求、问澄清问题、提出 2-3 种方案、获得设计批准、写设计文档）—— 在设计批准前不能写任何实现代码
- KP2: 第二步是 writing-plans（写实现计划，每步 2-5 分钟粒度，含具体文件路径和代码片段）
- KP3: 第三步是执行（选择 subagent-driven-development 或 executing-plans），执行过程中用 TDD（先写失败测试，再写实现），每个 task 后做双阶段审查
- KP4: 最后用 finishing-a-development-branch 完成（验证测试、选择合并方式、清理 worktree）

**反面要点**:
- AP1: 跳过 brainstorming 直接开始写代码或写计划
- AP2: 把 TDD 说成可选的
- AP3: 遗漏 worktree 隔离（executing-plans 和 subagent-driven 都要求先建 worktree）

---

### Q5: 我在用 Superpowers 的 brainstorming skill，它要求我"一次只问一个问题"，为什么？如果我的设计很简单，可以跳过 brainstorming 吗？

**类型**: 正确使用
**问题**: Brainstorming skill 的流程中规定"一次只问一个问题"，不能一条消息问多个问题。为什么这样限制？另外，如果我的需求非常简单（比如改一个配置值），可以跳过 brainstorming 吗？

**标准答案要点**:
- KP1: 一次问一个问题是为了不让用户被多个问题压倒，能够充分思考每个问题。尽可能用选择题而非开放题
- KP2: 不能跳过 brainstorming。这是 Hard Gate。Brainstorming 明确列出了 anti-pattern "This is too simple to need a design"，无论多简单都要走设计流程
- KP3: 对于真正简单的项目，设计可以很短（几句话），但必须呈现给用户并获得批准

**反面要点**:
- AP1: 说简单任务可以跳过 brainstorming
- AP2: 说可以一次问多个问题只要它们相关

---

### Q6: 我在用 Superpowers 写实现计划，怎样才算"粒度足够细"？

**类型**: 正确使用
**问题**: Writing-plans skill 要求计划任务是"bite-sized"的。什么叫 bite-sized？给我一个好的和差的例子对比。

**标准答案要点**:
- KP1: 每步 2-5 分钟，只做一个动作。"写测试"和"运行测试"是两个独立的步骤，不能合并
- KP2: 必须包含：确切的文件路径、完整的代码片段（不是"添加验证逻辑"这种模糊描述）、确切的运行命令和预期输出
- KP3: 差的例子："实现用户认证模块"（太大，不具体）。好的例子分为多个步骤：Step 1 写失败测试 → Step 2 运行确认失败 → Step 3 写最小实现 → Step 4 运行确认通过 → Step 5 commit

**反面要点**:
- AP1: 说 15-30 分钟的步骤也算 bite-sized
- AP2: 说代码片段可以省略或用伪代码代替

---

## 避坑判断 (2 题)

### Q7: 我装了 Superpowers 但发现 AI 完全不遵守任何 skill 规则，直接开始写代码。怎么排查？

**类型**: 避坑判断
**问题**: 我安装了 Superpowers，但在对话中发现 AI agent 完全忽略了 skills——不做 brainstorming，不做 TDD，直接写代码。可能是什么问题？怎么解决？

**标准答案要点**:
- KP1: 最可能的原因是 using-superpowers skill 没有正确加载。它是所有其他 skill 生效的基础，建立了"1% Rule"（即使 1% 可能相关也必须调用 skill）
- KP2: 检查安装：确认 marketplace 配置正确（先 `marketplace add`，再 `plugin install`），确认 SessionStart hook 正常触发（v4.3.0 改为同步加载）
- KP3: AI agent 有 12 种常见的合理化借口来跳过 skill（"太简单了"、"我先了解一下上下文"、"这不算一个任务"等），using-superpowers 的 Red Flags 表格专门列出了这些

**反面要点**:
- AP1: 建议修改 AI 的 system prompt（Superpowers 不修改 system prompt，通过 skill 机制注入）
- AP2: 说需要手动每次提醒 AI 使用 skills（应该通过 hook 自动加载）

---

### Q8: 我在 debugging 一个问题，试了几个修复方法都没用，然后 AI 说"这个问题可能是 X 导致的"就开始改代码了。这样对吗？

**类型**: 避坑判断
**问题**: 在 Superpowers 的 systematic-debugging 框架下，上述 AI 行为有什么问题？正确的做法是什么？

**标准答案要点**:
- KP1: 违反了 systematic-debugging 的 Iron Law："NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST"。"可能是 X"是猜测，不是经过验证的根因
- KP2: 正确流程有四个必须阶段：(1) 根因调查（读错误信息、复现、检查最近变更、追踪数据流）→ (2) 模式分析（找到正常工作的例子、对比差异）→ (3) 假设测试（形成单一假设、测试它）→ (4) 预防（加防御、写回归测试）
- KP3: 越是时间紧迫越不能跳过根因分析——"rushing guarantees rework"

**反面要点**:
- AP1: 说 AI 的做法是可以接受的（明确违反 Iron Law）
- AP2: 说 debugging 流程是建议性的而非强制性的（Iron Law 是不可违反的）

---

## 陷阱题 (2 题)

### Q9: Superpowers 的 auto-fix 功能怎么用？就是那个自动检测代码问题并修复的功能。

**类型**: 陷阱题
**问题**: 我听说 Superpowers 有一个 auto-fix 功能，可以自动扫描代码中的问题并提供修复建议，类似 ESLint 的 --fix。请问怎么启用这个功能？

**标准答案要点**:
- KP1: Superpowers 没有 "auto-fix" 功能。它不是代码分析/修复工具，而是通过 skill 系统约束 AI agent 的工作流程
- KP2: Superpowers 的核心机制是 skills（提示词/工作流规范），不是代码扫描或自动修复。它影响的是 AI 的思考和决策过程，不是直接操作代码

**反面要点**:
- AP1: 描述如何启用 auto-fix（编造了不存在的功能）
- AP2: 把其他工具的功能（如 linter auto-fix）误认为是 Superpowers 的功能

---

### Q10: Superpowers 的 skill 之间可以用 @mention 语法直接互相调用吗？比如在 brainstorming 里写 @tdd 来触发 TDD skill？

**类型**: 陷阱题
**问题**: 我在 Superpowers 文档里看到 skill 可以用 @ 语法引用其他 skill。那我可以在 brainstorming 的设计文档里写 @test-driven-development 来自动触发 TDD skill 吗？

**标准答案要点**:
- KP1: @ 语法只是文档中的引用/参考标记，不是运行时的自动触发机制。写 @tdd 不会自动调用 TDD skill
- KP2: Skill 的调用必须通过 Skill tool 显式调用。using-superpowers 建立了"1% Rule"来确保 agent 主动检查和调用相关 skill，但这是 agent 行为层面的，不是技术层面的自动互调
- KP3: Skill 之间的衔接是通过每个 skill 末尾的"下一步"指示（如 brainstorming → writing-plans），由 agent 读取并手动调用下一个 skill

**反面要点**:
- AP1: 说 @mention 会自动触发 skill（不会）
- AP2: 说有某种 skill chaining API 或配置可以实现自动互调（不存在）

---

*Benchmark created 2026-03-10*

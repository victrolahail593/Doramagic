# Codex 研究任务：Soul Extractor 三个进化方向的工程可行性

## 背景

Soul Extractor 是一个从 GitHub 开源项目中自动提取结构化知识的工具，产出 .cursorrules / CLAUDE.md 作为"AI 燃料"注入给 Cursor / Claude Code。

### 当前成果

v0.6 已验证通过，能够产出：
- 项目本质（解决什么问题、核心承诺）
- 3 概念卡 + 3 工作流卡（WHAT + HOW）
- 5+ 代码规则卡 + 3+ 社区陷阱卡（IF，含 GitHub Issues 数据）
- .cursorrules / CLAUDE.md / project_soul.md

### 关键发现：通过对 Superpowers（一个 AI 技能框架）的提取实验，我们发现了三个重大进化方向

#### 发现 1：WHY 层缺失

我们对 Superpowers 进行了两种分析：
- **人类研究**（Claude Opus 深度阅读 + 战略分析）发现了：反合理化设计源于 Cialdini 说服力研究、description 必须是触发器而非摘要的设计哲学、TDD-for-documentation 的元方法论
- **v0.6 自动提取**产出了：14 个 skill 的概念卡、工作流卡、规则卡

人类研究发现的 WHY 层知识（为什么这样设计）是 v0.6 完全没有捕获的。但 WHY 层恰恰是"专家级认知"与"文档级认知"的分水岭。

#### 发现 2：拆解能力

用户使用一个开源项目时，不是使用全部功能，而是解决特定问题。当前 Soul Extractor 全量提取、全量注入。
- 正确的思路不是"按代码模块拆"，而是"按问题域拆"——这个项目解决哪些问题？用什么技术/模块来解决？
- AI 燃料的价值 = 相关性 × 密度。全量注入降低相关性。

#### 发现 3：验证闭环缺失

Superpowers 的 DR-003（Iron Law: 没有失败测试就不写代码）和 DR-005（Two-Stage Review: 先查规格再查质量）给了我们启发：
- Soul Extractor 目前的产出没有经过任何验证
- 规则卡的 sources 引用的 file:line 是否真实存在？
- 真实场景是否是模型编造的？
- severity 评级是否合理？

## 前序研究衔接

你在上一轮完成了社区信号采集的工程研究（`20260309_codex_community_signals_report.md`）。那份报告的关键结论（sort=comments + 本地打分、Security Advisories、git log fix commits、结构化 Markdown 格式、≤20KB 预算）已全部落实到 v0.6 并验证通过。本次研究请在那份报告的基础上继续。

## Opus 对 Superpowers 的战略洞察（完整版）

以下是我们研究员对 Superpowers 的深度分析，v0.6 自动提取没有捕获这些 WHY 层知识：

1. **Soul Extractor 与 Superpowers 是互补关系**：Superpowers 注入方法论（教 AI 怎么干活），Soul Extractor 注入知识（教 AI 懂什么库）。一个改行为，一个补知识。

2. **Superpowers 验证了我们的核心假设**：用结构化文本注入给 AI，确实能显著改变 AI 的行为质量。这证明 .cursorrules 作为"AI 燃料"的产品逻辑有效。

3. **5 个可借鉴的设计模式**：
   - **Description 是触发器不是摘要**：SKILL.md 的 description 必须写触发条件（"Use when..."），绝不能写工作流摘要——模型可能只读 description 就按摘要执行，而不去读完整指令。
   - **反合理化设计 (Anti-rationalization)**：每个 skill 列出模型可能跳过步骤的借口（"红旗列表"），逐一封杀。源于 Robert Cialdini 的说服力研究，对 LLM 同样有效。
   - **技能链 (Skill Chaining)**：brainstorming → writing-plans → executing-plans → finishing-branch，每个技能知道"下一步调用谁"。
   - **上下文是公共资源**：严格控制每个 skill 的文字量（核心 <500 字），因为上下文窗口是公共财产。
   - **Iron Law / Hard Gate**：关键约束用零例外语言。

4. **战略启示**：Superpowers 是纯方法论注入框架，没有自动化知识提取能力。Soul Extractor 的差异化在于自动化知识提取管道。产出格式应与 Superpowers 生态兼容。

## v0.6 对 Superpowers 的实际提取结果（完整卡片）

以下是 v0.6 自动提取的全部产出，请仔细阅读并分析其中哪些知识被捕获、哪些缺失：

### 项目本质
- 解决什么问题：AI 编程助手盲目写代码、缺乏规划、跳过测试
- 核心承诺：通过可组合的"技能"让 AI 遵循完整软件工程工作流
- 一句话总结：Superpowers 让 AI 先思考再动手，把"代码机器"变成"软件工程师"

### 概念卡（3 张）
- CC-001: Skills System — 核心触发机制（1% Rule、Red Flag Detection）
- CC-002: Brainstorming — 设计优先工作流（HARD-GATE、一次一问）
- CC-003: Subagent-Driven Development — 两阶段审查执行（Fresh Subagent、Spec→Quality）

### 工作流卡（3 张）
- WF-001: Design Flow（Idea → Questions → Approaches → Design → Approval → writing-plans）
- WF-002: Execution Flow（Plan → Implementer → Spec Review → Quality Review → Complete）
- WF-003: TDD Flow（RED → Watch Fail → GREEN → Watch Pass → REFACTOR → Commit）

### 代码规则卡（5 张）
- DR-001 [CRITICAL]: 1% Rule — 有任何可能就必须调用 skill
- DR-002 [CRITICAL]: Hard Gate — 设计批准前不能写代码
- DR-003 [CRITICAL]: Iron Law — 没有失败测试不能写生产代码
- DR-004 [HIGH]: Fresh Subagent Per Task — 不复用上下文
- DR-005 [HIGH]: Two-Stage Review — 先查规格再查质量

### 社区陷阱卡（3 张）
- DR-101 [HIGH]: Skills 无法触发（Issue #58, #189, #446 共 65+ comments）
- DR-102 [HIGH]: 安装路径/Symlink 缺失（Issue #76）
- DR-103 [MEDIUM]: Token 消耗过高（Issue #512）

### 关键对比：人类洞察 vs 自动提取

| 人类洞察发现了，v0.6 没有 | 为什么缺失 |
|--------------------------|-----------|
| 反合理化设计源于 Cialdini 说服力研究 | WHY 层——设计哲学无法从代码/issues 提取 |
| Description 必须是触发器不是摘要 | WHY 层——设计决策的"为什么"而非"是什么" |
| TDD-for-Documentation 元方法论 | WHY 层——方法论背后的方法论 |
| Soul Extractor 与 Superpowers 的互补关系 | 交叉分析——需要同时理解两个项目 |
| 产出格式应与 Superpowers 生态兼容 | 战略判断——超出单项目知识提取范围 |

## 研究目标

请从工程实现角度，深入研究以下三个方向的可行性。

### 方向 1：验证闭环（优先级 P0）

我们认为这应该最先做，因为没有验证，其他方向可能放大错误。

**1.1 自检 STAGE 设计**

是否应该在 Stage 3 之后、Stage 4 (assembly) 之前，增加一个验证阶段？比如：
- 读取所有产出的卡片
- 检查 YAML frontmatter 是否完整（severity、sources 等必填字段）
- 检查 sources 中引用的 file:line 是否在 packed_compressed.xml 中真实存在
- 检查 DR-100~ 引用的 Issue 编号是否在 community_signals.md 中存在

这个验证阶段应该由模型做还是由脚本做？各有什么优缺点？

**1.2 Two-Stage Review 实现**

参考 Superpowers 的模式：
- 第一轮：规格合规性检查（格式、字段完整性）— 可以用脚本自动化
- 第二轮：内容质量检查（规则是否有价值、场景是否真实）— 需要模型参与

工程上怎么在弱模型（MiniMax-M2.5）的约束下实现？弱模型能同时生成和审查吗？还是必须分开？

**1.3 验证指标设计**

产出的卡片质量如何量化？请提出具体的指标体系：
- 格式合规率（有多少卡片满足所有必填字段？）
- 证据可追溯率（sources 中引用的行号有多少是真实的？）
- 社区信号利用率（community_signals.md 中的信号有多少被转化为 DR-100~ 卡？）

### 方向 2：WHY 层提取（优先级 P1）

**2.1 WHY 知识的来源分析**

WHY 层知识（为什么这样设计）通常存在于：
- 代码中的注释和 commit message
- README 中的 "Design Decisions" / "Architecture" 章节
- GitHub Discussions 中的设计讨论
- Issue 中标记为 "design" / "architecture" 的讨论
- 博客文章、会议演讲

哪些来源是 prepare-repo.sh 当前能获取的？哪些需要额外采集？

**2.2 WHY 卡片设计**

如果我们增加一种新卡片类型——比如 `design_rationale_card` (DRC)——它应该包含什么字段？请给出模板设计。

**2.3 弱模型能提取 WHY 吗？**

WHY 层需要"理解意图"而非"识别模式"。MiniMax-M2.5 这样的弱模型能否胜任？需要什么样的 prompt 设计？还是说 WHY 层必须用强模型？

### 方向 3：拆解/定向注入（优先级 P2）

**3.1 问题域拆解 vs 代码模块拆解**

正确的拆解思路是"这个项目解决哪些问题"而非"这个项目有哪些模块"。

以 python-dotenv 为例：
- 问题域拆解：① 配置加载 ② 配置修改 ③ 配置发现 ④ CLI 工具
- 代码模块拆解：① main.py ② parser.py ③ variables.py ④ cli.py

两种拆解如何对应？问题域拆解在工程上怎么实现——靠模型理解还是靠代码分析？

**3.2 定向 AI 燃料生成**

如果用户说"我只用 python-dotenv 的配置加载功能"，如何从完整灵魂中裁剪出定向的 .cursorrules？
- 是在提取阶段做（只提取相关部分）？
- 还是在组装阶段做（提取全部，组装时过滤）？
- 各有什么工程优缺点？

**3.3 产品交互设计**

用户如何告诉 Soul Extractor 他关心哪个问题域？
- 提取前指定？（"只提取配置加载相关的知识"）
- 提取后选择？（提取全部，展示问题域列表，用户选择）
- 全自动推断？（分析用户项目代码，自动判断用了哪些功能）

## 产出要求

请撰写一份技术可行性报告，包含：

1. **每个方向的工程实现方案**，附代码片段或伪代码
2. **优先级验证**：你是否同意"验证闭环 P0 > WHY 层 P1 > 拆解 P2"？如果不同意，给出你的排序和理由
3. **最小可行实现**：每个方向的 MVP 需要多少工作量？改几个文件？
4. **风险评估**：每个方向可能遇到的坑

报告文件名：`20260309_codex_evolution_directions_report.md`
报告放置路径：与本任务文件同目录

# Agentic 提取 MVP 设计 — 三方开放研究

## 背景

Soul Extractor 当前是**单遍静态提取**：Stage 0 把源码拼接成一个大文件 → LLM 一次性读完 → 按 Stage 1-4 逐步提取知识。这种架构的天花板已到：

- Session 26 实验结论：Prompt 优化已达边际递减（v3→v4 预计 < +0.3）
- **下一个量级需要架构变革 — Agentic 提取**
- 投资优先级排序：**#1**（预期 +0.7~1.0，天花板从 8.0→8.5+）

## 当前架构的瓶颈

### 1. 静态输入问题
Stage 0 用 `stage0-v2.sh` 做四层漏斗智能采样，把项目源码压缩成一个文件。但：
- 大项目（如 wger 12MB/1123 文件）必须大量截取，丢失信息
- 采样策略是静态的 — 不知道 LLM 会对什么感兴趣，只能猜
- marketingskills 55K 行截取到 5K — 90% 信息丢失

### 2. 单遍提取的局限
LLM 只看一遍代码，无法：
- 先形成假说 → 再去代码中验证
- 发现线索 → 追踪到相关文件 → 深入理解
- 对比不同模块的设计决策
- 回头修正之前的理解

### 3. WHY 提取的天花板
WHY（设计哲学/决策理由）是最高价值知识，但也最难提取：
- WHY 往往藏在 commit message、PR 讨论、代码注释的"为什么"中
- 单遍阅读很难捕捉跨文件的因果链
- Agentic 提取理论上能让 LLM 像专家一样"翻代码"

### 4. UNSAID 提取的瓶颈
UNSAID（未说出口的坑/陷阱）是核心技术壁垒：
- Session 27 确认：LLM 对小众项目的 UNSAID 覆盖率极低（vnpy 0% 严格 / 35% 宽松）
- Agentic 提取能否通过动态探索发现更多 UNSAID？

## 已有实验数据

### Stage 0 v2 的验证结论
- 输入质量是天花板（funNLP: +44% 来自 Stage 0 改进）
- 两个杠杆独立且可叠加：Prompt 优化（-0.5 噪音）+ Stage 0 优化（+0.7 信号）
- Stage 0 v2 让 LLM 看到完全不同的维度（funNLP v3 的 8 条 WHY 全部是新发现）

### 跨模型实验
- Sonnet 7.79 > Gemini 6.63，差距在"信息增量"
- 两者高分 WHY 几乎不重叠 → GDS 多模型融合有价值
- MiniMax 幻觉与目标项目熟悉度相关（superpowers 严重，wger 正常）

### 4 个 SEO 项目的灵魂提取
- 四路 Sonnet 并行提取，每个 4-5 分钟
- 产出 4 份 CLAUDE.md（166-261 行），质量不错
- 但这是小项目（9K-11K 行），大项目（55K+）质量下降

## Agent Harness 行业趋势（2026-03）

刚刚完成的 Agent Harness 分析揭示：
- Vercel：工具从 15 砍到 2，准确率 80%→100%
- Manus 架构：filesystem-as-memory + todo-list 进度机制 + context compaction
- OpenAI Codex：严格分层依赖 + 约束保持 agent 生产力
- Claude Code 架构：最小核心工具集（file read/write + bash + search）+ 两阶段 agent（Initializer + Coding Agent）
- **关键共识：简化工具集 > 复杂路由逻辑**

## Doramagic 已有的 Agentic 基础设施

- Soul Extractor 本身已是多阶段管线（Stage 0-5）
- 子代理模式已验证（4 路 Sonnet 并行提取 SEO 项目）
- OpenClaw 平台支持 agent 调度
- "代码说事实，AI 说故事"原则 = Agent Harness 的约束哲学

## 研究问题（开放式）

### 1. Agentic 提取的核心架构
- "Agent 动态读代码"具体是什么意思？LLM 应该有哪些工具？（file read? grep? AST parse? git log?）
- 单 agent 多轮迭代 vs 多 agent 协作？trade-off 是什么？
- 提取过程应该有多少"自由度"？完全自主探索 vs 有约束的引导式探索？
- 如何防止 agent 在大项目中迷路/陷入无关代码？

### 2. 与现有 Stage 架构的关系
- Agentic 提取是**替代** Stage 0-4 还是**增强**某些 Stage？
- Stage 0 的静态采样 vs Agent 的动态探索：完全替代？还是 Stage 0 做初始采样，Agent 做深入探索？
- Stage 1（灵魂发现）是否应该变成 Agent 的"假说生成"阶段？
- Stage 3.5（fact-checking gate）在 Agentic 架构中如何运作？

### 3. 工具集设计
- Harness Engineering 的经验：**工具越少越好**
- Soul Extractor 的 Agent 需要哪些最小工具集？
- 每个工具的输出格式如何设计？（结构化 vs 自由文本）
- 是否需要 AST 解析等高级工具？还是 grep + file read 足够？

### 4. 上下文管理
- 大项目（10K+ 文件）的上下文不可能全部装入
- Agent 如何决定"接下来看什么文件"？
- filesystem-as-memory 模式是否适用？（Agent 把中间发现写到文件，后续 stage 读取）
- context compaction 策略：什么时候压缩/遗忘已读的代码？

### 5. 知识类型与 Agent 策略的匹配
- WHAT（概念）：可能一遍扫描就够
- HOW（工作流）：可能需要追踪函数调用链
- IF（规则）：可能需要检查 config + validation + error handling
- WHY（设计哲学）：可能需要读 commit history + PR + comments
- UNSAID（暗坑）：可能需要读 issues + changelog + error patterns
- 不同知识类型是否需要不同的 agent 策略？

### 6. 质量与成本的 trade-off
- Agentic 提取的 token 消耗预估（vs 当前单遍）
- 多轮迭代的收益递减点在哪里？（第 1 轮 vs 第 5 轮 vs 第 10 轮）
- 如何控制成本？（设定 budget cap？限制轮数？）
- 用户是否愿意为更高质量的提取等待更长时间 / 支付更多？

### 7. 多模型协作
- Session 26 结论：Sonnet 和 Gemini 的高分 WHY 不重叠
- Agentic 架构下如何利用多模型？每个 agent 用不同模型？
- GDS（Generate-Discriminate-Select）融合在 Agentic 架构中如何实现？

### 8. MVP 定义
- Agentic 提取的最小可用形态是什么？
- 哪个 stage 最适合先做 agentic 化？
- MVP 的验证方式：用什么项目测试？怎么衡量质量提升？
- MVP 需要多少工程量？

### 9. 你还看到了什么我们没想到的？
- Agentic 提取是否暗示了更大的可能性？
- 有没有现有的 agentic code analysis 工具可以参考？
- 风险是什么？

## Doramagic 产品哲学提醒

> **代码说事实，AI 说故事。** Agent 的探索必须产出可追溯的证据，不是自由发挥。
> **不教用户做事，给他工具。** Agent 提取的目标是更高质量的知识，不是更多的自动化。
> **能力升级，本质不变。** Agentic 提取是 Soul Extractor 的架构升级，不是新产品。

## 实际约束

- OpenClaw 平台目前支持的 agent 能力（需要确认）
- 用户通过 Telegram 触发提取，等待时间不能太长（当前 4-5 分钟 / 项目）
- MiniMax 等弱模型也要能跑（不能只在 Claude/GPT-4 上可行）
- 大项目的 token 成本需要可控

## 输出要求

- 给出具体的架构方案，不要停留在"应该用 agent"的层面
- 用 4 个 SEO 项目和 wger 作为案例分析 agentic 提取的预期效果
- 对 MVP 给出明确定义（范围、工时、验证方式）
- 标注每个设计决策的 trade-off

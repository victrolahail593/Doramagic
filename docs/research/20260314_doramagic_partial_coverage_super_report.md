# Doramagic 深度研究报告：当“抄作业”零件不够时，产品应该怎么办

**Date:** 2026-03-14  
**Owner:** Codex  
**Status:** Draft  
**Topic:** Partial Coverage / Gap-Aware Assembly / Incomplete Skill  
**Scope:** 回答 Doramagic 在 OpenClaw 平台上，面对“用户需求无法被单个 repo / skill 完整覆盖”的常态场景时，产品、知识工程与系统架构应如何设计。

---

## 0. 执行摘要

这份报告的核心结论只有一句话：

> **Doramagic 不该把“零件不够”当成失败条件，而应把它当成默认工作模式。**

更具体地说，Doramagic 的真正产品不应该是“找到一个完美匹配的开源答案”，而应该是：

**把部分覆盖的问题，编译成最短闭环。**

这意味着 Doramagic 要从“灵魂提取器”进一步升级成：

- 能识别哪些部分可以直接抄
- 能识别哪些部分只能类比迁移
- 能识别哪些部分当前没有零件
- 能把这些缺口转化为最小补完任务
- 能把“未完成性”明确交付给用户，而不是偷偷用模型幻觉补平

因此，面对零件不够，Doramagic 最好的产品策略不是继续生成一个看起来完整的答案，而是切换成 **Gap-Aware Assembly（缺口感知拼装）** 模式，交付一种新的中间产物：

# **Incomplete Skill**

即：一个可运行、可安装、可继续演进，但显式声明仍有缺口的半成品 Skill。

这会把 Doramagic 从“会说的研究助手”拉成“能交付施工状态的工具编译器”。

---

## 1. 背景：Doramagic 不是知识搜索，而是“灵魂编译”

根据 Doramagic 现有产品定义，Doramagic 的定位并不是通用问答，也不是源码讲解器，而是：

- OpenClaw 生态中的哆啦A梦
- 不教用户做事，给用户工具
- 核心能力是从开源项目中提取 WHY 与 UNSAID
- 让 AI 从“知道代码是什么”升级到“理解为什么这样设计、哪里会踩坑、哪些隐含规则不能破坏”

这些定位在项目现有文档中是清晰的：

- `INDEX.md` 将 Doramagic 定义为“抄作业高手（非从零构建），有立场的专家（非信息搬运工）”
- `PRODUCT_MANUAL.md` 将 Doramagic 定义为“开源项目灵魂提取系统”，强调设计哲学、决策规则、社区踩坑与证据溯源
- `2026-03-11-doramagic-end-state-platform-design.md` 进一步提出 Suitability Engine 和 Assembly / Compiler Service

也就是说，Doramagic 从一开始就不是单纯做 retrieval，而是在做更高层的事情：

**把开源知识转成可执行、可验证、可注入的工具对象。**

问题在于：

现实世界中，真正有价值的用户需求，几乎都不是“一个 repo 正好完美解决”的需求。绝大多数是混合型、组合型、带约束的、部分覆盖的问题。

因此，“零件不够时怎么办”不是边缘问题，而是 Doramagic 这个产品是否成立的中心问题。

---

## 2. 第一性原理：部分覆盖不是异常，而是默认态

### 2.1 为什么完美匹配稀少

从开源生态和用户需求的结构上看，100% 匹配本来就罕见，原因至少有四层。

#### A. 开源项目解决的是“特定上下文中的问题”

每个 repo 都嵌在特定历史、特定团队、特定技术栈、特定治理边界里。你可以抄到 solution，但抄不到完整的 situation。

#### B. 用户需求通常是“组合题”

用户带来的需求常常同时混合：

- 业务目标
- 用户体验要求
- 技术栈偏好
- 部署条件
- 团队能力上限
- 风险偏好
- 预算与维护成本

而 GitHub repo 往往只覆盖其中一部分。

#### C. 真正难的常常不是功能，而是“连接处”

开源项目能教你“这个功能怎么做”，但用户真正卡住的往往是：

- 两个系统怎么对接
- 两种设计哲学是否冲突
- 哪些默认值在这个场景里危险
- 哪些边界条件需要重新定义

这恰好就是 WHY 与 UNSAID 最有价值的地方。

#### D. 最像的案例，不一定最可改造

Case-based design 研究很早就指出，复杂案例的关键不只是有没有相似案例，而是：

- 案例中应捕捉什么内容
- 如何把复杂案例切分成可复用片段
- 如何索引这些片段用于新任务检索

Domeshek 与 Kolodner 在 1993 年的研究里明确把“复杂案例如何分块、索引、复用”作为核心问题，而不是把整个案例整体照搬。[来源](https://www.cambridge.org/core/journals/ai-edam/article/using-the-points-of-large-cases/1F90A3C933ADF219671B06C55DC7C36F)

这对 Doramagic 的启示非常直接：

> **用户不需要一个最像的 repo；用户需要一组最能拼出闭环的零件。**

---

## 3. 研究视角一：RAG 的核心问题不是“检不到”，而是“检而不全”

传统 RAG 叙事容易让人把问题理解成：

- 要么检到正确知识
- 要么完全检不到

但近两年更有价值的研究都在指出另一件事：

> **不完美检索是常态。**

### 3.1 Adaptive Retrieval：不是每次都该检，而是要判断“检多少、检什么”

`RetrievalQA`（ACL Findings 2024）研究的是自适应检索，结论不是“多检一定更好”，而是系统应判断何时需要检索，以及检索应如何配合时间性与问题特征。[来源](https://aclanthology.org/2024.findings-acl.415/)

对 Doramagic 的启示是：

- 不是所有需求都值得大规模 repo 检索
- 有些问题更适合直接调用已有 skill
- 有些问题应先做需求澄清，再检索
- 有些问题应先识别覆盖缺口，再决定是否继续扩检

也就是说，Doramagic 的第一步不该是“搜”，而该是：

**判断这个需求属于哪种覆盖问题。**

### 3.2 Imperfect Retrieval：检索错、不全、相互冲突，都是常态

`Astute RAG`（ACL 2025）更进一步指出：

- imperfect retrieval 是不可避免、常见且有害的
- 外部检索知识和模型内部知识会发生冲突
- 后检索阶段的 source-aware consolidation 很关键

它的核心价值不在于“如何找到完美知识”，而在于“如何在不完美知识条件下整合并判断可信度”。[来源](https://aclanthology.org/2025.acl-long.1476/)

这几乎可以直接翻译成 Doramagic 的产品原则：

1. **接受零件不全是常态**
2. **接受零件之间会冲突**
3. **设计一套整合与降权机制，而不是假装一切一致**
4. **输出时必须显式区分：已覆盖 / 未覆盖 / 推断补足 / 存在冲突**

### 3.3 覆盖率比 Top-1 相似度更重要

`Joint Passage Ranking for Diverse Multi-Answer Retrieval`（EMNLP 2021）研究多答案检索时发现，只优化单条相似度会导致检索结果重复覆盖同一答案，而漏掉其他关键答案。它强调的是**答案集合的联合覆盖率**。[来源](https://aclanthology.org/2021.emnlp-main.560/)

`Topic Coverage-based Demonstration Retrieval`（EMNLP 2025）同样强调：演示或上下文的价值不在相似度最大，而在是否覆盖输入真正需要的主题点。[来源](https://aclanthology.org/2025.emnlp-main.1007/)

Doramagic 的对应结论是：

> **你不该检索一个“最像用户需求的 repo”，你该检索一组“联合起来最能覆盖用户需求的零件”。**

这是从“最佳单例”到“最佳组合”的根本转向。

---

## 4. 研究视角二：Case-Based Design 告诉我们，复用的对象不该是“整个案例”

Doramagic 的“抄作业”本质上非常接近 case-based reasoning，只不过对象从传统设计案例变成了 repo、skill、workflow、community wisdom。

相关研究给出两个极其关键的启示。

### 4.1 复杂案例的关键问题是：怎么切、怎么索引、怎么重组

`Using the points of large cases` 讨论的不是“案例库要不要做”，而是：

- 复杂案例里应该捕捉什么内容
- 如何将复杂案例分割为可使用的 chunk
- 如何为这些 chunk 建立检索索引

这与 Doramagic 当前“项目灵魂”文档虽然相关，但还不完全等价。因为灵魂文档仍偏向“项目级摘要”，而 Doramagic 要处理部分覆盖场景，就必须再往下走一层，把“灵魂”拆成真正可拼装的对象。

### 4.2 被复用的不是结果，而是策略、约束和 rationale

`Recording and reuse of design strategies in an integrated case-based design system` 强调，人类设计者并不只是复用过往结果，还会复用：

- plans
- goals
- critical constraints
- strategy

也就是：**为什么这样做、在什么约束下这样做、做的时候注意什么。**[来源](https://www.cambridge.org/core/journals/ai-edam/article/recording-and-reuse-of-design-strategies-in-an-integrated-casebased-design-system/FBD5A5982A9C1726E8761A000A5342CF)

这和 Doramagic 的 WHY / UNSAID 高度同构。

因此，Doramagic 不应把知识库存成“完整项目画像 + 若干摘要卡片”就结束，而应进一步拆分成至少五类可拼装单元：

1. **Capability Unit**：能做什么
2. **Constraint Unit**：在哪些条件下成立
3. **Rationale Unit**：为什么这样设计
4. **Interface Unit**：如何与其他零件连接
5. **Failure Unit**：在哪里会坏、哪些坑反复出现

只有这五类都具备，Doramagic 才真的能在零件不够时继续工作。

否则你能做推荐，做总结，做顾问，但做不了真正的“拼装”。

---

## 5. 研究视角三：教育理论告诉我们，用户真正需要的不是解释，而是脚手架

Doramagic 的定位是“不给方法，给工具”。这意味着它不能在零件不够时退化成一个课程产品。

但教育理论依然有借鉴意义。

### 5.1 Cognitive Apprenticeship：专家不是把答案讲给你听，而是搭支架让你做

Cambridge 的 `Cognitive Apprenticeship` 章节强调，学徒式学习的关键包括：

- scaffolded participation
- situated activity
- reflection
- productive failure

也就是：

- 不直接把抽象知识灌输给用户
- 而是在真实任务里，让用户拿着支架完成事情
- 允许失败，但失败必须是可推进理解的失败

[来源](https://www.cambridge.org/core/books/cambridge-handbook-of-the-learning-sciences/cognitive-apprenticeship/6FB3422B7B2F16076F2E082C5C18EAA7)

对 Doramagic 的翻译非常重要：

> 当零件不够时，产品不应交付一篇解释，而应交付一个“可运行的脚手架”。

### 5.2 Productive Failure：有控制的“做不完”，比假装做完更有价值

同一脉络中，productive failure 的核心不是鼓励失败，而是：

- 把失败变成清晰的前沿感知
- 让用户看到自己卡在哪里
- 让系统知道下一步该补什么

这和 Doramagic 非常契合。

因为“零件不够”本质上是一种产品化的 productive failure 场景：

- 如果系统假装给出完整答案，用户会在真实执行时摔跤
- 如果系统明确给出已完成部分、缺失部分和下一步补件路径，用户反而更容易继续推进

所以，对 Doramagic 来说，最危险的不是“我做不完”，而是：

**“我明明做不完，却输出得像已经做完。”**

---

## 6. 研究视角四：优秀 Agent 产品已经在从“回答”转向“解决”

OpenAI 与 Zendesk 的官方案例很有启发。Zendesk 强调的不是 message in / response out，而是 **resolution**：

- 理解真实问题
- 进行多轮澄清
- 编译 procedure
- 再按 guardrail 执行

官方文章中明确提到：他们从 intent-based bots 转向 adaptive reasoning，并引入了 procedure compilation 与 execution 分层。[来源](https://openai.com/index/zendesk/)

这对 Doramagic 的意义是：

> 用户来找 Doramagic，不是为了“获得一个听起来很懂开源项目的回答”，而是为了“拿到一个可执行的解决方向”。

另一个官方例子是 OpenAI 2026 年 1 月披露的内部 data agent：

- 它强调 context layering
- 在进展异常时会自我修正
- 允许用户保存记忆
- 严格继承权限模型
- 必要时主动澄清，不必要时用 sensible defaults 保持非阻塞推进

[来源](https://openai.com/index/inside-our-in-house-data-agent/)

这说明一个高价值 agent 的重点，不在“知道多少”，而在：

- 如何组织上下文
- 如何发现自己卡住
- 如何把迭代成本从用户转移到 agent
- 如何在不确定中继续前进，但不越过信任边界

Doramagic 在零件不够时，恰恰应复制这种精神：

**不是停在“我没找到”，也不是装作“我全找到了”，而是继续把用户往 resolution 推进。**

---

## 7. Doramagic 的核心转向：从“灵魂提取器”升级为“缺口感知的工具编译器”

基于以上研究，我认为 Doramagic 应作一个战略级定义升级：

### 旧定义
从 repo 提取灵魂，注入 AI，让其成为专家顾问。

### 新定义
从 repo / skill / 社区实践中提取可拼装的能力、约束、rationale 与失败经验，并在部分覆盖条件下，**编译出最短闭环工具**。

这里有三个关键词。

### 7.1 Gap-Aware
系统要知道自己缺什么，而不是只知道自己有什么。

### 7.2 Assembly
核心不是生成单个答案，而是组合多个互补零件。

### 7.3 Compile
输出不是报告，而是可运行、可验证、可继续演化的交付物。

如果不做这一步升级，Doramagic 很容易停留在“高级知识注入工具”层面。那会有价值，但不会形成真正的平台级壁垒。

---

## 8. 当零件不够时，Doramagic 应有的 6 种工作模式

下面是我认为 Doramagic 在运行时应显式支持的模式切换。

### 模式 1：Whole Reuse（整案复用）

适用场景：
- 有一个 skill / repo 对需求高覆盖
- 约束也大体兼容

输出：
- 直接给完整 skill / 配置 / 顾问对象

这是最简单模式，但不是主战场。

### 模式 2：Multi-Part Assembly（多零件拼装）

适用场景：
- 没有单个完美匹配对象
- 但多个 repo / skill 分别覆盖不同能力

输出：
- 能力覆盖图
- 互补零件集合
- 连接方案
- 冲突项

这是最常见也最关键的模式。

### 模式 3：Strategy Transfer（策略迁移）

适用场景：
- 没有现成实现可直接抄
- 但存在可迁移的架构原则、状态机、流程哲学、权限设计

输出：
- 可迁移原则
- 不可迁移边界
- 推荐重写部分
- 关键 WHY

这是 WHY / UNSAID 最能体现价值的模式。

### 模式 4：Scaffold Delivery（脚手架交付）

适用场景：
- 零件足够拼出 40%-70% 的闭环
- 仍有几个关键缺口未补

输出：
- 半成品 skill
- 占位模块
- 推荐补件顺序
- 最小验证清单

这是最适合产品化的模式。

### 模式 5：Frontier Exposure（前沿暴露）

适用场景：
- 缺口太大，无法交付可运行方案
- 但系统已能清楚说明卡点

输出：
- 已知覆盖部分
- 未覆盖部分
- 缺口类型
- 下一步调研方向

这不是失败，而是把“研究前沿”产品化。

### 模式 6：Abort with Precision（精准中止）

适用场景：
- 涉及高风险场景
- 当前证据不足
- 如果继续生成会误导用户

输出：
- 为什么不能继续
- 缺的是哪类证据
- 需要补什么输入或数据

不是所有需求都该被强行推进。可信系统必须允许“有理由地不做”。

---

## 9. 新产品对象：Incomplete Skill

我认为这是整个研究里最值得直接落地的概念。

当零件不够时，Doramagic 不应该只返回：

- 候选 repo 列表
- 一篇研究摘要
- 一组“你可以考虑”式建议

它应该返回一个正式对象：

# **Incomplete Skill**

它的定义是：

> 一个能被安装、运行、继续迭代，但明确声明自己尚未完成的 Skill 工件。

### 9.1 它应该包含什么

1. **已确认能力**
   - 已被 repo / skill / evidence 支撑的部分
2. **待补模块**
   - 还没有足够零件支持的部分
3. **占位实现**
   - 保证整体结构能跑，但该节点可能是 stub、fallback 或人工确认点
4. **lineage**
   - 来自哪些 repo / skill / 卡片 / 社区经验
5. **WHY / UNSAID 注释**
   - 为什么要这样拼，哪些默认值不能乱改
6. **冲突说明**
   - 哪些零件哲学不兼容，系统是如何取舍的
7. **验证清单**
   - 用户下一步该先验证什么
8. **升级路径**
   - 补齐哪些零件后，它会升级为完整 Skill

### 9.2 为什么这个对象重要

因为它解决了一个关键的产品张力：

- 你又不想只给研究报告
- 又不能在证据不足时给出“假完整”的工具

Incomplete Skill 是中间态工件，它既保持了“给工具”的产品定位，又诚实地保留了未完成性。

这是 Doramagic 区别于教程产品、研究产品、RAG 产品的地方。

---

## 10. 知识工程：Doramagic 需要的不是文档库，而是“可拼装知识单元”

如果要支持 Incomplete Skill，Doramagic 的知识层必须改变对象模型。

### 10.1 不够的做法：把 repo 当成一个整体对象

如果系统里只有：

- repo_profile
- project_soul.md
- 若干 card

那么系统很难知道：

- 哪些 card 是能力
- 哪些是约束
- 哪些是连接接口
- 哪些是失败警告
- 哪些能组合，哪些不能

### 10.2 更合适的对象层级

我建议至少引入以下六类对象：

#### A. Capability Object
- 完成某种用户任务所需的能力
- 例：表单收集、支付、CRM、排班、RAG 检索

#### B. Rationale Object
- 为什么这样设计
- 例：为什么选择事件驱动、为什么要求显式确认、为什么强制 schema 校验

#### C. Constraint Object
- 在什么约束下成立
- 例：只适合单租户、依赖 PostgreSQL、仅支持 webhook 驱动

#### D. Interface Object
- 如何被其他模块调用或拼接
- 例：输入输出结构、状态转换点、触发条件

#### E. Failure Object
- 已知失败模式、陷阱与禁区
- 例：某默认值会导致数据丢失、某组合在高并发下失效

#### F. Assembly Pattern Object
- 已被验证过的多零件拼装模板
- 例：客服 + CRM + 工作流自动化 + 日历预约

只有这样，Doramagic 才能从“检索知识”升级为“检索可拼装性”。

---

## 11. 推荐系统：不要再做 Top-1，改做“最小闭环组合搜索”

### 11.1 错误目标：哪个 repo 最像用户需求？

这个目标太弱了，因为：

- 最像可能只覆盖一个能力面
- 最像可能和用户约束冲突
- 最像可能非常难改
- 最像可能和其他候选组合不兼容

### 11.2 正确目标：哪组零件能以最低补完成本形成闭环？

因此 Doramagic 应该把每个用户请求先编译成一个 `Need Graph`：

- 核心目标
- 必需能力
- 可选能力
- 风险约束
- 明确禁项
- 用户偏好

然后对候选零件集合做三类评分：

#### 1. Coverage Score
覆盖了多少关键需求

#### 2. Adaptation Cost Score
改造成最终方案的成本多高

#### 3. Coherence Score
这些零件的设计哲学、状态模型、依赖边界是否一致

最终目标不是最高相似度，而是：

**Coverage 最大，Coherence 足够高，Adaptation Cost 最低。**

这就是“最短闭环”原则。

---

## 12. 系统最危险的四种错误

一个部分覆盖系统，最危险的失败不是“没找到”，而是以下四种。

### 12.1 虚假完整性
明明只覆盖了 55%，输出却像 95%。

### 12.2 错误拼装
每个零件 individually 正确，但放在一起关系错误。

### 12.3 冲突沉默
系统知道两个 repo 的前提互斥，却没有显式提醒用户。

### 12.4 幻觉补缝
本该标记“缺零件”，结果模型用常识和想象补平。

所以 Doramagic 必须把以下字段升格为主输出，不是附录：

- 已覆盖部分
- 未覆盖部分
- 低置信度部分
- 推断补足部分
- 冲突项
- 下一步最小验证动作

---

## 13. 产品体验：用户不需要“更懂”，用户需要“更少做错”

这点很关键。

Doramagic 的用户目标不是学会开源架构，而是解决眼前问题。

因此，当零件不够时，体验设计不能滑向：

- 长文教学
- 开源课代表
- 架构课
- 一堆理论分析

它应该继续像工具，只是工具形态从“完整机器”变成“可施工半成品”。

所以前台交付物最好固定包含：

1. **可运行骨架**
2. **已注入的灵魂**
3. **缺失模块列表**
4. **推荐补件顺序**
5. **冲突与风险说明**
6. **最小验证任务**

这本质上是在做“脚手架化工具交付”。

---

## 14. 运营与护城河：Doramagic 最终比拼的不是“提取知识”，而是“处理不完整知识”

长期来看，单纯的知识提取不会是最强护城河。原因很简单：

- 更多模型会擅长代码理解
- 更多工具会擅长 repo 总结
- 更多产品会做 skill 生成

但真正难的是：

1. 如何把开源世界切成真正可拼装的知识对象
2. 如何知道这些对象之间哪里兼容、哪里冲突
3. 如何在信息不完备时依然推进用户闭环
4. 如何把“不完整性”交付成高价值产物，而不是失败感
5. 如何从真实用户补件过程里学到下一轮更好的拼装模式

所以 Doramagic 的长期护城河不是“谁更会看懂 repo”，而是：

> **谁更会在不完整世界里，把碎片编译成可信的工具。**

---

## 15. 最终设计原则

如果要把上面的研究压缩成一组产品铁律，我建议是下面这 8 条。

### 原则 1：部分覆盖是默认态，不是异常态
产品流程必须默认考虑零件不全。

### 原则 2：不要输出假完整
任何不完整都必须显式可见。

### 原则 3：最小闭环优先于最大相似度
检索和推荐目标应改为“最短闭环”。

### 原则 4：复用策略、约束与 rationale，而不仅是实现
WHY / UNSAID 必须进入拼装逻辑，而不只是进入顾问语气。

### 原则 5：输出脚手架，而不是教程
零件不够时，交付半成品工具，不交付纯解释。

### 原则 6：冲突是主信息，不是噪音
系统要主动暴露不兼容项。

### 原则 7：缺口必须对象化
未覆盖部分要被建模为明确的 gap object，而不是一句“还需要调研”。

### 原则 8：把“未完成性”产品化
Incomplete Skill 应成为 Doramagic 的正式交付物。

---

## 16. 我对 Doramagic 的一句定义升级

如果让我替 Doramagic 写一句新的产品定义，我会写成：

> **Doramagic 是一个面向不完整性的工具编译器：它从开源世界提取 WHY 与 UNSAID，把碎片化零件拼装成最短闭环，并在无法完整交付时，诚实地交付可运行的半成品工具。**

这句话比“灵魂提取器”更接近它真正的未来。

---

## 17. 对你的问题的最终回答

### 问：一个“抄作业”型知识产品，在零件不够时应该怎么办？

答：

**它不应该继续假装自己能直接给完整答案。它应该切换成缺口感知拼装模式，把“能抄的部分、不能抄的部分、必须补的部分、下一步怎么闭环”编译成一个可运行的半成品工具。**

再压缩成一句话：

# **Doramagic 不该承诺完美匹配；它该承诺最短闭环。**

---

## 18. 证据层级说明

### A. 已验证外部依据

- 自适应检索与是否检索的判断：[RetrievalQA, ACL Findings 2024](https://aclanthology.org/2024.findings-acl.415/)
- 不完美检索与知识冲突的常态性：[Astute RAG, ACL 2025](https://aclanthology.org/2025.acl-long.1476/)
- 多答案/多主题覆盖优于单点相似度：[JPR, EMNLP 2021](https://aclanthology.org/2021.emnlp-main.560/), [TopicK, EMNLP 2025](https://aclanthology.org/2025.emnlp-main.1007/)
- 复杂案例应被切块、索引、重组：[Using the points of large cases, AI EDAM 1993](https://www.cambridge.org/core/journals/ai-edam/article/using-the-points-of-large-cases/1F90A3C933ADF219671B06C55DC7C36F)
- 设计复用不仅复用结果，还复用策略与约束：[Recording and reuse of design strategies..., AI EDAM 1994](https://www.cambridge.org/core/journals/ai-edam/article/recording-and-reuse-of-design-strategies-in-an-integrated-casebased-design-system/FBD5A5982A9C1726E8761A000A5342CF)
- 学徒式脚手架与 productive failure：[Cognitive Apprenticeship, Cambridge Handbook of the Learning Sciences](https://www.cambridge.org/core/books/cambridge-handbook-of-the-learning-sciences/cognitive-apprenticeship/6FB3422B7B2F16076F2E082C5C18EAA7)
- Agent 产品从回答走向 resolution：[Zendesk x OpenAI](https://openai.com/index/zendesk/)
- Agent 通过上下文分层、自修正与权限继承实现可信推进：[Inside OpenAI’s in-house data agent](https://openai.com/index/inside-our-in-house-data-agent/)

### B. 已验证本地产品上下文

- Doramagic 定位与“不给方法，给工具”：`INDEX.md`
- Doramagic 的灵魂提取定义、双半魂模型、证据门控：`docs/PRODUCT_MANUAL.md`
- Suitability Engine 与 Assembly / Compiler Service 方向：`docs/plans/2026-03-11-doramagic-end-state-platform-design.md`

### C. 本报告中的核心推断

以下属于基于 A+B 的产品推断，而非某篇文献的原话：

- “Gap-Aware Assembly” 应成为 Doramagic 的主工作模式
- “Incomplete Skill” 应成为正式产品对象
- 推荐系统目标应从 Top-1 similarity 改为最短闭环组合搜索
- Doramagic 的长期护城河在于“处理不完整知识”，而非仅“提取知识”

这些是本报告的综合判断，不是文献直接结论。

---

## 19. 对后续产品设计的直接建议

如果下一步要把这份研究落成产品方案，我建议优先做三件事：

1. **定义 Need Graph 与 Gap Object schema**
   - 让“缺什么”变成结构化对象
2. **定义 Incomplete Skill 规范**
   - 让“半成品工具”成为正式产物
3. **把检索目标从 single best match 改成 best closure set**
   - 真正把推荐系统从搜索升级为拼装

如果这三步成立，Doramagic 的路线会非常清晰。

---

## 20. 参考资料

### 本地文档

- `/Users/tang/Documents/vibecoding/Doramagic/INDEX.md`
- `/Users/tang/Documents/vibecoding/Doramagic/docs/PRODUCT_MANUAL.md`
- `/Users/tang/Documents/vibecoding/Doramagic/docs/plans/2026-03-11-doramagic-end-state-platform-design.md`

### 外部来源

1. Zihan Zhang, Meng Fang, and Ling Chen. *RetrievalQA: Assessing Adaptive Retrieval-Augmented Generation for Short-form Open-Domain Question Answering*. ACL Findings 2024.  
   https://aclanthology.org/2024.findings-acl.415/

2. Fei Wang, Xingchen Wan, Ruoxi Sun, Jiefeng Chen, and Sercan O. Arik. *Astute RAG: Overcoming Imperfect Retrieval Augmentation and Knowledge Conflicts for Large Language Models*. ACL 2025.  
   https://aclanthology.org/2025.acl-long.1476/

3. Sewon Min, Kenton Lee, Ming-Wei Chang, Kristina Toutanova, and Hannaneh Hajishirzi. *Joint Passage Ranking for Diverse Multi-Answer Retrieval*. EMNLP 2021.  
   https://aclanthology.org/2021.emnlp-main.560/

4. Wonbin Kweon, SeongKu Kang, Runchu Tian, Pengcheng Jiang, Jiawei Han, and Hwanjo Yu. *Topic Coverage-based Demonstration Retrieval for In-Context Learning*. EMNLP 2025.  
   https://aclanthology.org/2025.emnlp-main.1007/

5. Eric Domeshek and Janet Kolodner. *Using the points of large cases*. AI EDAM, 1993.  
   https://www.cambridge.org/core/journals/ai-edam/article/using-the-points-of-large-cases/1F90A3C933ADF219671B06C55DC7C36F

6. Jenmu Wang and H. Craig Howard. *Recording and reuse of design strategies in an integrated case-based design system*. AI EDAM, 1994.  
   https://www.cambridge.org/core/journals/ai-edam/article/recording-and-reuse-of-design-strategies-in-an-integrated-casebased-design-system/FBD5A5982A9C1726E8761A000A5342CF

7. Allan Collins and Manu Kapur. *Cognitive Apprenticeship*. The Cambridge Handbook of the Learning Sciences.  
   https://www.cambridge.org/core/books/cambridge-handbook-of-the-learning-sciences/cognitive-apprenticeship/6FB3422B7B2F16076F2E082C5C18EAA7

8. OpenAI. *Zendesk uses OpenAI to build adaptive service agents focused on resolutions*. 2025-03-27.  
   https://openai.com/index/zendesk/

9. OpenAI. *Inside OpenAI’s in-house data agent*. 2026-01-29.  
   https://openai.com/index/inside-our-in-house-data-agent/

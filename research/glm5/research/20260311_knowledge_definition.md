# 人类可用的知识 vs AI可用的知识：结构化研究报告

**研究主题**：人类可用的知识 vs AI可用的知识  
**研究日期**：2026年3月11日  
**研究目的**：为 Doramagic（从开源项目中提取"灵魂"的工具）提供理论支撑

---

## 执行摘要

本报告深入研究人类程序员与AI大模型在处理代码知识方面的本质差异。通过文献调研与理论分析，我们发现：

1. **人类的最小知识单元是"组块"（Chunk）**，通过认知机制组织和存储，具有情境依赖性
2. **AI的最小知识单元是"Token"**，通过统计模式嵌入高维向量空间，缺乏真实语义理解
3. **知识转化过程中存在显著丢失**：隐性知识难以完全显性化，时序/因果/意图信息在编码中丢失
4. **理解开源项目需要不同的知识组合**：人类依赖设计意图和决策背景，AI依赖代码结构和统计规律

---

## 一、人类可用的知识：认知科学的视角

### 1.1 最小知识单元：组块（Chunk）

认知科学研究表明，人类记忆的最小单元是**组块**——一种将离散信息整合为有意义单元的心理结构[1]。

- **组块定义**：将分散的信息元素组合成有意义的单元。例如，一个经验丰富的程序员看到 `for (int i = 0; i < n; i++)` 时，不会逐字符阅读，而是将其识别为一个"循环模式"的组块。
- **组块形成机制**：通过反复暴露和模式识别，相关信息被压缩为单一记忆单元。CHREST模型（Chunk Hierarchy and REtrieval STructures）证明，专家通过多年经验形成复杂的组块和模板结构[2]。

### 1.2 知识组织方式

人类程序员组织代码知识的方式包括：

| 组织方式 | 描述 | 示例 |
|---------|------|------|
| **层级结构** | 按抽象层级组织（类→模块→函数→语句） | 理解React组件的生命周期 |
| **模式匹配** | 识别常见编程模式 | MVC、Observer、Factory |
| **情境关联** | 与具体问题场景关联 | "这个bug在处理并发时出现" |
| **因果链条** | 理解代码行为的前因后果 | "修改这个函数会导致X问题" |

### 1.3 隐性知识（Tacit Knowledge）的核心地位

知识管理领域的经典理论将知识分为两类[3]：

- **显性知识（Explicit Knowledge）**：可编码、可文档化的知识，如API文档、代码注释、设计规范
- **隐性知识（Tacit Knowledge）**：难以表达的个人经验、直觉、"手感"，如：
  - "为什么选择这个算法而不是那个"——设计决策的理由
  - "这段代码哪里不对劲"——代码异味的直觉
  - "遇到这种问题通常先检查什么"——调试策略

**关键洞见**：隐性知识占软件工程知识的绝大部分，且难以通过文档传递[4]。正如研究者所指出的，"Monad的使用方式是隐性知识，而隐性知识本质上抵抗直接知识传递"[5]。

### 1.4 人类理解代码的认知模型

程序理解研究提出了多种认知模型，其中**Letovsky的认知模型**具有代表性[6]：

```
输入 → 认知过程 → 输出
  ↓       ↓        ↓
代码/文档 提问/推测 → 心理模型
```

- 程序员不断向代码提问并推测事实
- 认知过程在所有抽象层级同时工作
- 目标是构建程序的**心智模型**（Mental Model）

---

## 二、AI可用的知识：LLM的技术视角

### 2.1 最小知识单元：Token

大型语言模型（LLM）的最小处理单元是**Token**——经过分词（Tokenization）后的文本片段[7]。

- **分词方式**：字节对编码（BPE）、WordPiece等，将文本分解为子词单元
- **代码分词的独特挑战**：
  - 变量名`user_id_to_name_map`可能被分解为多个无意义的token片段[8]
  - 缩进和空格的处理方式影响模型对代码结构的理解
  - GPT-4专门针对Python缩进进行了优化分组[9]

### 2.2 语义表示：嵌入向量（Embedding）

LLM通过**嵌入**将token映射到高维向量空间：

- **语义空间**：语义相近的token在向量空间中距离更近
- **注意力机制**：Transformer架构通过自注意力捕获token间的依赖关系[10]
- **层级表示**：浅层捕获表面特征（token身份、语法角色），深层捕获抽象语义[11]

### 2.3 LLM理解代码的能力与局限

**能力**[12][13]：
- 理解代码语法结构，可充当AST解析器
- 具有一定的静态行为分析能力
- 能识别常见的编程模式和惯例

**局限**[14][15]：
- **语法vs语义**：生成的代码通常语法正确但语义可能有误
- **语义理解不完整**：对细微的语义变化敏感度不足（最新研究显示SOTA模型在语义等价性判断上表现不佳[16]）
- **缺乏执行理解**：不真正"运行"代码，无法验证运行时行为
- **长上下文限制**：大型代码库超出token限制时难以把握整体架构

---

## 三、知识转化：人类到AI的鸿沟

### 3.1 SECI模型与知识转化

野中郁次郎的SECI模型描述了隐性知识与显性知识的四种转化模式[17]：

| 模式 | 转化方向 | 描述 |
|------|---------|------|
| **社会化（Socialization）** | 隐性→隐性 | 通过共享经验传递知识（如pair programming） |
| **外化（Externalization）** | 隐性→显性 | 将隐性知识表达为文档（Doramagic的核心任务） |
| **组合（Combination）** | 显性→显性 | 整合不同来源的显性知识 |
| **内化（Internalization）** | 显性→隐性 | 通过学习将显性知识转化为个人经验 |

**关键洞见**：外化（隐性→显性）是最困难且最关键的转化机制，而这正是Doramagic试图做的事情。

### 3.2 知识转化过程中丢失的信息

当人类知识转化为AI可用格式时，以下信息显著丢失：

| 丢失类型 | 描述 | 示例 |
|---------|------|------|
| **时序信息** | 决策的先后顺序和历史背景 | "我们尝试了A方案，失败后才改用B" |
| **因果链条** | 决策背后的推理过程 | "因为性能问题，所以我们牺牲了可读性" |
| **意图/目的** | 代码设计的目标和动机 | "这段hack是为了兼容旧版API" |
| **情境依赖** | 特定场景下的适用性 | "这个模式在并发场景下有问题" |
| **权衡考量** | 多目标间的取舍决策 | "我们在安全性和性能之间选择了前者" |
| **失败经验** | 踩过的坑和教训 | "千万别用这个方案，会导致内存泄漏" |

### 3.3 Tokenization带来的语义损失

分词过程本身也会引入语义损失[18]：

- **形态分解**：`user_id_to_name_map` → `user`, `_`, `id`, `_`, `to`, `_`, `name`, `_`, `map`，破坏了变量的语义整体性
- **数字处理**：内存地址、十六进制值等对tokenizer构成挑战[19]
- **领域差异**：自然语言训练的tokenizer处理代码时表现不佳

---

## 四、理解开源项目：人类vs AI的知识需求

### 4.1 人类理解开源项目所需的知识

人类程序员理解陌生代码库时，需要的核心知识包括：

1. **设计意图（Why）**：为什么这样设计？解决什么问题？
2. **架构决策（How）**：模块如何划分？依赖关系如何组织？
3. **历史背景（When）**：为什么在这个时间点做出这个决定？
4. **决策权衡（Trade-offs）**：做了哪些取舍？放弃了什么？
5. **踩坑经验（Lessons）**：走过哪些弯路？有什么教训？

**典型场景**：
- 看到一个"奇怪"的代码模式，需要理解这是"历史遗留"还是"有意为之"
- 遇到bug，需要知道"之前是怎么工作的"和"为什么现在不工作了"
- 想要贡献代码，需要理解"这里的 coding style 背后有什么考量"

### 4.2 AI理解开源项目所需的知识

LLM理解代码库时，依赖以下知识：

1. **语法结构**：代码的AST表示、词法结构
2. **统计规律**：常见模式、惯例、风格
3. **语义关系**：函数调用、数据流、控制流
4. **文档内容**：README、API文档、注释

**典型场景**：
- 根据上下文补全代码
- 解释某个函数的作用
- 生成符合项目风格的代码

### 4.3 知识需求对比

| 维度 | 人类需求 | AI需求 |
|------|---------|--------|
| **核心** | 意图、动机、背景 | 结构、模式、关系 |
| **表达方式** | 叙事、故事、经验 | 向量、权重、概率 |
| **组织形式** | 关联网络 | 嵌入空间 |
| **获取方式** | 交流、实践、领悟 | 统计学习、模式匹配 |
| **可解释性** | 高（可讲述理由） | 低（黑箱） |

---

## 五、相关研究与论文

### 5.1 代码理解认知模型

- **Letovsky (1986)**: "Cognitive processes in program comprehension" - 提出了程序理解的认知模型[6]
- **Pennington (1987)**: "Program comprehension as a knowledge acquisition process" - 将程序理解视为知识获取
- **Shneiderman & Mayer**: 认知框架描述程序组成、理解、调试和修改

### 5.2 LLM代码语义理解

- **Wei Ma (2023)**: "LLMs: Understanding Code Syntax and Semantics for Code Analysis" - 系统分析LLM在代码分析中的语法/语义能力[12]
- **Nguyen & Vu (2024)**: "An Empirical Study on Capability of Large Language Models in Understanding Code Semantics" - 提出Empica框架评估LLM代码语义理解能力[13]
- **Stanford (2025)**: "EquiBench: Benchmarking Large Language Models' Understanding of Code Equivalence" - 测试LLM对代码语义等价性的理解[16]

### 5.3 知识管理与SECI模型

- **Nonaka & Takeuchi (1995)**: 《知识创造公司》- 提出SECI模型
- **Explicit and tacit knowledge conversion effects in software engineering (2017)** - 将SECI模型应用于软件工程教育[4]

### 5.4 程序理解工具

- **Software Archaeology**: 用VR技术探索旧代码库[20]
- **RepoLens**: 从代码仓库中提取概念知识[21]
- **Design Rationale Mining**: 从issue logs中挖掘设计知识[22]

---

## 六、Doramagic产品设计建议

基于本研究的发现，为Doramagic提供以下设计建议：

### 6.1 核心定位

Doramagic应该专注于**弥合人类隐性知识与AI可用表示之间的鸿沟**，即"外化"（Externalization）环节。

### 6.2 知识提取层次

建议采用多层次知识提取策略：

| 层次 | 内容 | 提取方法 |
|------|------|---------|
| **显性层** | API文档、结构说明 | 解析现有文档 |
| **模式层** | 编码风格、惯例 | 代码模式挖掘 |
| **决策层** | 设计决策、权衡 | Issue/PR分析、commit历史 |
| **经验层** | 踩坑教训、调试技巧 | 开发者访谈、社区讨论 |

### 6.3 保留转化过程中的信息

为减少知识转化丢失，建议：

1. **保留时序**：记录决策的时间线和演变过程
2. **保留权衡**：明确记录"选择A而非B的原因"
3. **保留意图**：提取代码编写时的目标描述
4. **保留上下文**：记录特定场景和适用条件

### 6.4 输出格式设计

考虑到AI处理的特点，建议输出：

- **结构化知识图谱**：实体（概念、模式）+关系（因果、依赖）
- **可检索的知识卡片**：按场景/问题组织的经验记录
- **上下文敏感的注释**：解释"为什么"而非"是什么"
- **多粒度表示**：从高层架构到具体实现的多层次视图

### 6.5 增强AI理解的策略

1. **Tokenization优化**：针对代码特点选择合适的分词策略
2. **结构化表示**：利用AST、控制流图等结构化表示
3. **上下文窗口管理**：大型代码库的分块和索引策略
4. **外部知识增强**：结合知识图谱补充训练数据的不足

### 6.6 评估指标

建议从以下维度评估知识提取效果：

- **完整性**：是否覆盖了人类理解所需的关键知识
- **准确性**：提取的知识是否正确
- **可用性**：AI能否有效利用这些知识
- **转化损失**：从人类知识到AI表示的过程中丢失了多少

---

## 七、结论

本研究揭示了人类可用的知识与AI可用的知识之间的本质差异：

1. **人类的知识**是以组块为单位的、情境依赖的、包含大量隐性知识的认知结构
2. **AI的知识**是以Token为单位的、统计嵌入的、缺乏真实意图理解的数学表示
3. **两者之间的转化**存在显著的信息丢失，特别是意图、因果和经验类知识
4. **理解开源项目**需要不同类型的知识组合，人类更依赖"为什么"，AI更依赖"是什么"

对于Doramagic而言，这意味着：
- 核心价值在于**提取和保存那些难以自动获取的隐性知识**
- 成功的关键在于**最小化知识转化过程中的信息损失**
- 产品设计应该**同时服务于人类的知识表达和AI的知识理解**

---

## 参考文献

[1] Chunking (psychology) - Wikipedia. https://en.wikipedia.org/wiki/Chunking_(psychology)

[2] CHREST | CHREST. http://www.chrest.info/chrest.html

[3] Tacit knowledge - Wikipedia. https://en.wikipedia.org/wiki/Tacit_knowledge

[4] Explicit and tacit knowledge conversion effects, in software engineering undergraduate students. Knowledge Management Research & Practice, 2017. https://link.springer.com/article/10.1057/s41275-017-0065-7

[5] Programming and Tacit Knowledge. https://mbuffett.com/posts/all-tacit-knowledge/

[6] Letovsky, S. (1986). Cognitive processes in program comprehension. Papers presented at the first workshop on empirical studies of programmers.

[7] Understanding tokens - .NET | Microsoft Learn. https://learn.microsoft.com/en-us/dotnet/ai/conceptual/understanding-tokens

[8] Tokenization in large language models, explained. https://seantrott.substack.com/p/tokenization-in-large-language-models

[9] LLM Tokenization. https://hundredblocks.github.io/transcription_demo/

[10] Transformer Explainer: LLM Transformer Model Visually Explained. https://poloclub.github.io/transformer-explainer/

[11] Understanding and controlling LLM internal representations. https://medium.com/@khayyam.h/understanding-and-controlling-llm-internal-representations-87c939957b25

[12] Wei Ma (2023). "LLMs: Understanding Code Syntax and Semantics for Code Analysis". arXiv:2305.12138

[13] Nguyen & Vu (2024). "An Empirical Study on Capability of Large Language Models in Understanding Code Semantics". arXiv:2407.03611

[14] LLMs Explain't: A Post-Mortem on Semantic Interpretability in Transformer Models. arXiv:2601.22928

[15] How Accurately Do Large Language Models Understand Code? arXiv:2504.04372

[16] EquiBench: Benchmarking Large Language Models' Understanding of Code Equivalence. Stanford CS.

[17] SECI Model of Knowledge Creation - ASCN. https://ascnhighered.org/ASCN/change_theories/collection/seci.html

[18] Why Your Next LLM Might Not Have A Tokenizer. Towards Data Science, 2025.

[19] How Different Tokenization Algorithms Impact LLMs and Transformer Models for Binary Code Analysis. arXiv:2511.03825

[20] Immersive Software Archaeology: Collaborative Exploration and Note Taking in Virtual Reality. ICPC 2024.

[21] RepoLens: Extracting Conceptual Knowledge to Locate Software Issues. arXiv:2509.21427

[22] A Novel Approach for Automated Design Information Mining from Issue Logs. arXiv:2405.19623

---

*报告完成时间：2026年3月11日*

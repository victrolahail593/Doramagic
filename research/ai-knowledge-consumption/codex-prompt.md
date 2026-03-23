# Codex 研究指令

复制以下内容到 Codex CLI 执行：

```
请完成以下研究任务，将报告写入 /Users/tang/Documents/vibecoding/Doramagic/research/ai-knowledge-consumption/reports/codex-report.md

## 研究背景

我们构建了一个知识提取引擎（Soul Extractor），从开源项目代码中提取知识（概念、工作流、决策规则、设计哲学）。这些知识最终要注入到 AI 助手的上下文中，让 AI 更好地帮用户工作。

核心问题：**提取出的知识以什么格式交付给 AI，AI 的消费效率最高？**

一个关键洞察：LLM 是大语言模型，天生擅长处理自然语言。结构化格式（YAML/JSON 卡片）vs 叙事体（自然语言段落）vs 混合格式——哪种让 AI 表现最好？

## 你的研究方向：工程实践视角

### 1. 现有 AI 工具的知识注入格式深度调研

逐个分析以下工具/系统的知识注入格式，每个都要说明"用什么格式、为什么选这个格式、效果如何"：

- **CLAUDE.md**：Claude Code 的项目指令文件。它用什么格式？为什么选自然语言+Markdown 而不是 JSON/YAML？有没有官方说明格式选择的理由？
- **.cursorrules / .cursor/rules**：Cursor 的项目规则文件。格式是什么？和 CLAUDE.md 有什么区别？
- **Cursor @docs**：文档索引功能。索引后的文档以什么格式注入上下文？chunk 还是全文？
- **GitHub Copilot Knowledge Bases / Copilot Spaces**：知识如何组织和注入？
- **Superpowers（obra/superpowers）**：SKILL.md 的格式设计——它为什么选择特定的 Markdown 结构？有什么效果数据？
- **Continue.dev @docs**：文档注入的格式
- **OpenAI Custom Instructions / System Prompts**：最佳实践是什么格式？
- **Anthropic 官方的 prompt engineering 指南**：对知识注入格式有什么建议？

### 2. 上下文管理的工程实践

- 知识放在 system prompt vs user context vs tool results 中，工程上有什么差异？
- 分块注入（RAG 检索按需注入）vs 一次性全量注入的工程 tradeoff
- 上下文窗口管理：当知识占比超过多少时开始影响 AI 对用户指令的响应？
- 有没有"上下文预算分配"的工程最佳实践？（知识 vs 代码 vs 用户指令的比例）

### 3. 格式转换的工程方案

- 如果源数据是结构化的（YAML 卡片），注入前转成自然语言叙事是否更好？
- 有没有工具或库在做"结构化数据 → LLM 友好格式"的转换？
- "编译"步骤（源格式 → 消费格式）在工程上怎么实现最优？

### 4. 真实案例分析

- 有没有公开的 A/B 测试数据，比较不同格式对 LLM 任务表现的影响？
- Cursor/Copilot 社区有没有关于"什么样的 .cursorrules 写法效果最好"的讨论？
- 有没有"prompt format vs task accuracy" 的 benchmark？

## 报告要求

1. 每个工具的格式分析必须附来源（官方文档 URL、源码链接、社区讨论）
2. 区分"已验证实践"和"推测"
3. 给出明确的格式推荐（针对不同知识类型）
4. 如果有量化数据（A/B 测试、benchmark）优先引用
5. 3000-5000 字，中文撰写
```

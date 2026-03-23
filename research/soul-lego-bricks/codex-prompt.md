# Codex 研究指令

复制以下内容到 Codex CLI 执行：

```
请完成以下研究任务，将报告写入 /Users/tang/Documents/vibecoding/Doramagic/research/soul-lego-bricks/reports/codex-report.md

## 研究背景

我们在构建一个 AI 知识提取引擎（Soul Extractor），它从开源项目代码中提取隐性知识（设计哲学、心智模型、社区踩坑经验）。

当前痛点：每次提取时 LLM 需要同时推断"框架通用知识"和"项目特有知识"，导致幻觉率高。

解决方案：预提取热门框架/生态的标准化知识块（"灵魂积木 / Soul Lego Bricks"），在提取过程中作为 RAG 参考注入，缩小 LLM 自由生成范围。

核心问题：这些积木的最优粒度是什么？

## 你的研究方向：工程与架构视角

请深入调研以下问题，每个问题都需要具体的技术方案和真实案例：

### 1. 现有 AI 开发工具的框架知识架构
- Cursor 的 codebase indexing 是怎么做的？它有没有预置的框架级知识？
- GitHub Copilot 的知识体系是纯依赖训练数据还是有额外的检索层？
- Sourcegraph Cody 的 context engine 怎么处理框架文档？
- Continue.dev 的 @docs 功能是怎么索引框架文档的？
- 有没有其他工具在做"框架知识预提取"？

### 2. RAG 系统中的粒度工程
- 主流 RAG 框架（LlamaIndex、LangChain、Haystack）的 chunking 策略有哪些？
- 什么 chunk size 对代码理解任务效果最好？（有没有 benchmark 数据？）
- "层次化检索"（先粗后细）在实践中效果如何？
- 有没有 adaptive chunking（根据内容类型自动选择粒度）的成熟方案？

### 3. 知识索引与组织的技术方案
- Knowledge Graph vs Vector Store vs Hybrid — 对于框架知识哪种最合适？
- 如何处理知识之间的层次关系（Django → Django ORM → Django ORM Migration）？
- 知识版本化（Django 4.x vs 5.x）在技术上怎么实现？
- 有没有成熟的"知识编译"工具（把文档/代码转成结构化知识）？

### 4. 积木格式设计建议
- 基于你的调研，一个"灵魂积木"应该包含什么字段/结构？
- 它应该是 JSON、YAML、Markdown 还是其他格式？
- 每个积木的 token 预算应该是多少？（考虑 RAG 注入的上下文成本）
- 如何设计积木之间的引用/依赖关系？

## 报告要求

1. 每个发现必须附来源（URL 或论文引用）
2. 区分"已验证的工程实践"和"推测/建议"
3. 给出明确的粒度推荐（框架级/模式级/领域级/混合）
4. 列出 Top 20 最值得优先预提取的框架/生态（按工程价值排序）
5. 设计一个具体的积木格式草案（给出示例）
6. 识别风险：这个方案可能在工程上失败的原因

报告长度：3000-5000 字。用中文撰写。
```

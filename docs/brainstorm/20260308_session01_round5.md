# AllInOne Brainstorm Session 01 — Round 5: Market & Tech Research
**Date**: 2026-03-08

---

## Tangsir 的关键修正
- 社区实践经验可能比代码灵魂更重要（AllInOne ≠ Claude Code）
- 需要跨语言：美国人和意大利人的经验可以互补
- 第一个成果应该是预研报告，不是开干
- 预研报告可以给不同大模型审阅出谋划策

## 两个调研方向

### 方向一：市场竞品分析
**结论：AllInOne 的完整愿景无人实现**

三层分离现状：
| 层 | 现有产品 | 状态 |
|---|---------|------|
| 吸收（理解代码） | DeepWiki, Greptile, Sourcegraph, Augment | 成熟 |
| 转化（变成服务） | Agent 构建器们 | 成熟但手动 |
| 服务（给普通人用） | Lovable, Replit, Elestio | 成熟但断开 |

最接近的产品：
- **DeepWiki** — 自动从 GitHub 生成 wiki + 问答，但止步于"理解"
- **Glean** — 吸收+转化+服务但只针对企业内部知识
- **Elestio** — 400+ 开源一键部署但无 AI 知识层

白色空间：**吸收→转化→服务的完整链条**

### 方向二：技术可行性

#### 代码半魂提取（①②③④）
- 工具链成熟：Repomix + Tree-sitter + LLM + KGGen
- 准确度：70-85%
- 成本：$2-5/项目

#### 社区半魂提取（⑤⑥）
- API 可用：GitHub Issues/PRs (REST), Discussions (GraphQL), SO, HN
- Reddit 获取较难（API 限速）
- 准确度：50-70%（噪音需过滤）
- 成本：$8-15/项目

#### 学术验证
- 《The Lost Soul of Software》确认：灵魂不在代码里，在人与人的对话中
- LLM 代码理解是"浅而广"的——适合知识提取，不适合精确调试
- 跨语言：现代大模型天然支持多语言知识提取

#### 三个核心技术挑战
1. 社区知识的质量过滤（信号 vs 噪音）
2. 知识的时效性（持续更新 vs 一次性提取）
3. 代码知识与社区知识的交叉关联

#### 成本估算
- 单个项目完整提取：$10-20
- 1000 个项目规模：$10,000-20,000

## 关键竞品详情
- DeepWiki (Cognition/Devin AI) - 最接近吸收层
- Greptile - $180M 估值，代码理解
- Sourcegraph Cody/Amp - 企业级代码搜索
- Augment Code - Context Engine 可作 API 使用
- PocketFlow - 开源，从代码生成教程
- Mintlify - a16z 投资，$18M A轮
- Lovable - $6.6B 估值，vibe coding
- Replit Agent - $100M ARR
- Simplai - 最接近 Agent 市场概念
- Glean - 企业内部知识 AI

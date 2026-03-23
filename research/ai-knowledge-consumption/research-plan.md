# AI 知识消费有效性研究计划

## 背景

Doramagic 的 Soul Extractor 从开源项目中提取知识（概念卡 CC、工作流卡 WF、决策规则卡 DR、设计哲学 WHY）。提取方法已确定：事实归确定性脚本，语义理解归 LLM。

但提取只是生产端。这些知识最终要被**下游 AI 消费**——注入到 AI 助手的上下文中，让 AI 更好地帮用户工作。

**核心洞察**（Tang 提出）：LLM 是大语言模型，叙事方法可能优于结构化方法。如果 AI 不能有效利用提取出的知识，提取再精确也毫无价值。

## 核心研究问题

**提取出的知识以什么形式交付给 AI 消费，效率最高？**

具体子问题：

### Q1: 结构化 vs 叙事体 vs 混合 — 哪种格式对 LLM 消费效率最高？
- LLM 处理 YAML/JSON 卡片 vs 自然语言段落 vs 混合格式，哪种任务表现更好？
- 有没有学术实验直接比较过不同上下文格式对 LLM 输出质量的影响？
- LLM 的 Transformer 架构对不同文本结构的注意力分布有什么规律？

### Q2: 现有工具的知识注入格式是什么？
- CLAUDE.md 是叙事体（自然语言段落 + Markdown 结构）
- .cursorrules 是规则列表
- Cursor @docs 的文档索引用什么格式注入？
- GitHub Copilot 的 Knowledge Bases 用什么格式？
- Superpowers（obra/superpowers）的 SKILL.md 是什么格式？效果如何？
- 这些工具的格式选择背后有什么设计理由？

### Q3: 上下文注入的位置、长度、结构对 LLM 注意力的影响？
- "Lost in the Middle" 现象：LLM 对上下文中间部分注意力衰减
- 知识放在 system prompt vs user message vs 独立 section 有什么差异？
- 知识块的长度 vs AI 实际利用率的关系？
- 分块注入（按需检索）vs 一次性注入的 tradeoff

### Q4: 不同知识类型是否适合不同的消费格式？
- 事实型知识（命令、API）→ 列表/表格可能更好？
- 规则型知识（IF/THEN）→ 结构化规则可能更好？
- 哲学型知识（WHY、心智模型）→ 叙事体可能更好？
- 踩坑型知识（UNSAID）→ 案例故事可能更好？
- 有没有"知识类型 × 消费格式"的最优矩阵？

### Q5: Doramagic 现有实验数据能告诉我们什么？
- exp01: CLAUDE.md（叙事体）注入后 42%→96%，格式是什么？为什么有效？
- exp06/07: v0.8 vs v0.9 的 CLAUDE.md 格式差异导致了什么效果差异？
- v0.8（纯叙事）28/30 vs v0.9（三路分离：规则+叙事+速查）26/30 — 为什么结构化反而降了分？
- 现有 CC/WF/DR 卡片被 Stage 4 合成叙事时，信息保留率如何？

### Q6: 从 LLM 架构第一性原理看，什么格式最优？
- Transformer 的自注意力机制对文本结构有什么偏好？
- 预训练数据中自然语言远多于 YAML/JSON — 这对格式选择有什么启示？
- Chain-of-thought 研究对知识注入格式有什么借鉴？
- 有没有 "prompt format vs task performance" 的系统性研究？

## 三方研究分工

### Track A: Codex — 工程实践视角
重点：现有 AI 工具（CLAUDE.md、.cursorrules、Cursor、Copilot、Superpowers）的知识注入格式调研 + 上下文管理工程实践
产出：`reports/codex-report.md`

### Track B: Gemini — 用户体验与产品视角
重点：知识类型 × 消费格式的最优矩阵 + "Lost in the Middle" 等 LLM 消费限制 + 从用户到 AI 的知识传递链路分析
产出：`reports/gemini-report.md`

### Track C: Claude — 学术深度视角
重点：Transformer 注意力机制对格式的偏好 + 结构化 vs 叙事体的学术实验 + Doramagic 实验数据分析 + prompt engineering 研究
产出：`reports/claude-report.md`

## 研究产出要求

每份报告必须包含：
1. **事实发现**（带来源）
2. **格式推荐**（带理由）— 结构化/叙事体/混合，以及每种知识类型的最优格式
3. **知识类型 × 消费格式矩阵**（如果有足够数据支撑）
4. **对 Doramagic 的具体建议** — CLAUDE.md 输出应该怎么改
5. **风险和未知**

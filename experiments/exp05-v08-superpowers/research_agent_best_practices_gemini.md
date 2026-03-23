# Soul Extractor 精简研究报告

**日期**: 2026-03-10  
**方法**: 基于已收齐的 Anthropic、Google、OpenAI 官方资料，以及 RAGAS、DeepEval、Evidently、LLM-as-a-Judge 偏差研究做压缩整理。  
**说明**: 下文严格区分“有据可查”和“合理推断”。

---

## 1. 当前流程是否合理？

**有据可查**

Anthropic《Building Effective AI Agents》明确把 prompt chaining、orchestrator-workers 视为高可靠任务的主流做法；Google ADK 把 sequential pipeline 作为确定性拆解任务的典型模式；OpenAI Agents SDK / AgentKit 也强调显式 agent 边界、工具调用与可追踪执行。Soul Extractor 当前的 Stage 0→1→2→3→3.5→4→5，本质上就是“分阶段工作流 + 中间检查点”，方向是对的。

**合理推断**

Soul Extractor 不该回退到“一次性大 prompt 总结仓库”，而应继续保持分阶段流水线；但每个阶段都必须承担独立认知任务，否则阶段过多只会增加成本。当前最值得保留的是 Stage 3.5，因为它决定系统有没有真正的质量门。

## 2. 中间产物和最终产物该怎么分工？

**有据可查**

Anthropic 的 Evaluator-Optimizer 模式要求：评估结果必须能驱动生成器修改，而不是只打分不回写。Anthropic 的 Context Engineering 与 Agent Skills 也都偏向结构化、可复用、可组合的知识单元，而不是长篇叙事直接充当运行时上下文。

**合理推断**

因此，概念卡、工作流卡、规则卡应继续作为“源知识层”；`expert_narrative.md` 适合作为解释层，不应替代规则层。v0.8 的问题不是“叙事不好”，而是叙事挤掉了 CRITICAL 规则，导致最终 `CLAUDE.md` 可执行性回退。最终组装应坚持“规则优先、叙事补充”。

## 3. 当前评估标准是否合理？

**有据可查**

LLM-as-a-Judge 已被多篇研究证明存在 self-preference bias、verbosity bias 等偏差；RAGAS 强调 faithfulness、answer relevancy、context precision；DeepEval 和 Evidently 都推荐混合评估：模型评分 + 程序化检查 + 人工复核，而不是只靠模型自评。

**合理推断**

所以，当前 7 维自评只能作为辅助信号，不能作为主判据。Soul Extractor 至少还缺四类硬指标：规则覆盖率、规则可执行率、知识溯源率、任务完成率。否则就会继续出现“文本更顺了，但规则反而丢了”的错判。

## 4. 优先级建议

- **P0：把 Stage 3.5 变成真阻断门**：验证失败就退回重写；评估输出必须是结构化修改意见，而不是泛泛点评。
- **P0：给最终文档加规则锚点**：`CLAUDE.md` 前部必须保留 CRITICAL 规则区，并设最小数量阈值。
- **P1：把评估改成混合制**：脚本统计规则数、示例率、溯源率；模型评分只做辅助手段。
- **P1：拆开规则路与叙事路**：Stage 5 组装时分别注入，再按固定比例合并，避免叙事吞掉规则。
- **P2：建立 A/B 基准任务集**：比较“有注入文件”和“无注入文件”时的真实任务成功率。

## 5. 最终结论

**有据可查的总判断**：Soul Extractor 的大方向是对的——它符合官方推荐的工作流化、可追踪、可评估思路。  
**合理推断的总判断**：当前真正的问题不在“要不要多阶段”，而在“验证没有形成硬约束、叙事没有被规则约束、评估过度依赖模型自评”。

只要先修复这三个点，Soul Extractor 就会从“研究上合理”进入“工程上可靠”。

---

## 参考来源

1. Anthropic - Building Effective AI Agents  
   https://www.anthropic.com/research/building-effective-agents
2. Anthropic - Effective Context Engineering for AI Agents  
   https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
3. Anthropic - Equipping Agents with Agent Skills  
   https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
4. Anthropic Cookbook - Evaluator Optimizer Pattern  
   https://github.com/anthropics/anthropic-cookbook/blob/main/patterns/agents/evaluator_optimizer.ipynb
5. Google ADK - Multi-Agent Systems  
   https://google.github.io/adk-docs/agents/multi-agents/
6. OpenAI Agents SDK  
   https://openai.github.io/openai-agents-python/
7. OpenAI - Introducing AgentKit  
   https://openai.com/index/introducing-agentkit/
8. RAGAS 论文  
   https://arxiv.org/abs/2309.15217
9. DeepEval  
   https://github.com/confident-ai/deepeval
10. Evidently - RAG Evaluation Guide  
   https://www.evidentlyai.com/llm-guide/rag-evaluation
11. Self-Preference Bias in LLM-as-a-Judge  
   https://arxiv.org/html/2410.21819v2

# Soul Extractor Agent 研究

## 问题1：流程是否合理？

- `【证据】` 现有“多阶段 pipeline + 中间检查点”总体合理。Anthropic 推荐 `prompt chaining`、`evaluator-optimizer`；Google ADK 提供 `Sequential/Parallel/Loop Workflow Agent`；OpenAI 强调 `trace/workflow-level grading`。结论：复杂知识提取应拆成可验证子任务，而非一次性大提示词。来源：Anthropic《Building effective agents》；Google ADK《Workflow Agents》；OpenAI《Agent Evaluation Flywheel》。
- `【证据】` 中间产物可以做验证节点，但必须可硬校验。Anthropic建议步骤间加 programmatic checks；Google支持 trajectory evaluation；OpenAI主张对工具调用、handoff、最终输出分别评分。结论：Stage 3.5 若只审“文风”不审“规则保留/证据覆盖”，就会失效。来源同上，另见 Google《Evaluate trajectory》。
- `【证据】` 单模型跑全流程不符合三家主流实践；它们都强调按子任务路由给专门 agent。`【推断】` 你更适合“提取/格式化用便宜模型，哲学归纳/叙事/评审用强模型”。来源：Anthropic《Building effective agents》；OpenAI《Agents SDK quickstart》《Node reference》《Model selection guide》。
- `【证据】` 公开 RAG 实践更支持“细粒度原子知识 + 最终整合”。OpenAI/Google强调 chunking、结构化输出、可引用证据；Anthropic《Contextual Retrieval》强调给 chunk 补上下文。`【推断】` 概念卡/规则卡应是 canonical source，`expert_narrative.md` 只能是派生视图，否则会像 v0.8 一样丢 CRITICAL 规则。来源：Anthropic《Contextual Retrieval》；OpenAI《Structured Outputs guide》；Google《RAG corpora / chunking》。

## 问题2：评价标准是否合理？

- `【证据】` 仅靠 AI 自评偏差很大。Anthropic要求 rubric 做 human calibration；Google要求 judge model 与 human ratings 对齐；LangSmith强调 pairwise + annotation queues；OpenAI强调 eval flywheel。来源：Anthropic《Develop test cases》；Google《Compare judge model to human raters》；LangSmith《Pairwise evaluation》；OpenAI《Agent Evaluation Flywheel》。
- `【证据】` 你现有 7 维缺少 5 类客观指标：`faithfulness/groundedness`、`coverage/recall`、`schema compliance`、`trajectory correctness`、`stability/reproducibility`。来源：RAGAS《Faithfulness》《Response Relevancy》；Google《Evaluate trajectory》；OpenAI《Tracing module》。
- `【推断】` 建议把评分拆成“结果指标 + 过程指标”。结果：关键规则保留率、证据覆盖率、矛盾率、注入后任务成功率；过程：阶段通过率、回退率、成本、时延、pass@k 稳定性。
- `【证据】` A/B 不应只比文风，应比真实下游任务。建议固定 benchmark：设计理解、改 bug、加 feature、避坑题；比较 `无注入 vs v0.8 vs 改进版`，记录任务成功率、测试通过率、规则违规率、人工 pairwise 偏好。来源：LangSmith《Pairwise evaluation》；Google《Create pointwise / pairwise metrics》；OpenAI《Agent Evaluation Flywheel》。

## 问题3：改进方向

- `P0` 把“卡片”设为唯一事实源；Stage 4 只允许摘要，禁止改写规则。新增硬门：`CRITICAL规则保留率=100%`、`关键坑点召回率`、`矛盾率=0`。来源：Anthropic《Building effective agents》；OpenAI《Structured Outputs guide》；Google《Evaluate trajectory》。
- `P0` 把评估升级为“三层”：脚本硬校验 + LLM judge + 小规模人工 pairwise 校准；先做 20~50 个 repo gold set。来源：Google《Compare judge model to human raters》；LangSmith《Pairwise evaluation》；OpenAI《Agent Evaluation Flywheel》。
- `P0` 改成多角色/多模型：提取器、合成器、评审器分离。`【推断】` judge 最好独立于生成器。来源：Anthropic《Building effective agents》；OpenAI《Node reference》《Model selection guide》。
- `P1` 每张卡必须绑定源码/issue/README 证据，最终叙事只能引用已绑定证据，降低“像专家但不可执行”的幻觉。来源：Anthropic《Contextual Retrieval》；RAGAS《Faithfulness》。
- `P1` 加入稳定性评估：同一 repo 多次运行，统计 pass@3、方差、最差分位数。来源：OpenAI《Agent Evaluation Flywheel》；Google《Create model-based metrics》。
- `P2` 对高质量输入引入早停：硬指标达阈值时跳过重复软审查，避免验证空转。`【推断】`

## 优先级排序

- `P0` 卡片事实源化 + CRITICAL 规则硬门
- `P0` 混合评估体系（硬校验/LLM judge/人工 pairwise）
- `P0` 多角色/多模型拆分
- `P1` source-linked evidence 与覆盖率指标
- `P1` 稳定性与 pass@k 评估
- `P2` 高分样本早停优化

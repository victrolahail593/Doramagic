# Agentic 提取 MVP 设计 — 三方研究综合报告

> 日期：2026-03-15
> 三方：Claude Opus（知识工程+系统架构）/ Gemini（产品+UX）/ Codex（工程实现+算法）

---

## 一、五项全票共识

### 共识 1：混合架构 — 新增 Stage 1.5 Agent Loop

三方全票推荐：**不替代现有管线，在 Stage 1 和 Stage 2 之间插入 Agent Exploration Loop。**

- **Claude**（方案 D）：Stage 0 广度 + Agent 深度，向后兼容，有清晰降级路径
- **Codex**（方案 C）：受约束的定向探索环，不是完全自主
- **Gemini**：认同分层，建议包装为"Fast Scan vs Deep Dive"双轨

```
Stage 0 → Stage 1（广度扫描+假说生成）→ [NEW] Stage 1.5（Agent Loop）→ Stage 2-3 → Stage 3.5 → Stage 4-5
```

**结论**：管线结构不变，只加一个 Stage。能力升级，本质不变。

### 共识 2：假说驱动探索，不是自由漫游

- **Claude**：假说列表是显式的、可追溯的、可审计的
- **Codex**：hypotheses.jsonl 作为 Agent 的任务清单
- **Gemini**："带着疑问翻阅代码的侦探"

**结论**：Stage 1 产出 hypothesis_list → Agent 按列表执行 → 不是让 Agent 自己决定做什么。假说质量是真正瓶颈。

### 共识 3：WHY 和 UNSAID 从 Agentic 受益最大

- **Claude**：WHY=极高（假说→证据循环），UNSAID=高（反模式搜索）；WHAT/STRUCTURE=低
- **Codex**：WHY/UNSAID 需要跨文件因果链，单遍做不到
- **Gemini**：UNSAID 是"命中一次就成死忠粉"的核心高光时刻

**结论**：MVP 优先验证 WHY 和 UNSAID 的提取质量提升。

### 共识 4：工具集最小化

- **Claude**：3 工具（file_read + search + list_dir）
- **Codex**：5 工具（read_artifact + list_tree + search_repo + read_file + append_finding）
- **Gemini**：认同 Harness 原则"工具越少越好"

**结论**：MVP 3-5 工具。Codex 的 read_artifact 和 append_finding 有工程价值（减少路径噪音 + 结构化记录发现），建议采纳 Codex 的 5 工具方案。

### 共识 5：失败可降级到当前管线

- **Claude**：Agent Loop 失败 → fallback 到纯 Stage 1 输出，不比现在差
- **Codex**：弱模型可执行受约束的探索，或完全回退
- **Gemini**：给用户选择权（Fast Scan / Deep Dive）

**结论**：Agentic 不是 all-or-nothing。降级路径必须从第一天就设计好。

---

## 二、各方独有最佳贡献

### Claude 独有：理论框架 + 体系整合

1. **第一性原理判断**：Agentic 解决的是"输入不足"而非"处理深度不足"。Session 24-25 数据支撑：Stage 0 改进（输入）+0.7，Prompt 改进（处理）+0.3。

2. **专家认知四阶段模型**：定向扫描(30s) → 假说驱动探索(5-20min) → 线索追踪(按需) → 模型修正(持续)。LLM 最适合前两个阶段。

3. **探索模式适合度矩阵**：假说驱动=高 / 系统性扫描=高 / 好奇心驱动=中 / 经验匹配=低（幻觉来源） / 社会线索=低

4. **repo_facts.json 三重角色扩展**：初始知识 + 假说种子（"16 个 skill 但 README 只提 8 个 → WHY 假说"）+ fact-checking 基线

5. **成本模型**：~2x 增幅。python-dotenv $0.06→$0.11，wger $0.17→$0.31。

6. **收益递减预测**：第 1-3 轮 60%，第 4-7 轮 30%，第 8+ 轮 10%。建议小项目 5 轮，大项目 10 轮。

7. **弱模型降级方案**：MiniMax 用增强版 Stage 0（Haiku 辅助采样），不进 Agent Loop。

8. **Build-for-deletion 分析**：假说 prompt / 工具调用上限 / exploration_log 强制记录 / INFERENCE 标记 — 都应可插拔。

9. **"假说质量是真正瓶颈"**：Agent 再强，假说不好也没用。

10. **"代码考古学"隐喻**：比"代码分析"更准确——提取的是设计决策的历史和理由。

### Codex 独有：工程深度

1. **5 工具完整 schema**：read_artifact / list_tree / search_repo / read_file / append_finding，每个有 JSON input/output 定义。

2. **Filesystem-as-memory 完整设计**：
   - `hypotheses.jsonl`：待验证假说
   - `exploration_log.jsonl`：工具调用记录（事实层）
   - `claim_ledger.jsonl`：已确认/已反驳/待定的知识声明
   - `evidence_index.json`：证据→文件→行号→假说的索引
   - `context_digest.md`：压缩后的当前理解（给下一轮 fresh context）

3. **短轮次交互模式**：不靠长对话记忆，每轮 fresh context + 读文件记忆。解决弱模型长上下文退化。

4. **三层 Budget 设计**：硬 budget（工具调用上限）+ 软 budget（token 上限）+ 信息增益 budget（连续 N 轮无新发现则停止）。Budget 减少时自动切换策略。

5. **每种知识类型的具体探索算法**：WHAT→广度扫描 / HOW→调用链追踪 / IF→config+validation 搜索 / WHY→commit+注释中的因果链 / UNSAID→error pattern+deprecation+workaround

6. **Stage 3.5 claim traceability 增强**：每条 claim 必须引用 exploration_log entry，无证据标 INFERENCE。

7. **A/B 测试设计 + 6 个衡量指标**。

8. **风险缓解方案**：死循环检测、假说质量降级、模型不稳定的 fallback。

### Gemini 独有：产品体验 + 市场定位

1. **"剧场效应"（Theater Effect）**：实时展示 Agent 探索过程。不是 loading 圈，是"办案实况直播"：
   - `[10:05] Agent 提出假说：项目似乎有自研路由引擎`
   - `[10:06] 正在深入 /src/router 寻找证据...`
   - `[10:12] 发现冲突：README 说用 React Router，代码中有未注明的自研 Hook`
   - **过程透明度本身就是产品价值。**

2. **"Fast Scan vs Deep Dive" 双轨**：
   - Fast Scan：3 分钟，WHAT+HOW，"这项目干嘛的"
   - Deep Dive：20 分钟，WHY+UNSAID，"我要不要抄这个"
   - **给用户选择权 = 不教用户做事。**

3. **竞品差异化定位**：
   - Cursor/Copilot = 建设者（帮你写代码）
   - Devin/SWE-agent = 修理工（帮你修 bug）
   - **Doramagic = 考古学家+哲学家（帮你理解设计决策）**
   - Doramagic 提取的灵魂可以**喂给** Cursor/Devin，是它们的"上位知识供给者"

4. **定价模型**：Free=静态单遍（2MB 上限）/ Pro=每月 X 次 Agentic / Pay-as-you-go / BYOK

5. **"专家会诊"多模型包装**：对用户可见——"研究员 Sonnet 完成全量检索，移交首席架构师 Opus 做哲学提炼..."

6. **"提取即测试"副产品**：Agent 发现"根据路由定义应该有控制器，但翻遍代码也没找到"→ 这是架构级 Bug 发现，不只是知识提取。

7. **用户线索注入**：探索过程中允许用户实时干预——"不要看 docs 目录，重点看 src/core/engine"。

8. **动态交互式架构地图**：Agent 的"脚印"可渲染为可交互的代码探索地图。

---

## 三、分歧与决策建议

### 分歧 1：工具数量

- **Claude**：3 工具（file_read + search + list_dir）
- **Codex**：5 工具（+read_artifact + append_finding）

**决策建议：采 Codex 5 工具。** read_artifact 减少路径噪音，append_finding 让发现结构化入库。额外 2 个工具的复杂度极低，但工程价值明显。

### 分歧 2：成本预估

- **Claude/Codex**：~2x 增幅（可控）
- **Gemini**：5-10x 增幅

**决策建议：采 Claude/Codex 估算。** Gemini 的估算缺乏具体 token 计算。混合架构下 Agent 只做定向深挖，不是全量重读，2x 是合理预估。

### 分歧 3：Gemini 的"用户线索注入"

- **Gemini**：允许用户实时干预 Agent 探索
- **Claude/Codex**：未提及

**决策建议：V2+ 探索。** 好概念，但 MVP 优先验证 Agent 自主探索质量。交互式探索需要实时 UI，当前 Telegram 触发不支持。

### 分歧 4：Gemini 的"提取即测试"

- **Gemini**：Agent 发现架构不一致性 = Bug 检测副产品
- **Claude/Codex**：未提及

**决策建议：记录但不优先。** 有趣的发散方向，但 MVP 聚焦知识提取质量，不额外承诺 Bug 检测。如果自然发生，作为 bonus 展示。

### 分歧 5：MVP 工时

- **Claude**：5 天（3-4 架构 + 1-2 测试）
- **Codex**：5-7 天

**决策建议：预估 5-7 天。** 含测试和调优。

---

## 四、直接采纳清单

| 来源 | 采纳内容 | 优先级 |
|------|---------|--------|
| 三方 | 混合架构：Stage 1.5 Agent Loop | MVP 核心 |
| 三方 | 假说驱动探索（hypothesis_list） | MVP 核心 |
| 三方 | 失败降级到现有管线 | MVP 核心 |
| Claude | "输入不足"而非"处理深度不足"（定位） | 设计指导 |
| Claude | repo_facts.json 三重角色 | MVP |
| Claude | 弱模型降级为增强 Stage 0 | MVP |
| Claude | Build-for-deletion 可插拔设计 | MVP |
| Claude | 成本模型（~2x） | 规划参考 |
| Claude | 收益递减预测（5 轮/10 轮默认） | MVP 配置 |
| Codex | 5 工具 + JSON schema | MVP 实现 |
| Codex | Filesystem-as-memory（5 个中间文件） | MVP 实现 |
| Codex | 短轮次交互 + fresh context | MVP 实现 |
| Codex | 三层 Budget 设计 | MVP 实现 |
| Codex | Stage 3.5 claim traceability | MVP 实现 |
| Codex | A/B 测试设计 + 6 指标 | MVP 验证 |
| Gemini | "剧场效应"实时探索展示 | V1.1（Telegram 可做简化版） |
| Gemini | Fast Scan / Deep Dive 双轨 | V1.1 产品设计 |
| Gemini | 竞品定位：考古学家+哲学家 | 产品叙事 |
| Gemini | 定价：Free 静态 / Pro Agentic / BYOK | 商业模型 |

---

## 五、MVP 定义（整合三方）

### 范围

**Stage 1 扩展 + Stage 1.5 新增 + Stage 3.5 增强**

| 组件 | 类型 | 内容 |
|------|------|------|
| STAGE-1 | 修改 | 新增 Q8：生成 hypothesis_list.json（3-5 个假说） |
| Stage 1.5 Agent Loop | **新增** | 脚本编排 + 单轮 LLM 调用 × N 轮 |
| 5 个中间文件 | **新增** | hypotheses.jsonl / exploration_log.jsonl / claim_ledger.jsonl / evidence_index.json / context_digest.md |
| 5 个工具 | **新增** | read_artifact / list_tree / search_repo / read_file / append_finding |
| validate_extraction.py | 修改 | +check_claims_have_evidence()（~30 行） |
| STAGE-3.5 | 修改 | 增加 claim traceability 验证 |
| STAGE-4 | 修改 | 合成时参考 CONFIRMED claims |

**不改动**：Stage 0 / prepare-repo.sh / assemble-output.sh / Stage 2/3/M/C/F

### 验证方式

A/B 对照：3 个项目（python-dotenv 小 / wger 大 / 1 个 SEO 项目中）
- A组：当前单遍提取
- B组：Agentic 提取（Stage 1.5）
- 评分：现有 4 维 WHY Rubric + UNSAID 新增维度
- 成功标准：WHY 评分提升 ≥ 0.5 / 大项目信息保留度显著提升 / Agent 走偏率 < 10%

### 工时

**5-7 个工作日**（含 A/B 测试）

### 降级策略

| 模型能力 | 策略 |
|---------|------|
| Sonnet/Opus/GPT-4 | 完整 Agent Loop |
| MiniMax/弱模型 | 增强 Stage 0（Haiku 辅助采样），跳过 Agent Loop |
| Agent Loop 失败 | 回退到纯 Stage 1 输出 |

---

## 六、一句话总结

> Agentic 提取 = 让 Stage 0 从"猜你想看什么"变成"你说想看什么我就给你看"。只加一个 Stage 1.5，5 个工具，5 个中间文件，5-7 天工程量。假说质量是瓶颈，不是 Agent 能力。

# Agentic 提取 MVP 设计 — 知识工程 + 系统架构视角

**研究员**: Claude Opus (知识工程 + 系统架构)
**日期**: 2026-03-15
**基于**: research-brief.md + Soul Extractor 全部技术笔记 + WHY 提取实验 + Agent Harness 分析 + SEO 实际提取样例 + 当前 SKILL.md

---

## 1. 第一性原理分析：Agentic 提取的本质

### 专家翻代码的认知过程

一个资深工程师第一次接手陌生代码库时，认知过程可以拆成四个阶段：

1. **定向扫描**（30 秒）：README、目录结构、依赖文件 → 形成"这是什么"的初始假说
2. **假说驱动探索**（5-20 分钟）：带着假说去翻入口文件、核心模块 → 验证/修正/深化
3. **线索追踪**（按需）：发现可疑设计 → 追踪调用链 → 读 commit message → 理解"为什么这样做"
4. **模型修正**（持续）：新发现与已有理解冲突 → 修正心智模型 → 回头重新解读之前看过的代码

关键观察：**专家不是从头读到尾，而是在假说和证据之间反复跳跃。** 阅读量可能只是全部代码的 5-15%，但选择看什么的决策质量极高。

### 可建模的探索模式

| 模式 | 描述 | LLM Agent 适合度 | 理由 |
|------|------|------------------|------|
| 假说驱动 | 先猜再验证 | **高** | LLM 天然擅长生成假说，工具调用可验证 |
| 系统性扫描 | 按结构遍历所有模块 | **高** | 可编程，确定性强 |
| 好奇心驱动 | 看到反常 → 深入 | **中** | LLM 能识别反常，但容易过度发散 |
| 经验匹配 | "这个模式我见过" | **低** | 依赖预训练知识，不可控，幻觉来源 |
| 社会线索 | 问同事、读 PR 讨论 | **低** | 需要外部数据源，当前不可行 |

### Agentic 提取解决的核心问题

**这不是"处理深度不足"，是"输入信息不足"。** 第一性原理证据：

1. Session 24-25 WHY 实验：Stage 0 v2 改进输入后，8 条 WHY 全部是新发现（v1/v2 从未出现）。Prompt 改进（处理深度）仅 +0.3，Stage 0 改进（输入信息）+0.7。
2. funNLP 案例：5.3→7.63 (+44%)，**最大提升来自 Stage 0 改进，不是 Prompt 改进**。
3. marketingskills：55K 行截取到 5K，90% 信息丢失 → 静态采样的硬天花板。

但有一个重要补充：**输入信息的价值取决于选择策略**。不是"看得越多越好"，而是"看对的东西"。Agentic 提取的本质是用 LLM 的理解能力来**指导采样**，让 Stage 0 从"猜你想看什么"变成"你说想看什么我就给你看"。

---

## 2. 架构方案对比

### 方案 A：Stage 0 增强（更智能的采样，仍是单遍）

**具体设计**：在 stage0-v2.sh 基础上，增加第五层——语义采样。用轻量模型（Haiku）先读目录结构和 README，生成"重点关注文件列表"，然后 shell 脚本按列表采样。

- **优势**：改动最小，与现有管线完全兼容，成本增加微小（一次 Haiku 调用）
- **劣势**：仍是单遍，无法根据提取中间发现调整采样；Haiku 的"重点文件判断"质量未知
- **复杂度**：1-2 天
- **Trade-off**：低风险低收益，天花板仍在

### 方案 B：单 Agent 多轮迭代

**具体设计**：一个 Agent 拥有 file_read + grep + list_dir 工具，从 Stage 1 开始自主探索代码库。每轮读取若干文件 → 更新知识提取 → 决定下一步读什么 → 直到达到 budget 上限或自判"信息饱和"。

- **优势**：最接近"专家翻代码"的认知模型；上下文在单 Agent 内连贯
- **劣势**：单 Agent 上下文窗口有限，大项目（wger 1123 文件）容易溢出；迷路风险高——Agent 可能在无关代码中打转；MiniMax 等弱模型在长上下文下表现急剧退化
- **复杂度**：3-5 天
- **Trade-off**：理论最优但工程风险最高，弱模型可行性存疑

### 方案 C：多 Agent 协作

**具体设计**：按知识类型分配 Agent——WHY Agent 读 commit history + 设计文档、UNSAID Agent 读 issues + error handling、STRUCTURE Agent 做模块地图。各 Agent 独立探索，最后合并结果。

- **优势**：天然并行（已在 SEO 4 路提取中验证），每个 Agent 的上下文更聚焦
- **劣势**：Agent 之间缺乏信息共享（WHY Agent 发现的线索 UNSAID Agent 看不到）；结果合并有冲突风险；管线复杂度指数级增长
- **复杂度**：5-8 天
- **Trade-off**：并行度高但协调成本高，过早复杂化

### 方案 D：混合架构（Stage 0 广度 + Agent 深度）【推荐】

**具体设计**：

```
Stage 0（确定性）→ Stage 1（单遍，广度扫描）→ Agent Loop（深度探索）→ Stage 3.5+（验证）→ Stage 4/5（合成）
```

Stage 0 保持现有 prepare-repo.sh + repomix，提供全局视图（目录结构 + 依赖关系 + 结构性文件 + repo_facts.json）。Stage 1 在 repomix 压缩包上做一次广度扫描，产出初始 soul discovery（Q1-Q7）+ 一份"深度探索计划"（hypothesis_list）。然后进入 Agent Loop：Agent 拿到 hypothesis_list，逐条用工具验证/深化，每验证一条假说产出带证据的 knowledge_claim，直到 budget 耗尽或所有假说已处理。

- **优势**：
  - Stage 0 的广度保证不遗漏（已验证的四层漏斗继续工作）
  - Agent 只在"已知值得深挖"的方向上投入 token（假说驱动，不乱翻）
  - 与现有管线向前兼容——Agent Loop 是 Stage 1.5，不替代任何现有 Stage
  - 假说列表是显式的、可追溯的、可审计的
  - Agent 探索失败时，fallback 到纯 Stage 1 输出，不会比现在更差
- **劣势**：
  - 需要设计"假说生成"的 prompt（Agent Loop 的质量取决于假说质量）
  - 增加了管线的执行时间（从 4-5 分钟到预估 8-12 分钟）
- **复杂度**：3-4 天
- **Trade-off**：中等复杂度，高兼容性，有清晰的降级路径

**推荐理由**：方案 D 是唯一同时满足三个硬约束的方案——(1) 代码说事实（Stage 0 确定性基础不变），(2) 能力升级本质不变（管线结构不变，只加一个 Stage），(3) 弱模型可行（假说列表是显式的，弱模型只需按列表执行工具调用，不需要自主规划）。

---

## 3. 知识类型与探索策略

### 各知识类型的探索策略分析

| 知识类型 | 当前来源 | Agentic 受益度 | 最佳探索策略 | 理由 |
|---------|---------|---------------|-------------|------|
| WHAT (概念) | repomix 单遍 | **低** | 广度扫描即可 | 概念通常在 README + 顶层代码中已经足够，SEO 4 项目验证单遍即可产出高质量 WHAT |
| HOW (工作流) | repomix 单遍 | **中** | 调用链追踪 | 需要跨文件追踪（入口→核心→出口），但 repomix 已包含大部分信息 |
| IF (规则) | repomix + community | **中** | config + validation 文件搜索 | 规则散落在 config/validation/error handling 中，grep 可以高效定位 |
| STRUCTURE (模块) | 目录结构 + import | **低** | 确定性提取 | repo_facts.json + 目录分析已覆盖，不需要 LLM 动态探索 |
| **WHY (设计哲学)** | repomix 单遍 | **极高** | **假说→证据循环** | WHY 藏在 commit message、PR 讨论、代码注释的因果链中，单遍看不到跨文件因果关系。Session 24-25 实验证明 Stage 0 v2 让 funNLP 8 条 WHY 全部是新发现——更多信号 = 更多 WHY |
| **UNSAID (暗坑)** | community signals | **高** | **反模式搜索** | UNSAID 藏在 error handling pattern、deprecation warning、workaround comment 中。vnpy 0%/35% 严格/宽松覆盖率说明单遍+社区信号远远不够 |

### 结论：按知识类型分 Agent 还是一个 Agent 综合探索？

**MVP 阶段用一个 Agent 综合探索，按假说类型标注。** 理由：

1. 知识类型之间不是独立的——WHY 的发现往往触发 UNSAID 的线索（"为什么要加这个 workaround"→ "因为这个坑"）。分 Agent 会切断这种线索传递。
2. SEO 4 路并行成功是因为 4 个项目互相独立。同一项目内 6 类知识不独立。
3. 方案 D 的假说列表天然支持标注类型（hypothesis_type: WHY/UNSAID/HOW），不需要物理分 Agent 来实现类型化探索。

**未来优化方向**：当单 Agent 的上下文不够时（超大项目），可以按"模块"而非"知识类型"分 Agent——每个 Agent 负责一个子系统，综合提取该子系统的所有知识类型。这与 Doramagic 的"按问题域拆解"原则一致。

---

## 4. Agent Harness 原则的应用

### "代码说事实，AI 说故事"在 Agentic 架构中如何落地

当前管线中，这个原则的分工是：

- **事实层**（代码说）：repo_facts.json（确定性提取命令/skill/入口点）、validate_extraction.py（硬校验）、stage0-v2.sh（结构性文件采样）
- **故事层**（AI 说）：Stage 1 灵魂发现、Stage 2-3 卡片生成、Stage 4 叙事合成

Agentic 架构新增一个维度：**Agent 的工具调用是事实层，Agent 的假说和解读是故事层。** 具体落地：

1. Agent 每次工具调用的返回值自动记录到 `exploration_log.jsonl`（事实层，可审计）
2. Agent 基于工具返回值生成的 knowledge_claim 必须引用至少一条 exploration_log entry（证据绑定）
3. 无证据的 claim 自动标记为 `INFERENCE`，进入 Stage 3.5 fact-checking gate 审查

这直接解决了 exp07 的核心教训——MiniMax 幻觉 `/plugin marketplace add` 通过验证是因为没有证据绑定。Agentic 架构下，Agent 必须 `grep "marketplace"` 找到源码才能声称命令存在。

### Agent 的自由度边界

| 维度 | 自主决定 | 硬约束 |
|------|---------|--------|
| 读哪个文件 | 是（基于假说列表） | 不能超出 repo 目录 |
| 搜索什么关键词 | 是 | 无约束 |
| 假说是否已验证 | 是（但必须附证据） | 验证结论格式固定：CONFIRMED/REFUTED/INCONCLUSIVE |
| 是否继续探索 | 是（直到 budget 耗尽） | 总工具调用次数硬上限 |
| 产出什么知识 | 否 | 必须按 knowledge_claim schema 输出 |
| 跳过某个假说 | 是（标注 SKIPPED + 原因） | 不能跳过 WHY/UNSAID 类型的假说 |

### 简化工具集

Vercel 的经验：工具从 15 砍到 2，准确率 80%→100%。Soul Extractor Agent 的最小工具集：

1. **file_read(path, start_line?, end_line?)**：读取文件片段
2. **search(pattern, path?, file_glob?)**：ripgrep 式搜索
3. **list_dir(path, depth?)**：列出目录结构

三个工具，不需要更多。理由：
- 不需要 AST 解析——Stage 0 v2 已经有 Python AST 提取，Agent 阶段只需要读结果
- 不需要 git log——可在 Stage 0 确定性提取 commit messages 到 `repo_facts.json`
- 不需要执行代码——Soul Extractor 是知识提取，不是测试
- search 替代 grep + find，一个工具覆盖两个场景

### Build for Deletion

以下 Agentic 组件应设计为可插拔/可移除：

| 组件 | 当前功能 | 何时可删除 | 设计要求 |
|------|---------|-----------|---------|
| 假说生成 prompt | 引导 Agent 探索方向 | 模型自主规划能力达到专家水平 | 假说列表是独立文件，不嵌入 Agent prompt |
| 工具调用次数上限 | 防止 Agent 发散 | 模型自判信息饱和能力可靠 | 上限是配置参数，不是硬编码 |
| exploration_log 强制记录 | 证据绑定 | 模型幻觉率降到可忽略 | log 是 sidecar 机制，不侵入 Agent 逻辑 |
| INFERENCE 标记分流 | 区分有证据/无证据的 claim | 模型不再产生无证据 claim | 标记逻辑在 Stage 3.5，不在 Agent 内部 |

---

## 5. 与已有体系的整合

### 各 Stage 的 Agentic 化决策

| Stage | 当前实现 | 是否 Agentic 化 | 理由 |
|-------|---------|----------------|------|
| Stage 0 | prepare-repo.sh + repomix + repo_facts.json | **保持不变** | 确定性基础，Agent 探索的前置条件。已验证有效。 |
| Stage 1 | 单遍广度扫描 (Q1-Q7) | **保持 + 扩展输出** | 继续做广度扫描产出 soul，新增 hypothesis_list 输出作为 Agent 的探索计划 |
| **NEW: Stage 1.5** | 不存在 | **新增 Agent Loop** | 核心变革点。Agent 按 hypothesis_list 动态探索代码库 |
| Stage 2 | 概念卡 + 工作流卡 | **保持不变** | 概念/工作流从 Stage 1 + Stage 1.5 的增强输入中获益，但 Stage 2 本身不需要 Agent |
| Stage 3 | 规则卡 | **保持不变** | 同上 |
| Stage 3.5 | 验证硬阻断 | **增强** | 新增 exploration_log 交叉验证——Stage 1.5 的 claim 必须在 log 中有对应工具调用 |
| Stage 4 | 专家叙事合成 | **保持不变** | 合成阶段不需要 Agent，但输入更丰富了 |
| Stage M | 模块地图 | **保持不变** | 确定性提取为主 |
| Stage C | 社区智慧 | **保持不变** | 依赖社区信号，不依赖代码探索 |
| Stage F | 组装 | **保持不变** | 确定性脚本 |

**只动一个点：新增 Stage 1.5。** 这符合"能力升级，本质不变"原则。

### repo_facts.json 在 Agentic 架构中的定位

repo_facts.json 的定位从"Stage 3.5 的 fact-checking whitelist"扩展为：

1. **Agent 的初始知识**（读取后减少重复探索——已知的命令/skill/入口点不需要 Agent 再发现）
2. **假说生成的锚点**（"repo_facts 发现 16 个 skills，但 README 只提到 8 个——为什么有 8 个未文档化的 skill？"→ 自动生成 WHY 类假说）
3. **Stage 3.5 的事实校验基线**（不变）

这是"确定性提取为骨架，LLM 做解读"原则在 Agentic 架构下的自然延伸。

### Stage 3.5 适配 Agentic 多轮输出

当前 Stage 3.5 校验的是 Stage 2-3 输出的卡片。Agentic 架构下，Stage 1.5 也会产出 knowledge_claim。适配方式：

1. Stage 1.5 的 claim 写入 `<output>/soul/claims/` 目录（与 `cards/` 平行）
2. validate_extraction.py 新增 `check_claims_have_evidence()` 函数——每条 claim 的 `evidence` 字段必须引用 exploration_log 中的真实条目
3. 无证据的 claim 标记为 `INFERENCE`，不参与 Stage 4 叙事合成的"设计哲学"部分（只能作为"推测"出现）

改动量：validate_extraction.py 新增约 30 行，不影响现有逻辑。

### 跨项目智能是否影响 Agentic 设计

**当前不影响，但未来会协同。** 理由：

- 跨项目智能（fingerprint, compare_projects）工作在项目间关系层面，Agent 工作在单项目深度层面，两者正交
- 但未来协同点明确：当领域知识图谱积累后，Agent 的假说可以从图谱中获取——"SEO 领域的其他项目都有 sitemap 生成功能，这个项目有吗？"→ 自动生成 IF/UNSAID 假说
- 这是第二飞轮的自然延伸，但 MVP 阶段不需要考虑

---

## 6. 成本模型

### 单遍 vs Agentic Token 消耗对比

**python-dotenv（小项目，~2K 行代码）**

| 方案 | 输入 token | 输出 token | 总 token | 预估成本 (Sonnet) |
|------|-----------|-----------|---------|------------------|
| 当前单遍 | ~15K (repomix) | ~5K (cards + soul) | ~20K | $0.06 |
| Agentic (5 轮) | ~15K (初始) + ~15K (5×3K 文件读取) | ~8K (claims + cards) | ~38K | $0.11 |
| **增幅** | | | **+90%** | **+$0.05** |

**wger（大项目，12MB/1123 文件）**

| 方案 | 输入 token | 输出 token | 总 token | 预估成本 (Sonnet) |
|------|-----------|-----------|---------|------------------|
| 当前单遍 | ~50K (repomix 压缩) | ~8K | ~58K | $0.17 |
| Agentic (10 轮) | ~50K + ~40K (10×4K) | ~12K | ~102K | $0.31 |
| **增幅** | | | **+76%** | **+$0.14** |

关键发现：**成本增幅在 2x 以内**，但预期质量增幅来自 WHY 实验的数据——Stage 0 信号增加带来 +0.7~1.0 分提升。ROI 明显正向。

### 收益递减曲线预测

基于第一性原理推理（非实测数据，需 exp09 验证）：

- **第 1-3 轮**：高价值。验证核心假说（设计哲学、主要模式、入口逻辑），新信息密度高。预测收益 ~60% of total。
- **第 4-7 轮**：中价值。追踪边缘假说、验证细节规则。新信息密度下降但仍有增量。预测收益 ~30% of total。
- **第 8+ 轮**：低价值。大部分假说已处理，Agent 倾向重复确认已知信息。预测收益 ~10% of total。

**建议 MVP 默认 budget：小项目 5 轮，大项目 10 轮。** 以假说列表清空为主要终止条件，轮次上限为硬兜底。

### 弱模型（MiniMax）在 Agentic 模式下的可行性

**可行，但需要降级处理。** 分析：

1. **工具调用能力**：MiniMax-M2.5 已成功执行 Soul Extractor 全部 6 个 Stage（exp07/exp08），包括运行 bash 脚本。工具调用基本可靠。
2. **假说质量风险**：MiniMax 的假说可能比 Sonnet 更浅层/更泛化——但这不致命，因为假说是由 Stage 1 在 repomix 上下文中生成的，不需要预训练知识。
3. **幻觉风险**：exp07 证明 MiniMax 对不熟悉的项目(superpowers)幻觉严重，但对熟悉的项目(wger)正常。Agentic 模式下，Agent 必须从工具返回值中提取信息，**理论上能约束幻觉**——但需要实验验证。
4. **上下文管理风险**：MiniMax 在长上下文下的表现未知。10 轮探索可能累积 ~100K token 上下文，弱模型处理能力存疑。

**降级方案**：MiniMax 使用 Stage 0 增强方案（方案 A），不进入 Agent Loop。成本增加极小（一次 Haiku 调用 ~$0.001），但能从更好的采样中获益。Agent Loop 仅对 Sonnet/Opus/GPT-4 级模型开放。

这不是歧视弱模型，是对用户负责——注入错误知识比不注入更危险（exp07 的 26/30→15/30 教训）。

---

## 7. MVP 定义

### 范围

**Agentic 提取 MVP = Stage 1 输出扩展 + Stage 1.5 Agent Loop + Stage 3.5 增强**

具体改动清单：

| 组件 | 改动类型 | 具体内容 |
|------|---------|---------|
| STAGE-1-essence.md | 修改 | Stage 1 新增 Q8："列出 3-5 个你最想深入了解的问题/假说"→ 输出 hypothesis_list.json |
| Stage 1.5 Agent Loop | **新增** | 新脚本/prompt：读取 hypothesis_list.json → 循环调用工具验证 → 输出 claims.jsonl + exploration_log.jsonl |
| SKILL.md | 修改 | 在 Stage 1 和 Stage 2 之间插入 Stage 1.5 |
| validate_extraction.py | 修改 | 新增 check_claims_have_evidence() 约 30 行 |
| STAGE-3.5-review.md | 修改 | 提及 claims/ 目录的验证 |
| STAGE-4-synthesis.md | 修改 | 合成时参考 claims.jsonl 中 CONFIRMED 的条目 |

**不改动**：prepare-repo.sh、assemble-output.sh、Stage 0/2/3/M/C/F、repo_facts.json 提取逻辑。

### 文件格式定义

**hypothesis_list.json**：
```json
[
  {
    "id": "H-001",
    "type": "WHY",
    "question": "为什么项目选择了自定义解析器而不是用标准库 configparser？",
    "initial_evidence": "Stage 1 观察到 src/parser.py 有 500+ 行自定义解析逻辑",
    "search_plan": ["读取 src/parser.py 的注释", "搜索 configparser 关键词", "检查 git log 中 parser 相关 commit"]
  }
]
```

**exploration_log.jsonl**（每行一条工具调用记录）：
```json
{"timestamp": "...", "hypothesis_id": "H-001", "tool": "search", "args": {"pattern": "configparser", "path": "."}, "result_summary": "0 matches found", "tokens_used": 312}
```

**claims.jsonl**（每行一条知识声明）：
```json
{"claim_id": "C-001", "hypothesis_id": "H-001", "type": "WHY", "statement": "项目选择自定义解析器因为需要支持 shell 变量展开语法，configparser 不支持", "confidence": "CONFIRMED", "evidence": ["exploration_log entry 3: src/parser.py:45 注释 '# shell-style variable expansion'", "exploration_log entry 7: tests/test_parser.py 有 15 个 shell expansion 测试用例"], "source_files": ["src/parser.py:45", "tests/test_parser.py"]}
```

### 验证方式：A/B 对照

**实验设计（exp09）**：

- **项目选择**：python-dotenv（小项目/已有 baseline）+ wger（大项目/已有 baseline）+ 1 个新项目（消除记忆效应）
- **A 组**：当前管线（Stage 0→1→2→3→3.5→4→F），Sonnet
- **B 组**：Agentic 管线（Stage 0→1→1.5→2→3→3.5→4→F），Sonnet
- **评估指标**：
  1. WHY 提取评分（4 维度 Rubric，已验证鲁棒）
  2. UNSAID 覆盖率（严格 + 宽松，与 exp 已有数据对比）
  3. 新增信息量（B 组中有多少 claim 是 A 组完全没覆盖的）
  4. 幻觉率（无证据 claim 的比例）
  5. Token 消耗对比
- **判定标准**：WHY 评分 +0.5 以上且幻觉率不增加 → Agentic 方案验证通过

### 工时估算

| 任务 | 工时 | 说明 |
|------|------|------|
| hypothesis_list.json 格式 + Stage 1 prompt 修改 | 0.5 天 | 在现有 STAGE-1-essence.md 基础上增加 Q8 |
| Stage 1.5 Agent Loop prompt + 编排逻辑 | 1.5 天 | 核心工作。需要设计 Agent 的系统 prompt + 工具调用循环逻辑 |
| exploration_log + claims.jsonl 输出机制 | 0.5 天 | Agent prompt 中要求结构化输出 |
| validate_extraction.py 增强 | 0.5 天 | 新增 evidence 校验函数 |
| Stage 3.5/4 修改 | 0.5 天 | 适配新增文件 |
| exp09 A/B 对照实验执行 + 评估 | 1.5 天 | 3 个项目 × 2 组 × 评分 |
| **总计** | **5 天** | |

### 技术实现关键决策

**Agent Loop 用 LLM 对话循环还是脚本编排？**

推荐用**脚本编排 + LLM 单轮调用**，而非 LLM 自主对话循环。理由：

1. 确定性编排层是难点 3 的结论——"不逼模型执行脚本，把关键步骤放到确定性编排层"
2. 脚本编排更容易控制 budget（Python 循环计数 vs LLM 自判"够了吗"）
3. 每轮 fresh context 防止上下文污染（Superpowers 的 fresh-subagent-per-task 模式）

具体实现：

```
# 伪代码
hypotheses = load("hypothesis_list.json")
for h in hypotheses:
    if budget_exhausted(): break
    # 单轮 LLM 调用：给定假说 + 工具 → 产出 exploration actions + claim
    result = llm_call(
        system="你是代码考古学家。验证以下假说，使用提供的工具。",
        user=f"假说：{h.question}\n初始证据：{h.initial_evidence}\n搜索计划：{h.search_plan}",
        tools=[file_read, search, list_dir],
        max_tool_calls=5  # 每个假说最多 5 次工具调用
    )
    log_exploration(result.tool_calls)
    save_claim(result.claim)
```

**OpenClaw 兼容性**：Stage 1.5 的编排逻辑用 Python 脚本实现（与 prepare-repo.sh 和 validate_extraction.py 模式一致）。OpenClaw 的子代理执行脚本能力已在 exp08 中验证。

---

## 8. 新洞察

### 8.1 假说质量是 Agentic 提取的真正瓶颈

Brief 聚焦于"Agent 能不能有效探索代码"，但更关键的问题是"Agent 知道要探索什么"。假说生成的质量决定了 Agentic 提取的上限。

**案例分析**：geo-seo-claude 的灵魂提取（CLAUDE.md 167 行）中，最有价值的洞察是"品牌提及 > 反向链接（Ahrefs 数据，相关性 0.737 vs 0.266）"。这个洞察来自 `brand_scanner.py` 中硬编码的研究数据。一个好的假说（"为什么品牌扫描器的权重高于技术 SEO？"）能直接引导 Agent 到这段代码。一个差的假说（"这个项目用了什么技术栈？"）只会产出 WHAT 级别的表层信息。

**启示**：Stage 1 的 Q8（假说生成）需要精心设计 prompt，引导 LLM 生成 WHY/UNSAID 类型的假说，而非 WHAT/HOW 类型。可以用 repo_facts.json 的"意外发现"作为种子——比如"repo_facts 检测到 16 个 skill 但 README 只文档化了 8 个"，自动转为假说。

### 8.2 "代码考古学"比"代码分析"更准确

Agentic 提取的隐喻不应该是"AI 分析师读代码"，而是"AI 考古学家挖掘遗址"。考古学家的方法论：

1. 先做地表调查（Stage 0 + Stage 1）
2. 在可疑位置开探沟（Agent Loop 按假说定向挖掘）
3. 每件出土物标注地层和坐标（exploration_log）
4. 基于出土物重建历史（Stage 4 叙事合成）
5. 区分"出土物说了什么"和"考古学家解读了什么"（代码说事实，AI 说故事）

这个隐喻比"专家翻代码"更精确，因为它强调了**证据绑定**和**解读的有限性**。考古学家从不声称"我知道这个人在想什么"，只说"基于这些证据，最合理的解释是..."。Soul Extractor 的 WHY 提取应该采用同样的认识论姿态。

### 8.3 Agentic 提取暗示了 Soul Extractor 的架构分层

当前管线是线性的：Stage 0→1→2→3→3.5→4→M→C→F。加入 Agent Loop 后，架构自然分成三层：

1. **感知层**（Stage 0 + Agent Loop）：从代码库中获取信息。确定性采样 + 动态探索。
2. **理解层**（Stage 1 + Stage 2-3）：将信息转化为结构化知识（卡片、规则、概念）。
3. **表达层**（Stage 4 + Stage M/C/F）：将知识编译为可消费的格式（CLAUDE.md、叙事、模块地图）。

这个分层在当前管线中是隐含的，Agentic 化让它变得显式。它的价值在于：**每层可以独立演进**。感知层可以从 3 个工具扩展到 10 个（加入 git log、AST 解析等），理解层可以从单模型变成多模型融合（GDS），表达层可以从 CLAUDE.md 扩展到 project_fingerprint.json——彼此不耦合。

### 8.4 exploration_log 是飞轮的隐藏资产

exploration_log.jsonl 记录了"AI 考古学家看了什么、发现了什么"。这份 log 在当前 MVP 中只用于 Stage 3.5 证据验证。但长期看，它是一份**高价值的训练数据**：

- 哪些假说被确认了？哪些被否定了？→ 优化假说生成 prompt
- Agent 平均几次工具调用验证一个假说？→ 优化 budget 分配
- 哪些类型的文件最常被读取？→ 优化 Stage 0 采样策略
- 不同项目的探索模式有什么共性？→ 跨项目智能的新维度

**不需要额外工作**，只需要在 MVP 中确保 log 格式标准化且持久保存。这是"Build for Accumulation"——log 今天是审计工具，明天是优化燃料。

### 8.5 Stage 1.5 的 Agent 不需要是"通用 Agent"

Brief 的隐含假设是 Agent 需要像 Claude Code 或 Manus 一样具备通用代码理解能力。但 Soul Extractor 的 Agent 是**极度专用的**——它只做一件事：验证关于代码设计决策的假说。

这意味着 Agent 的系统 prompt 可以非常聚焦：

> 你是代码考古学家。你的任务是验证关于这个项目的假说。你只能使用 file_read、search、list_dir 三个工具。对每个假说，你必须给出 CONFIRMED/REFUTED/INCONCLUSIVE 的结论，并列出支持结论的证据（文件路径 + 行号 + 引用文本）。不要猜测。如果工具返回的信息不足以得出结论，回答 INCONCLUSIVE。

这种极度聚焦的 Agent 比通用 Agent 更可靠，因为它的行动空间极小——只有三个工具，只有三种结论。这是 Vercel "工具越少越好"经验在 Soul Extractor 上的具体落地。

---

## 关键 Trade-off 汇总

| 决策 | 选择 | 放弃了什么 | 为什么值得 |
|------|------|-----------|-----------|
| 方案 D（混合）vs 方案 B（纯 Agent） | 保留 Stage 0 确定性基础 | Agent 的完全自主性 | 可控性 > 灵活性，降级路径清晰 |
| 单 Agent vs 多 Agent | 单 Agent 综合探索 | 并行度 | 知识类型间的线索传递比并行更重要 |
| 脚本编排 vs LLM 自主循环 | 脚本编排 | LLM 的动态规划能力 | 确定性控制 > 灵活性，弱模型也能跑 |
| 3 工具 vs 更多工具 | 最小工具集 | AST 解析、git log 等高级能力 | Vercel 经验：工具越少越好，Stage 0 已覆盖高级需求 |
| WHY/UNSAID 优先 vs 全类型 | 假说优先 WHY/UNSAID | WHAT/HOW/IF 的深度 | 高价值知识优先，低价值知识单遍已足够 |
| MiniMax 降级方案 A vs 全模型统一 | 弱模型用增强 Stage 0 | 弱模型的 Agentic 体验 | 注入错误知识比不注入更危险（exp07 教训） |
| Stage 1.5（新增）vs 替代 Stage 1 | 新增而非替代 | 管线简洁性 | 向前兼容，Agent 失败时 fallback 到纯 Stage 1 |
| 假说驱动 vs 自由探索 | 假说驱动 | Agent 发现"意外惊喜"的可能性 | 可控性 > 偶然发现，防止在大项目中迷路 |

---

## 附录：与现有实验数据的连接

| 实验 | 关键数据点 | 对 Agentic MVP 的启示 |
|------|-----------|---------------------|
| exp01 (python-dotenv) | 无 soul 42%→Full soul 96% | Soul 提取有效，Agentic 提升空间大（96% 天花板可能来自输入不足） |
| exp06/07 (superpowers) | MiniMax 15/30 vs 无注入 26/30 | 证据绑定是生死线，exploration_log 必须实现 |
| exp08 (wger) | MiniMax traceability 100% | 弱模型在熟悉项目上可靠，但假说质量可能低 |
| WHY 实验 Session 24-25 | Stage 0 v2: funNLP +44%, 8 条新 WHY | 输入信号增加 = WHY 质量跃升，Agentic 预期收益 +0.7~1.0 |
| SEO 4 路并行 | 4 个项目各 4-5 分钟，质量不错 | 小项目单遍已足够，Agentic 主要服务大项目 |
| Agent Harness 分析 | Vercel 工具 15→2，准确率+20% | 3 工具足够，不要过度工具化 |

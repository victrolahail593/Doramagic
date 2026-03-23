# 跨项目智能研究报告

> 研究员：Claude Opus 4.6
> 日期：2026-03-15
> 视角：知识工程 + 产品架构

---

## 一、从实验数据中看到的核心现象

先把四份灵魂提取结果摊开来看，不急着下结论。

### 1.1 知识的三层分布

在 4 个 SEO/GEO 项目的灵魂提取结果中，知识自然形成三个层次：

**共识层（4/4 或 3/4 项目独立提到）**：
- FAQPage schema 2023 年 8 月限制（4/4）
- HowTo schema 废弃（3/4：claude-seo, 30x-seo, geo-seo-claude）
- AI 爬虫不执行 JS（3/4：geo-seo-claude, claude-seo, 30x-seo）
- 134-167 词最优段落长度（3/4：geo-seo-claude, claude-seo, 30x-seo）
- YouTube 品牌提及相关性 0.737（3/4：geo-seo-claude, claude-seo, 30x-seo）
- Princeton GEO 研究数据：数据引用 +40%（2/4：marketingskills, claude-seo）

**架构层（项目间共享的设计模式）**：
- 并行子代理架构（4/4 都用了，但独立设计）
- 按需加载 reference 文件（3/4：claude-seo, 30x-seo, marketingskills）
- hooks 自动拦截废弃 schema（2/4：claude-seo, 30x-seo——但这两个实际上是同源项目）

**独创层（仅 1 个项目拥有）**：
- geo-seo-claude：citability scoring 引擎（5 维度量化评分）+ Brand Surface Area 概念
- marketingskills：product-marketing-context 共享底板（33 个 skill 的单一事实来源）
- claude-seo/30x-seo：validate-schema.py PostToolUse hook（代码层面拦截废弃 schema）

这个分布不是巧合。它揭示了一个深层结构：**领域知识天然具有共识-分化的双重特性**。共识层代表领域的"物理定律"（Google 的规则变更、AI 爬虫的技术限制），独创层代表项目的"工程选择"（如何响应这些定律）。

### 1.2 claude-seo 与 30x-seo：一个天然的控制实验

这两个项目的高度相似性其实是一个意外的礼物——它提供了一个控制实验：

| 维度 | claude-seo | 30x-seo | 解读 |
|------|-----------|---------|------|
| Stars | 2.3k | 11 | 人气不代表原创性 |
| Commits | 48 | 25 | 工程投入差异不大 |
| 子代理数 | 7 | 6 | 架构几乎一致 |
| Python 脚本 | 4 个（fetch_page, parse_html, analyze_visual, capture_screenshot）| 相同 4 个 | 代码层面高度重合 |
| Hooks | validate-schema.py + pre-commit-seo-check.sh | 相同 | 质量控制逻辑一致 |
| 相同 Bug | YAML frontmatter 前有 HTML 注释 | 相同 | 共享同一代码基 |
| 灵魂差异 | E-E-A-T 权重/GEO 子代理 seo-geo 更详细 | squirrelscan 依赖/24 vs 12 子技能 | 差异集中在包装层，不在核心知识 |

灵魂提取在这里做到了一件传统代码比较工具做不到的事：**它暴露了两个项目在知识层面的同源性，而不仅仅是代码层面的相似性**。代码可以重写、变量可以改名、文件结构可以调整——但灵魂（设计哲学、踩坑经验、领域知识的选择与编排）难以伪装。

---

## 二、知识指纹：理论基础与数据结构

### 2.1 为什么"知识指纹"不是代码指纹

代码重复检测（MOSS、JPlag、Copycat）工作在语法/token 层面——它比较的是表达形式。知识指纹需要工作在语义层面——它比较的是认知结构。

用一个具体例子说明差异：

```
# geo-seo-claude 的表达
"134-167 词是 AI 引用最优段落长度"
（出现在 citability_scorer.py 的评分逻辑中）

# marketingskills 的表达
"AI 引用的段落长度甜蜜区间" + Princeton GEO 研究引用
（出现在 ai-seo skill 的框架描述中）

# claude-seo 的表达
"passage 可引用性（134-167 词最优）"
（出现在 seo-geo agent 的分析维度中）
```

三个项目用不同的语言、在不同的文件中、以不同的结构表达了同一条领域知识。代码指纹完全无法识别这种等价关系。知识指纹必须能在语义层面做这种比对。

### 2.2 知识指纹的数据结构设计

我提议的知识指纹不是一个扁平的向量，而是一个**结构化的知识声明（Knowledge Claim）**：

```
KnowledgeClaim {
  // 核心内容
  claim_text: string          // 规范化的知识断言
  claim_type: enum {          // 6 类知识对象（对齐 Doramagic 已有框架）
    CAPABILITY,               // 能做什么
    RATIONALE,                // 为什么这样设计
    CONSTRAINT,               // 什么条件下成立
    INTERFACE,                // 怎么连接
    FAILURE,                  // 哪里会坏
    ASSEMBLY_PATTERN          // 验证过的组合方式
  }

  // 来源与置信度
  source_project: string
  evidence: Evidence[]        // 代码行号/文档引用/社区链接
  confidence: enum { SUPPORTED, CONTESTED, WEAK, REJECTED }

  // 语义锚定
  domain_tags: string[]       // 领域标签（如 "seo", "schema", "ai-crawlers"）
  specificity: float          // 0.0（通用常识）到 1.0（高度项目特定）
  temporal_validity: {        // 时效性
    introduced: date?,
    deprecated: date?,
    last_confirmed: date
  }

  // 比对用的语义向量
  embedding: float[768]       // 用于跨项目语义匹配
}
```

**为什么是这个结构？**

1. `claim_type` 对齐 Doramagic 已确立的 6 类知识对象，不是新发明，是已有架构的自然延伸。
2. `specificity` 是公约数提取的关键字段——低 specificity 的 claim 更可能是跨项目共识。
3. `temporal_validity` 直接来自 SEO 领域的教训——这 4 个项目中大量知识带有时效性（FAQPage 限制、FID 废弃、HowTo 移除）。缺少时效标记的知识是暗雷。
4. `embedding` 是计算层面的实现需求，但不能单独依赖它——纯向量相似度无法区分"相同知识"和"相关知识"。

### 2.3 知识指纹的生成过程

关键洞察：**知识指纹不应该是灵魂提取之后的附加步骤，而应该在提取过程中同步生成。**

当前 Soul Extractor 的 Stage 1-3 已经在做类型化提取（WHY/概念/规则），Stage 4 合成叙事。知识指纹的生成应该发生在 Stage 1-3 的输出端：

```
Stage 1 (WHY/Design Philosophy) → Rationale claims
Stage 2 (Concepts) → Capability + Interface claims
Stage 3 (Rules) → Constraint + Failure claims
Stage 0 (repo_facts.json) → Capability claims（确定性）
```

每个 Stage 的输出，除了已有的卡片格式，同步生成 KnowledgeClaim 对象。这些对象是跨项目对比的原子单元。

---

## 三、公约数提取：算法框架

### 3.1 从朴素匹配到置信度模型

朴素方法：对 N 个项目的所有 KnowledgeClaim 做两两语义相似度比较，相似度超过阈值的归为一组，被 K 个以上项目覆盖的组就是"公约数"。

问题：这是 O(N^2 * M^2) 的复杂度（N 个项目，每个 M 条 claim），而且纯语义匹配的假阳性很高。

**我提议的分层匹配算法：**

```
Phase 1: Coarse Clustering（粗粒度聚类）
  - 按 domain_tags 分桶：相同领域标签的 claims 才进入比对
  - 时间复杂度：O(M * N)

Phase 2: Semantic Matching（语义匹配）
  - 桶内按 embedding 做 approximate nearest neighbor
  - 阈值：cosine similarity > 0.85 视为候选匹配
  - 时间复杂度：O(K * log K)，K 是桶内 claim 数

Phase 3: Structural Alignment（结构对齐）
  - 候选匹配进入结构化比对：
    - claim_type 一致性检查
    - specificity 差异检查（差异过大 = 可能不是同一层级的知识）
    - temporal_validity 一致性检查（一个说有效、一个说废弃 = 冲突而非共识）
  - 这一步排除假阳性

Phase 4: Consensus Scoring（共识评分）
  - 通过 Phase 3 的匹配组，计算共识置信度：

    ConsensusConfidence = f(
      coverage_ratio,           // 覆盖率：K/N 个项目提到
      independence_score,       // 独立性：项目间无 fork/抄袭关系
      evidence_diversity,       // 证据多样性：不同类型的证据
      temporal_consistency,     // 时间一致性：没有版本冲突
      specificity_agreement     // 粒度一致性：都在同一抽象层级
    )
```

### 3.2 独立性评分：解决"假公约数"

**Brief 中提到的"假公约数"风险是真实的，而且比想象中严重。**

4 个 SEO 项目都提到"134-167 词最优段落长度"。这看起来是 4 个独立验证。但实际上：

1. claude-seo 和 30x-seo 是同源的（疑似 fork）——应该算 1 票，不是 2 票
2. 这个数据点可能都源自同一篇研究——如果 4 个项目引用的是同一个 source，那不是"4 次独立验证"，是"1 个源头的 4 次传播"

**独立性评分算法：**

```python
def independence_score(claim_group: list[KnowledgeClaim]) -> float:
    """
    评估一组 claims 的来源独立性。

    三个维度：
    1. 项目独立性：排除 fork/抄袭关系
    2. 证据独立性：不同类型的证据（代码实现 vs 文档引用 vs 社区讨论）
    3. 源头独立性：是否引用不同的原始研究/数据
    """
    # 1. 项目去重：用"项目打架"的结果排除同源项目
    independent_projects = deduplicate_by_origin(claim_group)
    project_independence = len(independent_projects) / len(claim_group)

    # 2. 证据类型多样性
    evidence_types = set()
    for claim in independent_projects:
        for e in claim.evidence:
            evidence_types.add(e.type)  # CODE, DOC, COMMUNITY, EXTERNAL
    evidence_diversity = len(evidence_types) / 4.0

    # 3. 源头追溯（最关键也最难的部分）
    # 如果所有 claims 都引用同一个 URL/论文/数据集，independence 应大幅降低
    upstream_sources = extract_upstream_citations(independent_projects)
    source_independence = 1.0 - max_source_concentration(upstream_sources)

    return (project_independence * 0.3 +
            evidence_diversity * 0.3 +
            source_independence * 0.4)
```

源头独立性（source_independence）的权重最高，因为它直接对应"假公约数"的根因：所有人都引用了同一个错误的源头。

### 3.3 一个具体的假公约数案例

在 4 个项目中，"YouTube 品牌提及相关性 0.737"被 3 个项目提到。追溯来源，全部指向"Ahrefs 2025 年 12 月对 75,000 个品牌的研究"。

这是 1 个来源的 3 次传播，不是 3 次独立验证。

如果 Ahrefs 的研究方法有偏差（比如只测了英语市场、只测了特定行业），这个"共识"就是一个假公约数。正确的处理是：标记 `source_independence = 低`，输出时注明"多项目引用同一研究，非独立验证"。

这不意味着这条知识是错的——它可能完全正确。但 Doramagic 应该诚实地告知用户这条知识的置信度基础。

---

## 四、灵魂 Diff：项目打架的判断维度

### 4.1 打架的 4 种情况

Brief 正确识别了 fork、致敬、独立趋同、共同上游依赖四种情况，但缺少一个判断框架。我把它扩展为一个决策树：

```
输入：两个项目 A, B 的灵魂提取结果

Step 1: 代码层面检查（确定性，不需要 LLM）
  ├─ 共享 commit hash? → Fork（直接证据）
  ├─ 共享相同 bug pattern（如 YAML frontmatter 注释 bug）? → 疑似 Fork
  ├─ 共享相同文件名 + 函数签名? → 疑似 Fork 或共同模板
  └─ 以上都不满足 → 进入 Step 2

Step 2: 知识层面检查（需要灵魂提取结果）
  ├─ 设计哲学相似度 > 0.9?
  │   ├─ 实现细节也高度相似 → 致敬/参考
  │   └─ 实现完全不同 → 独立趋同（哲学相近但工程路径不同）
  ├─ 共享知识 > 70% 但各有 >15% 独创? → 同领域竞品
  └─ 共享知识集中在某个子集? → 共同上游依赖

Step 3: 时间线检查（元数据辅助判断）
  ├─ A 创建时间 << B 且 B 的独创知识少? → B 可能 fork A
  ├─ A, B 创建时间相近? → 独立趋同可能性高
  └─ 两者都引用同一个更早的项目/规范? → 共同上游
```

### 4.2 灵魂 Diff 的输出格式

灵魂 diff 不应该只是"相似 vs 不同"的二分法。我建议输出一个结构化的对比报告：

```
SoulDiff {
  relationship: enum { FORK, TRIBUTE, CONVERGENT, COMPETITORS, COMPLEMENTARY }

  shared_knowledge: KnowledgeClaim[]    // 共享的知识（公约数）
  a_only: KnowledgeClaim[]             // A 的独创知识
  b_only: KnowledgeClaim[]             // B 的独创知识
  conflicts: ConflictPair[]            // 矛盾的知识

  recommendation: {
    if_need_one: "A" | "B" | "either"  // 只选一个该选谁
    if_can_combine: string             // 组合使用建议
    caution: string[]                  // 注意事项
  }
}
```

以 claude-seo vs geo-seo-claude 为例：

```
{
  relationship: COMPETITORS,
  shared_knowledge: [
    "FAQPage 2023-08 限制",
    "AI 爬虫不执行 JS",
    "134-167 词最优段落长度",
    "YouTube 品牌提及 0.737",
    "并行子代理架构",
    ...
  ],
  a_only: [  // claude-seo 独有
    "validate-schema.py PostToolUse hook",
    "E-E-A-T 权重框架（Experience 20%/Expertise 25%/Authority 25%/Trust 30%）",
    "DataForSEO 扩展系统",
    "SSRF 防护 + 路径遍历防护",
    "squirrelscan 依赖（via 30x-seo 共享）"
  ],
  b_only: [  // geo-seo-claude 独有
    "citability_scorer.py 5 维度评分引擎",
    "Brand Surface Area 概念",
    "brand_scanner.py 多平台品牌扫描",
    "PDF 报告生成器（面向代理机构）",
    "GEO 综合评分权重体系（AI 可引用性 25% + 品牌权威 20% + ...）"
  ],
  conflicts: [
    {
      topic: "SEO 评分权重",
      a_says: "技术 SEO 25%, AI 搜索可见性 5%",      // claude-seo/30x-seo
      b_says: "AI 可引用性 25%, 技术基础 15%",        // geo-seo-claude
      interpretation: "反映了不同的产品定位——claude-seo 偏传统 SEO，geo-seo-claude 偏 AI 搜索"
    }
  ],
  recommendation: {
    if_need_one: "取决于用户关注传统 SEO 还是 AI 搜索优化",
    if_can_combine: "geo-seo-claude 的 citability 引擎 + claude-seo 的 hooks 体系 + marketingskills 的共享上下文底板",
    caution: ["claude-seo 与 30x-seo 高度重合，不要同时安装"]
  }
}
```

### 4.3 权重冲突：一个比预期更有价值的发现

在对比中我发现了一个 brief 没有提到但极其重要的信号：**同领域项目在评分权重上的分歧，暴露了领域内部的路线之争。**

| 维度 | claude-seo/30x-seo | geo-seo-claude | marketingskills |
|------|-------------------|----------------|-----------------|
| 技术 SEO 权重 | 25% | 15% | （无综合评分，但 seo-audit 优先级：可抓取 > 技术 > 页面 > 内容 > 权威） |
| AI 搜索权重 | 5% | 25% | （ai-seo 是独立 skill，与 seo-audit 平行） |
| 品牌/权威权重 | -（隐含在内容 25%）| 20%（独立维度）| -（无独立维度） |

这种权重分歧不是"谁对谁错"——它反映了 2026 年 SEO 领域正在发生的范式转移：传统 SEO（以 Google 排名为中心）vs GEO（以 AI 引用为中心）。

**Doramagic 可以做的不仅是报告分歧，还可以把分歧本身作为高价值知识输出。** "这个领域的从业者在 X 问题上有路线分歧"本身就是 WHY 层知识——甚至可能是最有价值的 WHY 层知识。

---

## 五、"项目打架"的用户场景与决策框架

### 5.1 用户的真实决策场景

想象一个 Technical Marketer 在 2026 年面对的实际选择：

> "我需要给 Claude Code 装一个 SEO skill。GitHub 搜出来 4 个候选。我该选哪个？"

当前的解决方案：看 Stars、看 README、看最后更新时间、看 Issues 活跃度。这些信号充满噪音（claude-seo 2.3k stars vs 30x-seo 11 stars，但它们几乎是同一个东西）。

Doramagic 可以提供的解决方案：

```
用户输入: 4 个 GitHub URL
Doramagic 输出:
  1. 关系图：claude-seo ≈ 30x-seo（疑似同源），其余独立
  2. 去重后的独立项目：geo-seo-claude, marketingskills, claude-seo
  3. 每个项目的独创价值
  4. 公约数知识（无论选哪个都需要知道的领域共识）
  5. 推荐组合（如果可以混合使用）
  6. 路线分歧（领域内未达成共识的争议点）
```

这里有一个非常关键的产品洞察：**"公约数"和"独创知识"的分离，让用户可以做出理性的知识投资决策。**

公约数 = 无论选择哪个项目都需要知道的东西（领域必修课）。
独创知识 = 选择特定项目才能获得的额外知识（各项目的附加值）。

这完全对齐了 Doramagic "不教用户做事，给他工具" 的哲学——不是告诉用户"你应该选 A"，而是给用户足够的信息让他自己做决定。

### 5.2 超越"选哪个"的场景

项目打架能力的用途远不止"帮用户选技术栈"：

**场景 1：领域知识审计**
> 一个 SEO 代理机构想验证自己团队的知识是否过时。把自己内部的 SEO playbook（可以是一组文档或 skill）和 4 个开源项目做灵魂 diff——看看自己遗漏了什么、保留了什么过时知识。

**场景 2：技术尽职调查**
> 投资人在评估一个 SEO 工具的 startup 时，用 Doramagic 把该 startup 的开源组件与市场上的竞品做灵魂 diff——独创知识的数量和质量直接反映技术壁垒。

**场景 3：知识编译（最有前景的场景）**
> 用户不是在"选一个"，而是想"从多个中提炼最好的"。Doramagic 从 N 个项目中提取公约数 + 各项目最佳独创知识，编译出一份超越任何单个项目的知识包。

场景 3 值得特别关注，因为它代表了一种全新的知识生产方式：**多源知识编译**。这不再是"抄一个好作业"，而是"从多个作业中提炼出最佳答案"。

---

## 六、对 Doramagic 产品定位的战略影响

### 6.1 这是范式转变，不是渐进演化

Brief 问了一个关键问题："从单项目知识提取器到多项目知识图谱——是渐进演化还是范式转变？"

我的判断：**这是范式转变。**

理由：

1. **价值主张变了。** 单项目提取的价值主张是"让 AI 理解一个项目"。跨项目智能的价值主张是"让 AI 理解一个领域"。这是量变到质变——领域级知识的可靠性、覆盖度、实用价值都远超单项目知识。

2. **竞争壁垒变了。** 单项目灵魂提取的壁垒在"提取质量"（Soul Extractor 的工程能力）。跨项目智能的壁垒在"知识网络效应"——提取的项目越多，公约数越可靠，独创知识的对比越精确。后者是一个飞轮，前者不是。

3. **产品边界变了。** 单项目提取是一个工具。跨项目智能开始具有平台特性——它需要积累项目数据、维护知识图谱、追踪知识的时效性。

但范式转变不意味着需要推倒重来。Doramagic 当前的架构（6 类知识对象、类型化提取、Knowledge Compiler）恰好是跨项目智能的基础设施。KnowledgeClaim 结构自然地从已有的知识对象模型演化而来。

### 6.2 重新审视飞轮模型

之前确立的飞轮模型是：

```
用户需求 → 搜索已有 skill → 灵魂提取 → 新 skill 诞生 → 下一个用户搜到
```

跨项目智能给飞轮增加了一个新的循环：

```
N 个已提取项目 → 跨项目分析 → 领域知识图谱 → 新项目提取时自动比对
                                              → 知识图谱更精确
                                              → 进一步吸引同领域项目
```

这是一个第二飞轮，而且它有一个关键特性：**它在特定领域内加速。** SEO 领域提取的项目越多，对 SEO 新项目的分析就越准确，就越能吸引 SEO 从业者使用 Doramagic，就有更多 SEO 项目被提取。

这意味着 Doramagic 的增长策略可能应该是"按领域深耕"而非"广撒网"——先在一个垂直领域（比如 SEO/GEO）建立密集的知识图谱，形成明显的网络效应，再扩展到下一个领域。

### 6.3 对"好作业"评判体系的修正

跨项目智能改变了"好作业"的定义。之前的增量价值公式：

```
EHV = Gate * NeedFit * SourceValue * MarginalGain / AcquisitionCost
```

现在需要增加一个新维度：**NetworkValue（网络价值）**。

一个项目的价值不仅取决于它自身的知识质量，还取决于它与已有知识图谱的关系：
- 如果它能验证已有知识 → 提升公约数的置信度
- 如果它带来独创知识 → 扩展知识图谱的覆盖面
- 如果它与已有项目冲突 → 暴露潜在的路线分歧（也是有价值的）

```
EHV_v2 = Gate * NeedFit * SourceValue * MarginalGain * NetworkValue / AcquisitionCost
```

其中：

```
NetworkValue = f(
  consensus_reinforcement,  // 对已有共识的验证强度
  novelty_contribution,     // 独创知识的新鲜度
  conflict_informativeness, // 冲突的信息量
  domain_coverage_gap       // 对知识图谱盲区的覆盖
)
```

---

## 七、Brief 中没有提到的可能性

### 7.1 知识时效追踪：跨项目智能的自然延伸

4 个 SEO 项目共同暴露了一个巨大的问题：**SEO 知识衰减极快**。HowTo schema 2023 年 9 月废弃、FAQPage 2023 年 8 月限制、FID 2024 年 3 月被 INP 替代、SpecialAnnouncement 2025 年 7 月废弃……

当你有多个项目的灵魂时，你可以做一件单项目做不到的事：**追踪知识的生命周期**。

```
KnowledgeLifecycle {
  first_appeared: { project: "A", date: "2023-03" }
  confirmed_by: [
    { project: "B", date: "2023-06" },
    { project: "C", date: "2024-01" },
  ]
  deprecated_by: { project: "D", date: "2024-09" }

  status: DEPRECATED
  replacement: KnowledgeClaim("INP replaces FID")
}
```

如果 Doramagic 在 2024 年 6 月提取了一个 SEO 项目，其 CLAUDE.md 中说"优化 FID"。到了 2024 年 10 月又提取了另一个项目，发现它说"FID 已被 INP 替代"。Doramagic 可以自动回溯更新第一个项目的知识状态。

**这是多项目知识图谱的杀手级功能之一：单个项目可能不知道自己的知识已过时，但领域级知识图谱可以追踪到这一点。**

### 7.2 知识供应链分析

这 4 个项目的知识有一个有趣的供应链结构：

```
上游源头（学术/行业研究）
├── Ahrefs 2025 研究 → YouTube 品牌提及 0.737
├── Princeton GEO (KDD 2024) → 关键词堆砌 -10%, 数据引用 +40%
├── Google 官方变更 → FAQPage 限制、HowTo 废弃、INP 替代 FID
├── Gartner 预测 → 传统搜索流量 2028 年下降 50%
└── SparkToro 数据 → 来源未详

中游项目（提取对象）
├── geo-seo-claude → 选择性引用 Ahrefs + Google，加入自研的 citability 评分
├── marketingskills → 选择性引用 Princeton + Google，加入 context 底板设计
├── claude-seo/30x-seo → 全面引用以上，加入 hooks 自动化
└── 彼此之间可能也有引用关系

下游消费者（安装 skill 的用户）
└── 依赖中游项目的知识筛选和编排
```

Doramagic 在这个供应链中的独特位置是：**它是唯一能看到整个供应链的角色。** 用户只看到自己安装的一个项目；项目作者只看到自己引用的上游源头。Doramagic 看到所有项目、所有引用关系、所有知识传播路径。

这意味着 Doramagic 可以做知识供应链分析：
- 哪些上游源头被高度依赖？（单点故障风险）
- 哪些知识在传播过程中被扭曲了？（电话游戏效应）
- 哪些项目是知识的原创者，哪些只是传播者？

### 7.3 "反向公约数"：异常检测

公约数是"多数项目都认同的知识"。但**只有一个项目提到而其他项目都没提到的知识，同样值得关注**。

有两种可能：
1. 它是错的（幻觉/过时/特殊场景）→ 应该降低置信度
2. 它是对的但极少人知道（真正的独创洞察）→ 应该高亮为高价值知识

如何区分？靠证据链：

```python
def classify_outlier(claim: KnowledgeClaim, domain_graph: KnowledgeGraph) -> str:
    if claim.confidence == WEAK and claim.evidence_count < 2:
        return "SUSPECT"      # 可能是幻觉
    if claim.temporal_validity.introduced > domain_graph.latest_consensus_date:
        return "EMERGING"     # 可能是新发现，太新还没传播
    if claim.specificity > 0.8:
        return "NICHE"        # 可能只在特定场景下成立
    if claim.evidence_count >= 2 and claim.confidence == SUPPORTED:
        return "UNIQUE_INSIGHT"  # 有证据支撑的独创洞察
    return "NEEDS_REVIEW"
```

举例：geo-seo-claude 的 "Brand Surface Area 概念"在其他 3 个项目中完全没有对应物。但它有 Ahrefs 研究数据支撑、有代码实现（brand_scanner.py）。这应该被分类为 UNIQUE_INSIGHT，在输出中高亮标注。

### 7.4 领域成熟度指标

当你有一个领域内足够多项目的灵魂时，公约数的比例本身就是一个有价值的元指标：

- **公约数比例高**（>70%）→ 领域知识已高度收敛，选择哪个项目差异不大，用户需要的是"标准知识包"
- **公约数比例低**（<30%）→ 领域知识高度分散，可能是新兴领域或方法论尚未统一，用户需要的是"探索地图"
- **公约数比例中等但冲突多** → 领域正在经历范式转移（正是 SEO→GEO 的现状）

Doramagic 可以输出领域成熟度报告：

```
Domain: SEO/GEO for AI Agents (2026-03)
Maturity: TRANSITIONAL (公约数 45%, 冲突 15%, 独创分散 40%)
Interpretation: 传统 SEO 知识已高度收敛（schema 规则、CWV 阈值），
              但 AI 搜索优化（GEO）方法论仍在快速演化。
              权重分配是主要分歧点（AI 可见性应占多少权重）。
```

---

## 八、盲区与风险

### 8.1 灵魂提取质量是一切的基础

跨项目智能的所有能力都建立在单项目灵魂提取的质量之上。如果提取本身有系统性偏差（比如 LLM 过度推理），那跨项目对比会放大而非修正偏差。

具体到这 4 个项目：灵魂提取结果的格式和内容质量相当一致，但我注意到一些可疑的模式——比如所有 4 个项目的"设计哲学"部分都非常流畅、因果完整。这可能是 LLM 在 Stage 1 做了过度推理（暗雷 #1）。在跨项目对比时，如果两个项目的"设计哲学"相似，到底是真的设计哲学相似，还是 LLM 用类似的叙事模式润色了本质不同的设计？

**建议：跨项目对比应该优先使用 Stage 0-3 的结构化产物（repo_facts.json、知识卡片），而非 Stage 4 的叙事合成。叙事是给人看的；对比应该用原始数据。**

### 8.2 领域边界问题

4 个 SEO/GEO 项目是同一领域的，所以公约数提取很自然。但现实中"同领域"不是二元判断：
- claude-seo 和 30x-seo 是"同一个东西"
- claude-seo 和 geo-seo-claude 是"同领域不同侧重"
- marketingskills 包含 SEO 但远不止 SEO（33 个 skill 覆盖 CRO、内容策略、广告等）

公约数提取需要先回答"这些项目在什么粒度上可比？"。marketingskills 与其他 3 个的公约数，应该只在 ai-seo 和 seo-audit 两个子技能的范围内计算，而非整个项目。

**建议：引入"对比窗口"概念——用户在启动跨项目分析时，指定（或由 Doramagic 自动推断）对比的知识范围。** 这可以通过 domain_tags 的交集来实现。

### 8.3 N 的现实约束

Brief 提到 N 个项目的两两对比是 O(N^2)。实际上，N 在大多数场景下不会太大——用户不太可能一次比较 100 个同领域项目。更现实的场景是 3-10 个项目，O(N^2) 在这个范围内完全不是问题。

真正的性能瓶颈是**灵魂提取本身**——每个项目的提取需要 LLM 多轮调用、代码分析、社区信号收集。N=10 个项目的提取可能需要数小时。

**建议：优先优化提取的增量更新能力（项目更新时只重新提取变更部分），而非跨项目对比的算法效率。**

### 8.4 还未讨论的问题：跨项目知识注入

假设 Doramagic 成功从 4 个 SEO 项目中提取了公约数 + 各项目独创知识。接下来呢？

用户拿到这些知识后，如何注入到自己的 AI agent 中？

- 公约数知识是"领域必修课"→ 应该作为基础 context 始终加载
- 独创知识是"可选扩展"→ 按需加载
- 冲突知识是"决策参考"→ 不应该注入（会混淆 AI），而应该呈现给用户做选择

这引出了一个 Knowledge Compiler 的扩展需求：不仅编译单项目的知识，还要编译跨项目的知识图谱。编译策略因知识来源不同而不同：

```
ConsensusKnowledge → 高置信度，直接注入，优先级高
UniqueInsight → 中等置信度，按需注入，标注来源
ConflictKnowledge → 不注入，呈现给用户决策
OutdatedKnowledge → 标记废弃，注入废弃信息本身（防止 AI 使用旧知识）
```

---

## 九、总结与优先级建议

### 发现级别评估

| 发现 | 影响级别 | 理由 |
|------|---------|------|
| 知识天然具有共识-分化双重特性 | **基础性** | 这不是 SEO 领域的特例，是所有知识领域的普遍结构 |
| 灵魂 diff 暴露同源关系 | **高** | Stars 不可信，灵魂比代码更难伪装 |
| 权重冲突暴露领域路线之争 | **高** | "冲突本身是高价值知识"是一个新的认知 |
| 公约数的独立性评分是防假公约数的关键 | **高** | 没有独立性评分，公约数可能比单项目知识更危险 |
| 知识时效追踪需要多项目才能实现 | **中** | 是杀手级功能，但实现复杂度高 |
| 领域成熟度指标是自然产出 | **中** | 几乎零额外成本的副产品 |
| 知识供应链分析 | **中** | 有价值但当前数据量不足以充分展现 |

### 实施优先级

1. **P0：KnowledgeClaim 数据结构**——在现有 6 类知识对象基础上增加比对所需字段（embedding、specificity、temporal_validity）。改动小，但为后续所有能力奠基。

2. **P0：灵魂 diff（项目打架）**——两两比较，输出 SoulDiff 结构。直接面向用户最高频场景（"该选哪个？"）。用 exp-seo-skills 的 4 个项目作为验证数据。

3. **P1：独立性评分 + 公约数提取**——在灵魂 diff 的基础上扩展到 N 项目公约数。需要解决源头追溯问题。

4. **P2：知识时效追踪 + 领域成熟度**——需要积累足够多的项目数据才有意义。适合在飞轮跑起来之后逐步建设。

### 最后一个观察

这次 SEO/GEO 实验的 4 个项目可能是 Doramagic 迄今为止最有战略意义的实验——不是因为它验证了灵魂提取的准确性（这在之前的实验中已经验证过了），而是因为它意外地展示了 Doramagic 的第二条增长曲线。

单项目灵魂提取是 Doramagic 的第一产品。跨项目知识图谱可能是 Doramagic 的第二产品——而且是壁垒更深的那个。

引用 Doramagic 自己的产品哲学：不教用户做事，给他工具。跨项目智能给用户的不是"你应该选 A"，而是"这是 A、B、C、D 的灵魂 X 光片，你自己看"。这恰好是灵魂 diff 该有的姿态。

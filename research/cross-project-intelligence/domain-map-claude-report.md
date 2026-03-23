# 领域共识图谱预积累 -- 战略规划 + 知识工程研究报告

> 日期: 2026-03-15
> 视角: 战略规划 + 知识工程
> 输入: domain-knowledge-map-research-brief.md + synthesis-report.md + stitchcraft-synthesis.md + 4 个 SEO 项目灵魂提取
> 约束: "不教用户做事，给他工具" / "代码说事实，AI 说故事" / "能力升级，本质不变"

---

## 零、核心判断：这不是新范式，是飞轮的燃料

Tang 的修正必须作为本报告的第一行：**跨项目智能不是范式转变，是能力升级。** synthesis-report.md 中三方一致判断"这是范式转变"，被 Tang 否决。我同意 Tang 的修正。原因如下：

1. **Doramagic 的本质未变**：提取知识 -> 注入 AI -> AI 变聪明。领域图谱只是让"提取"从单项目扩展到多项目，让"注入"从单份灵魂扩展到领域共识，本质动作没变。
2. **产品承诺未变**：给用户工具，不教用户做事。图谱是更好的工具，不是新产品形态。
3. **飞轮的连续性**：预积累是飞轮的冷启动燃料，用户贡献是飞轮的持续动力。这是同一个飞轮的两个阶段，不是两个飞轮。

但"能力升级"的幅度可能很大。从 4 个 SEO 项目的实验数据看，跨项目对比产出了单项目不可能产出的知识类型（权重冲突 = 领域路线之争、FAQPage 的 GEO 价值 vs Google 价值的分歧、独立性评分揭示假公约数）。这种知识对用户的工具价值是指数级的。

---

## 一、领域选择的优先级排序框架

### 1.1 排序公式

```
DomainPriority = DemandSignal × SupplyReadiness × ExtractabilityScore × StrategicFit
```

四个因子的定义：

| 因子 | 含义 | 量化来源 | 权重 |
|------|------|---------|------|
| DemandSignal | 有多少用户会在这个领域使用 Doramagic | OpenClaw skill 下载量 + GitHub 搜索热度 + 开发者调查 | 35% |
| SupplyReadiness | 这个领域有多少高质量开源项目可供提取 | GitHub stars >500 的项目数 + 好作业评判体系打分 | 25% |
| ExtractabilityScore | 这个领域的项目是否适合灵魂提取 | 代码/文档比例、结构化程度、社区活跃度 | 20% |
| StrategicFit | 与 Doramagic 现有能力和验证路径的匹配度 | 是否已有实验数据、是否能复用已有管线 | 20% |

### 1.2 DemandSignal 的三级指标

不能拍脑袋说"SEO 很热"。需要可量化的信号：

**L1 - 直接信号（最可靠）：**
- OpenClaw 平台上该领域 skill 的安装量和日活
- 用户在 Doramagic 中搜索该领域时的 404 率（"找不到作业"的频率正是需求信号）

**L2 - 间接信号（有参考价值）：**
- GitHub 上该领域仓库的总 star 数和过去 12 个月增速
- Stack Overflow / Reddit 上该领域问题的数量和增长率
- "awesome-X" 列表中收录项目的数量

**L3 - 趋势信号（前瞻性）：**
- 技术媒体/会议中该领域的讨论频率变化
- 大公司在该领域的开源投入（新项目发布量）
- 领域是否正在经历范式转移（如 SEO -> GEO），转移中的领域需求最旺盛

### 1.3 领域粒度决策

Brief 问了一个关键问题：SEO 是一个领域还是应该拆成"技术 SEO"/"内容 SEO"/"AI SEO"？

**回答：先粗后细，以项目覆盖范围为粒度。**

从 4 个 SEO 项目的实际提取看：
- claude-seo 和 30x-seo 覆盖技术 SEO + 内容 SEO + Schema + 性能 + AI SEO（全栈）
- geo-seo-claude 专注 GEO/AI SEO（单维度深挖）
- marketingskills 覆盖 SEO + CRO + 内容策略 + 广告（跨领域）

这说明项目本身不尊重我们人为划定的领域边界。正确做法：
1. **图谱粒度 = 知识原子（Knowledge Atom）**，不是领域标签
2. **领域标签是图谱的视图（view）**，不是图谱的组织单位
3. 用户问"SEO 领域的真相"时，图谱返回所有 SEO 相关的知识原子 + 它们的聚类/冲突/趋势
4. 用户问"GEO 的真相"时，图谱返回 SEO 原子中 GEO 相关的子集

这意味着图谱的底层存储是无领域边界的知识原子池，领域分类是上层索引。

### 1.4 候选领域初始清单

基于上述框架的定性评估（正式实施时需用定量数据校准）：

| 领域 | DemandSignal | SupplyReadiness | Extractability | StrategicFit | 综合 | 理由 |
|------|-------------|-----------------|----------------|-------------|------|------|
| SEO/GEO | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ | S | 已有 4 项目实验数据，范式转移中 |
| Auth/IAM | ★★★★ | ★★★★★ | ★★★★ | ★★★ | A | 刚需，项目多，但 Doramagic 无先验 |
| RAG | ★★★★★ | ★★★★ | ★★★ | ★★★ | A | 热度极高，但项目质量参差 |
| CI/CD | ★★★ | ★★★★ | ★★★★ | ★★★ | B | 成熟领域，公约数高，增量价值有限 |
| Payments | ★★★ | ★★★ | ★★★★ | ★★ | B | 项目不多，但领域知识密度极高 |
| 数据管线 | ★★★★ | ★★★ | ★★★ | ★★ | B | 碎片化严重，提取难度大 |

**第一个领域必须是 SEO/GEO**。理由在第五节展开。

---

## 二、最小有效样本量

### 2.1 理论推导

公约数的可信度取决于来源独立性，不是覆盖数量。这是 synthesis-report.md 中三方共识的核心。因此最小样本量不是一个固定数字，而是一个与独立性相关的函数：

```
MinSampleSize = f(desired_confidence, source_independence, domain_homogeneity)
```

**关键变量：**
- `source_independence`：4 个 SEO 项目中，claude-seo 和 30x-seo 高度相似（Codex 识别为高 lineage），实际上只算 ~2.5 个独立来源
- `domain_homogeneity`：成熟领域（如 Auth）公约数比例高，需要更少的项目；转型领域（如 SEO/GEO）冲突多，需要更多项目来区分真冲突和噪音

### 2.2 从实验数据推算

4 个 SEO 项目的提取结果已经展示了：
- **共识知识**：FAQPage 状态变更、HowTo 废弃、Core Web Vitals 阈值、E-E-A-T 框架、段落长度 134-167 词 -- 这些在 3-4 个项目中被反复提及
- **冲突知识**：技术 SEO 权重（25% vs 15%）、FAQPage 价值判断（有害 vs 有 GEO 价值）-- 这些是领域路线之争
- **独创知识**：citability_scorer（geo-seo-claude 独有）、product-marketing-context 底板（marketingskills 独有）

4 个项目已经能产出有价值的共识图谱。但独立性不足：claude-seo 和 30x-seo 高度同源。

### 2.3 建议的样本量梯度

| 阶段 | 项目数 | 独立来源数 | 产出 | 置信度 |
|------|-------|-----------|------|--------|
| Alpha（可发布最小图谱） | 5-7 | >=4 | 初步公约数 + 主要冲突 | 低（标注"基于 N 项目"） |
| Beta（实用图谱） | 10-15 | >=7 | 可靠公约数 + 冲突分类 + 独创索引 | 中（support_independence >= 0.7） |
| GA（可信赖图谱） | 15-20 | >=10 | 高置信度公约数 + 领域成熟度指标 + 时效追踪 | 高（provenance clustering 稳定） |

**关键约束：独立来源数 >= 项目数 * 0.6**。如果 10 个项目里有 4 组 fork/同源，实际只有 6 个独立来源，图谱质量等价于 6 项目。

### 2.4 边际收益曲线

理论预测：
- 项目 1-5：边际收益递增（每加一个项目，新知识多、交叉验证价值高）
- 项目 5-15：边际收益稳定（公约数在收敛，但冲突和独创仍在发现）
- 项目 15+：边际收益递减（公约数已稳定，新项目多为已知知识的变体）
- 例外：如果新项目代表了范式转移（如 GEO 项目加入纯 SEO 图谱），即使在 15+ 阶段也能产出高价值新知

需要在 SEO 领域用实际数据验证这个曲线。建议：从 4 个增加到 10 个，每加一个就测量公约数的稳定性变化和新知识发现率。

---

## 三、图谱的数据结构与增量更新机制

### 3.1 数据结构设计

图谱的数据结构必须建立在已有的 project_fingerprint.json 之上，是其上层聚合。分三层：

```
domain_consensus_map/
  metadata.json                    # 图谱元信息
  knowledge_atoms/                 # 知识原子池（核心）
    atom_00001.json
    atom_00002.json
    ...
  consensus_index.json             # 共识索引
  conflict_graph.json              # 冲突图
  provenance_index.json            # 溯源索引
  domain_health.json               # 领域成熟度指标
  project_registry.json            # 贡献项目注册表
```

#### metadata.json

```json
{
  "domain": "seo-geo",
  "display_name": "SEO & Generative Engine Optimization",
  "version": "0.4.0",
  "created_at": "2026-03-15T00:00:00Z",
  "last_updated": "2026-03-15T00:00:00Z",
  "project_count": 4,
  "independent_source_count": 3,
  "atom_count": 127,
  "consensus_atom_count": 43,
  "conflict_count": 8,
  "confidence_level": "alpha",
  "schema_version": "1.0.0"
}
```

#### Knowledge Atom（核心数据单元）

每个知识原子是图谱的最小单位，直接继承 synthesis-report.md 中 Codex 提出的 Knowledge Atom 结构，并增加图谱级字段：

```json
{
  "atom_id": "SEO-ATOM-00042",
  "canonical_claim": {
    "subject": "FAQPage schema",
    "predicate": "restricted_to",
    "object": "government and healthcare authority sites",
    "modifiers": {
      "scope": "Google rich results only",
      "since": "2023-08",
      "note": "still has semantic value for AI crawlers"
    }
  },
  "consensus_status": "CONSENSUS",
  "support": {
    "count": 4,
    "projects": ["claude-seo", "30x-seo", "geo-seo-claude", "marketingskills"],
    "independence_score": 0.65,
    "evidence_diversity": "HIGH",
    "provenance_cluster": "google-schema-changelog"
  },
  "temporal": {
    "first_seen": "2026-03-15",
    "last_verified": "2026-03-15",
    "applies_to_version": "Google Search 2023-08+",
    "decay_risk": "LOW",
    "next_review": "2026-06-15"
  },
  "embeddings": {
    "text_embedding": [0.123, ...],
    "slot_hash": "sha256:abc..."
  },
  "tags": ["schema", "structured-data", "google", "rich-results"],
  "related_atoms": ["SEO-ATOM-00043", "SEO-ATOM-00044"],
  "source_spans": [
    {
      "project": "claude-seo",
      "file": "seo/references/schema-types.md",
      "context": "FAQPage | Restricted | Government/healthcare only since 2023-08"
    },
    {
      "project": "30x-seo",
      "file": "hooks/validate-schema.py",
      "context": "FAQPage type restricted to government and healthcare sites only"
    }
  ]
}
```

#### consensus_status 枚举

| 状态 | 定义 | 判定规则 |
|------|------|---------|
| CONSENSUS | 多项目独立验证的共识 | support_count >= 3 AND independence_score >= 0.6 |
| EMERGING_CONSENSUS | 趋向共识但样本不足 | support_count = 2 AND independence_score >= 0.7 |
| CONFLICT | 项目间存在分歧 | 存在矛盾的 canonical_claim |
| UNIQUE | 仅单个项目提及 | support_count = 1 |
| SUSPECT | 单项目提及且缺乏证据 | support_count = 1 AND evidence_quality = LOW |
| DEPRECATED | 已被新知识取代 | superseded_by 字段非空 |

#### conflict_graph.json

```json
{
  "conflicts": [
    {
      "conflict_id": "CONFLICT-001",
      "type": "ROUTE_DISPUTE",
      "description": "Technical SEO weight allocation",
      "side_a": {
        "claim": "Technical SEO weight = 25%",
        "supporters": ["claude-seo", "30x-seo"],
        "rationale": "Traditional SEO fundamentals remain critical"
      },
      "side_b": {
        "claim": "Technical SEO weight = 15%",
        "supporters": ["geo-seo-claude"],
        "rationale": "AI citation-driven paradigm reduces traditional SEO importance"
      },
      "resolution_type": "PARADIGM_SHIFT",
      "interpretation": "Reflects SEO->GEO transition; weight depends on whether target audience is traditional search or AI search",
      "related_atoms": ["SEO-ATOM-00001", "SEO-ATOM-00002"]
    }
  ]
}
```

#### domain_health.json（领域成熟度指标）

直接采用 Claude 在 synthesis-report.md 中提出的框架：

```json
{
  "domain": "seo-geo",
  "maturity_stage": "TRANSITIONAL",
  "consensus_ratio": 0.45,
  "conflict_ratio": 0.15,
  "unique_ratio": 0.40,
  "interpretation": "SEO/GEO is in paradigm transition. Traditional SEO knowledge is mature consensus, but GEO-specific knowledge is still emerging with active disputes.",
  "trend": "GEO atoms growing faster than traditional SEO atoms",
  "measured_at": "2026-03-15"
}
```

### 3.2 增量更新机制

新项目加入图谱时的流程：

```
新项目 → Soul Extractor 提取 → project_fingerprint.json
    ↓
compare_projects.py（新 fingerprint vs 现有图谱）
    ↓
三层匹配（lexical → semantic → structured）
    ↓
分类每个知识原子：
  - 匹配已有 CONSENSUS atom → 增加 support_count，更新 independence_score
  - 匹配已有 CONFLICT → 加入某一方或成为新的第三方
  - 匹配已有 UNIQUE → 升级为 EMERGING_CONSENSUS
  - 无匹配 → 新增 UNIQUE atom
    ↓
重新计算 domain_health.json
    ↓
生成 UPDATE_REPORT.md（本次更新引入了什么新知识、改变了哪些共识、发现了哪些冲突）
```

**关键设计决策：增量更新，不是全量重算。**

- 已稳定的 CONSENSUS atom 不需要每次重新匹配
- 只有新项目的 atom 需要与现有图谱对比
- 但 support_independence 需要在每次更新时全量重算（因为新项目可能暴露旧项目的同源关系）

### 3.3 版本管理

```
domain_consensus_map/
  v0.1.0/    # 初始 4 个项目
  v0.2.0/    # 新增 3 个项目
  v0.3.0/    # 季度刷新（检测过时知识）
  latest -> v0.3.0
  CHANGELOG.md
```

版本语义：
- **major**：领域定义变化（如从"SEO"扩展为"SEO + GEO"）
- **minor**：新项目加入或知识原子显著变化
- **patch**：时效性更新（标记过时知识、更新 temporal 字段）

---

## 四、图谱的保鲜机制

### 4.1 知识衰减的三种模式

从 4 个 SEO 项目的提取数据中，我看到了三种截然不同的知识衰减模式：

| 衰减模式 | 例子 | 检测方法 | 衰减速度 |
|---------|------|---------|---------|
| **断崖式失效** | HowTo schema 2023-09 废弃，FID 2024-03 被 INP 替代 | 官方公告 + 新项目不再提及 | 瞬时 |
| **渐变式过时** | 关键词堆砌从"无效但无害"变成"主动有害"（-10%） | 新项目的权重分配漂移 | 数月-数年 |
| **分裂式演化** | SEO -> GEO 范式转移，技术 SEO 权重从 25% 降到 15% | 冲突图中某一方支持者持续增加 | 数月-数年 |

### 4.2 自动保鲜机制

**机制 1：新项目对比检测（被动保鲜）**

每次有新项目加入图谱时，自动检查：
- 新项目是否缺少现有 CONSENSUS 中某些知识？如果 3 个最新项目都不再提及某条共识，标记为 `decay_risk: HIGH`
- 新项目是否引入了与现有共识矛盾的知识？如果矛盾来自更新的项目，可能意味着共识正在过时

**机制 2：时间戳驱动的定期审查（主动保鲜）**

每个知识原子带 `next_review` 日期。不同类型的知识审查频率不同：
- 平台规则类（Google 政策、API 变更）：每季度
- 最佳实践类（段落长度、权重分配）：每半年
- 架构原理类（并行子代理设计、知识分层）：每年

**机制 3：外部信号监控（前瞻保鲜）**

这一层超出 Doramagic 当前能力范围，但值得规划：
- 监控 Google Search Central 博客、Web.dev 更新
- 监控 schema.org 变更日志
- 将外部变更事件自动关联到可能受影响的知识原子

### 4.3 衰减标记

```json
{
  "atom_id": "SEO-ATOM-00099",
  "canonical_claim": {
    "subject": "FID (First Input Delay)",
    "predicate": "is_used_as",
    "object": "Core Web Vitals metric"
  },
  "consensus_status": "DEPRECATED",
  "temporal": {
    "first_seen": "2026-03-15",
    "deprecated_at": "2024-03-12",
    "superseded_by": "SEO-ATOM-00100",
    "deprecation_source": "Chrome 123 release, Google official announcement",
    "last_verified": "2026-03-15"
  }
}
```

DEPRECATED 的知识不删除，只标记。因为：
1. 用户可能在分析旧项目（2023 年的 SEO 工具仍然用 FID）
2. 衰减模式本身是高价值知识（"FID 何时、为何被替代"）
3. 保留完整时间线支持知识考古学

---

## 五、冷启动策略

### 5.1 第一个领域：SEO/GEO

不是"应该选"，是"必须选"。理由：

1. **已有实验数据**：4 个项目的灵魂提取已完成，是唯一有真实数据验证的领域。其他领域都是从零开始。StrategicFit 满分。
2. **范式转移中 = 需求最旺盛**：SEO 正在经历 SEO -> GEO 的范式转移。4 个项目中 geo-seo-claude 代表新范式，claude-seo / 30x-seo 代表旧范式，权重冲突（25% vs 15%）直接映射了行业争论。用户最需要"告诉我这个领域的真相"的时刻，恰恰是领域正在剧变的时刻。
3. **项目供应充足**：GitHub 上 SEO 相关的高质量 skill/工具项目很多（awesome-seo 列表、多个 MCP 服务器项目、AI SEO 工具涌现）。SupplyReadiness 满分。
4. **提取难度低**：SEO skill 项目主要是 Markdown + Python 脚本，结构化程度高，非常适合灵魂提取。ExtractabilityScore 满分。
5. **商业验证路径清晰**：SEO 行业的付费意愿强（geo-seo-claude 明确标注"支撑 $2K-$12K/月的服务定价"），如果领域图谱能增强 SEO 用户的体验，商业模式验证最快。

### 5.2 第一批项目选择

已有 4 个，还需要补充 3-6 个达到 Alpha 阶段（5-7 个项目，>=4 独立来源）。

**选择标准（综合好作业评判体系 + 暗雷检测）：**

| 维度 | 权重 | 说明 |
|------|------|------|
| 独立性 | 30% | 与已有 4 个项目不同源，不是 fork，覆盖不同技术栈或观点 |
| 知识密度 | 25% | 项目有明确的设计哲学和 WHY，不只是工具集 |
| 领域覆盖缺口 | 25% | 补充已有 4 项目未覆盖的子领域（如 Local SEO、电商 SEO、国际化 SEO） |
| 代码质量 | 10% | 代码结构清晰、有测试、有文档 |
| 社区活跃度 | 10% | 有真实用户反馈、有维护更新 |

**候选补充方向（补缺口）：**
- 电商 SEO 专项工具（当前 4 项目都偏 SaaS/内容站）
- Local SEO 工具（地理位置相关 SEO，30x-seo 有但不深入）
- 纯 AI SEO / LLM 优化工具（非 GEO 全栈，专注 AI 引用优化）
- 非英语 SEO 工具（国际化视角，补充文化差异知识）
- 内容驱动 SEO 工具（偏编辑部/内容团队，与当前偏工程的视角互补）

### 5.3 策展 vs 爬取

**V1 必须是策展（Curation），不是爬取（Crawling）。**

理由：
1. 图谱质量取决于输入项目质量。"垃圾进，垃圾出"在知识工程中比代码工程更致命。
2. 暗雷检测体系的核心警告：Deceptive Source Detection 是 Doramagic 的关键能力。自动爬取无法做暗雷检测。
3. 最小样本量研究表明 5-7 个精选项目的价值 > 20 个随机项目。
4. 冷启动阶段的每一个错误选择都会被放大（因为 N 小，一个坏样本能严重扭曲公约数）。

**策展流程：**
1. 人工列出候选项目清单（30-50 个）
2. 用好作业评判体系 + 暗雷检测自动筛选（缩小到 10-15 个）
3. 人工审查前 10 的独立性和覆盖互补性
4. 选出 5-7 个执行灵魂提取
5. 构建 Alpha 版图谱
6. 根据图谱缺口决定下一批候选

### 5.4 飞轮启动路径

```
阶段 0（现在）: 4 个 SEO 项目 → 验证图谱数据结构
                   ↓
阶段 1（+2 周）: 补充至 7 个项目 → Alpha 图谱发布
                   ↓
阶段 2（+1 月）: 用 Alpha 图谱增强新用户的 SEO 项目提取
                 → 用户提取的新项目 → 人工审核后回流图谱
                   ↓
阶段 3（+2 月）: 10-15 个项目 → Beta 图谱
                 → 开始积累用户贡献的增量数据
                   ↓
阶段 4（+3 月）: 第二个领域（RAG 或 Auth）启动冷启动
                 → SEO 图谱进入自动维护模式
```

---

## 六、图谱注入 Soul Extractor 管线的具体方案

### 6.1 注入点分析

Soul Extractor 当前管线：Stage 0 (prepare) -> Stage 1 (soul discovery) -> Stage 2 (concepts) -> Stage 3 (rules) -> Stage 3.5 (validation) -> Stage 4 (narrative) -> Stage 5 (assembly)

图谱应在三个位置注入：

**注入点 1：Stage 0 -- 作为 Brick 注入（最重要）**

WHY 提取实验结论已经证明"积木（Brick）增强 WHY 提取质量 +20%"。领域图谱的共识知识是最有价值的 Brick：

```
Stage 0 增强：
  原有: prepare-repo.sh → repomix + community_signals + repo_facts.json
  新增: inject_domain_context.py → 从图谱中提取与目标项目相关的知识原子
       输出: domain_context.json（相关共识、已知冲突、领域成熟度）
       → 注入 Stage 1 的 prompt context
```

效果：当 Stage 1 问"这个项目解决什么问题？"时，LLM 已经知道该领域的共识知识，能够：
- 更准确地定位项目在领域中的位置（"这个项目在 GEO 方向走得更远"）
- 识别独创知识（"这个 citability_scorer 是图谱中没有的新知识"）
- 检测过时知识（"这个项目仍在推荐 FID，而图谱显示 FID 已废弃"）

**注入点 2：Stage 3.5 -- 作为 Fact-Checking 参照**

当前 Stage 3.5 的 fact-checking gate 验证提取结果的正确性。图谱可以作为外部参照：
- 如果提取的知识与图谱 CONSENSUS 矛盾，标记为需要人工审查（可能是提取错误，也可能是新发现）
- 如果提取的知识与图谱中不存在，标记为候选 UNIQUE（可能的独创知识）

**注入点 3：Stage 5 -- 作为输出增强**

在最终 CLAUDE.md 中添加"领域定位"段落：

```markdown
## 领域定位（自动生成）

本项目属于 SEO/GEO 领域。基于 Doramagic 领域共识图谱（7 个项目，v0.2.0）：

- **与领域共识一致**：Core Web Vitals 使用 INP（非 FID）、FAQPage 限制、E-E-A-T 扩展到全域
- **独创贡献**：citability_scorer（AI 可引用性量化评分），在其他 SEO 项目中未见
- **与部分项目冲突**：技术 SEO 权重 15%（vs 行业常见 25%），反映 GEO-first 立场
- **过时风险**：无
```

### 6.2 注入不改变管线本质

关键：图谱注入是 context 增强，不是逻辑变更。Stage 1-4 的提取逻辑不变，只是 LLM 在提取时拥有了更好的背景知识。这完全符合"能力升级，本质不变"的约束。

---

## 七、"告诉我这个领域的真相"-- 技术需求拆解

这句话是 Gemini 在 synthesis-report.md 中提出的用户心智升级。让我拆解它背后的技术需求。

### 7.1 用户说这句话时，真正想要什么

不是要一篇综述文章。用户要的是：
1. **共识**：这个领域里，所有项目都同意什么？（"无争议的事实"）
2. **争论**：这个领域里，项目之间在吵什么？每一方的理由是什么？（"路线之争"）
3. **陷阱**：这个领域里，哪些看起来正确的知识其实已经过时或有条件限制？（"暗雷"）
4. **前沿**：这个领域里，只有少数项目在探索的新方向是什么？（"独创"）
5. **地图**：这些知识之间的关系是什么？（"全景"）

### 7.2 技术实现

```
用户输入: "告诉我 SEO 领域的真相"
    ↓
Step 1: 加载 domain_consensus_map/seo-geo/
    ↓
Step 2: 按 consensus_status 分组
    - CONSENSUS atoms → 确定性事实
    - CONFLICT atoms + conflict_graph → 路线之争
    - DEPRECATED atoms → 过时知识警告
    - UNIQUE atoms with high quality → 前沿探索
    ↓
Step 3: 按 tags 聚类，生成主题地图
    - Schema 相关 (FAQPage, HowTo, Organization...)
    - 权重分配 (技术 vs AI vs 内容...)
    - 工具链 (爬虫、评分器、报告生成...)
    ↓
Step 4: LLM 叙事生成（"AI 说故事"）
    - 输入: 结构化的 atoms + conflicts + health
    - 输出: 人类可读的领域真相报告
    - 约束: 每个叙事段落必须引用来源 atom_id
    ↓
Step 5: 输出 DOMAIN_TRUTH.md
```

### 7.3 输出格式

```markdown
# SEO/GEO 领域真相（基于 7 个项目 | v0.2.0 | 2026-03-15）

## 领域健康度
- 成熟度：过渡期（TRANSITIONAL）
- 共识比例：45% | 冲突比例：15% | 独创比例：40%
- 趋势：GEO 知识正在快速增长，传统 SEO 知识趋于稳定

## 无争议的共识（所有项目都同意）
1. HowTo schema 已废弃（2023-09），不应再使用
2. FID 已被 INP 替代（2024-03），任何引用 FID 的内容已过时
3. E-E-A-T 适用于所有竞争性查询（2025-12 核心更新）
4. AI 可引用段落最优长度：134-167 词
...（每条带来源项目标注）

## 路线之争（项目之间的分歧）
1. **技术 SEO 的权重**
   - 阵营 A（25%）：claude-seo, 30x-seo — 传统基础仍然关键
   - 阵营 B（15%）：geo-seo-claude — AI 引用驱动，传统技术退居次要
   - 解读：取决于你的目标是传统搜索流量还是 AI 引用流量
...

## 暗雷警告（看似正确但有条件限制）
1. FAQPage schema 不是有害的，只是 Google rich results 不再支持商业站
   — 但对 AI 爬虫仍有语义价值（GEO 视角）
...

## 前沿探索（少数项目的独创方向）
1. citability_scorer：量化段落的 AI 可引用性（geo-seo-claude 独有）
2. product-marketing-context 底板：跨 skill 的上下文共享（marketingskills 独有）
...

---
图谱来源：[项目列表] | 置信度标注：[独立性评分]
```

### 7.4 与 Doramagic 哲学的对齐

"告诉我这个领域的真相"不是 Doramagic 在教用户做事。它是给用户一张 X 光片：
- 共识 = 骨骼（确定性结构）
- 冲突 = 关节（需要用户自己决定方向的活动部位）
- 暗雷 = 骨折标记（已知风险）
- 前沿 = 生长板（正在发展的新区域）

用户拿到 X 光片后，自己决定怎么做。Doramagic 不开处方。

---

## 八、与飞轮模型的关系

### 8.1 预积累 = 飞轮的冷启动能量

飞轮模型（memory/doramagic-flywheel-and-partial-coverage.md）：

```
用户需求 → 搜索已有 skill
    ↓ 找到 → 灵魂提取，抄作业
    ↓ 没找到 → 调 OpenClaw 从零创建工具
                  ↓
              新 skill 诞生
                  ↓
              下一个用户搜到了
```

领域图谱给飞轮加了一层：

```
用户需求 → 搜索已有 skill
    ↓ 找到 → 灵魂提取（领域图谱增强，质量 +20%）
    ↓         ↓
    ↓     提取结果回流图谱 → 图谱更准 → 下次提取质量更高
    ↓
    ↓ 没找到 → 图谱显示领域概览（不是空手而归）
                  ↓
              用户带着领域知识去创建工具（起步更高）
                  ↓
              新 skill 诞生 + 回流图谱
```

**关键增强**：
1. "找到作业"时，图谱增强提取质量（Brick 效应已验证）
2. "没找到作业"时，图谱仍能提供领域真相（部分覆盖的价值交付）
3. 每次提取都是图谱的增量数据源（飞轮的持续动力）

### 8.2 用户贡献的回流机制

用户在 Doramagic 中提取了一个新 SEO 项目的灵魂。这个提取结果如何回流到图谱？

**三级回流：**

| 级别 | 触发条件 | 流程 | 延迟 |
|------|---------|------|------|
| 自动回流 | 用户同意分享（opt-in） | project_fingerprint.json 自动提交到图谱更新队列 | 实时 |
| 审核回流 | 图谱管理员审核 | 检查独立性、质量、暗雷后加入图谱 | 天级 |
| 策展回流 | 图谱维护者主动选择 | 高质量项目被策展加入图谱 | 周级 |

**V1 只做策展回流。** 自动回流和审核回流需要更成熟的质量保证机制。在图谱质量足够稳定之前，宁可慢也不能引入坏数据。

---

## 九、Brief 未提到的可能性与风险

### 9.1 可能性

**可能性 1：领域图谱作为"作业评审标准"**

当前好作业评判体系是通用的。有了领域图谱后，可以做领域特定的作业评审：
- "这个 SEO 项目的知识有 80% 与图谱共识一致，15% 是独创，5% 与共识矛盾"
- "矛盾的 5% 中，3% 是项目使用了过时知识（FID），2% 是新观点（值得关注）"

这让 Doramagic 从"告诉你这个项目的灵魂"升级为"告诉你这个项目的灵魂在行业中的定位"。

**可能性 2：领域图谱驱动的 Incomplete Skill 补完**

飞轮模型中的部分覆盖问题。当用户的 skill 只覆盖 70% 时，领域图谱可以精确指出缺失的 30% 在哪个方向，并推荐最相关的补充项目。这比通用推荐精准得多。

**可能性 3：知识流行病学**

图谱积累到足够规模后，可以追踪知识的传播路径。例如：
- Ahrefs 2025 年的品牌提及研究（相关性 0.737）是如何传播到不同项目中的？
- 传播过程中是否发生了扭曲？（某项目引用了这个数据但理解有误）
- 哪些知识源是"超级传播者"？（被大量项目引用的单一来源 -> 风险信号）

这是 synthesis-report.md 中 Claude 提出的"知识供应链分析"的具体化。

**可能性 4：跨领域的知识迁移检测**

当两个不同领域的图谱都建好后，可以检测跨领域的知识迁移。例如：
- SEO 领域的"内容可引用性"概念是否已经迁移到了 RAG 领域？
- Auth 领域的"零信任"理念是否影响了 API 设计领域？

这需要多个领域图谱同时存在，是长期价值。

### 9.2 风险

**风险 1：选择偏差固化**

如果只选择 stars 高的项目，图谱会偏向流行范式，遗漏小众但有价值的方向。

**缓解**：项目选择标准中"领域覆盖缺口"权重 25%，强制补充非主流视角。每次图谱更新时计算"视角多样性指标"。

**风险 2：图谱权威性的反噬**

一旦图谱被用户视为"领域标准"，图谱中的错误或偏见会被放大。用户可能不再质疑图谱共识。

**缓解**：
- 每个知识原子必须标注 confidence level 和 support_independence
- 图谱输出明确声明"基于 N 个项目，代表性有限"
- 冲突知识不消解，原样展示
- 这是"不教用户做事"的最深层含义：X 光片不能假装自己是诊断结论

**风险 3：维护成本超出预期**

每个领域 10-20 个项目，每季度刷新，每个项目的灵魂提取需要 LLM 调用成本。如果覆盖 10 个领域，每年的维护成本可能很高。

**缓解**：
- V1 只做 1 个领域（SEO/GEO），验证成本模型
- 增量更新而非全量刷新，降低每次更新的成本
- 时效性审查按知识类型分频率（不是所有知识都需要每季度检查）
- 用户贡献的回流减少主动提取的需求

**风险 4：图谱粒度的两难**

太粗（只有高级共识）-> 对用户没价值，不如直接读博客文章。
太细（精确到每个 API 参数）-> 维护成本爆炸，且容易过时。

**缓解**：知识原子的粒度标准 = "用户做决策时需要的最小信息单位"。以 SEO 为例：
- 太粗："Schema 很重要" -> 不可执行
- 合适："FAQPage schema 在 2023-08 后仅对政府/医疗站生效，但对 AI 爬虫仍有语义价值" -> 可执行决策
- 太细："Google 的 FAQPage 解析器的具体 CSS selector 规则" -> 维护成本太高

**风险 5：与 Soul Extractor 能力的耦合**

图谱质量取决于灵魂提取质量。如果 Soul Extractor 在某类项目上提取不准（如 exp07 中 MiniMax 的幻觉问题），图谱会继承这些错误。

**缓解**：
- 图谱入口项目只用高质量提取（Opus 或 Sonnet，不用弱模型）
- fact-checking gate 已实现（v0.9 P0 patch）
- repo_facts.json 确定性提取已就位
- 图谱构建时额外增加跨项目交叉验证（同一条知识在不同项目提取结果中是否一致）

---

## 十、商业模型初步思考

### 10.1 免费 vs 付费

**V1：领域图谱免费公开。** 理由：
1. 冷启动阶段需要最大化用户接触面，付费是摩擦
2. 图谱本身是飞轮的入口——用户因为图谱来，提取项目后贡献回图谱
3. 图谱的真正价值不在静态内容，在于与 Soul Extractor 的动态结合（这是付费点）

**付费点在增强服务：**
- 免费：查看领域图谱、获得领域真相报告
- 付费：图谱增强的灵魂提取（+20% 质量）、个性化领域定位报告、私有项目与公共图谱的对比分析

### 10.2 与 OpenClaw 的关系

图谱不应该在 OpenClaw 上作为 skill 发布。图谱是 Doramagic 的基础设施，不是用户安装的工具。但图谱中发现的独创知识可以指向 OpenClaw 上的具体 skill（"这个独创的 citability_scorer 来自 geo-seo-claude skill，可在 OpenClaw 安装"）。

---

## 十一、总结与行动计划

### 核心判断

1. 领域共识图谱是 Doramagic 飞轮的冷启动燃料，不是范式转变
2. 图谱的底层是无边界的知识原子池，领域分类是视图
3. 最小有效样本 = 5-7 个项目且独立来源 >= 4
4. 第一个领域必须是 SEO/GEO（唯一有实验验证的领域）
5. 图谱注入 Soul Extractor 的最佳位置是 Stage 0（作为 Brick）
6. V1 必须是人工策展，不是自动爬取

### 行动计划

| 阶段 | 时间 | 动作 | 产出 |
|------|------|------|------|
| 0 | 1-2 天 | 定稿图谱数据结构 + 用现有 4 个 SEO 项目手动构建原型 | domain_consensus_map/seo-geo/ v0.1.0 |
| 1 | 1 周 | 策展 + 提取 3-4 个补充 SEO 项目 | Alpha 图谱 v0.2.0（7 项目） |
| 2 | 1 周 | 实现 inject_domain_context.py + Stage 0 注入 | 图谱增强的灵魂提取 |
| 3 | 1 天 | A/B 验证：有图谱注入 vs 无图谱注入的提取质量对比 | 量化 ROI |
| 4 | 持续 | 增量更新机制 + 用户回流机制 | 飞轮启动 |

### 一句话总结

> 领域共识图谱不是给用户看的百科全书，是让 Soul Extractor 从"瞎子摸象"变成"带着地图摸象"。用户看到的不是图谱本身，而是图谱增强后的提取质量。这是一个引擎升级，不是一个新产品。

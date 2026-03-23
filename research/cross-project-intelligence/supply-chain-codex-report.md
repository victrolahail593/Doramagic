# 知识供应链 + 知识通胀 — Codex 工程实现研究报告

> 视角：工程架构 + 算法设计  
> 日期：2026-03-15  
> 模型：Codex

---

## 0. 执行摘要

先给结论：

1. **知识供应链值得做，但 V1 必须收敛成“显式来源追踪 + 回声校正”，不要一上来做全自动真相追溯器。**
2. **知识通胀值得做，但现在更适合作为“ORIGINAL 信号校正层”和“领域趋势层”，不适合作为硬判定层。**
3. **对 Doramagic 而言，这不是新系统，而是 `evidence chain + support_independence + domain map history` 的升级版。**
4. **真正该现在做的是 provenance clustering，不是幻想中的全知供应链图。**

我对投入时机的判断：

| 能力 | 判断 | 原因 |
|---|---|---|
| 显式上游来源提取 | **NOW** | 成本低、精度高、可直接改进 evidence chain |
| provenance clustering / adjusted independence | **NOW** | 直接修正“多个项目重复说同一句话 = 多重验证”的假象 |
| 基于结构槽位的扭曲检测 | **NOW-LITE** | 现有 atom schema 已有基础，但应只做高精度信号 |
| 推断式上游来源恢复 | **LATER** | 工程上可做，但高误报会污染整条链 |
| 知识通胀检测 | **LATER** | 需要时间快照和更大图谱规模，4 个项目只能做弱信号 |
| inflation-adjusted ORIGINAL | **NOW-LITE / LATER-FULL** | 现在能做保守校正；成熟版依赖图谱历史 |
| “自动判定唯一真实源头” | **NEVER（作为硬结论）** | 开源知识传播天然隐式，很多链条无法被证明 |

一句话概括：

> **供应链解决的是“这些支持到底独不独立”；通胀解决的是“这条知识还值不值钱”。**

---

## 1. 重新定义问题：Doramagic 需要的不是“知识引用网络”，而是“知识来路账本”

Claude 的供应链方向是对的，但如果工程上不收敛，很容易走偏成一个高成本、低置信的全链路推断系统。

对 Doramagic，正确的抽象不是“还原世界上真实发生的一切知识传播”，而是：

1. **对每个知识原子记录来路**
2. **对每个 cluster 判断支持是否独立**
3. **对每个 ORIGINAL 判断它是不是“真独创”还是“基础常识伪装成独创”**

所以系统目标应从：

- 追踪完整传播史  
变成
- **为每个 atom / cluster 生成一个足够可信的 provenance profile**

这和现有体系的关系非常清楚：

- `evidence chain` 解决：**这条知识被什么证据支撑**
- `support_independence` 解决：**这些支撑看起来有几份**
- `provenance clustering` 要解决：**这些支撑究竟是不是同一上游回声**
- `inflation detection` 要解决：**这条知识是不是已经从前沿差异化，变成行业基础设施**

这是升级，不是重做。

---

## 2. 先讲工程判断：V1 该做什么，不该做什么

### 2.1 应该做的 V1

V1 只做四件事：

1. **显式来源提取**
2. **同源聚类（provenance clustering）**
3. **adjusted independence 计算**
4. **弱通胀校正（只修正 ORIGINAL，不做宏大叙事）**

### 2.2 不应该做的 V1

V1 不做：

1. 无证据情况下的“唯一上游源头”硬判定
2. 依赖 LLM 自由发挥的传播链补完
3. 细粒度法律责任判断
4. 小样本条件下的强通胀结论

原因很简单：

- 供应链的价值在于**纠正假独立**
- 通胀的价值在于**纠正假独创**

这两个问题都可以用保守工程方案解决，不需要一开始就做“知识取证学”。

---

## 3. 上游来源自动提取：V1 只相信显式证据，V1.5 再做推断

## 3.1 可提取的显式上游来源

从项目代码和文档中，V1 可以提取的显式来源包括：

1. **README / docs 中的 URL**
2. **代码注释中的 URL**
3. **Markdown 链接文本 + href**
4. **commit message 中的链接**
5. **issue / PR 描述中的引用链接**
6. **引用标题模式**
   - “according to Google…”
   - “based on Ahrefs study…”
   - “see Princeton GEO paper…”
7. **结构化依赖元数据**
   - package homepage
   - docs metadata
   - frontmatter references
8. **硬编码常量旁的来源注释**
   - 如 `YOUTUBE_CORRELATION = 0.737  # Ahrefs 2025`

### 3.1.1 建议的数据结构

```json
{
  "source_ref_id": "src_ahrefs_2025_youtube_001",
  "source_type": "industry_research",
  "url": "https://ahrefs.com/...",
  "title": "Ahrefs study on AI brand visibility",
  "publisher": "Ahrefs",
  "published_at": "2025-02-01",
  "extracted_from": {
    "project_id": "geo-seo-claude",
    "file_path": "docs/brand-scoring.md",
    "line_start": 41,
    "line_end": 47,
    "commit_sha": "abc123"
  },
  "extraction_mode": "explicit",
  "confidence": 0.98
}
```

### 3.1.2 覆盖率估计

这里必须现实：

开源项目里，不是所有知识都有显式引用。

我的工程估计：

| 原子类型 | 显式引用覆盖率 |
|---|---:|
| 平台规则/官方公告类 | 40%-80% |
| 行业研究/数据点类 | 20%-50% |
| 经验规则/工程 heuristics | 5%-25% |
| WHY / UNSAID 类深层知识 | 0%-10% |

对一个典型知识工具仓库，**整体 atom 级显式来源覆盖率大概只有 15%-35%**。  
对这 4 个 SEO 项目，我会保守估计落在 **20%-30%**，因为它们文档相对重、引用意识较强。

这不是坏消息。因为供应链最有价值的地方，本来就集中在：

- 高影响规则
- 高传播度数据点
- 官方变更
- 被多个项目重复引用的“共识知识”

换句话说：**我们不需要为所有 atom 找到来源，先覆盖最关键的 20% 就够有产品价值。**

---

## 3.2 没有显式引用时，如何推断上游

这部分可以做，但必须降级成“候选来源”，不是“事实”。

### 3.2.1 候选来源检索算法

输入：

- 一个项目 atom
- 领域图谱中历史 atoms
- 已知 source_ref 库

候选检索三阶段：

1. **lexical candidate recall**
   - MinHash / BM25 / 关键词倒排
2. **semantic recall**
   - embedding ANN
3. **structured slot rerank**
   - 按 subject / relation / object / scope / time_anchor 重排

推荐评分函数：

```text
candidate_score =
  0.30 * lexical_overlap +
  0.30 * embedding_similarity +
  0.25 * slot_match_score +
  0.10 * temporal_prior +
  0.05 * rarity_bonus
```

其中：

- `temporal_prior`：候选源出现时间早于当前 atom 才加分
- `rarity_bonus`：对罕见数字、特殊术语给予更高加权

### 3.2.2 推断来源的工程边界

我建议分 3 个置信层：

| 层级 | 条件 | 用途 |
|---|---|---|
| `explicit_confirmed` | 明确 URL / 引用 | 可进入事实层 |
| `inferred_high_precision` | 语义 + 槽位 + 时间都强匹配 | 可进入分析层，但需标记 |
| `inferred_speculative` | 只有语义相似 | 只用于候选，不进入最终报告主结论 |

### 3.2.3 精度 / 召回现实预期

在没有专门训练数据前，我的工程预期是：

| 模式 | 精度 | 召回 |
|---|---:|---:|
| 显式来源提取 | 0.90-0.98 | 0.15-0.35 |
| 高精度推断来源 | 0.60-0.80 | 0.30-0.50 |
| 激进推断来源 | 0.35-0.60 | 0.50-0.70 |

所以 V1 不该用激进推断。

**trade-off：宁可少报，不要误报。**  
因为一旦上游链条错了，后面的：

- independence 修正
- distortion 判断
- inflation 归因

都会一起错。

---

## 4. 传播链数据结构：不要直接在 atom cluster 上硬塞全部语义

## 4.1 核心原则

传播链不是 atom cluster 的替代品。

- `atom cluster` 解决：**这些知识在说同一件事吗**
- `provenance graph` 解决：**这些知识是否来自同一上游**

两者经常重叠，但不是一回事。

例如：

- 3 个项目都说 FAQPage 受限 → 同一个 atom cluster
- 但它们都来自 Google 2023-08 公告 → 同一个 provenance root

另一个例子：

- `claude-seo` 和 `30x-seo` 几乎相同 → 既可能同 cluster，也可能共享项目级 lineage

所以我建议新增一层：**provenance cluster**。

---

## 4.2 推荐数据模型

### 4.2.1 AtomOccurrence

项目中的一个具体知识出现位置。

```json
{
  "occurrence_id": "occ_geo_000231",
  "project_id": "geo-seo-claude",
  "atom_id": "atom_youtube_brand_corr",
  "cluster_id": "cluster_youtube_corr",
  "text": "YouTube brand presence correlates with AI ranking visibility at 0.737",
  "slots": {
    "subject": "youtube_brand_presence",
    "relation": "correlates_with",
    "object": "ai_visibility",
    "value": 0.737,
    "scope": "brand_scoring",
    "normative_force": "descriptive",
    "time_anchor": "2025"
  },
  "first_seen_at": "2026-03-01T12:33:00Z",
  "source_refs": ["src_ahrefs_2025_youtube_001"]
}
```

### 4.2.2 ProvenanceEdge

```json
{
  "edge_id": "prov_edge_001",
  "from_node": "src_ahrefs_2025_youtube_001",
  "to_node": "occ_geo_000231",
  "edge_type": "cites",
  "confidence": 0.98,
  "mode": "explicit",
  "evidence": [
    {
      "file_path": "docs/brand-scoring.md",
      "line_start": 41,
      "line_end": 47
    }
  ]
}
```

### 4.2.3 PropagationEdge

用于项目之间的传播猜测或复制关系。

```json
{
  "edge_id": "prop_edge_031",
  "from_node": "occ_claude_seo_000871",
  "to_node": "occ_30x_000102",
  "edge_type": "copied_or_forked",
  "confidence": 0.94,
  "basis": {
    "lexical_similarity": 0.96,
    "slot_match_score": 1.0,
    "project_lineage_score": 0.92,
    "time_prior": 0.61
  }
}
```

### 4.2.4 ProvenanceCluster

```json
{
  "provenance_cluster_id": "prov_cluster_faqpage_google_202308",
  "root_nodes": ["src_google_faqpage_202308_001"],
  "member_occurrences": [
    "occ_geo_000019",
    "occ_market_003841",
    "occ_claude_000219",
    "occ_30x_000221"
  ],
  "root_type": "official_announcement",
  "root_count": 1,
  "project_count": 4,
  "project_independence": 0.84,
  "adjusted_independence": 0.31,
  "interpretation_variance": 0.12,
  "inflation_state": "infrastructure"
}
```

---

## 4.3 JSON schema：建议的新增字段

### 4.3.1 atom occurrence 扩展字段

```json
{
  "provenance": {
    "source_ref_ids": ["src_google_faqpage_202308_001"],
    "source_mode": "explicit",
    "source_confidence": 0.98,
    "upstream_root_ids": ["root_google_search_docs"],
    "propagation_suspects": ["occ_claude_000219"],
    "distortion_flags": ["scope_broadening"],
    "distortion_score": 0.27
  }
}
```

### 4.3.2 cluster 扩展字段

```json
{
  "provenance_profile": {
    "provenance_cluster_ids": ["prov_cluster_faqpage_google_202308"],
    "root_count": 1,
    "max_root_share": 1.0,
    "source_diversity": 0.25,
    "project_count": 4,
    "adjusted_independence": 0.31,
    "echo_risk": "high"
  },
  "inflation_profile": {
    "adoption_rate": 1.0,
    "independent_adoption_rate": 0.31,
    "phase": "infrastructure",
    "inflation_score": 0.92,
    "first_seen_at": "2023-08-10",
    "last_seen_at": "2026-03-15"
  }
}
```

---

## 5. 扭曲检测算法：用结构槽位做“硬检测”，让 AI 只负责命名和叙事

这部分最容易被做成玄学。

我的建议是：  
**扭曲检测必须是“槽位差异分析”，不是“让 LLM 判断它是不是误读”。**

### 5.1 需要比较的槽位

对每个 atom，至少标准化出以下字段：

- `subject`
- `relation`
- `object`
- `value` / `quantity`
- `scope`
- `conditions`
- `normative_force`
- `time_anchor`
- `evidence_strength`

其中最关键的是三个：

1. `scope`
2. `normative_force`
3. `value / quantity`

### 5.2 典型扭曲类型

| 类型 | 例子 | 检测特征 |
|---|---|---|
| 简化 | 原文有条件，下游删掉条件 | `conditions` 丢失 |
| 扩大化 | 特定场景结论被当成普遍规则 | `scope` 变宽 |
| 去上下文化 | 时间、样本、实验前提被抹掉 | `time_anchor` / `conditions` 丢失 |
| 误读 | 相关性被表述成因果性 | `relation` + `normative_force` 变强 |
| 数值漂移 | 0.737 变 0.74 或被当阈值 | `value` 改变 / 离散化 |
| 对象转移 | A 指标被套到 B 对象 | `object` 变化 |

### 5.3 `detect_distortion(upstream_atom, downstream_atom)` 伪代码

```pseudo
function detect_distortion(upstream_atom, downstream_atom):
    deltas = []
    score = 0.0

    if normalized_subject(upstream_atom) != normalized_subject(downstream_atom):
        deltas.append("subject_shift")
        score += 0.20

    if normalized_object(upstream_atom) != normalized_object(downstream_atom):
        deltas.append("object_shift")
        score += 0.20

    if relation_strength(downstream_atom.relation) > relation_strength(upstream_atom.relation):
        deltas.append("relation_escalation")
        score += 0.20

    if scope_contains(downstream_atom.scope, upstream_atom.scope) and downstream_atom.scope != upstream_atom.scope:
        deltas.append("scope_broadening")
        score += 0.20
    else if scope_contains(upstream_atom.scope, downstream_atom.scope) and downstream_atom.scope != upstream_atom.scope:
        deltas.append("scope_narrowing")
        score += 0.05

    if downstream_atom.conditions is empty and upstream_atom.conditions is not empty:
        deltas.append("condition_drop")
        score += 0.15

    if downstream_atom.time_anchor is empty and upstream_atom.time_anchor is not empty:
        deltas.append("temporal_context_drop")
        score += 0.10

    numeric_delta = compare_numeric(upstream_atom.value, downstream_atom.value)
    if numeric_delta > 0.05:
        deltas.append("numeric_drift")
        score += min(0.15, numeric_delta)

    if normative_force_rank(downstream_atom.normative_force) > normative_force_rank(upstream_atom.normative_force):
        deltas.append("normative_escalation")
        score += 0.15

    severity =
        "high" if score >= 0.45
        "medium" if score >= 0.20
        "low" otherwise

    return {
        "distortion_score": min(score, 1.0),
        "distortion_flags": deltas,
        "severity": severity
    }
```

### 5.4 设计 trade-off

- **优点**：可解释，可审计，可回放
- **缺点**：依赖 slots 质量；对隐性 WHY 扭曲不敏感

但这是正确取舍。  
**V1 宁可漏掉细腻的误读，也不要让系统对不存在的扭曲大做文章。**

---

## 6. provenance clustering：这是整个供应链系统真正的核心

如果只能做一件事，我会做这个。

### 6.1 provenance cluster 和 atom cluster 的区别

| 对象 | 问题 | 例子 |
|---|---|---|
| atom cluster | “是不是同一知识” | 4 个项目都说 FAQPage 受限 |
| provenance cluster | “是不是同一上游” | 4 个项目都来自 Google 2023-08 公告 |

多个项目说同一件事，不代表他们彼此独立。  
这就是 provenance clustering 的意义。

### 6.2 聚类算法

输入：

- 同一 atom cluster 的 member occurrences
- 每个 occurrence 的 source refs
- 项目 lineage / fork 信号

步骤：

1. 按显式 source_ref 先分桶
2. 没有显式 source_ref 的 occurrence，再按“最可能上游 occurrence”分桶
3. 若两个桶共享同一 root URL / same canonical source / same upstream project，则合并
4. 若两个 occurrence 来自强 fork 关系项目，则优先视为同 lineage

### 6.3 `adjusted_independence(cluster, provenance_graph)` 伪代码

```pseudo
function adjusted_independence(cluster, provenance_graph):
    project_count = count_unique_projects(cluster.members)
    if project_count == 0:
        return 0.0

    base_independence = cluster.support_independence

    root_ids = []
    root_weights = {}

    for occ in cluster.members:
        roots = resolve_root_sources(occ, provenance_graph)
        if roots is empty:
            roots = ["unknown:" + occ.project_id]
        for r in roots:
            root_ids.append(r)
            root_weights[r] = root_weights.get(r, 0) + 1

    unique_root_count = count_unique(root_ids)
    source_diversity = unique_root_count / project_count

    max_root_share = max(root_weights.values()) / len(cluster.members)

    lineage_penalty = compute_lineage_penalty(cluster.members)
    # 例如 claude-seo 与 30x-seo 高度相似时惩罚

    entropy = normalized_entropy(root_weights)

    adjusted =
        base_independence
        * (0.45 * source_diversity + 0.35 * entropy + 0.20 * (1 - max_root_share))
        * (1 - lineage_penalty)

    return clamp(adjusted, 0.0, 1.0)
```

### 6.4 为什么不能只看项目数

用 4 个 SEO 项目举例：

#### FAQPage 受限

- 项目支持数：4
- 上游根数：1（Google）
- 结论：**高可信，但低独立**

#### “134-167 词最优段落”

- 项目支持数：3
- 上游根数：很可能 1，且不明
- 结论：**看起来像共识，实际上接近回声**

#### `claude-seo ≈ 30x-seo`

- 项目支持数：2
- 独立项目数：表面是 2，实质接近 1
- 结论：**必须扣除 lineage**

这就是 adjusted independence 的价值：  
不是改变“这条知识是否正确”，而是改变“我们该把多少统计重量压在这份共识上”。

---

## 7. 知识通胀检测：不是检测真假，而是检测“差异化价值”衰减

Claude 对“通胀 = 第三类衰变”的方向是对的，但工程上必须再收敛一步：

> **通胀不是 correctness 信号，而是 marginal value 信号。**

也就是说：

- FAQPage 受限仍然是对的
- 但它已经不构成一个项目的差异化护城河

## 7.1 需要的数据

最小数据需求：

1. `cluster_id`
2. `first_seen_at per project`
3. `snapshot_date`
4. `eligible_project_count`
5. `supporting_project_count`
6. `adjusted_independence`

建议新增一个历史表：

```json
{
  "cluster_id": "cluster_faqpage_restricted",
  "snapshot_at": "2026-03-15",
  "eligible_projects": 4,
  "supporting_projects": 4,
  "adjusted_independence": 0.31,
  "root_count": 1,
  "adoption_rate": 1.0,
  "independent_adoption_rate": 0.31
}
```

## 7.2 通胀阶段模型

我建议用四阶段，而不是简单二元：

| 阶段 | 条件 | 含义 |
|---|---|---|
| `frontier` | adoption_rate < 0.2 | 前沿、稀缺 |
| `emerging_consensus` | 0.2 ≤ adoption_rate < 0.6 | 正在扩散 |
| `infrastructure` | adoption_rate ≥ 0.6 且持续稳定 | 行业基础设施 |
| `commodity` | adoption_rate 高且解释差异低 | 已经成常识模板 |

`commodity` 比 `infrastructure` 更强，意思是：

- 不只是“大家都知道”
- 而且“说法已经模板化了”

## 7.3 `detect_inflation(atom_id, domain_map_history)` 伪代码

```pseudo
function detect_inflation(cluster_id, domain_map_history):
    series = load_history(cluster_id, domain_map_history)
    if len(series) < 3:
        return {
            "status": "insufficient_history",
            "inflation_score": null
        }

    sort_by_snapshot_time(series)

    first = series[0]
    last = series[-1]

    adoption_growth = last.adoption_rate - first.adoption_rate
    independent_growth = last.independent_adoption_rate - first.independent_adoption_rate
    root_growth = last.root_count - first.root_count
    time_days = days_between(first.snapshot_at, last.snapshot_at)

    velocity = adoption_growth / max(time_days, 1)
    source_diversification = root_growth / max(time_days, 1)

    echo_component =
        adoption_growth * (1 - min(1.0, source_diversification * 10))

    infrastructure_component =
        last.adoption_rate * 0.5 +
        last.independent_adoption_rate * 0.3 +
        stability_score(series) * 0.2

    inflation_score = clamp(
        0.5 * echo_component + 0.5 * infrastructure_component,
        0.0, 1.0
    )

    phase =
        "frontier" if last.adoption_rate < 0.2
        "emerging_consensus" if last.adoption_rate < 0.6
        "commodity" if last.adoption_rate >= 0.8 and interpretation_variance(cluster_id) < 0.15
        "infrastructure"

    return {
        "inflation_score": inflation_score,
        "phase": phase,
        "adoption_rate": last.adoption_rate,
        "independent_adoption_rate": last.independent_adoption_rate,
        "velocity": velocity
    }
```

## 7.4 如何区分“通胀”与“验证”

这是最重要的问题。

如果 adoption_rate 上升，到底是：

- 因为大家都开始验证它了
- 还是因为大家都在互相抄

答案不能只看 adoption，要看 **adoption 和 source diversity 是否同步增长**。

### 核心判据

#### 更像“验证”

- adoption_rate 上升
- root_count 上升
- adjusted_independence 上升
- interpretation variance 仍然存在

#### 更像“通胀 / commoditization”

- adoption_rate 上升
- root_count 几乎不变
- adjusted_independence 不升反降
- 说法模板化

也就是：

> **验证增加可信度；通胀降低差异化价值。两者可以同时发生。**

FAQPage 受限就是典型：

- 可信度高
- 差异化价值低

---

## 8. 对 ORIGINAL 信号的校正：应该在 signal 层做，不该在 matching 层做

这个问题必须讲清楚。

当前 Health Check 的 `ORIGINAL = 图谱中没有匹配`。  
但没匹配不等于真独创，可能只是：

1. 图谱滞后
2. 图谱覆盖不够
3. 这条知识其实已经通胀，只是尚未被吸进图谱

### 8.1 为什么不能在 matching 层做校正

matching 层只回答一个问题：

> “图谱里有没有匹配物”

它不该背负“这条东西值不值钱”的语义。  
否则 matcher 会变成一个掺杂业务解释的黑箱。

### 8.2 正确位置：signal 层

流程应为：

1. `matching` 产出：`matched / unmatched`
2. `signal layer` 产出：`ORIGINAL / WEAK_ORIGINAL / LIKELY_COMMODITY`
3. `rendering` 再叙事化

### 8.3 推荐公式

```text
inflation_adjusted_originality =
  base_originality
  * map_freshness
  * (1 - inferred_commoditization_score)
```

其中：

- `base_originality`：来自 unmatched
- `map_freshness`：图谱最近更新时间因子
- `inferred_commoditization_score`：由 adoption / provenance / explicit-source coverage 估计

### 8.4 实际信号建议

| 信号 | 含义 |
|---|---|
| `ORIGINAL_STRONG` | 图谱未命中，且无通胀迹象 |
| `ORIGINAL_WEAK` | 图谱未命中，但有轻度通胀嫌疑 |
| `ORIGINAL_UNCERTAIN` | 图谱未命中，但图谱 coverage/freshness 不足 |
| `LIKELY_COMMODITY_GAP` | 图谱未命中，但它看起来像漏收录的基础常识 |

这比简单一个 `ORIGINAL` 强很多。

---

## 9. 用 4 个 SEO 项目验证方案

## 9.1 案例 A：FAQPage 受限

### 现象

- 4/4 项目都知道
- 来源几乎都能追溯到 Google 2023-08 公告

### 供应链判定

- provenance root：单一官方源
- project_count：4
- adjusted_independence：低到中
- trust：高

### 通胀判定

- adoption_rate：1.0
- independent_adoption_rate：有限
- phase：`infrastructure`

### 产品含义

- 不是 ORIGINAL
- 也不应被当成差异化亮点
- 但应被当成“必须具备的基础卫生”

## 9.2 案例 B：YouTube 相关性 0.737

### 现象

- 上游：Ahrefs 研究
- 3 个项目使用
- 解读不同

### 供应链判定

- provenance root：1
- interpretation variance：高
- distortion 风险：中高

### 产品含义

- 这不是“3 份独立验证”
- 这是“1 个上游数据点被 3 个项目二次编码”
- 如果某个项目把它从相关性写成优化因果律，应触发 `normative_escalation + scope_broadening`

## 9.3 案例 C：134-167 词最优段落

### 现象

- 3/4 项目出现
- 上游不明
- 可能是某项目首发后被回声传播

### 供应链判定

- explicit provenance：弱或无
- inferred provenance：可能单源
- echo risk：高

### 产品含义

- 不应因为“3 个项目都提到”就把它升成高置信共识
- 更合理的标签是：
  - `echo_suspect`
  - `low_root_diversity`
  - `high_commoditization_uncertainty`

## 9.4 案例 D：claude-seo ≈ 30x-seo

### 现象

- 两者几乎相同
- 极可能存在 fork / 套壳 / 重打包 lineage

### 供应链判定

- lineage_penalty：高
- 两者在 independence 计算中不应视为 2 个完整独立项目

### 产品含义

- 这不是供应链的边角案例
- 这是供应链系统必须优先修正的“假独立”样本

---

## 10. 复杂度、存储与工程侵入度

## 10.1 新增数据量

假设：

- 100 个项目
- 每项目 500 个 atoms
- 总 occurrence = 50,000

保守估计：

- 每 occurrence 平均 0.25 个显式 source refs → 12,500 条
- 每 occurrence 平均 0.15 个 propagation edges → 7,500 条
- history snapshots：每周 1 次 × 52 周 × 3,000 clusters → 156,000 条轻量记录

SQLite + JSONL + Parquet 下，这仍然是很小的量级。  
我会估计新增存储在 **几十 MB 到一两百 MB**，完全可控。

## 10.2 对现有管线的侵入程度

### 必改

1. Stage 0：加 Source Harvester
2. atom schema：加 provenance 字段
3. compare_projects.py：加 provenance clustering + lineage penalty
4. domain map builder：加 history snapshots
5. health check / renderer：消费 adjusted independence 与 inflation profile

### 可延后

1. inferred source recovery
2. 全量 distortion narrative
3. UI 级传播链可视化

## 10.3 复杂度

### 原始问题

同 cluster 内做两两比较是 `O(k²)`。

### 优化方案

1. **先按 cluster 限定候选**
2. **再按 explicit root 分桶**
3. **对剩余 occurrence 用 MinHash / ANN 召回**
4. **只对候选对做 slot diff**

于是整体更接近：

```text
O(total_occurrences)
+ O(total_candidate_pairs)
```

而不是粗暴的全局 `O(N²)`。

在 100 项目量级完全可做。

---

## 11. MVP 路径

## Phase 1 — NOW（1 周内）

目标：修正假独立。

交付：

1. 显式来源提取器
2. `source_refs.jsonl`
3. provenance clustering（显式来源优先）
4. adjusted independence
5. cluster 层 `echo_risk`

这个阶段就已经值回票价。

## Phase 2 — NOW-LITE / LATER（1-2 周）

目标：加入可解释扭曲检测。

交付：

1. slot-based distortion detector
2. 高精度 `scope_broadening` / `normative_escalation` / `condition_drop`
3. HEALTH_CHECK / domain map narrative 增强

## Phase 3 — LATER（需要更多项目和历史）

目标：做通胀。

交付：

1. snapshot history
2. inflation phase classifier
3. ORIGINAL adjustment
4. 趋势图 / 时间线

## Phase 4 — LATER（有 gold set 之后）

目标：做推断上游。

交付：

1. inferred provenance candidates
2. calibrated confidence
3. propagation narrative

---

## 12. 关键 trade-off 与风险

## 12.1 精度 vs 召回

供应链系统应该明显偏向 **精度优先**。

原因：

- 漏掉一条来源，只是少了洞察
- 错绑一条来源，会污染整条传播链

所以：

- 显式来源：事实层
- 推断来源：分析层

不要混。

## 12.2 显式引用 vs 推断引用

V1 我建议 **只把显式引用纳入核心评分**。  
推断引用可以生成候选，但不应进入：

- adjusted independence 的硬扣分
- ORIGINAL 的强降级

否则系统会“过拟合自己的猜测”。

## 12.3 通胀时间窗口敏感性

窗口太短：

- 会把噪声当趋势

窗口太长：

- 会把领域变迁看迟钝

建议：

- 小图谱：按 snapshot 数量，不按自然月
- 大图谱：同时维护 30d / 90d / 365d 三档

## 12.4 最大工程风险

### 风险 1：把“同一句话”误判成“同一来源”

很多行业常识会自然趋同，不一定彼此传播。

### 风险 2：把“官方单源”误判成“低可信”

Google 官方公告本来就是单源，但它并不低可信。

所以要分清：

- `root_count` 影响独立性
- `root_type` 影响可信度

### 风险 3：用小样本做大结论

只有 4 个项目时，通胀只能是“提示”，不是“审判”。

### 风险 4：用 narrative 覆盖 uncertainty

AI 生成的解释很容易显得比事实更确定。  
必须把以下字段直接带到渲染层：

- source_mode
- source_confidence
- root_count
- adjusted_independence
- inflation_history_length

---

## 13. 对 Claude 方向的补充与修正

我同意 Claude 的大方向：

- 供应链是 evidence chain / independence 的升级
- 通胀是第三类知识衰变

但工程上我会做两点修正：

### 修正 1：不要把供应链理解成“完整传播图”

真正可落地的对象是：

- `source_ref`
- `occurrence`
- `provenance_cluster`

而不是试图还原每一步真实传播过程。

### 修正 2：通胀不要直接绑定 correctness

通胀改变的是：

- ORIGINAL 的含义
- 差异化价值

不是知识真假。

如果把通胀误写成“衰减可信度”，会把“FAQPage 受限”这种正确但普及的知识错误降权。

---

## 14. 最终工程判断：now / later / never

| 能力 | 结论 | 理由 |
|---|---|---|
| 显式来源提取 | **NOW** | 低成本高收益，直接提高 evidence quality |
| provenance clustering | **NOW** | 这是修正假共识的核心 |
| adjusted independence | **NOW** | 可以直接接到 compare_projects 和 domain map |
| slot-based 扭曲检测 | **NOW-LITE** | 可解释、成本可控，但先做高精度规则 |
| inflation-adjusted ORIGINAL | **NOW-LITE** | 可作为弱校正，不应抢 matcher 的职责 |
| 全量知识通胀趋势系统 | **LATER** | 需要更多时间快照和领域样本 |
| 推断式上游恢复 | **LATER** | 价值高，但必须先有 gold set |
| “自动找唯一真源头” | **NEVER** | 这是知识生态里很多时候无法被证明的命题 |

我最终建议是：

> **现在就做供应链的“会计层”，暂时不做“侦探层”；  
> 现在就做通胀的“校正层”，暂时不做“裁判层”。**

这样既符合 Doramagic 的产品哲学，也符合工程现实。

---

## 15. 对 Doramagic 的真正意义

如果只从工程层看，这像是两个小功能。  
但从产品层看，它们其实在修两件更深的问题：

1. **供应链修的是“共识幻觉”**
2. **通胀修的是“独创幻觉”**

Doramagic 的价值，不只是会提取知识，  
而是知道：

- 哪些知识真的被独立验证过
- 哪些只是被很多项目回声传播
- 哪些看起来新，其实早就已经基础设施化

这会让 Doramagic 从“知识提取器”更进一步变成：

> **知识质量与知识稀缺性的编译器**

---

## 参考与可复用技术

本报告的工程方向可借鉴但不应直接照搬以下工作：

- SourcererCC，用于大规模代码克隆/近重复检测，适合项目 lineage 与近似复制识别：https://isr.uci.edu/content/sourcerercc-scaling-code-clone-detection-big-code.html
- NiCad 系列近似克隆检测研究，适合高精度 near-miss clone 思路参考
- Sentence-BERT，适合语义召回层而非最终事实判定：https://aclanthology.org/D19-1410/
- TruthFinder / truth discovery 一类多源冲突融合方法，适合做“源可靠性”启发，但不能直接套用到开源知识传播
- ProVe 这类 provenance verification 管线，适合参考“来源验证”思想：https://www.semantic-web-journal.net/content/prove-pipeline-automated-provenance-verification-knowledge-graphs-against-textual-sources-0

在 Doramagic 里，最正确的组合仍然是：

**代码做显式来源提取 + 槽位差分 + 统计校正；AI 只负责叙事。**


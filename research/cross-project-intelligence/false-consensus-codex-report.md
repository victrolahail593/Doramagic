# 错误共识检测（False Consensus Detection）— Codex 工程实现研究报告

> 视角：算法设计 + 数据结构 + 落地可行性  
> 日期：2026-03-15  
> 模型：Codex

---

## 0. 执行摘要

我的核心判断是：

> **Doramagic 不应该试图“判定一条共识是错的”，而应该为每个共识 cluster 计算一个“错误共识风险分”。**

这件事很重要，因为它决定了工程边界。

错误共识不是：

- `support_independence` 的替代品
- `provenance clustering` 的替代品
- `STALE` 的替代品

它是这三者之上的一个新层：

> **在“看起来像真共识”的 cluster 上，继续问一句：这条共识是否存在系统性误判风险？**

因此我推荐的工程路线不是：

- 新建一个“真假裁判器”

而是：

- 在 `AtomCluster` 上新增 `consensus_risk_profile`
- 用可解释的风险信号打分
- 在 Health Check / domain map / StitchCraft 中以 `risk annotation` 的形式消费

对“值不值得现在做”的明确判断：

| 能力 | 判断 | 原因 |
|---|---|---|
| 作为独立真伪判定系统 | **NEVER** | Doramagic 没有外部实验能力，无法形成“硬真值” |
| 作为 cluster 级风险评分层 | **NOW-LITE** | 可直接复用已有数据结构，收益明确，误报可控 |
| 作为完整的 standalone 子系统 | **LATER** | 需要更大的领域图谱和更多官方/研究型对照源 |

一句话概括：

> **错误共识检测不是在说“这条知识错了”，而是在说“这条共识不应该被当成无风险真理”。**

---

## 1. 先把边界讲清楚：什么叫错误共识，什么不叫

### 1.1 错误共识的精确定义

在 Doramagic 里，错误共识应定义为：

> **一个通过独立性和同源检测后仍成立的 atom cluster，但它的证据结构、时间结构、权威对齐或解释结构显示出明显的系统性风险。**

注意这一定义里没有“错”这个硬判断。  
因为工程上我们没有真值 oracle。

### 1.2 它和已有体系的关系

| 机制 | 解决的问题 | 不能解决的问题 |
|---|---|---|
| `support_independence` | 多个项目是不是看起来独立 | 独立的人也可能一起犯错 |
| `provenance clustering` | 多个项目是不是同一上游回声 | 不同上游也可能都在传错东西 |
| `DeprecationEvent` | 某条知识是否已被明确废弃 | 未废弃不等于正确 |
| `dark traps` | 单个项目/来源是不是有欺骗性结构 | 多个正常项目也可能形成错误共识 |
| `false consensus risk` | 这条共识是否不应被当成无风险真理 | 它也不能证明真伪 |

### 1.3 典型案例怎么分类

#### FAQPage 受限

- 属于：**正确共识**
- 原因：有官方 source，时间点明确，scope 清晰
- 错误共识风险应低

#### “134-167 词最优”

- 属于：**高风险启发式 / 可能的错误共识**
- 但在当前 4 项目样本里，更像“同源回声 + 弱实证”
- 也就是说，它不一定是“纯错误共识”，而是一个混合案例

#### “0.737 相关性 -> 因果性”

- 属于：**正确数据 + 错误解读**
- 这是最适合 false consensus risk 捕捉的案例

这个区分很重要。  
否则系统会把所有高风险 cluster 都叫“错误共识”，概念会失控。

---

## 2. 工程总原则：做风险层，不做真值层

我建议把 false consensus 做成一个 **cluster enrichment pass**：

```text
project atoms
  -> clustering
  -> support/provenance adjustment
  -> deprecation alignment
  -> false consensus risk scoring
  -> enriched domain map
```

核心原则有 4 条：

1. **代码说事实，AI 说故事**
2. **风险信号必须可解释**
3. **默认保守，宁可少报**
4. **优先 cluster 级，不优先 atom 级**

为什么优先 cluster？

- 错误共识本质是“跨项目重复”
- 单个 atom 的问题，更多属于 dark trap / fact-checking / deceptive source

所以 false consensus 的 natural home 是：

> **`AtomCluster` 之后，而不是单项目 extraction 之前。**

---

## 3. 可检测的风险信号

这里的关键不是“信号多”，而是“信号要能程序化”。

我建议 V1 只做 7 个信号。

---

## 3.1 信号 S1：高 normative force + 低 evidence strength

### 含义

如果一条 cluster 的表述非常强：

- must
- should always
- optimal
- best
- never

但支撑它的证据类型很弱：

- 无官方
- 无研究
- 无实验
- 只有 doc/community 复述

那它就是高风险。

### 检测算法

先把 `normative_force` 归一化：

```text
descriptive = 0.1
suggestive = 0.4
prescriptive = 0.7
mandatory = 1.0
optimality_claim = 1.0
```

再把 evidence strength 归一化：

```text
official = 1.0
peer_or_large_study = 0.9
code_enforced = 0.8
test_backed = 0.7
direct_project_measurement = 0.7
doc_reference = 0.4
community_reference = 0.3
inference_only = 0.1
```

然后只在 `claim_family in {heuristic, rule, benchmark, best_practice}` 上触发。

```pseudo
function signal_normative_evidence_mismatch(cluster):
    n = cluster.normative_force_score
    e = cluster.evidence_strength_score
    mismatch = max(0, n - e)
    return clamp(mismatch, 0, 1)
```

### 预期精度

- Precision：0.70-0.80
- Recall：0.45-0.60

### trade-off

- 优点：非常可解释
- 风险：对“经验型但确实有效”的 heuristics 会偏敏感

---

## 3.2 信号 S2：与官方规则 / DeprecationEvent 冲突

### 含义

如果 cluster 与官方文档或已知废弃事件直接冲突，风险应很高。

### 检测算法

复用 `DeprecationEvent` 和未来的 official constraint 表。

匹配维度：

- subject alias
- predicate opposition
- scope overlap
- effective_at

```pseudo
function signal_authority_conflict(cluster, deprecation_db, official_rules):
    candidates = retrieve_official_candidates(cluster.subject, cluster.scope)
    max_conflict = 0

    for event in candidates:
        if scopes_overlap(cluster.scope, event.scope) and predicates_conflict(cluster.predicate, event.predicate):
            if event.effective_at <= cluster.last_seen_at:
                max_conflict = max(max_conflict, 1.0)

    return max_conflict
```

### 预期精度

- Precision：0.90+
- Recall：0.20-0.35

### trade-off

- 优点：一旦命中，非常强
- 风险：覆盖范围很窄，只能抓“已知官方冲突”

---

## 3.3 信号 S3：间接引用堆积，无直接证据

### 含义

如果 cluster 的支撑主要来自：

- DOC
- COMMUNITY
- 引用二手总结

而没有：

- 官方 source
- 研究 source
- 直接实验
- code-enforced implementation

那它是典型“看起来很多人都说，但没有人真正证明”的风险。

### 重要限制

这个信号不能一刀切。  
必须先看 `claim_family`：

| claim_family | 期望的“直接证据” |
|---|---|
| `ecosystem_policy` | official source |
| `implementation_rule` | code/test |
| `heuristic_threshold` | study / direct measurement |
| `workflow_pattern` | code trace |

### 检测算法

```pseudo
function signal_indirect_evidence_only(cluster):
    expected = expected_evidence_families(cluster.claim_family)
    actual = cluster.evidence_family_distribution

    direct_score = sum(actual[x] for x in expected.direct)
    indirect_score = sum(actual[x] for x in expected.indirect)

    if direct_score > 0:
        return 0

    return clamp(indirect_score, 0, 1)
```

### 预期精度

- Precision：0.60-0.75
- Recall：0.50-0.65

### trade-off

- 优点：非常适合抓“行业口耳相传的伪常识”
- 风险：对纯外部知识领域会有一定误报，需要 claim_family 校正

---

## 3.4 信号 S4：解释升级 / 因果化

### 含义

最典型案例就是：

- 上游说“相关性”
- 下游说“应该做这个，因为它会提升效果”

这类错误不来自数据本身，而来自解释层。

### 检测算法

直接复用 supply chain 里的 distortion 分析结果。

重点看：

- `relation_escalation`
- `normative_escalation`
- `scope_broadening`

如果多个独立项目都出现同类升级，这就不再只是单项目误读，而是 cluster 风险。

```pseudo
function signal_interpretation_escalation(cluster, provenance_graph):
    escalated_members = 0
    total_members = 0

    for occ in cluster.member_occurrences:
        upstream = resolve_upstream_atom(occ, provenance_graph)
        if upstream is null:
            continue
        total_members += 1
        d = detect_distortion(upstream, occ)
        if has_any(d.flags, ["relation_escalation", "normative_escalation", "scope_broadening"]):
            escalated_members += 1

    if total_members == 0:
        return 0
    return escalated_members / total_members
```

### 预期精度

- Precision：0.75-0.85
- Recall：0.35-0.50

### trade-off

- 优点：对 “0.737 -> 因果性” 极强
- 风险：依赖 upstream 对齐质量

---

## 3.5 信号 S5：内部矛盾压力 / 隐性争议

### 含义

有些 cluster 看起来是共识，但图谱中其实存在强冲突簇，只是没有被编译成同一组对照关系。

例如：

- A 说 FAQPage “无用”
- B 说 FAQPage “对 AI crawler 仍有价值”

这不一定是错误共识，但如果一个 cluster 声称“绝对无用”，而领域内存在高质量反例，它就有风险。

### 检测算法

找：

- 同 subject
- scope overlap 高
- predicate 反向或 normative 方向冲突

并比较冲突方的 authority / freshness / independence。

```pseudo
function signal_contradiction_pressure(cluster, domain_map):
    candidates = retrieve_conflicting_clusters(cluster.subject, cluster.scope, domain_map)
    max_pressure = 0

    for other in candidates:
        if not predicates_conflict(cluster.predicate, other.predicate):
            continue
        pressure =
            0.4 * scope_overlap(cluster.scope, other.scope) +
            0.3 * other.authority_alignment +
            0.2 * other.adjusted_independence +
            0.1 * other.freshness_score
        max_pressure = max(max_pressure, pressure)

    return clamp(max_pressure, 0, 1)
```

### 预期精度

- Precision：0.60-0.70
- Recall：0.35-0.50

### trade-off

- 优点：能把“看似稳定，实则已有反证”的 cluster 揪出来
- 风险：容易把 scope 不同的正确分歧误报成风险，所以必须依赖 scope matching

---

## 3.6 信号 S6：时间异常 / 老结论长期无人更新

### 含义

某条结论非常老：

- 没有新引用
- 没有新验证
- 没有挑战
- 但还保持强 normative_force

这本身就是风险。

它不一定已被废弃，但可能已经脱离当前领域现实。

### 检测算法

先定义领域半衰期，例如 SEO 可设 180 天。

```pseudo
function signal_temporal_stagnation(cluster, now, domain_half_life_days):
    age_days = days_between(cluster.last_authoritative_refresh_at, now)
    challenge_gap = days_between(cluster.last_challenged_at or cluster.first_seen_at, now)

    if cluster.normative_force_score < 0.7:
        return 0

    age_score = min(1.0, age_days / (2 * domain_half_life_days))
    challenge_score = min(1.0, challenge_gap / (3 * domain_half_life_days))

    return 0.6 * age_score + 0.4 * challenge_score
```

### 预期精度

- Precision：0.50-0.65
- Recall：0.40-0.55

### trade-off

- 优点：能抓“老黄历型共识”
- 风险：对变化慢的子领域会偏激进

---

## 3.7 信号 S7：实现缺口

### 含义

如果多个项目都强烈宣称一个规则：

- 必须这样做
- 最优实践就是这样

但在它们自己的实现里并没有：

- enforcement
- validation
- automated checks
- tests

那这个 cluster 风险上升。

### 检测算法

这个信号只适用于 `claim_family in {implementation_rule, workflow_rule, operational_guardrail}`。

```pseudo
function signal_implementation_gap(cluster):
    if cluster.claim_family not in IMPLEMENTABLE_FAMILIES:
        return 0

    supported = count_members(cluster)
    enforced = count_members_with_code_or_test_enforcement(cluster)

    if supported == 0:
        return 0

    gap = 1 - enforced / supported
    return clamp(gap, 0, 1)
```

### 预期精度

- Precision：0.70-0.80
- Recall：0.25-0.40

### trade-off

- 优点：很适合抓“嘴上很确定，代码里没落实”
- 风险：很多知识型项目本来就不负责 enforcement，所以必须做 claim_family gating

---

## 4. 组合风险模型：不要用黑箱分类器，用“硬门 + noisy-OR”

### 4.1 为什么不用加权求和

纯加权求和的问题是：

- 一个超强风险信号会被几个低风险信号稀释
- 多个中等信号叠加不自然

### 4.2 为什么不用决策树

决策树的问题是：

- 小样本下极不稳定
- 用户很难理解“为什么是这个分支”

### 4.3 推荐模型：硬门 + noisy-OR

逻辑：

1. 先跑几个硬门条件
2. 再用 noisy-OR 合成剩余信号

#### 硬门

如果满足任一：

- `authority_conflict >= 0.95`
- `interpretation_escalation >= 0.8 and normative_evidence_mismatch >= 0.6`

则直接进入高风险区。

#### 合成公式

```text
consensus_risk_score = 1 - Π(1 - w_i * s_i)
```

其中：

- `s_i` = signal score
- `w_i` = signal reliability weight

建议初始权重：

| 信号 | 权重 |
|---|---:|
| authority_conflict | 1.00 |
| interpretation_escalation | 0.85 |
| normative_evidence_mismatch | 0.80 |
| indirect_evidence_only | 0.70 |
| contradiction_pressure | 0.65 |
| temporal_stagnation | 0.55 |
| implementation_gap | 0.60 |

### 4.4 `score_consensus_risk(cluster, domain_map, deprecation_db)` 伪代码

```pseudo
function score_consensus_risk(cluster, domain_map, deprecation_db, provenance_graph, now):
    # False consensus only makes sense after independence/provenance filters
    if cluster.support_count < 2:
        return not_applicable("insufficient_support")

    if cluster.adjusted_independence < 0.55:
        return not_applicable("handled_by_echo_risk")

    s1 = signal_normative_evidence_mismatch(cluster)
    s2 = signal_authority_conflict(cluster, deprecation_db, domain_map.official_rules)
    s3 = signal_indirect_evidence_only(cluster)
    s4 = signal_interpretation_escalation(cluster, provenance_graph)
    s5 = signal_contradiction_pressure(cluster, domain_map)
    s6 = signal_temporal_stagnation(cluster, now, domain_half_life_days=180)
    s7 = signal_implementation_gap(cluster)

    signals = {
        "normative_evidence_mismatch": s1,
        "authority_conflict": s2,
        "indirect_evidence_only": s3,
        "interpretation_escalation": s4,
        "contradiction_pressure": s5,
        "temporal_stagnation": s6,
        "implementation_gap": s7
    }

    if s2 >= 0.95:
        score = max(0.85, s2)
    else if s4 >= 0.8 and s1 >= 0.6:
        score = max(0.80, 1 - (1 - 0.85*s4) * (1 - 0.80*s1))
    else:
        score = 1
        weights = {
            "normative_evidence_mismatch": 0.80,
            "authority_conflict": 1.00,
            "indirect_evidence_only": 0.70,
            "interpretation_escalation": 0.85,
            "contradiction_pressure": 0.65,
            "temporal_stagnation": 0.55,
            "implementation_gap": 0.60
        }
        for name, value in signals.items():
            score = score * (1 - weights[name] * value)
        score = 1 - score

    band =
        "low" if score < 0.30
        "watch" if score < 0.55
        "suspect" if score < 0.80
        "high" otherwise

    reasons = sort_descending(signals).top(3)

    return {
        "applicable": true,
        "risk_score": round(score, 3),
        "risk_band": band,
        "primary_reasons": reasons,
        "signals": signals
    }
```

### 4.5 阈值策略：偏保守

我建议用户可见层要明显偏保守。

| 分数区间 | 用户呈现 |
|---|---|
| `< 0.30` | 不显示 |
| `0.30 - 0.54` | 内部 watch |
| `0.55 - 0.79` | `SUSPECT_CONSENSUS` |
| `>= 0.80` | `HIGH_RISK_CONSENSUS` |

原因：

- 错误指控比漏报更伤害 Doramagic 的可信度
- 用户需要的是“谨慎提醒”，不是“系统自封裁判”

---

## 5. 是否需要新的信号类型

我的结论是：

> **不应该把它做成第 8 个互斥主信号。**

### 5.1 为什么不该新增第 8 个互斥主信号

Health Check 现有 7 类信号描述的是：

- 项目相对图谱的状态

而 false consensus 描述的是：

- 图谱中某条 cluster 自身的风险

它是正交维度，不是互斥类别。

例如：

- `ALIGNED + SUSPECT_CONSENSUS`
- `MISSING + SUSPECT_CONSENSUS`
- `CONTESTED + SUSPECT_CONSENSUS`

都可能同时成立。

### 5.2 推荐设计

主信号保持 7 类不变。  
新增：

- `risk_annotations[]`
- 其中可包含 `SUSPECT_CONSENSUS`

### 5.3 与暗雷体系的关系

我的判断：

- **暗雷体系是 per-project / per-source 风险**
- **错误共识是 per-cluster / cross-project 风险**

因此：

> 错误共识不是一个暗雷类别，而是一个消费暗雷信号的上层聚合器。

例如：

- 某 cluster 的 member projects 中 3 个都命中 “经验值伪装成规律” 暗雷
- 那么 cluster 的 `normative_evidence_mismatch` 应被抬高

---

## 6. 数据结构设计

## 6.1 在 `AtomCluster` 上新增字段

```json
{
  "cluster_id": "seo:cluster_031",
  "canonical_claim": "Optimal AI-citable paragraph length is 134-167 words",
  "support_count": 3,
  "support_independence": 0.74,
  "adjusted_independence": 0.58,
  "confidence": 0.63,
  "status": "consensus",
  "claim_family": "heuristic_threshold",
  "normative_force_score": 1.0,
  "evidence_strength_score": 0.22,
  "consensus_risk_profile": {
    "applicable": true,
    "risk_score": 0.71,
    "risk_band": "suspect",
    "primary_reasons": [
      "normative_evidence_mismatch",
      "indirect_evidence_only",
      "temporal_stagnation"
    ],
    "signals": {
      "normative_evidence_mismatch": 0.78,
      "authority_conflict": 0.0,
      "indirect_evidence_only": 0.83,
      "interpretation_escalation": 0.10,
      "contradiction_pressure": 0.22,
      "temporal_stagnation": 0.61,
      "implementation_gap": 0.0
    },
    "calibration_version": "fcd-v0.1",
    "scored_at": "2026-03-15T12:00:00Z"
  }
}
```

## 6.2 新增轻量表：`ConsensusRiskSignal`

如果要做审计和调参，最好单独存一张信号表。

```json
{
  "cluster_id": "seo:cluster_031",
  "signal_code": "normative_evidence_mismatch",
  "score": 0.78,
  "reason_codes": ["optimality_claim", "no_study", "doc_only_support"],
  "evidence_refs": [
    "project:geo-seo-claude:atom_112",
    "project:claude-seo:atom_317"
  ]
}
```

## 6.3 `HealthFinding` 扩展

```json
{
  "finding_id": "HC-029",
  "signal": "ALIGNED",
  "cluster_id": "seo:cluster_031",
  "risk_annotations": ["SUSPECT_CONSENSUS"],
  "consensus_risk_score": 0.71,
  "risk_summary": {
    "primary_reasons": [
      "normative_evidence_mismatch",
      "indirect_evidence_only"
    ]
  }
}
```

### trade-off

- 优点：无需重写 7 类主信号
- 风险：前端与渲染层需要适配 annotation 展示

---

## 7. 与管线的集成位置

## 7.1 主计算位置

主计算应放在：

> **domain map compile 阶段，且在 provenance clustering 之后。**

顺序建议：

```text
project_fingerprint
  -> atom clustering
  -> support_independence
  -> provenance clustering
  -> adjusted_independence
  -> deprecation alignment
  -> false consensus scoring
  -> compiled domain map
```

原因：

- 没做 provenance clustering 前，很多“错误共识”其实只是 echo consensus
- false consensus 只应该处理“已经通过独立性过滤”的 cluster

## 7.2 单项目管线怎么消费

单项目提取阶段不负责生成 false consensus。  
但 Stage 3.5 / Stage 3.7 可消费已有图谱中的风险信息：

- 如果当前项目提取出的 rule 对齐到高风险 cluster
- 则降低它在 narrative / cards 中的 certainty

换句话说：

> **false consensus 是图谱生产层计算，单项目和体检层消费。**

## 7.3 和 Health Check 的关系

Health Check 最适合展示它，因为 Health Check 本来就不是“编译共识”，而是“解释项目与图谱的关系”。

推荐在 `HEALTH_CHECK.md` 中新增一节：

```text
## Consensus Risk
- ALIGNED but risky consensus: 2
- High-risk consensus clusters referenced by this project: 1
- Examples: ...
```

## 7.4 计算成本

如果已有：

- cluster index
- provenance graph
- deprecation index

那么 false consensus scoring 是轻量的。

复杂度大致：

```text
O(number_of_clusters × avg_candidate_conflicts)
```

候选冲突可通过：

- subject alias index
- scope hash
- predicate opposition table

压缩到很小。

对 1k-5k clusters 量级，完全可接受。

---

## 8. 用 4 个 SEO 项目做验证

这里必须诚实：

4 个项目太少，不足以“证明” false consensus detector 的统计有效性。  
但足以验证机制是否合理。

## 8.1 FAQPage 受限

### 预期结果

- `authority_conflict = 0`
- `indirect_evidence_only = 0 or low`
- `normative_evidence_mismatch = low`
- `temporal_stagnation = low`
- `consensus_risk_score ≈ 0.10 - 0.20`

### 原因

- 有官方 source
- 时间明确
- 作用域可描述
- 多项目一致

这应是系统的正确对照组。

## 8.2 “134-167 词最优”

### 预期结果

- `normative_evidence_mismatch = high`
- `indirect_evidence_only = high`
- `temporal_stagnation = medium/high`
- `authority_conflict = 0`

### 风险分预期

- 若 `adjusted_independence < 0.55`：标记为 echo-risk 主导，false consensus not_applicable
- 若强行打分：`0.60 - 0.80`

### 解释

这不是最纯的 false consensus 案例，  
但它是最好的“unsupported consensus”案例。

## 8.3 “0.737 相关性 -> 因果性”

### 预期结果

- `interpretation_escalation = high`
- `normative_evidence_mismatch = medium/high`
- `indirect_evidence_only = low to medium`（取决于是否保留 Ahrefs source）

### 风险分预期

- `0.65 - 0.85`

### 解释

这是当前 4 项目里最接近“纯错误共识”的案例。  
因为问题不在 source 是否存在，而在多个项目可能独立地犯了同一种解释错误。

## 8.4 Ground truth 划分

基于当前数据，建议临时 gold set：

| cluster | 标签 |
|---|---|
| FAQPage 受限 | correct_consensus |
| INP 替代 FID | correct_consensus |
| 134-167 词最优 | unsupported_or_echo_risk |
| 0.737 因果化 | suspect_false_consensus |

### 预期 precision / recall

V1 工程预期，不是实测结果：

- `HIGH_RISK_CONSENSUS` precision：0.75+
- `SUSPECT_CONSENSUS` precision：0.60-0.75
- overall recall：0.35-0.55

这个 recall 不高，但这是可接受的。  
因为 false consensus 的误报代价高于漏报。

---

## 9. 值不值得现在做

我的明确结论：

> **NOW-LITE。**

不是 because 它已经成熟，  
而是 because 它可以低成本挂在已有体系上，并直接解决一个真实信任问题。

## 9.1 为什么不是 NOW-FULL

因为现在缺：

- 更大的图谱规模
- 更多官方 / 研究对照源
- 更好的 gold set

在 4 个项目规模下，做 full false consensus system 会过拟合少数案例。

## 9.2 为什么不是 LATER

因为很多基础设施已经有了：

- `support_independence`
- `provenance clustering`
- `DeprecationEvent`
- `Health Check`
- `dark trap` 输出

再往上加一层 explainable risk score，边际成本并不高。

## 9.3 最小形态是什么

最小可行形态：

1. 只在 `AtomCluster` 上增加 `consensus_risk_profile`
2. 只做 4 个高价值信号
   - `normative_evidence_mismatch`
   - `authority_conflict`
   - `interpretation_escalation`
   - `indirect_evidence_only`
3. 只在 Health Check 中展示 `risk_annotation`
4. 不做单项目提取时的强制阻断

这已经足够验证价值。

## 9.4 多大规模图谱才真正有效

我的判断：

| 图谱规模 | false consensus 能力 |
|---|---|
| 4 项目 | 机制验证，案例驱动 |
| 8-12 项目 | 可开始稳定发现风险模式 |
| 15+ 项目 | 统计意义显著，值得做更完整 calibration |

所以：

> **现在做轻量版是对的；想让它成为“领域级信任层”，至少要等到 10+ 项目。**

---

## 10. 工程风险与新发现

## 10.1 最大风险：把“有争议”误报成“有问题”

很多 cluster 只是：

- scope 不同
- 目标不同
- 优化对象不同

不是错误共识。

所以 scope matching 和 conflict typing 是生死线。

## 10.2 第二风险：把“无官方 backing 的实战经验”一律打成高风险

很多真正有价值的工程经验，本来就没有论文和官方文档。

解决方法不是放弃 false consensus，  
而是：

- 让它只输出 risk，不输出 verdict
- 并让 claim_family 校正证据要求

## 10.3 第三个风险：重复造轮子

如果把 false consensus 做成另一个独立子系统，就会和：

- supply chain
- health check
- dark traps
- stale detection

产生大量重叠。

正确做法是：

> **把它做成 cluster enrichment pass。**

## 10.4 我看到的更大机会

false consensus 的更深价值，不在“抓错”，而在：

> **给 Doramagic 增加一个“不要过度相信重复” 的系统免疫层。**

这会改变很多下游决策：

- 共识排序
- 原创性判断
- StitchCraft 的默认拼装权重
- Health Check 的高信号优先级

换句话说：

它不是一个孤立功能，  
而是一个 **consensus trust adjustment layer**。

---

## 11. 最终建议

如果只保留一句工程建议，那就是：

> **现在就做一个保守的、可解释的、cluster 级错误共识风险层；不要试图做真值引擎。**

落地上最稳的路径是：

1. 先复用 provenance / deprecation / dark trap 输出
2. 在 domain map compile 后加 `consensus_risk_profile`
3. 只在 Health Check 和地图渲染里消费
4. 等图谱规模上来后再做 calibration 和更复杂信号

这是符合 Doramagic 产品哲学的：

- 不教用户做事
- 不假装自己知道真相
- 但也不把“很多人都这么说”直接当作可靠真理


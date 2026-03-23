# Knowledge Health Check 工程研究报告：原子匹配、过时检测、缓存与管线集成

## 1. 先给结论

我对这个功能的核心判断是：

> **Knowledge Health Check 不是一个“评分器”，而是一个“项目原子 vs 领域图谱”的受约束匹配与分类引擎。**

这句话很重要，因为它直接决定了工程实现：

- 不是对 `CLAUDE.md` 做文本分析
- 不是让 LLM 看一眼图谱然后“写个体检”
- 不是新系统

而是：

## **把项目知识原子对齐到领域图谱的 atom clusters，然后根据匹配状态生成 7 类信号。**

所以 Health Check 的工程骨架应该是：

```text
project_fingerprint.json
  -> canonical project atoms
  -> candidate retrieval
  -> structured alignment
  -> signal classification
  -> health_check.json
  -> HEALTH_CHECK.md
```

这里最关键的不是“渲染得多漂亮”，而是：

1. 原子匹配是否靠谱
2. scope 是否处理正确
3. 过时知识是否能独立检测
4. 图谱版本和缓存是否可追溯

如果这四件事成立，Health Check 就会是领域图谱的一个稳定消费层。  
如果这四件事不成立，它会退化成另一种“看起来有洞察的摘要生成器”。

---

## 2. 我同意 Claude 的大方向，但有三个工程补充

Claude 的报告已经把产品层和信号层定义得很完整了。我只指出三个工程上的补充或修正。

## 2.1 Stage 3.7 是对的，但必须是“可选阶段”

我同意把体检放在：

- Stage 3.5 fact-checking 之后
- Stage 4 narrative 之前

也就是一个新的 `Stage 3.7`

但工程上要加一句：

> **Stage 3.7 不能成为硬依赖。没有匹配图谱时，Soul Extractor 仍应能正常完成。**

所以它应该是：

- `optional enrich stage`
- 有图谱就跑
- 无图谱就跳过

否则会把单项目提取和领域图谱耦死。

## 2.2 slot matching 是对的，但不能只有 slot matching

Claude 强调“不要用纯 embedding，相似度会混淆 scope”，这个判断我完全同意。

但如果只做 slot matching，会有两个问题：

1. 原子 canonicalization 的噪声会让很多“其实同义”的 atom 匹配不上
2. paraphrase / domain synonym / alias 会导致召回太低

所以正确方案不是：

- `slot matching` 替代 `semantic retrieval`

而是：

- **semantic retrieval 做候选召回**
- **slot matching 做最终裁决**

也就是：

## **ANN/LSH 负责找谁值得比；structured matcher 负责判定是不是同一个 atom。**

## 2.3 不建议把 7 类信号全部放在同一条规则链上

Claude 的 7 类分类是对的，但工程上应拆成两路：

### Route A: deterministic signal engine

- ALIGNED
- STALE
- MISSING
- ORIGINAL

### Route B: interpretive signal engine

- DIVERGENT
- DRIFTED
- CONTESTED

原因：

- A 路主要依赖匹配与阈值
- B 路需要更多上下文与冲突图

这两路混在一个 matcher 里，后续维护会很痛苦。

---

## 3. 核心数据结构

体检的输入不是卡片全文，而是 canonical atoms。

## 3.1 项目原子：`ProjectAtom`

```json
{
  "atom_id": "claude-seo:dr_004",
  "type": "decision_rule",
  "claim": "FAQPage rich results are restricted since 2023-08",
  "normalized_claim": "faqpage rich results restricted",
  "subject": "FAQPage schema",
  "predicate": "availability_restricted",
  "object": "non-government-and-healthcare-sites",
  "scope": {
    "engine": ["google-rich-results"],
    "time": ["2023-08+"],
    "persona": ["seo"],
    "environment": ["production"],
    "version": ["current"]
  },
  "normative_force": "warning",
  "evidence_level": "E2",
  "evidence_refs": ["issue#123", "file:line"],
  "first_seen_at": "2023-08-08",
  "last_verified_at": "2026-03-15",
  "embedding_ref": "emb://..."
}
```

## 3.2 图谱簇：`AtomCluster`

```json
{
  "cluster_id": "seo-geo:cluster_017",
  "type": "decision_rule",
  "representative_claim": "FAQPage rich results restricted since 2023-08",
  "canonical_slots": {
    "subject": "FAQPage schema",
    "predicate": "availability_restricted",
    "object": "non-government-and-healthcare-sites"
  },
  "scope_signature": {
    "engine": ["google-rich-results"],
    "time": ["2023-08+"],
    "persona": ["seo"]
  },
  "member_atoms": [
    "claude-seo:dr_004",
    "30x-seo:dr_007"
  ],
  "support_count": 2,
  "support_independence": 0.76,
  "confidence": 0.91,
  "status": "consensus",
  "freshness_state": "fresh",
  "deprecated_by": null,
  "superseded_by": null,
  "embedding_ref": "emb://cluster_017"
}
```

## 3.3 废弃事件：`DeprecationEvent`

STALE 检测不应完全依赖图谱。

```json
{
  "event_id": "seo:google:cwv:fid_deprecated",
  "domain_id": "seo-geo",
  "subject_aliases": ["FID", "First Input Delay"],
  "predicate": "deprecated_for",
  "replacement": "INP",
  "effective_at": "2024-03-12",
  "severity": "high",
  "source_kind": "official",
  "source_refs": ["google-docs-url"],
  "matching_hints": {
    "engine": ["google-search", "core-web-vitals"],
    "artifact_types": ["decision_rule", "concept"]
  }
}
```

## 3.4 体检结果：`HealthFinding`

```json
{
  "finding_id": "HC-012",
  "signal": "MISSING",
  "severity": "HIGH-SIGNAL",
  "project_atom_id": null,
  "cluster_id": "seo-geo:cluster_031",
  "match_mode": "none",
  "score": 0.0,
  "reason_codes": ["high_consensus_cluster", "no_project_match"],
  "scope": {
    "engine": ["ai-crawlers"],
    "persona": ["geo"]
  },
  "evidence": {
    "support_count": 4,
    "support_independence": 0.81,
    "map_version": "seo-geo@2026-03-15+sha256:abc123"
  },
  "narrative": null
}
```

## 3.5 缓存键：`HealthCheckCacheKey`

```json
{
  "project_fingerprint_hash": "sha256:...",
  "domain_map_version": "seo-geo@2026-03-15+sha256:abc123",
  "matcher_version": "matcher-v0.3.1",
  "deprecation_db_version": "depdb-2026-03-15",
  "config_hash": "sha256:..."
}
```

这 5 个字段缺一个，缓存都不安全。

---

## 4. 原子匹配算法

这是整个系统的核心。

### 结论

> **匹配必须是“三段式”：候选召回 -> 结构化裁决 -> 信号分类。**

而不是：

- 直接 embedding top-1
- 直接 string match
- 直接 slot exact match

## 4.1 为什么不能纯 embedding

Claude 已经指出关键问题：scope。

例如：

- `FAQPage 对 Google rich results 受限`
- `FAQPage 对 AI crawler 仍有引用价值`

embedding 很可能会认为它们“很近”，但在体检里这两条恰恰不能视为 ALIGNED。

所以 embedding 只适合：

- 找候选

不适合：

- 做最终判定

## 4.2 为什么不能纯 slot exact matching

因为 canonicalization 永远不完美。

例如：

- `AI crawlers do not execute JS`
- `CSR pages are invisible to LLM bots`

它们在 slot 层可能不完全一致，但本质上是同一类约束。

所以精确 slot matching 只适合：

- 最终高置信 exact aligned

不适合：

- 做召回

## 4.3 推荐算法

### Step 1: 候选召回

按 type + domain + subject bucket 先切小搜索空间，再做两路召回：

1. lexical candidate retrieval
2. semantic candidate retrieval

#### 1. lexical candidate retrieval

用：

- subject alias table
- normalized claim token overlap
- MinHash/SimHash sketch

#### 2. semantic candidate retrieval

用：

- atom embedding ANN

输出一个候选集合，通常每个项目 atom 只需要 5-20 个候选。

### Step 2: structured matcher

对每个候选计算一个分层得分：

```text
MatchScore =
  0.30 * subject_score +
  0.25 * predicate_score +
  0.15 * object_score +
  0.20 * scope_score +
  0.10 * normative_force_score
```

其中：

- `subject_score`
  - exact alias match = 1.0
  - ontology sibling = 0.8
  - lexical/semantic close = 0.6
- `predicate_score`
  - exact relation = 1.0
  - same family = 0.75
- `object_score`
  - exact / compatible / incompatible
- `scope_score`
  - 时间、引擎、persona、environment 的加权 Jaccard
- `normative_force_score`
  - `critical > warning > info` 方向一致时加分

## 4.4 匹配阈值建议

我建议用四段阈值，而不是二元命中/不命中。

### `EXACT_ALIGNED`

- `MatchScore >= 0.92`
- 且 `scope_score >= 0.9`
- 且不存在 semantic opposition

### `SEMANTIC_ALIGNED`

- `0.80 <= MatchScore < 0.92`
- 且 `scope_score >= 0.75`
- 且没有更高分冲突候选

### `PARTIAL_MATCH`

- `0.62 <= MatchScore < 0.80`
- 或 slot 对齐但 scope 有部分重叠

### `NO_MATCH`

- `MatchScore < 0.62`

### Trade-off

- 阈值高：precision 高，recall 低，ORIGINAL 假阳性会上升
- 阈值低：recall 高，MISSING 会漏掉，ALIGNED 假阳性会上升

对于 Health Check，**我建议偏保守**：

- 宁可少报 ALIGNED
- 不要把 scope 不一致的 atom 硬判成一致

---

## 5. 7 类信号的工程判定逻辑

## 5.1 ALIGNED

项目 atom 匹配到一个：

- `cluster.status in {consensus, widely_supported}`
- 且 `match_mode in {EXACT_ALIGNED, SEMANTIC_ALIGNED}`
- 且 `scope_overlap >= 0.75`

则记为 `ALIGNED`。

### 注意

不要要求 cluster 一定是全领域共识。  
中等支持但高独立性、非冲突的 cluster 也可以视为 aligned reference。

## 5.2 MISSING

Claude 问的关键问题是：图谱中“共识覆盖率 > X%”的原子缺失时，X 该是多少？

### 我的建议

不要只用单个 `X`，要用双阈值：

#### 条件 1：覆盖率阈值

`effective_coverage >= 0.60`

其中：

`effective_coverage = support_count_weighted / independent_project_count`

#### 条件 2：独立性阈值

`support_independence >= 0.55`

#### 条件 3：最小独立支持数

`independent_support_count >= 3`

### 为什么是这组值

- `0.60`
  - 对 10 项目图谱意味着至少 6 个支持
  - 对 4 项目 alpha 图谱意味着至少 3 个支持
- `0.55 independence`
  - 过滤同源传播造成的假共识
- `>= 3` independent support
  - 防止小图谱里 2 个项目就被当成行业标准

### MISSING 判定

如果 cluster 满足上述条件，且：

- 项目中没有 `EXACT_ALIGNED / SEMANTIC_ALIGNED`
- 也没有一个明确 `DIVERGENT / CONTESTED` 的替代 atom

则标为 `MISSING`。

### Trade-off

这个阈值设计明显偏保守。  
好处是：

- 不会把脆弱图谱里的“暂时观察”包装成缺失警报

坏处是：

- 早期图谱的 MISSING recall 会偏低

我认为这是对的，因为体检比推荐更需要稳。

## 5.3 ORIGINAL

Claude 也问到了最难点：怎么排除“只是换个说法”的假阳性？

### ORIGINAL 判定必须同时满足

1. 没有 `EXACT_ALIGNED`
2. 没有 `SEMANTIC_ALIGNED`
3. 没有 `PARTIAL_MATCH + scope_compatible`
4. nearest cluster distance 足够大
5. 不是 alias expansion / ontology sibling / obvious paraphrase

### 建议做法

定义：

`novelty_score = 1 - best_match_score`

并要求：

- `novelty_score >= 0.30`
- 且 `best_scope_overlap < 0.60`

### 额外安全阈值

对高价值 ORIGINAL，再做一个 second-pass：

- 用更大的候选窗口重新检索
- 如果仍无可信匹配，才标 ORIGINAL

### Trade-off

这会增加一点计算成本，但能显著降低“只是表述不同”的假 ORIGINAL。

## 5.4 STALE

STALE 不依赖图谱即可运行。

判定条件：

- 项目 atom 匹配到一个明确 `DeprecationEvent`
- 或 atom cluster 自身 `freshness_state in {deprecated, superseded}`

必须有明确：

- `effective_at`
- `replacement or status`

这是一类确定性信号。

## 5.5 DRIFTED

DRIFTED 和 STALE 不是一回事。

### STALE

- 明确废弃
- 有硬事件
- 通常来自官方源或高置信 replacement

### DRIFTED

- 没有明确废弃
- 但领域重心已偏移
- 项目还停留在旧重心

### DRIFTED 检测建议

判定条件：

1. 项目 atom 对应 cluster 仍有效，不是 deprecated
2. 但该 cluster 的领域权重在最近 `T` 窗口内明显下降
3. 同主题的新 cluster 权重明显上升

例如：

- old metric cluster support ratio 从 `0.72 -> 0.31`
- new metric cluster support ratio 从 `0.18 -> 0.74`

这时旧 cluster 对应项目可标 `DRIFTED`。

### 工程前提

DRIFTED 需要：

- 图谱有时间版本
- cluster 有时间序列统计

所以它比 STALE 复杂，建议 V1 先做轻量版：

- 只在存在明确新旧替代对时检测

## 5.6 DIVERGENT

项目原子与图谱有高相似 cluster，但：

- claim 方向不同
- scope 相近
- 且冲突被归类为“路线差异”而非事实错误

此时标 `DIVERGENT`。

例子：

- 技术 SEO 权重 25%
- AI visibility 权重 25%

这不一定有对错，但表示站队不同。

## 5.7 CONTESTED

当图谱内部本身存在两个以上高支持、互相冲突的 cluster，且项目站其中一方时：

- 标 `CONTESTED`

和 DIVERGENT 的差异：

- DIVERGENT 是项目偏离 dominant cluster
- CONTESTED 是图谱内部没有 dominant cluster

---

## 6. STALE 检测引擎

## 6.1 废弃事件列表的数据结构

我建议单独维护一个：

- `deprecation_events.jsonl`

因为它本质上是 append-only knowledge base，不适合埋进某个 domain map 表里。

每行一条事件：

```json
{
  "event_id": "seo:google:faqpage:restricted_2023_08",
  "domain_id": "seo-geo",
  "aliases": ["FAQPage schema", "FAQ rich results"],
  "event_kind": "restricted",
  "effective_at": "2023-08-08",
  "replacement": null,
  "source_tier": "official",
  "source_refs": ["google-docs-url"],
  "match_rule": {
    "subject": ["FAQPage schema"],
    "predicate": ["availability_general"],
    "engine": ["google-rich-results"]
  }
}
```

## 6.2 维护机制

三种来源：

### A. 官方源

- API docs
- changelog
- Google Search docs
- vendor deprecation notices

优先级最高。

### B. 图谱内观察

如果多个新项目反复出现替代方案，旧 atom 下降明显，可生成候选 drift event。

### C. 社区共识

只可作为弱信号，不应直接变成 hard deprecation。

### 维护原则

- `official` 可直接进入 STALE engine
- `community` 只能进入 `candidate_events`
- 经人工或高置信交叉验证后再提升

## 6.3 没有领域图谱能不能跑 STALE

可以。

这点我和 Claude 一致，而且我会把它做成代码结构上的显式分离：

```text
stale_engine(project_atoms, deprecation_db)
map_alignment_engine(project_atoms, domain_map)
health_classifier(...)
```

这样：

- 无图谱时仍能跑 `STALE`
- 有图谱时再叠加其余 6 类信号

这会让 Stage 3.7 的降级路径非常干净。

---

## 7. 数据流与管线集成

## 7.1 Stage 3.5 -> Stage 3.7 接口

Stage 3.5 之后，系统应已有：

- validated cards
- normalized atom candidates
- traceability status

因此 Stage 3.7 不应再从 markdown 反解析。

### 推荐接口

输入：

```json
{
  "project_fingerprint_path": "...",
  "validated_atoms_path": "...",
  "traceability_report_path": "...",
  "domain_map_ref": "seo-geo@2026-03-15+sha256:abc123",
  "deprecation_db_ref": "depdb-2026-03-15"
}
```

输出：

```json
{
  "health_check_path": ".../health_check.json",
  "cache_hit": false,
  "summary": {
    "aligned": 18,
    "stale": 1,
    "missing": 3,
    "original": 6,
    "divergent": 2,
    "drifted": 0,
    "contested": 1
  }
}
```

## 7.2 完整数据流

```text
validated project atoms
  + domain router
  + map version resolver
  + deprecation db resolver
    -> cache lookup
    -> stale engine
    -> candidate retrieval
    -> structured matcher
    -> signal classifier
    -> severity scorer
    -> health_check.json
    -> markdown renderer
```

## 7.3 复杂度与优化

朴素复杂度：

- `N` 个项目原子
- `M` 个图谱原子
- 全量比较：`O(N*M)`

这在图谱稍大后不可接受。

### 优化方案

#### 1. 先按 `type` 分桶

- concept 只和 concept 比
- decision_rule 只和 decision_rule 比

#### 2. 再按 `subject` / ontology family 分桶

#### 3. 再做 ANN / lexical retrieval

把每个 atom 的候选数压到 `k`

则复杂度降为：

- `O(N * k)`

其中 `k` 通常可控制在 10-20。

#### 4. 对 STALE 单独跑

STALE engine 只需要：

- alias index
- event match

通常是 `O(N * log E)` 或更低。

## 7.4 缓存设计

重复体检必须命中缓存。

### 缓存条件

同一项目对同一图谱版本、同一 matcher 版本、同一 deprecation db 版本、同一配置：

- 直接返回缓存

### 存储建议

在 `health_checks/` 目录保存：

```text
health_checks/
  seo-geo/
    sha256_<cache_key>.json
    sha256_<cache_key>.md
```

并在 SQLite 里建索引表：

```sql
CREATE TABLE health_check_cache (
  cache_key TEXT PRIMARY KEY,
  project_hash TEXT NOT NULL,
  domain_map_version TEXT NOT NULL,
  matcher_version TEXT NOT NULL,
  deprecation_db_version TEXT NOT NULL,
  created_at TEXT NOT NULL,
  json_path TEXT NOT NULL,
  md_path TEXT
);
```

---

## 8. 图谱依赖管理

## 8.1 图谱更新后旧体检是否失效

答案是：

- 不删除
- 但标为 `outdated_by_map_version`

因为旧体检本身是一个时间快照，有保留价值。

### 规则

如果：

- `domain_map_version != latest_version_for_domain`

则在渲染层提示：

- `This report was generated against an older domain map`

## 8.2 图谱版本管理

不要只用日期字符串。

建议：

`domain_id@semantic_version+content_hash`

例如：

`seo-geo@0.3.2+sha256:abc123`

其中：

- semantic version：人可读版本
- content hash：强一致缓存键

## 8.3 多领域图谱匹配

用户项目可能跨领域，例如：

- SEO + content marketing
- SEO + analytics

因此不要强制单图谱。

### 推荐方案

先跑 domain router，输出：

```json
[
  {"domain_id": "seo-geo", "score": 0.81},
  {"domain_id": "content-marketing", "score": 0.67}
]
```

### 使用规则

- 最高分域 `>= 0.75`：主图谱
- 第二图谱 `>= 0.55`：可选副图谱

然后有两种模式：

### single-map mode

只对主图谱做体检，简单稳定，适合 V1。

### blended-map mode

分别跑两个图谱，再合并 findings，适合 V1.1+

我建议 V1 只做 `single-map mode`，但在元数据里保留 secondary domain candidates。

---

## 9. HEALTH_CHECK.md 渲染管线

## 9.1 哪些应确定性渲染

以下内容必须代码渲染：

- 标题
- 图谱版本
- summary counts
- findings table
- reason codes
- source links
- evidence stats

因为这些都是事实层。

## 9.2 哪些交给 LLM

只交给 LLM 做两件事：

### A. Executive summary

2-4 段，解释：

- 这个项目整体在图谱里的位置
- 最重要的高信号 finding
- originality / divergence 的含义

### B. finding explanation

只对 `HIGH-SIGNAL` 和部分 `SIGNAL` 生成简短说明。

不需要每条 finding 都讲长文。

## 9.3 narrative prompt 建议

```text
You are rendering a knowledge health check explanation.

Rules:
- Do not invent findings.
- Only explain facts present in the JSON.
- Distinguish consensus-backed findings from map-limited observations.
- Never prescribe changes. Describe what the finding means.
- If the map support is weak, say so explicitly.

Input:
1. project summary
2. reference map metadata
3. top HIGH-SIGNAL findings
4. top ORIGINAL / DIVERGENT findings

Output:
- 1 short executive summary
- bullet explanations for selected findings
```

## 9.4 token 成本估算

如果只喂：

- summary
- top 5-10 findings
- map metadata

那渲染输入通常可控制在：

- `1.5k-3k` tokens

输出：

- `0.8k-1.5k` tokens

所以单次 markdown narrative 渲染成本是很轻的。  
和完整 Soul Extractor 相比，几乎可以忽略。

---

## 10. 测试与验证

## 10.1 用 4 个 SEO 项目做 gold set

这是第一批最有价值的回归集。

### Test A: `claude-seo`

预期：

- ALIGNED 多
- STALE 少
- ORIGINAL 中等
- DIVERGENT 低到中

### Test B: `30x-seo`

预期：

- 与 `claude-seo` 高度相似
- health findings 分布应与 `claude-seo` 接近

### Test C: `geo-seo-claude`

预期：

- ORIGINAL 高
- DIVERGENT 高
- MISSING 可能存在，但应能解释为路线差异而不是简单缺失

### Test D: `marketingskills`

预期：

- domain routing 可能不稳定，因为跨域强
- ORIGINAL 高
- secondary domain candidate 明显

## 10.2 具体测试用例

### Case 1: 高共识缺失

构造：

- 从项目 atoms 中移除一个高支持 cluster 对应 atom

预期：

- 触发 MISSING

### Case 2: 表述不同但不应 ORIGINAL

构造两个 paraphrase atom：

- `AI crawlers do not execute JS`
- `CSR pages are invisible to LLM bots`

预期：

- 不应标 ORIGINAL

### Case 3: 作用域不同不应 ALIGNED

构造：

- FAQPage 对 Google rich results 受限
- FAQPage 对 AI crawler extraction 有价值

预期：

- 不应 ALIGNED
- 可能 PARTIAL / CONTESTED / CONTEXT

### Case 4: 明确废弃

构造：

- 包含 FID 作为当前指标

预期：

- STALE

## 10.3 衡量指标

### 对 MISSING / ORIGINAL

建议用：

- precision
- recall
- false_original_rate
- false_missing_rate

特别要盯：

- ORIGINAL 的 precision

因为这是最容易被错误高估的一类。

### 对整个报告

额外指标：

- finding Jaccard similarity between similar projects
- high-signal precision
- stale precision

对于 `claude-seo` 和 `30x-seo`：

- 期望 `HIGH-SIGNAL findings Jaccard >= 0.8`

对于 `geo-seo-claude` 与前两者：

- 期望 originality density 明显更高

---

## 11. 完整伪代码

```python
def run_health_check(project_atoms, domain_map, deprecation_db, config):
    cache_key = build_cache_key(
        project_atoms_hash=hash_atoms(project_atoms),
        domain_map_version=domain_map.version if domain_map else "none",
        matcher_version=config.matcher_version,
        deprecation_db_version=deprecation_db.version,
        config_hash=hash_config(config)
    )

    cached = load_health_check_cache(cache_key)
    if cached:
        return cached

    report = init_report(project_atoms, domain_map, deprecation_db, config)

    # 1. STALE engine can run independently of domain map
    stale_findings = []
    for atom in project_atoms:
        evt = match_deprecation_event(atom, deprecation_db)
        if evt:
            stale_findings.append(make_stale_finding(atom, evt, report))

    report.findings.extend(stale_findings)

    # 2. If no map, stop here with stale-only report
    if domain_map is None:
        finalize_summary(report)
        persist_cache(cache_key, report)
        return report

    # 3. Build retrieval indices
    lexical_index = domain_map.lexical_index
    semantic_index = domain_map.semantic_index
    cluster_store = domain_map.cluster_store

    aligned = []
    originals = []
    partials = []
    matched_project_atoms = set()
    covered_clusters = set()

    # 4. Project atom -> map alignment
    for atom in project_atoms:
        candidates = retrieve_candidates(
            atom=atom,
            lexical_index=lexical_index,
            semantic_index=semantic_index,
            top_k=config.top_k
        )

        best = None
        best_score = 0.0
        best_mode = "NO_MATCH"

        for cluster in candidates:
            score, detail = structured_match(atom, cluster, config)
            mode = classify_match_mode(score, detail.scope_score, detail.opposition)

            if score > best_score:
                best = (cluster, detail)
                best_score = score
                best_mode = mode

        if best_mode in ("EXACT_ALIGNED", "SEMANTIC_ALIGNED"):
            cluster, detail = best
            aligned.append(make_aligned_finding(atom, cluster, detail, report))
            matched_project_atoms.add(atom.atom_id)
            covered_clusters.add(cluster.cluster_id)
        elif best_mode == "PARTIAL_MATCH":
            partials.append((atom, best))
        else:
            originals.append(atom)

    # 5. Detect DIVERGENT and CONTESTED from partials
    divergent = []
    contested = []
    for atom, best in partials:
        cluster, detail = best

        if cluster_is_contested(cluster_store, cluster.cluster_id):
            contested.append(make_contested_finding(atom, cluster, detail, report))
        elif detail.opposition and detail.scope_score >= config.divergent_scope_threshold:
            divergent.append(make_divergent_finding(atom, cluster, detail, report))

    report.findings.extend(aligned)
    report.findings.extend(divergent)
    report.findings.extend(contested)

    # 6. ORIGINAL detection with second-pass defense
    original_findings = []
    for atom in originals:
        if passes_original_second_pass(atom, domain_map, config):
            original_findings.append(make_original_finding(atom, report))
    report.findings.extend(original_findings)

    # 7. MISSING detection from map -> project direction
    missing_findings = []
    for cluster in domain_map.clusters:
        if not qualifies_as_missing_candidate(cluster, domain_map, config):
            continue

        if cluster.cluster_id in covered_clusters:
            continue

        alt = find_divergent_or_contested_substitute(cluster, divergent, contested)
        if alt:
            continue

        missing_findings.append(make_missing_finding(cluster, report))
    report.findings.extend(missing_findings)

    # 8. DRIFTED detection
    drifted_findings = []
    for atom in project_atoms:
        drift_signal = detect_drift(atom, domain_map.history, config)
        if drift_signal:
            drifted_findings.append(make_drifted_finding(atom, drift_signal, report))
    report.findings.extend(drifted_findings)

    # 9. Deduplicate and severity score
    report.findings = dedupe_findings(report.findings)
    for finding in report.findings:
        finding.severity = score_severity(finding, domain_map, config)

    # 10. Sort findings
    report.findings = sort_findings(report.findings)

    # 11. Summary metrics
    report.summary = summarize_findings(report.findings, project_atoms, domain_map)

    # 12. Persist cache
    persist_cache(cache_key, report)

    return report
```

---

## 12. 工程风险与优化机会

## 12.1 最大风险：scope ontology 不稳定

如果：

- engine
- persona
- environment
- time

这些 scope slot 没稳定下来，matcher 质量会非常波动。

所以在做 fancy embedding 之前，先把 scope ontology 固定住。

## 12.2 第二大风险：ORIGINAL 会被过度报告

系统最容易“看起来聪明”的方式，就是说：

- 这很独创

但这也是最危险的假阳性。

所以 ORIGINAL 的阈值必须保守，而且要 second-pass。

## 12.3 优化机会：把 health check 结果回连到图谱浏览

虽然体检本身不应反写图谱，但每条 finding 都应该能 drill down：

- cluster
- source projects
- evidence refs

这会极大提升用户信任。

## 12.4 优化机会：用 report diff 做定期体检

一旦缓存和版本都做好，就能天然支持：

- 同一项目对比两个 map version 的体检差异

这会很适合后续“知识趋势体检”。

---

## 13. 最后一句话

如果要把整份报告压成一句话，我的建议是：

> **Knowledge Health Check 的工程核心不是“写一份好报告”，而是“把项目原子稳定地放进领域参照系里”。**

所以第一版最值得投资的不是 UI，不是总分，也不是漂亮 narrative，而是：

## `candidate retrieval + structured matcher + stale engine + cache/version discipline`

这四件事做稳了，Health Check 就会成为一个可靠的图谱消费层；做不稳，它就会变成又一个看起来很懂但不可回放的 AI 分析结果。

---

## 14. 参考资料

- Health check brief: `/Users/tang/Documents/vibecoding/Doramagic/research/cross-project-intelligence/health-check-research-brief.md`
- Claude report: `/Users/tang/Documents/vibecoding/Doramagic/research/cross-project-intelligence/health-check-claude-report.md`
- Cross-project engineering report: `/Users/tang/Documents/vibecoding/Doramagic/research/cross-project-intelligence/codex-report.md`
- Domain map engineering report: `/Users/tang/Documents/vibecoding/Doramagic/research/cross-project-intelligence/domain-map-codex-report.md`
- StitchCraft engineering report: `/Users/tang/Documents/vibecoding/Doramagic/research/cross-project-intelligence/stitchcraft-codex-report.md`

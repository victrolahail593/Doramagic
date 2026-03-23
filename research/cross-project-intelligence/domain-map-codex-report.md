# Domain Knowledge Map 工程研究报告：领域共识图谱的数据结构、更新机制与落地方案

## 1. 先给结论

我的核心判断是：

> **Doramagic 不应该把领域图谱做成一个“巨大的知识库”，而应该把它做成一个“可增量编译的领域知识索引层”。**

这句话很重要，因为它决定了整个工程路线。

如果把领域图谱理解成：

- 一个静态大文档
- 一个一次性生成的领域白皮书
- 或一个全量重算的离线产物

它很快会死在：

- 更新成本
- 过时知识
- provenance 丢失
- 冷启动负担

正确的理解应该是：

## **Domain Knowledge Map = 从多个 `project_fingerprint.json` 增量融合出来的、带时间与独立性标记的领域级知识层。**

它的作用不是取代单项目 Soul Extractor，而是给 Soul Extractor 提供：

1. **领域共识基座**
2. **项目打架参照系**
3. **过时知识检测的时间轴**
4. **新项目提取时的 WHY / UNSAID 先验锚点**

所以工程上最合理的路线不是上来就做 Neo4j 大图谱，而是：

## **`project_fingerprint.json` -> `domain_atoms.parquet` + `domain_map.sqlite` + `compiled_domain_bricks.md`**

也就是：

- 原始项目层继续用文件产物
- 领域索引用轻量数据库
- 最终注入 Soul Extractor 的消费层是编译后的 bricks / map 文档

这和 Doramagic 一贯的哲学一致：

> 代码说事实，AI 说故事。图谱负责事实与关系，提取管线再利用图谱去讲更好的故事。

---

## 2. 领域图谱到底是什么

brief 里把它定义成“对一个技术领域预先提取 10-20 个代表性开源项目的灵魂，经过公约数提取、冲突标注、独立性评分后形成的结构化知识地图”，这个方向是对的。

但工程上还需要进一步精确定义。

我建议把 Domain Knowledge Map 拆成四层。

## 2.1 Project Layer

单项目层，已有：

- `repo_facts.json`
- cards
- `CLAUDE.md`
- 计划中的 `project_fingerprint.json`

这一层是最小事实单元。

## 2.2 Atom Layer

跨项目对齐后的原子知识层。

每个 atom 表示一个：

- 概念
- 决策规则
- 架构模式
- 失败模式
- 约束
- workflow pattern

这是领域图谱最核心的数据层。

## 2.3 Consensus Layer

由多个项目支持、经过独立性折扣和作用域兼容性检查后的：

- 共识知识
- 争议知识
- 独创知识
- 过时知识

这一层是产品最有价值的层。

## 2.4 Consumption Layer

专门给下游使用的编译产物：

- `DOMAIN_MAP.md`
- `DOMAIN_BRICKS.json`
- `DOMAIN_CONSENSUS.md`
- `DOMAIN_DIFF_INDEX.json`

这一层不是 source of truth，只是消费接口。

---

## 3. 数据结构设计

我不建议在 `project_fingerprint.json` 基础上直接“长大成领域图谱”。  
更合理的是：

- 单项目继续保留 `project_fingerprint.json`
- 领域层引入新的 `domain_map` 结构

原因：

- project fingerprint 是单体、局部、版本化的
- domain map 是聚合、增量、跨项目的

两者职责不同。

## 3.1 项目级输入结构

延续已有方案：

```json
{
  "project_id": "claude-seo",
  "version": "v1.4.0",
  "metadata": {},
  "code_fingerprint": {},
  "knowledge_atoms": [],
  "soul_graph": {}
}
```

## 3.2 领域级核心结构

建议新建 `domain_map.json` 的逻辑模型，但实际存储不一定是单个 JSON。

建议 schema：

```json
{
  "domain_id": "seo-geo",
  "version": "2026-03-15",
  "project_members": [
    {
      "project_id": "claude-seo",
      "version": "v1.4.0",
      "added_at": "2026-03-15T10:00:00Z",
      "weight": 0.82,
      "independence_group": "family_02"
    }
  ],
  "atoms": [
    {
      "atom_id": "atom_001",
      "type": "decision_rule",
      "canonical_claim": "FAQPage rich results restricted since 2023-08",
      "scope": {
        "engine": ["google-rich-results"],
        "time": ["2023-08+"],
        "persona": ["seo"]
      },
      "supporting_projects": ["claude-seo", "30x-seo", "geo-seo-claude", "marketingskills"],
      "support_count": 4,
      "support_independence": 0.34,
      "confidence": 0.91,
      "status": "consensus",
      "first_seen_at": "2023-08-08",
      "last_verified_at": "2026-03-15",
      "freshness_state": "fresh",
      "upstream_sources": ["google-search-docs-faq-update-2023-08"],
      "evidence_refs": ["project:claude-seo:dr_004", "project:30x-seo:dr_007"]
    }
  ],
  "conflicts": [],
  "patterns": [],
  "bricks": []
}
```

## 3.3 领域图谱里的关键对象

至少需要 6 类对象：

### A. `DomainAtom`

最小可比较知识单元。

字段：

- canonical claim
- type
- scope
- provenance
- support_count
- support_independence
- confidence
- freshness state

### B. `DomainConflict`

描述冲突，而不是强行消解。

字段：

- left atom
- right atom
- conflict kind
- scope overlap
- resolution status

### C. `DomainPattern`

多个 atom 组合出来的 higher-order pattern。

例子：

- “并行子代理 + reference 按需加载 + hook 拦截”

### D. `ProjectMembership`

项目加入图谱后的元数据。

用于：

- 独立性折扣
- lineage 分析
- 更新触发

### E. `Brick`

专门供 Soul Extractor 注入的“领域积木”。

它不是 atom，而是面向消费的编译对象。

字段：

- title
- supported claims
- confidence
- when to use
- when not to use
- provenance summary

### F. `FreshnessEvent`

记录：

- 哪个 atom 被新项目支持
- 哪个 atom 被新版本推翻
- 哪个 atom 进入 stale / contradicted

---

## 4. 存储方案：不要一开始上图数据库

brief 问“图谱存在哪里”，这是一个很容易过度设计的点。

我的建议非常明确：

## **第一版用 SQLite + Parquet/JSONL，不要一开始上图数据库。**

原因：

1. 10-20 项目的单领域规模很小
2. 主要操作是：
   - 批量读取 atoms
   - 做聚类 / 对齐 / 增量更新
   - 输出编译结果
3. 图查询复杂度还远远没到 Neo4j 必要级别

## 4.1 推荐的物理存储

### A. SQLite

用于：

- domain metadata
- project membership
- atoms 索引
- conflict 表
- freshness events
- lineage / independence group

优点：

- 零运维
- 单文件
- 事务可靠
- 很适合增量更新

### B. Parquet

用于：

- atom embeddings
- 大批量 atom records
- 批处理分析结果

优点：

- 适合列式分析
- 压缩好
- 便于 DuckDB 查询

### C. JSONL

用于：

- append-only 更新日志
- freshness events
- batch run logs

### D. Markdown / JSON 编译产物

用于下游消费：

- `DOMAIN_CONSENSUS.md`
- `DOMAIN_BRICKS.json`

## 4.2 为什么不是向量数据库

向量检索确实有用，但第一版不值得为 10-20 项目引入一个独立系统。

更实际的做法：

- embedding 存 Parquet
- 用本地 ANN 索引或轻量 Python 索引

等规模上来再考虑独立向量服务。

## 4.3 为什么不是知识图谱数据库

图数据库适合：

- 高交互图遍历
- 多跳查询
- 实时图分析

而第一版领域图谱主要是离线编译和少量索引查询。  
所以现在上图数据库大概率是提前复杂化。

## 4.4 一个实际目录结构

```text
research/domain-maps/
  seo-geo/
    projects/
      claude-seo.project_fingerprint.json
      30x-seo.project_fingerprint.json
    store/
      domain_map.sqlite
      atoms.parquet
      embeddings.parquet
      freshness_events.jsonl
    compiled/
      DOMAIN_MAP.md
      DOMAIN_CONSENSUS.md
      DOMAIN_BRICKS.json
      DOMAIN_CONFLICTS.md
    runs/
      2026-03-15T10-20-00Z-build.json
```

---

## 5. 增量更新算法：新项目加入时怎么更新

这是整个系统能否长期运转的核心。

### 结论

> **不要全量重算。做“原子级增量融合 + 局部重编译”。**

## 5.1 全量重算的问题

如果每加一个新项目就：

- 重提取全部项目
- 重对齐全部 atoms
- 重算全部共识

那图谱很快不可维护。

## 5.2 增量融合思路

假设已有：

- `K` 个项目
- `M` 个领域 atoms

新项目 `P_new` 进来时：

1. 提取 `P_new.project_fingerprint.json`
2. 只把它的 atoms 与现有 domain atoms 做候选对齐
3. 对命中的 cluster 更新：
   - support_count
   - support_independence
   - last_verified_at
4. 对未命中的 atom：
   - 创建新 atom cluster
5. 重算受影响的：
   - conflicts
   - bricks
   - consensus markdown sections

## 5.3 关键数据结构：Atom Cluster

领域图谱的基本单位不是“单个 atom”，而是“atom cluster”。

```json
{
  "cluster_id": "cluster_017",
  "representative_atom_id": "atom_001",
  "member_atoms": [
    "claude-seo:dr_004",
    "30x-seo:dr_007"
  ],
  "support_count": 2,
  "support_independence": 0.76,
  "scope_signature": "google-rich-results|faqpage|2023-08+"
}
```

有了 cluster，增量更新就变成：

- new atom 找 cluster
- 找不到就建新 cluster

## 5.4 增量伪代码

```python
def update_domain_map(domain_store, new_fingerprint):
    new_atoms = canonicalize_atoms(new_fingerprint["knowledge_atoms"])

    impacted_clusters = set()

    for atom in new_atoms:
        candidates = retrieve_candidate_clusters(domain_store, atom)
        match = best_cluster_match(atom, candidates)

        if match and match.score >= MATCH_THRESHOLD:
            attach_atom_to_cluster(domain_store, atom, match.cluster_id)
            impacted_clusters.add(match.cluster_id)
        else:
            cluster_id = create_new_cluster(domain_store, atom)
            impacted_clusters.add(cluster_id)

    for cid in impacted_clusters:
        recompute_cluster_stats(domain_store, cid)
        recompute_conflicts_around(domain_store, cid)

    recompile_impacted_bricks(domain_store, impacted_clusters)
    recompile_domain_reports(domain_store, impacted_clusters)
```

## 5.5 什么时候需要全量重算

只在这些场景：

- canonicalization 规则变了
- scope ontology 变了
- independence grouping 逻辑变了
- embedding 模型大换代

也就是说，全量重算应该是 schema migration，不是日常更新。

---

## 6. 保鲜机制：如何自动检测过时知识

领域图谱最大的价值之一，就是它能比单项目更早发现“某条知识已经过时”。

## 6.1 三类过时信号

### A. 新项目反证

如果新加入项目反复出现与旧 atom 相反的新规则，并且证据等级更高，那旧 atom 应被降权。

### B. 原项目版本更新

如果同一项目新版本中：

- 规则消失
- 代码路径变化
- hook 被移除
- 文档明确废弃

则相关 atom 应标为 `possibly_resolved` 或 `stale`。

### C. 外部时间知识

某些领域有明确时效事件：

- Google 搜索政策变化
- API 废弃
- CVE 修复

这类变化可以用 changelog / release / docs 触发 freshness event。

## 6.2 freshness state 设计

建议：

```text
fresh
stale
contradicted
deprecated
superseded
unverified
```

## 6.3 保鲜算法

```python
def refresh_atom(atom, new_evidence):
    if confirms(atom, new_evidence):
        atom.last_verified_at = now()
        atom.freshness_state = "fresh"
        atom.confidence = min(1.0, atom.confidence + 0.05)
    elif contradicts(atom, new_evidence):
        atom.freshness_state = "contradicted"
        atom.confidence *= 0.3
    elif is_newer_replacement(atom, new_evidence):
        atom.freshness_state = "superseded"
        atom.superseded_by = new_evidence.atom_id
    else:
        age_days = days_since(atom.last_verified_at)
        if age_days > atom.ttl_days:
            atom.freshness_state = "stale"
```

## 6.4 实际工程实现

我建议不要单独做一个“图谱刷新系统”。  
直接把 freshness 检测挂到：

- 新项目入图
- 已有项目新版本重提取
- 定时 changelog / release 轮询

并把变化写成：

- `freshness_events.jsonl`

这和前面 memory 设计里 append-only + materialized snapshot 的思想一致。

---

## 7. 图谱怎么注入 Soul Extractor 管线

这是领域图谱能否真正提升提取质量的关键。

### 结论

> **图谱不应该从一开始就强灌给模型，而应该按阶段、按用途注入。**

## 7.1 Stage 0：作为项目定位与领域归属输入

在 Stage 0 完成 `repo_facts.json` 后，可以先做：

- 领域分类
- 近邻项目召回
- 候选领域图谱匹配

输出：

- `domain_id`
- top-k similar projects
- candidate bricks

这一阶段不做知识注入，只做路由和召回。

## 7.2 Stage 1：WHY 提取时作为“领域锚点”

这是最重要的注入点。

做法：

- 给模型 3-5 个高置信 domain bricks
- 这些 bricks 只包含：
  - 领域共识
  - 高独立性模式
  - 争议点提醒

用途：

- 避免 Stage 1 凭空编 WHY
- 让模型知道这个项目是在跟随共识，还是在偏离共识

但要严格限制：

- bricks 是参考，不是答案
- prompt 必须强调“项目可以偏离领域共识，禁止强行对齐”

## 7.3 Stage 2-3：规则提取时作为“候选校准器”

用途：

- 如果项目提取出一个规则，图谱可以问：
  - 这是共识？
  - 独创？
  - 还是争议？

这会显著提升：

- 规则分型
- scope 标注
- novelty 识别

## 7.4 Stage 3.5：作为交叉验证器

这一层最适合图谱发挥“硬门控”作用。

例如：

- 项目宣称一条规则是行业标准，但图谱里它只被 1 个独立项目支持
- 或者项目输出的规则已经被领域图谱标成 `deprecated`

那就应触发 warning / revise。

## 7.5 Stage 4：作为叙事增强材料

Stage 4 只应消费图谱编译产物，而不是原始图数据。

推荐输入：

- top consensus bricks
- top novelty notes
- top conflicts against domain

这样 Stage 4 会自然生成：

- “这个项目跟行业共识一致在哪里”
- “它独创在哪里”
- “它偏离共识的地方意味着什么”

这正是用户真正想看到的领域视角。

---

## 8. 冷启动自动化管线

brief 问冷启动怎么做，我建议一条完全可脚本化的 batch pipeline。

## 8.1 总流程

```text
discover_projects.py
  -> clone_projects.py
  -> batch_extract.py
  -> build_fingerprints.py
  -> compare_projects.py
  -> build_domain_map.py
  -> compile_domain_outputs.py
```

## 8.2 每一步做什么

### 1. `discover_projects.py`

输入：

- 领域关键词
- seeds
- curated list

输出：

- `candidate_projects.json`

### 2. `clone_projects.py`

批量拉取或更新 repos。

输出：

- 本地工作目录

### 3. `batch_extract.py`

复用现有 Soul Extractor，对每个 repo 跑：

- Stage 0-4

输出：

- cards
- `CLAUDE.md`

### 4. `build_fingerprints.py`

把每个项目编译成：

- `project_fingerprint.json`

### 5. `compare_projects.py`

复用前一份 cross-project intelligence 方案：

- 相似度
- lineage
- atom clusters

### 6. `build_domain_map.py`

领域层增量融合：

- 生成 SQLite / Parquet store
- 计算 conflicts / consensus / bricks

### 7. `compile_domain_outputs.py`

输出：

- `DOMAIN_MAP.md`
- `DOMAIN_BRICKS.json`
- `DOMAIN_CONSENSUS.md`

## 8.3 最小脚本骨架

```python
def cold_start_domain(domain_id, project_urls):
    repos = clone_all(project_urls)

    extracted = []
    for repo in repos:
        extracted.append(run_soul_extractor(repo))

    fps = [build_project_fingerprint(x) for x in extracted]
    comparisons = compare_projects(fps)
    domain_store = build_domain_store(domain_id, fps, comparisons)
    compile_domain_outputs(domain_store)
```

---

## 9. 成本估算：10-20 个项目的 token / 时间 / 存储

这部分必须明确说明：下面是基于现有单项目数据的**工程推断**，不是已跑过的真实批量统计。

## 9.1 已知基线

本地文档里，`python-dotenv` 单项目完整提取：

- 执行时间约 `40 分钟`
- 成本约 `$2-5`
- 目标项目规模：`1,105 行 Python, 23 files`

来源：[PRODUCT_MANUAL.md:936](/Users/tang/Documents/vibecoding/Doramagic/docs/PRODUCT_MANUAL.md#L936)

## 9.2 批量领域构建的估算模型

先按三档项目规模粗分：

### Small

- 1k-3k 行
- 20-80 文件
- 成本：`$2-5`
- 时间：`30-45 分钟`

### Medium

- 3k-15k 行
- 80-300 文件
- 成本：`$5-15`
- 时间：`45-120 分钟`

### Large

- 15k+ 行
- 300+ 文件
- 成本：`$15-40`
- 时间：`2-6 小时`

## 9.3 一个领域 10-20 项目的粗估

如果选择的都是类似 SEO skill 这类小到中型项目：

- `10 项目`
  - token / API 成本：约 `$40-120`
  - 墙钟时间（串行）：`8-15 小时`
  - 墙钟时间（并行 4 workers）：`2-5 小时`
  - 存储：
    - source repos：`0.5-2 GB`
    - 提取产物：`50-200 MB`
    - fingerprints + domain store：`10-100 MB`

- `20 项目`
  - token / API 成本：约 `$80-250`
  - 墙钟时间（并行 4 workers）：`4-10 小时`
  - 存储：`1-5 GB` 量级

### 重要说明

真正昂贵的不是图谱本身，而是：

- 首次完整提取
- 后续大版本刷新

图谱存储和增量更新本身非常便宜。

## 9.4 增量刷新成本

如果每周只刷新：

- 其中 20% 的项目有更新

那单次刷新成本大致是全量初建的 `10%-30%`。

原因：

- 只重提取变更项目
- 图谱只做局部增量融合

---

## 10. 可复用工具和基础设施

我建议直接复用而不是新造轮子：

## 10.1 现有 Doramagic 基础

- `extract_repo_facts.py`
- `validate_extraction.py`
- cards schema
- `validate_output.py`
- 计划中的 `project_fingerprint.json`
- `compare_projects.py`

这已经覆盖了 70% 路线。

## 10.2 适合补充的通用组件

### A. DuckDB

适合本地分析：

- Parquet atoms
- 批量统计
- 增量 SQL 分析

### B. SQLite

适合做 domain store metadata 和事务更新。

### C. MinHash / LSH

用于候选 cluster 检索。

### D. 本地 ANN 索引

用于 atom embedding 近邻召回。

### E. GitHub Actions / cron

用于：

- 周期刷新
- 新 release 触发
- 领域图谱重编译

---

## 11. 我看到的额外工程挑战与优化机会

brief 里没完全展开，但我认为很关键的有下面几项。

## 11.1 领域边界不是静态的

SEO/GEO 本身就在演化。  
所以 domain_id 不能被当作永恒标签。

更好的方式：

- 允许 domain map 有子域
- 允许 atom 跨域挂载

例如：

- `seo`
- `geo`
- `seo-geo`

否则图谱会被领域漂移拖垮。

## 11.2 图谱会固化偏见

如果前 10 个项目都偏某个栈：

- TypeScript heavy
- Claude Code centric
- self-hosted bias

图谱会天然放大这种偏见。

所以 domain store 应保存：

- stack distribution
- persona distribution
- project archetype distribution

这不是“元数据装饰”，而是质量控制的一部分。

## 11.3 Brick 编译才是真正的产品接口

领域图谱本身很复杂，但 Soul Extractor 和最终用户都不该直接消费 raw graph。

真正有产品价值的是：

- `Brick`

也就是说，图谱的真实输出不是 map，而是：

## **可注入的领域积木。**

这和你们之前的“最大公约数 = 领域级积木”完全对齐。

## 11.4 图谱会自然长出“异常检测”

当图谱成熟后，它不仅能做：

- 共识增强

还会自动长出：

- 项目偏离共识预警
- 过时知识预警
- 假公约数检测
- 新兴模式发现

也就是说，领域图谱不是静态资产，而是未来多个产品功能的底座。

## 11.5 不要一开始做实时图谱

实时更新听起来很酷，但现在完全没必要。

推荐：

- batch-first
- daily / weekly refresh
- 手动触发重编译

等数据规模和用户场景证明需要，再做流式增量。

---

## 12. 最终建议

如果让我给这条路线排优先级，我会这样做：

### P0

- 实现 `project_fingerprint.json`
- 实现 `compare_projects.py`

### P1

- 实现 `domain_map.sqlite + atoms.parquet`
- 实现 `build_domain_map.py`
- 实现 `DOMAIN_BRICKS.json`

### P2

- 把 domain bricks 注入 Stage 1 / 2 / 3.5
- 做 freshness events

### P3

- 做自动刷新
- 做多领域策展与批处理

一句话总结：

> **领域共识图谱不是一个新产品页面，而是 Doramagic 的预训练层。**

它的价值不在于“用户能看到一张图”，而在于：

## **用户来的时候，Doramagic 已经对这个领域有组织过的记忆。**

这会让你们的单项目提取、项目打架、StitchCraft 和未来的领域洞察，全部变成同一条数据飞轮上的不同消费面。

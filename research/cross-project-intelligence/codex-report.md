# Doramagic 跨项目智能研究报告：工程实现与算法视角

## 1. 先给结论

这个 brief 里最重要的发现，不是“可以做项目打架”和“可以做最大公约数”，而是：

> **Doramagic 已经不再只是单项目灵魂提取器，而是在逼近一种“项目间知识关系引擎”。**

一旦进入跨项目对比，你处理的对象就不再是 `repo -> soul document`，而是：

`repo set -> shared knowledge / unique knowledge / lineage / contamination / consensus`

这在工程上意味着三个变化：

1. 你需要一个**可比较的知识表示**，而不是只面向人类阅读的 `CLAUDE.md`
2. 你需要一个**分层对比管线**，而不是简单的两两 diff
3. 你需要一个**概率性判断框架**，而不是“谁抄谁”的绝对裁决器

我的核心建议是：

## **不要直接比较最终叙事文本。要把每个项目编译成三层知识指纹，再做多阶段比对。**

这三层是：

1. **Code Fingerprint**：代码与结构层
2. **Knowledge Atom Fingerprint**：概念、规则、工作流、架构、社区陷阱等原子知识层
3. **Soul Graph Fingerprint**：WHY / 模块关系 / 设计哲学 / 权衡逻辑层

然后用一条四阶段管线：

`cheap candidate generation -> typed alignment -> lineage scoring -> consensus / diff compilation`

这样可以同时支持：

- fork / 套壳检测
- 项目族谱分析
- 最大公约数提取
- 独创知识识别
- 领域知识演化追踪

---

## 2. 什么是“知识指纹”

如果两个项目的灵魂要可比较，首先不能只存成一篇长文。

`CLAUDE.md` 适合人读，不适合算法比。  
真正需要的是一个**机器可比较的中间表示**。

我建议用下面这个对象：

```json
{
  "project_id": "claude-seo",
  "version": "v1.4.0",
  "metadata": {
    "repo_url": "...",
    "created_at": "...",
    "updated_at": "...",
    "language_mix": ["python", "shell", "markdown"],
    "stars": 2300
  },
  "code_fingerprint": {
    "file_path_sketch": "...",
    "ast_shingles": ["..."],
    "api_surface": ["..."],
    "dependency_set": ["playwright", "..."],
    "tool_commands": ["/seo audit", "/seo schema"]
  },
  "knowledge_atoms": [
    {
      "id": "dr_001",
      "type": "decision_rule",
      "statement": "AI crawlers do not execute JS reliably, so CSR-only pages are low citability",
      "normalized_statement": "...",
      "scope": {
        "domain": "seo",
        "environment": ["ai-crawlers", "csr"],
        "version": ["2025+", "current"]
      },
      "evidence_level": "E2",
      "evidence_refs": ["issue#12", "file:line"],
      "source_kind": "code+community",
      "embedding": "...",
      "token_minhash": "...",
      "entity_tags": ["AI crawler", "JS rendering", "CSR"],
      "relation_tags": ["cause", "constraint", "recommendation"]
    }
  ],
  "soul_graph": {
    "nodes": [
      {"id": "p1", "type": "principle", "label": "rules_change_faster_than_models"},
      {"id": "m1", "type": "module", "label": "reference_files"},
      {"id": "w1", "type": "workflow", "label": "parallel_subagents"}
    ],
    "edges": [
      {"src": "p1", "dst": "m1", "type": "implemented_by"},
      {"src": "p1", "dst": "w1", "type": "motivates"},
      {"src": "w1", "dst": "m1", "type": "depends_on"}
    ]
  }
}
```

这不是要替换 `CLAUDE.md`，而是要在现有产物旁边新增一个：

`project_fingerprint.json`

### 为什么必须三层

因为三类任务看的不是同一件事：

- **fork / 套壳检测** 优先看 `code_fingerprint`
- **最大公约数提取** 优先看 `knowledge_atoms`
- **设计哲学对比** 优先看 `soul_graph`

如果把三者混成一个 embedding，结果会很差：

- 代码上不同但知识上相同的项目会被误判为不相关
- 代码上相同但 WHY 不同的项目会被误判为完全相同

---

## 3. 知识指纹的具体设计

## 3.1 Code Fingerprint

这一层回答：

- 这两个项目是不是代码直接复用或轻度改写？
- 相同结构到底来自同源代码，还是来自同一上游模式？

建议包含 5 类信号：

1. **路径骨架**
   - 文件路径集合
   - 目录层级模式
   - 关键文件名

2. **AST shingles**
   - 以函数、类、调用链、控制流片段做 shingling
   - 语言无关层可退化成 token shingles

3. **API surface**
   - CLI 命令
   - 配置字段
   - exports / entry points

4. **Dependency set**
   - 直接依赖
   - 工具链依赖
   - 外部服务依赖

5. **Hook / automation signatures**
   - pre-commit hooks
   - validate scripts
   - CI patterns

### 工程建议

- 轻量版：先用 Stage 0 的 `repo_facts.json` + 文件路径 + 命令/skill 名称
- 增强版：引入 Tree-sitter，把关键文件编成 AST 后做 subtree hashing  
  官方：<https://tree-sitter.github.io/tree-sitter/>

如果目标是最小可行产品，第一版不必做完整 AST diff。  
路径骨架 + token shingles + 关键文件 fuzzy hash，已经足够抓住大量“套壳换皮”。

---

## 3.2 Knowledge Atom Fingerprint

这是最关键的一层。

Doramagic 现有卡片体系已经很接近“原子知识”：

- CC：概念
- WC：工作流
- DR：决策规则
- AC：架构
- CT：合约

问题在于，这些卡片目前主要服务于人类消费和单项目编译，还没有被彻底 canonicalize。

我建议对每张卡额外导出一个 canonical atom：

```json
{
  "atom_type": "rule",
  "claim": "FAQPage schema rich results are restricted since Aug 2023",
  "subject": "FAQPage schema",
  "predicate": "availability_restricted",
  "object": "non-government-and-healthcare-sites",
  "modifiers": {
    "time": "2023-08+",
    "engine": "Google rich results"
  },
  "normative_force": "warning",
  "source_support": ["E2", "E3"],
  "negative_form": "Do not treat FAQ rich result eligibility as general-purpose"
}
```

### 为什么要 canonicalize

因为“134-167 词最优段落长度”和“最优 passage 长度是 134 到 167 个词”在文本上不同，但在知识上应视为同一 atom。

所以 atom 应有：

- 原始文本
- 规范化 claim
- slot 化结构
- embedding
- lexical sketch

这样后面才能同时做：

- 精确 match
- 语义 match
- slot-aware match

---

## 3.3 Soul Graph Fingerprint

这一层表达的是：

- 核心设计哲学
- 模块如何承载哲学
- 哪个原则驱动了哪个机制

如果只比较原子规则，会丢掉 WHY。

比如两个项目都说：

- 规则更新要独立于执行逻辑

但一个项目通过：

- reference files + progressive disclosure

另一个项目通过：

- external policy engine + runtime fetch

两者在 atom 层相似，在 soul graph 层才会显出差异。

### Graph 的最小 schema

节点：

- `principle`
- `module`
- `workflow`
- `constraint`
- `pitfall`
- `artifact`

边：

- `motivates`
- `implemented_by`
- `guards`
- `depends_on`
- `conflicts_with`
- `specializes`

### 工程现实

第一版不必做完整 KG。  
只要能从 Stage 1/2/3 产物里抽出 20-50 个节点和几十条 typed edges，就足够支撑“灵魂 diff”。

---

## 4. 公约数提取算法：不要做单一 intersection，要做“分层共识”

用户说“最大公约数”，工程上不能简单理解成 set intersection。

因为知识有三种“相同”：

1. **文本相同**
2. **语义相同**
3. **功能等价但表述不同**

所以我建议公约数提取用三层匹配。

## 4.1 第 1 层：Lexical overlap

对 atom 的 `normalized_statement` 做：

- tokenization
- canonicalization
- MinHash / SimHash / shingles

用于快速抓：

- 几乎一样的规则
- 套壳 copy 后的小改写

MinHash + LSH 的工程价值很高，因为它天然适合“集合相似候选生成”。  
参考 datasketch 官方文档：<https://ekzhu.com/datasketch/lsh.html>

## 4.2 第 2 层：Semantic overlap

对 atom claim 做 embedding，相似度匹配。

用途：

- “HowTo schema is deprecated” vs “HowTo rich results are no longer supported”
- “AI crawlers don't execute JS” vs “CSR pages are invisible to LLM bots”

工程建议：

- 直接使用 sentence embedding 模型
- 用 FAISS / HNSW 做 ANN 检索  
  FAISS 论文：<https://arxiv.org/abs/1702.08734>

## 4.3 第 3 层：Structured overlap

对 canonical slots 做 typed matching：

- subject 是否相同
- predicate 是否在同一 ontology
- object 是否相同或同义
- modifiers 是否兼容

这个层最重要，因为它能过滤掉“语义似乎接近，但作用域不同”的假共识。

例如：

- FAQ schema 对 Google rich results 被限制
- FAQ schema 对 AI crawler extraction 仍有价值

如果没有 modifier 层，会被错误合并。

## 4.4 最终共识定义

我建议不是“交集”，而是：

`Consensus(atom) = support_count × support_independence × semantic_agreement × scope_compatibility`

其中最关键的是：

- `support_count`：多少项目支持
- `support_independence`：这些项目是否真的独立
- `semantic_agreement`：它们是不是在说同一件事
- `scope_compatibility`：适用域是否一致

### 为什么要有 `support_independence`

因为四个项目提到同一句话，不一定比一个项目更可信。  
如果其中三个是 fork，那本质只是“一份知识重复出现三次”。

这意味着：

> **公约数能力的前提，不是多项目，而是多独立项目。**

---

## 5. Fork / 套壳检测：代码层和知识层各能做什么

这个问题必须拆开，不然会混淆。

## 5.1 代码层能做什么

代码层擅长回答：

- 是否存在直接拷贝
- 是否做了轻度 rename / move / formatting 改写
- 文件骨架是否高度一致
- hooks / scripts / changelog / bugfix 是否同步复现

可用方法：

1. 文件 hash / fuzzy hash
2. 路径集合 Jaccard
3. token shingle + MinHash
4. AST subtree hashing
5. plagiarism / clone detectors

可复用工具：

- JPlag：程序相似度检测，适合结构化 token 级比较  
  <https://github.com/jplag/JPlag>
- Tree-sitter：统一 AST 前端  
  <https://tree-sitter.github.io/tree-sitter/>

### 代码层的边界

代码层不能可靠回答：

- 谁先有这个想法
- 两项目是否独立趋同
- 一个项目只是用了相同上游 pattern，还是抄了灵魂

它只能说：

> “这两份实现很像”

---

## 5.2 知识层能做什么

知识层擅长回答：

- 这两个项目的核心原则是否一致
- 关键决策规则是否共享
- 是否引用相同领域共识
- 是否存在独创机制

它甚至可以检测：

- 代码不太像，但灵魂高度重合
- 代码不同、UI 不同、命名不同，但 workflow / hooks / rule set 一致

### 知识层的边界

知识层不能单独判定：

- 是否真的 fork
- 相似性来自抄袭还是行业共识
- 哪个项目是源头

所以正确结论不是二选一，而是：

## **代码层用于 lineage 候选生成，知识层用于解释相似性的性质。**

---

## 6. 如何区分 fork、套壳、趋同演化、共同上游依赖

这部分最容易被产品化过度。

我建议 Doramagic 不要输出武断标签，而输出一个分布：

```json
{
  "fork_likelihood": 0.82,
  "wrapper_likelihood": 0.67,
  "convergent_evolution_likelihood": 0.18,
  "shared_upstream_pattern_likelihood": 0.54
}
```

### 6.1 Fork / 套壳

强信号：

- 文件路径骨架高重合
- 关键脚本名称和逻辑高重合
- bugfix 顺序相同
- changelog 事件相同
- 知识 atoms 也高重合

### 6.2 独立趋同

强信号：

- 规则层接近
- 代码层差异较大
- 模块命名、脚本组织、hook 实现不同
- 都在适应相同领域事实

### 6.3 共同上游依赖

强信号：

- 相似部分主要落在依赖接口或宿主框架约束
- 独创 atoms 少，但 dependency dominance 高
- 设计限制主要来自上游系统

### 6.4 最关键的额外特征：时间

我认为 brief 里还缺了一个关键维度：

## **时间线不是辅助特征，而是核心特征。**

没有时间，就没有 lineage。

至少要比较：

- 首次出现某 atom 的 commit 时间
- 首次出现某模块骨架的时间
- 某 bugfix 在不同项目出现的时间差
- release/changelog 的时序传播

如果能做到 atom-level first-seen timestamp，Doramagic 就不只是“相似性引擎”，而会变成“知识传播分析器”。

---

## 7. O(N²) 的优化：不要做全量两两对比

这个问题在产品早期就会变成瓶颈。

正确做法是分层比较。

## 7.1 候选生成层：Cheap filtering

先用便宜特征把 N 个项目压进若干桶：

- 领域标签
- 任务标签
- 语言 / runtime
- dependency family
- command vocabulary
- topic embeddings

只有同桶项目才进入下一层。

## 7.2 LSH / ANN 层：近邻召回

对不同层用不同索引：

- `code_fingerprint`：MinHash LSH
- `knowledge_atoms`：FAISS / HNSW embedding ANN
- `path skeleton`：SimHash / Jaccard prefilter

这样复杂度从“所有项目两两比”变成：

- 每项目只与若干近邻比

## 7.3 聚类层：Project families

先做 cluster，再做 cluster 内精比对。

例如：

1. topic embedding 把 SEO / CRM / RAG / memory 分开
2. within SEO，再按 skill-style / repo-style / framework family 分桶
3. 只在桶内做 lineage 和 atom alignment

## 7.4 分层对比顺序

我建议顺序是：

```text
Metadata bucket
  -> lexical candidate generation
  -> semantic candidate generation
  -> typed atom alignment
  -> graph alignment
  -> lineage inference
```

不要一上来做 graph matching。  
图匹配最贵，也最应该只在少量候选上跑。

---

## 8. 现有研究和工具可以复用什么

## 8.1 Document / set fingerprint

可复用：

- MinHash / LSH：适合集合相似和候选生成  
  <https://ekzhu.com/datasketch/lsh.html>

适用到 Doramagic：

- rule token sets
- path skeleton
- command vocabulary
- module labels

## 8.2 Code clone / plagiarism

可复用：

- JPlag：多语言程序相似检测  
  <https://github.com/jplag/JPlag>
- Tree-sitter：统一 AST 解析  
  <https://tree-sitter.github.io/tree-sitter/>

适用到 Doramagic：

- 脚本 / hooks / agent files 的语法树归一化
- 关键函数/规则实现的 subtree hashing

## 8.3 Dense retrieval / ANN

可复用：

- FAISS：高维向量近邻检索  
  <https://arxiv.org/abs/1702.08734>

适用到 Doramagic：

- knowledge atoms embedding index
- topic / principle nearest neighbors

## 8.4 Knowledge graph alignment

可复用思路：

- 实体对齐
- 关系对齐
- 属性一致性

OpenEA 这类框架代表了 KG alignment 的标准范式：先做 candidate generation，再做迭代对齐，不是直接暴力图同构。  
<https://github.com/nju-websoft/OpenEA>

适用到 Doramagic：

- principle node alignment
- module role alignment
- workflow graph alignment

### 重要提醒

不要直接把学术 KG alignment 框架搬进来。  
它们通常假设：

- 图已经足够规范
- 实体命名比较稳定
- ontology 已清楚

而 Doramagic 的图是从 LLM 提取来的，噪声更大、别名更多、边界更松。  
你应该借鉴“流程”，不是借鉴“重模型”。

---

## 9. 最小可行工程方案

这个部分最关键：怎么在现有 Soul Extractor 上最小改动实现跨项目对比。

我的建议是分三步走。

## 9.1 第一步：新增 `project_fingerprint.json`

在现有输出旁边新增一个机器文件：

```text
output/
  CLAUDE.md
  judge-report.md
  cards/
  project_fingerprint.json
```

来源：

- Stage 0：`repo_facts.json`
- Stage 2-3：cards
- Stage 4：只抽取 principle / narrative anchors，不直接整段用文本

### 需要新增的最小字段

- normalized atoms
- token minhash
- atom embeddings
- typed edges
- path skeleton
- dependency set
- command set

这一步不需要改动核心提取逻辑，只是多一个编译产物。

## 9.2 第二步：做一个独立脚本 `compare_projects.py`

输入：

- 多个 `project_fingerprint.json`

输出：

- `pairwise_similarity.json`
- `lineage_candidates.json`
- `consensus_atoms.json`
- `unique_atoms.json`

### 比较流程

1. metadata / tags bucket
2. lexical candidates via MinHash
3. semantic atom matching via embeddings
4. graph overlap scoring
5. aggregate into:
   - code similarity
   - knowledge similarity
   - principle similarity
   - likely lineage

## 9.3 第三步：生成一个新型报告

例如：

- `CROSS_PROJECT_REPORT.md`
- `CONSENSUS.md`
- `SOUL_DIFF.md`

第一版先别做 UI，先把 markdown 报告跑通。

---

## 10. 我建议的评分体系

为了让系统产出对用户可解释，建议不是给一个总分，而是给四个分。

## 10.1 Similarity Score

两个项目有多像，不区分原因。

## 10.2 Lineage Score

这两者像，是否可能存在直接传播关系。

## 10.3 Consensus Score

某知识 atom 被多少独立项目支持。

## 10.4 Uniqueness Score

某项目贡献了多少当前 cluster 中少见、但高价值的 atoms。

这样用户就能看到：

- 谁像谁
- 像是为什么
- 哪些是共识
- 哪些是独创

---

## 11. brief 里没明确提到，但我认为非常重要的挑战

## 11.1 不是“相同知识”最难，而是“近似同义但作用域不同”

真正难的不是检测完全相同的规则。  
最难的是：

- 文本看起来一样
- 但一个针对 Google rich results
- 一个针对 AI crawler retrieval

如果 scope schema 不好，公约数一定会出假阳性。

所以：

> **scope normalization 比 embedding 更重要。**

## 11.2 最大公约数天然有“假共识”风险

brief 已经提到这一点，但我认为还可以更尖锐一点：

### 同样的知识被多个项目提到，不代表它被多次独立验证。

它可能是：

- 同一个上游博客的二次传播
- 同一个 SEO 圈子里的口耳相传
- 一个错误但流行的行业 myth

所以 consensus 不能只计数。  
必须做 provenance clustering。

即：

- 如果 4 个项目都引用同一来源，本质是 1 份证据，不是 4 份

## 11.3 评估数据集会成为真正门槛

跨项目智能最后会被“评测集”卡住。

你需要至少三类 gold set：

1. 已知 fork / wrapper pairs
2. 已知独立趋同 pairs
3. 已知领域共识 atoms

没有这个，算法只能靠 demo 感觉调。

## 11.4 Temporal versioning 必须从第一天就加

如果 atom 不带版本，你很快就会遇到：

- A 项目 2024 年是对的
- B 项目 2026 年是新的
- 系统却把两者当冲突或共识

所以 atom schema 第一版就应该带：

- `first_seen`
- `last_verified`
- `applies_to_version`

## 11.5 这是知识图谱问题，但也是供应链问题

“项目打架”不仅是知识相似性，也是在做：

- lineage
- provenance
- originality
- dependency inheritance

某种意义上，它已经开始接近“知识供应链分析”。

这意味着未来甚至可以做：

- 某项目的理念来源图
- 某领域共识的传播路径
- 某条错误规则的扩散链

这是 brief 里还没完全展开、但非常大的机会。

---

## 12. 我会怎么定义这个能力

如果让我给这套能力起一个工程化名字，我会叫：

## **Cross-Project Intelligence Engine**

它不是一个 feature，而是一个新层：

```text
Soul Extractor
  -> Knowledge Fingerprinter
  -> Similarity / Lineage Analyzer
  -> Consensus / Diff Compiler
```

这层一旦成立，Doramagic 的定位会变成：

- 单项目：提取灵魂
- 多项目：推断知识关系
- 领域层：生成共识与独创地图

也就是说，Doramagic 会从“项目阅读工具”进化成“开源领域知识基础设施”。

---

## 13. 最后一句话

你们已经看到了正确方向，但 brief 里还有一个更深的结论：

> **跨项目能力的真正价值，不是帮用户比较几个 repo，而是把“项目”抽象成可计算的知识单位。**

一旦做到这一步，“最大公约数”和“项目打架”只是第一批应用。

后面还会自然长出：

- 领域共识图谱
- 知识传播图
- 独创性评分
- 错误共识检测
- 最优缝合方案生成

所以最值得做的，不是先把 compare 页面做漂亮，而是先把：

## `project_fingerprint.json + compare_projects.py + consensus compiler`

这三个基础设施打牢。

---

## 14. 参考资料

- Research brief: `/Users/tang/Documents/vibecoding/Doramagic/research/cross-project-intelligence/research-brief.md`
- Doramagic product context: `/Users/tang/Documents/vibecoding/Doramagic/INDEX.md`
- Doramagic output/card schema: `/Users/tang/Documents/vibecoding/Doramagic/docs/PRODUCT_MANUAL.md`
- Example extracted soul: `/Users/tang/Documents/vibecoding/Doramagic/experiments/exp-seo-skills/claude-seo/CLAUDE.md`
- Tree-sitter: <https://tree-sitter.github.io/tree-sitter/>
- datasketch MinHash LSH docs: <https://ekzhu.com/datasketch/lsh.html>
- JPlag: <https://github.com/jplag/JPlag>
- FAISS: <https://arxiv.org/abs/1702.08734>
- OpenEA: <https://github.com/nju-websoft/OpenEA>

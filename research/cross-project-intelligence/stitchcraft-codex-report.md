# StitchCraft 工程研究报告：跨项目知识缝合的最小可行实现、算法框架与风险边界

## 1. 先给结论

我对这个方向的核心判断是：

> **Doramagic 第一版不应该做“代码缝合怪生成器”，而应该做“知识层缝合编译器”。**

也就是说，第一版 StitchCraft 的目标不是：

- 自动把 4 个 repo 的代码拼成一个新 repo
- 自动生成一个“完美终极 skill”

而是：

- 从多个项目的结构化知识对象中生成一份 **stitched knowledge package**
- 明确哪些能力可以兼容组合
- 明确哪些设计决策相互冲突
- 明确哪些部分是共识层，哪些是可选移植件，哪些需要用户拍板
- 在合规允许的范围内，生成一个 **可实现的组装提案**

如果更工程化地说：

## **StitchCraft 的 MVP = `project_fingerprint.json` 的受约束知识融合 + 兼容性分析 + 组装提案编译。**

这和自动代码合成是两回事。

原因很直接：

1. 代码层缝合会立刻碰到 license、依赖、目录结构、运行时假设、隐式环境等硬问题
2. 知识层缝合已经足够产生强产品价值
3. Doramagic 的产品哲学是“不教用户做事，给他工具”，而不是替用户做不可验证的大跃迁

所以 StitchCraft 应被定义成：

> **一个带约束的知识融合与组装提案系统，而不是自动拼尸器。**

---

## 2. “缝合”到底是哪一层操作

brief 里问得很对：缝合到底是知识层合并、代码层组合，还是架构层设计？

我的答案是：

### 2.1 第一层：知识层缝合

输入是多个项目的：

- 共识知识
- 独创能力
- 决策规则
- 模块与接口
- 约束与失败模式

输出是：

- stitched knowledge package
- conflict map
- assembly proposal

这层是 StitchCraft 的核心，而且是当前最可落地的层。

### 2.2 第二层：架构层缝合

在知识层之上，系统给出：

- 建议以谁为骨架
- 哪些能力适合移植
- 移植后需要补哪些接口
- 哪些冲突要用户选边

这层依然是“提案”，不是自动执行。

### 2.3 第三层：代码层缝合

这层是：

- 复制/改写文件
- 改依赖
- 改目录
- 改 hooks
- 改 config

这在工程和合规上都最重。

### 2.4 MVP 结论

第一版只做：

- 知识层缝合
- 架构层提案

不做：

- 自动代码拼装
- 自动发布最终 skill

如果要给这三层起名字：

```text
Knowledge Stitch
-> Architecture Stitch
-> Code Graft
```

MVP 到 Architecture Stitch 就够了。

---

## 3. 现有 Soul Extractor 基础上最小要增加什么

你们已经有：

- Stage 0 的 `repo_facts.json`
- Stage 1-3 的知识卡片
- Stage 4 的叙事合成
- 跨项目智能研究里建议的 `project_fingerprint.json`

所以 StitchCraft 不需要推翻重来。

它最小需要新增四个组件：

## 3.1 `stitch_profile.json`

这是从 `project_fingerprint.json` 再编译出来的一层，专门服务缝合。

它要把知识对象进一步分类成：

- `consensus_constraints`
- `unique_capabilities`
- `design_decisions`
- `architecture_patterns`
- `integration_points`
- `operational_assumptions`
- `license_claims`

一个建议 schema：

```json
{
  "project_id": "claude-seo",
  "base_license_expression": "MIT",
  "consensus_constraints": [],
  "unique_capabilities": [],
  "design_decisions": [],
  "architecture_patterns": [],
  "integration_points": [],
  "operational_assumptions": [],
  "license_claims": {
    "code_license": "MIT",
    "docs_license": "LicenseRef-Unknown",
    "third_party_components": ["Apache-2.0"]
  }
}
```

## 3.2 `stitch_candidates.json`

对一个项目集合先做候选兼容分析，输出：

- 哪些能力值得移植
- 哪些模式只是参考，不应自动合并
- 哪些冲突要用户确认

## 3.3 `conflict_graph.json`

把冲突显式图化，而不是等到生成叙事时才发现不一致。

节点：

- capability
- decision
- assumption
- dependency
- license

边：

- `conflicts_with`
- `subsumes`
- `requires`
- `exclusive_with`

## 3.4 `stitch_compiler.py`

输入多份 `stitch_profile.json`，输出：

- `STITCH_REPORT.md`
- `STITCHED_KNOWLEDGE.md`
- `ASSEMBLY_PLAN.md`
- `LICENSE_NOTICE.md`

这就是第一版的核心执行器。

---

## 4. 知识合并算法：如何从 N 份 fingerprint 生成 stitched output

这里不要直接从 N 份 `CLAUDE.md` 做 merge。  
应当只从结构化对象做。

## 4.1 输入

```text
N x project_fingerprint.json
or
N x stitch_profile.json
```

如果系统已经有 `project_fingerprint.json`，建议缝合前先跑：

`fingerprint -> stitch_profile`

## 4.2 输出

一个 stitched output 应至少分四层：

### A. Foundation Layer

被多个独立项目支持、可作为默认基座的共识层。

### B. Optional Grafts

来自单项目或少数项目的独创能力，标注适用前提。

### C. Conflict Layer

互斥设计、互斥权重、互斥架构假设。

### D. Assembly Plan

不是“已经缝好”，而是：

- 以谁为骨架
- 加什么
- 改哪里
- 风险是什么

## 4.3 具体算法

### Step 1: Canonicalize

先把所有知识对象 canonicalize：

- 规范化 rule claim
- 规范化 capability 名
- 规范化 scope
- 规范化 dependency 名
- 规范化 license expression

### Step 2: Cluster

按知识类型分别聚类：

- constraint cluster
- capability cluster
- pattern cluster
- decision cluster

### Step 3: Consensus extraction

对 cluster 求：

- support count
- support independence
- scope compatibility
- confidence

输出 `foundation layer`

### Step 4: Unique contribution extraction

对只在单项目中出现、但价值高的对象打标：

- `graftable`
- `reference_only`
- `experimental`

### Step 5: Conflict detection

对设计决策、权重、依赖、权限假设做显式冲突检测。

### Step 6: Assembly proposal synthesis

在确定性部分完成后，再由 LLM 生成解释性提案：

- 推荐骨架
- 推荐 graft
- 推荐保留的共识层
- 冲突说明

这一步是“AI 说故事”，但前面的事实骨架必须由代码产出。

---

## 5. 冲突检测与解决算法

这是 StitchCraft 的核心，不是附属功能。

## 5.1 冲突类型

至少要识别 6 类冲突。

### A. Semantic conflict

两个规则在同一作用域下给出相反结论。

例子：

- `AI visibility weight = 25%`
- `AI visibility weight = 5%`

### B. Scope conflict

表面冲突，实则作用域不同。

例子：

- 一条规则针对 Google rich results
- 一条规则针对 AI crawler citations

### C. Architecture conflict

两个模式要求不同骨架。

例子：

- shared context baseplate
- fully isolated skills

### D. Dependency conflict

依赖或运行时不兼容。

例子：

- 不同版本的同一 SDK
- 需要不同 Python / Node 版本

### E. Operational conflict

隐式环境假设不同。

例子：

- 一个 skill 假设 Playwright 可用
- 一个 skill 假设只靠 requests

### F. License conflict

许可证不允许代码层混合再分发。

---

## 5.2 冲突检测框架

冲突检测不要只靠 embedding，相似不等于可兼容。

我建议：

`ConflictScore = claim_opposition × scope_overlap × implementation_incompatibility × normative_strength`

其中：

- `claim_opposition`
  - 是否表达了相反判断
- `scope_overlap`
  - 时间、环境、persona、engine 是否重叠
- `implementation_incompatibility`
  - 是否要求不同依赖或骨架
- `normative_strength`
  - 这是不是硬约束还是软建议

### 伪代码

```python
def detect_conflicts(objects):
    conflicts = []
    for a, b in candidate_pairs(objects):
        if a.type != b.type:
            continue

        opposition = semantic_opposition(a.claim, b.claim)
        overlap = scope_overlap(a.scope, b.scope)
        impl = implementation_incompatibility(a, b)
        strength = min(a.normative_strength, b.normative_strength)

        score = opposition * overlap * max(impl, 0.5) * strength
        if score >= CONFLICT_THRESHOLD:
            conflicts.append({
                "left": a.id,
                "right": b.id,
                "score": score,
                "kind": classify_conflict(a, b)
            })
    return conflicts
```

## 5.3 冲突解决：不要自动“选最优”，要分层处理

这部分要非常克制。

我建议 4 种解决策略：

### 1. Preserve Both

如果作用域不同，就并存，附适用条件。

### 2. Promote Consensus

如果一个方案有更高独立支持和更低上下文依赖，可以进 foundation。

### 3. Ask User to Choose

如果属于路线分歧，不应系统代选。

### 4. Block Automatic Stitch

如果冲突涉及：

- license
- destructive operational assumptions
- incompatible architecture base

则自动缝合直接阻断。

### 决策规则

```python
def resolve_conflict(conflict, left, right):
    if not scopes_really_overlap(left.scope, right.scope):
        return preserve_both_with_conditions(left, right)

    if conflict.kind == "license":
        return block("license-incompatible")

    if conflict.kind == "architecture" and left.is_foundation and right.is_foundation:
        return ask_user("choose-foundation")

    if higher_consensus(left, right) and lower_context_dependency(left):
        return promote(left, demote=right)

    return ask_user("design-choice")
```

这和产品哲学一致：

> 决定路线的是用户，不是 Doramagic。

---

## 6. 缝合后的质量验证：怎么保证 stitched output 不自相矛盾

缝合的最大风险不是漏，而是：

> **产出一个内部看起来很顺、实际上相互矛盾的 stitched package。**

所以 StitchCraft 必须有自己的质量门控。

## 6.1 新增 Stage S：Stitch Validation Gate

我建议在现有 Stage 3.5 之外，新增一个 Stitch 专用门控。

检查项至少包括：

### A. Consistency

- 同一作用域下是否有冲突 rule 共存
- stitched narrative 是否和选定 foundation layer 一致

### B. Dependency closure

- graft 后依赖是否闭合
- 是否引入未满足运行前提

### C. Assumption closure

- 是否把必要的 operational assumptions 全部显式化

### D. License closure

- 是否存在不可兼容 license expression
- 是否缺 attribution / notices

### E. Traceability

- 每个 stitched knowledge object 是否可回溯到来源项目

### F. Actionability

- 是否给出了明确 assembly steps，而不是模糊综合叙事

## 6.2 建议的 stitched 验证输出

```json
{
  "status": "PASS | REVISE | BLOCKED",
  "consistency_errors": [],
  "dependency_errors": [],
  "license_errors": [],
  "warnings": [],
  "attribution_coverage": 0.97
}
```

### 伪代码

```python
def validate_stitched_package(pkg):
    errors = []
    warnings = []

    errors += check_scope_conflicts(pkg.rules)
    errors += check_dependency_closure(pkg.capabilities)
    errors += check_license_compatibility(pkg.license_plan)
    errors += check_missing_assumptions(pkg)

    attribution = attribution_coverage(pkg)
    if attribution < 0.95:
        warnings.append("low-attribution-coverage")

    if errors:
        return "BLOCKED", errors, warnings
    if warnings:
        return "REVISE", errors, warnings
    return "PASS", errors, warnings
```

---

## 7. 开源协议合规：MIT / Apache / GPL 混合缝合时怎么办

这里要非常明确：

> **知识层缝合和代码层缝合，在许可证上不是同一个问题。**

我不是律师，下面是工程实现视角，不是法律意见。

## 7.1 第一原则：先把“知识提炼”与“代码复制”分开

### 相对低风险

- 抽取事实、规则、架构模式、概念边界
- 重新实现能力
- 只保留 attribution 和 provenance

### 高风险

- 复制原文件
- 大段搬运文档/README/SKILL.md 文本
- 直接拼接 GPL 代码与 permissive 代码后再分发

所以 StitchCraft 第一版应默认：

## **只做知识层缝合，不自动复制代码。**

## 7.2 SPDX expression 是必须的

许可证处理必须机器化。

SPDX 规范和 License List 提供了标准短标识和表达式组合方式。  
官方：<https://spdx.org/licenses/>  
规范：<https://spdx.github.io/spdx-spec/v2.3/SPDX-license-expressions/>

因此每个项目至少要有：

```json
{
  "code_license_expression": "MIT",
  "docs_license_expression": "LicenseRef-Unknown",
  "third_party_license_expressions": [
    "Apache-2.0",
    "BSD-3-Clause"
  ]
}
```

## 7.3 许可证兼容性的工程规则

### MIT + Apache-2.0

一般可以一起进入更宽松的组合，但要保留 notice / attribution。

### Apache-2.0 + GPLv3

ASF 官方明确说明：Apache-2.0 可被包含进 GPLv3 作品，但反方向不成立；Apache 项目不能吸纳 GPLv3 代码并继续按 Apache 分发。  
官方：<https://www.apache.org/licenses/GPL-compatibility>

### Apache-2.0 + GPLv2-only

ASF FAQ 指出 Apache-2.0 与 GPLv2 不兼容。  
官方：<https://www.apache.org/foundation/license-faq.html>

### GPL family

如果 stitched artifact 包含 GPL 代码并构成 derivative work，分发义务会升级。  
这意味着：

- 不能把 GPL 代码层 graft 当作普通 capability 移植
- 一旦触发，整个 artifact 的分发策略都要变

## 7.4 工程上怎么做

第一版直接实现一个 `license gate`：

```python
def license_gate(projects, mode):
    exprs = [p.code_license_expression for p in projects]
    if mode == "knowledge_only":
        return PASS_WITH_ATTRIBUTION
    if contains_gpl_incompatible_mix(exprs):
        return BLOCK
    return PASS_WITH_NOTICES
```

并且明确两个模式：

### `knowledge_only`

- 允许更多组合
- 输出知识包、assembly plan、attribution

### `code_graft`

- 只有许可证兼容才允许
- 默认关闭

## 7.5 可复用工具

`license-expression` 这个库可以解析、归一化、比较 SPDX license expressions，很适合 StitchCraft 做 gate。  
<https://pypi.org/project/license-expression/>

---

## 8. 可借鉴技术：Knowledge Fusion / Ontology Merging / Model Merging

这三类技术都不能直接搬，但都各自有一条可借鉴原则。

## 8.1 Knowledge Fusion

知识融合领域最核心的问题是：

- 多源信息冲突
- 来源可信度不同
- 需要做 truth inference，而不是简单投票

`Multi-source knowledge fusion: a survey` 里的核心价值正好对应 StitchCraft 的 foundation layer：先做 source alignment，再做 conflict resolution 和 truth estimation。  
<https://link.springer.com/article/10.1007/s11280-020-00811-0>

可借鉴点：

- 不要直接多数投票
- 要建 provenance / source reliability / conflict resolution 管线

## 8.2 Ontology Merging / Matching

本体合并领域的经典问题和 StitchCraft 很像：

- 名称不同但语义相近
- 层级不一致
- schema 异构
- 局部一致但全局不一致

对 StitchCraft 最有用的不是“完整本体合并系统”，而是：

- 先 matching 再 merging
- merge 前先显式标注 relation：equivalent / subsumes / conflicts

这和你们已有的 canonical atom 路线完全兼容。

## 8.3 Model Merging

模型合并不是直接可用，但 `mergekit` 有一个非常值得借鉴的思想：

> **先配置 merge plan，再执行 merge；并且允许 slice-wise / piecewise assembly，而不是整模平均。**

官方项目：<https://github.com/arcee-ai/mergekit>

对 StitchCraft 的启发非常直接：

- 不要把整个项目整体缝合
- 要做 capability-wise / pattern-wise / rule-wise stitch
- 先声明 stitch config，再编译 stitched output

换句话说，StitchCraft 更像 knowledge mergekit，而不是 giant prompt synthesis。

---

## 9. 具体数据流

我建议的数据流如下：

```text
Input:
  N project_fingerprint.json

Step 1:
  fingerprint -> stitch_profile compiler

Step 2:
  canonicalization
  - normalize claims
  - normalize scope
  - normalize dependencies
  - normalize license expressions

Step 3:
  clustering and alignment
  - capability clusters
  - rule clusters
  - pattern clusters
  - decision clusters

Step 4:
  consensus extraction
  - shared independent constraints
  - shared architecture patterns

Step 5:
  uniqueness extraction
  - graftable capabilities
  - reference-only ideas
  - experimental pieces

Step 6:
  conflict detection
  - semantic
  - scope
  - architecture
  - dependency
  - operational
  - license

Step 7:
  foundation selection
  - choose recommended skeleton
  - do not finalize conflicting strategic choices automatically

Step 8:
  stitch validation gate

Step 9:
  compile outputs
  - STITCH_REPORT.md
  - STITCHED_KNOWLEDGE.md
  - ASSEMBLY_PLAN.md
  - LICENSE_NOTICE.md
```

---

## 10. 一版可落地的伪代码

```python
def stitch_projects(fingerprint_paths, mode="knowledge_only"):
    projects = [load_fingerprint(p) for p in fingerprint_paths]

    profiles = [compile_stitch_profile(p) for p in projects]

    license_result = license_gate(profiles, mode=mode)
    if license_result.status == "BLOCK":
        return blocked_report("license incompatibility", license_result.details)

    canon = [canonicalize_profile(p) for p in profiles]

    clusters = build_clusters(canon)

    foundation = extract_consensus_layers(clusters)
    grafts = extract_unique_grafts(clusters)
    conflicts = detect_all_conflicts(canon, clusters)

    skeleton = recommend_foundation_project(canon, conflicts)

    proposal = build_assembly_proposal(
        skeleton=skeleton,
        foundation=foundation,
        grafts=grafts,
        conflicts=conflicts
    )

    validation = validate_stitched_package(proposal)
    if validation.status == "BLOCKED":
        return blocked_report("stitch validation failed", validation.errors)

    return compile_outputs(
        proposal=proposal,
        validation=validation,
        license_result=license_result
    )
```

核心子函数：

```python
def compile_stitch_profile(fingerprint):
    return {
        "project_id": fingerprint["project_id"],
        "capabilities": extract_capabilities(fingerprint),
        "decisions": extract_design_decisions(fingerprint),
        "patterns": extract_architecture_patterns(fingerprint),
        "constraints": extract_constraints(fingerprint),
        "assumptions": extract_operational_assumptions(fingerprint),
        "licenses": extract_license_claims(fingerprint)
    }

def extract_consensus_layers(clusters):
    foundation = []
    for cluster in clusters:
        if support_count(cluster) >= 2 and support_independence(cluster) >= 0.5:
            if not has_unresolved_conflict(cluster):
                foundation.append(to_foundation_object(cluster))
    return foundation

def extract_unique_grafts(clusters):
    grafts = []
    for cluster in clusters:
        if support_count(cluster) == 1:
            atom = representative(cluster)
            if is_high_value(atom) and is_graftable(atom):
                grafts.append(atom)
    return grafts
```

---

## 11. 我看到的额外工程挑战

brief 里已经提到很多问题，但还有几个更硬的挑战没展开。

## 11.1 “能力能缝”不等于“依赖能缝”

一个 capability 看起来很好移植，但真实前提可能包括：

- 特定目录布局
- 特定 hook 生命周期
- 特定环境变量约定
- 特定工具安装路径

所以 capability 对象必须带：

- `required_files`
- `required_hooks`
- `required_commands`
- `required_env`

否则 assembly plan 会严重低估工作量。

## 11.2 文档/知识的许可证往往比代码更混乱

很多 repo 代码是 MIT，但文档、博客、指南、图表的许可证不清晰。  
而 StitchCraft 很容易复制文档式知识表达。

所以第一版最好：

- 只输出你自己的重新表述
- 不长段搬运原文
- 保留 provenance，不复制 narrative

## 11.3 Quality Gate 要防“伪统一叙事”

LLM 最容易犯的错不是拼错，而是把冲突解释得太漂亮。

所以 stitched narrative 生成时必须带硬约束：

- 冲突不得被消解成单一路线，除非有代码层共识支持
- 所有 unresolved conflict 必须保留在输出中

## 11.4 UI 最好从“组合地图”而不是“融合按钮”开始

如果一开始就做一个大按钮：

- `Generate ultimate skill`

它会诱导产品走向错误的全自动叙事。

更好的 UI 起点是：

- foundation layer
- optional grafts
- conflict map
- choose skeleton

也就是先做“组合工作台”，而不是“自动炼成炉”。

## 11.5 评测集会成为真正门槛

StitchCraft 要验证自己不是在胡乱拼装，至少要有三类 gold set：

1. 可安全组合的项目组
2. 强冲突不可自动组合的项目组
3. license 上不能进入 code graft 的项目组

没有这个评测集，系统只能演示，无法稳定迭代。

---

## 12. 我会怎么定义 StitchCraft

如果让我给这个能力下一句工程定义，我会写：

> **StitchCraft 是 Doramagic 的一个知识融合编译层：它从多个项目的结构化灵魂对象中提取共识、识别冲突、生成组装提案，并在质量与合规门控下输出可执行但不越权的 stitched knowledge package。**

这里最关键的是“编译层”三个字。

因为它说明：

- 输入必须结构化
- 过程必须分阶段
- 冲突必须显式化
- 输出必须可审计

而不是一口气让模型“综合一下”。

---

## 13. 最后一句话

你们真正应该追求的，不是“自动生成一个完美缝合怪”，而是：

## **让用户第一次拥有一个可靠的“开源零件组装台”。**

这更符合 Doramagic 的产品哲学，也更符合工程现实。

所以第一版最值得做的是：

`stitch_profile.json + conflict_graph.json + stitch_compiler.py + Stitch Validation Gate`

而不是自动代码缝合。

---

## 14. 参考资料

- Stitchcraft brief: `/Users/tang/Documents/vibecoding/Doramagic/research/cross-project-intelligence/stitchcraft-research-brief.md`
- Existing cross-project engineering report: `/Users/tang/Documents/vibecoding/Doramagic/research/cross-project-intelligence/codex-report.md`
- Doramagic context: `/Users/tang/Documents/vibecoding/Doramagic/INDEX.md`
- Card/evidence schema: `/Users/tang/Documents/vibecoding/Doramagic/docs/PRODUCT_MANUAL.md`
- Example extracted soul: `/Users/tang/Documents/vibecoding/Doramagic/experiments/exp-seo-skills/claude-seo/CLAUDE.md`
- Multi-source knowledge fusion survey: <https://link.springer.com/article/10.1007/s11280-020-00811-0>
- SPDX license list: <https://spdx.org/licenses/>
- SPDX license expressions spec: <https://spdx.github.io/spdx-spec/v2.3/SPDX-license-expressions/>
- Apache GPL compatibility: <https://www.apache.org/licenses/GPL-compatibility>
- Apache license FAQ: <https://www.apache.org/foundation/license-faq.html>
- license-expression library: <https://pypi.org/project/license-expression/>
- mergekit official repo: <https://github.com/arcee-ai/mergekit>

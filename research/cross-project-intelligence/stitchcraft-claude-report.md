# StitchCraft: 跨项目知识缝合的本质、架构与边界

> 研究员：Claude Opus 4.6
> 日期：2026-03-15
> 视角：知识工程 + 产品架构
> 案例基础：4 个 SEO/GEO 项目灵魂提取（geo-seo-claude / marketingskills / claude-seo / 30x-seo）

---

## 零、核心判断（先说结论）

**缝合不是合并，不是编译，不是蒸馏，也不是生成。缝合是"带约束的知识组合优化"——在一组已验证的知识对象中，按用户场景约束条件，寻找互补组合的帕累托最优前沿。**

这意味着：
1. 缝合的输入不是 CLAUDE.md（叙事），而是 `project_fingerprint.json`（类型化知识对象）
2. 缝合的输出不是"一个完美 skill"，而是一份"组合可能性地图 + 冲突标注 + 兼容性矩阵"
3. 缝合的决策者不是 Doramagic，而是用户——Doramagic 提供 X 光片，不开处方

这个判断的推导过程是本报告的主体。

---

## 一、"缝合"的本质：从四个候选模型中排除

在进入方案设计之前，必须先搞清楚"缝合"到底是什么操作。Brief 提出了四种候选模型：合并、编译、蒸馏、生成。逐一检验。

### 1.1 合并（Merge）——不是

合并的前提是同构数据。`git merge` 能工作，因为两个分支修改的是同一个文件系统。知识合并要求：相同的 schema、相同的 scope、相同的粒度。

但看 4 个 SEO 项目的实际情况：
- geo-seo-claude 的 citability_scorer.py 是一个 **Python 脚本**，输出 5 维度评分
- marketingskills 的 product-marketing-context 是一个 **架构模式**（共享底板），没有代码
- claude-seo 的 validate-schema.py 是一个 **pre-commit hook**，操作的是文件系统事件
- 30x-seo 的 squirrelscan 集成是一个 **外部依赖**

这四个东西不是同一个层次的对象。试图 merge 它们，就像试图 merge 一份简历、一件工具、一条规定和一个供应商——语义类型根本不同。

**排除理由：知识对象不同构，无法定义 merge 操作的语义。**

### 1.2 编译（Compile）——部分正确，但不完整

Knowledge Compiler 是 Doramagic 已有的概念：结构化源卡 -> 按知识类型编译为消费格式。编译有确定性转换的含义——给定输入，输出是确定的。

缝合中确实有编译成分：
- 公约数的提取是编译——4 个项目都说 "FAQPage 2023-08 受限"，这可以确定性地合并为一条共识规则
- 文件结构的兼容性检查是编译——检测 `.agents/skills/` vs `~/.claude/skills/` 的路径冲突是确定性的

但缝合中也有非编译成分：
- "geo-seo-claude 的品牌权重 20% vs 30x-seo 的品牌权重 5%"——这不是编译错误，这是设计哲学冲突
- "是否应该用 marketingskills 的 context 底板模式"——这是架构决策，取决于用户的使用场景

**判断：编译是缝合的确定性子集，但不覆盖全部。**

### 1.3 蒸馏（Distill）——危险的类比

蒸馏暗示 "从 N 个项目中提取本质"，这正是 Brief 中 "取各项目最佳部分" 的直觉来源。

但蒸馏有一个致命假设：**存在一个"本质"等待被提取**。现实是——

geo-seo-claude 的设计哲学是 "品牌存在面决定 AI 可见性"（权重分配：AI 可引用性 25% + 品牌 20% = 45%）。
30x-seo 的设计哲学是 "技术基础决定可发现性"（权重分配：技术 SEO 25% + 内容 25% = 50%）。

这两个哲学不是"同一个真理的不同近似"，而是 **2026 年 SEO->GEO 范式转移中的两条路线**。蒸馏它们就像蒸馏社会主义和资本主义——不是提纯，是消解。

更危险的是：蒸馏产物会给用户一种 "已有定论" 的错觉，违反 "不教用户做事" 的产品哲学。

**排除理由：蒸馏假设存在单一最优解，但领域路线分歧是合法的、有价值的知识本身。消解分歧 = 摧毁信息。**

### 1.4 生成（Generate）——最大的陷阱

Brief 中的假想 "终极 SEO skill" 描述听起来像生成：用 LLM 读完 4 份灵魂提取结果后，写出一份新的、综合的 CLAUDE.md。

这恰好命中了 Doramagic 暗雷体系中最危险的暗雷 #1（LLM 过度推理）。

实验数据已经证明：LLM 面对 4 个项目的冲突设计哲学时，会 **编造一个精巧的统一叙事**——就像同时用 Redis + Memcached 时编出 "分层缓存策略"。真实原因可能只是 "两个作者对 SEO 的理解不同"。

**排除理由：生成 = 让 LLM 做用户应该做的决策 + 高概率触发过度推理幻觉。双重违规。**

### 1.5 缝合的真实本质：带约束的组合优化

排除了四个候选之后，回到第一性原理。缝合真正要做的是什么？

用户面对 4 个 SEO 项目，想要的不是 "一个完美的第五个项目"，而是：
1. **知道每个项目在哪些方面最强**（独创贡献已由灵魂提取完成）
2. **知道哪些部分可以组合、哪些不能**（兼容性矩阵）
3. **知道组合时会遇到什么冲突**（冲突图）
4. **根据自己的场景选择组合方式**（用户决策）

这是一个经典的 **组合优化** 问题：在一组知识对象中，按兼容性约束和用户偏好，寻找互补最优组合。

与合并/编译/蒸馏/生成的根本区别：
- **不消解冲突**，标注冲突
- **不选择最优**，展示帕累托前沿
- **不替代用户**，给用户决策工具
- **确定性部分由代码处理**（兼容性检查、公约数提取），**AI 只做解读**（冲突的含义、组合的风险）

---

## 二、数据结构与算法框架

### 2.1 输入：project_fingerprint.json（已有）+ 新增 stitch_profile

跨项目智能研究已经定义了 `project_fingerprint.json` 的 schema：
```
metadata + code_fingerprint + knowledge_atoms + soul_graph
```

缝合需要在此基础上新增一个 **stitch_profile** 层，从 fingerprint 中自动生成：

```json
{
  "stitch_profile": {
    "capabilities": [
      {
        "id": "cap_citability_scoring",
        "type": "Capability",
        "description": "5-dimension AI citability scoring engine",
        "implementation": "scripts/citability_scorer.py",
        "dependencies": ["requests", "beautifulsoup4", "lxml"],
        "interface": {
          "input": "URL",
          "output": "JSON (5 dimension scores + overall 0-100)"
        },
        "uniqueness": "UNIQUE",  // SHARED | UNIQUE | VARIANT
        "source_project": "geo-seo-claude"
      }
    ],
    "design_decisions": [
      {
        "id": "dd_weight_ai_visibility",
        "topic": "SEO scoring weight allocation",
        "position": "AI visibility 25%, Brand authority 20%",
        "rationale": "Brand Surface Area determines AI visibility, not PageRank",
        "evidence": ["Ahrefs 2025 study: YouTube 0.737 vs backlinks 0.266"],
        "source_project": "geo-seo-claude",
        "conflicts_with": ["dd_weight_technical_seo"]  // 指向冲突
      }
    ],
    "architecture_patterns": [
      {
        "id": "ap_shared_context",
        "name": "Shared context baseplate",
        "description": "All skills read from a single product-marketing-context file",
        "applicability": "Multi-skill systems with shared domain context",
        "source_project": "marketingskills"
      }
    ],
    "constraints": [
      {
        "id": "con_faqpage_restricted",
        "claim": "FAQPage rich results restricted to government/healthcare since 2023-08",
        "type": "CONSENSUS",  // 所有 4 个项目一致
        "support_count": 4,
        "support_independence": 0.3,  // 来源可能相同（Google 官方公告）
        "temporal_validity": {
          "introduced": "2023-08",
          "last_confirmed": "2026-03"
        }
      }
    ]
  }
}
```

**设计要点：**

1. **类型化对象，不是文本块**。每个可缝合的知识单元都有明确的类型（Capability / Design Decision / Architecture Pattern / Constraint / Failure / Assembly Pattern——对应 6 类知识对象）。

2. **uniqueness 字段是缝合的核心**。对比 N 个 fingerprint 后，每个知识对象被标记为：
   - `SHARED`：多个项目共有（公约数）
   - `UNIQUE`：仅一个项目有（独创）
   - `VARIANT`：多个项目有但细节不同（冲突区域）

3. **conflicts_with 是显式边**。不是事后推断冲突，而是在 stitch_profile 生成阶段就识别并标注。

### 2.2 核心算法：三阶段缝合

```
Stage A: Consensus Extraction（共识提取）—— 确定性
Stage B: Compatibility Analysis（兼容性分析）—— 确定性 + 启发式
Stage C: Stitch Map Generation（缝合地图生成）—— 确定性骨架 + AI 解读
```

#### Stage A: 共识提取（代码说事实）

输入：N 个 project_fingerprint.json
输出：consensus_layer.json

算法：
1. 对所有 knowledge_atoms 做三层匹配（复用跨项目智能的 lexical -> semantic -> structured 管线）
2. 匹配到的 atoms 按 support_count 和 support_independence 评分
3. support_count >= threshold AND support_independence > 0.5 的 atoms 进入共识层
4. 每条共识附 provenance（来源项目列表 + 原始证据链）

**关键约束（来自前序研究）**：support_independence 是生死线。4 个项目都引用 Ahrefs 0.737 相关性数据，但这只是 1 次独立验证被传播了 4 次。代码必须做 provenance clustering：追溯到相同上游源头的多次引用折算为 1 次独立支持。

对 4 个 SEO 项目的预期输出：
- FAQPage 2023-08 限制：support=4, independence=LOW（同一 Google 公告）
- HowTo schema 废弃：support=4, independence=LOW
- AI 爬虫不执行 JS -> CSR 不可见：support=4, independence=MEDIUM（多个独立验证来源）
- 134-167 词最优引用段落：support=3, independence=LOW（可能同源）
- 并行子代理架构：support=4, independence=HIGH（独立设计决策）
- Progressive Disclosure 按需加载：support=4, independence=HIGH

#### Stage B: 兼容性分析（代码说事实 + 启发式规则）

输入：N 个 stitch_profile + consensus_layer
输出：compatibility_matrix.json + conflict_graph.json

##### B1: 依赖兼容性（确定性）

```python
def check_dependency_compatibility(profiles):
    """检查 N 个项目的依赖是否可共存"""
    all_deps = {}
    conflicts = []
    for p in profiles:
        for dep in p.dependencies:
            if dep.name in all_deps:
                if not version_compatible(all_deps[dep.name], dep.version):
                    conflicts.append(DependencyConflict(dep.name, ...))
            all_deps[dep.name] = dep
    return conflicts
```

对 4 个 SEO 项目：
- beautifulsoup4, requests, lxml：geo-seo-claude 和 claude-seo 都用，版本兼容
- playwright：claude-seo 和 30x-seo 都用，兼容
- reportlab：仅 geo-seo-claude 用（PDF 报告），无冲突
- squirrelscan：仅 30x-seo 用，无冲突

##### B2: 接口兼容性（确定性 + 启发式）

```python
def check_interface_compatibility(cap_a, cap_b):
    """两个 Capability 能否串联"""
    # 确定性检查：输出格式是否匹配输入格式
    if cap_a.output_format == cap_b.input_format:
        return COMPATIBLE
    # 启发式检查：是否可以通过适配层连接
    if both_json(cap_a.output, cap_b.input):
        return ADAPTABLE
    return INCOMPATIBLE
```

##### B3: 设计决策冲突检测（核心难点）

这是缝合中最复杂的部分。用 4 个 SEO 项目的实际冲突举例：

**冲突 1：SEO 评分权重分配**

| 维度 | geo-seo-claude | claude-seo | 30x-seo |
|------|---------------|------------|---------|
| 技术 SEO | 15% | 25% | 25% |
| AI 可见性 | 25% | 5% | 5% |
| 品牌权威 | 20% | - | - |
| 内容质量 | 20% | 25% | 25% |
| Schema | 10% | 10% | 10% |

缝合系统对此的正确响应不是 "取平均值"，也不是 "选最多人用的"，而是：

```json
{
  "conflict_id": "weight_allocation",
  "topic": "SEO scoring weight distribution",
  "positions": [
    {
      "camp": "GEO-first",
      "projects": ["geo-seo-claude"],
      "weights": {"ai_visibility": 25, "brand": 20, "technical": 15},
      "rationale": "2026 paradigm: Brand Surface Area > PageRank",
      "evidence": "Ahrefs 2025 75K brand study"
    },
    {
      "camp": "Technical-first",
      "projects": ["claude-seo", "30x-seo"],
      "weights": {"technical": 25, "content": 25, "ai_visibility": 5},
      "rationale": "Technical foundation enables all other dimensions",
      "evidence": "Crawlability is prerequisite for any visibility"
    }
  ],
  "interpretation": "This conflict reflects the SEO->GEO paradigm transition in 2026. Neither position is wrong — they serve different strategic priorities. GEO-first suits brands investing in AI search visibility; Technical-first suits sites with unresolved crawlability/indexation issues.",
  "user_decision_required": true
}
```

**冲突 2：Schema 验证策略**

- claude-seo/30x-seo：PostToolUse hook 自动拦截废弃 schema（零容忍）
- geo-seo-claude：将 FAQPage 标记为 "GEO 仍有价值"（保留态度）

这不是技术冲突，是 **scope 冲突**——前者从 Google rich results 角度判断，后者从 AI 引用角度判断。缝合系统的正确做法：标注 scope 差异，让用户根据自己的优化目标选择。

#### Stage C: 缝合地图生成（给用户工具，不给诊断）

最终输出是一份 **Stitch Map**，不是一份 "缝合后的 skill"。

```
STITCH_MAP.md
├── 1. 共识层（所有项目一致的知识，可直接采用）
│   ├── 领域事实（FAQPage 限制、HowTo 废弃、CSR 不可见...）
│   ├── 架构共识（并行子代理、Progressive Disclosure...）
│   └── 共识置信度和证据链
│
├── 2. 独创贡献地图（每个项目的独有价值）
│   ├── geo-seo-claude: citability scoring + Brand Surface Area
│   ├── marketingskills: shared context baseplate + skill graph
│   ├── claude-seo: PostToolUse hooks + SSRF protection + DataForSEO
│   └── 30x-seo: 24 skills coverage + squirrelscan + references
│
├── 3. 兼容性矩阵
│   ├── 依赖兼容性表
│   ├── 接口兼容性表（哪些 capability 可串联）
│   └── 架构模式兼容性（context baseplate 是否适用于所有项目）
│
├── 4. 冲突图
│   ├── 权重分配冲突（GEO-first vs Technical-first）
│   ├── Schema 策略冲突（零容忍 vs 保留 GEO 价值）
│   ├── 每个冲突的双方立场、证据、和解读
│   └── 每个冲突标注 "user_decision_required: true"
│
└── 5. 组合建议（帕累托前沿，非唯一最优）
    ├── 组合 A: GEO 优先方案（geo-seo-claude 为主 + marketingskills context）
    ├── 组合 B: 技术全面方案（30x-seo 为主 + claude-seo hooks）
    ├── 组合 C: 最大覆盖方案（所有独创 + 需解决 N 个冲突）
    └── 每个组合的适用场景、成本、风险
```

### 2.3 与 Doramagic 已有架构的关系

缝合不是独立系统，而是跨项目智能管线的下游消费者。关系图：

```
Soul Extractor（单项目提取）
    ↓ 产出 knowledge_atoms + soul_graph
project_fingerprint.json（跨项目智能，已规划）
    ↓ 产出 structured fingerprint
compare_projects.py（跨项目对比，已规划）
    ↓ 产出 similarity/lineage/consensus/uniqueness
stitch_profile_generator（新增）
    ↓ 产出 capabilities + design_decisions + conflicts
stitch_map_generator（新增）
    ↓ 产出 STITCH_MAP.md
```

**关键点：缝合完全建立在已规划组件之上。** 不需要新的提取管线，只需要在 compare_projects.py 的输出上再加一层组合分析。

与 6 类知识对象的映射：

| 知识对象 | 在缝合中的角色 |
|---------|-------------|
| Capability | 独创贡献地图的主体 |
| Rationale | 冲突图中设计决策的依据 |
| Constraint | 兼容性矩阵的检查项 |
| Interface | 接口兼容性分析的输入 |
| Failure | 各项目踩坑的去重和补全 |
| Assembly Pattern | 组合建议的经验依据（飞轮积累后） |

---

## 三、冲突解决策略：不解决冲突，标注冲突

这是缝合设计中最反直觉也最重要的决策。

### 3.1 为什么不应该自动解决冲突

回到 "不教用户做事" 的产品哲学。SEO 权重分配冲突（技术 25% vs 15%）的本质是：**你认为你的网站现在最大的问题是技术基础（爬不到、索引不了），还是品牌可见性（爬到了但 AI 不引用）？**

这是一个只有网站所有者能回答的问题。Doramagic 如果自动选择，就从 "给工具" 变成了 "教做事"。

### 3.2 冲突的分类与处理

不是所有冲突都需要用户决策。冲突有三种：

**Type 1: 事实冲突（确定性解决）**

例如：如果一个项目声称 "HowTo schema 仍然有效" 而另一个说 "已废弃"，这有确定性答案（Google 2023-09 废弃）。代码直接解决，标注为 RESOLVED，附证据。

**Type 2: Scope 冲突（标注 scope，不解决）**

例如：FAQPage schema 是 "无用"（Google rich results 角度）还是 "有价值"（AI 引用角度）——两者在各自 scope 内都正确。缝合系统标注两个 scope，用户根据自己的优化目标选择。

**Type 3: 路线冲突（展示双方，不裁决）**

例如：权重分配反映的是 GEO-first vs Technical-first 的路线之争。缝合系统展示双方立场、证据和适用场景，用户自己做战略决策。

这个分类对应了证据链体系中的裁决机制：
- RESOLVED -> 确定性裁决（代码处理）
- SCOPE_DEPENDENT -> 附加 scope 标签后保留双方（代码 + AI 解读）
- STRATEGIC_CHOICE -> 展示帕累托前沿（AI 解读为主）

### 3.3 冲突的价值：冲突本身是高价值知识

前序研究中 Claude 的独有洞察："权重冲突 = 领域路线之争，冲突本身是高价值知识。"

在缝合场景中更进一步：**冲突密度是领域成熟度的元指标**。

- 4 个 SEO 项目在 schema 废弃状态上 100% 一致 -> 这个子领域已沉淀
- 4 个 SEO 项目在权重分配上有 2 种路线 -> 这个子领域正在范式转移
- 如果未来缝合 10 个 AI Agent 项目，发现 8 种不同的记忆管理策略 -> 这个子领域尚未成熟

缝合地图应该把冲突密度可视化，让用户看到 "哪些区域是安全的共识，哪些区域是活跃的争论"。

---

## 四、质量验证方法

### 4.1 共识层质量验证

**指标 1: Provenance Accuracy（溯源准确率）**

对每条共识，检查其证据链是否可追溯到原始项目的具体文件。使用 repo_facts.json 的验证逻辑：claim 中的命令/schema/阈值必须在源项目中有 exact match。

预期对 4 个 SEO 项目的验证结果：
- "FAQPage 2023-08 限制" -> 4 个项目的 CLAUDE.md 中都有明确引用 -> PASS
- "134-167 词最优段落" -> 可追溯到 geo-seo-claude 的 citability_scorer.py -> PASS
- "YouTube 0.737 相关性" -> 可追溯到 Ahrefs 2025 研究引用 -> PASS，但 independence=LOW

**指标 2: Independence Score（独立性评分）**

使用 provenance clustering 检查多个项目是否引用了同一上游源头。对于 4 个 SEO 项目，预计大量共识的 independence 会偏低，因为 SEO 行业的知识上游高度集中（Google 官方、Ahrefs、Princeton GEO 研究）。

这不意味着共识不可信——而是说信心来自 "Google 说了"，不是来自 "4 个独立团队验证了"。缝合地图应如实标注。

### 4.2 兼容性矩阵验证

**方法：Dry-Run Composition Test**

选择缝合地图中的一个组合建议，实际尝试将两个项目的 Capability 组合到同一个环境中：

1. 安装 geo-seo-claude 的 citability_scorer.py + claude-seo 的 validate-schema.py hook
2. 检查：依赖冲突？路径冲突？输出格式是否可串联？
3. 如果兼容性矩阵预测 COMPATIBLE 但实际冲突 -> 矩阵有误
4. 如果矩阵预测 INCOMPATIBLE 但实际可工作 -> 矩阵过于保守

### 4.3 冲突图验证

**方法：Expert Review + Adversarial Test**

1. 让 SEO 领域专家审查每个标注的冲突，确认是否确实是冲突（而非误判）
2. 故意制造一个 "看起来像冲突但其实是 scope 不同" 的案例，测试系统能否正确分类
3. 制造一个 "看起来像共识但其实是同源传播" 的案例，测试 independence 评分

### 4.4 最终产物的端到端验证

用 Homework Evaluation Harness 的思路：

1. 给一个用户场景（如 "我是 SaaS 创业者，想优化 AI 搜索可见性"）
2. 方案 A：给用户 4 份完整的 CLAUDE.md，让用户自己读
3. 方案 B：给用户 STITCH_MAP.md
4. 测量：用户能否更快找到适合自己的组合方案？决策质量是否更高？

---

## 五、理论上限与实际下限

### 5.1 理论上限

**最好的情况**：当 N 个项目的知识对象高度互补、低冲突、接口兼容时，缝合可以产出一份接近 "超级项目" 的组合方案。

具体到 4 个 SEO 项目：
- marketingskills 的 context 底板设计（架构层）
- + geo-seo-claude 的 citability scoring（分析层）
- + claude-seo 的 hooks 体系（防护层）
- + 30x-seo 的 24 skill 覆盖面（执行层）
- + 全部公约数作为基础知识层

这个组合在理论上确实可以产生一个比任何单个项目都强的 SEO 工具。但注意：**缝合产出的是组合方案，不是可运行的代码**。实际组装需要工程工作。

### 5.2 实际下限

**最差的情况**：当 N 个项目高度同构（如 claude-seo 和 30x-seo，lineage 可能很高）时，缝合退化为 "选 A 还是选 B" 的二选一问题，独创贡献很少，组合价值有限。

更差的情况：当项目之间的冲突涉及根本性设计哲学（不只是参数差异），缝合地图会充满 "user_decision_required: true" 标记，用户需要自己做大量决策——这可能比直接读每个项目的 CLAUDE.md 更累。

**下限约束因素：**

1. **类型化程度**：如果 project_fingerprint.json 的知识对象粒度太粗（整个 CLAUDE.md 是一个 blob），缝合无法做精细组合。粒度是天花板。

2. **scope 标注质量**：如果知识对象没有 scope 标签（如 "此规则仅适用于商业网站" vs "此规则适用于所有网站"），scope 冲突无法被正确识别，会产生假冲突或漏检。

3. **用户参与意愿**：缝合地图需要用户做决策。如果用户只想要 "一键搞定"，缝合产品形态不适合。

### 5.3 甜蜜区间

缝合价值最大的场景：
- N = 3-8 个同领域项目（太少无统计意义，太多信息过载）
- 项目之间有 40-70% 共识（太少说明领域不成熟，太多说明差异不大）
- 用户有明确的场景约束（可以快速过滤不相关组合）
- 领域正在范式转移（冲突本身有高信息价值）

4 个 SEO 项目恰好落在甜蜜区间：N=4，共识约 45%，SEO->GEO 范式转移中。

---

## 六、其他领域的类比与可借鉴方法论

### 6.1 药物联合治疗（Drug Combination Therapy）

医学领域面对几乎相同的问题：N 种药物，每种对某些症状最有效，如何组合？

借鉴点：
- **药物相互作用矩阵**（Drug Interaction Matrix）-> 兼容性矩阵。不是所有药物都能同时使用。
- **联合治疗方案不是取各药最高剂量**——是根据患者具体情况调整组合和剂量。缝合也一样：不是取各项目 "最强部分"，而是根据用户场景选择互补组合。
- **禁忌症标注**（Contraindications）-> 冲突图。医生看禁忌症决定能否联用，用户看冲突图决定能否组合。
- **关键差异**：药物有临床试验验证联合疗效，缝合没有。这是缝合质量验证的最大缺口。

### 6.2 音频混音（Audio Mixing）

音乐制作中，混音师从多轨素材中组合出最终作品。

借鉴点：
- **频段分离**：每个轨道占据不同频段（低频、中频、高频），混音师确保它们不冲突。对应缝合中 "不同层次的知识对象不冲突"——架构层的 context 底板和分析层的 citability scoring 天然不冲突。
- **EQ 和 sidechain**：当两个轨道在同一频段冲突时，混音师用 EQ 切掉一个的冲突频段，或用 sidechain 让一个在另一个发声时自动让路。对应缝合中的 scope 标注——同一个 schema 规则在不同 scope 下各自适用。
- **关键差异**：混音有明确的审美标准（听起来好不好），缝合的 "好不好" 取决于用户场景。

### 6.3 法律判例综合（Legal Precedent Synthesis）

法学研究中，律师需要从多个判例中综合出法律原则。

借鉴点：
- **区分 ratio decidendi 和 obiter dictum**：判例的核心判决理由 vs 附带评论。对应缝合中区分 "核心设计决策"（权重分配）和 "实现细节"（具体脚本）。
- **判例冲突时的处理**：法院不是 "取平均"，而是分析冲突判例的具体情境差异（scope），或由更高级法院裁决（用户决策）。
- **判例的时效性**：旧判例可能被新判例覆盖。对应缝合中的 temporal_validity——2023 年的 SEO 规则可能在 2026 年已失效。

### 6.4 系统生物学中的通路分析（Pathway Analysis）

生物学中，单个基因的功能不重要，重要的是基因在通路（pathway）中的角色。

借鉴点：
- **功能冗余**（Functional Redundancy）：多个基因做同一件事，敲除一个影响不大。对应缝合中多个项目的共识知识——有冗余但不是浪费，是鲁棒性。
- **合成致死**（Synthetic Lethality）：单独敲除 A 或 B 都没事，同时敲除才致死。对应缝合中的 "看起来兼容但实际组合后出问题" 的场景——需要 Dry-Run 测试。
- **通路图**（Pathway Map）-> 缝合地图。不是列出所有基因（知识对象），而是展示它们之间的关系网络。

---

## 七、风险评估

### 7.1 产品风险

**风险 1：用户期望 "一键缝合" 但得到 "决策地图"**

缓解：在产品叙事中明确——Doramagic 不是裁缝，是制版师。Doramagic 给你裁剪图和面料清单，你决定怎么缝。

**风险 2：缝合地图信息过载**

当 N > 5 时，冲突图和兼容性矩阵会变得复杂。缓解：提供过滤机制——用户声明自己的场景约束（如 "我只关心 AI 搜索优化"），缝合系统自动过滤不相关的组合。

**风险 3：缝合质量无法验证**

与单项目灵魂提取不同，缝合的 "正确性" 没有 gold standard。缓解：先在 4 个 SEO 项目上做 dry-run，人工验证缝合地图的每一项，建立第一个 gold set。

### 7.2 技术风险

**风险 1：knowledge_atom 粒度不够支持精细缝合**

当前 knowledge_atom 的 canonical form（subject/predicate/object/modifiers）可能太粗。例如 "SEO scoring uses weights" 这个 atom 无法表达 "技术 SEO 25% vs 15%" 的具体差异。缓解：在 stitch_profile 层新增 design_decision 类型，专门记录有参数差异的决策。

**风险 2：冲突检测的假阳性/假阴性**

两个项目使用不同的术语描述同一件事（如 "Brand Surface Area" vs "品牌提及"），可能被误判为不同的东西。缓解：在语义匹配阶段使用 embedding similarity，但增加 slot-level 验证（subject 和 predicate 都要匹配）。

### 7.3 伦理与法律风险

**开源协议**：缝合不涉及代码复制。缝合地图只描述知识对象的组合关系，不包含源项目的代码。但如果用户根据缝合地图实际组合代码，需要遵守各项目的 license。缝合地图应标注每个 capability 的源项目 license。

**Credit**：缝合地图的每个知识对象都有 source_project 字段。这不是可选的——是强制的。没有溯源的缝合等于洗稿。

**"套壳"风险**：缝合本身不是套壳——它是明确标注来源的知识组合分析。但如果有人拿缝合地图去包装一个 "原创" 项目而不标注来源，这是用户行为问题，不是工具问题。类似 git blame 不为代码抄袭负责。

---

## 八、MVP 路径

基于上述分析，最小可行的缝合 MVP：

### Phase 1: Stitch Profile 生成（1 天）

在 compare_projects.py（已规划）的输出上新增一个函数：

```python
def generate_stitch_profile(fingerprints, comparison_result):
    """从 N 个 fingerprint + 对比结果生成 stitch_profile"""
    capabilities = extract_unique_capabilities(fingerprints)
    design_decisions = extract_design_decisions_with_conflicts(fingerprints)
    consensus = comparison_result.consensus_layer
    conflicts = detect_conflicts(design_decisions)
    compatibility = check_compatibility(capabilities)
    return StitchProfile(capabilities, design_decisions, consensus, conflicts, compatibility)
```

### Phase 2: Stitch Map 渲染（1 天）

```python
def generate_stitch_map(stitch_profile):
    """生成 STITCH_MAP.md"""
    # 确定性部分（代码处理）
    render_consensus_layer(stitch_profile.consensus)
    render_unique_contributions(stitch_profile.capabilities)
    render_compatibility_matrix(stitch_profile.compatibility)
    render_conflict_graph(stitch_profile.conflicts)

    # AI 解读部分（LLM 处理）
    interpret_conflicts(stitch_profile.conflicts)  # 冲突的含义
    suggest_combinations(stitch_profile)  # 帕累托前沿
```

### Phase 3: 用 4 个 SEO 项目验证（1 天）

1. 对 4 个已提取的 SEO 项目生成 stitch_profile
2. 生成 STITCH_MAP.md
3. 人工验证：共识是否正确？独创是否遗漏？冲突是否合理？组合建议是否可行？
4. 建立第一个 gold set

### 依赖关系

缝合 MVP 的前置依赖：
- project_fingerprint.json schema 定稿（跨项目智能 Phase 0）
- compare_projects.py 可运行（跨项目智能 Phase 1）

如果这两个前置已就绪，缝合 MVP 可在 2-3 天内完成。如果未就绪，缝合可以先用 4 个 CLAUDE.md 的文本作为输入做概念验证，但精度会低很多。

---

## 九、缝合怪暗示的更大可能性

### 9.1 领域知识地图

如果 Doramagic 持续在 SEO 领域缝合更多项目（不止 4 个，而是 20 个、50 个），缝合地图会逐渐演变为 **SEO 领域知识地图**：
- 哪些知识是行业共识（高 support_count + 高 independence）
- 哪些知识是前沿争论（高冲突密度）
- 哪些知识正在过时（temporal_validity 接近失效）
- 哪些知识是被低估的独创（仅 1-2 个项目有，但证据质量高）

这比任何单个项目的灵魂提取都有价值——因为它展示的是 **领域级结构**，不是项目级叙事。

### 9.2 知识时效监控

当缝合地图覆盖足够多的项目后，可以实现自动化的知识时效监控：
- HowTo schema 在 2023-09 被废弃 -> 检测还有哪些项目在推荐使用 -> 标记为过时
- INP 在 2024-03 替代 FID -> 检测还有哪些项目引用 FID -> 标记为过时

单个项目无法知道自己的知识是否过时。领域级缝合地图可以。

### 9.3 作业推荐引擎

当用户描述自己的需求时（"我要做 AI 搜索优化"），缝合系统可以根据已有的缝合地图推荐最适合的组合——不是推荐 "最好的项目"，而是推荐 "对你最互补的项目组合"。

这与好作业评分体系中的 NeedFit 维度直接对接：**好作业不是绝对质量最高的，而是对用户增量价值最大的**。缝合把这个原则从单项目推荐扩展到多项目组合推荐。

---

## 十、总结

| 问题 | 结论 |
|------|------|
| 缝合的本质 | 带约束的知识组合优化，不是合并/编译/蒸馏/生成 |
| 输入 | project_fingerprint.json（类型化知识对象），不是 CLAUDE.md（叙事） |
| 输出 | STITCH_MAP.md（组合可能性地图），不是 "缝合后的 skill" |
| 冲突解决 | 不解决冲突，标注冲突——事实冲突确定性解决，scope 冲突标注 scope，路线冲突展示帕累托前沿 |
| 与已有架构关系 | 建立在 fingerprint + compare_projects 之上的下游消费者，不需要新管线 |
| 质量验证 | Provenance Accuracy + Independence Score + Dry-Run Composition Test |
| 理论上限 | 产出超越任何单个项目的组合方案（在甜蜜区间） |
| 实际下限 | 退化为 "选 A 还是选 B"（当项目高度同构时） |
| MVP 依赖 | fingerprint schema + compare_projects.py，增量开发 2-3 天 |
| 产品哲学合规 | 给工具不开处方——缝合地图是 X 光片，用户是医生 |
| 最大的可能性 | 积累到足够项目后，从项目级缝合演变为领域级知识地图 |

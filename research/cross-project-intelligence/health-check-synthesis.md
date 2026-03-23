# 知识健康检查（Knowledge Health Check）三方研究综合报告

> 日期：2026-03-15
> 三方：Claude Opus（知识工程+产品设计）/ Gemini（产品+市场+UX）/ Codex（工程实现+算法）

---

## 一、六项全票共识

### 共识 1：体检是图谱的消费层，不是新产品

- **Claude**："图谱的消费界面，不是新产品"
- **Codex**："受约束匹配与分类引擎"，"不是新系统"
- **Gemini**："知识生命力的诊断"（在图谱框架内）

**结论**：体检不独立存在。没有图谱，就没有体检（STALE 除外）。

### 共识 2：不给总分，不定义"健康"

- **Claude**：明确拒绝总分，用雷达图/多维向量
- **Codex**："不是评分器"
- **Gemini**：用"知识星系坐标"而非打分

**结论**：体检展示位置和差异，不做好坏判断。"不教用户做事"原则的直接推论。

### 共识 3：STALE 检测可独立运行

- **Claude**："即使图谱尚未建成，也可以先上线知识时效检查"
- **Codex**：代码层显式分离 `stale_engine(atoms, deprecation_db)` 和 `map_alignment_engine(atoms, map)`
- **Gemini**：未深入，但不矛盾

**结论**：STALE 是体检的最小可用子集，是最早能上线的功能。它不依赖图谱，只依赖废弃事件数据库。

### 共识 4：参照系透明度是生死线

- **Claude**："参照系强度必须是视觉上无法忽略的——不是 footnote，是报告顶部的醒目标注"
- **Gemini**："明确展示图谱来源"，允许用户踢出项目重算
- **Codex**：缓存键包含 5 维版本信息，旧图谱版本的体检标注 `outdated_by_map_version`

**结论**：用户必须始终知道"这个结论基于多大的样本"。Alpha 阶段措辞必须克制。

### 共识 5：7 类信号分类体系

- **Claude**：提出完整 7 类（ALIGNED / STALE / MISSING / ORIGINAL / DIVERGENT / DRIFTED / CONTESTED）
- **Codex**：完全接受 7 类，补充拆成两路（确定性 + 解释性）
- **Gemini**：引用信号分类，更关注产品呈现

**结论**：7 类信号是体检的核心骨架。工程上拆双路（Codex 建议）是正确的。

### 共识 6：V1 从 CLI/文件输出开始，不做交互式界面

- **Claude**：V1 独立功能（`/health-check <project> --domain seo`），输出 health_check.json + HEALTH_CHECK.md
- **Codex**：完整数据流从 validated atoms 到 json 到 markdown
- **Gemini**：虽然设计了 Knowledge Galaxy 可视化，但这是 V2+ 的方向

**结论**：V1 产出文件，V2+ 有 web 界面时再做可视化。

---

## 二、各方独有最佳贡献

### Claude 独有：理论框架 + 哲学定位

1. **GIS 叠加分析类比**：排除了三个危险类比（医疗体检/财务审计/代码审查），找到准确定位——"地图叠加分析"。这决定了产品不做诊断、不做合规检查、不看代码质量，只做知识位置定位。

2. **6 个可观测维度**：共识覆盖率 / 时效性 / 独创密度 / 路线位置 / 缺失区域 / 参照系强度。不定义"健康"，但定义"可观测的坐标"。

3. **严重性分级**：HIGH-SIGNAL / SIGNAL / CONTEXT，拒绝了 Critical/Warning/Info（那是审计语言），用"信息密度"替代"严重性"。

4. **完整案例演示**：用 geo-seo-claude 的实际数据，生成了 130+ 行的 HEALTH_CHECK.md 样例。这是三方中唯一的端到端案例。

5. **4 个新可能性**：
   - 体检报告作为"项目简历"（OpenClaw 发布时附带）
   - 知识趋势追踪（定期体检的时间序列）
   - 匿名化领域健康度指标
   - 反向体检（图谱因新项目更新后通知旧用户）

6. **5 个风险分析**：权威性错觉 / 共识偏见固化 / 吹毛求疵 / 过时误判 / 选型依赖。每个有缓解方案。

### Gemini 独有：产品体验 + 市场策略

1. **知识星系可视化（Knowledge Galaxy）**：二维坐标系（横轴共识度、纵轴新颖度），项目作为"彗星"，标杆项目作为"行星群"。**评价：概念优秀，V2+ 时是有力的交互设计方向。**

2. **渐进式披露 UX**：30 秒概览（看板 3 个高能信号）→ 5 分钟关键发现（Feed 流）→ 按需深入（分屏对比）。**评价：即使 V1 只输出 Markdown，也应遵循此信息层次。**

3. **情感设计**：
   - 禁止使用"错误"、"漏掉"、"落后"
   - 推荐词汇："观测到差异"、"非主流路径"、"新兴趋势"
   - **评价：直接采纳。这是"不教用户做事"在措辞层的落地。**

4. **"作者辩论"功能**：允许作者对 finding 输入理由，AI 动态调整解读。**评价：好概念，V2+。V1 不做。**

5. **竞品差异化表**：

   | 维度 | SonarQube | GitHub Copilot | Doramagic KHC |
   |------|-----------|---------------|---------------|
   | 关注点 | 语法/安全/风格 | 代码生成/补全 | 架构决策/设计哲学/知识保鲜 |
   | 参照系 | 标准规则集 | 预测概率 | 跨项目共识图谱 |
   | 类比 | 纠错别字 | 帮你写下段 | 评估论文观点是否过时 |

6. **Freemium 商业模型**：
   - 免费层：基础体检 + 知识健康徽章（GitHub README 展示）
   - 付费层：详细证据链 + 保鲜订阅 + 重构方案
   - 企业级：内部项目 vs 标准架构灵魂的偏离度报告

7. **PM/CTO 翻译层**：将技术信号翻译为业务风险（STALE → 维护成本, ORIGINAL → 核心壁垒, DIVERGENT → 稳定性隐患）。**评价：有价值，但 V1 只做开发者视图。**

8. **"知识天气预报"**：聚合全平台体检数据，发布领域技术趋势预警。**评价：远期概念，需要大量数据积累。**

### Codex 独有：工程深度

1. **三段式匹配算法**：候选召回（lexical + semantic ANN）→ 结构化裁决 → 信号分类。**这是体检工程的核心骨架。**

2. **加权匹配公式**：
   ```
   MatchScore = 0.30 × subject + 0.25 × predicate + 0.15 × object + 0.20 × scope + 0.10 × normative_force
   ```

3. **四段匹配阈值**：
   - EXACT_ALIGNED ≥ 0.92（且 scope ≥ 0.9）
   - SEMANTIC_ALIGNED ≥ 0.80（且 scope ≥ 0.75）
   - PARTIAL_MATCH ≥ 0.62
   - NO_MATCH < 0.62
   - **设计原则：偏保守，宁可少报 ALIGNED。**

4. **MISSING 双阈值**：coverage ≥ 0.60 + independence ≥ 0.55 + 独立支持 ≥ 3。比 Claude 的"X%"更精确。

5. **ORIGINAL 二次检验**：用更大候选窗口重新检索，确认仍无匹配才标 ORIGINAL。防止"表述不同"的假阳性。

6. **确定性 vs 解释性双路分离**：
   - Route A（确定性）：ALIGNED / STALE / MISSING / ORIGINAL
   - Route B（解释性）：DIVERGENT / DRIFTED / CONTESTED
   - **评价：工程上正确。A 路靠阈值，B 路需要更多上下文。**

7. **5 个完整数据结构**：ProjectAtom / AtomCluster / DeprecationEvent / HealthFinding / HealthCheckCacheKey。每个有 JSON Schema。

8. **deprecation_events.jsonl**：独立的废弃事件数据库，三级来源（official > graph > community），append-only。**这是 STALE 引擎的基础设施。**

9. **复杂度优化**：type 分桶 → subject 分桶 → ANN 候选，将 O(N×M) 降到 O(N×k)。

10. **缓存 + 版本管理**：SQLite 索引表 + 5 维缓存键 + 图谱版本用 `domain_id@semver+content_hash`。

11. **4 个测试用例 + gold set 预期分布**：
    - claude-seo：ALIGNED 多 / ORIGINAL 中
    - 30x-seo：与 claude-seo 高度相似（Jaccard ≥ 0.8）
    - geo-seo-claude：ORIGINAL 高 / DIVERGENT 高
    - marketingskills：跨域强 / ORIGINAL 高

12. **完整伪代码**：`run_health_check()` 约 130 行，覆盖缓存 → STALE → 召回 → 匹配 → 7 类分类 → 去重 → 排序 → 汇总。

---

## 三、分歧与决策建议

### 分歧 1：匹配方法

- **Claude**：slot matching，不用 embedding（因为 scope 问题）
- **Codex**：hybrid——semantic retrieval 做召回，slot matching 做裁决

**决策建议：采 Codex 方案。** Claude 的直觉是对的（纯 embedding 会混淆 scope），但实现上需要 embedding 做召回层。两阶段分工解决了这个矛盾。

### 分歧 2：Gemini 的"重构方案生成"

- **Gemini**：付费层提供"一键式 Pull Request 补丁"
- **Claude**：V1 不连接 StitchCraft。推荐 = 开处方，违反"不教用户做事"。

**决策建议：不做自动推荐。** 如果用户主动请求"帮我补上缺失的知识"，那是另一个显式请求，由 StitchCraft 处理。体检只出 X 光片。

### 分歧 3：Gemini 的"健康徽章"和"社交货币"

- **Gemini**：高分项目获得官方认证，提升社区信用度
- **Claude**：不定义"健康"，不给总分

**决策建议：V1 不做徽章。** 如果做，必须是多维展示（"共识覆盖 78% / 独创密度 16%"），绝不是单一分数或"通过/不通过"。可以在 V2+ 探索"项目简历"形式。

### 分歧 4：V1 是否需要可视化

- **Gemini**：Knowledge Galaxy、分屏对比、Feed 流
- **Claude + Codex**：V1 输出 JSON + Markdown

**决策建议：V1 只做文件输出。** 但 Gemini 的渐进式披露思路应反映在 Markdown 结构中（概览表 → 高信号发现 → 完整列表）。Gemini 的情感设计用词（禁止"错误"/"落后"）直接采纳到渲染 prompt 中。

### 分歧 5：Gemini 的"作者辩论"功能

- **Gemini**：让作者输入理由，AI 调整解读
- **Claude + Codex**：未提及

**决策建议：V2+ 探索。** 好概念，但 V1 优先级是匹配引擎稳定性，不是交互体验。

---

## 四、直接采纳清单

以下内容无争议，直接进入实施计划：

| 来源 | 采纳内容 | 原因 |
|------|---------|------|
| Claude | GIS 叠加分析定位（非医疗/审计/代码审查） | 理论框架直接影响产品设计决策 |
| Claude | 7 类信号 + 6 可观测维度 + 不给总分 | 产品哲学一致 |
| Claude | STALE 独立运行 = 最小可用子集 | V0 就能上线 |
| Claude | 案例演示格式 | 直接作为 HEALTH_CHECK.md 模板 |
| Gemini | 情感设计用词（禁止"错误"/"落后"） | 渲染 prompt 必须包含 |
| Gemini | 渐进式披露层次（概览→关键→详细） | Markdown 结构遵循 |
| Gemini | 竞品差异化表 | 产品定位参考 |
| Codex | 三段式匹配算法 | 工程核心 |
| Codex | 加权匹配公式 + 四段阈值 | 可直接编码 |
| Codex | MISSING 双阈值 + ORIGINAL 二次检验 | 降低假阳性 |
| Codex | 确定性/解释性双路分离 | 工程可维护性 |
| Codex | deprecation_events.jsonl | STALE 引擎基础设施 |
| Codex | 缓存 5 维键 + SQLite 索引 | 可追溯性保证 |
| Codex | 完整伪代码 | 编码起点 |
| Codex | 4 个测试用例 + gold set 预期 | 验证标准 |

---

## 五、实施路径（整合三方）

| 阶段 | 时间 | 内容 | 关键依赖 |
|------|------|------|---------|
| **V0** | 1 天 | STALE 检测器：deprecation_events.jsonl + stale_engine() | 只需 Soul Extractor 输出 |
| **V0.5** | 1 天 | scope ontology 固定（engine/persona/environment/time 的枚举值） | 跨项目对比经验 |
| **V1-a** | 2 天 | 候选召回 + 结构化裁决：ALIGNED / MISSING / ORIGINAL 检测 | 领域图谱 Alpha |
| **V1-b** | 1 天 | health_check.json 编译 + HEALTH_CHECK.md 渲染（含 Gemini 情感用词 prompt） | V1-a |
| **V1-c** | 1 天 | 4 个 SEO 项目 gold set 验证 | V1-b |
| **V1.1** | 2 天 | DIVERGENT + DRIFTED + CONTESTED（解释性路线） | StitchCraft 冲突分类 |
| **V2** | TBD | 知识星系可视化 + 作者辩论 + 多图谱 blended mode | Web 界面 |

**总 V1 工时：约 6 天（在图谱 Alpha 就绪后）**

---

## 六、一句话总结

> 知识健康检查 = 领域图谱的镜子功能。代码做匹配（Codex 的三段式算法），结构做分类（Claude 的 7 类信号），措辞做尊重（Gemini 的情感设计）。三方各守一层，缺一不可。

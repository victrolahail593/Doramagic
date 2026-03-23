# 领域共识图谱三方研究综合报告

> 日期：2026-03-15
> 三方：Claude Opus（战略规划+知识工程）/ Gemini（产品+市场）/ Codex（工程实现+数据架构）

---

## 一、三方核心共识

### 共识 1：图谱是飞轮的冷启动燃料，不是新产品

- **Claude**："这不是新范式，是飞轮的燃料"。尊重 Tang 的修正，能力升级本质不变。
- **Codex**："领域共识图谱不是一个新产品页面，而是 Doramagic 的预训练层"
- **Gemini**：虽然用了更激进的语言（"领域真相引擎"），但本质也是增强现有提取能力

**结论**：图谱的价值不在于"用户能看到一张图"，而在于"用户来的时候，Doramagic 已经对这个领域有组织过的记忆"。

### 共识 2：第一个领域必须是 SEO/GEO

三方一致，无争议。理由：唯一有实验验证的领域、范式转移中需求最旺、项目供应充足、提取难度低。

### 共识 3：知识原子是图谱的核心单位，领域是视图

- **Claude**："图谱底层是无边界的知识原子池，领域分类是视图而非组织单位"
- **Codex**：四层结构（Project Layer → Atom Layer → Consensus Layer → Consumption Layer），atom cluster 是基本操作单位
- **Gemini**：未深入数据结构，但认同原子级别的可组合性

**结论**：不是"建一个 SEO 图谱"，是"建一个知识原子库，其中有 SEO 标签的子集"。

### 共识 4：V1 策展，不爬取

- **Claude**："V1 必须是策展，暗雷检测是关键能力，自动爬取无法做暗雷检测"
- **Codex**："手动触发重编译"，batch-first，不做实时
- **Gemini**：强调"策展团队"概念

**结论**：冷启动阶段每一个坏样本都会被放大。精选 5-7 个项目 > 随机 20 个。

### 共识 5：图谱注入 Soul Extractor 的最佳位置是 Stage 0/1

- **Claude**：三个注入点——Stage 0（Brick 注入，最重要）、Stage 3.5（fact-checking）、Stage 5（输出增强）
- **Codex**：Stage 0 做路由和召回、Stage 1 做 WHY 锚点（最重要）、Stage 2-3 做规则校准、Stage 3.5 做交叉验证
- **Gemini**：未深入管线注入

**结论**：Stage 0/1 注入是最高杠杆。Brick 效应已被 Session 24-25 实验验证（+20%）。

---

## 二、各方独有最佳贡献

### Claude 独有：战略框架

1. **领域选择四因子公式**：`DomainPriority = DemandSignal × SupplyReadiness × ExtractabilityScore × StrategicFit`，每个因子有三级可量化指标。6 个候选领域的定性评估表。

2. **最小有效样本量模型**：不是固定数字，是独立性的函数。Alpha 5-7（独立来源≥4）→ Beta 10-15（≥7）→ GA 15-20（≥10）。关键约束：独立来源数 ≥ 项目数 × 0.6。

3. **边际收益曲线预测**：项目 1-5 递增、5-15 稳定、15+ 递减，除非遇到范式转移项目。

4. **保鲜三种衰减模式**：断崖式失效（HowTo 废弃）/ 渐变式过时（关键词堆砌变有害）/ 分裂式演化（SEO→GEO）。

5. **"告诉我领域真相"的技术拆解**：5 步管线（加载图谱 → 按 status 分组 → 按 tags 聚类 → LLM 叙事 → 输出 DOMAIN_TRUTH.md）。输出格式：领域健康度 + 无争议共识 + 路线之争 + 暗雷警告 + 前沿探索。

6. **图谱 = X 光片的延伸**：共识=骨骼、冲突=关节、暗雷=骨折标记、前沿=生长板。

7. **新可能性**：图谱作为"作业评审标准"、驱动 Incomplete Skill 补完、知识流行病学、跨领域知识迁移检测。

### Gemini 独有：产品与市场

1. **竞品差异化分析**：
   - Gartner Magic Quadrant = 分析师手工、年度更新、$$$
   - ThoughtWorks Tech Radar = 人工策展、季度更新、单公司视角
   - StackShare = 用户自报、偏"用什么"不知"为什么"
   - Doramagic = 自动从代码提取、持续更新、回答"为什么"和"什么坑"

2. **"领域真相"的信任构建**：透明度策略——每条知识标注来源项目数、独立性评分、上游来源。"Doramagic 不制造真相，它从开源代码中提炼共识。"

3. **商业模型**：免费领域概览（吸引用户）+ 付费深度服务（图谱增强提取、私有项目对比、企业级定制图谱）

4. **"知识健康检查"概念**：用户把自己的项目放到领域图谱上做"体检"——哪些知识已过时、哪些缺失、哪些偏离共识。

### Codex 独有：工程深度

1. **四层架构**：Project Layer → Atom Layer → Consensus Layer → Consumption Layer。图谱的 source of truth 是前三层，Consumption Layer（DOMAIN_MAP.md / DOMAIN_BRICKS.json）是编译产物。

2. **存储方案**：SQLite（metadata + index + transactions）+ Parquet（atoms + embeddings 批处理）+ JSONL（append-only events）。明确反对一开始用图数据库或向量数据库。

3. **增量更新算法**：原子级增量融合——新项目的 atom 找已有 cluster → 命中则更新 cluster stats → 未命中则建新 cluster → 只重编译受影响的 bricks。全量重算仅在 schema migration 时。

4. **Atom Cluster 数据结构**：领域图谱的基本操作单位不是单个 atom，是 atom cluster（含 representative_atom + member_atoms + support_count + independence + scope_signature）。

5. **保鲜算法伪代码**：`refresh_atom()` 函数——confirms → 刷新时间戳+提升置信度 / contradicts → 标记+大幅降权 / supersedes → 链接替代 / 超 TTL → 标 stale。

6. **冷启动自动化管线**：7 步脚本（discover → clone → batch_extract → build_fingerprints → compare → build_domain_map → compile_outputs），含最小骨架伪代码。

7. **成本估算**：10 项目 ≈ $40-120、2-5 小时（并行 4 workers）；20 项目 ≈ $80-250、4-10 小时。增量刷新成本 ≈ 全量的 10%-30%。

8. **关键工程警告**：
   - 领域边界不是静态的（允许子域 + atom 跨域挂载）
   - 图谱会固化偏见（保存 stack/persona/archetype 分布做质量控制）
   - Brick 编译才是真正的产品接口（用户和管线都不应消费 raw graph）
   - 不做实时图谱，batch-first + daily/weekly refresh

---

## 三、分歧与决策建议

### 分歧 1：图谱的用户可见性

- **Claude**：图谱主要服务 Soul Extractor 管线，用户看到的是增强后的提取质量 + DOMAIN_TRUTH.md
- **Gemini**：图谱应有独立的用户界面（领域仪表盘、知识健康检查、交互式探索）
- **Codex**：图谱是预训练层，用户不直接消费 raw graph，只消费编译产物

**决策建议**：V1 采 Claude + Codex 路线（图谱 = 引擎升级，用户感知的是提取质量提升 + DOMAIN_TRUTH.md 报告）。Gemini 的交互式界面留到 V2+（需要足够数据量才有意义）。

### 分歧 2：存储方案

- **Claude**：JSON 文件体系（目录结构式）
- **Codex**：SQLite + Parquet + JSONL

**决策建议**：采 Codex 方案。10-20 项目规模 JSON 文件也能工作，但 SQLite 给增量更新提供了事务保证，Parquet 给批处理分析提供了列式查询能力，成本几乎为零。

### 分歧 3：Gemini 报告路径

Gemini 写到了 `/Users/tang/research/` 而非 `/Users/tang/Documents/vibecoding/Doramagic/research/`。需要手动移动文件。

---

## 四、完整实施路径（整合三方）

| 阶段 | 时间 | 动作 | 产出 |
|------|------|------|------|
| **P0** | 1-2 天 | 定稿 `project_fingerprint.json` schema + `compare_projects.py` | 跨项目智能基础设施 |
| **P1-a** | 1-2 天 | 用现有 4 个 SEO 项目手动构建图谱原型（SQLite + Parquet） | `domain_map.sqlite` v0.1.0 |
| **P1-b** | 1 周 | 策展 + 提取 3-4 个补充 SEO 项目（补缺口：电商 SEO、Local SEO、纯 AI SEO） | Alpha 图谱 v0.2.0（7 项目） |
| **P2** | 1 周 | 实现 `inject_domain_context.py` + Stage 0/1 注入 + `compile_domain_outputs.py` | 图谱增强的灵魂提取 + DOMAIN_BRICKS.json + DOMAIN_TRUTH.md |
| **P3** | 1 天 | A/B 验证：有图谱注入 vs 无图谱注入的提取质量对比 | 量化 ROI |
| **P4** | 持续 | 增量更新机制 + 保鲜事件 + 用户策展回流 | 飞轮启动 |

成本估算（SEO/GEO Alpha 图谱，7 项目）：
- 补充提取 3-4 个项目：$10-40、1-2 小时（并行）
- 图谱构建 + 编译：脚本开发 2-3 天，运行时间忽略不计
- 总投入：约 1 人·2 周

---

## 五、一句话总结

> 领域共识图谱让 Doramagic 从"瞎子摸象"变成"带着地图摸象"。用户看到的不是图谱本身，而是图谱增强后的提取质量——每一次提取都站在整个领域的肩膀上。

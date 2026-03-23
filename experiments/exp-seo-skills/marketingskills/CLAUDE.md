# marketingskills — Soul Extraction

> 基于仓库内容分析：README + 10 个核心 skill（product-marketing-context, seo-audit, ai-seo, site-architecture, programmatic-seo, schema-markup, content-strategy, page-cro + 2 more）+ tools registry

---

## 灵魂 (Soul)

**Q1. 解决什么问题？**
Technical marketer 或 SaaS founder 需要做 40 种营销任务（CRO、SEO、文案、广告），但 AI coding agent 缺乏营销领域的专业框架和最佳实践知识。

**Q2. 没有这个项目，人们怎么做？**
要么反复向 agent 解释营销背景（每次对话都要重新建立上下文），要么 agent 给出通用建议而非专业营销决策，相当于雇了一个没有营销经验的程序员做营销工作。

**Q3. 核心承诺是什么？**
让 AI agent 在第一次被调用时就已经掌握营销专家级的框架、决策树和行业规则，而不需要用户解释"什么是 CRO"或"SEO 优先级如何排序"。

**Q4. 如何兑现承诺？**
通过 33 个 Markdown skill 文件注入领域知识 + 一个共享上下文文件（`product-marketing-context.md`）做跨 skill 的产品信息复用，agent 调用前先读 context、再执行任务。

**Q5. 一句话总结**
marketingskills 让 technical marketer 用 AI coding agent 做专业营销决策，而不必每次从头解释"什么是营销"。

**Q6. 设计哲学**
营销知识最大的问题不是"找不到"而是"没有被结构化为可执行的决策树"。这个项目的核心信念是：**把专家头脑里的判断顺序编码成文件**——不是罗列知识点，而是把"先检查什么、再检查什么、遇到 X 情况怎么处理"这种专家经验写成 agent 可以逐步执行的框架。每个 skill 的结构（Initial Assessment → Framework → Output Format → Related Skills）本身就是一套决策流程，agent 读完就知道"下一步该问什么、输出什么格式"，而不需要发明它自己的流程。

**Q7. 心智模型**
把每个 skill 想象成一份外科手术清单（surgical checklist）：不是要教医生如何手术，而是把专家已经内化的步骤外化出来，防止遗漏关键项。`product-marketing-context` 就是病历表——手术前所有人先看一遍，术中不再重复问基本信息。

---

## 设计哲学 (Design Philosophy)

真正值得提炼的设计信念是：**上下文共享是知识系统的第一性原理，而不是功能堆叠。**

所有 33 个 skill 都以同样的模式开头：
```
Check for product marketing context first:
If `.agents/product-marketing-context.md` exists, read it before asking questions.
```

这不是巧合，而是架构决定。作者意识到，AI agent 在营销领域失败的根本原因不是"不懂 CRO"而是"每个任务都在真空中执行"。每次调用 `page-cro` 都要重新解释"我们卖什么、卖给谁、竞争对手是谁"，这种摩擦才是生产力杀手。

`product-marketing-context` skill 因此成为整个系统的基础层（foundation），其他 skill 都是在这个共享基础上的专业化执行层。这和软件架构里的"单一事实来源（single source of truth）"原则完全对应。

另一个信念：**边界清晰比功能全面更重要。** 每个 skill 都明确声明"不处理 X，X 请用 Y skill"。`page-cro` 不处理 signup 流程（用 `signup-flow-cro`），`seo-audit` 不处理 AI 搜索优化（用 `ai-seo`）。这种边界定义防止了 agent 在处理复杂任务时发生职责混乱，也让 skill 之间的 `Related Skills` 网络形成有向图而非无结构引用。

---

## 心智模型 (Mental Model)

**这是一套乐高积木系统，`product-marketing-context` 是底板。**

底板（context）定义了所有积木共享的参数：产品是什么、受众是谁、品牌声音是什么。每块积木（skill）有固定的接口协议（YAML frontmatter 的 `description` 字段用于 agent 的 skill 路由、`Related Skills` 字段用于跨 skill 跳转）。Agent 的任务是把正确的积木组合起来，而不是从头捏一个形状。

一旦理解这个模型，所有行为都可以自推导：为什么 `seo-audit` 和 `ai-seo` 要分开？因为它们是面向不同问题的不同积木。为什么每个 skill 都有 `Output Format` 节？因为积木的输出规格要标准化，下游 skill 才能接收。

---

## 为什么这样设计 (Why Designed This Way)

### 1. 为什么用 Markdown 文件而不是系统提示词？
因为 Markdown 文件可以被 agent 按需读取（lazy loading），而系统提示词是全量注入。33 个 skill 如果全部塞进系统提示词，会超出上下文窗口且大部分是噪声。Markdown 文件让 agent 在需要时读取相关 skill，其余时间不占用上下文。这就是为什么安装路径是 `.agents/skills/` 而不是系统配置文件。

**因为 X（skill 数量多、内容长）→ 所以 Y（按需加载比全量注入更经济）→ 这就是为什么 Z（每个 skill 是独立文件，通过 description 字段触发路由）**

### 2. 为什么 `product-marketing-context` 要单独存为文件而非内嵌在每个 skill？
因为产品信息会变化，而 skill 逻辑不变。如果把 ICP 定义写进 `page-cro` skill，下次产品更新就要改 skill 文件。把 context 抽出来存为 `.agents/product-marketing-context.md`，只需要更新一个文件，所有 skill 自动使用新信息。

**因为 X（context 易变、skill 逻辑稳定）→ 所以 Y（分离关注点）→ 这就是为什么 Z（所有 skill 第一步都是 "read context first"，而不是把信息硬编码进 skill）**

### 3. 为什么每个 skill 都有明确的 `Related Skills` 节？
因为营销任务在现实中是跨越的（CRO 依赖 copy，SEO 依赖 site architecture），但 agent 需要明确的跳转指令才能在 skill 之间导航。`Related Skills` 是手动维护的有向图，让 agent 在当前 skill 完成后知道"下一步该用哪个 skill"，而不是让用户再次描述新任务。

**因为 X（营销任务耦合但 skill 解耦）→ 所以 Y（显式声明跨 skill 关系）→ 这就是为什么 Z（`seo-audit` 在 schema 章节标注"use Rich Results Test, not web_fetch"，同时 Related Skills 里指向 `schema-markup`）**

---

## 你一定会踩的坑 (Pitfalls)

### 坑 1：`web_fetch` 检测不到 Schema Markup

你让 agent 做 SEO audit，它用 `web_fetch` 抓页面，然后告诉你"这个页面没有 schema markup"。你信了，准备花时间添加，结果发现 schema 其实早就在了——只是通过 JavaScript 注入的。

`web_fetch` 会剥离 `<script>` 标签，包括 `<script type="application/ld+json">`。而 Yoast、RankMath、AIOSEO 等 WordPress 插件全都是客户端 JS 注入 schema。这个假阴性（false negative）会导致你浪费时间"修复"一个根本不存在的问题。

`seo-audit` skill 专门在"Schema Markup Detection Limitation"章节写了这个警告，并给出了正确方法：用浏览器工具运行 `document.querySelectorAll('script[type="application/ld+json"]')`，或者用 Google Rich Results Test（它会渲染 JavaScript）。

### 坑 2：AI SEO 和关键词堆砌（Keyword Stuffing）

你知道 AI SEO 很重要，于是让 agent 在页面里堆砌关键词来提升 AI 可见性。这个策略在传统 SEO 里是"无效但无害"，在 AI SEO 里是**主动有害**。

Princeton GEO 研究（KDD 2024）通过 Perplexity.ai 的实验数据证明：关键词堆砌让 AI 引用率下降 10%。与此同时，添加数据引用 +40%、添加统计数字 +37%、添加专家引用 +30%。AI 系统更像一个学术评审，而不是一个关键词匹配引擎——它会惩罚明显为了迎合算法而写的内容。

`ai-seo` skill 在 "Common Mistakes" 节明确列出这个坑，并附上了来自实际研究的数字。

### 坑 3：没有先运行 `product-marketing-context` 就直接用其他 skill

你安装了 marketingskills，直接调用 `/page-cro` 让 agent 优化你的落地页。Agent 开始问：你的产品是什么？目标用户是谁？竞争对手有哪些？你一一回答，20 分钟后优化完成。下次你用 `/email-sequence`，又被问了一遍同样的问题。

所有 skill 的设计前提是 `.agents/product-marketing-context.md` 已经存在。没有这个文件，每个 skill 都要重新收集基础信息，这是设计上的"税"。正确的 onboarding 顺序是：先运行 `product-marketing-context` skill 建立基础文件，之后所有 skill 调用都会自动读取它，无需重复输入。

---

## 模块地图 (Module Map)

### Module 1: `product-marketing-context`
**职责**：建立并维护产品定位的单一事实来源，所有其他 skill 的前置读取文件。
**关键文件**：`skills/product-marketing-context/SKILL.md`
**输出文件**：`.agents/product-marketing-context.md`（12 个章节：产品概述、目标用户、人物画像、痛点、竞品、差异化、异议、切换动力、客户语言、品牌声音、证明点、目标）
**接口**：被所有其他 skill 的 "Initial Assessment" 章节读取；自动 fallback 检查 `.claude/product-marketing-context.md`（向后兼容 v1.0）

### Module 2: SEO & Discovery 集群
**职责**：搜索引擎和 AI 引擎的可见性优化，覆盖传统 SEO 到 AI 引用的完整链路。
**关键文件**：
- `skills/seo-audit/SKILL.md`：技术 SEO + 页面 SEO 的诊断框架，优先级：可抓取 → 技术基础 → 页面优化 → 内容质量 → 权威度
- `skills/ai-seo/SKILL.md`：AI 可见性优化，三柱模型（Structure/Authority/Presence），Princeton GEO 研究数据
- `skills/site-architecture/SKILL.md`：页面层级、URL 结构、内部链接，输出 ASCII tree + Mermaid 图
- `skills/programmatic-seo/SKILL.md`：12 种 pSEO playbook（Templates/Curation/Comparisons/Locations/Integrations 等）
- `skills/schema-markup/SKILL.md`：JSON-LD 实现，10 种 schema 类型模板
**依赖**：`seo-audit` ↔ `ai-seo` ↔ `schema-markup` 三角互相引用；`programmatic-seo` → `site-architecture`

### Module 3: Content & Copy 集群
**职责**：内容策略规划到具体文案写作的完整链路。
**关键文件**：
- `skills/content-strategy/SKILL.md`：内容支柱 + topic cluster 框架，优先级评分矩阵（Customer Impact 40% / Content-Market Fit 30% / Search Potential 20% / Resources 10%）
- `skills/copywriting/SKILL.md`：营销页文案
- `skills/copy-editing/SKILL.md`：文案审阅和打磨
- `skills/cold-email/SKILL.md`：B2B 冷邮件序列
- `skills/email-sequence/SKILL.md`：自动化邮件流
- `skills/social-content/SKILL.md`：社交媒体内容
**依赖**：`content-strategy` → `copywriting`；`copywriting` ↔ `page-cro`

### Module 4: CRO 集群
**职责**：按转化漏斗阶段拆分的6个专项 CRO skill，覆盖落地页到 paywall 的完整路径。
**关键文件**：
- `skills/page-cro/SKILL.md`：核心 CRO 框架，7 维度分析顺序（Value Proposition → Headline → CTA → Visual Hierarchy → Trust Signals → Objection Handling → Friction）
- `skills/signup-flow-cro/SKILL.md`：注册流程优化
- `skills/onboarding-cro/SKILL.md`：激活和首次价值实现
- `skills/form-cro/SKILL.md`：非注册表单（lead capture 等）
- `skills/popup-cro/SKILL.md`：弹窗和 overlay
- `skills/paywall-upgrade-cro/SKILL.md`：应用内 paywall 和升级弹窗
**接口**：`page-cro` ↔ `copywriting`；`ab-test-setup` 接收所有 CRO skill 的测试假设

### Module 5: Paid & Measurement 集群
**职责**：付费渠道投放和数据度量。
**关键文件**：
- `skills/paid-ads/SKILL.md`：Google/Meta/LinkedIn 广告投放
- `skills/ad-creative/SKILL.md`：广告素材批量生成
- `skills/analytics-tracking/SKILL.md`：GA4 等事件追踪设置
- `skills/ab-test-setup/SKILL.md`：A/B 实验设计
**接口**：`analytics-tracking` 为所有其他 skill 的度量层；`ab-test-setup` 接受来自 CRO skill 的假设输入

### Module 6: Strategy & GTM 集群
**职责**：产品发布、定价、竞品、销售赋能的战略决策层。
**关键文件**：
- `skills/launch-strategy/SKILL.md`
- `skills/pricing-strategy/SKILL.md`
- `skills/competitor-alternatives/SKILL.md`：竞品对比页（也是 pSEO 的 Comparisons playbook 落地）
- `skills/revops/SKILL.md`：线索生命周期管理
- `skills/sales-enablement/SKILL.md`：销售资料
- `skills/marketing-ideas/SKILL.md`：140 条 SaaS 营销想法
- `skills/marketing-psychology/SKILL.md`：行为科学在营销中的应用

### Module 7: Tools Registry
**职责**：定义 skill 可调用的外部工具，与具体 skill 解耦。
**关键文件**：`tools/REGISTRY.md`
**已注册工具**：`semrush`、`ahrefs`、`gsc`（Google Search Console）、`ga4`
**接口**：skill 文件通过 `[tools registry](../../tools/REGISTRY.md)` 引用，在需要外部工具时查询

---

## 社区智慧 (Community Wisdom)

基于 skill 内部记录的已知问题和最佳实践（这些通常来自真实使用反馈后的修订）：

### 高频痛点

**1. `web_fetch` / `curl` 无法检测 JS 注入的 schema**
根因：这类工具做静态 HTML 解析，而现代 CMS 插件在客户端渲染 schema。`seo-audit` 在专门章节"Schema Markup Detection Limitation"记录了这个陷阱，并提供了三种替代方法。这个章节的存在本身说明它被大量用户踩过。

**2. AI SEO 与传统 SEO 混淆**
根因：用户把提升传统排名的策略（关键词堆砌、大量内链）直接套用到 AI 可见性优化。`ai-seo` skill 专门区分了"get ranked vs. get cited"，并引用了定量研究数据来强化这个区别而不只是断言。

**3. v1.0 → v1.1 迁移：context 文件路径变化**
README 专门列出了升级步骤（从 `.claude/` 迁移到 `.agents/`），所有 skill 都添加了 fallback 逻辑（先查 `.agents/`，再查 `.claude/`）。这是 breaking change 被优雅处理的证据，说明作者有真实用户群且收到了迁移反馈。

### 社区验证的最佳实践

| 实践 | 来源 skill | 备注 |
|------|-----------|------|
| 先建 context 再用其他 skill | `product-marketing-context` | 所有 skill 的设计前提 |
| AI SEO: 数据引用 > 关键词密度 | `ai-seo` | Princeton GEO 研究，+40% 引用率 |
| pSEO: 子目录 > 子域名 | `programmatic-seo` | 权重集中在主域 |
| Schema 验证必用 Rich Results Test | `seo-audit`, `schema-markup` | 而非 web_fetch |
| 内容优先级：Customer Impact(40%) > Search Potential(20%) | `content-strategy` | 防止为 SEO 写没人看的内容 |
| CRO 分析顺序：Value Prop > CTA > Trust > Friction | `page-cro` | 高影响到低影响的优先级 |
| pSEO 内容原则：质量 100 页 > 数量 10000 页 | `programmatic-seo` | 防 thin content 惩罚 |

---

## 速查规则 (Quick Reference)

### Skill 路由决策表

| 用户意图 | 使用 skill | 注意边界 |
|---------|-----------|---------|
| 营销页转化率低 | `page-cro` | 注册流程 → `signup-flow-cro` |
| 激活率/留存差 | `onboarding-cro` | 付费升级 → `paywall-upgrade-cro` |
| SEO 审查 | `seo-audit` | AI 搜索 → `ai-seo` |
| 想出现在 ChatGPT/Perplexity 里 | `ai-seo` | 传统 SEO → `seo-audit` |
| 大规模生成 SEO 页面 | `programmatic-seo` | 单页优化 → `seo-audit` |
| 规划网站页面结构 | `site-architecture` | XML sitemap → `seo-audit` |
| 添加 structured data | `schema-markup` | SEO 审查 → `seo-audit` |
| 规划内容 | `content-strategy` | 写内容 → `copywriting` |
| B2B 冷邮件 | `cold-email` | 自动化邮件序列 → `email-sequence` |
| 设置 analytics | `analytics-tracking` | 设计 A/B 实验 → `ab-test-setup` |

### Skill 文件结构（通用模板）

```
SKILL.md 标准结构：
├── YAML frontmatter（name, description, metadata.version）
├── Initial Assessment（先读 product-marketing-context）
├── 主体框架（决策树/checklist/框架）
├── Output Format（输出规格）
├── Task-Specific Questions（收集上下文的提问清单）
└── Related Skills（有向图中的出边）
```

### 安装路径规范

| 文件类型 | 路径 |
|---------|------|
| Skill 文件 | `.agents/skills/<skill-name>/SKILL.md` |
| Product context | `.agents/product-marketing-context.md` |
| Claude Code 兼容 | `.claude/skills/` (symlink from `.agents/skills/`) |
| Fallback (v1.0) | `.claude/product-marketing-context.md` |
| Tools registry | `tools/REGISTRY.md` |

### AI SEO 核心数字（Princeton GEO 研究）

| 方法 | 可见性提升 |
|------|----------|
| 添加数据引用 | +40% |
| 添加统计数字 | +37% |
| 添加专家引用 | +30% |
| 关键词堆砌 | **-10%** |
| 添加 schema markup | +30-40% |
| Fluency + Statistics 组合 | 最高效组合 |

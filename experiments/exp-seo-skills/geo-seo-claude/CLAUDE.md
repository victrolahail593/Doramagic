# geo-seo-claude — Soul Extraction

> 灵魂提取基于仓库实际代码和文档，所有引用均来自真实文件。

---

## 灵魂 (Soul)

**Q1. 这个项目解决什么问题？**
数字营销人员和代理机构不知道如何让网站被 ChatGPT、Perplexity、Claude 等 AI 搜索引擎引用，而传统 SEO 工具只优化 Google，对 AI 搜索完全失效。

**Q2. 没有这个项目，人们怎么办？**
要么手工逐一检查 robots.txt、schema、llms.txt、品牌提及，要么花钱买企业级 GEO 工具（$2K–$12K/月），要么完全忽视 AI 搜索这个渠道——而 Gartner 预测 2028 年传统搜索流量将下降 50%。

**Q3. 它的核心承诺是什么？**
一个命令，全面诊断网站对所有主流 AI 搜索引擎（ChatGPT、Perplexity、Claude、Google AI Overviews、Bing Copilot）的可见性，并给出可执行的优先级行动清单。

**Q4. 它如何兑现这个承诺？**
通过 5 个并行子代理（AI 可见性 / 平台优化 / 技术 SEO / 内容质量 / Schema 结构化数据）同时分析目标网站，各自评分后合并为一个 0-100 的综合 GEO 分数，并输出客户级报告。

**Q5. 一句话总结：**
geo-seo-claude 让营销人员用一条 `/geo audit <url>` 命令，无需懂 AI 搜索技术，就能获得完整的 GEO 可见性诊断和行动计划。

**Q6. 设计哲学：**
AI 搜索与传统搜索在根本逻辑上是不同的游戏：传统搜索看链接权威，AI 搜索看"可被引用性"——内容是否能被 LLM 原文摘录作为答案。这个项目的设计核心信念是：**品牌在开放互联网上的存在面（Brand Surface Area）决定 AI 可见性，而不是 PageRank**。Ahrefs 2025 年对 75,000 个品牌的研究证实，品牌提及与 AI 引用的相关性（~0.737）是反向链接（~0.266）的 3 倍。因此，工具权重分配上，AI 可引用性（25%）+ 品牌权威信号（20%）占了接近一半，而传统 SEO 技术指标（15%）退居次要。

**Q7. 心智模型：**
把 AI 搜索引擎理解为一个极度挑剔的引用机器：它只引用"可以直接复制粘贴进答案"的段落。优化 GEO 的本质是把你的内容从"参考读物"改造成"引用片段工厂"——每个段落都要能独立站立、自我解释、包含可量化的事实。

---

## 设计哲学 (Design Philosophy)

传统 SEO 工具建立在"被 Google 爬虫索引 → 排名靠前 → 获得点击"这条链路上。但 AI 搜索引擎绕过了这条链路——它不给你点击，它直接回答用户问题，偶尔引用来源。

这个项目的创作者做出了一个根本性的认知转变：**优化的对象不是算法，是内容的"可引用密度"**。AI 搜索系统（ChatGPT、Perplexity）偏好的内容具有明确的特征——`citability_scorer.py` 中直接编码了这套标准：134-167 词的段落长度、低代词密度（<2% 代词占比）、答案在前 60 词内出现、包含具体统计数字。这些不是经验法则，是从 AI 引用行为反推出的工程规格。

项目同时意识到，不同 AI 平台的引用来源逻辑不同：ChatGPT 依赖 Bing 索引 + Wikipedia 实体识别；Perplexity 极度依赖 Reddit 等社区验证；Google AIO 依赖已有 Google 排名的页面。因此，`geo-platform-analysis.md` 对 5 个平台分别评分，而不是假设"优化一个就等于优化所有"——实际数据显示只有 11% 的域名同时被 ChatGPT 和 Google AIO 为相同查询引用。

---

## 心智模型 (Mental Model)

把每个网页想象成一个"证人出庭"：法官（AI 搜索引擎）问一个问题，证人（你的页面）必须用一句完整、独立、有依据的话直接回答，法官才会引用你的证词。证人说"嗯，就像我在第三章说的那样……"——会被立刻打断。

理解了这个模型，所有 GEO 优化行为都自然推导出来：段落必须独立（低代词）、答案必须在最前面（Answer Block Quality）、必须有数字（Statistical Density）、页面在多个权威平台上被提及（Brand Surface Area）。

---

## 为什么这样设计 (Why Designed This Way)

**设计决策一：5 个并行子代理，而非单一分析管线**

因为 GEO 的五个维度（AI 可见性、平台适配、技术、内容、Schema）彼此高度独立，数据来源不同，执行时间也不同 → 所以采用并行 subagent 架构（`agents/` 目录下 5 个独立 `.md` 文件）→ 这就是为什么一次 `/geo audit` 能在合理时间内完成全面分析，而不需要用户串行等待每个检查项。

**设计决策二：品牌提及分数权重高于结构化数据（20% vs 10%）**

因为 Ahrefs 对 75,000 个品牌的研究发现，YouTube 品牌提及与 AI 引用相关性高达 0.737，而域名权重（反向链接）相关性仅 0.266 → 所以 `brand_scanner.py` 把 YouTube、Reddit、Wikipedia、LinkedIn 都纳入扫描，而不只是检查 backlinks → 这就是为什么传统 SEO 工具的指标体系在 GEO 工具里是"次级"指标，而非核心。

**设计决策三：SSR（服务端渲染）检查权重最高（25%）**

因为 GPTBot、ClaudeBot、PerplexityBot 等 AI 爬虫通常不执行 JavaScript → 所以纯 CSR（客户端渲染）页面对 AI 爬虫来说内容是空的 → 这就是为什么 `geo-technical.md` 把 SSR 检查的权重设为所有技术指标中最高（25%），超过 Meta 标签（15%）和安全标头（10%）的总和。这个权重不是主观偏好，是 AI 爬虫架构决定的硬约束。

---

## 你一定会踩的坑 (Pitfalls)

**坑一：以为封锁了 GPTBot 就安全了，结果把所有 AI 流量都切断了**

某 SaaS 公司的技术团队在 robots.txt 里加了 `Disallow: /` 针对 GPTBot（他们认为只是防止被 OpenAI 抓取训练数据）。结果他们不知道 OAI-SearchBot（OpenAI 的搜索爬虫）和 GPTBot 是独立的——前者负责 ChatGPT 搜索功能，后者负责模型训练。`geo-ai-visibility.md` 里明确区分了这两个爬虫的不同职能：GPTBot 是训练爬虫，OAI-SearchBot 才是搜索爬虫。封锁 GPTBot 不会影响 ChatGPT 搜索引用，但很多网站主不知道这个区别，乱封锁后发现产品在 ChatGPT 里完全消失。`geo-crawlers` 技能追踪 14+ 个 AI 爬虫，正是因为这个区分至关重要。

**坑二：FAQPage schema 没有任何 rich result 效果却不知道为什么**

一个内容站辛苦实现了 FAQPage schema，在搜索控制台里验证也通过了，却发现搜索结果从未出现 FAQ 展开框。原因是 Google 在 2023 年 8 月限制了 FAQPage rich result，现在只有"知名政府和健康权威机构"才能展示。`geo-schema.md` 明确标注了这个状态变更，并指出：FAQPage schema 本身不有害（对 AI 模型理解 Q&A 结构还有语义价值），但继续投入时间把它加到所有页面是浪费——应该优先实现 Organization+sameAs 和 Article+speakable。很多工程师查到"FAQPage is supported"的旧文档就去做，结果白费功夫。

**坑三：Schema 部署在 React/Next.js 客户端，AI 爬虫完全看不到**

一个电商平台用 React 动态注入 JSON-LD（用 `react-helmet` 在客户端插入 `<script type="application/ld+json">`）。Schema 验证工具（Google Rich Results Test）显示正常，因为 Google 会渲染 JavaScript。但 GPTBot、ClaudeBot、PerplexityBot 不执行 JS，它们看到的是空的初始 HTML，Product schema 完全不存在。`geo-schema.md` 专门有一节"JavaScript Rendering Risk"（来自 Google 2025 年 12 月的指引），要求检查 schema 是在初始 HTML 中还是 JS 注入——这是 GEO 审计的强制检查项，但大多数 SEO 工具的 schema 验证器不检测这一点。

---

## 模块地图 (Module Map)

**模块一：geo/SKILL.md — 主编排器**
- 职责：解析用户命令（`/geo audit`、`/geo quick` 等），决定调用哪些子技能和子代理，聚合结果生成综合 GEO 分数
- 关键文件：`geo/SKILL.md`
- 依赖：所有 5 个 subagents + 10 个 skills
- 评分权重：AI 可引用性 25% / 品牌权威 20% / 内容质量 20% / 技术基础 15% / 结构化数据 10% / 平台优化 10%

**模块二：agents/ — 5 个并行分析子代理**
- 职责：并行执行不同维度的网站分析，各自产生独立报告段落
- 关键文件：`agents/geo-ai-visibility.md`（citability + crawlers + llms.txt + brand mentions）、`agents/geo-platform-analysis.md`（ChatGPT/Perplexity/Google AIO/Gemini/Bing）、`agents/geo-technical.md`、`agents/geo-content.md`、`agents/geo-schema.md`
- 接口：每个 agent 都输出固定格式的 markdown 报告段落，由主 SKILL 聚合

**模块三：scripts/citability_scorer.py — AI 可引用性评分引擎**
- 职责：解析页面 HTML，提取内容块，对每个段落按 5 个维度评分（Answer Block Quality 30% / Self-Containment 25% / Structural Readability 20% / Statistical Density 15% / Uniqueness 10%）
- 关键文件：`scripts/citability_scorer.py`
- 核心逻辑：最优段落长度 134-167 词；代词密度 < 2% 为最高分；答案在前 60 词内出现有加分；正则检测数字、百分比、美元金额密度
- 依赖：`requests`、`beautifulsoup4`、`lxml`

**模块四：scripts/brand_scanner.py — 品牌存在面扫描器**
- 职责：检测品牌在 YouTube、Reddit、Wikipedia、LinkedIn 及 7+ 平台的存在状态，返回品牌提及报告
- 关键文件：`scripts/brand_scanner.py`
- 核心数据：YouTube 相关性系数 0.737（最强）；Wikipedia 权重 20%；Wikidata API 直接调用验证实体存在
- 接口：输出 JSON，各平台状态 + 推荐行动

**模块五：scripts/fetch_page.py — 统一页面抓取层**
- 职责：HTTP 抓取 + HTML 解析 + robots.txt 解析 + llms.txt 检查 + sitemap 爬取 + SSR 检测
- 关键文件：`scripts/fetch_page.py`
- SSR 检测逻辑：检查 `#root`、`#app`、`#__next`、`#__nuxt` 等容器的内部文本长度——小于 50 字符则标记为纯 CSR
- AI 爬虫 UA 定义：内置 GPTBot、ClaudeBot、PerplexityBot 等 user-agent 字符串供测试用

**模块六：schema/ — JSON-LD 模板库**
- 职责：提供 6 种业务类型的可直接使用 JSON-LD 模板，填充占位符后可立即部署
- 关键文件：`schema/organization.json`（含 9 个 sameAs 链接槽位）、`schema/article-author.json`（含 speakable 属性）、`schema/software-saas.json`、`schema/product-ecommerce.json`、`schema/local-business.json`、`schema/website-searchaction.json`
- 设计亮点：organization.json 预置了 Wikipedia + Wikidata + LinkedIn + YouTube + Crunchbase + GitHub 的 sameAs 槽位，强制提醒用户完成跨平台实体链接

**模块七：scripts/generate_pdf_report.py — PDF 报告生成器**
- 职责：将审计 JSON 数据渲染为带评分仪表盘、彩色图表的专业客户报告 PDF
- 关键文件：`scripts/generate_pdf_report.py`
- 依赖：`reportlab>=4.4.0`、`Pillow`
- 用途：面向 GEO 代理机构的客户交付物，支撑 $2K–$12K/月的服务定价

---

## 社区智慧 (Community Wisdom)

基于仓库代码和文档中编码的行业研究发现（Ahrefs、Gartner、SparkToro、Google 官方指引）：

**高价值洞察：**
- **品牌提及 > 反向链接**：Ahrefs 2025 年 12 月对 75,000 个品牌研究，YouTube 品牌提及相关性 0.737，Domain Rating 相关性仅 0.266。GEO 代理机构应把"内容营销预算"从 guest post 转移到 YouTube 频道建设。
- **只有 11% 的域名同时被 ChatGPT 和 Google AIO 引用**：各平台引用来源逻辑独立，不能假设"Google 排名好 = AI 也会引用"。每个平台需要独立优化策略。
- **AI 引用流量质量是有机流量的 4.4 倍**：转化率远高于普通搜索流量，但目前只有 23% 的营销人员在投资 GEO。
- **CSR 页面对 AI 爬虫是透明的**：React SPA 如果没有 SSR/SSG，AI 爬虫看到的是空 HTML。这是目前行业中被忽视最严重的技术债。

**反复出现的痛点：**
- **llms.txt 几乎没人实现**：这个新兴标准帮助 AI 爬虫理解站点结构，但当前实现率极低，是"低成本高回报"的快速赢得机会。
- **speakable 属性被极度低估**：直接告诉 AI 助手哪些内容适合被语音读出/引用，`article-author.json` 模板中预置了 `cssSelector: [".article-summary", ".key-takeaway", "h2"]`，但几乎没有网站实现。
- **Wikipedia 实体页面是单一最强 AI 引用信号**：ChatGPT、Gemini、Perplexity 都优先引用有 Wikipedia 页面的实体。但大多数中小品牌不知道如何"建立通知性"（notability）——需要先积累独立第三方媒体报道，再创建 Wikipedia 词条。

**社区验证的最佳实践：**
- 优先确保主要 AI 爬虫在 robots.txt 中的状态（GPTBot vs OAI-SearchBot 必须区别对待）
- Organization schema 的 sameAs 属性需要链接到 9 个以上平台才算"完整"（Wikipedia + Wikidata + LinkedIn + YouTube + Crunchbase + Twitter + Facebook + GitHub + Google Maps）
- 内容块长度 134-167 词是 AI 引用的甜蜜区间——短了不够独立，长了不够精炼
- Reddit 的可信度来自"authentic participation"（真实参与），营销语言会被社区识别并反噬

---

## 速查规则 (Quick Reference)

| 类别 | 关键规则 | 来源文件 |
|------|---------|---------|
| GEO 综合评分 | AI 可引用性 25% + 品牌权威 20% + 内容质量 20% + 技术 15% + Schema 10% + 平台 10% | `geo/SKILL.md` |
| 最优段落长度 | 134-167 词（AI 引用甜蜜区间） | `scripts/citability_scorer.py` |
| 代词密度阈值 | <2% 为最高分，>6% 为惩罚区间 | `scripts/citability_scorer.py` |
| AI 爬虫追踪数量 | 14+ 个（GPTBot ≠ OAI-SearchBot，区别对待） | `scripts/fetch_page.py`, `agents/geo-ai-visibility.md` |
| SSR 检测阈值 | app root 内部文本 < 50 字符 = CSR 警告 | `scripts/fetch_page.py` |
| 品牌提及相关性 | YouTube 0.737，Domain Rating 0.266（Ahrefs 2025） | `scripts/brand_scanner.py` |
| Wikipedia 权重 | 品牌提及分 30 分中的 30 分（最大单项） | `agents/geo-ai-visibility.md` |
| FAQPage schema 状态 | 2023 年 8 月后仅对政府/健康权威机构生效 | `agents/geo-schema.md` |
| HowTo schema 状态 | 2023 年 9 月起彻底移除 rich result 支持 | `agents/geo-schema.md` |
| JS 注入 schema 风险 | AI 爬虫不执行 JS，JS 注入的 schema 对 AI 不可见 | `agents/geo-schema.md` |
| llms.txt 评分 | 缺失=0，存在且格式正确=50-70，含 llms-full.txt=90-100 | `agents/geo-ai-visibility.md` |
| 平台隔离度 | 仅 11% 域名同时被 ChatGPT 和 Google AIO 引用 | `geo/SKILL.md` |
| sameAs 最低要求 | 3+ 平台得 10 分，5+ 含 Wikipedia 得满分 15 分 | `agents/geo-schema.md` |
| 爬取限制 | 每次审计最多 50 页，请求间隔 1 秒，最多 5 并发 | `geo/SKILL.md` |

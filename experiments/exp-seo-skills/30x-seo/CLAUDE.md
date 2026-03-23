# 30x-seo — Soul Extraction

## 灵魂 (Soul)

**Q1. 这个项目解决什么问题？**
SEO 从业者和网站所有者需要用十几个不同工具才能完成一次完整的 SEO 审计，30x-seo 让他们在 Claude Code 内用一条命令调度 24 个专项技能，完成从技术审计到内容质量、从 Schema 生成到 AI 搜索可见性的全链路分析。

**Q2. 没有这个项目，人们会怎么做？**
手动切换 Screaming Frog、Ahrefs、Google Search Console、PageSpeed Insights、Rich Results Test 等工具，在不同界面之间复制粘贴数据，输出碎片化报告——一次完整审计要耗费半天人工时间，且知识全靠个人记忆，不可复现。

**Q3. 核心承诺是什么？**
一条 `/seo audit <url>` 命令，完成以往需要 6 个专家工具才能覆盖的 SEO 全栈分析，并输出带优先级的行动计划。

**Q4. 它如何兑现这个承诺？**
主编排器（`seo/SKILL.md`）识别业务类型后，将任务并行分发给 6 个专项子代理（技术、内容、Schema、Sitemap、性能、视觉），各自独立分析后汇总成统一的 SEO 健康评分（0-100）。

**Q5. 一句话概括**
30x-seo 让 SEO 工程师和内容团队在 Claude Code 里做全栈 SEO 分析，不再需要在十几个工具之间来回切换。

**Q6. 设计哲学**
SEO 知识本质上是规则集合，但规则随 Google 算法更新而频繁失效——今天推荐的 schema type 明天可能被废弃，今天的 FID 指标明年就被 INP 替代。这个项目的核心信念是：**将这些易腐的知识编码进工具本身，而不是依赖使用者的记忆**。所有过时信息（HowTo schema、FID、SpecialAnnouncement）直接在代码层面被拦截；质量门槛（30/50 个 location page 的硬停止）内建于流程而非靠人工判断。这是一个自带护栏的 SEO 专家，而不是一个搜索功能。

**Q7. 心智模型**
把 30x-seo 理解为一支 SEO 咨询团队，每人专攻一个领域（技术、内容、Schema……），团队负责人（主编排器）接到需求后同时派遣所有人并行工作，30 分钟后汇总报告——而不是一个通才顾问串行处理所有环节。技能文件就是每个顾问的"工作手册"，里面不光有方法，还有"绝对不能做的事"清单。

---

## 设计哲学 (Design Philosophy)

这个项目有一个反直觉的选择：它把大量精力花在**禁止**某些事情上，而不只是**允许**某些事情。

主 SKILL.md 里有硬性规则：`Never recommend HowTo schema`、`FAQ schema only for government and healthcare sites`、`All Core Web Vitals references use INP, never FID`。`validate-schema.py` hook 在任何 Edit/Write 操作后自动运行，检测到废弃 schema type 就返回 exit code 2 阻断操作。`pre-commit-seo-check.sh` 在 commit 前扫描 placeholder 文本和过时指标引用。

这背后的逻辑是：SEO 领域最大的风险不是"不知道最佳实践"，而是"以为自己在用最佳实践，其实在用已废弃的做法"。一个 2021 年写的 SEO 代码库到 2026 年可能充满了错误指导。所以 30x-seo 选择把知识的有效期管理内建到工具层面——deprecation 信息和知识一起打包，永远同步更新。

另一个关键设计是**Progressive Disclosure（渐进式揭示）**：主 SKILL.md 保持在 200 行以内，详细的 E-E-A-T 框架、CWV 阈值、schema 类型列表都在独立的 `references/` 文件里，按需加载，避免在不需要细节时污染上下文窗口。

---

## 心智模型 (Mental Model)

把每个 `SKILL.md` 文件理解为一个"能上岗的专科医生"，而不是"知识库文档"。医生不只是知道知识，还知道什么情况下绝对不能开某种药（deprecated schema types）、什么情况下要强制转诊（质量门槛触发时让用户先解释清楚）。主编排器是接诊台，负责分诊，而不是自己看病。整个系统的价值不在于知识总量，而在于**知识的可靠性**——你可以信任它给出的建议不会让你的网站受罚。

---

## 为什么这样设计 (Why Designed This Way)

### 1. 并行子代理而非串行分析

因为一次完整的 SEO 审计涉及 6 个完全独立的分析维度（技术/内容/Schema/Sitemap/性能/视觉），它们之间没有数据依赖关系 → 所以设计为同时派遣 6 个子代理并行执行 → 这就是为什么 `/seo audit` 的 `docs/ARCHITECTURE.md` 里画的是一个扇形分发图，而不是线性流程图。串行执行会让审计时间变成 6 倍，而 Claude Code 的子代理模型天然支持并发。

### 2. 质量门槛硬编码而非软提示

因为 location page 滥用（只换城市名的批量页面）是 Google doorway page 算法的典型打击目标，光靠文字提示"建议保持 60% 独特内容"很容易被忽略 → 所以在 `seo-sitemap` 子代理和 `quality-gates.md` 里设置了两档硬停止（30 页警告、50 页强制要求用户解释）→ 这就是为什么系统会主动"拦路"而不只是"建议"——因为在这个具体场景里，被拦住的成本（多解释几句）远低于继续执行的风险（被 Google 惩罚）。

### 3. Schema 验证作为 Post-Edit Hook 而非建议

因为 schema 错误（使用废弃 type、包含 placeholder 文本）直接影响 rich results 的获取，且错误往往在写入文件时就已经发生，等到审计时才发现已经是事后追责 → 所以 `validate-schema.py` 注册为 PostToolUse hook，在每次 Edit/Write 后立即运行，检测到严重错误返回 exit code 2 阻断 → 这就是为什么这个项目选择"在错误发生的时间点"拦截，而不是"在汇报的时间点"告知——因为预防比诊断便宜得多。

---

## 你一定会踩的坑 (Pitfalls)

### 坑 1：以为 squirrelscan 是可选的，跳过直接看子代理报告

新用户做完 `/seo audit` 后发现报告很详细，但整体健康分数感觉"来路不明"。原因是他们没安装 squirrelscan，直接跳到了 Step 4（子代理分析），而主编排器的 `SKILL.md` 里写的是 **Step 1 是阻塞的（BLOCKING）**——如果 squirrelscan 没安装，要先告知用户 `npm i -g squirrelscan`，然后再继续。没有 squirrelscan 给出的 0-100 全站分数，后续 6 个子代理的分析结果缺乏统一的参照系，Critical/High/Medium/Low 的优先级排序就变得不可靠。解决方案：先 `npm i -g squirrelscan`，再跑 audit。

### 坑 2：用 FID 指标引用旧优化文章，被 pre-commit hook 拦住

开发者把从 2023 年的技术博客里复制来的性能建议写进 HTML 注释或文档里，提交时被 `pre-commit-seo-check.sh` 拦截：`References FID — should use INP`。这个 hook 会扫描所有 staged 的 HTML/JSX/TSX/Vue/Svelte/PHP 文件，只要出现 `First Input Delay` 或 `"FID"` 字符串就触发警告。FID 已于 2024 年 3 月 12 日被 INP 完全替换，并于 2024 年 9 月 9 日从 Chrome 所有工具中移除。解决方案：全局替换为 `INP (Interaction to Next Paint)，目标 ≤200ms`。

### 坑 3：为商业网站添加 FAQPage schema，觉得这是"标准做法"

很多 SEO 从业者的肌肉记忆是"FAQ 页面就加 FAQPage schema"——因为这在 2022 年确实是最佳实践，会带来 rich results。但自 2023 年 8 月起，FAQ rich results **仅对政府和医疗权威网站开放**。`validate-schema.py` 会检测到 FAQPage type 并输出警告：`@type 'FAQPage' is restricted to government and healthcare sites only`。为商业 SaaS 或电商网站加这个 schema 不会带来 rich results，只是徒增无效代码。解决方案：商业网站移除 FAQPage schema，改用 Organization + Article 组合。

---

## 模块地图 (Module Map)

### 1. 主编排器 `seo/SKILL.md`
**职责**：命令路由、业务类型自动检测、审计流程编排（squirrelscan → 行业检测 → 并行子代理 → 汇总报告）
**关键文件**：`seo/SKILL.md`
**接口**：接收所有 `/seo *` 命令，路由到对应子技能；向 6 个子代理发出并行任务；输出统一 SEO 健康评分
**依赖**：WebFetch（页面抓取）、squirrelscan CLI（可选）

### 2. 专项子技能层 `skills/30x-seo-*/SKILL.md`（24 个）
**职责**：每个子技能封装一个 SEO 专项领域的完整知识和执行逻辑
**关键文件**：`skills/30x-seo-technical/`、`skills/30x-seo-content-audit/`、`skills/30x-seo-schema/`、`skills/30x-seo-sitemap/`、`skills/30x-seo-hreflang/`、`skills/30x-seo-geo-technical/` 等
**接口**：主编排器路由后直接加载；部分子技能之间有交叉引用（如 `seo-technical` 委托给 `seo-hreflang` 做详细 hreflang 验证）
**依赖**：WebFetch、DataForSEO API（4 个技能需要）、Google Search Console（1 个技能需要）

### 3. 并行子代理 `agents/seo-*.md`（6 个）
**职责**：在 `/seo audit` 时被主编排器并行派遣，独立分析各自专项后回传结果
**关键文件**：`agents/seo-technical.md`、`agents/seo-content.md`、`agents/seo-schema.md`、`agents/seo-sitemap.md`、`agents/seo-performance.md`、`agents/seo-visual.md`
**接口**：每个子代理有独立的工具权限声明（YAML frontmatter 中的 `tools`）；`seo-visual` 使用 Playwright，其余使用 WebFetch/Read
**依赖**：相互独立，无依赖关系

### 4. 知识参考层 `seo/references/`
**职责**：存储高密度、易过时的 SEO 知识（CWV 阈值、E-E-A-T 框架、Schema 类型状态、质量门槛），按需加载避免污染主上下文
**关键文件**：`seo/references/cwv-thresholds.md`、`seo/references/eeat-framework.md`、`seo/references/schema-types.md`、`seo/references/quality-gates.md`
**接口**：子技能或子代理需要详细数据时显式加载；主 SKILL.md 保持精简（<200 行）
**依赖**：无运行时依赖，纯静态知识

### 5. 自动化钩子层 `hooks/`
**职责**：在 Claude Code 工具调用前后自动触发质量检查，防止写入错误 SEO 代码
**关键文件**：`hooks/validate-schema.py`（PostToolUse: Edit/Write 后验证 JSON-LD）、`hooks/pre-commit-seo-check.sh`（PreToolUse: Bash 调用时检查 staged 文件）
**接口**：通过 `~/.claude/settings.json` 注册为 Claude Code hooks；`validate-schema.py` 返回 exit code 2 阻断操作，exit code 1 为警告
**依赖**：Python 标准库（json、re、sys）

### 6. Python 工具脚本 `scripts/`
**职责**：执行具体的网络操作和数据提取，为子代理提供可复用的基础能力
**关键文件**：`scripts/fetch_page.py`（SSRF 防护 + 重定向追踪）、`scripts/parse_html.py`（SEO 元素提取）、`scripts/capture_screenshot.py`（多视口截图）、`scripts/analyze_visual.py`（above-fold 分析）
**接口**：命令行调用，支持 JSON 输出（`--json` 参数）；`fetch_page.py` 和 `analyze_visual.py` 均有私有 IP 阻断（SSRF 防护）
**依赖**：beautifulsoup4、requests、lxml、playwright（可选）、Pillow、urllib3、validators

---

## 社区智慧 (Community Wisdom)

### 反复出现的痛点

**痛点 1：依赖安装地狱**
CHANGELOG v1.2.0 记录了大量安装相关修复：移除 `--break-system-packages`、改为 venv-based 安装、requirements.txt 在安装后持久化到技能目录。这说明早期版本用户在 `pip install` 后仍然遇到 `ModuleNotFoundError`，因为 requirements.txt 没有被复制到正确位置。社区验证的解决方案：使用 `pip install --user -r requirements.txt`，或切换到 venv。

**痛点 2：YAML frontmatter 解析失败导致技能不被识别**
v1.2.0 修复了 8 个文件的 YAML frontmatter 解析问题——这些文件在 `---` 分隔符之前有 HTML 注释，导致 Claude Code 的技能发现机制无法正确解析。症状是 `/seo` 命令被识别，但某些子命令显示"Skill not found"。根本原因是 YAML 前必须是文件的第一行 `---`，任何前缀内容都会导致解析失败。

**痛点 3：Schema hook 误报（假阳性）**
开发者在使用 `validate-schema.py` hook 时遇到误报，原因是 JSON-LD 中包含了合法的描述性文字但碰巧包含了 placeholder 检测词（如描述中写"Replace the old system"被误判为 placeholder）。`validate-schema.py` 的检测逻辑是字符串包含匹配（大小写不敏感），而非精确匹配，导致边界情况误判。暂时解决方案：直接运行 `python3 hooks/validate-schema.py test.html` 调试，在 Google Rich Results Test 上最终验证。

### 社区验证的最佳实践

- **DataForSEO 认证文件权限必须是 600**：`chmod 600 ~/.config/dataforseo/auth`。权限过宽会导致某些系统的安全检查拒绝读取。
- **Playwright 是可选的**：`seo-visual` 子代理在 Playwright 不可用时会回退到 WebFetch，视觉分析精度降低但不会报错。生产环境建议安装，开发调试时可以跳过。
- **field data 优于 lab data**：`cwv-thresholds.md` 明确指出 Google 用于排名的是 CrUX 字段数据（真实用户的 75th percentile），而非 Lighthouse 的模拟数据。从 CrUX Vis（替代了已废弃的 Looker Studio CrUX Dashboard）获取数据才是正确参照系。
- **SPA 的 CWV 盲区**：使用 React/Vue/Angular/Svelte 的单页应用目前在 CWV 测量上有已知盲区——Soft Navigations API 仍在 Chrome 139 的 Origin Trial 阶段（2025 年 7 月），尚无排名影响。审计 SPA 时应在报告中明确标注这个限制。

---

## 速查规则 (Quick Reference)

### Schema 状态速查

| Schema Type | 状态 | 备注 |
|-------------|------|------|
| HowTo | 已废弃 | 2023 年 9 月 rich results 移除 |
| FAQPage | 受限 | 仅限政府和医疗权威网站 |
| SpecialAnnouncement | 已废弃 | 2025 年 7 月 31 日 |
| CourseInfo / EstimatedSalary / LearningVideo | 已退役 | 2025 年 6 月 |
| ClaimReview / VehicleListing | 已退役 | 2025 年 6 月 |
| Article / Organization / Product / Service | 推荐使用 | 无限制 |
| WebApplication | 推荐用于 SaaS | 替代 SoftwareApplication（用于桌面/移动 app）|
| ProfilePage | 推荐 | 2025 新增，强化 E-E-A-T 作者信号 |

### Core Web Vitals 速查（2026）

| 指标 | 好 | 需改进 | 差 |
|------|-----|-------|-----|
| LCP | ≤2.5s | 2.5-4.0s | >4.0s |
| INP（替代 FID） | ≤200ms | 200-500ms | >500ms |
| CLS | ≤0.1 | 0.1-0.25 | >0.25 |

> FID 已于 2024 年 3 月 12 日被 INP 替换，2024 年 9 月 9 日从所有 Chrome 工具中完全移除。任何引用 FID 的内容均已过时。

### Location Page 质量门槛

| 页面数量 | 动作 |
|---------|------|
| <30 页 | 正常，建议 40%+ 独特内容 |
| 30-49 页 | 警告，强制 60%+ 独特内容 |
| 50+ 页 | 硬停止，要求用户提供明确理由 |

### SEO 健康评分权重

| 类别 | 权重 |
|------|------|
| 技术 SEO | 25% |
| 内容质量（E-E-A-T）| 25% |
| 页面 SEO | 20% |
| Schema / 结构化数据 | 10% |
| 性能（CWV）| 10% |
| 图片优化 | 5% |
| AI 搜索可见性 | 5% |

### E-E-A-T 权重（2026 年 12 月核心更新后）

| 维度 | 权重 | 关键变化 |
|------|------|---------|
| 可信度（Trustworthiness）| 30% | 最重要，评估其他三项 |
| 专业度（Expertise）| 25% | 匿名作者现在对非 YMYL 内容也有惩罚 |
| 权威性（Authoritativeness）| 25% | 外部引用和行业认可 |
| 经验（Experience）| 20% | 成为关键差异化因素（AI 无法伪造第一手经验）|

> 2025 年 12 月核心更新：E-E-A-T 现在适用于**所有竞争性查询**，不再局限于 YMYL 类别。

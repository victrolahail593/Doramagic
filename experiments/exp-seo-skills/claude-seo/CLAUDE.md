# claude-seo — Soul Extraction

> 项目地址: https://github.com/AgriciDaniel/claude-seo
> 版本: v1.4.0 (2026-03-12)
> 提取日期: 2026-03-15

---

## 灵魂 (Soul)

**Q1. 这个项目解决了什么问题？**
专业 SEO 工程师和开发者每次分析网站都要在十几个工具之间来回切换（Lighthouse、Search Console、Rich Results Test、PageSpeed、schema validators……），而 Claude Code 本身没有 SEO 领域知识，claude-seo 就是把完整 SEO 工作流打包成一个 Claude Code skill，让 AI 直接执行全链路分析。

**Q2. 没有这个项目，人们会怎么做？**
手动跑 Lighthouse、复制粘贴 HTML 到在线 schema 验证器、打开 PageSpeed Insights 网页、用电子表格汇总结果——每次审计至少花 2-3 小时，还需要持续追踪 Google 每季度一次的规则变更（FID→INP 替换、HowTo schema 下架、FAQ 限制、E-E-A-T 从 YMYL 扩展到全域……）。

**Q3. 核心承诺是什么？**
一条命令，7 个 subagent 并行执行，输出覆盖 9 个维度（可抓取性、可索引性、安全性、URL 结构、移动优化、Core Web Vitals、结构化数据、JS 渲染、IndexNow）的完整 SEO 健康报告。

**Q4. 如何实现这个承诺？核心机制是什么？**
主 orchestrator skill（`seo/SKILL.md`）接收命令后，按需路由到 12 个子技能或同时派生 7 个并行 subagent，每个 subagent 独立完成专项分析后汇总；Python 脚本（`fetch_page.py`、`parse_html.py`、`analyze_visual.py`、`capture_screenshot.py`）提供确定性的数据采集骨架，AI 在此之上做解读与建议。

**Q5. 一句话概括**
claude-seo 让 SEO 工程师用一条斜杠命令完成完整网站审计，而不需要在十几个在线工具之间手动切换和汇总。

**Q6. 设计哲学（创造者视角）**
SEO 知识衰减极快——Google 平均每季度重大变更一次，而大多数 SEO 工具的知识库永远落后半年。这个项目的核心信念是：**把当前规则编码进 skill 的指令层，而不是让 AI 自己"记住"规则**。每一个规则——FID 已死、HowTo schema 已废弃、FAQ 仅限政府和医疗、INP 的 200ms 阈值、75th percentile 作为评估标准——都明文写在对应 SKILL.md 或 reference 文件里，AI 只做推理和文本生成，不依赖训练数据里的 SEO 知识。这就是为什么 reference 文件是按需加载的独立文件，而不是嵌入主 skill：规则会变，结构不变。

**Q7. 心智模型**
把 claude-seo 理解为"一个随时更新的 SEO 法规手册 + 一支并行工作的 7 人专家团队"：法规手册（reference 文件）告诉专家们什么可以做、什么不能做；7 个专家同时开工，各管一个维度，最后汇总报告——而你只需要说"去查一下这个网站"。

---

## 设计哲学 (Design Philosophy)

claude-seo 的根本信念：**SEO 规则是事实，AI 做推理；规则的变化频率要求规则必须与执行逻辑解耦**。

这不是一个"让 Claude 用通识知识做 SEO"的工具。它是一个精心维护的规则系统——每条规则都有来源（Google 官方、QRG 日期、CVE 编号），每条规则都写在可独立更新的文件里。核心 SKILL.md 不超过 500 行，reference 文件不超过 200 行，Python 脚本必须输出 JSON——这三个约束共同保证了"规则更新不影响执行结构"。

当 Google 2024 年 3 月把 FID 换成 INP，当 HowTo schema 2023 年 9 月被下架，当 FAQ schema 2023 年 8 月被限制到政府和医疗，当 E-E-A-T 2025 年 12 月从 YMYL 扩展到所有竞争性查询——这些变化只需要更新一个 reference 文件或一条 SKILL.md 规则，不需要重新训练模型。

架构的另一个核心信念：**并行是正确的默认值**。7 个 subagent 同时分析不同维度，因为 SEO 的各个维度之间没有强依赖，串行等待只是浪费时间。这个选择反映了"分析维度独立性"这个领域事实，而不是工程上的过度设计。

---

## 心智模型 (Mental Model)

把 `/seo audit` 理解为：你雇了一支 7 人专家小组，给了他们一本随时更新的 Google 规则手册，让他们同时各自审查网站的一个维度，30 分钟后汇总报告给你。

推论：如果你只需要某一个维度，直接叫那个专家就行（`/seo technical`、`/seo schema`……）；如果 Google 更新了规则，你只需要更新手册里那一页，不需要换人。

---

## 为什么这样设计 (Why Designed This Way)

### 1. 为什么 reference 文件按需加载，而不是全放在主 SKILL.md 里？

因为 SEO 规则细节很多（CWV 阈值、schema 废弃列表、E-E-A-T 评分框架、质量门控…），如果全部预加载，主 skill 的 token 消耗会极高，而实际上每次审计只用到其中一部分。→ 所以采用 Progressive Disclosure：metadata 总是加载，详细规则按需读取 reference 文件。→ 这就是为什么 `seo/references/` 下的每个文件都是独立聚焦的主题（`cwv-thresholds.md`、`eeat-framework.md`、`quality-gates.md`、`schema-types.md`），而不是一个大文件。

### 2. 为什么 Python 脚本必须输出 JSON？

因为 Claude Code 的工具调用是程序性的——AI 需要解析脚本结果，不是读给人看的。→ 如果脚本输出人类可读文本，AI 就需要额外解析步骤，容易出错。→ 所以 `fetch_page.py`、`parse_html.py`、`analyze_visual.py` 全部强制 `--json` 输出，Claude 直接消费结构化数据，不做文本解析。→ 这就是为什么 CONTRIBUTING.md 把"Python scripts output JSON"列为硬性规则，而不是建议。

### 3. 为什么要内置 SSRF 防护和路径遍历防护？

因为 claude-seo 会接受用户输入的 URL，然后用 Python 脚本去抓取——这是一个经典的 SSRF 攻击面。→ 如果不加防护，恶意用户可以输入 `http://169.254.169.254/` 访问云元数据服务，或者输入相对路径访问本地文件。→ 所以 `fetch_page.py` 和 `analyze_visual.py` 都有 `ip.is_private or ip.is_loopback` 检查，`capture_screenshot.py` 有输出路径的 `os.path.realpath` 验证。→ v1.2.0 引入这些防护后，社区立刻发现 YAML frontmatter parsing bug（`#` 注释在 `---` 分隔符前面会破坏解析），说明安全和正确性是同步推进的。

---

## 你一定会踩的坑 (Pitfalls)

### 坑 1：User-Agent 用了 bot 风格字符串，Next.js 站点返回空 HTML

**场景**：你运行 `/seo technical https://somesaassite.com`，脚本抓回来的 HTML 里几乎什么都没有——title 空的，meta 空的，body 里只有一个 `<div id="app"></div>`。

**根因**：v1.2.1 之前，`fetch_page.py` 默认用 `ClaudeSEO/1.0` 作为 User-Agent。Next.js、Nuxt、Angular 等 SSR 框架检测到非浏览器 UA，直接返回未渲染的客户端 shell，而不是服务端渲染的完整 HTML。

**修复**：v1.2.1 把默认 UA 改成了 Chrome 风格字符串（带 `ClaudeSEO/1.2` 后缀）。v1.4.0 新增了 `--googlebot` flag，用 Googlebot UA 发请求，可以检测网站是否对 Googlebot 做了特殊预渲染——如果 Googlebot 和普通 UA 拿到的 HTML 大小差异很大，说明站点在做 dynamic rendering，这本身就是一个 technical SEO 信号。

**教训**：分析 SSR/CSR 混合的现代前端框架时，先检查 HTML 大小和内容完整性，再做任何其他分析。如果 body 里只有一个挂载点，直接告诉用户这是 CSR 站点，需要 Playwright 才能正确分析。

---

### 坑 2：FAQPage schema 在商业网站上用了，被标为 Critical 问题

**场景**：你在 `/seo schema` 输出里看到一条 Critical 错误：`FAQPage schema detected on commercial site — Google restricted FAQ rich results to government/healthcare only (August 2023)`。你慌了，以为要立刻删掉所有 FAQ 结构化数据。

**根因**：早期版本（v1.3.x）的 schema 验证逻辑过于激进，把"Google 不给 FAQ rich results"等同于"FAQPage 有害，必须删除"。这是错误的推断——FAQPage schema 即使拿不到 Google 的 rich result，仍然有两个价值：(1) AI/LLM 引用网站内容时，结构化的 FAQ 格式更容易被抽取为可引用段落；(2) 其他搜索引擎（Bing）仍然可能使用 FAQ 富结果。

**修复**：v1.4.0 把逻辑改成了三档：现有 FAQPage → Info 级别（不是 Critical），提示 GEO 价值；新增 FAQPage → 不推荐用于 Google，但注明 AI 可发现性价值；同时 `agents/seo-schema.md`、`seo/SKILL.md`、`seo/references/schema-types.md` 三处同步修改。

**教训**：schema 的"对 Google 有用"和"对内容可发现性有用"是两个维度。deprecated/restricted 不等于有害，要看具体场景。特别是 2025-2026 的 GEO 背景下，AI 引用的权重越来越高，单纯以 Google rich results 为标准评估 schema 价值会漏掉重要信号。

---

### 坑 3：Windows 安装脚本 `irm | iex` 被 Claude Code 本身的安全检查拦截

**场景**：你按照 README 里的 Windows 安装指引运行 `irm https://raw.githubusercontent.com/.../install.ps1 | iex`，但 Claude Code 拒绝执行，提示供应链风险。

**根因**：`irm | iex` 是 Windows PowerShell 的"下载并立即执行"模式，等价于 Unix 的 `curl | bash`——这种模式无法在执行前审查脚本内容。Claude Code 的安全 guardrail 把这类命令标记为供应链风险，拒绝运行。讽刺的是，这是由社区成员在实际使用中发现并报告的。

**修复**：v1.4.0 把 Windows 安装的主推方法改为 `git clone --tag v1.3.0` 然后本地运行 `powershell -File install.ps1`——先克隆再执行，用户可以在运行前审查脚本内容。`install.sh` 和 `install.ps1` 同时加入了版本固定（默认 clone 特定 release tag，而不是 main），防止静默更新。

**教训**：在 Claude Code 生态里发布工具时，不能用 `curl | bash` 或 `irm | iex` 作为主要安装方式——这不是建议而是硬性限制。`git clone + 审查 + 运行` 是正确模式。版本固定是必须的，`main` 分支安装等于放弃了版本控制。

---

## 模块地图 (Module Map)

### 1. 主 Orchestrator — `seo/SKILL.md`
**职责**：命令路由中枢，接收 `/seo` 命令后决定是直接处理、路由到子技能，还是派生 7 个并行 subagent。包含 routing table、business type 自动检测逻辑、整体 SEO Health Score 的权重分配。

**关键文件**：`seo/SKILL.md`（主入口，<500 行）、`seo/references/`（4 个按需加载的规则文件）

**依赖**：所有子技能和 subagent 都由它调度。

---

### 2. 数据采集层 — `scripts/`
**职责**：确定性的网页数据采集。`fetch_page.py` 抓 HTML（含 Googlebot UA 对比）；`parse_html.py` 解析结构（title、meta、H1、schema blocks、word count、links）；`analyze_visual.py` 用 Playwright 做视觉分析（above-fold、mobile scroll、font size）；`capture_screenshot.py` 截图（4 种 viewport）。

**关键文件**：`scripts/fetch_page.py`、`scripts/parse_html.py`、`scripts/analyze_visual.py`、`scripts/capture_screenshot.py`

**接口约定**：所有脚本必须支持 `--json` flag，输出结构化 JSON，供 AI subagent 消费。SSRF 防护（private IP block）和路径遍历防护（`os.path.realpath` 验证）是硬性要求。

---

### 3. 7 个并行 Subagent — `agents/`
**职责**：`/seo audit` 时同时派生，各自独立分析一个维度：
- `seo-technical.md`：可抓取性、可索引性、安全性、URL 结构、移动、CWV、JS 渲染、IndexNow（9 类）
- `seo-content.md`：E-E-A-T 评分（Experience 20%、Expertise 25%、Authority 25%、Trust 30%）、AI 引用就绪度
- `seo-schema.md`：JSON-LD 检测、废弃类型拦截（HowTo/SpecialAnnouncement/CourseInfo/VehicleListing）、生成正确 schema
- `seo-sitemap.md`：XML 格式验证、URL 状态码、50k 上限、location page 质量门控（30 页警告、50 页强制停止）
- `seo-performance.md`：CWV（LCP/INP/CLS）三项指标，75th percentile 标准，LCP subparts 诊断
- `seo-visual.md`：Playwright 截图、above-fold CTA 可见性、移动端响应式
- `seo-geo.md`：AI crawler 访问权限（GPTBot/ClaudeBot/PerplexityBot）、llms.txt 检测、passage 可引用性（134-167 词最优）、品牌信号（YouTube 关联度 0.737）

**接口约定**：通过 Task tool 以 `context: fork` 调用，不通过 Bash；YAML frontmatter 字段：`name`、`description`、`tools`（仅这三个）。

---

### 4. 12 个专项子技能 — `skills/`
**职责**：非全站审计场景下的单项深度分析。每个子技能对应一个 `/seo` 子命令，有完整的分析逻辑和输出格式规范。

**关键文件**：`skills/seo-audit/SKILL.md`（全站）、`skills/seo-geo/SKILL.md`（GEO/AEO）、`skills/seo-programmatic/SKILL.md`（程序化 SEO）、`skills/seo-hreflang/SKILL.md`（国际化）、`skills/seo-competitor-pages/SKILL.md`（竞品对比页）

**依赖**：可以相互委托（`seo-technical` 委托 `seo-hreflang` 做 hreflang 验证；`seo-audit` 委托 `seo-programmatic` 做程序化页面分析）。

---

### 5. Quality Gate 层 — `hooks/`
**职责**：在 code 被提交或文件被编辑时自动触发 SEO 校验，阻止明显错误进入代码库。

**关键文件**：`hooks/pre-commit-seo-check.sh`（检查 placeholder 文字、title 长度 30-60 字符、img 无 alt、deprecated schema 类型、FID 引用）；`hooks/validate-schema.py`（验证 JSON-LD 的 @context、@type、placeholder、废弃类型，exit code 2 时阻止操作）

**触发条件**：仅在有 staged 文件且文件是 HTML-like（`.html/.htm/.php/.jsx/.tsx/.vue/.svelte`）时生效，其他情况直接 exit 0，不影响性能。

---

### 6. 扩展系统 — `extensions/`
**职责**：可选的外部数据源集成。目前只有 DataForSEO 扩展，提供 22 个命令跨 9 个 API 模块（SERP、关键词、反链、on-page、竞品、内容分析、商业数据、AI 可见性、LLM 提及追踪）。安装后，其他 skill 自动检测并使用 live 数据。

**关键文件**：`extensions/dataforseo/install.sh`（非破坏性合并到 `~/.claude/settings.json`）、`extensions/dataforseo/field-config.json`（减少 75% token 消耗的字段过滤配置）

**架构约定**：每个扩展必须是自包含的（有独立的 install/uninstall），安装到标准路径（`~/.claude/skills/seo-<name>/`、`~/.claude/agents/seo-<name>.md`），MCP 配置非破坏性合并。

---

## 社区智慧 (Community Wisdom)

### 高频痛点与根因

**痛点 1：安装后 skill 不加载**
根因：SKILL.md 的 YAML frontmatter 前面有 HTML 注释（`<!-- ... -->`）。Anthropic 的 skill 解析器要求 `---` 必须是文件的第一行内容，任何前置内容都会导致 frontmatter 解析失败，skill 静默不加载。v1.2.0 修复了 8 个文件里的这个问题（来自 codex-seo fork 的 @kylewhirl 发现）。**诊断方法**：`head -5 ~/.claude/skills/seo/SKILL.md`，确认第一行是 `---`。

**痛点 2：Windows Python 检测失败**
根因：Windows 上 `python`、`python3`、`py -3` 三种调用方式并存，取决于安装方式和 PATH 配置。v1.2.0 引入了 `Resolve-Python` helper 按顺序尝试三种方式。同时，`pip install --break-system-packages`（Debian/Ubuntu 的 externally-managed-environment 保护）被移除，改为 venv 安装。**最安全做法**：永远用 `python -m pip` 而不是裸 `pip`。

**痛点 3：subagent 找不到**
根因：agents 文件需要在 `~/.claude/agents/` 目录下，而不是 skill 目录里。部分手动安装的用户只复制了 `skills/` 没有复制 `agents/`。v1.2.0 修复了 Windows installer 的非致命 subagent 复制问题（之前会 fatal exit）。**验证**：`ls ~/.claude/agents/seo-*.md` 应该有 7 个文件（含 seo-geo）。

**痛点 4：Playwright 安装了还是截图失败**
根因：`pip install playwright` 安装了 Python 库，但没有安装 Chromium 浏览器二进制。两步都要做：`pip install playwright && playwright install chromium`。如果安装在 venv 里，要用 venv 的 playwright：`~/.claude/skills/seo/.venv/bin/playwright install chromium`。

### 社区验证的最佳实践

**关于 schema**
- 永远用 `https://schema.org`（不是 `http://`），Google 对协议敏感
- 所有 URL 用绝对路径，不用相对路径
- 日期用 ISO 8601（`2026-03-15`，不是 `March 15, 2026`）
- 不要在生产代码里留 placeholder 文字——pre-commit hook 会阻止提交，但如果没装 hook 就会静默进入生产

**关于 GEO/AEO（AI 引用优化）**
- passage 长度 134-167 词是 AI 引用的最优区间（太短缺少上下文，太长被截断）
- YouTube 提及量与 AI 引用相关性最强（0.737），比反链（0.266）强得多——这意味着视频内容对 GEO 的投资回报率可能高于传统链接建设
- FAQPage schema 的 GEO 价值独立于 Google rich results 价值——两者不要混为一谈
- 只有 11% 的域名同时被 ChatGPT 和 Google AI Overviews 引用——平台间的优化策略需要分开考虑

**关于 E-E-A-T（2025 年 12 月 core update 之后）**
- "Experience" 维度现在是关键差异化因素：AI 可以生成听起来像专家的内容，但无法伪造真实经历。第一人称叙述（"I tested this..."）、原创截图、有具体细节的案例分析是现在最有价值的信号
- E-E-A-T 已从 YMYL 扩展到所有竞争性查询——不要以为自己不做健康/金融内容就不需要考虑

---

## 速查规则 (Quick Reference)

### 命令路由

| 命令 | 场景 | 输出 |
|------|------|------|
| `/seo audit <url>` | 全站审计，7 agent 并行 | FULL-AUDIT-REPORT.md + ACTION-PLAN.md |
| `/seo page <url>` | 单页深度分析 | 6 维度报告 |
| `/seo technical <url>` | 技术 SEO，9 类 | 评分 + 优先级问题列表 |
| `/seo content <url>` | E-E-A-T 评分 | 4 维度分项 + AI 引用就绪度 |
| `/seo schema <url>` | Schema 检测/验证/生成 | JSON-LD 代码块 |
| `/seo geo <url>` | AI 搜索优化 | GEO 健康评分（5 维度） |
| `/seo sitemap <url>` | XML sitemap 验证 | 逐项 pass/fail |
| `/seo images <url>` | 图片优化 | alt/size/format/CLS 检查 |
| `/seo plan <type>` | 战略规划（saas/local/ecommerce/publisher/agency） | 4 阶段路线图 |
| `/seo hreflang <url>` | 国际化 hreflang 验证 | 双向 return tag 检查 |
| `/seo programmatic` | 程序化 SEO 分析 | 数据源质量 + 模板引擎设计 |
| `/seo competitor-pages` | 竞品对比页生成 | X vs Y 内容框架 |

### 核心阈值速查

| 指标 | Good | Needs Improvement | Poor |
|------|------|-------------------|------|
| LCP | ≤2.5s | 2.5-4.0s | >4.0s |
| INP（取代 FID） | ≤200ms | 200-500ms | >500ms |
| CLS | ≤0.1 | 0.1-0.25 | >0.25 |
| Title 长度 | 30-60 chars | — | <30 or >60 |
| Meta description | 120-160 chars | — | 其他 |
| GEO passage 长度 | 134-167 词 | — | 其他 |

### Schema 废弃状态

| Schema 类型 | 状态 | 起效时间 |
|-------------|------|---------|
| HowTo | 废弃，无 rich result | 2023-09 |
| FAQ（商业站） | 受限，仅政府/医疗 | 2023-08 |
| SpecialAnnouncement | 废弃 | 2025-07-31 |
| CourseInfo / EstimatedSalary / LearningVideo | 退役 | 2025-06 |
| ClaimReview / VehicleListing | 退役 | 2025-06 |
| FAQPage（GEO 视角） | 仍有价值（AI 引用） | — |

### 文件大小约束

| 文件类型 | 上限 |
|----------|------|
| SKILL.md | 500 行 / 5000 tokens |
| Reference 文件 | 200 行 |
| Python 脚本 | 必须有 CLI 接口 + JSON 输出 |
| Shell 脚本 | 必须 `set -euo pipefail` |

### Location Page 质量门控

| 页面数量 | 动作 |
|----------|------|
| <30 页 | 正常处理 |
| 30-49 页 | WARNING：要求每页 60%+ 独特内容 |
| 50+ 页 | HARD STOP：要求用户明确理由才继续 |

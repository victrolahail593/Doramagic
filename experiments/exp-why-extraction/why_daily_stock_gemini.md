# WHY 提取分析报告: daily_stock_analysis

项目名：daily_stock_analysis (A股自选股智能分析系统)

```yaml
- why_id: W001
  type: architecture
  claim: "采用策略模式（Strategy Pattern）构建多源数据获取层，实现故障自动转移"
  reasoning_chain: "金融公开数据接口（如 AkShare、Tushare）稳定性极差（易反爬、易限流、接口常变更）→ 抽象 BaseFetcher 定义统一标准化接口 → DataFetcherManager 实现按优先级排序的自动 fallback 逻辑 → 确保分析流程不因单一数据源失效而中断"
  evidence:
    - type: CODE
      source: "data_provider/base.py (Line 9-13, DataFetcherManager implementation)"
  contrast: "不选择硬编码单一数据源或将切换逻辑耦合在业务层，是为了应对免费金融数据的高不可用性风险。"

- why_id: W002
  type: implementation
  claim: "实时行情数据采用长达 20 分钟（1200秒）的缓存 TTL"
  reasoning_chain: "批量分析（30+股票）通常在数分钟内完成 → AI 分析偏向趋势建议，不要求秒级同步数据（5-20 分钟延迟对日线/波段分析可接受）→ 极大幅度减少对免费 API 的高频调用 → 降低被封禁风险并提升整体响应速度"
  evidence:
    - type: CODE
      source: "data_provider/akshare_fetcher.py (Line 80-86)"
  contrast: "不追求实时推送或秒级缓存，是因为免费数据源难以承受高并发请求，且 AI 推理过程本身即存在分钟级滞后。"

- why_id: W003
  type: implementation
  claim: "使用 newspaper3k 提取新闻正文并严格限制 1500 字符"
  reasoning_chain: "原始网页包含大量 HTML 噪声（导航栏、广告、页脚）→ 噪声会消耗昂贵的 LLM Token 并干扰 AI 提取金融逻辑 → newspaper3k 提供相对干净的正文文本 → 截断长度在保证信息量的前提下适配大模型上下文窗口"
  evidence:
    - type: CODE
      source: "src/search_service.py (Line 71-100)"
  contrast: "不直接发送 raw HTML 或使用正则表达式，是为了在 Token 成本、解析准确度与开发复杂度之间取得平衡。"

- why_id: W004
  type: constraint
  claim: "在分析主流程中硬编码乖离率（Bias）与均线排列的交易纪律作为 Guardrail"
  reasoning_chain: "LLM 易产生“盲目看多”的幻觉或忽略极端风险 → 在提示词外预置硬性技术指标（如乖离率 > 5% 自动提示风险）→ 强制要求 AI 结论符合既定的趋势交易原则 → 提升投资建议的安全性"
  evidence:
    - type: CODE
      source: "main.py (Line 23-27), README.md (Built-in Trading Discipline)"
  contrast: "不完全依赖大模型自由发挥，是为了通过量化指标对“概率性”的 AI 结论进行确定性的约束。"

- why_id: W005
  type: negation
  claim: "在管理层统一剔除交易所后缀（Normalization），而非让各数据源各自处理"
  reasoning_chain: "不同数据源（AkShare, YFinance）对 A 股代码后缀定义不一（.SH vs .SS vs SH6xxxxx）→ 在 DataProviderManager 层统一剥离后缀并标准化 → 内部逻辑仅处理纯 5/6 位数字代码 → 简化跨源数据匹配逻辑"
  evidence:
    - type: CODE
      source: "data_provider/base.py (Line 73-100)"
  contrast: "不传递带后缀的代码，是为了避免上层逻辑（映射、缓存、存储）因后缀差异而出现重复请求或匹配失败。"

- why_id: W006
  type: implementation
  claim: "爬虫数据源引入 2-5 秒随机休眠与 User-Agent 轮换"
  reasoning_chain: "AkShare 依赖对金融门户网站的接口爬取 → 高频、固定规律的访问极易触发 IP 封锁 → 通过模拟人类随机访问行为来对抗反爬策略 → 延长系统在无代理环境下的生命周期"
  evidence:
    - type: CODE
      source: "data_provider/akshare_fetcher.py (Line 41-55)"
  contrast: "不选择高性能并发抓取，是因为对于复盘系统而言，数据的稳定获取（Availability）远比瞬间抓取速度重要。"

- why_id: W007
  type: architecture
  claim: "优先适配 GitHub Actions 的‘无服务器（Serverless）’批处理设计"
  reasoning_chain: "目标用户为个人投资者，运维成本敏感 → GitHub Actions 提供免费的定时触发与 Secrets 存储 → 设计为无状态执行模式，支持 dotenv 与系统环境变量双重配置 → 实现‘零成本’运行部署"
  evidence:
    - type: CODE
      source: "main.py (Line 15-20), README.md (Quick Start via GitHub Actions)"
  contrast: "不采用传统的 Web 后台常驻架构（如长期开启 Celery），是因为股票复盘是典型的离线任务，无需 24/7 消耗服务器资源。"

- why_id: W008
  type: selection
  claim: "选择 LiteLLM 作为统一的 AI 抽象层，而非直接集成 SDK"
  reasoning_chain: "主流模型（Gemini, Claude, DeepSeek）API 规范不一 → LiteLLM 提供标准化的 OpenAI-like 响应格式 → 允许用户通过简单的环境变量切换模型厂商 → 支持多模型间的无缝 fallback"
  evidence:
    - type: CODE
      source: "requirements.txt (litellm), README.md (AI Models section)"
  contrast: "不直接使用官方 SDK，是为了降低系统与特定模型厂商的耦合度，支持‘一键换脑’并提升多模型容灾能力。"
```

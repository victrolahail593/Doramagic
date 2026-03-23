# WHY Extraction: daily_stock_analysis

> 代码考古报告 — 设计哲学提取
> 项目：ZhuLinsen/daily_stock_analysis（A股/港股/美股自选股智能分析系统）
> 提取日期：2026-03-13

---

```yaml
- why_id: W001
  type: architecture
  claim: "用 GitHub Actions 定时触发替代自托管服务器，把运维成本转移给平台"
  reasoning_chain: >
    目标用户是个人投资者，没有运维能力 → 自托管服务器需要配置、维护、付费 →
    GitHub Actions 提供免费定时 cron（每月 2000 分钟）→ 任务时长约 5-10 分钟，
    30 只股票完全在免费额度内 → 因此将整个调度层外包给 GitHub，用户只需 Fork + 配置 Secrets →
    零成本、零运维、5 分钟部署完成
  evidence:
    - type: CODE
      source: ".github/workflows/daily_analysis.yml:3-6（schedule: cron '0 10 * * 1-5'）"
    - type: CODE
      source: ".github/workflows/daily_analysis.yml:34（timeout-minutes: 30）"
    - type: DOC
      source: "README.md:121（'5 分钟完成部署，零成本，无需服务器'）"
    - type: CODE
      source: ".github/workflows/daily_analysis.yml:38-39（随机延迟 0-60 秒启动，防固定时间被封）"
  contrast: >
    为什么不选 Celery + Redis 的后台任务队列？Celery 需要 Redis broker 和 worker 常驻进程，
    每月服务器成本 ≥¥50；对非开发者用户不可能完成部署。
    为什么不选 crontab？需要 Linux 服务器，用户须有 SSH 权限，超出目标用户能力范围。

- why_id: W002
  type: architecture
  claim: "数据层用策略模式（Strategy Pattern）实现多数据源自动故障切换，而不是写死单一数据源"
  reasoning_chain: >
    中国金融数据源全部基于爬虫或半官方接口 → 这些接口随时可能封禁（反爬）或宕机 →
    单一数据源意味着系统随时可能整体不可用 → 因此抽象出 BaseFetcher 接口，
    由 DataFetcherManager 按优先级（efinance=0, akshare=1, tushare=2, baostock=3, yfinance=4）
    依次尝试 → 任一数据源失败自动切换到下一个 → 系统可用性从单点依赖提升为多冗余
  evidence:
    - type: CODE
      source: "data_provider/base.py:7-15（模块注释：'策略模式 (Strategy Pattern)'，'失败自动切换到下一个数据源'）"
    - type: CODE
      source: "data_provider/base.py:451-481（DataFetcherManager.__init__：按 priority 排序 fetchers）"
    - type: CODE
      source: "requirements.txt:162-168（5个数据源依赖，注释标注 Priority 0-4）"
  contrast: >
    为什么不直接用 akshare 一个库？akshare 基于东方财富爬虫，遭遇高并发时被封概率高；
    tushare Pro 需要积分付费门槛，不适合入门用户。多源策略让免费用户也能获得稳定性，
    有 token 的用户可通过优先级配置提升数据质量。

- why_id: W003
  type: implementation
  claim: "monkeypatching requests.Session.request 注入反爬认证，而不是修改各处的 HTTP 调用"
  reasoning_chain: >
    东方财富接口要求携带 NID 令牌和合法 User-Agent → 项目使用 akshare/efinance 第三方库
    调用东方财富接口，无法直接修改这些库的内部 HTTP 调用 → 如果在每个 Fetcher 里包装，
    需要大量重复代码且不可能覆盖第三方库的内部请求 → 因此在全局层替换
    requests.Session.request 入口（monkeypatch），让所有通过 requests 的 HTTP 请求
    对目标域名（fund.eastmoney.com 等）自动注入认证头和随机休眠 →
    第三方库无感知地获得反爬保护
  evidence:
    - type: CODE
      source: "patch/eastmoney_patch.py:14（original_request = requests.Session.request）"
    - type: CODE
      source: "patch/eastmoney_patch.py:154-181（patched_request 函数：检查 URL，注入 User-Agent + NID Cookie，随机休眠 1-4 秒）"
    - type: CODE
      source: "patch/eastmoney_patch.py:181（requests.Session.request = patched_request，全局替换）"
    - type: CODE
      source: "data_provider/akshare_fetcher.py:652（from patch.eastmoney_patch import eastmoney_patch）"
  contrast: >
    为什么不 fork akshare 加入认证逻辑？维护成本高，akshare 每次更新都要合并；
    为什么不用代理中间件？需要额外网络基础设施。Monkeypatch 是侵入性最小、
    覆盖范围最广的方案，代价是隐式耦合（测试时需显式 disable）。

- why_id: W004
  type: selection
  claim: "用 LiteLLM 作为 LLM 统一调用层，而不是直接调用各家 SDK"
  reasoning_chain: >
    项目需要支持 Gemini、Claude、OpenAI、DeepSeek、通义千问等多个 LLM →
    每家 SDK 接口不同，错误处理不同，token 计数方式不同 → 直接适配每家意味着
    为每家写一套调用代码、重试逻辑、fallback 逻辑 → LiteLLM 提供统一的
    OpenAI-compatible 接口，支持 Router（多 Key 负载均衡 + fallback） →
    因此所有 LLM 调用通过 LiteLLM Router，只需配置 model_list，
    provider 切换不需要改业务代码
  evidence:
    - type: CODE
      source: "requirements.txt:181（litellm>=1.80.10，注释：'Unified LLM client'）"
    - type: CODE
      source: "src/analyzer.py:21（import litellm; from litellm import Router）"
    - type: CODE
      source: "src/agent/llm_adapter.py:1-8（模块注释：'Multi-provider LLM Tool-Calling Adapter. Normalizes function-calling / tool-use across all providers'）"
    - type: DOC
      source: "README.md:98（'统一通过 LiteLLM 调用，支持多 Key 负载均衡'）"
  contrast: >
    为什么不自己写适配层？LiteLLM 已处理 30+ provider 的协议差异（包括 DeepSeek 思考模式
    的 reasoning_content 特殊字段）；自建适配层需要持续跟进各家 API 变化，
    维护成本远超直接依赖一个活跃维护的开源库。

- why_id: W005
  type: constraint
  claim: "MA5 > MA10 > MA20 多头排列被硬编码为系统级交易纪律，而不是作为可配置参数"
  reasoning_chain: >
    目标用户是个人投资者，需要明确的操作决策（买/卖/观望），而非开放式分析 →
    如果把交易信号判断完全交给 LLM 自由发挥，输出结果不稳定，用户无法建立信任 →
    因此将核心交易纪律（多头排列、乖离率 ≤5% 不追高、缩量回踩买点）写进
    StockTrendAnalyzer 的计算逻辑（代码判断）和 Agent 的 SYSTEM_PROMPT（LLM 遵守）→
    这条规则在两处都出现，形成双重约束：即使 LLM 想"看多"一只空头排列的股票，
    系统代码层也会计算出 SELL 信号并传入 context，LLM 不得不响应
  evidence:
    - type: CODE
      source: "src/stock_analyzer.py:14（注释：'趋势交易 - MA5>MA10>MA20 多头排列，顺势而为'）"
    - type: CODE
      source: "src/agent/executor.py:98（AGENT_SYSTEM_PROMPT：'多头排列必须条件：MA5 > MA10 > MA20'）"
    - type: CODE
      source: "src/core/pipeline.py:95（初始化日志：'已启用趋势分析器 (MA5>MA10>MA20 多头判断)'）"
    - type: CODE
      source: "src/config.py:163（bias_threshold: float = 5.0，注释：'乖离率阈值（%），超过此值提示不追高'）"
  contrast: >
    为什么不让 LLM 自己判断技术面？LLM 在没有约束时倾向于给出模糊结论（"可以关注"）；
    硬编码规则强制 LLM 给出有立场的结论，这正是产品价值所在——
    对比市面上"提供信息"的工具，该系统提供的是"有操作建议的决策"。

- why_id: W006
  type: negation
  claim: "系统没有用关系型数据库存储分析报告的完整结构，而是将 JSON Dashboard 序列化为 Text 字段存入 SQLite"
  reasoning_chain: >
    分析结果的 Dashboard 是一个多层嵌套 JSON（core_conclusion / data_perspective /
    intelligence / battle_plan），结构会随功能迭代演变 → 如果将每个字段建为独立列，
    schema migration 成本极高（每新增一个 LLM 输出字段都要 ALTER TABLE）→
    SQLite 是 Python 内置，零额外服务依赖（requirements.txt 注释：'SQLite 是 Python 内置，无需额外安装'）→
    因此将整个 AnalysisResult 的 dashboard/raw_response 序列化为 Text(JSON) 存储，
    同时将 sentiment_score / decision_type 等需要查询的关键字段单独建列 →
    兼顾查询效率（关键字段可 WHERE）和模式演化灵活性（JSON 字段无需 migration）
  evidence:
    - type: CODE
      source: "src/storage.py:63-109（StockDaily 模型：OHLC + 技术指标作为独立列）"
    - type: CODE
      source: "requirements.txt:197（注释：'SQLite 是 Python 内置，无需额外安装'）"
    - type: CODE
      source: "src/schemas/report_schema.py:11（注释：'Uses Optional for lenient parsing; business-layer integrity checks are separate'）"
    - type: INFERENCE
      source: "src/storage.py 中 AnalysisReport 表结构（dashboard 作为 Text/JSON 字段，非拆分列）"
  contrast: >
    为什么不用 PostgreSQL + JSONB？需要额外服务，GitHub Actions 无状态运行无法持久化外部 DB；
    为什么不将 dashboard 完全拆平？LLM 输出结构在迭代中频繁变化，拆平意味着每次
    schema change 都需要数据迁移，对这个规模的项目代价过高。

- why_id: W007
  type: implementation
  claim: "Agent 分析模式与批量 Pipeline 模式共存，通过配置开关切换，而不是重写为纯 Agent 架构"
  reasoning_chain: >
    原始系统是确定性 Pipeline（fetch → trend_analyze → news_search → LLM →notify）→
    后来加入 Agent 模式（ReAct loop + 工具调用）→ 如果全量迁移到 Agent，
    稳定性难以保证（Agent 的工具调用顺序不确定，token 消耗不可预期）→
    Agent 模式适合交互式"问股"场景（用户实时提问），Pipeline 模式适合
    批量定时任务（每天分析 N 只股票，成本可控）→ 因此保留两条路径，
    通过 agent_mode 配置开关切换，甚至支持"有策略配置时自动启用 Agent"的混合模式
  evidence:
    - type: CODE
      source: "src/core/pipeline.py:223-231（use_agent 判断逻辑：先检查 agent_mode，再检查 configured_skills）"
    - type: CODE
      source: "src/config.py:166-169（agent_mode: bool = False，agent_skills: List[str]）"
    - type: CODE
      source: "src/agent/executor.py:70-100（AGENT_SYSTEM_PROMPT 定义了 4 阶段顺序工作流：行情→技术→情报→报告）"
    - type: CODE
      source: "src/core/pipeline.py:257-267（use_agent 为 True 时调用 _analyze_with_agent，否则继续确定性 pipeline）"
  contrast: >
    为什么不全量迁移到 Agent？Agent 的 token 消耗是 Pipeline 的 3-5 倍；
    GitHub Actions 每月分钟数有限，Agent 模式下 30 只股票×10步/只可能超出预算。
    Pipeline 模式是"确定性骨架"，Agent 是"灵活解读层"，两者互补而非替代。

- why_id: W008
  type: selection
  claim: "LLM 输出用 json-repair 容错解析，而不是直接 json.loads 或要求强格式"
  reasoning_chain: >
    系统要求 LLM 输出一个大型嵌套 JSON（含 30+ 字段）→ LLM 有时会在 JSON 中
    混入注释、尾随逗号、截断输出（token limit）→ 直接 json.loads 在任何格式错误时
    抛异常，导致整次分析失败 → json-repair 能修复常见的 LLM JSON 输出缺陷 →
    同时系统还有两层补救：Pydantic Schema 宽松解析（所有字段 Optional）+
    apply_placeholder_fill 填充缺失必填字段 → 三层容错确保
    即使 LLM 输出不完整，也能产出可推送的报告
  evidence:
    - type: CODE
      source: "requirements.txt:180（json-repair>=0.55.1，注释：'JSON 修复'）"
    - type: CODE
      source: "src/agent/executor.py:21（from json_repair import repair_json）"
    - type: CODE
      source: "src/schemas/report_schema.py:10-11（注释：'Uses Optional for lenient parsing; business-layer integrity checks are separate'）"
    - type: CODE
      source: "src/analyzer.py:61-93（apply_placeholder_fill：对缺失必填字段填充占位符）"
    - type: CODE
      source: "src/analyzer.py:33-58（check_content_integrity：检测必填字段是否缺失）"
  contrast: >
    为什么不用 Structured Output（OpenAI function calling 强制 JSON）？
    Structured Output 依赖 provider 支持，Gemini、DeepSeek 早期版本不稳定；
    为什么不让 LLM 重试直到格式正确？重试消耗 token，且 GitHub Actions 有超时限制，
    容错修复比重试代价更低。
```

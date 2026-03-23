# WHY 提取报告：daily_stock_analysis（Sonnet v3 — Stage 0 v2）

```yaml
- why_id: W001
  type: architecture
  claim: "数据层采用优先级驱动的多源 Failover 架构，而非单一数据源"
  reasoning_chain: >
    项目面向 A股/港股/美股，所有数据源（AkShare、Tushare、Pytdx、Baostock、YFinance）
    均为非官方/爬虫/有限免费 API → 任何单一源都有随时封禁或限流的风险
    → 以 priority 整数排序后依次尝试，失败自动 Failover
    → DataFetcherManager 统一调度，调用方无感知切换
    → 板块排行同样固定回退顺序（AkShare EM → Sina → Tushare → efinance）
  evidence:
    - type: CODE
      source: "data_provider/base.py:L1977-L2058 (DataFetcherManager.__init__, _init_default_fetchers, BaseFetcher.priority)"
    - type: CODE
      source: "data_provider/base.py:L2072-L2079 (get_sector_rankings 固定回退顺序注释)"
    - type: DOC
      source: "requirements.txt:L383-L388 (数据源依赖，注释标注 Priority 0–4)"
  contrast: >
    若只用单一数据源（如仅 AkShare），一旦东方财富反爬策略升级或接口变更，
    整个系统立即不可用。而若用随机负载均衡，则无法保证最优质/最稳定的源被优先使用。
    priority 整数 + failover 同时保证了质量优先和高可用。

- why_id: W002
  type: implementation
  claim: "AkshareFetcher 在每次请求前随机休眠 2–5 秒并轮换 User-Agent，而非直接发请求"
  reasoning_chain: >
    AkShare 本质是对东方财富等网站的爬虫封装 → 高频相同 UA 的请求极易触发反爬机制
    → 通过 random.uniform(sleep_min, sleep_max) 引入请求间隔抖动
    → 同时通过 fake-useragent 库随机替换 requests Session 的 User-Agent header
    → 模拟人类浏览器访问节奏，降低被封禁概率
    → 项目专门在 AkshareFetcher 的类 docstring 中将此列为"关键策略"
  evidence:
    - type: CODE
      source: "data_provider/akshare_fetcher.py:L1753-L1793 (AkshareFetcher.__init__, _set_random_user_agent, 类 docstring)"
    - type: CODE
      source: "data_provider/base.py:L2018-L2027 (BaseFetcher.random_sleep, 注释'防封禁策略：模拟人类行为的随机延迟')"
    - type: DOC
      source: "requirements.txt:L414 (fake-useragent>=1.4.0，注释'随机 User-Agent 防封禁')"
  contrast: >
    固定间隔（如每次 sleep(2)）会形成规律性请求节奏，仍可被服务端识别为自动化工具。
    固定 UA 则更明显。随机抖动 + UA 轮换共同打破了请求的规律性特征。

- why_id: W003
  type: selection
  claim: "选择 LiteLLM 作为唯一 LLM 调用层，而非直接调用各 LLM 的原生 SDK"
  reasoning_chain: >
    项目目标用户是中国散户，主流模型（Gemini、Claude、GPT）访问有网络障碍
    → 需要支持 AIHubMix 等国内聚合代理以及 DeepSeek、通义等本土模型
    → DeepSeek 的思考模式会返回额外的 reasoning_content 字段，原生 OpenAI SDK 无法处理
    → LiteLLM 提供统一 API 接口，并内置对 deepseek-reasoner、qwq 等模型 reasoning_content 的处理
    → 同时支持多 Key 负载均衡（LITELLM_FALLBACK_MODELS），缓解单 Key 限流问题
    → 用户只需配置 LITELLM_MODEL 一个环境变量即可切换任意后端
  evidence:
    - type: CODE
      source: "requirements.txt:L401-L403 (litellm>=1.80.10，注释'Unified LLM client'; openai 标注为'transitive dependency of litellm, kept explicit')"
    - type: DOC
      source: "README.md:L125-L173 (AI模型配置表，明确说明通过 LiteLLM 统一调用，DeepSeek 思考模式按模型名自动识别)"
    - type: DOC
      source: "litellm_config.example.yaml:L2592-L2643 (配置模板展示多后端统一路由)"
  contrast: >
    若为每家 LLM 维护独立适配器（自建适配层），每新增一个模型都要修改核心代码，
    且 DeepSeek 的 reasoning_content 等特殊字段处理会散布在各处。
    LiteLLM 将差异封装在库层，主代码路径保持统一。

- why_id: W004
  type: constraint
  claim: "GitHub Actions 工作流在触发前加入 0–60 秒随机延迟，而非准点执行"
  reasoning_chain: >
    系统定时执行且调用多个外部 API（AkShare 爬虫、LLM 接口、搜索引擎）
    → 大量 fork 用户同时在北京时间 18:00 准点触发，会形成请求峰值
    → 同一时刻数百个 IP 向同一数据源发送相同请求，触发反爬或速率限制的概率急剧上升
    → 通过 sleep $((RANDOM % 60)) 将触发时间分散在 60 秒窗口内
    → 每个实例的请求时间戳不同，避免集中攻击效果
  evidence:
    - type: CODE
      source: ".github/workflows/daily_analysis.yml:L709-L710 (步骤'随机延迟（避免固定时间访问）', 'sleep $((RANDOM % 60))')"
    - type: DOC
      source: ".github/workflows/daily_analysis.yml:L676-L677 (定时触发注释 'cron: 0 10 * * 1-5'，说明所有 fork 共用同一 cron)"
    - type: INFERENCE
      source: "README.md:L86，项目为 GitHub fork 模式部署，理论上存在大量并发实例"
  contrast: >
    准点执行简单直接，但在 GitHub Actions 上大量 fork 的场景下，
    这等同于组织了一次对数据提供商的协同请求。随机延迟是面向 fork 生态的特有工程决策。

- why_id: W005
  type: negation
  claim: "项目没有为 LLM 输出建立严格 schema 校验，而是用 json-repair 修复后直接使用"
  reasoning_chain: >
    LLM 的股票分析报告输出为自由格式 JSON → LLM 偶发输出格式错误（括号不匹配、多余逗号等）
    → 若使用严格 schema 校验（如 Pydantic validation），格式错误会导致整次分析失败
    → 项目选择引入 json-repair 库在解析前修复常见 JSON 错误
    → 同时设置 REPORT_INTEGRITY_ENABLED 标志，对缺失字段进行占位补全而非报错
    → 体现了"宁可得到一份不完美的报告，也不能让整条主流程崩溃"的设计取向（fail-open）
  evidence:
    - type: CODE
      source: "requirements.txt:L399 (json-repair>=0.55.1，注释'JSON 修复')"
    - type: DOC
      source: "README.md:L202-L203 (REPORT_INTEGRITY_ENABLED 说明：'缺失必填字段时重试或占位补全'，REPORT_INTEGRITY_RETRY 默认值 1)"
    - type: DOC
      source: "README.md:L244-L247 (基本面超时语义 P0 注释：'best-effort 软超时(fail-open)，超时会立即降级并继续主流程')"
  contrast: >
    严格校验能保证数据质量，但对于面向个人用户的每日推送系统，
    一次 LLM 格式错误导致"今日无报告"比"报告有个别字段为占位符"对用户体验的伤害更大。
    fail-open + 修复的策略将可靠性置于完美性之上。

- why_id: W006
  type: architecture
  claim: "股票代码在系统输入边界统一归一化（normalize_stock_code + canonical_stock_code），而非在各模块内部各自处理"
  reasoning_chain: >
    系统接受来自多个入口的股票代码（CLI 参数、Bot 消息、Web UI、API、.env 配置）
    → 用户输入可能包含各种格式：SH600519、600519.SH、sh600519、hk00700、AAPL、aapl 等
    → 若每个模块自行处理，则格式差异会导致数据库查询不命中、数据源调用失败等问题
    → normalize_stock_code 在 DataProviderManager 层统一剥离交易所前/后缀
    → canonical_stock_code 在所有输入边界统一转大写（Issue #355）
    → 两个函数职责明确分离：normalize 处理格式，canonical 处理大小写
  evidence:
    - type: CODE
      source: "data_provider/base.py:L1835-L1876 (normalize_stock_code，注释'This function is applied at the DataProviderManager layer so that all individual fetchers receive a clean 6-digit code')"
    - type: CODE
      source: "data_provider/base.py:L1949-L1963 (canonical_stock_code，注释'This is a display/storage layer concern, distinct from normalize_stock_code')"
    - type: CODE
      source: "main.py:L2323 (stock_codes = [canonical_stock_code(c) for c in ...], 注释'统一为大写 Issue #355')"
  contrast: >
    让各模块自行处理代码格式是常见的"能用就行"做法，但会造成同一只股票在数据库中
    以多种格式存储（600519 vs SH600519），历史报告查询、回测匹配都会悄然失败。
    集中归一化在系统边界一次性解决，后续所有模块见到的格式保证一致。

- why_id: W007
  type: implementation
  claim: "交易策略以 YAML 文件定义并存放在 strategies/ 目录，而非硬编码在 Python 源码中"
  reasoning_chain: >
    项目内置 11 种交易策略（均线金叉、缠论、波浪理论、情绪周期等）
    → 策略本质是描述给 LLM Agent 的"分析框架"（自然语言 instructions + 工具列表 + 评分规则）
    → 将策略逻辑写入 Python 代码意味着每次调整策略参数（如换手率阈值、情绪判断标准）
       都需要修改源码、提交 PR、等待发布
    → YAML 文件可被挂载覆盖（docker-compose.yml 中 strategies:/app/strategies:ro）
    → 环境变量 AGENT_STRATEGY_DIR 允许用户指定自定义策略目录，无需 fork 源码
  evidence:
    - type: CODE
      source: "strategies/bull_trend.yaml、strategies/ma_golden_cross.yaml、strategies/chan_theory.yaml 等（strategies/ 目录下的 YAML 结构）"
    - type: DOC
      source: "README.md:L232-L234 (AGENT_SKILLS、AGENT_STRATEGY_DIR 配置说明：'自定义策略目录（默认内置 strategies/）')"
    - type: CODE
      source: "docker/docker-compose.yml:L2568 (volumes 挂载：'../strategies:/app/strategies:ro'，策略文件独立于镜像)"
  contrast: >
    硬编码策略逻辑（如在 Python 类中定义策略参数）会将"业务规则"与"执行引擎"耦合。
    用户若想调整均线周期或添加自定义策略，必须修改源代码。
    YAML 外置使策略成为数据而非代码，LLM 动态读取，策略迭代无需重新部署。

- why_id: W008
  type: constraint
  claim: "美股历史数据与实时行情统一使用 YFinance，而非与 A股相同的数据源"
  reasoning_chain: >
    A股可用东方财富、Tushare 等国内数据源，这些源对美股的复权处理标准不统一
    → 回测和历史分析依赖一致的复权数据，若历史与实时来自不同数据源，复权基准不同
    → 会导致技术指标（MA、乖离率）计算值错位，进而影响 AI 分析结论
    → YFinance 对美股提供统一的历史 + 实时数据接口，复权处理由同一套逻辑保证一致性
    → 因此美股路径主动绕过多源 Failover 机制，单独使用 YFinance
  evidence:
    - type: DOC
      source: "README.md:L129 ('注：美股历史数据与实时行情统一使用 YFinance，确保复权一致性')"
    - type: CODE
      source: "data_provider/akshare_fetcher.py:L1658-L1681 (_is_us_code 函数，美股代码识别后路由到专用处理逻辑)"
    - type: CODE
      source: "requirements.txt:L388 ('yfinance>=0.2.0  # Priority 4: Yahoo Finance (Fallback)'，但对美股实为唯一源)"
  contrast: >
    若美股也加入多源 Failover（如 AkShare + YFinance 交替），
    不同数据源的复权因子计算方式差异会在历史数据中引入系统性偏差，
    导致支撑/阻力位计算、技术指标出现"幽灵信号"。
    一致性比冗余更重要，所以美股单独固定使用 YFinance。
```

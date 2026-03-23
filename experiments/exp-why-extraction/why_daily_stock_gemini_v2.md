# WHY 提取报告：daily_stock_analysis（Gemini v2）

```yaml
- why_id: W001
  type: architecture
  claim: "选择实现基于策略模式的多数据源自动降级机制，而非依赖单一商业API。"
  reasoning_chain: "项目主要依赖免费的数据爬虫（如 efinance、akshare） → 免费接口（特别是东方财富相关）极易触发反爬和封禁 → 为保证定时分析任务（如通过 GitHub Actions 每日运行）的高可用性 → 实现了按优先级（efinance > akshare > tushare 等）自动切换和熔断降级。"
  evidence:
    - type: CODE
      source: "data_provider/base.py:2-14"
    - type: DOC
      source: "requirements.txt:12-17"
  contrast: "不选择单一商业行情源（如通联数据/万得等付费 API），因为项目定位为免费、个人使用且可以通过 GitHub Actions 零成本部署，高昂的商业 API 费用违背了这一初衷。"

- why_id: W002
  type: constraint
  claim: "实时行情数据的本地缓存 TTL 被刻意设定为较长的 20 分钟。"
  reasoning_chain: "系统主要场景为批量分析个人的自选股列表（通常约 30 只） → 整个分析流程耗时一般在 5 分钟内 → 20 分钟的缓存足以覆盖单次批量运行的全周期 → 同时，日度级别的趋势分析对秒级行情的实时性要求不高 → 延长缓存有效防止了频繁请求接口导致 IP 被封禁。"
  evidence:
    - type: CODE
      source: "data_provider/akshare_fetcher.py:59-69"
    - type: INFERENCE
      source: "批量运行环境下，针对同一数据源的并发短时查询容易触发反爬阈值，利用长 TTL 可最大化缓存命中率。"
  contrast: "不使用 1 分钟内的短缓存，因为会导致批量分析同一只股票时重复请求被封禁；也不使用只存在于单次调用的内存状态，这无法在分散的请求（如 WebUI 触发）中复用数据以降低频次。"

- why_id: W003
  type: constraint
  claim: "在 AI 股票分析系统的底层逻辑中硬编码特定的技术指标交易纪律（如乖离率>5%不买入、均线多头排列）。"
  reasoning_chain: "纯粹依赖大模型进行股票分析时，AI 容易受当时新闻情绪影响或出现幻觉，给出盲目追高的建议 → 为了确保分析结果的安全边际，控制回撤风险 → 在系统代码层面对大模型的判定结果或提示词施加刚性的技术指标约束（严进策略）。"
  evidence:
    - type: CODE
      source: "main.py:16-19"
    - type: DOC
      source: "README.md:76-77"
  contrast: "不选择完全依赖大模型（如让 GPT-4 自由发挥阅读 K 线给出买卖点），因为大模型的发散性难以保证稳定的风控下限，往往偏离保守稳健的投资目标。"

- why_id: W004
  type: implementation
  claim: "在使用 newspaper3k 抓取新闻正文时显式关闭了图片下载和缓存，并强制截断前 1500 个字符。"
  reasoning_chain: "抓取新闻网页的唯一目的是提供给 LLM 作为舆情上下文 → 纯文本模型无法直接消费网页内嵌图片，下载图片会无谓增加带宽和耗时 → 本地缓存不利于无状态的 GitHub Actions 执行 → 将完整长文送入 LLM 会大幅增加 Token 成本且引入噪音，故只截取前 1500 字符获取核心事实即可。"
  evidence:
    - type: CODE
      source: "src/search_service.py:73-74"
    - type: CODE
      source: "src/search_service.py:82-85"
  contrast: "不保留原生网页的 HTML 结构、不下载图片以及不输入全量文本，因为在纯文本舆情分析场景下，多媒体资源和冗长正文只会拖累处理速度并消耗过多 Token 预算。"

- why_id: W005
  type: constraint
  claim: "将用于 LLM Token 统计的 tiktoken 库版本严格限制在 `<0.12.0`。"
  reasoning_chain: "系统需要 tiktoken 进行上下文 Token 长度的预估和截断 → tiktoken >= 0.12.0 引入了插件注册机制，可能导致依赖冲突或运行环境崩溃（Issue #537） → 为保证项目在各种自动化环境（尤其是无人值守的 GitHub Actions）下的高可靠性，选择了牺牲使用最新版本来锁定兼容性。"
  evidence:
    - type: CODE
      source: "requirements.txt:30"
    - type: INFERENCE
      source: "开源自动化工具对依赖的破坏性更新极其敏感，锁定次要版本号是防御上游破坏性更新的直接手段。"
  contrast: "不选择使用灵活的版本约束（如 `>=0.8.0`），因为自动化 CI/CD 流程中意外升级有缺陷的依赖库会导致所有定时运行的用户任务全部失效。"

- why_id: W006
  type: implementation
  claim: "实现递归解包异常链（unwrap_exception）以提取底层真正的错误原因。"
  reasoning_chain: "在多数据源并发请求、多层封装的复杂网络交互中，底层的实际网络错误（如 SSLError、Timeout）往往会被 requests 或 tenacity 等上层库多次包装为泛化异常 → 如果直接记录顶层异常，日志会失去关键调试线索，且无法基于底层错误类型进行精确重试 → 遍历 `__cause__` 和 `__context__` 找到根因，可建立稳定的异常摘要。"
  evidence:
    - type: CODE
      source: "data_provider/base.py:31-43"
    - type: CODE
      source: "data_provider/base.py:46-51"
  contrast: "不直接使用 `str(exc)` 记录或抛出顶层异常，因为这通常只能得到无意义的包装器类名，掩盖了底层网络或数据层面的真实故障类型。"

- why_id: W007
  type: implementation
  claim: "在规范化股票代码时，统一剥离 A 股的交易所前后缀，但刻意保留港股的“HK”前缀。"
  reasoning_chain: "A 股的代码体系（6位数字）在大多数底层行情爬虫接口（如 efinance/akshare）中，纯数字形式足以唯一标识，保留前后缀反而会导致查询 API 报错 → 但港股代码通常为 5 位数字，如果去掉“HK”前缀，在混排查询时极易与 A 股部分股票或基金代码产生解析混淆，且很多接口对港股有特定前缀要求 → 因此豁免港股的清洗规则。"
  evidence:
    - type: CODE
      source: "data_provider/base.py:54-84"
    - type: CODE
      source: "data_provider/akshare_fetcher.py:84-106"
  contrast: "不将所有市场的股票代码强制统一清洗为纯数字格式，因为非 A 股市场（如港股）的纯数字形式缺乏在跨接口查询时的全局上下文唯一性，会导致路由错误。"
```
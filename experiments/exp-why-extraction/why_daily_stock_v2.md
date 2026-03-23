# WHY 提取报告：daily_stock_analysis（Sonnet v2）

```yaml
- why_id: W001
  type: architecture
  claim: "数据层采用策略模式 + 优先级故障切换链，而不是单一数据源或随机轮询"
  reasoning_chain: >
    A 股免费数据源（东财/新浪/腾讯）依赖爬虫，单点封禁风险极高 →
    项目维护了 6 个 Fetcher（efinance P0 → akshare P1 → tushare/pytdx P2 → baostock P3 → yfinance P4），
    按 priority 字段排序后顺序尝试 →
    任一 Fetcher 失败时自动切换到下一个，并记录详细失败原因 →
    全部失败才抛出汇总异常；同时对美股代码做"快速路径"硬编码直接路由到 YfinanceFetcher，
    避免无效尝试中国数据源。
  evidence:
    - type: CODE
      source: "data_provider/base.py:L650-L693（_init_default_fetchers 初始化优先级链）"
      detail: "注释明确标注 Priority 0~4，并在 Tushare Token 存在时动态提升其优先级至 0"
    - type: CODE
      source: "data_provider/base.py:L738-L811（get_daily_data 故障切换循环）"
      detail: >
        美股走 L739-L773 快速路径直接路由 YfinanceFetcher；A 股走 L775-L811 顺序轮询，
        每次切换打印 [数据源切换] 日志，所有失败后拼接 error_summary 抛出
    - type: DOC
      source: "requirements.txt:L13-L18"
      detail: "注释显式标注 Priority 0~4 及各数据源特点（免费/需Token/爬虫/备选）"
  contrast: >
    随机轮询无法保证数据质量（低优先级源数据更新慢、字段更少）；
    单一数据源一旦被封禁整个系统停摆；自建统一 API 网关维护成本过高且对个人项目过度工程。

- why_id: W002
  type: selection
  claim: "美股数据统一路由到 YfinanceFetcher，不经过 A 股数据源链路"
  reasoning_chain: >
    A 股数据源（efinance/akshare/tushare/pytdx/baostock）均针对中国市场设计，
    对美股股票代码（纯字母 Ticker）无法返回有效数据，盲目尝试只会积累无效超时 →
    项目在 DataFetcherManager.get_daily_data 入口处检测 is_us_index_code/is_us_stock_code →
    命中则直接定位列表中的 YfinanceFetcher 并只尝试它，失败即终止，不再向下尝试中国数据源。
  evidence:
    - type: CODE
      source: "data_provider/base.py:L738-L773（美股快速路径）"
      detail: >
        L739：if is_us_index_code(stock_code) or is_us_stock_code(stock_code)
        进入专用分支；L740-L768 在 fetcher 列表中线性查找 name=='YfinanceFetcher' 直接调用；
        break 后若失败立即 raise DataFetchError，不继续尝试其他 Fetcher
    - type: DOC
      source: "requirements.txt:L18"
      detail: "注释：'Priority 4: Yahoo Finance (Fallback)'，暗示 yfinance 仅作终态兜底"
    - type: DOC
      source: "README.md（repo_facts L102）"
      detail: "明文声明：'美股历史数据与实时行情统一使用 YFinance，确保复权一致性'"
  contrast: >
    如果让美股代码走完整的 5 轮故障切换，每轮都会超时后才能继续，导致美股分析比 A 股慢数倍；
    且中国数据源对复权逻辑与 YFinance 不同，强行拼接会导致数据不一致。

- why_id: W003
  type: implementation
  claim: "LLM 响应中的筹码结构（chip_structure）不完全信任 LLM 填充，事后用确定性数据覆盖占位符"
  reasoning_chain: >
    LLM 对精确数值字段（获利比例、90%集中度）容易返回 N/A / 0 / 空字符串等占位值 →
    AkShare 可以确定性地拿到筹码数据（ChipDistribution 对象）→
    pipeline 在 analyze_stock() Step 7.6 / _analyze_with_agent() 中，拿到 result 后调用
    fill_chip_structure_if_needed(result, chip_data) →
    该函数检查 dashboard.data_perspective.chip_structure 中每个字段是否为占位符（_is_value_placeholder），
    只替换占位值、保留 LLM 已填写的非占位字段 →
    同时 _derive_chip_health 用 profit_ratio 和 concentration_90 确定性推导 chip_health 标签。
  evidence:
    - type: CODE
      source: "src/analyzer.py:L100-L178（_is_value_placeholder + fill_chip_structure_if_needed）"
      detail: >
        L101-L107 定义占位符集合（None/0/空/"N/A"/"数据缺失"/"未知"）；
        L156-L178 fill_chip_structure_if_needed 只覆盖占位键，
        L176：logger.info('[chip_structure] Filled placeholder chip fields from data source (Issue #589)')
    - type: CODE
      source: "src/core/pipeline.py:L359-L361（Step 7.6）"
      detail: >
        注释明确标注 "chip_structure fallback (Issue #589)"；
        L361：fill_chip_structure_if_needed(result, chip_data)，在 Step 7 AI 分析之后立即执行
    - type: CODE
      source: "src/core/pipeline.py:L601-L603（Agent 模式同样执行）"
      detail: >
        Agent 模式下同样执行 L603：fill_chip_structure_if_needed(result, chip_data)，
        注释 "chip_structure fallback (Issue #589), before save_analysis_history"
  contrast: >
    完全信任 LLM 填充：LLM 幻觉会导致筹码数据失真，影响决策；
    完全用程序计算替代 LLM：会丢失 LLM 对筹码结构的文字解读（chip_health 标签以外的语义描述）；
    当前方案取中间路：数值由程序保证精确，文字解读留给 LLM。

- why_id: W004
  type: constraint
  claim: "对 DeepSeek 思考模式（reasoning_content）做模型名判断而非 API 特性探测，且区分自动返回型与需手动激活型"
  reasoning_chain: >
    LiteLLM 调用时，deepseek-reasoner/deepseek-r1/qwq 等模型的 API 默认返回 reasoning_content 字段，
    如果再通过 extra_body 传 {"thinking": {"type": "enabled"}} 会导致 400 错误 →
    而 deepseek-chat 等模型需要显式 opt-in extra_body 才能开启思考模式 →
    项目维护两张独立映射表（_AUTO_THINKING_MODELS 和 _OPT_IN_THINKING_MODELS），
    get_thinking_extra_body() 优先检查是否在 auto 列表中（返回 None），
    再检查是否在 opt-in 列表中（返回激活 payload），其余模型不传 extra_body。
  evidence:
    - type: CODE
      source: "src/agent/llm_adapter.py:L48-L92（_AUTO_THINKING_MODELS + get_thinking_extra_body）"
      detail: >
        L49：_AUTO_THINKING_MODELS = ["deepseek-reasoner", "deepseek-r1", "qwq"]；
        L52-L54：_OPT_IN_THINKING_MODELS = {"deepseek-chat": {"thinking": {"type": "enabled"}}}；
        L80-L92 注释明文说明："sending extra_body would cause 400 because the API already enables thinking by default"
    - type: CODE
      source: "src/analyzer.py:L750-L752（调用点）"
      detail: >
        L750：extra = get_thinking_extra_body(model_short)；
        L751-L752：if extra: call_kwargs["extra_body"] = extra；
        仅在需要时才注入 extra_body
    - type: DOC
      source: "README.md（repo_facts L146）"
      detail: "文档说明：'DeepSeek 思考模式（deepseek-reasoner、deepseek-r1、qwq、deepseek-chat）按模型名自动识别，无需额外配置'"
  contrast: >
    用 API 特性探测（先发送再捕获 400）：增加每次初始化延迟和失败日志；
    统一不传 extra_body：opt-in 模型无法开启思考模式，推理质量下降；
    统一传 extra_body：auto-thinking 模型报 400 导致调用失败。

- why_id: W005
  type: implementation
  claim: "实时行情数据在代码层面保留 20 分钟全量缓存，而不是按股票代码细粒度缓存"
  reasoning_chain: >
    东方财富/efinance 的实时行情接口是全市场一次性拉取（5000+ 只股票）而非单股查询 →
    对于批量分析 30 只自选股的场景，如果每只股票触发一次 API 调用，
    相当于 30 次全量拉取，既浪费流量又触发封禁 →
    项目用一个共享字典 _realtime_cache（data/timestamp/ttl 三字段）
    存储最近一次全量拉取结果，TTL 设为 1200 秒（20 分钟），
    注释明确给出计算依据：30 只股票 5 分钟内分析完，20 分钟足够覆盖整个批次。
  evidence:
    - type: CODE
      source: "data_provider/akshare_fetcher.py:L683-L698（_realtime_cache 定义）"
      detail: >
        L683-L691：注释逐条解释 TTL=1200 的三个原因（批量场景/实时性/防封禁）；
        L687-L691：_realtime_cache = {'data': None, 'timestamp': 0, 'ttl': 1200}；
        同文件有同结构的 _etf_realtime_cache（L694-L698）
    - type: CODE
      source: "data_provider/base.py:L818-L897（prefetch_realtime_quotes）"
      detail: >
        L854-L871 检测当前优先级中是否包含 efinance/akshare_em 等全量接口；
        L874-L877：少于 5 只股票跳过预取（逐个查询更高效）；
        L883-L890：只用第一只股票触发 get_realtime_quote，缓存自动填充全市场数据
    - type: DOC
      source: "data_provider/akshare_fetcher.py:L684-L686（行内注释）"
      detail: "TTL=20分钟：批量分析场景通常30只股票在5分钟内分析完，20分钟足够覆盖；实时性：股票分析不需要秒级实时数据，20分钟延迟可接受"
  contrast: >
    按股票代码细粒度缓存：全量接口一次拉 5000 条，若只缓存其中 30 条，
    下次新股票请求时仍需重新拉全量，缓存命中率极低；
    不缓存：同一批次 30 只股票各触发一次全量拉取，触发速率限制或封禁。

- why_id: W006
  type: negation
  claim: "FundamentalSnapshot 表设计为纯写入（write-only），主链路完全不依赖读取该表"
  reasoning_chain: >
    基本面数据（估值/成长/龙虎榜/板块）来源多样且经常局部失败 →
    如果将基本面快照纳入主分析链路的读取依赖，一旦写入失败或数据不完整，
    就会阻塞 AI 分析步骤 →
    项目在 pipeline 的 analyze_stock() 中，先 get_fundamental_context()
    聚合基本面数据，然后通过 db.save_fundamental_snapshot() 写入快照，
    但该写入用 try/except 包裹，任何异常只打 debug 日志不抛出；
    读取路径（get_analysis_context / AI prompt 构建）从不查询 fundamental_snapshot 表，
    基本面数据只通过内存字典传递给当次 AI 分析。
  evidence:
    - type: CODE
      source: "src/storage.py:L182-L204（FundamentalSnapshot 模型定义）"
      detail: >
        类 docstring 明确标注：'仅用于写入，主链路不依赖读取该表，便于后续回测/画像扩展'；
        L188：__tablename__ = 'fundamental_snapshot'；
        表中无对 analysis_history 的外键依赖，无读取接口
    - type: CODE
      source: "src/core/pipeline.py:L245-L255（写入快照逻辑）"
      detail: >
        L245：注释 "P0: write-only snapshot, fail-open, no read dependency on this table"；
        L246-L254：save_fundamental_snapshot() 写入；
        L255：except → logger.debug 仅记录日志，不中断主流程
  contrast: >
    如果 FundamentalSnapshot 变为读写双向依赖：写入失败时需要降级逻辑；
    历史快照查询会引入额外的 DB 查询增加延迟；
    且基本面数据本身有 TTL（分析完即过期），持久化读取的业务价值有限。
    write-only 设计让回测和调试可以事后重放数据，而不干扰实时分析链路。

- why_id: W007
  type: architecture
  claim: "trading discipline（不追高 / MA 多头排列）作为硬编码规则写入 SYSTEM_PROMPT，而不是作为可配置参数"
  reasoning_chain: >
    项目的目标用户是个人投资者，核心价值主张之一是"内置交易纪律"，
    防止用户因情绪追高亏损 →
    乖离率 > 5% 不买入、MA5>MA10>MA20 作为绝对约束写入 GeminiAnalyzer.SYSTEM_PROMPT，
    并在 prompt 模板中要求 LLM "必须严格遵守" →
    同时 StockTrendAnalyzer 在 Python 层面计算 bias_ma5/bias_ma10 并在
    context 中传给 LLM，形成代码事实层（计算乖离率）+ LLM 解读层（生成建议）的双层架构。
  evidence:
    - type: CODE
      source: "src/analyzer.py:L439-L480（SYSTEM_PROMPT 交易纪律部分）"
      detail: >
        L440：注释 "## 核心交易理念（必须严格遵守）"；
        L444：'乖离率 > 5%：严禁追高！直接判定为"观望"'；
        L451：'多头排列必须条件：MA5 > MA10 > MA20，只做多头排列的股票，空头排列坚决不碰'
    - type: CODE
      source: "main.py:L18-L22（主模块 docstring）"
      detail: >
        模块 docstring 写明：'交易理念（已融入分析）：严进策略：不追高，乖离率 > 5% 不买入；
        趋势交易：只做 MA5>MA10>MA20 多头排列'，说明这是刻意的产品决策而非临时约束
    - type: DOC
      source: "README.md（repo_facts L104-L112）"
      detail: >
        README 有独立的'内置交易纪律'章节，明确列出'严禁追高'和'趋势交易'规则，
        并标注'乖离率超阈值（默认 5%，可配置）'，但 SYSTEM_PROMPT 中硬编码的是绝对禁止，
        可配置仅用于警告提示，形成软约束（用户告知）+ 硬约束（LLM 决策）分层
  contrast: >
    完全可配置：用户可能关闭追高保护，失去产品差异化价值；
    仅前端校验：LLM 层仍可能给出追高建议，用户可能绕过；
    写入 SYSTEM_PROMPT：LLM 生成建议时即遵守约束，产品层面无法绕过。
```

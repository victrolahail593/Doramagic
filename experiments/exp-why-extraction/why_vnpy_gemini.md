```yaml
- why_id: W001
  type: implementation
  claim: "UI组件的做多与做空配色采用中国市场红涨绿跌的标准"
  reasoning_chain: "目标用户主要是国内交易员 → 国内金融市场（A股、国内期货）习惯红色代表上涨/做多，绿色代表下跌/做空 → UI组件硬编码COLOR_LONG为红色、COLOR_SHORT为绿色"
  evidence:
    - type: CODE
      source: "vnpy/trader/ui/widget.py，第44-45行 (COLOR_LONG = QtGui.QColor('red'))"
  contrast: "没有采用国际金融通用的绿涨红跌规则，因为项目是 'By Traders, For Traders'，优先满足国内受众的使用直觉。"

- why_id: W002
  type: implementation
  claim: "使用 Decimal 对象来进行价格的 tick 最小变动价位对齐计算"
  reasoning_chain: "交易系统对价格精度要求极高 → 原生浮点数（float）运算存在精度丢失问题（如0.1+0.2的经典问题） → 在调整价格到最小变动价位（pricetick）时，通过转换为字符串并构造 Decimal 进行除法取整，最后再转回 float → 保证报单价格绝对符合交易所严格的跳价规则，避免被拒单"
  evidence:
    - type: CODE
      source: "vnpy/trader/utility.py，第111-133行 (round_to, floor_to, ceil_to 函数)"
  contrast: "没有直接使用常规的浮点数取整逻辑（如 round(value / target) * target），用性能换取金融计算的绝对精确性。"

- why_id: W003
  type: architecture
  claim: "优先使用当前工作目录下的 `.vntrader` 作为运行时主目录，否则才使用用户主目录"
  reasoning_chain: "量化交易经常需要在不同的策略、不同账户或不同测试环境间切换 → 如果统一将所有配置和数据固化在系统用户主目录下，会导致配置冲突 → 提供在当前执行路径（cwd）下寻找 `.vntrader` 的机制 → 实现了项目的『便携式/多环境隔离』运行能力"
  evidence:
    - type: CODE
      source: "vnpy/trader/utility.py，第33-51行 (_get_trader_dir 函数)"
  contrast: "没有像传统软件一样强制将数据写死在系统级用户目录（如 ~/.vntrader），这方便高阶用户通过不同的目录启动来隔离多套独立的交易系统环境。"

- why_id: W004
  type: selection
  claim: "将标的代码与交易所代码拼接成 vt_symbol 作为全局唯一标识符"
  reasoning_chain: "系统作为一个多市场交易平台，需要支持国内外数十种交易接口（Gateway） → 不同的交易所可能存在相同的品种代码（如A股和港股或不同期货交易所的简码重合） → 将 `symbol` 与 `exchange.value` 用 `.` 强行连接（如 IF2101.CFFEX） → 形成系统内部绝对唯一的数据主键"
  evidence:
    - type: CODE
      source: "vnpy/trader/utility.py，第26-30行 (extract_vt_symbol, generate_vt_symbol 函数)"
  contrast: "没有引入复杂的复合主键对象或由系统生成 UUID，而是以极简的字符串拼接解决了跨市场标的标识冲突问题，兼顾了可读性与唯一性。"

- why_id: W005
  type: architecture
  claim: "在 Alpha 回测引擎中将信号提取脱离回测循环，作为 DataFrame (signal_df) 预先传入"
  reasoning_chain: "AI/ML 策略涉及大量的多因子矩阵运算和深度学习模型推理 → 如果在传统的事件驱动回测循环（逐根 K 线）中调用模型推理，不仅无法利用向量化加速，且性能极其低下 → 将机器学习的预测过程前置，生成包含历史全量信号的面板数据（signal_df）传入引擎 → 回测引擎只需根据预先算好的信号处理执行和资金撮合逻辑，极大提升了回测速度"
  evidence:
    - type: CODE
      source: "vnpy/alpha/strategy/backtesting.py，第86-90行 (add_strategy 方法显式要求传入 signal_df)"
  contrast: "偏离了传统 CTA 策略回测在 `on_bar` 事件中实时计算技术指标并生成信号的模式，专门为机器学习量化场景（批量向量化计算）重构了工作流。"

- why_id: W006
  type: selection
  claim: "在核心 Alpha 模块中重度引入 polars 替代部分 pandas 职能"
  reasoning_chain: "vnpy.alpha 面向一站式多因子机器学习策略，涉及海量特征工程计算 → pandas 在处理大规模全市场面板数据时存在严重的内存溢出和性能瓶颈（受限于 GIL 和单线程） → 引入底层基于 Rust 开发、支持多线程并发和延迟计算（Lazy Execution）的 polars 库 → 以极小的时间成本完成复杂因子的批量特征运算"
  evidence:
    - type: CODE
      source: "vnpy/alpha/strategy/backtesting.py，第8行 (import polars as pl) 以及 pyproject.toml [project.optional-dependencies] 中的 polars"
  contrast: "尽管整个框架的传统 CTA 模块仍深度依赖 pandas，但面对 AI/ML 模块的高算力需求，团队没有被技术栈的一致性束缚，果断采用了性能更强的新生代工具 polars。"
```
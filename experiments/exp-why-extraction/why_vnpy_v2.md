# WHY 提取报告：vnpy（Sonnet v2）

```yaml
- why_id: W001
  type: architecture
  claim: "vnpy 用事件引擎（EventEngine）作为整个交易平台的通信骨架，所有模块通过事件类型字符串解耦，而不是直接调用彼此的方法"
  reasoning_chain: >
    EventEngine 持有一个 Queue 和一个专用线程，所有数据（tick、order、trade、position）
    都被封装成 Event 对象投入队列 →
    Gateway 只调用 on_tick/on_order 等回调，这些回调内部调用 event_engine.put() →
    OmsEngine 通过 register() 订阅感兴趣的事件类型，与 Gateway 完全不知道彼此的存在 →
    这使得同一套代码可以接入数十个不同的交易接口（CTP、XTP、Interactive Brokers 等），
    新接口只需实现 BaseGateway 抽象类，无需修改任何上层模块
  evidence:
    - type: CODE
      source: "vnpy/event/engine.py:L33-L78 — EventEngine 类定义，Queue + Thread + _handlers defaultdict 构成事件分发核心"
    - type: CODE
      source: "vnpy/trader/gateway.py:L86-L115 — on_tick/on_trade/on_order 统一调用 on_event()，on_event() 内部调用 event_engine.put()"
    - type: CODE
      source: "vnpy/trader/engine.py:L363-L371 — OmsEngine.register_event() 通过字符串事件类型注册处理函数，与 Gateway 实现零耦合"
  contrast: >
    替代方案是直接函数调用或观察者模式（Gateway 持有 OmsEngine 引用直接调用其方法）。
    但交易平台在运行时可能同时接入多个 Gateway，且 Gateway 的回调来自不同的行情/交易线程；
    事件队列天然解决了多线程竞态问题，而直接调用则需要在每个接口层加锁，维护成本极高。

- why_id: W002
  type: constraint
  claim: "vnpy 为中国期货交易所（SHFE/INE）单独实现了今仓/昨仓区分逻辑（OffsetConverter），这是强制性的业务约束，而非软件设计选择"
  reasoning_chain: >
    上海期货交易所（SHFE）和上海国际能源交易中心（INE）强制要求平仓时必须区分
    「平今仓」（CLOSETODAY）和「平昨仓」（CLOSEYESTERDAY） →
    如果策略发出通用的 Offset.CLOSE 指令，直接发送到 SHFE 会被拒单 →
    vnpy 在 OmsEngine 层拦截所有订单请求，OffsetConverter 根据合约所属交易所自动拆分 →
    策略代码无需感知交易所的仓位规则差异，可以用统一接口写策略
  evidence:
    - type: CODE
      source: "vnpy/trader/converter.py:L81-L107 — update_trade() 针对 SHFE/INE 交易所用 short_yd -= trade.volume 处理 Offset.CLOSE，其他交易所用 short_td -= trade.volume"
    - type: CODE
      source: "vnpy/trader/converter.py:L168-L200 — convert_order_request_shfe() 将 Offset.CLOSE 指令自动拆分为 CLOSETODAY + CLOSEYESTERDAY 两笔订单"
    - type: CODE
      source: "vnpy/trader/converter.py:L390-L402 — is_convert_required() 只对非净仓模式（非 net_position）合约启用转换，净仓模式合约（如港股）不需要区分今昨仓"
  contrast: >
    替代方案是让策略开发者自行管理今昨仓。但这意味着每个使用 SHFE 合约的策略都需要
    复制相同的仓位跟踪逻辑，且容易出错（今仓可用量计算涉及冻结量和已报但未成交的订单）。
    将这一「脏逻辑」下沉到框架层是正确的关注点分离。

- why_id: W003
  type: implementation
  claim: "vnpy 用 Decimal 而非 float 做价格取整运算（round_to/floor_to/ceil_to），是为了规避浮点数精度陷阱"
  reasoning_chain: >
    期货合约有最小价格跳动（pricetick），策略计算出的目标价格必须对齐到 pricetick 的整数倍 →
    如果直接用 float 做除法再取整，0.1 这类二进制无法精确表示的数会产生累积误差
    （例如 0.1 * 3 在 float 中不等于 0.3）→
    将 float 先转为 str 再构造 Decimal，避免了 Decimal(0.1) 继承 float 精度问题 →
    最终结果转回 float 供下游使用，接口层只在边界处做一次精确转换
  evidence:
    - type: CODE
      source: "vnpy/trader/utility.py:L105-L112 — round_to() 中 Decimal(str(value)) / Decimal(str(target)) 的完整实现，注释缺失但模式一致"
    - type: CODE
      source: "vnpy/alpha/strategy/backtesting.py:L733 — 回测引擎 send_order() 调用 round_to(price, self.priceticks[vt_symbol])，确保回测中报单价格符合真实交易规则"
  contrast: >
    直接用 round(value / target) * target 在大多数情况下可用，但对 0.05、0.1、0.025
    这类常见期货 pricetick 会出现数值漂移。使用 Decimal 是业界做法，但须注意
    Decimal(float) 直接构造会继承 float 误差，必须经过 str 中转，这是此处实现的关键细节。

- why_id: W004
  type: architecture
  claim: "vnpy 的 alpha 模块用 Polars 而非 Pandas 作为多标的截面数据的主要 DataFrame 引擎，是为了处理机器学习因子计算中的大规模多股票截面数据"
  reasoning_chain: >
    alpha 模块需要同时处理数百只股票的因子特征（Alpha158 包含158个特征），
    每只股票有多年日线/分钟线数据 →
    Polars 使用 Apache Arrow 列式存储，在多列并行计算上比 Pandas 快数倍，
    且内存占用更低（零拷贝切片） →
    信号生成、回测日结算都使用 pl.DataFrame，同一数据结构贯穿整个 alpha 工作流 →
    但 vnpy 核心 trader 模块（行情、报单、持仓）依然用 Python dataclass（BarData、OrderData），
    说明 Polars 是 alpha 模块的刻意选择，而非全局替换
  evidence:
    - type: CODE
      source: "vnpy/alpha/lab.py:L1-L9 — 文件顶部导入 polars as pl，核心数据存储以 Parquet 格式落盘（write_parquet/read_parquet），与 Pandas 的 CSV/HDF5 完全不同"
    - type: CODE
      source: "vnpy/alpha/lab.py:L219-L233 — load_bar_df() 用 Polars 原生 expr API（pl.col()、with_columns()、sum_horizontal()）做停牌日过滤，体现了 Polars lazy evaluation 的使用意图"
    - type: CODE
      source: "vnpy/alpha/strategy/backtesting.py:L525-L527 — BacktestingEngine 中 daily_df 和 signal_df 类型注解均为 pl.DataFrame，回测核心数据路径全程 Polars"
  contrast: >
    Pandas 是量化社区的默认选择，Qlib（vnpy alpha 模块的灵感来源）使用 Pandas。
    但 Pandas 在多股票大规模因子计算时内存峰值高（中间操作产生拷贝），
    且缺乏原生并行列运算。vnpy 选择 Polars 是为了在不换算法的前提下提升性能上限。

- why_id: W005
  type: selection
  claim: "vnpy 的 RPC 层用两个独立 ZeroMQ socket（REP + PUB）分别承载请求-响应和主动推送，而非只用一个双向连接"
  reasoning_chain: >
    客户端对服务端有两种通信需求：① 同步调用（查询账户、查持仓）需要请求-应答语义；
    ② 服务端主动推送行情/订单更新给客户端，是单向广播 →
    ZeroMQ REP socket 只能处理严格的请求-应答对，无法在等待应答期间推送消息 →
    PUB socket 是广播推送，不需要客户端显式请求 →
    用两个 socket 组合实现了「调用+推送」的完整 RPC 语义，且两个通道互不阻塞
  evidence:
    - type: CODE
      source: "vnpy/rpc/server.py:L25-L28 — RpcServer.__init__() 中显式创建两个 socket：socket_rep（zmq.REP）和 socket_pub（zmq.PUB）"
    - type: CODE
      source: "vnpy/rpc/server.py:L83-L114 — run() 只在 _socket_rep 上 poll，通过 send_pyobj/recv_pyobj 做同步调用；publish() 方法独立通过 _socket_pub 发布，两个通道完全独立"
  contrast: >
    替代方案是用单个 ZeroMQ DEALER/ROUTER 或 PAIR socket 复用一条连接，
    或者用 HTTP + WebSocket 分别承载两种模式。
    但 ZeroMQ 的双 socket 方案更轻量，不引入 HTTP 协议栈，
    且 REQ-REP 的严格配对语义天然防止了客户端请求乱序的问题。

- why_id: W006
  type: negation
  claim: "vnpy 的 BaseGateway 不提供「重连」的默认实现，而是把重连责任完全推给各接口子类——这是刻意规定而非遗漏"
  reasoning_chain: >
    不同交易接口的连接协议差异极大：CTP 是 C++ SDK 的回调模型，XTP 是自研协议，
    Interactive Brokers 是基于 socket 的私有协议 →
    重连逻辑（何时重连、重连前是否需要重新鉴权、断线期间的订单状态如何处理）
    在每个接口中完全不同，无法抽象出通用实现 →
    BaseGateway 的文档注释中明确写道「automatically reconnect if connection lost」是对子类的要求，
    而不是父类提供的能力 →
    强行在基类实现重连会引入错误的抽象，反而让子类难以覆盖或扩展
  evidence:
    - type: CODE
      source: "vnpy/trader/gateway.py:L38-L70 — BaseGateway 的类级注释明确列出「automatically reconnect if connection lost」作为子类必须满足的 requirement，但父类的 connect()/close() 只有 pass"
    - type: CODE
      source: "vnpy/trader/gateway.py:L160-L180 — connect() 的 abstractmethod docstring 写明子类需要处理连接、查询合约/账户/持仓/订单，但没有重连相关的钩子方法或模板方法"
  contrast: >
    替代设计是在 BaseGateway 中实现一个带指数退避的通用重连循环，子类覆盖 _connect_impl()。
    这在连接协议统一的场景（如纯 REST API 网关）是合理的。
    但期货接口多为 C++ SDK 的 session 对象，其生命周期管理（何时可以安全销毁并重建）
    无法用 Python 的通用重试框架描述，强行统一会让边界案例更难处理。

- why_id: W007
  type: implementation
  claim: "vnpy 的 ArrayManager 用固定大小的 numpy 数组 + 滚动覆盖（左移一位）存储时间序列，而不是用 Python list 或 deque"
  reasoning_chain: >
    策略的技术指标计算（SMA、RSI、ATR 等）需要在每根 K 线结束后立即调用 TA-Lib →
    TA-Lib 的 C 函数接受 numpy ndarray 作为输入，而非 Python list →
    如果用 deque，每次调用 TA-Lib 都需要 np.array(deque) 做一次全量拷贝，O(n) 开销 →
    固定大小 ndarray + 滚动覆盖（self.open_array[:-1] = self.open_array[1:]）实现了
    O(n) 时间的窗口维护，但消除了每次指标计算时的额外分配 →
    inited 标志在 count >= size 后才置 True，防止在数据不足时产生错误的指标值
  evidence:
    - type: CODE
      source: "vnpy/trader/utility.py:L501-L531 — ArrayManager.__init__() 预分配7个 np.zeros(size) 数组；update_bar() 中 open_array[:-1] = open_array[1:] 实现原地左移滚动"
    - type: CODE
      source: "vnpy/trader/utility.py:L586-L595 — sma() 直接将 self.close（已是 ndarray）传入 talib.SMA()，无需中间转换；返回 result_array[-1] 取最新值"
  contrast: >
    deque(maxlen=n) 是 Python 中实现滑动窗口的惯用法，内存效率更高（不需要左移）。
    但 deque 不能直接传给 TA-Lib，必须每次转换为 ndarray。
    对于高频策略（每秒处理数百根 tick 合成的分钟线），这个拷贝开销不可忽视。
    固定 ndarray 的方案是以轻微的 CPU 开销（左移）换取无分配的指标计算路径。
```

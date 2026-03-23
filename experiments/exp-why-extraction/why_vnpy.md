# WHY 提取报告：VeighNa (vnpy)

> 项目：VeighNa v4.3.0 — 基于 Python 的开源量化交易框架
> 分析时间：2026-03-13

---

```yaml
- why_id: W001
  type: architecture
  claim: "整个平台以单队列事件引擎为核心，所有模块通过事件总线通信，而非直接调用彼此"
  reasoning_chain: >
    交易系统需要同时处理来自多个 Gateway 的异步推送（Tick、Order 回报、成交），
    以及多个 App（CTA 策略、OMS、日志）对这些数据的处理 →
    如果各模块直接互相调用，任何一个 Gateway 的延迟都会阻塞其他模块 →
    将所有数据推送统一入队（EventEngine._queue: Queue），
    单线程消费（EventEngine._run）保证处理顺序确定性 →
    模块之间零耦合，Gateway 只负责推事件，不知道谁在监听。
  evidence:
    - type: CODE
      source: "vnpy/event/engine.py:51–63 — _run() 在独立线程中 block=True 从 Queue 取事件"
    - type: CODE
      source: "vnpy/event/engine.py:33–53 — EventEngine 持有单一 _queue，两个线程：_thread（消费）+ _timer（心跳）"
    - type: CODE
      source: "vnpy/trader/gateway.py:86–99 — BaseGateway.on_tick() 仅调用 event_engine.put()，不直接通知任何策略"
    - type: CODE
      source: "vnpy/trader/engine.py:363–371 — OmsEngine.register_event() 向 EventEngine 注册，而非被 Gateway 直接引用"
  contrast: >
    另一种做法是 Gateway 持有策略引用，直接回调（观察者模式的直接调用版）。
    但这会导致：回调链阻塞（一个策略卡死会延误其他策略）、模块强耦合（Gateway 需要知道上层模块），
    以及多线程安全问题。事件队列将异步推送和同步处理完全解耦。

- why_id: W002
  type: constraint
  claim: "Gateway 向上推送的所有 XxxData 对象必须是不可变的（immutable-by-convention），修改前需 copy.copy()"
  reasoning_chain: >
    EventEngine 的单消费线程处理事件时，多个 Handler 会拿到同一个 event.data 对象的引用 →
    OmsEngine 在 process_order_event 里缓存 order 引用，
    如果 Gateway 在推送后继续修改同一对象，OmsEngine 的缓存就会静默污染 →
    因此 BaseGateway 的文档明确要求："XxxData passed to callback should be constant...
    use copy.copy to create a new object before passing that data into on_xxxx"。
  evidence:
    - type: CODE
      source: "vnpy/trader/gateway.py:62–66 — 文档注释：'All the XxxData passed to callback should be constant...use copy.copy'"
    - type: CODE
      source: "vnpy/trader/engine.py:378–388 — OmsEngine.process_order_event() 直接将 order 存入 self.orders 字典，无防御性复制"
    - type: CODE
      source: "vnpy/trader/converter.py:56–62 — PositionHolding.update_order_request() 中对 req 调用 create_order_data 而非直接存 req，说明 request 对象同样遵守此约定"
  contrast: >
    如果 Gateway 内部用同一对象反复更新状态（常见的 C-binding 回调优化模式），
    会导致缓存引用指向的数据被 Gateway 线程静默修改，产生极难调试的竞态条件。
    框架选择以文档约束代替强制不可变类型（如 NamedTuple/frozen dataclass），
    是因为 dataclass 的可变性在某些场景（如 BarGenerator 聚合）确实需要。

- why_id: W003
  type: implementation
  claim: "ArrayManager 使用固定大小的 numpy 数组 + 左移滚动，而不是动态追加列表"
  reasoning_chain: >
    策略的 on_bar() 回调在每个 Tick 周期内同步执行，必须快速完成 →
    若用 list.append() + 转换为 np.ndarray，每次均摊 O(1) 但有 GC 压力，
    且每次计算指标都要重新 slice 整个列表 →
    固定大小数组（np.zeros(size)）分配一次，更新时整体左移一位（array[:-1] = array[1:]），
    只写最后一格（array[-1] = new_value） →
    talib 函数直接接受 np.ndarray，无转换开销；
    内存布局始终连续，CPU cache 友好。
  evidence:
    - type: CODE
      source: "vnpy/trader/utility.py:509–531 — ArrayManager.update_bar()：7 行连续的 array[:-1] = array[1:] 左移操作"
    - type: CODE
      source: "vnpy/trader/utility.py:495–507 — 构造函数中 np.zeros(size) 一次性分配，size 默认 100"
    - type: CODE
      source: "vnpy/trader/utility.py:586–595 — sma() 直接将 self.close（np.ndarray）传入 talib.SMA，无中间转换"
  contrast: >
    deque(maxlen=size) 是更 Pythonic 的滑动窗口容器，但 deque 不能直接传入 talib，
    每次都要 list() 或 np.array() 转换，在高频策略里产生可观的 GC 压力。
    固定 numpy 数组放弃了动态长度的灵活性，换取零额外分配的性能确定性。

- why_id: W004
  type: selection
  claim: "OffsetConverter 将国内期货「开/平/平今/平昨」的拆单逻辑集中在框架层，而不是让每个策略自行处理"
  reasoning_chain: >
    中国期货（尤其是上期所 SHFE、上期能源 INE）有独特规则：
    同一合约当日仓和隔日仓必须分开平，平今和平昨指令不同 →
    如果让策略自行处理，每个策略都要重新实现这段逻辑，且极易出错 →
    框架在 OmsEngine 层（process_contract_event）为每个 Gateway 初始化一个 OffsetConverter，
    跟踪每个合约的 long_td / long_yd / short_td / short_yd 四维持仓 →
    策略只需调用 convert_order_request(req, lock=False)，框架自动拆单。
  evidence:
    - type: CODE
      source: "vnpy/trader/converter.py:17–42 — PositionHolding 维护 long_td/long_yd/short_td/short_yd 六个字段"
    - type: CODE
      source: "vnpy/trader/converter.py:168–200 — convert_order_request_shfe()：专门处理 SHFE 平今优先逻辑"
    - type: CODE
      source: "vnpy/trader/converter.py:80–84 — update_trade() 中 exchange in {Exchange.SHFE, Exchange.INE} 的硬编码分支"
    - type: CODE
      source: "vnpy/trader/engine.py:425–427 — OmsEngine.process_contract_event()：首次收到合约推送时自动创建 OffsetConverter"
  contrast: >
    国际期货平台（如 IB）使用净持仓模式（net_position=True），无此问题，
    代码中 is_convert_required() 检查 contract.net_position 来跳过转换（converter.py:390–402）。
    将中国市场特有规则内化于框架而非策略，是对"国内期货是核心市场"这一定位的直接体现。

- why_id: W005
  type: architecture
  claim: "RPC 层同时使用 ZMQ 的两种模式：REQ-REP（同步调用）+ PUB-SUB（异步推送），而不是统一用一种"
  reasoning_chain: >
    分布式部署场景（如主进程 + 子进程策略运行器）需要两类通信：
    1. 策略发出查询/下单指令，需要等待响应确认（同步语义）→ REQ-REP 合适
    2. 服务端推送 Tick/Order 回报，不能因客户端处理慢而阻塞服务端（异步语义）→ PUB-SUB 合适 →
    如果全部用 REQ-REP，服务端推送时需要等待每个客户端 reply，违背实时行情的低延迟要求；
    如果全部用 PUB-SUB，客户端无法可靠地发送指令并获得确认。
  evidence:
    - type: CODE
      source: "vnpy/rpc/server.py:25–28 — RpcServer 同时持有 _socket_rep（zmq.REP）和 _socket_pub（zmq.PUB）"
    - type: CODE
      source: "vnpy/rpc/client.py:38–41 — RpcClient 对应持有 _socket_req（zmq.REQ）和 _socket_sub（zmq.SUB）"
    - type: CODE
      source: "vnpy/rpc/client.py:55–86 — __getattr__ 用 REQ socket 实现透明远程调用（send_pyobj + recv_pyobj）"
    - type: CODE
      source: "vnpy/rpc/server.py:116–121 — publish() 通过 PUB socket 推送，加锁保证线程安全"
    - type: CODE
      source: "vnpy/rpc/server.py:129–140 — heartbeat 通过 PUB 推送，客户端靠订阅超时检测断连"
  contrast: >
    gRPC 的双向流（bidirectional streaming）可以用单连接处理两种语义，
    但引入了 protobuf schema 和 HTTP/2 的复杂性。
    ZMQ 的原语组合方案无需 schema 定义（直接 send_pyobj 序列化 Python 对象），
    对量化交易的快速迭代更友好，代价是不支持跨语言调用。

- why_id: W006
  type: implementation
  claim: "价格精度计算（round_to / floor_to / ceil_to）通过 Decimal 中转，而不是直接用 float 运算"
  reasoning_chain: >
    期货下单价格必须是价格最小变动单位（pricetick）的整数倍 →
    float 浮点数存在精度误差（如 0.1 + 0.2 ≠ 0.3）→
    直接用 round(value / target) * target 会因浮点累积误差产生错误的价格步长 →
    将 float 先转 str 再转 Decimal，消除二进制浮点表示误差，
    用 Decimal 做整除和乘法，最后转回 float 传给 Gateway。
  evidence:
    - type: CODE
      source: "vnpy/trader/utility.py:120–127 — round_to()：Decimal(str(value)) + Decimal(str(target)) 再做整除"
    - type: CODE
      source: "vnpy/trader/utility.py:130–137 — floor_to() 同样路径：str → Decimal → floor → float"
    - type: CODE
      source: "vnpy/alpha/strategy/backtesting.py:733 — send_order() 调用 round_to(price, self.priceticks[vt_symbol])"
  contrast: >
    直接用 Python 的 round(value / pricetick) * pricetick 看似等价，
    但当 pricetick 为 0.01 这类十进制分数时，float 表示本身就有误差（0.01 → 0.01000000000000000020816…），
    导致委托价格偏离一个最小 tick，交易所会直接拒单。
    通过 str 中转是消除此类误差的标准 Python 手法，此处属于防御性编程的刻意选择。

- why_id: W007
  type: negation
  claim: "alpha 模块（ML 量化投研）没有使用 pandas，而是全面切换到 polars，但仍在特定边界保留 pandas 做转换"
  reasoning_chain: >
    alpha 模块面对的是多标的截面数据（100+ 只股票 × 数年日线 = 百万行以上）→
    因子特征工程需要大量列式运算（ts_mean、cs_rank 等），pandas 的链式操作在此规模下性能不足 →
    polars 的列式存储 + Lazy API + Rust 底层在此场景快 5–10 倍 →
    但 alphalens（因子分析）和部分 ML 库（scikit-learn）的接口仍依赖 pandas DataFrame/Series →
    框架在 I/O 边界（show_feature_performance、show_signal_performance）手动调用 .to_pandas() 转换。
  evidence:
    - type: CODE
      source: "vnpy/alpha/dataset/template.py:8–9 — 同时 import polars as pl 和 import pandas as pd"
    - type: CODE
      source: "vnpy/alpha/dataset/template.py:227–233 — show_feature_performance()：polars → pandas 只在 alphalens 调用前"
    - type: CODE
      source: "vnpy/alpha/lab.py:81–94 — save_bar_data() 用 polars DataFrame 并保存为 .parquet"
    - type: CODE
      source: "vnpy/alpha/strategy/backtesting.py:8 — import polars as pl，整个回测引擎无 pandas 依赖"
    - type: CODE
      source: "vnpy/alpha/dataset/template.py:103–116 — prepare_data() 用 multiprocessing + tqdm 并行计算因子，polars 的无 GIL 设计使多进程效益更高"
  contrast: >
    trader 模块（实盘交易核心）没有引入 polars，仍依赖 numpy/talib 做指标计算。
    这个分裂不是疏漏，而是刻意隔离：trader 模块的 ArrayManager 基于固定窗口实时流处理，
    polars 的批量列式处理反而不合适。alpha 模块是离线批量研究，两者的数据形态和性能要求根本不同。

- why_id: W008
  type: implementation
  claim: "on_tick 和 on_order 等 Gateway 回调会同时推送两个事件（全局事件 + 带 symbol/orderid 的精确事件），而不只推送一个"
  reasoning_chain: >
    系统中存在两类监听需求：
    1. OmsEngine 需要接收全部合约的所有 Tick（用于维护 ticks 字典）→ 监听全局 EVENT_TICK
    2. 策略只关心自己订阅的合约的 Tick（避免处理无关数据的开销）→ 监听 EVENT_TICK + vt_symbol →
    Gateway 在 on_tick() 里调用 on_event() 两次：
    一次用 EVENT_TICK（全局），一次用 EVENT_TICK + tick.vt_symbol（精确）→
    监听全局的收到所有推送；监听精确 topic 的只收到自己的合约，无需在 handler 内再过滤。
  evidence:
    - type: CODE
      source: "vnpy/trader/gateway.py:93–99 — on_tick()：self.on_event(EVENT_TICK, tick) + self.on_event(EVENT_TICK + tick.vt_symbol, tick)"
    - type: CODE
      source: "vnpy/trader/gateway.py:101–107 — on_trade() 同样双推：EVENT_TRADE + EVENT_TRADE + trade.vt_symbol"
    - type: CODE
      source: "vnpy/trader/gateway.py:109–115 — on_order() 双推：EVENT_ORDER + EVENT_ORDER + order.vt_orderid"
    - type: CODE
      source: "vnpy/event/engine.py:73–78 — _process() 先处理 type-specific handlers，再处理 general_handlers，两种注册方式共存"
  contrast: >
    单推全局事件 + handler 内过滤是更简单的实现，但当订阅合约数量多时，
    每个 Tick 都会唤醒所有注册了 EVENT_TICK 的 handler（包括不关心该合约的策略），
    形成 O(handlers × ticks) 的调用开销。双推方案允许策略按需精确订阅，是以代码冗余换运行效率。
```

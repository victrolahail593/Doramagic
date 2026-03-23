# WHY 提取报告：vnpy（Sonnet v3 — Stage 0 v2）

```yaml
- why_id: W001
  type: architecture
  claim: "事件驱动引擎（EventEngine）被设计为整个框架的核心总线，而非 App/Gateway 直接互相调用"
  reasoning_chain: >
    量化交易系统需要同时处理行情推送、订单状态、策略信号等异步事件 →
    如果 Gateway 直接回调 App，则形成紧耦合的调用图，新增接口或策略需要修改多处 →
    通过 EventEngine 作为消息总线，所有模块只与 EventEngine 交互 →
    Gateway 发布事件，App 订阅事件，两者完全解耦，可以独立插拔 →
    因此 vnpy.event 是被引用次数第二高（9次）的内部模块，仅次于 vnpy.trader.object
  evidence:
    - type: CODE
      source: "examples/no_ui/run.py:L9,L13-L14 — EventEngine 在 MainEngine 之前创建并作为参数传入，event_engine.register(EVENT_CTA_LOG, log_engine.process_log_event) 明确显示事件订阅模式"
    - type: CODE
      source: "examples/veighna_trader/run.py:L7-L8 — event_engine = EventEngine(); main_engine = MainEngine(event_engine)，两者构造顺序固定，EventEngine 是 MainEngine 的依赖"
    - type: DOC
      source: "README.md:L245 — 描述为'简洁易用的事件驱动引擎（event），作为事件驱动型交易程序的核心'"
  contrast: >
    不选择直接函数回调（callback hell）：在多 Gateway 多 App 的场景下，直接回调会导致 O(N×M) 的耦合关系；
    不选择 asyncio 事件循环作为主架构：CTP 等国内期货接口底层是 C++ 回调，线程模型更适配，asyncio 仅用于 REST/WebSocket 客户端层

- why_id: W002
  type: architecture
  claim: "所有功能模块（App）通过运行时注册而非编译时硬编码装入 MainEngine，且默认示例只加载极少数模块"
  reasoning_chain: >
    vnpy 面向专业交易员，不同机构/个人使用的交易品种和策略类型差异极大 →
    若所有模块内置，启动时加载 15+ App 会浪费内存并产生不必要的接口连接 →
    通过 main_engine.add_gateway() / main_engine.add_app() 按需注册，每个模块是独立 pip 包 →
    run.py 示例中大量 App 被注释掉（仅启用 CtaStrategy + CtaBacktester + DataManager），
    这不是遗忘，而是刻意展示"最小可用配置"的设计意图
  evidence:
    - type: CODE
      source: "examples/veighna_trader/run.py:L18-L38 — 13 个 add_gateway/add_app 调用被注释，只有 3 个实际启用，注释行保留是作为配置菜单供用户选择，不是历史遗留"
    - type: CODE
      source: "vnpy/trader/app.py:L1-L21 — BaseApp 是抽象类，app_name/engine_class/widget_name 等均为类变量而非实例变量，设计为注册时的元数据而非运行时状态"
    - type: DOC
      source: "README.md:L143 — '带有↑的模块代表已完成4.0升级适配测试'，其余模块可直接使用——说明模块独立性是刻意维护的"
  contrast: >
    不选择 monorepo 内置所有模块：vnpy 的 Gateway 依赖大量 C++ 二进制（如 CTP），
    若全部内置则安装包体积爆炸，且 Windows/Linux 二进制不同；
    不选择插件系统（如 setuptools entry_points）：交易系统需要在代码层面明确控制加载顺序，
    隐式自动发现在生产环境中风险过高

- why_id: W003
  type: selection
  claim: "alpha 模块的因子计算选用 Polars 而非 pandas，且将其设为可选依赖而非核心依赖"
  reasoning_chain: >
    Alpha 因子工程需要对 50只股票 × 300天 = 15,000行数据做大量窗口计算（ts_rank, ts_corr, cs_rank 等） →
    pandas 的窗口操作是行迭代实现，Polars 采用 Apache Arrow 内存格式 + Rust 实现，列操作速度快数倍 →
    但核心交易框架（trader/）不需要因子计算，强制所有用户安装 Polars（含 pyarrow）会显著增加基础安装成本 →
    因此 Polars 仅在 [alpha] extra 中声明，不进入主依赖树
  evidence:
    - type: CODE
      source: "pyproject.toml:L383-L392 — alpha extra 包含 polars>=1.26.0 和 pyarrow>=19.0.1，而主 dependencies 不含这两个包"
    - type: CODE
      source: "tests/test_alpha101.py:L1-L5 — import polars as pl 和 import numpy as np 并列使用，calculate_by_expression 返回 pl.DataFrame，说明因子计算全链路基于 Polars"
    - type: CODE
      source: "vnpy/alpha/strategy/backtesting.py:L1-L8 — import polars as pl 出现在回测引擎顶层，同文件同时 import numpy，但核心 BarData/OrderData 仍来自 vnpy.trader.object（保持与主框架的数据对象兼容）"
  contrast: >
    不选择纯 pandas：Alpha158 等因子集涉及 ts_corr/cs_rank 等复杂时序+截面操作，
    pandas 实现需要多次 groupby+apply，在 50×300 规模上耗时显著；
    不选择 DolphinDB/ClickHouse 等列式数据库做计算：这些需要独立服务，
    而 Polars 是纯 Python 内存计算库，不引入外部依赖

- why_id: W004
  type: implementation
  claim: "无界面（no_ui）生产运行模式采用父子双进程架构，而非单进程守护"
  reasoning_chain: >
    量化交易策略需要在交易时段（白天+夜盘）运行，非交易时段需要自动停止以释放连接资源 →
    若用单进程 + 定时检查，策略引擎、CTP 连接、事件循环全部在同一进程，
    出现内存泄漏或僵尸连接后无法彻底清理 →
    将策略运行放入子进程（run_child），父进程（run_parent）只做监控和生命周期管理 →
    非交易时段子进程 sys.exit(0) 彻底释放所有资源，父进程检测到后等待下一交易时段再 fork 新子进程
  evidence:
    - type: CODE
      source: "examples/no_ui/run.py:L715-L739 — run_parent() 用 multiprocessing.Process(target=run_child) 创建子进程，检测 child_process.is_alive() 决定是否重启，注释明确'非记录时间则退出子进程'"
    - type: CODE
      source: "examples/no_ui/run.py:L675-L713 — run_child() 中 check_trading_period() 返回 False 时调用 main_engine.close() 再 sys.exit(0)，是主动 exit 而非 signal 终止，确保 CTP 断连流程正常执行"
    - type: INFERENCE
      source: "CTP 协议要求登出时发送 ReqUserLogout，如果进程被 kill -9 则无法完成，sys.exit(0) 触发 Python atexit 和对象析构，保证 CTP C++ 层正常断连"
  contrast: >
    不选择单进程 + threading.Event 控制停止：CTP 底层回调是 C++ 线程，
    Python GIL + C++ 线程混合的清理顺序不可控，单进程无法保证完全释放；
    不选择 systemd/supervisor 等进程管理工具：这些工具不了解交易时段逻辑，
    需要外部 cron 配合，增加部署复杂度；双进程方案将时段逻辑内置在代码中，自包含

- why_id: W005
  type: selection
  claim: "RPC 层使用 ZeroMQ 的 REP+PUB 双 Socket 组合，而非单一通讯协议"
  reasoning_chain: >
    分布式交易系统有两类通讯需求：
    (1) 请求-响应（下单、查询持仓）：需要确认，一对一 →
    (2) 行情/事件推送（tick、成交回报）：不需确认，一对多 →
    若只用 REQ-REP：推送行情时需要每个客户端轮询，延迟高且服务端瓶颈明显 →
    若只用 PUB-SUB：下单等需要响应的指令无法得到确认，可靠性不足 →
    因此 RpcServer 同时维护 _socket_rep（REP）和 _socket_pub（PUB）两个 Socket
  evidence:
    - type: CODE
      source: "vnpy/rpc/server.py:L37-L41 — _socket_rep = context.socket(zmq.REP) 和 _socket_pub = context.socket(zmq.PUB) 在构造函数中同时创建，注释明确标注两种模式"
    - type: CODE
      source: "vnpy/rpc/server.py:L55-L57 — start() 接受 rep_address 和 pub_address 两个地址参数，说明两个 Socket 绑定在不同端口，是有意分离而非一个连接的两个方向"
    - type: DOC
      source: "README.md:L227 — rpc_service 描述为'允许将某一进程启动为服务端，作为统一的行情和交易路由通道，允许多客户端同时连接'——多客户端订阅行情正是 PUB-SUB 的典型用例"
  contrast: >
    不选择单一 REQ-REP：行情推送用轮询实现延迟无法接受，期货 tick 到达频率可达每秒数百次；
    不选择 gRPC streaming：gRPC 的 Python 实现在高频场景下序列化开销大，
    且双向 streaming 的错误恢复逻辑复杂；ZeroMQ 是 C 库绑定，序列化通过 pickle 在应用层控制

- why_id: W006
  type: constraint
  claim: "alpha 模块的 ML 模型统一使用 MSE 损失函数，且训练目标是预测 Alpha 因子值而非直接预测涨跌方向"
  reasoning_chain: >
    量化多因子策略的核心是截面排序（哪些股票相对强）而非绝对涨跌预测 →
    直接预测涨跌（分类问题）需要设定阈值，阈值选择高度依赖样本分布，泛化性差 →
    预测 Alpha 因子值（回归问题）保留了相对强弱信息，后续由策略层做截面排序处理 →
    MSE 损失对较大预测误差施以更重惩罚，与量化中"避免严重偏离"的风险控制思路一致
  evidence:
    - type: CODE
      source: "vnpy/alpha/model/models/mlp_model.py:L925 — MlpModel docstring 明确'Support for MSE loss function'，且 AlphaModel 基类要求 predict() 返回连续值而非 0/1 分类"
    - type: CODE
      source: "vnpy/alpha/strategy/backtesting.py:L1108-L1165 — BacktestingEngine 基于 pos_data（持仓量）而非 signal（方向），策略通过调整持仓比例而非买卖信号控制敞口，与因子值回归的连续输出对应"
    - type: DOC
      source: "README.md:L121-L123 — alpha/strategy 描述'支持截面多标的和时序单标的两种策略类型'，截面策略依赖多标的横向排序，必须是连续值输出"
  contrast: >
    不选择 CrossEntropy 分类损失：分类模型只输出涨/跌，丢失了"涨多少"的梯度信息，
    截面排序质量下降；
    不选择 Sharpe Ratio 作为直接优化目标（端到端策略学习）：虽然理论上更优，
    但梯度不稳定，训练困难，且与现有 backtesting 模块的解耦架构不兼容

- why_id: W007
  type: negation
  claim: "核心交易框架（vnpy/trader/）没有内置任何持久化/数据库逻辑，数据库通过 get_database() 工厂函数在运行时注入"
  reasoning_chain: >
    量化交易系统的数据存储需求因用户规模差异极大：
    个人开发者用 SQLite 够用，机构用户需要 TDengine/DolphinDB 处理 tick 级海量数据 →
    若将数据库驱动硬编码进 trader 核心，用户无法在不改框架代码的情况下替换存储后端 →
    get_database() 返回当前配置的数据库适配器实例，策略和回测代码只依赖接口而非实现 →
    因此 trader/object.py 和 trader/engine.py 等核心文件不 import 任何数据库相关模块
  evidence:
    - type: CODE
      source: "examples/candle_chart/run.py:L6 — from vnpy.trader.database import get_database —— 仅在示例代码中通过工厂函数获取数据库，而非直接 import sqlite/mysql 等具体实现"
    - type: CODE
      source: "pyproject.toml:L366-L380 — 主依赖中没有任何数据库驱动（无 sqlalchemy, pymysql, motor 等），数据库适配器全部是独立 pip 包（vnpy_sqlite, vnpy_mysql 等）"
    - type: DOC
      source: "README.md:L248-L263 — 数据库支持列表包含 SQLite/MySQL/PostgreSQL/DolphinDB/TDengine/MongoDB 六种，均作为独立模块列出，说明没有一个是默认强制的"
  contrast: >
    不选择 ORM 抽象层（如 SQLAlchemy）统一数据库接口：tick 数据写入是高频操作，
    ORM 的对象映射开销会成为瓶颈；不同数据库（时序 vs 关系型）的查询模式也差异极大，
    ORM 无法统一表达 TDengine 的超级表查询；
    因此采用自定义接口 + 工厂模式，每个适配器针对目标数据库做专项优化
```

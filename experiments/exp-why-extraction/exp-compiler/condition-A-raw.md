# vnpy 项目知识（原始格式 — 无编译）

以下是从 vnpy 项目中提取的设计决策知识，以原始 YAML 卡片形式直接拼接。

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
      source: "examples/no_ui/run.py:L9,L13-L14"
    - type: CODE
      source: "examples/veighna_trader/run.py:L7-L8"
    - type: DOC
      source: "README.md:L245"
  contrast: >
    不选择直接函数回调（callback hell）：多 Gateway 多 App 场景下 O(N×M) 耦合；
    不选择 asyncio：CTP 等国内期货接口底层是 C++ 回调，线程模型更适配

- why_id: W002
  type: architecture
  claim: "所有功能模块（App）通过运行时注册而非编译时硬编码装入 MainEngine，默认示例只加载极少数模块"
  reasoning_chain: >
    vnpy 面向专业交易员，不同机构/个人使用的交易品种和策略类型差异极大 →
    若所有模块内置，启动时加载 15+ App 会浪费内存 →
    通过 main_engine.add_gateway() / main_engine.add_app() 按需注册 →
    run.py 中大量 App 被注释掉，仅启用 3 个，这是刻意展示"最小可用配置"
  evidence:
    - type: CODE
      source: "examples/veighna_trader/run.py:L18-L38"
    - type: CODE
      source: "vnpy/trader/app.py:L1-L21"
    - type: DOC
      source: "README.md:L143"
  contrast: >
    不选择 monorepo 内置：Gateway 依赖大量 C++ 二进制，安装包体积爆炸；
    不选择插件系统（setuptools entry_points）：交易系统需要明确控制加载顺序，隐式发现风险过高

- why_id: W003
  type: selection
  claim: "alpha 模块的因子计算选用 Polars 而非 pandas，且将其设为可选依赖"
  reasoning_chain: >
    Alpha 因子工程需要对 50只×300天 数据做大量窗口计算 →
    pandas 窗口操作是行迭代，Polars 采用 Arrow + Rust，列操作快数倍 →
    但核心交易框架不需要因子计算，强制安装 Polars 增加基础成本 →
    因此 Polars 仅在 [alpha] extra 中声明
  evidence:
    - type: CODE
      source: "pyproject.toml:L383-L392"
    - type: CODE
      source: "tests/test_alpha101.py:L1-L5"
    - type: CODE
      source: "vnpy/alpha/strategy/backtesting.py:L1-L8"
  contrast: >
    不选择纯 pandas：复杂时序+截面操作在 50×300 规模上耗时显著；
    不选择 DolphinDB/ClickHouse：需要独立服务，Polars 是纯内存计算

- why_id: W004
  type: implementation
  claim: "无界面生产模式采用父子双进程架构，而非单进程守护"
  reasoning_chain: >
    策略需要在交易时段运行，非交易时段自动停止释放连接 →
    单进程内存泄漏或僵尸连接无法彻底清理 →
    子进程 run_child 运行策略，父进程 run_parent 做生命周期管理 →
    非交易时段子进程 sys.exit(0) 释放所有资源，父进程等待后 fork 新子进程
  evidence:
    - type: CODE
      source: "examples/no_ui/run.py:L715-L739"
    - type: CODE
      source: "examples/no_ui/run.py:L675-L713"
    - type: INFERENCE
      source: "CTP 协议要求 ReqUserLogout，sys.exit(0) 触发 atexit 保证断连"
  contrast: >
    不选择单进程 + threading.Event：CTP C++ 线程混合清理不可控；
    不选择 systemd/supervisor：不了解交易时段逻辑，需外部 cron 配合

- why_id: W005
  type: selection
  claim: "RPC 层使用 ZeroMQ 的 REP+PUB 双 Socket 组合"
  reasoning_chain: >
    分布式交易有两类通讯：请求-响应（下单）一对一 + 事件推送（行情）一对多 →
    只用 REQ-REP：推送行情需轮询，延迟高；只用 PUB-SUB：下单无法确认 →
    因此同时维护 _socket_rep 和 _socket_pub
  evidence:
    - type: CODE
      source: "vnpy/rpc/server.py:L37-L41"
    - type: CODE
      source: "vnpy/rpc/server.py:L55-L57"
    - type: DOC
      source: "README.md:L227"
  contrast: >
    不选择单一 REQ-REP：tick 频率每秒数百次，轮询不可接受；
    不选择 gRPC streaming：Python 高频场景序列化开销大

- why_id: W006
  type: constraint
  claim: "alpha 模块 ML 模型统一使用 MSE 损失，预测因子值而非涨跌方向"
  reasoning_chain: >
    多因子策略核心是截面排序而非绝对涨跌预测 →
    分类问题需要阈值，泛化性差 →
    回归问题保留相对强弱信息，后续由策略层排序 →
    MSE 对大误差惩罚更重，与风险控制思路一致
  evidence:
    - type: CODE
      source: "vnpy/alpha/model/models/mlp_model.py:L925"
    - type: CODE
      source: "vnpy/alpha/strategy/backtesting.py:L1108-L1165"
    - type: DOC
      source: "README.md:L121-L123"
  contrast: >
    不选择 CrossEntropy：丢失梯度信息，截面排序质量下降；
    不选择 Sharpe Ratio 直接优化：梯度不稳定，与解耦架构不兼容

- why_id: W007
  type: negation
  claim: "核心交易框架不内置任何持久化逻辑，数据库通过 get_database() 工厂函数运行时注入"
  reasoning_chain: >
    数据存储需求因用户规模差异极大（个人 SQLite vs 机构 TDengine） →
    硬编码驱动则无法替换存储后端 →
    get_database() 返回配置的适配器实例，代码只依赖接口 →
    因此 trader 核心文件不 import 任何数据库模块
  evidence:
    - type: CODE
      source: "examples/candle_chart/run.py:L6"
    - type: CODE
      source: "pyproject.toml:L366-L380"
    - type: DOC
      source: "README.md:L248-L263"
  contrast: >
    不选择 ORM（SQLAlchemy）：tick 写入高频，对象映射是瓶颈；
    时序 vs 关系型查询模式差异大，ORM 无法统一
```

# vnpy 项目知识（编译格式 — Knowledge Compiler §12 规则）

## 设计哲学

vnpy 的核心设计理念是**"总线解耦 + 按需组装"**。整个框架围绕一个事件驱动引擎（EventEngine）构建消息总线，所有模块——无论是交易网关（Gateway）还是策略应用（App）——只与总线交互，从不直接调用彼此。这不是简单的发布-订阅模式，而是对量化交易系统多源异步事件（行情推送、订单状态、策略信号）本质的深刻回应。当你需要同时接入 10 个交易所的行情并分发给 5 个策略时，O(N×M) 的直接回调根本不可行。总线把这变成了 O(N+M)。

在此之上，vnpy 采用运行时注册而非编译时绑定来组装功能。`run.py` 中被注释掉的 13 行 `add_gateway/add_app` 不是历史遗留——它们是有意设计的"配置菜单"，让专业交易员按需勾选。这与核心框架不内置任何数据库驱动（通过 `get_database()` 工厂注入）的决策一脉相承：**框架提供骨架和协议，具体实现由使用者组装**。

（来源：CODE: `examples/veighna_trader/run.py:L7-8,L18-38`；CODE: `vnpy/trader/app.py:L1-21`；DOC: `README.md:L245`）

## 关键规则

- **RPC 必须用双 Socket（REP+PUB）**：下单等请求-响应用 REP，行情推送用 PUB。因为 tick 到达频率每秒数百次，REQ-REP 轮询延迟不可接受，而 PUB-SUB 无法确认下单指令。（来源：CODE: `vnpy/rpc/server.py:L37-41,L55-57`）

- **Alpha ML 模型统一用 MSE 回归，不做涨跌分类**：多因子策略的核心是截面排序（哪些股票相对强），不是预测绝对涨跌。分类模型丢失梯度信息，截面排序质量下降。MSE 对大误差惩罚更重，与风险控制思路一致。（来源：CODE: `vnpy/alpha/model/models/mlp_model.py:L925`；CODE: `vnpy/alpha/strategy/backtesting.py:L1108-1165`）

- **Polars 是可选依赖，不进主依赖树**：Alpha 因子计算用 Polars（Arrow+Rust，比 pandas 快数倍），但核心交易框架不需要它。强制安装 Polars+pyarrow 会不必要地增加基础安装成本。声明在 `[alpha]` extra 中。（来源：CODE: `pyproject.toml:L383-392`）

- **数据库零内置，工厂函数注入**：`trader/` 核心文件不 import 任何数据库模块。个人用 SQLite，机构用 TDengine/DolphinDB——通过 `get_database()` 返回配置的适配器。不用 ORM 是因为 tick 写入高频，对象映射是瓶颈。（来源：CODE: `pyproject.toml:L366-380`；DOC: `README.md:L248-263`）

## 实战经验

生产环境（无 UI）运行策略时，vnpy 采用父子双进程架构而非单进程守护。这是从实际痛点中来的：CTP 等国内期货接口底层是 C++ 回调线程，单进程内 Python GIL + C++ 线程的混合清理顺序不可控，一旦出现僵尸连接无法彻底回收。父进程 `run_parent` 只做监控，子进程 `run_child` 跑策略——非交易时段子进程 `sys.exit(0)` 触发 atexit 保证 CTP 正常断连（CTP 协议要求发送 ReqUserLogout），父进程检测后等待下一时段再 fork。不用 systemd/supervisor 是因为它们不理解交易时段逻辑，需要额外 cron 配合。

（来源：CODE: `examples/no_ui/run.py:L675-739`）

## 速查表

| 模块 | 关键设计 | 不要做 |
|------|---------|--------|
| EventEngine | 核心总线，所有模块只与它交互 | 不要让 Gateway 直接回调 App |
| App 注册 | `add_gateway()`/`add_app()` 按需加载 | 不要内置所有模块，不要用 entry_points 自动发现 |
| RPC | REP(请求响应) + PUB(事件推送) 双 Socket | 不要只用一种 Socket 模式 |
| Alpha/ML | MSE 回归预测因子值 → 策略层截面排序 | 不要用分类模型预测涨跌 |
| 依赖管理 | Polars 在 [alpha] extra，DB 驱动独立包 | 不要把可选依赖放进主依赖树 |
| 生产部署 | 父子双进程，子进程 sys.exit(0) 干净退出 | 不要单进程守护，不要 kill -9 |

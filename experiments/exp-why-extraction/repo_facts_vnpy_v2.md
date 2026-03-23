# repo_facts: vnpy

## 项目类型: code
代码文件: 70 / 173

## 文件类型分布
  70 py
  52 md
  12 ipynb
  12 ico
   9 rst
   4 html
   3 bat
   2 sh
   2 css
   1 yml
   1 typed
   1 toml
   1 pot
   1 po
   1 gitignore

## 目录结构（前三层）

.git
.github
.github/workflows
docs
docs/_static
docs/_templates
docs/community
docs/community/app
docs/community/info
docs/community/install
docs/elite
docs/elite/extension
docs/elite/info
docs/elite/strategy
examples
examples/alpha_research
examples/candle_chart
examples/client_server
examples/cta_backtesting
examples/data_recorder
examples/download_bars
examples/no_ui
examples/notebook_trading
examples/portfolio_backtesting
examples/simple_rpc
examples/spread_backtesting
examples/veighna_trader
tests
vnpy
vnpy/alpha
vnpy/alpha/dataset
vnpy/alpha/model
vnpy/alpha/strategy
vnpy/chart
vnpy/event
vnpy/rpc
vnpy/trader
vnpy/trader/locale
vnpy/trader/ui

## Layer 1: 结构性文件

### README.md (341 行)
#### 前 200 行
# VeighNa - By Traders, For Traders, AI-Powered.

<p align="center">
  <img src ="https://vnpy.oss-cn-shanghai.aliyuncs.com/veighna-logo.png"/>
</p>

💬 Want to read this in **english** ? Go [**here**](README_ENG.md)

<p align="center">
    <img src ="https://img.shields.io/badge/version-4.3.0-blueviolet.svg"/>
    <img src ="https://img.shields.io/badge/platform-windows|linux|macos-yellow.svg"/>
    <img src ="https://img.shields.io/badge/python-3.10|3.11|3.12|3.13-blue.svg" />
    <img src ="https://img.shields.io/github/actions/workflow/status/vnpy/vnpy/pythonapp.yml?branch=master"/>
    <img src ="https://img.shields.io/github/license/vnpy/vnpy.svg?color=orange"/>
</p>

VeighNa是一套基于Python的开源量化交易系统开发框架，在开源社区持续不断的贡献下一步步成长为多功能量化交易平台，自发布以来已经积累了众多来自金融机构或相关领域的用户，包括私募基金、证券公司、期货公司等。

在使用VeighNa进行二次开发（策略、模块等）的过程中有任何疑问，请查看[**VeighNa项目文档**](https://www.vnpy.com/docs/cn/index.html)，如果无法解决请前往[**官方社区论坛**](https://www.vnpy.com/forum/)的【提问求助】板块寻求帮助，也欢迎在【经验分享】板块分享你的使用心得！

**想要获取更多关于VeighNa的资讯信息？** 请扫描下方二维码添加小助手加入【VeighNa社区交流微信群】：

<p align="center">
  <img src ="https://vnpy.oss-cn-shanghai.aliyuncs.com/github_wx.png"/, width=250>
</p>


## AI-Powered


VeighNa发布十周年之际正式推出4.0版本，重磅新增面向AI量化策略的[vnpy.alpha](./vnpy/alpha)模块，为专业量化交易员提供**一站式多因子机器学习（ML）策略开发、投研和实盘交易解决方案**：

<p align="center">
  <img src ="https://vnpy.oss-cn-shanghai.aliyuncs.com/alpha_demo.jpg"/, width=500>
</p>

* :bar_chart: **[dataset](./vnpy/alpha/dataset)**：因子特征工程

    * 专为ML算法训练优化设计，支持高效批量特征计算与处理
    * 内置丰富的因子特征表达式计算引擎，实现快速一键生成训练数据
    * [Alpha 158](./vnpy/alpha/dataset/datasets/alpha_158.py)：源于微软Qlib项目的股票市场特征集合，涵盖K线形态、价格趋势、时序波动等多维度量化因子

* :bulb: **[model](./vnpy/alpha/model)**：预测模型训练

    * 提供标准化的ML模型开发模板，大幅简化模型构建与训练流程
    * 统一API接口设计，支持无缝切换不同算法进行性能对比测试
    * 集成多种主流机器学习算法：
        * [Lasso](./vnpy/alpha/model/models/lasso_model.py)：经典Lasso回归模型，通过L1正则化实现特征选择
        * [LightGBM](./vnpy/alpha/model/models/lgb_model.py)：高效梯度提升决策树，针对大规模数据集优化的训练引擎
        * [MLP](./vnpy/alpha/model/models/mlp_model.py)：多层感知机神经网络，适用于复杂非线性关系建模

* :robot: **[strategy](./vnpy/alpha/strategy)**：策略投研开发

    * 基于ML信号预测模型快速构建量化交易策略
    * 支持截面多标的和时序单标的两种策略类型

* :microscope: **[lab](./vnpy/alpha/lab.py)**：投研流程管理

    * 集成数据管理、模型训练、信号生成和策略回测等完整工作流程
    * 简洁API设计，内置可视化分析工具，直观评估策略表现和模型效果

* :book: **[notebook](./examples/alpha_research)**：量化投研Demo

    * [download_data_rq](./examples/alpha_research/download_data_rq.ipynb)：基于RQData下载A股指数成分股数据，包含指数成分变化跟踪及历史行情获取
    * [download_data_xt](./examples/alpha_research/download_data_xt.ipynb)：基于迅投研数据服务，下载获取A股指数成分历史变化和股票K线数据
    * [research_workflow_lasso](./examples/alpha_research/research_workflow_lasso.ipynb)：基于Lasso回归模型的量化投研工作流，展示线性模型特征选择与预测能力
    * [research_workflow_lgb](./examples/alpha_research/research_workflow_lgb.ipynb)：基于LightGBM梯度提升树的量化投研工作流，利用高效集成学习方法进行预测
    * [research_workflow_mlp](./examples/alpha_research/research_workflow_mlp.ipynb)：基于多层感知机神经网络的量化投研工作流，展示深度学习在量化交易中的应用

vnpy.alpha模块的设计理念受到[Qlib](https://github.com/microsoft/qlib)项目的启发，在保持易用性的同时提供强大的AI量化能力，特此向Qlib开发团队致以诚挚感谢！


## 功能特点

带有 :arrow_up: 的模块代表已经完成4.0版本的升级适配测试，同时4.0核心框架采用了优先保证兼容性的升级方式，因此大多数模块也都可以直接使用（涉及到C++ API封装的接口必须升级后才能使用）。 

1. :arrow_up: 多功能量化交易平台（trader），整合了多种交易接口，并针对具体策略算法和功能开发提供了简洁易用的API，用于快速构建交易员所需的量化交易应用。

2. 覆盖国内外所拥有的下述交易品种的交易接口（gateway）：

    * 国内市场

        * :arrow_up: CTP（[ctp](https://www.github.com/vnpy/vnpy_ctp)）：国内期货、期权

        * :arrow_up: CTP Mini（[mini](https://www.github.com/vnpy/vnpy_mini)）：国内期货、期权

        * :arrow_up: CTP证券（[sopt](https://www.github.com/vnpy/vnpy_sopt)）：ETF期权

        * :arrow_up: 飞马（[femas](https://www.github.com/vnpy/vnpy_femas)）：国内期货

        * :arrow_up: 恒生UFT（[uft](https://www.github.com/vnpy/vnpy_uft)）：国内期货、ETF期权

        * :arrow_up: 易盛（[esunny](https://www.github.com/vnpy/vnpy_esunny)）：国内期货、黄金TD

        * :arrow_up: 顶点HTS（[hts](https://www.github.com/vnpy/vnpy_hts)）：ETF期权

        * :arrow_up: 顶点飞创（[sec](https://www.github.com/vnpy/vnpy_sec)）：ETF期权

        * :arrow_up: 中泰XTP（[xtp](https://www.github.com/vnpy/vnpy_xtp)）：国内证券（A股）、ETF期权

        * :arrow_up: 华鑫奇点（[tora](https://www.github.com/vnpy/vnpy_tora)）：国内证券（A股）、ETF期权

        * 东证OST（[ost](https://www.github.com/vnpy/vnpy_ost)）：国内证券（A股）

        * 东方财富EMT（[emt](https://www.github.com/vnpy/vnpy_emt)）：国内证券（A股）

        * 飞鼠（[sgit](https://www.github.com/vnpy/vnpy_sgit)）：黄金TD、国内期货

        * :arrow_up: 金仕达黄金（[ksgold](https://www.github.com/vnpy/vnpy_ksgold)）：黄金TD

        * :arrow_up: 利星资管（[lstar](https://www.github.com/vnpy/vnpy_lstar)）：期货资管

        * :arrow_up: 融航（[rohon](https://www.github.com/vnpy/vnpy_rohon)）：期货资管

        * :arrow_up: 杰宜斯（[jees](https://www.github.com/vnpy/vnpy_jees)）：期货资管

        * 中汇亿达（[comstar](https://www.github.com/vnpy/vnpy_comstar)）：银行间市场

        * :arrow_up: TTS（[tts](https://www.github.com/vnpy/vnpy_tts)）：国内期货（仿真）

    * 海外市场

        * :arrow_up: Interactive Brokers（[ib](https://www.github.com/vnpy/vnpy_ib)）：海外证券、期货、期权、贵金属等

        * :arrow_up: 易盛9.0外盘（[tap](https://www.github.com/vnpy/vnpy_tap)）：海外期货

        * :arrow_up: 直达期货（[da](https://www.github.com/vnpy/vnpy_da)）：海外期货

    * 特殊应用

        * :arrow_up: RQData行情（[rqdata](https://www.github.com/vnpy/vnpy_rqdata)）：跨市场（股票、指数、ETF、期货）实时行情

        * :arrow_up: 迅投研行情（[xt](https://www.github.com/vnpy/vnpy_xt)）：跨市场（股票、指数、可转债、ETF、期货、期权）实时行情

        * :arrow_up: RPC服务（[rpc](https://www.github.com/vnpy/vnpy_rpcservice)）：跨进程通讯接口，用于分布式架构

3. 覆盖下述各类量化策略的交易应用（app）：

    * :arrow_up: [cta_strategy](https://www.github.com/vnpy/vnpy_ctastrategy)：CTA策略引擎模块，在保持易用性的同时，允许用户针对CTA类策略运行过程中委托的报撤行为进行细粒度控制（降低交易滑点、实现高频策略）

    * :arrow_up: [cta_backtester](https://www.github.com/vnpy/vnpy_ctabacktester)：CTA策略回测模块，无需使用Jupyter Notebook，直接使用图形界面进行策略回测分析、参数优化等相关工作

    * :arrow_up: [spread_trading](https://www.github.com/vnpy/vnpy_spreadtrading)：价差交易模块，支持自定义价差，实时计算价差行情和持仓，支持价差算法交易以及自动价差策略两种模式

    * :arrow_up: [option_master](https://www.github.com/vnpy/vnpy_optionmaster)：期权交易模块，针对国内期权市场设计，支持多种期权定价模型、隐含波动率曲面计算、希腊值风险跟踪等功能

    * :arrow_up: [portfolio_strategy](https://www.github.com/vnpy/vnpy_portfoliostrategy)：组合策略模块，面向同时交易多合约的量化策略（Alpha、期权套利等），提供历史数据回测和实盘自动交易功能

    * :arrow_up: [algo_trading](https://www.github.com/vnpy/vnpy_algotrading)：算法交易模块，提供多种常用的智能交易算法：TWAP、Sniper、Iceberg、BestLimit等

    * :arrow_up: [script_trader](https://www.github.com/vnpy/vnpy_scripttrader)：脚本策略模块，面向多标的类量化策略和计算任务设计，同时也可以在命令行中实现REPL指令形式的交易，不支持回测功能

    * :arrow_up: [paper_account](https://www.github.com/vnpy/vnpy_paperaccount)：本地仿真模块，纯本地化实现的仿真模拟交易功能，基于交易接口获取的实时行情进行委托撮合，提供委托成交推送以及持仓记录

    * :arrow_up: [chart_wizard](https://www.github.com/vnpy/vnpy_chartwizard)：K线图表模块，基于RQData数据服务（期货）或者交易接口获取历史数据，并结合Tick推送显示实时行情变化

    * :arrow_up: [portfolio_manager](https://www.github.com/vnpy/vnpy_portfoliomanager)：交易组合管理模块，以独立的策略交易组合（子账户）为基础，提供委托成交记录管理、交易仓位自动跟踪以及每日盈亏实时统计功能

    * :arrow_up: [rpc_service](https://www.github.com/vnpy/vnpy_rpcservice)：RPC服务模块，允许将某一进程启动为服务端，作为统一的行情和交易路由通道，允许多客户端同时连接，实现多进程分布式系统

    * :arrow_up: [data_manager](https://www.github.com/vnpy/vnpy_datamanager)：历史数据管理模块，通过树形目录查看数据库中已有的数据概况，选择任意时间段数据查看字段细节，支持CSV文件的数据导入和导出

    * :arrow_up: [data_recorder](https://www.github.com/vnpy/vnpy_datarecorder)：行情记录模块，基于图形界面进行配置，根据需求实时录制Tick或者K线行情到数据库中，用于策略回测或者实盘初始化

    * :arrow_up: [excel_rtd](https://www.github.com/vnpy/vnpy_excelrtd)：Excel RTD（Real Time Data）实时数据服务，基于pyxll模块实现在Excel中获取各类数据（行情、合约、持仓等）的实时推送更新

    * :arrow_up: [risk_manager](https://www.github.com/vnpy/vnpy_riskmanager)：风险管理模块，提供包括交易流控、下单数量、活动委托、撤单总数等规则的统计和限制，有效实现前端风控功能

    * :arrow_up: [web_trader](https://www.github.com/vnpy/vnpy_webtrader)：Web服务模块，针对B-S架构需求设计，实现了提供主动函数调用（REST）和被动数据推送（Websocket）的Web服务器

4. Python交易API接口封装（api），提供上述交易接口的底层对接实现。

    * :arrow_up: REST Client（[rest](https://www.github.com/vnpy/vnpy_rest)）：基于协程异步IO的高性能REST API客户端，采用事件消息循环的编程模型，支持高并发实时交易请求发送

    * :arrow_up: Websocket Client（[websocket](https://www.github.com/vnpy/vnpy_websocket)）：基于协程异步IO的高性能Websocket API客户端，支持和REST Client共用事件循环并发运行

5. :arrow_up: 简洁易用的事件驱动引擎（event），作为事件驱动型交易程序的核心。

6. 对接各类数据库的适配器接口（database）：

    * SQL类

        * :arrow_up: SQLite（[sqlite](https://www.github.com/vnpy/vnpy_sqlite)）：轻量级单文件数据库，无需安装和配置数据服务程序，VeighNa的默认选项，适合入门新手用户

        * :arrow_up: MySQL（[mysql](https://www.github.com/vnpy/vnpy_mysql)）：主流的开源关系型数据库，文档资料极为丰富，且可替换其他NewSQL兼容实现（如TiDB）

        * :arrow_up: PostgreSQL（[postgresql](https://www.github.com/vnpy/vnpy_postgresql)）：特性更为丰富的开源关系型数据库，支持通过扩展插件来新增功能，只推荐熟手使用

    * NoSQL类

        * DolphinDB（[dolphindb](https://www.github.com/vnpy/vnpy_dolphindb)）：一款高性能分布式时序数据库，适用于对速度要求极高的低延时或实时性任务

        * :arrow_up: TDengine（[taos](https://www.github.com/vnpy/vnpy_taos)）：分布式、高性能、支持SQL的时序数据库，带有内建的缓存、流式计算、数据订阅等系统功能，能大幅减少研发和运维的复杂度

        * :arrow_up: MongoDB（[mongodb](https://www.github.com/vnpy/vnpy_mongodb)）：基于分布式文件储存（bson格式）的文档式数据库，内置的热数据内存缓存提供更快读写速度

7. 对接下述各类数据服务的适配器接口（datafeed）：

    * :arrow_up: 迅投研（[xt](https://www.github.com/vnpy/vnpy_xt)）：股票、期货、期权、基金、债券


#### 后 50 行
    main_engine.add_app(CtaBacktesterApp)

    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()

    qapp.exec()


if __name__ == "__main__":
    main()
```

在该目录下打开CMD（按住Shift->点击鼠标右键->在此处打开命令窗口/PowerShell）后运行下列命令启动VeighNa Trader：

    python run.py

## 贡献代码

VeighNa使用Github托管其源代码，如果希望贡献代码请使用github的PR（Pull Request）的流程:

1. [创建 Issue](https://github.com/vnpy/vnpy/issues/new) - 对于较大的改动（如新功能，大型重构等）建议先开issue讨论一下，较小的improvement（如文档改进，bugfix等）直接发PR即可

2. Fork [VeighNa](https://github.com/vnpy/vnpy) - 点击右上角**Fork**按钮

3. Clone你自己的fork: ```git clone https://github.com/$userid/vnpy.git```
	* 如果你的fork已经过时，需要手动sync：[同步方法](https://help.github.com/articles/syncing-a-fork/)

4. 从**dev**创建你自己的feature branch: ```git checkout -b $my_feature_branch dev```

5. 在$my_feature_branch上修改并将修改push到你的fork上

6. 创建从你的fork的$my_feature_branch分支到主项目的**dev**分支的[Pull Request] -  [在此](https://github.com/vnpy/vnpy/compare?expand=1)点击**compare across forks**，选择需要的fork和branch创建PR

7. 等待review, 需要继续改进，或者被Merge!

在提交代码的时候，请遵守以下规则，以提高代码质量：

  * 使用[ruff](https://github.com/astral-sh/ruff)检查你的代码样式，确保没有error和warning。在项目根目录下运行```ruff check .```即可。
  * 使用[mypy](https://github.com/python/mypy)进行静态类型检查，确保类型注解正确。在项目根目录下运行```mypy vnpy```即可。

## 其他内容

* [获取帮助](https://github.com/vnpy/vnpy/blob/dev/.github/SUPPORT.md)
* [社区行为准则](https://github.com/vnpy/vnpy/blob/dev/.github/CODE_OF_CONDUCT.md)
* [Issue模板](https://github.com/vnpy/vnpy/blob/dev/.github/ISSUE_TEMPLATE.md)
* [PR模板](https://github.com/vnpy/vnpy/blob/dev/.github/PULL_REQUEST_TEMPLATE.md)

## 版权说明

MIT

#### README 结构分析（所有标题）
1:# VeighNa - By Traders, For Traders, AI-Powered.
28:## AI-Powered
73:## 功能特点
227:## 环境准备
233:## 安装步骤
255:## 使用指南
269:## 脚本运行
308:## 贡献代码
332:## 其他内容
339:## 版权说明

#### README 链接统计
外部链接数: 87
GitHub 链接数: 12
图片引用数: 0
0

### 依赖文件
#### pyproject.toml
[project]
name = "vnpy"
dynamic = ["version"]
description = "A framework for developing quant trading systems."
readme = "README.md"
license = {text = "MIT"}
authors = [{name = "Xiaoyou Chen", email = "xiaoyou.chen@mail.vnpy.com"}]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "License :: OSI Approved :: MIT License",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX :: Linux",
    "Operating System :: MacOS",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: Implementation :: CPython",
    "Topic :: Office/Business :: Financial :: Investment",
    "Natural Language :: Chinese (Simplified)",
    "Typing :: Typed",
]
requires-python = ">=3.10"
dependencies = [
    "tzlocal>=5.3.1",
    "PySide6==6.8.2.1",
    "pyqtgraph>=0.13.7",
    "qdarkstyle>=3.2.3",
    "numpy>=2.2.3",
    "pandas>=2.2.3",
    "ta-lib>=0.6.4",
    "deap>=1.4.2",
    "pyzmq>=26.3.0",
    "plotly>=6.0.0",
    "tqdm>=4.67.1",
    "loguru>=0.7.3",
    "nbformat>=5.10.4"
]
keywords = ["quant", "quantitative", "investment", "trading", "algotrading"]

[project.optional-dependencies]
alpha = [
    "polars>=1.26.0",
    "scipy>=1.15.2",
    "alphalens-reloaded>=0.4.5",
    "scikit-learn>=1.6.1",
    "lightgbm>=4.6.0",
    "torch>=2.6.0",
    "pyarrow>=19.0.1",
]
dev = [
    "pandas-stubs>=2.2.3.250308",
    "hatchling>=1.27.0",
    "babel>=2.17.0",
]

[project.urls]
"Homepage" = "https://www.vnpy.com"
"Documentation" = "https://www.vnpy.com/docs"
"Changes" = "https://github.com/vnpy/vnpy/blob/master/CHANGELOG.md"
"Source" = "https://github.com/vnpy/vnpy/"
"Forum" = "https://www.vnpy.com/forum"

[build-system]
requires = ["hatchling>=1.27.0", "babel>=2.17.0"]
build-backend = "hatchling.build"

[tool.hatch.version]
path = "vnpy/__init__.py"
pattern = "__version__ = ['\"](?P<version>[^'\"]+)['\"]"

[tool.hatch.build.targets.wheel]
packages = ["vnpy"]
include-package-data = true

[tool.hatch.build.targets.sdist]
include = ["vnpy*"]

[tool.hatch.build.hooks.custom]
path = "vnpy/trader/locale/build_hook.py"

[tool.hatch.build.targets.wheel.force-include]
"vnpy/trader/locale/en/LC_MESSAGES/vnpy.mo" = "vnpy/trader/locale/en/LC_MESSAGES/vnpy.mo"

[tool.ruff]
target-version = "py310"
output-format = "full"

[tool.ruff.lint]
select = [
    "B",  # flake8-bugbear
    "E",  # pycodestyle error
    "F",  # pyflakes
    "UP",  # pyupgrade
    "W",  # pycodestyle warning
]
ignore = ["E501"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
strict_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true

[[tool.mypy.overrides]]
module = [
    "polars",
    "lightgbm",
    "hatchling.*"
]
ignore_missing_imports = true

### CI/CD 配置
#### .github/workflows/pythonapp.yml
name: Python application

on: [push]

jobs:
  build:

    runs-on: windows-latest

    steps:
    - uses: actions/checkout@v1
    - name: Set up Python 3.13
      uses: actions/setup-python@v1
      with:
        python-version: '3.13'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install ruff mypy uv types-tqdm
        uv pip install ta-lib==0.6.4 --index=https://pypi.vnpy.com --system
        uv pip install -e .[alpha,dev] --system
    - name: Lint with ruff
      run: |
        # Run ruff linter based on pyproject.toml configuration
        ruff check .
    - name: Type check with mypy
      run: |
        # Run mypy type checking based on pyproject.toml configuration
        mypy vnpy
    - name: Build packages with uv
      run: |
        # Build source distribution and wheel distribution
        uv build


### 容器与部署配置
(无容器/部署配置)

### .github 目录
#### .github/CODE_OF_CONDUCT.md
# 行为准则

这是一份VeighNa项目社区的行为准则，也是项目作者自己在刚入行量化金融行业时对于理想中的社区的期望：

* 为交易员而生：作为一款从金融机构量化业务中诞生的交易系统开发框架，设计上都优先满足机构专业交易员的使用习惯，而不是其他用户（散户、爱好者、技术人员等）

* 对新用户友好，保持耐心：大部分人在接触新东西的时候都是磕磕碰碰、有很多的问题，请记住此时别人对你伸出的援助之手，并把它传递给未来需要的人

* 尊重他人，慎重言行：礼貌文明的交流方式除了能得到别人同样的回应，更能减少不必要的摩擦，保证高效的交流

#### .github/PULL_REQUEST_TEMPLATE.md
建议每次发起的PR内容尽可能精简，复杂的修改请拆分为多次PR，便于管理合并。

## 改进内容

1. 
2. 
3.

## 相关的Issue号（如有）

Close #
#### .github/SUPPORT.md
# 获取帮助

在开发和使用VeighNa项目的过程中遇到问题时，获取帮助的渠道包括：

* Github Issues：[Issues页面](https://github.com/vnpy/vnpy/issues)
* 官方QQ群: 262656087
* 项目论坛：[VeighNa量化社区](http://www.vnpy.com/forum)
* 项目邮箱: vn.py@foxmail.com

#### .github/ISSUE_TEMPLATE.md
## 环境

* 操作系统: 如Windows 11或者Ubuntu 22.04
* Python版本: 如VeighNa Studio-4.0.0
* VeighNa版本: 如v4.0.0发行版或者dev branch 20250320（下载日期）

## Issue类型
三选一：Bug/Enhancement/Question

## 预期程序行为


## 实际程序行为


## 重现步骤

针对Bug类型Issue，请提供具体重现步骤以及报错截图



## Layer 2: Import 依赖中心度

主要语言: py

### 被引用最多的模块（Top 10）
  86 
  60 vnpy
  18 typing
  17 polars
  16 datetime
  14 collections
  11 time
   9 numpy
   7 abc
   6 pathlib

### 项目内部模块被引用次数（Top 10）
   9 vnpy.trader.object
   9 vnpy.event
   7 vnpy.trader.ui
   6 vnpy.trader.constant
   5 vnpy.trader.engine
   5 vnpy.alpha
   4 vnpy.trader.utility
   3 vnpy.trader.setting
   2 vnpy.trader.event
   2 vnpy.rpc

### 依赖中心度最高的文件（Top 5）
vnpy/trader/object.py
vnpy/event/__init__.py
vnpy/trader/ui/__init__.py
vnpy/trader/constant.py
vnpy/trader/engine.py

## Layer 3: Git 变更热点

总提交数: 1

## Layer 4: 关键代码片段

### examples/candle_chart/run.py (43 行)
```python
from datetime import datetime

from vnpy.trader.ui import create_qapp, QtCore
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import get_database
from vnpy.chart import ChartWidget, VolumeItem, CandleItem


if __name__ == "__main__":
    app = create_qapp()

    database = get_database()
    bars = database.load_bar_data(
        "IF888",
        Exchange.CFFEX,
        interval=Interval.MINUTE,
        start=datetime(2019, 7, 1),
        end=datetime(2019, 7, 17)
    )

    widget = ChartWidget()
    widget.add_plot("candle", hide_x_axis=True)
    widget.add_plot("volume", maximum_height=200)
    widget.add_item(CandleItem, "candle", "candle")
    widget.add_item(VolumeItem, "volume", "volume")
    widget.add_cursor()

    n = 1000
    history = bars[:n]
    new_data = bars[n:]

    widget.update_history(history)

    def update_bar() -> None:
        bar = new_data.pop(0)
        widget.update_bar(bar)

    timer = QtCore.QTimer()
    timer.timeout.connect(update_bar)
    # timer.start(100)

    widget.show()
    app.exec()
```

### examples/no_ui/run.py (125 行)
```python
import multiprocessing
import sys
from time import sleep
from datetime import datetime, time
from vnpy.event import EventEngine
from vnpy.trader.setting import SETTINGS
from vnpy.trader.engine import MainEngine, LogEngine
from vnpy.trader.logger import INFO, logger
from vnpy_ctp import CtpGateway
from vnpy_ctastrategy import CtaStrategyApp, CtaEngine
from vnpy_ctastrategy.base import EVENT_CTA_LOG

def check_trading_period() -> bool:
    """"""
    current_time = datetime.now().time()

    trading = False
    if (
        (current_time >= DAY_START and current_time <= DAY_END)
        or (current_time >= NIGHT_START)
        or (current_time <= NIGHT_END)
    ):
        trading = True

    return trading

def run_child() -> None:
    """
    Running in the child process.
    """
    SETTINGS["log.file"] = True

    event_engine: EventEngine = EventEngine()
    main_engine: MainEngine = MainEngine(event_engine)
    main_engine.add_gateway(CtpGateway)
    cta_engine: CtaEngine = main_engine.add_app(CtaStrategyApp)
    logger.info("主引擎创建成功")

    log_engine: LogEngine = main_engine.get_engine("log")       # type: ignore
    event_engine.register(EVENT_CTA_LOG, log_engine.process_log_event)
    logger.info("注册日志事件监听")

    main_engine.connect(ctp_setting, "CTP")
    logger.info("连接CTP接口")

    sleep(10)

    cta_engine.init_engine()
    logger.info("CTA策略初始化完成")

    cta_engine.init_all_strategies()
    sleep(60)   # Leave enough time to complete strategy initialization
    logger.info("CTA策略全部初始化")

    cta_engine.start_all_strategies()
    logger.info("CTA策略全部启动")

    while True:
        sleep(10)

        trading = check_trading_period()
        if not trading:
            logger.info("关闭子进程")
            main_engine.close()
            sys.exit(0)

def run_parent() -> None:
    """
    Running in the parent process.
    """
    print("启动CTA策略守护父进程")

    child_process = None

    while True:
        trading = check_trading_period()

        # Start child process in trading period
        if trading and child_process is None:
            print("启动子进程")
            child_process = multiprocessing.Process(target=run_child)
            child_process.start()
            print("子进程启动成功")

        # 非记录时间则退出子进程
        if not trading and child_process is not None:
            if not child_process.is_alive():
                child_process = None
                print("子进程关闭成功")

        sleep(5)

```

### examples/veighna_trader/run.py (87 行)
```python
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp
from vnpy_ctp import CtpGateway
from vnpy_ctastrategy import CtaStrategyApp
from vnpy_ctabacktester import CtaBacktesterApp
from vnpy_datamanager import DataManagerApp

def main():
    """"""
    qapp = create_qapp()

    event_engine = EventEngine()

    main_engine = MainEngine(event_engine)

    main_engine.add_gateway(CtpGateway)
    # main_engine.add_gateway(CtptestGateway)
    # main_engine.add_gateway(MiniGateway)
    # main_engine.add_gateway(FemasGateway)
    # main_engine.add_gateway(SoptGateway)
    # main_engine.add_gateway(UftGateway)
    # main_engine.add_gateway(EsunnyGateway)
    # main_engine.add_gateway(XtpGateway)
    # main_engine.add_gateway(ToraStockGateway)
    # main_engine.add_gateway(ToraOptionGateway)
    # main_engine.add_gateway(IbGateway)
    # main_engine.add_gateway(TapGateway)
    # main_engine.add_gateway(DaGateway)
    # main_engine.add_gateway(RohonGateway)
    # main_engine.add_gateway(TtsGateway)

    # main_engine.add_app(PaperAccountApp)
    main_engine.add_app(CtaStrategyApp)
    main_engine.add_app(CtaBacktesterApp)
    # main_engine.add_app(SpreadTradingApp)
    # main_engine.add_app(AlgoTradingApp)
    # main_engine.add_app(OptionMasterApp)
    # main_engine.add_app(PortfolioStrategyApp)
    # main_engine.add_app(ScriptTraderApp)
    # main_engine.add_app(ChartWizardApp)
    # main_engine.add_app(RpcServiceApp)
    # main_engine.add_app(ExcelRtdApp)
    main_engine.add_app(DataManagerApp)
    # main_engine.add_app(DataRecorderApp)
    # main_engine.add_app(RiskManagerApp)
    # main_engine.add_app(WebTraderApp)
    # main_engine.add_app(PortfolioManagerApp)

    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()

    qapp.exec()

```

### tests/test_alpha101.py (676 行)
```python
import pytest
import polars as pl
import numpy as np
from datetime import datetime, timedelta
from vnpy.alpha.dataset.utility import calculate_by_expression

def create_test_df(n_symbols: int = 50, n_days: int = 300) -> pl.DataFrame:
    """
    Create test DataFrame with extreme values.

    Columns: datetime, vt_symbol, open, high, low, close, volume, vwap
    """
    np.random.seed(42)

    symbols = [f"SH.{600000 + i}" for i in range(n_symbols)]
    dates = [datetime(2023, 1, 1) + timedelta(days=i) for i in range(n_days)]

    data = []
    for sym_idx, symbol in enumerate(symbols):
        # Base price for each symbol
        base_price = 10 + np.random.rand() * 90

        for day_idx, dt in enumerate(dates):
            # Generate random prices
            change = (np.random.rand() - 0.5) * 0.1
            close = base_price * (1 + change)
            high = close * (1 + np.random.rand() * 0.03)
            low = close * (1 - np.random.rand() * 0.03)
            open_price = low + (high - low) * np.random.rand()
            volume = float(np.random.randint(100000, 10000000))
            vwap = (high + low + close) / 3

            # Insert extreme values
            if day_idx == 50 + sym_idx % 10:
                close = np.nan
            elif day_idx == 100 + sym_idx % 10:
                volume = 0.0
            elif day_idx == 150 + sym_idx % 10:
                close = 1e-10

            data.append({
                "datetime": dt,
                "vt_symbol": symbol,
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
                "vwap": vwap
            })

            if not np.isnan(close):
                base_price = close

    return pl.DataFrame(data)

def test_df() -> pl.DataFrame:
    """Create test data: 50 symbols, 300 days, with extreme values."""
    return create_test_df(n_symbols=50, n_days=300)

class TestAlpha101:
    """Test Alpha101 Factors"""

    def test_alpha1(self, test_df: pl.DataFrame) -> None:
        """Test Alpha#1"""
        expr = f"(cs_rank(ts_argmax(pow1(quesval(0, {returns_expr}, close, ts_std({returns_expr}, 20)), 2.0), 5)) - 0.5)"
        result = calculate_by_expression(test_df, expr)
        assert "data" in result.columns

    def test_alpha2(self, test_df: pl.DataFrame) -> None:
        """Test Alpha#2"""
        expr = "(-1) * ts_corr(cs_rank(ts_delta(log(volume), 2)), cs_rank((close - open) / open), 6)"
        result = calculate_by_expression(test_df, expr)
        assert "data" in result.columns

    def test_alpha3(self, test_df: pl.DataFrame) -> None:
        """Test Alpha#3"""
        expr = "ts_corr(cs_rank(open), cs_rank(volume), 10) * -1"
        result = calculate_by_expression(test_df, expr)
        assert "data" in result.columns

    def test_alpha4(self, test_df: pl.DataFrame) -> None:
        """Test Alpha#4"""
        expr = "-1 * ts_rank(cs_rank(low), 9)"
        result = calculate_by_expression(test_df, expr)
        assert "data" in result.columns

    def test_alpha5(self, test_df: pl.DataFrame) -> None:
        """Test Alpha#5"""
        expr = "cs_rank((open - (ts_sum(vwap, 10) / 10))) * (-1 * abs(cs_rank((close - vwap))))"
        result = calculate_by_expression(test_df, expr)
        assert "data" in result.columns

    def test_alpha6(self, test_df: pl.DataFrame) -> None:
        """Test Alpha#6"""
        expr = "(-1) * ts_corr(open, volume, 10)"
        result = calculate_by_expression(test_df, expr)
        assert "data" in result.columns

    def test_alpha7(self, test_df: pl.DataFrame) -> None:
    # ... (554 lines omitted) ...
        """Test Alpha#100"""
        expr = "-1 * ((1.5 * cs_scale(cs_rank(((close - low) - (high - close)) / (high - low) * volume))) - cs_scale(ts_corr(close, cs_rank(ts_mean(volume, 20)), 5) - cs_rank(ts_argmin(close, 30)))) * (volume / ts_mean(volume, 20))"
        result = calculate_by_expression(test_df, expr)
        assert "data" in result.columns

    def test_alpha101(self, test_df: pl.DataFrame) -> None:
        """Test Alpha#101"""
        expr = "((close - open) / ((high - low) + 0.001))"
        result = calculate_by_expression(test_df, expr)
        assert "data" in result.columns

```

### vnpy/alpha/model/models/mlp_model.py (683 行)
```python
import copy
from collections import defaultdict
from typing import Literal, cast
import numpy as np
import pandas as pd
import polars as pl
from sklearn.metrics import mean_squared_error      # type: ignore
import torch
import torch.nn as nn
import torch.optim as optim
from vnpy.alpha import (

class MlpModel(AlphaModel):
    """
    Multi-Layer Perceptron Model

    Alpha factor prediction model implemented using multi-layer perceptron, with main features including:
    1. Building and training multi-layer perceptron neural networks
    2. Predicting Alpha factor values
    3. Model evaluation and feature importance analysis
    4. Support for early stopping and overfitting prevention
    5. Support for MSE loss function
    6. Optional Adam or SGD optimizer
    """

    def __init__(
        self,
        input_size: int,
        hidden_sizes: tuple[int] = (256,),
        lr: float = 0.001,
        n_epochs: int = 300,
        batch_size: int = 2000,
        early_stop_rounds: int = 50,
        eval_steps: int = 20,
        optimizer: Literal["sgd", "adam"] = "adam",
        weight_decay: float = 0.0,
        device: str = "cpu",
        seed: int | None = None
    ) -> None:
        """
        Initialize MLP model

        Parameters
        ----------
        input_size : int, default 360
            Input feature dimension
        hidden_sizes : tuple[int], default (256,)
            Number of neurons in hidden layers
        lr : float, default 0.001
            Learning rate
        n_epochs : int, default 300
            Maximum training steps
    # ... (419 lines omitted) ...
                importance_dict[feature_name] = importance

        df = pd.DataFrame({
            'Feature': list(importance_dict.keys()),
            'Importance': list(importance_dict.values())
        })
        df = df.sort_values('Importance', ascending=False)
        df = df.set_index('Feature')

        return df

class AverageMeter:
    """
    Class for calculating and storing average and current values

    Attributes
    ----------
    val : float
        Current value
    avg : float
        Average value
    sum : float
        Sum
    count : int
        Count
    """

    def __init__(self) -> None:
        """
        Initialize AverageMeter

        Returns
        -------
        None
        """
        self.reset()

    def reset(self) -> None:
        """
        Reset all statistics

        Returns
        -------
        None
        """
        self.val: float = 0
        self.avg: float = 0
        self.sum: float = 0
        self.count: int = 0

    def update(self, val: float, n: int = 1) -> None:
        """
        Update statistics

        Parameters
        ----------
        val : float
            Current value
        n : int, default 1
            Current batch size

        Returns
        -------
        None
        """
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count

class MlpNetwork(nn.Module):
    """
    Deep Neural Network Model Structure

    Used to build multi-layer perceptron network structure, supporting multiple hidden layers
    and different activation functions.

    Attributes
    ----------
    network : nn.ModuleList
        List of neural network layers
    """

    def __init__(
        self,
        input_size: int,
        output_size: int = 1,
        hidden_sizes: tuple[int] = (256,),
        activation: str = "LeakyReLU"
    ) -> None:
        """
        Constructor

        Parameters
        ----------
        input_size : int
            Input feature dimension, i.e., number of features per sample
        output_size : int, default 1
            Output dimension, used for predicting target values
        hidden_sizes : tuple[int], default (256,)
            Tuple of hidden layer neuron counts, e.g., (256, 128) represents two hidden layers
            with 256 and 128 neurons respectively
        activation : str, default "LeakyReLU"
            Activation function type, options:
            - "LeakyReLU": Leaky ReLU function
            - "SiLU": Sigmoid Linear Unit function
        """
        super().__init__()

        # Build network layers
    # ... (81 lines omitted) ...

        Returns
        -------
        torch.Tensor
            Model output tensor, shape (batch_size, output_size)
        """
        # Pass through all layers in the network sequentially
        for layer in self.network:
            x = layer(x)
        return x

```

### vnpy/alpha/strategy/backtesting.py (944 行)
```python
from collections import defaultdict
from datetime import date, datetime
from copy import copy
from typing import cast
import traceback
import numpy as np
import polars as pl
import plotly.graph_objects as go               # type: ignore
from plotly.subplots import make_subplots       # type: ignore
from tqdm import tqdm
from vnpy.trader.constant import Direction, Offset, Interval, Status
from vnpy.trader.object import OrderData, TradeData, BarData
from vnpy.trader.utility import round_to, extract_vt_symbol
from ..logger import logger
from ..lab import AlphaLab
from .template import AlphaStrategy

class BacktestingEngine:
    """Alpha strategy backtesting engine"""

    gateway_name: str = "BACKTESTING"

    def __init__(self, lab: AlphaLab) -> None:
        """Constructor"""
        self.lab: AlphaLab = lab

        self.vt_symbols: list[str] = []
        self.start: datetime
        self.end: datetime

        self.long_rates: dict[str, float] = {}
        self.short_rates: dict[str, float] = {}
        self.sizes: dict[str, float] = {}
        self.priceticks: dict[str, float] = {}

        self.capital: float = 0
        self.risk_free: float = 0
        self.annual_days: int = 0

        self.strategy_class: type[AlphaStrategy]
        self.strategy: AlphaStrategy
        self.bars: dict[str, BarData] = {}
        self.datetime: datetime | None = None

        self.interval: Interval
        self.history_data: dict[tuple, BarData] = {}
        self.dts: set[datetime] = set()

        self.limit_order_count: int = 0
        self.limit_orders: dict[str, OrderData] = {}
        self.active_limit_orders: dict[str, OrderData] = {}

        self.trade_count: int = 0
        self.trades: dict[str, TradeData] = {}

        self.logs: list[str] = []

    # ... (725 lines omitted) ...
        """Get current holding market value"""
        holding_value: float = 0

        for vt_symbol, pos in self.strategy.pos_data.items():
            bar: BarData = self.bars[vt_symbol]
            size: float = self.sizes[vt_symbol]

            holding_value += bar.close_price * pos * size

        return holding_value

class ContractDailyResult:
    """Contract daily profit and loss result"""

    def __init__(self, result_date: date, close_price: float) -> None:
        """Constructor"""
        self.date: date = result_date
        self.close_price: float = close_price
        self.pre_close: float = 0

        self.trades: list[TradeData] = []
        self.trade_count: int = 0

        self.start_pos: float = 0
        self.end_pos: float = 0

        self.turnover: float = 0
        self.commission: float = 0

        self.trading_pnl: float = 0
        self.holding_pnl: float = 0
        self.total_pnl: float = 0
        self.net_pnl: float = 0

    def add_trade(self, trade: TradeData) -> None:
        """Add trade information"""
        self.trades.append(trade)

    def calculate_pnl(
        self,
        pre_close: float,
        start_pos: float,
        size: float,
        long_rate: float,
        short_rate: float
    ) -> None:
        """Calculate profit and loss"""
        # If there is no previous close price, use 1 instead to avoid division error
        if pre_close:
            self.pre_close = pre_close
        # else:
        #     self.pre_close = 1

        # Calculate holding profit and loss
        self.start_pos = start_pos
        self.end_pos = start_pos

        self.holding_pnl = self.start_pos * (self.close_price - self.pre_close) * size

        # Calculate trading profit and loss
        self.trade_count = len(self.trades)

        for trade in self.trades:
            if trade.direction == Direction.LONG:
                pos_change: float = trade.volume
                rate: float = long_rate
            else:
                pos_change = -trade.volume
                rate = short_rate

            self.end_pos += pos_change

            turnover: float = trade.volume * size * trade.price

            self.trading_pnl += pos_change * (self.close_price - trade.price) * size
            self.turnover += turnover
            self.commission += turnover * rate

        # Calculate daily profit and loss
        self.total_pnl = self.trading_pnl + self.holding_pnl
        self.net_pnl = self.total_pnl - self.commission

    def update_close_price(self, close_price: float) -> None:
        """Update daily close price"""
        self.close_price = close_price

class PortfolioDailyResult:
    """Portfolio daily profit and loss result"""

    def __init__(self, result_date: date, close_prices: dict[str, float]) -> None:
        """Constructor"""
        self.date: date = result_date
        self.close_prices: dict[str, float] = close_prices
        self.pre_closes: dict[str, float] = {}
        self.start_poses: dict[str, float] = {}
        self.end_poses: dict[str, float] = {}

        self.contract_results: dict[str, ContractDailyResult] = {}

        for vt_symbol, close_price in close_prices.items():
            self.contract_results[vt_symbol] = ContractDailyResult(result_date, close_price)

        self.trade_count: int = 0
        self.turnover: float = 0
        self.commission: float = 0
        self.trading_pnl: float = 0
        self.holding_pnl: float = 0
        self.total_pnl: float = 0
        self.net_pnl: float = 0

    def add_trade(self, trade: TradeData) -> None:
        """Add trade information"""
        contract_result: ContractDailyResult = self.contract_results[trade.vt_symbol]
        contract_result.add_trade(trade)

    def calculate_pnl(
        self,
        pre_closes: dict[str, float],
        start_poses: dict[str, float],
        sizes: dict[str, float],
        long_rates: dict[str, float],
        short_rates: dict[str, float]
    ) -> None:
        """Calculate profit and loss"""
        self.pre_closes = pre_closes
        self.start_poses = start_poses

        for vt_symbol, contract_result in self.contract_results.items():
            contract_result.calculate_pnl(
                pre_closes.get(vt_symbol, 0),
                start_poses.get(vt_symbol, 0),
                sizes[vt_symbol],
                long_rates[vt_symbol],
                short_rates[vt_symbol]
            )

            self.trade_count += contract_result.trade_count
            self.turnover += contract_result.turnover
            self.commission += contract_result.commission
            self.trading_pnl += contract_result.trading_pnl
            self.holding_pnl += contract_result.holding_pnl
            self.total_pnl += contract_result.total_pnl
            self.net_pnl += contract_result.net_pnl

            self.end_poses[vt_symbol] = contract_result.end_pos

    def update_close_prices(self, close_prices: dict[str, float]) -> None:
        """Update daily close prices"""
        self.close_prices.update(close_prices)

        for vt_symbol, close_price in close_prices.items():
            contract_result: ContractDailyResult | None = self.contract_results.get(vt_symbol, None)
            if contract_result:
                contract_result.update_close_price(close_price)
            else:
                self.contract_results[vt_symbol] = ContractDailyResult(self.date, close_price)

```

### vnpy/rpc/server.py (140 行)
```python
import threading
import traceback
from time import time
from collections.abc import Callable
import zmq
from .common import HEARTBEAT_TOPIC, HEARTBEAT_INTERVAL

class RpcServer:
    """"""

    def __init__(self) -> None:
        """
        Constructor
        """
        # Save functions dict: key is function name, value is function object
        self._functions: dict[str, Callable] = {}

        # Zmq port related
        self._context: zmq.Context = zmq.Context()

        # Reply socket (Request–reply pattern)
        self._socket_rep: zmq.Socket = self._context.socket(zmq.REP)

        # Publish socket (Publish–subscribe pattern)
        self._socket_pub: zmq.Socket = self._context.socket(zmq.PUB)

        # Worker thread related
        self._active: bool = False                          # RpcServer status
        self._thread: threading.Thread | None = None        # RpcServer thread
        self._lock: threading.Lock = threading.Lock()

        # Heartbeat related
        self._heartbeat_at: float | None = None

    def is_active(self) -> bool:
        """"""
        return self._active

    def start(
        self,
        rep_address: str,
        pub_address: str,
    ) -> None:
        """
        Start RpcServer
        """
        if self._active:
    # ... (80 lines omitted) ...
        Check whether it is required to send heartbeat.
        """
        now: float = time()

        if self._heartbeat_at and now >= self._heartbeat_at:
            # Publish heartbeat
            self.publish(HEARTBEAT_TOPIC, now)

            # Update timestamp of next publish
            self._heartbeat_at = now + HEARTBEAT_INTERVAL

```

### vnpy/trader/app.py (21 行)
```python
from abc import ABC
from pathlib import Path
from typing import TYPE_CHECKING

class BaseApp(ABC):
    """
    Abstract class for app.
    """

    app_name: str                       # Unique name used for creating engine and widget
    app_module: str                     # App module string used in import_module
    app_path: Path                      # Absolute path of app folder
    display_name: str                   # Name for display on the menu.
    engine_class: type["BaseEngine"]    # App engine class
    widget_name: str                    # Class name of app widget
    icon_name: str                      # Icon file name of app widget

```

## 配置文件内容
### pyproject.toml
[project]
name = "vnpy"
dynamic = ["version"]
description = "A framework for developing quant trading systems."
readme = "README.md"
license = {text = "MIT"}
authors = [{name = "Xiaoyou Chen", email = "xiaoyou.chen@mail.vnpy.com"}]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "License :: OSI Approved :: MIT License",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX :: Linux",
    "Operating System :: MacOS",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: Implementation :: CPython",
    "Topic :: Office/Business :: Financial :: Investment",
    "Natural Language :: Chinese (Simplified)",
    "Typing :: Typed",
]
requires-python = ">=3.10"
dependencies = [
    "tzlocal>=5.3.1",
    "PySide6==6.8.2.1",
    "pyqtgraph>=0.13.7",
    "qdarkstyle>=3.2.3",
    "numpy>=2.2.3",
    "pandas>=2.2.3",
    "ta-lib>=0.6.4",
    "deap>=1.4.2",
    "pyzmq>=26.3.0",
    "plotly>=6.0.0",
    "tqdm>=4.67.1",
    "loguru>=0.7.3",
    "nbformat>=5.10.4"
]
keywords = ["quant", "quantitative", "investment", "trading", "algotrading"]

[project.optional-dependencies]
alpha = [
    "polars>=1.26.0",
    "scipy>=1.15.2",
    "alphalens-reloaded>=0.4.5",
    "scikit-learn>=1.6.1",
    "lightgbm>=4.6.0",
    "torch>=2.6.0",
    "pyarrow>=19.0.1",



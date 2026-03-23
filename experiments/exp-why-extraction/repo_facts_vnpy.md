# repo_facts: vnpy

## 语言分布
  70 py

## 目录结构（前两层）
/Users/tang/Documents/vibecoding/Doramagic/experiments/exp-why-extraction/vnpy
tests
docs
docs/_templates
docs/_static
docs/community
docs/elite
examples
examples/veighna_trader
examples/client_server
examples/download_bars
examples/candle_chart
examples/cta_backtesting
examples/notebook_trading
examples/data_recorder
examples/alpha_research
examples/simple_rpc
examples/no_ui
examples/portfolio_backtesting
examples/spread_backtesting
.github
.github/workflows
vnpy
vnpy/trader
vnpy/chart
vnpy/rpc
vnpy/alpha
vnpy/event
.git

## README（前100行）
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


## 依赖
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

## 配置文件
pyproject.toml

## 核心代码文件（按大小排序 Top 10）
    1292 vnpy/trader/ui/widget.py
    1281 vnpy/trader/utility.py
     944 vnpy/alpha/strategy/backtesting.py
     683 vnpy/alpha/model/models/mlp_model.py
     676 tests/test_alpha101.py
     633 vnpy/trader/engine.py
     556 vnpy/chart/widget.py
     480 vnpy/alpha/lab.py
     427 vnpy/trader/object.py
     402 vnpy/trader/converter.py

## 关键代码片段
### vnpy/trader/ui/widget.py
```python
"""
Basic widgets for UI.
"""

import csv
import platform
from enum import Enum
from typing import cast, Any
from copy import copy
from tzlocal import get_localzone_name
from datetime import datetime
from importlib import metadata

from .qt import QtCore, QtGui, QtWidgets, Qt
from ..constant import Direction, Exchange, Offset, OrderType
from ..engine import MainEngine, Event, EventEngine
from ..event import (
    EVENT_QUOTE,
    EVENT_TICK,
    EVENT_TRADE,
    EVENT_ORDER,
    EVENT_POSITION,
    EVENT_ACCOUNT,
    EVENT_LOG
)
from ..object import (
    OrderRequest,
    SubscribeRequest,
    CancelRequest,
    ContractData,
    PositionData,
    OrderData,
    QuoteData,
    TickData
)
from ..utility import load_json, save_json, get_digits, ZoneInfo
from ..setting import SETTING_FILENAME, SETTINGS
from ..locale import _


COLOR_LONG = QtGui.QColor("red")
COLOR_SHORT = QtGui.QColor("green")
COLOR_BID = QtGui.QColor(255, 174, 201)
COLOR_ASK = QtGui.QColor(160, 255, 160)
COLOR_BLACK = QtGui.QColor("black")


class BaseCell(QtWidgets.QTableWidgetItem):
    """
    General cell used in tablewidgets.
    """

    def __init__(self, content: Any, data: Any) -> None:
        """"""
        super().__init__()

        self._text: str = ""
        self._data: Any = None

        self.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.set_content(content, data)

    def set_content(self, content: Any, data: Any) -> None:
        """
        Set text content.
        """
        self._text = str(content)
        self._data = data

        self.setText(self._text)

    def get_data(self) -> Any:
        """
        Get data object.
        """
        return self._data

    def __lt__(self, other: "BaseCell") -> bool:        # type: ignore
        """
        Sort by text content.
        """
        result: bool = self._text < other._text
        return result


class EnumCell(BaseCell):
    """
    Cell used for showing enum data.
    """

    def __init__(self, content: Enum, data: Any) -> None:
        """"""
        super().__init__(content, data)

    def set_content(self, content: Any, data: Any) -> None:
        """
        Set text using enum.constant.value.
        """
        if content:
            super().set_content(content.value, data)


class DirectionCell(EnumCell):
    """
    Cell used for showing direction data.
    """

    def __init__(self, content: Enum, data: Any) -> None:
        """"""
        super().__init__(content, data)

    def set_content(self, content: Any, data: Any) -> None:
        """
        Cell color is set according to direction.
        """
        super().set_content(content, data)

        if content is Direction.SHORT:
            self.setForeground(COLOR_SHORT)
        else:
            self.setForeground(COLOR_LONG)


class BidCell(BaseCell):
    """
    Cell used for showing bid price and volume.
    """

    def __init__(self, content: Any, data: Any) -> None:
        """"""
        super().__init__(content, data)

        self.setForeground(COLOR_BID)


class AskCell(BaseCell):
    """
    Cell used for showing ask price and volume.
    """

    def __init__(self, content: Any, data: Any) -> None:
        """"""
        super().__init__(content, data)

        self.setForeground(COLOR_ASK)


class PnlCell(BaseCell):
    """
```

### vnpy/trader/utility.py
```python
"""
General utility functions.
"""

import json
import sys
from datetime import datetime, time
from pathlib import Path
from collections.abc import Callable
from decimal import Decimal
from math import floor, ceil
from typing import overload, Literal

import numpy as np
import talib
from zoneinfo import ZoneInfo, available_timezones      # noqa

from .object import BarData, TickData
from .constant import Exchange, Interval
from .locale import _


def extract_vt_symbol(vt_symbol: str) -> tuple[str, Exchange]:
    """
    :return: (symbol, exchange)
    """
    symbol, exchange_str = vt_symbol.rsplit(".", 1)
    return symbol, Exchange(exchange_str)


def generate_vt_symbol(symbol: str, exchange: Exchange) -> str:
    """
    return vt_symbol
    """
    return f"{symbol}.{exchange.value}"


def _get_trader_dir(temp_name: str) -> tuple[Path, Path]:
    """
    Get path where trader is running in.
    """
    cwd: Path = Path.cwd()
    temp_path: Path = cwd.joinpath(temp_name)

    # If .vntrader folder exists in current working directory,
    # then use it as trader running path.
    if temp_path.exists():
        return cwd, temp_path

    # Otherwise use home path of system.
    home_path: Path = Path.home()
    temp_path = home_path.joinpath(temp_name)

    # Create .vntrader folder under home path if not exist.
    if not temp_path.exists():
        temp_path.mkdir()

    return home_path, temp_path


TRADER_DIR, TEMP_DIR = _get_trader_dir(".vntrader")
sys.path.append(str(TRADER_DIR))


def get_file_path(filename: str) -> Path:
    """
    Get path for temp file with filename.
    """
    return TEMP_DIR.joinpath(filename)


def get_folder_path(folder_name: str) -> Path:
    """
    Get path for temp folder with folder name.
    """
    folder_path: Path = TEMP_DIR.joinpath(folder_name)
    if not folder_path.exists():
        folder_path.mkdir()
    return folder_path


def get_icon_path(filepath: str, ico_name: str) -> str:
    """
    Get path for icon file with ico name.
    """
    ui_path: Path = Path(filepath).parent
    icon_path: Path = ui_path.joinpath("ico", ico_name)
    return str(icon_path)


def load_json(filename: str) -> dict:
    """
    Load data from json file in temp path.
    """
    filepath: Path = get_file_path(filename)

    if filepath.exists():
        with open(filepath, encoding="UTF-8") as f:
            data: dict = json.load(f)
        return data
    else:
        save_json(filename, {})
        return {}


def save_json(filename: str, data: dict) -> None:
    """
    Save data into json file in temp path.
    """
    filepath: Path = get_file_path(filename)
    with open(filepath, mode="w+", encoding="UTF-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


def round_to(value: float, target: float) -> float:
    """
    Round price to price tick value.
    """
    decimal_value: Decimal = Decimal(str(value))
    decimal_target: Decimal = Decimal(str(target))
    rounded: float = float(int(round(decimal_value / decimal_target)) * decimal_target)
    return rounded


def floor_to(value: float, target: float) -> float:
    """
    Similar to math.floor function, but to target float number.
    """
    decimal_value: Decimal = Decimal(str(value))
    decimal_target: Decimal = Decimal(str(target))
    result: float = float(int(floor(decimal_value / decimal_target)) * decimal_target)
    return result


def ceil_to(value: float, target: float) -> float:
    """
    Similar to math.ceil function, but to target float number.
    """
    decimal_value: Decimal = Decimal(str(value))
    decimal_target: Decimal = Decimal(str(target))
    result: float = float(int(ceil(decimal_value / decimal_target)) * decimal_target)
    return result


def get_digits(value: float) -> int:
```

### vnpy/alpha/strategy/backtesting.py
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

        self.daily_results: dict[date, PortfolioDailyResult] = {}
        self.daily_df: pl.DataFrame

        self.pre_closes: defaultdict = defaultdict(float)

        self.cash: float = 0
        self.signal_df: pl.DataFrame

    def set_parameters(
        self,
        vt_symbols: list[str],
        interval: Interval,
        start: datetime,
        end: datetime,
        capital: int = 1_000_000,
        risk_free: float = 0,
        annual_days: int = 240
    ) -> None:
        """Set parameters"""
        self.vt_symbols = vt_symbols
        self.interval = interval

        self.start = start
        self.end = end
        self.capital = capital
        self.risk_free = risk_free
        self.annual_days = annual_days

        self.cash = capital

        contract_settings: dict = self.lab.load_contract_setttings()
        for vt_symbol in vt_symbols:
            setting: dict | None = contract_settings.get(vt_symbol, None)
            if not setting:
                logger.warning(f"找不到合约{vt_symbol}的交易配置，请检查！")
                continue

            self.long_rates[vt_symbol] = setting["long_rate"]
            self.short_rates[vt_symbol] = setting["short_rate"]
            self.sizes[vt_symbol] = setting["size"]
            self.priceticks[vt_symbol] = setting["pricetick"]

    def add_strategy(self, strategy_class: type, setting: dict, signal_df: pl.DataFrame) -> None:
        """Add strategy"""
        self.strategy_class = strategy_class
        self.strategy = strategy_class(
            self, strategy_class.__name__, copy(self.vt_symbols), setting
        )
        self.signal_df = signal_df

    def load_data(self) -> None:
        """Load historical data"""
        logger.info("开始加载历史数据")

        if not self.end:
            self.end = datetime.now()

        if self.start >= self.end:
            logger.info("起始日期必须小于结束日期")
            return

        # Clear previously loaded historical data
        self.history_data.clear()
        self.dts.clear()

        # Load historical data for each symbol
        empty_symbols: list[str] = []
        for vt_symbol in tqdm(self.vt_symbols, total=len(self.vt_symbols)):
            data: list[BarData] = self.lab.load_bar_data(
                vt_symbol,
                self.interval,
                self.start,
                self.end
            )

            for bar in data:
                self.dts.add(bar.datetime)
                self.history_data[(bar.datetime, vt_symbol)] = bar

            data_count = len(data)
            if not data_count:
                empty_symbols.append(vt_symbol)

        if empty_symbols:
            logger.info(f"部分合约历史数据为空：{empty_symbols}")

        logger.info("所有历史数据加载完成")

    def run_backtesting(self) -> None:
```

## 入口文件

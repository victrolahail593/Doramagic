# repo_facts: daily_stock_analysis

## 项目类型: code
代码文件: 260 / 407

## 文件类型分布
 188 py
  49 png
  35 tsx
  32 ts
  26 md
  14 yml
  12 yaml
   7 json
   5 sh
   5 js
   4 ps1
   4 j2
   3 psd
   2 svg
   2 jpg

## 目录结构（前三层）

.git
.github
.github/ISSUE_TEMPLATE
.github/scripts
.github/workflows
api
api/middlewares
api/v1
api/v1/endpoints
api/v1/schemas
apps
apps/dsa-desktop
apps/dsa-desktop/renderer
apps/dsa-web
apps/dsa-web/public
apps/dsa-web/src
bot
bot/commands
bot/platforms
data_provider
docker
docs
docs/architecture
docs/bot
docs/docker
patch
scripts
sources
sources/dsa_vi
sources/dsa_vi/darklogo.iconset
sources/dsa_vi/lightlogo.iconset
src
src/agent
src/agent/skills
src/agent/tools
src/core
src/data
src/notification_sender
src/repositories
src/schemas
src/services
src/utils
strategies
templates
tests

## Layer 1: 结构性文件

### README.md (407 行)
#### 前 200 行
<div align="center">

# 📈 股票智能分析系统

[![GitHub stars](https://img.shields.io/github/stars/ZhuLinsen/daily_stock_analysis?style=social)](https://github.com/ZhuLinsen/daily_stock_analysis/stargazers)
[![CI](https://github.com/ZhuLinsen/daily_stock_analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/ZhuLinsen/daily_stock_analysis/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Ready-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/)

> 🤖 基于 AI 大模型的 A股/港股/美股自选股智能分析系统，每日自动分析并推送「决策仪表盘」到企业微信/飞书/Telegram/邮箱

[**功能特性**](#-功能特性) · [**快速开始**](#-快速开始) · [**推送效果**](#-推送效果) · [**完整指南**](docs/full-guide.md) · [**常见问题**](docs/FAQ.md) · [**更新日志**](docs/CHANGELOG.md)

简体中文 | [English](docs/README_EN.md) | [繁體中文](docs/README_CHT.md)

</div>

## 💖 赞助商 (Sponsors)
<div align="center">
  <a href="https://serpapi.com/baidu-search-api?utm_source=github_daily_stock_analysis" target="_blank">
    <img src="./sources/serpapi_banner_zh.png" alt="轻松抓取搜索引擎上的实时金融新闻数据 - SerpApi" height="160">
  </a>
</div>
<br>


## ✨ 功能特性

| 模块 | 功能 | 说明 |
|------|------|------|
| AI | 决策仪表盘 | 一句话核心结论 + 精确买卖点位 + 操作检查清单 |
| 分析 | 多维度分析 | 技术面（盘中实时 MA/多头排列）+ 筹码分布 + 舆情情报 + 实时行情 |
| 市场 | 全球市场 | 支持 A股、港股、美股及美股指数（SPX、DJI、IXIC 等） |
| 基本面 | 结构化聚合 | 新增 `fundamental_context`（valuation/growth/earnings/institution/capital_flow/dragon_tiger/boards，其中 `boards` 表示板块涨跌榜），主链路 fail-open 降级 |
| 策略 | 市场策略系统 | 内置 A股「三段式复盘策略」与美股「Regime Strategy」，输出进攻/均衡/防守或 risk-on/neutral/risk-off 计划，并附“仅供参考，不构成投资建议”提示 |
| 复盘 | 大盘复盘 | 每日市场概览、板块涨跌；支持 cn(A股)/us(美股)/both(两者) 切换 |
| 智能导入 | 多源导入 | 支持图片、CSV/Excel 文件、剪贴板粘贴；Vision LLM 提取代码+名称；置信度分层确认；名称→代码解析（本地+拼音+AkShare） |
| 回测 | AI 回测验证 | 自动评估历史分析准确率，方向胜率、止盈止损命中率 |
| **Agent 问股** | **策略对话** | **多轮策略问答，支持均线金叉/缠论/波浪等 11 种内置策略，Web/Bot/API 全链路** |
| 推送 | 多渠道通知 | 企业微信、飞书、Telegram、钉钉、邮件、Pushover |
| 自动化 | 定时运行 | GitHub Actions 定时执行，无需服务器 |

> 历史报告详情会优先展示 AI 返回的原始「狙击点位」文本，避免区间价、条件说明等复杂内容在历史回看时被压缩成单个数字。

### 技术栈与数据来源

| 类型 | 支持 |
|------|------|
| AI 模型 | [AIHubMix](https://aihubmix.com/?aff=CfMq)、Gemini、OpenAI 兼容、DeepSeek、通义千问、Claude 等（统一通过 [LiteLLM](https://github.com/BerriAI/litellm) 调用，支持多 Key 负载均衡）|
| 行情数据 | AkShare、Tushare、Pytdx、Baostock、YFinance |
| 新闻搜索 | Tavily、SerpAPI、Bocha、Brave、MiniMax |

> 注：美股历史数据与实时行情统一使用 YFinance，确保复权一致性

### 内置交易纪律

| 规则 | 说明 |
|------|------|
| 严禁追高 | 乖离率超阈值（默认 5%，可配置）自动提示风险；强势趋势股自动放宽 |
| 趋势交易 | MA5 > MA10 > MA20 多头排列 |
| 精确点位 | 买入价、止损价、目标价 |
| 检查清单 | 每项条件以「满足 / 注意 / 不满足」标记 |
| 新闻时效 | 可配置新闻最大时效（默认 3 天），避免使用过时信息 |

## 🚀 快速开始

### 方式一：GitHub Actions（推荐）

> 5 分钟完成部署，零成本，无需服务器。


#### 1. Fork 本仓库

点击右上角 `Fork` 按钮（顺便点个 Star⭐ 支持一下）

#### 2. 配置 Secrets

`Settings` → `Secrets and variables` → `Actions` → `New repository secret`

**AI 模型配置（至少配置一个）**

> 详细配置说明见 [LLM 配置指南](docs/LLM_CONFIG_GUIDE.md)（三层配置、渠道模式、YAML高级配置、Vision、Agent、排错），GitHub Actions用户也可以实现YAML高级配置。进阶用户可配置 `LITELLM_MODEL`、`LITELLM_FALLBACK_MODELS` 或 `LLM_CHANNELS` 多渠道模式。

> 💡 **推荐 [AIHubMix](https://aihubmix.com/?aff=CfMq)**：一个 Key 即可使用 Gemini、GPT、Claude、DeepSeek 等全球主流模型，无需科学上网，含免费模型（glm-5、gpt-4o-free 等），付费模型高稳定性无限并发。本项目可享 **10% 充值优惠**。

| Secret 名称 | 说明 | 必填 |
|------------|------|:----:|
| `AIHUBMIX_KEY` | [AIHubMix](https://aihubmix.com/?aff=CfMq) API Key，一 Key 切换使用全系模型，免费模型可用 | 可选 |
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/) 获取免费 Key（需科学上网） | 可选 |
| `ANTHROPIC_API_KEY` | [Anthropic Claude](https://console.anthropic.com/) API Key | 可选 |
| `ANTHROPIC_MODEL` | Claude 模型（如 `claude-3-5-sonnet-20241022`） | 可选 |
| `OPENAI_API_KEY` | OpenAI 兼容 API Key（支持 DeepSeek、通义千问等） | 可选 |
| `OPENAI_BASE_URL` | OpenAI 兼容 API 地址（如 `https://api.deepseek.com/v1`） | 可选 |
| `OPENAI_MODEL` | 模型名称（如 `gemini-3.1-pro-preview`、`gemini-3-flash-preview`、`gpt-5.2`） | 可选 |
| `OPENAI_VISION_MODEL` | 图片识别专用模型（部分第三方模型不支持图像；不填则用 `OPENAI_MODEL`） | 可选 |

> 注：AI 优先级 Gemini > Anthropic > OpenAI（含 AIHubmix），至少配置一个。`AIHUBMIX_KEY` 无需配置 `OPENAI_BASE_URL`，系统自动适配。图片识别需 Vision 能力模型。DeepSeek 思考模式（deepseek-reasoner、deepseek-r1、qwq、deepseek-chat）按模型名自动识别，无需额外配置。

<details>
<summary><b>通知渠道配置</b>（点击展开，至少配置一个）</summary>


| Secret 名称 | 说明 | 必填 |
|------------|------|:----:|
| `WECHAT_WEBHOOK_URL` | 企业微信 Webhook URL | 可选 |
| `FEISHU_WEBHOOK_URL` | 飞书 Webhook URL | 可选 |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token（@BotFather 获取） | 可选 |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID | 可选 |
| `TELEGRAM_MESSAGE_THREAD_ID` | Telegram Topic ID (用于发送到子话题) | 可选 |
| `EMAIL_SENDER` | 发件人邮箱（如 `xxx@qq.com`） | 可选 |
| `EMAIL_PASSWORD` | 邮箱授权码（非登录密码） | 可选 |
| `EMAIL_RECEIVERS` | 收件人邮箱（多个用逗号分隔，留空则发给自己） | 可选 |
| `EMAIL_SENDER_NAME` | 邮件发件人显示名称（默认：daily_stock_analysis股票分析助手） | 可选 |
| `STOCK_GROUP_N` / `EMAIL_GROUP_N` | 股票分组发往不同邮箱（如 `STOCK_GROUP_1=600519,300750` `EMAIL_GROUP_1=user1@example.com`） | 可选 |
| `PUSHPLUS_TOKEN` | PushPlus Token（[获取地址](https://www.pushplus.plus)，国内推送服务） | 可选 |
| `PUSHPLUS_TOPIC` | PushPlus 群组编码（一对多推送，配置后消息推送给群组所有订阅用户） | 可选 |
| `SERVERCHAN3_SENDKEY` | Server酱³ Sendkey（[获取地址](https://sc3.ft07.com/)，手机APP推送服务） | 可选 |
| `CUSTOM_WEBHOOK_URLS` | 自定义 Webhook（支持钉钉等，多个用逗号分隔） | 可选 |
| `CUSTOM_WEBHOOK_BEARER_TOKEN` | 自定义 Webhook 的 Bearer Token（用于需要认证的 Webhook） | 可选 |
| `WEBHOOK_VERIFY_SSL` | Webhook HTTPS 证书校验（默认 true）。设为 false 可支持自签名证书。警告：关闭有严重安全风险，仅限可信内网 | 可选 |
| `SINGLE_STOCK_NOTIFY` | 单股推送模式：设为 `true` 则每分析完一只股票立即推送 | 可选 |
| `REPORT_TYPE` | 报告类型：`simple`(精简)、`full`(完整)、`brief`(3-5句概括)，Docker环境推荐设为 `full` | 可选 |
| `REPORT_SUMMARY_ONLY` | 仅分析结果摘要：设为 `true` 时只推送汇总，不含个股详情 | 可选 |
| `REPORT_TEMPLATES_DIR` | Jinja2 模板目录（相对项目根，默认 `templates`） | 可选 |
| `REPORT_RENDERER_ENABLED` | 启用 Jinja2 模板渲染（默认 `false`，保证零回归） | 可选 |
| `REPORT_INTEGRITY_ENABLED` | 启用报告完整性校验，缺失必填字段时重试或占位补全（默认 `true`） | 可选 |
| `REPORT_INTEGRITY_RETRY` | 完整性校验重试次数（默认 `1`，`0` 表示仅占位不重试） | 可选 |
| `REPORT_HISTORY_COMPARE_N` | 历史信号对比条数，`0` 关闭（默认），`>0` 启用 | 可选 |
| `ANALYSIS_DELAY` | 个股分析和大盘分析之间的延迟（秒），避免API限流，如 `10` | 可选 |
| `MERGE_EMAIL_NOTIFICATION` | 个股与大盘复盘合并推送（默认 false），减少邮件数量 | 可选 |
| `MARKDOWN_TO_IMAGE_CHANNELS` | 将 Markdown 转为图片发送的渠道（逗号分隔）：`telegram,wechat,custom,email` | 可选 |
| `MARKDOWN_TO_IMAGE_MAX_CHARS` | 超过此长度不转图片，避免超大图片（默认 `15000`） | 可选 |
| `MD2IMG_ENGINE` | 转图引擎：`wkhtmltoimage`（默认）或 `markdown-to-file`（emoji 更好） | 可选 |

> 至少配置一个渠道，配置多个则同时推送。图片发送与引擎安装细节请参考 [完整指南](docs/full-guide.md)

</details>

**其他配置**

| Secret 名称 | 说明 | 必填 |
|------------|------|:----:|
| `STOCK_LIST` | 自选股代码，如 `600519,hk00700,AAPL,TSLA` | ✅ |
| `TAVILY_API_KEYS` | [Tavily](https://tavily.com/) 搜索 API（新闻搜索） | 推荐 |
| `MINIMAX_API_KEYS` | [MiniMax](https://platform.minimaxi.com/) Coding Plan Web Search（结构化搜索结果） | 可选 |
| `SERPAPI_API_KEYS` | [SerpAPI](https://serpapi.com/baidu-search-api?utm_source=github_daily_stock_analysis) 全渠道搜索 | 可选 |
| `BOCHA_API_KEYS` | [博查搜索](https://open.bocha.cn/) Web Search API（中文搜索优化，支持AI摘要，多个key用逗号分隔） | 可选 |
| `BRAVE_API_KEYS` | [Brave Search](https://brave.com/search/api/) API（隐私优先，美股优化，多个key用逗号分隔） | 可选 |
| `SEARXNG_BASE_URLS` | SearXNG 自建实例（无配额兜底，需在 settings.yml 启用 format: json） | 可选 |
| `TUSHARE_TOKEN` | [Tushare Pro](https://tushare.pro/weborder/#/login?reg=834638 ) Token | 可选 |
| `PREFETCH_REALTIME_QUOTES` | 实时行情预取开关：设为 `false` 可禁用全市场预取（默认 `true`） | 可选 |
| `WECHAT_MSG_TYPE` | 企微消息类型，默认 markdown，支持配置 text 类型，发送纯 markdown 文本 | 可选 |
| `NEWS_MAX_AGE_DAYS` | 新闻最大时效（天），默认 3，避免使用过时信息 | 可选 |
| `BIAS_THRESHOLD` | 乖离率阈值（%），默认 5.0，超过提示不追高；强势趋势股自动放宽 | 可选 |
| `AGENT_MODE` | 开启 Agent 策略问股模式（`true`/`false`，默认 false） | 可选 |
| `AGENT_SKILLS` | 激活的策略（逗号分隔），`all` 启用全部 11 个；不配置时默认 4 个，详见 `.env.example` | 可选 |
| `AGENT_MAX_STEPS` | Agent 最大推理步数（默认 10） | 可选 |
| `AGENT_STRATEGY_DIR` | 自定义策略目录（默认内置 `strategies/`） | 可选 |
| `TRADING_DAY_CHECK_ENABLED` | 交易日检查（默认 `true`）：非交易日跳过执行；设为 `false` 或使用 `--force-run` 强制执行 | 可选 |
| `ENABLE_CHIP_DISTRIBUTION` | 启用筹码分布（Actions 默认 false；需筹码数据时在 Variables 中设为 true，接口可能不稳定） | 可选 |
| `ENABLE_FUNDAMENTAL_PIPELINE` | 基本面聚合总开关；关闭时保持主流程不变 | 可选 |
| `FUNDAMENTAL_STAGE_TIMEOUT_SECONDS` | 基本面阶段总预算（秒） | 可选 |
| `FUNDAMENTAL_FETCH_TIMEOUT_SECONDS` | 单能力源调用超时（秒） | 可选 |
| `FUNDAMENTAL_RETRY_MAX` | 基本面能力重试次数（包含首次） | 可选 |
| `FUNDAMENTAL_CACHE_TTL_SECONDS` | 基本面缓存 TTL（秒） | 可选 |
| `FUNDAMENTAL_CACHE_MAX_ENTRIES` | 基本面缓存最大条目数（避免长时间运行内存增长） | 可选 |

> 基本面超时语义（P0）：
> - 当前采用 `best-effort` 软超时（fail-open），超时会立即降级并继续主流程；
> - 不承诺严格硬中断第三方调用线程，因此 `P95 <= 1.5s` 是阶段目标而非硬 SLA；
> - 若业务需要硬 SLA，可在后续阶段升级为“子进程隔离 + kill”的硬超时方案。
> - 字段契约：
>   - `fundamental_context.boards.data` = `sector_rankings`（板块涨跌榜，结构 `{top, bottom}`）；
>   - `get_stock_info.belong_boards` = 个股所属板块列表；
>   - `get_stock_info.boards` 为兼容别名，值与 `belong_boards` 相同（未来仅在大版本考虑移除）；
>   - `get_stock_info.sector_rankings` 与 `fundamental_context.boards.data` 保持一致。
> - 板块涨跌榜采用固定回退顺序：`AkShare(EM->Sina) -> Tushare -> efinance`。

#### 3. 启用 Actions

`Actions` 标签 → `I understand my workflows, go ahead and enable them`

#### 4. 手动测试

`Actions` → `每日股票分析` → `Run workflow` → `Run workflow`

#### 完成

默认每个**工作日 18:00（北京时间）**自动执行，也可手动触发。默认非交易日（含 A/H/US 节假日）不执行。

> 💡 **关于跳过交易日检查的两种机制：**
> | 机制 | 配置方式 | 生效范围 | 适用场景 |
> |------|----------|----------|----------|
> | `TRADING_DAY_CHECK_ENABLED=false` | 环境变量/Secrets | 全局、长期有效 | 测试环境、长期关闭检查 |
> | `force_run` (UI 勾选) | Actions 手动触发时选择 | 单次运行 | 临时在非交易日执行一次 |
>
> - **环境变量方式**：在 `.env` 或 GitHub Secrets 中设置，影响所有运行方式（定时触发、手动触发、本地运行）
> - **UI 勾选方式**：仅在 GitHub Actions 手动触发时可见，不影响定时任务，适合临时需求

#### 后 50 行
## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

详见 [贡献指南](docs/CONTRIBUTING.md)

### 本地门禁（建议先跑）

```bash
pip install -r requirements.txt
pip install flake8 pytest
./scripts/ci_gate.sh
```

如修改前端（`apps/dsa-web`）：

```bash
cd apps/dsa-web
npm ci
npm run lint
npm run build
```

## 📄 License
[MIT License](LICENSE) © 2026 ZhuLinsen

如果你在项目中使用或基于本项目进行二次开发，
非常欢迎在 README 或文档中注明来源并附上本仓库链接。
这将有助于项目的持续维护和社区发展。

## 📬 联系与合作
- GitHub Issues：[提交 Issue](https://github.com/ZhuLinsen/daily_stock_analysis/issues)
- 合作邮箱：zhuls345@gmail.com

## ⭐ Star History
**如果觉得有用，请给个 ⭐ Star 支持一下！**

<a href="https://star-history.com/#ZhuLinsen/daily_stock_analysis&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=ZhuLinsen/daily_stock_analysis&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=ZhuLinsen/daily_stock_analysis&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=ZhuLinsen/daily_stock_analysis&type=Date" />
 </picture>
</a>

## ⚠️ 免责声明

本项目仅供学习和研究使用，不构成任何投资建议。股市有风险，投资需谨慎。作者不对使用本项目产生的任何损失负责。

---

#### README 结构分析（所有标题）
3:# 📈 股票智能分析系统
20:## 💖 赞助商 (Sponsors)
29:## ✨ 功能特性
47:### 技术栈与数据来源
57:### 内置交易纪律
67:## 🚀 快速开始
69:### 方式一：GitHub Actions（推荐）
74:#### 1. Fork 本仓库
78:#### 2. 配置 Secrets
181:#### 3. 启用 Actions
185:#### 4. 手动测试
189:#### 完成
202:### 方式二：本地运行 / Docker 部署
205:# 克隆项目
208:# 安装依赖
211:# 配置环境变量
214:# 运行分析
221:## 📱 推送效果
223:### 决策仪表盘
253:### 大盘复盘
269:## ⚙️ 配置说明
274:## 🖥️ Web 界面
282:### 智能导入
300:### 历史报告详情
304:### 🤖 Agent 策略问股
319:### 启动方式
338:## 🗺️ Roadmap
347:## ☕ 支持项目
358:## 🤝 贡献
364:### 本地门禁（建议先跑）
381:## 📄 License
388:## 📬 联系与合作
392:## ⭐ Star History
403:## ⚠️ 免责声明

#### README 链接统计
外部链接数: 37
GitHub 链接数: 8
图片引用数: 7

### 依赖文件
#### requirements.txt
# ===================================
# A股自选股智能分析系统 - 依赖列表
# ===================================

# 核心依赖
python-dotenv>=1.0.0        # 环境变量配置管理
tenacity>=8.2.0             # 重试机制（指数退避）
sqlalchemy>=2.0.0           # ORM数据库操作
schedule>=1.2.0             # 定时任务调度
exchange-calendars>=4.5.0   # 交易日历（A股/港股/美股，Issue #373）

# 数据源依赖（多源策略，按优先级排序）
efinance>=0.5.5             # Priority 0: 东方财富数据源（最高优先级）https://github.com/Micro-sheep/efinance
akshare>=1.12.0             # Priority 1: 东方财富爬虫数据源
tushare>=1.4.0              # Priority 2: 挖地兔 Pro API
pytdx>=1.72                 # Priority 2: 通达信行情服务器
baostock>=0.8.0             # Priority 3: 证券宝数据
yfinance>=0.2.0             # Priority 4: Yahoo Finance (Fallback)

#飞书
lark-oapi>=1.0.0             # 飞书API

# 数据处理
pandas>=2.0.0               # 数据分析
pypinyin>=0.50.0            # Name-to-code resolver (pinyin matching)
openpyxl>=3.1.0             # Excel (.xlsx) parsing for import
numpy>=1.24.0               # 数值计算
json-repair>=0.55.1         # JSON 修复

# AI 分析
litellm>=1.80.10            # Unified LLM client (Gemini/Anthropic/OpenAI/DeepSeek etc.)
tiktoken>=0.8.0,<0.12.0    # BPE tokenizer for LLM token counting (pin <0.12 to avoid plugin registration issues, #537)
openai>=1.0.0               # OpenAI SDK (transitive dependency of litellm, kept explicit)
PyYAML>=6.0                 # YAML parser for LITELLM_CONFIG support

# 搜索引擎（用于获取股票新闻）
tavily-python>=0.3.0        # Tavily 搜索 API（每月 1000 次免费）
google-search-results>=2.4.0  # SerpAPI（每月 100 次免费）

# 网络请求
requests>=2.31.0            # HTTP 请求
markdown2>=2.4.0            # Markdown 转 HTML
imgkit>=1.2.0              # Markdown 转图片（需安装 wkhtmltopdf）
fake-useragent>=1.4.0       # 随机 User-Agent 防封禁
httpx[socks]                # HTTP 客户端 + SOCKS 代理支持（OpenAI 可选依赖）
dingtalk-stream >= 0.24.3    # 钉钉 Stream SDK
# 数据库
# SQLite 是 Python 内置，无需额外安装

# Discord 机器人
discord.py>=2.0.0              # Discord 机器人开发库

# Web Content Extraction
newspaper3k>=0.2.8          # Article extraction
lxml_html_clean             # Fix for lxml.html.clean ImportError in newer lxml versions

# 报告模板引擎（Report Engine P0）
jinja2>=3.1.0               # Jinja2 template engine for report rendering

# FastAPI Web 框架
fastapi>=0.109.0            # 现代 Python Web 框架
uvicorn[standard]>=0.27.0   # ASGI 服务器
python-multipart>=0.0.6     # FastAPI File/Form upload support

#### setup.cfg
[flake8]
max-line-length = 120
exclude = 
    .git,
    __pycache__,
    .env,
    venv,
    .venv,
    build,
    dist,
    *.egg-info
# E501: 行太长（有些地方确实需要长行）
# W503: 运算符在换行前（与 black 冲突）
# E203: 切片前的空格（与 black 冲突）
# E402: 模块级导入不在文件顶部（有时需要先设置环境变量）
ignore = E501,W503,E203,E402

[tool:pytest]
testpaths = .
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short
markers =
    unit: fast offline unit tests
    integration: service-level integration tests without external network dependency
    network: tests requiring external network or third-party services

[isort]
profile = black
line_length = 120
skip = .git,__pycache__,.env,venv,.venv
known_first_party = config,storage,analyzer,notification,scheduler,search_service,market_analyzer,stock_analyzer,data_provider

#### pyproject.toml
[tool.black]
line-length = 120
target-version = ['py310', 'py311', 'py312']
include = '\.pyi?$'
exclude = '''
/(
    \.git
    | \.hg
    | \.mypy_cache
    | \.tox
    | \.venv
    | venv
    | _build
    | buck-out
    | build
    | dist
    | __pycache__
)/
'''

[tool.isort]
profile = "black"
line_length = 120
skip = [".git", "__pycache__", ".env", "venv", ".venv"]

[tool.bandit]
exclude_dirs = ["tests", "test_*.py"]
skips = ["B101"]  # assert 语句在测试中是允许的


### CI/CD 配置
#### .github/workflows/auto-tag.yml
name: Auto Tag

# 触发条件：当代码 push 到 main 分支时
on:
  push:
    branches: [main]
    paths-ignore:
      - 'docs/**'
      - '**.md'
      - 'LICENSE'
      - '.gitignore'
      - 'local/**'
      - '.github/**'
      - 'source/**'

jobs:
  tag:
    runs-on: ubuntu-latest
    # Default: NO tag. Only tag when commit message contains #patch, #minor, or #major.
    if: >-
      contains(github.event.head_commit.message, '#patch') ||
      contains(github.event.head_commit.message, '#minor') ||
      contains(github.event.head_commit.message, '#major')

    permissions:
      contents: write

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Bump version and push tag
        uses: anothrNick/github-tag-action@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          WITH_V: true
          DEFAULT_BUMP: patch
          INITIAL_VERSION: 2.1.0
          PATCH_STRING_TOKEN: '#patch'
          MINOR_STRING_TOKEN: '#minor'
          MAJOR_STRING_TOKEN: '#major'

#### .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main]

concurrency:
  group: ci-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

jobs:
  changes:
    name: 🔎 Change Detection
    runs-on: ubuntu-latest
    outputs:
      frontend: ${{ steps.filter.outputs.frontend }}
    steps:
      - name: 📥 Checkout
        uses: actions/checkout@v4
      - name: 🧭 Filter paths
        id: filter
        uses: dorny/paths-filter@v3
        with:
          filters: |
            frontend:
              - 'apps/dsa-web/**'

  backend-gate:
    name: backend-gate
    runs-on: ubuntu-latest
    steps:
      - name: 📥 Checkout
        uses: actions/checkout@v4
      - name: 🐍 Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - name: 📦 Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install flake8 pytest
      - name: ✅ Run backend gate
        run: ./scripts/ci_gate.sh

  docker-build:
    name: docker-build
    runs-on: ubuntu-latest
    needs: [backend-gate]
    steps:
      - name: 📥 Checkout
        uses: actions/checkout@v4
      - name: 🐳 Build image
        run: |
          docker build -t stock-analysis:test -f docker/Dockerfile .
          docker run --rm stock-analysis:test python -c "print('✅ Docker OK')"
      - name: 🔍 Docker smoke imports
        run: |
          docker run --rm stock-analysis:test python -c "
          from src.config import get_config; print('✅ config')
          from src.storage import DatabaseManager; print('✅ storage')
          from src.notification import NotificationService; print('✅ notification')
          from data_provider import DataFetcherManager; print('✅ data_provider')
          from src.analyzer import GeminiAnalyzer; print('✅ analyzer')
          from patch.eastmoney_patch import eastmoney_patch; print('✅ patch')
          from bot.dispatcher import CommandDispatcher; print('✅ bot')
          from api.app import app; print('✅ api')
          print('✅ All Docker imports OK')
          "

  web-gate:
    name: web-gate
    runs-on: ubuntu-latest
    needs: [changes]
    if: needs.changes.outputs.frontend == 'true'
    defaults:
      run:
        working-directory: apps/dsa-web
    steps:

#### .github/workflows/create-release.yml
name: Create GitHub Release from Tag

# Trigger: annotated tag pushed (vX.Y.Z)
on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Extract tag annotation message
        id: tag_body
        run: |
          TAG="${GITHUB_REF_NAME}"
          # Get full annotation message (body only, strip first line if it's just the version)
          BODY="$(git tag -l --format='%(contents)' "$TAG")"
          if [[ -z "${BODY// }" ]]; then
            echo "No annotation message found for $TAG, using default."
            BODY="See CHANGELOG for details."
          fi
          # Write to file to safely handle multi-line content
          printf '%s' "$BODY" > /tmp/release_body.txt
          echo "tag=$TAG" >> "$GITHUB_OUTPUT"

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ steps.tag_body.outputs.tag }}
          name: ${{ steps.tag_body.outputs.tag }}
          body_path: /tmp/release_body.txt
          draft: false
          prerelease: false
          generate_release_notes: false

#### .github/workflows/daily_analysis.yml
name: 每日股票分析

on:
  # 定时触发 - 每天北京时间 18:00 (UTC 10:00)
  schedule:
    - cron: '0 10 * * 1-5'     # 周一到周五，UTC 10:00 = 北京时间 18:00
  
  # 手动触发
  workflow_dispatch:
    inputs:
      mode:
        description: '运行模式'
        required: true
        default: 'full'
        type: choice
        options:
          - full          # 完整分析（股票+大盘）
          - market-only   # 仅大盘复盘
          - stocks-only   # 仅股票分析
      force_run:
        description: '强制运行（跳过交易日检查）'
        required: false
        default: false
        type: boolean

# 并发控制：同一时间只运行一个分析任务
concurrency:
  group: stock-analysis
  cancel-in-progress: false

jobs:
  analyze:
    runs-on: ubuntu-latest
    # 添加超时限制，防止任务卡死
    timeout-minutes: 30
    
    steps:
      - name: 随机延迟（避免固定时间访问）
        run: sleep $((RANDOM % 60))  # 随机延迟0-60秒启动
      
      - name: 检出代码
        uses: actions/checkout@v4
      
      - name: 设置 Python 环境
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: 安装依赖
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: 创建必要目录
        run: |
          mkdir -p data logs reports
      
      - name: 执行股票分析
        env:
          # ==========================================
          # AI 配置
          # ==========================================
          # LITELLM_CONFIG
          LITELLM_CONFIG: ${{ vars.LITELLM_CONFIG || secrets.LITELLM_CONFIG }}
          LITELLM_CONFIG_YAML: ${{ vars.LITELLM_CONFIG_YAML || secrets.LITELLM_CONFIG_YAML }}
          LITELLM_API_KEY: ${{ secrets.LITELLM_API_KEY }}
          LITELLM_MODEL: ${{ vars.LITELLM_MODEL || secrets.LITELLM_MODEL }}

          # Gemini AI（主选）
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GEMINI_MODEL: ${{ vars.GEMINI_MODEL || secrets.GEMINI_MODEL || 'gemini-3-flash-preview' }}
          GEMINI_MODEL_FALLBACK: ${{ vars.GEMINI_MODEL_FALLBACK || secrets.GEMINI_MODEL_FALLBACK || 'gemini-2.5-flash' }}
          GEMINI_REQUEST_DELAY: '3.0'
          
          # AIHubMix（优先于 OPENAI_API_KEY，自动适配 base_url，推荐国内用户）
          AIHUBMIX_KEY: ${{ secrets.AIHUBMIX_KEY }}

          # OpenAI 兼容 API（备选）
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

#### .github/workflows/desktop-release.yml
name: Desktop Release

on:
  push:
    tags:
      - 'v*.*.*'
  workflow_dispatch:
    inputs:
      release_tag:
        description: 'Existing release tag in semver format, e.g. v3.2.12'
        required: true
        type: string

concurrency:
  group: desktop-release-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build-windows:
    runs-on: windows-latest
    permissions:
      contents: read
    env:
      RELEASE_TAG: ${{ github.event_name == 'workflow_dispatch' && inputs.release_tag || github.ref_name }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Resolve release ref
        shell: bash
        run: |
          if [[ "${GITHUB_EVENT_NAME}" == "workflow_dispatch" ]]; then
            [[ "${RELEASE_TAG}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]
            git fetch --tags --force
            git rev-parse "${RELEASE_TAG}" >/dev/null
            git checkout "${RELEASE_TAG}"
          fi

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: |
            apps/dsa-web/package-lock.json
            apps/dsa-desktop/package-lock.json

      - name: Build desktop package (Windows)
        shell: pwsh
        env:
          DSA_SKIP_DEVMODE_CHECK: 'true'
        run: |
          powershell -ExecutionPolicy Bypass -File scripts/build-all.ps1

      - name: Prepare release artifact (Windows)
        shell: pwsh
        run: |
          $installerExe = Get-ChildItem -Path 'apps/dsa-desktop/dist' -Filter '*.exe' `
            | Where-Object { $_.Name -match 'Setup' } `
            | Sort-Object LastWriteTime -Descending `
            | Select-Object -First 1
          if (-not $installerExe) {
            throw 'No NSIS setup .exe found under apps/dsa-desktop/dist.'
          }
          $winUnpacked = 'apps/dsa-desktop/dist/win-unpacked'
          if (-not (Test-Path $winUnpacked)) {
            throw 'No win-unpacked directory found under apps/dsa-desktop/dist.'
          }
          New-Item -ItemType Directory -Path 'dist/release-assets' -Force | Out-Null
          $exeTarget = "dist/release-assets/daily-stock-analysis-windows-installer-$env:RELEASE_TAG.exe"
          $zipTarget = "dist/release-assets/daily-stock-analysis-windows-noinstall-$env:RELEASE_TAG.zip"
          Copy-Item -Path $installerExe.FullName -Destination $exeTarget -Force
          Compress-Archive -Path $winUnpacked -DestinationPath $zipTarget -CompressionLevel Optimal -Force

      - uses: actions/upload-artifact@v4

#### .github/workflows/docker-publish.yml
name: Docker Publish

on:
  push:
    tags:
      - 'v*.*.*'
  workflow_dispatch:
    inputs:
      release_tag:
        description: 'Release tag in semver format, e.g. v3.0.6'
        required: true
        type: string

concurrency:
  group: docker-publish-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      id-token: write

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Resolve release ref
        run: |
          if [[ "${GITHUB_EVENT_NAME}" == "workflow_dispatch" ]]; then
            RELEASE_TAG="${{ inputs.release_tag }}"
            [[ "$RELEASE_TAG" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]
            git fetch --tags --force
            git rev-parse "$RELEASE_TAG" >/dev/null
            git checkout "$RELEASE_TAG"
            echo "Using manual release tag: $RELEASE_TAG"
          else
            echo "Using event ref: ${GITHUB_REF_NAME}"
          fi

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install backend gate dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install flake8 pytest

      - name: Run backend gate before publish
        run: ./scripts/ci_gate.sh

      - name: Validate release docs
        run: |
          test -f README.md
          if [[ "${GITHUB_EVENT_NAME}" == "workflow_dispatch" ]]; then
            [[ "${{ inputs.release_tag }}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]
            VERSION="${{ inputs.release_tag }}"
          elif [[ "${GITHUB_REF_TYPE:-}" == "tag" ]]; then
            VERSION="${GITHUB_REF_NAME}"
          else
            echo "Unsupported trigger type"
            exit 1
          fi
          # Validate using annotated tag message instead of CHANGELOG entry.
          # Requires: git tag -a <version> -m "<release notes>"
          TAG_BODY="$(git tag -l --format='%(contents)' "$VERSION")"
          if [[ -z "${TAG_BODY// }" ]]; then
            echo "ERROR: Tag $VERSION has no annotation message."
            echo "Use: git tag -a $VERSION -m '<release notes>' (annotated tag required)"
            exit 1
          fi
          echo "Tag annotation found for $VERSION ($(echo "$TAG_BODY" | wc -l) lines). Gate passed."

      - uses: docker/setup-buildx-action@v3

#### .github/workflows/ghcr-dockerhub.yml
name: Build and Push Multi-Arch Docker Images 2026.1.26同时推送镜像至ghcr和dockerhub

on:
  workflow_dispatch:
    inputs:
      image_tag:
        description: 'Image tag version (e.g., v1.0.0, latest)'
        required: true
        default: 'latest'

env:
  GHCR_REGISTRY: ghcr.io
  DOCKERHUB_REGISTRY: docker.io
  # GitHub 仓库全名作为 GHCR 镜像名
  GHCR_IMAGE_NAME: ${{ github.repository }}
  # Docker Hub 镜像名（需要根据实际情况设置）
  DOCKERHUB_IMAGE_NAME: ${{ secrets.DOCKERHUB_USERNAME }}/${{ github.event.repository.name }}

jobs:
  build-and-push:
    runs-on: ubuntu-24.04
    permissions:
      contents: read
      packages: write
      id-token: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
        with:
          driver-opts: |
            image=moby/buildkit:master
            network=host

      - name: Set up QEMU for multi-platform build
        uses: docker/setup-qemu-action@v3

      # 登录到 GHCR
      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.GHCR_REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      # 登录到 Docker Hub（需要预先设置 secrets.DOCKERHUB_USERNAME 和 secrets.DOCKERHUB_TOKEN）
      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          registry: ${{ env.DOCKERHUB_REGISTRY }}
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      # 为 GHCR 生成元数据
      - name: Extract metadata for GHCR
        id: meta-ghcr
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.GHCR_REGISTRY }}/${{ env.GHCR_IMAGE_NAME }}
          tags: |
            type=raw,value=${{ inputs.image_tag }}
            type=raw,value=latest,enable=${{ inputs.image_tag != 'latest' }}
          flavor: |
            latest=true

      # 为 Docker Hub 生成元数据
      - name: Extract metadata for Docker Hub
        id: meta-dockerhub
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.DOCKERHUB_REGISTRY }}/${{ env.DOCKERHUB_IMAGE_NAME }}
          tags: |
            type=raw,value=${{ inputs.image_tag }}
            type=raw,value=latest,enable=${{ inputs.image_tag != 'latest' }}
          flavor: |
            latest=true


#### .github/workflows/network-smoke.yml
name: Network Smoke

on:
  schedule:
    - cron: '0 2 * * 1-5'
  workflow_dispatch:

concurrency:
  group: network-smoke-${{ github.ref }}
  cancel-in-progress: true

jobs:
  smoke:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - name: 📥 Checkout
        uses: actions/checkout@v4

      - name: 🐍 Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: 📦 Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest

      - name: 🌐 Run pytest network smoke (non-blocking)
        continue-on-error: true
        run: |
          set -o pipefail
          python -m pytest -m network -q | tee pytest-network.log

      - name: 🚀 Run quick smoke (non-blocking)
        continue-on-error: true
        run: |
          set -o pipefail
          ./test.sh quick --no-notify | tee quick-smoke.log

      - name: 📤 Upload smoke logs
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: network-smoke-logs-${{ github.run_number }}
          path: |
            pytest-network.log
            quick-smoke.log
          if-no-files-found: ignore

#### .github/workflows/pr-review.yml
# PR 自动审查 - 语法检查 + AI 语义审查
# 当有 PR 创建或更新时自动触发

name: PR Review

on:
  pull_request_target:
    types: [opened, synchronize, reopened]
    paths:
      - '**.py'
      - '**.md'
      - '**.ts'
      - '**.tsx'
      - 'docs/**'
      - 'README.md'
      - 'AGENTS.md'
      - 'apps/dsa-web/**'
      - 'requirements.txt'
      - 'pyproject.toml'
      - 'setup.cfg'
      - '.github/PULL_REQUEST_TEMPLATE.md'
      - '.github/workflows/**'
      - '.github/scripts/**'
      - 'docker/Dockerfile'
      - 'docker-compose.yml'
  # 支持手动触发（用于重新审查）
  workflow_dispatch:

# 限制并发，避免同一 PR 多次触发时重复评论
concurrency:
  group: pr-review-${{ github.event.pull_request.number || github.run_id }}
  cancel-in-progress: true

permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  # ==================== 安全检查（检测敏感文件修改）====================
  security-check:
    name: 🔒 安全检查
    runs-on: ubuntu-latest
    outputs:
      safe_to_run: ${{ steps.check_sensitive.outputs.safe_to_run }}
      sensitive_files_changed: ${{ steps.check_sensitive.outputs.sensitive_files_changed }}
    
    steps:
      - name: 📥 检出代码
        uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha || github.sha }}
          fetch-depth: 0
      
      - name: 🔄 获取 base 分支
        run: git fetch origin ${{ github.base_ref || 'main' }}:refs/remotes/origin/${{ github.base_ref || 'main' }}
      
      - name: 🔒 检查敏感文件修改
        id: check_sensitive
        run: |
          BASE_REF="${{ github.base_ref || 'main' }}"
          SENSITIVE_FILES=$(git diff --name-only origin/$BASE_REF...HEAD | grep -E '^(\.github/workflows/.*\.yml|\.github/scripts/.*\.py)$' || echo "")
          
          if [ -n "$SENSITIVE_FILES" ]; then
            echo "⚠️ **检测到敏感文件修改，需要人工审核！**" >> $GITHUB_STEP_SUMMARY
            echo "" >> $GITHUB_STEP_SUMMARY
            echo "修改的敏感文件：" >> $GITHUB_STEP_SUMMARY
            echo '```' >> $GITHUB_STEP_SUMMARY
            echo "$SENSITIVE_FILES" >> $GITHUB_STEP_SUMMARY
            echo '```' >> $GITHUB_STEP_SUMMARY
            echo "" >> $GITHUB_STEP_SUMMARY
            echo "已标记为敏感变更，请重点人工复核；自动流程继续执行。" >> $GITHUB_STEP_SUMMARY
            echo "sensitive_files_changed=true" >> $GITHUB_OUTPUT
            echo "safe_to_run=true" >> $GITHUB_OUTPUT
          else
            echo "✅ 未检测到敏感文件修改" >> $GITHUB_STEP_SUMMARY
            echo "sensitive_files_changed=false" >> $GITHUB_OUTPUT
            echo "safe_to_run=true" >> $GITHUB_OUTPUT
          fi


#### .github/workflows/stale.yml
# 自动关闭过期的 Issues 和 PR
# 每天检查一次，标记长时间无响应的 issues/PRs

name: Stale Issues & PRs

on:
  schedule:
    # 每天 UTC 0:00（北京时间 8:00）检查一次
    - cron: '0 0 * * *'
  # 支持手动触发
  workflow_dispatch:

permissions:
  issues: write
  pull-requests: write

jobs:
  stale:
    name: 🧹 清理过期 Issues/PRs
    runs-on: ubuntu-latest
    
    steps:
      - name: 🏷️ 标记并关闭过期内容
        uses: actions/stale@v9
        with:
          # ===== Issue 配置 =====
          days-before-issue-stale: 7
          days-before-issue-close: 7
          stale-issue-label: 'stale'
          stale-issue-message: |
            👋 这个 Issue 已经 **7 天** 没有活动了。
            
            如果问题仍然存在，请回复说明最新情况，我们会继续跟进。
            如果问题已解决或不再需要，可以直接关闭此 Issue。
            
            **如果 7 天内没有回复，此 Issue 将自动关闭。**
          close-issue-message: |
            🔒 由于长时间没有活动，此 Issue 已自动关闭。
            
            如果问题仍然存在，欢迎重新打开或创建新的 Issue。
          
          # ===== PR 配置 =====
          days-before-pr-stale: 21
          days-before-pr-close: 14
          stale-pr-label: 'stale'
          stale-pr-message: |
            👋 这个 PR 已经 **21 天** 没有活动了。
            
            请检查是否需要：
            - 解决合并冲突
            - 回复 review 意见
            - 更新代码
            
            **如果 14 天内没有更新，此 PR 将自动关闭。**
          close-pr-message: |
            🔒 由于长时间没有活动，此 PR 已自动关闭。
            
            如果您仍希望合入这些更改，请重新打开或创建新的 PR。
          
          # ===== 排除规则 =====
          # 带有这些标签的不会被标记为 stale
          exempt-issue-labels: 'pinned,security,enhancement,help wanted,good first issue'
          exempt-pr-labels: 'pinned,security,work-in-progress,wip'
          
          # 排除草稿 PR
          exempt-draft-pr: true
          
          # ===== 其他配置 =====
          # 每次运行最多处理的数量
          operations-per-run: 50
          
          # 只处理这些状态的
          only-labels: ''
          
          # 移除 stale 标签（当有新活动时）
          remove-stale-when-updated: true
          
          # 调试模式（设为 true 时只打印不实际操作）
          debug-only: false


### 容器与部署配置
(无容器/部署配置)

### .github 目录
#### .github/FUNDING.yml
custom: ["https://github.com/ZhuLinsen/daily_stock_analysis#sponsor"]

#### .github/release.yml
changelog:
  exclude:
    labels:
      - duplicate
      - invalid
      - wontfix
      - stale
      - skip-changelog
    authors:
      - dependabot
      - github-actions[bot]
  categories:
    - title: "🚀 New Features"
      labels:
        - enhancement
    - title: "🤖 AI & Analysis"
      labels:
        - ai
    - title: "🐛 Bug Fixes"
      labels:
        - bug
    - title: "📡 Data Sources"
      labels:
        - data-source
    - title: "🔔 Notifications"
      labels:
        - notification
        - feishu
    - title: "⚙️ Configuration"
      labels:

#### .github/CODEOWNERS
* @ZhuLinsen
#### .github/PULL_REQUEST_TEMPLATE.md
## PR Type

- [ ] fix
- [ ] feat
- [ ] refactor
- [ ] docs
- [ ] chore
- [ ] test

## Background And Problem

请描述当前问题、影响范围与触发场景。

## Scope Of Change

请列出本 PR 修改的模块和文件范围。

## Issue Link

必须填写以下之一：
- `Fixes #<issue_number>`
- `Refs #<issue_number>`
- 无 Issue 时说明原因与验收标准

## Verification Commands And Results

请填写你实际执行过的命令和关键结果（不要只写“已测试”）：

```bash
# example

#### .github/scripts/ai_review.py
#!/usr/bin/env python3
"""
AI code review script used by GitHub Actions PR Review workflow.
"""
import json
import os
import subprocess
import traceback


MAX_DIFF_LENGTH = 18000
REVIEW_PATHS = [
    '*.py',
    '*.md',
    'README.md',
    'AGENTS.md',
    'docs/**',
    '.github/PULL_REQUEST_TEMPLATE.md',
    'requirements.txt',
    'pyproject.toml',
    'setup.cfg',
    '.github/workflows/*.yml',
    '.github/scripts/*.py',
    'apps/dsa-web/**',
]


def run_git(args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:

#### .github/ISSUE_TEMPLATE/feature_request.md
---
name: 功能建议
about: 提出新功能或改进建议
title: '[Feature] '
labels: enhancement
assignees: ''
---

## 功能描述
简明扼要地描述你希望增加的功能。

## 使用场景
描述在什么情况下需要这个功能。

## 期望实现
描述你期望这个功能如何工作。

## 备选方案
描述你考虑过的其他替代方案。

## 相关信息
- 是否愿意贡献代码实现: [是/否]
- 参考链接/文档:
- 其他说明:

#### .github/ISSUE_TEMPLATE/bug_report.md
---
name: Bug 报告
about: 报告一个问题帮助我们改进
title: '[Bug] '
labels: bug
assignees: ''
---

## ⚠️ 提交前必读
请确认已更新到最新版本后再提交 Issue，避免重复报告已修复的问题。

## 版本确认（必填）
- [ ] 我已同步最新代码（Fork 用户请先 Sync fork，然后重新运行 Actions）
- 代码版本：
  - 本地运行：执行 `git rev-parse --short HEAD` 的输出：______
  - GitHub Actions：查看 workflow 运行日志开头的 commit hash：______

## 问题描述
简明扼要地描述遇到的问题。

## 复现步骤
1. 执行命令 '...'
2. 配置 '...'
3. 查看 '...'
4. 出现错误

## 期望行为
描述你期望发生的情况。

## 实际行为

#### .github/ISSUE_TEMPLATE/config.yml
blank_issues_enabled: true
contact_links:
  - name: 💬 讨论区
    url: https://github.com/ZhuLinsen/daily_stock_analysis/discussions
    about: 有问题想讨论？欢迎来讨论区交流
  - name: 📖 使用文档
    url: https://github.com/ZhuLinsen/daily_stock_analysis#-快速开始
    about: 查看 README 获取使用帮助


## Layer 2: Import 依赖中心度

主要语言: py

### 被引用最多的模块（Top 10）
 203 src
 102 typing
  89 logging
  75 unittest
  49 datetime
  46 os
  43 bot
  36 sys
  36 api
  31 

### 项目内部模块被引用次数（Top 10）
   2 tests.litellm_stub

### 依赖中心度最高的文件（Top 5）
tests/litellm_stub.py

## Layer 3: Git 变更热点

总提交数: 1

## Layer 4: 关键代码片段

### api/app.py (203 行)
```python

async def app_lifespan(app: FastAPI):
    """Initialize and release shared services for the app lifecycle."""
    app.state.system_config_service = SystemConfigService()
    try:
        yield
    finally:
        if hasattr(app.state, "system_config_service"):
            delattr(app.state, "system_config_service")

def create_app(static_dir: Optional[Path] = None) -> FastAPI:
    """
    创建并配置 FastAPI 应用实例
    
    Args:
        static_dir: 静态文件目录路径（可选，默认为项目根目录下的 static）
        
    Returns:
        配置完成的 FastAPI 应用实例
    """
    # 默认静态文件目录
    if static_dir is None:
        static_dir = Path(__file__).parent.parent / "static"
    
    # 创建 FastAPI 实例
    app = FastAPI(
        title="Daily Stock Analysis API",
        description=(
            "A股/港股/美股自选股智能分析系统 API\n\n"
            "## 功能模块\n"
            "- 股票分析：触发 AI 智能分析\n"
            "- 历史记录：查询历史分析报告\n"
            "- 股票数据：获取行情数据\n\n"
            "## 认证方式\n"
            "当前版本暂无认证要求"
        ),
        version="1.0.0",
        lifespan=app_lifespan,
    )
    
    # ============================================================
    # CORS 配置
    # ============================================================
    
    allowed_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    # ... (102 lines omitted) ...
            file_path = static_dir / full_path
            if file_path.exists() and file_path.is_file():
                # Issue #520: Explicitly resolve MIME type to avoid
                # browsers rejecting JS modules served as text/plain.
                content_type, _ = mimetypes.guess_type(str(file_path))
                return FileResponse(file_path, media_type=content_type)
            
            return FileResponse(static_dir / "index.html")
    
    return app

```

### bot/commands/base.py (128 行)
```python

class BotCommand(ABC):
    """
    命令处理器抽象基类
    
    所有命令都必须继承此类并实现抽象方法。
    
    使用示例：
        class MyCommand(BotCommand):
            @property
            def name(self) -> str:
                return "mycommand"
            
            @property
            def aliases(self) -> List[str]:
                return ["mc", "我的命令"]
            
            @property
            def description(self) -> str:
                return "这是我的命令"
            
            @property
            def usage(self) -> str:
                return "/mycommand [参数]"
            
            def execute(self, message: BotMessage, args: List[str]) -> BotResponse:
                return BotResponse.text_response("命令执行成功")
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        命令名称（不含前缀）
        
        例如 "analyze"，用户输入 "/analyze" 触发
        """
        pass
    
    @property
    @abstractmethod
    # ... (63 lines omitted) ...
            args: 命令参数列表
            
        Returns:
            如果参数有效返回 None，否则返回错误信息
        """
        return None
    
    def get_help_text(self) -> str:
        """获取帮助文本"""
        return f"**{self.name}** - {self.description}\n用法: `{self.usage}`"

```

### bot/platforms/base.py (153 行)
```python

class BotPlatform(ABC):
    """
    平台适配器抽象基类
    
    负责：
    1. 验证 Webhook 请求签名
    2. 解析平台消息为统一格式
    3. 将响应转换为平台格式
    
    使用示例：
        class MyPlatform(BotPlatform):
            @property
            def platform_name(self) -> str:
                return "myplatform"
            
            def verify_request(self, headers, body) -> bool:
                # 验证签名逻辑
                return True
            
            def parse_message(self, data) -> Optional[BotMessage]:
                # 解析消息逻辑
                return BotMessage(...)
            
            def format_response(self, response, message) -> WebhookResponse:
                # 格式化响应逻辑
                return WebhookResponse.success({"text": response.text})
    """
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """
        平台标识名称
        
        用于路由匹配和日志标识，如 "feishu", "dingtalk"
        """
        pass
    
    @abstractmethod
    def verify_request(self, headers: Dict[str, str], body: bytes) -> bool:
    # ... (88 lines omitted) ...
            return None, challenge_response
        
        # 2. 验证请求签名
        if not self.verify_request(headers, body):
            return None, WebhookResponse.error("Invalid signature", 403)
        
        # 3. 解析消息
        message = self.parse_message(data)
        
        return message, None

```

### data_provider/akshare_fetcher.py (1856 行)
```python

def _is_etf_code(stock_code: str) -> bool:
    """
    判断代码是否为 ETF 基金
    
    ETF 代码规则：
    - 上交所 ETF: 51xxxx, 52xxxx, 56xxxx, 58xxxx
    - 深交所 ETF: 15xxxx, 16xxxx, 18xxxx
    
    Args:
        stock_code: 股票/基金代码
        
    Returns:
        True 表示是 ETF 代码，False 表示是普通股票代码
    """
    etf_prefixes = ('51', '52', '56', '58', '15', '16', '18')
    code = stock_code.strip().split('.')[0]
    return code.startswith(etf_prefixes) and len(code) == 6

def _is_hk_code(stock_code: str) -> bool:
    """
    判断代码是否为港股

    港股代码规则：
    - 5位数字代码，如 '00700' (腾讯控股)
    - 部分港股代码可能带有前缀，如 'hk00700', 'hk1810'

    Args:
        stock_code: 股票代码

    Returns:
        True 表示是港股代码，False 表示不是港股代码
    """
    # 去除可能的 'hk' 前缀并检查是否为纯数字
    code = stock_code.lower()
    if code.startswith('hk'):
        # 带 hk 前缀的一定是港股，去掉前缀后应为纯数字（1-5位）
        numeric_part = code[2:]
        return numeric_part.isdigit() and 1 <= len(numeric_part) <= 5
    # 无前缀时，5位纯数字才视为港股（避免误判 A 股代码）
    return code.isdigit() and len(code) == 5

def is_hk_stock_code(stock_code: str) -> bool:
    """
    Public API: determine if a stock code is a Hong Kong stock.

    Delegates to _is_hk_code for internal compatibility.

    Args:
        stock_code: Stock code (e.g. '00700', 'hk00700')

    Returns:
        True if HK stock, False otherwise
    """
    return _is_hk_code(stock_code)

def _is_us_code(stock_code: str) -> bool:
    """
    判断代码是否为美股股票（不包括美股指数）。

    委托给 us_index_mapping 模块的 is_us_stock_code()。

    Args:
        stock_code: 股票代码

    Returns:
        True 表示是美股代码，False 表示不是美股代码

    Examples:
        >>> _is_us_code('AAPL')
        True
        >>> _is_us_code('TSLA')
        True
        >>> _is_us_code('SPX')
        False
        >>> _is_us_code('600519')
        False
    """
    return is_us_stock_code(stock_code)

def _to_sina_tx_symbol(stock_code: str) -> str:
    """Convert 6-digit A-share code to sh/sz/bj prefixed symbol for Sina/Tencent APIs."""
    base = (stock_code.strip().split(".")[0] if "." in stock_code else stock_code).strip()
    if is_bse_code(base):
        return f"bj{base}"
    # Shanghai: 60xxxx, 5xxxx (ETF), 90xxxx (B-shares)
    if base.startswith(("6", "5", "90")):
        return f"sh{base}"
    return f"sz{base}"

def _classify_realtime_http_error(exc: Exception) -> Tuple[str, str]:
    """
    Classify Sina/Tencent realtime quote failures into stable categories.
    """
    detail = str(exc).strip() or type(exc).__name__
    lowered = detail.lower()

    remote_disconnect_keywords = (
        "remotedisconnected",
        "remote end closed connection without response",
        "connection aborted",
        "connection broken",
        "protocolerror",
        "chunkedencodingerror",
    )
    timeout_keywords = (
        "timeout",
        "timed out",
        "readtimeout",
        "connecttimeout",
    )
    rate_limit_keywords = (
        "banned",
        "blocked",
        "频率",
        "rate limit",
        "too many requests",
        "429",
        "限制",
        "forbidden",
        "403",
    )

    if any(keyword in lowered for keyword in remote_disconnect_keywords):
        return "remote_disconnect", detail
    if isinstance(exc, (TimeoutError, requests.exceptions.Timeout)) or any(
        keyword in lowered for keyword in timeout_keywords
    ):
        return "timeout", detail
    if any(keyword in lowered for keyword in rate_limit_keywords):
        return "rate_limit_or_anti_bot", detail
    if isinstance(exc, requests.exceptions.RequestException):
        return "request_error", detail
    return "unknown_request_error", detail

def _build_realtime_failure_message(
    source_name: str,
    endpoint: str,
    stock_code: str,
    symbol: str,
    category: str,
    detail: str,
    elapsed: float,
    error_type: str,
) -> str:
    return (
        f"{source_name} 实时行情接口失败: endpoint={endpoint}, stock_code={stock_code}, "
        f"symbol={symbol}, category={category}, error_type={error_type}, "
        f"elapsed={elapsed:.2f}s, detail={detail}"
    )

class AkshareFetcher(BaseFetcher):
    """
    Akshare 数据源实现
    
    优先级：1（最高）
    数据来源：东方财富网爬虫
    
    关键策略：
    - 每次请求前随机休眠 2.0-5.0 秒
    - 随机 User-Agent 轮换
    - 失败后指数退避重试（最多3次）
    """
    
    name = "AkshareFetcher"
    priority = int(os.getenv("AKSHARE_PRIORITY", "1"))
    
    def __init__(self, sleep_min: float = 2.0, sleep_max: float = 5.0):
        """
        初始化 AkshareFetcher
        
        Args:
            sleep_min: 最小休眠时间（秒）
            sleep_max: 最大休眠时间（秒）
        """
        self.sleep_min = sleep_min
        self.sleep_max = sleep_max
        self._last_request_time: Optional[float] = None
        # 东财补丁开启才执行打补丁操作
        if get_config().enable_eastmoney_patch:
            eastmoney_patch()
    
    def _set_random_user_agent(self) -> None:
        """
        设置随机 User-Agent
        
        通过修改 requests Session 的 headers 实现
        这是关键的反爬策略之一
        """
        try:
            import akshare as ak
    # ... (1473 lines omitted) ...
                for _, row in top.iterrows()
            ]
            bottom_sectors = [
                {'name': str(row[name_col]), 'change_pct': float(row[change_col])}
                for _, row in bottom.iterrows()
            ]
            return top_sectors, bottom_sectors
        except Exception as e:
            logger.error(f"[Akshare] 新浪接口获取板块排行也失败: {e}")
            return None

```

### data_provider/base.py (2123 行)
```python

def unwrap_exception(exc: Exception) -> Exception:
    """
    Follow chained exceptions and return the deepest non-cyclic cause.
    """
    current = exc
    visited = set()

    while current is not None and id(current) not in visited:
        visited.add(id(current))
        next_exc = current.__cause__ or current.__context__
        if next_exc is None:
            break
        current = next_exc

    return current

def summarize_exception(exc: Exception) -> Tuple[str, str]:
    """
    Build a stable summary for logs while preserving the application-layer message.
    """
    root = unwrap_exception(exc)
    error_type = type(root).__name__
    message = str(exc).strip() or str(root).strip() or error_type
    return error_type, " ".join(message.split())

def normalize_stock_code(stock_code: str) -> str:
    """
    Normalize stock code by stripping exchange prefixes/suffixes.

    Accepted formats and their normalized results:
    - '600519'      -> '600519'   (already clean)
    - 'SH600519'    -> '600519'   (strip SH prefix)
    - 'SZ000001'    -> '000001'   (strip SZ prefix)
    - 'BJ920748'    -> '920748'   (strip BJ prefix, BSE)
    - 'sh600519'    -> '600519'   (case-insensitive)
    - '600519.SH'   -> '600519'   (strip .SH suffix)
    - '000001.SZ'   -> '000001'   (strip .SZ suffix)
    - '920748.BJ'   -> '920748'   (strip .BJ suffix, BSE)
    - 'HK00700'     -> 'HK00700'  (keep HK prefix for HK stocks)
    - 'AAPL'        -> 'AAPL'     (keep US stock ticker as-is)

    This function is applied at the DataProviderManager layer so that
    all individual fetchers receive a clean 6-digit code (for A-shares/ETFs).
    """
    code = stock_code.strip()
    upper = code.upper()

    # Strip SH/SZ prefix (e.g. SH600519 -> 600519)
    if upper.startswith(('SH', 'SZ')) and not upper.startswith('SH.') and not upper.startswith('SZ.'):
        candidate = code[2:]
        # Only strip if the remainder looks like a valid numeric code
        if candidate.isdigit() and len(candidate) in (5, 6):
            return candidate

    # Strip BJ prefix (e.g. BJ920748 -> 920748)
    if upper.startswith('BJ') and not upper.startswith('BJ.'):
        candidate = code[2:]
        if candidate.isdigit() and len(candidate) == 6:
            return candidate

    # Strip .SH/.SZ/.BJ suffix (e.g. 600519.SH -> 600519, 920748.BJ -> 920748)
    if '.' in code:
        base, suffix = code.rsplit('.', 1)
        if suffix.upper() in ('SH', 'SZ', 'SS', 'BJ') and base.isdigit():
            return base

    return code

def _is_us_market(code: str) -> bool:
    """判断是否为美股/美股指数代码（不含中文前后缀）。"""
    from .us_index_mapping import is_us_stock_code, is_us_index_code

    normalized = (code or "").strip().upper()
    return is_us_index_code(normalized) or is_us_stock_code(normalized)

def _is_hk_market(code: str) -> bool:
    """
    判定是否为港股代码。

    支持 `HK00700` 及纯 5 位数字形式（A 股 ETF/股票常见为 6 位）。
    """
    normalized = (code or "").strip().upper()
    if normalized.startswith("HK"):
        return True
    if normalized.isdigit() and len(normalized) == 5:
        return True
    return False

def _is_etf_code(code: str) -> bool:
    """判定 A 股 ETF 基金代码（保守规则）。"""
    normalized = normalize_stock_code(code)
    return (
        normalized.isdigit()
        and len(normalized) == 6
        and normalized.startswith(ETF_PREFIXES)
    )

def _market_tag(code: str) -> str:
    """返回市场标签: cn/us/hk."""
    if _is_us_market(code):
        return "us"
    if _is_hk_market(code):
        return "hk"
    return "cn"

def is_bse_code(code: str) -> bool:
    """
    Check if the code is a Beijing Stock Exchange (BSE) A-share code.

    BSE rules:
    - Old format (pre-2024): 8xxxxx (e.g. 838163), 4xxxxx (e.g. 430047)
    - New format (2024+, post full migration Oct 2025): 920xxx+
    Note: 900xxx are Shanghai B-shares, NOT BSE — must return False.
    """
    c = (code or "").strip().split(".")[0]
    if len(c) != 6 or not c.isdigit():
        return False
    return c.startswith(("8", "4")) or c.startswith("92")

def is_st_stock(name: str) -> bool:
    """
    Check if the stock is an ST or *ST stock based on its name.

    ST stocks have special trading rules and typically a ±5% limit.
    """
    n = (name or "").upper()
    return 'ST' in n

def is_kc_cy_stock(code: str) -> bool:
    """
    Check if the stock is a STAR Market (科创板) or ChiNext (创业板) stock based on its code.

    - STAR Market: Codes starting with 688
    - ChiNext: Codes starting with 300
    Both have a ±20% limit.
    """
    c = (code or "").strip().split(".")[0]
    return c.startswith("688") or c.startswith("30")

def canonical_stock_code(code: str) -> str:
    """
    Return the canonical (uppercase) form of a stock code.

    This is a display/storage layer concern, distinct from normalize_stock_code
    which strips exchange prefixes. Apply at system input boundaries to ensure
    consistent case across BOT, WEB UI, API, and CLI paths (Issue #355).

    Examples:
        'aapl'    -> 'AAPL'
        'AAPL'    -> 'AAPL'
        '600519'  -> '600519'  (digits are unchanged)
        'hk00700' -> 'HK00700'
    """
    return (code or "").strip().upper()

class DataFetchError(Exception):
    """数据获取异常基类"""
    pass

class RateLimitError(DataFetchError):
    """API 速率限制异常"""
    pass

class DataSourceUnavailableError(DataFetchError):
    """数据源不可用异常"""
    pass

class BaseFetcher(ABC):
    """
    数据源抽象基类
    
    职责：
    1. 定义统一的数据获取接口
    2. 提供数据标准化方法
    3. 实现通用的技术指标计算
    
    子类实现：
    - _fetch_raw_data(): 从具体数据源获取原始数据
    - _normalize_data(): 将原始数据转换为标准格式
    """
    
    name: str = "BaseFetcher"
    priority: int = 99  # 优先级数字越小越优先
    
    @abstractmethod
    def _fetch_raw_data(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        从数据源获取原始数据（子类必须实现）
        
        Args:
            stock_code: 股票代码，如 '600519', '000001'
            start_date: 开始日期，格式 'YYYY-MM-DD'
            end_date: 结束日期，格式 'YYYY-MM-DD'
            
        Returns:
            原始数据 DataFrame（列名因数据源而异）
        """
        pass
    
    @abstractmethod
    def _normalize_data(self, df: pd.DataFrame, stock_code: str) -> pd.DataFrame:
        """
        标准化数据列名（子类必须实现）

        将不同数据源的列名统一为：
        ['date', 'open', 'high', 'low', 'close', 'volume', 'amount', 'pct_chg']
        """
    # ... (179 lines omitted) ...
    def random_sleep(min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
        """
        智能随机休眠（Jitter）
        
        防封禁策略：模拟人类行为的随机延迟
        在请求之间加入不规则的等待时间
        """
        sleep_time = random.uniform(min_seconds, max_seconds)
        logger.debug(f"随机休眠 {sleep_time:.2f} 秒...")
        time.sleep(sleep_time)

class DataFetcherManager:
    """
    数据源策略管理器
    
    职责：
    1. 管理多个数据源（按优先级排序）
    2. 自动故障切换（Failover）
    3. 提供统一的数据获取接口
    
    切换策略：
    - 优先使用高优先级数据源
    - 失败后自动切换到下一个
    - 所有数据源都失败时抛出异常
    """
    
    def __init__(self, fetchers: Optional[List[BaseFetcher]] = None):
        """
        初始化管理器
        
        Args:
            fetchers: 数据源列表（可选，默认按优先级自动创建）
        """
        self._fetchers: List[BaseFetcher] = []
        
        if fetchers:
            # 按优先级排序
            self._fetchers = sorted(fetchers, key=lambda f: f.priority)
        else:
            # 默认数据源将在首次使用时延迟加载
            self._init_default_fetchers()
        self._fundamental_adapter = AkshareFundamentalAdapter()
        self._fundamental_cache: Dict[str, Dict[str, Any]] = {}
        self._fundamental_cache_lock = RLock()
        self._fundamental_timeout_worker_limit = 8
        self._fundamental_timeout_slots = BoundedSemaphore(self._fundamental_timeout_worker_limit)

    def _get_fundamental_cache_key(self, stock_code: str, budget_seconds: Optional[float] = None) -> str:
        """生成基本面缓存 key（包含预算分桶以避免低预算结果污染高预算请求）。"""
        normalized_code = normalize_stock_code(stock_code)
        if budget_seconds is None:
    # ... (1623 lines omitted) ...
        return [], [], source_chain, last_error

    def get_sector_rankings(self, n: int = 5) -> Tuple[List[Dict], List[Dict]]:
        """获取板块涨跌榜（自动切换数据源）"""
        # 按需求固定回退顺序：Akshare(EM) -> Akshare(Sina) -> Tushare -> Efinance
        top, bottom, _, last_error = self._get_sector_rankings_with_meta(n)
        if top or bottom:
            return top, bottom
        logger.warning(f"[板块排行] 所有数据源均失败，最终错误: {last_error}")
        return [], []

```

### main.py (720 行)
```python

def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='A股自选股智能分析系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python main.py                    # 正常运行
  python main.py --debug            # 调试模式
  python main.py --dry-run          # 仅获取数据，不进行 AI 分析
  python main.py --stocks 600519,000001  # 指定分析特定股票
  python main.py --no-notify        # 不发送推送通知
  python main.py --single-notify    # 启用单股推送模式（每分析完一只立即推送）
  python main.py --schedule         # 启用定时任务模式
  python main.py --market-review    # 仅运行大盘复盘
        '''
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式，输出详细日志'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='仅获取数据，不进行 AI 分析'
    )

    parser.add_argument(
        '--stocks',
        type=str,
        help='指定要分析的股票代码，逗号分隔（覆盖配置文件）'
    )

    parser.add_argument(
        '--no-notify',
        action='store_true',
        help='不发送推送通知'
    # ... (107 lines omitted) ...
        help='回测评估窗口（交易日数，默认使用配置）'
    )

    parser.add_argument(
        '--backtest-force',
        action='store_true',
        help='强制回测（即使已有回测结果也重新计算）'
    )

    return parser.parse_args()

def _compute_trading_day_filter(
    config: Config,
    args: argparse.Namespace,
    stock_codes: List[str],
) -> Tuple[List[str], Optional[str], bool]:
    """
    Compute filtered stock list and effective market review region (Issue #373).

    Returns:
        (filtered_codes, effective_region, should_skip_all)
        - effective_region None = use config default (check disabled)
        - effective_region '' = all relevant markets closed, skip market review
        - should_skip_all: skip entire run when no stocks and no market review to run
    """
    force_run = getattr(args, 'force_run', False)
    if force_run or not getattr(config, 'trading_day_check_enabled', True):
        return (stock_codes, None, False)

    from src.core.trading_calendar import (
        get_market_for_stock,
        get_open_markets_today,
        compute_effective_region,
    )

    open_markets = get_open_markets_today()
    filtered_codes = []
    for code in stock_codes:
        mkt = get_market_for_stock(code)
        if mkt in open_markets or mkt is None:
            filtered_codes.append(code)

    if config.market_review_enabled and not getattr(args, 'no_market_review', False):
        effective_region = compute_effective_region(
            getattr(config, 'market_review_region', 'cn') or 'cn', open_markets
        )
    else:
        effective_region = None

    should_skip_all = (not filtered_codes) and (effective_region or '') == ''
    return (filtered_codes, effective_region, should_skip_all)

def run_full_analysis(
    config: Config,
    args: argparse.Namespace,
    stock_codes: Optional[List[str]] = None
):
    """
    执行完整的分析流程（个股 + 大盘复盘）

    这是定时任务调用的主函数
    """
    try:
        # Issue #529: Hot-reload STOCK_LIST from .env on each scheduled run
        if stock_codes is None:
            config.refresh_stock_list()

        # Issue #373: Trading day filter (per-stock, per-market)
        effective_codes = stock_codes if stock_codes is not None else config.stock_list
        filtered_codes, effective_region, should_skip = _compute_trading_day_filter(
            config, args, effective_codes
        )
        if should_skip:
            logger.info(
                "今日所有相关市场均为非交易日，跳过执行。可使用 --force-run 强制执行。"
            )
            return
        if set(filtered_codes) != set(effective_codes):
            skipped = set(effective_codes) - set(filtered_codes)
            logger.info("今日休市股票已跳过: %s", skipped)
        stock_codes = filtered_codes

        # 命令行参数 --single-notify 覆盖配置（#55）
        if getattr(args, 'single_notify', False):
            config.single_stock_notify = True

        # Issue #190: 个股与大盘复盘合并推送
        merge_notification = (
            getattr(config, 'merge_email_notification', False)
            and config.market_review_enabled
            and not getattr(args, 'no_market_review', False)
            and not config.single_stock_notify
    # ... (135 lines omitted) ...
                )
                logger.info(
                    f"自动回测完成: processed={stats.get('processed')} saved={stats.get('saved')} "
                    f"completed={stats.get('completed')} insufficient={stats.get('insufficient')} errors={stats.get('errors')}"
                )
        except Exception as e:
            logger.warning(f"自动回测失败（已忽略）: {e}")

    except Exception as e:
        logger.exception(f"分析流程执行失败: {e}")

def start_api_server(host: str, port: int, config: Config) -> None:
    """
    在后台线程启动 FastAPI 服务
    
    Args:
        host: 监听地址
        port: 监听端口
        config: 配置对象
    """
    import threading
    import uvicorn

    def run_server():
        level_name = (config.log_level or "INFO").lower()
        uvicorn.run(
            "api.app:app",
            host=host,
            port=port,
            log_level=level_name,
            log_config=None,
        )

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    logger.info(f"FastAPI 服务已启动: http://{host}:{port}")

def _is_truthy_env(var_name: str, default: str = "true") -> bool:
    """Parse common truthy / falsy environment values."""
    value = os.getenv(var_name, default).strip().lower()
    return value not in {"0", "false", "no", "off"}

def start_bot_stream_clients(config: Config) -> None:
    """Start bot stream clients when enabled in config."""
    # 启动钉钉 Stream 客户端
    if config.dingtalk_stream_enabled:
        try:
            from bot.platforms import start_dingtalk_stream_background, DINGTALK_STREAM_AVAILABLE
            if DINGTALK_STREAM_AVAILABLE:
                if start_dingtalk_stream_background():
                    logger.info("[Main] Dingtalk Stream client started in background.")
                else:
                    logger.warning("[Main] Dingtalk Stream client failed to start.")
            else:
                logger.warning("[Main] Dingtalk Stream enabled but SDK is missing.")
                logger.warning("[Main] Run: pip install dingtalk-stream")
        except Exception as exc:
            logger.error(f"[Main] Failed to start Dingtalk Stream client: {exc}")

    # 启动飞书 Stream 客户端
    if getattr(config, 'feishu_stream_enabled', False):
        try:
            from bot.platforms import start_feishu_stream_background, FEISHU_SDK_AVAILABLE
            if FEISHU_SDK_AVAILABLE:
                if start_feishu_stream_background():
                    logger.info("[Main] Feishu Stream client started in background.")
                else:
                    logger.warning("[Main] Feishu Stream client failed to start.")
            else:
                logger.warning("[Main] Feishu Stream enabled but SDK is missing.")
                logger.warning("[Main] Run: pip install lark-oapi")
        except Exception as exc:
            logger.error(f"[Main] Failed to start Feishu Stream client: {exc}")

def main() -> int:
    """
    主入口函数

    Returns:
        退出码（0 表示成功）
    """
    # 解析命令行参数
    args = parse_arguments()

    # 加载配置（在设置日志前加载，以获取日志目录）
    config = get_config()

    # 配置日志（输出到控制台和文件）
    setup_logging(log_prefix="stock_analysis", debug=args.debug, log_dir=config.log_dir)

    logger.info("=" * 60)
    logger.info("A股自选股智能分析系统 启动")
    logger.info(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # 验证配置
    warnings = config.validate()
    for warning in warnings:
        logger.warning(warning)

    # 解析股票列表（统一为大写 Issue #355）
    stock_codes = None
    if args.stocks:
        stock_codes = [canonical_stock_code(c) for c in args.stocks.split(',') if (c or "").strip()]
        logger.info(f"使用命令行指定的股票列表: {stock_codes}")

    # === 处理 --webui / --webui-only 参数，映射到 --serve / --serve-only ===
    if args.webui:
        args.serve = True
    if args.webui_only:
        args.serve_only = True

    # 兼容旧版 WEBUI_ENABLED 环境变量
    if config.webui_enabled and not (args.serve or args.serve_only):
    # ... (157 lines omitted) ...

        return 0

    except KeyboardInterrupt:
        logger.info("\n用户中断，程序退出")
        return 130

    except Exception as e:
        logger.exception(f"程序执行失败: {e}")
        return 1

```

### server.py (54 行)
```python
# -*- coding: utf-8 -*-
"""
===================================
Daily Stock Analysis - FastAPI 后端服务入口
===================================

职责：
1. 提供 RESTful API 服务
2. 配置 CORS 跨域支持
3. 健康检查接口
4. 托管前端静态文件（生产模式）

启动方式：
    uvicorn server:app --reload --host 0.0.0.0 --port 8000
    
    或使用 main.py:
    python main.py --serve-only      # 仅启动 API 服务
    python main.py --serve           # API 服务 + 执行分析
"""

import logging

from src.config import setup_env, get_config
from src.logging_config import setup_logging

# 初始化环境变量与日志
setup_env()

config = get_config()
level_name = (config.log_level or "INFO").upper()
level = getattr(logging, level_name, logging.INFO)

setup_logging(
    log_prefix="api_server",
    console_level=level,
    extra_quiet_loggers=['uvicorn', 'fastapi'],
)

# 从 api.app 导入应用实例
from api.app import app  # noqa: E402

# 导出 app 供 uvicorn 使用
__all__ = ['app']


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
```

### src/core/backtest_engine.py (554 行)
```python

class DailyBarLike(Protocol):
    """Protocol for objects representing a daily OHLC bar."""

    date: date
    high: Optional[float]
    low: Optional[float]
    close: Optional[float]

class BacktestResultLike(Protocol):
    """Protocol for objects that behave like a stored BacktestResult."""

    eval_status: str
    position_recommendation: Optional[str]
    outcome: Optional[str]
    direction_correct: Optional[bool]
    stock_return_pct: Optional[float]
    simulated_return_pct: Optional[float]
    hit_stop_loss: Optional[bool]
    hit_take_profit: Optional[bool]
    first_hit: Optional[str]
    first_hit_trading_days: Optional[int]
    operation_advice: Optional[str]

class EvaluationConfig:
    eval_window_days: int
    neutral_band_pct: float = 2.0
    engine_version: str = "v1"

class BacktestEngine:
    """Long-only daily-bar backtesting engine."""

    # Operation advice keywords (Chinese + English)
    _BULLISH_KEYWORDS = (
        "买入",
        "加仓",
        "强烈买入",
        "增持",
        "建仓",
        "strong buy",
        "buy",
        "add",
    )
    _BEARISH_KEYWORDS = (
        "卖出",
        "减仓",
        "强烈卖出",
        "清仓",
        "strong sell",
        "sell",
        "reduce",
    )
    _HOLD_KEYWORDS = (
        "持有",
        "hold",
    )
    _WAIT_KEYWORDS = (
        "观望",
        "等待",
        "wait",
    )

    # Negation prefixes (trailing spaces stripped for suffix-matching against prefix text).
    # English patterns include trailing space in their canonical form; rstrip is
    # applied during matching so "do not" matches prefix "do not " or "do not".
    _NEGATION_PATTERNS = (
        "not", "don't", "do not", "no", "never", "avoid",  # English
        "不要", "不", "别", "勿", "没有",  # Chinese
    )
    # ... (455 lines omitted) ...
        first_hit_counts: Dict[str, int] = {}
        for row in results:
            status = (row.eval_status or "").strip() or "(unknown)"
            status_counts[status] = status_counts.get(status, 0) + 1
            first_hit = (row.first_hit or "").strip() or "(none)"
            first_hit_counts[first_hit] = first_hit_counts.get(first_hit, 0) + 1
        return {
            "eval_status": status_counts,
            "first_hit": first_hit_counts,
        }

```

## 配置文件内容
### .github/FUNDING.yml
custom: ["https://github.com/ZhuLinsen/daily_stock_analysis#sponsor"]

### .github/release.yml
changelog:
  exclude:
    labels:
      - duplicate
      - invalid
      - wontfix
      - stale
      - skip-changelog
    authors:
      - dependabot
      - github-actions[bot]
  categories:
    - title: "🚀 New Features"
      labels:
        - enhancement
    - title: "🤖 AI & Analysis"
      labels:
        - ai
    - title: "🐛 Bug Fixes"
      labels:
        - bug
    - title: "📡 Data Sources"
      labels:
        - data-source
    - title: "🔔 Notifications"
      labels:
        - notification
        - feishu
    - title: "⚙️ Configuration"
      labels:
        - configuration
    - title: "🧪 Testing"
      labels:
        - testing
    - title: "🔧 CI/CD & Maintenance"
      labels:
        - ci/cd
    - title: "📝 Documentation"
      labels:
        - documentation
    - title: "🔀 Other Changes"
      labels:
        - "*"

### docker/docker-compose.yml
# ===================================
# A股自选股智能分析系统 - Docker Compose
# ===================================
# 
# 使用方式:
#   定时模式: docker-compose -f ./docker/docker-compose.yml up -d
#   FastAPI模式: docker-compose -f ./docker/docker-compose.yml up -d server
#   同时启动: docker-compose -f ./docker/docker-compose.yml up -d analyzer server

name: daily-stock-analysis
version: '3.8'

x-common: &common
  build:
    context: ..
    dockerfile: docker/Dockerfile
  restart: unless-stopped

  # 环境变量（从 .env 文件加载）
  env_file:
    - ../.env

  volumes:
    - ../data:/app/data
    - ../logs:/app/logs
    - ../reports:/app/reports
    - ../.env:/app/.env
    - ../strategies:/app/strategies:ro
    # 如需覆盖前端静态资源，可挂载本地 static 目录
    # - ../static:/app/static:ro

  environment:
    - TZ=Asia/Shanghai

    # Web/API service bind address (must be 0.0.0.0 inside container)
    - WEBUI_HOST=0.0.0.0
    # API_PORT 从 .env 文件读取，无需在此硬编码

    # 代理设置（如果需要）
    # - http_proxy=http://host.docker.internal:10809
    # - https_proxy=http://host.docker.internal:10809
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
  # 资源限制
  deploy:
    resources:
      limits:

### litellm_config.example.yaml
# ===================================
# LiteLLM Router 配置模板
# ===================================
# 配套文档：docs/LLM_CONFIG_GUIDE.md 第 3.2 节
#
# 用法：
# 1. 复制此文件为 litellm_config.yaml
# 2. 在 .env 中设置 LITELLM_CONFIG=./litellm_config.yaml
# 3. 按需配置下面的 model_list
#
# 密钥引用格式：
#   api_key: "os.environ/ENV_VAR_NAME"  → 从环境变量读取，避免明文写入文件
#   api_key: "sk-xxxxxxxx"              → 直接写入（不推荐）
#
# 更多文档: https://docs.litellm.ai/docs/proxy/configs
# ===================================

model_list:
  # --- siliconflow (OpenAI 兼容，一个 Key 使用多种模型) ---
  # 这是一个关于如何配置在LiteLLM自定义OpenAI兼容API接口的示例
  - model_name: openai/Qwen/Qwen3.5-397B-A17B
    litellm_params:
      model: openai/Qwen/Qwen3.5-397B-A17B
      api_key: "os.environ/LITELLM_API_KEY" # 从环境变量读取 Key，安全防泄漏
      api_base: https://api.siliconflow.cn/v1
      # 以下配置是表示如何启用Qwen模型的enable_thinking开关
      extra_body:
        chat_template_kwargs:
          enable_thinking: true

  # --- AIHubmix (OpenAI 兼容，一个 Key 使用多种模型) ---
  - model_name: openai/gpt-4o-mini
    litellm_params:
      model: openai/gpt-4o-mini
      api_key: "os.environ/AIHUBMIX_KEY"
      api_base: https://aihubmix.com/v1

  - model_name: openai/claude-3-5-sonnet-20241022
    litellm_params:
      model: openai/claude-3-5-sonnet-20241022
      api_key: "os.environ/AIHUBMIX_KEY"
      api_base: https://aihubmix.com/v1

  # --- DeepSeek 官方 API (原生 provider，自动解析 base_url) ---
  - model_name: deepseek/deepseek-chat
    litellm_params:
      model: deepseek/deepseek-chat
      api_key: "os.environ/DEEPSEEK_API_KEY"

  - model_name: deepseek/deepseek-reasoner

### pyproject.toml
[tool.black]
line-length = 120
target-version = ['py310', 'py311', 'py312']
include = '\.pyi?$'
exclude = '''
/(
    \.git
    | \.hg
    | \.mypy_cache
    | \.tox
    | \.venv
    | venv
    | _build
    | buck-out
    | build
    | dist
    | __pycache__
)/
'''

[tool.isort]
profile = "black"
line_length = 120
skip = [".git", "__pycache__", ".env", "venv", ".venv"]

[tool.bandit]
exclude_dirs = ["tests", "test_*.py"]
skips = ["B101"]  # assert 语句在测试中是允许的

### setup.cfg
[flake8]
max-line-length = 120
exclude = 
    .git,
    __pycache__,
    .env,
    venv,
    .venv,
    build,
    dist,
    *.egg-info
# E501: 行太长（有些地方确实需要长行）
# W503: 运算符在换行前（与 black 冲突）
# E203: 切片前的空格（与 black 冲突）
# E402: 模块级导入不在文件顶部（有时需要先设置环境变量）
ignore = E501,W503,E203,E402

[tool:pytest]
testpaths = .
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short
markers =
    unit: fast offline unit tests
    integration: service-level integration tests without external network dependency
    network: tests requiring external network or third-party services

[isort]
profile = black
line_length = 120
skip = .git,__pycache__,.env,venv,.venv
known_first_party = config,storage,analyzer,notification,scheduler,search_service,market_analyzer,stock_analyzer,data_provider

### strategies/bottom_volume.yaml
# Bottom Volume Surge Strategy / 底部放量
# After extended decline, price stabilizes and volume spikes. Potential reversal.

name: bottom_volume
display_name: 底部放量
description: 检测长期下跌后底部放量信号，潜在趋势反转信号。
category: reversal
core_rules: [2, 5]
required_tools:
  - get_daily_history
  - analyze_trend

instructions: |
  **底部放量（Bottom Volume Surge Strategy）**

  反转判定标准：

  1. **持续下跌确认**：
     - 使用 `get_daily_history`（30日）。
     - 股价从 20 日高点到近期低点跌幅 > 15%。
     - `analyze_trend` → trend_status 应为 BEAR 或 STRONG_BEAR。

  2. **量能异动**：
     - 当日成交量 > 5 日均量的 3 倍。
     - 使用 `get_realtime_quote` → volume_ratio > 3.0。
     - 该异动应出现在前期极度缩量之后。

  3. **价格企稳**：
     - 当日K线收阳（收盘价 > 开盘价）。
     - 价格守住近期低点。
     - 最好出现长下影线，显示买方支撑。

  4. **确认因素**（关联理念5：风险排查）：
     - 通过 `search_stock_news` 确认是否有基本面催化。
     - 筹码分布：平均成本接近现价（成本收敛）。

  5. **风险提示**（关联理念2：趋势交易）：
     - 这是反转信号，风险高于趋势跟踪。
     - 仓位建议较小（最多 2-3 成）。
     - 止损必须严格（设在近期低点下方）。

  评分调整：
  - 底部放量确认：sentiment_score +8
  - 配合阳线 + 新闻催化：额外 +5
  - 在 `buy_reason` 和 `pattern_analysis` 中注明"底部放量"。
  - 止损设在近期低点。

### strategies/box_oscillation.yaml
# Box Range Trading Strategy / 箱体震荡战法
# Buy at box support, sell at box resistance, profit from range-bound oscillation.

name: box_oscillation
display_name: 箱体震荡
description: 识别价格箱体区间，在箱底买入、箱顶减仓，适用于横盘震荡行情。
category: framework
core_rules: [1, 2, 3]
required_tools:
  - get_daily_history
  - analyze_trend
  - get_realtime_quote

instructions: |
  **箱体震荡战法（Box Range Trading Strategy）**

  核心逻辑：箱体内部价格在阻力位与支撑位之间反复震荡，
  "贴着支撑买、接近阻力卖"，通过波段操作获取区间收益。

  ## 分析步骤

  ### 1. 箱体识别
  使用 `get_daily_history` 获取近 60~120 日数据：

  - **箱体顶部（阻力位）**：近期多次触碰但未有效突破的高点连线。
    通常为 20~60 日内3次以上的高点聚集区域。
  - **箱体底部（支撑位）**：近期多次下探但未有效跌破的低点连线。
  - 箱体有效性：顶部和底部各至少触碰 2~3 次方可确认。
  - 使用 `analyze_trend` 的 support_levels / resistance_levels 辅助定位。

  ### 2. 当前位置判断
  使用 `get_realtime_quote` 获取现价，与箱体边界对比：

  - **箱底区域**（距支撑 ≤5%）：买入/加仓信号，止损设箱底下方 3%。
  - **箱中区域**（箱体中间 1/3）：观望，不主动操作。
  - **箱顶区域**（距阻力 ≤5%）：减仓/止盈信号，无需追高。

  ### 3. 量能辅助判断
  - **箱底放量企稳**：支撑有效的强信号，可较重仓。
  - **箱顶缩量滞涨**：阻力有效的卖出信号。
  - **箱体突破（放量超过均量2倍以上）**：
    - 向上有效突破 → 转为多头趋势策略，新目标 = 箱体高度延伸。
    - 向下有效跌破 → 离场等待，原支撑转阻力。

  ### 4. 箱体宽度与预期收益
  - 计算箱体宽度：(顶部 - 底部) / 底部 × 100%。
  - 宽度 < 5%：操作空间过小，不建议参与。
  - 宽度 5%~15%：标准箱体，波段操作可行。
  - 宽度 > 15%：大箱体，可做更大波段。


### strategies/bull_trend.yaml
# Default Bull Trend Strategy / 默认多头趋势

name: bull_trend
display_name: 默认多头趋势
description: 默认个股分析优先策略，识别多头排列、趋势延续与回踩低吸机会。
category: trend
core_rules: [1, 2, 3]
required_tools:
  - get_daily_history
  - analyze_trend

instructions: |
  **默认多头趋势（Default Bull Trend Strategy）**

  适用场景：
  - 常规个股分析的默认策略。
  - 优先寻找“趋势向上 + 风险可控 + 不追高”的机会。

  分析框架：

  1. **趋势确认（优先级最高）**
     - 使用 `analyze_trend` 判断 MA5/MA10/MA20 排列。
     - MA5 >= MA10 >= MA20 且 MA20 斜率向上，视为多头结构。
     - 若价格显著跌破 MA20，则降低看多权重。

  2. **位置与节奏**
     - 优先“回踩不破”而非“高位追涨”。
     - 当价格距离 MA5/MA10 过远时，提示等待回踩。
     - 放量突破有效阻力时可提高胜率评级。

  3. **量价验证**
     - 使用 `get_daily_history` 检查突破日/反弹日是否放量。
     - 缩量上涨需谨慎，放量滞涨需警惕分歧。

  4. **交易建议输出**
     - 输出明确的“买入/观望/减仓”倾向及触发条件。
     - 必须给出止损参考（如 MA20 下方或结构低点）。
     - 若无清晰优势，明确写“暂不出手”，避免过度交易。

  评分调整建议：
  - 多头排列 + 趋势强度良好：`sentiment_score +12`
  - 回踩关键均线后企稳：`sentiment_score +8`
  - 放量突破关键阻力：`sentiment_score +10`
  - 跌破 MA20 或趋势转弱：`sentiment_score -12`
### strategies/chan_theory.yaml
# Chan Theory Strategy / 缠论
# Based on Zen channel theory: pen, stroke, segment, hub structure analysis.

name: chan_theory
display_name: 缠论
description: 基于缠论笔、线段、中枢结构，判断趋势级别、买卖点与背驰信号。
category: framework
core_rules: [1, 2, 3, 4]
required_tools:
  - get_daily_history
  - analyze_trend
  - get_realtime_quote

instructions: |
  **缠论（Chan Theory / Zen Channel Theory）**

  核心框架：分型 → 笔 → 线段 → 中枢 → 趋势

  ## 分析步骤

  ### 1. 判断价格结构（中枢识别）
  - 使用 `get_daily_history` 获取近 60 日日线数据。
  - 识别近期价格的高低点序列，判断当前是否在
    **震荡中枢**（1个以上中枢）还是**趋势段**（脱离中枢向上/向下）。
  - 中枢：连续3段走势重叠区间，价格在此区间反复震荡。
  - 趋势：连续3个同级别中枢均向同一方向移动。

  ### 2. 背驰判断（最高优先级信号）
  - **顶背驰**：价格创新高但MACD红柱面积缩小 → 卖出/减仓信号。
  - **底背驰**：价格创新低但MACD绿柱面积缩小 → 买入/加仓信号。
  - 使用 `analyze_trend` 获取 MACD 数据，与价格高低点对比。

  ### 3. 买卖点判定
  - **一买**（最强）：下跌趋势中，最后一个中枢出现底背驰。
  - **二买**：离开下跌中枢后的第一次回调不破中枢高点。
  - **三买**：中枢震荡后向上突破（不回中枢内）。
  - **一卖/二卖/三卖**：对称结构，方向相反。
  - 当前价格所处的买卖点级别决定仓位大小。

  ### 4. 级别与仓位
  - 日线级别买卖点可用较重仓位 (30-50%)。
  - 周线级别买卖点可用较大仓位 (50-80%)。
  - 多级别共振（日线+周线同方向）时信号最强。

  ### 5. 输出要求
  - 明确说明当前处于：上涨趋势/下跌趋势/中枢震荡。
  - 指出是否存在背驰信号及背驰级别。
  - 给出当前买卖点类型（一买/二买/三买 等），若无则写"暂无明确买卖点"。
  - 止损设于前低（买入时）或前高（卖出时）。


### strategies/dragon_head.yaml
# Dragon Head Strategy / 龙头策略
# Identifies sector leaders during sector rotation cycles.

name: dragon_head
display_name: 龙头策略
description: 板块轮动中识别龙头股。适用于板块启动或行业催化剂出现时。
category: trend
core_rules: [2, 7]
required_tools:
  - get_realtime_quote
  - get_sector_rankings
  - search_stock_news

instructions: |
  **龙头策略（Dragon Head Strategy）**

  评估标准：

  1. **板块领涨地位**：
     - 使用 `get_sector_rankings` 检查该股所在板块是否为近期涨幅前列。
     - 确认该股是否在板块启动周期中率先上涨或涨停。

  2. **换手率与动能**（关联理念7：强势趋势股放宽）：
     - 使用 `get_realtime_quote` 检查换手率。龙头股换手率通常 > 5%。
     - 量比 > 1.5 说明有活跃的交易兴趣。

  3. **相对强度**：
     - 对比个股涨跌幅与板块平均值。
     - 真正的龙头在上涨日应跑赢板块 2% 以上。

  4. **新闻催化**：
     - 使用 `search_stock_news` 搜索板块级催化剂（政策、事件、业绩）。
     - 龙头行情常伴随板块整体催化。

  5. **乖离率检查**（关联理念1：严进策略）：
     - 龙头股可适当放宽乖离率至 7%，但超过 10% 仍需谨慎。

  评分调整：
  - 确认为龙头股：sentiment_score +10
  - 板块正处于主动轮动期：额外 +5
  - 在 `buy_reason` 中注明"龙头策略"判断结果。

### strategies/emotion_cycle.yaml
# Sentiment Cycle Strategy / 情绪周期
# Uses market sentiment, turnover rate and volume pattern to time entries against crowd behavior.

name: emotion_cycle
display_name: 情绪周期
description: 基于市场情绪、换手率与量价结构，识别情绪低点（恐慌底）与情绪高点（狂热顶），逆情绪布局。
category: framework
core_rules: [1, 2, 3, 5]
required_tools:
  - get_daily_history
  - get_realtime_quote
  - analyze_trend
  - search_stock_news

instructions: |
  **情绪周期策略（Sentiment Cycle Strategy）**

  核心哲学：市场参与者的情绪在"恐慌→悲观→怀疑→希望→乐观→兴奋→贪婪→狂热"
  之间循环。聪明钱在恐慌底部布局，在狂热顶部离场。

  ## 情绪阶段量化指标

  ### 第一步：换手率分析（情绪热度核心指标）
  使用 `get_daily_history` 和 `get_realtime_quote`：

  - **换手率 < 0.5%/日**：市场冷淡，无人关注，潜在底部区域（贪婪时买入别人的恐慌）。
  - **换手率 0.5%~2%**：正常交投，情绪平稳。
  - **换手率 2%~5%**：活跃，市场开始关注，不宜追高。
  - **换手率 > 5%**：高热度，游资/散户涌入，警惕情绪顶。
  - **换手率 > 10%（日均）**：极度过热，通常为短期顶部。

  ### 第二步：连续换手率走势
  使用 `get_daily_history` 计算近 20 日换手率走势：
  - 由高向低（持续降温）+ 成交量萎缩 → 情绪退潮，耐心等待。
  - 由低向高（加速升温）+ 成交量陡增 → 情绪启动，可介入。
  - 突然单日暴量（换手率超过前期5倍）→ 往往是主力出货，需警惕。

  ### 第三步：新闻情绪面分析
  使用 `search_stock_news` 搜索近期新闻，分析情绪倾向：
  - 新闻集中出现"利好兑现、业绩超预期、涨停板、机构推荐"等 → 情绪可能过热。
  - 新闻集中出现"业绩下滑、利空、跌破支撑" → 悲观情绪可能造就底部。
  - 散户论坛/社交媒体情绪极端负面 → 反向指标，可能接近底部。

  ### 第四步：均线收缩与波动率
  使用 `analyze_trend`：
  - MA5/MA10/MA20 三线粘合（均线收缩）→ 蓄势，方向待定，情绪冷淡。
  - 波动率降至低位（ATR 萎缩）→ 情绪极度低迷，蓄势爆发前兆。

  ## 情绪底部特征（买入区）
  满足以下3项以上：

### strategies/ma_golden_cross.yaml
# MA Golden Cross Strategy / 均线金叉
# MA5 crosses above MA10 (or MA10 above MA20) with volume confirmation.

name: ma_golden_cross
display_name: 均线金叉
description: 检测均线金叉配合量能确认信号，经典的趋势反转/延续信号。
category: trend
core_rules: [1, 2, 3]
required_tools:
  - get_daily_history
  - analyze_trend

instructions: |
  **均线金叉（MA Golden Cross Strategy）**

  信号判定标准：

  1. **金叉检测**（关联理念2：趋势交易）：
     - 使用 `analyze_trend` 检查均线排列和 MACD 状态。
     - 主信号：MA5 在最近 3 个交易日内上穿 MA10。
     - 强信号：MA10 上穿 MA20（更慢但更可靠）。
     - 检查 MACD 状态是否为金叉或零轴上方金叉。

  2. **量能确认**（关联理念3：效率优先）：
     - 金叉日成交量应高于 5 日均量。
     - 使用 `get_daily_history` 验证。
     - 金叉日量比 > 1.2 为积极信号。

  3. **趋势背景**：
     - 盘整后金叉：最强信号。
     - 上升趋势中金叉：延续信号。
     - 深度下跌中金叉：弱信号，需更多确认。

  4. **价格位置**（关联理念1：严进策略）：
     - 价格应在交叉均线附近或上方。
     - 乖离率 < 5% — 避免追高延迟入场。

  评分调整：
  - MA5 × MA10 金叉配合量能：sentiment_score +10
  - MA10 × MA20 金叉：sentiment_score +8
  - MACD 零轴上方金叉：额外 +5
  - 在 `ma_analysis` 和 `buy_reason` 中注明"均线金叉"。
  - 理想买点设在交叉均线水平附近。

### strategies/one_yang_three_yin.yaml
# One Yang Three Yin Strategy / 一阳夹三阴
# K-line pattern: bullish → 3 small bearish → bullish. Consolidation end signal.

name: one_yang_three_yin
display_name: 一阳夹三阴
description: 检测一阳夹三阴K线整理形态，趋势延续入场信号。
category: pattern
core_rules: [2, 4]
required_tools:
  - get_daily_history
  - analyze_trend

instructions: |
  **一阳夹三阴（One Yang Three Yin Strategy）**

  形态定义（最近 5 个交易日）：

  1. **第1日**：大阳线（收盘价 > 开盘价，实体 > 股价的 2%）。
  2. **第2-4日**：连续三根阴线或小K线：
     - 每根K线最低价不跌破第1日开盘价。
     - 成交量应逐步萎缩（量比 < 0.8）。
     - 三根K线应收在第1日实体范围内。
  3. **第5日**：又一根阳线，收盘价突破第1日收盘价。

  如何使用工具评估：

  1. 使用 `get_daily_history` 获取最近 10 日数据。
  2. 检查最后 5 根K线是否符合上述形态。
  3. 使用 `analyze_trend` 确认多头排列（关联理念2：趋势交易，MA5 > MA10 > MA20）。

  评分调整：
  - 形态成立 + 趋势看多：sentiment_score +15
  - 形态成立但趋势不明：sentiment_score +5
  - 在 `pattern_analysis` 和 `buy_reason` 中注明"一阳夹三阴"。
  - 理想买点设在第5日收盘价附近，止损设在第1日开盘价下方。

### strategies/shrink_pullback.yaml
# Shrink Volume Pullback Strategy / 缩量回踩
# Volume shrinks during pullback to MA5/MA10, then price bounces.

name: shrink_pullback
display_name: 缩量回踩
description: 检测缩量回踩均线支撑信号，趋势延续的理想入场点。
category: trend
core_rules: [1, 2, 4]
required_tools:
  - get_daily_history
  - analyze_trend
  - get_realtime_quote

instructions: |
  **缩量回踩（Shrink Volume Pullback Strategy）**

  入场判定标准：

  1. **前提条件**（关联理念2：趋势交易）：
     - 股票必须处于上升趋势（MA5 > MA10 > MA20）。
     - 使用 `analyze_trend` 确认多头排列。

  2. **回踩检测**（关联理念4：买点偏好）：
     - 使用 `get_daily_history` 和 `get_realtime_quote`。
     - 价格回踩至 MA5 附近（误差 1% 以内）或 MA10 附近（误差 2% 以内）。
     - 回调期间成交量 < 5 日均量的 70%（缩量特征）。
     - `analyze_trend` → volume_status 应显示缩量。

  3. **反弹信号**（关联理念1：严进策略）：
     - 当前价格守住均线支撑位。
     - MA5 乖离率 < 2% — 最佳买入区间。

  4. **确认条件**（关联理念5：风险排查）：
     - `search_stock_news` 无利空消息。
     - 筹码分布健康（获利比例 50-80%）。

  评分调整：
  - 缩量回踩 MA5：sentiment_score +10
  - 缩量回踩 MA10 且量能 < 0.6 倍均量：sentiment_score +8
  - 理想买点设在 MA5 水平，次优买点设在 MA10。
  - 止损设在 MA20 水平。
  - 在 `buy_reason` 中注明"缩量回踩"。

### strategies/volume_breakout.yaml
# Volume Breakout Strategy / 放量突破
# Price breaks above resistance on heavy volume (>2x average).

name: volume_breakout
display_name: 放量突破
description: 检测放量突破阻力位信号。适用于股价接近已知阻力位时。
category: trend
core_rules: [1, 2, 3]
required_tools:
  - get_daily_history
  - analyze_trend
  - get_realtime_quote

instructions: |
  **放量突破（Volume Breakout Strategy）**

  突破判定标准：

  1. **阻力位识别**：
     - 使用 `analyze_trend` → resistance_levels 获取阻力位。
     - 通常为 20 日高点或前期震荡平台顶部。

  2. **量能确认**（关联理念3：效率优先）：
     - 当日成交量 > 5 日均量的 2 倍。
     - 使用 `get_realtime_quote` → volume_ratio > 2.0 确认。
     - 使用 `get_daily_history` 计算均量进行交叉验证。

  3. **价格确认**（关联理念1：严进策略）：
     - 收盘价必须站上阻力位。
     - 收盘应在当日振幅上方 30%（强势收盘）。
     - 突破后乖离率检查：仍需 < 5%，避免追高。

  4. **后续验证**（如有数据）：
     - 次日开盘应在突破位之上，区分真突破与假突破。

  5. **风险过滤**（关联理念5：风险排查）：
     - 通过 `search_stock_news` 检查无重大利空。
     - PE 不应过高（避免泡沫型突破）。

  评分调整：
  - 放量突破确认：sentiment_score +12
  - 突破伴随板块共振（板块也走强）：额外 +5
  - 理想买点设在突破位附近，止损设在突破位下方 3%。
  - 在 `buy_reason` 和 `volume_analysis` 中注明"放量突破"。

### strategies/wave_theory.yaml
# Elliott Wave Theory Strategy / 波浪理论
# 5-wave impulse + 3-wave corrective pattern analysis for trend and position sizing.

name: wave_theory
display_name: 波浪理论
description: 基于艾略特波浪理论的推动浪与调整浪结构，判断当前所处浪型与潜在目标价。
category: framework
core_rules: [1, 2, 3, 4]
required_tools:
  - get_daily_history
  - analyze_trend
  - get_realtime_quote

instructions: |
  **波浪理论（Elliott Wave Theory）**

  核心原则：市场按照 5 浪推进 + 3 浪调整的循环结构运行。

  ## 分析步骤

  ### 1. 识别当前浪型
  使用 `get_daily_history` 获取近 120 日数据，结合 `analyze_trend` 趋势数据：

  **推动浪（1-3-5）识别特征**：
  - 第1浪：趋势反转的第一波，成交量温和放大。
  - 第3浪：最强劲的推动浪，通常放大量，MACD 强势；绝不是最短浪。
  - 第5浪：量能往往弱于第3浪，出现顶背离则走高后即将结束。

  **调整浪（A-B-C）识别特征**：
  - A 浪：第一次下跌，成交量较大，多数人以为是回调。
  - B 浪：反弹，力度弱于前期涨幅，成交量萎缩，陷阱风险高。
  - C 浪：第二次下跌，力度往往超过 A 浪，完成调整。

  ### 2. 黄金位置判断
  - 第2浪回调通常在第1浪的 38.2%~61.8%。
  - 第3浪目标通常是第1浪的 1.618~2.618 倍延伸。
  - 第4浪不得进入第1浪价格区域（违反波浪规则）。
  - C浪目标：A 浪顶端起算，等于或超过 A 浪长度。

  ### 3. 最优买点
  - **第2浪回调企稳**（黄金坑）：最安全买点，止损第1浪起点。
  - **第4浪回调企稳**：次优，止损第1浪顶部。
  - **第3浪初期突破**：放量突破第1浪高点时。
  - 避免在第5浪末端追高（顶背离风险）。

  ### 4. 风险提示
  - B浪反弹不宜重仓（陷阱性质）。
  - 波浪计数存在主观性，需结合其他技术指标验证。
  - 若波浪规则被违反（如第4浪侵入第1浪），需重新归数。




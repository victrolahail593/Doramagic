# 社区知识报告：OpenClaw 航班/旅行 Skill 轻量提取

**提取日期**: 2026-03-18
**目标**: sim3-flight — 机票搜索 + 最优飞行路线 Skill
**来源**: GitHub openclaw/skills 档案库 + 社区独立仓库 + API 调研

---

## 一、各 Skill 轻量提取

### 1. FlightClaw (jackculpan/flightclaw)

**来源**: https://github.com/jackculpan/flightclaw
**星标**: 34 | **更新**: 19 天前 | **语言**: Python

**核心功能**:
- `search_flights` — 搜索特定路线当前价格
- `search_dates` — 在日期范围内找最便宜出行日
- `track_flight` — 监控路线价格，可设目标价
- `check_prices` — 扫描所有已追踪航班，检测价格变化
- `list_tracked` / `remove_tracked` — 管理监控列表

**数据源**: `fli` 库（Python 包 `flights`）查询 Google Flights，本地货币自动从 IP 检测

**触发方式**:
- MCP Server: `claude mcp add flightclaw -- python3 /path/to/server.py`
- OpenClaw 包: `npx skills add jackculpan/flightclaw`
- 脚本直调: `scripts/search-flights.py`, `scripts/track-flight.py`

**过滤参数**: 舱位、乘客数（成人/儿童/抱婴）、航空公司代码、最高价格、飞行时长、起降时间窗口、中转时长、多机场（逗号分隔）

**持久化**: 价格历史存 `data/tracked.json`，支持 R2 云备份

**可复用知识**:
- 价格追踪 + 阈值告警的完整设计模式
- 多机场扩展成所有路线组合的策略
- cron 兼容的价格检查架构

---

### 2. skill-google-flights (andrepaim/skill-google-flights)

**来源**: https://github.com/andrepaim/skill-google-flights
**更新**: 6 天前 | **语言**: Python

**核心功能**:
- 实时航班搜索，返回结构化 JSON
- Protobuf 抓取 + Playwright 自动降级（当 Google 封锁时）

**数据源**: Google Flights（fast-flights Protobuf 逆向工程 + Playwright 备用）

**触发方式**（命令行）:
```bash
uv run scripts/search.py \
  --from <IATA> --to <IATA> --date YYYY-MM-DD \
  [--return-date] [--trip one-way|round-trip|multi-city] \
  [--seat economy|premium-economy|business|first] \
  [--adults N] [--children N] \
  [--currency CODE] [--max-stops N] [--limit N]
```

**关键设计细节**:
- 默认货币 BRL（巴西雷亚尔），需要中文用户时要改 CNY
- `current_price` 字段：Google 评定为 low / typical / high / 不可用
- 明确约束：**绝不代替用户订票**（价格为估算，引导用户自行完成）
- Exit code 0 = 成功；1 = 错误（JSON `{"error": ...}` 写 stdout）

**可复用知识**:
- Protobuf 主路 + Playwright 降级的双轨策略
- `--return-date` 支持往返搜索的参数设计
- `uv run` 自动依赖管理模式

---

### 3. flights-skill (Anmoldureha/flights-skill)

**来源**: https://github.com/Anmoldureha/flights-skill
**更新**: 29 天前 | **语言**: Python

**核心功能**:
- 纯 Protobuf 逆向，无 API Key 的 Google Flights 搜索
- MCP Server 模式 + 直接脚本调用两用

**数据源**: Google Flights（Protobuf 逆向，企业级速度）

**触发方式**:
```bash
python search.py SFO JFK 2026-03-01
```
OpenClaw 集成映射: `flight_search` → `venv/bin/python3 search.py {{from}} {{to}} {{date}}`

**输出格式**: 结构化 JSON，面向 AI agent 优化（不是 HTML）

**可复用知识**:
- `{{from}} {{to}} {{date}}` 模板参数在 SKILL.md 中的映射模式
- 分离 `search.py`（搜索逻辑）和 `mcp_server.py`（agent 服务）的模块化设计

---

### 4. flight-pricer (jrojas537/flight-pricer)

**来源**: https://github.com/jrojas537/flight-pricer
**语言**: Python

**核心功能**:
- CLI 工具，通过 Duffel API 搜索航班价格
- 子命令架构：`search` + `config`

**数据源**: **Duffel API**（需要 API Key，付费）

**触发方式**:
```bash
flight-pricer search --from DTW --to MIA --depart 2026-04-06 --return 2026-04-10 --non-stop --cabin first
flight-pricer config set --api-key YOUR_DUFFEL_API_KEY
```

**参数**: `--from`, `--to`, `--depart`, `--return`, `--passengers`, `--max-stops`, `--non-stop`, `--cabin`

**可复用知识**:
- API Key 安全存储在 `~/.config/flight-pricer/config.yaml`（不硬编码）
- `--non-stop` 作为 `--max-stops 0` 的便捷别名
- 结果以可读表格输出，同时适配 CLI 和 agent 集成

---

### 5. Aerobase OpenClaw Skill (Aerobase-app/aerobase-openclaw-skill)

**来源**: https://github.com/Aerobase-app/aerobase-openclaw-skill
**语言**: Python

**核心功能**: 8 个工具
1. `flight_search` — 搜索航班 + 计算时差评分
2. `flight_scoring` — 单独获取时差分析详情
3. `flight_comparison` — 比较多个航班选项
4. `recovery_planning` — 生成个性化时差恢复计划
5. `deal_discovery` — 找时差友好的优惠
6. `airport_information` — 机场设施 + 休息室数据
7. `hotel_search` — 时差友好酒店推荐
8. `itinerary_analysis` — 多段行程整体分析

**数据源**: Aerobase API（需 API Key，`AEROBASE_API_KEY` 环境变量）

**唯一差异化**: **时差评分（0-100）** — 将航班转换成身体恢复成本
- 80-100: 优秀（0-2天恢复）
- 60-79: 良好（2-3天）
- 40-59: 中等（3-5天）
- 20-39: 较差（5-7天）
- 0-19: 严重（7天以上）

**频率限制**: 免费100次/天，Pro 1000次/天，Concierge 10000次/天

**可复用知识**:
- 将"非功能性体验"（时差、疲劳）量化为数字评分的产品思路
- 人类可读输出 + JSON 输出双模式设计

---

### 6. travel-manager (alvarobcmed/travel-manager)

**来源**: openclaw/skills 档案库 → alvarobcmed/travel-manager/SKILL.md
**版本**: 1.0.0 | **发布时间**: 1770221563265

**SKILL.md 原文核心字段**:
```yaml
name: travel-manager
description: Comprehensive travel planning, booking, and management skill.
  Use when needing to plan international trips, manage multi-destination
  itineraries, handle family travel logistics, optimize travel costs, and
  coordinate complex travel arrangements.
```

**核心功能**:
1. Destination Analysis — 目的地分析
2. Route Optimization — 路线优化
3. Cost Calculation — 费用计算
4. Document Preparation — 证件准备
5. Booking Coordination — 预订协调

**数据源**: 无外部 API（LLM 直接生成，参考内置文档）

**参考文档**（references/）:
- `family-travel-checklist.md` — 证件（护照/签证）+ 儿童需求 + 座位/行李安排
- `travel-documents.md` — 护照有效期≥6个月、每国至少2空白页、签证要求、保险

**家庭旅行关键考量**:
- 儿童友好路线、中转舒适度
- 年龄别需求、行李额

**适用场景**: 多国家庭旅行规划、经济路线查找、复杂证件准备

**可复用知识**:
- `references/` 子目录存放领域知识文档的 Skill 结构模式
- 无外部 API 的 LLM-only skill 仍然可以通过结构化 references 提升质量

---

### 7. openclaw-travel-planner-skill (2718564960)

**来源**: https://github.com/2718564960/openclaw-travel-planner-skill
**更新**: 4 天前 | **版本**: 1.0.0 | **语言**: 中文优先

**核心功能**:

| 功能 | 说明 |
|------|------|
| 航班搜索 | 多段实时查询，支持直飞/中转过滤 |
| 酒店推荐 | 基于到达时间和家庭需求 |
| 预算分析 | 三档方案（经济/舒适/豪华） |
| 行程优化 | 考虑儿童日程、天气、特殊活动 |
| 报告生成 | Markdown 完整旅行规划报告 |

**数据源**: 浏览器自动化 + 网络搜索 + 内容提取（无明确指定单一 API）

**参数设计**（最完整的参数规范）:

必填: `origin`, `destinations[]`, `startDate`, `endDate`, `adults`, `children[]`（年龄数组）

选填: `budgetLevel`（economy/comfort/luxury）, `flightPreference`（direct/price/time）, `hotelPreference`, `specialEvents[]`, `outputFormat`（markdown/json）

**特殊场景处理**:
- 随行儿童：避免红眼航班、优先上午/中午出发、飞行时长<6小时
- 特殊节假日：提前2-3个月预订、预算+30-50%、家庭友好活动筛选
- 预算优化：三档标准明确，经济档优先公共交通，豪华档强调便利性

**可复用知识**:
- `children: [age1, age2]` 年龄数组 + 儿童适配逻辑的完整 UX 模式
- 三档预算框架（经济/舒适/豪华）是中文用户最常见的决策框架
- `specialEvents[]` 特殊节日参数是差异化功能点

---

### 8. Trip.com TripGenie — 竞品参考

**来源**: 公开搜索调研

**现状**: GitHub 上无公开的 TripGenie OpenClaw skill，Trip.com 无公开开发者 API 文档。

**TripGenie 已知特征**（基于公开信息）:
- Trip.com 自研的 AI 旅行助手，集成在 Trip.com App 内
- 支持对话式旅行规划（机票+酒店+行程一体化）
- 数据源: Trip.com 自有航班/酒店库（全球覆盖，尤其亚太线路）
- **对 OpenClaw Skill 开发的意义**: 竞品而非数据源，不存在官方 API 集成路径

**结论**: TripGenie 是封闭系统，社区无可复用的 skill 或 API 集成方案。

---

## 二、社区公约数（跨 Skill 共同模式）

### 2.1 数据获取层的三条路

```
路线 A: Google Flights Protobuf 逆向（免费，不稳定）
  └─ fast-flights 库 / fli 库
  └─ 用: FlightClaw, skill-google-flights, flights-skill

路线 B: 商业 API（稳定，付费）
  └─ Duffel API（flight-pricer）
  └─ Amadeus API（travel-mcp-server, mcp-amadeusflights）
  └─ Aerobase API（aerobase-openclaw-skill）

路线 C: LLM 直接生成（无数据源，低准确性）
  └─ travel-manager（alvarobcmed）
  └─ openclaw-travel-planner-skill（部分功能）
```

### 2.2 统一的参数结构

所有 Skill 都收敛到同一组核心参数：

| 参数 | 类型 | 说明 |
|------|------|------|
| `from` / `origin` | IATA 代码或城市名 | 出发地 |
| `to` / `destination` | IATA 代码或城市名 | 目的地 |
| `date` / `depart` | YYYY-MM-DD | 出发日期 |
| `return-date` | YYYY-MM-DD | 返程日期（往返可选）|
| `adults` | int | 成人数，默认 1 |
| `cabin` / `seat` | economy/business/first | 舱位 |
| `max-stops` | int | 最大中转次数 |

### 2.3 通用设计规则

1. **不替用户订票** — skill-google-flights 和 FlightClaw 均明确："价格为估算，引导用户自行完成预订"
2. **JSON 输出优先** — 所有 Skill 都输出结构化 JSON，面向 agent pipeline 消费
3. **IATA 机场代码** — 无论接受城市名还是代码，内部统一用 IATA 三字码
4. **MCP + CLI 双模式** — 多数 Skill 同时支持 MCP Server（agent 调用）和 CLI 脚本（人工测试）
5. **credentials 外置** — API Key 存 `~/.config/` 或环境变量，不硬编码

### 2.4 触发词模式

```yaml
# 典型 SKILL.md 触发描述
description: "Use when needing to search flights, compare prices, track price drops,
  plan multi-destination trips, or optimize travel routes."
```

共同触发关键词集合：`search flights`, `compare prices`, `track price`, `plan trip`, `travel itinerary`, `best route`, `cheapest dates`

---

## 三、API 选型建议

### 3.1 主要 API 比较

| API | 类型 | 免费额度 | 数据质量 | 稳定性 | OpenClaw 适配度 |
|-----|------|----------|----------|--------|-----------------|
| Google Flights (Protobuf 逆向) | 非官方 | 无限制（但有封 IP 风险）| 实时，覆盖全球 | 低（随时可能失效）| 中（需要代理层）|
| Amadeus Self-Service | 官方 | 测试环境固定月配额 | 实时，GDS 数据 | 高 | 高 |
| Duffel | 官方 | 无免费层（按量计费）| 实时，含预订能力 | 高 | 高 |
| AviationStack | 官方 | 100次/月（免费）| 实时飞行状态 | 中 | 中（仅状态追踪）|
| Skyscanner API | 官方 | 无公开免费层（RapidAPI 代理）| 准实时 | 中 | 低（访问门槛高）|
| Aerobase | 官方 | 100次/天 | 含时差评分，非标数据 | 中 | 中（场景较垂直）|

### 3.2 推荐选型

**推荐方案: Amadeus（主）+ fast-flights（副）双轨**

**理由**:

1. **Amadeus** 是 GDS（全球分销系统）直连，数据最权威，覆盖 99% 的商业航班。
   - Self-Service API 有测试环境免费额度，足够 MVP 开发
   - Python SDK 成熟（`amadeus` 包），文档完整
   - MCP 集成已有多个开源参考（`mcp-amadeusflights`, `amadeus-mcp`, `travel-mcp-server`）
   - 关键端点: `shopping.flight_offers_search`, `shopping.flight_dates`（最便宜日期）

2. **fast-flights（Protobuf 逆向）** 作为无需 API Key 的备用方案，适合：
   - 快速原型验证
   - 轻量查询（价格比较不需要 GDS 精度）
   - 降低 API 成本的补充查询

**不推荐 Duffel**（原因: 无免费层，预订能力对 OpenClaw Skill 场景过度）
**不推荐 Skyscanner**（原因: 公开 API 已停止，RapidAPI 代理不稳定且中文覆盖差）
**不推荐 AviationStack**（原因: 仅做飞行状态追踪，不做票价搜索）

### 3.3 Amadeus 关键端点速查

```python
# 航班报价搜索
amadeus.shopping.flight_offers_search.get(
    originLocationCode="SHA",
    destinationLocationCode="NRT",
    departureDate="2026-04-06",
    adults=2,
    children=1,
    travelClass="ECONOMY",
    max=10
)

# 最便宜日期（灵活日期搜索）
amadeus.shopping.flight_dates.get(
    origin="SHA",
    destination="BKK"
)

# 机场/城市搜索（处理中文城市名 → IATA）
amadeus.reference_data.locations.get(
    keyword="Shanghai",
    subType="AIRPORT,CITY"
)
```

---

## 四、社区空白（差异化机会）

### 4.1 已被覆盖（不需要重复做）

- 单段航班搜索（FlightClaw, skill-google-flights, flights-skill 均已覆盖）
- 价格追踪 + 告警（FlightClaw 已完整实现）
- 家庭旅行清单（travel-manager 已有 references 文档）

### 4.2 明确空白（差异化机会）

**空白 1: 多城市最优路线组合（核心需求，无人实现）**

现有 Skill 全部是"A→B 单段"搜索，没有 Skill 能做：
- 给定 A→B→C→A 的多城市行程，自动优化中间枢纽选择
- 将多段 leg 组合成总价最优的行程
- 时间窗口遍历（同一路线不同日期的价格矩阵）

fast-flights 的 Soul Extractor 已发现：`multi-city` 在 Protobuf schema 中存在但标记为 `not implemented`，意味着**底层能力支持，产品层没人做**。

**空白 2: 中文城市名 → IATA 的自然语言解析层**

所有英文 Skill 都要求 IATA 三字码（SFO, JFK）。中文用户说"上海飞曼谷"，没有任何 Skill 能直接处理。需要：
- 中文城市名 → IATA 映射层（Amadeus `reference_data.locations` 可以实现）
- 处理歧义（上海 = PVG or SHA，北京 = PEK or PKX）

**空白 3: 价格 + 时长 + 中转次数的多目标权衡**

所有 Skill 只做单目标排序（按价格或按时长），没有：
- 用户设定权重（"我愿意多花 500 元换直飞"）
- Pareto 最优解输出（展示价格-时长 Pareto 前沿）
- 置信度评分（"这个价格在过去30天属于 low"）

**空白 4: 时区感知的行程时间计算**

openclaw-travel-planner-skill 做到了"儿童不适合红眼航班"的规则，但没有实现：
- 到达当地时间的时区换算
- 时差叠加（上海→迪拜→纽约的累计时差）
- Aerobase 的时差评分思路，但集成到免费方案中

**空白 5: 价格历史 + 趋势预测**

FlightClaw 有价格历史记录（`tracked.json`），但没有：
- 基于历史的"现在是否是好时机"评判
- 季节性价格规律提示
- "再等X天可能便宜Y%"的预测

**空白 6: 中文出发的亚太航线覆盖**

所有社区 Skill 以欧美路线为默认值（默认货币 BRL/USD，默认机场 SFO/JFK）。针对中文用户的亚太航线（上海/北京/广州 → 东南亚/日本/韩国）没有专门优化。

---

## 五、对 sim3-flight Skill 的直接建议

### 5.1 核心定位（差异化）

**不要做**: 又一个 Google Flights 单段搜索 wrapper
**要做**: 中文用户的多城市最优路线规划器

定位: **"给定出发城市 + 多个目的地 + 预算约束，自动规划最优行程顺序和航班组合"**

### 5.2 技术路线推荐

```
输入层: 中文自然语言 → LLM 解析 → 结构化参数
         ↓
城市解析: 中文城市名 → IATA (Amadeus reference_data 或本地字典)
         ↓
搜索层: Amadeus flight_offers_search (主) + fast-flights (备)
         ↓
优化层: 多段 leg 组合 → Pareto 最优解 (价格 vs 时长 vs 中转)
         ↓
输出层: Markdown 行程报告 + JSON 结构化数据
```

### 5.3 可直接复用的社区代码

| 来源 | 可复用内容 | 文件 |
|------|-----------|------|
| skill-google-flights | 完整参数结构 + Protobuf/Playwright 双轨逻辑 | `scripts/search.py` |
| FlightClaw | 价格追踪 + 持久化模式 | `tracking.py` + `data/tracked.json` |
| flight-pricer | Duffel API 集成 + 安全 credential 存储 | `src/` |
| openclaw-travel-planner-skill | 家庭旅行参数结构 + 三档预算框架 | `SKILL.md` |
| travel-mcp-server | Amadeus + AviationStack 双 API 集成 | GitHub |

### 5.4 SKILL.md 触发描述草案

```yaml
name: flight-optimizer
description: "Use when user wants to search flights between cities, compare prices
  across dates, plan multi-destination itineraries, find the cheapest travel dates,
  or optimize multi-city trip routes. Handles Chinese city names. Supports family
  travel with children. Outputs both Markdown itineraries and structured JSON."
```

---

*报告完成时间: 2026-03-18*
*数据来源: GitHub openclaw/skills 档案 + 社区独立仓库调研 + MCP 生态搜索*

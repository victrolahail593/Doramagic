---
name: flight-search
version: 0.1.0
description: |
  机票搜索与最优飞行路线规划。搜索航班价格，比较方案，
  规划多城市最优路线。支持单程/往返/多城市。
  Triggers on: "搜航班", "机票", "飞行路线", "search flights",
  "cheapest flight", "multi-city route", "航班比价", "最便宜的航班"
user-invocable: true
tags: [flights, travel, route-optimization, price-comparison]
allowed-tools:
  - Bash
  - Read
  - Write
  - AskUserQuestion
metadata:
  openclaw:
    category: travel
    requires:
      bins: ["python3", "pip"]
      env: ["AMADEUS_API_KEY", "AMADEUS_API_SECRET"]
      optional_env: ["BRIGHTDATA_API_KEY"]
---

# Flight Search -- 机票搜索与最优飞行路线

从口袋里掏出的航班搜索工具。搜索实时价格、比较方案、规划多城市最优路线。

**核心原则**: 给用户工具，不替用户做决策。Skill 提供数据和排序，用户自己决定买哪张票。

---

## 架构概览

```
用户自然语言输入
    |
    v
[意图解析层] LLM 将自然语言转换为结构化参数
    |
    v
[城市解析层] 中文城市名 / 模糊表达 → IATA 三字码
    |
    v
[数据获取层] Amadeus API (主) / fast-flights (备)
    |
    v
[路线优化层] 单段: 直接排序 / 多城市: Pareto 最优组合
    |
    v
[输出层] 结构化 JSON + Markdown 报告
```

**铁律**: 代码说事实（价格、时长、中转次数来自 API），AI 说故事（自然语言解读和建议来自 LLM）。价格排序、Pareto 前沿计算等确定性逻辑必须用代码实现，禁止让 LLM 做数值比较。

---

## 流程一：单程/往返航班搜索

### 触发条件

用户意图包含：搜索/查询/找 + 机票/航班/飞 + 出发地 + 目的地 + 日期

### Step 1: 意图提取

从用户自然语言中提取以下参数。缺少必填参数时，用 `AskUserQuestion` 询问。

**必填参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `origin` | string | 出发地（IATA 代码或中文城市名） |
| `destination` | string | 目的地（IATA 代码或中文城市名） |
| `depart_date` | YYYY-MM-DD | 出发日期 |

**选填参数**（有默认值，不必每次都问用户）:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `return_date` | YYYY-MM-DD | null | 返程日期，有值则为往返 |
| `adults` | int | 1 | 成人数（1-9） |
| `children` | int | 0 | 儿童数 |
| `infants` | int | 0 | 婴儿数（<=成人数） |
| `cabin` | enum | economy | economy / premium_economy / business / first |
| `max_stops` | int | null | 最大中转次数，null=不限 |
| `currency` | string | CNY | ISO 4217 货币代码 |
| `sort_by` | enum | pareto | pareto / price / duration / stops |

**意图提取 Prompt 契约**:

```
你是航班搜索参数提取器。从用户输入中提取结构化搜索参数。

规则:
1. 今天是 {today_date}
2. 相对日期（"下周五"、"三月底"）转换为绝对日期 YYYY-MM-DD
3. 中文城市名保持原样（后续由城市解析层处理）
4. 如果用户未指定舱位，默认经济舱
5. 如果用户说"直飞"，设 max_stops=0
6. 如果用户提到返程日期，设 return_date
7. "最便宜" → sort_by=price；"最快" → sort_by=duration；"直飞优先" → sort_by=stops

输出严格 JSON 格式:
{
  "origin": "上海",
  "destination": "东京",
  "depart_date": "2026-04-15",
  "return_date": null,
  "adults": 1,
  "children": 0,
  "infants": 0,
  "cabin": "economy",
  "max_stops": null,
  "currency": "CNY",
  "sort_by": "pareto"
}
```

### Step 2: 城市名 → IATA 解析

对 `origin` 和 `destination`，如果不是 IATA 三字码（3个大写字母），执行解析:

```bash
python3 {baseDir}/scripts/resolve_city.py "上海"
# 输出: {"city": "上海", "iata_candidates": [{"code": "PVG", "name": "浦东国际机场"}, {"code": "SHA", "name": "虹桥国际机场"}], "default": "PVG"}
```

**歧义处理规则**:
- 同城多机场（上海=PVG/SHA，北京=PEK/PKX，东京=NRT/HND）：默认选国际航班主机场，但告知用户可选其他
- 无法识别：用 `AskUserQuestion` 请用户确认
- 数据源: 内置 `data/city_iata_map.json`（覆盖主要中文城市 + 热门国际目的地），Amadeus `reference_data.locations` API 兜底

### Step 3: 调用航班搜索 API

**主路径 -- Amadeus**:

```bash
python3 {baseDir}/scripts/search_flights.py \
  --origin PVG --destination NRT \
  --depart 2026-04-15 \
  --return 2026-04-20 \
  --adults 1 --children 0 --infants 0 \
  --cabin economy \
  --max-stops 1 \
  --currency CNY \
  --limit 20
```

脚本内部调用 `amadeus.shopping.flight_offers_search.get()`，输出结构化 JSON:

```json
{
  "query": { "origin": "PVG", "destination": "NRT", "depart_date": "2026-04-15" },
  "results": [
    {
      "id": "offer_001",
      "price": 2850,
      "currency": "CNY",
      "total_duration_min": 195,
      "stops": 0,
      "segments": [
        {
          "departure": {"iata": "PVG", "time": "2026-04-15T08:30"},
          "arrival": {"iata": "NRT", "time": "2026-04-15T12:45"},
          "airline": "MU",
          "flight_number": "MU521",
          "duration_min": 195,
          "aircraft": "A350"
        }
      ],
      "cabin": "economy",
      "booking_url_hint": "https://www.google.com/travel/flights?q=PVG-NRT-20260415"
    }
  ],
  "metadata": {
    "source": "amadeus",
    "search_time_ms": 1250,
    "result_count": 15,
    "price_range": {"min": 2850, "max": 8900}
  }
}
```

**备用路径 -- fast-flights**:

当 Amadeus API 不可用（无 Key、超额度、超时）时自动降级:

```bash
python3 {baseDir}/scripts/search_flights_fallback.py \
  --origin PVG --destination NRT \
  --depart 2026-04-15 \
  --seat economy \
  --trip one-way \
  --currency CNY
```

使用 `fast-flights` 库（Protobuf 逆向 Google Flights）。注意事项:
- 需要代理（BrightData 或类似）避免 IP 封锁
- 价格返回为裸 int，脚本自动附加 currency 字段
- 结果可能与 Amadeus 有差异（数据源不同），输出时标注 `"source": "google_flights"`

### Step 4: 结果排序与展示

**Pareto 排序**（默认）:

对搜索结果做三维 Pareto 过滤，输出 Pareto 前沿上的方案（在价格、时长、中转三个维度上不被其他方案完全支配的选项）。

```
Pareto 支配定义:
方案 A 支配方案 B，当且仅当:
  A.price <= B.price AND A.duration <= B.duration AND A.stops <= B.stops
  且至少有一个维度严格小于。

Pareto 前沿 = 所有不被支配的方案集合。
```

**单维排序**: 当用户明确指定 `sort_by=price/duration/stops` 时，按该维度升序排列。

**展示格式**:

输出 Markdown 表格给用户:

```markdown
## 搜索结果: 上海(PVG) → 东京(NRT) | 2026-04-15

| # | 航班 | 价格 | 时长 | 中转 | 出发→到达 |
|---|------|------|------|------|-----------|
| 1 | MU521 | ¥2,850 | 3h15m | 直飞 | 08:30→12:45 |
| 2 | CA919 | ¥2,650 | 5h20m | 1转(PEK) | 07:00→15:20 |
| 3 | NH972 | ¥3,200 | 2h55m | 直飞 | 10:15→14:10 |

> 数据来源: Amadeus | 查询时间: 2026-04-10 14:30 CST
> 价格为估算值，以航司官网实际价格为准。
```

同时将完整 JSON 结果写入 `{workDir}/flight_results_{timestamp}.json`。

---

## 流程二：多城市最优路线规划（核心差异化）

### 触发条件

用户意图包含：多个目的地 + 路线/行程/顺序 + 最优/最便宜/规划

示例: "我要从上海出发，去东京、曼谷、新加坡，最后回上海，怎么飞最划算？"

### Step 1: 意图提取

在单段搜索参数基础上，增加:

| 参数 | 类型 | 说明 |
|------|------|------|
| `origin` | string | 出发地（同时也是返回地） |
| `destinations` | string[] | 目的地列表（无序，Skill 来排最优顺序） |
| `date_range` | {start, end} | 旅行时间窗口 |
| `days_per_city` | int | 每个城市停留天数（默认 2-3） |
| `return_to_origin` | bool | 是否回到出发地（默认 true） |

### Step 2: 搜索矩阵构建

对所有城市对（含出发地），搜索航班价格，构建价格矩阵:

```
城市列表: [PVG, NRT, BKK, SIN]  (出发地 + 3个目的地)

搜索任务: C(4,2) * 2 = 12 个方向的航班搜索
  PVG→NRT, PVG→BKK, PVG→SIN
  NRT→PVG, NRT→BKK, NRT→SIN
  BKK→PVG, BKK→NRT, BKK→SIN
  SIN→PVG, SIN→NRT, SIN→BKK
```

**并行搜索**: 所有搜索任务并行执行（Amadeus API 支持并发）。

```bash
python3 {baseDir}/scripts/build_flight_matrix.py \
  --cities PVG,NRT,BKK,SIN \
  --date-start 2026-04-15 \
  --date-end 2026-04-30 \
  --days-per-city 3 \
  --adults 1 \
  --cabin economy \
  --currency CNY
```

输出 `flight_matrix.json`:

```json
{
  "cities": ["PVG", "NRT", "BKK", "SIN"],
  "matrix": {
    "PVG→NRT": {"best_price": 2850, "best_duration": 175, "best_stops": 0, "options": [...]},
    "PVG→BKK": {"best_price": 2100, "best_duration": 300, "best_stops": 0, "options": [...]},
    "NRT→BKK": {"best_price": 3500, "best_duration": 420, "best_stops": 1, "options": [...]},
    ...
  },
  "search_date": "2026-04-10",
  "currency": "CNY"
}
```

### Step 3: 路线优化

**城市数 <=8: 精确解（穷举所有排列）**

```bash
python3 {baseDir}/scripts/optimize_route.py \
  --matrix flight_matrix.json \
  --origin PVG \
  --return-to-origin true \
  --optimization pareto
```

算法:
1. 生成所有目的地排列（N! 种，N<=7 时最多 5040 种）
2. 对每种排列，计算总价格、总时长、总中转次数
3. 对所有排列做 Pareto 过滤
4. 输出 Pareto 前沿上的 Top 方案（最多 5 个）

**城市数 >8: 近似解（贪心最近邻 + 2-opt 改进）**

```bash
python3 {baseDir}/scripts/optimize_route.py \
  --matrix flight_matrix.json \
  --origin PVG \
  --return-to-origin true \
  --optimization greedy \
  --improvement 2opt
```

算法:
1. 贪心最近邻: 从出发地开始，每步选"综合成本最低的下一个未访问城市"
2. 2-opt 改进: 尝试交换任意两段路线，如果总成本降低则接受
3. 重复多次随机起点，取最优结果
4. 明确标注"近似解，可能非全局最优"

**多目标综合评分**:

```
综合成本 = alpha * normalize(price) + beta * normalize(duration) + gamma * stops_penalty

默认权重: alpha=0.5, beta=0.3, gamma=0.2
用户说"最便宜": alpha=0.8, beta=0.1, gamma=0.1
用户说"最快": alpha=0.1, beta=0.8, gamma=0.1
用户说"少转机": alpha=0.2, beta=0.1, gamma=0.7

normalize(x) = (x - min) / (max - min)  // min-max 归一化
stops_penalty = stops / max_stops_in_set
```

### Step 4: 结果展示

```markdown
## 最优路线方案: 上海出发 → 东京/曼谷/新加坡 → 回上海

### 方案 A: 最便宜 (总价 ¥11,200)
```
PVG → BKK (¥2,100 / 5h / 直飞) 4月15日
  ↓ [曼谷停留 3 天]
BKK → SIN (¥1,800 / 2h30m / 直飞) 4月18日
  ↓ [新加坡停留 3 天]
SIN → NRT (¥3,500 / 7h / 1转) 4月21日
  ↓ [东京停留 3 天]
NRT → PVG (¥3,800 / 3h15m / 直飞) 4月24日
```

### 方案 B: 最快 (总飞行时间 14h)
...

### 方案 C: 平衡方案 (总价 ¥12,500 / 总飞行 16h / 全程 1 转)
...

> 共评估 6 种路线排列，展示 Pareto 前沿上的 3 个不支配方案。
> 数据来源: Amadeus | 查询时间: 2026-04-10 | 价格为估算值。
```

---

## 流程三：价格追踪与提醒

### 触发条件

用户意图包含：追踪/监控/提醒 + 价格/降价/便宜

### Step 1: 创建追踪任务

```bash
python3 {baseDir}/scripts/track_flight.py add \
  --origin PVG --destination NRT \
  --depart 2026-04-15 \
  --target-price 2500 \
  --currency CNY
```

追踪数据存储在 `{dataDir}/tracked_flights.json`:

```json
{
  "tracks": [
    {
      "id": "trk_001",
      "origin": "PVG",
      "destination": "NRT",
      "depart_date": "2026-04-15",
      "target_price": 2500,
      "currency": "CNY",
      "created_at": "2026-04-10T14:30:00+08:00",
      "price_history": [
        {"date": "2026-04-10", "price": 2850, "source": "amadeus"},
        {"date": "2026-04-11", "price": 2750, "source": "amadeus"}
      ],
      "status": "active"
    }
  ]
}
```

### Step 2: 价格检查（cron 兼容）

```bash
python3 {baseDir}/scripts/track_flight.py check
```

遍历所有 active 追踪任务，搜索当前价格，更新 price_history。如果价格 <= target_price，输出告警消息:

```
[降价提醒] PVG→NRT 4月15日: 当前 ¥2,480（目标 ¥2,500）
过去 5 天价格趋势: ¥2,850 → ¥2,750 → ¥2,650 → ¥2,550 → ¥2,480 (持续下降)
建议: 当前价格已达目标，但趋势仍在下降，可以再观望 1-2 天。
```

### Step 3: 管理追踪列表

```bash
python3 {baseDir}/scripts/track_flight.py list    # 列出所有追踪
python3 {baseDir}/scripts/track_flight.py remove --id trk_001  # 移除追踪
```

---

## 数据源设计

### 主数据源: Amadeus Self-Service API

**认证**:

```bash
# 环境变量（必须）
export AMADEUS_API_KEY="your_api_key"
export AMADEUS_API_SECRET="your_api_secret"

# 或配置文件
# {dataDir}/config.yaml
amadeus:
  api_key: ${AMADEUS_API_KEY}
  api_secret: ${AMADEUS_API_SECRET}
  environment: production  # test | production
```

**关键端点**:

| 端点 | 用途 | 响应时间 |
|------|------|----------|
| `shopping.flight_offers_search` | 航班报价搜索 | 2-5s |
| `shopping.flight_dates` | 最便宜日期 | 1-3s |
| `reference_data.locations` | 城市/机场模糊搜索 | <1s |

**频率限制**: 测试环境 10 req/s，生产环境按合同。脚本内置 rate limiter。

### 备用数据源: fast-flights (Google Flights Protobuf 逆向)

**使用条件**: Amadeus 不可用时自动降级，或用户明确请求 Google Flights 数据。

**依赖**: `pip install fast-flights`（需要 Python >=3.10, primp Rust 扩展）

**限制**:
- IP 封锁风险，生产环境必须配代理（BrightData `BRIGHTDATA_API_KEY`）
- 价格无货币单位，脚本自动附加查询时指定的 currency
- `multi-city` trip type 在 proto 中声明但未实现，多城市必须拆成多个单程查询
- JavaScript 数据路径 (`payload[3][0]`) 可能随 Google 更新失效

### 健康检查

```bash
python3 {baseDir}/scripts/healthcheck.py
# 输出:
# Amadeus API: OK (test env, 847/1000 monthly quota remaining)
# fast-flights: OK (Google Flights responding, last check 2 min ago)
# city_iata_map: 523 cities loaded
```

建议: 每日运行一次健康检查。Amadeus 不可用时邮件/消息告警。

---

## AI Prompt 契约

### 契约 1: 意图提取（用户输入 → 结构化参数）

```
角色: 航班搜索参数提取器
温度: 0（确定性解析）
输入: 用户自然语言
输出: 严格 JSON（schema 见 Step 1）

规则:
- 今天日期: {today_date}
- 默认货币: CNY
- 中文城市名保持原样
- 歧义优先问用户，不猜
- 多个目的地 → 触发多城市流程
```

### 契约 2: 结果叙述（搜索结果 → 自然语言解读）

```
角色: 航班搜索结果解读者
温度: 0.3（允许轻微叙述变化）
输入: 结构化搜索结果 JSON（已裁剪，只含用户决策所需字段）
输出: Markdown 格式的结果展示 + 简要建议

规则:
- 价格数字必须直接来自 JSON 数据，禁止编造
- 可以说"直飞通常更舒适"，不能说"我建议你选方案 A"
- 提供预订提示链接（Google Flights URL），不替用户订票
- 如果结果为空，如实说"未找到符合条件的航班"，不虚构航班信息
```

### 契约 3: 数据裁剪（API 原始响应 → LLM 可消费格式）

从 API 原始响应中只保留以下字段回注 LLM:
- 价格、货币
- 出发/到达时间
- 航司代码、航班号
- 总时长（分钟）
- 中转次数、中转机场
- 舱位

丢弃: 票价规则、行李政策、退改条款等（这些信息由预订平台提供，Skill 不做）。

---

## 存储路径与格式

```
{dataDir}/                          # 默认 ~/.flight-search/
  config.yaml                       # API 密钥和配置
  city_iata_map.json                # 中文城市→IATA 映射表
  tracked_flights.json              # 价格追踪任务
  cache/                            # 搜索结果缓存
    {origin}_{dest}_{date}.json     # 单次搜索缓存（TTL 4小时）
  results/                          # 历史搜索结果
    flight_results_{timestamp}.json # 每次搜索完整结果
    route_plan_{timestamp}.json     # 多城市路线方案
```

**缓存策略**: 同一路线 + 同一日期的搜索结果缓存 4 小时。多城市矩阵搜索中，已缓存的城市对直接读缓存，减少 API 调用。

---

## 已知限制

1. **价格为估算值**: API 返回的价格随时变动，实际购买以航司官网为准
2. **多城市上限**: 穷举优化最多 8 个目的地（8! = 40320 排列），超过自动切换贪心算法
3. **不含行李/退改**: Skill 不处理行李额度、退改签政策，这些信息因航司和票价类别而异
4. **fast-flights 脆弱性**: Google Flights 的 Protobuf schema 或 JS 数据路径变更会导致备用数据源失效
5. **日期范围搜索成本**: "最便宜日期"搜索 30 天窗口 = 30 次 API 调用，注意额度消耗
6. **中转成本未量化**: 中转等候时间的隐性成本（餐饮、住宿、疲劳）未计入综合评分
7. **仅搜索不订票**: Skill 永远不会执行预订操作，只提供信息和跳转链接

---

## 暗坑警告（给 Skill 维护者）

1. **Amadeus 测试环境返回模拟数据**: 测试环境的价格不是真实价格，切换到生产环境前务必知晓
2. **fast-flights 的 `multi-city` 是假功能**: proto 里存在但标记 `not implemented`，传入不会报错但结果未定义
3. **同城多机场**: 上海(PVG/SHA)、北京(PEK/PKX)、东京(NRT/HND) 等城市搜索时应搜索所有机场组合，取最优
4. **round-trip 的 airlines 过滤 bug**: fast-flights 中，round-trip 搜索只有去程的 airlines 过滤生效，回程被服务器忽略
5. **primp 的浏览器版本过期**: fast-flights 的 `impersonate="chrome_145"` 是硬编码版本号，需定期更新
6. **API 异步搜索**: 部分 Flight API（如 trip.ir 模式）是提交→轮询模型，单次 await 可能返回不完整结果

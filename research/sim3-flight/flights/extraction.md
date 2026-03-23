# Soul Extraction: fast-flights (v3.0rc1)

**Project**: `/tmp/flights`
**Extracted**: 2026-03-18
**Extractor**: Soul Extractor v0.9

---

## Stage 0 — repo_facts

```json
{
  "name": "fast-flights",
  "version": "3.0rc1",
  "description": "The fast, robust, strongly-typed Google Flights scraper (API) implemented in Python.",
  "author": "AWeirdDev",
  "license": "MIT",
  "python_requires": ">=3.10",
  "dependencies": ["primp", "protobuf>=5.27.0", "selectolax"],
  "optional_dependencies": { "local": ["playwright"] },
  "entry_points": ["get_flights", "fetch_flights_html", "create_query", "FlightQuery", "Passengers", "Query"],
  "integration_points": ["BrightData (paid proxy network)"],
  "key_files": [
    "fast_flights/querying.py",
    "fast_flights/fetcher.py",
    "fast_flights/parser.py",
    "fast_flights/model.py",
    "fast_flights/types.py",
    "fast_flights/pb/flights.proto",
    "fast_flights/pb/flights_pb2.py",
    "fast_flights/integrations/base.py",
    "fast_flights/integrations/bright_data.py"
  ],
  "architecture": "protobuf_query_encode → http_fetch → js_data_parse → typed_dataclasses",
  "test_files": ["example.py", "test_bright_data.py"],
  "notable": {
    "parser_credit": "Data discovery by @kftang (comment in parser.py:31)",
    "multi_city": "declared in proto enum but marked 'not implemented' (flights.proto:27)",
    "tfs_param": "Base64(protobuf_serialized_Info_message) becomes ?tfs= URL param",
    "js_data_path": "payload[3][0] for flights, payload[7][1][0/1] for alliances/airlines"
  }
}
```

---

## Stage 1 — 灵魂发现

### 本质 (Essence)

`fast-flights` 的本质是一个**协议逆向工程库**。

Google Flights 在 2018 年关闭了公开 API，但其 UI 仍在运行。这个库的核心发现是：Google Flights 的搜索请求参数 `?tfs=` 是一个 Base64 编码的 Protobuf 二进制序列化消息。只要能构造合法的 Protobuf 消息并序列化，就能发送任意搜索请求，完全绕过没有公开 API 的限制。

**一句话本质**：用 Protobuf 重新"说"Google 的语言，从 HTML 响应中提取 JavaScript 嵌入数据，实现零成本 Google Flights 数据访问。

### 设计哲学 (Design Philosophy)

1. **速度优先于完整性**：名字叫"fast-flights"，拒绝 Playwright（"one word: slow. two words: extremely slow"），选择 `primp`（浏览器指纹伪装 HTTP 客户端）直接发请求。
2. **强类型即文档**：整个库用 `@dataclass` + `Literal` 类型注解构建，`SeatType`/`TripType`/`Language`/`Currency` 全是 `Literal` 联合类型。IDE 自动补全就是使用手册。
3. **两层分离原则**：查询构造（`querying.py`）与数据解析（`parser.py`）完全分离。构造层说"发什么请求"，解析层说"拿到什么数据"，`fetcher.py` 只是胶水。
4. **开放集成点**：`Integration` ABC 允许替换 HTTP 层（BrightData 是第一个实现）。核心解析逻辑与传输层解耦。
5. **边界内做事**：README 明确说"Google allowed many companies like Serpapi to scrape their web pretending nothing happened"——这是作者的法律心理安慰，不是法律意见。

### 心智模型 (Mental Model)

作者的思维链完整保留在 README 里，是罕见的"逆向工程思维日记"：

```
目标：搜索航班价格
→ 找 Google Flights API → 2018年死了
→ 找现有 scraper → hugoglvs 用 Playwright，慢且不能跑在 Edge
→ 看 URL 参数 → tfs= 是什么鬼
→ Base64 解码 → 看到日期但乱码
→ 猜是某种序列化格式 → 搜"google's json alternative"
→ 发现 Protobuf → 用在线解码器验证
→ 写最简 .proto → 能编解码了
→ 完工
```

这个心智模型的关键洞见：**URL 参数不是 opaque token，是可解析的结构化数据**。大多数人看到 `CBwQAhoeEgoyMDI0LTA1LTI4ag...` 就放弃了，作者选择追到底。

---

## Stage 2 — 结构化卡片

### CC-01: Protobuf 查询构造

**类别**: Core Concept
**标题**: Google Flights 的 `?tfs` 参数是 Base64(Protobuf(Info))

**证据**:
- `fast_flights/pb/flights.proto:1-43` — 完整 proto schema，`Info` 消息包含 `FlightData[]`, `Seat`, `Passenger[]`, `Trip`
- `fast_flights/querying.py:22-36` — `Query.pb()` 返回 `Info`，`to_bytes()` 调用 `SerializeToString()`，`to_str()` 调用 `b64encode`
- `fast_flights/querying.py:43-50` — `Query.url()` 拼接 `?tfs=` + base64 string + `&hl=` + `&curr=`

**字段映射**（`flights.proto`）:
- Airport: `field 2 = airport string`（注意 field number 是 2 不是 1，这是 Google 内部编号）
- FlightData: `field 2=date, 13=from_airport, 14=to_airport, 5=max_stops, 6=airlines`
- Info: `field 3=data[], 9=seat, 8=passengers[], 19=trip`

**含义**: 这些非连续 field number 是 Google 内部 Protobuf schema 的真实编号，作者通过逆向发现并硬编码。任何编号变动都会导致静默失败（Google 服务器正常响应但数据错误）。

---

### CC-02: JavaScript 嵌入数据解析

**类别**: Core Concept
**标题**: 响应 HTML 中的 `<script class="ds:1">` 包含完整航班 JSON

**证据**:
- `fast_flights/parser.py:27` — `script = parser.css_first(r"script.ds\:1")`
- `fast_flights/parser.py:33` — `data = js.split("data:", 1)[1].rsplit(",", 1)[0]`
- `fast_flights/parser.py:31` — 注释："Data discovery by @kftang, huge shout out!"

**数据路径**（`parser.py:41-109`）:
- `payload[7][1][0]` → alliances 列表 `[(code, name), ...]`
- `payload[7][1][1]` → airlines 列表 `[(code, name), ...]`
- `payload[3][0]` → 航班列表（None 表示无结果）
- 每条航班 `k[0]` = flight info，`k[1][0][1]` = price
- 单段航班字段：`[3]=from_code, [4]=from_name, [6]=to_name, [5]=to_code, [8]=dep_time, [10]=arr_time, [11]=duration, [17]=plane_type, [20]=dep_date, [21]=arr_date`
- `flight[22][7]` = carbon_emission，`flight[22][8]` = typical_carbon

**注意**: 这是硬编码的数字索引路径，完全依赖 Google JavaScript 数据结构不变。v3.0 切换到 JS 数据是因为之前的 HTML DOM 结构变了。

---

### CC-03: Browser Impersonation via `primp`

**类别**: Core Concept
**标题**: 用 `primp` 伪装成 Chrome 145 on macOS 发请求，绕过机器人检测

**证据**:
- `fast_flights/fetcher.py:78-84` — `Client(impersonate="chrome_145", impersonate_os="macos", referer=True, cookie_store=True)`
- `pyproject.toml:22` — `primp` 是核心依赖（非 optional）

**含义**: `primp` 是 Rust 实现的 HTTP 客户端，能在 TLS 指纹层面伪装成真实浏览器。这比 `requests` + User-Agent 欺骗更难被检测，也比 Playwright 快得多（不需要渲染引擎）。

---

### WF-01: 完整数据流

**类别**: Workflow
**标题**: 从用户调用到结构化航班列表的完整路径

```
用户代码
  → create_query(flights=[FlightQuery(...)], seat=..., trip=...) [querying.py:133]
  → Query 对象，持有 flight_data[], seat, trip, passengers, language, currency
  → get_flights(query) [fetcher.py:47]
  → fetch_flights_html(query) [fetcher.py:64]
    → query.params() → {"tfs": base64_protobuf, "hl": lang, "curr": curr} [querying.py:52]
    → primp.Client.get("https://www.google.com/travel/flights", params=...) [fetcher.py:92]
    → 返回 HTML string
  → parse(html) [parser.py:23]
    → LexborHTMLParser(html).css_first("script.ds:1") [parser.py:27]
    → parse_js(script_text) [parser.py:32]
      → json.loads(split_js_data) [parser.py:36]
      → 提取 alliances, airlines → JsMetadata
      → 遍历 payload[3][0] → list[Flights]
  → 返回 MetaList[Flights]（MetaList 是 list[Flights] 的子类，带 metadata 属性）
```

**证据**:
- `fast_flights/fetcher.py:60-61`
- `fast_flights/parser.py:23-28`
- `fast_flights/querying.py:52-54`

---

### WF-02: Integration 替换 HTTP 层

**类别**: Workflow
**标题**: Integration 接口允许用代理服务替换直连抓取

**证据**:
- `fast_flights/integrations/base.py:15-23` — `Integration` ABC，单一方法 `fetch_html(q) -> str`
- `fast_flights/fetcher.py:77-96` — `if integration is None: 直连; else: integration.fetch_html(q)`
- `fast_flights/integrations/bright_data.py:38-48` — BrightData 实现：POST 到 BrightData API，传入 Google Flights URL

**设计含义**: 解析逻辑与传输完全解耦。只要实现 `fetch_html` 方法返回正确的 HTML，什么传输方式都行（代理池、缓存、本地 Playwright 等）。

---

### DR-01: 强类型 Query 构建器模式

**类别**: Design Rule
**标题**: 所有输入在构造时验证，输出路径唯一

**证据**:
- `fast_flights/querying.py:98-103` — Passengers 构造器内做两个 assert：总人数≤9，婴儿数≤成人数
- `fast_flights/querying.py:120-130` — `SEAT_LOOKUP`, `TRIP_LOOKUP` 字典做字符串→枚举映射，无效值会 KeyError
- `fast_flights/types.py:3-73` — Language 是 58 个合法值的 `Literal` 联合，Currency 是 70+ 个合法值的 `Literal` 联合
- `fast_flights/model.py:41` — `duration` 字段用 `Annotated[int, "(minutes)"]` 标注单位

**规则含义**: 库的设计哲学是"垃圾进，错误出"（fail fast at construction），而非"垃圾进，垃圾出"（silent corruption）。

---

### DR-02: MetaList — 数据与元数据同容器

**类别**: Design Rule
**标题**: `MetaList` 继承 `list[Flights]`，在同一对象上附加 `.metadata`

**证据**:
- `fast_flights/parser.py:17-18` — `class MetaList(list[Flights]): metadata: JsMetadata`
- `fast_flights/parser.py:111` — `flights.metadata = meta`（直接属性赋值到 list 实例）

**设计含义**: 这是一个非常 Python 的做法——子类化内置类型，避免引入 wrapper 或 Result 对象。但也是一个潜在陷阱：直接遍历 `res` 得到 `Flights`，访问 `res.metadata` 得到全局元数据。两者共存于同一对象。

---

### DR-03: 多城市功能声明但未实现

**类别**: Design Rule
**标题**: `MULTI_CITY` 在 Proto enum 里存在，但代码注释标为 "not implemented"

**证据**:
- `fast_flights/pb/flights.proto:27` — `MULTI_CITY = 3; // not implemented`
- `fast_flights/querying.py:129` — `"multi-city": Trip.MULTI_CITY` 在 TRIP_LOOKUP 中存在

**含义**: 用户可以传入 `trip="multi-city"`，查询会构造成功并发出，但结果行为未定义。这是一个**静默的未实现功能**。

---

## Stage 3.5 — INFERENCE 标注

以下结论无直接代码证据，基于结构推断：

- **INFERENCE**: `script.ds:1` 这个 CSS 选择器是硬编码的，Google 任何时候重命名这个脚本标签（或增加/删除前缀脚本）都会导致 `parse()` 抛 AttributeError（`script` 为 None 时调用 `.text()` 失败）。

- **INFERENCE**: `payload[3][0]` 等数字索引路径是脆弱的。历史上 v3.0 就是因为之前的 HTML 解析方式失效才切换到 JS 数据（README changelog: "v3.0rc0 - Uses Javascript data instead"）。这意味着这个路径**已经断过一次**。

- **INFERENCE**: `primp` 的 `impersonate="chrome_145"` 是写死的版本号。Chrome 主版本号每隔几周递增，当 Google 检测到 Chrome 145 的 TLS 指纹过老时，可能触发 bot detection 或返回不同的页面结构。

- **INFERENCE**: `test_bright_data.py` 使用了旧 API（`create_filter`, `get_flights_from_filter`, `filter.as_b64()`），与当前 `__init__.py` 导出的 API 不匹配。这说明 test 文件没有随 API 重构更新，**测试文件已失效**。

---

## UNSAID — 暗坑

### UNSAID-01: Google 协议随时可能变更，无预警机制

这是整个库最大的脆弱性，但 README 和文档几乎没有提。

具体风险层次：
1. **Protobuf field numbers 变更**：`FlightData.from_airport` 在 field 13，`to_airport` 在 field 14。如果 Google 内部 schema 演进，这些编号改变，序列化出的二进制消息就会被服务器解读为错误字段（Protobuf 按 field number 匹配，不按字段名），导致返回错误结果而不是报错。
2. **JavaScript 数据路径变更**：`payload[3][0]`、`payload[7][1][1]` 这些索引是经验值，Google 随时可以重排数据结构。v2→v3 的迁移历史证明这已经发生过。
3. **`script.ds:1` 标签变更**：这个 CSS class 是 Google 内部渲染 key，没有任何稳定性保证。

**对 Skill 开发者的意义**：任何生产使用都必须加健康检查层（定期用已知查询验证结果），并设计降级路径。

---

### UNSAID-02: 没有价格货币的强制类型，`price` 是裸 `int`

**证据**：`fast_flights/model.py:56` — `price: int`

价格是一个没有货币单位的裸整数。`Currency` 在查询时可以指定（`fast_flights/querying.py:139`），但返回的 `Flights.price` 只是 `int`，货币信息丢失。

用户必须自己记住"我查询时用的是什么货币"，然后才能理解返回的价格数字。在多货币场景（比如比较不同出发地的票价）中，这会造成无声的数据混淆。

---

### UNSAID-03: `multi-city` 是假功能，但不会报错

**证据**：`fast_flights/pb/flights.proto:27`（注释 "not implemented"）+ `fast_flights/querying.py:129`（存在于 TRIP_LOOKUP）

如果用户传入 `trip="multi-city"`，查询对象会正常构造，HTTP 请求会发出，但返回结果未定义。可能返回空列表，可能返回单程结果，可能抛出 parse 异常——取决于 Google 服务器如何处理这个 trip 值。库不会在任何地方抛出 `NotImplementedError` 或发出警告。

---

### UNSAID-04: `airlines` 过滤参数有服务端限制，文档隐藏在 docs/filters.md

**证据**：`docs/filters.md:30` — "the server side currently ignores the `airlines` parameter added to the FlightData of all the flights which is not the first flight"

对于 round-trip 搜索，只有第一个 `FlightData` 的 `airlines` 过滤生效，回程的 airlines 过滤被服务器静默忽略。这个信息只出现在文档页面的一段长括号注释中，代码里没有任何提示。

---

### UNSAID-05: `primp` 依赖 Rust 二进制，部署环境受限

`primp` 是 Rust 编写的 Python 扩展（maturin），需要预编译二进制。在 Alpine Linux、musl libc 环境（常见于 Docker）、或非标准 CPU 架构（ARM、RISC-V）中可能没有预编译 wheel，需要本地编译 Rust 工具链。README 提到"doesn't even run on the Edge because of configuration errors, missing libraries"正是这类问题——作者自己踩过这个坑。

---

## 对"机票搜索 + 最优路线 Skill"的贡献分析

### 直接可用组件

| 组件 | 价值 | 文件 |
|------|------|------|
| `create_query` + `FlightQuery` | 完整的 Google Flights 查询构造，支持 one-way/round-trip，多 leg | `querying.py:133` |
| `get_flights` | 单次航班搜索，返回 `MetaList[Flights]` | `fetcher.py:47` |
| `Flights` dataclass | 含 price, airlines, flights(list[SingleFlight]), carbon | `model.py:52-58` |
| `SingleFlight` dataclass | 含 from/to airport, departure/arrival datetime, duration(min), plane_type | `model.py:35-43` |
| BrightData integration | 生产级代理绕过，避免 bot detection | `integrations/bright_data.py` |

### 关键能力

1. **多 leg 支持**：`flights: list[FlightQuery]` 支持传多个 leg（这是 multi-city 的数据层基础，即使 trip 枚举未实现，多个 FlightData 本身 proto 支持）
2. **停靠次数过滤**：`FlightQuery.max_stops` 可以限制中转次数，对"最优路线"搜索关键
3. **时长原始数据**：`duration: int (minutes)` 是整数分钟，可直接用于路线比较算法
4. **碳排数据**：`CarbonEmission.emission` + `typical_on_route`，如果 Skill 需要绿色出行维度可用

### Skill 构建建议

```python
# 最优路线搜索的核心模式：并行搜索多个候选路线段
from fast_flights import FlightQuery, Passengers, create_query, get_flights

def search_leg(from_airport: str, to_airport: str, date: str) -> list:
    q = create_query(
        flights=[FlightQuery(date=date, from_airport=from_airport, to_airport=to_airport)],
        seat="economy",
        trip="one-way",
        passengers=Passengers(adults=1),
        max_stops=1,  # 限制中转
    )
    results = get_flights(q)
    return sorted(results, key=lambda f: f.price)  # 按价格排序
```

**注意事项**：
- 不适合做实时价格监控（无 webhook，需轮询；Google 随时可能封 IP）
- round-trip 搜索：两个 FlightQuery 传给同一个 create_query，而不是分两次调用
- 价格无货币单位，Skill 需要在 create_query 时固定 currency 参数并自行记录
- 生产环境必须用 BrightData 或类似代理，否则 IP 会被封

### 与"最优路线"逻辑的接口边界

`fast-flights` 只做**数据获取层**，不做路线优化。Skill 需要在其之上构建：
- 多城市行程规划（对每个 leg 分别调用 `get_flights`，然后组合）
- 价格 vs. 时长 vs. 中转次数的权衡算法
- 出发时间窗口遍历（当前 API 只支持单日搜索，日期范围需要循环调用）
- 结果缓存（避免重复请求同一 leg 触发 bot detection）

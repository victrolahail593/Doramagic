# Soul Extraction: gpt-search-flights

**Project**: Flight-GPT — OpenAI Function Calling + Iranian Flight Search
**Source**: /tmp/gpt-search-flights
**Extracted**: 2026-03-18
**Extractor**: Doramagic Soul Extractor

---

## Stage 0: repo_facts

```json
{
  "project_name": "flight-gpt",
  "author": "Hossein Marzban",
  "runtime": "Deno (v1.x, std@0.191.0)",
  "framework": "Hono 3.2.5",
  "openai_sdk": "openai@3.2.1 (v3 legacy)",
  "gpt_model": "gpt-3.5-turbo-0613",
  "flight_api": "trip.ir (https://gateway.trip.ir/api/LowFareSearch)",
  "http_client": "axios@1.4.0",
  "entry_point": "index.js",
  "routes": [
    "GET /",
    "GET /tickets",
    "POST /gpt/search-flights"
  ],
  "key_files": [
    "index.js",
    "routers/gptSearchFlights.js",
    "routers/getTickets.js",
    "helpers/getTickets.js"
  ],
  "language_support": "multilingual input (Farsi demo shown in README)",
  "domain": "Iranian domestic flights only",
  "one_way_sentinel": "NaN-NaN-NaN (literal string for missing return date)",
  "two_phase_api": true,
  "build_targets": ["windows", "linux", "apple-arm", "apple-intel"]
}
```

---

## Stage 1: Soul Discovery

**核心灵魂一句话**：用 GPT function calling 做自然语言到结构化 API 参数的翻译器——LLM 是意图解析器，不是搜索引擎。

这个项目揭示了一个极其清晰的模式：**GPT 不负责搜索，只负责理解**。用户用任意语言说"我要从德黑兰飞基什岛，23号去26号回"，GPT 把这句话拆解成结构化参数（机场代码、日期格式、单程/往返），然后真正的搜索由 trip.ir 完成。GPT 是翻译层，不是执行层。

这个分工非常干净，也非常有教育价值。

---

## Stage 2: 概念卡片 (CC — Core Concepts)

### CC-01: Function Calling 作为意图解析器

**核心思想**：GPT function calling 的本质是把自然语言意图转换成结构化函数参数，而不是让 LLM 直接执行业务逻辑。

**证据**：
- `routers/gptSearchFlights.js:12-48` — `GPTFunctions` 数组定义了一个函数 `get_flight_tickets`，其 5 个参数（`OriginAirport`, `DestAirport`, `StrDepartDateTime`, `StrArriveDateTime`, `OneWay`）完全映射到后端 API 所需字段
- `routers/gptSearchFlights.js:77-84` — 第一次 GPT 调用设置 `temperature: 0`，这是确定性解析的信号，不是创意生成
- `routers/gptSearchFlights.js:91-98` — GPT 输出 `function_call.arguments` 直接 `JSON.parse()` 后传给真实 API

**本质**：function calling = 结构化意图提取，不是 AI 搜索。

---

### CC-02: 两阶段 Trip.ir API 调用模式

**核心思想**：真实航班搜索 API 需要两次调用——第一次发起搜索获取 SearchId，第二次用 SearchId 取回结果。

**证据**：
- `helpers/getTickets.js:5-6` — 函数签名 `getTickets(InputFunc, SearchId = null)`，SearchId 可选
- `helpers/getTickets.js:6` — `searchURL = TRIP_IR_API + (SearchId ? '?searchId=${SearchId}' : '')`
- `routers/gptSearchFlights.js:101-105` — 明确的两步调用：
  ```js
  const responseTickets0 = await getTickets(inputFunctionParameters);
  const responseTickets = await getTickets(inputFunctionParameters, responseTickets0.SearchId);
  ```
- `routers/getTickets.js:13-14` — 测试路由也遵循同一模式

**本质**：trip.ir 是异步搜索模型（提交 → 轮询），用两次同步调用模拟。

---

### CC-03: 两轮对话闭环（Function → 结果回注）

**核心思想**：function calling 需要两轮 LLM 调用：第一轮提取参数，第二轮把真实数据回注并生成自然语言答案。

**证据**：
- `routers/gptSearchFlights.js:156-168` — 把 assistant 的 function_call 和 function 角色的结果依次追加进 `CompletionMessages`：
  ```js
  CompletionMessages.push({ role: "assistant", content: null, function_call: {...} });
  CompletionMessages.push({ role: "function", name: "get_flight_tickets", content: JSON.stringify(tickets) });
  ```
- `routers/gptSearchFlights.js:171-183` — 第二次 `createChatCompletion` 接收含真实数据的完整 messages 数组
- `routers/gptSearchFlights.js:185` — 最终返回第二轮 LLM 生成的自然语言文本（`message.content`）

**本质**：LLM → 函数 → LLM 这个三步闭环是 function calling 的标准执行模式。

---

### CC-04: System Prompt 的上下文锚定

**核心思想**：assistant role 的开场 prompt 注入了三个关键上下文约束，确保 LLM 在正确域内解析意图。

**证据**：
- `routers/gptSearchFlights.js:59-75` — assistant 消息包含：
  1. 今天的日期（`new Date().toLocaleDateString()`）— 解决相对日期（"下周五"）
  2. 周末是周四周五 — 伊朗日历约定
  3. 所有机场默认在伊朗 — 域限定

**本质**：system context = 约束解析空间，不是提升能力。三行文字把一个通用 LLM 变成一个懂伊朗航班的专家。

---

### CC-05: 数据裁剪作为 Token 预算管理

**核心思想**：从 API 返回的完整响应中只选取 LLM 需要的字段，丢弃其余，防止 token 溢出和幻觉。

**证据**：
- `routers/gptSearchFlights.js:107-152` — `responseTickets.Trips.map()` 手动提取 10 个字段（IATA、名称、时刻、座位、价格），构建精简的 `tickets` 数组
- 原始 API 响应字段远多于此（可从完整 trip.ir 响应推断），但代码只保留用户决策所需信息

**本质**：你喂给 LLM 的数据形状决定了它能说什么。裁剪 = 对 LLM 输出的隐式控制。

---

## Stage 3: 工作流卡片 (WF — Workflows)

### WF-01: 主搜索流程

```
用户自然语言输入 (任意语言)
    ↓
POST /gpt/search-flights [routers/gptSearchFlights.js:50]
    ↓
构建带上下文的 messages 数组 [gptSearchFlights.js:58-75]
    ↓
GPT Round 1: function calling 提取参数 [gptSearchFlights.js:77-84]
    ↓
检测 function_call 响应 [gptSearchFlights.js:91]
    ↓
JSON.parse(arguments) → 结构化参数 [gptSearchFlights.js:92-93]
    ↓
Trip.ir 调用 Round 1: 发起搜索，获取 SearchId [helpers/getTickets.js:5-48]
    ↓
Trip.ir 调用 Round 2: 用 SearchId 取结果 [helpers/getTickets.js:5-48]
    ↓
数据裁剪: 只保留必要字段 [gptSearchFlights.js:107-152]
    ↓
回注 function 结果到 messages [gptSearchFlights.js:156-168]
    ↓
GPT Round 2: 生成自然语言答案 [gptSearchFlights.js:171-183]
    ↓
返回 HTML 文本给用户 [gptSearchFlights.js:185]
```

**总计**: 2 次 LLM 调用 + 2 次 Flight API 调用 = 每次用户请求 4 次外部网络调用

---

### WF-02: 单程/往返判断逻辑

**证据**：`helpers/getTickets.js:8-11`

```
StrArriveDateTime 存在 AND SearchId 存在
    → OneWay = false (往返)
StrArriveDateTime 缺失 OR 第一次调用
    → OneWay = true (单程)
```

**注意**：OneWay 的判断依赖 SearchId 是否存在，不依赖 GPT 返回的 `OneWay` 字段。实际上 GPT 提取的 `OneWay` boolean 在 `helpers/getTickets.js` 中被忽略了，改由本地逻辑重新计算。这是一个潜在的不一致点。

---

## Stage 3.5: 设计决策卡片 (DR — Design Decisions)

### DR-01: 选择 Deno 而非 Node

**决策**：用 Deno 运行时，通过 URL import 直接引用标准库。
**可能原因（INFERENCE）**：Deno 的 `deno compile` 可直接打包成单一可执行文件（4 个平台的 build 脚本），无需 Docker 或 Node 环境，降低分发门槛。
**代价**：`package.json` 里的 `main: "index.js"` 是误导性的（Deno 不用 package.json），与 `openai@3.2.1`（旧版 SDK）混用 npm: 协议，依赖管理有混乱。

**证据**：`package.json:8-13`（build 脚本）、`index.js:1-3`（URL imports）

---

### DR-02: 用 "NaN-NaN-NaN" 作为缺失日期哨兵值

**决策**：单程票的返回日期字段不设为 null 或空字符串，而是 `"NaN-NaN-NaN"`。
**可能原因（INFERENCE）**：trip.ir API 要求该字段存在（不能缺失），但单程场景下无返回日期。`NaN-NaN-NaN` 是开发者找到的"合法但无意义"的占位值。
**风险**：这是一个对 trip.ir API 行为的未文档假设。如果 trip.ir 某天改变对该字段的解析，会静默失败。

**证据**：`helpers/getTickets.js:16`、`routers/gptSearchFlights.js:38-39`（GPT function 描述中明确写了这个哨兵）

---

### DR-03: temperature: 0 + penalty: 0 锁定确定性解析

**决策**：两轮 GPT 调用都设置 `temperature: 0, frequency_penalty: 0, presence_penalty: 0`。
**原因**：第一轮是结构化提取，必须确定性；第二轮是展示结果，数据已固定，创意空间为零。这是正确的。
**证据**：`routers/gptSearchFlights.js:82-84`、`gptSearchFlights.js:175-177`

---

### DR-04: assistant role 而非 system role 作为上下文注入

**决策**：上下文约束（今天日期、伊朗周末、机场默认伊朗）放在第一条 `role: "assistant"` 消息里，而非 `role: "system"`。
**可能原因（INFERENCE）**：可能是开发者对 openai v3 SDK 的 messages 格式不熟悉，或刻意模拟"assistant 开场白"的对话感。
**代价**：system role 的约束力比 assistant role 更强（模型对 system 的遵从优先级更高）。当前设计在对抗性输入下更容易被覆盖。

**证据**：`routers/gptSearchFlights.js:59-75`

---

### DR-05: 错误处理极简（只有一处 catch）

**决策**：整个流程只在第二次 GPT 调用处有 `.catch()`，其余外部调用（trip.ir axios、第一次 GPT 调用）无错误处理。
**风险**：trip.ir 超时或 429 会导致未捕获异常，服务崩溃。
**证据**：`helpers/getTickets.js:42-44`（`console.error` 但无抛出处理）、`routers/gptSearchFlights.js:180-183`（唯一 catch）

---

## Stage 4: UNSAID — 暗坑与未说出的真相

### UNSAID-01: GPT 提取的 OneWay 字段被忽略

`GPTFunctions` 里有 `OneWay: boolean` 参数，GPT 会从自然语言中提取它。但 `helpers/getTickets.js:8-11` 里 OneWay 的判断完全忽略了这个值，改用 `SearchId` 是否存在来判断。

**后果**：用户说"单程票"，GPT 正确提取 `OneWay: true`，但 helpers 里在第二次调用时因为 `StrArriveDateTime` 存在（哨兵值 NaN-NaN-NaN 是字符串，truthy）且 `SearchId` 存在，会把 OneWay 置为 false，可能触发往返搜索。这是一个逻辑 bug。

**证据**：`helpers/getTickets.js:8-11` vs `routers/gptSearchFlights.js:39-46`

---

### UNSAID-02: trip.ir API 未授权使用

README 明确写道："I used trip.ir, I hope they are not get mad at me"（原文如此）。这是未授权抓取（scraping）或使用未公开 API，没有 API key，没有速率限制处理，没有服务条款保障。

**后果**：任何时候 trip.ir 改变 API 结构或添加认证，整个项目立即失效。这不是技术债，是存在性风险。

**证据**：`README.md:10-11`、`helpers/getTickets.js:3`（无 Authorization header）

---

### UNSAID-03: 两阶段 API 调用是异步搜索的同步模拟，有竞态风险

Trip.ir 的两步模式（提交 → SearchId → 取结果）暗示后端是异步处理。代码用顺序 await 假设第二次调用时结果一定就绪，但没有轮询或等待机制。

**后果**：在高负载或慢速搜索场景下，第二次调用可能取到空结果或不完整结果，而代码不会重试，直接把空数据喂给 LLM，LLM 会说"没有找到航班"（幻觉为真）。

**证据**：`routers/gptSearchFlights.js:101-105`（两次 await 顺序调用，无轮询）

---

### UNSAID-04: 只处理了 function_call 路径，未处理 GPT 直接回答的路径

代码检查 `if (result.data.choices[0].message.function_call)` 存在才进入正常流程，否则在第 188 行直接返回 `c.json(result.data.choices[0].message)`。

**后果**：如果用户说"你好"或"谢谢"，GPT 不会触发 function，直接返回 raw message 对象（JSON）而非用户友好的响应。对话能力缺失。

**证据**：`routers/gptSearchFlights.js:186-188`

---

### UNSAID-05: 乘客数量硬编码为 1 成人

无论用户说"我和我太太两个人"还是"一家四口"，API 调用永远是 `NoOfAdults: "1", NoOfChilds: "0", NoOfInfants: "0"`。

**后果**：价格计算错误，座位可用性判断不准。GPT function 的 schema 里也没有乘客数量字段，所以这个信息即使用户提供了也会被丢弃。

**证据**：`helpers/getTickets.js:23-25`（硬编码值）、`routers/gptSearchFlights.js:12-48`（GPTFunctions schema 无乘客字段）

---

### UNSAID-06: 日期处理存在语言/日历歧义

System prompt 说"dates based on Gregorian calendar"，但 README 的 curl 示例用的是"23 and return 26 of this month"（相对日期），GPT 需要结合当天日期计算绝对日期。

**暗坑**：伊朗用波斯历（Solar Hijri），用户可能自然地用波斯历说日期（如"خرداد ۲۳" 即伊朗6月23日，不是公历6月23日）。System prompt 要求 GPT 转换到公历，但 GPT 对波斯历-公历转换的准确性未经验证。

**证据**：`routers/gptSearchFlights.js:63-64`（注入今天公历日期）、`README.md:122-123`（注明日期需用公历）

---

## Stage 5: 对"机票搜索+最优路线 Skill"的贡献

### 可直接复用的模式

**1. Function Schema 设计模板**

`GPTFunctions` 的 5 字段设计（origin, dest, depart_date, return_date, one_way）是机票搜索意图提取的最小完备集。`required` 字段设置也有参考价值（`StrArriveDateTime` 不在 required 里，OneWay 在）。

参考：`routers/gptSearchFlights.js:12-48`

**2. 两轮对话闭环的消息构建模式**

把 `function_call` 追加为 assistant 消息、把 API 结果追加为 `function` 角色消息的顺序，是 function calling 正确实现的样板代码，可直接作为 Doramagic skill 的参考实现。

参考：`routers/gptSearchFlights.js:156-168`

**3. 上下文锚定的三要素**

日期基准 + 域限定（只在某国） + 文化约定（周末定义），三者构成一个完整的上下文锚定模式，适用于任何有地区特殊性的航班搜索场景。

参考：`routers/gptSearchFlights.js:59-75`

**4. 数据裁剪原则**

只把 LLM 需要的字段回注，不回注原始 API 响应，这个原则对 token 预算控制和 LLM 输出质量都有直接影响。

参考：`routers/gptSearchFlights.js:107-152`

---

### 需要修正的设计缺陷（Skill 开发时避免）

| 缺陷 | 修正方向 |
|------|---------|
| OneWay 逻辑 bug | 直接使用 GPT 提取的 OneWay boolean，不用 SearchId 重新判断 |
| 乘客数量缺失 | function schema 增加 `AdultCount`, `ChildCount`, `InfantCount` |
| 无 API 认证 | Skill 必须使用有授权的 flight API（Amadeus / Skyscanner / 航司官方） |
| 两阶段无轮询 | 如果 API 是异步模型，需实现轮询或 webhook 回调 |
| 错误处理缺失 | 每个外部调用需 try/catch + 重试逻辑 + 降级响应 |
| assistant vs system role | 上下文约束放 system role，不放 assistant role |

---

### Skill 架构启发

这个项目验证了一个核心架构原则：

> **LLM 是意图翻译器，Flight API 是执行器，LLM 是结果叙述者。**
> 三者分工清晰，LLM 不做搜索，搜索引擎不做自然语言。

对于 Doramagic 的"机票搜索+最优路线"skill：
- 意图提取层：function calling（参考本项目）
- 搜索层：真实授权 API（需替换 trip.ir）
- 最优路线层：本项目缺失——多段行程的价格/时间权衡需要额外的排序/评分逻辑，LLM 不应该做这个计算
- 叙述层：第二轮 LLM 调用（参考本项目闭环模式）

最优路线的核心难点在本项目中未涉及：如何在多个出发时间/中转方案之间做 Pareto 最优选择（最便宜、最快、最少中转），这需要确定性的排序代码，不能依赖 LLM 判断。

---

*extraction.md — gpt-search-flights — Soul Extractor v0.9*

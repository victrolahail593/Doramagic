# Phase E: 知识综合报告

**Skill**: flight-search (机票搜索 + 最优飞行路线)
**综合日期**: 2026-03-18
**输入来源**: 4 份提取报告 + 社区调研

---

## 1. 公约数（四方共识）

以下知识点在多个来源中独立出现，可信度最高。

### C-01: IATA 机场代码是统一语言

**共识**: 所有航班系统的内部标识统一使用 IATA 三字码（SFO, NRT, PVG）。无论用户输入什么（中文城市名、英文全称、模糊表达），系统内部必须在第一时间转换为 IATA 代码。

**来源**: fast-flights（`FlightQuery.from_airport` = IATA）、gpt-flights（`OriginAirport` = IATA）、社区全部 Skill（统一 IATA 参数）、travel-planner（城市编号映射，本质等价）

**相关度**: 高 -- Skill 参数设计的基石

### C-02: 航班搜索的最小完备参数集

**共识**: 所有实现都收敛到同一组核心参数：出发地、目的地、出发日期、返程日期（可选）、乘客数、舱位、最大中转次数。

**来源**: fast-flights（FlightQuery 5 字段）、gpt-flights（GPTFunctions 5 字段）、社区（统一参数表）

**相关度**: 高 -- 直接定义 Skill 输入规范

### C-03: LLM 是意图翻译器，不是搜索引擎

**共识**: LLM 负责将自然语言转换为结构化搜索参数，真实搜索由 Flight API 执行，LLM 再将结果转化为自然语言答案。三层分工清晰。

**来源**: gpt-flights（核心架构 = LLM→API→LLM 三步闭环）、社区（skill-google-flights 明确"不代替订票"）、Doramagic 原则（"代码说事实，AI 说故事"完美对应）

**相关度**: 极高 -- 直接决定 Skill 架构

### C-04: 不替用户订票

**共识**: 所有 Skill 都明确声明"价格为估算，引导用户自行完成预订"。Skill 提供信息和工具，不替代用户决策。

**来源**: skill-google-flights（明确约束）、FlightClaw（价格追踪但不订票）、Doramagic 产品哲学（"不教用户做事，给他工具"）

**相关度**: 极高 -- 产品设计红线

### C-05: JSON 输出是 Agent 管线的通用接口

**共识**: 面向 AI agent 的 Skill 输出必须是结构化 JSON，Markdown 是给人类看的可选格式。

**来源**: flights-skill（面向 AI agent 的 JSON 输出）、FlightClaw（JSON 追踪数据）、gpt-flights（JSON 裁剪后回注 LLM）、社区（JSON 输出优先规则）

**相关度**: 高 -- 输出格式设计

---

## 2. 打架（分歧与各方立场）

### D-01: 数据源选型 -- 逆向抓取 vs 商业 API

| 立场 | 支持者 | 论据 |
|------|--------|------|
| Google Flights Protobuf 逆向（免费但不稳定） | fast-flights, skill-google-flights, flights-skill | 零成本、数据覆盖全球、无需注册 |
| 商业 API（稳定但付费） | flight-pricer (Duffel), Aerobase, 社区推荐 (Amadeus) | GDS 数据权威、有 SLA、不会突然失效 |
| LLM 直接生成（无数据源） | travel-manager | 零依赖、无 API 成本 |

**综合判断**: 双轨方案。Amadeus 做主数据源（稳定、权威、有免费测试额度），fast-flights 做备用和快速原型验证。LLM 直接生成不可接受（违反"代码说事实"原则）。

### D-02: 多城市路线 -- 算法方案

| 立场 | 支持者 | 论据 |
|------|--------|------|
| Dijkstra 最短路径 | travel-planner | 经典算法，代码简单，小规模图可用 |
| 穷举 + Pareto 过滤 | 社区暗示（无人实现） | 多目标优化需要展示 Pareto 前沿 |
| 贪心最近邻 | travel-planner (UNSAID 建议) | 城市数 >12 时唯一实际可行方案 |

**综合判断**: 分层策略。城市数 <=8 用动态规划/穷举求精确解；>8 用贪心最近邻求近似解。所有方案输出 Pareto 前沿（价格 vs 时长 vs 中转），不做单一"最优"判断。

### D-03: 价格货币处理

| 立场 | 支持者 | 论据 |
|------|--------|------|
| 查询时指定，返回裸数字 | fast-flights | 简单，但丢失货币信息 |
| 统一 CNY | openclaw-travel-planner-skill | 中文用户默认 |
| IP 自动检测 | FlightClaw (fli 库) | 智能，但不可控 |

**综合判断**: Skill 固定使用 CNY，所有价格输出带货币单位。多货币比较场景需要用户明确指定。

---

## 3. 独创知识（每个来源独有的）

### fast-flights 独创

- **Protobuf 逆向工程的完整链路**: `tfs=` 参数 = Base64(Protobuf(Info))，这是零成本访问 Google Flights 数据的核心发现。（CC-01）
- **JavaScript 嵌入数据解析**: `script.ds:1` → `payload[3][0]` 的完整数据路径。（CC-02）
- **浏览器指纹伪装**: `primp` 库在 TLS 层面伪装 Chrome，比 User-Agent 欺骗更深一层。（CC-03）
- **Integration ABC 设计**: 传输层可替换（BrightData 等），解析逻辑与传输解耦。（WF-02）

### travel-planner 独创

- **预算可达性分析**: "给定预算，能到哪些城市"的逆向问题建模，用受约束的 Dijkstra 实现。（CC-02）
- **多目标权重公式**: `score = alpha * price + beta * duration + gamma * stops_penalty`，alpha+beta+gamma=1。（Stage 5.3）
- **中转成本建模缺失的洞察**: "两段 100 块加 12 小时中转不如 180 块直飞"——隐性成本必须显式建模。（UNSAID-05）

### gpt-flights 独创

- **Function Calling 作为意图解析器的完整实现**: GPT temperature=0 + function schema = 确定性意图提取。（CC-01）
- **两轮对话闭环**: function_call→API→function role 回注→第二轮 LLM 生成的消息构建模式。（CC-03）
- **上下文锚定三要素**: 日期基准 + 地域限定 + 文化约定，三行 system prompt 把通用 LLM 变成领域专家。（CC-04）
- **数据裁剪 = Token 预算管理**: 只喂 LLM 需要的字段，控制输出形状。（CC-05）

### 社区调研独创

- **FlightClaw 价格追踪架构**: tracked.json + cron 检查 + 阈值告警的完整设计模式。
- **Aerobase 时差评分**: 将非功能性体验（时差、疲劳）量化为 0-100 分，产品思路新颖。
- **三档预算框架**: 经济/舒适/豪华是中文用户最熟悉的决策框架。（openclaw-travel-planner-skill）
- **六大社区空白识别**: 多城市组合、中文城市名解析、多目标权衡、时区感知、价格趋势、亚太航线优化。

---

## 4. 与用户需求相关度评分

| 需求维度 | 权重 | 最相关来源 | 理由 |
|----------|------|-----------|------|
| 机票搜索（单程/往返） | 高 | fast-flights + 社区 FlightClaw | 完整实现可直接参考 |
| 最优飞行路线规划 | 极高（核心差异化） | travel-planner + 社区空白分析 | 算法骨架来自 travel-planner，社区空白确认市场机会 |
| 自然语言意图解析 | 高 | gpt-flights | function calling 模式可直接复用 |
| 多城市组合优化 | 极高（核心差异化） | travel-planner（算法）+ 社区（空白确认） | 无人实现，最大差异化点 |
| 价格追踪/提醒 | 中 | 社区 FlightClaw | 已有成熟方案，差异化不大 |
| 中文用户适配 | 高 | 社区空白分析 | 中文城市名→IATA 是明确空白 |
| 实时数据质量 | 高 | fast-flights + Amadeus 推荐 | 双轨方案平衡成本和稳定性 |
| OpenClaw 平台适配 | 必要 | 社区 SKILL.md 格式 | 所有 Skill 的通用结构已收敛 |

---

## 5. 知识选择建议

### 采纳（直接进入 SKILL.md）

1. **LLM→API→LLM 三步闭环架构**（gpt-flights CC-01/CC-03）
2. **统一 IATA 参数 + 最小完备参数集**（四方共识 C-01/C-02）
3. **Amadeus 主 + fast-flights 备的双轨数据源**（社区推荐 + fast-flights 能力）
4. **多目标权重公式**（travel-planner Stage 5.3）
5. **价格追踪 tracked.json 模式**（FlightClaw）
6. **上下文锚定三要素**（gpt-flights CC-04，适配中文场景）
7. **数据裁剪原则**（gpt-flights CC-05）
8. **不替用户订票的红线**（四方共识 C-04）

### 借鉴但需改造

1. **Dijkstra 最短路径** → 改为多维权重 + Pareto 前沿（travel-planner CC-01，需重新设计边权）
2. **预算可达性** → 改为"预算内最优行程"而非"可达城市列表"（travel-planner CC-02，需补路径输出）
3. **Function Calling Schema** → 扩展乘客数量 + 中文城市名 + 多城市列表（gpt-flights 缺陷修正）

### 丢弃

1. **D&C 多城市"优化"** — 实质无优化，替换为贪心最近邻或 DP（travel-planner CC-03）
2. **trip.ir 未授权 API** — 存在性风险，替换为 Amadeus 授权 API（gpt-flights UNSAID-02）
3. **LLM 直接生成航班数据** — 违反"代码说事实"原则（travel-manager）
4. **NaN-NaN-NaN 哨兵值** — 脆弱设计，改用 null/undefined（gpt-flights DR-02）
5. **硬编码浏览器版本** — primp chrome_145 会过时（fast-flights UNSAID，通过配置外置解决）

---

*综合报告完成。下一步: Phase F (Skill 组装)*

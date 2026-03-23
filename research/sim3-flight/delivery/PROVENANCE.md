# PROVENANCE.md -- 知识溯源

**Skill**: flight-search v0.1.0
**综合日期**: 2026-03-18
**来源数量**: 4 份提取报告 + 社区调研

---

## 知识来源清单

### 来源 1: fast-flights (v3.0rc1)

| 字段 | 值 |
|------|-----|
| 项目 | AWeirdDev/fast-flights |
| 许可 | MIT |
| 提取文件 | `/research/sim3-flight/flights/extraction.md` |
| 核心贡献 | Protobuf 逆向工程模式、备用数据获取层、Integration ABC 设计 |
| 代码复用 | 无直接代码复用，复用架构模式和 API 知识 |

**具体知识溯源**:

| SKILL.md 位置 | 来自 fast-flights 的知识 | 提取报告引用 |
|---------------|------------------------|-------------|
| 备用数据源设计 | Protobuf 逆向 Google Flights 的完整链路 | CC-01, CC-02, CC-03 |
| BrightData 代理集成 | Integration ABC 允许替换 HTTP 传输层 | WF-02 |
| 暗坑 #2 (multi-city 假功能) | `MULTI_CITY = 3; // not implemented` | DR-03, UNSAID-03 |
| 暗坑 #4 (airlines 过滤 bug) | round-trip 只有去程 airlines 过滤生效 | UNSAID-04 |
| 暗坑 #5 (浏览器版本) | `impersonate="chrome_145"` 硬编码 | INFERENCE-3 |
| 价格无货币单位的处理 | `Flights.price: int` 裸整数 | UNSAID-02 |
| 限制 #4 (JS 路径脆弱性) | `payload[3][0]` 硬编码索引 | UNSAID-01, INFERENCE-2 |

### 来源 2: travel-smart-planner

| 字段 | 值 |
|------|-----|
| 项目 | TravelSmartPlanner2.java (课程项目) |
| 许可 | 未声明（学术项目） |
| 提取文件 | `/research/sim3-flight/travel-planner/extraction.md` |
| 核心贡献 | 路线优化算法骨架、多目标权重公式、UNSAID 分析 |
| 代码复用 | 无直接代码复用（Java→Python 重写），复用算法思路 |

**具体知识溯源**:

| SKILL.md 位置 | 来自 travel-planner 的知识 | 提取报告引用 |
|---------------|--------------------------|-------------|
| 多目标综合评分公式 | `alpha*price + beta*duration + gamma*stops` | Stage 5.3 |
| 精确解 vs 近似解分层 | 城市数 <=8 穷举，>8 贪心 | UNSAID-02, Stage 5.5 |
| 限制 #6 (中转成本未量化) | 隐性中转成本建模缺失 | UNSAID-05 |
| D&C 被丢弃的决策 | D&C 实质无优化（输出=输入顺序） | CC-03, Stage 5.2 |
| 优先队列 Dijkstra 参考 | PQ 版比线性扫描版更适合扩展 | Stage 5.1 |

### 来源 3: gpt-search-flights (Flight-GPT)

| 字段 | 值 |
|------|-----|
| 项目 | Hossein Marzban / flight-gpt |
| 许可 | 未声明 |
| 提取文件 | `/research/sim3-flight/gpt-flights/extraction.md` |
| 核心贡献 | LLM 意图解析模式、两轮对话闭环、上下文锚定、数据裁剪 |
| 代码复用 | 无直接代码复用，复用架构模式 |

**具体知识溯源**:

| SKILL.md 位置 | 来自 gpt-flights 的知识 | 提取报告引用 |
|---------------|----------------------|-------------|
| 架构概览 (LLM→API→LLM) | function calling 三步闭环 | CC-01, CC-03 |
| AI Prompt 契约 1 (意图提取) | temperature=0 确定性解析 + function schema | CC-01, DR-03 |
| AI Prompt 契约 2 (结果叙述) | 两轮对话闭环的消息构建 | CC-03 |
| AI Prompt 契约 3 (数据裁剪) | 只保留用户决策所需字段 | CC-05 |
| 上下文锚定设计 | 日期基准 + 地域限定 + 文化约定 | CC-04 |
| 暗坑 #6 (API 异步搜索) | 两阶段 API 的竞态风险 | UNSAID-03 |

**明确未采纳的知识**:
- trip.ir 未授权 API（UNSAID-02）→ 替换为 Amadeus 授权 API
- NaN-NaN-NaN 哨兵值（DR-02）→ 使用 null
- assistant role 注入上下文（DR-04）→ 改用 system role
- 乘客数量硬编码为 1（UNSAID-05）→ 增加完整乘客参数

### 来源 4: 社区调研报告

| 字段 | 值 |
|------|-----|
| 来源 | 8 个社区项目/Skill 调研 |
| 提取文件 | `/research/sim3-flight/community/extraction.md` |
| 核心贡献 | 社区空白识别、API 选型建议、参数规范共识、价格追踪模式 |

**具体知识溯源**:

| SKILL.md 位置 | 来自社区的知识 | 社区来源 |
|---------------|--------------|---------|
| Amadeus 主 + fast-flights 备的双轨设计 | API 选型比较表 + 推荐理由 | 社区 Section 三 |
| 价格追踪流程 (流程三) | tracked.json + cron 检查 + 阈值告警 | FlightClaw |
| 统一参数结构 | 跨 Skill 参数共识表 | 社区 Section 2.2 |
| "不替用户订票"红线 | 多个 Skill 的共同约束 | 社区 Section 2.3 |
| 多城市路线是核心差异化 | 六大社区空白分析 | 社区 Section 四 |
| 中文城市名→IATA 解析 | 空白 2 识别 | 社区 Section 4.2 |
| 三档预算框架 | 经济/舒适/豪华 | openclaw-travel-planner-skill |
| MCP + CLI 双模式 | 社区通用设计规则 | 社区 Section 2.3 |
| Aerobase 时差评分思路 | 非功能性体验量化 | Aerobase-app |
| SKILL.md 触发描述设计 | 共同触发关键词集 | 社区 Section 2.4 |

---

## 许可证汇总

| 来源 | 许可 | 风险 |
|------|------|------|
| fast-flights | MIT | 低 -- 允许任何用途 |
| travel-smart-planner | 未声明 | 无 -- 未使用其代码，仅参考算法思路（算法思路不受版权保护） |
| gpt-search-flights | 未声明 | 无 -- 未使用其代码，仅参考架构模式 |
| 社区 Skills | 各异（MIT 为主） | 低 -- 未直接复用代码 |
| Amadeus API | 商业 API TOS | 需遵守 Amadeus Self-Service API 使用条款 |

**结论**: 本 Skill 不包含任何来源的直接代码复用。所有知识均为架构模式、算法思路和设计决策层面的借鉴，不存在许可证合规风险。

---

## 综合决策追溯表

对于 SKILL.md 中的每个关键设计决策，追溯其知识来源和决策理由:

| 设计决策 | 最终选择 | 知识来源 | 被否决的备选方案 | 否决理由 |
|----------|---------|---------|----------------|---------|
| 数据源 | Amadeus主+fast-flights备 | 社区推荐 + fast-flights能力 | Duffel (无免费层), Skyscanner (API 停止), LLM 生成 (违反原则) | 成本/稳定性/原则 |
| 路线优化算法 | 穷举(<=8) + 贪心(>8) | travel-planner算法+UNSAID | D&C (travel-planner 的假实现) | 实质无优化 |
| 意图解析方式 | LLM function calling | gpt-flights CC-01 | 正则匹配, 关键词模板 | 无法处理自然语言多样性 |
| 排序方式 | Pareto 前沿 | travel-planner 5.3 + 社区空白3 | 单维排序 | 多维度权衡是核心差异化 |
| 货币处理 | 固定 CNY + 显式标注 | fast-flights UNSAID-02 教训 | 裸数字无单位 | 数据混淆风险 |
| 缓存策略 | 4小时 TTL | fast-flights 使用建议 | 无缓存 / 永久缓存 | 价格时效性 vs API 成本平衡 |
| 价格追踪 | tracked.json + cron | FlightClaw 完整模式 | 无持久化 / 数据库 | 简单可靠，MVP 足够 |

---

*溯源报告完成。每一条 SKILL.md 中的知识都可追溯到具体来源和证据。*

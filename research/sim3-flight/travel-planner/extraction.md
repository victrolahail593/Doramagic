# Soul Extractor — travel-smart-planner

**项目路径**: /tmp/travel-smart-planner
**提取日期**: 2026-03-18
**提取模型**: claude-sonnet-4-6
**目标 skill**: 机票搜索 + 最优飞行路线

---

## Stage 0: repo_facts（确定性提取）

| 字段 | 值 |
|------|-----|
| 语言 | Java（单文件） |
| 入口 | TravelSmartPlanner2.java |
| 规模 | 219 行，1 个 public class，1 个 inner class `Graph` |
| 数据结构 | 邻接矩阵 `int[6][6]`，固定 6 个节点 |
| 算法数量 | 3 个（Dijkstra / Greedy BFS / Divide-and-Conquer） |
| 领域 | 孟加拉国六城市地面路线（非航班） |
| 交互方式 | 控制台 Scanner 菜单 |
| 外部依赖 | 无（纯 JDK） |
| 边权语义 | 整型"距离/费用"，无单位说明 |
| 图类型 | 无向图（addEdge 双向写入），稀疏（8 条边 / 15 可能最大边） |

**城市编号**（`TravelSmartPlanner2.java:5`）:
```
0=Rajshahi, 1=Sylhet, 2=Chittagong, 3=Barishal, 4=Khulna, 5=Dhaka
```

**硬编码图结构**（`TravelSmartPlanner2.java:150-157`）:
```java
graph.addEdge(0, 1, 9);   // Rajshahi <-> Sylhet      weight=9
graph.addEdge(1, 2, 6);   // Sylhet <-> Chittagong    weight=6
graph.addEdge(2, 5, 15);  // Chittagong <-> Dhaka     weight=15
graph.addEdge(5, 4, 7);   // Dhaka <-> Khulna         weight=7
graph.addEdge(5, 3, 10);  // Dhaka <-> Barishal       weight=10
graph.addEdge(4, 3, 9);   // Khulna <-> Barishal      weight=9
graph.addEdge(3, 2, 11);  // Barishal <-> Chittagong  weight=11
graph.addEdge(0, 5, 2);   // Rajshahi <-> Dhaka       weight=2
```

---

## Stage 1: 灵魂发现（Soul Discovery）

### 核心设计意图

这个项目展示了三种经典算法在同一图问题上的不同用途切割：

1. **Dijkstra = 单目标最短路径**：给定 source/destination，输出最优唯一路径。
2. **Greedy BFS = 预算可达性探索**：给定 source/budget，输出"能到达的所有城市集合"。
3. **Divide-and-Conquer = 多城市排序拼接**：给定城市列表，输出固定顺序遍历。

三者解决的是**不同维度的同一问题**：
- Dijkstra：我去哪里最省？（点对点最优）
- Greedy：我的预算能到哪些地方？（预算约束下的可达集）
- D&C：我要去这几个地方，顺序怎么排？（序列规划）

### 最重要的发现（WHY）

**为什么用邻接矩阵而非邻接表？**
6 个节点的图用邻接矩阵（6×6=36 单元格）是正确选择——节点少、查询 O(1)。若扩展到数百城市，邻接矩阵会浪费内存，应换邻接表。这是一个**规模敏感型设计决策**，当前代码无法扩展。

**为什么 Greedy Budget 算法实质是 Dijkstra 变体？**
`planTripWithinBudget`（`TravelSmartPlanner2.java:81-113`）使用了 `PriorityQueue`，其核心逻辑与 Dijkstra 完全相同，区别仅在于：
- Dijkstra：求到达所有点的最小成本，输出到达指定点的路径。
- Budget Greedy：求到达所有点的最小成本，过滤掉超出 budget 的点，输出可达集合（无路径）。

这意味着命名为"Greedy"是**误导性标签**，实质是受约束的 Dijkstra。

**为什么 Divide-and-Conquer 是空壳？**
`divideAndConquerRoute`（`TravelSmartPlanner2.java:131-143`）做的事情是：将输入数组递归拆分再拼接，输出结果**与输入顺序完全相同**。没有任何优化。这是一个教学演示，不是真正的路线优化。真正的多城市优化是 TSP（旅行商问题），需要不同算法（如贪心最近邻、动态规划、遗传算法）。

---

## Stage 2: 结构化知识卡片

### CC-01: Dijkstra 最短路径实现

**类型**: Core Concept
**证据**: `TravelSmartPlanner2.java:27-50`

**事实**:
- 使用 `boolean[] visited` + 线性扫描 `findMinVertex` 实现，时间复杂度 O(V²)。
- 不使用优先队列，适合小图（V≤20）。
- `parent[]` 数组记录路径前驱，栈回溯还原路径（`TravelSmartPlanner2.java:69-76`）。
- 终止条件：`findMinVertex` 返回 -1 即无未访问节点（`TravelSmartPlanner2.java:37`）。

**WHY**: O(V²) Dijkstra 在密集小图上常数因子小于优先队列版本，代码更简单。6 个城市的场景完全合理。

---

### CC-02: 预算过滤的 Dijkstra（误称 Greedy）

**类型**: Core Concept
**证据**: `TravelSmartPlanner2.java:81-113`

**事实**:
- 使用 `PriorityQueue<int[]>`（最小堆），按累计成本排序。
- 松弛条件增加预算约束：`newCost <= budget && newCost < cost[neighbor]`（`TravelSmartPlanner2.java:106`）。
- 不记录路径，只输出"可到达的城市 + 最低成本"。
- 起点城市本身不输出（`TravelSmartPlanner2.java:99`）。

**UNSAID（暗坑）**: 输出没有说明是否为"最低成本"——用户看到的价格是从 source 到该城市的**最短路成本**，而非"这条路线的机票价格"。两者在实际场景中完全不同。

---

### CC-03: 假 D&C 路线拼接

**类型**: Core Concept
**证据**: `TravelSmartPlanner2.java:131-143`

**事实**:
- 递归将数组二分，左右递归后合并——输出顺序与输入顺序**完全相同**。
- `totalCost` 直接读取邻接矩阵 `adjacencyMatrix[from][to]`（`TravelSmartPlanner2.java:124`），若两城市无直连边则返回 `INF`（Integer.MAX_VALUE），导致整数溢出累加出现负数结果。
- 没有任何排列优化逻辑。

**WHY（INFERENCE）**: 作者可能对 D&C 的适用场景理解有限，将"递归拆分"误认为就是"分治优化"。真正的 D&C 应在合并阶段做优化决策，而非简单拼接。

---

### WF-01: 用户交互流程

**类型**: Workflow
**证据**: `TravelSmartPlanner2.java:159-215`

```
程序启动
  → 显示菜单（4 选项）
  → 用户输入数字
  → case 1: 输入 source + destination → dijkstra() → 打印路径+距离
  → case 2: 输入 starting city + budget → planTripWithinBudget() → 打印可达城市列表
  → case 3: 输入城市数量 → 逐个输入城市编号 → multiCityTravelPlan() → 打印顺序+总费用
  → case 4: 退出
```

**关键约束**: 全部使用城市**编号**输入（0-5），非名称。无输入验证，越界输入直接 ArrayIndexOutOfBoundsException。

---

### WF-02: 图初始化流程

**类型**: Workflow
**证据**: `TravelSmartPlanner2.java:146-157`

```
Graph 构造 → 邻接矩阵全填 INF，对角线填 0
  → 8 次 addEdge 调用（双向）
  → 图固化，运行时不可修改
```

**INFERENCE**: 设计上图是静态的，没有"动态添加城市/航线"的机制。

---

### DR-01: 多城市路由中的 INF 溢出陷阱

**类型**: Dark Reality
**证据**: `TravelSmartPlanner2.java:124`

```java
totalCost += adjacencyMatrix[from][to];
```

若用户输入的城市序列中存在无直连边的相邻城市对（如 Rajshahi→Sylhet→Barishal，其中 Sylhet→Barishal=INF），`totalCost` 会加上 `Integer.MAX_VALUE`，造成整数溢出，输出错误负数。程序不会报错，用户会看到"Total travel cost: -1234567890"之类的荒谬结果。

**严重程度**: 高。直接影响用户看到的数字正确性。

---

### DR-02: 算法命名误导

**类型**: Dark Reality
**证据**: `TravelSmartPlanner2.java:80` vs `TravelSmartPlanner2.java:81-113`

`planTripWithinBudget` 注释写"Greedy Algorithm"，实现却是带预算过滤的 Dijkstra（优先队列+松弛）。Greedy 算法在路径规划中通常指"每步选局部最优而不回头"，而这里的实现有全局状态追踪（`cost[]` 数组）和重复入队处理（`visited` 去重）。

**对 skill 的影响**: 如果参考此代码实现"greedy 预算规划"，可能会混淆算法语义，导致错误设计决策。

---

### DR-03: 图数据完全硬编码

**类型**: Dark Reality
**证据**: `TravelSmartPlanner2.java:5`, `TravelSmartPlanner2.java:150-157`

城市列表和边权重均为编译时常量，无配置文件、无 API 接入、无数据库。扩展到新城市需修改源码重编译。

**对实际航班 skill 的致命约束**: 航班数据本质上是实时变化的（价格每秒变动）。这种硬编码架构与实际需求完全不兼容，需要完全重新设计数据层。

---

## Stage 3.5: INFERENCE 标记汇总

以下结论无直接代码证据，基于代码模式推断：

| # | 推断内容 | 依据 |
|---|---------|------|
| I-1 | 项目为算法课程作业 | 三算法强行对应三功能，无实际业务需求驱动；有 .pptx 和 project_report.pdf |
| I-2 | 作者对 TSP 问题不熟悉 | D&C 实现无任何路径优化，仅做数组拼接 |
| I-3 | 边权语义为"距离"而非"价格" | 权重值（2、6、7、9 等）与孟加拉城际机票价格数量级不符 |
| I-4 | 代码可能从网络参考简化而来 | Dijkstra 实现规范，但 D&C 与预期功能严重不匹配 |

---

## Stage 4: UNSAID 暗坑（对机票 skill 的警告）

### UNSAID-01: "最短路径"不等于"最便宜机票"

图的边权是静态整数，而实际机票价格是：
- 时间相关（提前购票 vs 临时购票）
- 舱位相关（经济/商务/头等）
- 供需相关（节假日涨价）
- 中转相关（直飞 vs 经停，价格可能反转）

Dijkstra 只能处理静态权重图，无法应对多维动态定价。直接套用会给用户错误的"最优"答案。

### UNSAID-02: 多城市优化是 NP-Hard 问题

真正的多城市路线优化是旅行商问题（TSP），NP-Hard。本项目的 D&C 实现实质上根本没有做任何优化——它只是按用户输入顺序输出。实际 skill 需要明确承认：

- 城市数 ≤ 12：可用动态规划精确求解
- 城市数 > 12：需要启发式算法（贪心最近邻、模拟退火、遗传算法）
- 城市数 > 20：实际产品通常限制数量或只给近似解

### UNSAID-03: "Budget Reachability" 不等于 "行程规划"

`planTripWithinBudget` 告诉用户"在预算内能到哪些城市"，但没有告诉用户"如何设计一个行程让所有想去的城市都在预算内"。前者是可达性分析，后者是约束优化问题。两者差距巨大，用户真实需求通常是后者。

### UNSAID-04: 无路径输出的预算模式是残缺产品

当 `planTripWithinBudget` 告诉用户"Chittagong: cost 21"时，用户不知道走的是哪条路线。实际 skill 必须同时输出路径，否则用户无法订票。这是信息残缺导致的可用性缺陷。

### UNSAID-05: 中转成本模型缺失

现有图只有"城市间直连边"，没有"中转机场停留成本"（时间成本、住宿、转机费）。两段 100 块的票加上 12 小时中转不如一张 180 块的直飞票。这个隐性成本在图模型中完全不存在。

---

## Stage 5: 对"机票搜索 + 最优路线 skill"的贡献分析

### 5.1 可直接借鉴的算法逻辑

| 算法 | 代码位置 | 适用性 | 迁移难度 |
|------|---------|--------|---------|
| Dijkstra 核心（松弛 + 回溯路径） | `java:27-78` | 高：静态价格图的最短路 | 低（直接翻译） |
| 优先队列版 Dijkstra（预算版） | `java:81-113` | 高：实时价格图的 Dijkstra | 低（已是优化版） |
| parent[] 路径回溯 | `java:62-78` | 高：所有最短路 skill 都需要 | 极低 |

**关键结论**: 优先队列版（`planTripWithinBudget`）比线性扫描版（`dijkstra`）更适合扩展到大城市网络，应优先使用前者的模式。

### 5.2 必须重新设计的部分

| 问题 | 原因 | 替代方案 |
|------|------|---------|
| 硬编码图数据 | 航班数据实时变化 | 接入 Amadeus/Skyscanner API，动态构建图 |
| 单一整型边权 | 机票有价格+时间+中转次数多维度 | 边权改为对象（price, duration, stops） |
| D&C 多城市"优化" | 实质上没有优化 | 用贪心最近邻（小规模）或限制城市数量 |
| 无输入验证 | 越界崩溃 | 城市名称匹配 + 范围检查 |
| 控制台交互 | OpenClaw 是消息驱动 | 改为函数接口，输入/输出为 JSON/文本 |

### 5.3 多目标优化的设计建议（来自 UNSAID 分析）

实际"最优路线"需要三维权重：
```
flight_score = α × price_normalized + β × duration_normalized + γ × stops_penalty
```

其中 α + β + γ = 1，用户可通过偏好设置调整（"最便宜"/ "最快"/ "直飞优先"）。

Dijkstra 在多维权重下仍然适用，但需要将 `comparingInt` 改为自定义比较器，对综合 score 排序。

### 5.4 架构迁移路线图（面向 OpenClaw skill）

```
[用户输入] 出发城市 + 目的城市 + 日期 + 偏好（价格/时间/中转）
    ↓
[API 层] Amadeus Flight Offers Search API（实时数据）
    ↓
[图构建] 动态构建航班图（节点=城市，边=航班，权=综合 score）
    ↓
[算法层]
  - 直飞：直接查 API，无需图算法
  - 多城市：Dijkstra（城市数≤15）或贪心最近邻（城市数>15）
    ↓
[结果格式化] 路径 + 每段价格 + 总价 + 总时长 + 中转说明
    ↓
[OpenClaw 输出] Markdown 格式，含"立即搜索"跳转链接
```

### 5.5 最高价值洞察（排序）

1. **优先队列 Dijkstra 是核心算法骨架**，直接可用，迁移成本低。
2. **多城市优化不要碰 D&C**，用贪心最近邻 + 城市数限制（≤8）是实际产品合理边界。
3. **预算模式需要改为"行程规划"而非"可达性列表"**，这是用户真实需求和现有实现之间最大的鸿沟。
4. **中转成本建模**是这类项目普遍缺失的，加入后是显著差异化竞争点。
5. **边权必须多维化**，否则"最优路线"对用户毫无意义（最短距离≠最好选择）。

---

## 附：repo_facts.json（结构化）

```json
{
  "project": "travel-smart-planner",
  "language": "Java",
  "entry_point": "TravelSmartPlanner2.java",
  "loc": 219,
  "graph_model": {
    "type": "undirected weighted",
    "representation": "adjacency_matrix",
    "nodes": 6,
    "edges": 8,
    "weight_semantics": "unknown (distance or cost, no unit)"
  },
  "algorithms": [
    {
      "name": "Dijkstra",
      "method": "dijkstra(int startVertex, int endVertex)",
      "line": "27-50",
      "variant": "linear_scan_O(V^2)",
      "output": "shortest distance + path"
    },
    {
      "name": "Budget-Filtered Dijkstra",
      "label_in_code": "Greedy Algorithm",
      "method": "planTripWithinBudget(int startVertex, int budget)",
      "line": "81-113",
      "variant": "priority_queue_O((V+E)logV)",
      "output": "reachable city set with minimum costs"
    },
    {
      "name": "Array-Split Passthrough",
      "label_in_code": "Divide-and-Conquer",
      "method": "multiCityTravelPlan(int[] citiesToVisit)",
      "line": "116-143",
      "variant": "no_optimization",
      "output": "input order preserved, total direct cost"
    }
  ],
  "bugs": [
    {
      "id": "BUG-01",
      "location": "line:124",
      "description": "INF + INF integer overflow in totalCost accumulation for disconnected city pairs"
    }
  ],
  "design_constraints": [
    "hardcoded graph (no dynamic data)",
    "console I/O only",
    "no input validation",
    "6 cities fixed"
  ],
  "transferable_to_flight_skill": {
    "priority_queue_dijkstra": "YES - direct port",
    "path_reconstruction": "YES - direct port",
    "budget_filtering": "YES - with modification",
    "multi_city_dc": "NO - replace entirely",
    "graph_data": "NO - replace with API"
  }
}
```

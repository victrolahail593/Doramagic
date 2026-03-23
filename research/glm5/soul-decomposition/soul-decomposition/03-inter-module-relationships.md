# 模块间关系建模研究报告

研究日期: 2026-03-10 | 模型: GLM-5

---

## 一、关系类型分类

模块间关系是理解系统架构的核心。基于软件架构理论和实际项目分析，我们将关系分为以下类型：

### 1.1 依赖关系维度

| 类型 | 定义 | 特征 | 知识流动 |
|------|------|------|----------|
| **调用依赖** | 模块A直接调用模块B的函数/方法 | 同步、显式、编译时可检测 | A→B（A需要知道B的接口） |
| **继承依赖** | 模块A继承模块B的类或接口 | 强耦合、层次结构、is-a关系 | B→A（子类继承父类知识） |
| **组合依赖** | 模块A包含模块B的实例 | 生命周期绑定、has-a关系 | B→A（组件向容器提供能力） |
| **接口依赖** | 模块A实现模块B定义的接口 | 解耦、多态、可替换 | B→A（接口定义行为契约） |
| **事件依赖** | 模块A发布事件，模块B订阅 | 异步、松耦合、运行时绑定 | A→B（发布者定义事件语义） |
| **配置依赖** | 模块A依赖模块B的配置输出 | 外部化、环境相关 | B→A（配置决定行为） |
| **数据依赖** | 模块A和B共享数据结构 | 结构耦合、schema绑定 | 双向（共享知识模型） |
| **时序依赖** | 模块A必须在模块B之前执行 | 流程约束、编排逻辑 | 隐式（流程知识） |

### 1.2 关系方向性

```
                    ┌─────────────────────────────────────┐
                    │           Knowledge Flow            │
                    │                                     │
    ┌───────────────┼─────────────────────────────────────┼───────────────┐
    │               │                                     │               │
    │   UPSTREAM    │         ← KNOWLEDGE SOURCE ←        │   DOWNSTREAM  │
    │   (Provider)  │                                     │   (Consumer)  │
    │               │         → CONTROL FLOW →            │               │
    │               │                                     │               │
    │               │         ← DATA FLOW ←               │               │
    │               │                                     │               │
    └───────────────┴─────────────────────────────────────┴───────────────┘
```

**关键洞察**：
- 控制流和知识流方向相反
- 数据流取决于调用模式（push/pull）
- 知识流动决定了"谁需要理解谁"

### 1.3 DDD限界上下文视角

从领域驱动设计角度，模块间关系可映射为：

| DDD概念 | 对应关系类型 | 特点 |
|---------|--------------|------|
| 共享内核 | 数据依赖 | 双向强耦合 |
| 客户-供应商 | 调用依赖 | 下游主导需求 |
| 遵奉者 | 调用依赖 | 上游主导设计 |
| 防腐层 | 接口依赖 + 适配器 | 隔离外部模型 |
| 开放主机服务 | 接口依赖 | 公开标准化API |
| 发布语言 | 事件依赖 + 数据依赖 | 异步解耦通信 |

---

## 二、知识流动模型

### 2.1 知识的定义

在模块上下文中，"知识"指的是：

```
知识 = 接口语义 + 行为约定 + 隐式假设 + 领域模型
```

**组成部分**：
1. **接口语义**：参数含义、返回值约定、副作用说明
2. **行为约定**：前置条件、后置条件、不变量
3. **隐式假设**：性能特性、线程安全、资源管理
4. **领域模型**：业务概念、状态机、验证规则

### 2.2 知识流动层次

```
┌─────────────────────────────────────────────────────────────────┐
│                      KNOWLEDGE FLOW LAYERS                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Layer 4: META-KNOWLEDGE (Why)                                 │
│  ├── 设计意图、架构决策、trade-off理由                          │
│  └── 通常在注释、文档、ADR中                                    │
│                                                                 │
│  Layer 3: DOMAIN KNOWLEDGE (What)                              │
│  ├── 业务概念、领域模型、状态转换                               │
│  └── 嵌入在数据结构、命名、方法签名中                          │
│                                                                 │
│  Layer 2: BEHAVIORAL KNOWLEDGE (How)                           │
│  ├── 调用协议、错误处理、资源管理                              │
│  └── 体现在API设计、异常类型、生命周期钩子                     │
│                                                                 │
│  Layer 1: STRUCTURAL KNOWLEDGE (Form)                          │
│  ├── 类型定义、接口签名、数据结构                              │
│  └── 编译器可验证，最容易被提取                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 知识流动模式

#### 模式1: 瀑布式流动
```
[A] →→→ [B] →→→ [C] →→→ [D]
 ↓      ↓      ↓      ↓
知识单向传递，下游不感知上游
典型：管道架构、编译器各阶段
```

#### 模式2: 辐射式流动
```
        ┌──→ [Consumer1]
        │
[Core] ─┼──→ [Consumer2]
        │
        └──→ [Consumer3]
        
核心模块向外辐射知识
典型：框架核心、领域模型
```

#### 模式3: 闭环式流动
```
[A] ←→ [B]
 ↑      ↓
 ↓      ↑
[C] ←→ [D]

知识在闭环中循环迭代
典型：事件循环、Actor模型
```

#### 模式4: 分层式流动
```
┌─────────────────────────────────┐
│      Presentation Layer         │  Layer 3
├─────────────────────────────────┤
│       Business Layer            │  Layer 2
├─────────────────────────────────┤
│       Data Layer                │  Layer 1
└─────────────────────────────────┘

        ↓ 知识逐层下钻 ↓
        ↑ 依赖逐层上报 ↑
```

### 2.4 知识流动度量

| 度量指标 | 计算方法 | 意义 |
|----------|----------|------|
| **知识传递深度** | 从源头到消费者的路径长度 | 理解成本 |
| **知识扇出** | 一个模块被多少模块依赖 | 影响范围 |
| **知识扇入** | 一个模块依赖多少模块 | 复杂度 |
| **知识耦合度** | 共享知识量 / 总知识量 | 解耦难度 |
| **知识新鲜度** | 最后更新时间、变更频率 | 维护优先级 |

---

## 三、接口契约提取

### 3.1 契约的定义

```
契约 = 接口 + 语义 + 保证 + 责任

┌─────────────────────────────────────────────────────────┐
│                    CONTRACT ANATOMY                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ┌─────────────┐    ┌─────────────┐                   │
│   │  STRUCTURE  │    │ SEMANTICS   │                   │
│   │  (形式)     │    │ (语义)      │                   │
│   │             │    │             │                   │
│   │ • 类型签名  │    │ • 参数含义  │                   │
│   │ • 参数列表  │    │ • 返回语义  │                   │
│   │ • 返回类型  │    │ • 副作用    │                   │
│   └─────────────┘    └─────────────┘                   │
│                                                         │
│   ┌─────────────┐    ┌─────────────┐                   │
│   │ GUARANTEES  │    │LIABILITIES  │                   │
│   │ (保证)      │    │ (责任)      │                   │
│   │             │    │             │                   │
│   │ • 前置条件  │    │ • 调用责任  │                   │
│   │ • 后置条件  │    │ • 错误处理  │                   │
│   │ • 不变量    │    │ • 资源管理  │                   │
│   └─────────────┘    └─────────────┘                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3.2 API契约提取方法

#### 方法1: 静态分析提取

```yaml
# 从代码静态分析
api_contract:
  name: "UserService.createUser"
  signature:
    params:
      - name: userDto
        type: CreateUserDto
        required: true
      - name: options
        type: CreateUserOptions
        required: false
        default: {}
    returns:
      type: Promise<User>
      success: User
      error: UserCreationError[]
  
  semantic_hints:
    - "Creates a new user with hashed password"
    - "Sends welcome email asynchronously"
    - "Requires ADMIN role"
  
  guarantees:
    precondition: "userDto.email is unique"
    postcondition: "User is persisted, email is queued"
    invariant: "Password is never stored in plain text"
  
  liabilities:
    caller: "Must validate email format before calling"
    callee: "Must rollback on email service failure"
```

#### 方法2: 测试用例推断

```
从测试代码推断契约：

┌────────────────────────────────────────────────┐
│                TEST → CONTRACT                 │
├────────────────────────────────────────────────┤
│                                                │
│  Given (前置条件)                              │
│    └─→ 提取 precondition                       │
│                                                │
│  When (操作)                                   │
│    └─→ 提取 signature + semantic               │
│                                                │
│  Then (断言)                                   │
│    └─→ 提取 postcondition + invariant          │
│                                                │
│  Error Cases                                   │
│    └─→ 提取 error contract                     │
│                                                │
└────────────────────────────────────────────────┘
```

#### 方法3: 运行时监控提取

```python
# 运行时契约发现
class ContractDiscovery:
    def __init__(self):
        self.observed_inputs = []
        self.observed_outputs = []
        self.observed_errors = []
    
    def record_call(self, inputs, outputs, errors):
        self.observed_inputs.append(inputs)
        self.observed_outputs.append(outputs)
        if errors:
            self.observed_errors.append(errors)
    
    def infer_contract(self):
        return {
            "input_schema": self._infer_schema(self.observed_inputs),
            "output_schema": self._infer_schema(self.observed_outputs),
            "error_patterns": self._cluster_errors(self.observed_errors),
            "call_frequency": len(self.observed_inputs)
        }
```

### 3.3 事件契约提取

```yaml
# 事件契约定义
event_contract:
  name: "UserCreated"
  
  schema:
    type: object
    properties:
      userId:
        type: string
        format: uuid
      email:
        type: string
        format: email
      createdAt:
        type: string
        format: iso8601
    required: [userId, email, createdAt]
  
  metadata:
    source: "user-service"
    version: "1.0.0"
    topic: "user.events"
    
  semantic:
    description: "Emitted after successful user registration"
    idempotency: true
    ordering: "per-userId"
    
  guarantees:
    - "Emitted exactly once per user creation"
    - "userId is globally unique"
    - "createdAt reflects server time"
    
  subscribers_must:
    - "Handle duplicate events (idempotency)"
    - "Not depend on event ordering across users"
```

### 3.4 数据契约提取

```yaml
# 数据契约（共享数据结构）
data_contract:
  name: "User"
  schema:
    type: object
    properties:
      id:
        type: string
        format: uuid
        description: "Unique identifier"
      email:
        type: string
        format: email
        description: "Primary contact email"
      status:
        type: enum
        values: [active, suspended, deleted]
        default: active
      
  ownership:
    primary_owner: "user-service"
    readers: ["order-service", "notification-service"]
    writers: ["user-service"]
    
  lifecycle:
    created_by: "user-service"
    mutable_fields: ["email", "status"]
    immutable_fields: ["id"]
    
  events:
    on_create: "UserCreated"
    on_update: "UserUpdated"
    on_delete: "UserDeleted"
```

### 3.5 契约提取优先级

| 来源 | 优先级 | 完整性 | 准确性 | 自动化难度 |
|------|--------|--------|--------|------------|
| 类型定义 | P0 | 结构层 | 高 | 低 |
| 测试用例 | P0 | 行为层 | 高 | 中 |
| 文档注释 | P1 | 语义层 | 中 | 中 |
| 运行时监控 | P1 | 全层 | 中 | 中 |
| 示例代码 | P2 | 行为层 | 低 | 低 |
| README/ADR | P2 | 元层 | 低 | 高 |

---

## 四、关系强度量化

### 4.1 量化维度框架

```
┌─────────────────────────────────────────────────────────────────┐
│                   COUPLING STRENGTH MODEL                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    COUPLING INTENSITY                           │
│                         ↑                                       │
│    STRONG ──────────────────────────────────────► WEAK          │
│                                                                 │
│    ┌─────────────────────────────────────────────────────────┐  │
│    │                                                         │  │
│    │  LEGAL COUPLING    │    KNOWLEDGE COUPLING              │  │
│    │  (编译器强制)       │    (运行时推断)                    │  │
│    │                     │                                    │  │
│    │  • 继承 ████████   │    • 调用频率 ████                 │  │
│    │  • 实现 ███████    │    • 数据共享 ███                  │  │
│    │  • 组合 ██████     │    • 配置依赖 ██                   │  │
│    │  • 调用 █████      │    • 事件订阅 █                   │  │
│    │                     │                                    │  │
│    └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│    CHANGE PROPAGATION RISK                                      │
│                         ↑                                       │
│    HIGH RISK ──────────────────────────────► LOW RISK          │
│                                                                 │
│    • 共享可变状态  ████████                                    │
│    • 循环依赖      ███████                                     │
│    • 紧密时序      ██████                                       │
│    • 接口变更      █████                                        │
│    • 数据结构变更  ████                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 量化公式

#### 4.2.1 基础耦合度计算

```
Coupling(A→B) = α × Structural + β × Behavioral + γ × Data + δ × Temporal

其中：
  Structural  = 类型依赖深度 × 接口暴露面
  Behavioral  = 调用频率 × 调用复杂度
  Data        = 共享数据量 × 数据耦合紧密度
  Temporal    = 执行顺序依赖度

权重建议：
  α = 0.3  (结构耦合影响长期维护)
  β = 0.3  (行为耦合影响运行时)
  γ = 0.25 (数据耦合影响一致性)
  δ = 0.15 (时序耦合影响测试和调试)
```

#### 4.2.2 综合关系强度

```python
def calculate_coupling_strength(module_a, module_b, codebase):
    """计算模块间耦合强度"""
    
    # 1. 结构耦合（静态分析）
    structural = calculate_structural_coupling(module_a, module_b, codebase)
    
    # 2. 行为耦合（动态分析）
    behavioral = calculate_behavioral_coupling(module_a, module_b, codebase)
    
    # 3. 数据耦合
    data = calculate_data_coupling(module_a, module_b, codebase)
    
    # 4. 时序耦合
    temporal = calculate_temporal_coupling(module_a, module_b, codebase)
    
    # 加权综合
    total = (
        0.30 * structural +
        0.30 * behavioral +
        0.25 * data +
        0.15 * temporal
    )
    
    return {
        "total": total,
        "breakdown": {
            "structural": structural,
            "behavioral": behavioral,
            "data": data,
            "temporal": temporal
        }
    }
```

#### 4.2.3 详细计算方法

```python
def calculate_structural_coupling(module_a, module_b, codebase):
    """结构耦合计算"""
    
    # 类型依赖深度
    type_dependency_depth = calculate_type_dependency_depth(
        module_a, module_b, codebase
    )
    
    # 接口暴露面（多少API被外部使用）
    interface_exposure = len(get_used_interfaces(module_b, module_a))
    
    # 继承深度（如果是继承关系）
    inheritance_depth = get_inheritance_depth(module_a, module_b)
    
    # 组合紧密度
    composition_tightness = get_composition_tightness(module_a, module_b)
    
    return normalize(
        type_dependency_depth * 0.3 +
        interface_exposure * 0.3 +
        inheritance_depth * 0.25 +
        composition_tightness * 0.15
    )

def calculate_behavioral_coupling(module_a, module_b, codebase):
    """行为耦合计算"""
    
    # 调用频率（每单位时间/请求）
    call_frequency = analyze_call_frequency(module_a, module_b, codebase)
    
    # 调用复杂度（参数数量、嵌套深度）
    call_complexity = analyze_call_complexity(module_a, module_b, codebase)
    
    # 错误传播概率
    error_propagation = analyze_error_propagation(module_a, module_b, codebase)
    
    return normalize(
        call_frequency * 0.4 +
        call_complexity * 0.3 +
        error_propagation * 0.3
    )

def calculate_data_coupling(module_a, module_b, codebase):
    """数据耦合计算"""
    
    # 共享数据类型数量
    shared_types = count_shared_data_types(module_a, module_b, codebase)
    
    # 数据字段重叠度
    field_overlap = calculate_field_overlap(module_a, module_b, codebase)
    
    # 数据流向（单向 vs 双向）
    data_flow_direction = analyze_data_flow_direction(module_a, module_b)
    
    # 共享可变状态
    shared_mutable = has_shared_mutable_state(module_a, module_b, codebase)
    
    return normalize(
        shared_types * 0.3 +
        field_overlap * 0.3 +
        (0.4 if data_flow_direction == "bidirectional" else 0.2) +
        (0.5 if shared_mutable else 0)
    )
```

### 4.3 关系强度分级

| 等级 | 得分范围 | 特征 | 维护建议 |
|------|----------|------|----------|
| **S级（强依赖）** | 0.8-1.0 | 继承、共享可变状态、循环依赖 | 必须一起修改、优先重构 |
| **A级（紧密）** | 0.6-0.8 | 组合、频繁调用、共享数据 | 谨慎修改、充分测试 |
| **B级（中等）** | 0.4-0.6 | 接口依赖、定期调用 | 按接口修改、注意版本 |
| **C级（松散）** | 0.2-0.4 | 事件依赖、配置依赖 | 独立修改、通知变更 |
| **D级（极弱）** | 0.0-0.2 | 间接依赖、文档引用 | 完全独立 |

### 4.4 变更影响分析

```
┌─────────────────────────────────────────────────────────────────┐
│                   CHANGE IMPACT PROPAGATION                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Module A (changed)                                           │
│       │                                                         │
│       ├──► [Direct Dependency]                                  │
│       │    └──► Coupling: S → High impact probability           │
│       │    └──► Coupling: B → Medium impact probability        │
│       │                                                         │
│       ├──► [Transitive Dependency]                              │
│       │    └──► First order: 0.7 × direct_coupling             │
│       │    └──► Second order: 0.5 × first_order_coupling       │
│       │    └──► Third order: 0.3 × second_order_coupling       │
│       │                                                         │
│       └──► [Hidden Dependency]                                  │
│            └──► Shared data structure → Unexpected impact       │
│            └──► Configuration → Runtime failure                │
│            └──► Event schema → Integration break               │
│                                                                 │
│   IMPACT SCORE = Σ (coupling × propagation_factor)              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 五、关系图设计

### 5.1 数据结构

```typescript
/**
 * 模块间关系图数据结构
 */
interface ModuleRelationGraph {
  // 节点：模块
  modules: Map<ModuleId, ModuleNode>;
  
  // 边：关系
  relations: RelationEdge[];
  
  // 元数据
  metadata: GraphMetadata;
}

interface ModuleNode {
  id: ModuleId;
  name: string;
  type: ModuleType;
  
  // 知识属性
  knowledge: {
    domain: string[];          // 领域概念
    responsibilities: string[]; // 职责列表
    contracts: Contract[];      // 暴露的契约
    dependencies: Dependency[]; // 依赖声明
  };
  
  // 度量
  metrics: {
    linesOfCode: number;
    cyclomaticComplexity: number;
    cohesionScore: number;
    testCoverage: number;
  };
  
  // 位置信息
  location: {
    path: string;
    repository: string;
    package: string;
  };
}

interface RelationEdge {
  id: RelationId;
  source: ModuleId;
  target: ModuleId;
  
  // 关系类型
  type: RelationType;
  
  // 关系方向
  direction: 'outbound' | 'inbound' | 'bidirectional';
  
  // 契约详情
  contract?: {
    type: 'api' | 'event' | 'data' | 'config';
    schema: SchemaDefinition;
    guarantees: string[];
    version: string;
  };
  
  // 强度量度
  strength: {
    overall: number;           // 0-1 综合得分
    structural: number;        // 结构耦合
    behavioral: number;        // 行为耦合
    data: number;              // 数据耦合
    temporal: number;          // 时序耦合
  };
  
  // 知识流动
  knowledgeFlow: {
    direction: 'source-to-target' | 'target-to-source' | 'bidirectional';
    knowledgeTypes: KnowledgeType[];
    volume: number;            // 知识量估算
  };
  
  // 变更影响
  changeImpact: {
    propagationRisk: number;   // 传播风险
    affectedTestCount: number;  // 影响测试数
    recentChangeFrequency: number;
  };
}

type RelationType = 
  | 'call'           // 函数调用
  | 'inherit'        // 继承
  | 'implement'      // 接口实现
  | 'compose'        // 组合
  | 'subscribe'      // 事件订阅
  | 'emit'           // 事件发布
  | 'configure'      // 配置依赖
  | 'share-data'     // 数据共享
  | 'sequence';      // 时序依赖

type KnowledgeType =
  | 'domain-concept'   // 领域概念
  | 'api-contract'     // API契约
  | 'event-schema'     // 事件模式
  | 'data-model'       // 数据模型
  | 'config-schema'    // 配置模式
  | 'error-handling';  // 错误处理
```

### 5.2 图存储方案

```yaml
# 图数据库选型
graph_storage:
  primary:
    type: Neo4j
    reason: "原生图查询，Cypher语法友好，社区成熟"
    
  alternative:
    - type: Amazon Neptune
      reason: "云托管，自动扩展"
    - type: ArangoDB
      reason: "多模型，支持文档+图"
      
  schema:
    nodes:
      - label: Module
        properties: [name, type, domain, responsibilities]
      - label: Contract
        properties: [name, type, version, schema]
        
    edges:
      - type: DEPENDS_ON
        properties: [strength, coupling_type]
      - type: EXPOSES
        properties: [visibility, version]
      - type: KNOWS_ABOUT
        properties: [knowledge_type, depth]

# 查询示例
queries:
  # 查找强依赖模块
  strong_dependencies: |
    MATCH (a:Module)-[r:DEPENDS_ON]->(b:Module)
    WHERE r.strength > 0.7
    RETURN a.name, b.name, r.strength
    ORDER BY r.strength DESC
    
  # 查找变更影响范围
  change_impact: |
    MATCH (changed:Module {name: $module_name})-[r:DEPENDS_ON*1..3]-(affected:Module)
    RETURN affected.name, 
           sum(r.strength) as impact_score
    ORDER BY impact_score DESC
    
  # 查找循环依赖
  circular_dependencies: |
    MATCH (a:Module)-[:DEPENDS_ON]->(b:Module)-[:DEPENDS_ON]->(a)
    RETURN a.name, b.name
```

### 5.3 可视化设计

```
┌─────────────────────────────────────────────────────────────────┐
│                     VISUALIZATION LAYERS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Layer 1: STRUCTURE VIEW                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                                                         │   │
│   │     [Module A] ════► [Module B]                        │   │
│   │        ║               ║                                │   │
│   │        ║               ║                                │   │
│   │        ▼               ▼                                │   │
│   │     [Module C] ◄════ [Module D]                        │   │
│   │                                                         │   │
│   │   图例：════ 强依赖    ──── 弱依赖                       │   │
│   │         ║ 继承关系     ══► 调用关系                      │   │
│   │                                                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   Layer 2: KNOWLEDGE FLOW VIEW                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                                                         │   │
│   │            Knowledge Flow Direction                    │   │
│   │                                                         │   │
│   │     [Core] ─────────────────────► [API]                 │   │
│   │       │      domain concepts      │                     │   │
│   │       │      data models          │                     │   │
│   │       │                           ▼                     │   │
│   │       └────────────────────► [Service]                 │   │
│   │            business rules                               │   │
│   │                                                         │   │
│   │   颜色深度 = 知识量                                      │   │
│   │   箭头粗细 = 知识流动频率                                │   │
│   │                                                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   Layer 3: CHANGE IMPACT VIEW                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                                                         │   │
│   │   修改 [Module A] 的影响范围：                          │   │
│   │                                                         │   │
│   │   ████████ [Module B]  - 直接影响 (0.85)               │   │
│   │   ██████   [Module C]  - 直接影响 (0.72)               │   │
│   │   ████     [Module D]  - 二级影响 (0.51)               │   │
│   │   ██       [Module E]  - 二级影响 (0.34)               │   │
│   │   █        [Module F]  - 三级影响 (0.12)               │   │
│   │                                                         │   │
│   │   颜色强度 = 影响程度                                    │   │
│   │                                                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.4 图分析算法

```python
class ModuleGraphAnalyzer:
    """模块关系图分析器"""
    
    def __init__(self, graph: ModuleRelationGraph):
        self.graph = graph
    
    def find_hotspots(self) -> List[ModuleNode]:
        """找出热点模块（高扇入/扇出）"""
        return sorted(
            self.graph.modules.values(),
            key=lambda m: self._calculate_centroid(m),
            reverse=True
        )
    
    def find_cycles(self) -> List[List[ModuleId]]:
        """检测循环依赖"""
        return self._detect_cycles_tarjan()
    
    def calculate_change_impact(
        self, 
        module_id: ModuleId,
        depth: int = 3
    ) -> Dict[ModuleId, float]:
        """计算变更影响范围"""
        impacts = {}
        self._propagate_impact(module_id, impacts, 1.0, depth)
        return impacts
    
    def find_coupling_clusters(self) -> List[Set[ModuleId]]:
        """找出强耦合模块簇"""
        # 使用社区发现算法
        return self._community_detection()
    
    def suggest_refactoring(self) -> List[RefactoringSuggestion]:
        """重构建议"""
        suggestions = []
        
        # 检测循环依赖
        cycles = self.find_cycles()
        for cycle in cycles:
            suggestions.append({
                "type": "break_cycle",
                "modules": cycle,
                "reason": "循环依赖增加维护成本",
                "priority": "P0"
            })
        
        # 检测高耦合簇
        clusters = self.find_coupling_clusters()
        for cluster in clusters:
            if self._should_split(cluster):
                suggestions.append({
                    "type": "extract_module",
                    "modules": cluster,
                    "reason": "强耦合簇应考虑拆分",
                    "priority": "P1"
                })
        
        return suggestions
```

---

## 六、优先级建议

### P0 - 必须实现（核心功能）

| 功能 | 描述 | 价值 |
|------|------|------|
| **依赖类型识别** | 自动识别调用、继承、组合等关系类型 | 关系建模基础 |
| **强度量化算法** | 实现四维耦合度计算 | 决策依据 |
| **图存储** | Neo4j图数据库存储 | 查询效率 |
| **循环依赖检测** | Tarjan算法检测环 | 质量保障 |
| **变更影响分析** | 单点修改的影响范围计算 | 风险评估 |

### P1 - 重要功能（增强体验）

| 功能 | 描述 | 价值 |
|------|------|------|
| **契约提取器** | 从代码、测试、注释提取契约 | 自动化知识捕获 |
| **知识流动分析** | 可视化知识传递路径 | 架构理解 |
| **热点识别** | 高扇入/扇出模块检测 | 重构优先级 |
| **社区发现** | 自动聚类强耦合模块 | 模块化评估 |
| **关系强度热力图** | 可视化展示耦合分布 | 直观呈现 |

### P2 - 增强功能（锦上添花）

| 功能 | 描述 | 价值 |
|------|------|------|
| **历史演进分析** | 追踪关系变化趋势 | 趋势预测 |
| **重构建议生成** | 自动生成拆分/合并建议 | 辅助决策 |
| **契约版本管理** | 追踪契约演化历史 | 兼容性分析 |
| **多语言支持** | 支持 Java/Go/Python 等 | 广泛适用 |
| **CI/CD 集成** | 变更影响自动预警 | 持续监控 |

---

## 附录：参考资料

### 学术论文
1. "Software Architecture in Practice" - Bass, Clements, Kazman
2. "Documenting Software Architectures" - Clements et al.
3. "Building Evolutionary Architectures" - Ford, Parsons, Kua

### 相关标准
1. UML Component Diagram
2. C4 Model - Context, Containers, Components, Code
3. DDD Strategic Design - Context Mapping

### 工具参考
1. Neo4j - 图数据库
2. Structure101 - 依赖分析
3. ArchUnit - 架构规则检查
4. Sonargraph - 模块度分析

---

*报告完成 | 待后续研究：知识注入文件格式设计、模块边界自动化检测*

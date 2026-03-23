# 知识图谱结构设计研究报告

研究日期: 2026-03-10 | 模型: GLM-5

---

## 一、节点设计

### 1.1 节点类型体系

灵魂拆解的知识图谱需要支持多层次的代码知识表示，采用 **多类型节点** 架构：

#### 1.1.1 模块节点 (Module Node)

**语义**：表示代码的组织单元，是灵魂提取的核心载体

```json
{
  "id": "module:auth-service:1.2.0",
  "type": "Module",
  "label": "AuthService",
  "properties": {
    "name": "auth-service",
    "version": "1.2.0",
    "path": "src/services/auth/",
    "language": "TypeScript",
    "description": "用户认证服务模块",
    "tokenCount": 15420,
    "lastModified": "2026-03-10T12:00:00Z",
    "gitHash": "abc123def456",
    "sourceCommit": "https://github.com/org/repo/commit/abc123",
    "soulExtractedAt": "2026-03-10T13:00:00Z",
    "extractorVersion": "2.1.0"
  }
}
```

**属性说明**：
| 属性 | 类型 | 必需 | 说明 |
|------|------|------|------|
| name | string | ✓ | 模块唯一名称 |
| version | string | ✓ | 语义版本号 |
| path | string | ✓ | 代码路径（相对根目录） |
| language | string | | 主要编程语言 |
| description | string | | 模块功能描述 |
| tokenCount | integer | | 灵魂文档 Token 数 |
| gitHash | string | | 源代码 Git 提交哈希 |
| soulHash | string | | 灵魂内容哈希（用于变更检测） |

#### 1.1.2 概念节点 (Concept Node)

**语义**：表示模块中的关键概念、设计思想、抽象模式

```json
{
  "id": "concept:auth:jwt-strategy",
  "type": "Concept",
  "label": "JWT Authentication Strategy",
  "properties": {
    "name": "jwt-strategy",
    "category": "DesignPattern",
    "abstractionLevel": "high",
    "description": "基于 JWT 的无状态认证策略",
    "keywords": ["jwt", "authentication", "stateless", "token"],
    "relatedPatterns": ["OAuth2", "Session-Cookie"],
    "tradeoffs": {
      "pros": ["无状态", "可扩展", "跨域友好"],
      "cons": ["无法主动失效", "Token 较大"]
    }
  }
}
```

**概念分类**：
- `DesignPattern`：设计模式（单例、工厂、观察者等）
- `ArchitecturePattern`：架构模式（微服务、CQRS、事件驱动）
- `DomainConcept`：领域概念（用户、订单、支付）
- `TechnicalConcept`：技术概念（缓存、队列、限流）

#### 1.1.3 规则节点 (Rule Node)

**语义**：表示代码中的业务规则、约束条件、最佳实践

```json
{
  "id": "rule:auth:password-strength",
  "type": "Rule",
  "label": "Password Strength Rule",
  "properties": {
    "name": "password-strength",
    "category": "ValidationRule",
    "severity": "error",
    "description": "密码必须包含大小写字母、数字，长度≥8",
    "condition": "password.matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d).{8,}$/)",
    "enforcementPoints": ["registration", "password-reset"],
    "examples": {
      "valid": ["Pass123word", "Secure99"],
      "invalid": ["password", "Pass1", "12345678"]
    }
  }
}
```

**规则分类**：
- `ValidationRule`：验证规则
- `BusinessRule`：业务规则
- `SecurityRule`：安全规则
- `PerformanceRule`：性能规则

#### 1.1.4 代码节点 (Code Node)

**语义**：表示具体的代码实体（函数、类、接口、常量等）

```json
{
  "id": "code:auth:validateToken",
  "type": "Code",
  "label": "validateToken",
  "properties": {
    "name": "validateToken",
    "codeType": "Function",
    "signature": "(token: string) => Promise<TokenPayload>",
    "filePath": "src/services/auth/token.service.ts",
    "lineStart": 45,
    "lineEnd": 78,
    "isExported": true,
    "isAsync": true,
    "complexity": 5,
    "testCoverage": 0.92,
    "description": "验证并解析 JWT Token",
    "throws": ["TokenExpiredError", "InvalidTokenError"]
  }
}
```

**代码类型枚举**：
- `Function`：函数
- `Class`：类
- `Interface`：接口
- `Type`：类型定义
- `Constant`：常量
- `Enum`：枚举
- `Module`：子模块

### 1.2 节点标识规范

**ID 格式**：`{type}:{module}:{name}[:version]`

```
module:auth-service:1.2.0          # 模块节点
concept:auth:jwt-strategy          # 概念节点
rule:auth:password-strength        # 规则节点
code:auth:validateToken            # 代码节点
```

**命名约定**：
- 使用 kebab-case 命名
- 模块名作为命名空间前缀
- 版本号仅用于模块节点
- 保证全局唯一性

---

## 二、边设计

### 2.1 边类型体系

#### 2.1.1 依赖边 (DEPENDS_ON)

**语义**：模块间的依赖关系，表示编译/运行时依赖

```json
{
  "id": "edge:depends:auth:database",
  "type": "DEPENDS_ON",
  "source": "module:auth-service:1.2.0",
  "target": "module:database-layer:2.0.0",
  "properties": {
    "dependencyType": "runtime",
    "optional": false,
    "versionConstraint": "^2.0.0",
    "importedSymbols": ["QueryRunner", "ConnectionPool"],
    "importCount": 12
  }
}
```

**依赖类型**：
- `compile`：编译时依赖
- `runtime`：运行时依赖
- `dev`：开发依赖
- `peer`：对等依赖

#### 2.1.2 包含边 (CONTAINS)

**语义**：层级包含关系，用于构建树状结构

```json
{
  "id": "edge:contains:auth:validateToken",
  "type": "CONTAINS",
  "source": "module:auth-service:1.2.0",
  "target": "code:auth:validateToken",
  "properties": {
    "isPrimary": true,
    "visibility": "public"
  }
}
```

**包含层级**：
```
System → Module → Submodule → Class/Function → CodeBlock
```

#### 2.1.3 引用边 (REFERENCES)

**语义**：知识引用关系，表示概念/规则的使用

```json
{
  "id": "edge:ref:auth:jwt-strategy",
  "type": "REFERENCES",
  "source": "module:auth-service:1.2.0",
  "target": "concept:auth:jwt-strategy",
  "properties": {
    "referenceContext": "implementation",
    "strength": 0.85,
    "soulSection": ["Architecture", "Security Model"]
  }
}
```

**引用上下文**：
- `implementation`：实现参考
- `documentation`：文档引用
- `test`：测试引用
- `configuration`：配置引用

#### 2.1.4 调用边 (CALLS)

**语义**：代码调用关系，表示函数/方法调用

```json
{
  "id": "edge:calls:validateToken:decodeJWT",
  "type": "CALLS",
  "source": "code:auth:validateToken",
  "target": "code:jwt:decodeJWT",
  "properties": {
    "callType": "direct",
    "frequency": "high",
    "callSites": [
      {"file": "token.service.ts", "line": 52},
      {"file": "token.service.ts", "line": 67}
    ]
  }
}
```

### 2.2 边方向与语义

| 边类型 | 方向性 | 源节点 | 目标节点 | 典型查询 |
|--------|--------|--------|----------|----------|
| DEPENDS_ON | 有向 | 依赖方 | 被依赖方 | 查依赖树、影响分析 |
| CONTAINS | 有向 | 父节点 | 子节点 | 查模块组成、粒度导航 |
| REFERENCES | 有向 | 引用方 | 被引用方 | 查概念关联、知识溯源 |
| CALLS | 有向 | 调用方 | 被调用方 | 查调用链、影响范围 |

### 2.3 边权重与强度

```json
{
  "strength": 0.85,    // 关系强度 [0-1]
  "confidence": 0.92,  // 提取置信度 [0-1]
  "frequency": "high", // 交互频率：low/medium/high
  "recency": 0.7       // 时效性权重 [0-1]
}
```

---

## 三、元数据设计

### 3.1 版本控制

```json
{
  "version": {
    "major": 1,
    "minor": 2,
    "patch": 0,
    "preRelease": null,
    "buildMetadata": "git.abc123"
  },
  "versionHistory": [
    {
      "version": "1.2.0",
      "timestamp": "2026-03-10T13:00:00Z",
      "changes": ["新增 OAuth2 支持", "重构 Token 验证逻辑"],
      "deltaFrom": "1.1.0",
      "deltaHash": "sha256:xyz789"
    }
  ]
}
```

### 3.2 时间戳体系

```json
{
  "timestamps": {
    "createdAt": "2026-01-15T10:00:00Z",
    "modifiedAt": "2026-03-10T13:00:00Z",
    "soulExtractedAt": "2026-03-10T13:00:00Z",
    "lastQueriedAt": "2026-03-10T15:30:00Z",
    "expiresAt": "2026-04-10T13:00:00Z"
  }
}
```

### 3.3 哈希与完整性

```json
{
  "hashes": {
    "contentHash": "sha256:a1b2c3d4e5f6...",
    "structureHash": "sha256:g7h8i9j0k1l2...",
    "dependencyHash": "sha256:m3n4o5p6q7r8..."
  },
  "verification": {
    "verified": true,
    "verifiedAt": "2026-03-10T13:05:00Z",
    "verifier": "soul-extractor@2.1.0"
  }
}
```

### 3.4 来源追溯 (Provenance)

```json
{
  "provenance": {
    "source": {
      "type": "git",
      "repository": "https://github.com/org/repo.git",
      "commit": "abc123def456",
      "branch": "main",
      "tag": "v1.2.0"
    },
    "extraction": {
      "tool": "soul-extractor",
      "version": "2.1.0",
      "config": {
        "model": "gpt-4-turbo",
        "temperature": 0.3
      },
      "duration": 45.2,
      "tokenUsage": {
        "prompt": 15000,
        "completion": 5000,
        "total": 20000
      }
    },
    "lineage": [
      {"action": "created", "at": "2026-01-15T10:00:00Z", "by": "user@example.com"},
      {"action": "updated", "at": "2026-03-10T13:00:00Z", "by": "soul-extractor"}
    ]
  }
}
```

---

## 四、存储格式

### 4.1 格式对比分析

| 格式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **JSON** | 通用性强、解析快、工具链成熟 | 无内置图查询、大文件性能差 | 单模块存储、API 传输 |
| **Neo4j** | 原生图查询、ACID 事务、丰富生态 | 需要独立服务、内存占用高 | 复杂关系查询、实时分析 |
| **SQLite + FTS** | 轻量、无依赖、全文检索 | 图查询需手动实现 | 本地缓存、离线查询 |
| **Markdown** | 人类可读、Git 友好 | 查询需解析、结构松散 | 文档归档、版本对比 |
| **Protocol Buffers** | 高效序列化、跨语言 | 需预定义 Schema、调试困难 | 高性能传输、长期存储 |

### 4.2 推荐方案：混合存储

```
soul-repo/
├── graph.db/              # Neo4j 图数据库（主存储）
│   ├── data/
│   └── index/
├── exports/               # 导出层
│   ├── json/             # JSON 格式（API/传输）
│   │   ├── modules/
│   │   └── concepts/
│   └── markdown/          # Markdown 格式（文档/归档）
│       └── souls/
└── cache/                 # 本地缓存层
    └── sqlite/           # SQLite + FTS（快速检索）
        ├── nodes.db
        └── edges.db
```

### 4.3 JSON Schema 定义

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://soul-extractor.io/schemas/module-soul.json",
  "title": "Module Soul",
  "type": "object",
  "required": ["id", "type", "label", "properties", "edges"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^module:[a-z0-9-]+(:[0-9]+\\.[0-9]+\\.[0-9]+)?$"
    },
    "type": {
      "type": "string",
      "enum": ["Module", "Concept", "Rule", "Code"]
    },
    "label": {
      "type": "string",
      "minLength": 1,
      "maxLength": 255
    },
    "properties": {
      "type": "object",
      "additionalProperties": true
    },
    "edges": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/Edge"
      }
    },
    "metadata": {
      "$ref": "#/definitions/Metadata"
    }
  },
  "definitions": {
    "Edge": {
      "type": "object",
      "required": ["type", "target"],
      "properties": {
        "type": {
          "type": "string",
          "enum": ["DEPENDS_ON", "CONTAINS", "REFERENCES", "CALLS"]
        },
        "target": { "type": "string" },
        "properties": { "type": "object" }
      }
    },
    "Metadata": {
      "type": "object",
      "properties": {
        "version": { "type": "string" },
        "timestamps": { "type": "object" },
        "hashes": { "type": "object" },
        "provenance": { "type": "object" }
      }
    }
  }
}
```

---

## 五、查询接口设计

### 5.1 查询语言选择

| 查询场景 | 推荐语言 | 原因 |
|----------|----------|------|
| 图遍历/关系查询 | **Cypher** | Neo4j 原生，表达式直观 |
| API 查询接口 | **GraphQL** | 类型安全、按需取数据 |
| 全文检索 | **FTS5** | SQLite 内置，性能优秀 |
| 程序化查询 | **Gremlin** | 语言中立，可移植性好 |

### 5.2 核心 Cypher 查询示例

#### 查询模块依赖树

```cypher
// 查询模块的所有依赖（递归）
MATCH path = (m:Module {id: $moduleId})-[:DEPENDS_ON*]->(dep:Module)
RETURN path
ORDER BY length(path)
```

#### 查询概念关联模块

```cypher
// 查询使用某概念的所有模块
MATCH (m:Module)-[r:REFERENCES]->(c:Concept {name: $conceptName})
WHERE r.strength > 0.5
RETURN m, r
ORDER BY r.strength DESC
```

#### 查询影响范围

```cypher
// 查询修改某函数的影响范围
MATCH (f:Code {id: $codeId})<-[:CALLS*]-(caller:Code)
RETURN caller
UNION
MATCH (f:Code)<-[:CONTAINS]-(m:Module)
RETURN m as caller
```

### 5.3 GraphQL API Schema

```graphql
type Query {
  """获取模块及其灵魂"""
  module(id: ID!): Module
  
  """搜索模块"""
  searchModules(
    query: String!
    filters: ModuleFilter
    limit: Int = 10
  ): [Module!]!
  
  """获取概念详情"""
  concept(id: ID!): Concept
  
  """查询依赖关系"""
  dependencies(
    moduleId: ID!
    depth: Int = 3
    direction: Direction = DOWNSTREAM
  ): DependencyGraph!
}

type Module {
  id: ID!
  name: String!
  version: String!
  path: String!
  description: String
  soul: SoulDocument
  concepts: [Concept!]!
  rules: [Rule!]!
  codeNodes: [Code!]!
  dependencies: [Module!]!
  dependents: [Module!]!
}

type Concept {
  id: ID!
  name: String!
  category: ConceptCategory!
  description: String
  usedBy: [Module!]!
}

enum Direction {
  UPSTREAM    # 被谁依赖
  DOWNSTREAM  # 依赖谁
  BOTH        # 双向
}

input ModuleFilter {
  language: String
  minVersion: String
  maxVersion: String
  hasConcepts: [String!]
  hasRules: [String!]
}
```

### 5.4 REST API 端点

```
GET    /api/v1/modules                    # 列出模块
GET    /api/v1/modules/:id                # 获取模块详情
GET    /api/v1/modules/:id/soul           # 获取模块灵魂文档
GET    /api/v1/modules/:id/dependencies   # 获取依赖图
GET    /api/v1/modules/:id/impact         # 影响分析

GET    /api/v1/concepts                   # 列出概念
GET    /api/v1/concepts/:id               # 获取概念详情
GET    /api/v1/concepts/:id/modules       # 使用该概念的模块

GET    /api/v1/search?q=:query            # 全文搜索
POST   /api/v1/query                      # Cypher 查询
```

---

## 六、Schema 定义

### 6.1 Neo4j 节点标签与约束

```cypher
// 创建唯一性约束
CREATE CONSTRAINT module_id_unique IF NOT EXISTS
FOR (m:Module) REQUIRE m.id IS UNIQUE;

CREATE CONSTRAINT concept_id_unique IF NOT EXISTS
FOR (c:Concept) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT rule_id_unique IF NOT EXISTS
FOR (r:Rule) REQUIRE r.id IS UNIQUE;

CREATE CONSTRAINT code_id_unique IF NOT EXISTS
FOR (c:Code) REQUIRE c.id IS UNIQUE;

// 创建索引加速查询
CREATE INDEX module_name_index IF NOT EXISTS
FOR (m:Module) ON (m.name);

CREATE INDEX module_version_index IF NOT EXISTS
FOR (m:Module) ON (m.version);

CREATE INDEX concept_category_index IF NOT EXISTS
FOR (c:Concept) ON (c.category);

CREATE FULLTEXT INDEX soul_search_index IF NOT EXISTS
FOR (m:Module) ON EACH [m.name, m.description];
```

### 6.2 完整 GraphQL Schema

```graphql
schema {
  query: Query
  mutation: Mutation
}

"""
模块灵魂知识图谱 Schema
"""
type Query {
  module(id: ID!): Module
  modules(filter: ModuleFilter, page: PageInput): ModuleConnection!
  concept(id: ID!): Concept
  concepts(filter: ConceptFilter, page: PageInput): ConceptConnection!
  rule(id: ID!): Rule
  rules(filter: RuleFilter, page: PageInput): RuleConnection!
  code(id: ID!): Code
  search(query: String!, types: [NodeType!], limit: Int): SearchResult!
  graph(moduleId: ID!, depth: Int, edgeTypes: [EdgeType!]): Graph!
}

type Mutation {
  createModule(input: CreateModuleInput!): Module!
  updateModule(id: ID!, input: UpdateModuleInput!): Module!
  deleteModule(id: ID!): Boolean!
  createConcept(input: CreateConceptInput!): Concept!
  linkConcept(moduleId: ID!, conceptId: ID!, strength: Float): Module!
}

# Node Types
enum NodeType {
  MODULE
  CONCEPT
  RULE
  CODE
}

enum EdgeType {
  DEPENDS_ON
  CONTAINS
  REFERENCES
  CALLS
}

# Filter Inputs
input ModuleFilter {
  name: String
  nameContains: String
  version: String
  language: String
  hasDependency: ID
  hasConcept: ID
  createdAfter: DateTime
  modifiedAfter: DateTime
}

input ConceptFilter {
  name: String
  category: ConceptCategory
  usedByModule: ID
}

# Pagination
input PageInput {
  first: Int = 20
  after: String
}

type ModuleConnection {
  edges: [ModuleEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type ModuleEdge {
  node: Module!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

scalar DateTime
scalar JSON
```

---

## 七、优先级建议

### P0 - 核心必须（MVP）

| 优先级 | 功能 | 说明 | 预估工时 |
|--------|------|------|----------|
| P0 | 模块节点设计 | 核心载体，必须有 | 2h |
| P0 | DEPENDS_ON 边 | 依赖关系是灵魂拆解基础 | 1h |
| P0 | CONTAINS 边 | 层级结构必需 | 1h |
| P0 | JSON 存储格式 | 通用性强，实现简单 | 2h |
| P0 | 基础元数据 | 版本、时间戳、哈希 | 1h |
| P0 | Cypher 基础查询 | 依赖树、概念关联 | 2h |

**P0 总计：约 9 小时**

### P1 - 重要增强

| 优先级 | 功能 | 说明 | 预估工时 |
|--------|------|------|----------|
| P1 | 概念节点 | 知识提取核心价值 | 2h |
| P1 | 规则节点 | 业务知识表示 | 2h |
| P1 | 代码节点 | 细粒度知识定位 | 2h |
| P1 | REFERENCES 边 | 概念关联必需 | 1h |
| P1 | CALLS 边 | 代码调用关系 | 2h |
| P1 | 来源追溯元数据 | 可审计性 | 1h |
| P1 | GraphQL API | API 标准化 | 3h |
| P1 | SQLite 缓存层 | 离线查询支持 | 2h |

**P1 总计：约 15 小时**

### P2 - 未来优化

| 优先级 | 功能 | 说明 | 预估工时 |
|--------|------|------|----------|
| P2 | 边权重计算 | 智能排序、推荐 | 3h |
| P2 | 全文检索索引 | 快速搜索 | 2h |
| P2 | Markdown 导出 | 文档归档 | 2h |
| P2 | Protocol Buffers | 高性能传输 | 3h |
| P2 | 版本历史快照 | 版本对比 | 4h |
| P2 | 增量更新机制 | 变更检测 | 4h |

**P2 总计：约 18 小时**

### 实施路线图

```
Week 1: P0 核心实现
├── Day 1-2: 节点设计 + JSON Schema
├── Day 3: 边设计 + Neo4j 约束
├── Day 4: 元数据体系
└── Day 5: 基础查询实现

Week 2: P1 重要增强
├── Day 1-2: 概念/规则/代码节点
├── Day 3: REFERENCES/CALLS 边
├── Day 4: GraphQL API
└── Day 5: SQLite 缓存层

Week 3-4: P2 持续优化
├── 边权重算法
├── 全文检索
├── 导出格式
└── 性能调优
```

---

## 附录：设计原则

1. **唯一标识**：所有节点必须有全局唯一 ID
2. **版本可追溯**：每次变更都有完整历史
3. **增量友好**：支持部分更新，避免全量重建
4. **查询高效**：合理索引，避免全图扫描
5. **存储灵活**：主存储 + 多格式导出
6. **扩展开放**：节点属性支持扩展字段

---

*报告完成于 2026-03-10*

# AllInOne 技术栈选择策略设计

**日期**: 2026-03-08  
**版本**: v0.1  
**性质**: 产品架构与技术栈策略设计文档  
**目标**: 为 AllInOne 设计一套“固定核心、开放外围、最小依赖、渐进扩展”的技术栈策略，最大化用户选择权，最小化供应商锁定

---

# 一、问题定义

AllInOne 的目标不是做一个“只能跑在某一套固定栈上的 AI 应用”，而是做一个像 OpenClaw 一样的**个人 AI 能力底座**：

- 用户可以选择自己偏好的大模型
- 用户可以选择自己接受的成本结构
- 用户可以选择云服务或本地运行方式
- 用户可以选择是否引入嵌入、向量库、图数据库
- 用户可以从“只有一个 API key”开始，逐步升级能力

这意味着 AllInOne 的技术栈设计不能走下面这种路线：

> 必须先部署 Neo4j + Qdrant + 特定 embedding model + 特定 reranker + 特定 orchestration framework，系统才可用。

这种路线的问题不是“太复杂”，而是它违背了产品哲学：

- 用户失去选择权
- 迁移成本高
- 初始门槛高
- 系统很快被某个供应商或某类架构绑定
- 技术演进时，整个系统很难替换局部组件

AllInOne 更合理的路线应当是：

> **固定的是协议、数据格式、抽象接口、执行语义；开放的是提供商、模型、存储、索引和数据源。**

---

# 二、核心结论（先给结论）

我对 AllInOne 技术栈策略的最终建议是：

> **“以能力为中心，而不是以供应商为中心。”**

也就是说，AllInOne 不应该要求用户“选某个厂商全家桶”，而应该允许用户按层选择能力提供方：

- LLM 层：Claude / GPT / Gemini / DeepSeek / 本地 OpenAI-compatible 模型
- Embedding 层：OpenAI / Voyage / Gemini / Jina / BGE / 本地 embedding
- Retrieval 层：纯 LLM / 本地倒排 / 向量检索 / 图检索 / 混合检索
- Storage 层：文件系统 / SQLite / Postgres / pgvector / Qdrant / Weaviate / Milvus / Neo4j / Memgraph
- 采集层：GitHub / GitLab / RSS / 文档站 / Notion / 本地文件夹 / MCP / 自定义 Connector

但与此同时，AllInOne 必须固定少数几个“不可随意变化的核心层”：

1. **标准输入输出格式**
2. **统一抽象接口**
3. **能力注册机制**
4. **任务执行语义**
5. **灵魂资产的数据模型**
6. **配置与作用域机制**
7. **观察性与可追溯性规范**

也就是说：

- **开放的是“谁提供能力”**
- **固定的是“能力怎么接入系统、怎么被系统消费”**

这和 OpenClaw 的哲学是一致的：

- 平台不替用户做供应商选择
- 平台负责把不同能力接成统一体验
- 平台尽量使用开放协议，而不是私有耦合

---

# 三、OpenClaw 参考哲学：AllInOne 应该学什么

OpenClaw 的关键启发不是某个具体工具，而是一种产品哲学：

## 3.1 不把用户困在某个厂商里

在个人 AI 终端/工作流生态中，真正重要的是：

- 用户的模型偏好会变
- 用户的成本承受能力会变
- 用户所在地区的服务可用性会变
- 用户的数据合规需求会变
- 某个今天最好的模型，六个月后可能不是最优

因此 AllInOne 不能假设：

- 所有人都用同一个 LLM
- 所有人都接受同一个 embedding 模型
- 所有人都愿意部署向量库
- 所有人都需要图数据库

## 3.2 平台负责抽象，不负责强制绑定

一个好的平台做两件事：

- 定义标准接口
- 隐藏 provider 差异

但不做两件事：

- 把 provider 差异变成产品依赖
- 把工程选择变成用户负担

## 3.3 用户应有多层级选择权

“可选择”不应只停留在一个全局设置里，而应有多层作用域：

- 全局默认
- 项目级默认
- 工作流级选择
- 单次任务级 override

AllInOne 也应该采用相同策略。

---

# 四、OpenClaw 生态对照调研：Claude Code / Cursor / 通用协议

以下结论基于 2026-03-08 当天可访问的一手官方文档与公开项目文档整理。

## 4.1 Claude Code 的技术栈选择哲学

Claude Code 的核心哲学可以概括为：

- **模型是可配置的**：支持在 session、启动参数、环境变量、settings 中切换模型
- **工具是可插拔的**：通过 MCP 接入外部工具、数据库、API、服务
- **配置是分层的**：用户级、项目级、本地级、托管策略级
- **协议是开放的**：MCP 是开放协议，Claude Code 既可以作为 MCP client，也可以作为 MCP server

### 关键观察

#### 观察 1：Claude Code 把“模型配置”当成正式能力

Anthropic 官方文档明确支持：

- `/model` 在会话内切换模型
- `--model` 启动时指定模型
- `ANTHROPIC_MODEL` 环境变量设置默认模型
- settings 文件持久化模型偏好

这说明：

> **模型不是被写死在产品内部的，而是被显式抽象成可配置层。**

#### 观察 2：Claude Code 的工具接入不是私有 SDK，而是 MCP

Anthropic 官方将 MCP 描述为一个开放协议，用于标准化 AI 应用如何接入工具和上下文。

Claude Code 通过 MCP 接入：

- 数据源
- 数据库
- issue tracker
- 设计工具
- 自定义服务

而且 Claude Code 本身还能 `claude mcp serve` 暴露为 MCP server。

这说明：

> **Claude Code 的核心不是“内置多少工具”，而是“接入工具的协议层够不够开放”。**

#### 观察 3：Claude Code 配置作用域非常清晰

Anthropic 文档支持：

- `~/.claude/settings.json` 用户级
- `.claude/settings.json` 项目共享级
- `.claude/settings.local.json` 项目本地级
- managed settings 企业托管级

这对 AllInOne 的启发极大：

> **选择权不仅要存在，还要能在不同作用域下存在。**

### Claude Code 的启发

AllInOne 应该学习的是：

- 模型配置是正式一等公民
- 工具接入走开放协议
- 配置支持多层级覆盖
- 核心产品不依赖单一外部工具厂商

### 需要注意的边界

Claude Code 在“模型无关”这件事上并不是完全开放到任何 provider，它的模型层仍然围绕 Claude 系列展开；但在**工具协议和配置机制**上，它展示了非常强的开放性。

这意味着 AllInOne 要比 Claude Code 再多走一步：

- Claude Code 的开放重点在工具协议
- AllInOne 的开放重点应同时覆盖模型、检索、存储和采集

## 4.2 Cursor 的技术栈选择哲学

Cursor 的技术栈选择哲学更像是：

- **Bring Your Own Provider**
- **Bring Your Own Tooling**
- **由编辑器/CLI负责统一体验**

### 关键观察

#### 观察 1：Cursor 支持用户自带 API Keys

Cursor 官方文档明确支持用户填写自己的 API keys，并直接调用多个 provider，包括：

- OpenAI
- Anthropic
- Google
- Azure OpenAI
- AWS Bedrock

这说明 Cursor 把“provider 选择”明确交给用户，而不是让用户只能消费 Cursor 自己包装后的模型池。

#### 观察 2：Cursor 也采用 MCP 作为工具层协议

Cursor 官方 MCP 文档说明：

- 支持 stdio、SSE、Streamable HTTP 三种 transport
- 支持 OAuth
- MCP tools 可启用/禁用
- Editor 与 CLI 共用 MCP 配置

这说明 Cursor 在工具层也走的是开放协议，而不是私有 integration stack。

#### 观察 3：Cursor 把可选择性做到 UI/工作流层

Cursor 不只是“底层支持很多 provider”，而是把这种能力做到了实际用户体验里：

- 模型可选
- MCP tools 可选
- auto-run 可选
- tools 可 toggle

这启发 AllInOne：

> **“开放”不能只存在于 SDK 里，必须存在于用户的可见配置和操作面板中。**

## 4.3 这些工具如何实现“用户选择”而不是“供应商锁定”

从 Claude Code 与 Cursor 的共同点来看，它们都没有试图通过“强绑定基础设施”来制造护城河。

它们依赖的是三个策略：

### 策略 1：协议标准化

工具和上下文接入通过 MCP，而不是每个服务单独写私有 glue code。

### 策略 2：配置分层化

用户可以在不同层级定义偏好，不必被单一全局设置绑定。

### 策略 3：能力抽象化

对产品而言，需要的是：

- 文本生成能力
- 工具调用能力
- 长上下文能力
- 检索能力

至于具体来自哪个 provider，只要满足接口契约即可。

---

# 五、通用协议与标准：AllInOne 应优先拥抱什么

## 5.1 MCP：上下文与工具接入标准

### 定位

MCP 解决的问题是：

> AI 应用如何以标准方式接入工具、上下文、资源和提示。

### 价值

- 避免每个服务写一套独立集成
- 降低工具层供应商锁定
- 让本地工具和远程服务统一接入
- 让 editor、CLI、agent runtime 共享能力层

### 对 AllInOne 的意义

AllInOne 应把 MCP 视为：

- 第一优先级工具协议
- 第一优先级外部上下文协议
- 外部生态接入的默认方式

### 结论

> **AllInOne 不应自己发明一套新的工具协议。应该优先兼容 MCP。**

## 5.2 A2A：Agent-to-Agent 互操作标准

### 定位

A2A（Agent2Agent）解决的问题是：

> 不同 agent 之间如何通信、协作、传递任务与状态。

Google 公布 A2A 时明确将其定位为与 MCP 互补：

- MCP 偏“工具与上下文接入”
- A2A 偏“agent 之间互联互通”

### 对 AllInOne 的意义

AllInOne 当前最重要的不是先把 A2A 做成强依赖，而是：

- 内部 agent/task/message 模型设计时，尽量向 A2A 的思想对齐
- 保留未来把 AllInOne agent 暴露成 A2A server 的能力
- 保留未来消费外部 A2A agents 的能力

### 结论

> **MCP 应是当前优先落地协议，A2A 应是未来兼容目标协议。**

## 5.3 OpenAI Function Calling / Tool Calling：模型 API 侧的事实标准

### 定位

OpenAI 在官方 Responses API 文档中，把 function/tool calling 定义成模型调用外部能力的标准方式；并且文档已经把：

- function calling
- built-in tools
- remote MCP

放进同一个工具框架下。

### 对 AllInOne 的意义

这说明业界正在形成两个层次的事实标准：

- **应用侧工具协议**：MCP
- **模型 API 侧工具语义**：JSON Schema function calling / tool calling

AllInOne 应统一采用的内部表达应当是：

- 工具说明 = JSON Schema 风格
- 工具调用 = 标准化 request / response envelope
- 如 provider 不支持 strict schema，则降级为 prompt-guided tool plan

### 结论

> **AllInOne 的工具抽象层，应该在内部兼容 Function Calling 的语义模型。**

---

# 六、AllInOne 应该固定什么、开放什么

这是最核心的设计决策。

## 6.1 必须固定的组件

这些组件一旦不固定，整个系统会变成碎片化“拼装项目”。

### 固定项 1：核心数据模型

必须固定：

- `Document`
- `Chunk`
- `EmbeddingRecord`
- `KnowledgeArtifact`
- `GraphNode`
- `GraphEdge`
- `Task`
- `ToolSpec`
- `ModelResponse`
- `ProviderCapability`

原因：

- 只有固定数据模型，才可能让下层 provider 可替换
- 否则每换一个存储/模型，整个链路都要改

### 固定项 2：抽象接口（SPI / Provider Contracts）

必须固定：

- LLMProvider
- EmbeddingProvider
- VectorStore
- GraphStore
- BlobStore
- Connector
- ToolAdapter
- Reranker
- RetrievalPlanner

原因：

- 这是系统真正的“插槽边界”
- 如果接口不固定，开放性只是口号

### 固定项 3：配置格式与作用域机制

必须固定：

- 配置文件格式（建议 YAML/JSON 二选一，内部统一解析）
- 作用域机制（global / project / workflow / task）
- provider alias 与 profile 机制

原因：

- 这是用户选择权真正落地的地方

### 固定项 4：任务执行语义

必须固定：

- task state machine
- retries / timeout / fallback / cancellation semantics
- capability detection rules

原因：

- 否则 workflow 层很难稳定运行

### 固定项 5：观察性标准

必须固定：

- trace id / task id / artifact id
- provider cost accounting
- latency metrics
- confidence / evidence / source tracking

原因：

- 可替换架构如果没有统一观察性，会变成不可调试架构

## 6.2 应该开放给用户选择的组件

### 开放项 1：LLM Provider

用户应可选：

- Anthropic
- OpenAI
- Google Gemini
- DeepSeek
- Azure OpenAI
- AWS Bedrock
- OpenAI-compatible local endpoint（如 Ollama / vLLM / LM Studio / 自建 gateway）

### 开放项 2：Embedding Provider

用户应可选：

- OpenAI embeddings
- Voyage
- Gemini embeddings
- Jina embeddings
- BGE / Nomic / E5 / local embedding model
- 甚至“无 embedding 模式”

### 开放项 3：Retrieval Backend

用户应可选：

- 无向量检索（纯 LLM / 关键词）
- 本地 SQLite FTS / BM25
- Postgres + pgvector
- Qdrant
- Weaviate
- Milvus
- Elasticsearch/OpenSearch 混合检索

### 开放项 4：Graph Backend

用户应可选：

- 无图数据库模式
- SQLite adjacency / JSON graph
- Neo4j
- Memgraph
- Postgres graph-like tables

### 开放项 5：Connector / 数据源

用户应可选：

- GitHub / GitLab
- RSS / 网站 / 文档站
- 本地文件夹
- Notion / Confluence
- MCP 资源
- 自定义 HTTP Connector

### 开放项 6：Reranker / Ranking Strategy

用户应可选：

- 无 reranker
- 纯 embedding similarity
- lexical + semantic hybrid
- provider reranker API
- 本地 cross-encoder

## 6.3 不建议开放的内容

以下内容如果全部交给用户，会导致系统失控：

- 内部 artifact schema
- provider interface shape
- task lifecycle semantics
- evidence/confidence format
- plugin manifest contract

这些必须由 AllInOne 自己定义。

---

# 七、分层架构设计

```mermaid
flowchart TD
    A[User / App / Workflow] --> B[Experience Layer]
    B --> C[Orchestrator Layer]
    C --> D[Capability Registry]

    D --> E1[LLM Provider Adapters]
    D --> E2[Embedding Provider Adapters]
    D --> E3[Retrieval Adapters]
    D --> E4[Storage Adapters]
    D --> E5[Connector Adapters]
    D --> E6[Tool / MCP / A2A Adapters]

    E1 --> F1[Anthropic OpenAI Gemini DeepSeek Local]
    E2 --> F2[OpenAI Voyage Jina BGE Local]
    E3 --> F3[None FTS pgvector Qdrant Weaviate Milvus]
    E4 --> F4[Filesystem SQLite Postgres Blob Graph]
    E5 --> F5[GitHub GitLab RSS MCP Notion Local Files]
    E6 --> F6[MCP Client MCP Server Future A2A]

    C --> G[Artifact Store]
    C --> H[Observability & Policy]
```

## 7.1 Experience Layer

职责：

- 接收用户配置
- 展示可选 provider/profile
- 支持作用域覆盖
- 提供“最小模式”和“高级模式”体验

## 7.2 Orchestrator Layer

职责：

- 读取能力注册表
- 根据任务目标选择 provider 组合
- 管理 fallback / retry / routing
- 管理 retrieval pipeline

## 7.3 Capability Registry

职责：

- 把“一个 provider 能做什么”标准化描述出来
- 用能力而不是品牌驱动路由

## 7.4 Provider Adapter Layers

职责：

- 隐藏 provider 差异
- 保证统一接口
- 暴露能力说明

## 7.5 Artifact Store

职责：

- 存知识产物，而不是只存“原始向量”
- 支持无向量模式和多后端模式

## 7.6 Observability & Policy

职责：

- 成本追踪
- Provider 使用记录
- 数据来源跟踪
- 安全与权限策略

---

# 八、每层的抽象接口定义

以下接口采用伪 TypeScript 风格，只表达契约，不绑定具体语言。

## 8.1 LLM 层接口

```ts
interface LLMProvider {
  id(): string
  capabilities(): LLMCapabilities
  generate(request: LLMRequest): Promise<LLMResponse>
  stream?(request: LLMRequest): AsyncIterable<LLMEvent>
  validateConfig(config: ProviderConfig): Promise<ValidationResult>
}

interface LLMCapabilities {
  supportsTools: boolean
  supportsJsonSchema: boolean
  supportsVision: boolean
  supportsLongContext: boolean
  supportsReasoningBudget: boolean
  maxContextTokens?: number
  maxOutputTokens?: number
}

interface LLMRequest {
  model: string
  system?: string
  input: Message[]
  tools?: ToolSpec[]
  responseFormat?: ResponseFormat
  temperature?: number
  metadata?: Record<string, any>
}
```

### 设计要点

- 统一描述 capability，而不是假定每个 provider 都一样
- `tools` 应沿用 JSON Schema / function calling 思维模型
- 不支持 tools/json schema 的 provider，允许 adapter 内部降级

## 8.2 Embedding 层接口

```ts
interface EmbeddingProvider {
  id(): string
  profile(): EmbeddingProfile
  embed(request: EmbeddingRequest): Promise<EmbeddingResponse>
  validateConfig(config: ProviderConfig): Promise<ValidationResult>
}

interface EmbeddingProfile {
  model: string
  dimensions: number
  metric: 'cosine' | 'dot' | 'l2'
  normalized: boolean
}
```

### 设计要点

- embedding 不是可随便混用的
- 每个向量索引都必须绑定 `embedding_profile`
- 切换 embedding model 时，应重建新 namespace/index，而不是覆盖老数据

## 8.3 Vector Store 接口

```ts
interface VectorStore {
  id(): string
  ensureIndex(spec: VectorIndexSpec): Promise<void>
  upsert(records: EmbeddingRecord[]): Promise<void>
  search(query: VectorQuery): Promise<VectorHit[]>
  delete(filter: Record<string, any>): Promise<void>
}
```

### 设计要点

- AllInOne 不应直接暴露 Qdrant/Weaviate 的私有 API 到业务层
- 业务层只认 `search/upsert/delete`

## 8.4 Graph Store 接口

```ts
interface GraphStore {
  id(): string
  upsertNodes(nodes: GraphNode[]): Promise<void>
  upsertEdges(edges: GraphEdge[]): Promise<void>
  querySubgraph(query: GraphQuery): Promise<GraphResult>
}
```

### 设计要点

- 内部只定义图语义，不绑定 Cypher 或特定图库
- 没有图数据库时，可以用简化实现（SQLite/JSON adjacency）

## 8.5 Blob / Document Store 接口

```ts
interface BlobStore {
  put(blob: BlobObject): Promise<BlobRef>
  get(ref: BlobRef): Promise<BlobObject>
  delete(ref: BlobRef): Promise<void>
}

interface ArtifactStore {
  save(artifact: KnowledgeArtifact): Promise<void>
  load(id: string): Promise<KnowledgeArtifact | null>
  list(filter?: ArtifactFilter): Promise<KnowledgeArtifact[]>
}
```

### 设计要点

- 向量库不应承担 artifact store 的全部职责
- AllInOne 应把“知识资产”和“检索索引”视为两层

## 8.6 Connector 接口

```ts
interface Connector {
  id(): string
  capabilities(): ConnectorCapabilities
  scan(source: SourceConfig, cursor?: CursorState): AsyncIterable<RawDocument>
  fetch?(id: string): Promise<RawDocument>
  checkpoint?(cursor: CursorState): Promise<void>
}
```

### 设计要点

- 采集是开放的，但输入统一为 `RawDocument`
- Connector 不直接向下游暴露 provider 私有结构

## 8.7 Tool / MCP 接口

```ts
interface ToolAdapter {
  id(): string
  spec(): ToolSpec
  invoke(input: ToolInput): Promise<ToolOutput>
}

interface MCPGateway {
  listServers(): Promise<MCPServerInfo[]>
  listTools(serverId: string): Promise<ToolSpec[]>
  callTool(serverId: string, tool: string, input: any): Promise<ToolOutput>
}
```

### 设计要点

- 内部工具与 MCP 工具应能统一被编排器消费
- 外部世界优先兼容 MCP

---

# 九、AllInOne 的固定层与开放层：最终建议

## 9.1 固定层（平台必须拥有）

| 层 | 是否固定 | 原因 |
|---|---|---|
| Core runtime architecture | 是 | 否则系统没有统一行为 |
| Config format & scope | 是 | 否则用户选择无从落地 |
| Provider SPI contracts | 是 | 否则无法替换组件 |
| Artifact schema | 是 | 否则资产不可复用 |
| Task semantics | 是 | 否则 workflow 不稳定 |
| Observability schema | 是 | 否则无法调试和算成本 |

## 9.2 开放层（用户应可选择）

| 层 | 是否开放 | 说明 |
|---|---|---|
| LLM provider | 是 | Claude/GPT/Gemini/DeepSeek/local |
| Model | 是 | 同 provider 下不同模型可切换 |
| Embedding model | 是 | 可无 embedding 或多 embedding |
| Retrieval backend | 是 | 可无向量库、可 pgvector、可 Qdrant |
| Graph backend | 是 | 可无图库、可 Neo4j、可 Memgraph |
| Connectors | 是 | GitHub/RSS/MCP/本地文件夹等 |
| Reranker | 是 | 可不用，也可选 API / 本地模型 |

---

# 十、具体技术栈方案

## 10.1 LLM 层：支持 Claude / GPT / Gemini / DeepSeek / 本地模型切换

### 推荐方案

AllInOne 采用 **Provider Adapter + Capability Matrix + Routing Policy** 三件套。

#### Provider Adapter

每个 provider 一个 adapter：

- `anthropic`
- `openai`
- `google-gemini`
- `deepseek`
- `azure-openai`
- `bedrock`
- `openai-compatible`

#### Capability Matrix

系统维护如下能力矩阵：

- 是否支持 tool calling
- 是否支持 strict JSON schema
- 是否支持 long context
- 是否支持 image/file inputs
- 是否支持 streaming
- 成本区间
- 延迟等级
- 数据驻留/隐私级别

#### Routing Policy

允许三种路由模式：

- `user_pinned`: 用户指定 provider/model
- `profile_pinned`: 工作流 profile 指定
- `capability_routed`: 系统按能力匹配

### 为什么这样设计

这样可以做到：

- 用户强控时，用户说了算
- 用户不想管时，系统按能力匹配
- 不会因为某个模型下线，整个系统瘫痪

## 10.2 Embedding 层：支持多 embedding 模型

### 推荐方案

- Embedding 作为完全独立 provider 层
- 每个索引绑定一个 `embedding_profile_id`
- 不同 embedding profile 拥有独立 namespace/collection

### 设计规则

- 切换 embedding model = 新建索引，不覆盖旧索引
- 若未配置 embedding provider，则退化到：
  - keyword search
  - direct artifact scan
  - pure LLM retrieval

### 为什么这样设计

embedding 是可选增强，不应是系统启动前提。

## 10.3 存储层：支持多种向量数据库 / 图数据库

### 向量存储建议

#### 最小级别

- `none`
- `sqlite-fts`

#### 标准级别

- `postgres + pgvector`

#### 高级级别

- `qdrant`
- `weaviate`
- `milvus`
- `opensearch hybrid`

### 图存储建议

#### 最小级别

- `none`
- `sqlite-graph-lite`

#### 高级级别

- `neo4j`
- `memgraph`

### 为什么这样设计

- 大部分个人用户根本不需要一上来就上图数据库
- 很多知识提取工作只靠 artifact store + 关键词/语义检索就够用
- 图数据库适合复杂关系探索，而不是系统默认前置依赖

## 10.4 采集层：支持多种数据源

### 统一输入模型

无论来自哪里，最终都归一化成：

```ts
interface RawDocument {
  id: string
  sourceType: string
  title?: string
  content: string
  metadata: Record<string, any>
  updatedAt?: string
}
```

### 推荐支持的数据源

- GitHub / GitLab repositories
- 本地目录
- RSS / 网站 / 文档站
- Markdown / PDF / HTML
- Notion / Confluence
- MCP resources
- 自定义 HTTP / webhook / queue connector

### 为什么这样设计

采集层的价值在于“可接入”，不是“标准化一切外部世界”。
标准化应在 RawDocument 层完成。

---

# 十一、最小依赖原则：AllInOne 的最小可运行配置

## 11.1 理想状态

> **只需要一个 LLM API key，就能跑起来。**

## 11.2 最小可运行依赖建议

### 必需

- 一个 LLM provider API key（或一个本地 OpenAI-compatible endpoint）
- 本地文件系统
- SQLite

### 默认不开启

- embedding provider
- vector DB
- graph DB
- reranker
- external queue

## 11.3 最小模式下系统能做什么

即使只用这套最小配置，也应支持：

- 基础内容采集
- 基础切片
- 纯 LLM 摘要 / 提取 / 结构化输出
- 本地 SQLite + 文件系统存 artifact
- 关键词检索 / 简单 metadata filter
- MCP 工具接入（如果用户配置了）

## 11.4 不应要求的东西

最小模式下，不应要求用户先准备：

- Docker Compose 全家桶
- Qdrant
- Neo4j
- 特定 embedding model
- 特定 GPU 环境

---

# 十二、渐进式扩展路径

这是 AllInOne 的关键产品策略之一。

## Stage 0：Pure LLM 模式

### 依赖

- 1 个 LLM key
- SQLite + 文件系统

### 能力

- 采集
- 提取
- 结构化知识资产
- 关键词检索

### 适用

- 个人用户
- 概念验证
- 低成本起步

## Stage 1：加 Embedding

### 新增

- embedding provider

### 获得

- 语义相似检索
- 更稳定的 chunk recall

### 注意

- 仍不强制向量数据库，可以先用本地简化索引

## Stage 2：加 Vector Store

### 新增

- pgvector / Qdrant / Weaviate 等

### 获得

- 大规模语义检索
- 多 namespace 管理
- 更好的召回性能

## Stage 3：加 Reranker / Hybrid Retrieval

### 新增

- reranker API 或本地 cross-encoder
- lexical + semantic 混合检索

### 获得

- 更高质量的 top-k 结果

## Stage 4：加 Graph Store

### 新增

- Neo4j / Memgraph / graph-lite

### 获得

- 跨实体关系探索
- 决策路径/依赖关系可视化
- 更强的知识结构导航

### 注意

图数据库应是“增强器”，不是默认前置依赖。

## Stage 5：MCP + A2A 生态扩展

### 新增

- 外部 MCP servers
- future A2A agent integration

### 获得

- 工具与数据源生态接入
- 多 agent 协作扩展

---

# 十三、配置作用域设计：把选择权真正交给用户

AllInOne 建议支持四层作用域：

1. `global`
2. `project`
3. `workflow`
4. `task`

覆盖优先级：

```text
task > workflow > project > global
```

## 示例配置（建议）

```yaml
defaults:
  llm_profile: fast-default
  retrieval_profile: minimal
  storage_profile: local-default

llm_profiles:
  fast-default:
    provider: openai
    model: gpt-4.1-mini
  deep-reasoning:
    provider: anthropic
    model: claude-opus-4-1
  local-private:
    provider: openai-compatible
    base_url: http://localhost:11434/v1
    model: qwen2.5-coder:32b

embedding_profiles:
  off:
    provider: none
  openai-small:
    provider: openai
    model: text-embedding-3-small
  local-bge:
    provider: local
    model: BAAI/bge-m3

retrieval_profiles:
  minimal:
    mode: keyword_only
  semantic:
    mode: vector
    embedding_profile: openai-small
    vector_store: pgvector-default
  hybrid:
    mode: hybrid
    embedding_profile: local-bge
    vector_store: qdrant-default
    reranker: jina-reranker

storage_profiles:
  local-default:
    artifact_store: sqlite+fs
    vector_store: none
    graph_store: none
  pgvector-default:
    artifact_store: postgres
    vector_store: pgvector
    graph_store: none
  graph-heavy:
    artifact_store: postgres
    vector_store: qdrant-default
    graph_store: neo4j-default
```

### 为什么这样设计

- 用户可以只改 profile，不用懂底层 provider 细节
- 高级用户仍可 override 具体 provider
- 同一个系统可同时支持低门槛与高定制

---

# 十四、AllInOne 的推荐技术栈基线

在不违背“开放选择”原则的前提下，我建议 AllInOne 自己固定的基线实现如下：

## 14.1 Control Plane

建议固定：

- **TypeScript / Node.js** 作为主控制层

原因：

- MCP / agent tooling / JSON schema / config tooling 生态强
- CLI、服务端、插件协议、配置系统实现效率高
- 与现代 AI tool ecosystem 兼容性好

## 14.2 Optional Worker Plane

建议允许：

- Python sidecar / worker

原因：

- embedding、reranker、本地 ML、数据处理等场景，Python 生态成熟
- 但 Python 不应成为系统唯一主 runtime

## 14.3 Core Storage Baseline

建议固定默认：

- 文件系统
- SQLite

原因：

- 这是最接近“只要能运行就行”的基线
- 对个人用户最友好

## 14.4 Advanced Storage Options

建议开放：

- Postgres / pgvector
- Qdrant / Weaviate / Milvus
- Neo4j / Memgraph

原因：

- 高级需求存在，但不该成为强依赖

---

# 十五、最终技术栈策略建议

如果只用一句话概括：

> **AllInOne 应该固定“协议、抽象、数据契约、任务语义”，开放“模型、嵌入、检索、存储、采集和工具来源”。**

具体来说：

## 必须固定

- 内部数据格式
- Provider SPI
- 配置系统
- 作用域覆盖规则
- Task lifecycle
- Artifact schema
- 观察性标准

## 必须开放

- LLM provider / model
- embedding provider / model
- vector backend
- graph backend
- connector / ingestion source
- reranker
- tool sources（优先 MCP）

## 最小可运行依赖

- 1 个 LLM API key
- 文件系统 + SQLite

## 渐进扩展路径

- 纯 LLM
- + embedding
- + vector store
- + reranker / hybrid
- + graph store
- + MCP / A2A ecosystem

---

# 十六、给 AllInOne 的落地建议（产品层）

最后给一个非常明确的产品建议：

## 16.1 安装体验

安装第一天，用户只应看到两个问题：

1. 你想用哪个 LLM provider？
2. 你现在是否要开启“增强检索”？

而不应该一上来就看到：

- 你要部署哪种图数据库？
- 你要选哪个 embedding 维度？
- 你要不要先配 reranker？

## 16.2 设置面板

设置面板应按“能力”组织，而不是按“厂商”组织：

- 推理模型
- 快速模型
- 嵌入模型
- 检索模式
- 存储后端
- 数据源
- 工具连接

## 16.3 用户心智

用户不应该被要求理解：

- MCP / A2A / function calling 的细节
- vector db vs graph db 的理论差异

用户只需要理解：

- 我是否需要更强检索
- 我是否需要本地隐私模式
- 我是否需要更便宜/更快/更强的模型

平台负责把复杂性藏在抽象层后面。

---

# 十七、参考资料（2026-03-08 调研）

以下资料为本设计的关键参考：

- Anthropic Claude Code MCP 文档  
  - https://docs.anthropic.com/en/docs/claude-code/mcp
- Anthropic MCP 总览  
  - https://docs.anthropic.com/en/docs/mcp
- Anthropic Claude Code Settings  
  - https://docs.anthropic.com/en/docs/claude-code/settings
- Anthropic Claude Code Model Config  
  - https://docs.anthropic.com/en/docs/claude-code/model-config
- Cursor API Keys / BYO Provider  
  - https://docs.cursor.com/advanced/api-keys
- Cursor MCP 文档  
  - https://docs.cursor.com/en/context/mcp
- Cursor CLI MCP 文档  
  - https://docs.cursor.com/cli/mcp
- OpenAI Function Calling Guide  
  - https://platform.openai.com/docs/guides/function-calling/how-do-i-ensure-the-model-calls-the-correct-function
- OpenAI Tools / Remote MCP 文档  
  - https://platform.openai.com/docs/guides/tools/file-search
- Google A2A 发布说明  
  - https://developers.googleblog.com/es/a2a-a-new-era-of-agent-interoperability/
- A2A 捐赠至 Linux Foundation 说明  
  - https://developers.googleblog.com/google-cloud-donates-a2a-to-linux-foundation/

---

# 十八、最终判断

AllInOne 不应被设计成“依赖一串高级组件才能跑起来的 AI 平台”。

它更应该像 OpenClaw 那样：

- **默认轻**
- **按需重**
- **能力分层**
- **协议优先**
- **用户选择优先**

只有这样，AllInOne 才能既适合个人用户，也能逐步长成更强的平台，而不会在第一天就把自己锁死在某一套技术栈上。

---

# 十九、工程落地补充：建议的代码目录与模块边界

如果 AllInOne 要真正做到“固定核心、开放外围”，那代码仓库本身也要按这个原则组织。

建议的仓库结构如下：

```text
allinone/
  config/
    allinone.yaml
    providers.yaml
    workflows.yaml
    sources.yaml
  data/
    artifacts/
    blobs/
    cache/
    sqlite/
  src/
    core/
      contracts/
        llm.ts
        embedding.ts
        vector-store.ts
        graph-store.ts
        blob-store.ts
        connector.ts
        reranker.ts
        tool.ts
        artifact.ts
        config.ts
      types/
      errors/
      registry/
      observability/
    runtime/
      orchestrator/
      router/
      retrieval/
      ingestion/
      workflows/
      policy/
    providers/
      llm/
        anthropic/
        openai/
        gemini/
        deepseek/
        openai-compatible/
      embedding/
        openai/
        voyage/
        jina/
        local/
      vector-store/
        none/
        sqlite-fts/
        pgvector/
        qdrant/
        weaviate/
      graph-store/
        none/
        sqlite-graph-lite/
        neo4j/
        memgraph/
      blob-store/
        filesystem/
        s3/
      connectors/
        github/
        gitlab/
        rss/
        local-files/
        mcp-resource/
      tools/
        mcp/
        local/
    api/
    cli/
  docs/
  tests/
```

## 为什么这样拆

### `core/contracts`

这里必须极度稳定。它定义的是 AllInOne 的**平台语言**。

一旦这里频繁变化，所有 provider adapter 都会被拖着改。

### `runtime`

这里负责“编排逻辑”。

- 怎么选 provider
- 怎么做 fallback
- 怎么做 retrieval planning
- 怎么做 task execution

它不应直接依赖某个具体 provider SDK。

### `providers`

这里是“可替换组件区”。

任何供应商适配，都只应在这里扩张，而不应该渗透进 `runtime`。

---

# 二十、配置文件与对象定义（工程优先版）

## 20.1 建议的配置文件拆分

为了兼顾简单与扩展，建议采用“主配置 + 分域配置”的方式：

```text
config/
  allinone.yaml      # 总开关、默认 profile、作用域策略
  providers.yaml     # 各类 provider 实例
  workflows.yaml     # 工作流与任务路由
  sources.yaml       # 数据源与 connector 配置
  policies.yaml      # 成本、隐私、fallback、权限策略
```

### 原则

- 新手用户只改 `allinone.yaml`
- 高级用户再拆分 provider/workflow/source/policy
- 内部加载器统一合并为一个 `ResolvedConfig`

## 20.2 核心配置对象定义

```ts
interface AllInOneConfig {
  defaults: DefaultConfig
  providers: ProviderRegistryConfig
  profiles: ProfileRegistryConfig
  workflows?: WorkflowRegistryConfig
  sources?: SourceRegistryConfig
  policies?: PolicyConfig
}

interface DefaultConfig {
  llmProfile: string
  retrievalProfile: string
  storageProfile: string
  workflowProfile?: string
  scopePrecedence?: ScopeLevel[]
}

type ScopeLevel = 'global' | 'project' | 'workflow' | 'task'
```

## 20.3 Provider 配置对象

```ts
interface ProviderRegistryConfig {
  llm?: LLMProviderConfig[]
  embedding?: EmbeddingProviderConfig[]
  vectorStore?: VectorStoreConfig[]
  graphStore?: GraphStoreConfig[]
  blobStore?: BlobStoreConfig[]
  reranker?: RerankerConfig[]
  connectors?: ConnectorConfig[]
  toolGateways?: ToolGatewayConfig[]
}

interface BaseProviderConfig {
  id: string
  adapter: string
  enabled: boolean
  auth?: AuthConfig
  endpoint?: EndpointConfig
  options?: Record<string, any>
  tags?: string[]
}

interface AuthConfig {
  apiKeyEnv?: string
  tokenEnv?: string
  oauthProfile?: string
  apiKeyLiteral?: string
}

interface EndpointConfig {
  baseUrl?: string
  timeoutMs?: number
  headers?: Record<string, string>
}
```

## 20.4 LLM Provider 配置

```ts
interface LLMProviderConfig extends BaseProviderConfig {
  kind: 'llm'
  models: LLMModelConfig[]
  defaultModel?: string
  capabilityOverrides?: Partial<LLMCapabilities>
}

interface LLMModelConfig {
  id: string
  providerModelId: string
  costTier?: 'low' | 'medium' | 'high'
  latencyTier?: 'fast' | 'balanced' | 'slow'
  reasoningTier?: 'light' | 'deep'
  maxContextTokens?: number
  maxOutputTokens?: number
}
```

## 20.5 Retrieval / Storage Profile 配置

```ts
interface ProfileRegistryConfig {
  llm: LLMProfile[]
  retrieval: RetrievalProfile[]
  storage: StorageProfile[]
  workflow?: WorkflowProfile[]
}

interface LLMProfile {
  id: string
  primary: ModelSelector
  fallback?: ModelSelector[]
  routing?: RoutingPolicy
}

interface RetrievalProfile {
  id: string
  mode: 'keyword_only' | 'vector' | 'hybrid' | 'graph' | 'hybrid_graph'
  embeddingProfile?: string
  vectorStore?: string
  graphStore?: string
  reranker?: string
  topK?: number
  candidateK?: number
}

interface StorageProfile {
  id: string
  artifactStore: string
  blobStore: string
  vectorStore?: string
  graphStore?: string
}
```

## 20.6 Connector 配置

```ts
interface ConnectorConfig extends BaseProviderConfig {
  kind: 'connector'
  sourceType: 'github' | 'gitlab' | 'rss' | 'local-files' | 'http' | 'mcp-resource' | 'notion'
  schedule?: string
  defaults?: Record<string, any>
}

interface SourceRegistryConfig {
  items: SourceConfig[]
}

interface SourceConfig {
  id: string
  connectorId: string
  enabled: boolean
  params: Record<string, any>
  checkpointKey?: string
  tags?: string[]
}
```

---

# 二十一、Provider Manifest 与 Capability Registry 设计

AllInOne 不应该把“能力描述”写死在代码里。建议每个 provider adapter 都暴露一个 manifest。

## 21.1 Provider Manifest

```json
{
  "id": "anthropic-main",
  "kind": "llm",
  "adapter": "anthropic",
  "enabled": true,
  "models": [
    {
      "id": "claude-sonnet",
      "providerModelId": "claude-sonnet-4-5",
      "latencyTier": "balanced",
      "reasoningTier": "deep",
      "maxContextTokens": 200000
    }
  ],
  "capabilities": {
    "supportsTools": true,
    "supportsJsonSchema": true,
    "supportsVision": true,
    "supportsLongContext": true,
    "supportsReasoningBudget": true
  },
  "auth": {
    "apiKeyEnv": "ANTHROPIC_API_KEY"
  },
  "endpoint": {
    "baseUrl": "https://api.anthropic.com",
    "timeoutMs": 120000
  }
}
```

## 21.2 Capability Registry 运行时对象

```ts
interface CapabilityRegistryEntry {
  providerId: string
  kind: ProviderKind
  enabled: boolean
  health: 'unknown' | 'healthy' | 'degraded' | 'down'
  capabilities: Record<string, any>
  scopes: ScopeLevel[]
  tags: string[]
}
```

## 21.3 工程规则

- `providers.yaml` 是静态配置来源
- `Capability Registry` 是运行时解析结果
- 运行时 health check 只更新 registry，不修改原始配置
- `adapter` 负责把 provider 私有特性映射到统一 capability 字段

---

# 二十二、最小可运行文件集合（只要一个 LLM key）

这是最重要的工程落地部分。

## 22.1 最小文件布局

```text
allinone/
  config/
    allinone.yaml
  data/
    sqlite/
    artifacts/
    blobs/
  .env
```

## 22.2 最小 `.env`

```bash
OPENAI_API_KEY=sk-xxxx
```

## 22.3 最小 `config/allinone.yaml`

```yaml
defaults:
  llmProfile: quickstart
  retrievalProfile: minimal
  storageProfile: local-default
  scopePrecedence: [task, workflow, project, global]

providers:
  llm:
    - id: openai-main
      kind: llm
      adapter: openai
      enabled: true
      auth:
        apiKeyEnv: OPENAI_API_KEY
      endpoint:
        baseUrl: https://api.openai.com/v1
        timeoutMs: 120000
      models:
        - id: gpt-fast
          providerModelId: gpt-4.1-mini
          latencyTier: fast
          reasoningTier: light
          maxContextTokens: 128000

  blobStore:
    - id: fs-default
      kind: blob-store
      adapter: filesystem
      enabled: true
      options:
        rootDir: ./data/blobs

  vectorStore:
    - id: none
      kind: vector-store
      adapter: none
      enabled: true

  graphStore:
    - id: none
      kind: graph-store
      adapter: none
      enabled: true

profiles:
  llm:
    - id: quickstart
      primary:
        providerId: openai-main
        modelId: gpt-fast

  retrieval:
    - id: minimal
      mode: keyword_only
      topK: 8

  storage:
    - id: local-default
      artifactStore: sqlite-artifacts
      blobStore: fs-default
      vectorStore: none
      graphStore: none
```

## 22.4 最小模式的运行语义

在这个模式下：

- 不构建 embedding
- 不访问向量库
- 不访问图数据库
- 只做：
  - artifact 落盘
  - SQLite metadata 管理
  - keyword search / metadata filtering
  - LLM 直接提取与总结

这就是 AllInOne 应该交付给用户的 quickstart 体验。

---

# 二十三、渐进式扩展的配置样例

## 23.1 Stage 1：加 Embedding，不加向量库

```yaml
providers:
  embedding:
    - id: openai-embed
      kind: embedding
      adapter: openai
      enabled: true
      auth:
        apiKeyEnv: OPENAI_API_KEY
      models:
        - id: text-embedding-3-small
          providerModelId: text-embedding-3-small
      options:
        dimensions: 1536
        metric: cosine

profiles:
  retrieval:
    - id: semantic-lite
      mode: vector
      embeddingProfile: openai-embed-small
      vectorStore: sqlite-vec-lite
      topK: 12
```

## 23.2 Stage 2：加 pgvector

```yaml
providers:
  vectorStore:
    - id: pgvector-main
      kind: vector-store
      adapter: pgvector
      enabled: true
      endpoint:
        baseUrl: postgres://user:pass@localhost:5432/allinone

profiles:
  storage:
    - id: postgres-semantic
      artifactStore: postgres-artifacts
      blobStore: fs-default
      vectorStore: pgvector-main
      graphStore: none
```

## 23.3 Stage 3：加 Qdrant + reranker

```yaml
providers:
  vectorStore:
    - id: qdrant-main
      kind: vector-store
      adapter: qdrant
      enabled: true
      endpoint:
        baseUrl: http://localhost:6333

  reranker:
    - id: jina-reranker
      kind: reranker
      adapter: jina
      enabled: true
      auth:
        apiKeyEnv: JINA_API_KEY

profiles:
  retrieval:
    - id: hybrid-prod
      mode: hybrid
      embeddingProfile: local-bge-m3
      vectorStore: qdrant-main
      reranker: jina-reranker
      candidateK: 50
      topK: 10
```

## 23.4 Stage 4：加 Neo4j

```yaml
providers:
  graphStore:
    - id: neo4j-main
      kind: graph-store
      adapter: neo4j
      enabled: true
      endpoint:
        baseUrl: bolt://localhost:7687
      auth:
        tokenEnv: NEO4J_AUTH

profiles:
  storage:
    - id: graph-heavy
      artifactStore: postgres-artifacts
      blobStore: fs-default
      vectorStore: qdrant-main
      graphStore: neo4j-main
```

---

# 二十四、运行时路由与 fallback 算法（可直接实现）

为了让工程实现更直观，下面给出一个建议的路由算法。

## 24.1 LLM 路由算法

```ts
function resolveLLM(task: TaskContext, config: ResolvedConfig, registry: CapabilityRegistry) {
  const scoped = resolveScopedLLMProfile(task, config)
  const candidates = [scoped.primary, ...(scoped.fallback ?? [])]

  for (const candidate of candidates) {
    const provider = registry.get(candidate.providerId)
    if (!provider || !provider.enabled || provider.health === 'down') continue
    if (!supportsTask(provider.capabilities, task.requirements)) continue
    return candidate
  }

  throw new Error('NoCompatibleLLMProvider')
}
```

## 24.2 Retrieval 路由算法

```ts
function resolveRetrieval(task: TaskContext, config: ResolvedConfig) {
  const profile = resolveScopedRetrievalProfile(task, config)

  if (profile.mode === 'keyword_only') {
    return { mode: 'keyword_only' }
  }

  if (profile.mode === 'vector' && !profile.embeddingProfile) {
    return { mode: 'keyword_only', degraded: true, reason: 'missing_embedding_profile' }
  }

  if (profile.mode === 'graph' && !profile.graphStore) {
    return { mode: 'keyword_only', degraded: true, reason: 'missing_graph_store' }
  }

  return profile
}
```

## 24.3 发布与降级原则

- provider down → 自动切 fallback
- capability mismatch → 自动切兼容 provider
- vector store unavailable → 降级到 keyword search
- graph store unavailable → 关闭 graph augmentation，不阻断主流程
- embedding missing → 允许进入纯 LLM 模式

## 24.4 工程上必须坚持的规则

- **降级优先于失败**，除非任务明确声明“必须使用某种能力”
- **用户 pin 的 provider 不自动偷偷改写**，只在失败时给出可解释 fallback 说明
- 所有降级都必须记录到 trace / log / task result metadata

---

# 二十五、建议的实施顺序（工程团队视角）

如果要把这份设计真正落地，我建议按下面顺序开发：

## Phase 1：Core Contracts + Quickstart

先做：

- `core/contracts/*`
- `config loader`
- `provider registry`
- `openai llm adapter`
- `filesystem + sqlite artifact store`
- `keyword-only retrieval`

目标：

- 一个 LLM key 即可跑通

## Phase 2：Provider Multiplexing

再做：

- anthropic / gemini / deepseek / openai-compatible adapters
- profile-based routing
- scoped overrides
- fallback semantics

## Phase 3：Embedding + Vector Store

再做：

- embedding SPI
- pgvector / qdrant adapters
- namespace-by-embedding-profile 规则

## Phase 4：Graph + MCP

最后做：

- graph SPI
- neo4j / memgraph adapter
- MCP tool gateway / MCP resource connector
- future A2A compatibility layer

这个顺序能最大程度保证：

- 最小依赖先落地
- 高级能力后加装
- 不会一上来把系统做成重型基础设施项目

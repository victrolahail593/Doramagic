# Doramagic v2 技术框架与开发需求

> 日期: 2026-03-11
> 状态: 技术规格文档 v1.0
> 基于: doramagic-v2-redesign.md + v2-tech-gap-analysis.md + v1.0 技术资产审计
> 目标读者: 核心开发团队、架构评审

---

## 1. 系统总览

### 一句话定义

**Doramagic v2 是基于 MCP 协议和自适应 Agent 架构的"超级抄作业引擎"——它理解用户的模糊需求，通过语义发现从开源项目、MCP Server 和 OpenClaw Skill 中提取知识、资源和模式，像拼乐高一样自动组装出开袋即食的个性化 AI 技能，并通过反馈闭环持续进化。**

### 架构全景图

```
用户的一句话需求
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Orchestrator Agent (总控)                      │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │              共享工作记忆 (Shared Working Memory)          │     │
│  │  ┌──────────┬──────────┬──────────┬──────────┬────────┐ │     │
│  │  │need_     │source_   │cards_    │skill_    │feedback│ │     │
│  │  │profile   │map       │registry  │draft     │_log    │ │     │
│  │  └──────────┴──────────┴──────────┴──────────┴────────┘ │     │
│  └─────────────────────────────────────────────────────────┘     │
│                                                                   │
│  自适应状态机：根据当前状态 + 质量信号动态调度子代理                    │
│                                                                   │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │
│  │ 需求    │ │ 发现    │ │ 提取    │ │ 拼装    │ │ 交付    │        │
│  │ Agent  │ │ Agent  │ │ Agent  │ │ Agent  │ │ Agent  │        │
│  │        │ │        │ │  ×N    │ │        │ │        │        │
│  └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘        │
│      │          │          │          │          │               │
│  ┌───┴──────────┴──────────┴──────────┴──────────┴───┐          │
│  │                   工具层 (Tool Layer)                │          │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐           │          │
│  │  │MCP Client│ │AST/Code  │ │Web Search│           │          │
│  │  │(资源调用) │ │Indexer   │ │& Semantic│           │          │
│  │  └──────────┘ └──────────┘ └──────────┘           │          │
│  └───────────────────────────────────────────────────┘          │
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐       │
│  │              MCP 资源层 (MCP Resource Layer)            │       │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │       │
│  │  │akshare  │ │Web      │ │File     │ │Custom   │    │       │
│  │  │MCP      │ │Search   │ │System   │ │Generated│    │       │
│  │  │Server   │ │MCP      │ │MCP      │ │MCP      │    │       │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘    │       │
│  └───────────────────────────────────────────────────────┘       │
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐       │
│  │           MEMORY.md 持久层 (Feedback Loop)              │       │
│  │  用户偏好 │ Skill 运行日志 │ 资源健康状态 │ 学习记录     │       │
│  └───────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

### 核心设计原则

| 原则 | 含义 | 技术映射 |
|------|------|---------|
| **MCP-first** | 资源通过 MCP 协议接入，而非内嵌代码调用 | 生成的 Skill 通过 MCP Client 调用资源，资源可热插拔 |
| **自适应循环** | Agent 根据质量信号动态调度，而非线性流水线 | Orchestrator 状态机 + 回退/前进规则 |
| **AST-aware** | 代码理解基于语法树而非文本压缩 | Tree-sitter 解析 + 代码嵌入索引 |
| **反馈闭环** | 生成的 Skill 持续进化，而非一次性交付 | MEMORY.md 读写 + Skill 体检 + 参数微调 |
| **OpenClaw-native** | 深度利用平台原生能力 | MEMORY.md、AGENTS.md、MCP 集成、多模型调度、Skill 间调用 |

---

## 2. Agent 架构设计

### 2.1 Orchestrator Agent

**职责**: 总控代理，理解全局目标，根据当前状态和质量信号动态调度子代理。

**不是**线性阶段执行器，**而是**自适应状态机。

#### 状态机定义

```
                    ┌──────────────────────────────────┐
                    │                                  │
                    ▼                                  │
    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────┴───┐  ┌──────────┐
    │          │  │          │  │          │  │          │  │          │
───▶│  NEED    ├─▶│ DISCOVER ├─▶│ EXTRACT  ├─▶│ ASSEMBLE ├─▶│ DELIVER  │
    │          │  │          │  │          │  │          │  │          │
    └──────────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
                       │             │             │             │
                       │             │             │             │
                       ▼             ▼             ▼             ▼
                    回退到NEED    回退到DISCOVER  回退到EXTRACT  回退到ASSEMBLE
                    (需求模糊)   (源泉不足)     (卡片不足)    (冒烟失败)
```

**状态定义**:

```typescript
// orchestrator-states.ts
type OrchestratorState =
  | 'IDLE'          // 等待用户输入
  | 'NEED'          // 需求理解中
  | 'DISCOVER'      // 源泉发现中
  | 'EXTRACT'       // 多源提取中
  | 'ASSEMBLE'      // 智能拼装中
  | 'DELIVER'       // 交付验证中
  | 'COMPLETE'      // 成功完成
  | 'FAILED';       // 终止（超过最大重试次数）

interface OrchestratorContext {
  state: OrchestratorState;
  retryCount: Record<OrchestratorState, number>;
  maxRetries: Record<OrchestratorState, number>;  // 默认: 每阶段最多 2 次回退
  workingMemory: SharedWorkingMemory;
  qualitySignals: QualitySignal[];
  userInteractionLog: UserInteraction[];
}
```

#### 状态转换规则

| 当前状态 | 前进条件 | 回退条件 | 回退目标 |
|---------|---------|---------|---------|
| NEED | need_profile 包含 core_problem + trigger + expected_output | 对话 5 轮仍不明确 | 终止并提示用户重新描述 |
| DISCOVER | >= 1 主力源泉 + >= 1 资源源泉 + 用户确认 | 搜索结果相关度 < 0.6 | NEED（补充搜索关键词） |
| EXTRACT | >= 3 知识卡 + >= 2 资源卡 + >= 1 模式卡 + 验证通过 | 验证失败率 > 20% | DISCOVER（换源泉）或重试 EXTRACT |
| ASSEMBLE | Skill 包结构完整 + 资源绑定成功 | 资源绑定失败（API 不可达） | EXTRACT（补充备选资源） |
| DELIVER | 冒烟测试通过 | 冒烟测试失败 | ASSEMBLE（修复 Skill） |

#### Orchestrator 核心逻辑

```typescript
// orchestrator.ts
import { Agent, handoff } from '@anthropic-ai/agent-sdk';

const orchestrator = new Agent({
  name: 'doramagic-orchestrator',
  model: 'claude-sonnet',  // 调度逻辑用 Sonnet 即可
  instructions: `你是 Doramagic 的总控代理。你的职责是：
    1. 理解用户需求的全局目标
    2. 根据共享工作记忆的当前状态，决定下一步调度哪个子代理
    3. 监控质量信号，必要时回退到之前的阶段
    4. 确保最终交付质量满足门控标准`,

  tools: [
    readWorkingMemory,
    writeWorkingMemory,
    checkQualityGate,
    reportProgress,
  ],

  handoffs: [
    handoff(needAgent,      { condition: 'state === NEED' }),
    handoff(discoverAgent,  { condition: 'state === DISCOVER' }),
    handoff(extractAgent,   { condition: 'state === EXTRACT' }),
    handoff(assembleAgent,  { condition: 'state === ASSEMBLE' }),
    handoff(deliverAgent,   { condition: 'state === DELIVER' }),
  ],
});
```

### 2.2 五个子代理详细定义

#### 2.2.1 需求 Agent (Need Agent)

| 属性 | 定义 |
|------|------|
| **角色** | 产品顾问——通过苏格拉底对话挖掘用户真实需求 |
| **模型** | claude-sonnet（对话任务） |
| **输入** | 用户的自然语言需求描述 |
| **输出** | need_profile（写入共享工作记忆） |
| **工具集** | readMemory（读取用户历史偏好）、readInstalledSkills（读取已安装 Skill 列表）、writeWorkingMemory |
| **成功标准** | need_profile 包含全部 7 个必填字段 |
| **失败处理** | 对话超 5 轮仍不明确 → 向 Orchestrator 报告，建议用户提供更具体描述 |

**继承自 v1.0**: `skill-forge/stages/STAGE-1-discovery.md` 的对话策略和产出格式。

**v2 增强**:
- 新增 `user_environment` 字段（平台、可用模型、已安装 Skill）
- 新增 `search_keywords` 字段（为发现 Agent 提供初始搜索方向）
- 读取 MEMORY.md 中的用户历史偏好

```typescript
const needAgent = new Agent({
  name: 'need-agent',
  model: 'claude-sonnet',
  instructions: `{baseDir}/agents/AGENT-need.md`,
  tools: [readMemory, readInstalledSkills, writeWorkingMemory],
});
```

#### 2.2.2 发现 Agent (Discover Agent)

| 属性 | 定义 |
|------|------|
| **角色** | 开源生态专家 + Skill 市场分析师 |
| **模型** | claude-sonnet（搜索+分析） |
| **输入** | need_profile（从共享工作记忆读取） |
| **输出** | source_map（写入共享工作记忆） |
| **工具集** | webSearch、githubSearch、mcpRegistrySearch、skillMarketSearch、writeWorkingMemory |
| **成功标准** | >= 1 主力源泉 + >= 1 资源/MCP 源泉，用户确认方向 |
| **失败处理** | 搜索结果不足 → 请求 Orchestrator 回退到 NEED 阶段补充关键词 |

**继承自 v1.0**: `skill-forge/stages/STAGE-2-search.md` 的搜索框架。

**v2 增强**:
- 搜索范围扩展到四类源泉（开源项目、OpenClaw Skill、MCP Server、社区经验）
- 增加 MCP Server 注册表搜索
- 语义搜索（Phase C 实现），初期用 LLM 知识 + 关键词搜索

```typescript
const discoverAgent = new Agent({
  name: 'discover-agent',
  model: 'claude-sonnet',
  instructions: `{baseDir}/agents/AGENT-discover.md`,
  tools: [webSearch, githubSearch, mcpRegistrySearch, skillMarketSearch, writeWorkingMemory],
});
```

#### 2.2.3 提取 Agent (Extract Agent)

| 属性 | 定义 |
|------|------|
| **角色** | 提取工程师团队——并行执行知识、资源、模式提取 |
| **模型** | claude-opus（复杂分析）/ claude-sonnet（简单提取） |
| **输入** | source_map（从共享工作记忆读取） |
| **输出** | cards_registry（知识卡片 + 资源卡片 + 模式卡片，写入共享工作记忆） |
| **工具集** | cloneRepo、runExtractRepoResources、astAnalyze、codeSearch、readFile、runValidation、mcpDiscover、writeWorkingMemory |
| **成功标准** | >= 3 CC/WC/DR 卡片 + >= 2 RC 卡片 + >= 1 PT 卡片 + 验证通过率 >= 95% |
| **失败处理** | 验证失败 → 结构化反馈重试（最多 2 次）；仍失败 → 请求 Orchestrator 换源泉 |

**继承自 v1.0**: Soul Extractor Stage 1-3.5（知识提取管线）、`extract_repo_facts.py`、`validate_extraction.py`。

**v2 增强**:
- 新增资源提取子管线（生成 RC 卡片或发现/生成 MCP Server）
- 新增模式提取子管线（从 Skill/项目中提取设计模式）
- 验证脚本扩展支持 RC 和 PT 卡片类型
- 使用 AST 分析代替纯文本 Repomix（Phase C 实现）

**并行提取架构**:

```
Extract Agent (协调者)
  │
  ├─ 子任务 A: 知识提取 (per source)
  │   └─ 执行精简版 Soul Extraction (Stage 1-3.5)
  │
  ├─ 子任务 B: 资源提取 (per source)
  │   └─ 运行 extract_repo_resources.py → 发现/生成 MCP Server
  │
  ├─ 子任务 C: 模式提取 (per Skill source)
  │   └─ 分析 SKILL.md + stages/ 提取设计模式
  │
  └─ 子任务 D: 社区信号收集
      └─ GitHub Issues + SO + 论坛爬取
```

```typescript
const extractAgent = new Agent({
  name: 'extract-agent',
  model: 'claude-opus',  // 复杂分析需要 Opus
  instructions: `{baseDir}/agents/AGENT-extract.md`,
  tools: [
    cloneRepo, runExtractRepoResources, astAnalyze,
    codeSearch, readFile, runValidation,
    mcpDiscover, writeWorkingMemory,
  ],
});
```

#### 2.2.4 拼装 Agent (Assemble Agent)

| 属性 | 定义 |
|------|------|
| **角色** | Skill 架构师——选积木、设计蓝图、生成 Skill 包 |
| **模型** | claude-opus（架构设计需要深度推理） |
| **输入** | need_profile + cards_registry（从共享工作记忆读取） |
| **输出** | skill_draft（SKILL.md + stages/ + config.yaml，写入共享工作记忆） |
| **工具集** | readWorkingMemory、generateSkillPackage、bindMcpResources、injectRules、writeFile、writeWorkingMemory |
| **成功标准** | Skill 包结构完整（SKILL.md + >= 2 stages + config.yaml）+ 所有资源绑定成功 |
| **失败处理** | 资源绑定失败 → 请求 Orchestrator 回退到 EXTRACT 补充备选资源 |

**继承自 v1.0**: `skill-forge/stages/STAGE-5-generate.md` 的 Skill 生成模板。

**v2 重写**:
- 资源绑定逻辑（通过 MCP 协议而非内嵌代码）
- 规则注入逻辑（从 DR 卡片自动注入 stage 指令）
- "开袋即食"默认配置生成
- 输出从 CLAUDE.md 变为完整 Skill 包

```typescript
const assembleAgent = new Agent({
  name: 'assemble-agent',
  model: 'claude-opus',
  instructions: `{baseDir}/agents/AGENT-assemble.md`,
  tools: [
    readWorkingMemory, generateSkillPackage,
    bindMcpResources, injectRules,
    writeFile, writeWorkingMemory,
  ],
});
```

#### 2.2.5 交付 Agent (Deliver Agent)

| 属性 | 定义 |
|------|------|
| **角色** | 交付工程师 + 产品顾问 |
| **模型** | claude-sonnet（交付和测试） |
| **输入** | skill_draft（从共享工作记忆读取） |
| **输出** | 已安装的 Skill + 冒烟测试结果 + 用户引导 |
| **工具集** | installSkill、runSmokeTest、readWorkingMemory、writeMemory、reportToUser |
| **成功标准** | 冒烟测试通过 + Skill 安装成功 + 用户收到能力清单 |
| **失败处理** | 冒烟测试失败 → 请求 Orchestrator 回退到 ASSEMBLE 修复 |

```typescript
const deliverAgent = new Agent({
  name: 'deliver-agent',
  model: 'claude-sonnet',
  instructions: `{baseDir}/agents/AGENT-deliver.md`,
  tools: [
    installSkill, runSmokeTest,
    readWorkingMemory, writeMemory, reportToUser,
  ],
});
```

### 2.3 Agent 间通信机制

所有 Agent 通过 **共享工作记忆 (Shared Working Memory)** 通信，而非文件传递。

工作记忆是一个运行时内存对象，持久化为 JSON 文件以支持断点恢复。

完整 schema 见 [附录 A](#附录-a-共享工作记忆完整-schema)。

```typescript
interface SharedWorkingMemory {
  // 元信息
  session_id: string;
  created_at: string;
  updated_at: string;
  current_state: OrchestratorState;

  // Phase 1 产出
  need_profile: NeedProfile | null;

  // Phase 2 产出
  source_map: SourceMap | null;

  // Phase 3 产出
  cards_registry: {
    knowledge_cards: KnowledgeCard[];  // CC, WC, DR
    resource_cards: ResourceCard[];     // RC
    pattern_cards: PatternCard[];       // PT
    mcp_servers: McpServerRef[];        // 发现或生成的 MCP Server
    validation_report: ValidationReport | null;
  };

  // Phase 4 产出
  skill_draft: {
    skill_md: string;
    stages: StageFile[];
    config: SkillConfig;
    bound_resources: BoundResource[];
  } | null;

  // Phase 5 产出
  delivery: {
    install_path: string;
    smoke_test_result: SmokeTestResult;
    capability_summary: string;
    upgrade_suggestions: string[];
  } | null;

  // 质量信号
  quality_signals: QualitySignal[];

  // 回退历史
  rollback_history: RollbackEvent[];
}
```

### 2.4 Agent 切换 (Handoff) 模式

使用 Claude Agent SDK 的 handoff 协议实现代理间切换：

```typescript
// handoff 流程
// 1. 子代理完成任务 → 将结果写入共享工作记忆
// 2. 子代理调用 handoff() 返回控制权给 Orchestrator
// 3. Orchestrator 检查质量门控
// 4. 根据状态转换规则，handoff 到下一个子代理

// 例: Extract Agent 完成后的 handoff
function onExtractComplete(memory: SharedWorkingMemory): HandoffDecision {
  const report = memory.cards_registry.validation_report;

  if (report.overall_pass) {
    return handoff(assembleAgent, {
      context: '提取完成，验证通过，开始拼装',
    });
  }

  if (memory.quality_signals.retryCount.EXTRACT < 2) {
    return handoff(extractAgent, {
      context: `验证未通过，重试提取。反馈: ${report.structured_feedback}`,
    });
  }

  return handoff(discoverAgent, {
    context: '提取多次失败，回退到发现阶段寻找替代源泉',
  });
}
```

---

## 3. MCP 资源层设计

### 3.1 MCP Server 发现机制

当提取 Agent 分析一个开源项目时，按以下优先级获取 MCP 资源：

```
优先级 1: 查找已有 MCP Server
  └─ 在 MCP Server 注册表中搜索（如 mcp.run、npmjs @mcp/ scope）
  └─ 在项目仓库中搜索 mcp.json / mcp-server 配置

优先级 2: 从项目自动生成 MCP Server wrapper
  └─ 分析项目的 API 端点 / SDK 接口
  └─ 生成 MCP Server 代码（TypeScript）
  └─ 包含认证、速率限制、错误处理

优先级 3: 生成轻量 MCP 代理
  └─ 对简单库（如 akshare），生成函数级 MCP 工具
  └─ 每个关键函数映射为一个 MCP tool
```

### 3.2 MCP Server 自动生成框架

对于没有现成 MCP Server 的开源库，自动生成 wrapper：

```typescript
// mcp-generator.ts — 从 extract_repo_resources.py 的输出生成 MCP Server

interface McpGeneratorInput {
  library_name: string;           // e.g., "akshare"
  api_endpoints: ApiEndpoint[];   // 从 AST 分析提取的函数签名
  auth_pattern: AuthPattern;      // 认证方式
  rate_limits: RateLimit;         // 速率限制
  known_gotchas: string[];        // 已知陷阱（来自 DR 卡片）
}

// 生成的 MCP Server 结构
// generated-mcp-servers/
//   akshare-mcp/
//     ├── package.json
//     ├── src/
//     │   ├── index.ts          # MCP Server 入口
//     │   ├── tools/            # 每个 API 端点一个 tool
//     │   │   ├── stock-realtime.ts
//     │   │   ├── stock-history.ts
//     │   │   └── stock-financial.ts
//     │   └── utils/
//     │       ├── rate-limiter.ts
//     │       └── error-handler.ts
//     └── mcp.json              # MCP Server 元数据
```

**生成的 MCP tool 示例**:

```typescript
// tools/stock-realtime.ts
import { Tool } from '@modelcontextprotocol/sdk';

export const stockRealtimeTool: Tool = {
  name: 'get_stock_realtime',
  description: 'A股实时行情查询。数据源：东方财富（通过 akshare）。注意：非交易时间返回空数据不是错误。',
  inputSchema: {
    type: 'object',
    properties: {
      market: {
        type: 'string',
        enum: ['sh', 'sz', 'all'],
        default: 'all',
        description: '市场筛选：上海/深圳/全部',
      },
    },
  },
  handler: async (input) => {
    // 调用 akshare Python 库（通过子进程或 pybridge）
    const result = await callPython('akshare', 'stock_zh_a_spot_em', input);
    return { content: [{ type: 'text', text: JSON.stringify(result) }] };
  },
};
```

### 3.3 MCP Server 注册表 Schema

完整 schema 见 [附录 B](#附录-b-mcp-server-注册表完整-schema)。

```yaml
# mcp-registry.yaml — MCP Server 注册表
version: "1.0"
servers:
  - id: "akshare-mcp"
    name: "A股数据 MCP Server"
    source: "auto-generated"       # auto-generated | community | official
    source_library: "akshare"
    version: "0.1.0"
    status: "active"               # active | deprecated | experimental
    auth_required: false
    tools:
      - name: "get_stock_realtime"
        description: "A股实时行情"
        category: "data_query"
      - name: "get_stock_history"
        description: "个股历史行情"
        category: "data_query"
    metadata:
      reliability: "high"
      rate_limit: "1 req/sec recommended"
      data_source: "东方财富"
      known_issues:
        - "盘后数据延迟 15 分钟"
        - "非交易时间返回空 DataFrame"
    resource_card_ref: "RC-AKSHARE-001"  # 关联的 Resource Card
    install_command: "npm install @doramagic/akshare-mcp"
    last_health_check: "2026-03-10T08:00:00Z"
    health_status: "healthy"
```

### 3.4 Skill 通过 MCP 协议调用资源

生成的 Skill 中，资源调用通过 MCP 协议而非内嵌代码：

```markdown
<!-- stages/STAGE-2-data.md 中的资源调用指令 -->
## 数据获取

使用以下 MCP 工具获取数据：

### 实时行情
调用 MCP 工具 `akshare-mcp.get_stock_realtime`：
- market: "all" (默认查全市场)

### 个股历史
调用 MCP 工具 `akshare-mcp.get_stock_history`：
- symbol: 用户指定的股票代码
- period: "daily"
- start_date: 一年前

### 注意事项
- 非交易时间调用会返回空数据，这不是错误，应提示用户"当前非交易时间"
- 建议间隔 1 秒以上调用，避免频率过高
```

### 3.5 Resource Card 与 MCP Server 的关系

Resource Card (RC) 在 v2 中的定位变化：

```
v2 原方案: RC 是最终产物，Skill 内嵌 RC 中的代码调用
v2 升级后: RC 是 MCP Server 的元数据描述，Skill 通过 MCP 协议调用

RC 的新角色:
  ├─ MCP Server 的人类可读文档
  ├─ MCP Server 健康检查的基准信息
  ├─ 用于拼装 Agent 选择最优资源的决策依据
  └─ 在 MCP Server 不可用时的降级参考（内嵌代码 fallback）
```

### 3.6 冷启动策略

首批 MCP Server 库（MVP 阶段手动准备）：

| 类别 | MCP Server | 来源 | 状态 |
|------|-----------|------|------|
| 金融数据 | akshare-mcp | 自动生成 | MVP 必备 |
| Web 搜索 | web-search-mcp | OpenClaw 内置 | 已有 |
| 文件操作 | filesystem-mcp | MCP 官方 | 已有 |
| GitHub | github-mcp | MCP 官方 | 已有 |
| 数据库 | sqlite-mcp | MCP 官方 | 已有 |
| Python 执行 | python-exec-mcp | 自动生成 | MVP 必备 |

---

## 4. 代码理解层设计

### 4.1 AST 分析 Pipeline

```
git clone
    │
    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Tree-sitter │     │   结构索引    │     │   嵌入索引    │
│  AST 解析    │────▶│  (JSON)      │────▶│  (向量DB)    │
│              │     │              │     │              │
│ 支持语言:     │     │ 函数签名      │     │ 函数语义      │
│ Python,TS,   │     │ 类定义        │     │ 文档注释      │
│ JS,Go,Rust,  │     │ 导入关系      │     │ 代码片段      │
│ Java         │     │ 路由定义      │     │              │
└──────────────┘     │ SDK 调用      │     └──────────────┘
                     └──────────────┘
```

**Tree-sitter 集成方案**:

```typescript
// ast-analyzer.ts
import Parser from 'tree-sitter';
import Python from 'tree-sitter-python';
import TypeScript from 'tree-sitter-typescript';

interface AstAnalysisResult {
  functions: FunctionSignature[];      // 所有函数/方法签名
  classes: ClassDefinition[];          // 类定义及其方法
  imports: ImportStatement[];          // 导入依赖
  api_routes: ApiRoute[];              // HTTP 路由定义
  sdk_calls: SdkCall[];                // 外部 SDK/API 调用
  env_refs: EnvReference[];            // 环境变量引用
  exports: ExportedSymbol[];           // 导出符号
}

async function analyzeRepository(repoPath: string): Promise<AstAnalysisResult> {
  const parser = new Parser();
  const results: AstAnalysisResult = { /* ... */ };

  // 按文件类型选择语法
  for (const file of await walkSourceFiles(repoPath)) {
    const lang = detectLanguage(file);
    parser.setLanguage(lang);
    const tree = parser.parse(await readFile(file));

    // 提取函数签名
    results.functions.push(...extractFunctions(tree, file));
    // 提取 API 路由 (Flask/FastAPI/Express)
    results.api_routes.push(...extractRoutes(tree, file, lang));
    // 提取 SDK 调用
    results.sdk_calls.push(...extractSdkCalls(tree, file));
    // 提取环境变量引用
    results.env_refs.push(...extractEnvRefs(tree, file));
  }

  return results;
}
```

### 4.2 代码嵌入索引方案

**向量存储选型评估**:

| 方案 | 优点 | 缺点 | 推荐 |
|------|------|------|------|
| **Qdrant (self-hosted)** | 性能优秀、过滤能力强、持久化 | 需运维独立服务 | Phase C（生产环境） |
| **Chroma (embedded)** | 零运维、嵌入式、Python 友好 | 大规模性能有限 | Phase B（开发阶段） |
| **lancedb (embedded)** | 零运维、Rust 核心、高性能 | 生态较新 | 备选 |
| **内存 Map** | 最简单、无依赖 | 不持久、大仓库内存压力 | Phase A（MVP） |

**推荐路径**: Phase A 用内存 Map + 全量加载 → Phase B 迁移到 Chroma 嵌入式 → Phase C 视规模决定是否迁移到 Qdrant。

**嵌入模型选择**: `voyage-code-3`（代码嵌入专用）或 `text-embedding-3-large`（OpenAI 通用）。

```typescript
// code-index.ts
interface CodeChunk {
  id: string;
  file_path: string;
  symbol_name: string;
  symbol_type: 'function' | 'class' | 'method' | 'route' | 'config';
  code: string;              // 原始代码片段
  doc_comment: string;        // 文档注释
  embedding: number[];        // 嵌入向量
  ast_metadata: {
    params: Parameter[];
    return_type: string;
    decorators: string[];
    imports: string[];
  };
}

// Agent 查询接口
async function searchCode(query: string, filters?: CodeSearchFilter): Promise<CodeChunk[]> {
  const queryEmbedding = await embed(query);
  return vectorStore.search(queryEmbedding, {
    topK: 10,
    filter: filters,  // 如: { symbol_type: 'route', file_path: 'src/api/**' }
  });
}
```

### 4.3 按需加载策略

Agent 不再一次性喂入全部代码，而是通过查询接口按需读取：

```typescript
// Agent 的代码查询工具
const codeSearchTool: Tool = {
  name: 'search_code',
  description: '在目标仓库中搜索代码。支持语义搜索和结构化过滤。',
  inputSchema: {
    type: 'object',
    properties: {
      query: { type: 'string', description: '搜索查询（自然语言或代码片段）' },
      symbol_type: { type: 'string', enum: ['function', 'class', 'route', 'config'] },
      file_pattern: { type: 'string', description: '文件路径 glob 模式' },
    },
    required: ['query'],
  },
};

// 使用示例
// Agent: "我需要找到所有 API 路由定义"
// → search_code({ query: "API route endpoint", symbol_type: "route" })
// → 返回相关路由定义的代码片段（而非整个仓库）
```

### 4.4 与现有 Repomix 的关系

```
Phase A (MVP):
  ├─ 继续使用 Repomix compress 作为代码输入方式
  ├─ extract_repo_resources.py 基于正则扫描（扩展自 extract_repo_facts.py）
  └─ 兼容现有 prepare-repo.sh 流程

Phase B (Enhanced):
  ├─ 新增 AST 分析作为补充（Repomix + AST 并行）
  ├─ 资源提取优先使用 AST 结果，Repomix 作为 fallback
  └─ 代码嵌入索引开始建立

Phase C (Advanced):
  ├─ AST 分析 + 代码嵌入成为主要代码理解方式
  ├─ Repomix 降级为"快速概览"工具（仅用于小仓库）
  └─ 按需加载完全替代全量压缩
```

### 4.5 extract_repo_resources.py 完整设计

扩展自 v1.0 的 `extract_repo_facts.py`，新增资源维度提取：

```python
#!/usr/bin/env python3
"""
Doramagic v2: Extract deterministic facts AND resources from a repository.
Produces repo_resources.json — extends repo_facts.json with API, auth, data format info.

Usage:
    python3 extract_repo_resources.py --repo-path <path> --output-dir <output_dir>

Output: <output_dir>/artifacts/repo_resources.json
"""

# === 继承自 extract_repo_facts.py 的函数 ===
# extract_cli_commands()    — 保持不变
# extract_skill_names()     — 保持不变
# extract_file_paths()      — 保持不变
# extract_config_keys()     — 保持不变

# === v2 新增提取函数 ===

def extract_api_endpoints(repo_path):
    """扫描 API 路由定义（Flask, FastAPI, Express, Django）。"""
    endpoints = []
    patterns = {
        'flask': r'@\w+\.route\(["\']([^"\']+)',
        'fastapi': r'@\w+\.(get|post|put|delete|patch)\(["\']([^"\']+)',
        'express': r'\w+\.(get|post|put|delete|patch)\(["\']([^"\']+)',
        'django': r'path\(["\']([^"\']+)',
    }
    # 扫描所有 Python/JS/TS 文件...
    return endpoints

def extract_http_clients(repo_path):
    """扫描 HTTP 客户端调用模式（requests, axios, fetch）。"""
    clients = []
    patterns = {
        'requests': r'requests\.(get|post|put|delete)\(["\']([^"\']+)',
        'axios': r'axios\.(get|post|put|delete)\(["\']([^"\']+)',
        'fetch': r'fetch\(["\']([^"\']+)',
    }
    return clients

def extract_sdk_initializations(repo_path):
    """扫描 SDK/客户端初始化代码。"""
    inits = []
    # 扫描 import + 初始化模式
    # e.g., import akshare as ak; ak.stock_zh_a_spot_em()
    return inits

def extract_env_variables(repo_path):
    """扫描环境变量引用。扩展自 extract_config_keys，增加代码中的引用。"""
    env_vars = []
    # .env.example + os.environ + process.env + dotenv
    return env_vars

def extract_data_formats(repo_path):
    """扫描返回值类型注解、JSON Schema 定义。"""
    formats = []
    # TypedDict, dataclass, Pydantic model, JSON Schema, TypeScript interface
    return formats

def extract_dependencies(repo_path):
    """扫描外部服务依赖。"""
    deps = []
    # 数据库连接串、Redis、MQ、S3 等
    return deps

def extract_auth_patterns(repo_path):
    """扫描认证模式。"""
    auth = []
    # API Key, OAuth, JWT, Basic Auth
    return auth

def extract_example_usages(repo_path):
    """扫描示例代码。"""
    examples = []
    # examples/ 目录、README 中的代码块、docstring 中的示例
    return examples

def main():
    # ... (命令行解析同 v1.0)
    resources = {
        # v1.0 继承
        "repo_path": repo_path,
        "commands": extract_cli_commands(repo_path),
        "skills": extract_skill_names(repo_path),
        "files": extract_file_paths(repo_path),
        "config_keys": extract_config_keys(repo_path),
        # v2 新增
        "api_endpoints": extract_api_endpoints(repo_path),
        "http_clients": extract_http_clients(repo_path),
        "sdk_initializations": extract_sdk_initializations(repo_path),
        "env_variables": extract_env_variables(repo_path),
        "data_formats": extract_data_formats(repo_path),
        "dependencies": extract_dependencies(repo_path),
        "auth_patterns": extract_auth_patterns(repo_path),
        "example_usages": extract_example_usages(repo_path),
    }
    # 写入 repo_resources.json
```

---

## 5. 知识卡片体系 v2

### 5.1 卡片类型总览

| 卡片类型 | 缩写 | 状态 | 用途 |
|---------|------|------|------|
| 概念卡 (Concept Card) | CC | 保留 | 核心概念的身份、关系和边界 |
| 工作流卡 (Workflow Card) | WC | 保留 | 操作流程的步骤和决策点 |
| 决策规则卡 (Decision Rule Card) | DR | 保留 | IF-THEN 规则和社区踩坑 |
| 资源卡 (Resource Card) | RC | **新增** | 可调用资源的调用方式和约束 |
| 模式卡 (Pattern Card) | PT | **新增** | 可复用的设计模式和架构模式 |

v1.0 的 CT（社区陷阱卡）和 AC（架构组件卡）被合并：CT 合入 DR（severity=COMMUNITY），AC 合入 RC。

### 5.2 各卡片完整 YAML Schema

完整 schema 见 [附录 C](#附录-c-所有卡片类型的完整-yaml-schema)。以下为关键字段摘要：

#### CC - 概念卡（保留，微调）

```yaml
---
card_type: concept_card
card_id: CC-{PROJECT}-{NNN}
source: "{project_name}"
title: "概念名称"
evidence_level: E2        # v2 新增字段
related_cards: [DR-xxx, WC-xxx]  # v2 新增字段
---

## Identity
[这个概念是什么]

## Mental Model
[该概念在系统中的心智模型]

## Boundaries
[该概念的边界——是什么/不是什么]

## Evidence
[证据来源：代码引用、文档引用]
```

#### WC - 工作流卡（保留，微调）

```yaml
---
card_type: workflow_card
card_id: WC-{PROJECT}-{NNN}
source: "{project_name}"
title: "工作流名称"
evidence_level: E2
trigger: "触发条件"
---

## Steps
1. [步骤1]
2. [步骤2]
...

## Decision Points
[流程中的关键决策点]

## Error Handling
[异常处理路径]
```

#### DR - 决策规则卡（保留，增强）

```yaml
---
card_type: decision_rule_card
card_id: DR-{PROJECT}-{NNN}   # 001-099=代码规则, 100-199=社区规则
source: "{project_name}"
type: code_rule | community_gotcha
title: "规则名称"
severity: CRITICAL | HIGH | MEDIUM | LOW
rule: "IF [条件] THEN [动作]"
do:
  - "正确做法（含代码示例）"
dont:
  - "错误做法"
confidence: 0.95
evidence_level: E1
sources:
  - "file.py:42"
  - "Issue #123"
---

## 真实场景
[该规则被触发的真实案例]

## 影响范围
[违反该规则的后果]
```

#### RC - 资源卡（新增）

```yaml
---
card_type: resource_card
card_id: RC-{PROJECT}-{NNN}
source: "{project_name}"
title: "资源名称"
resource_type: api | data_feed | tool | library | service | mcp_server
auth_required: false | api_key | oauth | paid
integration_complexity: low | medium | high
reliability: high | medium | low | unknown
evidence_level: E2
mcp_server_ref: "akshare-mcp"     # 关联的 MCP Server（如已生成）
related_cards: [DR-xxx, CC-xxx]
---

## 调用方式
[代码示例，或 MCP tool 调用方式]

## 认证要求
[认证方式详情]

## 速率限制
[QPS、日配额、并发数]

## 数据格式
[返回结构、字段说明]

## 依赖安装
[安装命令]

## 可靠性
[可靠性评估及依据]

## 已知陷阱
[关联的 DR 卡片引用]

## 适用场景
[checkist: 适用/不适用的场景]
```

#### PT - 模式卡（新增）

```yaml
---
card_type: pattern_card
card_id: PT-{SOURCE}-{NNN}
source: "{source_name}"
source_type: skill | project | community
title: "模式名称"
pattern_type: architecture | interaction | data_flow | error_handling
evidence_level: E3
applicability: high | medium | low
---

## 模式描述
[该模式解决什么问题，怎么解决]

## 结构
[模式的结构化描述——阶段、组件、数据流]

## 可复用元素
[可直接复用的具体元素列表]

## 适配建议
[应用到目标 Skill 时需要的修改]

## 已知限制
[该模式的局限性]
```

### 5.3 卡片间关联关系

```
CC (概念) ──references──▶ DR (规则)     "概念 X 受规则 Y 约束"
CC (概念) ──requires────▶ RC (资源)     "概念 X 需要资源 Y 实现"
DR (规则) ──warns───────▶ RC (资源)     "规则 X 是资源 Y 的使用陷阱"
PT (模式) ──uses────────▶ RC (资源)     "模式 X 使用资源 Y"
PT (模式) ──embeds──────▶ DR (规则)     "模式 X 内化规则 Y"
WC (工作流) ─calls──────▶ RC (资源)     "工作流步骤 X 调用资源 Y"
RC (资源) ──backed_by───▶ MCP Server    "资源 X 由 MCP Server Y 提供"
```

### 5.4 证据级别体系 (E1-E4)

| 级别 | 含义 | 来源 | 可信度 |
|------|------|------|--------|
| **E1** | 代码直接证据 | AST 分析、函数签名、测试用例 | 最高 |
| **E2** | 文档明确记载 | README、API docs、CHANGELOG | 高 |
| **E3** | 社区经验验证 | GitHub Issues（已关闭/已确认）、SO 高票答案 | 中 |
| **E4** | LLM 推断 | 模型基于代码/文档的推理，未经外部验证 | 需标注 |

**规则**: 所有卡片必须标注 evidence_level。E4 级别的卡片在拼装阶段降低优先级，仅在无更高证据时使用。

---

## 6. 源泉发现引擎设计

### 6.1 语义搜索架构

```
用户需求 (自然语言)
      │
      ▼
┌──────────────┐
│ 需求分解      │  "帮我选股" → [金融数据获取, 筛选算法, 结果呈现]
│ (LLM)        │
└──────┬───────┘
       │ 能力需求列表
       ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ 能力向量索引  │     │ MCP 注册表    │     │ 实时搜索      │
│ (嵌入匹配)   │     │ (精确匹配)    │     │ (GitHub/Web) │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │ 结果融合排序  │
                    │ (相关度+质量  │
                    │  +可用性)     │
                    └──────────────┘
```

**嵌入模型选型**:

| 模型 | 优点 | 场景 |
|------|------|------|
| `voyage-code-3` | 代码语义理解最强 | 代码片段搜索 |
| `text-embedding-3-large` | 通用语义理解 | 项目描述/能力描述搜索 |

**推荐**: 双模型方案——代码级搜索用 voyage-code-3，描述级搜索用 text-embedding-3-large。

### 6.2 能力图谱数据模型

```typescript
// capability-graph.ts
interface CapabilityNode {
  id: string;
  name: string;                    // e.g., "金融数据获取"
  description: string;
  embedding: number[];              // 语义嵌入
  category: string;                 // e.g., "data_access"
  providers: CapabilityProvider[];   // 能提供该能力的源泉
}

interface CapabilityProvider {
  type: 'project' | 'skill' | 'mcp_server' | 'community';
  id: string;                       // e.g., "akshare"
  name: string;
  relevance_score: number;          // 0-1
  quality_signals: {
    stars: number;                   // GitHub stars
    last_update: string;             // 最近更新日期
    install_count: number;           // 安装量
    known_issues: number;            // 已知问题数
  };
  auth_required: boolean;
  free: boolean;
}

// 图谱关系
interface CapabilityEdge {
  from: string;    // 能力节点 ID
  to: string;      // 能力节点 ID
  relation: 'requires' | 'enhances' | 'alternative_to';
}
```

### 6.3 四类源泉搜索策略

| 源泉类型 | 搜索方法 | 评分权重 | 冷启动方案 |
|---------|---------|---------|-----------|
| **开源项目** | GitHub API + LLM 知识 + 能力索引 | 相关性 40% + 质量 30% + 活跃度 30% | LLM 内置知识（知道主流项目） |
| **OpenClaw Skill** | Skill 市场 API（如有）+ 本地已安装 Skill 扫描 | 功能匹配 50% + 评分 30% + 可复用性 20% | 从本地已安装 Skill 开始 |
| **MCP Server** | MCP 注册表 + npmjs/PyPI 搜索 | 精确匹配 60% + 可靠性 40% | 手动维护首批注册表 |
| **社区经验** | GitHub Issues + SO + 技术博客 | 痛点密度 50% + 方案质量 50% | Web 搜索实时获取 |

### 6.4 冷启动方案

```
阶段 0 (MVP 初期):
  ├─ 搜索完全依赖 LLM 内置知识 + 实时 Web 搜索
  ├─ 手动维护 50 个常见领域的推荐项目列表
  └─ 首批 MCP Server 注册表（10 个核心服务）

阶段 1 (数据积累):
  ├─ 每次成功交付的 Skill → 源泉信息回流到能力索引
  ├─ 用户反馈丰富项目质量信号
  └─ 社区贡献扩充 MCP Server 注册表

阶段 2 (语义索引):
  ├─ 对 GitHub Top 1000 项目建立能力向量索引
  ├─ 语义搜索替代关键词搜索
  └─ 能力图谱支持"沿图发现"
```

---

## 7. 反馈闭环与持续学习

### 7.1 MEMORY.md 利用方案

**读取策略** — 在以下时机读取 MEMORY.md：
- 需求 Agent 启动时：读取用户历史偏好和已完成的 Skill 记录
- 拼装 Agent 启动时：读取用户的参数偏好历史
- Skill 运行时：读取该 Skill 的运行记忆

**写入策略** — 在以下时机写入 MEMORY.md：
- Skill 交付成功：记录使用的源泉、卡片数量、用户满意度
- Skill 运行时：记录用户反馈和参数调整
- Skill 体检时：记录资源健康状态

**格式定义**:

```markdown
<!-- MEMORY.md 中 Doramagic 相关段落 -->

## Doramagic

### 用户偏好
- 复杂度偏好: simple_first
- 语言偏好: 中文
- 常用领域: 金融, 数据分析

### 已生成 Skill
- my-stock-advisor (2026-03-11): 源泉=akshare+vnpy, 满意度=高
- data-cleaner (2026-03-05): 源泉=pandas+great-expectations, 满意度=中

### Skill 运行记忆
#### my-stock-advisor
- 用户偏好: PE阈值=20, ROE阈值=15%, 关注沪深300
- 反馈: "选股结果太多，需要更严格的筛选" (2026-03-12)
- 资源健康: akshare=healthy (最近检查: 2026-03-11)
```

### 7.2 Skill 自我优化机制

```
Skill 运行
    │
    ├─ 隐式反馈收集
    │   ├─ 用户是否修改了输出？ → 记录修改模式
    │   ├─ 用户是否重复调用同一功能？ → 记录常用路径
    │   └─ 用户是否报错？ → 记录错误模式
    │
    ├─ 显式反馈收集
    │   ├─ "这个结果有帮助吗？"（定期询问，不要每次）
    │   └─ 用户主动说"不准"/"太多"/"太少" → 参数微调
    │
    └─ 自我优化
        ├─ 参数微调：根据反馈调整阈值/权重（写入 MEMORY.md）
        ├─ 规则补充：发现新的陷阱 → 新增 DR 卡片 → 更新 stage 指令
        └─ 资源更新：检测 API 变更 → 更新 MCP Server / RC 卡片
```

### 7.3 Skill 体检机制

定期（或触发式）检查 Skill 的健康状态：

```typescript
interface SkillHealthCheck {
  skill_id: string;
  check_time: string;
  checks: {
    // 资源可用性
    resource_health: {
      mcp_server: string;
      status: 'healthy' | 'degraded' | 'down';
      response_time_ms: number;
      last_error: string | null;
    }[];
    // 数据质量
    data_quality: {
      sample_query: string;
      returned_data: boolean;
      data_freshness: string;  // "实时" | "延迟15分钟" | "过时"
    };
    // 规则有效性
    rule_validity: {
      total_rules: number;
      verified_rules: number;
      deprecated_rules: number;
    };
  };
  recommendation: 'healthy' | 'needs_update' | 'needs_rebuild';
}
```

**触发时机**:
- 定期：每周一次（通过 OpenClaw 定时任务）
- 触发式：用户报告错误、资源返回异常时
- 主动式：用户说"检查一下我的 Skill"

---

## 8. 质量保障体系 v2

### 8.1 验证门控（扩展版）

扩展 v1.0 的 `validate_extraction.py`，新增 RC 和 PT 卡片支持：

```python
# v2 验证扩展
VALID_CARD_TYPES_V2 = {
    "decision_rule_card",    # DR — 继承
    "concept_card",          # CC — 继承
    "workflow_card",         # WC — 继承
    "resource_card",         # RC — 新增
    "pattern_card",          # PT — 新增
}

# RC 卡片必填字段
REQUIRED_RC_FIELDS = [
    "card_type", "card_id", "source", "title",
    "resource_type", "auth_required", "integration_complexity",
    "evidence_level",
]

# PT 卡片必填字段
REQUIRED_PT_FIELDS = [
    "card_type", "card_id", "source", "title",
    "pattern_type", "evidence_level", "applicability",
]

# RC 特有检查
def check_rc_has_call_example(meta, body):
    """RC 卡片必须包含调用方式代码示例。"""
    if "```" not in body and "调用" not in body:
        return ["Resource card lacks code example in 调用方式 section"]
    return []

def check_rc_has_gotchas(meta, body):
    """RC 卡片应关联已知陷阱。"""
    if "已知陷阱" not in body and "known" not in body.lower():
        return ["Resource card missing 已知陷阱 section (warning)"]
    return []
```

### 8.2 5+1 维评分体系

| 维度 | 含义 | 评分标准 | 来源 |
|------|------|---------|------|
| **准确性** | 提取内容是否正确 | 与代码/文档的一致率 | v1.0 继承 |
| **完整性** | 是否覆盖关键维度 | 卡片覆盖率 | v1.0 继承 |
| **可追溯性** | 每条声明是否有证据 | sources 字段完整率 | v1.0 继承 |
| **一致性** | 卡片间是否矛盾 | 交叉验证通过率 | v1.0 继承 |
| **实用性** | 对 Skill 生成的价值 | 拼装 Agent 使用率 | v1.0 继承 |
| **可用性** | 生成的 Skill 是否可运行 | 冒烟测试通过率 | **v2 新增** |

### 8.3 冒烟测试框架

```typescript
// smoke-test.ts
interface SmokeTest {
  skill_id: string;
  test_cases: SmokeTestCase[];
}

interface SmokeTestCase {
  name: string;
  type: 'data_fetch' | 'format_check' | 'interaction_flow';
  input: string;           // 模拟用户输入
  expected: {
    returns_data: boolean;  // 是否返回数据
    format_valid: boolean;  // 输出格式是否正确
    no_error: boolean;      // 是否无运行时错误
    latency_ms: number;     // 最大延迟（毫秒）
  };
}

// 示例：股票 Skill 冒烟测试
const stockSkillSmokeTest: SmokeTest = {
  skill_id: 'my-stock-advisor',
  test_cases: [
    {
      name: '实时行情查询',
      type: 'data_fetch',
      input: '查一下贵州茅台今天行情',
      expected: {
        returns_data: true,
        format_valid: true,     // 包含股票名、价格、涨跌幅
        no_error: true,
        latency_ms: 10000,
      },
    },
    {
      name: '选股筛选',
      type: 'data_fetch',
      input: '帮我从沪深300中选出低估值的股票',
      expected: {
        returns_data: true,
        format_valid: true,     // 包含表格：股票名、PE、ROE 等
        no_error: true,
        latency_ms: 30000,
      },
    },
  ],
};
```

### 8.4 端到端质量指标

| 指标 | 门控值 | 测量方式 |
|------|--------|---------|
| 卡片格式合规率 | >= 95% | validate_extraction.py |
| 证据可追溯率 | = 100% | sources 字段全部可验证 |
| 资源可达率 | >= 80% | MCP Server 健康检查 |
| 冒烟测试通过率 | = 100% | 全部测试用例通过 |
| 用户确认率 | >= 1 次 | Phase 2 用户确认 |
| 端到端耗时 | < 15 分钟 | 从需求到交付（不含用户对话时间） |

---

## 9. 用户体验设计

### 9.1 进度透明方案

每个阶段向用户展示的信息：

| 阶段 | 用户可见信息 | 交互方式 |
|------|------------|---------|
| NEED | 对话进行中，当前已明确 N/5 个维度 | 对话式（3-5 轮） |
| DISCOVER | 搜索进度 + 已发现源泉列表 | 实时更新 + 1 轮确认 |
| EXTRACT | 每个子代理的进度条 + 已提取卡片数 | 实时更新，无需交互 |
| ASSEMBLE | 蓝图设计进度 + 资源绑定状态 | 实时更新，无需交互 |
| DELIVER | 安装结果 + 冒烟测试 + 能力清单 + 升级建议 | 展示 + 试用引导 |

**进度展示格式**:

```
[Doramagic] 正在为你打造专属技能...

[1/5] 需求理解 ✓ — 价值投资选股 + 持仓跟踪
[2/5] 源泉发现 ✓ — 找到 akshare + vnpy + stock-skill
[3/5] 多源提取 ⟳
  ├─ akshare 知识提取 ✓ (3 概念 + 5 规则)
  ├─ akshare MCP Server ✓ (8 个工具)
  ├─ vnpy 策略提取 ⟳ ...
  └─ 社区信号收集 ✓ (12 条)
[4/5] 智能拼装 — 等待中
[5/5] 交付验证 — 等待中
```

### 9.2 "开袋即食"默认配置策略

```yaml
# config.yaml — 生成的 Skill 默认配置
defaults:
  # 无需任何配置即可使用的功能
  zero_config:
    data_source: akshare          # 免费，无需 API Key
    market: A_share               # 默认 A 股
    language: zh_CN               # 默认中文

  # 有合理默认值的参数
  sensible_defaults:
    pe_threshold: 20              # PE < 20 视为低估
    roe_threshold: 15             # ROE > 15% 视为优质
    profit_growth_years: 3        # 连续3年净利润增长
    output_format: markdown_table # Markdown 表格输出

  # 标记为可选升级
  optional_upgrades:
    tushare_token:
      description: "注册 tushare 可解锁：10年历史数据回测"
      required: false
      how_to_get: "访问 tushare.pro 免费注册"
    portfolio:
      description: "提供持仓清单可解锁：每日变动提醒"
      required: false
      format: "股票代码列表，如 ['000001', '600519']"
```

### 9.3 "可选升级"提示机制

```
触发时机:
  ├─ 交付时：展示全部可选升级（不强制）
  ├─ 使用中：当用户的操作接近升级功能时，提示一次
  └─ 体检时：如果有新的升级可能，提示用户

提示原则:
  ├─ 不打断正常使用流程
  ├─ 每个升级项最多提示 2 次
  ├─ 明确说明"不升级也完全可用"
  └─ 提供一步到位的升级指令（如"提供你的 tushare token"）
```

### 9.4 错误恢复与用户沟通策略

| 错误类型 | 系统处理 | 用户看到的 |
|---------|---------|-----------|
| 源泉搜索无结果 | 自动回退到 NEED 阶段 | "这个方向我找不到好的参考，能再描述一下你想要什么吗？" |
| 提取验证失败 | 自动重试 2 次或换源泉 | "正在优化提取质量..." |
| 资源不可达 | 切换备选资源或降级 | "原计划的数据源暂时不可用，已切换到备选方案" |
| 冒烟测试失败 | 自动修复 + 重新拼装 | "第一版有点小问题，正在修复..." |
| 超过最大重试 | 终止并保存进度 | "这次没能完全搞定，但已保存进度。你可以调整需求后再试" |

---

## 10. 开发计划

### Phase A: MVP (4-6 周)

**目标**: 核心流程跑通，MCP-first 资源层，可端到端生成一个可用 Skill。

**范围**:
- Orchestrator 线性模式（5 阶段顺序执行，简单重试，无自适应回退）
- 需求 Agent（继承 Skill Forge Stage 1）
- 发现 Agent（LLM 知识 + Web 搜索，无语义索引）
- 提取 Agent（Repomix 文本 + extract_repo_resources.py 正则扫描）
- 拼装 Agent（Skill 包生成 + MCP 资源绑定）
- 交付 Agent（安装 + 基础冒烟测试）
- RC 卡片支持（validate_extraction.py 扩展）
- 首批 MCP Server（akshare-mcp, 复用已有 web-search / filesystem MCP）

**关键里程碑**:
| 周次 | 里程碑 | 验收标准 |
|------|--------|---------|
| W1-2 | 共享工作记忆 + Orchestrator 骨架 + 需求 Agent | 能完成 3 轮对话生成 need_profile |
| W3 | 发现 Agent + extract_repo_resources.py | 能搜索并选出 >= 2 个源泉 |
| W4 | 提取 Agent + RC 卡片 + 验证扩展 | 能生成 CC+DR+RC 卡片且验证通过 |
| W5 | 拼装 Agent + MCP 资源绑定 | 能生成完整 Skill 包 + MCP 调用 |
| W6 | 交付 Agent + 冒烟测试 + 端到端验证 | 股民老王场景端到端通过 |

**技术风险**:
- MCP Server 自动生成的稳定性（Python 库 → TypeScript MCP wrapper 的 bridge 可靠性）
- Repomix 对大仓库的 token 限制（缓解：优先分析关键目录）

**v1.0 迁移计划**:
| v1.0 资产 | 迁移方式 |
|-----------|---------|
| extract_repo_facts.py | 复制 → 扩展为 extract_repo_resources.py |
| validate_extraction.py | 复制 → 增加 RC/PT 卡片验证 |
| STAGE-1-discovery.md | 复制 → 适配为 AGENT-need.md 指令 |
| STAGE-5-generate.md | 重写为 AGENT-assemble.md（增加 MCP 绑定逻辑） |
| prepare-repo.sh | 保留，增加 extract_repo_resources.py 调用 |
| 知识卡片 schema (CC/WC/DR) | 保留，增加 evidence_level 和 related_cards 字段 |

### Phase B: Enhanced (4-6 周)

**目标**: Orchestrator 自适应循环 + 反馈闭环 + PT 卡片 + MEMORY.md 集成。

**范围**:
- Orchestrator 升级为自适应状态机（回退/前进规则）
- PT 模式卡片支持（从 OpenClaw Skill 提取设计模式）
- MEMORY.md 读写集成（用户偏好 + Skill 运行记忆）
- Skill 自我优化机制（参数微调、规则补充）
- Skill 体检机制
- Chroma 嵌入式向量存储（替代内存 Map）
- 多模型调度（Opus 做复杂分析，Sonnet 做调度，Haiku 做监控）

**关键里程碑**:
| 周次 | 里程碑 | 验收标准 |
|------|--------|---------|
| W1-2 | Orchestrator 自适应循环 | 提取失败时自动回退到发现阶段 |
| W3 | PT 卡片 + Skill 模式提取 | 能从已有 Skill 提取设计模式 |
| W4 | MEMORY.md 集成 | Skill 运行时能读写用户偏好 |
| W5-6 | 反馈闭环 + Skill 体检 | 用户反馈后 Skill 行为自动调整 |

**技术风险**:
- 自适应循环的死循环防护（缓解：最大重试次数 + 状态回退深度限制）
- MEMORY.md 并发读写冲突（缓解：文件锁 + 写入队列）

### Phase C: Advanced (6-8 周)

**目标**: AST 代码理解 + 语义发现 + 能力图谱。

**范围**:
- Tree-sitter AST 分析 pipeline
- 代码嵌入索引（Chroma → 视规模决定是否迁移 Qdrant）
- 按需加载代码（Agent 查询接口）
- 语义搜索（需求 → 能力分解 → 向量匹配）
- 能力图谱（节点：能力，边：依赖/增强/替代）
- Repomix 降级为 fallback
- 大仓库支持优化

**关键里程碑**:
| 周次 | 里程碑 | 验收标准 |
|------|--------|---------|
| W1-2 | Tree-sitter 集成 + AST 分析 | Python/TS/JS 仓库的函数签名/路由提取 |
| W3-4 | 代码嵌入 + 按需加载 | Agent 能语义搜索代码片段 |
| W5-6 | 语义搜索 + 能力图谱 | "帮我选股"→ 自动发现 akshare/vnpy |
| W7-8 | 集成测试 + 性能优化 | 大仓库(>10k 文件)端到端 < 20 分钟 |

**技术风险**:
- Tree-sitter 对不同语言的解析质量差异（缓解：优先支持 Python/TS/JS）
- 能力图谱冷启动数据量（缓解：从 Phase A/B 的使用数据逐步积累）

---

## 11. 技术选型

### Agent 框架: Claude Agent SDK

- **选型理由**: Anthropic 官方 SDK，原生支持 handoff 协议、工具调用、多模型切换
- **使用方式**: Orchestrator + 5 个子代理
- **模型分配**: Opus（提取/拼装）、Sonnet（需求/发现/交付/调度）、Haiku（监控/体检）

### MCP 框架: MCP TypeScript SDK

- **选型理由**: MCP 协议官方实现，TypeScript 生态完善
- **使用方式**: MCP Client（Skill 调用资源）+ MCP Server Generator（自动生成 wrapper）
- **版本**: `@modelcontextprotocol/sdk` latest

### AST 分析: Tree-sitter

- **选型理由**: 2026 年代码分析事实标准，多语言支持，增量解析
- **使用方式**: Node.js 绑定 `tree-sitter` + 语言包 `tree-sitter-python/typescript/javascript`
- **Phase C 引入**，Phase A/B 用 Repomix 过渡

### 向量数据库评估

| 方案 | 推荐阶段 | 理由 |
|------|---------|------|
| **内存 Map** | Phase A | 零依赖，MVP 够用 |
| **Chroma (embedded)** | Phase B-C | 零运维，Python 嵌入式，持久化 |
| **Qdrant (self-hosted)** | Phase C+ (视规模) | 高性能，过滤能力强，适合大规模索引 |
| **lancedb** | 备选 | Rust 核心高性能，但生态较新 |

**推荐路径**: 内存 Map → Chroma → 视规模决定

### 知识图谱评估

| 方案 | 推荐 | 理由 |
|------|------|------|
| **JSON Graph (内存)** | Phase A-B | 零依赖，能力图谱初期规模小 |
| **Neo4j** | Phase C+ (视规模) | 图查询能力强，适合复杂关系 |
| **轻量方案 (TypeScript Map)** | MVP | 最简实现，后续可迁移 |

**推荐路径**: JSON Graph → 视规模决定是否迁移 Neo4j

### 运行时

- **Node.js 18+**: 与 v1.0 保持一致
- **TypeScript 5.x**: 类型安全，与 MCP SDK 一致
- **Python 3.11+**: extract_repo_resources.py、Tree-sitter Python 绑定
- **包管理**: pnpm（workspace 模式管理多包）

---

## 附录 A: 共享工作记忆完整 Schema

```typescript
// shared-working-memory.ts

interface SharedWorkingMemory {
  // === 元信息 ===
  session_id: string;                  // UUID
  created_at: string;                  // ISO 8601
  updated_at: string;                  // ISO 8601
  current_state: OrchestratorState;
  version: '2.0';

  // === Phase 1: 需求理解产出 ===
  need_profile: {
    core_problem: string;              // 用户真正要解决的问题
    user_persona: string;              // 用户画像
    trigger: string;                   // 触发条件
    expected_output: string;           // 期望输出
    success_criteria: string;          // 成功标准
    anti_requirements: string;         // 反需求
    complexity: 'simple_first' | 'full_featured' | 'configurable';
    search_keywords: string[];         // 搜索关键词
    user_environment: {
      platform: string;
      available_models: string[];
      installed_skills: string[];
      memory_files: string[];
    };
  } | null;

  // === Phase 2: 源泉发现产出 ===
  source_map: {
    primary_sources: {
      name: string;
      type: 'project' | 'skill' | 'mcp_server';
      url: string;
      stars: number;
      extract_targets: string[];       // 提取目标
      extract_types: ('knowledge' | 'resource' | 'pattern')[];
    }[];
    secondary_sources: {
      name: string;
      type: string;
      extract_targets: string[];
      extract_types: string[];
    }[];
    community_signals: {
      source: string;
      query: string;
    }[];
    user_confirmed: boolean;
  } | null;

  // === Phase 3: 多源提取产出 ===
  cards_registry: {
    knowledge_cards: {
      card_id: string;
      card_type: 'concept_card' | 'workflow_card' | 'decision_rule_card';
      source: string;
      title: string;
      severity?: string;
      evidence_level: 'E1' | 'E2' | 'E3' | 'E4';
      content: string;                // 完整 Markdown 内容
    }[];
    resource_cards: {
      card_id: string;
      source: string;
      title: string;
      resource_type: 'api' | 'data_feed' | 'tool' | 'library' | 'service' | 'mcp_server';
      auth_required: boolean | string;
      integration_complexity: 'low' | 'medium' | 'high';
      reliability: 'high' | 'medium' | 'low' | 'unknown';
      evidence_level: string;
      mcp_server_ref: string | null;
      content: string;
    }[];
    pattern_cards: {
      card_id: string;
      source: string;
      title: string;
      pattern_type: 'architecture' | 'interaction' | 'data_flow' | 'error_handling';
      applicability: 'high' | 'medium' | 'low';
      content: string;
    }[];
    mcp_servers: {
      id: string;
      name: string;
      source: 'discovered' | 'auto_generated';
      tools: { name: string; description: string }[];
      status: 'ready' | 'generating' | 'failed';
    }[];
    validation_report: {
      overall_pass: boolean;
      format_compliance_rate: number;
      traceability_rate: number;
      card_count: {
        knowledge: number;
        resource: number;
        pattern: number;
      };
      errors: { card_id: string; errors: string[] }[];
      structured_feedback: string | null;
    } | null;
  };

  // === Phase 4: 智能拼装产出 ===
  skill_draft: {
    skill_md: string;                  // SKILL.md 完整内容
    stages: {
      filename: string;
      content: string;
    }[];
    config: {
      zero_config: Record<string, any>;
      sensible_defaults: Record<string, any>;
      optional_upgrades: Record<string, {
        description: string;
        required: boolean;
        how_to_get?: string;
      }>;
    };
    bound_resources: {
      resource_card_id: string;
      mcp_server_id: string;
      binding_status: 'success' | 'failed' | 'fallback';
      fallback_code?: string;
    }[];
  } | null;

  // === Phase 5: 交付产出 ===
  delivery: {
    install_path: string;
    smoke_test_result: {
      overall_pass: boolean;
      test_cases: {
        name: string;
        pass: boolean;
        error?: string;
        latency_ms: number;
      }[];
    };
    capability_summary: string;
    upgrade_suggestions: string[];
  } | null;

  // === 质量信号 ===
  quality_signals: {
    timestamp: string;
    source: string;                    // 哪个 Agent 产生的
    signal_type: 'gate_pass' | 'gate_fail' | 'retry' | 'rollback' | 'warning';
    message: string;
    data?: any;
  }[];

  // === 回退历史 ===
  rollback_history: {
    timestamp: string;
    from_state: OrchestratorState;
    to_state: OrchestratorState;
    reason: string;
    retry_count: number;
  }[];
}
```

---

## 附录 B: MCP Server 注册表完整 Schema

```yaml
# mcp-registry-schema.yaml
version: "1.0"
description: "Doramagic MCP Server 注册表 Schema"

server_entry:
  required:
    - id              # string, 唯一标识 (slug 格式)
    - name            # string, 人类可读名称
    - source          # enum: official | community | auto_generated
    - version         # semver string
    - status          # enum: active | deprecated | experimental | disabled
    - tools           # array of tool definitions
  optional:
    - source_library  # string, 原始库名 (如 "akshare")
    - source_repo     # string, 原始仓库 URL
    - auth_required   # boolean, 是否需要认证
    - metadata        # object, 扩展元数据
    - resource_card_ref  # string, 关联的 RC 卡片 ID
    - install_command    # string, 安装命令
    - last_health_check  # datetime, 最近健康检查时间
    - health_status      # enum: healthy | degraded | down | unknown

tool_entry:
  required:
    - name            # string, 工具名称
    - description     # string, 工具描述
  optional:
    - category        # string, 工具类别 (data_query, action, analysis)
    - input_schema    # JSON Schema, 输入参数定义
    - rate_limit      # string, 速率限制描述
    - auth_scope      # string, 需要的认证范围

metadata:
  optional:
    - reliability     # enum: high | medium | low
    - rate_limit      # string, 全局速率限制
    - data_source     # string, 底层数据来源
    - known_issues    # array of string, 已知问题
    - supported_languages  # array of string, 支持的编程语言
    - dependencies    # array of string, 系统依赖
```

**完整注册表示例**:

```yaml
version: "1.0"
servers:
  - id: "akshare-mcp"
    name: "A股数据 MCP Server"
    source: auto_generated
    source_library: "akshare"
    source_repo: "https://github.com/jindaxiang/akshare"
    version: "0.1.0"
    status: active
    auth_required: false
    tools:
      - name: "get_stock_realtime"
        description: "获取 A 股实时行情数据（全市场或指定市场）"
        category: "data_query"
        input_schema:
          type: object
          properties:
            market:
              type: string
              enum: [sh, sz, all]
              default: all
        rate_limit: "1 req/sec recommended"

      - name: "get_stock_history"
        description: "获取个股历史行情数据"
        category: "data_query"
        input_schema:
          type: object
          properties:
            symbol:
              type: string
              description: "股票代码，如 000001"
            period:
              type: string
              enum: [daily, weekly, monthly]
              default: daily
            start_date:
              type: string
              format: date
          required: [symbol]

      - name: "get_stock_financial"
        description: "获取个股财务指标（PE、PB、ROE 等）"
        category: "data_query"

    metadata:
      reliability: high
      rate_limit: "无官方限制，建议 <= 1 req/sec"
      data_source: "东方财富"
      known_issues:
        - "盘后数据可能延迟 15 分钟"
        - "非交易时间返回空 DataFrame（不是错误）"
        - "港股数据偶尔缺失"
    resource_card_ref: "RC-AKSHARE-001"
    install_command: "npm install @doramagic/akshare-mcp"
    last_health_check: "2026-03-10T08:00:00Z"
    health_status: healthy

  - id: "web-search-mcp"
    name: "Web 搜索 MCP Server"
    source: official
    version: "1.2.0"
    status: active
    auth_required: false
    tools:
      - name: "web_search"
        description: "搜索互联网内容"
        category: "data_query"
      - name: "web_fetch"
        description: "获取指定 URL 的内容"
        category: "data_query"
    metadata:
      reliability: high
    install_command: "内置于 OpenClaw"
    health_status: healthy

  - id: "filesystem-mcp"
    name: "文件系统 MCP Server"
    source: official
    version: "1.0.0"
    status: active
    auth_required: false
    tools:
      - name: "read_file"
        description: "读取文件内容"
        category: "action"
      - name: "write_file"
        description: "写入文件内容"
        category: "action"
      - name: "list_directory"
        description: "列出目录内容"
        category: "data_query"
    metadata:
      reliability: high
    install_command: "内置于 OpenClaw"
    health_status: healthy
```

---

## 附录 C: 所有卡片类型的完整 YAML Schema

### CC - 概念卡 (Concept Card)

```yaml
# --- YAML Frontmatter ---
card_type: concept_card          # 固定值
card_id: CC-{PROJECT}-{NNN}      # 格式: CC-项目缩写-三位序号
source: "{project_name}"         # 来源项目名称
title: "概念名称"                 # 人类可读标题
evidence_level: E1 | E2 | E3 | E4  # 证据级别
related_cards:                    # 关联卡片 ID 列表
  - "DR-{PROJECT}-{NNN}"
  - "WC-{PROJECT}-{NNN}"
  - "RC-{PROJECT}-{NNN}"
tags:                             # 可选标签
  - "core_concept"
  - "data_model"
# --- End Frontmatter ---

# Body Sections (Markdown):

## Identity
# 这个概念是什么——一句话精确定义

## Mental Model
# 该概念在系统中的心智模型——它如何工作，与其他概念如何交互

## Boundaries
# 是什么 / 不是什么——明确边界防止混淆

## Relationships
# 与其他概念的关系图

## Evidence
# 证据来源：代码引用(file:line)、文档引用、社区验证
```

### WC - 工作流卡 (Workflow Card)

```yaml
# --- YAML Frontmatter ---
card_type: workflow_card
card_id: WC-{PROJECT}-{NNN}
source: "{project_name}"
title: "工作流名称"
evidence_level: E1 | E2 | E3 | E4
trigger: "触发该工作流的条件"
output: "工作流的产出"
related_cards:
  - "CC-{PROJECT}-{NNN}"
  - "RC-{PROJECT}-{NNN}"
# --- End Frontmatter ---

## Steps
# 1. [步骤1] — 描述 + 输入 + 输出
# 2. [步骤2]
# ...

## Decision Points
# 流程中的关键分支——什么条件走哪条路

## Error Handling
# 每个步骤的异常处理路径

## Performance Notes
# 性能相关信息（耗时、资源占用、并发限制）

## Evidence
# 证据来源
```

### DR - 决策规则卡 (Decision Rule Card)

```yaml
# --- YAML Frontmatter ---
card_type: decision_rule_card
card_id: DR-{PROJECT}-{NNN}      # 001-099=代码规则, 100-199=社区规则
source: "{project_name}"
type: code_rule | community_gotcha
title: "规则名称"
severity: CRITICAL | HIGH | MEDIUM | LOW
rule: "IF [条件] THEN [动作]"     # 必须包含条件语言
do:                                # 正确做法列表（CRITICAL/HIGH 须含代码示例）
  - "正确做法1（含 `代码示例`）"
  - "正确做法2"
dont:                              # 错误做法列表
  - "错误做法1"
  - "错误做法2"
confidence: 0.95                   # 0-1 之间
evidence_level: E1 | E2 | E3 | E4
sources:                           # 证据来源（不可为空）
  - "file.py:42"                   # 代码规则: 文件:行号
  - "Issue #123"                   # 社区规则: Issue 编号
related_cards:
  - "CC-{PROJECT}-{NNN}"
  - "RC-{PROJECT}-{NNN}"
# --- End Frontmatter ---

## 真实场景
# 该规则被触发的真实案例

## 影响范围
# 违反该规则的后果——严重程度说明

## 例外情况
# 该规则不适用的场景（如有）
```

### RC - 资源卡 (Resource Card) — 新增

```yaml
# --- YAML Frontmatter ---
card_type: resource_card
card_id: RC-{PROJECT}-{NNN}
source: "{project_name}"
title: "资源名称"
resource_type: api | data_feed | tool | library | service | mcp_server
auth_required: false | api_key | oauth | paid
integration_complexity: low | medium | high
reliability: high | medium | low | unknown
evidence_level: E1 | E2 | E3 | E4
mcp_server_ref: "{mcp_server_id}"   # 关联的 MCP Server ID（如已生成）
free: true | false                    # 是否免费
related_cards:
  - "DR-{PROJECT}-{NNN}"             # 关联的陷阱规则
  - "CC-{PROJECT}-{NNN}"             # 关联的核心概念
# --- End Frontmatter ---

## 调用方式
# 代码示例或 MCP tool 调用方式
# ```python
# import xxx
# result = xxx.some_function()
# ```

## 认证要求
# 无需认证 / API Key（获取方式）/ OAuth（流程）/ 付费（价格）

## 速率限制
# QPS、日配额、并发数、来源（官方文档/社区经验）

## 数据格式
# 返回值类型、字段说明、示例数据

## 依赖安装
# 安装命令、环境要求、版本兼容性

## 可靠性
# 可靠性评估 + 依据（社区反馈、运行时间、维护频率）

## 已知陷阱
# 关联的 DR 卡片列表 + 简要描述
# - DR-{PROJECT}-{NNN}: "描述"

## 适用场景
# - [x] 适用场景1
# - [x] 适用场景2
# - [ ] 不适用场景1（原因）
```

### PT - 模式卡 (Pattern Card) — 新增

```yaml
# --- YAML Frontmatter ---
card_type: pattern_card
card_id: PT-{SOURCE}-{NNN}
source: "{source_name}"
source_type: skill | project | community
title: "模式名称"
pattern_type: architecture | interaction | data_flow | error_handling
evidence_level: E1 | E2 | E3 | E4
applicability: high | medium | low    # 对当前需求的适用性
related_cards:
  - "RC-{PROJECT}-{NNN}"
  - "DR-{PROJECT}-{NNN}"
# --- End Frontmatter ---

## 模式描述
# 该模式解决什么问题，怎么解决

## 结构
# 模式的结构化描述
# 1. 阶段/组件1 — 职责 + 输入 + 输出
# 2. 阶段/组件2
# ...
# 数据流: 组件1 → 组件2 → ...

## 可复用元素
# 可直接复用的具体元素
# - 元素1: 描述 + 复用方式
# - 元素2: 描述 + 复用方式

## 适配建议
# 应用到目标 Skill 时需要的修改
# - 修改1: 原因 + 方法
# - 修改2: 原因 + 方法

## 已知限制
# 该模式的局限性
# - 限制1: 描述 + 缓解方案
```

---

## 附录 D: 股民老王端到端示例（技术视角）

### 完整数据流

```
用户输入: "我想要一个帮我炒股的 AI 助手"
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│ Orchestrator: state = IDLE → NEED                           │
│ handoff → Need Agent                                        │
└─────────────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│ Need Agent: 3 轮苏格拉底对话                                  │
│                                                               │
│ 产出 → SharedWorkingMemory.need_profile:                      │
│   core_problem: "A股选股+跟踪，手动耗时不系统"                  │
│   user_persona: "个人投资者，非技术，价值投资偏好"               │
│   trigger: "帮我选股 | 分析XXX | 今天大盘 | 看看持仓"           │
│   expected_output: "选股列表 + 个股分析 + 持仓变动提醒"         │
│   success_criteria: "每天5分钟了解动态，每周收到建议"            │
│   anti_requirements: "不需要自动交易"                          │
│   complexity: "simple_first"                                  │
│   search_keywords: ["A股数据", "量化选股", "股票分析", "行情API"]│
│                                                               │
│ handoff → Orchestrator (gate: PASS)                           │
└─────────────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│ Orchestrator: state = NEED → DISCOVER                        │
│ handoff → Discover Agent                                     │
└─────────────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│ Discover Agent:                                               │
│   工具调用: webSearch("A股数据 Python 库")                     │
│   工具调用: githubSearch("stock data china")                  │
│   工具调用: mcpRegistrySearch("financial data")               │
│                                                               │
│ 产出 → SharedWorkingMemory.source_map:                        │
│   primary_sources:                                            │
│     - akshare (GitHub ★4.2k, extract: knowledge+resource)    │
│     - stock-analysis-skill (OpenClaw, extract: pattern)       │
│   secondary_sources:                                          │
│     - vnpy (GitHub ★21k, extract: knowledge)                 │
│     - tushare (extract: resource, 标记为可选升级)              │
│   community_signals:                                          │
│     - "akshare 踩坑" GitHub Issues top 20                     │
│   user_confirmed: true (1 轮确认)                             │
│                                                               │
│ handoff → Orchestrator (gate: PASS)                           │
└─────────────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│ Orchestrator: state = DISCOVER → EXTRACT                     │
│ handoff → Extract Agent                                      │
└─────────────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│ Extract Agent: 并行 4 个子任务                                 │
│                                                               │
│ 子任务 A — akshare 知识提取:                                   │
│   工具: cloneRepo → runExtractRepoResources → readFile        │
│   产出: CC-AK-001 (DataFrame 数据模型)                         │
│          CC-AK-002 (行情数据更新机制)                           │
│          CC-AK-003 (数据源分层架构)                             │
│          DR-AK-001 (CRITICAL: 非交易时间返回空DF不是错误)       │
│          DR-AK-002 (HIGH: 建议<=1req/sec)                     │
│          ... (共 3CC + 5DR)                                    │
│                                                               │
│ 子任务 B — akshare MCP Server 生成:                            │
│   工具: mcpDiscover (未找到现有) → 自动生成                     │
│   产出: RC-AK-001 (A股实时行情, auth=false, complexity=low)    │
│          RC-AK-002 (个股历史数据)                               │
│          RC-AK-003 (财务指标查询)                               │
│          MCP Server: akshare-mcp (8 个 tools, status=ready)   │
│                                                               │
│ 子任务 C — vnpy 知识提取:                                      │
│   产出: CC-VN-001 (价值投资五因子模型)                          │
│          DR-VN-001 (选股因子权重平衡规则)                       │
│                                                               │
│ 子任务 D — stock-skill 模式提取:                                │
│   产出: PT-SS-001 (4阶段交互模式: 意图→数据→分析→呈现)         │
│                                                               │
│ 子任务 E — 社区信号:                                            │
│   产出: DR-AK-101~108 (8条社区踩坑规则)                        │
│                                                               │
│ 验证: validate_extraction.py                                  │
│   format_compliance: 100%                                     │
│   traceability: 100%                                          │
│   卡片统计: 5CC + 14DR + 3RC + 1PT = 23 张卡片                │
│   overall: PASS                                               │
│                                                               │
│ handoff → Orchestrator (gate: PASS)                           │
└─────────────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│ Orchestrator: state = EXTRACT → ASSEMBLE                     │
│ handoff → Assemble Agent                                     │
└─────────────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│ Assemble Agent:                                               │
│                                                               │
│ Step 1 — 蓝图设计:                                            │
│   参考 PT-SS-001 (4阶段模式) + need_profile                   │
│   设计: 意图识别 → 数据获取 → 价值分析 → 结果呈现              │
│                                                               │
│ Step 2 — MCP 资源绑定:                                        │
│   akshare-mcp.get_stock_realtime → STAGE-2 (免费, 默认启用)   │
│   akshare-mcp.get_stock_history  → STAGE-2 (免费, 默认启用)   │
│   akshare-mcp.get_stock_financial → STAGE-3 (免费, 默认启用)  │
│   绑定状态: 全部 success                                      │
│                                                               │
│ Step 3 — 规则注入:                                            │
│   DR-AK-001 (CRITICAL) → STAGE-2 错误处理指令                 │
│   DR-AK-002 (HIGH)     → STAGE-2 速率控制指令                 │
│   DR-VN-001            → STAGE-3 选股策略指令                 │
│   DR-AK-101~108        → 各 stage 注意事项                    │
│                                                               │
│ Step 4 — 生成 Skill 包:                                       │
│   SKILL.md (my-stock-advisor)                                 │
│   stages/STAGE-1-intent.md                                    │
│   stages/STAGE-2-data.md                                      │
│   stages/STAGE-3-analysis.md                                  │
│   stages/STAGE-4-present.md                                   │
│   config.yaml (开袋即食, akshare 免费数据源)                   │
│                                                               │
│ handoff → Orchestrator (gate: PASS)                           │
└─────────────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│ Orchestrator: state = ASSEMBLE → DELIVER                     │
│ handoff → Deliver Agent                                      │
└─────────────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│ Deliver Agent:                                                │
│                                                               │
│ Step 1 — 安装:                                                │
│   写入 ~/.openclaw/skills/my-stock-advisor/                   │
│                                                               │
│ Step 2 — 冒烟测试:                                            │
│   测试 1: "查一下贵州茅台" → akshare-mcp.get_stock_realtime   │
│     结果: 返回数据 ✓, 格式正确 ✓, 无错误 ✓, 耗时 3200ms ✓    │
│   测试 2: "帮我选股" → akshare-mcp.get_stock_financial        │
│     结果: 返回数据 ✓, 格式正确 ✓, 无错误 ✓, 耗时 8500ms ✓    │
│   overall: PASS                                               │
│                                                               │
│ Step 3 — 能力呈现:                                            │
│   展示: 能力清单 + 试用引导 + 升级建议                         │
│                                                               │
│ Step 4 — 写入 MEMORY.md:                                      │
│   记录: skill=my-stock-advisor, sources=akshare+vnpy,         │
│          cards=23, smoke_test=pass                             │
│                                                               │
│ handoff → Orchestrator (state → COMPLETE)                     │
└─────────────────────────────────────────────────────────────┘

最终用户看到:
  "你的「老王的A股助手」已安装完成！
   ✅ 说'帮我选股' → 从沪深全市场筛选低估值好公司
   ✅ 说'分析一下贵州茅台' → 出基本面分析报告
   ✅ 说'看看我的持仓' → 跟踪关注的股票变动
   后续可升级: tushare token → 历史回测, 持仓清单 → 每日提醒"
```

### 关键技术节点总结

| 节点 | 技术实现 | v1.0 复用 | v2 新建 |
|------|---------|-----------|---------|
| 苏格拉底对话 | Agent SDK + STAGE-1-discovery 指令 | 80% | 20% (环境感知) |
| 源泉搜索 | Web Search + GitHub API + MCP Registry | 40% | 60% (MCP+语义) |
| 知识提取 | Soul Extractor Stage 1-3.5 | 90% | 10% (evidence_level) |
| 资源提取 | extract_repo_resources.py + MCP 生成 | 30% | 70% (全新维度) |
| 模式提取 | Skill 结构分析 | 0% | 100% (全新) |
| 验证门控 | validate_extraction.py 扩展 | 70% | 30% (RC/PT 支持) |
| Skill 拼装 | Agent SDK + MCP 绑定 + 规则注入 | 20% | 80% (MCP-first) |
| 冒烟测试 | MCP 调用验证 + 格式检查 | 0% | 100% (全新) |
| 反馈闭环 | MEMORY.md 读写 | 0% | 100% (全新) |

---

> 文档结束。本文档定义了 Doramagic v2 的完整技术框架。后续开发应以此为基准，按 Phase A → B → C 顺序推进。

# Doramagic 第四阶段：能力积木呈现 - 完整设计方案

> 设计日期：2026-03-11
> 背景：基于所有研究文档的综合分析与重构

---

## 一、核心理念重构

### 1.1 原有方案的不足

之前的研究有一个重大遗漏：**从未考虑开源项目中隐藏的「资源」**。

### 1.2 新增：资源维度

经过与 Tangsir 的讨论，我们认为「灵魂提取」应该包含三类内容：

| 维度 | 定义 | 来源 |
|------|------|------|
| **知识** | 代码设计、架构意图、决策原因 | 代码、文档 |
| **经验** | 踩过的坑、最佳实践、workaround | Issues、Discussions |
| **资源** | 好用的 API、工具链、信息源、配置模板 | 整个开源项目生态 |

---

## 二、能力积木的完整定义

### 2.1 积木的四种类型

```
┌─────────────────────────────────────────────────────────┐
│                    能力积木体系                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   触发积木    │  │   能力积木    │  │   资源积木    │  │
│  │  Trigger    │  │   Action     │  │  Resource   │  │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤  │
│  │ 触发关键词   │  │ 操作命令      │  │ API 端点    │  │
│  │ 使用场景    │  │ 输入/输出    │  │ 工具推荐    │  │
│  │ 用户意图    │  │ 配置要求      │  │ 信息源      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                         │
│  ┌──────────────┐                                      │
│  │   依赖积木    │                                      │
│  │  Dependency │                                      │
│  ├──────────────┤                                      │
│  │ 环境变量     │                                      │
│  │ 安装要求     │                                      │
│  │ 权限需求     │                                      │
│  └──────────────┘                                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.2 积木的完整属性

```yaml
block:
  # 基础信息
  id: "trello-list-boards"
  name: "查看所有 Board"
  emoji: "📋"
  type: "action"  # trigger | action | resource | dependency
  
  # 来源追踪
  source:
    project: "trello"                    # 开源项目名
    repo: "github.com/trello/trello"     # GitHub 地址
    extracted_at: "2026-03-11"             # 提取时间
    extraction_type: "code|issue|doc|manual"  # 来源类型
  
  # 能力定义
  capability:
    verb: "list"                          # 动词
    noun: "boards"                        # 名词
    description: "查看用户所有的 Board 列表"
    
  # 技术细节
  tech:
    type: "rest_api"                      # rest_api | cli | native
    endpoint: "GET /1/members/me/boards"   # API 端点 / CLI 命令
    method: "curl"
    params:                                # 参数定义
      - name: "key"
        required: true
        source: "env:TRELLO_API_KEY"
      - name: "token"
        required: true
        source: "env:TRELLO_TOKEN"
      - name: "fields"
        required: false
        default: "name,id"
    output:
      format: "json"
      sample: |
        [{"id":"abc123","name":"My Board"}]
  
  # 经验沉淀（来自社区）
  experience:
    has_workaround: false
    common_issues: []
    best_practices:
      - "使用 fields 参数限制返回字段提升性能"
    related_issues: []
  
  # 资源推荐（新增）
  resources:
    apis:
      - name: "Trello REST API"
        url: "https://developer.atlassian.com/cloud/trello/rest/"
        quality: "official"  # official | community | third_party
    tools:
      - name: "Power-Ups"
        description: "官方扩展能力"
      - name: " Butler"
        description: "自动化规则"
    configs:
      - name: "board template"
        description: "Board 模板配置"
    alternatives:
      - name: "monday.com"
        description: "类似替代方案"
  
  # 依赖信息
  dependencies:
    env:
      - name: "TRELLO_API_KEY"
        required: true
        how_to_get: "https://trello.com/app-key"
      - name: "TRELLO_TOKEN"
        required: true
        how_to_get: "点击 API Key 页面的 Token 链接"
    bins: []
    os: []
```

---

## 三、「四足够」设计原则

### 3.1 足够专业：充分利用 OpenClaw 资源

**设计思路**：Doramagic 应该能读取用户的 OpenClaw 上下文，为用户提供个性化的积木推荐。

```python
class OpenClawContextAnalyzer:
    """分析用户的 OpenClaw 资源"""
    
    def analyze(self):
        # 1. 可用模型
        available_models = self.get_available_models()
        # 2. 记忆文件
        memory_context = self.get_memory_context()
        # 3. 内置工具
        built_in_tools = self.get_builtin_tools()
        # 4. 已安装 Skill
        installed_skills = self.get_installed_skills()
        # 5. 用户偏好
        user_preferences = self.get_user_preferences()
        
        return {
            "models": available_models,
            "memory": memory_context,
            "tools": built_in_tools,
            "skills": installed_skills,
            "prefs": user_preferences
        }
```

**应用场景**：

| 用户资源 | 积木呈现策略 |
|----------|--------------|
| 有 Claude 模型 | 优先推荐需要深度理解的能力 |
| 有 MiniMax 模型 | 优先推荐需要多轮对话的能力 |
| 记忆文件有股票 | 优先推荐 A 股相关能力 |
| 已安装 Trello Skill | 问「要增强 Trello 能力吗？」 |
| macOS 系统 | 优先推荐 macOS 原生能力 |

### 3.2 足够智能：子代理并行工作

**设计思路**：用户只需要说一句话，Doramagic 内部用多个子代理并行工作，减少用户交互。

```
用户: Dora 我想管 Trello
           ↓
┌─────────────────────────────────────────────┐
│           Doramagic 内部处理                  │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────┐  ┌─────────────┐          │
│  │ 意图理解    │  │ 资源检索    │  ← 并行    │
│  │ 子代理      │  │ 子代理      │          │
│  └─────────────┘  └─────────────┘          │
│         ↓                ↓                  │
│  ┌─────────────┐  ┌─────────────┐          │
│  │ 置信度评估  │  │ 积木匹配    │          │  ← 并行
│  │ 子代理      │  │ 子代理      │          │
│  └─────────────┘  └─────────────┘          │
│                                             │
└─────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────┐
│           一次性呈现完整结果                   │
│                                             │
│  Trello 能做的：                              │
│  • 查看所有 Board ✓                          │
│  • 创建新 Card ✓                             │
│  • 移动 Card ✓                               │
│                                             │
│  你可能还需要：                               │
│  • 配置 API Key（已检测：未配置）⚠️           │
│  • 你的记忆里有「任务管理」，推荐这个模板 📋    │
└─────────────────────────────────────────────┘
```

**子代理分工**：

| 子代理 | 功能 | 输出 |
|--------|------|------|
| `intent_agent` | 理解用户需求 | 意图 + 场景 + 置信度 |
| `resource_agent` | 检索相关积木 | 候选积木列表 + 匹配度 |
| `match_agent` | 匹配用户上下文 | 个性化推荐 + 理由 |
| `config_agent` | 检查依赖配置 | 缺失配置 + 解决建议 |
| `presentation_agent` | 生成最终呈现 | UI 描述 + 引导文案 |

### 3.3 足够适用：开箱即用 + 配置引导

**设计思路**：默认给出最可能成功的组合，同时告诉用户配置什么可以增强能力。

**三层配置状态**：

```
┌─────────────────────────────────────────────────────────┐
│                    配置状态金字塔                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│                    ┌─────────────┐                       │
│                    │  开箱即用   │ ← 默认推荐            │
│                    │  (0 配置)   │                      │
│                    └──────┬──────┘                       │
│                           │                              │
│                    ┌──────┴──────┐                      │
│                    │  轻量配置    │ ← 提示建议            │
│                    │  (1-2 项)   │                      │
│                    └──────┬──────┘                      │
│                           │                              │
│                    ┌──────┴──────┐                      │
│                    │  完整配置    │ ← 进阶用户            │
│                    │  (3+ 项)    │                      │
│                    └─────────────┘                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**示例：股票项目**

```
用户: Dora 我想炒股票

Doramagic（一次性呈现）:

🎯 推荐：A股量化交易 Skill（开箱即用）

└─ 已包含能力：
   □ 实时行情查询 ✓
   □ 涨跌幅监控 ✓
   □ 自选股管理 ✓

⚡ 增强能力（配置后可解锁）：
   ├─ 交易执行 - 需要：券商 API Key
   │   配置指南：tangsir 的华鑫证券账户，支持 Python API
   ├─ 实盘推送 - 需要：微信/钉钉 Webhook
   └─ 量化回测 - 需要：历史数据下载权限

💡 你可能感兴趣：
   - 你的记忆里有「比亚迪」，推荐关注实时行情监控
   - 根据你的持仓，推荐设置涨跌幅提醒
```

### 3.4 足够透明：实时进度可见

**设计思路**：用户不需要等待 30 分钟才看到结果，而是能看到每个阶段的关键进展。

**进度展示设计**：

```
用户: Dora 帮我做个监控系统

┌─────────────────────────────────────────────────────────┐
│  🎯 正在分析你的需求...                                   │
│  ████████████░░░░░░░░░░░░░░░░░░░░░░  45%              │
├─────────────────────────────────────────────────────────┤
│  ✓ 已理解需求：监控系统                                  │
│  ✓ 检索到相关积木：23 个                                 │
│  ◐ 匹配用户上下文...                                     │
├─────────────────────────────────────────────────────────┤
│  预计还需 10 秒完成                                      │
└─────────────────────────────────────────────────────────┘

                    ↓（完成后）

┌─────────────────────────────────────────────────────────┐
│  🎉 完成！帮你找到 3 个最佳方案                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  方案 A：Prometheus + Grafana（推荐）                   │
│  ├─ 完整度：90%                                        │
│  ├─ 匹配度：95%（你有用过 Prometheus）                   │
│  └─ 配置：需要安装 2 个工具                             │
│                                                         │
│  方案 B：CloudMonitor                                  │
│  ├─ 完整度：70%                                        │
│  ├─ 匹配度：80%                                        │
│  └─ 配置：需要阿里云账号                                │
│                                                         │
│  方案 C：Node Exporter                                  │
│  ├─ 完整度：50%                                        │
│  ├─ 匹配度：60%                                        │
│  └─ 配置：需要服务器权限                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**关键技术实现**：

```python
class ProgressTracker:
    """进度追踪器"""
    
    def __init__(self):
        self.stages = []
        self.current_stage = None
        
    async def update(self, stage: str, progress: float, message: str):
        """更新进度"""
        self.stages.append({
            "stage": stage,
            "progress": progress,
            "message": message,
            "timestamp": now()
        })
        
        # 实时推送给用户
        await self.push_to_user()
        
    async def push_to_user(self):
        """推送进度给用户（流式输出）"""
        # 使用 OpenClaw 的流式能力
        await message.send_streaming(
            format_progress(self.stages)
        )
```

---

## 四、完整交互流程

### 4.1 流程概览

```
用户输入
    ↓
【第一阶段：自适应交互】（之前讨论过）
    ↓
【第二阶段：意图理解 + 资源检索】（子代理并行）
    ↓
【第三阶段：能力积木呈现】（本阶段讨论）
    ↓
【第四阶段：用户选择 + 配置】
    ↓
【第五阶段：Skill 生成 + 交付】
```

### 4.2 详细流程

```
用户: Dora 我想管 Trello

─────────────────────────────────────────────────────
【自适应交互阶段】
    ↓
置信度判断：高（72%）
    ↓
直接进入下一阶段
─────────────────────────────────────────────────────
【子代理并行处理】

1️⃣ intent_agent:
   - 识别：能力=Trello，场景=任务管理
   - 置信度：72%
   - 输出：{ intent: "task_management", entity: "Trello" }

2️⃣ resource_agent:
   - 检索关键词：["Trello", "task", "board", "card"]
   - 找到积木：15 个
   - 按质量排序

3️⃣ match_agent:
   - 读取用户上下文：已安装 Trello Skill
   - 匹配结果：推荐增强现有 Skill

4️⃣ config_agent:
   - 检查 Trello API Key 配置
   - 结果：已配置 ✓

5️⃣ presentation_agent:
   - 整合所有结果
   - 生成最终呈现
─────────────────────────────────────────────────────
【能力积木呈现】

🎯 帮你找到 Trello 相关能力（共 8 个）

【你可能需要的】
✓ 查看所有 Board      [推荐] 你之前查过 Board
✓ 创建新 Card        [推荐] 符合「任务管理」场景
✓ 移动 Card          [推荐] 
✓ 查看 Card 详情

【增强能力】⚡ 配置后可解锁
• 批量操作 - 需要 Power-Up
• 自动化规则 - 需要 Butler（付费）
• Webhook 通知 - 需要公网地址

【你可能还感兴趣】
• CalDAV 日历同步 - 你在用日历 Skill
• GitHub 任务同步 - 检测到你是开发者

─────────────────────────────────────────────────────
【用户选择】

用户: 给我前3个 + Webhook

─────────────────────────────────────────────────────
【Skill 生成】

生成中...
✓ 已添加 3 个能力
✓ 已检测 Webhook 依赖
⚠️ 需要配置：
   - 用户需要配置公网 Webhook URL
   - 提示：可以使用 ngrok 本地调试

🎉 Skill 已就绪！

─────────────────────────────────────────────────────
【交付】

你的 Trello 助手已生成：
• 名称：我的 Trello 管理器
• 触发词：管 Trello、Trello 任务
• 能力：list_boards, create_card, move_card
• 状态：已安装，待配置 Webhook
```

---

## 五、技术实现要点

### 5.1 积木索引结构

```python
class BlockIndex:
    """积木索引 - 支持高速检索"""
    
    def __init__(self):
        # 向量索引 - 语义匹配
        self.vector_store = qdrant.Client()
        
        # 关键词索引 - 精确匹配
        self.keyword_store = redis.Redis()
        
        # 图谱索引 - 关系推理
        self.graph_store = networkx.Graph()
        
    def search(self, query: str, user_context: dict) -> list[Block]:
        """检索积木"""
        # 1. 语义检索
        semantic_results = self.vector_store.search(query, top_k=20)
        
        # 2. 关键词过滤
        keyword_results = self.keyword_store.mget(query.keywords)
        
        # 3. 上下文增强
        contextualized = self.apply_context(user_context, semantic_results + keyword_results)
        
        # 4. 排序与去重
        ranked = self.rank_and_dedup(contextualized)
        
        return ranked[:10]
```

### 5.2 子代理编排

```python
async def process_user_request(user_input: str, context: OpenClawContext):
    """处理用户请求 - 子代理并行"""
    
    # 并行启动所有子代理
    intent_task = intent_agent.run(user_input)
    resource_task = resource_agent.run(user_input)
    config_task = config_agent.run(context)
    
    # 等待所有结果
    intent, resources, config = await asyncio.gather(
        intent_task, resource_task, config_task
    )
    
    # 匹配与整合
    matched = match_agent.run(intent, resources, context)
    
    # 生成呈现
    presentation = presentation_agent.run(matched, config)
    
    return presentation
```

---

## 六、总结

### 6.1 核心设计原则

| 原则 | 实现 |
|------|------|
| **足够专业** | 分析用户 OpenClaw 上下文，个性化推荐 |
| **足够智能** | 子代理并行工作，一次性呈现结果 |
| **足够适用** | 开箱即用 + 配置引导 + 增强建议 |
| **足够透明** | 实时进度 + 阶段可见 + 预计时间 |

### 6.2 新增的价值维度

| 维度 | 内容 |
|------|------|
| **资源** | API、工具、信息源、配置模板 |
| **增强** | 配置什么可以解锁什么能力 |
| **透明** | 每个阶段用户都能看到 |

---

*本方案基于 2026-03-11 的所有研究文档综合设计*

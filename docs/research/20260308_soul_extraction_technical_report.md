# AllInOne 灵魂提取技术方案（纯技术报告）

**日期**: 2026-03-08
**版本**: v0.1
**性质**: 纯技术调研——如何用今天的 AI 能力从开源项目中提取"灵魂"

---

# 一、提取什么：六类知识的技术定义

| 类型 | 知识 | 技术提取难度 | 需要 LLM 吗 |
|------|------|-------------|------------|
| ① 领域知识（WHAT） | 概念、实体、分类法、数据模型 | 低 | 结构用静态分析，语义需 LLM |
| ② 流程经验（HOW） | 工作流、步骤、状态机 | 中 | 调用图用静态分析，描述需 LLM |
| ③ 判断规则（IF/WHEN） | 条件分支、业务规则 | 中 | 显式规则可静态分析，隐式需 LLM |
| ④ 数据关系（STRUCTURE） | ER 关系、API 契约 | 低 | ORM/Schema 不需要，隐式关系需 LLM |
| ⑤ 踩坑教训（WHY） | 决策原因、失败教训 | 高 | 必须用 LLM |
| ⑥ 未说出口的常识（UNSAID） | 社区心照不宣的最佳实践 | 高 | 必须用 LLM |

---

# 二、代码半魂提取（①②③④）

## 2.1 类型①：领域知识（WHAT）

### 最佳方法：Tree-sitter AST 解析 + LLM 语义解读

**Tree-sitter** 把源代码解析为语法树，支持 40+ 种语言，精准定位 class/struct/type/enum：

```json
// 输出示例
{
  "class": "Invoice",
  "fields": [
    {"name": "sender", "type": "Company"},
    {"name": "line_items", "type": "List[LineItem]"},
    {"name": "tax_rate", "type": "float"}
  ],
  "inherits": "Document",
  "methods": ["calculate_total()", "validate()", "to_pdf()"]
}
```

- **准确度**：语法层面接近 100%
- **局限**：知道 `tax_rate: float` 存在，但不知道它是"增值税税率"——**语义理解需要 LLM**

**辅助方法**：
- 标识符拆词（camelCase/snake_case） → 词频聚类 → 发现领域概念群
- **CodeQL**：把代码编译成关系数据库，SQL-like 查询提取类型关系和继承层次
- **IBM COMEX**（Tree-sitter 扩展）：同时提取 AST + CFG + DFG 多视图

### 工具链

| 工具 | GitHub | 用途 |
|------|--------|------|
| Tree-sitter | tree-sitter/tree-sitter | AST 解析，40+ 语言 |
| IBM COMEX | IBM/tree-sitter-codeviews | AST+CFG+DFG 多视图 |
| CodeQL | github/codeql | 代码即数据查询 |
| MCP Server for Tree-sitter | — | 让 AI 直接查询代码结构 |

## 2.2 类型②：流程经验（HOW）

### 最佳方法：调用图分析 + Aider RepoMap

**调用图工具**：

| 语言 | 工具 | 说明 |
|------|------|------|
| Python | PyCG / Pyan | 静态调用图生成 |
| Java | SootUp / WALA | 指针分析级精度 |
| 多语言 | Tree-sitter 遍历 | 提取函数调用节点构图 |

**准确度**：覆盖 80-90% 的直接调用。动态分派（多态、反射、回调）是主要盲区。

**Aider 的 RepoMap 方法**（特别推荐）：
1. Tree-sitter 提取所有函数定义和引用
2. 构建 NetworkX 有向图
3. **PageRank 算法**排序重要代码——找出"最核心"的函数/类
4. 输出压缩的仓库地图

论文 **Repository Intelligence Graph (RIG)**（2026年1月）证实：提供这种结构化图让 LLM 准确率提升 12.2%，多语言仓库提升 17.7%。

**状态机提取**：
- 显式 switch/case 模式 → **StateMachineExtraction** 可直接提取
- 隐式状态机 → **FlowFSM** 用 LLM prompt chaining 提取
- 准确度差异大：显式高、隐式不稳定

```
// 输出示例
generate_report()
  ├── collect_data()
  │     ├── query_database()
  │     └── fetch_api()
  ├── validate_data()
  ├── aggregate()
  └── format_output()
        ├── to_pdf()
        └── to_csv()
```

## 2.3 类型③：判断规则（IF/WHEN）

### 最佳方法：Semgrep 模式匹配 + CodeQL 深度分析 + LLM 解读

**三层方法**：

| 层 | 工具 | 提取什么 | 准确度 |
|----|------|---------|--------|
| 快速扫描 | **Semgrep** | 用代码模式匹配条件逻辑 | 高（但需预知模式） |
| 深度分析 | **CodeQL** | 数据流+控制流跨过程分析 | 最高（但需构建环境+QL技能） |
| 语义理解 | **LLM** | 解读规则的业务含义、提取隐式规则 | 中（可能幻觉） |

**隐式规则**（不在 if/else 中）：
- 函数选择模式分析：哪些函数在哪些上下文中被选择
- BREX 基准（2025）：409 个真实业务文档、2855 条专家标注规则

```yaml
# 输出示例
rules:
  - condition: "user.region == 'EU'"
    action: "apply_gdpr_rules()"
    source: "user_handler.py:142"
  - condition: "order.total > 500"
    action: "require_manager_approval()"
    source: "order_processor.py:89"
```

## 2.4 类型④：数据关系（STRUCTURE）

### 最佳方法：ORM Schema 解析（最直接）

| ORM/框架 | 提取方法 | 准确度 |
|----------|---------|--------|
| Django | `manage.py inspectdb` 或 `graph_models` | ~100% |
| SQLAlchemy | 反射 metadata 或解析模型类 | ~100% |
| Prisma | schema.prisma 本身就是声明式 ER | ~100% |
| TypeORM | 解析 `@Entity` / `@ManyToOne` 装饰器 | ~100% |

**无 ORM 项目**：SchemaSpy / SchemaCrawler 通过 JDBC 逆向工程

**API 契约提取**：
| 类型 | 方法 |
|------|------|
| REST | 代码路由定义 → OpenAPI spec |
| GraphQL | Schema 即类型定义 |
| gRPC | .proto 文件即契约 |

**APIAgent**（Agoda 开源，2026年2月）：自动从 OpenAPI/GraphQL 推断完整 schema

---

# 三、社区半魂提取（⑤⑥）

## 3.1 数据源 API 清单

### GitHub Issues/PRs

| 操作 | 端点 | 说明 |
|------|------|------|
| Issue 列表 | `GET /repos/{owner}/{repo}/issues?state=all&per_page=100` | |
| Issue 评论 | `GET /repos/{owner}/{repo}/issues/{number}/comments` | |
| PR Review | `GET /repos/{owner}/{repo}/pulls/{number}/reviews` | 含审查摘要和状态 |
| PR 行内评论 | `GET /repos/{owner}/{repo}/pulls/{number}/reviews/{review_id}/comments` | 代码行级讨论 |

速率限制：PAT 认证 5,000 次/小时。REST API Issue 评论上限约 30,000 条，超过用 GraphQL。

### GitHub Discussions（仅 GraphQL）

```graphql
query ($owner: String!, $repo: String!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    discussions(first: 100, after: $cursor) {
      nodes {
        title, body, createdAt
        answer { body, author { login } }
        comments(first: 100) { nodes { body, replies(first: 100) { nodes { body } } } }
      }
      pageInfo { hasNextPage, endCursor }
    }
  }
}
```

GraphQL 速率限制：5,000 点/小时。

### Stack Overflow

| 端点 | 用途 |
|------|------|
| `/search/advanced?tagged=项目名&accepted=True&sort=votes` | 搜索高质量问答 |
| `/questions/{ids}/answers?filter=withbody` | 获取答案正文 |
| `/tags/{tag}/related` | 发现项目生态标签 |

速率限制：无 Key 300次/天，有 Key 10,000次/天。

**质量信号**：`score >= 10` + `is_accepted` + `owner.reputation >= 10,000` + `view_count >= 10,000`

**CC BY-SA 合规**：可提取知识点用自己语言重述，不能原样引用。

### Reddit

| 方法 | 限制 | 费用 |
|------|------|------|
| PRAW（免费 OAuth） | 100次/分钟 | $0，仅限非商业 |
| 商业 API | 协议制 | $0.24/1000次 或 $12,000+/年 |

2025 年起所有 API 使用需预先审批。

### Hacker News（Algolia）

`GET https://hn.algolia.com/api/v1/search?query=项目名&tags=story`
- `numericFilters=points>50` 只取高分
- 无显式速率限制
- HN 评论者常是项目实际用户/维护者，知识密度极高

### YouTube 字幕

**官方 API 下载字幕需视频所有者 OAuth 授权——对别人的视频不可用。**

实际方案：
| 工具 | 是否需要 API Key |
|------|-----------------|
| `youtube-transcript-api`（Python） | 否 |
| `yt-dlp` + Whisper（本地转录） | 否 |
| Gemini 2.0 多模态（直接理解视频） | 需 API Key |

```python
from youtube_transcript_api import YouTubeTranscriptApi
transcript = YouTubeTranscriptApi.get_transcript("video_id")
full_text = " ".join([t["text"] for t in transcript])
```

### 博客/教程

| 方法 | 工具 |
|------|------|
| 发现 | Google Custom Search API（100次/天免费）、dev.to API、Medium RSS |
| 提取 | Jina Reader（`r.jina.ai/{url}`）、Trafilatura、Firecrawl |

## 3.2 识别"高价值"内容的启发式规则

### GitHub Issues 高价值信号

| 信号 | 原因 |
|------|------|
| 已关闭 + 有 fix commit | 解决过程含知识 |
| 评论数 >= 5 | 长讨论含决策权衡 |
| 标签含 `breaking-change`, `wontfix`, `RFC` | 直接表明是决策 |
| 含关键词 `"we decided"`, `"trade-off"`, `"rejected"` | 决策叙事语言标志 |
| PR 的 CHANGES_REQUESTED review | reviewer 解释"为什么不行" |

### Reddit 噪音过滤

| 过滤 | 方法 |
|------|------|
| 帖子质量 | `score >= 20` |
| 内容类型 | flair = Discussion/Help/Tip，忽略 Meme/Showcase |
| 关键词触发 | `"pro tip"`, `"don't use"`, `"learned the hard way"`, `"PSA"`, `"TIL"` |
| 时间衰减 | 优先近 12 个月 |

## 3.3 质量过滤技术

### LLM-as-Judge

```
评估维度（每项 1-5 分）：
1. 可操作性：是否提供具体行动建议？
2. 独特性：官方文档中找不到？
3. 可验证性：能通过代码验证？
4. 时效性：附带版本信息？
输出 JSON：{"actionability": 4, "uniqueness": 5, "verifiability": 3, "recency": 4, "keep": true}
```

LLM 与人类专家一致率约 60-68%。高置信度自动处理，边界案例人工复核。

### 情绪分析（两层）

```python
# 第一层：VADER 快速筛选（毫秒级）
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# compound > 0.5 或 < -0.5 = 强烈观点

# 第二层：RoBERTa 精细分析（准确率 92%+）
from transformers import pipeline
classifier = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
```

### 过时信息检测

| 策略 | 实现 |
|------|------|
| 版本号比对 | 正则提取 `v\d+\.\d+`，与当前版本对比 |
| 时间衰减 | `weight = 1 / (1 + months_since_publish / 12)` |
| API 验证 | 知识中提到的函数是否仍存在于代码中 |
| Changelog 交叉检查 | 功能是否被标记 deprecated/removed |

---

# 四、知识合成：从碎片到灵魂文档

## 4.1 灵魂文档格式

2026 年已形成三大标准，全部使用 Markdown：

```
SOUL.md  → 人格和价值观（不变）     = "你是谁"
CLAUDE.md → 项目规范和行为约定      = "你在这个项目怎么做事"
SKILL.md  → 专项技能和可执行代码    = "你擅长做什么"
```

**Codified Context 论文**（arXiv 2602.20478）的关键架构：
- **热记忆**：每次会话都加载的约定和协议（CLAUDE.md）
- **冷记忆**：按需通过 MCP 检索的规格文档（`.claude/context/*.md`）
- 核心洞见：**文档即基础设施**——AI Agent 依赖的"承重构件"

## 4.2 合成管道（五步）

```
Step 1: 实体提取
  KGGen / LLM 从代码和社区中提取实体和关系

Step 2: 实体解析
  合并同义实体（KGGen 聚类方法）
  代码名 ↔ 社区讨论名 映射

Step 3: 冲突解决
  代码实际运行行为 > 官方文档 > 维护者回复 > SO 高票 > 博客
  KARMA 式多 Agent 辩论机制（NeurIPS 2025，移除辩论降 4.9% 正确性）

Step 4: 知识合成
  生成分层 Soul Document：
  - 热记忆宪法（CLAUDE.md / SOUL.md）
  - 冷记忆文档（按主题分文件）
  - 知识图谱（Neo4j + 向量 DB）

Step 5: 质量验证
  RAGAS 四指标评估（Faithfulness / Relevancy / Precision / Recall）
  漂移检测脚本（代码变更时自动检查文档一致性）
```

## 4.3 冲突解决优先级

```
1. 代码的实际运行时行为（测试验证）  ← 最高权威
2. 代码注释和内联文档
3. 官方文档和 README
4. Git commit messages / PR 描述
5. GitHub Issues 中的维护者回复
6. Stack Overflow 高票回答
7. 博客文章和教程                   ← 最低权威
```

## 4.4 知识图谱构建

**KGGen（Stanford，NeurIPS 2025）**：准确率 66%，超 GraphRAG 18 个百分点

```
pip install kg-gen
# 支持 OpenAI / Anthropic / Ollama / Gemini / Deepseek
```

**Neo4j 中代码 ↔ 社区知识的链接**：

```
[Function Node]──uses──>[Library Node]──documented_in──>[SO Answer Node]
      │                       │                              │
      └──implements──>[Pattern Node]──explained_in──>[Blog Post Node]
                            │
                            └──has_pitfall──>[Known Issue Node]
```

**检索策略：混合路由**
- 简单查询 → Vector RAG（低延迟、低成本）
- 复杂关系/推理查询 → GraphRAG（高准确率，但延迟 2-3 倍）

## 4.5 增量更新

```
git diff HEAD~1 → 变更文件列表
  ├── 修改的文件 → 只重新提取这些文件的知识
  ├── 新增的文件 → 新增知识条目
  ├── 删除的文件 → 标记相关知识为 deprecated
  └── 依赖这些文件的知识 → 检查是否需要更新
```

---

# 五、从灵魂文档到 AI Agent

## 5.1 三条路径

| 路径 | 原理 | 适用场景 | 复杂度 |
|------|------|---------|--------|
| **System Prompt** | 知识直接注入 system prompt | 中小项目、知识量 <100 页 | 低 |
| **RAG** | 知识存向量 DB，按需检索 | 大项目、知识频繁更新 | 中 |
| **LoRA 微调** | 训练项目专家小模型 | 行为风格、延迟要求、隐私需求 | 高 |

**最佳实践：LoRA + RAG 组合**——RAG 提供运行时上下文，LoRA 提供生成能力。

## 5.2 推荐技术栈

| 组件 | 推荐 | 备选 |
|------|------|------|
| 代码打包 | Repomix | — |
| 知识提取 LLM | Claude Sonnet 4 | GPT-4o, Qwen3-30B |
| KG 提取 | KGGen (kg-gen) | Neo4j LLM KG Builder |
| 图数据库 | Neo4j | FalkorDB |
| 向量数据库 | Qdrant | pgvector |
| Embedding | Qwen3-Embedding-8B | BGE-M3（可自托管） |
| 代码 Embedding | UniXcoder | LoRACode（更新） |
| Agent 运行时 | Claude Opus 4 | GPT-5, Qwen3-235B |
| 评估 | RAGAS | DeepEval |
| 按需检索 | MCP Server | LangChain Tools |

---

# 六、完整管道架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                      AllInOne Soul Extraction Pipeline                │
│                                                                      │
│  ┌──────────────────┐              ┌──────────────────┐             │
│  │   SOURCE CODE     │              │  COMMUNITY DATA   │             │
│  │   GitHub Repo     │              │  SO / Reddit / HN │             │
│  │                   │              │  YouTube / Blogs  │             │
│  └────────┬─────────┘              └────────┬─────────┘             │
│           │                                  │                       │
│     ┌─────▼──────┐                    ┌─────▼──────┐                │
│     │  Repomix   │                    │  API 采集   │                │
│     │  打包+压缩  │                    │  + 爬虫     │                │
│     └─────┬──────┘                    └─────┬──────┘                │
│           │                                  │                       │
│     ┌─────▼──────┐                    ┌─────▼──────┐                │
│     │ Tree-sitter │                    │ 初筛       │                │
│     │ AST 解析    │                    │ VADER+规则  │                │
│     │ + 调用图    │                    │ ~15-25% 通过│                │
│     │ + ORM 解析  │                    └─────┬──────┘                │
│     └─────┬──────┘                          │                       │
│           │                                  │                       │
│           └──────────┬───────────────────────┘                       │
│                      │                                               │
│                ┌─────▼──────┐                                        │
│                │  KGGen      │  实体提取 + 聚类去重                    │
│                │  (Stanford) │  准确率 66%                            │
│                └─────┬──────┘                                        │
│                      │                                               │
│              ┌───────┼───────┐                                       │
│              ▼               ▼                                       │
│        ┌──────────┐   ┌──────────┐                                  │
│        │ Neo4j    │   │ Qdrant   │                                  │
│        │ 知识图谱  │   │ 向量 DB   │                                  │
│        └────┬─────┘   └────┬─────┘                                  │
│             └───────┬──────┘                                         │
│                     ▼                                                │
│        ┌────────────────────────┐                                    │
│        │  LLM 合成 + 冲突解决   │  KARMA 多 Agent 辩论               │
│        │  + 缺口标注            │                                    │
│        └───────────┬────────────┘                                    │
│                    ▼                                                 │
│        ┌────────────────────────┐                                    │
│        │  Soul Document         │                                    │
│        │  ├── 热记忆（CLAUDE.md）│  始终加载                          │
│        │  ├── 冷记忆（context/） │  MCP 按需检索                      │
│        │  └── 知识图谱           │  关系推理                          │
│        └───────────┬────────────┘                                    │
│                    ▼                                                 │
│        ┌────────────────────────┐                                    │
│        │  RAGAS 质量验证        │  + 漂移检测                         │
│        └───────────┬────────────┘                                    │
│                    ▼                                                 │
│        ┌────────────────────────┐                                    │
│        │  AI Agent Runtime      │                                    │
│        │  System Prompt + MCP   │                                    │
│        │  + Tool Calling        │                                    │
│        └────────────────────────┘                                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

# 七、成本与性能估算

## 7.1 单项目提取成本（50K 行代码中等规模）

| 阶段 | 成本 |
|------|------|
| 代码打包（Repomix） | $0（本地执行） |
| GitHub/SO/HN API 调用 | $0（免费额度内） |
| Reddit（商业） | $0.12 |
| 博客提取 | $0-2 |
| LLM 知识提取 | $4-12 |
| LLM 冲突解决 | $3-8 |
| Soul Document 生成 | $2-5 |
| RAGAS 评估 | $2-5 |
| Embedding 生成 | $0.25 |
| **首次提取总计** | **$12-38** |
| **增量更新（每次）** | **$1-5** |

## 7.2 处理时间

| 阶段 | 50K 行项目 |
|------|-----------|
| Repomix 打包 | ~5 秒 |
| 静态分析（AST+调用图） | ~1-3 分钟 |
| 社区数据采集 | ~30-60 分钟（受 API 限速） |
| 初筛 | ~2-5 分钟 |
| LLM 深度提取 | ~20-40 分钟 |
| 知识合成 | ~3-5 分钟 |
| 质量验证 | ~5-10 分钟 |
| **总计** | **~1-2 小时** |

## 7.3 存储

| 数据 | 规模 |
|------|------|
| 原始采集数据 | ~50-200 MB |
| 处理后知识条目 | ~2-5 MB |
| Embedding 向量 | ~10-20 MB |
| 知识图谱 | ~5-10 MB |
| **总计/项目** | **~70-250 MB** |

---

# 八、现有开源实现分析

| 工具 | 做什么 | 内部原理 | 与 AllInOne 的关系 |
|------|--------|---------|-------------------|
| **Repomix** | 代码打包成 AI 友好格式 | globby 发现+Tree-sitter 压缩+Secretlint 安检+Tinypool 并行 | 管道第一步：打包 |
| **RepoAgent**（清华） | 仓库级文档自动生成 | AST 全局结构分析→LLM 语义推断→Git hook 增量更新 | 可作代码半魂提取器 |
| **PocketFlow** | 代码库转教程 | "鹰眼+深潜"方法论，RAG 架构，仅 100 行框架 | 参考方法论 |
| **DeepWiki** | GitHub 仓库交互式 Wiki | Next.js+FastAPI，AdalFlow 分块+嵌入，RAG 问答 | 最接近的竞品（但只做理解不做服务化） |
| **KGGen** | 文本→知识图谱 | LLM 迭代实体提取+聚类去重，NeurIPS 2025 | 知识图谱构建核心工具 |

---

# 九、关键技术结论

1. **代码半魂提取已成熟**：Tree-sitter + 调用图 + ORM 解析的组合可覆盖 ①②③④ 四类知识，准确度 70-85%。

2. **社区半魂提取可行但需要强过滤**：API 通道完整（GitHub/SO/HN 免费，Reddit 受限），核心挑战是噪音过滤和过时检测。

3. **合成是最难的一步**：不是简单拼接，是冲突解决 + 权重排序 + 缺口标注的知识融合。KARMA 多 Agent 辩论方法值得采用。

4. **静态分析 + LLM 的组合是最优解**：静态分析不幻觉但不懂含义，LLM 懂含义但会幻觉。两者互补。

5. **YouTube 视频是未被触及的金矿**：`youtube-transcript-api` + Gemini 多模态 = 提取调试视频中的操作经验。竞品未做。

6. **灵魂文档不是一个文件，是一个分层系统**：热记忆（始终加载）+ 冷记忆（按需检索）+ 知识图谱（关系推理）。

7. **成本可控**：$12-38/项目首次提取，$1-5 增量更新。千级项目规模约 $12,000-38,000。

---

# 附录：核心参考资料

## 工具
- [Tree-sitter](https://github.com/tree-sitter/tree-sitter) / [IBM COMEX](https://github.com/IBM/tree-sitter-codeviews)
- [Repomix](https://github.com/yamadashy/repomix) / [RepoAgent](https://github.com/OpenBMB/RepoAgent)
- [KGGen](https://github.com/stair-lab/kg-gen) / [DeepWiki-Open](https://github.com/AsyncFuncAI/deepwiki-open)
- [PyCG](https://github.com/vitsalis/PyCG) / [Pyan](https://github.com/Technologicat/pyan) / [Aider](https://github.com/Aider-AI/aider)
- [Semgrep](https://github.com/semgrep/semgrep) / [CodeQL](https://github.com/github/codeql)
- [RAGAS](https://docs.ragas.io/) / [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)

## 论文
- Repository Intelligence Graph (RIG), arXiv 2601.10112
- Codified Context Infrastructure, arXiv 2602.20478
- KGGen, arXiv 2502.09956, NeurIPS 2025
- KARMA Multi-Agent KG Enrichment, NeurIPS 2025
- RepoAgent, EMNLP 2024
- BREX Business Rules Extraction, arXiv 2505.18542
- RAG vs GraphRAG Evaluation, arXiv 2502.11371

## API 文档
- [GitHub REST API](https://docs.github.com/en/rest) / [GraphQL API](https://docs.github.com/en/graphql)
- [Stack Exchange API](https://api.stackexchange.com/docs)
- [HN Algolia API](https://hn.algolia.com/api)
- [PRAW](https://praw.readthedocs.io/)
- [YouTube Data API v3](https://developers.google.com/youtube/v3)

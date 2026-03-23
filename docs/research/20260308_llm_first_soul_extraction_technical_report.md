# AllInOne 灵魂提取技术方案 v2（LLM-First）

**日期**: 2026-03-08
**版本**: v0.2
**性质**: 纯技术调研——基于 LLM 的灵魂提取最佳工程实践
**核心前提**: 提取出的灵魂必须是为 LLM 消费而设计的，因为最终是 LLM 为用户交付服务

---

# 一、设计原则：为什么是 LLM-First

## 1.1 价值链决定技术路线

```
提取灵魂 → 灵魂以某种形式存储 → LLM 读取灵魂 → LLM 为用户交付服务
```

如果灵魂不是为 LLM 准备的，后面全断。因此：
- **提取工具**应该是 LLM 本身（LLM 最懂什么格式自己用起来最好）
- **存储格式**应该是 LLM 最擅长处理的格式
- **质量验证**应该是"LLM 用这个灵魂能不能更好地服务用户"

## 1.2 LLM vs 静态分析：最新数据

2025 年基准测试（GPT-4.1 / Mistral-Large / DeepSeek V3 vs SonarQube / CodeQL / SnykCode）：

| 指标 | LLM | 静态分析工具 |
|------|-----|-------------|
| F1 分数 | **0.75 - 0.80** | 0.26 - 0.55 |
| 召回率 | 高（理解上下文） | 低（受限于规则） |
| 精确度 | 中（有幻觉风险） | 高（确定性规则） |

**关键结论**：对于提取"灵魂"——领域概念、架构模式、业务逻辑、设计决策——LLM **优于**静态分析。静态分析的优势（精确的语法解析）对于知识提取场景不是关键需求。

## 1.3 AllInOne 与低代码/无代码的本质区别

| | 低代码/无代码 | AllInOne |
|---|---|---|
| 知识在哪 | **用户脑子里** | **系统里**（从开源世界提取） |
| 用户需要知道 | 怎么做 | 想要什么结果 |
| 本质 | 更好的锤子 | 自带经验的师傅 |

这意味着灵魂提取的质量直接决定了 AllInOne 能否提供有价值的服务。

---

# 二、提取什么：六类知识

| 类型 | 知识 | 来源 | LLM 可提取性 |
|------|------|------|-------------|
| ① 领域知识（WHAT） | 概念、实体、分类法、数据模型 | 代码 + 文档 | 高 |
| ② 流程经验（HOW） | 工作流、步骤、状态机 | 代码 + 文档 + 示例 | 高 |
| ③ 判断规则（IF/WHEN） | 条件分支、业务规则 | 代码 | 高 |
| ④ 数据关系（STRUCTURE） | ER 关系、API 契约 | 代码 + Schema | 高 |
| ⑤ 踩坑教训（WHY） | 决策原因、失败教训 | Issue/PR/社区讨论 | 中 |
| ⑥ 未说出口的常识（UNSAID） | 社区心照不宣的最佳实践 | Reddit/HN/YouTube/博客 | 中 |

**核心判断**：⑤⑥ 的价值 ≥ ①②③④。代码逻辑是免费的，但"在什么场景下该怎么做"的决策智慧是昂贵的。

---

# 三、代码半魂提取（①②③④）：LLM-First 方法

## 3.1 核心管道：Repomix + LLM

**Repomix** 把整个代码仓库打包成一个 LLM 友好的文件：

```bash
repomix --remote user/repo --compress --style xml -o packed.xml
```

- `--compress`：用 Tree-sitter 只保留函数签名和结构，去掉函数体，**token 减少约 70%**
- `--style xml`：XML 格式，研究表明 LLM 解析 XML 最准确
- `--token-count-tree`：查看哪些目录/文件消耗最多 token
- `--split-output 1mb`：超大仓库自动分割

**这是唯一用到 Tree-sitter 的地方**——仅作为 Repomix 内部的压缩工具，不需要我们自己操作。

## 3.2 大仓库处理策略

现代 LLM 上下文窗口 200K-2M token，但典型生产代码库可能有数百万 token。

### 策略 A：鹰眼 + 深潜（推荐，来自 PocketFlow）

```
第一轮（鹰眼）：
  Repomix 压缩后的代码 → LLM
  Prompt："识别这个项目的 5-10 个核心抽象概念，
          每个概念给出：
          - 一句话描述（普通人能懂的类比）
          - 涉及哪些文件"

第二轮（深潜）：
  对每个核心概念 → 读取相关文件的完整代码 → LLM
  Prompt："深入分析这个概念：
          - 它解决什么问题
          - 工作流程是什么
          - 有哪些业务规则
          - 有哪些边界条件和异常处理"

第三轮（关系映射）：
  所有概念的提取结果 → LLM
  Prompt："这些概念之间是什么关系？
          - 谁调用谁
          - 数据怎么流动
          - 依赖关系"
```

**为什么这方法最好**：它模仿人类专家理解项目的方式——先看全貌，再逐个深入。PocketFlow 用这个方法在 Hacker News 获得 900+ 赞（2025年4月），并以此为基础推出了 code2tutorial.com。

### 策略 B：Map/Reduce 摘要（超大仓库）

当代码库超过任何上下文窗口时：
1. 按模块/目录分块
2. 每块独立提取知识
3. 合并所有块的知识，用 LLM 去重和融合

**关键论文**：LLMxMapReduce（2024）识别了两个核心问题：
- **跨块依赖**：证据分散在多个块中会丢失
- **跨块冲突**：不同块可能包含矛盾信息
解决方案：结构化信息协议，在块之间传递上下文。

### 策略 C：Aider RepoMap 风格（最小化 Tree-sitter）

1. Tree-sitter 仅用于提取函数定义和引用关系
2. 构建 NetworkX 有向图
3. **PageRank 排序**找出最重要的函数/类
4. 只把 top-ranked 符号传给 LLM（默认仅 1K token）

**适用场景**：当你需要快速定位"这个项目最核心的代码在哪"时，作为鹰眼阶段的辅助。

## 3.3 提取 Prompt 链

### Prompt 链 1：架构发现

```
Step 1: "列出所有文件及其用途（基于命名和导入关系）"
Step 2: "识别核心抽象/组件及其职责"
Step 3: "映射组件之间的关系（调用关系、数据流）"
Step 4: "描述整体架构模式（MVC、微服务等）"
```

### Prompt 链 2：业务规则提取

```
Step 1: "识别所有条件逻辑、验证规则和约束"
Step 2: "对每条规则描述：触发条件、执行动作、影响的数据"
Step 3: "按业务领域分组（用户认证、支付等）"
Step 4: "输出结构化 JSON：rule_id, domain, condition, action"
```

### Prompt 链 3：数据模型提取

```
Step 1: "识别所有数据结构、Schema、类型及其字段"
Step 2: "映射实体之间的关系（1:1, 1:N, N:N）"
Step 3: "识别验证约束和默认值"
Step 4: "生成 ER 关系描述"
```

### Prompt 工程最佳实践

| 技术 | 效果 |
|------|------|
| Few-shot 示例（3个） | 比 zero-shot 显著提升结构化提取质量 |
| Chain-of-Thought | 帮助 LLM 推理实体类型和关系 |
| 结构化输出（JSON Schema） | 防止输出格式漂移 |
| Prompt 链（N步串联） | 比一个巨大 prompt 更好处理复杂任务 |

来源：Polat, Tiddi & Groth (2025) 测试了 17 种 prompt 模板，结论是"简单指令 + 3 个检索选择的示例"显著优于 zero-shot 或纯 CoT。

## 3.4 DeepWiki 方法（参考）

DeepWiki 的完整管道：
1. 克隆仓库
2. 文件扫描 + 过滤（区分实现代码 vs 测试代码）
3. Token 验证（跳过超大文件）
4. AdalFlow TextSplitter 分块（重叠分块，保留上下文）
5. 嵌入生成（OpenAI/Google/Ollama，500 批次）
6. FAISS 向量索引

**适用场景**：当项目灵魂超过 200K token 需要 RAG 时参考其架构。

---

# 四、社区半魂提取（⑤⑥）：LLM-First 方法

## 4.1 数据源 API 清单

### GitHub Issues/PRs（REST API）

| 操作 | 端点 |
|------|------|
| Issue 列表 | `GET /repos/{owner}/{repo}/issues?state=all&per_page=100` |
| Issue 评论 | `GET /repos/{owner}/{repo}/issues/{number}/comments` |
| PR Review | `GET /repos/{owner}/{repo}/pulls/{number}/reviews` |
| PR 行内评论 | `GET /repos/{owner}/{repo}/pulls/{number}/reviews/{review_id}/comments` |

速率限制：PAT 认证 5,000 次/小时。

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

### Stack Overflow

| 端点 | 用途 |
|------|------|
| `/search/advanced?tagged=项目名&accepted=True&sort=votes` | 高质量问答 |
| `/questions/{ids}/answers?filter=withbody` | 答案正文 |

速率限制：有 Key 10,000次/天。质量信号：`score >= 10` + `is_accepted`。

### Reddit

PRAW（免费 OAuth），100次/分钟，仅限非商业。2025 年起需预先审批。

### Hacker News（Algolia）

`GET https://hn.algolia.com/api/v1/search?query=项目名&tags=story&numericFilters=points>50`
无显式速率限制。HN 评论者常是实际维护者，知识密度极高。

### YouTube 字幕

```python
from youtube_transcript_api import YouTubeTranscriptApi
transcript = YouTubeTranscriptApi.get_transcript("video_id")
full_text = " ".join([t["text"] for t in transcript])
```

### 博客/教程

| 方法 | 工具 |
|------|------|
| 发现 | Google Custom Search API、dev.to API、Medium RSS |
| 提取 | Jina Reader（`r.jina.ai/{url}`）、Trafilatura、Firecrawl |

## 4.2 三层过滤管道（LLM-First）

传统方案用 VADER + 关键词匹配做初筛。但 VADER 准确率仅 56-60%，无法处理讽刺、隐喻、多语言。

**LLM-First 三层方案**：

```
Tier 1: 规则初筛（免费，即时）
  → 删除：太短（<50字）、纯 emoji、bot 消息、CI 输出、+1 评论
  → 通过率：~50%

Tier 2: 小模型分类（GPT-4o-mini / Gemini Flash，~$0.30/M token）
  → 判断：是否与项目使用经验相关？是否包含可操作建议？
  → 输出：relevance_score (1-5), content_type (问题/解决方案/经验/观点)
  → 通过率：~40%（即总数据的 20%）

Tier 3: 大模型深度提取（Claude / GPT-4o，~$3/M token）
  → 仅处理 Tier 2 通过的高价值内容
  → 结构化输出：问题、解决方案、适用条件、注意事项、来源
  → 使用 LangExtract / ContextGem 模式确保来源可追溯
```

### 成本估算

处理 10,000 条社区帖子（平均 500 token/条）：

| 层 | 处理量 | 成本 |
|----|--------|------|
| Tier 1 规则初筛 | 10,000 条 | $0 |
| Tier 2 小模型 | 5,000 条 (2.5M token) | $0.75 |
| Tier 3 大模型 | 1,000 条 (1.5M token) | $4.50 |
| **总计** | | **~$5.25** |

## 4.3 GitHub Issue 线程知识提取

Issue 是多轮对话，知识埋在噪音中。最佳实践：

1. **展平线程**：`[作者] [时间] [角色: 提问者/维护者/贡献者] [内容]`
2. **标记解决信号**：关闭/合并状态、"this fixed it" 短语、采纳的答案
3. **LLM 提取**：问题描述、尝试过的方案、最终解决方案、注意事项、关联 Issue
4. **过滤噪音**：在发给 LLM 之前删除 +1 评论、bot 消息、CI 输出、重复引用

**推荐工具**：
- **Google LangExtract**（2025年7月开源）：精确来源溯源（每个提取事实映射到原文的具体字符位置），2 次提取达 93% 召回率，3 次达 96%，**反幻觉设计**
- **ContextGem**（2025）：双 LLM 管道——小模型提取主题，大模型推理。从 40 页文档提取 20 个概念仅需 ~$0.18、~8 秒

## 4.4 YouTube 视频知识提取

YouTube 调试演示视频是最丰富的 ⑥ 类知识来源。

**管道**：
1. `youtube-transcript-api` 获取字幕
2. 清洗：合并短片段、用小模型加标点
3. 如果 <100K token：直接整体发给 LLM 提取
4. 如果 >100K token：Map/Reduce 分块（2000 token/块，15% 重叠）
5. LLM 提取：关键主张、操作步骤、工具推荐、观点 vs 事实、关键时刻的时间戳

**工具**：Cleanscript.ai 可将 YouTube 视频转为 LLM 优化的干净字幕。

## 4.5 跨源知识融合

同一个话题在 GitHub Issue、Stack Overflow、Reddit 和博客中都被讨论过时：

1. **独立提取**：从每个来源提取结构化知识条目（问题、方案、上下文、来源、日期、置信度）
2. **语义去重**：用嵌入相似度聚类关于同一话题的条目
3. **LLM 融合**：将同一话题的所有条目呈现给 LLM，要求合成统一条目、标记冲突
4. **来源优先级**：

```
1. 代码的实际运行行为（测试验证）  ← 最高权威
2. 官方文档和 README
3. GitHub Issues 中维护者的回复
4. Stack Overflow 高票采纳答案
5. Reddit/HN 高赞评论
6. 博客文章和教程                ← 最低权威
```

## 4.6 过时信息处理

社区内容老化很快。2022 年关于 Next.js 12 的 SO 回答用在 Next.js 15 上可能有害。

| 策略 | 实现 |
|------|------|
| 时间标记 | 每条知识必须带日期 |
| 版本标记 | 提取版本号作为元数据（"适用于 v14.x"） |
| 衰减评分 | `relevance = base_score × 1/(1 + months/12)` |
| 矛盾检测 | 新来源与旧来源矛盾时，标记旧条目为"可能过时" |
| LLM 新鲜度检查 | 定期问 LLM："这个建议在 2026 年是否仍然适用？" |

---

# 五、灵魂文档：为 LLM 消费而设计的知识格式

## 5.1 为什么选择结构化 Markdown

2025-2026 年对嵌套数据格式的基准测试：

| 格式 | GPT-5 Nano | Llama 3.2 | Gemini 2.5 |
|------|-----------|----------|-----------|
| **YAML** | **62.1%** | 49.1% | **51.9%** |
| **Markdown** | 54.3% | 48.0% | 48.2% |
| JSON | 50.3% | **52.7%** | 43.1% |
| XML | 44.4% | 50.7% | 33.8% |

关键事实：
- **Markdown 比 JSON 省 34-38% token**
- Markdown 是 LLM 训练数据中最多的格式（网页内容本质上就是 Markdown-like）
- 人类可读，方便调试
- YAML 在嵌套/结构化数据上表现最好 → **Markdown 正文 + YAML 块**是最佳组合

## 5.2 三层灵魂架构（Codified Context 论文，arXiv 2602.20478）

```
┌─────────────────────────────────────────────────┐
│  热记忆（Hot Memory）— 始终加载                   │
│  SOUL.md：项目身份、核心架构、关键模式             │
│  < 500 行，< 200K token                          │
│  放在 system prompt 的开头（避免 Lost-in-Middle） │
├─────────────────────────────────────────────────┤
│  冷记忆（Cold Memory）— 按需检索                  │
│  每个子系统/主题一个 .md 文件                      │
│  结构化分块，Contextual Retrieval 嵌入            │
│  通过 MCP 或 RAG 管道按需加载                     │
├─────────────────────────────────────────────────┤
│  知识图谱（可选）— 关系推理                       │
│  仅当需要跨概念复杂关系推理时                      │
│  FalkorDB 报告：幻觉减少 90%，查询延迟 <50ms     │
└─────────────────────────────────────────────────┘
```

**关键数据**（Codified Context 论文，283 个会话，108K 行 C#）：
- 热记忆宪法：~660 行 Markdown
- 19 个专业 Agent，平均 327-711 行
- 34 个冷记忆规格文档，共 ~16,250 行
- 上下文基础设施 = 代码库的 24.2%

**核心洞见**：文档不是文档，是基础设施——AI Agent 依赖的"承重构件"。当灵魂文档过时或结构不良时，AI Agent 就会输出错误结果。

## 5.3 灵魂文档模板

```markdown
# [项目名] Soul Document

## 身份
- 这个项目帮 [谁] 解决 [什么问题]
- 核心能力：[1-3 句话]

## 领域模型（WHAT）
### 核心概念
- **[概念A]**：[一句话解释 + 普通人能懂的类比]
- **[概念B]**：...

### 概念关系
```yaml
关系:
  - 概念A --包含--> 概念B
  - 概念B --依赖--> 概念C
```

## 工作流程（HOW）
### 主流程
1. [步骤1]：[做什么，为什么]
2. [步骤2]：...

### 异常流程
- 如果 [条件X]：[怎么处理]

## 业务规则（IF/WHEN）
```yaml
规则:
  - 条件: "[具体条件]"
    动作: "[具体动作]"
    原因: "[为什么有这条规则]"
```

## 数据结构（STRUCTURE）
### 核心实体
```yaml
实体:
  - 名称: "[实体名]"
    字段:
      - name: "[字段名]"
        type: "[类型]"
        说明: "[业务含义]"
    关系:
      - "[与其他实体的关系]"
```

## 踩坑教训（WHY）
- ⚠️ [教训1]：[描述] — 来源：[GitHub Issue #xxx / SO 链接]
- ⚠️ [教训2]：...

## 最佳实践（UNSAID）
- ✅ [推荐做法1]：[描述] — 来源：[社区讨论链接]
- ❌ [避免做法1]：[描述] — 来源：[...]

## 常见问题
- Q: [问题1]
  A: [答案] — 来源：[...]

## 适用边界
- 适合：[场景列表]
- 不适合：[场景列表]
- 替代方案：[当不适合时推荐什么]
```

## 5.4 System Prompt vs RAG 决策

| 项目灵魂大小 | 方案 | 原因 |
|-------------|------|------|
| < 200K token（~500 页） | **直接放 system prompt** + prompt caching | Anthropic 明确推荐，省去 RAG 基础设施 |
| 200K - 1M token | **热记忆 in prompt + 冷记忆 via RAG** | 核心知识始终可用，详细信息按需检索 |
| > 1M token | **全 RAG** | 超出所有上下文窗口的实际有效范围 |

**Lost-in-the-Middle 问题**：
- LLM 对开头和结尾的信息注意力最高，中间信息准确率下降 20-30%
- NoLiMa 基准：在 32K token 时，12 个模型中 11 个降至短上下文性能的 50% 以下
- **解决方案**：最重要的灵魂放在 prompt 开头，不要埋在中间

**Prompt 压缩**：
- Microsoft LLMLingua：最高 **20x 压缩**，性能损失极小
- LLMLingua-2：将压缩问题转化为 token 分类问题，用 BERT 大小的模型完成，速度快成本低
- 可将一个项目的完整灵魂压缩到 system prompt 可承受的范围

## 5.5 RAG 最佳实践（当需要时）

### 分块策略

2026年2月基准测试（7种策略，50篇学术论文）：
- **递归 512-token 分块：69% 准确率**（胜出）
- 语义分块：54% 准确率（碎片化严重，平均仅 43 token）
- NAACL 2025 结论：语义分块的计算成本不值得——固定 200 词分块同样好甚至更好

**对代码知识**：按代码结构分块（函数、类、模块），不按字符数。

### Anthropic Contextual Retrieval（突破性方法）

在嵌入前，为每个 chunk 添加上下文前缀：

```
原始 chunk：
"The company's revenue grew by 3%"

添加上下文后：
"[这段来自 Acme Corp 2024 Q3 SEC 文件的财务摘要部分]
The company's revenue grew by 3%"
```

效果：
- 仅 Contextual Embeddings：检索失败减少 **35%**
- + Contextual BM25：减少 **49%**
- + Reranking：减少 **67%**

### 嵌入模型推荐

| 模型 | 优势 | 许可 |
|------|------|------|
| **Qwen3 Embedding** | 100+ 自然语言 + 编程语言，指令感知 | 开源 |
| **Nomic Embed V2** | MoE 架构，100+ 编程语言，高效 | 开源 |
| **CodeXEmbed (7B)** | 代码检索 SOTA，CoIR 排行榜第一 | 研究用途 |
| **BGE-M3** | 密集 + 稀疏 + 多向量混合检索 | 开源 |

### 混合搜索

密集嵌入（语义）+ BM25（关键词），权重比 4:1，取 top-20 结果。

---

# 六、完整管道架构

## 6.1 端到端流程

```
┌─────────────────────────────────────────────────────────────────┐
│                 AllInOne Soul Extraction Pipeline (LLM-First)    │
│                                                                  │
│  ┌──────────────────┐              ┌──────────────────┐         │
│  │   SOURCE CODE     │              │  COMMUNITY DATA   │         │
│  │   GitHub Repo     │              │  SO / Reddit / HN │         │
│  │                   │              │  YouTube / Blogs  │         │
│  └────────┬─────────┘              └────────┬─────────┘         │
│           │                                  │                   │
│     ┌─────▼──────┐                    ┌─────▼──────┐            │
│     │  Repomix   │                    │  API 采集   │            │
│     │  --compress │                    │  GitHub/SO/ │            │
│     │  --style xml│                    │  Reddit/HN/ │            │
│     └─────┬──────┘                    │  YouTube    │            │
│           │                           └─────┬──────┘            │
│           │                                  │                   │
│     ┌─────▼──────┐                    ┌─────▼──────┐            │
│     │  LLM       │                    │  三层过滤   │            │
│     │  鹰眼+深潜  │                    │  规则→小模型 │            │
│     │  Prompt 链  │                    │  →大模型    │            │
│     └─────┬──────┘                    └─────┬──────┘            │
│           │                                  │                   │
│           └──────────┬───────────────────────┘                   │
│                      │                                           │
│                ┌─────▼──────┐                                    │
│                │  LLM 融合   │                                    │
│                │  去重+冲突  │                                    │
│                │  解决+补缺  │                                    │
│                └─────┬──────┘                                    │
│                      │                                           │
│                ┌─────▼──────┐                                    │
│                │  Soul Doc   │                                    │
│                │  生成       │                                    │
│                │  Markdown   │                                    │
│                │  + YAML     │                                    │
│                └─────┬──────┘                                    │
│                      │                                           │
│              ┌───────┼───────┐                                   │
│              ▼               ▼                                   │
│        ┌──────────┐   ┌──────────┐                              │
│        │ 热记忆    │   │ 冷记忆    │                              │
│        │ SOUL.md  │   │ RAG 索引  │                              │
│        │ <500行   │   │ (按需)    │                              │
│        └────┬─────┘   └────┬─────┘                              │
│             └───────┬──────┘                                     │
│                     ▼                                            │
│        ┌────────────────────────┐                                │
│        │  RAGAS 质量验证        │                                │
│        │  + Lynx 幻觉检测      │                                │
│        └───────────┬────────────┘                                │
│                    ▼                                             │
│        ┌────────────────────────┐                                │
│        │  AI Agent Runtime      │                                │
│        │  System Prompt (热记忆)│                                │
│        │  + MCP/RAG (冷记忆)   │                                │
│        │  + Tool Calling       │                                │
│        └────────────────────────┘                                │
└─────────────────────────────────────────────────────────────────┘
```

## 6.2 与之前方案的对比

| | v1（静态分析 + LLM 混合） | v2（LLM-First） |
|---|---|---|
| 代码分析工具 | Tree-sitter + CodeQL + Semgrep + ORM 解析 | Repomix（内置 Tree-sitter 压缩）+ LLM |
| 社区过滤 | VADER + 规则 → LLM | 规则 → 小 LLM → 大 LLM |
| 知识表示 | 知识图谱（Neo4j + 向量 DB） | 结构化 Markdown（热记忆 + 冷记忆） |
| 需要搭建的工具链 | 6+ 种工具 | Repomix + LLM API |
| 技术门槛 | 需要静态分析专业知识 | 需要 Prompt 工程能力 |
| 架构复杂度 | 高 | **低** |

---

# 七、质量验证：灵魂是否有用

## 7.1 验证的正确问题

不是"提取准不准"，而是"**LLM 用这个灵魂，能不能更好地为用户服务**"。

## 7.2 RAGAS 评估框架

| 指标 | 衡量什么 |
|------|---------|
| Context Precision | 检索到的内容是否真的相关？ |
| Context Recall | 是否找到了所有相关信息？ |
| **Faithfulness** | 生成的回答是否基于灵魂内容（不是幻觉）？ |
| **Answer Relevancy** | 回答是否真的解决了用户的问题？ |

**对 AllInOne 最重要的指标**：Faithfulness（忠实度）——Agent 的回答是否基于项目的真实知识，而不是编造的。

## 7.3 A/B 验证法

```
组 A：LLM 没有灵魂文档，直接回答用户问题
组 B：LLM 加载了灵魂文档，回答同样的问题

对比：
- 回答的准确性（人工评判）
- 回答的具体性（是否给出了项目特定的建议而非通用建议）
- 回答的可操作性（用户能否直接照做）
- 幻觉率（回答中编造的信息比例）
```

## 7.4 合成测试生成

RAGAS 支持自动生成测试问题，减少人工标注 90%。

对每个项目的灵魂：
1. 自动生成 50-100 个测试问题（涵盖六类知识）
2. 用有灵魂和无灵魂的 LLM 分别回答
3. 对比 Faithfulness 和 Answer Relevancy
4. 如果差异不显著 → 灵魂提取质量有问题，需要迭代

## 7.5 幻觉检测

**Lynx**（开源）：在长上下文场景下，幻觉检测优于 RAGAS。作为 RAGAS 的补充使用。

---

# 八、成本与性能估算

## 8.1 单项目提取成本（50K 行代码中等规模）

| 阶段 | 成本 |
|------|------|
| Repomix 打包 | $0（本地执行） |
| 代码半魂 LLM 提取（鹰眼+深潜） | $3-8 |
| GitHub/SO/HN API 调用 | $0（免费额度内） |
| 社区数据三层过滤+提取 | $5-10 |
| 知识融合 + 冲突解决 | $2-5 |
| Soul Document 生成 | $1-3 |
| RAGAS 评估 | $2-5 |
| **首次提取总计** | **$13-31** |
| **增量更新（每次）** | **$2-6** |

## 8.2 处理时间

| 阶段 | 50K 行项目 |
|------|-----------|
| Repomix 打包 | ~5 秒 |
| LLM 代码分析（鹰眼+深潜） | ~15-30 分钟 |
| 社区数据采集 | ~30-60 分钟（受 API 限速） |
| 三层过滤 | ~10-20 分钟 |
| 知识融合 | ~5-10 分钟 |
| Soul Document 生成 | ~3-5 分钟 |
| 质量验证 | ~5-10 分钟 |
| **总计** | **~1-2.5 小时** |

## 8.3 成本优化策略

| 策略 | 节省幅度 |
|------|---------|
| **模型路由**（RouteLLM，ICLR 2025） | 2x+ 成本降低，不损失质量 |
| **批量处理**（OpenAI Batch API） | 50% 折扣（24 小时 SLA） |
| **语义缓存** | 15-30%（相似查询复用响应） |
| **Prompt 压缩**（LLMLingua） | 最高 20x 压缩 |
| **级联路由**（ETH Zurich，ICML 2025） | 比单独路由再提升 14% |

---

# 九、推荐技术栈

| 组件 | 推荐 | 备选 |
|------|------|------|
| 代码打包 | **Repomix** | — |
| 知识提取 LLM | **Claude Sonnet 4** | GPT-4o, Gemini 2.5 Pro |
| 小模型过滤 | **GPT-4o-mini** | Gemini Flash, 本地 Llama |
| 结构化提取 | **Google LangExtract** | ContextGem |
| 嵌入模型 | **Qwen3 Embedding** | Nomic Embed V2, BGE-M3 |
| 向量数据库（如需 RAG） | **Qdrant** | pgvector |
| Agent 运行时 | **Claude Opus 4** | GPT-5 |
| 评估 | **RAGAS** + **Lynx** | DeepEval |
| Prompt 压缩 | **LLMLingua-2** | — |
| 模型路由 | **RouteLLM** | Cascade Routing |

---

# 十、关键技术结论

1. **LLM-First 是正确路线**：LLM 在"理解代码灵魂"这件事上已经优于静态分析工具（F1: 0.75-0.80 vs 0.26-0.55）。不需要搭建复杂的工具链。

2. **Repomix 是唯一必需的非 LLM 工具**：它用 Tree-sitter 做压缩（减少 70% token），但这对我们是透明的——我们只需要运行一条命令。

3. **鹰眼+深潜是最佳提取方法论**：先让 LLM 看全貌找出核心概念，再逐个深入。这模仿了人类专家理解项目的方式。

4. **结构化 Markdown 是最佳灵魂格式**：比 JSON 省 34-38% token，LLM 理解最好，人类也能读。YAML 块处理嵌套数据。

5. **小项目灵魂直接放 system prompt**：<200K token 的灵魂不需要 RAG，直接放 prompt 开头，配合 prompt caching。

6. **社区半魂用三层 LLM 过滤**：规则→小模型→大模型，1 万条帖子仅需 ~$5，比之前 VADER + 规则方案更准确。

7. **验证标准是"灵魂有没有用"**：不是提取准确率，而是 A/B 测试——有灵魂的 LLM 是否比没有灵魂的 LLM 更好地服务用户。

8. **成本可控**：$13-31/项目首次提取，$2-6 增量更新，比 v1 方案（$12-38）略低且架构简单得多。

---

# 附录：核心参考来源

## 工具
- [Repomix](https://github.com/yamadashy/repomix) — 代码打包
- [Google LangExtract](https://github.com/google/langextract) — 结构化信息提取，来源溯源
- [ContextGem](https://github.com/shcherbak-ai/contextgem) — 双 LLM 知识提取
- [LLMLingua](https://github.com/microsoft/LLMLingua) — Prompt 压缩
- [RouteLLM](https://github.com/lm-sys/RouteLLM) — 模型路由，成本优化
- [RAGAS](https://docs.ragas.io/) — RAG 评估框架
- [Lynx](https://github.com/patronus-ai/Lynx) — 幻觉检测
- [PocketFlow](https://github.com/The-Pocket/PocketFlow) — 鹰眼+深潜方法论
- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) — YouTube 字幕提取

## 论文与基准
- LLMs vs Static Analyzers Benchmark (2025), arXiv 2508.04448
- Codified Context Infrastructure, arXiv 2602.20478
- LLMxMapReduce (2024), arXiv 2410.09342
- Contextual Retrieval, Anthropic Blog (2024)
- KARMA Multi-Agent KG Enrichment, NeurIPS 2025
- RouteLLM, ICLR 2025, arXiv 2406.18665
- Cascade Routing, ICML 2025 (ETH Zurich)
- Prompt Engineering for KE, Polat et al. (2025)
- NoLiMa Benchmark — 长上下文性能衰减
- RAG Chunking Strategies Benchmark (2026)
- LLM-as-Judge Survey, arXiv 2411.15594
- RAGAS Paper, arXiv 2309.15217

## API 文档
- [GitHub REST API](https://docs.github.com/en/rest) / [GraphQL API](https://docs.github.com/en/graphql)
- [Stack Exchange API](https://api.stackexchange.com/docs)
- [HN Algolia API](https://hn.algolia.com/api)
- [PRAW](https://praw.readthedocs.io/)

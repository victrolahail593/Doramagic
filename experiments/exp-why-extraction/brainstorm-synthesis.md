# WHY 提取改进 — 三方综合方案

> 数据来源：Gemini 2.5 Pro brainstorm + Claude Opus 独立思考 + 实验数据（44 WHYs, 2 models × 3 projects × 2 versions）
> Codex (o3) API 不可用，待后续补充。

---

## 一、改进方向总览（按杠杆率排序）

| 优先级 | 方向 | 杠杆率 | 来源 | 理由 |
|---|---|---|---|---|
| **P0** | Stage 0 智能采样 | ★★★★★ | 共识 | 输入质量是输出天花板。funNLP 5.0 vs daily_stock 7.6 的差距主要来自 Stage 0 |
| **P0** | Agentic 提取（替代单次 prompt） | ★★★★★ | Gemini | 单次 prompt 无法"顺藤摸瓜"，Agent 可以主动探索代码 |
| **P1** | 多模型生成-辩论-综合 | ★★★★ | Gemini+Opus | 已验证互补性，需要系统化合并机制 |
| **P1** | Git/PR/Issue 社会性数据源 | ★★★★ | Gemini+Opus | WHY 的原始来源是人的讨论，不只是代码 |
| **P2** | 自动化评分（LLM + 确定性校验） | ★★★ | 共识 | 规模化的前提是自动质量门控 |
| **P2** | 对比式提取（Contrastive） | ★★★ | Opus | 先生成"应该怎么做"再找差异 |
| **P3** | WHY 元数据扩展 | ★★ | Opus | confidence, impact_scope, prerequisite_knowledge |
| **P3** | Prompt 继续微调 | ★ | 共识 | 边际效益递减，v2→v3 提升空间 <0.3 |

---

## 二、P0-A：Stage 0 智能采样方案

### 现状问题
- 当前策略：按文件大小 Top 3 × 前 150 行
- 失败案例：funNLP（几乎没有代码，大文件是 README）、自动生成的文件被误选

### 改进方案：四层漏斗采样

```
Layer 1: 结构性文件（必选）
├── README.md / CONTRIBUTING.md / ARCHITECTURE.md
├── 配置文件: pyproject.toml, setup.cfg, Dockerfile, docker-compose.yml
├── CI/CD: .github/workflows/*.yml
└── 入口文件: main.py, app.py, __main__.py, manage.py

Layer 2: Import 依赖图中心度（新增）
├── 扫描所有 import 语句，构建文件依赖图
├── 按入度(in-degree)排序
└── 取 Top 5 被依赖最多的文件

Layer 3: Git 变更热点（新增）
├── git log --stat --since="1 year ago" 分析变更频率
├── 按变更行数 × 提交次数排序
└── 取 Top 5 热点文件（排除 lock 文件和自动生成文件）

Layer 4: AST 语义块提取（替代"前 150 行"）
├── 用 AST 解析器提取完整的类/函数定义
├── 优先提取: 抽象基类(ABC)、@abstractmethod、__init__ 方法
├── 每个文件提取最重要的 3-5 个语义块
└── 保留完整签名和 docstring，截断过长的函数体（>80 行取首尾各 30 行）
```

### 对 funNLP 的特殊处理
- 代码极少的项目：触发"非代码资产优先"模式
- 提取 README 的结构分析（H2 标题列表 + 链接分类统计）
- 提取目录结构的组织逻辑
- 这类项目的 WHY 主要在"信息架构"层面，而非"代码实现"层面

---

## 三、P0-B：Agentic 提取（从单次 Prompt 到多步探索）

### 核心理念
当前流程是 `Stage 0 → 固定输入 → LLM 单次生成 WHYs`，LLM 无法"追问"。

改为：`Stage 0 → 初始上下文 → Agent 循环（读代码 → 提问 → 读更多代码 → 确认/修正 → 输出）`

### 具体设计

```
Agent Loop:
1. 读取 Stage 0 基础信息
2. 生成初步假设："我怀疑这个项目在 X 方面有一个设计选择..."
3. 工具调用：搜索相关文件、读取特定函数、grep 特定模式
4. 验证或推翻假设
5. 重复 2-4 直到发现 5-8 条有充分证据的 WHY
6. 输出最终结果
```

### 与当前流程的对比
| | 当前（单次 Prompt） | Agentic 提取 |
|---|---|---|
| 信息访问 | 固定 Stage 0 输出 | 可以动态读取任意文件 |
| 证据质量 | 受限于采样命中率 | 可以主动搜索验证 |
| 覆盖范围 | 取决于采样运气 | 系统性探索 |
| 成本 | 1 次 API 调用 | 5-15 次 API 调用 |
| 延迟 | ~10 秒 | ~2-5 分钟 |

### 关键约束
- Agent 必须有访问完整 repo 的能力（git clone 到临时目录）
- 需要限制最大探索步数（防止无限循环）
- 仍然保留 Stage 0 作为 Agent 的初始上下文（冷启动加速）

---

## 四、P1-A：多模型生成-辩论-综合

### Gemini 的"GDS 模式"（我认为最有价值的新想法）

```
Phase 1 - Generate（并行）:
  Sonnet → WHYs_A (深度优先)
  Gemini → WHYs_B (广度优先)

Phase 2 - Debate（交叉质询）:
  Sonnet 评审 WHYs_B: "哪些你认同？哪些你认为证据不足？"
  Gemini 评审 WHYs_A: "哪些你认同？哪些你认为遗漏了重要背景？"

Phase 3 - Synthesize（仲裁合并）:
  Opus 作为仲裁者:
  - 输入: WHYs_A + WHYs_B + Sonnet评审 + Gemini评审
  - 输出: 去重合并后的最终 WHYs 列表
  - 规则: 两个模型都认可的 WHY → 直接保留
         只有一个模型提出但另一个认可 → 保留
         被质疑且无法补充证据 → 丢弃
```

### 成本估算
- 当前：1 次 API 调用
- GDS 模式：4 次 API 调用（2 生成 + 2 交叉 + 1 合并 ≈ 5 次）
- 成本 ×5，但质量可能从 7.1 → 8.0+

---

## 五、P1-B：社会性数据源（Git History + PR + Issue）

### 数据源优先级
1. **Commit Messages**（最易获取）：筛选 `Refactor`、`Change`、`Add support for`、`Breaking` 关键词的提交
2. **PR Descriptions**（中等获取）：GitHub API 拉取 merged PRs，按评论数排序
3. **Issue Discussions**（最丰富但噪音最大）：标记为 `discussion`、`feature`、`enhancement` 的 Issues

### 技术实现
```bash
# Stage 0 扩展：提取高价值 commit messages
git log --all --oneline --since="2 years ago" | grep -iE "refactor|redesign|change.*to|replace|migrate|add support" | head -20

# 提取 PR（如果是 GitHub 项目）
gh pr list --state merged --limit 20 --json title,body,comments
```

### 价值
- 直接获得"作者自己说的 WHY"，而非从代码推断
- 特别适合 funNLP 这类代码少但社区活跃的项目
- 补充当前纯代码分析的盲区

---

## 六、P2-A：自动化评分方案

### 三层评分架构

```
Layer 1: 确定性校验（脚本，0 成本）
├── 引用的文件路径是否存在
├── 引用的行号范围是否在文件行数内
├── evidence 数量是否 ≥ 2
└── 是否至少有 1 个 CODE 类型 evidence
→ 不通过则直接标记为"证据不可信"

Layer 2: 向量化常识检测（embedding，低成本）
├── 将 WHY claim 向量化
├── 与项目 README + 框架官方文档的向量对比
├── cosine similarity > 0.85 → 标记为"疑似常识"
└── 辅助人工复核

Layer 3: LLM 评分（API 调用，中等成本）
├── 提供 4 维度 rubric + few-shot 正反例
├── 强制输出评分理由
├── 可选：成对比较（ELO 排名）替代绝对分数
└── 质量门控：≤ 5 分的 WHY 自动丢弃
```

---

## 七、P2-B：对比式提取（Contrastive Extraction）— Opus 独创

### 核心思路
不直接问"为什么这样做"，而是：
1. 让 LLM 先生成"按行业标准做法，这个模块应该怎么实现"
2. 将预期实现 vs 实际代码做 diff
3. 差异点自然就是 WHY 的候选

### 示例
```
预期：量化交易系统通常用 Pandas 处理时间序列数据
实际：vnpy alpha 模块用 Polars
差异 → WHY：为什么选 Polars 不选 Pandas？→ Apache Arrow 列式存储在多股票截面计算中性能优势
```

### 价值
- 自动发现"偏离"——人可能因为熟悉而忽略的选择
- 特别适合发现 negation 类型的 WHY（"为什么没有用 X"）

---

## 八、Negative Sampling 验证 — Opus 独创

### 思路
生成故意错误的 WHY（hallucinated claims），混入真实 WHY 中，让另一个 LLM 鉴别。

### 具体做法
1. 从真实 WHYs 中随机选 3 条
2. 让 LLM 生成 3 条"看起来合理但实际错误"的 WHY（基于同一项目）
3. 6 条混合后让另一个 LLM 判断哪些是真的
4. 鉴别准确率 = WHY 质量的间接度量

### 价值
- 完全可自动化的质量评估方法
- 如果鉴别模型无法区分真假 WHY，说明真实 WHY 的信息增量太低

---

## 九、实施路线图

### Phase 1（本周）— 验证最高杠杆改进
- [ ] 实现 Stage 0 四层漏斗采样的 Layer 1-3（shell 脚本可完成）
- [ ] 用改进后的 Stage 0 重新提取 funNLP（验证 Stage 0 是否确实是瓶颈）
- [ ] 对比 funNLP 新旧 Stage 0 的 WHY 质量差异

### Phase 2（下周）— Agentic 提取 MVP
- [ ] 设计 Agent 提取的工具集（read_file, grep, list_dir, git_log）
- [ ] 实现单模型 Agent 提取循环
- [ ] 用 vnpy 做 A/B 测试：单次 prompt vs Agent 提取

### Phase 3（后续）— 系统化
- [ ] 多模型 GDS 融合 pipeline
- [ ] 自动化评分三层架构
- [ ] 社会性数据源集成

---

## 十、关键洞察总结

1. **Stage 0 是天花板** — 改 prompt 的收益已经趋于 0，改输入质量才是正道
2. **Agentic > Prompt** — 单次 prompt 的本质局限是"无法追问"，Agent 模式是质的飞跃
3. **多模型互补已验证** — 下一步是系统化融合（GDS 模式），而非继续各跑各的
4. **代码之外有金矿** — Git history、PR、Issue 包含作者亲口说的 WHY
5. **自动化评分必须分层** — 确定性校验（免费）→ 向量化（便宜）→ LLM 评分（贵），逐层过滤
6. **对比式提取是发现 negation WHY 的利器** — "这个项目应该怎么做但没这么做"

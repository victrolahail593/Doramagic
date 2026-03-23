# 竞品与最佳实践研究报告

研究日期: 2026-03-10 | 模型: bailian/glm-5

---

## 竞品分析

### 1. Repomix — 代码打包工具标杆

**定位**: 将整个代码仓库打包成单个 AI 友好的文件

**核心特性**:
- Tree-sitter 智能压缩（~70% token 减少）
- MCP Server 集成
- GitHub Actions 自动化
- 自定义指令输出
- Git 历史包含（commit 信息、日期、文件路径）

**设计思路**:
- **纯结构化输出**: 不尝试理解代码语义，只做格式转换
- **配置驱动**: `repomix.config.json` 控制包含/排除规则
- **多格式支持**: XML、Markdown、纯文本
- **在线+本地双模式**: CLI、Docker、Web 服务

**与 soul-extractor 的差异**:
| 维度 | Repomix | Soul Extractor |
|------|---------|----------------|
| 目标 | 代码→AI 输入 | 代码→专家知识 |
| 提取层次 | 文件结构、代码文本 | 设计哲学、心智模型 |
| 产出物 | 单一打包文件 | 多维度知识卡片 |
| Token 优化 | 压缩算法 | 知识提炼 |
| 适用场景 | 代码审查、文档生成 | 团队知识传承、AI 上下文注入 |

---

### 2. GPTMe — AI 知识注入框架

**定位**: 终端 AI Agent，具备上下文注入能力

**核心概念**:

| 概念 | 作用 |
|------|------|
| Knowledge Files | 静态上下文注入 |
| Lessons | 关键词触发动态注入 |
| Tools | 能力扩展 |
| Hooks | 生命周期钩子 |
| Plugins | 打包分发机制 |

**Lessons 机制（核心创新）**:
```
Lessons — contextual guidance that auto-injects into conversations 
based on keywords, tools, and patterns.
```
- 从用户/助手消息中提取关键词匹配相关 lessons
- 支持启用/禁用自动包含
- 跨对话上下文持久化

**最佳实践**:
- **分层上下文**: Agent identity → Tools → Workspace files
- **选择性注入**: `context_include` 配置细粒度控制
- **环境变量驱动**: `GPTME_LESSONS_REFRESH` 控制刷新策略

---

### 3. Cursor Rules Generator — 项目上下文注入

**定位**: 为 Cursor IDE 生成项目专属 AI 规则

**核心机制**:

| 类型 | 作用范围 | 应用时机 |
|------|----------|----------|
| Global Rules | 所有项目 | 始终应用 |
| Project Rules | 单个项目 | 匹配时应用 |
| .cursorrules (deprecated) | 单个项目 | 始终应用 |

**最佳实践**:
- **文件模式匹配**: `globs` 精确控制触发条件
- **@file 引用**: 将关键文件作为上下文自动包含
- **描述驱动**: `description` 字段用于 AI 选择性加载
- **拆分策略**: 避免单一文件臃肿，按功能域拆分 `.mdc` 文件

**社区资源**:
- `awesome-cursorrules`: 500+ stars，各语言/框架模板
- `cursorrules.org`: 在线生成器 + AST 分析器

---

### 4. Code2Prompt / Repo2Prompt / Codebase-Digest

**定位**: 代码到 Prompt 的转换工具

| 工具 | 特点 |
|------|------|
| Code2Prompt | 结构化 AI 提示生成 |
| Repo2Prompt | GitHub 仓库直接转换 |
| Codebase-Digest | 60+ 内置分析 Prompts + 指标生成 |

**设计模式**:
- **Prompt 模板库**: 预定义分析场景（代码审查、架构分析、安全审计）
- **多视角分析**: Architect / Developer / Security 视角切换
- **结构化输出**: Markdown/JSON 格式化

---

### 5. 知识图谱提取工具

**Graph4Code (IBM WALA)**:
- 从 1.3M Python 文件提取知识图谱
- 2B+ 三元组规模
- 整合文档、论坛帖子、代码分析

**Knowledge Graph Based Code Generation**:
- 代码→知识图谱→检索→生成的 Pipeline
- 混合检索系统提升代码生成质量

**核心方法论**:
```
Parsing → Element Extraction → Relation Extraction → Graph Construction
```

---

## 最佳实践

### 1. 上下文工程原则 (Anthropic)

**核心框架**:
1. **Clarity First**: 明确指令放在 Prompt 末尾
2. **Avoid Over-engineering**: 只做被要求的改动
3. **Few-shot Prompting**: 示例比规则更有效
4. **XML Structuring**: 结构化上下文提升理解
5. **Chain-of-Thought**: 复杂任务分步推理

**Claude Code Skills 最佳实践**:
```markdown
Skills are basically scoped prompt engineering + tool access control.

- Skills expose minimal metadata for retrieval
- Skills can be composable (call other skills/tools)
- Skills are lazy-loaded only when relevant
```

---

### 2. Google Prompt Engineering 白皮书要点

| 技术 | 应用场景 |
|------|----------|
| 正向指令 | 优于约束式限制 |
| Token 限制 | 智能设置输出长度 |
| 分类 Prompt | 打乱类顺序避免过拟合 |
| Few-shot | 3-5 示例最佳 |
| Context Anchoring | 大数据块后用过渡短语连接 |

---

### 3. 知识注入设计模式

**模式 1: 分层注入**
```
System Prompt → Agent Identity → Tools → Workspace → Lessons
```

**模式 2: 懒加载**
```
Name + Description (always loaded) → Body (loaded when invoked)
```

**模式 3: 关键词触发**
```
User Message → Keyword Extraction → Lesson Matching → Context Injection
```

**模式 4: 文件模式匹配**
```
File Path → Glob Match → Rule Selection → Context Assembly
```

---

### 4. 知识提炼方法论

**从代码到知识的层次**:

```
Level 1: 结构层 (Structure)
  - 文件组织、目录结构
  - 模块边界、依赖关系

Level 2: 行为层 (Behavior)
  - API 设计、数据流
  - 状态管理、错误处理

Level 3: 意图层 (Intent)
  - 设计决策、权衡取舍
  - 问题背景、解决方案

Level 4: 智慧层 (Wisdom)
  - 设计哲学、心智模型
  - 踩坑经验、最佳实践
```

---

## 差距分析

### Soul Extractor 的优势

| 方面 | 优势 |
|------|------|
| 提取深度 | 唯一聚焦"灵魂层"的工具 |
| 叙事质量 | 专家级知识传递，非规则列表 |
| 结构化产出 | 多维度卡片（概念卡、规则卡、工作流卡） |
| 多平台输出 | .cursorrules + CLAUDE.md + 项目灵魂 |

### Soul Extractor 的差距

| 方面 | 差距 | 竞品参考 |
|------|------|----------|
| **配置灵活性** | 无配置文件控制提取策略 | Repomix config.json |
| **压缩效率** | 无 Token 优化机制 | Repomix Tree-sitter 压缩 |
| **动态注入** | 无关键词触发机制 | GPTMe Lessons |
| **文件模式匹配** | 无细粒度上下文控制 | Cursor Rules globs |
| **模板库** | 无预定义提取模板 | Codebase-Digest 60+ prompts |
| **知识图谱** | 无结构化关系提取 | Graph4Code |
| **增量更新** | 无差异提取能力 | - |
| **多语言支持** | 主要针对单一技术栈 | - |
| **输出格式** | 固定 Markdown | Repomix 多格式 |

---

## 改进建议

### P0 — 核心能力增强

1. **配置化提取策略**
   - 新增 `soul-extractor.config.yaml`
   - 支持自定义 Stage、问题模板、输出格式
   - 参考 Repomix 的配置驱动模式

2. **Token 预算控制**
   - Stage 执行前估算 Token 消耗
   - 支持 `--max-tokens` 参数限制输出大小
   - 关键信息优先提取

3. **增量提取模式**
   - Git diff 感知，只分析变更文件
   - 知识卡片版本管理
   - 支持 `--since` 时间范围

### P1 — 上下文注入能力

4. **关键词触发机制**（参考 GPTMe Lessons）
   - 在 `.cursorrules` 中嵌入触发条件
   - 支持工具、文件类型、代码模式匹配
   - 懒加载策略

5. **文件模式匹配**（参考 Cursor Rules）
   - 每个 Soul 卡片关联 `globs` 规则
   - 细粒度上下文组装
   - 支持排除规则

6. **多平台适配增强**
   - 支持 Windsurf / Cline / GitHub Copilot
   - 输出格式适配层
   - 平台特性检测

### P2 — 知识工程能力

7. **结构化知识图谱输出**
   - 可选输出 Neo4j 兼容格式
   - 实体-关系三元组
   - 支持 GraphRAG 集成

8. **提取模板库**
   - 预定义场景模板：
     - Library/API 仓库
     - CLI 工具
     - Web 应用
     - 框架/SDK
   - 社区贡献机制

9. **质量评估框架**
   - 提取结果置信度评分
   - 跨仓库一致性检查
   - 人工反馈循环

---

## 优先级排序

```
P0 (立即需要):
├── 配置化提取策略
├── Token 预算控制
└── 增量提取模式

P1 (短期目标):
├── 关键词触发机制
├── 文件模式匹配
└── 多平台适配增强

P2 (长期规划):
├── 结构化知识图谱输出
├── 提取模板库
└── 质量评估框架
```

---

## 附录：竞品资源链接

| 工具 | 链接 |
|------|------|
| Repomix | https://github.com/yamadashy/repomix |
| GPTMe | https://github.com/gptme/gptme |
| awesome-cursorrules | https://github.com/PatrickJS/awesome-cursorrules |
| Code2Prompt | https://code2prompt.dev/ |
| Codebase-Digest | https://github.com/kamilstanich/codebase-digest |
| Graph4Code | https://github.com/wala/graph4code |
| Anthropic Prompt Tutorial | https://github.com/anthropics/prompt-eng-interactive-tutorial |
| Google Prompt Whitepaper | https://cloud.google.com/discover/what-is-prompt-engineering |

---

*研究完成于 2026-03-10*

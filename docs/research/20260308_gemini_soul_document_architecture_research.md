# AI 编程工具上下文管理与知识文档体系——最佳实践调研报告

**调研时间**: 2026年3月8日  
**调研模式**: Deep Research (2026版)  
**调研对象**: Claude Code, Cursor, GitHub Copilot, Windsurf, AGENTS.md  

---

## 第1章：Claude Code 的 CLAUDE.md 体系

### 1.1 完整规范与格式 (信心度：高)
CLAUDE.md 是 Claude Code 的核心项目指令文件，旨在为 AI 提供“项目说明书”。
*   **格式**: 标准 Markdown，但强调**结构化**。通常包含：`Project Overview`, `Tech Stack`, `Coding Guidelines`, `Common Commands` (Build, Test, Lint), `Architecture Map`。
*   **继承规则与作用域**:
    1.  **Managed (最高)**: `/Library/Application Support/ClaudeCode/CLAUDE.md` (IT/DevOps 强管控，不可覆盖)。
    2.  **Local Override**: `CLAUDE.local.md` (开发者个人对当前项目的私有调整，不进 Git)。
    3.  **Project**: `./CLAUDE.md` 或 `./.claude/CLAUDE.md` (团队共享的项目基准规则)。
    4.  **User (最低)**: `~/.claude/CLAUDE.md` (全局个人偏好，如“始终使用中文回复”)。
*   **协作机制**: Claude 会在启动时自动合并这些文件。如果根目录和子目录同时存在 CLAUDE.md，通常以**最靠近当前操作路径**的文件为准。

### 1.2 加载与优先级
Claude 会将这些文件内容注入到 System Prompt 或 Conversation Context 的起始位置。
*   **优先级排序**: `Managed > Local > Project > User`。

### 1.3 局限性
*   **静态性**: 它是一次性加载的，不支持基于文件类型的动态过滤。
*   **Context 冗余**: 如果 CLAUDE.md 过长（建议不超过 200 行），会严重挤占 AI 的推理空间，导致“Lost in the middle”现象。

---

## 第2章：Cursor Rules 体系

### 2.1 .cursorrules 与 .mdc (信心度：高)
Cursor 已经从单一的 `.cursorrules` 文件进化到了更加强大的 **.mdc (Markdown Config)** 体系。
*   **格式**: Markdown + YAML Frontmatter。
*   **核心特性**: 
    *   **Auto-trigger**: 在 Frontmatter 中定义 `globs`，例如 `globs: "src/**/*.ts"`。只有当 AI 处理匹配的文件时，该规则才会被载入上下文。
    *   **Action Modes**: 支持 `Always`, `Auto`, `Manual` 三种触发模式。
*   **差异化**: 相比 CLAUDE.md 的“全量加载”，Cursor Rules 实现了**“按需加载”**，极大地优化了 Context Window 的利用率。

### 2.2 社区最佳实践
*   **原子化规则**: 每一个功能模块（如 `auth`, `ui-components`, `testing`）编写独立的 `.mdc` 文件。
*   **规则互联**: 通过 Frontmatter 的 `related_rules` 实现规则间的跳转和联想。

---

## 第3章：其他 AI 工具的上下文管理

### 3.1 GitHub Copilot (信心度：中高)
*   **方案**: 使用 `.github/copilot-instructions.md`。
*   **特点**: 深度集成 GitHub 生态，能够引用特定的 Issue 或 PR 作为上下文。最新版本支持通过 `applyTo` 属性实现路径级别的指令覆盖。

### 3.2 Windsurf / Cline / Aider
*   **Windsurf**: 使用 `.windsurf/rules/` 目录下的规则，强调对 "Cascade" 代理的动作约束。
*   **Cline (原 Claude Dev)**: 支持自定义 `.clinerules`，通常用于定义复杂的任务流（Plan-Act-Validate）。
*   **Aider**: 提倡 `CONVENTIONS.md`，专注于代码风格和 Git 提交规范。

### 3.3 AGENTS.md 规范 (信心度：高)
这是由 Agentic AI Foundation 推动的开源标准。
*   **目标**: 解决“一家工具一套规则”的混乱。
*   **现状**: 目前 Claude Code, Cursor, Gemini CLI 均已支持读取 `AGENTS.md`。它被视为“给机器人看的 README”。

---

## 第4章：双层知识架构的设计模式

### 4.1 继承与覆盖模式 (Inheritance)
*   **全局 (Global)**: 处理“通用价值观”。例如：代码注释风格、安全性检查基线、交互语气。
*   **项目 (Project)**: 处理“特定业务逻辑”。例如：本项目使用的特殊框架补丁、特定数据库 Schema、历史遗留问题的处理方式。

### 4.2 热记忆 (Always loaded) vs 冷记忆 (On-demand)
*   **热记忆 (Hot)**: 核心 SOP、当前任务指令。必须始终存在于 Context 中。
*   **冷记忆 (Cold)**: 历史踩坑记录、非核心模块文档。通过 **RAG (检索增强生成)** 或 **路径匹配 (MDC 模式)** 动态拉取。

### 4.3 知识版本控制
*   **版本锚点**: 在灵魂文档中记录关键的版本快照 ID。
*   **增量更新**: AI 在对话过程中发现的新“灵魂知识”（如解决了一个奇葩 Bug）应被标记并提示用户更新到 `AGENTS.md` 中。

---

## 第5章：对 AllInOne 双层灵魂文档的设计建议

### 5.1 全局灵魂 (Global Soul) 建议
*   **内容**: 
    1.  **AI 交互协议**: 响应语言、解释深度、对命令运行的确认逻辑。
    2.  **通用安全策略**: 不泄露 API Key、不删除系统关键目录。
    3.  **常用工具链定义**: 全局可用的 CLI 工具及其简写。
*   **存储**: 用户 Home 目录下的隐藏文件夹，如 `~/.allinone/soul.global.md`。

### 5.2 项目灵魂 (Project Soul) 建议
*   **内容**:
    1.  **灵魂画像**: 项目的愿景、核心逻辑流程、主要模块分布。
    2.  **踩坑记录 (The Pitfalls)**: 最具价值的部分。记录“为什么不这么写”、“那个奇葩 Bug 的修复逻辑”。
    3.  **社区经验**: 从 GitHub Issues 提取的、代码之外的共识。
*   **存储**: 仓库根目录，建议文件名为 `SOUL.md` 或遵循标准采用 `AGENTS.md`。

### 5.3 协作与格式推荐
*   **推荐格式**: **Markdown + YAML Frontmatter**。
    ```markdown
    ---
    allinone_role: project_soul
    scope: "src/backend"
    knowledge_type: "community_experience"
    last_sync: "2026-03-08"
    ---
    # 项目灵魂：后端核心逻辑
    ...
    ```
*   **协作逻辑**: 
    - AI 在启动任务前，先扫描 `SOUL.md`。
    - 如果当前任务涉及特定路径，动态加载匹配的冷记忆片段。
    - 任务结束后，AI 自动总结本次任务产生的“新灵魂碎片”，询问用户是否持久化。

**结论**: 灵魂文档不应只是“死文档”，而应是 AI 可以通过**动态触发**、**分层覆盖**、**持续进化**的“运行态内存”。建议 AllInOne 深度兼容 `AGENTS.md` 标准，并在此基础上增加“社区灵魂提取”这一差异化特色。
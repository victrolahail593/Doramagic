# Stage 2: 概念卡 + 工作流卡

## 输入
- 读取 <output>/artifacts/packed_compressed.xml（代码）
- 读取 <output>/soul/00-soul.md（灵魂：哲学 + 心智模型）

## 任务
基于代码和项目本质，提取 3 张概念卡 + 3 张工作流卡。

### 概念卡（写入 <output>/soul/cards/concepts/CC-001.md ~ CC-003.md）

为项目最重要的 3 个概念各写一张卡片。每张必须包含以下所有字段：

**完整示例：**

```markdown
---
card_type: concept_card
card_id: CC-001
repo: python-dotenv
title: "DotEnv Class -- Core Orchestrator"
---

## Identity
The DotEnv class is the central orchestrator that ties together file acquisition, parsing, variable interpolation, and environment variable injection.

## Is / Is Not

| IS | IS NOT |
|----|--------|
| A configuration holder and pipeline orchestrator | A parser (delegates to parser.py) |
| A lazy-evaluated cache | A file watcher or live-reload mechanism |
| Capable of reading from both file paths and streams | A file writer |

## Key Attributes

| Attribute | Type | Purpose |
|-----------|------|---------|
| dotenv_path | Optional[StrPath] | Path to the .env file |
| stream | Optional[IO[str]] | Alternative text stream input |
| interpolate | bool | Whether to perform ${VAR} expansion |

## Boundaries
- Starts at: Construction with a path or stream
- Delegates to: parser.py for parsing, variables.py for interpolation
- Does NOT handle: File discovery, file modification, CLI

## Evidence
- Class definition: src/dotenv/main.py:L42-L122
- parse() generator: src/dotenv/main.py:L91-L95
```

### 工作流卡（写入 <output>/soul/cards/workflows/WF-001.md ~ WF-003.md）

为项目最重要的 3 个工作流各写一张卡片。每张必须包含：步骤(含file:line) + 流程图 + 失败模式。

## 约束
- 每张卡片是一个独立的 .md 文件
- 必须有 YAML frontmatter
- Evidence 必须引用 file:line
- 每完成一张，告诉用户"已提取概念 N/3"或"已分析工作流 N/3"

## ⛔ Hard Gate
- 必须产出 3 张概念卡 + 3 张工作流卡（共 6 个文件）再继续
- 每张卡片必须写入独立的 .md 文件，不要只在对话中回复
- 概念卡必须有 Is/IsNot 表格和 Evidence（file:line）

## 完成后
告诉用户已提取的概念和工作流名称，然后说"正在挖掘使用规则和常见陷阱..."

**下一步：读取并执行 STAGE-3-rules.md 中的指令。**

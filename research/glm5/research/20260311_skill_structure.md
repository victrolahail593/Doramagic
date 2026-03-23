# OpenClaw Skill 结构模式研究报告

> 研究日期：2026-03-11
> 研究目的：为 Doramagic "玩乐高" 拼 Skill 的体验设计提供参考

---

## 一、Sample 分析

本次研究分析了 10 个不同类型的 OpenClaw Skill：

| Skill | 类型 | 依赖方式 | 核心能力 |
|-------|------|----------|----------|
| Trello | REST API | env (API Key + Token) | board/list/card CRUD |
| CalDAV Calendar | 本地 CLI | bins (vdirsyncer, khal) | sync, list, search, new, edit |
| Answer Overflow | 搜索 + Web Fetch | 无认证 | search, fetch thread |
| Himalaya | 邮件 CLI | bins (himalaya) | list, read, write, reply, forward, search |
| nano-pdf | Python CLI | bins (nano-pdf) | PDF 编辑 |
| blogwatcher | Go CLI | bins (blogwatcher) | 博客/RSS 监控 |
| Brave Search | Node.js + API | env (BRAVE_API_KEY) | search, content extraction |
| Peekaboo | macOS UI 自动化 | bins + os (darwin) | 截图、点击、输入、窗口管理 |
| Apple Notes | macOS 原生 | bins + os (darwin) | note CRUD |
| Weather | HTTP API | bins (curl) | 天气查询 |

---

## 二、共同结构分析

### 2.1 文件结构

```
skill-name/
├── SKILL.md              # 主文件 - Skill 定义
├── _meta.json            # 元数据 (ownerId, slug, version)
├── references/          # 参考文档 (可选)
│   ├── configuration.md
│   └── ...
└── .clawhub/            # ClawHub 相关
```

### 2.2 SKILL.md 结构

每个 SKILL.md 遵循统一的三段式结构：

#### (1) Frontmatter (YAML 头)

```yaml
---
name: skill-name
description: "简短描述 - 告诉 AI 什么时候使用这个 Skill"
homepage: https://official-link
metadata:
  emoji: "📧"
  requires:
    bins: ["himalaya"]           # 需要的二进制工具
    env: ["TRELLO_API_KEY"]      # 需要的环境变量
    os: ["darwin"]               # 操作系统限制 (可选)
  install:                       # 安装说明
    - id: "brew"
      kind: "brew"
      formula: "himalaya"
      bins: ["himalaya"]
      label: "Install Himalaya (brew)"
---
```

#### (2) 主内容区

结构化内容通常包含：

```
# Skill 名称

一句话描述...

## References (可选)
- 参考文档链接...

## Prerequisites / Setup
前置条件说明...

## Common Operations / Commands
### 操作1
命令语法...

### 操作2
命令语法...

## Examples
```bash
# 示例代码
```

## Notes / Limitations
- 注意事项...
- 限制说明...
```

#### (3) 命名规范

- **文件头**: `name` 使用 kebab-case (e.g., `apple-notes`)
- **标题**: 使用标题大小写 (e.g., `# Apple Notes CLI`)
- **命令**: 使用 code block

---

## 三、Skill 组成部分详解

### 3.1 必要组成部分

| 部分 | 必填 | 说明 |
|------|------|------|
| `name` | ✅ | Skill 标识符 |
| `description` | ✅ | 使用场景描述 |
| `metadata` | ✅ | 依赖和安装信息 |
| 主内容 | ✅ | 命令和操作说明 |

### 3.2 Metadata 结构

```yaml
metadata:
  # UI 显示
  emoji: "📧"                    # 图标
  
  # 依赖声明
  requires:
    bins: ["himalaya", "jq"]    # 需要安装的 CLI 工具
    env: ["API_KEY", "TOKEN"]   # 需要的环境变量
    os: ["darwin", "linux"]     # 操作系统限制
  
  # 安装指引
  install:
    - id: "unique-id"           # 安装方式标识
      kind: "brew|go|uv|pip|npm" # 包管理器类型
      formula: "package-name"   # 包名
      module: "npm/go module"   # 模块名 (可选)
      bins: ["executable"]      # 安装的二进制
      label: "显示名称"          # UI 显示
```

### 3.3 能力定义方式

**核心发现**: Skill 的"能力"通过 **"动词 + 名词"** 模式定义，每个能力对应一个或多个 CLI 命令。

```
List emails    → himalaya envelope list
Create card    → curl -X POST .../cards
Search blogs   → blogwatcher scan
Edit PDF        → nano-pdf edit <file> <page> "<instruction>"
```

**能力的粒度**:
- 细粒度: 每个 CLI 子命令为一个能力 (Peekaboo 有 30+ 命令)
- 粗粒度: 每个功能域为一个能力 (Weather 只有一个能力域)

---

## 四、依赖管理机制

### 4.1 依赖类型

```
┌─────────────────────────────────────────────────┐
│                  Skill 依赖                      │
├─────────────┬─────────────┬─────────────────────┤
│   bins      │    env      │        os           │
├─────────────┼─────────────┼─────────────────────┤
│ 本地 CLI 工具│ API 密钥    │ darwin / linux /   │
│ (必须安装)   │ (运行时设置) │ win32 / all        │
└─────────────┴─────────────┴─────────────────────┘
```

### 4.2 安装方式

| kind | 包管理器 | 示例 |
|------|----------|------|
| `brew` | Homebrew | `brew install himalaya` |
| `go` | Go | `go install ...@latest` |
| `uv` | uv | `uv pip install nano-pdf` |
| `npm` | npm | `npm ci` |
| `pip` | pip | `pip install ...` |

### 4.3 配置管理

- **无配置**: Weather, Answer Overflow (直接可用)
- **环境变量**: Trello, Brave Search (需设置 env)
- **配置文件**: Himalaya (`~/.config/himalaya/config.toml`)
- **系统权限**: Peekaboo, Apple Notes (需要 macOS 权限)

---

## 五、Skill 类型分类

### 5.1 按实现方式

```
Skill 类型
│
├── 🔌 API 型
│   ├── REST API (Trello)
│   └── HTTP API (Weather, Brave Search)
│
├── 🖥️ CLI 型
│   ├── 本地工具 (CalDAV: vdirsyncer, khal)
│   ├── 独立 CLI (Himalaya, blogwatcher)
│   └── 脚本集合 (Brave Search: Node.js)
│
├── 🍎 原生集成型
│   ├── macOS API (Apple Notes, Peekaboo)
│   └── 系统能力 (文件、剪贴板等)
│
└── 🔍 信息获取型
    ├── 搜索 (Web Search)
    └── 抓取 (Web Fetch)
```

### 5.2 按认证需求

| 类型 | 示例 | 认证方式 |
|------|------|----------|
| 无认证 | Weather, Answer Overflow | - |
| API Key | Brave Search | env |
| Token | Trello | env |
| 账户配置 | Himalaya | 配置文件 |
| 系统权限 | Peekaboo | macOS 授权 |

---

## 六、对 Doramagic "积木块" 设计的建议

### 6.1 积木块类型映射

```
OpenClaw Skill    →    Doramagic 积木块
─────────────────────────────────────────
name              →    积木名称
description       →    积木描述 (触发条件)
metadata.emoji    →    积木图标
metadata.requires →    积木依赖 (input)
commands          →    积木能力 (actions)
```

### 6.2 积木设计维度

| 维度 | 说明 | 示例 |
|------|------|------|
| **触发条件** | 什么时候使用这个积木 | "查天气", "管理 Trello" |
| **输入** | 需要什么参数/依赖 | API Key, 文件路径, 查询词 |
| **输出** | 返回什么结果 | 卡片列表, 天气数据 |
| **能力** | 能做什么操作 | list, create, edit, delete |
| **配置** | 如何初始化 | env 设置, 配置文件 |

### 6.3 积木块组合建议

基于研究，建议 Doramagic 设计以下几类积木：

#### (1) 触发积木 (Trigger)
```
当用户说 "查天气" → 触发 Weather Skill
当用户说 "创建 Trello 卡片" → 触发 Trello Skill
```

#### (2) 能力积木 (Action)
```
获取天气 → 需要 location 参数
创建卡片 → 需要 boardId, listId, name 参数
```

#### (3) 依赖积木 (Dependency)
```
API Key 积木 → 提供认证信息
配置积木 → 提供配置文件
```

#### (4) 转换积木 (Transformer)
```
JSON 解析 → 提取 API 响应中的数据
格式化 → 将数据转为人类可读格式
```

### 6.4 可视化设计建议

```
┌─────────────────────────────────────────────┐
│           🌤️  Weather Skill                │
├─────────────────────────────────────────────┤
│  触发: "天气" / "温度" / "下雨"              │
├─────────────────────────────────────────────┤
│  依赖: ○ curl                                │
├─────────────────────────────────────────────┤
│  能力:                                       │
│  ┌─────────────────────────────────────┐    │
│  │ get_weather(location)               │    │
│  │ get_forecast(days, location)        │    │
│  └─────────────────────────────────────┘    │
├─────────────────────────────────────────────┤
│  输出: 天气描述, 温度, 湿度, 降雨概率          │
└─────────────────────────────────────────────┘
```

---

## 七、总结

### 7.1 核心发现

1. **标准化结构**: 所有 Skill 遵循 `SKILL.md + _meta.json` 格式
2. **声明式定义**: 能力通过命令描述声明，不绑定具体实现
3. **依赖清晰**: 明确声明 bins/env/os 依赖，安装指南内置
4. **粒度灵活**: 从单命令到 30+ 命令均可为一个 Skill
5. **自包含**: 参考文档可内嵌，配置通过 metadata 声明

### 7.2 Doramagic 设计原则建议

| 原则 | 说明 |
|------|------|
| **声明式** | 积木声明"能做什么"，不关心"怎么做" |
| **可组合** | 积木之间通过输入/输出连接 |
| **可发现** | description 包含触发关键词 |
| **可配置** | 依赖通过 UI 提示配置 |
| **可测试** | 每个积木有明确的输入/输出契约 |

---

## 八、附录：字段速查

```yaml
# SKILL.md Frontmatter 全字段
---
name: string              # 必填，kebab-case
description: string       # 必填，使用场景
homepage: string          # 可选，官方链接
metadata:
  emoji: string          # 可选，图标
  requires:
    bins: [string]       # 依赖的 CLI 工具
    env: [string]       # 依赖的环境变量
    os: [string]        # 操作系统限制
  install:              # 安装指南
    - id: string
      kind: string      # brew|go|uv|pip|npm
      formula: string   # 包名
      module: string   # npm/go module
      bins: [string]   # 可执行文件名
      label: string    # 显示名称
---
```

---

*报告生成时间: 2026-03-11*

# OpenClaw API 技术实现参考文档

> 本文档为 Doramagic 项目提供 OpenClaw API 能力参考
> 生成日期：2026-03-11

---

## 目录

1. [子代理调用 (Subagents)](#1-子代理调用-subagents)
2. [文件操作](#2-文件操作)
3. [工具列表](#3-工具列表)
4. [消息发送](#4-消息发送)
5. [Skills 调用](#5-skills-调用)
6. [上下文获取](#6-上下文获取)

---

## 1. 子代理调用 (Subagents)

### 1.1 如何 Spawn 子代理

使用 `sessions_spawn` 工具启动子代理：

```javascript
{
  "tool": "sessions_spawn",
  "params": {
    "task": "任务描述",           // 必需，子代理执行的任务
    "label": "可选标签",          // 可选，用于标识
    "agentId": "agent-id",       // 可选，指定代理 ID
    "model": "provider/model",   // 可选，覆盖默认模型
    "thinking": "high|low|off",  // 可选，覆盖思考级别
    "runTimeoutSeconds": 900,    // 可选，超时秒数
    "thread": false,             // 可选，是否绑定线程
    "mode": "run",               // 可选，"run" 或 "session"
    "cleanup": "keep",           // 可选，"delete" 或 "keep"
    "sandbox": "inherit"         // 可选，"inherit" 或 "require"
  }
}
```

### 1.2 子代理返回结果

子代理完成后会自动 **announce** 结果到请求者的聊天频道：

- 结果包含：`Result`（助手回复文本）、`Status`（完成状态）、运行时统计
- 结果推送是最佳 effort，如果直接投递失败会回退到队列路由
- 可以使用 `sessions_history` 工具获取完整历史

### 1.3 嵌套子代理

支持两层嵌套（需要配置 `maxSpawnDepth: 2`）：

```json5
{
  agents: {
    defaults: {
      subagents: {
        maxSpawnDepth: 2,
        maxChildrenPerAgent: 5,
        maxConcurrent: 8,
        runTimeoutSeconds: 900
      }
    }
  }
}
```

### 1.4 线程绑定模式

在支持的渠道（目前主要是 Discord），子代理可以绑定到线程：

```javascript
{
  "tool": "sessions_spawn",
  "params": {
    "task": "任务",
    "thread": true,
    "mode": "session"  // 持久化会话
  }
}
```

---

## 2. 文件操作

### 2.1 读取文件

```javascript
{
  "tool": "read",
  "params": {
    "file_path": "/path/to/file",  // 支持相对或绝对路径
    "limit": 100,                   // 可选，最大行数
    "offset": 1                     // 可选，起始行号（1-indexed）
  }
}
```

### 2.2 写入文件

```javascript
{
  "tool": "write",
  "params": {
    "content": "文件内容",
    "file_path": "/path/to/file"    // 相对或绝对路径
  }
}
```

### 2.3 编辑文件

```javascript
{
  "tool": "edit",
  "params": {
    "path": "/path/to/file",
    "old_string": "要替换的文本",   // 必须精确匹配
    "new_string": "替换后的文本"
  }
}
```

### 2.4 路径规范

- **Workspace 目录**: `~/.openclaw/workspace/`
- 相对路径相对于 workspace 解析
- 绝对路径从系统根目录开始
- 工具策略可使用 `group:fs` 快捷方式

---

## 3. 工具列表

### 3.1 核心内置工具

| 工具名称 | 功能描述 |
|---------|---------|
| `read` | 读取文件内容 |
| `write` | 写入/创建文件 |
| `edit` | 编辑文件（精确替换） |
| `apply_patch` | 应用结构化补丁 |
| `exec` | 执行 Shell 命令 |
| `process` | 管理后台进程 |
| `sessions_list` | 列出会话 |
| `sessions_history` | 获取会话历史 |
| `sessions_send` | 发送消息到会话 |
| `sessions_spawn` | 启动子代理 |
| `session_status` | 获取会话状态 |
| `message` | 跨渠道发送消息 |
| `browser` | 控制浏览器 |
| `canvas` | 控制节点 Canvas |
| `nodes` | 节点管理 |
| `web_search` | Web 搜索 |
| `web_fetch` | 获取网页内容 |
| `image` | 分析图片 |
| `pdf` | 分析 PDF |
| `cron` | 定时任务管理 |
| `gateway` | 网关控制 |

### 3.2 Browser 工具

用于控制 OpenClaw 管理的独立浏览器：

```javascript
{
  "tool": "browser",
  "params": {
    "action": "status|start|stop|tabs|open|close|snapshot|screenshot|act",
    "profile": "openclaw",           // 浏览器配置
    "url": "https://example.com",    // 用于 open/navigate
    "target": "sandbox|host|node"    // 执行目标
  }
}
```

常用操作：

- `browser status` - 查看状态
- `browser start` - 启动浏览器
- `browser open <url>` - 打开页面
- `browser snapshot` - 获取页面快照
- `browser act` - 执行操作（click/type/hover 等）

### 3.3 Web Search 工具

支持多个搜索提供商：

```javascript
{
  "tool": "web_search",
  "params": {
    "query": "搜索关键词",
    "count": 5,                        // 结果数量 1-10
    "freshness": "day|week|month|year" // 时间过滤
  }
}
```

**支持的提供商**：
- Brave Search（默认）
- Gemini（Google Search 基础）
- Grok（xAI）
- Kimi（Moonshot）
- Perplexity

配置 API key：`openclaw configure --section web`

### 3.4 Web Fetch 工具

获取网页可读内容：

```javascript
{
  "tool": "web_fetch",
  "params": {
    "url": "https://example.com",
    "extractMode": "markdown|text",
    "maxChars": 50000                  // 最大字符数
  }
}
```

### 3.5 Canvas 工具

控制 macOS 节点的 Canvas：

```javascript
{
  "tool": "canvas",
  "params": {
    "action": "present|hide|navigate|eval|snapshot",
    "node": "node-id",                 // 可选，指定节点
    "javaScript": "code"               // 用于 eval
  }
}
```

### 3.6 Nodes 工具

管理配对的设备节点：

```javascript
{
  "tool": "nodes",
  "params": {
    "action": "status|describe|camera_snap|screen_record|location_get|run",
    "node": "node-name",
    "command": ["echo", "hello"]       // 用于 run
  }
}
```

### 3.7 Image 工具

分析图片：

```javascript
{
  "tool": "image",
  "params": {
    "image": "/path/to/image.jpg",
    "prompt": "描述图片内容"
  }
}
```

### 3.8 PDF 工具

分析 PDF 文档：

```javascript
{
  "tool": "pdf",
  "params": {
    "pdf": "/path/to/file.pdf",
    "prompt": "分析这个 PDF",
    "pages": "1-5"                      // 可选页码范围
  }
}
```

### 3.9 Cron 工具

管理定时任务：

```javascript
{
  "tool": "cron",
  "params": {
    "action": "list|add|update|remove|run",
    "job": { /* cron job 配置 */ }
  }
}
```

---

## 4. 消息发送

### 4.1 发送消息到渠道

使用 `message` 工具：

```javascript
{
  "tool": "message",
  "params": {
    "action": "send",
    "channel": "telegram|discord|slack|whatsapp...",  // 渠道类型
    "target": "+1234567890",                            // 目标（ID 或名称）
    "message": "消息内容",
    "media": "/path/to/media.jpg",                     // 可选附件
    "threadId": "thread-123",                          // 可选线程
    "replyTo": "message-id"                            // 可选回复
  }
}
```

### 4.2 支持的渠道

- Telegram
- Discord
- Slack
- WhatsApp
- Signal
- iMessage / BlueBubbles
- Microsoft Teams
- Google Chat
- IRC
- Matrix
- Feishu
- LINE
- Mattermost
- Nextcloud Talk
- Nostr
- Synology Chat
- Twitch
- Zalo

### 4.3 其他消息操作

```javascript
{
  "tool": "message",
  "params": {
    "action": "react|edit|delete|poll|send",
    "messageId": "消息ID",
    "emoji": "👍"
  }
}
```

---

## 5. Skills 调用

### 5.1 SKILL.md 结构

每个 Skill 目录包含 `SKILL.md` 文件，格式如下：

```markdown
---
name: skill-name
description: "技能描述"
metadata:
  {
    "openclaw": {
      "requires": {
        "bins": ["command"],
        "env": ["ENV_VAR"],
        "config": ["some.config.path"]
      },
      "primaryEnv": "API_KEY"
    }
  }
---

# Skill 文档

使用说明...
```

### 5.2 必需字段

- `name`: 技能名称
- `description`: 技能描述

### 5.3 可选字段

| 字段 | 描述 |
|-----|------|
| `homepage` | 技能官网 URL |
| `user-invocable` | 是否可用户调用 |
| `disable-model-invocation` | 是否排除模型调用 |
| `command-dispatch` | 命令分发模式 |
| `command-tool` | 分发的工具名 |

### 5.4 条件过滤 (Gating)

使用 `metadata` 进行加载时过滤：

```markdown
---
name: example
description: "示例技能"
metadata:
  {
    "openclaw": {
      "requires": {
        "bins": ["curl"],
        "env": ["API_KEY"],
        "config": ["feature.enabled"]
      },
      "os": ["darwin", "linux"]
    }
  }
---
```

### 5.5 Skills 位置与优先级

1. **Bundled skills**: npm 包内置
2. **Managed skills**: `~/.openclaw/skills`
3. **Workspace skills**: `<workspace>/skills`

优先级：`workspace` > `managed` > `bundled`

### 5.6 安装 Skills

```bash
# 使用 ClawHub 安装
clawhub install <skill-slug>

# 更新所有 skills
clawhub update --all
```

---

## 6. 上下文获取

### 6.1 获取可用模型

使用 `/model list` 命令或查看配置：

```bash
openclaw model list
```

模型选择顺序：
1. Primary 模型 (`agents.defaults.model.primary`)
2. Fallbacks (`agents.defaults.model.fallbacks`)
3. Provider auth failover

### 6.2 会话管理

```javascript
// 列出所有会话
{
  "tool": "sessions_list",
  "params": {
    "activeMinutes": 60,
    "kinds": ["main", "subagent"],
    "limit": 10
  }
}

// 获取会话历史
{
  "tool": "sessions_history",
  "params": {
    "sessionKey": "agent:main:subagent:xxx",
    "limit": 20,
    "includeTools": false
  }
}

// 发送消息到会话
{
  "tool": "sessions_send",
  "params": {
    "sessionKey": "agent:main:subagent:xxx",
    "message": "消息内容",
    "timeoutSeconds": 30
  }
}

// 获取当前会话状态
{
  "tool": "session_status",
  "params": {
    "model": "default"
  }
}
```

### 6.3 工具策略配置

在 `openclaw.json` 中配置工具权限：

```json5
{
  tools: {
    profile: "coding",  // minimal | coding | messaging | full
    allow: ["group:fs", "browser"],
    deny: ["exec"],
    byProvider: {
      "openai/gpt-5.2": { allow: ["group:fs"] }
    }
  }
}
```

工具组快捷方式：
- `group:runtime`: exec, bash, process
- `group:fs`: read, write, edit, apply_patch
- `group:sessions`: sessions_list, sessions_history, sessions_send, sessions_spawn, session_status
- `group:memory`: memory_search, memory_get
- `group:web`: web_search, web_fetch
- `group:ui`: browser, canvas
- `group:messaging`: message
- `group:nodes`: nodes

---

## 附录

### A. 相关文档链接

- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [Tools 文档](https://docs.openclaw.ai/tools)
- [Subagents 文档](https://docs.openclaw.ai/tools/subagents)
- [Skills 文档](https://docs.openclaw.ai/tools/skills)
- [Browser 文档](https://docs.openclaw.ai/tools/browser)
- [Web Tools 文档](https://docs.openclaw.ai/tools/web)

### B. 配置文件位置

- 主配置：`~/.openclaw/openclaw.json`
- 环境变量：`~/.openclaw/.env`
- Workspace：`~/.openclaw/workspace/`

### C. 常用 CLI 命令

```bash
# 启动向导
openclaw onboard

# 发送消息
openclaw message send --to +1234567890 --message "Hello"

# 与代理对话
openclaw agent --message "Your message"

# 查看会话
openclaw sessions list

# 配置
openclaw configure --section web
```

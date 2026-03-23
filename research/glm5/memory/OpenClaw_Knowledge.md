# OpenClaw 知识库

> 最后更新: 2026-03-09 | 来源: GitHub + Web Search

---

## 什么是 OpenClaw

**OpenClaw** 是一个开源的个人 AI 助手框架（formerly Moltbot / Clawdbot）。核心理念：**Any OS. Any Platform. The lobster way. 🦞**

定位：**AI Agent 的操作系统** — 把 AI 当作基础设施问题来解决：sessions、memory、tool sandboxing、access control、orchestration。

---

## 核心架构

### Gateway（核心）
- 单一控制平面，管理 sessions、channels、tools、events
- 所有 LLM 调用和 tool 调用都经过 Gateway
- 停止 Gateway = 停止所有 agent、session、scheduled tasks

### Workspace（工作空间）
- 本地优先：对话、长期记忆、skills 存储为 Markdown/YAML
- 路径：`~/.openclaw/` + `~/.openclaw/workspace/`
- 支持多 workspace（多 agent 配置）

### Sessions（会话）
- **main**: 主会话
- **group**: 群聊会话
- **isolated**: 隔离会话（子代理）

### Channels（渠道）
支持 50+ 渠道：
- 即时通讯: WhatsApp, Telegram, Slack, Discord, Signal, iMessage, IRC, Microsoft Teams, Matrix, Feishu, LINE, Mattermost, Nextcloud Talk, Nostr, Synology Chat, Twitch, Zalo
- 语音/视频: Google Meet
- 平台: macOS, iOS/Android (Nodes)
- Web: WebChat

### Tools（工具）
- 内置工具: exec, read, write, edit, browser, canvas, nodes, message, sessions_* 等
- 支持 MCP Servers
- Tool allow/deny lists（按 agent 配置）

### Skills（技能）
- 可扩展的能力包（类似 plugin）
- 5400+ 官方 skills 注册（ClawHub）
- 存储在 `~/.openclaw/skills/` 或 workspace 内

---

## 核心概念

### Multi-Agent Routing（多 agent 路由）
```json
{
  "agents": {
    "list": [
      {
        "id": "family",
        "name": "Family",
        "workspace": "~/.openclaw/workspace-family",
        "sandbox": {
          "mode": "all",
          "scope": "agent"
        },
        "tools": {
          "allow": ["exec", "read", "sessions_list"],
          "deny": ["write", "browser", "nodes"]
        }
      }
    ]
  },
  "bindings": [
    {
      "agentId": "family",
      "match": {
        "channel": "whatsapp",
        "peer": { "kind": "group", "id": "xxx@g.us" }
      }
    }
  ]
}
```

### ACP (Agent Client Protocol)
- 外部编码 harness 的标准化协议
- 支持: Pi, Claude Code, Codex, OpenCode, Gemini CLI, Kimi
- 通过 `acpx` backend 运行
- 支持 thread-bound 持久会话

### Subagents（子代理）
- OpenClaw 原生代理运行模式
- 与 ACP 并行（ACP = 外部 harness，subagent = 内部）

---

## 版本信息

- **当前版本**: 2026.3.8（2026-03-09）
- **前身**: Moltbot → Clawdbot → OpenClaw
- **更新时间**: 2026-03-09（Tangsir 手动升级）

---

## 生态项目

### 官方周边
- **nanobot**: 超轻量级 OpenClaw（单 pip install）
- **ClawWork**: OpenClaw 作为 AI 同事（$15K/11hr）
- **awesome-openclaw-skills**: 5400+ skills 精选集

### 社区项目
- **openclaw-mission-control**: AI Agent 编排仪表板
- **LumaDock**: 多 agent 协调教程

---

## 关键配置

### 权限模型
- `permissionMode`: approve-all / approve-reads / deny-all
- `nonInteractivePermissions`: fail / deny
- Sandbox: all / none / agent

### Session 清理
- 超过 24h 未使用的 session 可被清理
- 规则在 `HEARTBEAT.md` 定义

---

## 相关文档

- 官方文档: https://docs.openclaw.ai
- 官网: https://openclaw.ai
- GitHub: https://github.com/openclaw/openclaw
- Skills 市场: https://clawhub.com

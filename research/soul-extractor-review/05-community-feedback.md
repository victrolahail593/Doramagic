# 社区反馈研究报告

研究日期: 2026-03-10 | 模型: GLM-5

## 反馈来源

### 1. Reddit 社区讨论
- **r/openclaw**: 多个关于 SOUL.md 配置和问题的讨论帖
  - "Paste your SOUL.md and I'll tell you what's wrong with it" (5天前)
  - "I made 12 OpenClaw SOUL.md + STYLE.md templates" (2周前)
  - "What does your SOUL.md actually look like?" (1周前)
  - "The ULTIMATE OpenClaw Setup Guide" (3周前)
- **r/AI_Agents**: "Am I doing something wrong or is openclaw incredibly overblown?" (Feb 4, 2026)
- **r/vibecoding**: "How I Finally Understood soul.md, user.md, and memory.md" (1个月前)
- **r/LocalLLaMA**: "I think openclaw is OVERHYPED. Just use skills" (2周前)
- **r/hacking**: "I Scanned Popular OpenClaw Skills - Here's What I Found" (1个月前)
- **r/ArtificialSentience**: "Do Not Use OpenClaw" - 安全架构批评 (Feb 4, 2026)

### 2. GitHub Issues & Discussions
- **steipete/SOUL.md**: Issues 页面存在但开放 issue 较少
- **openclaw/openclaw #24852**: Subagent Sessions 不加载 SOUL.md/IDENTITY.md/USER.md
- **openclaw/openclaw #20131**: "I built a curated list of copy-paste SOUL.md templates"
- **moltbot/moltbot #2948**: soul.md 链接损坏问题

### 3. 相关技能项目
- **aaronjmars/soul.md**: 官方 soul 构建工具，支持数据提取和人格生成
- **kesslerio/soulcraft-openclaw-skill**: 通过对话创建/改进 SOUL.md
- **NEON-SOUL (ClawHub)**: 自动化灵魂合成，从记忆文件提取身份
- **agent-soul-crafter**: 结构化 SOUL.md 模板设计

### 4. 技术博客与教程
- dev.to: "The Complete SOUL.md Template Guide"
- Medium: SOUL.md 完整指南
- openclawsoul.org: 官方人格系统文档
- soulspec.org: AI Agent 人格开放标准
- mindstudio.ai: OpenClaw 介绍文章
- smallai.in: SOUL.md 深度解析

## 用户痛点

### P0 - 严重问题（影响核心功能）

1. **SOUL.md 不被加载或被忽略**
   - 文件位置错误导致 OpenClaw 静默忽略
   - 重启 gateway 后代理"忘记"人格
   - 子代理会话不继承主代理的 SOUL.md/IDENTITY.md/USER.md

2. **Personality Drift（人格漂移）**
   - 代理在对话中逐渐偏离设定的人格
   - 较弱的模型（GPT-4o-mini, Qwen, Gemini Flash）更严重
   - SOUL.md 改变频繁导致系统身份不稳定

3. **SOUL.md 内容无效**
   - 空文件或过于泛化的内容
   - 过长的文档被模型忽略（只读前几段）
   - 用户花费 30-60 分钟编写，代理仍表现得像通用聊天机器人

### P1 - 重要问题（影响用户体验）

4. **默认配置过于通用**
   - 默认 SOUL.md 和 AGENTS.md 不包含用户特定信息
   - 用户需要花费大量时间调优配置
   - "90% 的 'it just works' 帖子来自花了数小时调配置的人"

5. **知识管理困难**
   - 信息杂乱，难以手动梳理所有 md 文件
   - 系统增长后变得不可靠
   - 缺乏有效的上下文切换机制

6. **模型兼容性问题**
   - 较小模型无法从文件中读取指令并正确执行
   - 需要将 SOUL.md 放入系统提示才能生效
   - 跨模型移植性差

### P2 - 改进机会（影响便利性）

7. **模板质量参差不齐**
   - 付费模板 ($17) 但不含 AGENTS.md
   - 社区模板分散，难以找到高质量资源

8. **安全性担忧**
   - 身份层可从执行上下文内部修改，无需验证
   - ClawHub 发现 341 个恶意技能 (ClawHavoc 攻击)
   - 代理权限过大，与用户相同

## 用户期望

### 高优先级期望

1. **自动化人格提取**
   - 从现有数据（聊天记录、文档、社交媒体）自动提取人格特征
   - 智能发现模式、价值观、沟通风格
   - 支持 Claude、ChatGPT、Substack、X 等数据源导入

2. **人格稳定性保障**
   - 防止人格漂移的机制
   - 一致性验证和漂移检测
   - 宪法式不可协商规则

3. **更好的模板系统**
   - 高质量预构建模板
   - 分层模板结构（默认语气 + 渠道特定规则 + 硬性限制）
   - SOUL.md + STYLE.md 分离模式

### 中优先级期望

4. **知识管理改进**
   - 可预测的知识管理机制
   - 防止系统无限膨胀
   - 上下文切换的清晰边界

5. **跨模型兼容**
   - SOUL.md 可移植性测试工具
   - 自动检测漂移并修复
   - 适配不同模型能力的输出

6. **安全性增强**
   - 身份层不可变保护
   - 技能安全审计
   - 沙箱隔离

### 低优先级期望

7. **调试和反馈工具**
   - SOUL.md 问题诊断
   - 人格表现可视化
   - 配置验证和错误提示

8. **多代理协作**
   - 不同人格的代理团队
   - 人格间的协调机制

## 改进建议

### 针对 soul-extractor skill 的具体建议

#### P0 - 必须实现

1. **智能提取验证**
   - 提取后自动验证人格一致性
   - 检测矛盾价值观和冲突规则
   - 提供置信度评分

2. **漂移防护机制**
   - 生成"宪法条款"（不可协商规则）
   - 定期验证输出与 SOUL.md 的一致性
   - 自动回滚检测到的漂移

3. **多数据源整合**
   - 支持常见数据格式导入（JSON, CSV, Markdown）
   - 自动去重和冲突解决
   - 数据来源追溯（provenance）

#### P1 - 应该实现

4. **分层输出结构**
   ```
   extracted-soul/
   ├── SOUL.md          # 核心人格
   ├── STYLE.md         # 沟通风格
   ├── VALUES.md        # 价值观和原则
   ├── BOUNDARIES.md    # 边界和限制
   └── CONTEXT.md       # 情境特定规则
   ```

5. **模型适配层**
   - 自动检测目标模型能力
   - 为较弱模型生成精简版 SOUL
   - 为强大模型生成完整版

6. **交互式精炼**
   - 提取后引导用户确认关键人格特征
   - 提供选项调整提取结果
   - 生成多个候选版本供选择

#### P2 - 可以实现

7. **社区模板集成**
   - 支持从 ClawHub/souls.directory 导入模板
   - 自动匹配用户需求与现有模板
   - 基于模板的快速定制

8. **安全审计功能**
   - 检测潜在恶意指令
   - 验证人格修改权限
   - 生成安全报告

## 优先级排序

### P0 (必须)
- 提取验证和一致性检查
- 人格漂移防护机制
- 核心数据源支持（本地文件 + 常见格式）

### P1 (重要)
- 分层输出结构
- 模型适配层
- 交互式精炼流程
- 多数据源整合

### P2 (有价值)
- 社区模板集成
- 安全审计功能
- 高级调试工具
- 多代理协作支持

---

## 附录：关键引用

> "Your SOUL.md is doing more work than any skill you'll ever install. It's the first thing your agent reads on every single message. If it's bad, everything feels off and you can't figure out why."
> — Reddit r/openclaw

> "90% of the 'it just works' posts you see on X come from people who spent hours dialing in their config files. The default SOUL.md and AGENTS.md are super generic."
> — Reddit r/AI_Agents

> "For weaker or smaller models: paste your SOUL.md and STYLE.md directly into the system prompt. Smaller models are worse at following instructions from files they read mid-conversation."
> — aaronjmars/soul.md

> "If soul.md changes often, your system doesn't have stable identity."
> — Reddit r/vibecoding

> "The fundamental issue isn't just finding specific malicious skills, but that the architecture of most agent frameworks defaults to full user permissions."
> — Reddit r/hacking
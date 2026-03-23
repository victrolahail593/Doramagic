# OpenClaw 用户真实使用情况研究报告

*基于 2026 年 3 月 Web 研究数据*

---

## 一、OpenClaw 用户画像（实际用户是谁）

### 1.1 核心用户群

**技术开发者（占比最大）**：GitHub 250,000+ Stars 的项目，核心用户群是有服务器运维经验的开发者。V2EX 社区大量帖子表明，最活跃的用户群体是独立开发者和技术极客，他们把 OpenClaw 部署在 Mac mini、Hetzner VPS 或树莓派上。

**"懂一点技术的普通人"（增长最快但流失也最大）**：36氪报道称"第一批玩 OpenClaw 的人，已经开始清醒了"——大量用户花钱找人安装（甚至万元安装费有人下单），但装好后"不知道用来干嘛"。V2EX 帖子标题直接是"openclaw 搭建好了却不知道用来干嘛"和"感觉好像很牛逼，但他到底能干啥？"

**独立创业者 / Solo Founder**：多个案例显示，solo founder 用 OpenClaw 搭建 4 个专业 agent（策略、开发、营销、商务），通过 Telegram 7x24 运行。

**企业行政/文秘人员**：少数派文章提到企业行政人员把 OpenClaw 定位为"文秘"，交给它写日报、周报、季度总结和年度考核材料。

### 1.2 地域差异

| 维度 | 中国用户 | 西方用户 |
|------|---------|---------|
| 主要渠道 | 飞书（最主流）、企业微信、钉钉、QQ | Telegram（最主流）、Discord、Slack |
| 核心模型 | DeepSeek（便宜）、免费 API（HodlAI） | Claude/GPT-4/Gemini |
| 痛点侧重 | Token 费用（"倾家荡产"）、安装门槛 | 安全性、记忆管理 |
| 生态项目 | openclaw-china（微信适配）、openclaw-feishu | Home Assistant 集成、SwitchBot AI Hub |

---

## 二、高频使用场景排名（基于真实数据）

根据社区讨论频次、ClawHub 下载量、Showcase 项目和用户分享文章综合排序：

### Tier 1：最高频（大量用户日常使用）

**1. 每日信息聚合 / 早间简报**
- 固定时间通过 Telegram/飞书推送天气、日历、任务、新闻、健康数据、股票涨跌
- 几乎所有"OpenClaw 能干什么"的教程都以此为第一个示例
- 代表性 skill：Summarize（22,400+ 下载）、Weather（18,600+ 下载）

**2. 邮件收件箱管理**
- 自动分类、退订垃圾邮件、起草回复。有用户 2 天清理 4,000+ 封邮件
- 但也有 V2EX 用户反馈"收发整理邮件意义不大，都不够支付 token 的钱"

**3. 编码辅助 / DevOps 自动化**
- 审查 build 日志、修复 CI/CD、推送代码、创建 issue
- 有开发者遛狗时让 OpenClaw 自动修复 PR 中的 bug 并重新部署
- 代表性 skill：GitHub（21,600+ 下载）

### Tier 2：中高频（技术用户常用）

**4. 网页浏览与信息抓取**
- 抓取竞品价格、监控论坛热帖、抓取 X（推特）内容
- 代表性 skill：Tavily Search（23,800+ 下载）、Agent Browser（11,000+）、ByteRover（16,000+）
- Browserwing 等浏览器自动化工具被称为"让 OpenClaw 真正能落地干活的秘密武器"

**5. 内容创作与社交媒体运营**
- 自动生成文章、发布推文、运营 X 账号
- 有用户的 agent 自主运营 X 账号，"99% 的内容是 agent 自己想的和写的"
- 但稳定性和质量控制仍需人工把关

**6. 智能家居控制**
- Home Assistant 集成最成熟；SwitchBot 2026 年 2 月发布原生 OpenClaw 支持的 AI Hub
- 用户给 Agent 配置了浣熊人格来控制家里的设备
- 场景：根据天气预报调节锅炉、控制空气净化器、语音指令控灯

### Tier 3：中低频（特定需求用户）

**7. 金融分析与交易**
- 股票动量评分、RSI 分析、止损规则、自动记录交易
- 加密货币套利监控（7x24 Telegram 推送）
- 但多数用户反馈 token 成本过高，简单的股价提醒一晚上烧掉 570 万 tokens

**8. 多 Agent 协作系统**
- Discord 中搭建研究 agent + 写作 agent + 设计 agent 的"内容工厂"
- V2EX 用户开发了 ClawBrain OS（短期经验 + 中期方法 + 长期知识三层记忆）

**9. 会议纪要与任务分配**
- 转录 → 结构化摘要 → 自动创建 Jira/Linear/Todoist 任务

**10. CRM 与销售自动化**
- 新线索自动研究公司、查 LinkedIn、匹配案例、生成方案、5 分钟内发送

---

## 三、用户最常安装的 Skills 类别

基于 ClawHub 下载量数据（截至 2026 年 2 月，13,729 个 skill，150 万+ 总下载量）：

| 排名 | Skill 名称 | 下载量 | 类别 |
|------|-----------|--------|------|
| 1 | Capability Evolver | ~35,000 | Agent 自进化 |
| 2 | gog | ~29,400 | 通用工具 |
| 3 | Tavily Search | ~23,800 | 网页搜索 |
| 4 | Summarize | ~22,400 | 内容摘要 |
| 5 | GitHub | ~21,600 | 代码管理 |
| 6 | Weather | ~18,600 | 信息聚合 |
| 7 | Sonoscli | ~18,600 | 音频控制 |
| 8 | Ontology | ~18,100 | 知识图谱 |
| 9 | Wacli | ~16,400 | CLI 工具 |
| 10 | ByteRover | ~16,000 | 浏览器自动化 |
| 11 | Self-Improving Agent | ~15,900 | Agent 自改进 |
| 12 | Browser Relay | ~11,000+ | 浏览器自动化 |

**类别排序**：
1. **Agent 自进化/自改进**（Capability Evolver + Self-Improving Agent = 50,000+）
2. **网页搜索与浏览**（Tavily + ByteRover + Browser Relay = 50,000+）
3. **内容处理**（Summarize + Ontology = 40,000+）
4. **开发者工具**（GitHub + Wacli = 38,000+）
5. **信息聚合**（Weather 等 = 18,000+）

值得注意的是排名第一的不是实用工具，而是"Agent 自进化"类——说明技术用户群体对 Agent 自主成长能力的兴趣超过了具体的实用功能。

---

## 四、用户未被满足的需求

### 4.1 用户明确提出但做不到的

**记忆系统根本性缺陷**：
- 记忆无上限时全部加载导致 context 溢出，中间记忆被静默截断
- "用得越多，记忆越差——它记住了你说的所有东西，但理解不了任何东西"
- 社区开发了 ClawIntelligentMemory 等补丁，但官方方案仍不成熟

**Token 成本控制**：
- 工作区文件浪费 93.5% 的 token 预算
- Cron job 每次运行累积上下文，简单提醒月费可达 $750
- 用户普遍反映"不够支付 token 的钱"

**精确操控专业软件**：
- Agent 无法准确操作企业级专业软件——大模型不懂特定软件的界面和操作逻辑
- "经常点错地方或误解指令"

**安全与隐私**：
- API key 明文存储（"2026 年的应用犯了 2002 年的错误"）
- 13.5 万+ 实例暴露在公网，无需登录即可访问
- ClawHavoc 事件：1,184 个恶意 skill 窃取 API 密钥、SSH 私钥、加密钱包

**多用户 / 权限控制**：
- 没有多用户访问控制
- 家庭或团队场景下无法区分不同用户的权限

### 4.2 用户想要但生态中缺失的

- **可靠的中文 IM 原生支持**：微信个人号接入稳定性和合规性差，企业微信是折中方案
- **可视化的执行过程**：代码生成和任务执行过程对用户不可见
- **一键安装 skill 的完善体验**：大多数 skill 依赖 brew 等系统工具，无法真正一键安装
- **离线 / 本地模型的深度整合**：用 Ollama 跑本地模型很吃 GPU 和内存，体验不够流畅
- **Agent 行为的可预测性**：Agent 经常"跑偏"——"在完成小任务时可能陷入不必要的推理循环、反复调用工具、或中途重新解释目标"

---

## 五、与 AllInOne 的关联分析

OpenClaw 的 SOUL.md / MEMORY.md / USER.md 体系揭示了一个核心问题：**Agent 的"灵魂"依赖用户手动编写和维护，缺乏从真实数据中自动提取和构建的能力。**

### 5.1 "灵魂提取"最有价值的场景

1. **个人知识库自动构建** — 解决 memory.md 膨胀失真问题
2. **个性化 SOUL.md 生成** — 从行为中提取，而非手写
3. **信息聚合个性化增强** — 让简报基于用户真正关心的话题
4. **专业领域知识注入** — 解决"大模型什么都懂但什么都不精"
5. **跨平台人格一致性** — 多渠道场景下保持统一理解

### 5.2 战略定位

OpenClaw 生态最大空白：**从"手动配置灵魂"到"自动理解用户"的鸿沟**。ClawHub 排名第一的 Capability Evolver（35,000+ 下载）说明用户最渴望的是 Agent 自主进化和理解用户的能力。

---

**Sources:**

- [OpenClaw Official Site](https://openclaw.ai/)
- [ClawHub Skill Registry](https://clawhub.ai/)
- [VoltAgent/awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills)
- [少数派: 高强度使用两周体验](https://sspai.com/post/106232)
- [36氪: 第一批玩OpenClaw的人已经开始清醒了](https://36kr.com/p/3709855637598595)
- [V2EX: 搭建好了不知道用来干嘛](https://www.v2ex.com/t/1195953)
- [知乎: 记忆系统架构深度解析](https://zhuanlan.zhihu.com/p/2005943466006438841)
- [The 20 Biggest OpenClaw Problems](https://github.com/openclaw/openclaw/discussions/26472)
- [CyberPress: ClawHavoc 1,184 Malicious Skills](https://cyberpress.org/clawhavoc-poisons-openclaws-clawhub-with-1184-malicious-skills/)

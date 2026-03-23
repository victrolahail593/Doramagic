# Doramagic 深度研究报告：什么是“好作业”，以及如何科学地定义和量化它

**Date:** 2026-03-15  
**Owner:** Codex  
**Status:** Draft  
**Scope:** 回答 Doramagic 作为“抄作业”型知识产品，应该如何系统性评估 GitHub 项目与 Skill 市场资产是否值得提取，并形成可落地的指标体系与评分框架。

---

## 0. 执行摘要

这份报告的核心结论是：

> **“好作业”不是最火的项目，也不是写得最漂亮的项目，而是能在 Doramagic 场景里，最大化“提取后增量价值”的项目。**

对 Doramagic 来说，一个 source 的价值不是静态的“代码质量”或“社区热度”，而是下面这个目标函数：

`GoodHomeworkValue = NeedFit × Trust × ExtractableKnowledge × RuntimeTransferability × MarginalGain / Cost`

这五个词分别解决五个问题：

- `NeedFit`：它是不是用户当前问题的合适作业，而不是一般意义上的好项目？
- `Trust`：它是否足够可靠，避免垃圾进垃圾出？
- `ExtractableKnowledge`：它有没有值得 Doramagic 提取的 WHY / UNSAID，而不只是功能清单？
- `RuntimeTransferability`：它能不能被锻造成可用 AI 道具，而不是只能写成一篇研究报告？
- `MarginalGain`：提取它之后，对基础模型和现有 Doramagic 资产，究竟增加了多少新知识？

这里最关键的不是“source 本身好不好”，而是：

## **source 对 Doramagic 的下游价值有多大。**

因此，Doramagic 应该把“好作业”的判断拆成两层：

1. **Source Quality**：开源项目或 Skill 本身靠不靠谱  
2. **Extraction Value**：它是否值得 Doramagic 花提取成本去做

高质量 source 不一定是高提取价值 source。反过来，某些中等热度但高度结构化、边界清晰、社区踩坑密集的项目，反而可能是 Doramagic 最好的“作业”。

---

## 1. Doramagic 语境下，“好作业”不是通用定义

Doramagic 的定位不是代码搜索，也不是项目排行，而是：

- 从开源世界找到现成方案
- 提取 WHY 与 UNSAID
- 把它们锻造成用户可直接使用的 AI 道具

这意味着 Doramagic 关心的不是“这个 repo 在 GitHub 上是否优秀”这种泛化问题，而是：

### 1.1 它是不是一个值得被“抄”的参考对象

有些项目很成功，但不适合抄：

- 过度依赖内部基础设施
- 组织流程太重
- 针对极大规模场景过度设计
- 抽象层太厚，普通用户场景迁移成本太高

### 1.2 它是不是一个值得被“提取”的知识对象

有些项目很实用，但提取价值低：

- 文档完整到接近教科书，WHY/UNSAID 稀缺
- 基础模型已经高度熟悉其主路径
- 社区讨论少，边缘案例少
- 核心思想太薄，只是已有模式的轻量包装

### 1.3 它是不是一个值得被“锻造”为工具”的基础

有些项目理论价值高，但锻造成 Skill 很差：

- 依赖复杂
- 接口不稳定
- 运维负担极高
- 权限模型危险
- 与 OpenClaw / agent runtime 的动作模式不兼容

所以，Doramagic 不能沿用 GitHub 用户的“好项目”定义。  
它必须建立自己的定义：

> **好作业 = 在当前用户需求与 Doramagic 提取管线下，能稳定产出高增量、可迁移、可锻造知识的 source。**

---

## 2. 为什么 GitHub 项目和 Skill 市场必须分开评判

这两个 source 看起来都叫“作业”，但本体不同。

## 2.1 GitHub 项目是“原料型作业”

GitHub 项目的价值通常来自：

- 原始设计哲学
- 架构取舍
- 社区积累的坑
- 实际被验证过的模块边界
- 文档、Issue、PR、Release Notes 中的隐性知识

它偏向知识密度高，但离最终用户可直接使用还有距离。

## 2.2 Skill 市场资产是“半成品作业”

Skill 已经是面向 agent runtime 的产品化对象。

它的价值更多来自：

- 触发机制是否精准
- 配置是否清晰
- 依赖是否可安装
- 运行是否稳定
- 权限是否可控
- 和其他 Skill 是否能组合

它偏向运行时价值高，但原始 WHY/UNSAID 可能比 GitHub 项目薄。

## 2.3 结论

因此两者需要不同的评判体系：

- **GitHub 项目**：更看重知识密度、生态验证、社区智慧和架构代表性
- **Skill 市场**：更看重运行成功率、安全边界、可组合性和安装维护成本

如果混用同一套榜单，Doramagic 会犯两个大错：

- 用“热度”去挑 Skill，结果选到安装失败率高、权限爆炸的资产
- 用“可运行性”去挑 repo，结果错过真正有 WHY/UNSAID 密度的项目

---

## 3. 第一性原理：Doramagic 真正要最大化的是什么

我建议 Doramagic 把“好作业”建模成一个**期望增量价值问题**，而不是一个“静态质量打分问题”。

### 3.1 基本公式

先给一个总公式：

`EHV = Gate × NeedFit × SourceValue × MarginalGain ÷ AcquisitionCost`

其中：

- `Gate`：硬门槛，只要踩线就直接淘汰
- `NeedFit`：和当前用户任务的匹配度
- `SourceValue`：source 本身的综合质量
- `MarginalGain`：提取后能给 Doramagic 带来的新增知识量
- `AcquisitionCost`：提取、验证、维护它的成本

### 3.2 为什么这是 Doramagic 的正确目标

因为 Doramagic 已经在内部验证过：  
完整“灵魂”注入可以把回答质量从 `42%` 提高到 `96%`，代码半魂也能把质量从 `42%` 提高到 `83%`。这说明对 Doramagic 来说，source 的真正价值不是“它多有名”，而是“它能把模型质量拉高多少”。  
参见 [PRODUCT_MANUAL.md](/Users/tang/Documents/vibecoding/Doramagic/docs/PRODUCT_MANUAL.md#L948)。

因此，最重要的指标不是 stars，也不是 downloads，而是：

## **Delta Quality：提取它之后，Doramagic 的能力提升了多少。**

这个结论决定了后面的所有指标都不应独立存在，而应为“增量价值”服务。

---

## 4. 硬门槛：先过滤“再热门也不该抄”的 source

在评分之前，先做 `Gate`。

## 4.1 GitHub 项目 Gate

以下任一命中，默认不进入候选池，除非人工 override：

- 仓库已 archived
- 没有明确 license
- 近 12-18 个月无有效维护，且 issue / release 也停滞
- 核心依赖存在未处理高危漏洞
- 项目依赖或安装路径高度脆弱，无法复现
- 社区信号存在明显异常，疑似刷星或僵尸热度

官方与生态支持：

- GitHub 官方的 Community Profile Metrics 本身就把 README、License、Code of Conduct、Contributing、Issue/PR templates 等作为项目健康信号的一部分  
  https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-community-profiles-for-public-repositories
- OpenSSF Scorecard 会检查 branch protection、CI、dependency update、signed releases、pinned dependencies、security policy 等供应链与工程风险  
  https://scorecard.dev/
- deps.dev 提供依赖、版本、advisory、maintainers 等可机器读取的包生态信息  
  https://docs.deps.dev/

## 4.2 Skill Gate

Skill 市场的 Gate 更严格，因为它更接近运行时执行对象。

默认淘汰条件：

- 权限范围过大且解释不清
- 依赖外部命令或服务过多，安装路径脆弱
- 版本变更频繁但缺乏 changelog
- 存在明显越权、读写工作区、网络调用风险但没有明确安全声明
- 多个版本安装成功率或首跑成功率过低
- 市场有下载/点赞，但几乎没有成功使用证据

OpenClaw / ClawHub 官方材料也强调：第三方 skill 应视为 untrusted，安装在隔离目录，使用前应审查，并且市场面板会暴露 stars、downloads、version history、verification 等信号。  
https://openclaw.notion.site/ClawHub-User-Guide-2484959f1a7b80d8a89acdb3ebf4e67f  
https://www.openclaw.cloud/en/clawhub

结论很简单：

> Doramagic 的第一原则不是“热不热门”，而是“能不能安全、稳定地作为作业被抄”。 

---

## 5. GitHub 项目的“好作业”指标体系

我建议把 GitHub 项目的评分拆成六个大维度。

## 5.1 Need Fit：任务契合度

这是最重要的一项，应该权重最高。

不是“项目整体有多强”，而是：

- 是否覆盖当前用户任务的关键能力
- 是否符合用户约束
- 改造成目标方案的成本有多高

建议拆成三个子分：

### A. Capability Coverage

项目覆盖多少必需能力。

示例：

- 用户要“AI 客服 + CRM + 预约”
- 某 repo 只覆盖客服，没有预约和 CRM
- 那它可能是好项目，但不是当前任务的好作业

### B. Constraint Match

项目是否满足用户约束：

- self-hosted / cloud
- Python / TS / no-code
- low-ops / high-control
- 单租户 / 多租户
- 低成本 / 高扩展性

### C. Adaptation Cost

迁移到用户场景需要付出多大改造代价。

我建议公式化为：

`NeedFit = 0.45 × Coverage + 0.35 × ConstraintMatch + 0.20 × (1 - AdaptationCost)`

其中 `Coverage` 不要做简单关键词相似度，而要做任务图覆盖率。

---

## 5.2 Trust：项目可靠性与生存性

这类指标的目标不是判断“项目写得优不优雅”，而是判断：

**Doramagic 把它当作知识源，会不会引入过时、脆弱、错误或不可持续的知识。**

建议至少看以下六类信号。

### A. 维护活跃度

- 最近 90 / 180 / 365 天 commit 活跃度
- 最近一次 release 距今多久
- 版本节奏是否仍在推进

### B. 社区响应速度

CHAOSS 指标体系长期把 `issue resolution duration`、`response time`、`change request closure ratio` 一类时间性指标作为社区健康的重要组成部分。  
https://chaoss.community/kb-metric-issue-resolution-duration/  
https://chaoss.community/kb-metric-change-request-closure-ratio/

可量化为：

- 中位数首响应时间
- 中位数关闭时间
- 90 天关闭率

### C. 维护者集中度

这决定“作者一走项目就死”的风险。

可以使用：

- top-1 contributor 占比
- top-3 contributor 占比
- 最近 180 天活跃 maintainer 数

这类风险可以用 bus factor / elephant factor 思想建模。对 Doramagic 来说，这不是学术洁癖，而是直接影响知识是否会快速失效。

### D. 供应链与安全

OpenSSF Scorecard 可以直接作为机器信号：

- branch protection
- security policy
- fuzzing
- token permissions
- pinned dependencies
- CI tests
- signed releases

### E. 真实被采用程度

GitHub 官方允许显示 dependents / used by，这类信号比 stars 更接近“被真实集成”。  
https://docs.github.com/en/repositories/viewing-activity-and-data-for-your-repository/viewing-a-repositorys-dependencies/exploring-the-dependencies-of-a-repository

对于包生态，还可以结合：

- package manager dependents
- download counts
- deps.dev advisories / versions / maintainers

### F. 治理完整度

GitHub Community Profile Metrics 中的以下项目都值得进入评分：

- README
- License
- Security policy
- Contributing guide
- Issue templates
- PR template
- Code of conduct

这些不是形式主义。它们通常代表：

- 项目是否面向外部协作
- 知识是否可进入社区循环
- 决策是否相对稳定

---

## 5.3 Extractable Knowledge：可提取知识密度

这是 Doramagic 和一般开源榜单最大的分野。

一个项目再靠谱，如果只能提取出“它有这些功能”，对 Doramagic 的价值仍然有限。Doramagic 真正需要的是：

- WHY
- UNSAID
- 边界条件
- 社区踩坑
- 决策规则

所以我建议单独建一个 `Knowledge Yield Score`。

### A. Rationale Visibility

WHY 是否有外显载体：

- Architecture Decision Records
- release notes 中的 breaking-change 理由
- maintainer 在 issue / discussion / PR 里的 design rationale
- docs 中的 trade-off 说明

### B. Community Wisdom Density

Issue / Discussion / PR 评论中是否存在高价值、反复出现的坑。

不看总量，看“有价值密度”：

- 高互动线程数
- 问题复现 + maintainer 解释 + workaround 同时存在的线程比例
- 过去 12 个月内依然活跃的 FAQ / trap 类讨论

### C. Example / Test Richness

例子和测试并不只是验证质量，也能暴露：

- API 典型用法
- edge cases
- 真实约束

对 Doramagic 来说，example 和 tests 是把 WHAT 转成 HOW / IF 的关键材料。

### D. Contradiction Richness

真正有价值的 source 往往不是“没有争议”，而是：

- 有争议
- 有取舍
- 有清晰理由

因为 WHY 常常诞生在取舍和反例里。

### E. Modularity / Boundary Clarity

模块边界越清楚，越容易被拆成知识卡片和可复用单元。

可观测信号：

- 明确模块目录
- 插件架构
- adapter / provider / storage 等边界层
- extension points

这决定 Doramagic 能否做“拆零件”而不是只能做项目总览。

---

## 5.4 Runtime Transferability：可锻造成工具的程度

这一步经常被忽略，但对 Doramagic 很关键。

有些项目知识密度高，但很难变成 OpenClaw Skill 或 AI 道具。

建议看四类信号：

### A. 安装与复现路径是否清晰

- 是否有一条标准安装路径
- 是否有 lockfile / docker / compose / example env
- 是否有快速开始示例

### B. 接口是否稳定

- API / CLI / config schema 是否频繁 breaking
- release notes 是否说明迁移路径

### C. 是否具备 agent-friendly surface

- CLI 命令清晰
- 配置文件结构化
- 输入输出可被机器消费
- 文档具备脚本化执行价值

### D. 是否存在明确扩展点

如果项目本身就是插件式、模块式、workflow 式，其知识更容易被转成 Skill。

---

## 5.5 Ecosystem Validation：生态验证强度

这部分是大家最熟悉的 stars / forks / downloads / mentions。

但我的结论是：

> **这些指标必须被保留，但必须被重做。**

### A. Stars 不能直接用原值

原因有三：

1. stars 是兴趣信号，不是质量真值  
2. stars 分布重尾，直接线性比较会让头部项目碾压一切  
3. 近期研究表明 GitHub star 存在被虚假账号操纵的风险，且机器人和假账号在图结构上可形成可识别模式  
   https://www.ndss-symposium.org/ndss-paper/auto-draft-421/

因此我建议：

- 对 stars 取 `log1p`
- 在同类目内做 percentile 或 z-score
- 再叠加 fraud penalty

推荐：

`StarScore = percentile(log1p(stars), cohort) × (1 - FraudRisk)`

### B. 增长速度比绝对量更有信息量

一个项目 20k stars 但三年没长，和一个项目 3k stars 但过去 90 天高速增长，信号不同。

我建议用：

`GrowthScore = percentile(log1p(new_stars_90d) / sqrt(age_months + 1), cohort)`

设计原因：

- 对年轻项目避免绝对量劣势
- 对老项目避免历史存量神话

### C. Dependents 比 Forks 更接近“被真实用于生产”

fork 经常包含：

- 教程 fork
- 试验 fork
- 镜像 fork

dependents / used by 更接近“被真实集成”。

### D. 下载量要和成功使用率分开

下载量和安装量都可以造假，或者只是试用。

对 package / skill 生态来说，更有价值的是：

- install-to-first-success
- retained usage
- downstream references

如果平台能拿到这些数据，它们应当压过 raw downloads。

---

## 5.6 Marginal Gain：增量知识价值

这是 Doramagic 独有、也最重要的维度。

为什么“太有名的项目反而提取价值低”这句话成立？  
不是因为名气大不好，而是因为：

### **提取价值看的是增量，不是总量。**

如果基础模型已经对某项目主路径非常熟悉，那么再花很大成本提取它，增益可能有限。  
反过来，一个中等热度但 community wisdom 高、边界复杂、基础模型经常答错的项目，可能是更好的“作业”。

我建议把这个维度正式量化为：

`MarginalGain = BenchmarkLift × Novelty × CoverageOfKnownWeaknesses`

### A. BenchmarkLift

对候选 source 建一组标准问题：

- WHY 问题
- UNSAID / 踩坑问题
- deployment / integration 问题
- trade-off 问题

先让基础模型裸答，再让模型使用轻量提取物或完整提取物回答。

`BenchmarkLift = score_with_source - score_without_source`

这个方法完全符合 Doramagic 自己的产品逻辑，也与现有 A/B/C 实验一脉相承。

### B. Novelty

这里的 novelty 不是“世界上没人见过”，而是：

- 对基础模型不是高度显性的
- 对现有 Doramagic 资产不是重复的
- 对用户真实决策有新增信息

推荐用三个 proxy：

- 与已有知识卡片库的语义去重距离
- 基础模型在该项目 benchmark 上的原始得分
- 社区讨论中 trap / workaround 的独特性

### C. Coverage Of Known Weaknesses

Doramagic 应跟踪“模型在哪些类型题上最容易错”：

- 配置细节
- 兼容性
- 部署坑
- 权限边界
- 默认值误解

如果某个 source 恰好能补这些短板，它的价值应被放大。

这是比“流行度”更接近产品价值的排序方式。

---

## 6. Skill 市场的“好作业”指标体系

Skill 的逻辑和 repo 不同。  
它不是原始知识源，而是接近最终形态的 AI 产品零件。

因此我建议 Skill 评分重点转向运行时。

## 6.1 Need Fit：用户场景匹配度

这和 repo 一样重要，但粒度更细：

- Skill 的触发语义是否正好命中用户意图
- 输入输出是否接近用户任务
- 是否是“拿来就能用”的对象，而不是还要大改

---

## 6.2 Runtime Reliability：运行成功率

这是 Skill 最核心的指标。

推荐看：

- install success rate
- first-run success rate
- median time to first success
- runtime error rate
- rollback / uninstall rate

如果平台暂时没有这些数据，先用 proxy：

- 版本更新后的故障反馈
- issue / comment 中的安装失败比例
- changelog 中的 hotfix 密度

---

## 6.3 Safety Blast Radius：权限与安全边界

Skill 比 repo 更危险，因为它更接近 agent 执行动作。

应对每个 Skill 建 `Safety Score`：

- 是否需要 filesystem write
- 是否需要 network access
- 是否调用外部 shell
- 是否读取 secrets
- 是否跨工作区访问
- 是否能触发 destructive action

同样重要的是：

- 权限是否最小化
- 风险是否可解释
- 是否有 verification / moderation / trusted publisher 标记

Skill 市场里，“好作业”首先必须是“不会把用户环境炸掉”的作业。

---

## 6.4 Composability：可组合性

对 Doramagic 来说，好的 Skill 不只是单点有效，还要能进入更大的工具组合。

建议量化：

- 配置 schema 是否清晰
- 输入输出是否结构化
- 是否和常见 Skill 共存
- 是否依赖特殊全局状态
- 是否需要非常强的 prompt discipline 才能稳定运行

真正好的 Skill 应该像 Lego，不像一次性脚本。

---

## 6.5 Market Validation：市场验证

Skill 市场也可以看 stars、downloads、ratings、comments，但建议权重低于 repo 的生态验证。

原因：

- Skill 更容易被短期流量驱动
- 安装不等于成功
- 热门不等于稳定
- 安全问题的代价更高

因此建议：

- `downloads` 做 `log1p`
- `stars` 做 `log1p`
- 计算 `download-to-star ratio`
- 对 `first_success_rate` 赋更高权重

推荐：

`MarketValidation = 0.25 × log_downloads + 0.15 × log_stars + 0.30 × success_rate + 0.30 × retention_or_reuse`

如果后两项拿不到，就不要高估前两项。

---

## 6.6 Learning Yield：作为“作业”的学习价值

不是每个 Skill 都值得提取。

有些 Skill 只是：

- 一层 prompt 包装
- 一个简单命令转发器
- 一个很窄的工作流脚本

它能用，但不值得作为 Doramagic 的知识源重点投资。

真正值得提取的 Skill 通常具备：

- 明确的任务边界
- 明确的风险边界
- 稳定的配置哲学
- 可迁移到其他任务的通用 pattern

也就是说：

> 对 Skill 来说，Doramagic 看的不是“它能不能跑”，而是“它有没有沉淀出可复用的工具哲学”。 

---

## 7. 不同类型项目的“好”是不同的：不要把所有 source 压成一条排行榜

用户已经指出一个非常关键的问题：  
大厂项目和个人作者项目的“好”，常常不是一种好。

我建议 Doramagic 把 source 先映射到不同 archetype，再在类内比较。

## 7.1 四种 archetype

### A. Canonical Base

特征：

- 高 adoption
- 高 dependents
- 高治理完整度
- 文档与接口稳定

价值：

- 适合做“默认底座”
- 适合做用户教育成本低的安全方案

风险：

- WHY 可能趋于通用化
- LLM prior 已较强，边际提取价值未必最高

### B. Insight Mine

特征：

- 中等 adoption
- 高 issue / discussion 密度
- 高坑点密度
- 维护者愿意讲 rationale

价值：

- 最适合提取 WHY / UNSAID
- 常常是 Doramagic 的黄金作业

### C. Sharp Innovator

特征：

- 体量不大
- 增长快
- 设计尖锐
- 模式新

价值：

- 适合做探索池
- 适合捕捉未来趋势

风险：

- survivability 差
- 安全和稳定性不一定够

### D. Productized Skill

特征：

- 安装简单
- 运行闭环明确
- 用户成功路径短

价值：

- 最适合直接变成道具

风险：

- 知识密度可能薄

## 7.2 战略建议

Doramagic 不应全押“最有名”的作业。  
更合理的策略是组合投资：

- `40%` Canonical Base
- `40%` Insight Mine
- `20%` Sharp Innovator / 新兴 Skill

这能同时兼顾：

- 可信度
- 知识密度
- 边际增益
- 未来趋势

---

## 8. 推荐的量化公式

下面给出一版可直接工程化的量化框架。

## 8.1 GitHub Repo Homework Score

```text
RepoScore =
Gate × NeedFit × (
  0.18 Trust +
  0.20 KnowledgeYield +
  0.12 RuntimeTransferability +
  0.15 EcosystemValidation +
  0.20 MarginalGain +
  0.15 CostEfficiency
)
```

建议子项：

- `NeedFit`
  - capability coverage
  - constraint match
  - adaptation cost
- `Trust`
  - maintenance recency
  - issue response / closure
  - maintainer concentration inverse
  - security / scorecard
  - governance completeness
- `KnowledgeYield`
  - rationale visibility
  - community wisdom density
  - example / test richness
  - contradiction richness
  - modularity
- `RuntimeTransferability`
  - install reproducibility
  - interface stability
  - agent-friendly CLI / config
  - extension points
- `EcosystemValidation`
  - log stars
  - growth velocity
  - dependents / used by
  - package downloads
  - issue / clone / visitor trends
- `MarginalGain`
  - benchmark lift
  - novelty
  - weakness coverage
- `CostEfficiency`
  - extraction cost
  - validation cost
  - maintenance cost

## 8.2 Skill Homework Score

```text
SkillScore =
Gate × NeedFit × (
  0.25 RuntimeReliability +
  0.22 Safety +
  0.18 Composability +
  0.10 MarketValidation +
  0.15 LearningYield +
  0.10 Maintenance
)
```

建议子项：

- `RuntimeReliability`
  - install success
  - first-run success
  - runtime error rate inverse
  - rollback inverse
- `Safety`
  - permission blast radius inverse
  - external call risk inverse
  - secret handling clarity
  - verification / moderation
- `Composability`
  - schema clarity
  - structured outputs
  - dependency simplicity
  - workspace compatibility
- `MarketValidation`
  - log downloads
  - log stars
  - reuse / retention
  - comment quality
- `LearningYield`
  - reusable pattern density
  - rationale clarity
  - risk boundary clarity
- `Maintenance`
  - days since update
  - version stability
  - changelog quality

---

## 9. stars 为什么应该做对数和 cohort normalization

用户提出“Stars 和质量不是线性关系，可能是对数关系”，我赞同，但需要更精确地说：

> **Stars 不是质量的线性代理，而是兴趣与社会传播的弱信号。它应被压缩、归一化、校正，而不应直接相加。**

我的建议：

### 9.1 先取 `log1p`

原因：

- 100 到 1,000 的差距信息量大
- 100,000 到 101,000 的差距信息量很小

### 9.2 再按 cohort 标准化

按下面维度分 cohort：

- 语言
- 类目
- 仓库年龄
- 部署形态
- 是否 library / app / infra / template

否则：

- JS SaaS app 会天然压过 niche infra tool
- 十年老项目会天然压过一年新项目

### 9.3 再叠加 fraud / hype penalty

基于假星研究与市场操纵风险，建议做异常扣分：

- stars 暴涨但 clones / visitors / issues / contributors 不同步增长
- account graph 异常集中
- 新注册用户集中打星

这部分宁可粗糙，也要存在。

---

## 10. Doramagic 最独特的一步：把“好作业”变成实验问题，而不是纯 heuristic 问题

这是我最推荐 Doramagic 采用的做法。

别只做规则打分。  
在规则打分之外，再做一层 **source-to-lift 实验**。

## 10.1 设计一个 Homework Evaluation Harness

对每个候选 source：

1. 自动生成 10-20 个 benchmark 问题
2. 问题覆盖：
   - WHAT
   - HOW
   - WHY
   - UNSAID
   - deployment
   - integration
3. 用基础模型裸答，得到 baseline
4. 用轻量 source 注入后回答，得到 assisted score
5. 计算增量：

`Lift = assisted_score - baseline_score`

## 10.2 为什么这一步极其重要

因为这会直接回答三个 Doramagic 特有问题：

- 太有名的项目是否真的还有提取价值？
- 哪类项目最能补模型短板？
- 哪些 source 虽然质量高，但对 Doramagic 增益很低？

换句话说：

> Doramagic 最终不该依赖“大家都说这个项目好”，而该依赖“这个项目对 Doramagic 的增量实验结果好”。 

这是从 heuristic ranking 进入 scientific ranking 的关键。

---

## 11. 最后的结论

如果把整份报告压成一句话，我的答案是：

> **对 Doramagic 来说，“好作业”不是最火、最大、最标准的 source，而是最能稳定提供高质量增量知识、并可被锻造成用户可用工具的 source。**

因此，Doramagic 应当：

1. 把 GitHub 项目和 Skill 市场分开评估
2. 用硬门槛先过滤不可信 source
3. 对 popularity 做 `log + cohort normalization + fraud penalty`
4. 引入维护、治理、安全、dependents、运行成功率等“真实使用信号”
5. 把 WHY / UNSAID 的“知识密度”做成独立维度
6. 最重要的是，把 `MarginalGain` 做成实验指标

最终，Doramagic 不该回答“这个项目是不是好项目”，而该回答：

## **“这个项目是不是值得被 Doramagic 抄，并且抄完之后真的能让用户更强。”**

---

## 12. 对产品落地的直接建议

如果下一步要工程化，我建议按这个顺序推进：

1. 先实现 `Gate + RepoScore + SkillScore` 的 v0 规则版
2. 再接 GitHub / deps.dev / Scorecard / 市场统计等外部信号
3. 最后补 `Homework Evaluation Harness`，把 `MarginalGain` 从推测变成实验量

一旦第三步完成，Doramagic 的“作业选择”就会从经验主义进入真正的数据驱动。

---

## 13. 参考资料

### 本地上下文

- [INDEX.md](/Users/tang/Documents/vibecoding/Doramagic/INDEX.md)
- [PRODUCT_MANUAL.md](/Users/tang/Documents/vibecoding/Doramagic/docs/PRODUCT_MANUAL.md#L948)

### 外部资料

- GitHub Community Profile Metrics  
  https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-community-profiles-for-public-repositories

- GitHub Dependents / Used by  
  https://docs.github.com/en/repositories/viewing-activity-and-data-for-your-repository/viewing-a-repositorys-dependencies/exploring-the-dependencies-of-a-repository

- OpenSSF Scorecard  
  https://scorecard.dev/

- deps.dev Documentation  
  https://docs.deps.dev/

- CHAOSS Issue Resolution Duration  
  https://chaoss.community/kb-metric-issue-resolution-duration/

- CHAOSS Change Request Closure Ratio  
  https://chaoss.community/kb-metric-change-request-closure-ratio/

- NDSS 2026: Understanding and Quantifying the Security Risks of Fake Stars on GitHub  
  https://www.ndss-symposium.org/ndss-paper/auto-draft-421/

- OpenClaw / ClawHub User Guide  
  https://openclaw.notion.site/ClawHub-User-Guide-2484959f1a7b80d8a89acdb3ebf4e67f

- ClawHub Marketplace  
  https://www.openclaw.cloud/en/clawhub

## 14. 证据与推断边界

下面这些是外部资料直接支持的：

- GitHub 的社区治理完整度可作为公开健康信号
- dependents 比单纯 stars 更接近真实集成
- OpenSSF Scorecard 与 deps.dev 可提供安全与依赖生态信号
- CHAOSS 对响应时长、关闭率等社区健康指标有成熟定义
- fake stars 是真实存在的风险，不能把 stars 当作无偏真值
- Skill 市场存在 untrusted code 与隔离安装等安全前提

下面这些是本报告的综合推断：

- Doramagic 应把“好作业”定义为增量价值最大化问题
- GitHub 项目和 Skill 必须用不同权重
- “太有名的项目提取价值可能更低”应通过 `MarginalGain` 实验来验证，而不是直接拍脑袋判断
- `Homework Evaluation Harness` 是 Doramagic 最值得投资的评测基础设施

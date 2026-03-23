# Doramagic 深度研究报告：看起来像好作业、实际上会误导知识提取引擎的“暗雷”清单

**Date:** 2026-03-15  
**Owner:** Codex  
**Status:** Draft  
**Scope:** 研究那些表面健康、活跃、有社区、看起来值得提取，但会让 Doramagic 的 WHY / UNSAID / Rule 提取产出错误、误导或不可迁移知识的项目与 Skill 类型，并给出识别方法。

---

## 0. 执行摘要

这份报告的核心判断是：

> **最危险的 source，不是明显差的 source，而是“看起来像好作业”的 source。**

因为明显差的 source 很容易被已有过滤器淘汰；真正会伤害 Doramagic 的，是那些：

- GitHub 指标不错
- 社区活跃
- 文档存在
- 代码也不差

但它们会系统性诱导提取引擎犯四类错误：

1. **假 WHY**：项目没有公开足够的设计 rationale，LLM 用“合理故事”补全  
2. **假 UNSAID**：社区讨论只是局部噪声、临时 workaround 或例外情况，却被抽成通用规则  
3. **假可迁移性**：规则在原项目上下文里成立，但换到用户场景就失效  
4. **假高质量**：证据链看似充足，卡片结构也完整，但整体知识图谱把用户带向错误方向

因此，Doramagic 需要的不只是“好作业评分”，还需要一套：

## **Deceptive Source Detection（欺骗性优质作业识别）**

也就是：

- 识别哪些 source 会诱导 Stage 1 伪造 WHY
- 识别哪些 source 会诱导 Stage 2-3 把局部现象抽成全局规则
- 识别哪些 source 会让 Knowledge Compiler 编译出“内部一致但外部错误”的知识包

本报告把这些暗雷归纳为 12 类，并给出每类的：

- 欺骗机制
- 伤害路径
- 可观测识别信号
- 对应的管线防护建议

---

## 1. 问题定义：什么叫“提取陷阱”

Doramagic 已经有一层 source quality filter，比如：

- 死项目
- 无 license
- 刷星
- 纯 wrapper

这些不是本报告关注点。

本报告研究的是更难的一类对象：

> **表面上足够像“好作业”，因此能通过前置筛选；但进入提取管线后，会系统性污染知识产物。**

这里的“污染”不是简单错误，而是更麻烦的三种情况：

### 1.1 结构化正确，语义错误

卡片格式没错，字段齐全，证据也能对上某些文本，但提取出的结论不是项目真正的工作哲学。

### 1.2 局部真实，全局误导

某条规则对某个 issue、某个版本、某个部署环境是真的，但被提升成通用 truth。

### 1.3 项目内正确，用户侧错误

知识忠实反映了原项目上下文，但迁移到用户场景后不成立，导致 Doramagic 给出“有依据但不适用”的建议。

---

## 2. 为什么这些暗雷会骗过提取引擎

表面健康的坏 source 之所以危险，是因为它们利用了知识提取系统的几个天然弱点。

## 2.1 LLM 会在 rationale 缺失处自动补全

如果代码能解释 WHAT，文档能解释 HOW，但 WHY 没写，模型很容易生成“看上去合理”的设计哲学。  
这种现象在 repo 级问答里尤其危险：检索不完整、知识冲突和模型内部先验会共同导致高置信错误整合。`Astute RAG` 直接指出 imperfect retrieval 和 internal-vs-external knowledge conflict 是常态，而不是异常。  
来源：https://aclanthology.org/2025.acl-long.1476/

## 2.2 GitHub 不是中立真相源，而是高度偏置的活动表面

MSR 领域经典研究早就警告过，GitHub 数据并不能被当作“软件开发全貌”的直接代理。`The promises and perils of mining GitHub` 指出很多仓库不是主开发地、issue tracker 和 pull request 流程经常不完整、事件记录不能直接当真。  
来源：https://dl.acm.org/doi/10.1145/2597073.2597074

这对 Doramagic 的含义很直接：

- 你看到的 issue，不等于项目真正关心的问题
- 你看到的讨论，不等于团队真正做决策的地方
- 你看到的活跃，不等于知识完整

## 2.3 架构知识天然会蒸发

SEI 对架构知识管理的研究长期强调：设计 rationale、权衡过程和边界条件如果不被显式保存，会快速丢失。  
来源：https://www.sei.cmu.edu/library/architectural-knowledge-vaporization/

因此，对很多“看起来成熟”的项目，最危险的事实不是它文档差，而是：

> 它的真正 WHY 根本不在公开文本里。

一旦如此，Stage 1 就会被迫从结果反推动机，而这正是最容易生成伪 WHY 的地方。

## 2.4 社区讨论天然高噪声、强情境、易过时

灰色文献系统综述显示，软件工程里的博客、Q&A、论坛和经验帖价值高，但质量标准不稳定、可获得性差、上下文缺失严重。  
来源：https://www.sciencedirect.com/science/article/abs/pii/S0950584921000904

GitHub Discussions 本身也允许回答标记、锁帖、隐藏旧路线图项等治理动作，这意味着公开可见的“社区共识”本来就是被管理过的表面。  
来源：https://docs.github.com/en/discussions  
来源：https://docs.github.com/en/issues/planning-and-tracking-with-projects/understanding-fields/about-single-select-fields?apiVersion=2022-11-28

这会让 Stage 3 的社区提取特别容易把“可见度高的信息”错当成“代表性高的信息”。

---

## 3. 12 类最危险的暗雷

下面这 12 类，是我认为最值得 Doramagic 专门防的 deceptive-good sources。

---

## 3.1 经典名项目先验污染陷阱

### 现象

项目很有名，模型训练中见过很多；一旦进入提取阶段，模型会把自己“早就知道的东西”混进当前 source 理解里。

### 为什么危险

这类 source 不会让模型显得不懂，反而会让模型显得“特别懂”。  
于是错误变成高置信错误。

### 典型后果

- Stage 1 生成过于流畅的 WHY 叙事，但证据锚点稀薄
- Stage 2-3 把模型先验里的最佳实践，投射成该项目的决策哲学
- Stage 4 产出非常像专家、实际上半是记忆半是推断的 narrative

### 识别方法

- 做 blind grounding 对照：只给代码/issue 证据，不给项目名，看 WHY 是否大幅变化
- 做 anti-memory prompt：要求“只引用 source 内证据，不允许使用训练先验”
- 统计 `evidence density / narrative confidence` 比例，如果叙事很强、E1/E2 锚点很薄，标红

### 管线建议

- 对头部名项目提高“证据密度阈值”
- 单独引入 `prior contamination risk`
- 强制输出“这部分是证据支持 / 这部分是推断”

本地佐证：Doramagic 自己在 superpowers 实验中已经观察到“模型对熟悉项目反而更容易幻觉”的现象。[INDEX.md](/Users/tang/Documents/vibecoding/Doramagic/INDEX.md#L154)

---

## 3.2 Rationale Vacuum Trap：公开材料几乎没有 WHY，但结果很整齐

### 现象

代码结构很好，README 很完整，测试也不少，但真正的设计取舍没有记录。

### 为什么危险

这种项目最容易让提取引擎做“逆向心理学”：

- 看到这个结构
- 猜作者一定是为了某种架构原则

问题是，很多结构只是历史偶然、团队习惯、时间压力或遗留约束的结果。

### 典型后果

- 假 WHY
- 假哲学
- 把“现状”误读为“意图”

### 识别方法

- 计算 `Rationale Support Ratio`：
  - ADR / design notes / trade-off docs
  - release notes 中解释 breaking changes 的比例
  - maintainer 在 PR / issue 中明确解释“为什么”的密度
- 如果代码复杂但 rationale support 极低，则把 WHY 标为高风险

### 管线建议

- Stage 1 输出 WHY 前，先判断“是否有足够 rationale evidence”
- 若不足，允许输出“WHY 不可可靠恢复”，而不是硬写

SEI 的架构知识蒸发研究正好支持这一点：真正危险的不是没有代码，而是没有留下 rationale。  
来源：https://www.sei.cmu.edu/library/architectural-knowledge-vaporization/

---

## 3.3 Rewrite Window Trap：项目处于重写/迁移/双轨并存窗口

### 现象

项目很活跃，但同时存在：

- 新旧架构并行
- 文档还没完全更新
- issue 里的建议分属不同版本
- maintainer 说法前后矛盾

### 为什么危险

提取引擎很容易把两个时代的知识拼成一个“统一哲学”，而真实情况是：

- A 规则只适用于旧架构
- B 规则只适用于新架构
- C workaround 已经准备被删除

### 典型后果

- 过时 UNSAID 被当成有效规则
- 版本依赖条件丢失
- 编译出的知识包内部自相矛盾

### 识别方法

- `Temporal Conflict Score`
  - 最近 180 天 release note 是否频繁提 breaking changes
  - 文档与代码中是否出现 old/new、legacy/v2、migration 等信号
  - 高频 issue 是否集中在迁移兼容问题
- 同一主题的 advice 是否在时间轴上明显反转

### 管线建议

- 所有规则默认带 `applies_to_versions`
- Rewrite 窗口内的 source 不应做单一 project philosophy 总结
- 把知识拆成“legacy stack / current stack / future direction”

---

## 3.4 Exception Bias Trap：社区讨论被边缘故障主导

### 现象

社区很活跃，但讨论大量集中在：

- 稀有部署环境
- 极端配置
- 某个版本的奇异 bug
- 特定平台兼容问题

### 为什么危险

issue tracker 不是“正常使用日志”，而是“问题上报表面”。  
如果 Stage 3 只抓高互动线程，就很容易把异常场景抽成通用规则。

### 典型后果

- 提取出的 DR 卡片非常“避坑”，但泛化后吓坏用户
- 例外 workaround 被抬升成默认操作
- 正常 happy path 反而在知识包里缺位

### 识别方法

- `Exception Dominance Ratio`
  - 高互动线程中，部署/兼容/平台异常类占比
- 将 issue cluster 与代码主路径做覆盖比对
- 如果社区规则大多无法映射到核心模块，则降权

### 管线建议

- 社区规则必须带 `scope conditions`
- Rule Compiler 不允许把单 issue workaround 直接提升为 CRITICAL
- 对高频异常场景单独放到“context-bound traps”，而不是 project-wide rules

---

## 3.5 Support Desk Trap：社区活跃其实只是用户支持量大

### 现象

项目社区非常热闹，但内容主要是：

- 安装失败
- 环境变量没配
- 版本没对齐
- 新手不会用

### 为什么危险

这会制造一种错觉：社区很丰富，所以 UNSAID 很多。  
实际上这些讨论只说明用户群大，不说明项目内部有深的决策知识。

### 典型后果

- 提取系统产出一堆“教程型规则”
- 规则听起来具体，但其实是 FAQ，不是哲学或隐性知识
- WHY 层很薄，却被社区热度掩盖

### 识别方法

- `Support-vs-Architecture Mix`
  - 问题求助类线程占比
  - maintainer 设计解释类线程占比
- 统计 issue 中“how do I / installation / error when starting”模式比例

### 管线建议

- 将 support threads 与 architecture/rationale threads 分离采样
- 对“新手支持密集型项目”降低 community wisdom 权重

---

## 3.6 Hidden Context Trap：真正的决策场不在 GitHub

### 现象

项目看起来成熟、活跃、专业，但很多真正决策：

- 发生在 Slack / Discord / internal RFC
- 由企业客户闭门推动
- 或由商业公司内部 roadmap 主导

GitHub 只是最终结果的镜面。

### 为什么危险

提取引擎会错误地假设“公共痕迹足以恢复完整 WHY”，但实际只有局部、甚至是 PR 后的清洗版叙事。

### 典型后果

- Stage 1 把 post-hoc explanation 当成真实动机
- Stage 2 把缺失上下文的 trade-off 抽成一般原则
- Stage 4 生成高一致性 narrative，实则遗漏真正关键约束

### 识别方法

- issue / PR 中频繁出现“discussed offline / internal / sync / RFC elsewhere”
- 大公司开源项目但公共 debate 很少
- 大改动 merged 快、解释少、design review 痕迹薄

### 管线建议

- 对 enterprise-backed 项目引入 `public-context completeness` 指标
- 如果隐藏上下文风险高，限制 WHY 抽象层级
- 倾向提取“observable contract”而不是“claimed philosophy”

GitHub / MSR 研究提醒我们：GitHub 从来不是完整开发现场。  
来源：https://dl.acm.org/doi/10.1145/2597073.2597074

---

## 3.7 Moderated Consensus Trap：你看到的社区“共识”是被治理后的表面

### 现象

项目社区井井有条，讨论有 accepted answer、thread lock、旧路线图项被隐藏，维护者回复很规范。

### 为什么危险

这会给提取引擎一种“这里的社区智慧很稳定”的错觉。  
但被标记为答案、被锁定、被隐藏，本身就是治理动作，不是客观 truth。

### 典型后果

- 维护者当时的临时判断被抽成长期规则
- 争议被压平后，看起来像统一哲学
- 已过时的讨论因为还可见而继续被当作有效证据

### 识别方法

- `Moderation Footprint`
  - accepted answers 比例
  - locked / stale / archived 讨论比例
  - issue / discussion 被关闭但未对应代码变化
- 对“被标记答案”的内容做时序验证，看后续是否被 release/changelog 推翻

### 管线建议

- 不把 accepted answer 直接等同于 ground truth
- 需要后续代码或版本证据做二次确认

GitHub Discussions 官方文档说明了回答标记、锁帖、转移、管理等机制；这些都意味着“可见内容”本身经过治理。  
来源：https://docs.github.com/en/discussions

---

## 3.8 Multi-Persona Trap：同一个项目服务多个完全不同人群

### 现象

项目对：

- 核心开发者
- framework integrators
- DevOps
- beginner users
- enterprise customers

分别有不同最佳实践。

### 为什么危险

如果提取引擎强行输出“该项目的统一哲学”，就会把不同 persona 的 advice 混合，造成错误迁移。

### 典型后果

- 一条对 library author 成立的规则，被用于 end-user
- 一条对 self-hosted 成立的规则，被用于 SaaS 用户
- 叙事看起来完整，实际上 persona 混淆

### 识别方法

- issue / docs / examples 是否分明显 persona
- 是否存在多套安装、部署、扩展文档
- advice 是否依人群分叉明显

### 管线建议

- 知识卡片增加 `audience` / `persona`
- 编译时按 persona 分层，不做单一 project summary

---

## 3.9 Upstream Shadow Trap：关键知识实际属于上游依赖，不属于当前项目

### 现象

项目本身不薄弱，也不是纯 wrapper；但它的大部分关键行为其实由上游框架、SDK、数据库、云平台决定。

### 为什么危险

提取引擎很容易把“当前 repo 的表面行为”误认为“该 repo 的设计哲学”，而真实 WHY 其实在上游系统里。

### 典型后果

- 错把依赖限制当成项目原则
- 错把宿主框架习惯当成作者主动设计
- 导致规则迁移时方向完全反了

### 识别方法

- `Dependency Dominance Index`
  - 关键模块是否主要是 adapters / glue code
  - 核心复杂性是否位于外部 API 契约
- 高比例文档在解释第三方系统，而不是本项目自身结构

### 管线建议

- 将规则标记为 `origin = project | upstream | integration-layer`
- 对 upstream-derived rule 单独降权
- 必要时将提取对象从 repo 升级为“repo + upstream pair”

---

## 3.10 Winner’s History Trap：维护者会重写历史，让当前方案显得理所当然

### 现象

项目维护者表达清晰、文章漂亮、talk 很强，README 和 blog 中有完整 narrative。

### 为什么危险

强 narrative 不一定是假，但它常常是：

- 事后整理
- 为了说服用户或贡献者形成的解释
- 对失败路线的压缩改写

这类 post-hoc rationale 特别容易让 Stage 1 误以为自己抓到了“原始 WHY”。

### 典型后果

- 设计哲学被提取得很漂亮，但缺乏反例与边界
- 历史上的偶然性、妥协、技术债全部消失
- 用户得到的是品牌叙事，不是操作性知识

### 识别方法

- narrative 与早期 PR / issue 历史是否一致
- 是否只存在 polished docs，缺少争议痕迹
- 版本演进中是否有明显“说法更新”

### 管线建议

- 对维护者 blog / 官网文案单列证据等级，不得直接压过代码与 issue
- Stage 1 必须查反例：有哪些设计选择被拒绝过

---

## 3.11 Skill Demo Trap：Skill 看起来很火，其实只是 demo 路径很顺

### 现象

某个 Skill 市场资产：

- 展示效果极好
- stars / downloads 很高
- 安装页写得漂亮

但真实使用场景很窄。

### 为什么危险

Doramagic 如果把它当成“好作业”，会提取出一套对 demo 成立、对真实用户失败的工具哲学。

### 典型后果

- Stage 4 叙事把“顺滑演示路径”描述成“成熟通用工作流”
- 实际部署后失败率高
- 用户以为拿到的是稳定技能，其实是 showcase artifact

### 识别方法

- 下载高但 retention / reuse 低
- comments 高度集中在 showcase use case
- changelog 中大量首跑修复
- first-run success 低于市场均值

### 管线建议

- Skill 市场必须引入 `first-success-rate`
- 对“演示优等生”与“生产优等生”做分榜

---

## 3.12 Skill Over-Permission Trap：功能强、口碑好，但依赖极大权限和隐式环境

### 现象

Skill 很受欢迎，也确实解决问题，但它默认要求：

- 写工作区
- 访问网络
- 调 shell
- 读 secrets
- 依赖一堆本地工具和环境变量

### 为什么危险

从知识提取视角看，这类 Skill 的“成功经验”很容易被误抽为一般规则，但真实前提是：

- 运行环境受控
- 权限足够
- 操作者懂风险

一旦脱离原上下文，知识立即失真。

### 典型后果

- 提取得到的 workflow 看起来高效，实际对普通用户危险
- 规则卡缺少权限边界，误导用户认为这是默认最佳实践

### 识别方法

- 权限 blast radius 审计
- 依赖环境清单长度
- 成功运行是否要求隐式前置配置
- 文档是否明确写出限制条件

### 管线建议

- Skill 提取时必须生成 `operational assumptions`
- 缺少 assumptions 的 workflow 不得进入默认推荐

OpenClaw / ClawHub 官方也强调第三方 skill 属于 untrusted code，应在隔离目录中安装与审查。  
来源：https://openclaw.notion.site/ClawHub-User-Guide-2484959f1a7b80d8a89acdb3ebf4e67f

---

## 4. 最危险的不是单条错规则，而是“高一致性的错知识包”

Doramagic 的风险不只在单卡片错误，更在于一个 source 会让整条管线产出“内部很一致”的错误知识。

典型路径：

1. Stage 0 提取到很多表面事实
2. Stage 1 在 rationale 真空里生成一个顺滑 WHY
3. Stage 2-3 用社区高可见度异常案例补充规则
4. Stage 3.5 因为每张卡都有局部锚点而放行
5. Compiler 把这些局部真实、全局错误的卡片拼成完整知识包
6. Stage 4 叙事进一步放大一致性

于是最终产物最危险的地方在于：

> **它不像胡说，而像非常成熟、非常有体系的专家知识。**

这正是需要专门建立“暗雷检测”的原因。

---

## 5. 可直接工程化的识别指标

下面这些指标最值得直接变成预警器。

## 5.1 Rationale Support Ratio

`明确 WHY 证据 / 总叙事断言`

如果叙事很多、WHY 强，但 ADR、trade-off 文档、maintainer rationale 解释很少，则红灯。

## 5.2 Temporal Conflict Score

`跨版本相互冲突 advice / 总 advice`

用于识别 rewrite / migration trap。

## 5.3 Exception Dominance Ratio

`高互动异常线程占比 / 高互动线程总数`

用于识别 exception bias。

## 5.4 Support-Desk Share

`安装/求助/不会用类线程占比`

用于识别 support desk trap。

## 5.5 Public Context Completeness

基于下面 proxy 反推：

- 是否频繁引用外部讨论场
- 是否缺少 design debate 痕迹
- 是否大改动解释极少

用于识别 hidden context trap。

## 5.6 Persona Divergence Score

不同 persona 的 advice 是否显著分叉。

用于识别 multi-persona trap。

## 5.7 Dependency Dominance Index

判断关键行为是不是主要由上游系统决定。

用于识别 upstream shadow trap。

## 5.8 Narrative-Evidence Tension

`叙事流畅度高，但引用证据离散/薄弱/非核心`

这是识别假 WHY 最直接的 signal。

## 5.9 Skill First-Success Gap

`下载量高，但首跑成功率低`

用于识别 skill demo trap。

## 5.10 Assumption Opacity Score

workflow 是否严重依赖未显式写出的权限和环境前提。

用于识别 over-permission trap。

---

## 6. 对 Doramagic 管线的直接建议

如果只选三件最值得做的事，我建议是：

## 6.1 在 Stage 1 前新增“WHY 可恢复性判断”

不要默认每个项目都值得产出 WHY narrative。  
先判断：

- 是否存在足够 rationale evidence
- 是否存在显著时间冲突
- 是否存在高 prior contamination risk

如果不满足，就允许输出：

`WHY cannot be reliably reconstructed from public evidence`

这比编造一个漂亮 WHY 强得多。

## 6.2 在 Stage 3 对 community rule 增加“适用域约束”

所有社区规则默认都不是全局 truth，必须显式携带：

- version
- environment
- persona
- exception or normal path
- source confidence

不带这些字段，不允许提升为高严重度规则。

## 6.3 在 Stage 3.5 增加“暗雷审查”

当前 Stage 3.5 已有证据锚点验证，但还不够。  
还需要加一层 deception checks：

- rationale support check
- temporal conflict check
- support-desk dominance check
- exception dominance check
- persona divergence check
- dependency dominance check

也就是从“有没有证据”升级到“这些证据是不是在骗你”。

---

## 7. 最后的结论

如果把整份报告压成一句话，我的答案是：

> **Doramagic 最该防的，不是低质量 source，而是“表面高质量、但公开痕迹不足以支撑正确知识恢复”的 source。**

这些 source 的共同特征不是坏，而是：

- 足够好，能通过前置筛选
- 足够复杂，能诱导 LLM 补完
- 足够活跃，能制造社区智慧假象
- 足够一致，能把错误包装成体系

因此，对 Doramagic 来说，真正的质量控制不只是判断“source 好不好”，而是判断：

## **“这个 source 会不会系统性诱导我们产出漂亮但错的知识。”**

这就是 Deceptive Source Detection 的意义。

---

## 8. 参考资料

### 本地上下文

- [INDEX.md](/Users/tang/Documents/vibecoding/Doramagic/INDEX.md)
- [PRODUCT_MANUAL.md](/Users/tang/Documents/vibecoding/Doramagic/docs/PRODUCT_MANUAL.md)
- [20260309_unsaid_knowledge_extraction_research.md](/Users/tang/Documents/vibecoding/Doramagic/docs/research/20260309_unsaid_knowledge_extraction_research.md)

### 外部资料

- Kalliamvakou et al. *The promises and perils of mining GitHub*. MSR 2014.  
  https://dl.acm.org/doi/10.1145/2597073.2597074

- SEI. *Architectural Knowledge Vaporization*.  
  https://www.sei.cmu.edu/library/architectural-knowledge-vaporization/

- Wang et al. *Astute RAG: Overcoming Imperfect Retrieval Augmentation and Knowledge Conflicts for Large Language Models*. ACL 2025.  
  https://aclanthology.org/2025.acl-long.1476/

- GitHub Docs. *Discussions*.  
  https://docs.github.com/en/discussions

- GitHub Docs. *About single select fields* / outdated items visibility behavior.  
  https://docs.github.com/en/issues/planning-and-tracking-with-projects/understanding-fields/about-single-select-fields?apiVersion=2022-11-28

- Garousi et al. *Use of Grey Literature in Software Engineering Research: A Systematic Literature Review*.  
  https://www.sciencedirect.com/science/article/abs/pii/S0950584921000904

- OpenClaw / ClawHub User Guide.  
  https://openclaw.notion.site/ClawHub-User-Guide-2484959f1a7b80d8a89acdb3ebf4e67f

## 9. 证据与推断边界

下面这些是外部资料直接支持的：

- GitHub 事件流和讨论表面不能直接等同于完整开发事实
- 架构 rationale 容易蒸发，公开材料常不足以恢复完整 WHY
- retrieval conflict 与不完整检索会导致高置信错误整合
- 讨论内容会被治理、标记、锁定、隐藏
- 灰色文献价值高但质量标准不稳定、上下文缺失严重
- 第三方 Skill 天然存在 untrusted code 风险

下面这些是本报告的综合推断：

- “经典名项目先验污染陷阱”应被当作独立风险模型
- Support Desk Trap 与 Exception Bias Trap 会系统性污染 UNSAID 提取
- Doramagic 应新增 `WHY recoverability` 与 `Deceptive Source Detection` 两层机制
- `Narrative-Evidence Tension` 是识别假 WHY 的高价值指标

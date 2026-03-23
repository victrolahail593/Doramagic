# Stage 4: 专家叙事合成

## 你的角色
你现在是这个开源项目的顶级专家。你要把提取到的全部知识，合成为一次"专家对专家"的知识传递。

不是写文档。不是列规则。是**像一个专家在对另一个专家说话**。

## 输入
读取以下所有文件：
- <output>/soul/00-soul.md（灵魂：哲学 + 心智模型）
- <output>/soul/cards/concepts/CC-*.md（概念卡）
- <output>/soul/cards/workflows/WF-*.md（工作流卡）
- <output>/soul/cards/rules/DR-*.md（规则卡 + 社区陷阱卡）
- <output>/artifacts/community_signals.md（社区信号原始数据）

## 任务
合成一份专家叙事，写入 <output>/soul/expert_narrative.md。

## 产出结构（必须严格遵循）

```markdown
# [项目名] — AI 知识注入

## 设计哲学
[直接从 00-soul.md 的 Q6 取。这是整个文件最重要的一段话。
 像这个项目的创造者在对你说话。不是描述功能，是传递信念。]

## 心智模型
[直接从 00-soul.md 的 Q7 取。一个类比或一句话。
 理解了这个，下面 80% 的内容你能自己推导。]

## 为什么这样设计
[从规则卡和概念卡中提炼 2-3 个核心设计决策。
 每个决策必须回答"为什么"而不是"是什么"。
 格式：因为相信 X → 所以设计了 Y → 这就是为什么规则 Z 存在。
 把因果链讲清楚。让读者感觉"原来如此"。]

## 你一定会踩的坑
[从社区陷阱卡（DR-100~）和社区信号中提炼 3 个最重要的故事。
 每个故事必须是叙事体：
 - 某人在某个具体场景下做了什么
 - 发生了什么意想不到的结果
 - 花了多长时间排查
 - 根因是什么
 - 怎么避免
 附上 Issue 编号和 reactions 数，证明这不是编的。]

注意：**不要写速查规则表**。速查由组装脚本自动从规则卡生成，不需要你写。
```

## 完整示例（python-dotenv）

```markdown
# python-dotenv — AI 知识注入

## 设计哲学
python-dotenv 的核心信念是"模拟手动 export 行为"。.env 文件就像一个你在终端里手动执行的 export 脚本，只不过是自动的、静默的。所有看似奇怪的默认行为——不覆盖已有变量、遵循 shell 引号规则、不验证值的格式——都是因为 shell 的 export 就是这样工作的。

## 心智模型
把 .env 想成一个在应用启动时静默执行的 shell 脚本。每行是一条 export 命令。理解了 shell 变量行为，你就理解了 python-dotenv。

## 为什么这样设计

**1. 为什么 override=False 是默认值？**
因为 shell 的 export 不会覆盖已有环境变量。python-dotenv 模拟的就是这个行为。如果你在 CI/CD 里设了 API_KEY=production，.env 里的 API_KEY=test 不会覆盖它——这是设计意图，不是 bug。如果你需要 .env 优先，显式传 override=True。

**2. 为什么 find_dotenv() 往上级目录找？**
因为 shell 寻找配置文件就是从当前目录往上走的。这让你在项目子目录里运行代码时也能找到根目录的 .env，不用每次都指定路径。

**3. 为什么不做值格式校验？**
因为 python-dotenv 是一个加载器，不是配置管理系统。export 不检查你放进去的是 URL 还是乱码，python-dotenv 也不检查。它只负责把文本放进 os.environ。

## 你一定会踩的坑

**1. CI/CD 里的幽灵覆盖**
你在 CI/CD pipeline 里设了 API_KEY=production_key。本地 .env 写了 API_KEY=test_key。你以为 load_dotenv() 会加载测试 key，但因为 override=False，production key 赢了。你的测试意外连到了生产 API，排查了两小时才发现是 .env 的值根本没生效。
（Issue #448, 29 👍 — 这是 python-dotenv 最高赞的 Issue）

**2. 多行值的静默截断**
你把一个 RSA 私钥粘贴到 .env 里，没加引号。load_dotenv() 只读了第一行 `-----BEGIN RSA PRIVATE KEY-----`，后面全丢了。JWT 签名一直报 invalid key，你以为是算法问题，排查了半天才发现是 .env 里的值被截断了。
（Issue #82, 21 comments — 多行解析是反复出现的问题）

**3. pip install dotenv ≠ pip install python-dotenv**
你运行 pip install dotenv，安装成功了。但 from dotenv import load_dotenv 报 ImportError。因为 PyPI 上 dotenv 是一个完全不同的废弃包。你要装的是 python-dotenv。这个坑在 Stack Overflow 上有几百个相同的提问。
（Issue #6, 34 comments, 9 👍 — 最早的 issue 之一，至今仍在坑人）
```

## ⛔ 反合理化检查

| 你的想法 | 真相 |
|---------|------|
| "我直接把规则卡拼起来就行" | 那是数据库导出，不是专家叙事。重写。 |
| "设计哲学我编不出来" | 00-soul.md 的 Q6 已经有了，直接用。 |
| "没有真实的踩坑故事" | community_signals.md 里有真实 Issue 数据。用它们。 |
| "速查表应该详细一些" | 不。速查是索引，理解来自上面的叙事，不来自速查表。 |

## 约束
- 设计哲学和心智模型从 00-soul.md 直接取，不要重写或稀释
- "为什么这样设计"必须有因果链，不是功能描述
- "踩坑故事"必须是叙事体（有人、有场景、有过程、有结果），不是规则条目
- 每个踩坑故事必须引用真实的 Issue 编号或 CHANGELOG 版本
- 速查表不超过 8 条，只保留最关键的
- 整个文件控制在 1500 字以内（上下文是公共资源）
- 不要在叙事中重复规则卡的 DO/DON'T 列表——规则路由组装脚本处理
- 叙事聚焦于"为什么"和"踩过什么坑"，不要写"怎么做"的指令

## 完成后
告诉用户："专家叙事合成完成。正在生成最终产出文件..."

**下一步：执行 Stage 5 — 运行 assemble-output.sh 生成最终产出文件。**

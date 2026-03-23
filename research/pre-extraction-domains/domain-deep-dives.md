# Doramagic 核心领域深度提取蓝图 (Part 2: 认知与护城河层)

**角色**：产品/市场分析师
**日期**：2026-03-18
**覆盖领域**：Top 3 (内容去噪), Top 4 (PKM 归档), Top 5 (电子遗产)

---

## Top 3: 内容去噪与策展 (Anti-AI Curation)
**核心命题**：在 AI 垃圾生成的时代，如何定义和提取“人类品味”？

### 1. 竞品缺口分析 (Skill Gap)
*   **现有 Skill**：`fetch-rss-feed`, `summarize-article`
*   **Doramagic 增量**：不仅是抓取，而是**“判别”**。提取出“为什么这篇文章是高价值的”隐性特征。解决“抓取了一堆垃圾并用 AI 总结了一堆垃圾”的模糊烦恼。

### 2. 知识锚点 (Knowledge Anchors)
*   **正则表达式与启发式过滤**：扫描 `FreshRSS` 和 `Miniflux` 的社区共享过滤规则。提取对特定关键词（如“本文由 AI 生成”、“点击领红包”）或特定 HTML 结构（如密集的 Affiliate 链接块）的正则匹配共识。
*   **阅读模式的降级哲学**：提取 `Readability.js` (Mozilla) 或 `Wallabag` 的核心逻辑。当面对复杂的单页应用 (SPA) 或动态加载的 Paywall 时，它们如何决定保留哪些 `<div>`，抛弃哪些 `<iframe>`？这背后是对“什么是正文”的审美共识。
*   **行为特征分析**：扫描 `NewsBlur` 的 Intelligence Classifier 代码，提取它如何根据用户“跳过”、“点赞”或“快速滚动”行为来构建贝叶斯概率模型。

---

## Top 4: PKM 语义归档与清理 (Knowledge Maintenance)
**核心命题**：从“全文检索”向“本地知识图谱”的进化。

### 1. 竞品缺口分析 (Skill Gap)
*   **现有 Skill**：`append-to-notion`, `search-obsidian-vault`
*   **Doramagic 增量**：不仅是搜索，而是**“自动编织”**。提取“孤立笔记”之间可能存在关联的推断逻辑，解决“写了就忘，找不到连接点”的终极烦恼。

### 2. 知识锚点 (Knowledge Anchors)
*   **原子化关联规则**：扫描 `Logseq` 和 `Obsidian` 插件生态（如 Dataview, Smart Connections）。重点提取对于标签（Tags）、双向链接（Backlinks）和属性（Frontmatter）的命名共识与最佳实践。
*   **跨领域实体解析**：提取 `Zotero Translators` 的代码逻辑。这些代码包含了如何从数万个不同网站（论文、新闻、博客）中准确抽取出统一的实体元数据（作者、日期、DOI）的硬核经验。
*   **图谱防腐 (Anti-Data-Rot)**：扫描 `Anytype` 或类似 Local-first 项目关于如何处理“死链”、“合并冲突”和“孤儿节点 (Orphan nodes)”的底层巡检脚本。

---

## Top 5: 电子遗产与数字存档 (Digital Legacy)
**核心命题**：为未来 50 年的数据可靠性建立 AI “守陵人”机制。

### 1. 竞品缺口分析 (Skill Gap)
*   **现有 Skill**：`backup-to-s3`, `zip-folder`
*   **Doramagic 增量**：不仅是备份，而是**“校验与格式迁移”**。解决“云盘破产了怎么办”、“三十年后 JPEG 打不开了怎么办”的深层焦虑。这是建立平台绝对信任感的杀手锏。

### 2. 知识锚点 (Knowledge Anchors)
*   **内容寻址设计**：扫描 `Perkeep (Camlistore)`。提取其“不依赖文件路径，仅依赖内容 Hash”的存储哲学代码。这是实现数据永生（Data Immortality）的基础。
*   **法证级数据保留**：提取 `BitCurator` 中的工作流。关注它在读取陈旧磁盘镜像或归档社交媒体时，如何无损保留原始元数据（EXIF, 创建时间戳）。
*   **静默损坏 (Bit-rot) 预防**：扫描 `Restic` 或 `ZFS` 相关工具生态，提取定期执行 `scrub`（数据清洗与校验）的频率策略及错误自动修复的决策树。

---

## 总结：Doramagic 的三层能力架构

通过这 5 个领域的预提取，Doramagic 实际上为 OpenClaw 赋予了三层不同维度的智能：

1.  **基础设施层 (Top 1 HomeLab + Top 2 Health)**: 让 Agent 懂机器的脾气、懂硬件的数据。这是**基础生存能力**。
2.  **认知过滤层 (Top 3 Curation + Top 4 PKM)**: 让 Agent 有品味、懂整理。这是**数字脑助理**的核心价值。
3.  **长期信赖层 (Top 5 Legacy)**: 让 Agent 成为可以托付终身数据的管家。这是**品牌护城河**。

*（完）*

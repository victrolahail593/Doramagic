# 跨项目智能研究 — 三方开放研究

## 背景

Doramagic 是一个从开源项目中提取"灵魂"（知识、设计哲学、社区智慧）的工具。原本设计为单项目提取。

## 实验发现

我们用 Doramagic 对 4 个同领域（SEO/GEO for Claude Code）的开源项目做了灵魂提取，**意外发现了两个全新的产品价值**：

### 实验对象

| 项目 | Stars | Commits | 语言 | 本质 |
|------|-------|---------|------|------|
| geo-seo-claude | 2.5k | 9 | Python | GEO 优化 skill |
| marketingskills | 13.5k | 165 | Markdown | 33 个营销 skill 集合 |
| claude-seo | 2.3k | 48 | Python/Shell | 通用 SEO skill |
| 30x-seo | 11 | 25 | Python | SEO 自动化 skill |

### 提取结果关键发现

**发现 1：claude-seo ≈ 30x-seo（疑似 fork/套壳）**
- 相同的 6-7 个子代理架构
- 相同的 Python 脚本（fetch_page.py, parse_html.py, analyze_visual.py, capture_screenshot.py）
- 相同的 hooks 设计（validate-schema.py + pre-commit-seo-check.sh）
- 连 CHANGELOG 中修复的 bug 都一样（YAML frontmatter 前有 HTML 注释导致解析失败）
- 但 Stars 差异巨大：2.3k vs 11

**发现 2：4 个项目共享大量 SEO 领域知识**
- FAQPage schema 2023 年 8 月限制（4/4 项目都提到）
- HowTo schema 废弃（3/4）
- AI 爬虫不执行 JS → CSR 页面不可见（3/4）
- 134-167 词是 AI 引用最优段落长度（3/4）
- YouTube 品牌提及相关性 0.737 > 反向链接 0.266（3/4）

**发现 3：每个项目也有独创知识**
- marketingskills：product-marketing-context 共享底板设计（独创）
- geo-seo-claude：citability scoring 引擎 + Brand Surface Area 概念（独创）
- claude-seo / 30x-seo：hooks 自动拦截废弃 schema（独创但两者共享）

### 由此推导出的两个新价值主张

**价值 1："最大公约数"能力**
> 用户给 Doramagic 一堆同领域项目 → Doramagic 从中提取"共识知识"（被多个独立项目交叉验证的知识）

这本质上是"积木"概念的用户端表达：公约数 = 领域级积木。

**价值 2："项目打架"能力**
> 用户找到 N 个做同一件事的项目，不知道该用哪个 → Doramagic 通过灵魂对比判断谁是原创、谁是套壳、谁有独创价值

这本质上是暗雷检测 + 好作业评判的具体应用场景。

**完整链路**：
```
N 个项目 → 打架去重 → M 个独立项目 → 求公约数 → 领域共识知识
                                    → 求差异 → 各项目独创知识
```

## 研究问题（开放式）

以下问题作为起点，但不限于此。鼓励发散性思考，提出我们没想到的角度。

1. **"最大公约数"能力的深层含义是什么？**
   - 这和传统的代码重复检测（如 MOSS、JPlag）有什么本质区别？
   - "知识层面的公约数"与"代码层面的公约数"有何不同？
   - 公约数知识的可信度是否天然高于单项目知识？为什么？
   - 有没有"假公约数"的风险（比如所有项目都引用了同一个错误来源）？

2. **"项目打架"能力的边界在哪里？**
   - Fork、致敬、独立趋同（convergent evolution）、共同上游依赖——如何区分？
   - Stars / Commits / 创建时间这些元数据应该参与判断吗？
   - 灵魂提取能否判断"谁先有这个想法"？
   - 这个能力对用户的实际决策场景有哪些？（选技术栈？评估项目质量？投资判断？）

3. **这两个能力如何改变 Doramagic 的产品定位？**
   - 从"单项目知识提取器"到"多项目知识图谱"——这是渐进演化还是范式转变？
   - 是否存在一个"知识 diff"的概念——类似 git diff，但 diff 的是两个项目的灵魂？
   - 多项目对比能力应该是核心功能还是高级功能？
   - 这是否改变了 Doramagic 的竞争壁垒？

4. **工程实现的关键挑战是什么？**
   - 如何定义"知识指纹"使其可比较？
   - 公约数提取的算法框架是什么？
   - 如何处理不同粒度的知识对比（设计哲学级 vs 具体规则级）？
   - 性能问题：N 个项目的两两对比是 O(N²)，如何优化？

5. **你还看到了什么我们没看到的？**
   - 这个发现是否暗示了更大的可能性？
   - 有没有现有的学术研究、产品或方法论可以参考？
   - 这个能力在其他领域（非软件）有类比吗？

## 研究输出要求

- 不限格式，鼓励发散
- 如果有具体的产品设计建议或算法框架，请详细展开
- 如果发现了我们的盲区，请直接指出
- 字数不限，但质量优先于数量

## 附录：四个项目的灵魂提取结果

提取文件位置：
- `/Users/tang/Documents/vibecoding/Doramagic/experiments/exp-seo-skills/geo-seo-claude/CLAUDE.md`
- `/Users/tang/Documents/vibecoding/Doramagic/experiments/exp-seo-skills/marketingskills/CLAUDE.md`
- `/Users/tang/Documents/vibecoding/Doramagic/experiments/exp-seo-skills/claude-seo/CLAUDE.md`
- `/Users/tang/Documents/vibecoding/Doramagic/experiments/exp-seo-skills/30x-seo/CLAUDE.md`

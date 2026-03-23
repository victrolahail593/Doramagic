# Codex 研究任务：社区信号采集的工程最佳实践

## 背景

我们在构建一个叫 Soul Extractor 的 AI 技能（Skill），它从 GitHub 开源项目中提取结构化知识，生成 .cursorrules / CLAUDE.md 文件作为 "AI 燃料"，注入给 Cursor 或 Claude Code 使用。

### 当前架构

Soul Extractor 分 4 个阶段执行：

- **Stage 0 (prepare-repo.sh)**：克隆仓库 → 用 Repomix 打包源码为 XML → 【新增】采集社区信号
- **Stage 1 (STAGE-1-essence.md)**：提取项目本质（解决什么问题、核心承诺）
- **Stage 2 (STAGE-2-concepts.md)**：提取 3 概念卡 + 3 工作流卡
- **Stage 3 (STAGE-3-rules.md)**：提取规则卡（代码规则 DR-001~ + 社区陷阱 DR-100~）
- **Stage 4 (assemble-output.sh)**：组装最终产出（.cursorrules, CLAUDE.md, project_soul.md）

### 我们遇到的问题

在 v0.5 测试中，Stage 3 产出了 10 张规则卡（DR-001~010），质量不错，但**全部来自源码静态分析**。设计中要求的 "社区陷阱"（DR-100~）一张都没有产出。

根因分析：
1. 模型只读到了 packed_compressed.xml（源码），**没有任何社区数据输入**
2. 即使 STAGE-3 提到了"社区陷阱"这个类别，模型没有数据来源就无法产出
3. 社区陷阱的价值恰恰在于**真实世界的痛苦经验**——GitHub Issues 里反复被报告的 bug、CHANGELOG 里的 breaking changes、Stack Overflow 上高票的 gotcha——这些是纯代码分析无法发现的

### 我们的初步方案

在 prepare-repo.sh 中新增社区信号采集，生成 `community_signals.md`，包含三部分：

1. **CHANGELOG 提取**：grep breaking/deprecat/remov/renam 等关键词，带上下文
2. **README FAQ 提取**：sed 提取 FAQ/Troubleshooting/Gotcha 等章节
3. **GitHub Issues 采集**：通过 GitHub API 拉取按 reactions 排序的 Top 30 issue，包含标题、标签、状态、body 前 500 字

当前实现的脚本如下（已写入 prepare-repo.sh）：

```bash
# --- Collect community signals ---
COMMUNITY="$OUTPUT_DIR/artifacts/community_signals.md"
if [ ! -f "$COMMUNITY" ]; then
    echo "=== Collecting community signals ==="
    echo "# Community Signals for $REPO_NAME" > "$COMMUNITY"

    # 1. CHANGELOG breaking changes
    grep -i -B1 -A3 'break|deprecat|remov|renam|drop|migration|upgrade|incompatible' "$CHANGELOG_FILE" | head -200 >> "$COMMUNITY"

    # 2. README FAQ sections
    sed -n '/^#.*\(FAQ\|Troubleshoot\|Common\|Gotcha\)/I,/^# [^#]/p' "$README_FILE" | head -150 >> "$COMMUNITY"

    # 3. GitHub Issues top 30 by reactions
    curl -sL "https://api.github.com/repos/$GH_SLUG/issues?state=all&sort=reactions&direction=desc&per_page=30" | python3 -c "
import json, sys
issues = json.load(sys.stdin)
for i in issues[:30]:
    thumbs = i.get('reactions', {}).get('+1', 0)
    labels = ', '.join(l['name'] for l in i.get('labels', []))
    title = i.get('title', '')
    number = i.get('number', '')
    body = (i.get('body') or '')[:500]
    print(f'### [{thumbs} 👍] #{number}: {title}')
    print(f'Labels: {labels}')
    print(body[:500])
    print()
" >> "$COMMUNITY"
fi
```

## 研究目标

请你从**工程实现**角度，深入研究以下问题，并撰写一份详细报告。

### 问题 1：GitHub API 采集策略优化

当前方案只用了 `/repos/{owner}/{repo}/issues` 一个端点，按 reactions 排序。请研究：

- **是否应该同时拉取 issue comments？** 很多有价值的信息在评论中（workaround、root cause 分析），而不是 issue body。如果要拉取，如何控制数据量？
- **是否应该拉取 Discussions？** 很多项目把 Q&A 放在 GitHub Discussions 而非 Issues。端点是什么？数据结构和 Issues 有何不同？
- **是否应该区分 issue 类型？** 比如 bug vs feature request vs question，对于"社区陷阱"卡，bug 和 question 的价值远高于 feature request
- **API rate limit 问题**：未认证请求每小时 60 次，认证后 5000 次。我们的脚本在用户机器上运行（OpenClaw 平台），用户可能没有 `gh` CLI 登录态。如何优雅处理限流？是否需要缓存？
- **GitHub API 在中国大陆的可达性**：api.github.com 是否会被墙？是否需要像仓库克隆一样提供镜像 fallback？

### 问题 2：CHANGELOG 解析的鲁棒性

当前用 grep 关键词匹配，比较粗糙。请研究：

- **不同项目的 CHANGELOG 格式差异有多大？** 比如 Keep a Changelog 格式、Conventional Commits、自由格式。我们的 grep 策略能覆盖多少？
- **如何提取版本号与 breaking change 的关联？** 用户最需要知道 "从 v0.x 升到 v1.x 哪些东西变了"，而不是零散的关键词匹配行
- **是否应该直接把完整 CHANGELOG 传给模型？** 而不是预过滤。让模型自己判断哪些是 breaking change。如果 CHANGELOG 太大（>100KB），如何截断？

### 问题 3：额外的社区信号来源

除了 GitHub Issues 和 CHANGELOG，还有哪些有价值的社区信号来源？请逐一评估可行性：

- **Stack Overflow**：能否通过 API 搜索项目相关问题？高票回答的 gotcha 信息价值很高。是否有 API？是否需要 API key？
- **PyPI / npm 下载统计**：是否能反映项目的成熟度和使用场景？
- **GitHub Stars / Forks 趋势**：是否有信息价值？
- **git log 的 commit message 分析**：fix: 开头的 commit message 可能暗示高频 bug
- **安全公告 (Security Advisories)**：GitHub 有专门的安全公告 API，是否值得采集？
- **其他你认为有价值的来源**

### 问题 4：community_signals.md 的信息架构

当前我们把所有信号平铺在一个 markdown 文件里，直接丢给模型。请研究：

- **信息结构化 vs 自然语言**：应该用结构化格式（YAML/JSON）还是自然语言 markdown？考虑到下游消费者是 MiniMax-M2.5 这样的弱模型
- **信号的权重/优先级**：是否应该在文件里标注信号的重要程度？比如 29👍 的 issue 和 1👍 的 issue 价值差异很大
- **信息量控制**：community_signals.md 不应该太大（会占用模型上下文），最终文件应该控制在多大？有没有最佳实践？
- **去重和去噪**：GitHub Issues 中大量 issue 是重复的、无关的、或已过期的。是否需要预处理去重？怎么做？

### 问题 5：非 GitHub 项目的支持

Soul Extractor 目前假设输入是 GitHub URL。如果用户传入 GitLab、Gitee、Bitbucket URL，怎么办？

- 各平台的 API 差异有多大？
- 是否值得现在就支持？还是先只做 GitHub？
- 如果只做 GitHub，遇到非 GitHub URL 时应该怎么降级？

## 产出要求

请撰写一份详细的技术报告，包含：

1. **每个问题的研究结论**，附具体的 API 端点、参数、返回数据示例
2. **推荐方案**：如果你是工程师，你会怎么实现？给出具体的代码片段或伪代码
3. **优先级排序**：哪些改进应该先做（ROI 最高），哪些可以延后
4. **风险和注意事项**：每个方案可能遇到的坑

报告文件名：`20260309_codex_community_signals_report.md`
报告放置路径：与本任务文件同目录

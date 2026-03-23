# 社区信号采集的工程最佳实践研究报告（Codex）

> 日期：2026-03-09  
> 任务文件：`20260309_codex_community_signals_task.md`

## 执行摘要

### 核心结论

1. **当前脚本里的 GitHub Issues 排序策略有明显问题。** 你们现在调用的是：
   `GET /repos/{owner}/{repo}/issues?sort=reactions&direction=desc&per_page=30`。  
   但 GitHub 官方的 “List repository issues” 文档只列出 `created`、`updated`、`comments` 作为合法 `sort` 值，没有 `reactions`。因此这段实现不能作为可靠的“按点赞排序”方案。  
   置信度：**高**

2. **社区陷阱不应只靠 issue body；但也不应无脑抓全量 comments。** 最稳妥的方案是：
   - 先抓一批候选 issues/discussions
   - 本地排序与过滤
   - 只对前 N 个候选补抓少量高信号 comments / answers
   置信度：**高**

3. **GitHub Discussions 值得支持，但应作为“有 token 时开启”的增强项。** GitHub 官方 Discussions API 在 GraphQL 中可用，适合抓 Q&A、已回答讨论、最佳实践，但会显著增加实现复杂度，而且认证要求更现实。  
   置信度：**中高**

4. **`community_signals.md` 不应该是纯自由文本，也不应该是纯 JSON。** 对 MiniMax-M2.5 这类弱模型，更推荐“**结构化 Markdown + 紧凑 YAML 元数据 + 每条 1 段摘要**”的混合格式。  
   置信度：**高**

5. **短期只建议正式支持 GitHub。** GitLab 其次；Bitbucket 的 issue comment API 已出现 deprecation 信号；Gitee 的官方 API 文档在本次调研中未能通过稳定的一手资料完整验证。产品上应先把 GitHub 路径做深做稳。  
   置信度：**中高**

### 推荐落地顺序

**P0（立刻做）**
- 修掉 `sort=reactions` 假设，改为“抓候选 + 本地打分”
- 加 `GITHUB_TOKEN` 可选认证、ETag 缓存、超时与 graceful fallback
- 增加 Security Advisories 采集
- 重构 `community_signals.md` 为结构化 Markdown

**P1（1–2 天）**
- 对 Top issues 补抓少量 issue comments
- 增加 `git log` 修复类 commit 信号
- 把 CHANGELOG 解析升级为“按版本块提取”而不是 grep 行

**P2（1–2 周）**
- 增加 GitHub Discussions（GraphQL）
- 增加 Stack Overflow 信号
- 视需求再评估 GitLab 支持

---

## 一、研究范围与方法

本报告覆盖 5 个问题：

1. GitHub API 采集策略优化
2. CHANGELOG 解析鲁棒性
3. 额外社区信号来源
4. `community_signals.md` 信息架构
5. 非 GitHub 项目支持策略

研究方法：
- 阅读当前 `prepare-repo.sh` 的实现
- 查阅 GitHub、GitLab、Bitbucket、Stack Exchange、PyPI、Keep a Changelog 等官方文档
- 结合 Soul Extractor 当前链路（弱模型、Stage 3 规则卡、上下文预算）给出工程建议

---

## 二、对当前实现的直接评估

当前脚本位于：
`/Users/tang/Documents/vibecoding/allinone/skills/soul-extractor/scripts/prepare-repo.sh`

### 现状优点

- 已把社区信号前移到 Stage 0，方向是对的
- 已兼顾本地静态来源（CHANGELOG / README）和远端来源（GitHub Issues）
- 已把产物落成单独文件，便于 Stage 3 读取

### 现状问题

1. **`sort=reactions` 不可靠**
   - GitHub `List repository issues` 官方文档未列出 `reactions` 作为可用排序项
   - 这意味着“按 reactions 排序”的产品意图，没有被 API 正式承诺

2. **Issues 没有过滤 PR**
   - GitHub 的 issues 列表接口会混入 pull requests，需要通过响应中的 `pull_request` 字段过滤

3. **对 comments / discussions 完全没覆盖**
   - 很多真实 workaround、maintainer root cause、最终修复建议都在评论区
   - Q&A 型项目经常把知识放在 Discussions，而不是 Issues

4. **没有认证、缓存、限流设计**
   - 当前是 best-effort `curl`
   - 用户机器上若没有 `gh` 登录态，GitHub REST 限额很快会成为隐患

5. **Markdown 是平铺拼接，后续难排序、去重、裁剪**
   - 现在的文件格式不利于后续 Stage 3 只读“最高价值信号”

---

## 三、问题 1：GitHub API 采集策略优化

## 3.1 先纠正一个关键实现误区

### 结论

**不建议继续依赖 `/repos/{owner}/{repo}/issues?sort=reactions`。**

### 依据

GitHub 官方 “List repository issues” 文档中，`sort` 参数支持的是：
- `created`
- `updated`
- `comments`

没有 `reactions`。

### 工程建议

改成两段式：

1. **抓候选 issue 集合**
2. **本地打分排序**

推荐候选接口：

```http
GET /repos/{owner}/{repo}/issues?state=all&sort=comments&direction=desc&per_page=50&page=1
Accept: application/vnd.github+json
X-GitHub-Api-Version: 2022-11-28
```

### 为什么选 `sort=comments`

- comments 是“社区反复讨论”的代理指标
- 它比 `updated` 更接近“真实痛点热度”
- 且是官方支持排序项

### 本地打分建议

```text
score = source_weight
      + label_weight
      + log(1 + comments_count)
      + reaction_bonus
      + resolution_bonus
      + recency_bonus
      - feature_request_penalty
```

推荐权重：

- `bug` / `question` / `support` 标签：`+2`
- `enhancement` / `feature` / `proposal`：`-2`
- `closed` 且 close 后未反复 reopen：`+1`
- 最近 18 个月活跃：`+1`
- 有 maintainer 参与：`+1`
- Security advisory 关联：`+3`

> 注：如果后续需要 reaction 信息，可对前 10 个 issue 再调用 reactions 相关接口或从响应中的 reaction summary 字段补分；但不应把它作为第一阶段排序的硬依赖。

置信度：**高**

---

## 3.2 是否应该拉取 issue comments？

### 结论

**应该，但只拉 Top issue 的少量 comments。不要全量抓。**

### 原因

有价值的信息常出现在：
- maintainer 给出的 workaround
- 用户补充的复现条件
- 关闭前的最终解释
- 升级路径 / 配置差异说明

而这些往往不在 issue body 里。

### 推荐策略

#### 阶段一：先选候选 issues

- 先抓 `50` 个 issue 候选
- 本地过滤掉 PR、feature request、噪声标签
- 取 Top `8–12` 个 issue

#### 阶段二：只对 Top issue 抓评论

接口：

```http
GET /repos/{owner}/{repo}/issues/{issue_number}/comments?sort=updated&direction=desc&per_page=3
Accept: application/vnd.github+json
X-GitHub-Api-Version: 2022-11-28
```

或仓库级接口（不推荐直接用于最终提取，只适合增量扫描）：

```http
GET /repos/{owner}/{repo}/issues/comments?sort=updated&direction=desc&since=2025-01-01T00:00:00Z&per_page=100
```

### 为什么 `per_page=3`

- Stage 0 目标不是“完整归档讨论”，而是“给 Stage 3 提供高信号样本”
- 每个 issue 抓 3 条，10 个 issue 也只是 30 条评论，体量可控
- comments 太多会稀释真正重要的 maintainer 结论

### 推荐过滤规则

优先保留：
- `author_association` 为 `MEMBER` / `OWNER` / `COLLABORATOR`
- 包含关键词：`workaround`, `fix`, `root cause`, `expected`, `breaking`, `regression`
- issue 关闭前后 7 天内的评论

### 示例返回字段（关心的字段）

```json
{
  "id": 1,
  "user": {"login": "maintainer"},
  "author_association": "MEMBER",
  "created_at": "2026-03-01T10:00:00Z",
  "updated_at": "2026-03-01T12:00:00Z",
  "body": "Workaround: call load_dotenv with override=True ..."
}
```

置信度：**高**

### 风险

- comment 接口不支持按 reaction/votes 排序，只支持 `created` / `updated`
- 仍需要你们自己在本地做“高信号评论选择”

---

## 3.3 是否应该拉 GitHub Discussions？

### 结论

**值得做，但建议作为“有 `GITHUB_TOKEN` 时开启”的增强项，而不是 P0 必做项。**

### 原因

Discussions 更适合捕捉：
- Q&A
- 使用最佳实践
- 迁移经验
- 常见误解
- 维护者对“这不是 bug，而是设计如此”的解释

这些非常适合生成 “社区陷阱” 卡。

### 官方接口形态

GitHub Discussions 在官方文档里主要通过 **GraphQL** 暴露。关键对象包含：
- `repository.discussions`
- `discussion.comments`
- `discussionComment.replies`
- `isAnswered`
- `answerChosenAt`
- `category`

### 推荐查询方向

```graphql
query($owner: String!, $repo: String!, $n: Int!) {
  repository(owner: $owner, name: $repo) {
    discussions(first: $n, orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes {
        number
        title
        bodyText
        isAnswered
        upvoteCount
        createdAt
        updatedAt
        category { name }
        comments(first: 2) {
          nodes {
            bodyText
            isAnswer
            replies(first: 1) {
              nodes { bodyText }
            }
          }
        }
      }
    }
  }
}
```

### 推荐采样规则

- 只抓 `Q&A` / `Help` / `General` 等类别
- 优先 `isAnswered = true`
- 只取 `first: 5–10` 个 discussions
- 每个 discussion 只保留：标题、摘要、已采纳回答 / 前 2 条高信号评论

### 为什么不建议 P0 就上

- GraphQL 实现与错误处理比 REST 明显复杂
- 认证约束更现实
- 你们眼下先把 GitHub issue + security + changelog 路径打稳，ROI 更高

置信度：**中高**

### 风险

- 不是所有仓库都启用 Discussions
- category 命名不统一
- 无 token 时成功率与可控性下降

---

## 3.4 是否应该区分 issue 类型？

### 结论

**应该，而且要在 Stage 0 明确做掉。**

### 推荐分类优先级

对“社区陷阱”价值从高到低：

1. `bug`
2. `question`
3. `support`
4. `documentation`
5. `enhancement` / `feature request`
6. `discussion/proposal`

### 为什么

- `bug`：暴露真实失效模式
- `question/support`：暴露用户最常卡住的理解鸿沟
- `enhancement/feature request`：更多反映产品诉求，不一定是“坑”

### GitHub 实现建议

优先使用两层策略：

1. **标签判断**：`bug`, `question`, `support`, `enhancement`, `feature`
2. **issue type / 文本兜底**：
   - 官方 issues API 提供 `type` 过滤参数，但项目 adoption 不一
   - 因此不要把 `type` 当唯一依据

### 推荐伪代码

```python
def classify_issue(issue):
    labels = {label['name'].lower() for label in issue.get('labels', [])}
    title = (issue.get('title') or '').lower()
    body = (issue.get('body') or '').lower()

    if {'bug', 'type:bug', 'kind/bug'} & labels:
        return 'bug'
    if {'question', 'support', 'help wanted'} & labels:
        return 'question'
    if {'enhancement', 'feature', 'proposal'} & labels:
        return 'feature'
    if 'how do i' in title or 'why does' in title:
        return 'question'
    if 'error' in title or 'fails' in title or 'broken' in title:
        return 'bug'
    return 'unknown'
```

置信度：**高**

---

## 3.5 Rate limit：如何优雅处理？

### 官方约束

GitHub REST API 官方文档：
- **未认证**：主限额通常是 **每小时 60 次**
- **认证后**：通常是 **每小时 5,000 次**

### 推荐设计

#### 方案 A：默认匿名，认证增强

- 无 `GITHUB_TOKEN`：继续工作，但只抓最小集合
- 有 `GITHUB_TOKEN`：开启完整增强采集

#### 方案 B：加本地缓存（强烈推荐）

缓存键：

```text
cache/community/github/<owner>__<repo>/<endpoint_hash>.json
```

缓存元数据：

```json
{
  "url": "https://api.github.com/repos/...",
  "etag": "W/\"abc123\"",
  "fetched_at": "2026-03-09T12:00:00Z",
  "expires_at": "2026-03-10T12:00:00Z"
}
```

请求时带：

```http
If-None-Match: W/"abc123"
```

GitHub 官方文档明确建议使用条件请求（conditional requests）以减少不必要的数据传输和限额消耗。

#### 方案 C：硬性预算控制

单次任务 GitHub API 预算建议：

- `1` 次：issues 列表
- `0–10` 次：issue comments（仅 Top N）
- `0–1` 次：security advisories
- `0–1` 次：discussions（GraphQL）

目标：**匿名模式单任务不超过 12 次请求**。

### 推荐降级策略

```text
有 token      -> issues + comments + advisories + discussions
无 token      -> issues + advisories
命中 403/429  -> 仅本地信号（CHANGELOG/README/git log）
网络超时      -> 继续执行，不阻塞提取
```

置信度：**高**

### 风险

- GitHub secondary rate limit 可能在高并发下提前触发
- 同机多任务并发会放大匿名额度风险

---

## 3.6 GitHub API 在中国大陆的可达性

### 结论

**不建议假设 `api.github.com` 在中国大陆永远稳定可达。工程上应视为“best effort 外部依赖”。**

### 这次调研能确认的

- GitHub 官方文档没有提供专门的中国大陆镜像 API 端点
- 也没有提供类似源码 clone 镜像那样的官方替代域名

### 因此推荐做法

1. **把 GitHub API 采集做成可失败、不阻塞主流程**
2. **所有 API 请求设置较短超时**（如 `--connect-timeout 5 --max-time 15`）
3. **支持标准代理环境变量**：`HTTPS_PROXY` / `ALL_PROXY`
4. **把失败写进 `community_signals.md` 的元信息，而不是 silent fail**

### 推荐状态写法

```yaml
remote_github:
  attempted: true
  success: false
  reason: timeout
  fallback: local_only
```

置信度：**中高**

### 局限说明

本问题缺少 GitHub 官方的中国大陆网络保证文档；因此以上判断主要基于“未见官方替代方案 + 你们产品用户环境约束 + 工程保守设计”。

---

## 四、问题 2：CHANGELOG 解析的鲁棒性

## 4.1 不同项目的 CHANGELOG 格式差异有多大？

### 结论

**差异很大，单纯 grep 关键词不够稳。**

### 主要格式族

1. **Keep a Changelog**
   - 典型分节：`Added / Changed / Deprecated / Removed / Fixed / Security`
   - 优点：结构清晰，适合抽版本块

2. **Conventional Commits / Release Notes 风格**
   - 可能以版本头 + commit 摘要组织
   - breaking changes 可能体现在 `BREAKING CHANGE:` 或 major 版本说明

3. **自由格式**
   - 手写 release notes
   - 可能完全没有统一标题或 category

### 对当前 grep 的评估

当前策略能覆盖：
- 明确写出 `breaking`, `deprecated`, `removed`, `rename`, `migration` 的项目

覆盖不了：
- 用版本块和语义描述、但不出现这些关键词的说明
- “升级到 v2 后默认行为变化”这类没有显式关键词的迁移信息
- 结构化 changelog 中的上下文边界

置信度：**高**

---

## 4.2 如何提取“版本号 ↔ breaking change”关联？

### 结论

**应该先按版本块切分，再在版本块内提取 breaking / migration / deprecation。**

### 推荐流程

#### 第一步：识别 changelog 文件

优先顺序：
- `CHANGELOG.md`
- `CHANGELOG`
- `CHANGES.md`
- `HISTORY.md`
- `RELEASES.md`

#### 第二步：按版本标题切分

建议正则：

```regex
^(#{1,3}\s*)?(\[?v?\d+\.\d+(?:\.\d+)?[^\]]*\]?)(?:\s*-\s*\d{4}-\d{2}-\d{2})?
```

兼容：
- `## [1.2.0] - 2025-01-10`
- `## v1.0.0`
- `# 2.0`

#### 第三步：对每个版本块打标签

- `breaking`
- `deprecated`
- `removed`
- `migration`
- `security`

#### 第四步：输出结构化摘要

```yaml
- version: 1.0.0
  date: 2025-01-10
  signals:
    - type: breaking
      summary: Default override behavior changed
      evidence: "Changed precedence of .env loading ..."
    - type: migration
      summary: Users must pass explicit override=True
      evidence: "Migration: set override=True to keep old behavior"
```

### 为什么这比 grep 好

- 能把“版本背景”保留下来
- 更符合用户真正关心的问题：**我从哪个版本升到哪个版本会踩坑？**

置信度：**高**

---

## 4.3 是否应该直接把完整 CHANGELOG 交给模型？

### 结论

**小文件可以；大文件不建议直接全塞。**

### 推荐阈值

- `<= 80 KB`：可以原样进入预处理，再由脚本切版本块
- `80 KB ~ 200 KB`：只保留最近 `10` 个版本块 + 含 breaking/migration 关键词的历史块
- `> 200 KB`：不直接全传；只保留摘要结果和关键版本块

### 为什么

- Stage 3 不是单独读取 changelog，还要读源码与项目本质
- 大 changelog 的噪声会迅速侵蚀弱模型可用上下文

### 推荐折中方案

不是二选一“grep 行” vs “整文件全塞”，而是：

1. 脚本先做结构化切块
2. 再只把高价值版本块和摘要传给模型

### 推荐输出

```markdown
## Changelog Signals

### v2.0.0 (2025-01-10)
- [breaking] Default config precedence changed
- [migration] Pass `override=True` to preserve old behavior

### v1.5.0 (2024-09-12)
- [deprecated] `find_dotenv(usecwd=False)` will be removed in v2
```

置信度：**高**

### 风险

- 版本标题格式非常自由时，正则切块会失误
- `HISTORY.rst` / 纯文本 changelog 需要额外兼容

---

## 五、问题 3：额外的社区信号来源

## 5.1 Stack Overflow

### 结论

**值得做，但排在 GitHub comments / advisories 之后。**

### 官方 API 能力

Stack Exchange API 提供：

#### 搜问题

```http
GET /2.3/search/advanced?order=desc&sort=votes&site=stackoverflow&tagged=python&intitle=python-dotenv&pagesize=10
```

#### 拉某组问题的答案

```http
GET /2.3/questions/{ids}/answers?order=desc&sort=votes&site=stackoverflow&filter=withbody
```

### 官方限额

文档显示：
- 按 `key` 统计时，默认每日请求额度通常是 `10,000`
- 还存在请求节流与 backoff 机制

### 为什么它有价值

- 高票答案往往就是“真实 workaround”
- 比 issue 更偏“面向最终用户的使用坑”
- 能补齐某些维护者不活跃仓库的社区知识

### 为什么不是 P0

- 项目名歧义大，搜索 query 设计不易
- 很多库没有稳定 tag
- 容易抓到与仓库无关的同名概念

### 建议实现方式

仅当满足以下条件时开启：
- 仓库是主流包（如 PyPI/npm 包）
- 有明确 package name
- GitHub 信号不足时再补充

置信度：**中高**

### 风险

- 搜索噪声大
- 非英语问题质量参差
- 与 repo 版本的对应关系弱

---

## 5.2 PyPI / npm 下载统计

### 结论

**可以作为成熟度背景信号，但不适合直接生成“社区陷阱”卡。**

### PyPI 官方情况

PyPI 官方 Stats API 公开的是：
- top packages
- total size / count 等全站级指标

而更细的下载数据在官方文档里是通过 **BigQuery 公共数据集** 提供分析能力，不适合你们这种用户机器上的轻量脚本直接消费。

### 工程判断

- 对“成熟度/生态规模”有用
- 对“规则卡 / gotcha”帮助很弱
- 成本高于收益

### 建议

**P2 以后再考虑**，而且更适合进入 `project_profile`，不是 `community_signals` 主体。

置信度：**中高**

### npm 说明

本次调研未找到稳定、明确的 npm 官方下载统计 API 文档，可作为后续单独议题处理；因此不建议现在把 npm 下载量接入到主流程里。

---

## 5.3 GitHub Stars / Forks 趋势

### 结论

**低价值，不建议进入 Stage 0。**

### 原因

- Stars / Forks 反映的是受欢迎程度，不是“容易踩的坑”
- 很多老项目 star 高但 issue 早已过时
- 趋势分析还需要历史时间序列，不适合轻量脚本

### 建议用途

如果要用，只放在 repo 背景摘要里，例如：
- “生态成熟”
- “活跃维护中”

不要让它进入社区陷阱提取核心数据面。

置信度：**高**

---

## 5.4 `git log` commit message 分析

### 结论

**高 ROI，建议立即加。**

### 为什么

- 完全本地，无网络依赖
- 能补充“最近修了哪些高频问题”
- 尤其适合没有完善 changelog 的项目

### 推荐命令

```bash
git -C "$REPO_PATH" log --no-merges --date=short \
  --pretty=format:'%h\t%ad\t%s' -n 200 \
  | grep -Ei 'fix|bug|regress|workaround|breaking|deprecat|rename|remove|migration'
```

### 推荐用途

- 补充 changelog
- 提示“最近哪些坑被集中修过”
- 为 Stage 3 提供候选规则标题

### 风险

- commit message 噪声很大
- 不少项目消息过于简略，如 `fix tests`

### 结论定位

把它当 **补充证据**，不要当主来源。

置信度：**高**

---

## 5.5 GitHub Security Advisories

### 结论

**非常值得加，优先级高。**

### 官方接口

```http
GET /repos/{owner}/{repo}/security-advisories?state=published&per_page=10
Accept: application/vnd.github+json
X-GitHub-Api-Version: 2022-11-28
```

### 为什么价值高

- 直接对应“高严重度规则卡”
- 数据结构清晰，包含：
  - `severity`
  - `summary`
  - `description`
  - `vulnerabilities[].package.ecosystem`
  - `vulnerabilities[].package.name`
  - `vulnerabilities[].vulnerable_version_range`
  - `vulnerabilities[].first_patched_version`

### 示例字段（伪示例）

```json
{
  "ghsa_id": "GHSA-xxxx-xxxx-xxxx",
  "summary": "Environment file path traversal under certain configs",
  "severity": "high",
  "vulnerabilities": [
    {
      "package": {"ecosystem": "pip", "name": "python-dotenv"},
      "vulnerable_version_range": "< 1.0.1",
      "first_patched_version": {"identifier": "1.0.1"}
    }
  ]
}
```

### 建议用途

- 直接生成候选 `DR-1xx` 高危规则
- 提示版本升级/修复范围

置信度：**高**

### 风险

- 很多项目没有公开 security advisories
- 不能代替普通使用坑，只能补高危面

---

## 5.6 其他值得考虑的来源

### 推荐：README Migration / Upgrade Sections

虽然你们已经抓 FAQ，但建议单独把 README 里的这些章节单列出来：
- Migration
- Upgrade guide
- Caveats
- Known issues

它们往往比 FAQ 更直接地描述“从旧版本升级会出什么问题”。

### 不推荐：Release popularity / social media

对规则卡价值低，且噪声大。

---

## 六、问题 4：`community_signals.md` 的信息架构

## 6.1 结构化 vs 自然语言：应该选什么？

### 结论

**推荐“结构化 Markdown”，不要纯 JSON/YAML，也不要纯散文。**

### 为什么不是纯 JSON/YAML

- 弱模型读大段 JSON 容易丢重点
- JSON 对人类调试不友好
- 你们当前脚本生成和后续肉眼检查都更适合 Markdown

### 为什么不是纯散文 Markdown

- 后续难去重、裁剪、排序
- Stage 3 难判断哪条信号更重要
- 不利于未来演进到 `.cursorrules` / `CLAUDE.md` 注入包

### 推荐模板

```markdown
# Community Signals

## Collection Meta

```yaml
repo: theskumar/python-dotenv
collected_at: 2026-03-09T12:00:00Z
provider: github
budget:
  issues_fetched: 50
  issue_comments_fetched: 18
  discussions_fetched: 0
  advisories_fetched: 1
status:
  github_api: partial
  stackoverflow: skipped
```

## Ranked Signals

### SIG-001 — Override precedence confusion

```yaml
source: github_issue
kind: bug
score: 0.91
confidence: high
upvotes: 29
comments: 14
state: closed
labels: [bug, docs]
url: https://github.com/.../issues/123
```

**Summary**: Users expect existing env vars to win, but default loading order differs in this scenario.

**Evidence**:
- Issue body: ...
- Maintainer comment: ...
- Resolution: pass `override=True`

**Actionable takeaway**:
- Prefer explicit `override=`
- Document precedence in deployment examples
```

### 优点

- 脚本容易生成
- 模型容易扫读
- 后续容易按 `score` 裁剪
- 人也能快速审查

置信度：**高**

---

## 6.2 是否应该标注权重 / 优先级？

### 结论

**必须标。**

### 原因

29 👍 的已关闭 bug 和 1 👍 的模糊提问，价值完全不同。

### 推荐字段

```yaml
score: 0.91
confidence: high
priority: P1
source_weight: 0.8
freshness_months: 3
```

### 简化打分公式

```python
def signal_score(signal):
    base = {
        'security_advisory': 1.00,
        'github_issue_bug': 0.85,
        'github_issue_question': 0.75,
        'github_discussion_answered': 0.70,
        'changelog_breaking': 0.80,
        'git_fix_commit': 0.45,
        'stackoverflow_accepted': 0.75,
    }[signal.kind]

    engagement = min(0.15, math.log1p(signal.engagement) / 20)
    recency = 0.05 if signal.months_since_update <= 18 else 0
    resolved = 0.05 if signal.resolved else 0
    penalty = 0.15 if signal.is_feature_request else 0
    return round(max(0, min(1, base + engagement + recency + resolved - penalty)), 2)
```

置信度：**高**

---

## 6.3 信息量控制：最终文件应该多大？

### 结论

**推荐目标：`12–20 KB`，硬上限 `32 KB`。**

### 理由

- Stage 3 还要读源码与前置分析文件
- `community_signals` 只是“辅助证据面”，不是主上下文
- 弱模型看到 50KB+ 的社区材料，很容易被噪声淹没

### 推荐配额

- meta：`< 1 KB`
- changelog：`2–4 KB`
- issues：`6–10 KB`
- security：`1–3 KB`
- git log：`1–2 KB`
- discussions / SO：按预算替换，不叠加失控

### 推荐条目数

- `Top signals`: 8–12 条
- 每条摘要正文：`80–180` 字
- 每条证据：最多 `3` 条 bullet

> 这部分属于工程经验判断，不是某个官方文档给出的硬阈值；但对你们当前弱模型场景非常实用。

置信度：**中高**

---

## 6.4 去重和去噪

### 结论

**需要，而且先做启发式就够了。**

### P0 启发式去重规则

1. **URL 去重**：相同 URL 直接去重
2. **标题归一化去重**：
   - 小写
   - 去标点
   - 去版本号
   - 去 stop words
3. **正文相似度去重**：
   - trigram Jaccard > `0.6` 时合并
4. **标签去噪**：
   - `enhancement`, `proposal`, `feature request` 降权
5. **时效去噪**：
   - 5 年前且已解决、且无后续重复的 issue 降权

### 合并后的输出

```yaml
duplicates:
  merged_from:
    - issue#123
    - issue#456
canonical_signal: issue#123
```

### 为什么不用更复杂方案

embedding / clustering 当然更强，但不适合 Stage 0 shell 脚本的复杂度预算。

置信度：**高**

---

## 七、问题 5：非 GitHub 项目支持

## 7.1 GitLab

### 结论

**GitLab 是最值得作为第二平台支持的。**

### 官方 API

#### 列项目 issues

```http
GET /projects/:id/issues
```

#### 列 issue discussions

```http
GET /projects/:id/issues/:issue_iid/discussions
```

### 为什么它最像 GitHub

- 有完整 issue 体系
- 有 threaded discussions / notes 能力
- 社区知识面较完整

### 工程复杂度

- 需要把 `owner/repo` 转成 project id 或 URL-encoded path
- 认证模型与 GitHub 不同
- 字段命名、分页机制要单独适配

### 建议

**如果要做第二平台，优先 GitLab。**

置信度：**高**

---

## 7.2 Bitbucket

### 结论

**不建议近期支持。**

### 原因

- Bitbucket Cloud 有 issues API
- 但官方文档中 issue comment 列表端点已出现 deprecation 信号
- 整体生态使用密度、社区内容密度通常也低于 GitHub / GitLab

### 官方接口示例

```http
GET /repositories/{workspace}/{repo_slug}/issues
```

注：issues comments 相关接口在官方文档中带有 deprecated 标记。

### 建议

短期直接跳过。

置信度：**中高**

---

## 7.3 Gitee

### 结论

**现在不要正式支持。先做 clone-only 降级。**

### 原因

- 从产品角度，中国大陆用户确实会遇到 Gitee 仓库
- 但本次调研未能通过稳定、明确的一手官方文档链路，完整验证 Gitee issues/comments/discussions 的 API 细节
- 在没有高置信 API 资料的前提下，不建议把它纳入 v1 主路径

### 推荐降级策略

当输入为 Gitee URL：

1. 继续 clone repo（如果可访问）
2. 继续本地信号：CHANGELOG / README / git log
3. 跳过远端社区 API 采集
4. 在元信息中注明：

```yaml
provider: gitee
remote_community_support: false
reason: not_implemented
```

### 信息不足说明

本次通过公开检索能看到 Gitee OpenAPI 存在 issue/comment 能力的迹象，但未拿到足够稳定、可核实的官方文档页面内容，因此不建议在本报告中给出实现级 API 细节。

置信度：**低到中**

---

## 7.4 如果只做 GitHub，非 GitHub URL 应如何降级？

### 推荐行为

```text
GitHub URL     -> full mode
GitLab URL     -> local-only now, reserve provider hook
Gitee URL      -> local-only
Bitbucket URL  -> local-only
Local path     -> local-only
```

### local-only 模式包含

- CHANGELOG / HISTORY
- README FAQ / Migration
- `git log` 修复类 commit
- 安全信息（若仓库内存在 advisory / security 文档）

### 用户提示建议

> 已完成本地信号采集；当前远端社区 API 仅正式支持 GitHub，因此未抓取平台 issue/discussion 数据。

置信度：**高**

---

## 八、推荐方案：如果我是工程师，我会怎么实现

## 8.1 总体架构

```text
prepare-repo.sh
  -> detect provider
  -> collect_local_signals
  -> if github: collect_github_signals
  -> merge + rank + dedupe
  -> render community_signals.md
```

---

## 8.2 推荐端点清单

### GitHub（P0/P1）

1. **Issues candidates**
```http
GET /repos/{owner}/{repo}/issues?state=all&sort=comments&direction=desc&per_page=50&page=1
```

2. **Issue comments for Top N**
```http
GET /repos/{owner}/{repo}/issues/{issue_number}/comments?sort=updated&direction=desc&per_page=3
```

3. **Security advisories**
```http
GET /repos/{owner}/{repo}/security-advisories?state=published&per_page=10
```

4. **Optional: Discussions (GraphQL)**
```graphql
repository { discussions { ... } }
```

### Stack Overflow（P2）

1. Search advanced
```http
GET /2.3/search/advanced?site=stackoverflow&intitle=<repo_or_package>&sort=votes&order=desc&pagesize=10
```

2. Answers
```http
GET /2.3/questions/{ids}/answers?site=stackoverflow&sort=votes&order=desc&filter=withbody
```

### GitLab（Future）

1. Project issues
```http
GET /projects/:id/issues
```

2. Issue discussions
```http
GET /projects/:id/issues/:issue_iid/discussions
```

---

## 8.3 推荐伪代码

```python
from math import log1p


def collect_community_signals(repo_url, repo_path, output_dir, env):
    provider = detect_provider(repo_url)

    signals = []
    signals.extend(collect_changelog_signals(repo_path))
    signals.extend(collect_readme_signals(repo_path))
    signals.extend(collect_gitlog_signals(repo_path))

    if provider == 'github':
        gh = GitHubClient(token=env.get('GITHUB_TOKEN'), cache_dir=f"{output_dir}/cache")

        issues = gh.list_repo_issues(sort='comments', state='all', per_page=50)
        issues = [issue for issue in issues if 'pull_request' not in issue]
        issues = [issue for issue in issues if classify_issue(issue) != 'feature']

        ranked_issues = rank_issues(issues)[:10]

        for issue in ranked_issues:
            signals.append(issue_to_signal(issue))
            comments = gh.list_issue_comments(issue['number'], sort='updated', per_page=3)
            signals.extend(comment_to_signal(issue, comment) for comment in pick_high_signal_comments(comments))

        advisories = gh.list_security_advisories(per_page=10)
        signals.extend(advisory_to_signal(item) for item in advisories)

        if env.get('GITHUB_TOKEN'):
            discussions = gh.list_discussions_graphql(limit=5)
            signals.extend(discussion_to_signal(d) for d in discussions)

    signals = dedupe_signals(signals)
    signals = rerank_signals(signals)
    signals = trim_to_budget(signals, max_bytes=20_000, max_items=12)

    render_markdown(signals, f"{output_dir}/artifacts/community_signals.md")
```

---

## 8.4 Shell 级实现建议

如果你们短期还想留在 shell + Python one-liner 体系，建议拆成两个脚本：

- `prepare-repo.sh`
- `scripts/collect-community-signals.py`

原因：
- comments/discussions/ranking/dedupe 超出纯 shell 舒适区
- Python 更适合做 JSON 处理、缓存、打分和模板渲染

### 最小调用方式

```bash
python3 "$BASE_DIR/scripts/collect-community-signals.py" \
  --repo-url "$REPO_INPUT" \
  --repo-path "$REPO_PATH" \
  --output "$OUTPUT_DIR/artifacts/community_signals.md"
```

置信度：**高**

---

## 九、优先级排序

## P0：今天就该做

1. **修正 GitHub issues 采集策略**
   - 去掉 `sort=reactions`
   - 改为 `sort=comments` + 本地打分

2. **增加 GitHub Security Advisories**
   - 高信号、结构清晰、请求少

3. **加缓存 + 条件请求 + token 可选增强**
   - 否则很快踩 rate limit

4. **重构 `community_signals.md` 为结构化 Markdown**
   - 为 Stage 3 做准备

## P1：1–2 天内完成

5. **对 Top issues 拉少量 comments**
6. **增加 `git log` fix 信号**
7. **把 CHANGELOG 升级为版本块提取**

## P2：1–2 周内再做

8. **GitHub Discussions（GraphQL）**
9. **Stack Overflow**
10. **GitLab provider**

## 暂不做

- Bitbucket provider
- Gitee 远端社区 API 正式支持
- PyPI / npm 下载统计进入主流程
- stars/forks 趋势

---

## 十、风险与注意事项

### 1. 认证和匿名模式必须共存

用户机器上未必有：
- `gh auth login`
- `GITHUB_TOKEN`

因此一定要支持：
- 有 token：增强采集
- 无 token：最小采集
- 失败：local-only fallback

### 2. 不能让远端 API 失败阻塞主链路

社区信号是增强项，不是 repo 打包的前置硬依赖。

### 3. 不要让 `community_signals.md` 失控膨胀

如果文件超过 30KB，Stage 3 的弱模型很容易被噪声淹没。

### 4. 必须显式过滤 PR

GitHub issues 列表会混 pull requests；不滤掉会污染“社区陷阱”候选集。

### 5. Discussion / Stack Overflow 容易引入版本错配

所以所有远端信号都应该带：
- `created_at`
- `updated_at`
- `version_hint`（若能解析）
- `confidence`

---

## 十一、最终推荐

### 我会采用的方案

**版本 1（立刻可做）**

- 本地：CHANGELOG + README Migration/FAQ + `git log`
- GitHub：issues candidates + top issue comments + security advisories
- 输出：结构化 `community_signals.md`
- 限制：`<= 20 KB`，Top 12 信号
- 降级：无 token / API 失败时不阻塞主流程

### 版本 2（增强版）

- 有 `GITHUB_TOKEN` 时增加 Discussions
- 信号写入统一 ranking / dedupe 管线
- 后续可导出成 Stage 3 更易消费的 `community_signals.yaml`

### 明确不建议的方案

- 继续依赖 `sort=reactions`
- 全量抓 issue comments
- 一开始就支持 GitHub/GitLab/Gitee/Bitbucket 四平台
- 让 `community_signals.md` 成为一个 50KB+ 的信息垃圾场

---

## 参考来源

### GitHub / GitLab / Bitbucket / Stack Exchange / PyPI

1. GitHub REST — Issues:  
   https://docs.github.com/en/rest/issues/issues
2. GitHub REST — Issue comments:  
   https://docs.github.com/en/rest/issues/comments
3. GitHub REST — Rate limits for the REST API:  
   https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
4. GitHub REST — Best practices for using the REST API:  
   https://docs.github.com/en/rest/guides/best-practices-for-using-the-rest-api
5. GitHub GraphQL — Discussion object:  
   https://docs.github.com/en/graphql/reference/objects#discussion
6. GitHub GraphQL — DiscussionComment object:  
   https://docs.github.com/en/graphql/reference/objects#discussioncomment
7. GitHub REST — Repository security advisories:  
   https://docs.github.com/en/rest/security-advisories/repository-advisories
8. GitLab API — Issues:  
   https://docs.gitlab.com/api/issues/
9. GitLab API — Discussions:  
   https://docs.gitlab.com/api/discussions/
10. Bitbucket Cloud REST API — Issues:  
    https://developer.atlassian.com/cloud/bitbucket/rest/api-group-issues/
11. Stack Exchange API — Search:  
    https://api.stackexchange.com/docs/search
12. Stack Exchange API — Advanced search:  
    https://api.stackexchange.com/docs/advanced-search
13. Stack Exchange API — Answers on questions:  
    https://api.stackexchange.com/docs/answers-on-questions
14. Stack Exchange API — Throttle and rate limits:  
    https://api.stackexchange.com/docs/throttle
15. PyPI Stats API:  
    https://docs.pypi.org/api/stats/
16. PyPI BigQuery Datasets:  
    https://docs.pypi.org/api/bigquery/
17. Keep a Changelog:  
    https://keepachangelog.com/en/1.1.0/

### 本地实现

- `Documents/vibecoding/allinone/skills/soul-extractor/scripts/prepare-repo.sh`
- `Documents/vibecoding/allinone/experiments/exp01-v04-minimax/research/20260309_codex_community_signals_task.md`

### 信息不足说明

- 本次未能通过稳定的一手资料，完整核实 Gitee 远端社区 API 的实现级细节，因此报告中对 Gitee 只给出降级建议，没有给出正式接入方案。
- 本次未找到稳定、明确的 npm 官方下载统计 API 文档，因此只把 PyPI 下载统计作为“成熟度背景信号”进行讨论。

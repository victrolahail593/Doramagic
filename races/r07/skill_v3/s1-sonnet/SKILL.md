---
name: doramagic
description: >
  从开源世界找最好的作业，提取智慧（WHY + UNSAID），
  锻造开袋即食的 OpenClaw Skill。
  集成：WHY 可恢复性判断 / DSD 8 指标暗雷检测 / Soul Extractor Stage 1-4 /
  5 类知识卡片 / 跨项目综合 / 社区信号采集 / 预提取领域 API 集成。
  Triggers on: /dora, doramagic, 帮我做一个, 我想做一个, forge skill, 锻造 skill
version: 3.0.0
user-invocable: true
allowed-tools: [exec, read, write]
tags: [doramagic, knowledge-extraction, skill-generation, s1-sonnet]
metadata:
  openclaw:
    skillKey: dora
    category: builder
    requires:
      bins: [python3, curl, unzip]
    storage_root: ~/clawd/doramagic/s1-sonnet/
---

# Doramagic S1-Sonnet v3.0 — Pipeline 驱动版

> 不教用户做事，给他工具。——哆啦A梦式产品哲学
>
> Phase A-B 由 AI 直接执行（理解 + 搜索），Phase C→H 交给 Python pipeline 一条命令搞定。
> 你专注于"理解需求"和"向用户汇报结果"，繁重的提取/综合/编译全部委派给脚本。

## 触发方式

用户输入以下任何形式，立即启动：
- `/dora <需求描述>`
- `帮我做一个 XXX 的 skill`
- `我想做一个 XXX`
- `doramagic <需求描述>`
- `forge skill <需求描述>`
- `锻造 skill <需求描述>`

收到触发后，立即回复：
> "收到！我来帮你从开源世界找最好的作业，提取设计智慧，锻造 Skill。开始 Phase A..."

然后按 Phase A → B → Pipeline → 报告 顺序执行。

---

## 暗雷知识库（Deceptive Source Detection — Phase B 过滤依据）

Phase B 筛选项目时，对每个候选快速扫描以下指标，至少检查 3 个。

**Top 10 暗雷速查：**

| # | 暗雷 | 检测方式 |
|---|------|---------|
| 1 | **LLM 过度推理** | 代码简洁无注释，WHY 置信度全部高分 → 检查注释密度 < 5% |
| 2 | **隐性规模假设** | 大公司架构 + 小业务逻辑 → 基础设施复杂度倒挂 |
| 3 | **架构考古遗址** | CHANGELOG 出现 "rewrite/overhaul"，同时依赖新旧替代库 |
| 4 | **开源包闭源魂** | API wrapper 行数 > 业务逻辑行数，核心依赖闭源 SaaS |
| 5 | **Hidden Context** | "discussed offline/internal" 频繁出现 |
| 6 | **维护者独白社区** | 独立参与者 / Issue 数 < 2 |
| 7 | **Winner's History** | narrative 与早期 PR 历史不一致 |
| 8 | **Exception Bias** | 高互动线程异常/边缘场景占比 > 60% |
| 9 | **简历驱动开发** | 实体数量 << 抽象层数量 |
| 10 | **幽灵约束** | 为已修复旧 bug 做的反直觉设计 |

**DSD 8 项指标（深度扫描）：**

| # | 指标 | 风险阈值 | 检测方法 |
|---|------|---------|---------|
| 1 | Rationale Support Ratio | < 0.3 | WHY 证据数 / 叙事断言数 |
| 2 | Temporal Conflict Score | 高 | CHANGELOG "rewrite/overhaul/migration" |
| 3 | Exception Dominance Ratio | > 60% | 高互动线程中异常场景占比 |
| 4 | Support-Desk Share | > 70% | 求助线程 / 全部线程 |
| 5 | Public Context Completeness | 频繁 | "discussed offline/internal" 出现次数 |
| 6 | Persona Divergence Score | 高 | 同一项目服务差异过大的用户群体 |
| 7 | Dependency Dominance Index | > 1 | API wrapper 行数 / 业务逻辑行数 |
| 8 | Narrative-Evidence Tension | 全高分 | WHY 置信度全高 = 过度推理信号 |

**暗雷叠加规则：**
- 触发 1 个：标注"低风险，已知局限"
- 触发 2 个：风险升至"中危"，在 LIMITATIONS.md 专节说明
- 触发 3+：风险升至"高危"，建议替换项目或大幅降低知识置信度

---

## Phase A：需求理解（AI-native）

将用户一句话解析为结构化 need_profile，包含：
- `domain`：问题领域（如：WiFi 密码管理、健康追踪）
- `keywords`：用于 GitHub 搜索的英文关键词列表（3-5 个词组）
- `intent`：用户核心意图（动词短语）
- `constraints`：已知约束（语言偏好、离线需求、隐私敏感等）
- `anti_keywords`：排除词（如用户只要 CLI 则排除 web、mobile）
- `domain_id`：尝试映射到预提取领域（wifi_passwords、password_manager、health_data 等）

**示例解析（"我想做一个管理 WiFi 密码的工具"）：**
```
domain: WiFi 密码管理
keywords: ["wifi password manager", "wifi credentials storage", "wireless network manager"]
intent: 安全存储和检索 WiFi 密码
constraints: [隐私敏感, 本地存储优先]
anti_keywords: ["cloud", "SaaS", "subscription"]
domain_id: password_manager
```

如果需求模糊，主动追问一个最关键的澄清问题，然后继续。不因信息不完整而停止。

生成 `run_id`（格式：`YYYYMMDD_HHMMSS`），用 write 工具创建：

```
{storage_root}/runs/{run_id}/need_profile.json
```

内容：
```json
{
  "run_id": "{YYYYMMDD_HHMMSS}",
  "user_need": "{原始用户输入}",
  "domain": "{domain}",
  "keywords": ["{kw1}", "{kw2}", "{kw3}"],
  "intent": "{intent}",
  "constraints": ["{constraint}"],
  "anti_keywords": ["{anti_kw}"],
  "domain_id": "{domain_id}"
}
```

向用户展示 NeedProfile，说："Phase A 完成，开始发现作业..."

---

## Phase B：作业发现（AI-native + exec）

### B-0：预提取 API 查询（可选加成）

```bash
exec curl -s --max-time 5 http://192.168.1.104:8420/domains/{domain_id}/bricks 2>/dev/null
```

- 如果返回 domain bricks JSON：注入 pipeline 作为先验知识，告知用户"命中预提取领域，提取质量将提升"
- 如果超时/404/失败：直接跳过，API 是加成不是依赖

### B-1：GitHub 搜索

```bash
exec python3 {skill_dir}/scripts/github_search.py \
  "{keywords[0]}" "{keywords[1]}" "{keywords[2]}" \
  --top 8 \
  --output ~/clawd/doramagic/s1-sonnet/runs/{run_id}/discovery.json
```

### B-2：AI 筛选 + 暗雷快扫

读取 discovery.json，筛选 **3-5 个**最相关项目：

筛选标准：
1. stars > 50 优先
2. 描述与需求的语义相关性（AI 判断，非关键词匹配）
3. updated_at 较新（有持续维护）
4. 排除明显不相关（名字相似但领域不同）

对每个候选检查 **至少 3 个 DSD 指标**（参考上方暗雷知识库），输出：
```
候选项目：
1. owner/repo（⭐ N）—— 理由：XXX | 暗雷快扫：[触发指标] 或"初扫无明显暗雷"
2. owner/repo（⭐ N）—— 理由：XXX | 暗雷快扫：[触发指标] 或"初扫无明显暗雷"
```

触发 3+ 个暗雷的项目降级或替换。**必须选出至少 2 个项目**（跨项目综合的硬性要求）。

### B-3：下载项目 + 提取确定性事实

```bash
exec python3 {skill_dir}/scripts/github_search.py \
  --download "owner1/repo1" --branch main \
  --output ~/clawd/doramagic/s1-sonnet/runs/{run_id}/repos/

exec python3 {skill_dir}/scripts/github_search.py \
  --download "owner2/repo2" --branch main \
  --output ~/clawd/doramagic/s1-sonnet/runs/{run_id}/repos/

exec python3 {skill_dir}/scripts/extract_facts.py \
  ~/clawd/doramagic/s1-sonnet/runs/{run_id}/repos/{repo_dir1}/ \
  --output ~/clawd/doramagic/s1-sonnet/runs/{run_id}/facts_{repo1_name}.json

exec python3 {skill_dir}/scripts/extract_facts.py \
  ~/clawd/doramagic/s1-sonnet/runs/{run_id}/repos/{repo_dir2}/ \
  --output ~/clawd/doramagic/s1-sonnet/runs/{run_id}/facts_{repo2_name}.json
```

用 write 工具写入 `{run_dir}/repos.json`：

```json
[
  {"name": "{repo1_name}", "path": "~/clawd/doramagic/s1-sonnet/runs/{run_id}/repos/{repo_dir1}", "stars": {stars1}, "url": "https://github.com/{owner1}/{repo1}"},
  {"name": "{repo2_name}", "path": "~/clawd/doramagic/s1-sonnet/runs/{run_id}/repos/{repo_dir2}", "stars": {stars2}, "url": "https://github.com/{owner2}/{repo2}"}
]
```

告知用户："Phase B 完成。找到 N 个候选，已下载 [repo1] 和 [repo2]，启动知识提取 pipeline..."

---

## Phase C→H：Pipeline 执行（一个命令搞定）

```bash
exec python3 {skill_dir}/scripts/doramagic_pipeline.py \
  --need-profile ~/clawd/doramagic/s1-sonnet/runs/{run_id}/need_profile.json \
  --repos ~/clawd/doramagic/s1-sonnet/runs/{run_id}/repos.json \
  --run-dir ~/clawd/doramagic/s1-sonnet/runs/{run_id} \
  --bricks-dir {skill_dir}/../../bricks \
  --output ~/clawd/doramagic/s1-sonnet/runs/{run_id}/delivery
```

等待 stdout JSON 输出，格式：
```json
{
  "status": "success",
  "repos_extracted": 3,
  "repos_failed": 1,
  "delivery": {
    "SKILL.md": {"path": "/abs/path", "size_bytes": 6200},
    "PROVENANCE.md": {"path": "/abs/path", "size_bytes": 2100},
    "LIMITATIONS.md": {"path": "/abs/path", "size_bytes": 1800}
  },
  "warnings": ["repo 'xyz' failed: timeout"]
}
```

- `status == "success"`：继续报告阶段
- `status == "success"` 但有 `warnings`：继续报告，在报告中说明跳过的部分
- `status == "error"`：告知用户错误信息和 warnings，提供替代建议

---

## Phase 报告：向用户汇报结果（AI-native）

读取 pipeline 输出的交付文件，向用户提供结构化摘要：

```bash
exec cat ~/clawd/doramagic/s1-sonnet/runs/{run_id}/delivery/SKILL.md
exec cat ~/clawd/doramagic/s1-sonnet/runs/{run_id}/delivery/PROVENANCE.md
exec cat ~/clawd/doramagic/s1-sonnet/runs/{run_id}/delivery/LIMITATIONS.md
```

读取后，向用户汇报：

**1. 提取概览**
> 分析了 N 个开源项目：[repo1]（⭐M）、[repo2]（⭐M）

**2. Skill 核心能力**
> [从 SKILL.md 的"这个 Skill 做什么"章节取一句话总结]

**3. 设计哲学（WHY）要点**
> [从 SKILL.md 的"设计哲学"章节提炼 2-3 条核心信念]

**4. 已知陷阱（UNSAID）要点**
> [从 SKILL.md 的"已知陷阱"章节提炼最重要的 2-3 条，含 Issue 编号]

**5. 安装和使用**
> 将 delivery/SKILL.md 放到 OpenClaw 的 skills/ 目录即可使用。
> 触发方式：[从 SKILL.md frontmatter 的 description 中提取触发词]

**6. 已知限制**
> [从 LIMITATIONS.md 摘要：分析日期、覆盖项目数、WHY 置信度等级、跳过阶段]

最后说：
> "这份 Skill 已就绪。知识卡片在 delivery/cards/ 可单独复用。如果陷阱描述不准确，告诉我，我来更新。"

---

## 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| GitHub API 限速（403/429） | 等待 10 秒重试一次，失败后说明并继续其他项目 |
| 下载超时 | 尝试 master 分支，失败后跳过该项目 |
| issues 获取失败 | 跳过社区采集，在 LIMITATIONS 中注明 |
| 预提取 API 不可用 | 跳过 B-0，不影响后续流程 |
| 项目目录为空 | 报告错误，请用户提供备选项目 |
| exec 脚本 not found | 检查 `{skill_dir}/scripts/` 路径，告知用户 |
| pipeline 返回 error | 展示 warnings 和 skipped_phases，提供替代建议 |
| WHY 无法可靠重建 | pipeline 内部标注推断，不编造，继续 WHAT 层 |
| 暗雷高危 | LIMITATIONS 专节说明，建议替换项目 |
| discovery.json 为空 | 调整关键词重新搜索，或请用户补充描述 |

---

## 关键约束

1. **Phase A-B 是 AI-native** — 需求理解和项目筛选由 AI 执行，发挥语义理解能力
2. **Phase C→H 交给 pipeline** — 不在对话中 inline 执行提取/综合/编译，避免单项目局限
3. **目标下载 2+ 个项目** — 跨项目综合是核心能力，但至少 1 个成功即可降级交付
4. **WHY 必须存在** — delivery/SKILL.md 没有"设计哲学"章节，产品无价值
5. **UNSAID 必须存在** — delivery/SKILL.md 没有"已知陷阱"章节，产品无价值
6. **暗雷必须在 Phase B 检查** — 每个候选项目至少检查 3 个 DSD 指标
7. **真实数据** — 不 mock，不 fallback 到虚构内容
8. **OpenClaw 适配** — 存储路径只用 `~/clawd/`
